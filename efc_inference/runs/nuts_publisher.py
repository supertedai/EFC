#!/usr/bin/env python3
"""
NUTS Result Publisher — Picks up JSON from GPU-PC and publishes to Neo4j.

Runs on Mac. Scans GPU-PC outputs/ for new NUTS results, publishes to Neo4j,
and moves processed files to outputs/published/.

Usage:
    python3 efc_inference/runs/nuts_publisher.py --once
    python3 efc_inference/runs/nuts_publisher.py --daemon --interval 300

Architecture:
    GPU-PC (NUTS) → outputs/nuts_*.json → scp → Mac → Neo4j publish
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Ensure efc_inference is importable (publisher runs from repo root)
_repo_root = str(Path(__file__).resolve().parents[2])
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [nuts_publisher] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nuts_publisher")

# ── config ──────────────────────────────────────────────────────────
GPU_HOST     = os.environ.get("GPU_HOST", "user@gpu-host")
GPU_OUTPUTS  = os.environ.get("GPU_OUTPUTS", "/mnt/c/efc_worker/outputs")
LOCAL_STAGING = Path("/tmp/nuts_staging")

NEO4J_URI      = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER     = os.environ.get("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD", "")


def _get_neo4j_driver():
    """Get Neo4j driver."""
    from neo4j import GraphDatabase
    if not NEO4J_PASSWORD:
        # Try reading from env file
        env_path = Path(__file__).resolve().parents[2] / ".env"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("NEO4J_PASSWORD="):
                    pw = line.split("=", 1)[1].strip().strip('"').strip("'")
                    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, pw))
        raise RuntimeError("NEO4J_PASSWORD not set and .env not found")
    return GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def fetch_results() -> list[Path]:
    """Fetch new NUTS result JSONs from GPU-PC via SSH/scp."""
    LOCAL_STAGING.mkdir(parents=True, exist_ok=True)

    # List completed (non-published) results on GPU-PC
    cmd = f"ssh {GPU_HOST} 'wsl -d Ubuntu-24.04 -- bash -c \"ls {GPU_OUTPUTS}/nuts_*.json 2>/dev/null\"'"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
    except (subprocess.TimeoutExpired, Exception) as e:
        logger.warning(f"SSH list failed: {e}")
        return []

    if not files:
        return []

    logger.info(f"Found {len(files)} result files on GPU-PC")

    # Copy each to staging
    local_files = []
    for remote_path in files:
        fname = Path(remote_path).name
        local_path = LOCAL_STAGING / fname

        # Convert WSL path to Windows for scp
        win_path = remote_path.replace("/mnt/c/", "C:/")
        scp_cmd = f"scp {GPU_HOST}:{win_path} {local_path}"
        try:
            subprocess.run(scp_cmd, shell=True, check=True, capture_output=True, timeout=15)
            local_files.append(local_path)
        except Exception as e:
            logger.warning(f"SCP failed for {fname}: {e}")

    return local_files


def _save_chain_artifact(result: dict) -> str:
    """Save posterior chain as .npz artifact. Returns artifact path or empty string."""
    chain_data = result.get("posterior_chain")
    if not chain_data:
        return ""

    import numpy as np
    cycle_id = result.get("cycle_id", "unknown")
    artifact_dir = LOCAL_STAGING / "chain_artifacts"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    chain_arr = np.array(chain_data)
    artifact_path = artifact_dir / f"{cycle_id}_chain.npz"
    np.savez_compressed(
        artifact_path,
        chain=chain_arr,
        columns=result.get("chain_columns", ["Omega_m", "H0", "sigma8", "alpha"]),
    )
    logger.info(f"Chain artifact saved: {artifact_path} ({chain_arr.shape})")
    return str(artifact_path)


def _notify_mattermost_nuts(result: dict, verdict: str, significance: float):
    """Post NUTS result to Mattermost #mcmc-nuts channel."""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        from tools.shared.mattermost_notify import post_research_result
        diag = result.get("diagnostics", {})
        fields = {
            "α": f"{result['alpha_mean']:.3f} ± {result['alpha_std']:.3f}",
            "Significance": f"{significance:.2f}σ",
            "ΔAIC": f"{result.get('daic', 0):+.2f}",
            "n_eff": str(int(result.get("n_eff_min", 0))),
            "r̂": f"{result.get('r_hat_max', 0):.4f}",
        }
        if diag and "error" not in diag:
            fields["N1"] = diag.get("n1_verdict", "?")
            fields["T7"] = f"{diag.get('t7_pass_count', '?')}/{diag.get('t7_n_total', '?')}"
        post_research_result("mcmc-nuts", {
            "title": f"NUTS Cycle: {result['cycle_id'][:20]}",
            "fields": fields,
            "verdict": verdict,
            "icon": ":chart_with_upwards_trend:",
            "username": "NUTS GPU Daemon",
        })

        # LLM narrative interpretation
        try:
            from tools.shared.research_narrator import narrate_mcmc
            from tools.shared.mattermost_notify import post_to_channel
            diag_summary = {}
            if diag and "error" not in diag:
                diag_summary["N1"] = diag.get("n1_verdict", "?")
                diag_summary["T7"] = f"{diag.get('t7_pass_count', '?')}/{diag.get('t7_n_total', '?')}"
            narrative = narrate_mcmc(
                alpha=result["alpha_mean"],
                alpha_std=result["alpha_std"],
                daic=result.get("daic", 0),
                significance=significance,
                diagnostics=diag_summary,
                sampler="NUTS",
                cycle_id=result["cycle_id"],
                n_eff=result.get("n_eff_min"),
                r_hat=result.get("r_hat_max"),
            )
            if narrative:
                post_to_channel("mcmc-nuts", narrative,
                                username="Research Narrator", icon_emoji=":brain:")
        except Exception:
            pass  # Narrator is best-effort
    except Exception as e:
        logger.debug(f"Mattermost notify failed: {e}")


def publish_to_neo4j(result: dict) -> bool:
    """Publish a NUTS result to Neo4j as ResearchCycleResult."""
    if result.get("status") != "completed":
        logger.warning(f"Skipping non-completed result: {result.get('cycle_id')}")
        return False

    driver = _get_neo4j_driver()

    # Save chain artifact locally (not inline in Neo4j)
    chain_artifact = _save_chain_artifact(result)

    # ── Schema contract fields ──────────────────────────────────────
    from efc_inference.runs.schema_contract import (
        SCHEMA_VERSION, validate_cycle_data, get_code_commit,
    )

    manifest = result.get("manifest", {})
    code_commit = manifest.get("code_commit") or get_code_commit(
        str(Path(__file__).resolve().parents[2])
    )
    dataset_hash = manifest.get("dataset_hash", "")
    assumptions_hash = manifest.get("assumptions_hash", "")
    cosmology_model = manifest.get("cosmology_model", "efc_variant_a")

    cypher = """
    MERGE (rc:ResearchCycleResult {cycle_id: $cycle_id})
    SET rc.timestamp = datetime($timestamp),
        rc.sampler_type = 'nuts',
        rc.schema_version = $schema_version,
        rc.code_commit = $code_commit,
        rc.dataset_hash = $dataset_hash,
        rc.assumptions_hash = $assumptions_hash,
        rc.cosmology_model = $cosmology_model,
        rc.verdict = $verdict,
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
        rc.wall_time_seconds = $wall_time,
        rc.manifest_json = $manifest_json,
        rc.source = 'gpu_nuts_daemon',
        rc.has_posterior_chain = $has_chain,
        rc.chain_artifact_path = $chain_artifact,
        rc.dll_bao = $dll_bao,
        rc.dll_growth = $dll_growth,
        rc.dll_hz = $dll_hz,
        rc.dll_snia = $dll_snia,
        rc.bao_source = $bao_source
    RETURN rc.cycle_id
    """

    significance = result.get("alpha_significance", 0)
    convergence = result.get("convergence_pass", False)

    # Determine verdict
    if not convergence:
        verdict = "NUTS_CONVERGENCE_FAILED"
    elif significance >= 1.7 and result.get("daic", 0) <= 0:
        verdict = "ROBUST"
    elif significance >= 1.5:
        verdict = "PARTIAL"
    elif significance >= 1.0:
        verdict = "MARGINAL"
    else:
        verdict = "NO_SIGNAL"

    params = {
        "cycle_id": result["cycle_id"],
        "timestamp": result["timestamp"],
        "schema_version": SCHEMA_VERSION,
        "code_commit": code_commit,
        "dataset_hash": dataset_hash,
        "assumptions_hash": assumptions_hash,
        "cosmology_model": cosmology_model,
        "verdict": verdict,
        "alpha_mean": result["alpha_mean"],
        "alpha_std": result["alpha_std"],
        "alpha_significance": significance,
        "p_alpha_negative": result.get("p_alpha_negative", 0),
        "daic": result.get("daic", 0),
        "dbic": result.get("dbic", 0),
        "om_mean": result.get("om_mean", 0),
        "om_std": result.get("om_std", 0),
        "h0_mean": result.get("h0_mean", 0),
        "h0_std": result.get("h0_std", 0),
        "s8_mean": result.get("s8_mean", 0),
        "s8_std": result.get("s8_std", 0),
        "n_data": manifest.get("n_data", 70),
        "signal_detected": significance >= 1.5,
        "convergence_pass": convergence,
        "n_eff_min": result.get("n_eff_min", 0),
        "r_hat_max": result.get("r_hat_max", 0),
        "wall_time": result.get("wall_time_seconds", 0),
        "manifest_json": json.dumps(manifest),
        "has_chain": bool(chain_artifact),
        "chain_artifact": chain_artifact,
        # Per-probe ΔlogL (for sector-separation analysis)
        "dll_bao": result.get("dll_bao"),
        "dll_growth": result.get("dll_growth"),
        "dll_hz": result.get("dll_hz"),
        "dll_snia": result.get("dll_snia"),
        "bao_source": result.get("bao_source", "bao_starter.csv"),
    }

    # Validate against schema contract (warn but don't block for v1.0 transition)
    try:
        valid, errors = validate_cycle_data(params, strict=False)
        if not valid:
            logger.warning(f"Schema validation warnings for {result['cycle_id']}: {errors}")
    except Exception as e:
        logger.warning(f"Schema validation error: {e}")

    try:
        with driver.session() as session:
            session.run(cypher, params)

        # Link to previous cycle
        link_cypher = """
        MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
        WITH rc
        OPTIONAL MATCH (prev:ResearchCycleResult)
        WHERE prev.timestamp < rc.timestamp AND prev.cycle_id <> $cycle_id
        WITH rc, prev ORDER BY prev.timestamp DESC LIMIT 1
        WHERE prev IS NOT NULL
        MERGE (prev)-[:FOLLOWED_BY]->(rc)
        """
        with driver.session() as session:
            session.run(link_cypher, {"cycle_id": result["cycle_id"]})

        # Publish diagnostics if present
        diag = result.get("diagnostics", {})
        if diag and "error" not in diag:
            diag_cypher = """
            MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
            SET rc.n1_verdict = $n1_verdict,
                rc.n2_verdict = $n2_verdict,
                rc.t7_verdict = $t7_verdict,
                rc.t7_pass_count = $t7_pass_count,
                rc.t7_n_total = $t7_n_total,
                rc.t7_robustness = $t7_robustness,
                rc.t7_criterion = $t7_criterion,
                rc.t7_strength_counts = $t7_strength_counts,
                rc.n1a_alpha_sig = $n1a_alpha_sig,
                rc.n1b_alpha_sig = $n1b_alpha_sig,
                rc.n2_stram_sig = $n2_stram_sig,
                rc.n3_verdict = $n3_verdict,
                rc.n3_reparameterized = $n3_reparameterized,
                rc.n3_aeff_sig = $n3_aeff_sig,
                rc.n3_aeff_mean = $n3_aeff_mean,
                rc.n3_aeff_std = $n3_aeff_std,
                rc.n3_aeff_p_negative = $n3_aeff_p_negative,
                rc.n3_alpha_derived_mean = $n3_alpha_derived_mean,
                rc.n3_alpha_derived_std = $n3_alpha_derived_std,
                rc.n3_a_t_mean = $n3_a_t_mean,
                rc.n3_delta_a_mean = $n3_delta_a_mean,
                rc.n3_corr_aeff_at = $n3_corr_aeff_at,
                rc.n3_corr_aeff_da = $n3_corr_aeff_da,
                rc.n3_sweep_stable = $n3_sweep_stable,
                rc.n4_verdict = $n4_verdict,
                rc.n4_free_alpha_sig = $n4_free_alpha_sig,
                rc.n4_mu0_mean = $n4_mu0_mean,
                rc.n4_mu0_std = $n4_mu0_std,
                rc.n4_mu0_deviation_from_gr = $n4_mu0_deviation_from_gr,
                rc.n4_corr_alpha_mu0 = $n4_corr_alpha_mu0,
                rc.n4_sweep_stable = $n4_sweep_stable,
                rc.n4_alpha_survives = $n4_alpha_survives,
                rc.n5_verdict = $n5_verdict,
                rc.n5_sweep_stable = $n5_sweep_stable,
                rc.n5_max_corr_alpha_rd = $n5_max_corr_alpha_rd,
                rc.n5_alpha_survives_flat = $n5_alpha_survives_flat,
                rc.n5_high_degeneracy = $n5_high_degeneracy,
                rc.n5_sig_range = $n5_sig_range,
                rc.n5_tight_alpha_sig = $n5_tight_alpha_sig,
                rc.n5_broad_alpha_sig = $n5_broad_alpha_sig,
                rc.n5_flat_alpha_sig = $n5_flat_alpha_sig,
                rc.n5_flat_rd_mean = $n5_flat_rd_mean,
                rc.n5_flat_rd_std = $n5_flat_rd_std,
                rc.n6_verdict = $n6_verdict,
                rc.n6_rd_efc_mean = $n6_rd_efc_mean,
                rc.n6_rd_efc_std = $n6_rd_efc_std,
                rc.n6_rd_gr_mean = $n6_rd_gr_mean,
                rc.n6_delta_rd_pct = $n6_delta_rd_pct,
                rc.n6_safety_pass = $n6_safety_pass,
                rc.n6_safety_level = $n6_safety_level,
                rc.n6_R_max = $n6_R_max,
                rc.n6_R_at_drag_mean = $n6_R_at_drag_mean,
                rc.n6_c_eff_at_drag = $n6_c_eff_at_drag,
                rc.n7_grav_verdict = $n7_grav_verdict,
                rc.n7_grav_alpha_mean = $n7_grav_alpha_mean,
                rc.n7_grav_alpha_std = $n7_grav_alpha_std,
                rc.n7_grav_alpha_sig = $n7_grav_alpha_sig,
                rc.n7_grav_alpha_p_negative = $n7_grav_alpha_p_negative,
                rc.n7_grav_daic = $n7_grav_daic,
                rc.n7_grav_dbic = $n7_grav_dbic,
                rc.d2_verdict = $d2_verdict,
                rc.d2_alpha_mean = $d2_alpha_mean,
                rc.d2_alpha_std = $d2_alpha_std,
                rc.d2_alpha_sig = $d2_alpha_sig,
                rc.d2_delta_alpha_sig = $d2_delta_alpha_sig,
                rc.d2_rd_mean = $d2_rd_mean,
                rc.d2_rd_std = $d2_rd_std,
                rc.d2_daic = $d2_daic,
                rc.d2_dbic = $d2_dbic,
                rc.diag_time_seconds = $diag_time
            """
            diag_params = {
                "cycle_id": result["cycle_id"],
                "n1_verdict": diag.get("n1_verdict", ""),
                "n2_verdict": diag.get("n2_verdict", ""),
                "t7_verdict": diag.get("t7_verdict", ""),
                "t7_pass_count": diag.get("t7_pass_count", 0),
                "t7_n_total": diag.get("t7_n_total", 0),
                "t7_robustness": diag.get("t7_robustness", 0),
                "t7_criterion": diag.get("t7_criterion", "sigma_threshold"),
                "t7_strength_counts": json.dumps(diag.get("t7_strength_counts", {})),
                "n1a_alpha_sig": diag.get("n1a_alpha_sig", 0),
                "n1b_alpha_sig": diag.get("n1b_alpha_sig", 0),
                "n2_stram_sig": diag.get("n2_stram_sig", 0),
                # N3 gate freedom (A_eff reparameterized)
                "n3_verdict": diag.get("n3_verdict", ""),
                "n3_reparameterized": diag.get("n3_reparameterized", False),
                "n3_aeff_sig": diag.get("n3_aeff_sig", 0),
                "n3_aeff_mean": diag.get("n3_aeff_mean", 0),
                "n3_aeff_std": diag.get("n3_aeff_std", 0),
                "n3_aeff_p_negative": diag.get("n3_aeff_p_negative", 0),
                "n3_alpha_derived_mean": diag.get("n3_alpha_derived_mean", 0),
                "n3_alpha_derived_std": diag.get("n3_alpha_derived_std", 0),
                "n3_a_t_mean": diag.get("n3_a_t_mean", 0),
                "n3_delta_a_mean": diag.get("n3_delta_a_mean", 0),
                "n3_corr_aeff_at": diag.get("n3_corr_aeff_at", 0),
                "n3_corr_aeff_da": diag.get("n3_corr_aeff_da", 0),
                "n3_sweep_stable": diag.get("n3_sweep_stable", False),
                # N4 modified Poisson
                "n4_verdict": diag.get("n4_verdict", ""),
                "n4_free_alpha_sig": diag.get("n4_free_alpha_sig", 0),
                "n4_mu0_mean": diag.get("n4_mu0_mean", 0),
                "n4_mu0_std": diag.get("n4_mu0_std", 0),
                "n4_mu0_deviation_from_gr": diag.get("n4_mu0_deviation_from_gr", 0),
                "n4_corr_alpha_mu0": diag.get("n4_corr_alpha_mu0", 0),
                "n4_sweep_stable": diag.get("n4_sweep_stable", False),
                "n4_alpha_survives": diag.get("n4_alpha_survives", False),
                # N5 sound horizon prior sweep (D2a)
                "n5_verdict": diag.get("n5_verdict", ""),
                "n5_sweep_stable": diag.get("n5_sweep_stable", False),
                "n5_max_corr_alpha_rd": diag.get("n5_max_corr_alpha_rd", 0),
                "n5_alpha_survives_flat": diag.get("n5_alpha_survives_flat", False),
                "n5_high_degeneracy": diag.get("n5_high_degeneracy", False),
                "n5_sig_range": diag.get("n5_sig_range", 0),
                "n5_tight_alpha_sig": diag.get("n5_tight_alpha_sig", 0),
                "n5_broad_alpha_sig": diag.get("n5_broad_alpha_sig", 0),
                "n5_flat_alpha_sig": diag.get("n5_flat_alpha_sig", 0),
                "n5_flat_rd_mean": diag.get("n5_flat_rd_mean", 0),
                "n5_flat_rd_std": diag.get("n5_flat_rd_std", 0),
                # N6 EFC sound horizon (D2b)
                "n6_verdict": diag.get("n6_verdict", ""),
                "n6_rd_efc_mean": diag.get("n6_rd_efc_mean", 0),
                "n6_rd_efc_std": diag.get("n6_rd_efc_std", 0),
                "n6_rd_gr_mean": diag.get("n6_rd_gr_mean", 0),
                "n6_delta_rd_pct": diag.get("n6_delta_rd_pct", 0),
                "n6_safety_pass": diag.get("n6_safety_pass", False),
                "n6_safety_level": diag.get("n6_safety_level", ""),
                "n6_R_max": diag.get("n6_R_max", 0),
                "n6_R_at_drag_mean": diag.get("n6_R_at_drag_mean", 0),
                "n6_c_eff_at_drag": diag.get("n6_c_eff_at_drag", 0),
                # N7-GRAV: GRAV-locked cross-probe ("Domstolen")
                "n7_grav_verdict": diag.get("n7_grav_verdict", ""),
                "n7_grav_alpha_mean": diag.get("n7_grav_alpha_mean", 0),
                "n7_grav_alpha_std": diag.get("n7_grav_alpha_std", 0),
                "n7_grav_alpha_sig": diag.get("n7_grav_alpha_sig", 0),
                "n7_grav_alpha_p_negative": diag.get("n7_grav_alpha_p_negative", 0),
                "n7_grav_daic": diag.get("n7_grav_daic", 0),
                "n7_grav_dbic": diag.get("n7_grav_dbic", 0),
                # D2 self-consistent sound horizon
                "d2_verdict": diag.get("d2_verdict", ""),
                "d2_alpha_mean": diag.get("d2_alpha_mean", 0),
                "d2_alpha_std": diag.get("d2_alpha_std", 0),
                "d2_alpha_sig": diag.get("d2_alpha_sig", 0),
                "d2_delta_alpha_sig": diag.get("d2_delta_alpha_sig", 0),
                "d2_rd_mean": diag.get("d2_rd_mean", 0),
                "d2_rd_std": diag.get("d2_rd_std", 0),
                "d2_daic": diag.get("d2_daic", 0),
                "d2_dbic": diag.get("d2_dbic", 0),
                "diag_time": diag.get("diag_time_seconds", 0),
            }
            with driver.session() as session:
                session.run(diag_cypher, diag_params)
            n3v = diag.get('n3_verdict', '')
            n4v = diag.get('n4_verdict', '')
            n5v = diag.get('n5_verdict', '')
            n6v = diag.get('n6_verdict', '')
            n7gv = diag.get('n7_grav_verdict', '')
            d2v = diag.get('d2_verdict', '')
            logger.info(f"  Diagnostics published: N1={diag.get('n1_verdict')} "
                        f"N2={diag.get('n2_verdict')} T7={diag.get('t7_verdict')} "
                        f"N3={n3v} N4={n4v} N5={n5v} N6={n6v} N7g={n7gv} D2={d2v}")

        # Publish VariantG scenarios as separate VariantGResult nodes
        if diag:
            for sc_name in ["G10", "G02", "G01"]:
                pfx = f"vg_{sc_name.lower()}_"
                sc_verdict = diag.get(f"{pfx}verdict", "")
                if sc_verdict and sc_verdict not in ("", "SKIPPED", "ERROR"):
                    vg_cypher = """
                    MERGE (vg:VariantGResult {cycle_id: $cycle_id, scenario: $scenario})
                    SET vg.timestamp = datetime(),
                        vg.verdict = $verdict,
                        vg.dll_total = $dll_total,
                        vg.daic_same_k = $daic_same_k,
                        vg.s8_vg_mean = $s8_vg_mean,
                        vg.s8_vg_std = $s8_vg_std,
                        vg.s8_lcdm_mean = $s8_lcdm_mean,
                        vg.s8_lcdm_std = $s8_lcdm_std,
                        vg.s8_shift = $s8_shift,
                        vg.om_vg_mean = $om_vg_mean,
                        vg.h0_vg_mean = $h0_vg_mean,
                        vg.mu_amp = $mu_amp,
                        vg.mu_span = $mu_span,
                        vg.k_eff = $k_eff,
                        vg.epsilon_eff = $epsilon_eff,
                        vg.screen_k_eff = $screen_k_eff,
                        vg.n_eff_min = $n_eff_min,
                        vg.r_hat_max = $r_hat_max,
                        vg.cosmology_model = 'EFCVariantG',
                        vg.source = 'gpu_nuts_daemon'
                    WITH vg
                    MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                    MERGE (rc)-[:HAS_VARIANT_G]->(vg)
                    """
                    vg_params = {
                        "cycle_id": result["cycle_id"],
                        "scenario": sc_name,
                        "verdict": sc_verdict,
                        "dll_total": diag.get(f"{pfx}dll_total", 0),
                        "daic_same_k": diag.get(f"{pfx}daic_same_k", 0),
                        "s8_vg_mean": diag.get(f"{pfx}s8_vg_mean", 0),
                        "s8_vg_std": diag.get(f"{pfx}s8_vg_std", 0),
                        "s8_lcdm_mean": diag.get(f"{pfx}s8_lcdm_mean", 0),
                        "s8_lcdm_std": diag.get(f"{pfx}s8_lcdm_std", 0),
                        "s8_shift": diag.get(f"{pfx}s8_shift", 0),
                        "om_vg_mean": diag.get(f"{pfx}om_vg_mean", 0),
                        "h0_vg_mean": diag.get(f"{pfx}h0_vg_mean", 0),
                        "mu_amp": diag.get(f"{pfx}mu_amp", 0),
                        "mu_span": diag.get(f"{pfx}mu_span", 0),
                        "k_eff": diag.get(f"{pfx}k_eff", 0.1),
                        "epsilon_eff": diag.get(f"{pfx}epsilon_eff", 0),
                        "screen_k_eff": diag.get(f"{pfx}screen_k_eff", 0),
                        "n_eff_min": diag.get(f"{pfx}n_eff_min", 0),
                        "r_hat_max": diag.get(f"{pfx}r_hat_max", 99.0),
                    }
                    try:
                        with driver.session() as session:
                            session.run(vg_cypher, vg_params)
                        logger.info(f"  VariantG {sc_name} published → Neo4j "
                                     f"(verdict={sc_verdict}, k_eff={vg_params['k_eff']})")
                    except Exception as e:
                        logger.warning(f"  VariantG {sc_name} Neo4j publish failed: {type(e).__name__}: {e}")

        # Publish VariantH (entropy-gradient growth ∇S → μ) results
        if diag:
            vh_verdict = diag.get("vh_verdict", "")
            if vh_verdict and vh_verdict not in ("", "SKIPPED", "ERROR"):
                vh_cypher = """
                MERGE (vh:VariantHResult {cycle_id: $cycle_id})
                SET vh.timestamp = datetime(),
                    vh.verdict = $verdict,
                    vh.s_bar_0_mean = $s_bar_0_mean,
                    vh.s_bar_0_std = $s_bar_0_std,
                    vh.s_bar_0_sig = $s_bar_0_sig,
                    vh.beta_0_mean = $beta_0_mean,
                    vh.beta_0_std = $beta_0_std,
                    vh.dll_total = $dll_total,
                    vh.dll_growth = $dll_growth,
                    vh.daic = $daic,
                    vh.dbic = $dbic,
                    vh.s8_mean = $s8_mean,
                    vh.s8_std = $s8_std,
                    vh.om_mean = $om_mean,
                    vh.h0_mean = $h0_mean,
                    vh.corr_s_bar_0_s8 = $corr_s_bar_0_s8,
                    vh.corr_s_bar_0_beta_0 = $corr_s_bar_0_beta_0,
                    vh.n_eff_min = $n_eff_min,
                    vh.r_hat_max = $r_hat_max,
                    vh.mu_min = $mu_min,
                    vh.mu_max = $mu_max,
                    vh.mu_z0_5 = $mu_z0_5,
                    vh.mu_z0_7 = $mu_z0_7,
                    vh.mu_z1_0 = $mu_z1_0,
                    vh.cosmology_model = 'EFCVariantH',
                    vh.source = 'gpu_nuts_daemon'
                WITH vh
                MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
                MERGE (rc)-[:HAS_VARIANT_H]->(vh)
                """
                vh_params = {
                    "cycle_id": result["cycle_id"],
                    "verdict": vh_verdict,
                    "s_bar_0_mean": diag.get("vh_s_bar_0_mean", 0),
                    "s_bar_0_std": diag.get("vh_s_bar_0_std", 0),
                    "s_bar_0_sig": diag.get("vh_s_bar_0_sig", 0),
                    "beta_0_mean": diag.get("vh_beta_0_mean", 0),
                    "beta_0_std": diag.get("vh_beta_0_std", 0),
                    "dll_total": diag.get("vh_dll_total", 0),
                    "dll_growth": diag.get("vh_dll_growth", 0),
                    "daic": diag.get("vh_daic", 0),
                    "dbic": diag.get("vh_dbic", 0),
                    "s8_mean": diag.get("vh_s8_mean", 0),
                    "s8_std": diag.get("vh_s8_std", 0),
                    "om_mean": diag.get("vh_om_mean", 0),
                    "h0_mean": diag.get("vh_h0_mean", 0),
                    "corr_s_bar_0_s8": diag.get("vh_corr_s_bar_0_s8", 0),
                    "corr_s_bar_0_beta_0": diag.get("vh_corr_s_bar_0_beta_0", 0),
                    "n_eff_min": diag.get("vh_n_eff_min", 0),
                    "r_hat_max": diag.get("vh_r_hat_max", 99.0),
                    "mu_min": diag.get("vh_mu_min", 1.0),
                    "mu_max": diag.get("vh_mu_max", 1.0),
                    "mu_z0_5": diag.get("vh_mu_z0_5", 1.0),
                    "mu_z0_7": diag.get("vh_mu_z0_7", 1.0),
                    "mu_z1_0": diag.get("vh_mu_z1_0", 1.0),
                }
                try:
                    with driver.session() as session:
                        session.run(vh_cypher, vh_params)
                    logger.info(f"  VariantH published → Neo4j "
                                 f"(verdict={vh_verdict}, "
                                 f"S̄₀={vh_params['s_bar_0_mean']:.4f}±{vh_params['s_bar_0_std']:.4f}, "
                                 f"β₀={vh_params['beta_0_mean']:.3f})")
                except Exception as e:
                    logger.warning(f"  VariantH Neo4j publish failed: {type(e).__name__}: {e}")

        # Publish Axiom 0 results if present
        ax0 = result.get("axiom0")
        if ax0 and isinstance(ax0, dict):
            ax0_cypher = """
            MERGE (a:Axiom0TestResult {cycle_id: $cycle_id, test_version: 'v2.0'})
            SET a.timestamp = datetime(),
                a.n_points = $n_points,
                a.s_flow_trans = $s_flow_trans,
                a.s_trans_latent = $s_trans_latent,
                a.primary_p_value = $primary_p,
                a.primary_null_std = $null_std,
                a.primary_method = $primary_method,
                a.secondary_frac_pos = $sign_frac,
                a.secondary_p_binomial = $p_binom,
                a.mean_boundary_distance = $mean_dist,
                a.min_boundary_distance = $min_dist,
                a.n_transition_latent = $n_trans_lat,
                a.sources_locked = 'Madau-Dickinson + Tacconi/PHIBSS Table3b beta=2',
                a.alpha_mean = $alpha_mean,
                a.alpha_std = $alpha_std,
                a.source = 'gpu_nuts_daemon'
            WITH a
            MATCH (rc:ResearchCycleResult {cycle_id: $cycle_id})
            MERGE (rc)-[:HAS_AXIOM0_TEST]->(a)
            WITH a
            MERGE (v:EFCValidation {test_id: 'axiom0_s_hat_v1'})
            ON CREATE SET v.name = 'Axiom 0: S_hat(z) Regime Boundary Test',
                          v.description = 'Pre-registered phenomenological test: BAO anomalies cluster at EFC regime boundaries in S_hat(z) = log10(rho_SFR) + log10(f_gas) + C0. Sources locked (Madau-Dickinson + Tacconi/PHIBSS Table 3b beta=2). Primary null: uniform random z. v2.0: fixed Tacconi f_gas formula (prior versions had sign error).',
                          v.prediction = 'BAO sigma-deviations cluster near S_flow/S_trans and S_trans/S_latent boundaries',
                          v.vl_category = 'phenomenological',
                          v.vl_public = true,
                          v.data_source = 'BAO surveys (6dF, MGS, BOSS, eBOSS, DESI)',
                          v.created = datetime()
            SET v.status = CASE
                WHEN $primary_p < 0.05 THEN 'success'
                WHEN $primary_p < 0.20 THEN 'partial'
                ELSE 'pending'
                END,
                v.result = 'Primary p=' + toString($primary_p) + ', Sign coherence p=' + toString($p_binom),
                v.quantitative_result = 'p_primary=' + toString($primary_p) + ' p_binom=' + toString($p_binom) + ' n=' + toString($n_points) + ' method=' + $primary_method,
                v.last_synced = datetime(),
                v.notes = 'Auto-updated by nuts_publisher. test_version=v2.0 method=' + $primary_method
            WITH a, v
            MERGE (a)-[:VALIDATES]->(v)
            """
            ax0_params = {
                "cycle_id": result["cycle_id"],
                "n_points": ax0.get("n_points", 0),
                "s_flow_trans": ax0.get("s_flow_trans", 0),
                "s_trans_latent": ax0.get("s_trans_latent", 0),
                "primary_p": ax0.get("primary_p", 0),
                "null_std": ax0.get("primary_null_std", 0.0),
                "primary_method": ax0.get("primary_method", "randomise_z_uniform"),
                "sign_frac": ax0.get("secondary_sign_frac", 0),
                "p_binom": ax0.get("secondary_p_binomial", 0),
                "mean_dist": ax0.get("mean_boundary_distance", 0),
                "min_dist": ax0.get("min_boundary_distance", 0),
                "n_trans_lat": ax0.get("n_transition_latent", 0),
                "alpha_mean": result.get("alpha_mean"),
                "alpha_std": result.get("alpha_std"),
            }
            with driver.session() as session:
                session.run(ax0_cypher, ax0_params)
            logger.info(f"  Axiom 0 published: p={ax0.get('primary_p', '?')}, "
                        f"sign={ax0.get('secondary_sign_frac', '?')}, "
                        f"→ EFCValidation axiom0_s_hat_v1")

        logger.info(f"Published to Neo4j: {result['cycle_id']} → {verdict}")
        logger.info(f"  α={result['alpha_mean']:.3f}±{result['alpha_std']:.3f} ({significance:.2f}σ), ΔAIC={result.get('daic', 0):+.2f}")

        # Notify Mattermost
        _notify_mattermost_nuts(result, verdict, significance)

        return True

    except Exception as e:
        logger.error(f"Neo4j publish failed: {type(e).__name__}: {e}")
        return False
    finally:
        driver.close()


def mark_published(remote_path: str, cycle_id: str):
    """Move processed file to published/ on GPU-PC."""
    cmd = (
        f"ssh {GPU_HOST} 'wsl -d Ubuntu-24.04 -- bash -c \""
        f"mkdir -p {GPU_OUTPUTS}/published && "
        f"mv {GPU_OUTPUTS}/{cycle_id}.json {GPU_OUTPUTS}/published/"
        f"\"'"
    )
    try:
        subprocess.run(cmd, shell=True, capture_output=True, timeout=15)
    except Exception:
        pass


def process_all():
    """Fetch, publish, and archive all pending results."""
    files = fetch_results()
    if not files:
        logger.info("No new NUTS results to process")
        return 0

    published = 0
    for fpath in files:
        try:
            with open(fpath) as f:
                result = json.load(f)

            cycle_id = result.get("cycle_id", "unknown")

            if publish_to_neo4j(result):
                mark_published(GPU_OUTPUTS, cycle_id)
                published += 1
            else:
                logger.warning(f"Failed to publish {cycle_id}")

        except Exception as e:
            logger.error(f"Error processing {fpath.name}: {e}")
        finally:
            fpath.unlink(missing_ok=True)

    logger.info(f"Published {published}/{len(files)} results")
    return published


def main():
    parser = argparse.ArgumentParser(description="NUTS Result Publisher")
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Poll interval (seconds)")
    args = parser.parse_args()

    if args.once or not args.daemon:
        process_all()
    else:
        logger.info(f"Starting publisher daemon (poll every {args.interval}s)")
        while True:
            try:
                process_all()
            except Exception as e:
                logger.error(f"Publisher error: {e}")
            time.sleep(args.interval)


if __name__ == "__main__":
    main()
