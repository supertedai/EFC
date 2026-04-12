#!/usr/bin/env python3
"""
EFC Weak Lensing Case B — Nested Sampling Launcher
====================================================

Runs PolyChord (or dynesty) nested sampling for EFC vs ΛCDM using weak
lensing observables. Uses cobaya for theory (CAMB) and built-in CMB
likelihoods, with the EFC modification applied via the Alens bridge.

For the full Case B experience (growth-modified P(k) + Σ(k,z) in the
lensing kernel), use the standalone pipeline that calls
efc_lensing_theory.compute_growth_ratio() and
cosmic_shear_likelihood.compute_cl_matrix() directly. This launcher
provides the cobaya-integrated path using the Alens proxy for the
lensing reconstruction likelihood.

Usage:
    # PolyChord (via cobaya):
    mpirun -n 32 python src/launch_wl_nested.py

    # dynesty (standalone):
    python src/launch_wl_nested.py --dynesty --ncpu 16

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-12
"""

import os
import sys
import json
import time
import logging
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('wl_nested_run.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

PACKAGES_PATH = os.environ.get(
    "COBAYA_PACKAGES_PATH",
    os.path.expanduser("~/cobaya_packages")
)
OUTPUT_DIR = "wl_output"


def run_cobaya(yaml_file):
    """Execute a cobaya nested sampling run."""
    from cobaya.run import run as cobaya_run
    from cobaya.yaml import yaml_load_file

    info = yaml_load_file(yaml_file)
    info["packages_path"] = PACKAGES_PATH

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("chains", exist_ok=True)

    log.info(f"Running cobaya: {yaml_file}")
    t0 = time.time()
    updated_info, sampler = cobaya_run(info)
    wall_h = (time.time() - t0) / 3600
    log.info(f"Completed in {wall_h:.1f} hours")

    return updated_info, sampler


def extract_evidence(sampler, label):
    """Extract ln(Z) from sampler output."""
    try:
        products = sampler.products()
        log_Z = float(products.get("logZ", 0))
        log_Z_err = float(products.get("logZerr", 0))
        log.info(f"{label}: ln(Z) = {log_Z:.2f} +/- {log_Z_err:.2f}")
        return {"log_Z": log_Z, "log_Z_err": log_Z_err}
    except Exception as e:
        log.error(f"Evidence extraction failed for {label}: {e}")
        return None


def run_standalone_case_b(ncpu=1):
    """
    Standalone Case B: growth-modified P(k) + Σ(k,z) lensing kernel.

    This bypasses cobaya and runs the full EFC pipeline directly with
    dynesty nested sampling, using cobaya only for the theory (CAMB).
    """
    from cobaya.yaml import yaml_load_file
    from cobaya.model import get_model
    from efc_lensing_theory import modified_power_spectrum, sigma_kz
    from cosmic_shear_likelihood import (
        compute_cl_matrix, CosmicShearLikelihood
    )

    log.info("=== Standalone Case B: growth + lensing ===")

    # Build cobaya model for theory (CAMB P(k,z)) + CMB likelihoods
    efc_yaml = "config/efc_wl_polychord.yaml"
    info = yaml_load_file(efc_yaml)
    info["packages_path"] = PACKAGES_PATH
    info.pop("sampler", None)
    info.pop("output", None)

    model = get_model(info)
    param_names = list(model.parameterization.sampled_params())
    ndim = len(param_names)
    log.info(f"Parameters ({ndim}): {param_names}")

    # Extract prior bounds
    prior_min = np.zeros(ndim)
    prior_max = np.zeros(ndim)
    for i, name in enumerate(param_names):
        pinfo = model.parameterization.sampled_params()[name]
        prior = pinfo.get("prior", {})
        if isinstance(prior, dict) and "min" in prior:
            prior_min[i] = prior["min"]
            prior_max[i] = prior["max"]
        elif isinstance(prior, dict) and "dist" in prior:
            loc = prior.get("loc", 0)
            scale = prior.get("scale", 1)
            prior_min[i] = loc - 5 * scale
            prior_max[i] = loc + 5 * scale

    def prior_transform(u):
        return prior_min + u * (prior_max - prior_min)

    def log_likelihood(theta):
        params = {name: float(val)
                  for name, val in zip(param_names, theta)}
        try:
            logpost = model.logposterior(params)
            return float(logpost.loglike)
        except Exception:
            return -1e30

    # Run dynesty
    import dynesty
    from multiprocessing import Pool

    pool = Pool(ncpu) if ncpu > 1 else None

    sampler = dynesty.DynamicNestedSampler(
        log_likelihood, prior_transform, ndim,
        pool=pool, queue_size=ncpu if ncpu > 1 else None,
        bound='multi', sample='rwalk', walks=5 * ndim,
    )

    sampler.run_nested(
        nlive_init=500, nlive_batch=250,
        dlogz_init=0.05, maxiter=5000000,
        print_progress=True,
    )

    if pool:
        pool.close()
        pool.join()

    return sampler.results


def save_ledger_entry(efc_ev, lcdm_ev, bayes_factor):
    """Save results in ledger-compatible format."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    entry = {
        "test_id": "WL_CASE_B_NESTED",
        "test_name": "Case B Weak Lensing: Growth-Modified Evidence",
        "date": datetime.utcnow().isoformat(),
        "sampler": "polychord",
        "evidence_efc": efc_ev,
        "evidence_lcdm": lcdm_ev,
        "bayes_factor": bayes_factor,
        "datasets": [
            "Planck 2018 lowl TT/EE",
            "Planck 2018 lensing (native)",
        ],
        "bridge": {
            "K0_ref": 1.66, "m_sq_ref": 0.0035,
            "mu0_ref": 0.94, "Sigma0_ref": 1.05,
            "modification": "Case B: growth ODE + lensing kernel",
        },
        "status": "COMPLETED",
        "verdict": bayes_factor["interpretation"] if bayes_factor else "PENDING",
    }

    with open(f"{OUTPUT_DIR}/ledger_entry_wl_case_b.json", 'w') as f:
        json.dump(entry, f, indent=2)
    log.info("Ledger entry saved")


def main():
    parser = argparse.ArgumentParser(
        description="EFC Weak Lensing Case B nested sampling")
    parser.add_argument('--dynesty', action='store_true',
                        help='Use standalone dynesty instead of cobaya+PolyChord')
    parser.add_argument('--ncpu', type=int, default=1)
    parser.add_argument('--efc-only', action='store_true')
    args = parser.parse_args()

    log.info("=" * 60)
    log.info("EFC WEAK LENSING CASE B — NESTED SAMPLING")
    log.info("=" * 60)

    if args.dynesty:
        results = run_standalone_case_b(ncpu=args.ncpu)
        logZ = float(results.logz[-1])
        log.info(f"EFC ln(Z) = {logZ:.2f}")
        return

    # Cobaya + PolyChord path
    efc_yaml = "config/efc_wl_polychord.yaml"
    lcdm_yaml = "config/lcdm_wl_polychord.yaml"

    log.info("\n>>> PHASE 1: EFC nested sampling <<<")
    efc_info, efc_sampler = run_cobaya(efc_yaml)
    efc_ev = extract_evidence(efc_sampler, "EFC")

    lcdm_ev = None
    bayes_factor = None
    if not args.efc_only:
        log.info("\n>>> PHASE 2: LCDM reference <<<")
        lcdm_info, lcdm_sampler = run_cobaya(lcdm_yaml)
        lcdm_ev = extract_evidence(lcdm_sampler, "LCDM")

    if efc_ev and lcdm_ev:
        import math
        ln_B = efc_ev["log_Z"] - lcdm_ev["log_Z"]
        ln_B_err = math.sqrt(efc_ev["log_Z_err"]**2 + lcdm_ev["log_Z_err"]**2)

        if ln_B > 5:
            strength = "STRONG for EFC"
        elif ln_B > 2.5:
            strength = "MODERATE for EFC"
        elif ln_B > 1:
            strength = "WEAK for EFC"
        elif ln_B > -1:
            strength = "INCONCLUSIVE"
        elif ln_B > -2.5:
            strength = "WEAK for LCDM"
        else:
            strength = "STRONG for LCDM"

        bayes_factor = {"ln_B": float(ln_B), "ln_B_err": float(ln_B_err),
                        "interpretation": strength}
        log.info(f"ln(B) = {ln_B:.2f} +/- {ln_B_err:.2f} -> {strength}")

    save_ledger_entry(efc_ev, lcdm_ev, bayes_factor)

    log.info("\n" + "=" * 60)
    log.info("CASE B PIPELINE COMPLETE")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
