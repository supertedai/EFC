#!/usr/bin/env python3
"""
GPU NUTS Daemon — Autonomous NUTS inference on GPU-PC.

Runs NUTS baseline + LCDM on dual-GPU (RTX 5080), writes results to JSON.
Results are picked up by the Mac-side publisher for Neo4j + validation ledger.

Usage (WSL2):
    python3 /mnt/c/efc_worker/efc_inference/runs/gpu_nuts_daemon.py --mode once
    python3 /mnt/c/efc_worker/efc_inference/runs/gpu_nuts_daemon.py --mode daemon --interval 21600

Output:
    /mnt/c/efc_worker/outputs/nuts_<timestamp>.json
"""
import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [gpu_nuts_daemon] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("gpu_nuts_daemon")

# ── paths ──────────────────────────────────────────────────────────
WORKER_DIR = Path(os.environ.get("EFC_WORKER_DIR", "/mnt/c/efc_worker"))
OUTPUT_DIR = WORKER_DIR / "outputs"
LOCK_FILE  = OUTPUT_DIR / "nuts_daemon.lock"

# Add efc_worker to path so efc_inference package is importable
sys.path.insert(0, str(WORKER_DIR))


def _get_code_commit() -> str:
    """Get git short hash from WORKER_DIR."""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "-C", str(WORKER_DIR), "rev-parse", "--short=8", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


def _compute_data_hash(data) -> str:
    """Compute dataset hash from ProbeData."""
    import hashlib
    h = hashlib.sha256()
    # Hash all probe arrays
    for attr in ["bao_z", "bao_obs", "bao_err", "bao_types",
                 "growth_z", "growth_obs", "growth_err",
                 "hz_z", "hz_obs", "hz_err",
                 "snia_z", "snia_obs", "snia_err"]:
        v = getattr(data, attr, None)
        if v is not None:
            import numpy as np
            h.update(np.asarray(v).tobytes())
    return h.hexdigest()[:16]


def _compute_assumptions_hash() -> str:
    """Compute hash of assumptions.yaml if it exists."""
    import hashlib
    assumptions_path = WORKER_DIR / "efc_inference" / "configs" / "assumptions.yaml"
    if assumptions_path.exists():
        return hashlib.sha256(assumptions_path.read_bytes()).hexdigest()[:16]
    return "no_assumptions"


def _acquire_lock() -> bool:
    """PID-based lock to prevent overlapping runs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if LOCK_FILE.exists():
        try:
            old_pid = int(LOCK_FILE.read_text().strip())
            # Check if process still alive
            os.kill(old_pid, 0)
            logger.warning(f"Lock held by PID {old_pid} — skipping")
            return False
        except (ProcessLookupError, ValueError):
            logger.info(f"Stale lock removed (PID gone)")
            LOCK_FILE.unlink()
    LOCK_FILE.write_text(str(os.getpid()))
    return True


def _release_lock():
    try:
        LOCK_FILE.unlink(missing_ok=True)
    except Exception:
        pass


def run_nuts_cycle(
    num_warmup: int = 500,
    num_samples: int = 2000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    run_diag: bool = True,
    diag_sigma_threshold: float = 1.5,
) -> dict:
    """Run a single NUTS inference cycle and return results as dict."""

    # Import JAX/numpyro (only available on GPU-PC)
    logger.info("Importing JAX/numpyro...")
    import jax
    jax.config.update("jax_enable_x64", True)

    devices = jax.devices()
    logger.info(f"JAX devices: {devices}")
    logger.info(f"Float64 enabled: {jax.config.x64_enabled}")

    # Import our NUTS implementation
    from efc_inference.runs.jax_efc_nuts import (
        load_data, run_nuts_efc, NUTSResult,
        run_n1_nuts, run_n2_nuts, run_t7_nuts, run_n3_nuts, run_n4_nuts,
        run_n5_nuts,
    )

    cycle_id = f"nuts_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    logger.info(f"=== NUTS CYCLE: {cycle_id} ===")

    # Load data
    logger.info("Loading data...")
    # BAO_PATH: default = DESI DR2 (full covariance). Override via env.
    bao_path = os.environ.get("EFC_BAO_DATA_PATH",
                               str(WORKER_DIR / "efc_inference/data/bao/desi_dr2/bao_desi_dr2.json"))
    if not os.path.isabs(bao_path):
        bao_path = str(WORKER_DIR / bao_path)
    data = load_data(
        bao_path=bao_path,
        growth_path=str(WORKER_DIR / "efc_inference/data/growth/fs8_extended.csv"),
        hz_path=str(WORKER_DIR / "efc_inference/data/hubble/hz_cosmic_chronometers.csv"),
        snia_path=str(WORKER_DIR / "efc_inference/data/snia/pantheon_binned.csv"),
        snia_cov_path=str(WORKER_DIR / "efc_inference/data/snia/pantheon_binned_covtotal.npy"),
    )
    n_bao = len(data.bao_z)
    n_growth = len(data.growth_z)
    n_hz = len(data.hz_z)
    n_snia = len(data.snia_z)
    n_data = data.n_total
    logger.info(f"Data: BAO={n_bao}, Growth={n_growth}, Hz={n_hz}, SNIa={n_snia} = {n_data} pts")

    # Run NUTS
    logger.info(f"Running NUTS: {num_chains} chains × {num_warmup}w + {num_samples}s, target_accept={target_accept}")
    t0 = time.time()
    result: NUTSResult = run_nuts_efc(
        data=data,
        num_warmup=num_warmup,
        num_samples=num_samples,
        num_chains=num_chains,
        seed=seed,
        target_accept=target_accept,
    )
    wall_time = time.time() - t0
    logger.info(f"NUTS complete in {wall_time:.0f}s ({wall_time/60:.1f}min)")

    # Compute significance
    significance = abs(result.alpha_mean) / result.alpha_std if result.alpha_std > 0 else 0.0

    logger.info(f"  alpha = {result.alpha_mean:.4f} ± {result.alpha_std:.4f} ({significance:.2f}σ)")
    logger.info(f"  Om = {result.om_mean:.4f} ± {result.om_std:.4f}")
    logger.info(f"  H0 = {result.h0_mean:.2f} ± {result.h0_std:.2f}")
    logger.info(f"  s8 = {result.s8_mean:.4f} ± {result.s8_std:.4f}")
    logger.info(f"  ΔAIC = {result.daic:+.2f}, ΔBIC = {result.dbic:+.2f}")
    logger.info(f"  n_eff_min = {result.n_eff_min:.0f}, r_hat_max = {result.r_hat_max:.4f}")
    logger.info(f"  P(α<0) = {result.alpha_p_negative*100:.1f}%")

    # Build output dict
    output = {
        "cycle_id": cycle_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sampler": "nuts",
        "status": "completed",
        "wall_time_seconds": round(wall_time, 1),

        # Alpha signal
        "alpha_mean": float(result.alpha_mean),
        "alpha_std": float(result.alpha_std),
        "alpha_significance": round(significance, 3),
        "p_alpha_negative": round(float(result.alpha_p_negative), 4),

        # Other params
        "om_mean": float(result.om_mean),
        "om_std": float(result.om_std),
        "h0_mean": float(result.h0_mean),
        "h0_std": float(result.h0_std),
        "s8_mean": float(result.s8_mean),
        "s8_std": float(result.s8_std),

        # Model comparison
        "daic": float(result.daic),
        "dbic": float(result.dbic),
        "ll_max_efc": float(result.ll_max_efc),
        "ll_max_lcdm": float(result.ll_max_lcdm),

        # Convergence diagnostics
        "n_eff_min": float(result.n_eff_min),
        "r_hat_max": float(result.r_hat_max),
        "convergence_pass": result.r_hat_max <= 1.05 and result.n_eff_min >= 200,

        # Manifest (schema_version 1.0)
        "manifest": {
            "seed": seed,
            "num_warmup": num_warmup,
            "num_samples": num_samples,
            "num_chains": num_chains,
            "target_accept": target_accept,
            "dense_mass": True,
            "float64": True,
            "max_tree_depth": 10,
            "n_data": n_data,
            "jax_version": jax.__version__,
            "devices": [str(d) for d in devices],
            "time_efc": float(result.time_efc),
            "time_lcdm": float(result.time_lcdm),
            # Schema contract v1.0
            "code_commit": _get_code_commit(),
            "dataset_hash": _compute_data_hash(data),
            "assumptions_hash": _compute_assumptions_hash(),
            "cosmology_model": "efc_variant_a",
        },
    }

    # Add posterior chain if available (for PPC / LOO diagnostics)
    if result.posterior_chain is not None:
        chain = result.posterior_chain
        output["posterior_chain"] = chain.tolist()  # (n_samples, 4) → list-of-lists
        output["chain_shape"] = list(chain.shape)
        output["chain_columns"] = ["Omega_m", "H0", "sigma8", "alpha"]
        logger.info(f"  Posterior chain: {chain.shape} included in output")

    # Per-probe ΔlogL at best-fit (for sector-separation analysis)
    try:
        from efc_inference.runs.research_mcmc import load_modules, RD_FIXED
        bao_path_for_modules = os.environ.get("EFC_BAO_DATA_PATH",
                                               str(WORKER_DIR / "efc_inference/data/bao/desi_dr2/bao_desi_dr2.json"))
        if not os.path.isabs(bao_path_for_modules):
            bao_path_for_modules = str(WORKER_DIR / bao_path_for_modules)
        modules = load_modules(bao_path=bao_path_for_modules)
        # Best-fit EFC params
        params_efc = {
            "Omega_m": result.om_mean, "H0": result.h0_mean,
            "sigma8": result.s8_mean, "alpha_cosmo": result.alpha_mean, "rd": RD_FIXED,
        }
        # Best-fit ΛCDM params (use posterior means but α=0)
        params_lcdm = {
            "Omega_m": result.om_mean, "H0": result.h0_mean,
            "sigma8": result.s8_mean, "alpha_cosmo": 0.0, "rd": RD_FIXED,
        }
        probe_map = {"bao": "bao", "growth": "growth", "hz": "hz", "snia": "snia"}
        for probe_key, mod_key in probe_map.items():
            if mod_key in modules:
                ll_e = modules[mod_key].log_likelihood(params_efc)
                ll_l = modules[mod_key].log_likelihood(params_lcdm)
                if np.isfinite(ll_e) and np.isfinite(ll_l):
                    output[f"dll_{probe_key}"] = round(float(ll_e - ll_l), 4)
        output["bao_source"] = os.path.basename(bao_path_for_modules)
        logger.info(f"  Per-probe ΔlogL: BAO={output.get('dll_bao')}, growth={output.get('dll_growth')}, "
                     f"Hz={output.get('dll_hz')}, SNIa={output.get('dll_snia')}")
    except Exception as e:
        logger.warning(f"Per-probe ΔlogL computation failed: {e}")

    # Run diagnostics if signal meets hint threshold
    if run_diag and significance >= diag_sigma_threshold:
        logger.info(f"  Signal {significance:.2f}σ ≥ {diag_sigma_threshold}σ — running diagnostics")
        try:
            diag = run_diagnostics(
                data=data,
                num_warmup=min(num_warmup, 300),
                num_samples=min(num_samples, 1000),
                num_chains=num_chains,
                seed=seed + 1000,
                target_accept=target_accept,
                growth_path=str(WORKER_DIR / "efc_inference/data/growth/fs8_extended.csv"),
                posterior_chain=result.posterior_chain,
                baseline_alpha_sig=significance,
            )
            diag_out = {
                "n1_verdict": diag["n1"]["verdict"],
                "n1a_alpha_sig": diag["n1"]["n1a"]["alpha"]["significance"],
                "n1b_alpha_sig": diag["n1"]["n1b"]["alpha"]["significance"],
                "n1b_rd_mean": diag["n1"]["n1b"].get("rd_mean", 0),
                "n1b_rd_ci_width": diag["n1"]["n1b"].get("rd_ci_width_95", 0),
                "n2_verdict": diag["n2"]["verdict"],
                "n2_stram_sig": diag["n2"]["variants"]["stram"]["alpha"]["significance"],
                "n2_middels_sig": diag["n2"]["variants"]["middels"]["alpha"]["significance"],
                "n2_flat_sig": diag["n2"]["variants"]["flat"]["alpha"]["significance"],
                "t7_verdict": diag["t7"]["verdict"],
                "t7_pass_count": diag["t7"]["pass_count"],
                "t7_n_total": diag["t7"]["n_total"],
                "t7_robustness": diag["t7"]["robustness_score"],
                "t7_criterion": diag["t7"].get("criterion", "sigma_threshold"),
                "t7_strength_counts": str(diag["t7"].get("strength_counts", {})),
                "diag_time_seconds": diag["total_time_seconds"],
            }
            # N3 gate freedom — A_eff or legacy α (may not be present if errored)
            n3 = diag.get("n3", {})
            if n3.get("verdict"):
                diag_out["n3_verdict"] = n3["verdict"]
                diag_out["n3_reparameterized"] = n3.get("reparameterized", False)
                fg = n3.get("free_gate", {})
                if fg:
                    # A_eff version (v2)
                    aeff = fg.get("aeff", {})
                    if aeff:
                        diag_out["n3_aeff_sig"] = aeff.get("significance", 0)
                        diag_out["n3_aeff_mean"] = aeff.get("mean", 0)
                        diag_out["n3_aeff_std"] = aeff.get("std", 0)
                        diag_out["n3_aeff_p_negative"] = aeff.get("p_negative", 0)
                        diag_out["n3_alpha_derived_mean"] = aeff.get("alpha_derived_mean", 0)
                        diag_out["n3_alpha_derived_std"] = aeff.get("alpha_derived_std", 0)
                    else:
                        # Legacy α version (v1 fallback)
                        diag_out["n3_free_alpha_sig"] = fg.get("alpha", {}).get("significance", 0)
                        diag_out["n3_free_alpha_mean"] = fg.get("alpha", {}).get("mean", 0)
                    diag_out["n3_a_t_mean"] = fg.get("a_t_mean", 0)
                    diag_out["n3_delta_a_mean"] = fg.get("delta_a_mean", 0)
                    corrs = fg.get("correlations", {})
                    # A_eff uses "aeff_at", legacy uses "alpha_at"
                    diag_out["n3_corr_aeff_at"] = corrs.get("aeff_at", corrs.get("alpha_at", 0))
                    diag_out["n3_corr_aeff_da"] = corrs.get("aeff_da", corrs.get("alpha_da", 0))
                diag_out["n3_sweep_stable"] = n3.get("sweep_stable", False)
            # N4 modified Poisson (may not be present if it errored)
            n4 = diag.get("n4", {})
            if n4.get("verdict"):
                diag_out["n4_verdict"] = n4["verdict"]
                fm = n4.get("free_mu", {})
                if fm:
                    diag_out["n4_free_alpha_sig"] = fm.get("alpha_sig", 0)
                    diag_out["n4_free_alpha_mean"] = fm.get("alpha_mean", 0)
                    diag_out["n4_mu0_mean"] = fm.get("mu0_mean", 0)
                    diag_out["n4_mu0_std"] = fm.get("mu0_std", 0)
                    diag_out["n4_mu0_deviation_from_gr"] = fm.get("mu0_deviation_from_gr", 0)
                corrs = n4.get("correlations", {})
                if corrs:
                    # NUTS uses "alpha_mu0", emcee uses "a_mu0"
                    diag_out["n4_corr_alpha_mu0"] = corrs.get("alpha_mu0", corrs.get("a_mu0", 0))
                diag_out["n4_sweep_stable"] = n4.get("sweep_stable", False)
                diag_out["n4_alpha_survives"] = n4.get("alpha_survives_freedom", False)
            # N5 sound horizon prior sweep (D2a)
            n5 = diag.get("n5", {})
            if n5.get("verdict"):
                diag_out["n5_verdict"] = n5["verdict"]
                diag_out["n5_sweep_stable"] = n5.get("sweep_stable", False)
                diag_out["n5_max_corr_alpha_rd"] = n5.get("max_corr_alpha_rd", 0)
                diag_out["n5_alpha_survives_flat"] = n5.get("alpha_survives_flat", False)
                diag_out["n5_high_degeneracy"] = n5.get("high_degeneracy", False)
                diag_out["n5_sig_range"] = n5.get("sig_range", 0)
                # Extract per-config significances
                sweep = n5.get("sweep_results", [])
                for sr in sweep:
                    cfg = sr.get("config", "")
                    if cfg == "tight":
                        diag_out["n5_tight_alpha_sig"] = sr.get("alpha_sig", 0)
                    elif cfg == "broad":
                        diag_out["n5_broad_alpha_sig"] = sr.get("alpha_sig", 0)
                    elif cfg == "flat":
                        diag_out["n5_flat_alpha_sig"] = sr.get("alpha_sig", 0)
                        diag_out["n5_flat_rd_mean"] = sr.get("rd_mean", 0)
                        diag_out["n5_flat_rd_std"] = sr.get("rd_std", 0)
            # N6 EFC sound horizon (D2b — post-fit)
            n6 = diag.get("n6", {})
            if n6.get("verdict") and n6["verdict"] != "SKIPPED":
                diag_out["n6_verdict"] = n6["verdict"]
                diag_out["n6_rd_efc_mean"] = n6.get("rd_efc_mean", 0)
                diag_out["n6_rd_efc_std"] = n6.get("rd_efc_std", 0)
                diag_out["n6_rd_gr_mean"] = n6.get("rd_gr_mean", 0)
                diag_out["n6_delta_rd_pct"] = n6.get("delta_rd_pct_mean", 0)
                diag_out["n6_safety_pass"] = n6.get("safety_pass", False)
                diag_out["n6_safety_level"] = n6.get("safety_level", "")
                diag_out["n6_R_max"] = n6.get("R_max", 0)
                diag_out["n6_R_at_drag_mean"] = n6.get("R_at_drag_mean", 0)
                diag_out["n6_c_eff_at_drag"] = n6.get("c_eff_at_drag_mean", 0)
            # N7-GRAV: GRAV-locked cross-probe ("Domstolen")
            n7g = diag.get("n7_grav", {})
            if n7g.get("verdict") and n7g["verdict"] != "SKIPPED":
                diag_out["n7_grav_verdict"] = n7g["verdict"]
                diag_out["n7_grav_alpha_mean"] = n7g.get("alpha_mean", 0)
                diag_out["n7_grav_alpha_std"] = n7g.get("alpha_std", 0)
                diag_out["n7_grav_alpha_sig"] = n7g.get("alpha_sig", 0)
                diag_out["n7_grav_alpha_p_negative"] = n7g.get("alpha_p_negative", 0)
                diag_out["n7_grav_daic"] = n7g.get("daic", 0)
                diag_out["n7_grav_dbic"] = n7g.get("dbic", 0)
                diag_out["n7_grav_n_eff_min"] = n7g.get("n_eff_min", 0)
                diag_out["n7_grav_r_hat_max"] = n7g.get("r_hat_max", 0)
            # D2 self-consistent sound horizon
            d2 = diag.get("d2", {})
            if d2.get("verdict") and d2["verdict"] not in ("SKIPPED",):
                diag_out["d2_verdict"] = d2["verdict"]
                diag_out["d2_alpha_mean"] = d2.get("alpha_mean", 0)
                diag_out["d2_alpha_std"] = d2.get("alpha_std", 0)
                diag_out["d2_alpha_sig"] = d2.get("alpha_sig", 0)
                diag_out["d2_delta_alpha_sig"] = d2.get("delta_alpha_sig", 0)
                diag_out["d2_rd_mean"] = d2.get("rd_mean", 0)
                diag_out["d2_rd_std"] = d2.get("rd_std", 0)
                diag_out["d2_daic"] = d2.get("daic", 0)
                diag_out["d2_dbic"] = d2.get("dbic", 0)
            # VariantG constitutive law — 3 pre-registered scenarios
            vg_all = diag.get("vg", {})
            for sc_name in ["G10", "G02", "G01"]:
                vg = vg_all.get(sc_name, {})
                if vg.get("verdict") and vg["verdict"] not in ("SKIPPED",):
                    pfx = f"vg_{sc_name.lower()}_"  # e.g. vg_g10_, vg_g02_, vg_g01_
                    diag_out[f"{pfx}verdict"] = vg["verdict"]
                    diag_out[f"{pfx}dll_total"] = vg.get("dll_total", 0)
                    diag_out[f"{pfx}daic_same_k"] = vg.get("daic_same_k", 0)
                    diag_out[f"{pfx}s8_vg_mean"] = vg.get("s8_vg_mean", 0)
                    diag_out[f"{pfx}s8_vg_std"] = vg.get("s8_vg_std", 0)
                    diag_out[f"{pfx}s8_lcdm_mean"] = vg.get("s8_lcdm_mean", 0)
                    diag_out[f"{pfx}s8_lcdm_std"] = vg.get("s8_lcdm_std", 0)
                    diag_out[f"{pfx}s8_shift"] = vg.get("s8_shift", 0)
                    diag_out[f"{pfx}om_vg_mean"] = vg.get("om_vg_mean", 0)
                    diag_out[f"{pfx}h0_vg_mean"] = vg.get("h0_vg_mean", 0)
                    diag_out[f"{pfx}mu_amp"] = vg.get("mu_amp", 0.0)
                    diag_out[f"{pfx}mu_span"] = vg.get("mu_span", 0.0)
                    diag_out[f"{pfx}k_eff"] = vg.get("k_eff", 0.1)
                    diag_out[f"{pfx}epsilon_eff"] = vg.get("epsilon_eff", 0)
                    diag_out[f"{pfx}screen_k_eff"] = vg.get("screen_k_eff", 0)
                    diag_out[f"{pfx}n_eff_min"] = vg.get("n_eff_min", 0)
                    diag_out[f"{pfx}r_hat_max"] = vg.get("r_hat_max", 99.0)
            output["diagnostics"] = diag_out
            n3_v = diag.get('n3', {}).get('verdict', 'N/A')
            n4_v = diag.get('n4', {}).get('verdict', 'N/A')
            n5_v = diag.get('n5', {}).get('verdict', 'N/A')
            n6_v = diag.get('n6', {}).get('verdict', 'N/A')
            n7g_v = n7g.get('verdict', 'N/A') if n7g else 'N/A'
            d2_v = diag.get('d2', {}).get('verdict', 'N/A')
            vg_v = "/".join(v.get('verdict', 'N/A') for v in diag.get('vg', {}).values() if isinstance(v, dict))
            logger.info(f"  Diagnostics: N1={diag['n1']['verdict']} "
                        f"N2={diag['n2']['verdict']} "
                        f"T7={diag['t7']['verdict']} ({diag['t7']['pass_count']}/{diag['t7']['n_total']}) "
                        f"N3={n3_v} N4={n4_v} N5={n5_v} N6={n6_v} N7g={n7g_v} D2={d2_v} VG={vg_v}")
        except Exception as e:
            logger.error(f"  Diagnostics failed: {type(e).__name__}: {e}")
            output["diagnostics"] = {"error": f"{type(e).__name__}: {str(e)[:300]}"}
    elif run_diag:
        logger.info(f"  Signal {significance:.2f}σ < {diag_sigma_threshold}σ — skipping diagnostics")

    # Email notification if signal above threshold
    _send_signal_notification(output, significance)

    # Divergence analysis — find where EFC and LCDM differ most
    try:
        from .divergence_engine import DivergenceEngine
        chain = output.get("posterior_chain")
        if chain is not None and len(chain) > 0:
            chain = np.array(chain)  # (n_samples, 4): Om, H0, s8, alpha
            params_efc = {
                "Omega_m": float(np.median(chain[:, 0])),
                "H0": float(np.median(chain[:, 1])),
                "sigma8": float(np.median(chain[:, 2])),
                "alpha_cosmo": float(np.median(chain[:, 3])),
                "r_d": 147.09,
            }
            params_lcdm = {
                "Omega_m": params_efc["Omega_m"],
                "H0": params_efc["H0"],
                "sigma8": params_efc["sigma8"],
                "alpha_cosmo": 0.0,
                "r_d": 147.09,
            }
            deng = DivergenceEngine()
            report = deng.run(params_efc, params_lcdm)
            deng.save_report(report)
            output["divergence"] = {
                "total_delta_logL": report.total_delta_logL,
                "best_probe": report.best_probe,
                "best_z": report.best_z,
                "best_delta_sigma": report.best_delta_sigma,
            }
            logger.info(f"  Divergence: ΔlogL={report.total_delta_logL:+.3f}, "
                         f"best={report.best_probe}@z={report.best_z:.2f}")
    except Exception as e:
        logger.warning(f"  Divergence analysis skipped: {type(e).__name__}: {e}")

    # ── Axiom 0: S_hat(z) regime boundary test ──
    try:
        import sys as _sys
        _repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        # GPU-PC: daemon lives in /mnt/c/efc_worker/, scripts in ./scripts/axiom0/
        # Mac: daemon lives in efc_inference/runs/, scripts in ../../scripts/axiom0/
        _axiom0_dir = os.path.join(_repo_root, 'scripts', 'axiom0')
        if not os.path.exists(_axiom0_dir):
            _axiom0_dir = os.path.join(os.path.dirname(__file__), 'scripts', 'axiom0')
        if not os.path.exists(_axiom0_dir):
            _axiom0_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'axiom0')
        if _axiom0_dir not in _sys.path:
            _sys.path.insert(0, _axiom0_dir)

        from axiom0_s_hat import (
            compute_c0_zero_at_z0, s_hat as s_hat_fn,
            compute_regime_boundaries_from_grid,
            regime_label, distance_to_nearest_boundary, nearest_boundary_label,
            permutation_test_mean_distance, sign_coherence_transition_latent,
            read_bao_csv,
        )

        bao_csv = os.path.join(_axiom0_dir, 'bao_points.csv')
        if os.path.exists(bao_csv):
            logger.info("--- AXIOM 0: S_hat regime test ---")
            points = read_bao_csv(bao_csv)
            c0 = compute_c0_zero_at_z0()
            bounds = compute_regime_boundaries_from_grid(
                zmin=0.0, zmax=1.5, ngrid=10000,
                quantiles=(1/3, 2/3), c0=c0,
            )
            zs = np.array([p.z for p in points], dtype=float)
            svals = s_hat_fn(zs, c0=c0)

            zmin, zmax = 0.0, 1.5
            perm = permutation_test_mean_distance(
                points=points, s_at_points=svals, boundaries=bounds,
                nperm=50000, seed=1337,
                z_range=(zmin, zmax), c0=c0,
            )
            sign = sign_coherence_transition_latent(points, svals, bounds)
            n_sign, k_sign = int(sign["n"]), int(sign["npos"])
            from math import comb as _comb
            p_binom = (sum(_comb(n_sign, i) * 0.5**n_sign
                           for i in range(k_sign, n_sign + 1))
                       if n_sign > 0 else float("nan"))

            # Raw metrics for downstream correlation analysis
            distances = [distance_to_nearest_boundary(float(sv), bounds)
                         for sv in svals]

            # Boundary-proximate points with label
            boundary_hits = []
            for p, sv, d in zip(points, svals, distances):
                if d < 0.05:
                    blabel = nearest_boundary_label(float(sv), bounds)
                    boundary_hits.append({
                        "name": p.name, "z": p.z, "dist": round(d, 6),
                        "boundary": blabel, "s_hat": round(float(sv), 6),
                    })

            null_std = perm.get("null_std", 0.0)
            primary_is_degenerate = (
                abs(perm["t_obs"] - perm["null_median"]) < 1e-6
                and null_std < 1e-6
            )

            output["axiom0"] = {
                "n_points": len(points),
                "primary_p": perm["p_value"],
                "primary_t_obs": perm["t_obs"],
                "primary_null_median": perm["null_median"],
                "primary_null_std": null_std,
                "primary_method": perm.get("method", "randomise_z_uniform"),
                "primary_is_degenerate": primary_is_degenerate,
                "secondary_sign_frac": sign["frac_pos"],
                "secondary_p_binomial": p_binom,
                "secondary_n": n_sign,
                "secondary_npos": k_sign,
                "s_flow_trans": bounds.s_flow_trans,
                "s_trans_latent": bounds.s_trans_latent,
                "mean_boundary_distance": float(np.mean(distances)),
                "min_boundary_distance": float(np.min(distances)),
                "n_transition_latent": n_sign,
                "boundary_hits": boundary_hits,
            }
            logger.info(f"  Primary p={perm['p_value']:.4f} "
                         f"(degenerate={primary_is_degenerate}), "
                         f"sign {k_sign}/{n_sign}={sign['frac_pos']:.3f} "
                         f"(binom p={p_binom:.4f})")
    except Exception as e:
        logger.warning(f"  Axiom 0 skipped: {type(e).__name__}: {e}")

    return output


def _send_signal_notification(output: dict, significance: float):
    """Send email if signal exceeds NOTIFY_SIGMA_THRESHOLD."""
    to_addr = os.environ.get("NOTIFY_EMAIL_TO", "")
    if not to_addr:
        return
    threshold = float(os.environ.get("NOTIFY_SIGMA_THRESHOLD", "2.0"))
    if significance < threshold:
        return

    import smtplib
    from email.mime.text import MIMEText

    from_addr = os.environ.get("NOTIFY_EMAIL_FROM", "efc-daemon@symbiose.local")
    smtp_host = os.environ.get("NOTIFY_SMTP_HOST", "localhost")
    smtp_port = int(os.environ.get("NOTIFY_SMTP_PORT", "587"))
    smtp_user = os.environ.get("NOTIFY_SMTP_USER", "")
    smtp_pass = os.environ.get("NOTIFY_SMTP_PASS", "")

    a_m = output.get("alpha_mean", 0)
    a_s = output.get("alpha_std", 0)
    daic = output.get("daic", 0)

    subject = f"[EFC NUTS] α = {a_m:.3f}±{a_s:.3f} ({significance:.2f}σ) — ΔAIC={daic:+.2f}"
    body = f"""EFC NUTS Daemon — Signal Alert

Cycle: {output.get('cycle_id', '?')}
Sampler: nuts (GPU)

α = {a_m:.3f} ± {a_s:.3f}  ({significance:.2f}σ)
ΔAIC = {daic:+.2f}
n_eff_min = {output.get('n_eff_min', 0):.0f}
r_hat_max = {output.get('r_hat_max', 0):.4f}

---
Threshold: {threshold}σ
Automated message from gpu_nuts_daemon.
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
        logger.info(f"  Signal notification sent to {to_addr}")
    except Exception as e:
        logger.warning(f"  Email notification failed: {type(e).__name__}: {e}")


def run_diagnostics(
    data,
    num_warmup: int = 300,
    num_samples: int = 1000,
    num_chains: int = 2,
    seed: int = 42,
    target_accept: float = 0.8,
    growth_path: str = None,
    posterior_chain = None,
    baseline_alpha_sig: float = 0.0,
) -> dict:
    """Run N1/N2/T7/N3/N4/N5/N6/N7/D2 diagnostics via NUTS. Returns diagnostics dict."""
    from efc_inference.runs.jax_efc_nuts import run_n1_nuts, run_n2_nuts, run_t7_nuts, run_n3_nuts, run_n3_aeff_nuts, run_n4_nuts, run_n5_nuts, run_n6_nuts, run_n7_nuts

    if growth_path is None:
        growth_path = str(WORKER_DIR / "efc_inference/data/growth/fs8_extended.csv")

    logger.info("=== RUNNING NUTS DIAGNOSTICS (N1 + N2 + T7 + N3 + N4 + N5 + N6 + N7) ===")
    t0 = time.time()

    # N1: rd diagnostic
    logger.info("--- N1: rd diagnostic ---")
    n1 = run_n1_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                     num_chains=num_chains, seed=seed, target_accept=target_accept)
    logger.info(f"  N1 verdict: {n1['verdict']} ({n1['total_time_seconds']:.0f}s)")

    # N2: sigma8 sweep
    logger.info("--- N2: sigma8 sweep ---")
    n2 = run_n2_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                     num_chains=num_chains, seed=seed, target_accept=target_accept)
    logger.info(f"  N2 verdict: {n2['verdict']} ({n2['total_time_seconds']:.0f}s)")

    # T7: leave-one-out
    logger.info("--- T7: leave-one-out ---")
    t7 = run_t7_nuts(data, growth_path=growth_path,
                     num_warmup=min(num_warmup, 200), num_samples=min(num_samples, 800),
                     num_chains=num_chains, seed=seed, target_accept=target_accept)
    logger.info(f"  T7 verdict: {t7['verdict']} — {t7['pass_count']}/{t7['n_total']} "
                f"({t7['total_time_seconds']:.0f}s)")

    # N3: gate freedom with A_eff reparameterization (v2)
    logger.info("--- N3-AEFF: gate freedom (A_eff reparameterized) ---")
    try:
        n3 = run_n3_aeff_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                              num_chains=num_chains, seed=seed, target_accept=target_accept)
        logger.info(f"  N3-AEFF verdict: {n3['verdict']} ({n3['total_time_seconds']:.0f}s)")
    except Exception as e:
        logger.error(f"  N3 failed: {type(e).__name__}: {e}")
        n3 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # N4: modified Poisson (μ≠1)
    logger.info("--- N4: modified Poisson (μ≠1) ---")
    try:
        n4 = run_n4_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                         num_chains=num_chains, seed=seed, target_accept=target_accept)
        logger.info(f"  N4 verdict: {n4['verdict']} ({n4['total_time_seconds']:.0f}s)")
    except Exception as e:
        logger.error(f"  N4 failed: {type(e).__name__}: {e}")
        n4 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # N5: sound horizon prior sweep (D2a)
    logger.info("--- N5: sound horizon prior sweep (D2a) ---")
    try:
        n5 = run_n5_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                         num_chains=num_chains, seed=seed, target_accept=target_accept)
        logger.info(f"  N5 verdict: {n5['verdict']} ({n5['total_time_seconds']:.0f}s)")
    except Exception as e:
        logger.error(f"  N5 failed: {type(e).__name__}: {e}")
        n5 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # N6: EFC sound horizon (D2b — post-fit, no MCMC)
    n6 = {"verdict": "SKIPPED", "reason": "no posterior chain"}
    if posterior_chain is not None:
        logger.info("--- N6: EFC sound horizon (D2b) ---")
        try:
            # Convert chain (n_samples, 4) to dict format for run_n6_nuts
            # posterior_chain columns: [Om, H0, s8, alpha]
            # run_n6_nuts expects non-centered z-space samples
            # Reverse: z_Om = (Om - 0.30)/0.05, z_H0 = (H0 - 67.0)/5.0
            fake_samples = {
                "z_Om": (posterior_chain[:, 0] - 0.30) / 0.05,
                "z_H0": (posterior_chain[:, 1] - 67.0) / 5.0,
            }
            n6 = run_n6_nuts(posterior_samples=fake_samples)
            logger.info(f"  N6 verdict: {n6['verdict']} ({n6['total_time_seconds']:.1f}s)")
        except Exception as e:
            logger.error(f"  N6 failed: {type(e).__name__}: {e}")
            n6 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}
    else:
        logger.info("--- N6: skipped (no posterior chain) ---")

    # N7: power-law gate (Lorentzian-derived, n=2 from L0)
    logger.info("--- N7: power-law gate (n=2, Lorentzian) ---")
    try:
        n7 = run_n7_nuts(data, num_warmup=num_warmup, num_samples=num_samples,
                         num_chains=num_chains, seed=seed)
        logger.info(f"  N7 verdict: {n7['verdict']} ({n7['total_time_seconds']:.0f}s)")
    except Exception as e:
        logger.error(f"  N7 failed: {type(e).__name__}: {e}")
        n7 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # N7-GRAV: global parameter-lock cross-probe ("Domstolen")
    # GRAV-locked G_eff in growth source. All frozen: C=2.32, k_lambda=0.0014
    logger.info("--- N7-GRAV: GRAV-locked cross-probe ('Domstolen') ---")
    try:
        from efc_inference.runs.jax_efc_nuts import run_n7_grav_lock_nuts
        n7_grav_result = run_n7_grav_lock_nuts(
            data, num_warmup=num_warmup, num_samples=num_samples,
            num_chains=num_chains, seed=seed, target_accept=target_accept,
        )
        n7_grav = {
            "verdict": n7_grav_result.verdict or "UNKNOWN",
            "alpha_mean": n7_grav_result.alpha_mean,
            "alpha_std": n7_grav_result.alpha_std,
            "alpha_sig": n7_grav_result.alpha_significance,
            "alpha_p_negative": n7_grav_result.alpha_p_negative,
            "daic": n7_grav_result.daic,
            "dbic": n7_grav_result.dbic,
            "n_eff_min": n7_grav_result.n_eff_min,
            "r_hat_max": n7_grav_result.r_hat_max,
            "total_time_seconds": n7_grav_result.time_efc + n7_grav_result.time_lcdm,
        }
        logger.info(f"  N7-GRAV verdict: {n7_grav['verdict']} "
                     f"(α={n7_grav['alpha_mean']:.3f}±{n7_grav['alpha_std']:.3f}, "
                     f"{n7_grav['alpha_sig']:.2f}σ)")
    except Exception as e:
        logger.error(f"  N7-GRAV failed: {type(e).__name__}: {e}")
        n7_grav = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # D2: self-consistent sound horizon (replaces r_d proxy with r_d(Ωm, H0))
    d2 = {"verdict": "SKIPPED", "reason": "not enabled"}
    logger.info("--- D2: self-consistent sound horizon ---")
    try:
        from efc_inference.runs.jax_efc_nuts import run_d2_nuts
        d2 = run_d2_nuts(
            data=data,
            baseline_alpha_sig=baseline_alpha_sig,
            num_warmup=num_warmup,
            num_samples=num_samples,
            num_chains=num_chains,
            seed=seed + 2000,
            target_accept=target_accept,
        )
        logger.info(f"  D2 verdict: {d2['verdict']} "
                     f"(α={d2['alpha_mean']:.3f}±{d2['alpha_std']:.3f}, "
                     f"{d2['alpha_sig']:.2f}σ, r_d={d2['rd_mean']:.1f}±{d2['rd_std']:.1f} Mpc)")
    except Exception as e:
        logger.error(f"  D2 failed: {type(e).__name__}: {e}")
        d2 = {"verdict": "ERROR", "error": f"{type(e).__name__}: {str(e)[:300]}"}

    # VariantG: Constitutive law growth diagnostic — 3 pre-registered k_eff scenarios
    # G10 (k_eff=0.10, nulltest), G02 (k_eff=0.02, plausible), G01 (k_eff=0.01, strong)
    vg_scenarios = {}
    logger.info("--- VariantG: Constitutive law growth diagnostic (3 scenarios) ---")
    for vg_scenario in ["G10", "G02", "G01"]:
        try:
            from efc_inference.runs.jax_efc_nuts import run_variant_g_nuts
            vg_result = run_variant_g_nuts(
                data=data,
                num_warmup=num_warmup,
                num_samples=num_samples,
                num_chains=num_chains,
                seed=seed + 3000,
                target_accept=target_accept,
                scenario=vg_scenario,
            )
            # Flatten mu_diagnostics from nested dict
            mu_diag = vg_result.get("mu_diagnostics", {})
            vg_flat = {
                "verdict": vg_result.get("verdict", "UNKNOWN"),
                "scenario": vg_scenario,
                "k_eff": vg_result.get("k_eff", 0.1),
                "dll_total": vg_result.get("dll_total", 0),
                "daic_same_k": vg_result.get("daic_same_k", 0),
                "s8_vg_mean": vg_result.get("s8_vg_mean", 0),
                "s8_vg_std": vg_result.get("s8_vg_std", 0),
                "s8_lcdm_mean": vg_result.get("s8_lcdm_mean", 0),
                "s8_lcdm_std": vg_result.get("s8_lcdm_std", 0),
                "s8_shift": vg_result.get("s8_shift", 0),
                "om_vg_mean": vg_result.get("om_vg_mean", 0),
                "h0_vg_mean": vg_result.get("h0_vg_mean", 0),
                "mu_min": mu_diag.get("mu_min", 1.0),
                "mu_max": mu_diag.get("mu_max", 1.0),
                "mu_amp": vg_result.get("mu_amp", 0.0),
                "mu_span": vg_result.get("mu_span", 0.0),
                "mu_z0_3": mu_diag.get("mu_z0.3", 1.0),
                "mu_z0_5": mu_diag.get("mu_z0.5", 1.0),
                "mu_z0_7": mu_diag.get("mu_z0.7", 1.0),
                "mu_z1_0": mu_diag.get("mu_z1.0", 1.0),
                "mu_z1_5": mu_diag.get("mu_z1.5", 1.0),
                "mu_z2_3": mu_diag.get("mu_z2.3", 1.0),
                "chi_c": mu_diag.get("chi_c", 0),
                "epsilon_eff": mu_diag.get("epsilon_eff", 0),
                "screen_k_eff": mu_diag.get("screen_k_eff", 0),
                "C_grav": mu_diag.get("C_grav", 2.32),
                "k_lambda": mu_diag.get("k_lambda", 0.0014),
                "hill_n": 2,
                "n_eff_min": vg_result.get("n_eff_min", 0),
                "r_hat_max": vg_result.get("r_hat_max", 99.0),
                "total_time_seconds": vg_result.get("total_time_seconds", 0),
            }
            vg_scenarios[vg_scenario] = vg_flat
            logger.info(f"  {vg_scenario} (k_eff={vg_flat['k_eff']}): {vg_flat['verdict']} "
                         f"(ΔlogL={vg_flat['dll_total']:+.4f}, "
                         f"μ_amp={vg_flat['mu_amp']:.5f})")
        except Exception as e:
            logger.error(f"  VariantG {vg_scenario} failed: {type(e).__name__}: {e}")
            vg_scenarios[vg_scenario] = {"verdict": "ERROR", "scenario": vg_scenario,
                                          "error": f"{type(e).__name__}: {str(e)[:300]}"}

    total_time = time.time() - t0
    logger.info(f"  Total diagnostics time: {total_time:.0f}s ({total_time/60:.1f}min)")

    return {
        "n1": n1,
        "n2": n2,
        "t7": t7,
        "n3": n3,
        "n4": n4,
        "n5": n5,
        "n6": n6,
        "n7": n7,
        "n7_grav": n7_grav,
        "d2": d2,
        "vg": vg_scenarios,
        "total_time_seconds": round(total_time, 1),
    }


def save_result(result: dict) -> Path:
    """Save result to JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / f"{result['cycle_id']}.json"
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    logger.info(f"Result saved: {path}")
    return path


def main():
    parser = argparse.ArgumentParser(description="GPU NUTS Daemon")
    parser.add_argument("--mode", default="once", choices=["once", "daemon"])
    parser.add_argument("--interval", type=int, default=21600, help="Seconds between cycles (daemon mode)")
    parser.add_argument("--warmup", type=int, default=int(os.environ.get("NUTS_WARMUP", "500")))
    parser.add_argument("--samples", type=int, default=int(os.environ.get("NUTS_SAMPLES", "2000")))
    parser.add_argument("--chains", type=int, default=int(os.environ.get("NUTS_CHAINS", "2")))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    logger.info(f"GPU NUTS Daemon — mode={args.mode}, interval={args.interval}s")
    logger.info(f"  warmup={args.warmup}, samples={args.samples}, chains={args.chains}, seed={args.seed}")

    while True:
        if not _acquire_lock():
            if args.mode == "once":
                sys.exit(1)
            time.sleep(60)
            continue

        try:
            result = run_nuts_cycle(
                num_warmup=args.warmup,
                num_samples=args.samples,
                num_chains=args.chains,
                seed=args.seed,
            )
            save_result(result)

            # Signal success
            significance = result["alpha_significance"]
            logger.info(f"Cycle complete: α={result['alpha_mean']:.3f}±{result['alpha_std']:.3f} ({significance:.2f}σ)")

        except Exception as e:
            logger.error(f"Cycle failed: {type(e).__name__}: {e}")
            # Save error
            error_result = {
                "cycle_id": f"nuts_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "sampler": "nuts",
                "status": "error",
                "error": f"{type(e).__name__}: {str(e)[:500]}",
            }
            save_result(error_result)
        finally:
            _release_lock()

        if args.mode == "once":
            break

        if args.interval > 0:
            logger.info(f"Sleeping {args.interval}s ({args.interval/3600:.1f}h) until next cycle...")
            time.sleep(args.interval)
        else:
            logger.info("Continuous mode — starting next cycle in 30s...")
            time.sleep(30)


if __name__ == "__main__":
    main()
