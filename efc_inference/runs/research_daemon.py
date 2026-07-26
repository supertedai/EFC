#!/usr/bin/env python3
"""
Autonomous EFC Research Daemon.

SEE -> THINK -> ACT -> VERIFY -> LEARN cycle with policy-driven gates.

Runs baseline BAO+Growth inference, detects alpha signals,
triggers robustness diagnostics (N1 rd-control, N2 sigma8-sweep,
T7 leave-one-out), and publishes results to Neo4j.

Pass/fail rules are 100% deterministic (loaded from research_policy.yaml).
LLM is used ONLY for narrative synthesis (and never crashes the daemon).

Usage:
    python -m efc_inference.runs.research_daemon --mode once
    python -m efc_inference.runs.research_daemon --mode daemon --interval 21600
    python -m efc_inference.runs.research_daemon --mode once --policy path/to/policy.yaml
"""
import os
import sys
import json
import time
import signal
import hashlib
import logging
import argparse
import subprocess

import smtplib
from email.mime.text import MIMEText

import yaml
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from efc_inference.runs.research_mcmc import (
    load_modules,
    run_joint_inference,
    run_joint_inference_nuts,
    _nuts_available,
    run_n1_rd_diagnostic,
    run_n2_sigma8_sweep,
    run_t7_leave_one_out,
    run_n3_gate_sweep,
    run_n4_mu_sweep,
    run_n5_rd_sweep,
    run_n6_rd_efc,
    run_n7_cross_probe_lock,
    check_convergence,
    alpha_stats_to_dict,
    param_stats_to_dict,
    comparison_to_dict,
    BAO_PATH,
    GROWTH_PATH,
    HZ_PATH,
    SNIA_PATH,
    SNIA_COV_PATH,
    DEFAULT_NWALKERS,
    DEFAULT_NSTEPS,
    DEFAULT_BURNIN,
    DEFAULT_SEED,
    RD_FIXED,
)
from efc_inference.runs.research_policy import ResearchPolicy
from efc_inference.runs.data_hygiene import run_data_hygiene
from efc_inference.runs.case_lifecycle import CaseManager, CaseState
from efc_inference.runs.stop_conditions import StopConditionChecker
from efc_inference.core.cosmology_model import CosmologyModel, EFCVariantA, get_cosmology

logger = logging.getLogger("research_daemon")

# Default policy path
DEFAULT_POLICY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "configs", "research_policy.yaml"
)

# Default assumptions path
DEFAULT_ASSUMPTIONS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "configs", "assumptions.yaml"
)


# ═══════════════════════════════════════════════════════════════
#  CONFIGURATION (backward compat shim)
# ═══════════════════════════════════════════════════════════════

@dataclass
class ResearchRules:
    """Legacy shim — reads from ResearchPolicy when available."""
    signal_threshold: float = 1.5
    pass_sigma: float = 1.7
    pass_daic: float = 0.0
    collapse_sigma: float = 1.3
    loo_min_pass: int = 5
    rd_ci_trigger: float = 20.0


# ═══════════════════════════════════════════════════════════════
#  E-MAIL NOTIFICATION — fires on signal above threshold
# ═══════════════════════════════════════════════════════════════

def send_signal_notification(cycle_id: str, alpha_mean: float, alpha_std: float,
                             significance: float, verdict: str, diagnostics: dict,
                             sampler: str = "emcee"):
    """Send email notification when signal exceeds threshold.

    Configured via env vars:
        NOTIFY_EMAIL_TO       — recipient (default: none, disables notification)
        NOTIFY_EMAIL_FROM     — sender (default: efc-daemon@symbiose.local)
        NOTIFY_SMTP_HOST      — SMTP server (default: localhost)
        NOTIFY_SMTP_PORT      — SMTP port (default: 587)
        NOTIFY_SMTP_USER      — SMTP user (optional)
        NOTIFY_SMTP_PASS      — SMTP password (optional)
        NOTIFY_SIGMA_THRESHOLD — minimum significance to trigger (default: 2.0)
    """
    to_addr = os.environ.get("NOTIFY_EMAIL_TO", "")
    if not to_addr:
        return  # notification disabled

    threshold = float(os.environ.get("NOTIFY_SIGMA_THRESHOLD", "2.0"))
    if significance < threshold:
        return  # below threshold

    from_addr = os.environ.get("NOTIFY_EMAIL_FROM", "efc-daemon@symbiose.local")
    smtp_host = os.environ.get("NOTIFY_SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("NOTIFY_SMTP_PORT", "587"))
    smtp_user = os.environ.get("NOTIFY_SMTP_USER", "")
    smtp_pass = os.environ.get("NOTIFY_SMTP_PASS", "")

    # Build diagnostic summary
    diag_lines = []
    for key in ["n1", "n2", "t7", "n3", "n4", "n5", "n6", "n7"]:
        d = diagnostics.get(key, {})
        v = d.get("verdict", "N/A") if isinstance(d, dict) else "N/A"
        diag_lines.append(f"  {key.upper()}: {v}")

    subject = f"[EFC {sampler}] α = {alpha_mean:.3f}±{alpha_std:.3f} ({significance:.2f}σ) — {verdict}"

    body = f"""EFC Research Daemon — Signal Alert

Cycle: {cycle_id}
Sampler: {sampler}
Verdict: {verdict}

α = {alpha_mean:.3f} ± {alpha_std:.3f}  ({significance:.2f}σ)
P(α < 0) = {abs(alpha_mean) / alpha_std * 50 + 50:.1f}%

Diagnostics:
{chr(10).join(diag_lines)}

---
Threshold: {threshold}σ
This is an automated message from efc-research-daemon.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to_addr

    try:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            if smtp_port == 587:
                server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        logger.info(f"  📧 Signal notification sent to {to_addr} ({significance:.2f}σ ≥ {threshold}σ)")
    except Exception as e:
        logger.warning(f"  Email notification failed: {type(e).__name__}: {e}")


# ═══════════════════════════════════════════════════════════════
#  LOCK FILE — prevents overlapping cycles
# ═══════════════════════════════════════════════════════════════

class LockFile:
    """Context manager that prevents overlapping daemon cycles."""

    def __init__(self, path: str):
        self.path = path

    def __enter__(self):
        if os.path.exists(self.path):
            try:
                with open(self.path) as f:
                    old_pid = int(f.read().strip())
                # In Docker, PID 1 is init/entrypoint — never a real MCMC cycle.
                # Also stale if lockfile PID matches our own PID.
                if old_pid == os.getpid() or old_pid == 1:
                    logger.warning(f"Removing stale lock (PID {old_pid}): {self.path}")
                else:
                    os.kill(old_pid, 0)
                    raise RuntimeError(
                        f"Another cycle is running (PID {old_pid}). "
                        f"Remove {self.path} if stale."
                    )
            except (ValueError, OSError):
                logger.warning(f"Removing stale lock: {self.path}")

        os.makedirs(os.path.dirname(self.path) or ".", exist_ok=True)
        with open(self.path, "w") as f:
            f.write(str(os.getpid()))
        return self

    def __exit__(self, *args):
        try:
            os.unlink(self.path)
        except OSError:
            pass


# ═══════════════════════════════════════════════════════════════
#  SAFE LLM — never crashes the daemon
# ═══════════════════════════════════════════════════════════════

def safe_llm(messages: list, fallback: str = "") -> str:
    """LLM call that NEVER crashes the daemon."""
    try:
        from apis.unified_api.clients.llm_client import chat_with_fallback
        return chat_with_fallback(messages, timeout=30.0)
    except Exception as e:
        logger.warning(f"LLM unavailable ({type(e).__name__}), using fallback")
        return fallback


# ═══════════════════════════════════════════════════════════════
#  NEO4J PUBLISHER — direct driver for research nodes
# ═══════════════════════════════════════════════════════════════

class ResearchPublisher:
    """Publish ResearchCycleResult and DiagnosticResult to Neo4j."""

    def __init__(self):
        self._driver = None

    def _get_driver(self):
        if self._driver is None:
            try:
                from neo4j import GraphDatabase
                uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
                user = os.environ.get("NEO4J_USER", "neo4j")
                pwd = os.environ.get("NEO4J_PASSWORD", "")
                self._driver = GraphDatabase.driver(uri, auth=(user, pwd))
            except Exception as e:
                logger.warning(f"Neo4j unavailable: {e}")
                return None
        return self._driver

    def publish_cycle(self, cycle_data: dict):
        """MERGE a ResearchCycleResult node (schema_version 1.0)."""
        driver = self._get_driver()
        if driver is None:
            logger.warning("Skipping Neo4j publish (no driver)")
            return

        cypher = """
        MERGE (rc:ResearchCycleResult {cycle_id: $cycle_id})
        SET rc.timestamp = $timestamp,
            rc.schema_version = $schema_version,
            rc.code_commit = $code_commit,
            rc.dataset_hash = $dataset_hash,
            rc.assumptions_hash = $assumptions_hash,
            rc.cosmology_model = $cosmology_model,
            rc.verdict = $verdict,
            rc.verdict_reasoning = $verdict_reasoning,
            rc.alpha_mean = $alpha_mean,
            rc.alpha_std = $alpha_std,
            rc.alpha_significance = $alpha_significance,
            rc.p_alpha_negative = $p_alpha_negative,
            rc.daic = $daic,
            rc.dbic = $dbic,
            rc.om_mean = $om_mean,
            rc.om_std = $om_std,
            rc.h0_mean = $h0_mean,
            rc.h0_std = $h0_std,
            rc.s8_mean = $s8_mean,
            rc.s8_std = $s8_std,
            rc.n_data = $n_data,
            rc.signal_detected = $signal_detected,
            rc.convergence_pass = $convergence_pass,
            rc.n_eff_min = $n_eff_min,
            rc.r_hat_max = $r_hat_max,
            rc.diagnostics_triggered = $diagnostics_triggered,
            rc.total_mcmc_time = $total_mcmc_time,
            rc.artifact_path = $artifact_path,
            rc.manifest_json = $manifest_json,
            rc.assumptions_json = $assumptions_json,
            rc.sampler_type = $sampler_type,
            rc.n6_verdict = $n6_verdict,
            rc.n6_safety_level = $n6_safety_level,
            rc.n6_delta_rd_pct = $n6_delta_rd_pct,
            rc.n6_safety_pass = $n6_safety_pass,
            rc.d2_verdict = $d2_verdict,
            rc.d2_alpha_sig = $d2_alpha_sig,
            rc.d2_delta_alpha_sig = $d2_delta_alpha_sig,
            rc.d2_rd_mean = $d2_rd_mean,
            rc.d2_rd_std = $d2_rd_std,
            rc.dll_bao = $dll_bao,
            rc.dll_growth = $dll_growth,
            rc.dll_hz = $dll_hz,
            rc.dll_snia = $dll_snia,
            rc.bao_source = $bao_source,
            rc.diagnostics_forced = $diagnostics_forced,
            rc.diagnostics_reason = $diagnostics_reason,
            rc.source = 'research_daemon'
        RETURN elementId(rc) AS node_id
        """
        try:
            with driver.session() as session:
                result = session.run(cypher, **cycle_data)
                record = result.single()
                if record:
                    logger.info(f"Published ResearchCycleResult: {cycle_data['cycle_id']}")
        except Exception as e:
            logger.error(f"Failed to publish cycle: {e}")

    def publish_diagnostic(self, diag_data: dict, cycle_id: str):
        """MERGE a DiagnosticResult node and TRIGGERED relation."""
        driver = self._get_driver()
        if driver is None:
            return

        cypher = """
        MERGE (dr:DiagnosticResult {diagnostic_id: $diagnostic_id})
        SET dr.test_type = $test_type,
            dr.cycle_id = $cycle_id,
            dr.timestamp = $timestamp,
            dr.verdict = $verdict,
            dr.alpha_significance_best = $alpha_significance_best,
            dr.alpha_significance_worst = $alpha_significance_worst,
            dr.details_json = $details_json,
            dr.artifact_path = $artifact_path,
            dr.source = 'research_daemon'
        WITH dr
        MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
        MERGE (rc)-[:TRIGGERED]->(dr)
        RETURN elementId(dr) AS node_id
        """
        try:
            with driver.session() as session:
                session.run(cypher, **diag_data)
                logger.info(f"Published DiagnosticResult: {diag_data['diagnostic_id']}")
        except Exception as e:
            logger.error(f"Failed to publish diagnostic: {e}")

    def link_previous_cycle(self, current_cycle_id: str):
        """Create FOLLOWED_BY from previous cycle to current."""
        driver = self._get_driver()
        if driver is None:
            return

        cypher = """
        MATCH (prev:ResearchCycleResult)
        WHERE prev.cycle_id <> $current_id
        WITH prev ORDER BY prev.timestamp DESC LIMIT 1
        MATCH (curr:ResearchCycleResult {cycle_id: $current_id})
        MERGE (prev)-[:FOLLOWED_BY]->(curr)
        """
        try:
            with driver.session() as session:
                session.run(cypher, current_id=current_cycle_id)
        except Exception as e:
            logger.error(f"Failed to link cycles: {e}")

    def close(self):
        if self._driver:
            self._driver.close()


# ═══════════════════════════════════════════════════════════════
#  RESEARCH DAEMON
# ═══════════════════════════════════════════════════════════════

class EFCResearchDaemon:
    """Autonomous EFC inference research daemon.

    SEE -> THINK -> ACT -> VERIFY -> LEARN cycle with policy-driven gates.
    """

    def __init__(
        self,
        rules: ResearchRules = None,
        output_dir: str = "outputs/research",
        nwalkers: int = DEFAULT_NWALKERS,
        nsteps: int = DEFAULT_NSTEPS,
        burnin: int = DEFAULT_BURNIN,
        seed: int = DEFAULT_SEED,
        policy_path: str = None,
        assumptions_path: str = None,
        sampler: str = "emcee",
    ):
        # Load policy
        policy_path = policy_path or os.environ.get(
            "RESEARCH_POLICY_PATH", DEFAULT_POLICY_PATH
        )
        self.policy = ResearchPolicy.from_yaml(policy_path)
        logger.info(f"Policy loaded: v{self.policy.version} from {policy_path}")

        # Load cosmology from assumptions.yaml
        self.cosmology, self.assumptions_audit = self._load_cosmology(assumptions_path)
        logger.info(f"Cosmology loaded: {self.cosmology.name}")

        # Sampler selection: "emcee" (CPU) or "nuts" (GPU via JAX/numpyro)
        self.sampler = sampler.lower()
        if self.sampler == "nuts" and not _nuts_available():
            logger.warning("NUTS requested but JAX/numpyro not available — falling back to emcee")
            self.sampler = "emcee"
        logger.info(f"Sampler: {self.sampler}")

        # Backward compat: derive rules from policy
        self.rules = self.policy.to_research_rules()

        # Override MCMC params from policy if not explicitly set via args
        self.output_dir = output_dir
        self.nwalkers = nwalkers
        self.nsteps = nsteps
        self.burnin = burnin
        self.seed = seed
        self.publisher = ResearchPublisher()

        # NUTS-specific parameters (from env or defaults)
        self.nuts_warmup = int(os.environ.get("RESEARCH_NUTS_WARMUP", "500"))
        self.nuts_samples = int(os.environ.get("RESEARCH_NUTS_SAMPLES", "2000"))
        self.nuts_chains = int(os.environ.get("RESEARCH_NUTS_CHAINS", "2"))

        # Case manager and stop condition checker
        self._case_manager = None
        self._stop_checker = StopConditionChecker(self.policy)

        os.makedirs(output_dir, exist_ok=True)

    def _get_case_manager(self) -> Optional[CaseManager]:
        """Lazy init case manager (needs Neo4j driver)."""
        if self._case_manager is None:
            driver = self.publisher._get_driver()
            if driver:
                self._case_manager = CaseManager(driver)
        return self._case_manager

    @staticmethod
    def _load_cosmology(assumptions_path: str = None) -> tuple:
        """Load CosmologyModel from assumptions.yaml.

        Returns:
            (cosmology, assumptions_audit) tuple.
            Falls back to EFCVariantA() if file not found.
        """
        assumptions_path = assumptions_path or os.environ.get(
            "RESEARCH_ASSUMPTIONS_PATH", DEFAULT_ASSUMPTIONS_PATH
        )

        assumptions_audit = {}

        try:
            with open(assumptions_path) as f:
                cfg = yaml.safe_load(f) or {}

            cosmo_name = cfg.get("default_cosmology", "efc_variant_a")
            gate_cfg = cfg.get("gate", {})
            assumptions_audit = cfg.get("assumptions_audit", {})

            # Build cosmology with gate overrides from YAML
            # get_cosmology filters out extra keys (e.g. variant_b_defaults)
            cosmology = get_cosmology(cosmo_name, **gate_cfg)
            logger.info(f"Cosmology loaded: {cosmo_name} "
                        f"(gate: a_t={getattr(cosmology, '_a_t', 'N/A')}, "
                        f"delta_a={getattr(cosmology, '_delta_a', 'N/A')})")

        except FileNotFoundError:
            logger.warning(f"assumptions.yaml not found at {assumptions_path}, "
                           f"using default EFCVariantA()")
            cosmology = EFCVariantA()
            assumptions_audit = cosmology.assumptions

        except Exception as e:
            logger.warning(f"Failed to load assumptions.yaml: {e}, "
                           f"using default EFCVariantA()")
            cosmology = EFCVariantA()
            assumptions_audit = cosmology.assumptions

        return cosmology, assumptions_audit

    def run_once(self) -> dict:
        """Run one full cycle with policy-driven gates."""
        cycle_id = f"rc_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        timestamp = datetime.now(timezone.utc).isoformat()
        t_total_start = time.time()

        logger.info("=" * 70)
        logger.info(f"  RESEARCH CYCLE: {cycle_id}")
        logger.info("=" * 70)

        # Load all observation modules with injected cosmology
        modules = load_modules(cosmology=self.cosmology)
        n_bao = modules["bao"].n_data
        n_growth = modules["growth"].n_data
        n_hz = modules["hz"].n_data if modules.get("hz") else 0
        n_snia = modules["snia"].n_data if modules.get("snia") else 0
        n_total = n_bao + n_growth + n_hz + n_snia
        probes = [p for p, n in [("BAO", n_bao), ("Growth", n_growth),
                                  ("Hz", n_hz), ("SNIa", n_snia)] if n > 0]
        logger.info(f"  Data: {'+'.join(probes)} = {n_total} pts")
        logger.info(f"  Cosmology: {self.cosmology.name}")

        # ══════════════════════════════════════════════════════
        # PHASE 0: DATA HYGIENE GATE (NEW)
        # ══════════════════════════════════════════════════════
        logger.info("\n--- PHASE 0: DATA HYGIENE ---")
        # Include all active data files in hygiene hash
        extra_paths = {}
        if HZ_PATH and os.path.exists(HZ_PATH):
            extra_paths["hz"] = HZ_PATH
        if SNIA_PATH and os.path.exists(SNIA_PATH):
            extra_paths["snia"] = SNIA_PATH
        if SNIA_COV_PATH and os.path.exists(SNIA_COV_PATH):
            extra_paths["snia_cov"] = SNIA_COV_PATH
        hygiene = run_data_hygiene(
            BAO_PATH, GROWTH_PATH, modules["bao"], modules["growth"], self.policy,
            extra_data_paths=extra_paths if extra_paths else None,
        )

        if not hygiene.passed:
            logger.error(f"  DATA HYGIENE FAILED: {hygiene.failures}")
            total_time = time.time() - t_total_start
            self._publish_result(
                cycle_id, timestamp, None, {},
                "DATA_SUSPECT", f"Data hygiene failed: {hygiene.failures}", total_time,
            )
            # Publish hygiene result to Neo4j
            cm = self._get_case_manager()
            if cm:
                cm.publish_hygiene_result(cycle_id, hygiene)
            self._publish_data_suspect(cycle_id, hygiene)
            return {"verdict": "DATA_SUSPECT", "cycle_id": cycle_id}

        logger.info(f"  Data hygiene: PASS (hashes: bao={hygiene.data_hashes.get('bao', 'N/A')[:12]}..., "
                     f"growth={hygiene.data_hashes.get('growth', 'N/A')[:12]}...)")

        # Store data hashes for schema contract
        self._data_hashes = hygiene.data_hashes

        # Get or create case by data hash
        combined_hash = self._compute_combined_hash(hygiene.data_hashes)
        case = None
        cm = self._get_case_manager()
        if cm:
            case = cm.get_or_create_case(combined_hash)
            case.gates.data_hygiene = True

            # Handle terminal states: if case is ESCALATED or CLOSED,
            # the transition to RUNNING will fail. Log and continue without
            # case tracking — the MCMC still runs and publishes results.
            if case.state in (CaseState.ESCALATED, CaseState.CLOSED):
                logger.warning(
                    f"  Case {case.case_id} is in terminal state {case.state.value}. "
                    f"Cycle will run but case promotion is disabled. "
                    f"Reset case state in Neo4j or change data to create new case."
                )
            else:
                cm.transition(case, CaseState.RUNNING, f"cycle {cycle_id} started")
            cm.publish_hygiene_result(cycle_id, hygiene)

        # Pre-baseline stop conditions (no_value check)
        driver = self.publisher._get_driver()
        if driver:
            stop = self._stop_checker.check_no_value(driver)
            if stop:
                logger.warning(f"  STOP CONDITION: {stop.rule_name} → {stop.action}")
                total_time = time.time() - t_total_start
                self._publish_result(
                    cycle_id, timestamp, None, {},
                    f"STOPPED_{stop.rule_name.upper()}", stop.description, total_time,
                )
                StopConditionChecker.publish_stop_condition(
                    cycle_id, case.case_id if case else "unknown", stop, driver
                )
                if case and cm:
                    target = CaseState.CLOSED if stop.action == "CLOSE" else CaseState.ESCALATED
                    cm.transition(case, target, stop.description)
                return {"verdict": f"STOPPED_{stop.rule_name}", "cycle_id": cycle_id}

        # ══════════════════════════════════════════════════════
        # PHASE 1: SEE — baseline inference
        # ══════════════════════════════════════════════════════
        logger.info(f"\n--- PHASE 1: SEE (baseline inference, sampler={self.sampler}) ---")

        if self.sampler == "nuts":
            baseline = run_joint_inference_nuts(
                num_warmup=self.nuts_warmup,
                num_samples=self.nuts_samples,
                num_chains=self.nuts_chains,
                seed=self.seed,
            )
        else:
            baseline = run_joint_inference(
                modules,
                nwalkers=self.nwalkers, nsteps=self.nsteps,
                burnin=self.burnin, seed=self.seed,
            )

        # Convergence gate
        conv_result = None
        if self.sampler == "nuts":
            # NUTS convergence: use n_eff and r_hat from manifest
            n_eff = baseline.manifest.get("n_eff_min", float("nan"))
            r_hat = baseline.manifest.get("r_hat_max", float("nan"))
            if not np.isnan(n_eff) and not np.isnan(r_hat):
                converged = (r_hat <= 1.05 and n_eff >= 200)
                conv_result = {
                    "converged": converged,
                    "rhat_max": r_hat,
                    "ess_min": n_eff,
                    "acceptance_mean": 0.0,   # N/A for NUTS
                    "details": {
                        "sampler": "nuts",
                        "n_eff_min": n_eff,
                        "r_hat_max": r_hat,
                    },
                }
                logger.info(f"  NUTS convergence: {'PASS' if converged else 'FAIL'} "
                            f"(r_hat={r_hat:.4f}, n_eff={n_eff:.0f})")
            if case:
                case.gates.convergence = conv_result["converged"] if conv_result else True
        elif self.policy.inference_gates.convergence.enabled and baseline.sampler_efc is not None:
            logger.info("\n  >> Convergence gate")
            conv_result = check_convergence(baseline.sampler_efc, self.burnin, self.policy)

            if not conv_result["converged"] and self.policy.runtime.mcmc.retry_on_fail:
                # Retry with 2x nsteps
                retry_nsteps = int(self.nsteps * self.policy.runtime.mcmc.retry_nsteps_multiplier)
                logger.warning(f"  Convergence FAIL — retrying with nsteps={retry_nsteps}")
                baseline = run_joint_inference(
                    modules,
                    nwalkers=self.nwalkers, nsteps=retry_nsteps,
                    burnin=self.burnin, seed=self.seed,
                )
                conv_result = check_convergence(baseline.sampler_efc, self.burnin, self.policy)

                if not conv_result["converged"]:
                    logger.error("  Convergence STILL FAILS after retry — ESCALATING")
                    total_time = time.time() - t_total_start
                    self._publish_result(
                        cycle_id, timestamp, baseline, {},
                        "CONVERGENCE_FAIL", "MCMC did not converge after retry", total_time,
                    )
                    if case and cm:
                        cm.transition(case, CaseState.ESCALATED, "convergence failure after retry")
                    return {"verdict": "CONVERGENCE_FAIL", "cycle_id": cycle_id}

            if case:
                case.gates.convergence = conv_result["converged"]
        elif case:
            # No convergence check — auto-pass
            case.gates.convergence = True

        # Prior dominance stop condition (post-baseline)
        if driver:
            stop = self._stop_checker.check_prior_dominance(baseline.alpha.std)
            if stop:
                logger.warning(f"  STOP CONDITION: {stop.rule_name} → {stop.action}")
                total_time = time.time() - t_total_start
                self._publish_result(
                    cycle_id, timestamp, baseline, {},
                    f"STOPPED_{stop.rule_name.upper()}", stop.description, total_time,
                )
                StopConditionChecker.publish_stop_condition(
                    cycle_id, case.case_id if case else "unknown", stop, driver
                )
                if case and cm:
                    cm.transition(case, CaseState.ESCALATED, stop.description)
                return {"verdict": f"STOPPED_{stop.rule_name}", "cycle_id": cycle_id}

        # Link cycle to case
        if case and cm:
            cm.link_cycle(case.case_id, cycle_id)

        # ══════════════════════════════════════════════════════
        # PHASE 2: THINK — signal detection (deterministic)
        # ══════════════════════════════════════════════════════
        logger.info("\n--- PHASE 2: THINK (signal detection) ---")
        alpha_sig = baseline.alpha.significance
        mc = self.policy.inference_gates.model_comparison
        force_diag = self.policy.inference_gates.force_diagnostics
        force_diag_reason = self.policy.inference_gates.force_diagnostics_reason or "forced"
        signal_detected = alpha_sig >= mc.hint.alpha_sigma_min
        run_diagnostics = signal_detected or force_diag

        # Classify signal tier
        if case:
            case.gates.hint_signal = alpha_sig >= mc.hint.alpha_sigma_min
            case.gates.candidate_signal = (
                alpha_sig >= mc.candidate.alpha_sigma_min
                and baseline.comparison.daic <= mc.candidate.daic_max
            )
            case.gates.robust_signal = (
                alpha_sig >= mc.robust.alpha_sigma_min
                and baseline.comparison.daic <= mc.robust.daic_max
                and baseline.alpha.p_negative >= mc.robust.p_negative_min
            )

        logger.info(f"  alpha = {baseline.alpha.mean:.3f} +/- {baseline.alpha.std:.3f} "
                     f"({alpha_sig:.2f}sigma)")
        logger.info(f"  Signal threshold (hint): {mc.hint.alpha_sigma_min}")
        logger.info(f"  Signal detected: {signal_detected}")
        if force_diag and not signal_detected:
            logger.info(f"  force_diagnostics=True (reason: {force_diag_reason}) — running diagnostics despite low signal")

        if not run_diagnostics:
            narrative = safe_llm(
                [
                    {"role": "system", "content": (
                        "You are a scientific research assistant for EFC cosmology. "
                        "Write a brief 2-sentence summary of why no significant signal "
                        "was detected in this inference cycle. Be factual."
                    )},
                    {"role": "user", "content": (
                        f"Baseline inference: alpha = {baseline.alpha.mean:.3f} "
                        f"+/- {baseline.alpha.std:.3f} ({alpha_sig:.2f}sigma). "
                        f"Signal threshold: {mc.hint.alpha_sigma_min}sigma. "
                        f"dAIC = {baseline.comparison.daic:.2f}."
                    )},
                ],
                fallback=f"No significant EFC signal detected "
                         f"(alpha = {baseline.alpha.mean:.3f} +/- {baseline.alpha.std:.3f}, "
                         f"{alpha_sig:.2f}sigma < {mc.hint.alpha_sigma_min}sigma threshold).",
            )

            total_time = time.time() - t_total_start
            self._publish_result(
                cycle_id, timestamp, baseline, {},
                "NO_SIGNAL", narrative, total_time,
            )
            # Update case gates
            if case and cm:
                cm.update_gates(case)
                promoted = cm.evaluate_promotion(case, self.policy)
                if promoted:
                    cm.transition(case, promoted, f"promoted after cycle {cycle_id}")

            logger.info(f"  VERDICT: NO_SIGNAL ({total_time:.0f}s)")
            return {"verdict": "NO_SIGNAL", "cycle_id": cycle_id}

        # ══════════════════════════════════════════════════════
        # PHASE 3: ACT — run diagnostics
        # NOTE: N1/N2/T7 always use emcee (CPU) regardless of baseline sampler.
        # NUTS provides a superior baseline, but robustness diagnostics
        # need emcee's raw chain format for per-run model comparison.
        # ══════════════════════════════════════════════════════
        logger.info("\n--- PHASE 3: ACT (diagnostics, sampler=emcee) ---")
        diagnostics = {}

        # N1: rd diagnostic
        if self.policy.robustness_suite.n1.enabled:
            logger.info("\n  >>> N1: rd diagnostic")
            n1_result = run_n1_rd_diagnostic(
                modules,
                nwalkers=self.nwalkers, nsteps=self.nsteps,
                burnin=self.burnin, seed=self.seed,
                pass_sigma=self.rules.pass_sigma,
                pass_daic=self.rules.pass_daic,
            )
            diagnostics["n1"] = n1_result

        # N2: sigma8 sweep
        if self.policy.robustness_suite.n2.enabled:
            logger.info("\n  >>> N2: sigma8 sweep")
            n2_result = run_n2_sigma8_sweep(
                modules,
                nwalkers=self.nwalkers, nsteps=self.nsteps,
                burnin=self.burnin, seed=self.seed,
                pass_sigma=self.rules.pass_sigma,
                pass_daic=self.rules.pass_daic,
                collapse_sigma=self.rules.collapse_sigma,
            )
            diagnostics["n2"] = n2_result

        # T7: LOO (only if N1 AND N2 both pass)
        n1_pass = diagnostics.get("n1", {}).get("verdict") == "PASS"
        n2_pass = diagnostics.get("n2", {}).get("verdict") == "PASS"
        if self.policy.robustness_suite.t7.enabled and n1_pass and n2_pass:
            logger.info("\n  >>> T7: leave-one-out (N1+N2 passed)")
            t7_result = run_t7_leave_one_out(
                modules, growth_path=GROWTH_PATH,
                nwalkers=self.nwalkers,
                nsteps=3000, burnin=1000,
                seed=self.seed,
                pass_sigma=self.rules.pass_sigma,
                pass_daic=self.rules.pass_daic,
                loo_min_pass=self.policy.robustness_suite.t7.min_pass,
            )
            diagnostics["t7"] = t7_result
        elif not (n1_pass and n2_pass):
            logger.info(f"\n  >>> T7: SKIPPED (N1={diagnostics.get('n1', {}).get('verdict', 'N/A')}, "
                         f"N2={diagnostics.get('n2', {}).get('verdict', 'N/A')})")

        # N3: gate freedom (runs independently of N1/N2/T7 pass)
        # Note: emcee N3 uses legacy α (not A_eff). NUTS GPU uses A_eff.
        # A_eff reparameterization is primarily critical for NUTS where
        # the degeneracy COLLAPSED verdict was observed.
        if self.policy.robustness_suite.n3.enabled:
            logger.info("\n  >>> N3: gate freedom diagnostic (emcee, α-param)")
            try:
                n3_result = run_n3_gate_sweep(
                    modules,
                    nwalkers=self.nwalkers, nsteps=self.nsteps,
                    burnin=self.burnin, seed=self.seed,
                    pass_sigma=self.policy.robustness_suite.n3.pass_sigma,
                    collapse_sigma=self.policy.robustness_suite.n3.collapse_sigma,
                )
                diagnostics["n3"] = n3_result
                logger.info(f"  N3 verdict: {n3_result['verdict']}")
            except Exception as e:
                logger.error(f"  N3 failed: {type(e).__name__}: {e}")
                diagnostics["n3"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # N4: modified Poisson (runs independently of N1/N2/T7)
        if self.policy.robustness_suite.n4.enabled:
            logger.info("\n  >>> N4: modified Poisson (μ≠1) diagnostic")
            try:
                n4_result = run_n4_mu_sweep(
                    modules,
                    nwalkers=self.nwalkers, nsteps=self.nsteps,
                    burnin=self.burnin, seed=self.seed,
                    pass_sigma=self.policy.robustness_suite.n4.pass_sigma,
                    collapse_sigma=self.policy.robustness_suite.n4.collapse_sigma,
                    degeneracy_corr_max=self.policy.robustness_suite.n4.degeneracy_corr_max,
                )
                diagnostics["n4"] = n4_result
                logger.info(f"  N4 verdict: {n4_result['verdict']}")
            except Exception as e:
                logger.error(f"  N4 failed: {type(e).__name__}: {e}")
                diagnostics["n4"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # N5: sound horizon prior sweep (D2a — runs independently)
        if self.policy.robustness_suite.n5.enabled:
            logger.info("\n  >>> N5: sound horizon prior sweep (D2a)")
            try:
                n5_result = run_n5_rd_sweep(
                    modules,
                    nwalkers=self.nwalkers, nsteps=self.nsteps,
                    burnin=self.burnin, seed=self.seed,
                    pass_sigma=self.policy.robustness_suite.n5.pass_sigma,
                    collapse_sigma=self.policy.robustness_suite.n5.collapse_sigma,
                    degeneracy_corr_max=self.policy.robustness_suite.n5.degeneracy_corr_max,
                )
                diagnostics["n5"] = n5_result
                logger.info(f"  N5 verdict: {n5_result['verdict']}")
            except Exception as e:
                logger.error(f"  N5 failed: {type(e).__name__}: {e}")
                diagnostics["n5"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # N6: EFC sound horizon (D2b — post-fit, no MCMC)
        if self.policy.robustness_suite.n6.enabled and baseline.chain_efc is not None:
            logger.info("\n  >>> N6: EFC sound horizon (D2b)")
            try:
                n6_cfg = self.policy.robustness_suite.n6
                n6_result = run_n6_rd_efc(
                    baseline_chains=baseline.chain_efc,
                    R_max=n6_cfg.R_max,
                    sigma_ln_a=n6_cfg.sigma_ln_a,
                    safety_threshold_pct=n6_cfg.safety_threshold_pct,
                    Omega_b=n6_cfg.Omega_b,
                    sweep_R_max=n6_cfg.sweep_R_max,
                )
                diagnostics["n6"] = n6_result
                logger.info(f"  N6 verdict: {n6_result['verdict']}")
            except Exception as e:
                logger.error(f"  N6 failed: {type(e).__name__}: {e}")
                diagnostics["n6"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # N7: global parameter-lock cross-probe ("Domstolen")
        # GRAV-locked G_eff in growth source, all other params frozen.
        # Runs AFTER N1+N2+T7 — this is the "final exam".
        if self.policy.robustness_suite.n7.enabled:
            logger.info("\n  >>> N7: GRAV-locked cross-probe ('Domstolen')")
            try:
                n7_result = run_n7_cross_probe_lock(
                    modules,
                    nwalkers=self.nwalkers, nsteps=self.nsteps,
                    burnin=self.burnin, seed=self.seed,
                )
                diagnostics["n7"] = n7_result
                logger.info(f"  N7 verdict: {n7_result['verdict']}")
            except Exception as e:
                logger.error(f"  N7 failed: {type(e).__name__}: {e}")
                diagnostics["n7"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # Update case robustness gate
        if case:
            t7_pass = diagnostics.get("t7", {}).get("verdict") == "PASS"
            case.gates.robustness_suite = n1_pass and n2_pass and t7_pass

        # ── D2: Self-consistent sound horizon ─────────────────
        if self.policy.robustness_suite.d2.enabled and baseline is not None:
            logger.info("\n  >>> D2: self-consistent sound horizon")
            try:
                from efc_inference.runs.research_mcmc import run_d2_comparison
                d2_cfg = self.policy.robustness_suite.d2
                d2_result = run_d2_comparison(
                    modules,
                    baseline_result=baseline,
                    nwalkers=self.nwalkers, nsteps=self.nsteps,
                    burnin=self.burnin, seed=self.seed,
                    R_max=d2_cfg.R_max,
                    pass_delta_alpha=d2_cfg.pass_delta_alpha,
                )
                diagnostics["d2"] = d2_result
                logger.info(f"  D2 verdict: {d2_result['verdict']} "
                            f"(α={d2_result['alpha_sig']:.2f}σ, "
                            f"r_d={d2_result['rd_posterior_mean']:.2f} Mpc)")
            except Exception as e:
                logger.error(f"  D2 failed: {type(e).__name__}: {e}")
                diagnostics["d2"] = {"verdict": "ERROR", "error": str(e)[:300]}

        # ── PPC gate (Fase 2) ──────────────────────────────────
        # NOTE: PPC requires full posterior chain. NUTS baseline provides
        # only summary stats (1-row synthetic chain), so PPC auto-passes
        # for NUTS. Full PPC coverage comes from emcee diagnostics above.
        ppc_result = None
        if self.sampler == "nuts":
            # Auto-pass PPC for NUTS (no full posterior chain available)
            logger.info("\n  >>> PPC: auto-pass (NUTS baseline, no posterior chain)")
            if case:
                case.gates.ppc = True
        elif self.policy.ppc_gate.enabled and not self.policy.ppc_gate.auto_pass:
            logger.info("\n  >>> PPC: Running posterior predictive checks...")
            try:
                ppc_result = self._run_ppc(baseline, modules)
                ppc_pass = ppc_result["passed"]
                logger.info(f"  >>> PPC: {'PASS' if ppc_pass else 'FAIL'} — {ppc_result['reason']}")
                for mod_name, mod_res in ppc_result["modules"].items():
                    r = mod_res["report"]
                    p_val = r.get("bayesian_p_value", None)
                    p_str = f"{p_val:.3f}" if p_val is not None else "N/A"
                    logger.info(
                        f"      {mod_name}: chi2_red={r['chi2_reduced']:.3f}, "
                        f"cal_1s={r['calibration']['within_1sigma']:.3f}, "
                        f"p_val={p_str}"
                    )
                if case:
                    case.gates.ppc = ppc_pass
            except Exception as exc:
                logger.error(f"  >>> PPC: EXCEPTION — {exc}")
                ppc_result = {"passed": False, "modules": {},
                              "reason": f"exception: {exc}"}
                if case:
                    case.gates.ppc = False
        else:
            # Auto-pass (backward compat or PPC disabled)
            if case:
                case.gates.ppc = True
            logger.info("\n  >>> PPC: auto-pass (not enabled)")

        diagnostics["ppc"] = ppc_result

        # ── SBC gate (Fase 3 — ACTIVE) ───────────────────────
        sbc_result = None
        if self.policy.sbc_gate.enabled and not self.policy.sbc_gate.auto_pass:
            # Only run SBC on CANDIDATE→ROBUST transition (expensive)
            should_run_sbc = (case and case.state in ("CANDIDATE", "WATCHLIST")
                              and self.sampler != "nuts")
            if should_run_sbc:
                logger.info("\n  >>> SBC: Running Simulation-Based Calibration...")
                try:
                    from efc_inference.core.sbc import sbc_for_emcee, sbc_verdict_to_dict
                    from efc_inference.runs.research_mcmc import _log_prob_baseline_efc

                    sbc_cfg = self.policy.sbc_gate
                    sbc_result = sbc_for_emcee(
                        modules=modules,
                        log_prob_fn=_log_prob_baseline_efc,
                        n_simulations=sbc_cfg.n_simulations,
                        nwalkers=sbc_cfg.nwalkers,
                        nsteps=sbc_cfg.nsteps,
                        burnin=sbc_cfg.burnin,
                        seed=self.seed + 5000,
                    )
                    if sbc_result.passed:
                        if case:
                            case.gates.sbc = True
                        logger.info(f"  SBC: PASS — {sbc_result.verdict}")
                    else:
                        logger.warning(f"  SBC: FAIL — {sbc_result.verdict}")
                    diagnostics["sbc"] = sbc_verdict_to_dict(sbc_result)
                except Exception as e:
                    logger.error(f"  SBC failed: {type(e).__name__}: {e}")
                    diagnostics["sbc"] = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
            else:
                logger.info(f"\n  >>> SBC: skipped (state={case.state if case else 'none'}, "
                            f"sampler={self.sampler})")
                if case:
                    case.gates.sbc = False
        elif self.policy.sbc_gate.auto_pass:
            if case:
                case.gates.sbc = True
            logger.info("\n  >>> SBC: auto-pass")

        # ══════════════════════════════════════════════════════
        # PHASE 4: VERIFY — deterministic verdict
        # ══════════════════════════════════════════════════════
        logger.info("\n--- PHASE 4: VERIFY (verdict) ---")
        verdict = self._compute_verdict(baseline, diagnostics)

        # ── VariantH: always runs regardless of alpha verdict ──
        # VariantH tests entropy-gradient growth (∇S → μ) independently of
        # the Friedmann-gate alpha parameter. Must run even if alpha is dead.
        logger.info("\n--- PHASE 9 (early): VariantH entropy-gradient growth ---")
        try:
            self._run_variant_h_diagnostic(cycle_id)
        except Exception as e:
            logger.warning(f"VariantH failed (non-fatal): {type(e).__name__}: {e}")

        # Degeneracy stop condition (post-verdict)
        if driver and verdict == "DEGENERACY_LIMITED":
            stop = self._stop_checker.check_degeneracy_persists(driver)
            if stop:
                logger.warning(f"  STOP CONDITION: {stop.rule_name} → {stop.action}")
                total_time = time.time() - t_total_start
                self._publish_result(
                    cycle_id, timestamp, baseline, diagnostics,
                    f"STOPPED_{stop.rule_name.upper()}", stop.description, total_time,
                )
                StopConditionChecker.publish_stop_condition(
                    cycle_id, case.case_id if case else "unknown", stop, driver
                )
                if case and cm:
                    cm.transition(case, CaseState.ESCALATED, stop.description)
                return {"verdict": f"STOPPED_{stop.rule_name}", "cycle_id": cycle_id}

        # LLM narrative (never crashes)
        narrative = safe_llm(
            [
                {"role": "system", "content": (
                    "You are a scientific research assistant for EFC cosmology. "
                    "Write a concise 3-4 sentence ledger-grade summary of this "
                    "inference cycle result. Include alpha significance, "
                    "diagnostics passed, and verdict. Be factual, not speculative."
                )},
                {"role": "user", "content": (
                    f"Baseline: alpha = {baseline.alpha.mean:.3f} "
                    f"+/- {baseline.alpha.std:.3f} ({alpha_sig:.2f}sigma). "
                    f"N1 verdict: {diagnostics.get('n1', {}).get('verdict', 'N/A')}. "
                    f"N2 verdict: {diagnostics.get('n2', {}).get('verdict', 'N/A')}. "
                    f"T7 verdict: {diagnostics.get('t7', {}).get('verdict', 'N/A')}. "
                    f"N3 verdict: {diagnostics.get('n3', {}).get('verdict', 'N/A')}. "
                    f"N4 verdict: {diagnostics.get('n4', {}).get('verdict', 'N/A')}. "
                    f"N5 verdict: {diagnostics.get('n5', {}).get('verdict', 'N/A')}. "
                    f"Overall: {verdict}."
                )},
            ],
            fallback=f"Research cycle {cycle_id}: verdict={verdict}, "
                     f"alpha={baseline.alpha.mean:.3f}+/-{baseline.alpha.std:.3f} "
                     f"({alpha_sig:.2f}sigma).",
        )

        logger.info(f"  VERDICT: {verdict}")

        # Signal notification (email if above threshold)
        send_signal_notification(
            cycle_id, baseline.alpha.mean, baseline.alpha.std,
            alpha_sig, verdict, diagnostics, sampler=self.sampler,
        )

        # ══════════════════════════════════════════════════════
        # PHASE 5: LEARN — publish + save artifacts
        # ══════════════════════════════════════════════════════
        logger.info("\n--- PHASE 5: LEARN (publish + save) ---")
        total_time = time.time() - t_total_start

        self._publish_result(
            cycle_id, timestamp, baseline, diagnostics,
            verdict, narrative, total_time,
        )
        self._save_artifacts(
            cycle_id, baseline, diagnostics, verdict, narrative,
            hygiene_result=hygiene, convergence_result=conv_result,
        )

        # Notify Mattermost
        self._notify_mattermost_emcee(cycle_id, baseline, diagnostics, verdict, total_time)

        # Update case gates and evaluate promotion
        if case and cm:
            cm.update_gates(case)
            promoted = cm.evaluate_promotion(case, self.policy)
            if promoted:
                cm.transition(case, promoted, f"promoted to {promoted.value} after {verdict}")
                logger.info(f"  Case {case.case_id} promoted to {promoted.value}")

        # PHASE 6: DIVERGENCE ANALYSIS — find where EFC and LCDM differ most
        # ══════════════════════════════════════════════════════════════════
        try:
            self._run_divergence_analysis(baseline)
        except Exception as e:
            logger.warning(f"Divergence analysis failed (non-fatal): {type(e).__name__}: {e}")

        # PHASE 7: AXIOM 0 — S_hat(z) regime boundary test
        # ══════════════════════════════════════════════════════════════════
        try:
            self._run_axiom0_test(cycle_id, baseline)
        except Exception as e:
            logger.warning(f"Axiom 0 test failed (non-fatal): {type(e).__name__}: {e}")

        # PHASE 8: VARIANT-G — Constitutive law growth diagnostic (3 k_eff scenarios)
        # ══════════════════════════════════════════════════════════════════
        for vg_scenario in ["G10", "G02", "G01"]:
            try:
                self._run_variant_g_diagnostic(cycle_id, scenario=vg_scenario)
            except Exception as e:
                logger.warning(f"VariantG {vg_scenario} failed (non-fatal): {type(e).__name__}: {e}")

        # (VariantH moved to pre-stop-condition — see "PHASE 9 (early)" above)

        # PHASE 10: FORBIDDEN PATTERN DISTANCE — quantify distance to each FP trigger
        # ══════════════════════════════════════════════════════════════════
        try:
            self._run_fp_distance(cycle_id, baseline)
        except Exception as e:
            logger.warning(f"FP distance failed (non-fatal): {type(e).__name__}: {e}")

        # PHASE 11: PARAMETER-LOCK CONSISTENCY — freeze params, check per-probe
        # ══════════════════════════════════════════════════════════════════
        try:
            self._run_parameter_lock(cycle_id, baseline)
        except Exception as e:
            logger.warning(f"Parameter-lock failed (non-fatal): {type(e).__name__}: {e}")

        logger.info(f"\n  Cycle complete: {verdict} in {total_time:.0f}s "
                     f"({total_time/60:.1f}min)")
        logger.info("=" * 70)

        return {"verdict": verdict, "cycle_id": cycle_id}

    def _run_divergence_analysis(self, baseline):
        """Run Divergence Maximization Engine on the latest MCMC results.

        Extracts best-fit params from baseline, runs full divergence scan,
        saves report JSON, and logs the summary.
        """
        from .divergence_engine import DivergenceEngine

        logger.info("\n--- PHASE 6: DIVERGENCE ANALYSIS ---")

        # Extract best-fit from posterior chain (median)
        chain = baseline.chain_efc  # shape (n_samples, 4): Om, H0, s8, alpha
        if chain is None or len(chain) == 0:
            logger.warning("  No posterior chain available — skipping divergence")
            return

        params_efc = {
            "Omega_m": float(np.median(chain[:, 0])),
            "H0": float(np.median(chain[:, 1])),
            "sigma8": float(np.median(chain[:, 2])),
            "alpha_cosmo": float(np.median(chain[:, 3])),
            "r_d": RD_FIXED,
        }

        # LCDM: use baseline's LCDM chain if available, else similar Om/H0
        chain_lcdm = baseline.chain_lcdm
        if chain_lcdm is not None and len(chain_lcdm) > 0:
            params_lcdm = {
                "Omega_m": float(np.median(chain_lcdm[:, 0])),
                "H0": float(np.median(chain_lcdm[:, 1])),
                "sigma8": float(np.median(chain_lcdm[:, 2])),
                "alpha_cosmo": 0.0,
                "r_d": RD_FIXED,
            }
        else:
            params_lcdm = {
                "Omega_m": params_efc["Omega_m"],
                "H0": params_efc["H0"],
                "sigma8": params_efc["sigma8"],
                "alpha_cosmo": 0.0,
                "r_d": RD_FIXED,
            }

        engine = DivergenceEngine()
        report = engine.run(params_efc, params_lcdm)
        engine.save_report(report)

        # Log compact summary
        logger.info(f"  Total ΔlogL: {report.total_delta_logL:+.3f}")
        logger.info(f"  Best discriminator: {report.best_probe} at z={report.best_z:.3f}")
        for name, pd in report.probe_divergences.items():
            logger.info(f"    {name}: ΔlogL={pd.delta_logL:+.3f}, "
                         f"max @z={pd.z_of_max_divergence:.2f} ({pd.max_delta_sigma:.2f}σ)")

    def _run_axiom0_test(self, cycle_id: str, baseline):
        """Phase 7: Axiom 0 S_hat(z) regime boundary test.

        Uses locked Madau-Dickinson + Tacconi/PHIBSS sources to build S_hat(z),
        maps BAO residuals to S_hat-space, and runs boundary clustering +
        sign coherence tests. Results are published to Neo4j.

        This is a pre-registered phenomenological test — NOT a model fit.
        Sources are locked; no re-fit or tuning happens here.
        """
        logger.info("\n--- PHASE 7: AXIOM 0 (S_hat regime test) ---")

        # Import axiom0 functions (they live in scripts/axiom0/)
        import sys as _sys
        _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        _axiom0_dir = os.path.join(_repo_root, 'scripts', 'axiom0')
        if _axiom0_dir not in _sys.path:
            _sys.path.insert(0, _axiom0_dir)

        from axiom0_s_hat import (
            compute_c0_zero_at_z0, s_hat, compute_regime_boundaries_from_grid,
            regime_label, distance_to_nearest_boundary, nearest_boundary_label,
            permutation_test_mean_distance, sign_coherence_transition_latent,
            BaoPoint, read_bao_csv,
        )

        # ── Load BAO residuals ──
        # Try to compute live residuals from the current MCMC posterior.
        # Fall back to locked CSV if posterior not available.
        bao_csv = os.path.join(_axiom0_dir, 'bao_points.csv')
        if not os.path.exists(bao_csv):
            logger.warning(f"  BAO CSV not found at {bao_csv} — skipping Axiom 0")
            return

        points = read_bao_csv(bao_csv)
        logger.info(f"  Loaded {len(points)} BAO points from {bao_csv}")

        # ── Compute S_hat ──
        c0 = compute_c0_zero_at_z0()
        zmin, zmax, ngrid = 0.0, 1.5, 10000
        zgrid = np.linspace(zmin, zmax, ngrid, dtype=float)

        bounds = compute_regime_boundaries_from_grid(
            zmin=zmin, zmax=zmax, ngrid=ngrid,
            quantiles=(1/3, 2/3), c0=c0,
        )
        logger.info(f"  Boundaries: FLOW/TRANS={bounds.s_flow_trans:.3f}  "
                     f"TRANS/LAT={bounds.s_trans_latent:.3f}")

        zs = np.array([p.z for p in points], dtype=float)
        svals = s_hat(zs, c0=c0)

        # ── Primary: randomisation test (v1.1: randomise z, not S_hat) ──
        perm = permutation_test_mean_distance(
            points=points, s_at_points=svals, boundaries=bounds,
            nperm=50000, seed=1337,  # 50k for daemon speed (200k for standalone)
            z_range=(zmin, zmax), c0=c0,
        )
        logger.info(f"  Primary p: {perm['p_value']:.4f} "
                     f"(obs={perm['t_obs']:.3f}, null_med={perm['null_median']:.3f}, "
                     f"method={perm.get('method', 'unknown')})")

        # ── Secondary: sign coherence ──
        sign = sign_coherence_transition_latent(points, svals, bounds)
        n_sign = int(sign["n"])
        k_sign = int(sign["npos"])

        from math import comb as _comb
        if n_sign > 0:
            p_binom = sum(_comb(n_sign, i) * 0.5**n_sign
                          for i in range(k_sign, n_sign + 1))
        else:
            p_binom = float("nan")

        logger.info(f"  Secondary: sign {k_sign}/{n_sign} = {sign['frac_pos']:.3f} "
                     f"(binomial p={p_binom:.4f})")

        # ── Raw metrics (for downstream correlation analysis) ──
        distances = [distance_to_nearest_boundary(float(sv), bounds)
                     for sv in svals]
        mean_boundary_distance = float(np.mean(distances))
        min_boundary_distance = float(np.min(distances))
        n_transition_latent = n_sign  # already computed above

        # ── Boundary-proximate points (with boundary label) ──
        boundary_hits = []
        boundary_hits_json = []
        for p, sv, d in zip(points, svals, distances):
            blabel = nearest_boundary_label(float(sv), bounds)
            if d < 0.05:
                boundary_hits.append(f"{p.name}(z={p.z},d={d:.3f},{blabel})")
                boundary_hits_json.append({
                    "name": p.name, "z": p.z, "dist": round(d, 6),
                    "boundary": blabel, "s_hat": round(float(sv), 6),
                })
        if boundary_hits:
            logger.info(f"  Boundary-proximate: {', '.join(boundary_hits)}")

        # ── Degeneracy detection ──
        # v1.1: With z-randomisation, degeneracy only occurs if null_std ≈ 0
        null_std = perm.get("null_std", 0.0)
        primary_is_degenerate = (
            abs(perm["t_obs"] - perm["null_median"]) < 1e-6
            and null_std < 1e-6
        )

        # ── Min-distance boundary label (argmin) ──
        min_idx = int(np.argmin(distances))
        min_boundary_label = nearest_boundary_label(float(svals[min_idx]), bounds)

        # ── Degeneracy reason (for v2 prereg protection) ──
        primary_degeneracy_reason = (
            "null distribution collapsed (std < 1e-6); likely structural degeneracy"
            if primary_is_degenerate else ""
        )

        logger.info(f"  Raw: mean_dist={mean_boundary_distance:.4f}, "
                     f"min_dist={min_boundary_distance:.4f} ({min_boundary_label}), "
                     f"n_trans_lat={n_transition_latent}, "
                     f"degenerate={primary_is_degenerate}")

        # ── Publish to Neo4j ──
        try:
            driver = self.publisher._get_driver()
            if driver:
                per_point_json = json.dumps([
                    {
                        "name": p.name, "z": p.z, "sigma_dev": p.sigma_dev,
                        "s_hat": round(float(sv), 6),
                        "regime": regime_label(float(sv), bounds),
                        "dist": round(distance_to_nearest_boundary(float(sv), bounds), 6),
                    }
                    for p, sv in zip(points, svals)
                ])

                # Extract alpha from baseline for cycle context
                alpha_mean = float(baseline.alpha.mean) if baseline and hasattr(baseline, 'alpha') else None
                alpha_std = float(baseline.alpha.std) if baseline and hasattr(baseline, 'alpha') else None

                cypher = """
                MERGE (a:Axiom0TestResult {cycle_id: $cycle_id, test_version: 'v2.0'})
                SET a.timestamp = datetime(),
                    a.n_points = $n_points,
                    a.s_flow_trans = $s_flow_trans,
                    a.s_trans_latent = $s_trans_latent,
                    a.primary_p_value = $primary_p,
                    a.primary_t_obs = $t_obs,
                    a.primary_null_median = $null_median,
                    a.primary_null_std = $null_std,
                    a.primary_nperm = $nperm,
                    a.secondary_n = $sign_n,
                    a.secondary_npos = $sign_npos,
                    a.secondary_frac_pos = $sign_frac,
                    a.secondary_p_binomial = $p_binom,
                    a.mean_boundary_distance = $mean_dist,
                    a.min_boundary_distance = $min_dist,
                    a.n_transition_latent = $n_trans_lat,
                    a.boundary_hits = $boundary_hits,
                    a.boundary_hits_json = $boundary_hits_json,
                    a.primary_is_degenerate = $primary_is_degenerate,
                    a.primary_degeneracy_reason = $primary_degeneracy_reason,
                    a.primary_method = $primary_method,
                    a.min_boundary_distance_label = $min_boundary_label,
                    a.points_json = $points_json,
                    a.sources_locked = 'Madau-Dickinson + Tacconi/PHIBSS Table3b beta=2',
                    a.c0 = $c0,
                    a.alpha_mean = $alpha_mean,
                    a.alpha_std = $alpha_std,
                    a.source = 'research_daemon'
                WITH a
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MERGE (rc)-[:HAS_AXIOM0_TEST]->(a)
                WITH a
                MERGE (v:EFCValidation {test_id: 'axiom0_s_hat_v1'})
                ON CREATE SET v.name = 'Axiom 0: S_hat(z) Regime Boundary Test',
                              v.description = 'Pre-registered phenomenological test: BAO anomalies cluster at EFC regime boundaries in S_hat(z) = log10(rho_SFR) + log10(f_gas) + C0. Sources locked (Madau-Dickinson + Tacconi/PHIBSS Table 3b beta=2). Regime boundaries from uniform z-grid quantiles. Primary null: uniform random z. v2.0: fixed Tacconi f_gas formula (prior versions had sign error).',
                              v.prediction = 'BAO sigma-deviations cluster near S_flow/S_trans and S_trans/S_latent boundaries',
                              v.vl_category = 'phenomenological',
                              v.vl_public = true,
                              v.data_source = 'BAO surveys (6dF, MGS, BOSS, eBOSS, DESI)',
                              v.created = datetime()
                SET v.status = CASE
                    WHEN $primary_is_degenerate THEN 'pending'
                    WHEN $primary_p < 0.05 THEN 'success'
                    WHEN $primary_p < 0.20 THEN 'partial'
                    ELSE 'pending'
                    END,
                    v.result = CASE
                        WHEN $primary_is_degenerate THEN 'DEGENERATE_N' + toString($n_points)
                        WHEN $primary_p < 0.05 THEN 'SIGNIFICANT'
                        WHEN $primary_p < 0.20 THEN 'MARGINAL'
                        ELSE 'NO_SIGNAL'
                        END,
                    v.quantitative_result = 'p_primary=' + toString($primary_p) + ' p_binom=' + toString($p_binom) + ' n=' + toString($n_points) + ' method=' + $primary_method,
                    v.last_synced = datetime(),
                    v.notes = 'Auto-updated by research_daemon Phase 7. test_version=v2.0 method=' + $primary_method
                        END
                WITH a, v
                MERGE (a)-[:VALIDATES]->(v)
                """
                with driver.session() as session:
                    session.run(cypher, {
                        "cycle_id": cycle_id,
                        "n_points": len(points),
                        "s_flow_trans": bounds.s_flow_trans,
                        "s_trans_latent": bounds.s_trans_latent,
                        "primary_p": perm["p_value"],
                        "t_obs": perm["t_obs"],
                        "null_median": perm["null_median"],
                        "nperm": int(perm["nperm"]),
                        "sign_n": n_sign,
                        "sign_npos": k_sign,
                        "sign_frac": sign["frac_pos"],
                        "p_binom": p_binom,
                        "mean_dist": mean_boundary_distance,
                        "min_dist": min_boundary_distance,
                        "n_trans_lat": n_transition_latent,
                        "boundary_hits": ", ".join(boundary_hits) if boundary_hits else "",
                        "boundary_hits_json": json.dumps(boundary_hits_json) if boundary_hits_json else "[]",
                        "primary_is_degenerate": primary_is_degenerate,
                        "primary_degeneracy_reason": primary_degeneracy_reason,
                        "primary_method": perm.get("method", "randomise_z_uniform"),
                        "null_std": perm.get("null_std", 0.0),
                        "min_boundary_label": min_boundary_label,
                        "points_json": per_point_json,
                        "c0": c0,
                        "alpha_mean": alpha_mean,
                        "alpha_std": alpha_std,
                    })
                logger.info(f"  Published Axiom0TestResult → Neo4j (cycle={cycle_id})")
                logger.info(f"  Linked to EFCValidation test_id=axiom0_s_hat_v1")
        except Exception as e:
            logger.warning(f"  Neo4j publish failed: {type(e).__name__}: {e}")

        logger.info("  Phase 7 complete")

    def _run_variant_g_diagnostic(self, cycle_id: str, scenario: str = "G10"):
        """Phase 8: VariantG constitutive law growth diagnostic.

        Tests whether entropy-gradient-driven mu(z) improves growth likelihood.
        Zero extra free parameters vs LCDM — both 3-param [Om, H0, s8].
        The ONLY difference is growth_source: mu(z) from chi vs mu=1.

        Three pre-registered instrument scenarios:
            G10: k_eff=0.10  (nulltest, expect UNDETECTABLE)
            G02: k_eff=0.02  (plausible, ~1.4% mu_amp)
            G01: k_eff=0.01  (strong, ~5.5% mu_amp)

        Publishes VariantGResult node to Neo4j with ΔlogL_growth,
        mu_diagnostics, and deterministic verdict.
        """
        from .research_mcmc import run_variant_g_diagnostic

        logger.info(f"\n--- PHASE 8: VARIANT-G scenario={scenario} ---")

        result = run_variant_g_diagnostic(
            modules={},  # ignored, rebuilt internally with correct cosmology
            nwalkers=48,
            nsteps=4000,
            burnin=1500,
            seed=42,
            scenario=scenario,
        )

        logger.info(f"  VariantG {scenario} verdict: {result['verdict']}")
        logger.info(f"  ΔlogL_growth: {result['dll_growth']:+.4f}")
        logger.info(f"  mu_amp: {result.get('mu_amp', 0):.6f}")
        logger.info(f"  σ8 shift: {result['s8_shift']:+.4f}")

        # ── Publish to Neo4j ──
        try:
            driver = self.publisher._get_driver()
            if driver:
                mu_diag = result.get("mu_diagnostics", {})
                frozen = result.get("frozen_params", {})
                dll_probes = result.get("dll_per_probe", {})

                # MERGE key: {cycle_id, scenario} — separate node per scenario
                cypher = """
                MERGE (vg:VariantGResult {cycle_id: $cycle_id, scenario: $scenario})
                SET vg.timestamp = datetime(),
                    vg.verdict = $verdict,
                    vg.dll_growth = $dll_growth,
                    vg.dll_total = $dll_total,
                    vg.dll_bao = $dll_bao,
                    vg.dll_hz = $dll_hz,
                    vg.dll_snia = $dll_snia,
                    vg.daic_same_k = $daic_same_k,
                    vg.s8_vg_mean = $s8_vg_mean,
                    vg.s8_vg_std = $s8_vg_std,
                    vg.s8_lcdm_mean = $s8_lcdm_mean,
                    vg.s8_lcdm_std = $s8_lcdm_std,
                    vg.s8_shift = $s8_shift,
                    vg.om_vg_mean = $om_vg_mean,
                    vg.h0_vg_mean = $h0_vg_mean,
                    vg.mu_min = $mu_min,
                    vg.mu_max = $mu_max,
                    vg.mu_z0_3 = $mu_z0_3,
                    vg.mu_z0_5 = $mu_z0_5,
                    vg.mu_z0_7 = $mu_z0_7,
                    vg.mu_z1_0 = $mu_z1_0,
                    vg.mu_z1_5 = $mu_z1_5,
                    vg.mu_z2_3 = $mu_z2_3,
                    vg.chi_c = $chi_c,
                    vg.epsilon_eff = $epsilon_eff,
                    vg.screen_k_eff = $screen_k_eff,
                    vg.C_grav = $C_grav,
                    vg.k_lambda = $k_lambda,
                    vg.k_eff = $k_eff,
                    vg.hill_n = $hill_n,
                    vg.mu_amp = $mu_amp,
                    vg.mu_span = $mu_span,
                    vg.total_time_seconds = $total_time,
                    vg.cosmology_model = 'EFCVariantG',
                    vg.source = 'research_daemon'
                WITH vg
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MERGE (rc)-[:HAS_VARIANT_G]->(vg)
                """
                with driver.session() as session:
                    session.run(cypher, {
                        "cycle_id": cycle_id,
                        "scenario": scenario,
                        "verdict": result["verdict"],
                        "dll_growth": result["dll_growth"],
                        "dll_total": result["dll_total"],
                        "dll_bao": dll_probes.get("bao", 0.0),
                        "dll_hz": dll_probes.get("hz", 0.0),
                        "dll_snia": dll_probes.get("snia", 0.0),
                        "daic_same_k": result.get("daic_same_k", 0.0),
                        "s8_vg_mean": result["s8_vg_mean"],
                        "s8_vg_std": result["s8_vg_std"],
                        "s8_lcdm_mean": result["s8_lcdm_mean"],
                        "s8_lcdm_std": result["s8_lcdm_std"],
                        "s8_shift": result["s8_shift"],
                        "om_vg_mean": result.get("om_vg_mean"),
                        "h0_vg_mean": result.get("h0_vg_mean"),
                        "mu_min": mu_diag.get("mu_min"),
                        "mu_max": mu_diag.get("mu_max"),
                        "mu_z0_3": mu_diag.get("mu_z0.3"),
                        "mu_z0_5": mu_diag.get("mu_z0.5"),
                        "mu_z0_7": mu_diag.get("mu_z0.7"),
                        "mu_z1_0": mu_diag.get("mu_z1.0"),
                        "mu_z1_5": mu_diag.get("mu_z1.5"),
                        "mu_z2_3": mu_diag.get("mu_z2.3"),
                        "chi_c": frozen.get("chi_c"),
                        "epsilon_eff": frozen.get("epsilon_eff"),
                        "screen_k_eff": frozen.get("screen_k_eff"),
                        "C_grav": frozen.get("C", 2.32),
                        "k_lambda": frozen.get("k_lambda", 0.0014),
                        "k_eff": frozen.get("k_eff", 0.1),
                        "hill_n": frozen.get("hill_n", 2),
                        "mu_amp": result.get("mu_amp", 0.0),
                        "mu_span": result.get("mu_span", 0.0),
                        "total_time": result.get("total_time_seconds", 0.0),
                    })
                logger.info(f"  Published VariantGResult {scenario} → Neo4j (cycle={cycle_id})")
        except Exception as e:
            logger.warning(f"  Neo4j publish failed: {type(e).__name__}: {e}")

        logger.info(f"  Phase 8 {scenario} complete")

    def _run_fp_distance(self, cycle_id: str, baseline):
        """Phase 10: Forbidden Pattern distance-to-trigger for 5 EFC-FPs.

        Quantifies how far EFC is from triggering each pre-registered Forbidden
        Pattern in nσ units. Uses per-probe ΔlogL from the current cycle.

        Results published as ForbiddenPatternResult node in Neo4j.
        """
        logger.info("\n--- PHASE 10: FORBIDDEN PATTERN DISTANCE ---")

        import sys as _sys
        _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        _scripts_dir = os.path.join(_repo_root, 'scripts')
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)

        from forbidden_pattern_distance import run_forbidden_pattern_distance

        # Build MCMC data dict from baseline
        alpha = baseline.alpha
        mcmc_data = {
            "alpha_mean": alpha.mean,
            "alpha_std": alpha.std,
            "cycle_id": cycle_id,
            "sampler_type": "emcee",
        }

        # Add per-probe ΔlogL from baseline.probe_likelihoods
        pl = baseline.probe_likelihoods or {}
        probe_map = {"bao": "dll_bao", "growth": "dll_growth",
                     "hz": "dll_hz", "snia": "dll_snia"}
        for probe_key, mcmc_key in probe_map.items():
            if probe_key in pl and "delta_logL" in pl[probe_key]:
                mcmc_data[mcmc_key] = pl[probe_key]["delta_logL"]

        summary = run_forbidden_pattern_distance(mcmc_data)

        logger.info(f"  Overall: {summary.overall_status} (min distance: {summary.min_distance_sigma:.1f}σ)")
        for r in summary.results:
            avail = "" if r.data_available else " [NO DATA]"
            logger.info(f"    {r.fp_id}: {r.distance_sigma:.1f}σ [{r.status}]{avail}")

        # Publish to Neo4j
        try:
            driver = self.publisher._get_driver()
            if driver:
                import json as _json
                fp_results_json = _json.dumps([{
                    "fp_id": r.fp_id, "distance_sigma": r.distance_sigma,
                    "status": r.status, "details": r.details, "data_available": r.data_available,
                } for r in summary.results])

                with driver.session() as session:
                    session.run("""
                        MERGE (fp:ForbiddenPatternResult {cycle_id: $cycle_id})
                        SET fp.timestamp = datetime(),
                            fp.sampler_type = 'emcee',
                            fp.alpha_mean = $alpha_mean,
                            fp.alpha_std = $alpha_std,
                            fp.min_distance_sigma = $min_dist,
                            fp.overall_status = $overall,
                            fp.results_json = $results_json,
                            fp.fp_p1d_distance = $d_p1d,
                            fp.fp_highz_distance = $d_highz,
                            fp.fp_rsd_distance = $d_rsd,
                            fp.fp_bao_distance = $d_bao,
                            fp.fp_4ch_distance = $d_4ch
                        WITH fp
                        MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                        MERGE (rc)-[:HAS_FP_DISTANCE]->(fp)
                    """, {
                        "cycle_id": cycle_id,
                        "alpha_mean": alpha.mean,
                        "alpha_std": alpha.std,
                        "min_dist": summary.min_distance_sigma,
                        "overall": summary.overall_status,
                        "results_json": fp_results_json,
                        "d_p1d": summary.results[0].distance_sigma,
                        "d_highz": summary.results[1].distance_sigma,
                        "d_rsd": summary.results[2].distance_sigma,
                        "d_bao": summary.results[3].distance_sigma,
                        "d_4ch": summary.results[4].distance_sigma,
                    })

                    # Update EFCValidation singleton
                    status = ("failed" if summary.n_triggered > 0
                              else "partial" if summary.n_critical > 0
                              else "success" if summary.min_distance_sigma > 2.0
                              else "pending")
                    session.run("""
                        MERGE (v:EFCValidation {test_id: 'forbidden_pattern_distance'})
                        SET v.title = 'Forbidden Pattern Distance-to-Trigger (5 FP)',
                            v.status = $status,
                            v.vl_category = 'framework_constraint',
                            v.vl_public = true,
                            v.last_updated = datetime(),
                            v.last_cycle_id = $cycle_id,
                            v.min_distance_sigma = $min_dist,
                            v.overall_status = $overall
                    """, {"status": status, "cycle_id": cycle_id,
                          "min_dist": summary.min_distance_sigma, "overall": summary.overall_status})

                logger.info(f"  Published FP distance → Neo4j (cycle={cycle_id})")
        except Exception as e:
            logger.warning(f"  Neo4j publish failed: {type(e).__name__}: {e}")

        logger.info("  Phase 10 complete")

    def _run_parameter_lock(self, cycle_id: str, baseline):
        """Phase 11: Global parameter-lock consistency test.

        Freezes best-fit EFC and LCDM parameters, evaluates each probe
        independently with fixed params, checks for internal consistency.

        Kill condition: degradation > 5 logL/pt on any probe.
        """
        logger.info("\n--- PHASE 11: PARAMETER-LOCK CONSISTENCY ---")

        import sys as _sys
        _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        _scripts_dir = os.path.join(_repo_root, 'scripts')
        if _scripts_dir not in _sys.path:
            _sys.path.insert(0, _scripts_dir)

        from parameter_lock_consistency import run_parameter_lock

        # Build parameter dicts from posterior chains
        chain_efc = baseline.chain_efc
        if chain_efc is None or len(chain_efc) == 0:
            logger.warning("  No EFC chain — skipping parameter-lock")
            return

        params_efc = {
            "Omega_m": float(np.median(chain_efc[:, 0])),
            "H0": float(np.median(chain_efc[:, 1])),
            "sigma8": float(np.median(chain_efc[:, 2])),
            "alpha_cosmo": float(np.median(chain_efc[:, 3])),
            "r_d": RD_FIXED,
        }

        chain_lcdm = baseline.chain_lcdm
        if chain_lcdm is not None and len(chain_lcdm) > 0:
            params_lcdm = {
                "Omega_m": float(np.median(chain_lcdm[:, 0])),
                "H0": float(np.median(chain_lcdm[:, 1])),
                "sigma8": float(np.median(chain_lcdm[:, 2])),
                "alpha_cosmo": 0.0,
                "r_d": RD_FIXED,
            }
        else:
            params_lcdm = dict(params_efc, alpha_cosmo=0.0)

        summary = run_parameter_lock(params_efc, params_lcdm,
                                     cycle_id=cycle_id, sampler_type="emcee")

        logger.info(f"  Verdict: {summary.verdict}")
        logger.info(f"  Details: {summary.verdict_details}")
        for p in summary.probes:
            logger.info(f"    {p.probe}: ΔlogL={p.delta_logL:+.3f}, "
                        f"χ²r={p.chi2_red_efc:.2f}, deg/pt={p.degradation_per_pt:.4f} [{p.status}]")

        # Publish to Neo4j
        try:
            driver = self.publisher._get_driver()
            if driver:
                import json as _json
                probes_json = _json.dumps([{
                    "probe": p.probe, "n_data": p.n_data,
                    "logL_efc": p.logL_efc, "logL_lcdm": p.logL_lcdm,
                    "delta_logL": p.delta_logL, "chi2_red_efc": p.chi2_red_efc,
                    "degradation_per_pt": p.degradation_per_pt, "status": p.status,
                } for p in summary.probes])

                with driver.session() as session:
                    session.run("""
                        MERGE (pl:ParamLockResult {cycle_id: $cycle_id})
                        SET pl.timestamp = datetime(),
                            pl.sampler_type = 'emcee',
                            pl.alpha = $alpha,
                            pl.omega_m = $om,
                            pl.h0 = $h0,
                            pl.sigma8 = $s8,
                            pl.total_delta_logL = $total_delta,
                            pl.max_degradation_per_pt = $max_deg,
                            pl.worst_probe = $worst,
                            pl.verdict = $verdict,
                            pl.verdict_details = $details,
                            pl.probes_json = $probes_json,
                            pl.n_pass = $n_pass,
                            pl.n_marginal = $n_marginal,
                            pl.n_fail = $n_fail
                        WITH pl
                        MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                        MERGE (rc)-[:HAS_PARAM_LOCK]->(pl)
                    """, {
                        "cycle_id": cycle_id,
                        "alpha": params_efc["alpha_cosmo"],
                        "om": params_efc["Omega_m"],
                        "h0": params_efc["H0"],
                        "s8": params_efc["sigma8"],
                        "total_delta": summary.total_delta_logL,
                        "max_deg": summary.max_degradation_per_pt,
                        "worst": summary.worst_probe,
                        "verdict": summary.verdict,
                        "details": summary.verdict_details,
                        "probes_json": probes_json,
                        "n_pass": summary.n_pass,
                        "n_marginal": summary.n_marginal,
                        "n_fail": summary.n_fail,
                    })

                    # EFCValidation singleton
                    status = ("failed" if summary.verdict == "INCONSISTENT"
                              else "partial" if summary.verdict == "TENSION"
                              else "success")
                    session.run("""
                        MERGE (v:EFCValidation {test_id: 'global_parameter_lock'})
                        SET v.title = 'Global Parameter-Lock Consistency (4 probes)',
                            v.status = $status,
                            v.vl_category = 'consistency_check',
                            v.vl_public = true,
                            v.last_updated = datetime(),
                            v.last_cycle_id = $cycle_id,
                            v.verdict = $verdict,
                            v.max_degradation = $max_deg
                    """, {"status": status, "cycle_id": cycle_id,
                          "verdict": summary.verdict, "max_deg": summary.max_degradation_per_pt})

                logger.info(f"  Published ParamLockResult → Neo4j (cycle={cycle_id})")
        except Exception as e:
            logger.warning(f"  Neo4j publish failed: {type(e).__name__}: {e}")

        logger.info("  Phase 11 complete")

    def _run_variant_h_diagnostic(self, cycle_id: str):
        """Phase 9: VariantH entropy-gradient growth with 2 free parameters.

        Tests core EFC mechanism: ∇S → μ → fσ₈ with S̄₀ and β₀ as free MCMC params.
        Background: pure LCDM (no alpha). Only growth sector modified.
        5 params [Om, H0, s8, S_bar_0, beta_0] vs LCDM 3 params.
        """
        from .research_mcmc import run_variant_h_diagnostic

        logger.info(f"\n--- PHASE 9: VARIANT-H (entropy-gradient, 2 free params) ---")

        result = run_variant_h_diagnostic(
            modules={},  # ignored, rebuilt internally with correct cosmology
            nwalkers=48,
            nsteps=4000,
            burnin=1500,
            seed=42,
        )

        verdict = result.get("verdict", "UNKNOWN")
        S_bar_0_mean = result.get("S_bar_0_mean", 0.0)
        S_bar_0_std = result.get("S_bar_0_std", 0.0)
        S_bar_0_sigma = result.get("S_bar_0_sigma", 0.0)
        beta_0_mean = result.get("beta_0_mean", 0.0)
        beta_0_std = result.get("beta_0_std", 0.0)
        dll_growth = result.get("dll_growth", 0.0)
        dll_total = result.get("dll_total", 0.0)
        daic = result.get("daic", 0.0)
        dbic = result.get("dbic", 0.0)

        logger.info(f"  VariantH verdict: {verdict}")
        logger.info(f"  S̄₀ = {S_bar_0_mean:.6f} ± {S_bar_0_std:.6f} ({S_bar_0_sigma:.2f}σ)")
        logger.info(f"  β₀ = {beta_0_mean:.4f} ± {beta_0_std:.4f}")
        logger.info(f"  ΔlogL_growth: {dll_growth:+.4f}")
        logger.info(f"  ΔAIC: {daic:+.3f}, ΔBIC: {dbic:+.3f}")

        # Publish to Neo4j via the shared lazy driver (owned by ResearchPublisher —
        # do not close it here; publish_cycle reuses it later in the same run)
        try:
            driver = self.publisher._get_driver()
            if driver is None:
                raise RuntimeError("Neo4j driver unavailable")
            cypher = """
            MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
            MERGE (vh:VariantHResult {cycle_id: $cycle_id})
            ON CREATE SET
                vh.created_at = datetime(),
                vh.verdict = $verdict,
                vh.S_bar_0_mean = $S_bar_0_mean,
                vh.S_bar_0_std = $S_bar_0_std,
                vh.S_bar_0_sigma = $S_bar_0_sigma,
                vh.beta_0_mean = $beta_0_mean,
                vh.beta_0_std = $beta_0_std,
                vh.dll_growth = $dll_growth,
                vh.dll_total = $dll_total,
                vh.daic = $daic,
                vh.dbic = $dbic,
                vh.s8_vh_mean = $s8_vh_mean,
                vh.s8_vh_std = $s8_vh_std,
                vh.s8_shift = $s8_shift,
                vh.total_time = $total_time
            MERGE (rc)-[:HAS_VARIANT_H]->(vh)
            """
            with driver.session() as session:
                session.run(cypher, {
                    "cycle_id": cycle_id,
                    "verdict": verdict,
                    "S_bar_0_mean": S_bar_0_mean,
                    "S_bar_0_std": S_bar_0_std,
                    "S_bar_0_sigma": S_bar_0_sigma,
                    "beta_0_mean": beta_0_mean,
                    "beta_0_std": beta_0_std,
                    "dll_growth": dll_growth,
                    "dll_total": dll_total,
                    "daic": daic,
                    "dbic": dbic,
                    "s8_vh_mean": result.get("s8_vh_mean", 0.0),
                    "s8_vh_std": result.get("s8_vh_std", 0.0),
                    "s8_shift": result.get("s8_shift", 0.0),
                    "total_time": result.get("total_time_seconds", 0.0),
                })
            logger.info(f"  Published VariantHResult → Neo4j (cycle={cycle_id})")
        except Exception as e:
            logger.warning(f"  Neo4j publish failed: {type(e).__name__}: {e}")

        logger.info(f"  Phase 9 complete")

    def _compute_combined_hash(self, data_hashes: dict) -> str:
        """Compute combined hash from individual data file hashes."""
        combined = "|".join(f"{k}={v}" for k, v in sorted(data_hashes.items()))
        return hashlib.sha256(combined.encode()).hexdigest()

    def _run_ppc(self, baseline, modules: dict) -> dict:
        """Run PPC on all loaded modules using the posterior chain.

        Returns combined result with per-module reports and overall verdict.
        """
        from ..core.ppc import ppc_report, ppc_verdict

        chain = baseline.chain_efc  # shape: (n_samples, 4)
        median_params = {
            "Omega_m": float(np.median(chain[:, 0])),
            "H0": float(np.median(chain[:, 1])),
            "sigma8": float(np.median(chain[:, 2])),
            "alpha_cosmo": float(np.median(chain[:, 3])),
            "r_d": RD_FIXED,
        }

        n_samples = self.policy.ppc_gate.n_posterior_samples
        results = {}

        for name, mod in modules.items():
            if mod is None:
                continue
            report = ppc_report(
                mod, median_params,
                posterior_samples=chain,
                n_ppc_samples=n_samples,
            )
            verdict = ppc_verdict(report, self.policy.ppc_gate)
            results[name] = {"report": report, "verdict": verdict}

        # Overall: all modules must pass
        overall_pass = all(r["verdict"]["passed"] for r in results.values())
        failures = [
            f"{name}: {r['verdict']['reason']}"
            for name, r in results.items()
            if not r["verdict"]["passed"]
        ]

        return {
            "passed": overall_pass,
            "modules": results,
            "reason": "ALL_PASSED" if overall_pass else "; ".join(failures),
        }

    def _compute_verdict(self, baseline, diagnostics: dict) -> str:
        """100% deterministic verdict — NO LLM."""
        n1_pass = diagnostics.get("n1", {}).get("verdict") == "PASS"
        n2_pass = diagnostics.get("n2", {}).get("verdict") == "PASS"
        t7_pass = diagnostics.get("t7", {}).get("verdict") == "PASS"
        t7_ran = "t7" in diagnostics

        any_collapsed = any(
            d.get("verdict") == "COLLAPSED"
            for d in diagnostics.values()
        )
        baseline_below_collapse = (
            baseline.alpha.significance < self.policy.inference_gates.degeneracy.collapse_sigma
        )

        if any_collapsed or baseline_below_collapse:
            return "DEGENERACY_LIMITED"
        elif n1_pass and n2_pass and t7_pass:
            return "ROBUST"
        elif n1_pass and n2_pass and not t7_ran:
            return "ROBUST_PENDING"
        elif n1_pass or n2_pass:
            return "PARTIAL"
        else:
            return "MARGINAL"

    def _notify_mattermost_emcee(self, cycle_id, baseline, diagnostics, verdict, total_time):
        """Post emcee cycle result to Mattermost #mcmc-emcee channel."""
        try:
            from tools.shared.mattermost_notify import post_research_result
            fields = {
                "α": f"{baseline.alpha.mean:.3f} ± {baseline.alpha.std:.3f}",
                "Significance": f"{baseline.alpha.significance:.2f}σ",
                "ΔAIC": f"{baseline.daic:+.2f}" if hasattr(baseline, 'daic') else "?",
                "n_eff": str(int(baseline.n_eff)) if hasattr(baseline, 'n_eff') else "?",
                "Wall time": f"{total_time:.0f}s",
            }
            # Add diagnostic summaries
            for key in ["n1_verdict", "n2_verdict", "t7_verdict"]:
                if key in diagnostics:
                    label = key.replace("_verdict", "").upper()
                    fields[label] = diagnostics[key]
            # Build diagnostic summary for narrator
            diag_summary = {}
            for key in ["n1_verdict", "n2_verdict", "t7_verdict"]:
                if key in diagnostics:
                    diag_summary[key.replace("_verdict", "").upper()] = diagnostics[key]

            post_research_result("mcmc-emcee", {
                "title": f"Emcee Cycle: {cycle_id[:20]}",
                "fields": fields,
                "verdict": verdict,
                "icon": ":chart_with_upwards_trend:",
                "username": "Emcee Research Daemon",
            })

            # LLM narrative interpretation
            try:
                from tools.shared.research_narrator import narrate_mcmc
                from tools.shared.mattermost_notify import post_to_channel
                narrative = narrate_mcmc(
                    alpha=baseline.alpha.mean,
                    alpha_std=baseline.alpha.std,
                    daic=baseline.daic if hasattr(baseline, 'daic') else 0,
                    significance=baseline.alpha.significance,
                    diagnostics=diag_summary,
                    sampler="emcee",
                    cycle_id=cycle_id,
                    n_eff=baseline.n_eff if hasattr(baseline, 'n_eff') else None,
                )
                if narrative:
                    post_to_channel("mcmc-emcee", narrative,
                                    username="Research Narrator", icon_emoji=":brain:")
            except Exception:
                pass  # Narrator is best-effort
        except Exception as e:
            logger.debug(f"Mattermost notify failed: {e}")

    def _publish_result(
        self,
        cycle_id: str,
        timestamp: str,
        baseline,
        diagnostics: dict,
        verdict: str,
        narrative: str,
        total_time: float,
    ):
        """Publish to Neo4j: ResearchCycleResult + DiagnosticResult nodes."""
        from efc_inference.runs.schema_contract import (
            SCHEMA_VERSION, compute_dataset_hash, compute_assumptions_hash,
            get_code_commit,
        )

        artifact_path = os.path.join(self.output_dir, cycle_id)
        cosmology_model = self.cosmology.name
        assumptions_json = json.dumps(self.assumptions_audit, default=str)

        # Schema contract fields
        code_commit = get_code_commit(
            os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        )
        dataset_hash = compute_dataset_hash(data_dict={
            "n_data": getattr(self, '_n_data', 70),
        })
        # Use data hashes from hygiene gate if available
        if hasattr(self, '_data_hashes') and self._data_hashes:
            dataset_hash = hashlib.sha256(
                json.dumps(self._data_hashes, sort_keys=True).encode()
            ).hexdigest()[:16]
        assumptions_hash = compute_assumptions_hash(
            assumptions_dict=self.assumptions_audit
        )

        # Shared schema fields
        schema_fields = {
            "schema_version": SCHEMA_VERSION,
            "code_commit": code_commit,
            "dataset_hash": dataset_hash,
            "assumptions_hash": assumptions_hash,
        }

        # Handle case where baseline is None (e.g., DATA_SUSPECT)
        if baseline is None:
            self.publisher.publish_cycle({
                **schema_fields,
                "cycle_id": cycle_id,
                "timestamp": timestamp,
                "cosmology_model": cosmology_model,
                "verdict": verdict,
                "verdict_reasoning": narrative[:2000],
                "alpha_mean": 0.0,
                "alpha_std": 0.0,
                "alpha_significance": 0.0,
                "p_alpha_negative": 0.0,
                "daic": 0.0,
                "dbic": 0.0,
                "om_mean": 0.0, "om_std": 0.0,
                "h0_mean": 0.0, "h0_std": 0.0,
                "s8_mean": 0.0, "s8_std": 0.0,
                "n_data": getattr(self, '_n_data', 70),
                "signal_detected": False,
                "convergence_pass": False,
                "n_eff_min": 0.0,
                "r_hat_max": 0.0,
                "diagnostics_triggered": [],
                "total_mcmc_time": total_time,
                "artifact_path": artifact_path,
                "manifest_json": "{}",
                "assumptions_json": assumptions_json,
                "sampler_type": self.sampler,
                "n6_verdict": None,
                "n6_safety_level": None,
                "n6_delta_rd_pct": None,
                "n6_safety_pass": None,
                "d2_verdict": None,
                "d2_alpha_sig": None,
                "d2_delta_alpha_sig": None,
                "d2_rd_mean": None,
                "d2_rd_std": None,
                # Per-probe ΔlogL (unavailable for failed cycles)
                "dll_bao": None,
                "dll_growth": None,
                "dll_hz": None,
                "dll_snia": None,
                "bao_source": os.path.basename(BAO_PATH),
                "diagnostics_forced": self.policy.inference_gates.force_diagnostics,
                "diagnostics_reason": self.policy.inference_gates.force_diagnostics_reason,
            })
            self.publisher.link_previous_cycle(cycle_id)
            return

        # Cycle node
        triggered = list(diagnostics.keys())
        mc = self.policy.inference_gates.model_comparison
        # Extract diagnostics from manifest
        n_eff_min = baseline.manifest.get("n_eff_min", 0.0)
        r_hat_max = baseline.manifest.get("r_hat_max", 0.0)
        # Handle NaN values (convert to 0.0 for Neo4j)
        if isinstance(n_eff_min, float) and np.isnan(n_eff_min):
            n_eff_min = 0.0
        if isinstance(r_hat_max, float) and np.isnan(r_hat_max):
            r_hat_max = 0.0

        # Extract full posterior stats from BaselineResult dataclass
        om_mean = baseline.om.mean if hasattr(baseline, 'om') else 0.0
        om_std = baseline.om.std if hasattr(baseline, 'om') else 0.0
        h0_mean = baseline.h0.mean if hasattr(baseline, 'h0') else 0.0
        h0_std = baseline.h0.std if hasattr(baseline, 'h0') else 0.0
        s8_mean = baseline.s8.mean if hasattr(baseline, 's8') else 0.0
        s8_std = baseline.s8.std if hasattr(baseline, 's8') else 0.0
        p_neg = baseline.alpha.p_negative if hasattr(baseline.alpha, 'p_negative') else 0.0
        convergence = baseline.manifest.get("convergence_pass", True)
        n_data = baseline.manifest.get("n_total", getattr(self, '_n_data', 70))

        self.publisher.publish_cycle({
            **schema_fields,
            "cycle_id": cycle_id,
            "timestamp": timestamp,
            "cosmology_model": cosmology_model,
            "verdict": verdict,
            "verdict_reasoning": narrative[:2000],
            "alpha_mean": baseline.alpha.mean,
            "alpha_std": baseline.alpha.std,
            "alpha_significance": baseline.alpha.significance,
            "p_alpha_negative": p_neg,
            "daic": baseline.comparison.daic,
            "dbic": baseline.comparison.dbic,
            "om_mean": om_mean,
            "om_std": om_std,
            "h0_mean": h0_mean,
            "h0_std": h0_std,
            "s8_mean": s8_mean,
            "s8_std": s8_std,
            "n_data": n_data,
            "signal_detected": baseline.alpha.significance >= mc.hint.alpha_sigma_min,
            "convergence_pass": convergence,
            "n_eff_min": n_eff_min,
            "r_hat_max": r_hat_max,
            "diagnostics_triggered": triggered,
            "total_mcmc_time": total_time,
            "artifact_path": artifact_path,
            "manifest_json": json.dumps(baseline.manifest),
            "assumptions_json": assumptions_json,
            "sampler_type": self.sampler,
            # N6 fields for RC node (so ledger publisher can read them)
            "n6_verdict": diagnostics.get("n6", {}).get("verdict"),
            "n6_safety_level": diagnostics.get("n6", {}).get("safety_level"),
            "n6_delta_rd_pct": diagnostics.get("n6", {}).get("delta_rd_pct_mean"),
            "n6_safety_pass": diagnostics.get("n6", {}).get("safety_pass"),
            # D2 self-consistent sound horizon
            "d2_verdict": diagnostics.get("d2", {}).get("verdict"),
            "d2_alpha_sig": diagnostics.get("d2", {}).get("alpha_sig"),
            "d2_delta_alpha_sig": diagnostics.get("d2", {}).get("delta_alpha_sig"),
            "d2_rd_mean": diagnostics.get("d2", {}).get("rd_posterior_mean"),
            "d2_rd_std": diagnostics.get("d2", {}).get("rd_posterior_std"),
            # Per-probe ΔlogL (for sector-separation analysis)
            "dll_bao": baseline.probe_likelihoods.get("bao", {}).get("delta_logL") if baseline.probe_likelihoods else None,
            "dll_growth": baseline.probe_likelihoods.get("growth", {}).get("delta_logL") if baseline.probe_likelihoods else None,
            "dll_hz": baseline.probe_likelihoods.get("hz", {}).get("delta_logL") if baseline.probe_likelihoods else None,
            "dll_snia": baseline.probe_likelihoods.get("snia", {}).get("delta_logL") if baseline.probe_likelihoods else None,
            "bao_source": os.path.basename(BAO_PATH),
            "diagnostics_forced": self.policy.inference_gates.force_diagnostics,
            "diagnostics_reason": self.policy.inference_gates.force_diagnostics_reason,
        })

        # Diagnostic nodes
        for test_type, result in diagnostics.items():
            if result is None:
                continue
            diag_id = f"dr_{test_type}_{cycle_id}"
            ts = datetime.now(timezone.utc).isoformat()

            if test_type == "n1":
                sigs = [
                    result["n1a"]["alpha"].significance,
                    result["n1b"]["alpha"].significance,
                ]
            elif test_type == "n2":
                sigs = [
                    v["alpha"].significance
                    for v in result["variants"].values()
                ]
            elif test_type == "t7":
                sigs = [
                    r["alpha"].significance
                    for r in result["loo_results"]
                ]
            elif test_type == "n5":
                sigs = [
                    sr["alpha"].significance
                    for sr in result.get("sweep_results", [])
                    if hasattr(sr.get("alpha"), "significance")
                ]
                if not sigs:
                    sigs = [0.0]
            elif test_type == "ppc":
                # PPC: no alpha significances — use chi2_red values
                sigs = [0.0]
            else:
                sigs = [0.0]

            details = self._serialize_diagnostic(test_type, result)

            # PPC verdict is at result["passed"], not result["verdict"]
            if test_type == "ppc":
                diag_verdict = "PASS" if result.get("passed") else "FAIL"
            else:
                diag_verdict = result.get("verdict", "UNKNOWN")

            self.publisher.publish_diagnostic(
                {
                    "diagnostic_id": diag_id,
                    "test_type": test_type,
                    "cycle_id": cycle_id,
                    "timestamp": ts,
                    "verdict": diag_verdict,
                    "alpha_significance_best": max(sigs) if sigs else 0.0,
                    "alpha_significance_worst": min(sigs) if sigs else 0.0,
                    "details_json": json.dumps(details, default=str),
                    "artifact_path": os.path.join(artifact_path, test_type),
                },
                cycle_id=cycle_id,
            )

        # Publish EFCValidation nodes for each diagnostic + baseline
        self._publish_efc_validations(cycle_id, baseline, diagnostics, verdict)

        # Link to previous cycle
        self.publisher.link_previous_cycle(cycle_id)

    def _publish_data_suspect(self, cycle_id: str, hygiene_result):
        """Publish a DataSuspect alert when hygiene fails."""
        driver = self.publisher._get_driver()
        if driver is None:
            return

        try:
            now = datetime.now(timezone.utc).isoformat()
            with driver.session() as session:
                session.run("""
                    CREATE (ds:MaintenanceAlert {
                        alert_type: 'data_suspect',
                        cycle_id: $cycle_id,
                        severity: 'critical',
                        message: $message,
                        details_json: $details_json,
                        timestamp: datetime($now),
                        source: 'research_daemon'
                    })
                """,
                    cycle_id=cycle_id,
                    message=f"Data hygiene failed: {hygiene_result.failures}",
                    details_json=json.dumps(hygiene_result.to_dict()),
                    now=now,
                )
        except Exception as e:
            logger.error(f"Failed to publish DataSuspect: {e}")

    def _publish_efc_validations(self, cycle_id: str, baseline, diagnostics: dict, verdict: str):
        """Publish EFCValidation nodes so diagnostics appear in the Living Validation Ledger.

        MERGEs on {name} — idempotent. Each daemon cycle updates the same node
        with latest results (same pattern as grav_publisher).
        """
        driver = self.publisher._get_driver()
        if driver is None:
            return

        status_map = {
            "PASS": "success",
            "COLLAPSED": "failed",
            "MARGINAL": "partial",
            "ROBUST": "success",
            "PARTIAL": "partial",
            "FAIL": "failed",
            "ERROR": "failed",
        }

        def _merge_validation(session, name: str, description: str, prediction: str,
                              data_source: str, status: str, quantitative: str,
                              category: str = "consistency_check"):
            # 1. MERGE the public-facing node (one per test, idempotent)
            session.run("""
                MERGE (v:EFCValidation {name: $name})
                SET v.description = $desc,
                    v.prediction = $pred,
                    v.data_source = $ds,
                    v.status = $status,
                    v.quantitative_result = $qr,
                    v.vl_category = $cat,
                    v.vl_public = true,
                    v.pipeline = 'EFC-Native',
                    v.cycle_id = $cid,
                    v.last_updated = datetime()
            """, name=name, desc=description, pred=prediction,
                 ds=data_source, status=status, qr=quantitative,
                 cat=category, cid=cycle_id)

            # 2. CREATE run-history node (provenance / drift tracking)
            session.run("""
                MATCH (v:EFCValidation {name: $name})
                CREATE (r:EFCValidationRun {
                    cycle_id: $cid,
                    status: $status,
                    quantitative_result: $qr,
                    pipeline: 'EFC-Native',
                    timestamp: datetime()
                })
                MERGE (v)-[:HAS_RUN]->(r)
                WITH v, r
                OPTIONAL MATCH (v)-[old:LATEST]->()
                DELETE old
                MERGE (v)-[:LATEST]->(r)
            """, name=name, cid=cycle_id, status=status, qr=quantitative)

        try:
            with driver.session() as session:
                # ── Baseline α-signal ──
                alpha = baseline.alpha
                bl_status = status_map.get(verdict, "pending")
                _merge_validation(
                    session,
                    name="EFC Baseline α-signal",
                    description="Joint BAO+H(z)+SNIa+fσ₈ MCMC with EFC α-parameter. Tests whether dark energy data prefers α<0 (entropic flow) over ΛCDM (α=0).",
                    prediction="α < 0 at ≥2σ significance with ΔAIC < -2 (moderate evidence)",
                    data_source=f"emcee MCMC, {baseline.manifest.get('n_total', 70)} data points, {self.sampler} sampler",
                    status=bl_status,
                    quantitative=json.dumps({
                        "alpha_mean": round(alpha.mean, 4),
                        "alpha_std": round(alpha.std, 4),
                        "significance_sigma": round(alpha.significance, 2),
                        "daic": round(baseline.comparison.daic, 2),
                        "dbic": round(baseline.comparison.dbic, 2),
                        "verdict": verdict,
                    }),
                    category="physics_test",
                )

                # ── N1: Sound Horizon Control ──
                n1 = diagnostics.get("n1")
                if n1:
                    n1_status = status_map.get(n1.get("verdict", "UNKNOWN"), "pending")
                    n1a_sig = n1.get("n1a", {}).get("alpha", type('', (), {"significance": 0})()).significance if isinstance(n1.get("n1a", {}).get("alpha"), object) else 0
                    n1b_sig = n1.get("n1b", {}).get("alpha", type('', (), {"significance": 0})()).significance if isinstance(n1.get("n1b", {}).get("alpha"), object) else 0
                    # Safer extraction
                    try:
                        n1a_sig = n1["n1a"]["alpha"].significance
                    except Exception:
                        n1a_sig = 0.0
                    try:
                        n1b_sig = n1["n1b"]["alpha"].significance
                    except Exception:
                        n1b_sig = 0.0

                    _merge_validation(
                        session,
                        name="N1 Sound Horizon Control",
                        description="Tests whether α-signal survives when rd (sound horizon) is (a) fixed to Planck, (b) freed as MCMC parameter. Rules out rd-degeneracy.",
                        prediction="α significance survives within 0.5σ of baseline under both rd treatments",
                        data_source="emcee MCMC, N1a (fixed rd) + N1b (free rd)",
                        status=n1_status,
                        quantitative=json.dumps({
                            "n1a_sigma": round(n1a_sig, 2),
                            "n1b_sigma": round(n1b_sig, 2),
                            "verdict": n1.get("verdict"),
                        }),
                    )

                # ── N2: σ8 Prior Sweep ──
                n2 = diagnostics.get("n2")
                if n2:
                    n2_status = status_map.get(n2.get("verdict", "UNKNOWN"), "pending")
                    variants = n2.get("variants", {})
                    n2_quant = {"verdict": n2.get("verdict")}
                    for mode, v in variants.items():
                        try:
                            n2_quant[f"{mode}_sigma"] = round(v["alpha"].significance, 2)
                        except Exception:
                            pass
                    _merge_validation(
                        session,
                        name="N2 σ8 Prior Sweep",
                        description="Tests α-signal stability across tight/medium/flat σ₈ priors. Rules out prior-driven artifact.",
                        prediction="α significance stable (within 0.5σ) across all σ₈ prior widths",
                        data_source="emcee MCMC, 3 σ₈ prior configurations",
                        status=n2_status,
                        quantitative=json.dumps(n2_quant),
                    )

                # ── N3: Gate Freedom (IDENTIFIABILITY test) ──
                n3 = diagnostics.get("n3")
                if n3:
                    n3_status = status_map.get(n3.get("verdict", "UNKNOWN"), "pending")
                    _merge_validation(
                        session,
                        name="N3 Gate Freedom",
                        description=(
                            "IDENTIFIABILITY test: frees gate parameters (a_t, δ_a) alongside α "
                            "using EFCVariantB (6-param MCMC). Tests whether α is identifiable "
                            "when gate shape has freedom, or collapses into α–gate degeneracy. "
                            "Reports A_eff = α·G (gate-normalized amplitude) for comparison with N7. "
                            "Distinct from N7 (shape-robustness): N3 asks 'can α be extracted?' "
                            "while N7 asks 'does α survive a different gate class?'"
                        ),
                        prediction="α identifiable: no α–a_t degeneracy, A_eff consistent with fixed-gate baseline",
                        data_source="emcee MCMC, EFCVariantB with free gate",
                        status=n3_status,
                        quantitative=json.dumps({
                            "verdict": n3.get("verdict"),
                            "details": "see DiagnosticResult for full sweep + A_eff",
                        }),
                    )

                # ── N4: Modified Poisson μ≠1 ──
                n4 = diagnostics.get("n4")
                if n4:
                    n4_status = status_map.get(n4.get("verdict", "UNKNOWN"), "pending")
                    _merge_validation(
                        session,
                        name="N4 Modified Poisson μ≠1",
                        description="Tests whether EFC growth modification μ(a) = 1 + (μ₀−1)·g(a) is consistent with fσ₈ data. Uses EFCVariantC.",
                        prediction="μ₀ consistent with 1.0; no tension with growth data",
                        data_source="emcee MCMC, EFCVariantC with free μ₀",
                        status=n4_status,
                        quantitative=json.dumps({
                            "verdict": n4.get("verdict"),
                            "details": "see DiagnosticResult for μ₀ posterior",
                        }),
                    )

                # ── N5: Flat rd Prior ──
                n5 = diagnostics.get("n5")
                if n5:
                    n5_status = status_map.get(n5.get("verdict", "UNKNOWN"), "pending")
                    _merge_validation(
                        session,
                        name="N5 Flat rd Prior",
                        description="Tests α-signal with completely flat (uniform) rd prior over [100, 200] Mpc. Ultimate rd-independence check.",
                        prediction="α significance survives flat rd prior",
                        data_source="emcee MCMC, uniform rd prior [100, 200] Mpc",
                        status=n5_status,
                        quantitative=json.dumps({
                            "verdict": n5.get("verdict"),
                            "details": "see DiagnosticResult for rd posterior",
                        }),
                    )

                # ── T7: Leave-One-Out Robustness ──
                t7 = diagnostics.get("t7")
                if t7:
                    t7_status = status_map.get(t7.get("verdict", "UNKNOWN"), "pending")
                    loo_results = t7.get("loo_results", [])
                    sigs = []
                    for r in loo_results:
                        try:
                            sigs.append(round(r["alpha"].significance, 2))
                        except Exception:
                            pass
                    _merge_validation(
                        session,
                        name="T7 Leave-One-Out Robustness",
                        description="Drops each probe (BAO/H(z)/SNIa/fσ₈) one at a time and re-runs MCMC. Tests that no single dataset drives the α-signal.",
                        prediction="α significance survives in ≥6/7 LOO runs (no single-probe dependency)",
                        data_source="emcee MCMC, 7 leave-one-out configurations",
                        status=t7_status,
                        quantitative=json.dumps({
                            "verdict": t7.get("verdict"),
                            "n_pass": t7.get("n_passed", 0),
                            "n_total": t7.get("n_total", 7),
                            "sigma_range": sigs,
                        }),
                    )

                # ── N7: Power-law Gate Shape-Robustness (NUTS only) ──
                # N7 runs only on GPU-PC via gpu_nuts_daemon; here we publish
                # results if the daemon has stored them in this cycle's diagnostics.
                n7 = diagnostics.get("n7")
                if n7:
                    n7_status = status_map.get(n7.get("verdict", "UNKNOWN"), "pending")
                    n7_quant = {
                        "verdict": n7.get("verdict"),
                        "alpha_mean": n7.get("alpha_mean"),
                        "alpha_std": n7.get("alpha_std"),
                        "alpha_sigma": n7.get("alpha_significance"),
                    }
                    # A_eff: gate-normalized amplitude (comparable across gate classes)
                    if "A_eff_mean" in n7:
                        n7_quant["A_eff_mean"] = n7["A_eff_mean"]
                        n7_quant["A_eff_std"] = n7["A_eff_std"]
                        n7_quant["A_eff_sigma"] = n7["A_eff_significance"]
                        n7_quant["gate_mass_powerlaw"] = n7.get("gate_mass_powerlaw")
                        n7_quant["gate_mass_logistic"] = n7.get("gate_mass_logistic")
                        n7_quant["gate_mass_ratio"] = n7.get("gate_mass_ratio")
                    _merge_validation(
                        session,
                        name="N7 Power-law Gate Shape-Robustness",
                        description=(
                            "SHAPE-ROBUSTNESS test: replaces logistic gate with power-law "
                            "gate g(a)=1/(1+(a_t/a)^n), n=2 from L0 Lorentzian derivation "
                            "(Core Derivation Note v0.2, Eq. 6-8). Tests whether α survives "
                            "a different gate CLASS — model-invariance across functional forms. "
                            "Reports both raw α and A_eff=α·G (gate-mass-normalized amplitude) "
                            "for fair cross-gate comparison. Distinct from N3 (identifiability): "
                            "N7 asks 'does α survive a different gate class?' while N3 asks "
                            "'can α be extracted when gate has freedom?'"
                        ),
                        prediction="α survives at ≥1.5σ with power-law gate; A_eff consistent with logistic baseline",
                        data_source="NUTS HMC, EFCVariantE (power-law gate, n=2)",
                        status=n7_status,
                        quantitative=json.dumps(n7_quant),
                        category="consistency_check",
                    )

                n_published = 1 + sum(1 for k in ["n1", "n2", "n3", "n4", "n5", "t7", "n7"] if k in diagnostics)
                logger.info(f"Published {n_published} EFCValidation nodes for ledger (pipeline=EFC-Native)")

        except Exception as e:
            logger.error(f"Failed to publish EFCValidation nodes: {e}")

    def _serialize_diagnostic(self, test_type: str, result: dict) -> dict:
        """Convert diagnostic result to JSON-serializable dict."""
        if test_type == "n1":
            return {
                "n1a": {
                    "alpha": alpha_stats_to_dict(result["n1a"]["alpha"]),
                    "comparison": comparison_to_dict(result["n1a"]["comparison"]),
                    "correlations": result["n1a"]["correlations"],
                },
                "n1b": {
                    "alpha": alpha_stats_to_dict(result["n1b"]["alpha"]),
                    "comparison": comparison_to_dict(result["n1b"]["comparison"]),
                    "correlations": result["n1b"]["correlations"],
                    "rd_mean": result["n1b"]["rd_mean"],
                    "rd_std": result["n1b"]["rd_std"],
                    "rd_ci_width_95": result["n1b"]["rd_ci_width_95"],
                },
                "verdict": result["verdict"],
                "alpha_survives_n1a": result["alpha_survives_n1a"],
                "alpha_survives_n1b": result["alpha_survives_n1b"],
            }
        elif test_type == "n2":
            variants = {}
            for mode, v in result["variants"].items():
                variants[mode] = {
                    "alpha": alpha_stats_to_dict(v["alpha"]),
                    "comparison": comparison_to_dict(v["comparison"]),
                    "correlations": v["correlations"],
                }
            return {
                "variants": variants,
                "verdict": result["verdict"],
                "alpha_survives_stram": result["alpha_survives_stram"],
            }
        elif test_type == "t7":
            loo = []
            for r in result["loo_results"]:
                loo.append({
                    "idx": r["idx"],
                    "z_excluded": r["z_excluded"],
                    "fs8_excluded": r["fs8_excluded"],
                    "alpha": alpha_stats_to_dict(r["alpha"]),
                    "comparison": comparison_to_dict(r["comparison"]),
                    "passed": r["passed"],
                })
            return {
                "loo_results": loo,
                "pass_count": result["pass_count"],
                "n_total": result["n_total"],
                "robustness_score": result["robustness_score"],
                "verdict": result["verdict"],
                "most_influential_idx": result["most_influential_idx"],
                "alpha_range": list(result["alpha_range"]),
            }
        elif test_type == "n3":
            # N3 gate freedom diagnostic
            sweep = {}
            for label, sr in result.get("sweep_results", {}).items():
                sweep[label] = {
                    "a_t": sr["a_t"],
                    "delta_a": sr["delta_a"],
                    "alpha": alpha_stats_to_dict(sr["alpha"]) if "alpha" in sr else sr.get("alpha", {}),
                    "comparison": comparison_to_dict(sr["comparison"]) if "comparison" in sr else {},
                }
            fg = result.get("free_gate", {})
            free_gate_out = {}
            if fg:
                free_gate_out = {
                    "alpha": alpha_stats_to_dict(fg["alpha"]) if "alpha" in fg else fg.get("alpha", {}),
                    "comparison": comparison_to_dict(fg["comparison"]) if "comparison" in fg else {},
                    "a_t_mean": fg.get("a_t_mean", 0),
                    "a_t_std": fg.get("a_t_std", 0),
                    "delta_a_mean": fg.get("delta_a_mean", 0),
                    "delta_a_std": fg.get("delta_a_std", 0),
                    "correlations": fg.get("correlations", {}),
                }
            return {
                "sweep_results": sweep,
                "free_gate": free_gate_out,
                "verdict": result.get("verdict", "UNKNOWN"),
                "sweep_stable": result.get("sweep_stable", False),
                "alpha_survives_freedom": result.get("alpha_survives_freedom", False),
                "high_degeneracy": result.get("high_degeneracy", False),
            }
        elif test_type == "n4":
            # N4 modified Poisson (μ≠1) diagnostic
            sweep = []
            for sr in result.get("sweep_results", []):
                sweep.append({
                    "label": sr.get("label", ""),
                    "mu_0": sr.get("mu_0", 1.0),
                    "alpha_mean": sr.get("alpha_mean", 0),
                    "alpha_std": sr.get("alpha_std", 0),
                    "alpha_sig": sr.get("alpha_sig", 0),
                })
            fm = result.get("free_mu", {})
            free_mu_out = {}
            if fm:
                free_mu_out = {
                    "alpha_mean": fm.get("alpha_mean", 0),
                    "alpha_std": fm.get("alpha_std", 0),
                    "alpha_sig": fm.get("alpha_sig", 0),
                    "alpha_p_negative": fm.get("alpha_p_negative", 0),
                    "mu0_mean": fm.get("mu0_mean", 0),
                    "mu0_std": fm.get("mu0_std", 0),
                    "mu0_deviation_from_gr": fm.get("mu0_deviation_from_gr", 0),
                }
            return {
                "sweep_results": sweep,
                "free_mu": free_mu_out,
                "correlations": result.get("correlations", {}),
                "verdict": result.get("verdict", "UNKNOWN"),
                "sweep_stable": result.get("sweep_stable", False),
                "alpha_survives_freedom": result.get("alpha_survives_freedom", False),
                "high_degeneracy": result.get("high_degeneracy", False),
            }
        elif test_type == "n5":
            # N5 sound horizon prior sweep (D2a)
            sweep = []
            for sr in result.get("sweep_results", []):
                alpha = sr.get("alpha")
                sweep.append({
                    "config": sr.get("config", ""),
                    "rd_prior_mu": sr.get("rd_prior_mu"),
                    "rd_prior_sigma": sr.get("rd_prior_sigma"),
                    "alpha": alpha_stats_to_dict(alpha) if hasattr(alpha, 'mean') else alpha,
                    "rd_mean": sr.get("rd_mean", 0),
                    "rd_std": sr.get("rd_std", 0),
                    "rd_ci_width_95": sr.get("rd_ci_width_95", 0),
                    "corr_alpha_rd": sr.get("corr_alpha_rd", 0),
                    "corr_alpha_om": sr.get("corr_alpha_om", 0),
                })
            return {
                "sweep_results": sweep,
                "verdict": result.get("verdict", "UNKNOWN"),
                "sweep_stable": result.get("sweep_stable", False),
                "max_corr_alpha_rd": result.get("max_corr_alpha_rd", 0),
                "alpha_survives_flat": result.get("alpha_survives_flat", False),
                "high_degeneracy": result.get("high_degeneracy", False),
                "sig_range": result.get("sig_range", 0),
                "total_time_seconds": result.get("total_time_seconds", 0),
            }
        elif test_type == "ppc":
            # PPC result — per-module reports + overall verdict
            modules = {}
            for mod_name, mod_data in result.get("modules", {}).items():
                report = mod_data.get("report", {})
                verdict_data = mod_data.get("verdict", {})
                modules[mod_name] = {
                    "chi2_reduced": report.get("chi2_reduced"),
                    "bayesian_p_value": report.get("bayesian_p_value"),
                    "calibration": report.get("calibration", {}),
                    "residuals": report.get("residuals", {}),
                    "verdict": verdict_data,
                }
            return {
                "passed": result.get("passed", False),
                "reason": result.get("reason", ""),
                "modules": modules,
            }
        return {}

    def _save_artifacts(
        self,
        cycle_id: str,
        baseline,
        diagnostics: dict,
        verdict: str,
        narrative: str,
        hygiene_result=None,
        convergence_result=None,
    ):
        """Save chains, manifest, data hashes, diagnostics, and git commit to disk."""
        cycle_dir = os.path.join(self.output_dir, cycle_id)
        os.makedirs(cycle_dir, exist_ok=True)

        # Manifest (now includes cosmology info)
        manifest = baseline.manifest.copy()
        manifest["verdict"] = verdict
        manifest["diagnostics_triggered"] = list(diagnostics.keys())
        manifest["policy_version"] = self.policy.version
        manifest["cosmology_model"] = self.cosmology.name
        with open(os.path.join(cycle_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

        # Assumptions audit (ontological registry for this cycle)
        assumptions_data = {
            "cosmology_model": self.cosmology.name,
            "model_assumptions": self.cosmology.assumptions,
            "assumptions_audit": self.assumptions_audit,
        }
        with open(os.path.join(cycle_dir, "assumptions.json"), "w") as f:
            json.dump(assumptions_data, f, indent=2)

        # Baseline chains (compressed)
        np.savez_compressed(
            os.path.join(cycle_dir, "baseline_chains.npz"),
            chain_efc=baseline.chain_efc,
            chain_lcdm=baseline.chain_lcdm,
        )

        # Summary JSON (all diagnostics, no chains)
        summary = {
            "cycle_id": cycle_id,
            "verdict": verdict,
            "narrative": narrative,
            "baseline": {
                "alpha": alpha_stats_to_dict(baseline.alpha),
                "comparison": comparison_to_dict(baseline.comparison),
                "correlations": baseline.correlations,
                "om": param_stats_to_dict(baseline.om),
                "s8": param_stats_to_dict(baseline.s8),
                "h0": param_stats_to_dict(baseline.h0),
            },
        }
        for test_type, result in diagnostics.items():
            summary[test_type] = self._serialize_diagnostic(test_type, result)

        with open(os.path.join(cycle_dir, "summary.json"), "w") as f:
            json.dump(summary, f, indent=2)

        # Data hashes (NEW)
        if hygiene_result:
            with open(os.path.join(cycle_dir, "data_hashes.json"), "w") as f:
                json.dump({
                    "hashes": hygiene_result.data_hashes,
                    "checks": hygiene_result.checks,
                    "lcdm_chi2_red": hygiene_result.lcdm_chi2_red,
                }, f, indent=2)

        # Diagnostics JSON (NEW) — convergence + gates
        diag_info = {}
        if convergence_result:
            diag_info["convergence"] = convergence_result
        with open(os.path.join(cycle_dir, "diagnostics.json"), "w") as f:
            json.dump(diag_info, f, indent=2, default=str)

        # PPC results JSON (Fase 2)
        ppc_data = diagnostics.get("ppc")
        if ppc_data:
            # Serialize — strip numpy types
            ppc_serializable = json.loads(json.dumps(ppc_data, default=str))
            with open(os.path.join(cycle_dir, "ppc_results.json"), "w") as f:
                json.dump(ppc_serializable, f, indent=2)

        # Git commit hash (NEW)
        try:
            git_hash = subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
            ).decode().strip()
            with open(os.path.join(cycle_dir, "code_commit.txt"), "w") as f:
                f.write(git_hash)
        except Exception:
            pass

        logger.info(f"  Artifacts saved: {cycle_dir}/")

    # ── Trigger file support (Gap→Runner bridge) ────────────
    def _check_triggers(self) -> list:
        """Check for pending trigger files from gap_runner_bridge."""
        trigger_dir = os.path.join(self.output_dir, "triggers")
        if not os.path.exists(trigger_dir):
            return []

        triggers = []
        for fname in sorted(os.listdir(trigger_dir)):
            if not fname.startswith("trigger_") or not fname.endswith(".json"):
                continue
            path = os.path.join(trigger_dir, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                if data.get("status") == "pending":
                    data["_path"] = path
                    triggers.append(data)
            except Exception as e:
                logger.warning(f"Failed to read trigger {fname}: {e}")
        return triggers

    def _complete_trigger(self, trigger: dict, cycle_id: str, verdict: str):
        """Mark a trigger file as completed with cycle result."""
        path = trigger.get("_path")
        if not path or not os.path.exists(path):
            return
        try:
            with open(path) as f:
                data = json.load(f)
            data["status"] = "completed"
            data["result_cycle_id"] = cycle_id
            data["result_verdict"] = verdict
            data["completed_at"] = datetime.now(timezone.utc).isoformat()
            with open(path, "w") as f:
                json.dump(data, f, indent=2)
            logger.info(f"  Trigger completed: {path} → {verdict}")
        except Exception as e:
            logger.warning(f"Failed to update trigger: {e}")

    def loop(self, interval: int = 21600):
        """Daemon loop: run cycle -> sleep -> repeat.

        Also checks for trigger files from gap_runner_bridge between cycles.
        Triggered runs happen immediately (no wait for next scheduled cycle).
        """
        logger.info(f"Starting daemon loop (interval={interval}s = {interval/3600:.1f}h)")

        while True:
            try:
                lock_path = os.path.join(self.output_dir, "daemon.lock")
                with LockFile(lock_path):
                    # Check for gap-driven triggers
                    triggers = self._check_triggers()
                    if triggers:
                        logger.info(f"Found {len(triggers)} pending trigger(s) from gap_runner_bridge")
                        for trigger in triggers:
                            logger.info(f"  Trigger: {trigger.get('gap_title', 'unknown')}")

                    result = self.run_once()

                    # Mark triggers as completed with this cycle's result
                    if triggers:
                        cycle_id = result.get("cycle_id", "unknown")
                        verdict = result.get("verdict", "UNKNOWN")
                        for trigger in triggers:
                            self._complete_trigger(trigger, cycle_id, verdict)

            except RuntimeError as e:
                logger.warning(f"Skipping cycle: {e}")
            except KeyboardInterrupt:
                logger.info("Daemon stopped by user")
                break
            except Exception:
                logger.exception("Cycle failed unexpectedly")

            logger.info(f"Sleeping {interval}s until next cycle...")
            time.sleep(interval)

    def close(self):
        """Clean up resources."""
        self.publisher.close()


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="EFC Autonomous Research Daemon"
    )
    parser.add_argument(
        "--mode", choices=["once", "daemon"], default="once",
        help="once: single cycle, daemon: loop with interval",
    )
    parser.add_argument(
        "--interval", type=int,
        default=int(os.environ.get("RESEARCH_DAEMON_INTERVAL", "21600")),
        help="Seconds between cycles in daemon mode (default: 21600 = 6h)",
    )
    parser.add_argument(
        "--output-dir", default="outputs/research",
        help="Directory for artifacts (chains, manifests, summaries)",
    )
    parser.add_argument(
        "--policy", default=None,
        help="Path to research_policy.yaml (default: env RESEARCH_POLICY_PATH or auto)",
    )
    parser.add_argument(
        "--nwalkers", type=int,
        default=int(os.environ.get("RESEARCH_NWALKERS", str(DEFAULT_NWALKERS))),
    )
    parser.add_argument(
        "--nsteps", type=int,
        default=int(os.environ.get("RESEARCH_NSTEPS", str(DEFAULT_NSTEPS))),
    )
    parser.add_argument(
        "--burnin", type=int,
        default=int(os.environ.get("RESEARCH_BURNIN", str(DEFAULT_BURNIN))),
    )
    parser.add_argument(
        "--seed", type=int, default=DEFAULT_SEED,
    )
    parser.add_argument(
        "--sampler", default=os.environ.get("RESEARCH_SAMPLER", "emcee"),
        choices=["emcee", "nuts"],
        help="Sampler: emcee (CPU) or nuts (GPU via JAX/numpyro). "
             "Default: env RESEARCH_SAMPLER or emcee.",
    )
    parser.add_argument(
        "--log-level", default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    daemon = EFCResearchDaemon(
        output_dir=args.output_dir,
        nwalkers=args.nwalkers,
        nsteps=args.nsteps,
        burnin=args.burnin,
        seed=args.seed,
        policy_path=args.policy,
        sampler=args.sampler,
    )

    try:
        if args.mode == "once":
            result = daemon.run_once()
            logger.info(f"Final result: {result}")
        else:
            daemon.loop(interval=args.interval)
    finally:
        daemon.close()


if __name__ == "__main__":
    main()
