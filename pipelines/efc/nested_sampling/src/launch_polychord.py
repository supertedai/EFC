#!/usr/bin/env python3
"""
EFC PolyChord Nested Sampling — Launch Script
==============================================

Runs full Bayesian inference for EFC vs ΛCDM using PolyChord via cobaya.
Produces: full posterior, ln(Z) evidence, corner plots, Bayes factor,
and a ledger-compatible JSON entry.

Both EFC and ΛCDM runs use IDENTICAL likelihoods, priors (for shared
parameters), and theory settings. Only difference: EFC samples K0 and
m_sq; ΛCDM does not.

Usage:
    # Full MGCAMB run (requires MGCAMB fork):
    mpirun -n 32 python src/launch_polychord.py

    # Reduced run (vanilla CAMB, sandbox-compatible):
    mpirun -n 32 python src/launch_polychord.py --reduced

    # Or via cobaya directly:
    cobaya-run config/efc_polychord.yaml -f

Requirements:
    pip install cobaya pypolychord getdist matplotlib
    cobaya-install config/efc_polychord.yaml --packages-path ~/cobaya_packages

Author: Morten Magnusson / Symbiose Research
Date:   2026-04-12
"""

import os
import sys
import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('polychord_run.log'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

PACKAGES_PATH = os.environ.get(
    "COBAYA_PACKAGES_PATH",
    os.path.expanduser("~/cobaya_packages")
)
OUTPUT_DIR = "polychord_output"


def check_prerequisites():
    """Verify all dependencies are available."""
    missing = []
    for pkg, name in [("cobaya", "cobaya"), ("camb", "camb"),
                      ("getdist", "getdist")]:
        try:
            mod = __import__(pkg)
            log.info(f"{name} {getattr(mod, '__version__', 'OK')} found")
        except ImportError:
            missing.append(name)

    try:
        import pypolychord
        log.info("pypolychord found")
    except ImportError:
        log.warning("pypolychord not found — cobaya may install it")

    return missing


def run_cobaya(yaml_file):
    """Execute a cobaya nested sampling run and return (info, sampler)."""
    from cobaya.run import run as cobaya_run
    from cobaya.yaml import yaml_load_file

    info = yaml_load_file(yaml_file)
    info["packages_path"] = PACKAGES_PATH

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs("chains", exist_ok=True)

    sampler_cfg = info["sampler"]["polychord"]
    log.info("=" * 60)
    log.info(f"  Config:   {yaml_file}")
    log.info(f"  Packages: {PACKAGES_PATH}")
    log.info(f"  nlive:    {sampler_cfg.get('nlive', '?')}")
    log.info(f"  repeats:  {sampler_cfg.get('num_repeats', '?')}")
    log.info("=" * 60)

    t0 = time.time()
    updated_info, sampler = cobaya_run(info)
    wall_h = (time.time() - t0) / 3600
    log.info(f"Completed in {wall_h:.1f} hours")

    return updated_info, sampler


def extract_evidence(sampler, model_label):
    """Extract ln(Z) from PolyChord output."""
    try:
        products = sampler.products()
        log_Z = float(products.get("logZ", 0))
        log_Z_err = float(products.get("logZerr", 0))
        log.info(f"{model_label}: ln(Z) = {log_Z:.2f} +/- {log_Z_err:.2f}")
        return {"log_Z": log_Z, "log_Z_err": log_Z_err,
                "model": model_label, "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        log.error(f"Could not extract evidence for {model_label}: {e}")
        return None


def compute_bayes_factor(efc_ev, lcdm_ev):
    """ln(B) = ln(Z_EFC) - ln(Z_LCDM) with Kass & Raftery interpretation."""
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
    elif ln_B > -5:
        strength = "MODERATE for LCDM"
    else:
        strength = "STRONG for LCDM"

    result = {"ln_B": float(ln_B), "ln_B_err": float(ln_B_err),
              "interpretation": strength, "scale": "Kass & Raftery 1995"}
    log.info(f"ln(B) = {ln_B:.2f} +/- {ln_B_err:.2f} -> {strength}")
    return result


def make_corner_plots(chain_root, param_names_efc, param_names_full):
    """Generate corner/triangle plots with GetDist."""
    try:
        from getdist import plots, loadMCSamples

        samples = loadMCSamples(chain_root)

        # EFC-specific corner: K0, m_sq vs key derived
        g = plots.get_subplot_plotter()
        efc_params = [p for p in param_names_efc
                      if p in [n.name for n in samples.paramNames.names]]
        if efc_params:
            g.triangle_plot(samples, efc_params, filled=True, title_limit=1)
            g.export(f"{OUTPUT_DIR}/efc_corner_K0_msq.pdf")
            log.info("K0-m_sq corner plot saved")

        # Full corner
        g2 = plots.get_subplot_plotter()
        full_params = [p for p in param_names_full
                       if p in [n.name for n in samples.paramNames.names]]
        if full_params:
            g2.triangle_plot(samples, full_params, filled=True, title_limit=1)
            g2.export(f"{OUTPUT_DIR}/efc_full_corner.pdf")
            log.info("Full corner plot saved")

        # Parameter summary
        stats = samples.getMargeStats()
        summary = {}
        for par in samples.paramNames.names:
            m = stats.parWithName(par.name)
            if m is not None:
                summary[par.name] = {
                    "mean": float(m.mean), "std": float(m.err),
                    "lower_95": float(m.limits[1].lower) if len(m.limits) > 1 else None,
                    "upper_95": float(m.limits[1].upper) if len(m.limits) > 1 else None,
                }

        with open(f"{OUTPUT_DIR}/parameter_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        log.info("Parameter summary saved")
        return summary

    except Exception as e:
        log.error(f"Corner plot generation failed: {e}")
        return None


def save_ledger_entry(efc_ev, lcdm_ev, bayes_factor, summary, variant):
    """Save results in ledger-compatible format."""
    entry = {
        "test_id": f"MCMC_NESTED_{variant.upper()}",
        "test_name": f"Full Bayesian Evidence: EFC vs LCDM ({variant})",
        "date": datetime.utcnow().isoformat(),
        "sampler": "polychord",
        "nlive": 500,
        "evidence_efc": efc_ev,
        "evidence_lcdm": lcdm_ev,
        "bayes_factor": bayes_factor,
        "parameter_summary": summary,
        "datasets": {
            "full": ["Planck 2018 plik_lite TTTEEE + lowl + lensing.clik",
                     "DESI 2024 BAO", "Pantheon+ SNe Ia"],
            "reduced": ["Planck 2018 lowl TT/EE + lensing.native",
                        "DESI 2024 BAO", "Pantheon+ SNe Ia"],
        }[variant],
        "bridge": {
            "K0_ref": 1.66, "m_sq_ref": 0.0035,
            "mu0_ref": 0.94, "Sigma0_ref": 1.05,
            "source": "tools/cobaya_bridge/bridge_theory.py",
        },
        "status": "COMPLETED",
        "verdict": bayes_factor["interpretation"] if bayes_factor else "PENDING",
    }

    outfile = f"{OUTPUT_DIR}/ledger_entry_{variant}.json"
    with open(outfile, 'w') as f:
        json.dump(entry, f, indent=2)
    log.info(f"Ledger entry saved: {outfile}")
    return entry


def main():
    parser = argparse.ArgumentParser(
        description="EFC PolyChord nested sampling pipeline")
    parser.add_argument('--reduced', action='store_true',
                        help='Use reduced dataset (vanilla CAMB, no MGCAMB)')
    parser.add_argument('--efc-only', action='store_true',
                        help='Run EFC only (skip LCDM reference)')
    args = parser.parse_args()

    variant = "reduced" if args.reduced else "full"
    efc_yaml = f"config/efc_polychord{'_reduced' if args.reduced else ''}.yaml"
    lcdm_yaml = f"config/lcdm_polychord{'_reduced' if args.reduced else ''}.yaml"

    log.info("=" * 60)
    log.info("EFC NESTED SAMPLING PIPELINE")
    log.info(f"Variant: {variant}")
    log.info("=" * 60)

    missing = check_prerequisites()
    if "cobaya" in missing or "camb" in missing:
        log.error("Critical deps missing: pip install cobaya camb getdist")
        sys.exit(1)

    # Phase 1: EFC
    log.info("\n>>> PHASE 1: EFC nested sampling <<<")
    efc_info, efc_sampler = run_cobaya(efc_yaml)
    efc_ev = extract_evidence(efc_sampler, "EFC")

    # Phase 2: ΛCDM reference
    lcdm_ev = None
    bayes_factor = None
    if not args.efc_only:
        log.info("\n>>> PHASE 2: LCDM reference <<<")
        lcdm_info, lcdm_sampler = run_cobaya(lcdm_yaml)
        lcdm_ev = extract_evidence(lcdm_sampler, "LCDM")

    # Phase 3: Bayes factor
    if efc_ev and lcdm_ev:
        bayes_factor = compute_bayes_factor(efc_ev, lcdm_ev)

    # Phase 4: Corner plots
    chain_root = efc_info.get("output", "chains/efc_polychord")
    summary = make_corner_plots(
        chain_root,
        param_names_efc=["K0", "m_sq", "sigma8", "S8", "H0"],
        param_names_full=["ombh2", "omch2", "ns", "tau", "K0", "m_sq"],
    )

    # Phase 5: Ledger entry
    save_ledger_entry(efc_ev, lcdm_ev, bayes_factor, summary, variant)

    log.info("\n" + "=" * 60)
    log.info("PIPELINE COMPLETE")
    if efc_ev:
        log.info(f"  EFC:  ln(Z) = {efc_ev['log_Z']:.2f} +/- {efc_ev['log_Z_err']:.2f}")
    if lcdm_ev:
        log.info(f"  LCDM: ln(Z) = {lcdm_ev['log_Z']:.2f} +/- {lcdm_ev['log_Z_err']:.2f}")
    if bayes_factor:
        log.info(f"  ln(B) = {bayes_factor['ln_B']:.2f} -> {bayes_factor['interpretation']}")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
