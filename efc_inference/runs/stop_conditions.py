#!/usr/bin/env python3
"""
Stop Conditions — deterministic checks that can halt or escalate a case.

Four stop conditions:
  1. prior_dominance: posterior ≈ prior (alpha_std >= prior_width * threshold)
  2. no_value: N consecutive NO_SIGNAL cycles
  3. degeneracy_persists: N consecutive DEGENERACY_LIMITED verdicts
  4. manual: external escalation (checked via Neo4j flag)

Usage:
    checker = StopConditionChecker(policy)
    result = checker.check_all(baseline, case, driver)
    if result:
        checker.publish_stop_condition(cycle_id, case_id, result, driver)
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("stop_conditions")

# Prior width for alpha_cosmo (flat prior [-5, 5])
ALPHA_PRIOR_WIDTH = 10.0  # full width
ALPHA_PRIOR_HALF = 5.0    # half-width


# ═══════════════════════════════════════════════════════════════
#  RESULT
# ═══════════════════════════════════════════════════════════════

@dataclass
class StopResult:
    """Result from a triggered stop condition."""
    rule_name: str          # prior_dominance, no_value, degeneracy_persists, manual
    action: str             # ESCALATE or CLOSE
    description: str
    details: dict


# ═══════════════════════════════════════════════════════════════
#  CHECKER
# ═══════════════════════════════════════════════════════════════

class StopConditionChecker:
    """Deterministic stop condition evaluator."""

    def __init__(self, policy):
        self.policy = policy
        self.sc = policy.stop_conditions

    def check_prior_dominance(self, alpha_std: float) -> Optional[StopResult]:
        """Check if posterior is dominated by the prior.

        Triggered when alpha_std >= prior_half_width * threshold.
        (Threshold 0.95 means the posterior is ≥95% as wide as the prior.)
        """
        rule = self.sc.prior_dominance
        if not rule.enabled:
            return None

        threshold_width = ALPHA_PRIOR_HALF * rule.threshold
        if alpha_std >= threshold_width:
            return StopResult(
                rule_name="prior_dominance",
                action=rule.action,
                description=(
                    f"Posterior dominated by prior: alpha_std={alpha_std:.3f} "
                    f">= {threshold_width:.3f} (prior_half={ALPHA_PRIOR_HALF} * {rule.threshold})"
                ),
                details={
                    "alpha_std": alpha_std,
                    "threshold_width": threshold_width,
                    "prior_half_width": ALPHA_PRIOR_HALF,
                    "threshold_fraction": rule.threshold,
                },
            )
        return None

    def check_no_value(self, driver) -> Optional[StopResult]:
        """Check for N consecutive NO_SIGNAL cycles.

        Reads recent verdicts from Neo4j.
        """
        rule = self.sc.no_value
        if not rule.enabled:
            return None

        n_required = int(rule.threshold)
        verdicts = _get_recent_verdicts(driver, limit=n_required + 2)

        consecutive = 0
        for v in verdicts:
            if v == "NO_SIGNAL":
                consecutive += 1
            else:
                break

        if consecutive >= n_required:
            return StopResult(
                rule_name="no_value",
                action=rule.action,
                description=(
                    f"{consecutive} consecutive NO_SIGNAL cycles "
                    f"(threshold: {n_required})"
                ),
                details={
                    "consecutive_no_signal": consecutive,
                    "threshold": n_required,
                },
            )
        return None

    def check_degeneracy_persists(self, driver) -> Optional[StopResult]:
        """Check for N consecutive DEGENERACY_LIMITED verdicts."""
        rule = self.sc.degeneracy_persists
        if not rule.enabled:
            return None

        n_required = int(rule.threshold)
        verdicts = _get_recent_verdicts(driver, limit=n_required + 2)

        consecutive = 0
        for v in verdicts:
            if v == "DEGENERACY_LIMITED":
                consecutive += 1
            else:
                break

        if consecutive >= n_required:
            return StopResult(
                rule_name="degeneracy_persists",
                action=rule.action,
                description=(
                    f"{consecutive} consecutive DEGENERACY_LIMITED cycles "
                    f"(threshold: {n_required})"
                ),
                details={
                    "consecutive_degeneracy": consecutive,
                    "threshold": n_required,
                },
            )
        return None

    def check_all(self, baseline_result, driver) -> Optional[StopResult]:
        """Run all stop condition checks. Returns first triggered, or None.

        Args:
            baseline_result: BaselineResult from MCMC (for prior_dominance check).
                             Can be None if checking before baseline runs.
            driver: Neo4j driver for history queries.
        """
        # Prior dominance (only if we have a baseline)
        if baseline_result is not None:
            result = self.check_prior_dominance(baseline_result.alpha.std)
            if result:
                return result

        # No value (consecutive NO_SIGNAL)
        result = self.check_no_value(driver)
        if result:
            return result

        # Degeneracy persists
        result = self.check_degeneracy_persists(driver)
        if result:
            return result

        return None

    @staticmethod
    def publish_stop_condition(cycle_id: str, case_id: str,
                                stop: StopResult, driver) -> None:
        """Publish a StopCondition node to Neo4j and link to cycle."""
        now = datetime.now(timezone.utc).isoformat()

        with driver.session() as session:
            session.run("""
                CREATE (sc:StopCondition {
                    cycle_id: $cycle_id,
                    case_id: $case_id,
                    rule_name: $rule_name,
                    description: $description,
                    action: $action,
                    details_json: $details_json,
                    timestamp: datetime($now)
                })
            """,
                cycle_id=cycle_id,
                case_id=case_id,
                rule_name=stop.rule_name,
                description=stop.description,
                action=stop.action,
                details_json=json.dumps(stop.details),
                now=now,
            )

            # Link to cycle
            session.run("""
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MATCH (sc:StopCondition {cycle_id: $cycle_id})
                MERGE (rc)-[:TRIGGERED_STOP]->(sc)
            """, cycle_id=cycle_id)

        logger.info(f"Stop condition: {stop.rule_name} → {stop.action} "
                     f"(cycle {cycle_id}, case {case_id})")


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _get_recent_verdicts(driver, limit: int = 10) -> list:
    """Get recent cycle verdicts from Neo4j, most recent first."""
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (rc:ResearchCycleResult)
                WHERE rc.verdict IS NOT NULL
                RETURN rc.verdict AS verdict
                ORDER BY rc.timestamp DESC
                LIMIT $limit
            """, limit=limit)

            return [r["verdict"] for r in result]
    except Exception as e:
        logger.warning(f"Failed to fetch recent verdicts: {e}")
        return []
