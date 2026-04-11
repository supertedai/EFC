#!/usr/bin/env python3
"""
SPARC 175 Kill-Test Universality Analysis
==========================================
Extends Kill-Test v6 probe-2 (5 galaxies) to ALL 175 SPARC galaxies.

For each galaxy:
  1. Fit EFC model: v(r) = v_flat * sqrt(1 - exp(-(r/r_turnon)^sharpness))
  2. Fit NFW model: v²(r) = V200² * [ln(1+x) - x/(1+x)] / [ln(1+c) - c/(1+c)]
  3. Compute χ²_red, AIC, ΔAIC = AIC_NFW - AIC_EFC
  4. Classify regime (FLOW / TRANSITION / LATENT)
  5. Assign Kill-Test verdict per galaxy

Output: sparc175_killtest_results.json (ledger-compatible)

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research
License: CC-BY-4.0
"""

import json
import os
import sys
from typing import Dict
from datetime import datetime, timezone

try:
    from scipy.optimize import differential_evolution
    from scipy.stats import spearmanr, mannwhitneyu
    import numpy as np
except ImportError:
    print("ERROR: scipy and numpy required. Install with:")
    print("  pip install scipy numpy --break-system-packages")
    sys.exit(1)


# ============================================================================
# CONFIGURATION — matches Kill-Test v6 frozen parameters
# ============================================================================

EFC_BOUNDS = {
    "v_flat":    (10.0, 350.0),
    "r_turnon":  (0.05, 50.0),
    "sharpness": (0.3, 6.0),
}

NFW_BOUNDS = {
    "V200": (10.0, 400.0),
    "c":    (1.0, 50.0),
}

H0 = 67.4  # km/s/Mpc (Planck 2018)


# ============================================================================
# MODEL FUNCTIONS
# ============================================================================

def efc_velocity(r, v_flat, r_turnon, sharpness):
    """EFC rotation curve: v(r) = v_flat * sqrt(1 - exp(-(r/r_turnon)^sharpness))"""
    x = (r / r_turnon) ** sharpness
    x = np.clip(x, 0.0, 500.0)
    return v_flat * np.sqrt(1.0 - np.exp(-x))


def nfw_velocity(r, V200, c):
    """NFW rotation curve: v²(r) = V200² * [ln(1+s) - s/(1+s)] / [ln(1+c) - c/(1+c)] / (r/r200)
    where s = c * r / r200 and r200 = V200 / (10 * H0 * 1e-3)"""
    r200 = V200 / (10.0 * H0 * 1e-3)  # kpc
    s = c * r / r200
    denom = np.log(1.0 + c) - c / (1.0 + c)
    numer = np.log(1.0 + s) - s / (1.0 + s)
    ratio = np.maximum(r / r200, 1e-10)
    v_sq = V200**2 * (numer / denom) / ratio
    v_sq = np.maximum(v_sq, 0.0)
    return np.sqrt(v_sq)


# ============================================================================
# FITTING ENGINE
# ============================================================================

def chi2(v_obs, v_model, v_err):
    """Compute chi-squared with zero-error guard."""
    err = v_err.copy()
    nonzero = err[err > 0]
    min_err = nonzero.min() * 0.5 if len(nonzero) > 0 else 1.0
    err[err <= 0] = min_err
    residuals = (v_obs - v_model) / err
    return float(np.sum(residuals**2))


def fit_efc(r_obs, v_obs, v_err):
    bounds = [EFC_BOUNDS["v_flat"], EFC_BOUNDS["r_turnon"], EFC_BOUNDS["sharpness"]]

    def objective(params):
        return chi2(v_obs, efc_velocity(r_obs, *params), v_err)

    try:
        result = differential_evolution(
            objective, bounds,
            seed=42, maxiter=500, tol=1e-8,
            polish=True, init='sobol'
        )
        v_flat, r_turnon, sharpness = result.x
        v_model = efc_velocity(r_obs, v_flat, r_turnon, sharpness)
        chi2_val = chi2(v_obs, v_model, v_err)
        n, k = len(r_obs), 3
        dof = max(n - k, 1)
        return {
            "converged": True,
            "v_flat": float(v_flat),
            "r_turnon": float(r_turnon),
            "sharpness": float(sharpness),
            "chi2": float(chi2_val),
            "chi2_red": float(chi2_val / dof),
            "aic": float(chi2_val + 2 * k),
            "n_data": n,
            "n_params": k,
            "dof": dof,
            "residuals_rms": float(np.sqrt(np.mean((v_obs - v_model) ** 2))),
        }
    except Exception as e:
        return {"converged": False, "error": str(e)}


def fit_nfw(r_obs, v_obs, v_err):
    bounds = [NFW_BOUNDS["V200"], NFW_BOUNDS["c"]]

    def objective(params):
        return chi2(v_obs, nfw_velocity(r_obs, *params), v_err)

    try:
        result = differential_evolution(
            objective, bounds,
            seed=42, maxiter=500, tol=1e-8,
            polish=True, init='sobol'
        )
        V200, c = result.x
        v_model = nfw_velocity(r_obs, V200, c)
        chi2_val = chi2(v_obs, v_model, v_err)
        n, k = len(r_obs), 2
        dof = max(n - k, 1)
        return {
            "converged": True,
            "V200": float(V200),
            "c": float(c),
            "chi2": float(chi2_val),
            "chi2_red": float(chi2_val / dof),
            "aic": float(chi2_val + 2 * k),
            "n_data": n,
            "n_params": k,
            "dof": dof,
            "residuals_rms": float(np.sqrt(np.mean((v_obs - v_model) ** 2))),
        }
    except Exception as e:
        return {"converged": False, "error": str(e)}


# ============================================================================
# CLASSIFICATION & VERDICT
# Convention: ΔAIC = AIC_NFW − AIC_EFC. Positive → EFC wins.
# Matches Kill-Test v6: DDO 154 ΔAIC = +35.4 → EFC_decisive.
# ============================================================================

def classify_regime(delta_aic, chi2_red_efc):
    if delta_aic >= 10.0 and chi2_red_efc < 20.0:
        return "FLOW"
    elif delta_aic <= -10.0 or chi2_red_efc > 50.0:
        return "LATENT"
    else:
        return "TRANSITION"


def assign_verdict(delta_aic):
    if delta_aic > 10.0:
        return "EFC_decisive"
    elif delta_aic > 2.0:
        return "EFC"
    elif delta_aic >= -2.0:
        return "tied"
    elif delta_aic >= -10.0:
        return "LCDM"
    else:
        return "LCDM_decisive"


# ============================================================================
# DATA LOADING — SPARC rotation curves (Lelli+2016 Rotmod_LTG format)
# Column layout in sparc_rotation_curves.dat:
#   0: Galaxy name
#   1: Distance (Mpc)        [ignored]
#   2: Radius (kpc)
#   3: V_obs (km/s)
#   4: V_err (km/s)
#   5: V_gas
#   6: V_disk
#   7: V_bulge
# ============================================================================

def load_sparc_data(filepath: str) -> Dict[str, Dict]:
    galaxies = {}

    if filepath.endswith('.json'):
        with open(filepath, 'r') as f:
            data = json.load(f)
        iterable = data if isinstance(data, list) else [
            {"name": k, **v} for k, v in data.items()
        ]
        for entry in iterable:
            name = entry.get("name") or entry.get("galaxy")
            if name and "radii" in entry and "v_obs" in entry:
                galaxies[name] = {
                    "r": np.array(entry["radii"], dtype=float),
                    "v_obs": np.array(entry["v_obs"], dtype=float),
                    "v_err": np.array(
                        entry.get("v_err", [1.0] * len(entry["radii"])),
                        dtype=float,
                    ),
                }
        return galaxies

    # Tabular SPARC format — use columns 2,3,4 (NOT 1,2,3; col 1 is distance).
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            name = parts[0]
            try:
                r = float(parts[2])
                v_obs = float(parts[3])
                v_err = float(parts[4])
            except (ValueError, IndexError):
                continue
            if v_err <= 0:
                v_err = max(abs(v_obs) * 0.1, 1.0)
            galaxies.setdefault(name, {"r": [], "v_obs": [], "v_err": []})
            galaxies[name]["r"].append(r)
            galaxies[name]["v_obs"].append(v_obs)
            galaxies[name]["v_err"].append(v_err)

    for name in galaxies:
        for key in ("r", "v_obs", "v_err"):
            galaxies[name][key] = np.array(galaxies[name][key], dtype=float)

    return galaxies


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def run_universality_analysis(data_dir: str, output_dir: str = ".") -> Dict:
    print("=" * 70)
    print("SPARC 175 Kill-Test Universality Analysis")
    print("Extending Kill-Test v6 probe-2 to ALL 175 galaxies")
    print("=" * 70)
    print()

    rc_paths = [
        os.path.join(data_dir, "sparc-n175-extended", "sparc_rotation_curves.dat"),
        os.path.join(data_dir, "sparc_rotation_curves.dat"),
        os.path.join(data_dir, "data", "sparc175_fits.json"),
        os.path.join(data_dir, "sparc175_fits.json"),
    ]

    galaxies = {}
    data_source = None
    for path in rc_paths:
        if os.path.exists(path):
            print(f"Loading data from: {path}")
            galaxies = load_sparc_data(path)
            data_source = path
            break

    if not galaxies:
        print("ERROR: No SPARC data found. Expected locations:")
        for p in rc_paths:
            print(f"  {p}")
        sys.exit(1)

    n_galaxies = len(galaxies)
    print(f"Loaded {n_galaxies} galaxies from {data_source}")
    print()

    results = []
    verdicts = {"EFC_decisive": 0, "EFC": 0, "tied": 0, "LCDM": 0, "LCDM_decisive": 0}
    regimes = {"FLOW": 0, "TRANSITION": 0, "LATENT": 0}
    failed = []

    for i, (name, data) in enumerate(sorted(galaxies.items())):
        r = data["r"]
        v_obs = data["v_obs"]
        v_err = data["v_err"]

        if len(r) < 5:
            failed.append({"name": name, "reason": f"Too few data points ({len(r)})"})
            continue

        mask = np.isfinite(r) & np.isfinite(v_obs) & np.isfinite(v_err)
        r, v_obs, v_err = r[mask], v_obs[mask], v_err[mask]

        if len(r) < 5:
            failed.append({"name": name, "reason": "Too few valid data points after cleanup"})
            continue

        v_obs = np.abs(v_obs)

        if (i + 1) % 10 == 0 or i == 0:
            print(f"  [{i+1:3d}/{n_galaxies}] Fitting {name}...")

        efc_result = fit_efc(r, v_obs, v_err)
        nfw_result = fit_nfw(r, v_obs, v_err)

        if not efc_result["converged"] or not nfw_result["converged"]:
            failed.append({
                "name": name,
                "reason": f"EFC converged={efc_result.get('converged')}, NFW converged={nfw_result.get('converged')}",
                "efc_error": efc_result.get("error"),
                "nfw_error": nfw_result.get("error"),
            })
            continue

        delta_aic = nfw_result["aic"] - efc_result["aic"]
        delta_chi2 = nfw_result["chi2"] - efc_result["chi2"]
        regime = classify_regime(delta_aic, efc_result["chi2_red"])
        verdict = assign_verdict(delta_aic)
        verdicts[verdict] += 1
        regimes[regime] += 1

        results.append({
            "name": name,
            "n_data": int(len(r)),
            "r_range_kpc": [float(r.min()), float(r.max())],
            "v_max_obs": float(v_obs.max()),
            "efc": {
                "v_flat": round(efc_result["v_flat"], 2),
                "r_turnon": round(efc_result["r_turnon"], 3),
                "sharpness": round(efc_result["sharpness"], 3),
                "chi2": round(efc_result["chi2"], 3),
                "chi2_red": round(efc_result["chi2_red"], 4),
                "aic": round(efc_result["aic"], 3),
                "residuals_rms_kms": round(efc_result["residuals_rms"], 2),
            },
            "nfw": {
                "V200": round(nfw_result["V200"], 2),
                "c": round(nfw_result["c"], 2),
                "chi2": round(nfw_result["chi2"], 3),
                "chi2_red": round(nfw_result["chi2_red"], 4),
                "aic": round(nfw_result["aic"], 3),
                "residuals_rms_kms": round(nfw_result["residuals_rms"], 2),
            },
            "comparison": {
                "delta_chi2": round(delta_chi2, 3),
                "delta_aic": round(delta_aic, 3),
                "regime": regime,
                "verdict": verdict,
            },
        })

    # Aggregate statistics
    n_fitted = len(results)
    n_failed = len(failed)

    delta_aics = np.array([r["comparison"]["delta_aic"] for r in results])
    chi2_reds_efc = np.array([r["efc"]["chi2_red"] for r in results])
    chi2_reds_nfw = np.array([r["nfw"]["chi2_red"] for r in results])
    v_maxes = np.array([r["v_max_obs"] for r in results])

    if len(v_maxes) > 5:
        rho_vmax, p_vmax = spearmanr(delta_aics, v_maxes)
    else:
        rho_vmax, p_vmax = 0.0, 1.0

    flow_aics = [r["comparison"]["delta_aic"] for r in results if r["comparison"]["regime"] == "FLOW"]
    latent_aics = [r["comparison"]["delta_aic"] for r in results if r["comparison"]["regime"] == "LATENT"]

    if len(flow_aics) > 1 and len(latent_aics) > 1:
        mw_stat, mw_p = mannwhitneyu(flow_aics, latent_aics, alternative='greater')
    else:
        mw_stat, mw_p = 0.0, 1.0

    efc_wins = verdicts["EFC_decisive"] + verdicts["EFC"]
    lcdm_wins = verdicts["LCDM_decisive"] + verdicts["LCDM"]
    ties = verdicts["tied"]

    output = {
        "$schema": "kill_test_v6_universality",
        "metadata": {
            "title": "SPARC 175 Kill-Test Universality Analysis",
            "description": "Extension of Kill-Test v6 probe-2 to all 175 SPARC galaxies",
            "author": "Morten Magnusson",
            "orcid": "0009-0002-4860-5095",
            "affiliation": "Symbiose Research",
            "date": datetime.now(timezone.utc).isoformat(),
            "methodology": "Kill-Test v6 (differential evolution + AIC comparison)",
            "data_source": data_source,
            "efc_model": "v(r) = v_flat * sqrt(1 - exp(-(r/r_turnon)^sharpness))",
            "nfw_model": "v^2(r) = V200^2 * [ln(1+s) - s/(1+s)] / [ln(1+c) - c/(1+c)] / (r/r200)",
            "delta_aic_convention": "AIC_NFW - AIC_EFC (positive = EFC wins)",
            "frozen_parameters": {
                "H0": H0,
                "nfw_c_bounds": list(NFW_BOUNDS["c"]),
            },
        },
        "summary": {
            "n_galaxies_total": n_galaxies,
            "n_fitted": n_fitted,
            "n_failed": n_failed,
            "verdict_distribution": verdicts,
            "regime_distribution": regimes,
            "efc_win_rate_percent": round(100.0 * efc_wins / max(n_fitted, 1), 1),
            "lcdm_win_rate_percent": round(100.0 * lcdm_wins / max(n_fitted, 1), 1),
            "tie_rate_percent": round(100.0 * ties / max(n_fitted, 1), 1),
            "median_delta_aic": round(float(np.median(delta_aics)), 3) if len(delta_aics) > 0 else None,
            "mean_delta_aic": round(float(np.mean(delta_aics)), 3) if len(delta_aics) > 0 else None,
            "median_chi2_red_efc": round(float(np.median(chi2_reds_efc)), 4) if len(chi2_reds_efc) > 0 else None,
            "median_chi2_red_nfw": round(float(np.median(chi2_reds_nfw)), 4) if len(chi2_reds_nfw) > 0 else None,
        },
        "statistical_tests": {
            "spearman_delta_aic_vs_vmax": {
                "rho": round(float(rho_vmax), 4),
                "p_value": round(float(p_vmax), 6),
                "interpretation": "Tests if EFC advantage correlates with v_max (mass proxy)",
            },
            "mann_whitney_flow_vs_latent": {
                "U_statistic": round(float(mw_stat), 2),
                "p_value": round(float(mw_p), 6),
                "n_flow": len(flow_aics),
                "n_latent": len(latent_aics),
                "interpretation": "Tests if FLOW galaxies have significantly higher ΔAIC than LATENT",
            },
        },
        "kill_test_v6_extension": {
            "original_probe2": {
                "n_galaxies": 5,
                "verdict": "EFC_decisive",
                "success_rate_percent": 100,
            },
            "extended_to_175": {
                "n_galaxies": n_fitted,
                "efc_decisive_count": verdicts["EFC_decisive"],
                "efc_decisive_rate_percent": round(100.0 * verdicts["EFC_decisive"] / max(n_fitted, 1), 1),
                "cherry_picking_refuted": efc_wins > n_fitted * 0.5,
                "universality_verdict": (
                    "CONFIRMED" if efc_wins > n_fitted * 0.6
                    else "PARTIAL" if efc_wins > n_fitted * 0.4
                    else "FAILED"
                ),
            },
        },
        "per_galaxy_results": sorted(results, key=lambda x: -x["comparison"]["delta_aic"]),
        "failed_galaxies": failed,
    }

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sparc175_killtest_results.json")
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    print()
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"  Galaxies fitted:     {n_fitted} / {n_galaxies}")
    print(f"  Failed:              {n_failed}")
    print()
    print("  VERDICT DISTRIBUTION:")
    for k in ("EFC_decisive", "EFC", "tied", "LCDM", "LCDM_decisive"):
        pct = 100 * verdicts[k] / max(n_fitted, 1)
        print(f"    {k:<15s}  {verdicts[k]:3d}  ({pct:.1f}%)")
    print()
    print("  REGIME DISTRIBUTION:")
    for k in ("FLOW", "TRANSITION", "LATENT"):
        print(f"    {k:<15s}  {regimes[k]:3d}")
    print()
    print(f"  EFC win rate:        {100*efc_wins/max(n_fitted,1):.1f}%")
    print(f"  Median ΔAIC:         {output['summary']['median_delta_aic']}")
    print(f"  Median χ²_red EFC:   {output['summary']['median_chi2_red_efc']}")
    print(f"  Median χ²_red NFW:   {output['summary']['median_chi2_red_nfw']}")
    print()
    print(f"  Universality verdict: {output['kill_test_v6_extension']['extended_to_175']['universality_verdict']}")
    print()
    print(f"  Output: {output_path}")
    print("=" * 70)

    return output


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    default_dirs = [
        "docs/papers/efc/Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling",
        os.path.expanduser("~/efc/sparc175"),
        ".",
    ]

    data_dir = None
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        for d in default_dirs:
            if os.path.isdir(d):
                data_dir = d
                break

    if data_dir is None:
        print("Usage: python sparc175_killtest_universality.py [data_dir] [output_dir]")
        sys.exit(1)

    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    run_universality_analysis(data_dir, output_dir)
