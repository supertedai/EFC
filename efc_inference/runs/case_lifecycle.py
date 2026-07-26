#!/usr/bin/env python3
"""
Case Lifecycle — state machine + Neo4j persistence.

A ResearchCase tracks one continuous investigation of a specific
dataset (identified by data_hash). Cases persist across daemon
cycles and accumulate gate statuses, cycle history, and stop
conditions.

Usage:
    manager = CaseManager(neo4j_driver)
    case = manager.get_or_create_case(data_hash)
    manager.transition(case, CaseState.RUNNING, "cycle started")
    manager.link_cycle(case.case_id, cycle_id)
    manager.update_gates(case)
    new_state = manager.evaluate_promotion(case, policy)
"""
import os
import json
import logging
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger("case_lifecycle")


# ═══════════════════════════════════════════════════════════════
#  CASE STATE
# ═══════════════════════════════════════════════════════════════

class CaseState(Enum):
    """Research case states."""
    OPEN = "OPEN"
    RUNNING = "RUNNING"
    WATCHLIST = "WATCHLIST"
    CANDIDATE = "CANDIDATE"
    ROBUST = "ROBUST"
    CLOSED = "CLOSED"
    ESCALATED = "ESCALATED"


# Valid transitions
VALID_TRANSITIONS = {
    CaseState.OPEN: {CaseState.RUNNING, CaseState.CLOSED, CaseState.ESCALATED},
    CaseState.RUNNING: {CaseState.WATCHLIST, CaseState.CLOSED, CaseState.ESCALATED},
    CaseState.WATCHLIST: {CaseState.RUNNING, CaseState.CANDIDATE, CaseState.CLOSED, CaseState.ESCALATED},
    CaseState.CANDIDATE: {CaseState.RUNNING, CaseState.ROBUST, CaseState.CLOSED, CaseState.ESCALATED},
    CaseState.ROBUST: {CaseState.CLOSED, CaseState.ESCALATED},
    CaseState.CLOSED: set(),     # terminal
    CaseState.ESCALATED: set(),  # terminal
}


# ═══════════════════════════════════════════════════════════════
#  GATE STATUS
# ═══════════════════════════════════════════════════════════════

@dataclass
class GateStatus:
    """Tracks which gates have passed for the current cycle."""
    data_hygiene: bool = False
    convergence: bool = False
    hint_signal: bool = False
    candidate_signal: bool = False
    robust_signal: bool = False
    robustness_suite: bool = False  # N1 AND N2 AND T7
    ppc: bool = False
    sbc: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "GateStatus":
        return cls(**{k: v for k, v in d.items() if k in cls.__dataclass_fields__})


# ═══════════════════════════════════════════════════════════════
#  CASE RECORD
# ═══════════════════════════════════════════════════════════════

@dataclass
class CaseRecord:
    """In-memory representation of a ResearchCase."""
    case_id: str
    data_hash: str
    state: CaseState
    gates: GateStatus = field(default_factory=GateStatus)
    cycle_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "data_hash": self.data_hash,
            "state": self.state.value,
            "gates": self.gates.to_dict(),
            "cycle_count": self.cycle_count,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }


# ═══════════════════════════════════════════════════════════════
#  CASE MANAGER
# ═══════════════════════════════════════════════════════════════

class CaseManager:
    """Manages ResearchCase lifecycle in Neo4j."""

    def __init__(self, neo4j_driver):
        self.driver = neo4j_driver

    def get_or_create_case(self, data_hash: str) -> CaseRecord:
        """Get existing case by data_hash, or create new one.

        New data hash = new case (policy: data_hash_determines_case).
        """
        case_id = f"case_{data_hash[:12]}"
        now = datetime.now(timezone.utc).isoformat()

        with self.driver.session() as session:
            result = session.run("""
                MERGE (c:ResearchCase {case_id: $case_id})
                ON CREATE SET
                    c.data_hash = $data_hash,
                    c.state = 'OPEN',
                    c.cycle_count = 0,
                    c.gates_json = '{}',
                    c.created_at = datetime($now),
                    c.updated_at = datetime($now),
                    c.source = 'research_daemon'
                ON MATCH SET
                    c.updated_at = datetime($now)
                RETURN c.state AS state,
                       c.cycle_count AS cycle_count,
                       c.gates_json AS gates_json,
                       toString(c.created_at) AS created_at,
                       toString(c.updated_at) AS updated_at
            """, case_id=case_id, data_hash=data_hash, now=now)

            record = result.single()
            state_str = record["state"] if record else "OPEN"
            cycle_count = record["cycle_count"] if record else 0
            gates_json = record["gates_json"] if record else "{}"
            created_at = record["created_at"] if record else now
            updated_at = record["updated_at"] if record else now

        try:
            gates = GateStatus.from_dict(json.loads(gates_json)) if gates_json else GateStatus()
        except Exception:
            gates = GateStatus()

        case = CaseRecord(
            case_id=case_id,
            data_hash=data_hash,
            state=CaseState(state_str),
            gates=gates,
            cycle_count=cycle_count,
            created_at=created_at,
            updated_at=updated_at,
        )

        logger.info(f"Case {case_id}: state={case.state.value}, cycles={cycle_count}")
        return case

    def transition(self, case: CaseRecord, new_state: CaseState, reason: str) -> bool:
        """Transition case to a new state. Validates the transition.

        Returns True if transition was made, False if invalid.
        """
        if new_state == case.state:
            return True  # no-op

        valid = VALID_TRANSITIONS.get(case.state, set())
        if new_state not in valid:
            logger.warning(
                f"Invalid transition: {case.state.value} → {new_state.value} "
                f"(case {case.case_id})"
            )
            return False

        old_state = case.state.value
        now = datetime.now(timezone.utc).isoformat()

        with self.driver.session() as session:
            # Update case state
            session.run("""
                MATCH (c:ResearchCase {case_id: $case_id})
                SET c.state = $new_state,
                    c.updated_at = datetime($now)
            """, case_id=case.case_id, new_state=new_state.value, now=now)

            # Record state change as self-relationship for history
            session.run("""
                MATCH (c:ResearchCase {case_id: $case_id})
                CREATE (c)-[:STATE_CHANGE {
                    from_state: $from_state,
                    to_state: $to_state,
                    reason: $reason,
                    timestamp: datetime($now)
                }]->(c)
            """, case_id=case.case_id, from_state=old_state,
                 to_state=new_state.value, reason=reason, now=now)

        case.state = new_state
        case.updated_at = now
        logger.info(f"Case {case.case_id}: {old_state} → {new_state.value} ({reason})")
        return True

    def link_cycle(self, case_id: str, cycle_id: str):
        """Link a ResearchCycleResult to this case."""
        with self.driver.session() as session:
            session.run("""
                MATCH (c:ResearchCase {case_id: $case_id})
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MERGE (c)-[:INCLUDES_CYCLE]->(rc)
            """, case_id=case_id, cycle_id=cycle_id)

            # Increment cycle count
            session.run("""
                MATCH (c:ResearchCase {case_id: $case_id})
                SET c.cycle_count = coalesce(c.cycle_count, 0) + 1
            """, case_id=case_id)

        logger.info(f"Linked cycle {cycle_id} to case {case_id}")

    def update_gates(self, case: CaseRecord):
        """Write current gate status to Neo4j."""
        gates_json = json.dumps(case.gates.to_dict())
        now = datetime.now(timezone.utc).isoformat()

        with self.driver.session() as session:
            session.run("""
                MATCH (c:ResearchCase {case_id: $case_id})
                SET c.gates_json = $gates_json,
                    c.updated_at = datetime($now)
            """, case_id=case.case_id, gates_json=gates_json, now=now)

    def evaluate_promotion(self, case: CaseRecord, policy) -> Optional[CaseState]:
        """Evaluate if case should be promoted based on gates and policy.

        Returns the new state if promotion is warranted, None otherwise.
        Deterministic — no LLM.
        """
        gates = case.gates
        promo = policy.promotion_rules

        # Check each promotion level in order
        if case.state == CaseState.RUNNING:
            level = promo.to_watchlist
            req = level.required_gates
            if _gates_satisfied(gates, req, policy):
                return CaseState.WATCHLIST

        elif case.state == CaseState.WATCHLIST:
            level = promo.to_candidate
            req = level.required_gates
            if _gates_satisfied(gates, req, policy):
                return CaseState.CANDIDATE

        elif case.state == CaseState.CANDIDATE:
            level = promo.to_robust
            req = level.required_gates
            if _gates_satisfied(gates, req, policy):
                return CaseState.ROBUST

        return None

    def publish_hygiene_result(self, cycle_id: str, hygiene_result) -> None:
        """Publish DataHygieneResult node to Neo4j."""
        now = datetime.now(timezone.utc).isoformat()

        with self.driver.session() as session:
            session.run("""
                MERGE (dh:DataHygieneResult {cycle_id: $cycle_id})
                SET dh.passed = $passed,
                    dh.checks_json = $checks_json,
                    dh.failures_json = $failures_json,
                    dh.data_hashes_json = $data_hashes_json,
                    dh.lcdm_chi2_red = $lcdm_chi2_red,
                    dh.timestamp = datetime($now)
            """,
                cycle_id=cycle_id,
                passed=hygiene_result.passed,
                checks_json=json.dumps(hygiene_result.checks),
                failures_json=json.dumps(hygiene_result.failures),
                data_hashes_json=json.dumps(hygiene_result.data_hashes),
                lcdm_chi2_red=hygiene_result.lcdm_chi2_red,
                now=now,
            )

            # Link to cycle result
            session.run("""
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MATCH (dh:DataHygieneResult {cycle_id: $cycle_id})
                MERGE (rc)-[:HYGIENE_RESULT]->(dh)
            """, cycle_id=cycle_id)


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════

def _gates_satisfied(gates: GateStatus, req, policy) -> bool:
    """Check if all required gates are satisfied."""
    if req.data_hygiene and not gates.data_hygiene:
        return False
    if req.convergence and not gates.convergence:
        return False
    if req.signal and not gates.hint_signal:
        return False
    if req.robustness and not gates.robustness_suite:
        return False

    # PPC/SBC: if required but gate auto-passes, check the auto_pass flag
    if req.ppc:
        if policy.ppc_gate.auto_pass:
            pass  # auto-pass
        elif not gates.ppc:
            return False

    if req.sbc:
        if policy.sbc_gate.auto_pass:
            pass  # auto-pass
        elif not gates.sbc:
            return False

    return True
