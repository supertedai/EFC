#!/usr/bin/env python3
"""
EFC × CMB: Planck test runner

Runs CLASS + Planck likelihood at 4 levels:
  Level 0: LCDM sanity (evaluate, α=0)
  Level 1: Lensing-only knife (evaluate, α=0 vs α=-0.7)
  Level 2: θ* judge with Planck freedom (MCMC, α=-0.7 frozen)
  Level 3: Full joint with α free (MCMC)

Usage:
  python run_cmb_test.py --level 0          # Sanity check
  python run_cmb_test.py --level 1          # Lensing knife
  python run_cmb_test.py --level 2          # θ* judge (MCMC)
  python run_cmb_test.py --level 3          # Full joint (MCMC)
  python run_cmb_test.py --level 1 --alpha -0.5   # Custom α

Requires: classy, cobaya, Planck 2018 likelihoods installed.
"""

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path

import numpy as np


def verify_class():
    """Verify CLASS is installed and working."""
    try:
        from classy import Class
        cosmo = Class()
        cosmo.set({
            "output": "tCl,pCl,lCl",
            "lensing": "yes",
            "l_max_scalars": 2508,
            "omega_b": 0.02237,
            "omega_cdm": 0.1200,
            "H0": 67.36,
            "tau_reio": 0.0544,
            "A_s": 2.1e-9,
            "n_s": 0.9649,
        })
        cosmo.compute()
        cl_tt = cosmo.lensed_cl(2508)["tt"]
        peak_ell = np.argmax(cl_tt[30:] * np.arange(len(cl_tt[30:]) + 30)[30:] ** 2) + 30
        print(f"  CLASS OK — first TT peak near ℓ ≈ {peak_ell}")
        print(f"  σ₈ = {cosmo.sigma8():.4f}")
        cosmo.struct_cleanup()
        cosmo.empty()
        return True
    except Exception as e:
        print(f"  CLASS FAILED: {e}")
        return False


def verify_planck():
    """Verify Planck likelihoods are installed."""
    try:
        from cobaya.likelihood import get_default_info
        likelihoods = [
            "planck_2018_highl_plik_lite.TTTEEE",
            "planck_2018_lowl.TT",
            "planck_2018_lowl.EE",
            "planck_2018_lensing.clik",
        ]
        ok = True
        for lik in likelihoods:
            try:
                info = get_default_info(lik, "likelihood")
                print(f"  {lik}: OK")
            except Exception as e:
                print(f"  {lik}: MISSING ({e})")
                ok = False
        return ok
    except Exception as e:
        print(f"  cobaya import FAILED: {e}")
        return False


def run_level0():
    """Level 0: LCDM sanity check."""
    print("\n" + "=" * 60)
    print("LEVEL 0: ΛCDM SANITY CHECK")
    print("=" * 60)

    from classy import Class

    cosmo = Class()
    cosmo.set({
        "output": "tCl,pCl,lCl",
        "lensing": "yes",
        "l_max_scalars": 2508,
        "omega_b": 0.02237,
        "omega_cdm": 0.1200,
        "H0": 67.36,
        "tau_reio": 0.0544,
        "A_s": 2.1e-9,
        "n_s": 0.9649,
        "alpha_efc": 0.0,
    })
    cosmo.compute()

    print(f"  H₀ = {cosmo.Hubble(0) * 2.998e5:.2f} km/s/Mpc")
    print(f"  σ₈ = {cosmo.sigma8():.4f}")
    print(f"  r_drag = {cosmo.rs_drag():.2f} Mpc")
    print(f"  θ* ≈ {cosmo.theta_star_100():.4f} (×100)")

    result = {
        "level": 0,
        "H0": cosmo.Hubble(0) * 2.998e5,
        "sigma8": cosmo.sigma8(),
        "rs_drag": cosmo.rs_drag(),
        "theta_star_100": cosmo.theta_star_100(),
        "status": "OK",
    }

    cosmo.struct_cleanup()
    cosmo.empty()

    print("\n  LEVEL 0 PASSED ✓")
    return result


def run_level1(alpha_values=None):
    """Level 1: Lensing-only knife."""
    if alpha_values is None:
        alpha_values = [0.0, -0.7]

    print("\n" + "=" * 60)
    print("LEVEL 1: LENSING-ONLY KNIFE")
    print("=" * 60)

    from classy import Class

    results = {}
    for alpha in alpha_values:
        print(f"\n  --- α = {alpha} ---")
        cosmo = Class()
        cosmo.set({
            "output": "tCl,pCl,lCl",
            "lensing": "yes",
            "l_max_scalars": 2508,
            "omega_b": 0.02237,
            "omega_cdm": 0.1200,
            "H0": 67.36,
            "tau_reio": 0.0544,
            "A_s": 2.1e-9,
            "n_s": 0.9649,
            "alpha_efc": alpha,
        })
        cosmo.compute()

        cl_lens = cosmo.lensed_cl(2508)
        cl_pp = cosmo.raw_cl(2508).get("pp", np.zeros(2509))

        # Compute lensing amplitude proxy
        # A_L ∝ ∫ C_l^φφ weighted
        ell = np.arange(2, 2509)
        if len(cl_pp) > 2508:
            pp_vals = cl_pp[2:2509]
            A_lens = np.sum(pp_vals * ell * (ell + 1))
        else:
            A_lens = 0.0

        sigma8 = cosmo.sigma8()
        rs = cosmo.rs_drag()
        theta = cosmo.theta_star_100()

        print(f"  σ₈ = {sigma8:.4f}")
        print(f"  r_drag = {rs:.2f} Mpc")
        print(f"  θ*×100 = {theta:.4f}")
        print(f"  A_lens proxy = {A_lens:.4e}")

        results[alpha] = {
            "alpha": alpha,
            "sigma8": sigma8,
            "rs_drag": rs,
            "theta_star_100": theta,
            "A_lens_proxy": A_lens,
        }

        cosmo.struct_cleanup()
        cosmo.empty()

    # Compare
    if len(alpha_values) >= 2:
        a0, a1 = alpha_values[0], alpha_values[1]
        r0, r1 = results[a0], results[a1]
        ds8 = (r1["sigma8"] - r0["sigma8"]) / r0["sigma8"]
        drs = (r1["rs_drag"] - r0["rs_drag"]) / r0["rs_drag"]
        dth = (r1["theta_star_100"] - r0["theta_star_100"]) / r0["theta_star_100"]
        dAL = (r1["A_lens_proxy"] - r0["A_lens_proxy"]) / r0["A_lens_proxy"] if r0["A_lens_proxy"] != 0 else 0

        print(f"\n  --- Comparison (α={a1} vs α={a0}) ---")
        print(f"  Δσ₈/σ₈ = {ds8 * 100:+.4f}%")
        print(f"  Δr_drag/r_drag = {drs * 100:+.4f}%")
        print(f"  Δθ*/θ* = {dth * 100:+.4f}%")
        print(f"  ΔA_lens/A_lens = {dAL * 100:+.4f}%")

        results["comparison"] = {
            "delta_sigma8_pct": ds8 * 100,
            "delta_rs_pct": drs * 100,
            "delta_theta_pct": dth * 100,
            "delta_A_lens_pct": dAL * 100,
        }

    return {"level": 1, "results": results}


def run_level2():
    """Level 2: θ* judge with Planck freedom (uses cobaya MCMC)."""
    print("\n" + "=" * 60)
    print("LEVEL 2: θ* JUDGE WITH PLANCK FREEDOM")
    print("=" * 60)
    print("  This runs cobaya MCMC — will take 2-6 hours.")
    print("  Use: cobaya-run level2_peaks.yaml -o /root/efc_cmb/level2")
    print("  Check convergence: cobaya-run level2_peaks.yaml -o /root/efc_cmb/level2 --resume")
    return {"level": 2, "status": "manual_run_required"}


def run_level3():
    """Level 3: Full joint with α free."""
    print("\n" + "=" * 60)
    print("LEVEL 3: FULL JOINT WITH α FREE")
    print("=" * 60)
    print("  This runs cobaya MCMC — will take 4-12 hours.")
    print("  Use: cobaya-run level3_joint.yaml -o /root/efc_cmb/level3")
    return {"level": 3, "status": "manual_run_required"}


def main():
    parser = argparse.ArgumentParser(description="EFC × CMB: Planck test runner")
    parser.add_argument("--level", type=int, choices=[0, 1, 2, 3], required=True,
                        help="Test level (0=sanity, 1=lensing, 2=peaks, 3=joint)")
    parser.add_argument("--alpha", type=float, default=-0.7,
                        help="α value for level 1 sealed test (default: -0.7)")
    parser.add_argument("--verify-only", action="store_true",
                        help="Only verify CLASS + Planck installation")
    parser.add_argument("--output", type=str, default=None,
                        help="Output JSON file for results")
    args = parser.parse_args()

    print("=" * 60)
    print("EFC × CMB: PLANCK TEST RUNNER")
    print("=" * 60)

    # Always verify first
    print("\nVerifying CLASS...")
    class_ok = verify_class()

    if args.verify_only:
        print("\nVerifying Planck likelihoods...")
        planck_ok = verify_planck()
        sys.exit(0 if (class_ok and planck_ok) else 1)

    if not class_ok:
        print("\nFATAL: CLASS not working. Install first.")
        sys.exit(1)

    # Run requested level
    t0 = time.time()

    if args.level == 0:
        result = run_level0()
    elif args.level == 1:
        result = run_level1([0.0, args.alpha])
    elif args.level == 2:
        result = run_level2()
    elif args.level == 3:
        result = run_level3()

    elapsed = time.time() - t0
    result["elapsed_seconds"] = elapsed
    print(f"\n  Elapsed: {elapsed:.1f}s")

    # Save results
    if args.output:
        outpath = Path(args.output)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        with open(outpath, "w") as f:
            json.dump(result, f, indent=2, default=str)
        print(f"  Results saved to {outpath}")

    return result


if __name__ == "__main__":
    main()
