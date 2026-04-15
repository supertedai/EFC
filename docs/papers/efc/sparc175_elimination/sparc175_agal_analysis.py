#!/usr/bin/env python3
"""
A_gal Analysis — What IS the missing degree of freedom?

After showing that 1 param/galaxy (A_gal) is sufficient to match NFW,
the critical question is: what does A_gal correlate with?

If A_gal correlates strongly with observable properties → it's predictable
→ we can build a universal model after all.

If A_gal is uncorrelated → it's a genuinely free parameter (like NFW's V200).

Tests:
1. Correlations: A_gal vs (M_bar, V_max, R_last, Σ_mean, f_gas, g_bar_mean)
2. Multiple regression: can A_gal be predicted from observables?
3. Residual analysis: what's left after prediction?
4. Physical interpretation: what does A_gal represent?
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar, differential_evolution
from scipy.stats import spearmanr, pearsonr
from collections import defaultdict
import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sparc"
SPARC_DAT = DATA_DIR / "sparc_rotation_curves.dat"
CLASSIFIED_JSON = DATA_DIR / "sparc175_classified.json"
ONE_PARAM_RESULTS = Path(__file__).resolve().parent / "sparc175_one_param_results" / "one_param_results.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "sparc175_agal_analysis"

UPSILON_DISK = 0.5
UPSILON_BULGE = 0.7
MIN_ERROR = 1.0
K_LOCKED = 0.415
G_CONV = 1e6 / 3.0857e19
G_NEWTON = 6.674e-11
KPC_TO_M = 3.0857e19
KMS_TO_MS = 1e3
MSUN = 1.989e30


def load_sparc():
    galaxies = defaultdict(lambda: {
        "r": [], "Vobs": [], "eV": [],
        "Vgas": [], "Vdisk": [], "Vbul": []
    })
    with open(SPARC_DAT) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            try:
                name = parts[0]
                galaxies[name]["r"].append(float(parts[2]))
                galaxies[name]["Vobs"].append(float(parts[3]))
                galaxies[name]["eV"].append(max(float(parts[4]), MIN_ERROR))
                galaxies[name]["Vgas"].append(float(parts[5]))
                galaxies[name]["Vdisk"].append(float(parts[6]))
                galaxies[name]["Vbul"].append(float(parts[7]))
            except (ValueError, IndexError):
                continue
    for name in galaxies:
        for key in galaxies[name]:
            galaxies[name][key] = np.array(galaxies[name][key])
    return dict(galaxies)


def load_regimes():
    if not CLASSIFIED_JSON.exists():
        return {}
    with open(CLASSIFIED_JSON) as f:
        data = json.load(f)
    return {name: info.get("regime", "UNKNOWN")
            for name, info in data.get("results", {}).items()}


def main():
    print("=" * 80)
    print("A_gal ANALYSIS — WHAT IS THE MISSING DEGREE OF FREEDOM?")
    print("=" * 80)

    galaxies = load_sparc()
    regimes = load_regimes()

    # Load A_gal from previous results
    with open(ONE_PARAM_RESULTS) as f:
        prev = json.load(f)
    agal_data = prev["results_per_galaxy"]

    # Compute galaxy properties
    print("\n[COMPUTE] Galaxy properties...")
    props = {}
    for name, g in galaxies.items():
        r = g["r"]
        Vobs = g["Vobs"]
        n = len(r)

        V2_bar = g["Vgas"]**2 + UPSILON_DISK * g["Vdisk"]**2 + UPSILON_BULGE * g["Vbul"]**2
        V_bar = np.sqrt(np.maximum(V2_bar, 1e-10))

        # Max observed velocity
        V_max = float(np.max(Vobs))

        # Last measured radius
        R_last = float(r[-1])

        # Mean baryonic acceleration
        g_bar = V2_bar * G_CONV / np.maximum(r, 1e-10)
        g_bar_mean = float(np.mean(g_bar))
        log_g_mean = float(np.log10(max(g_bar_mean, 1e-30)))

        # Baryonic mass proxy: M_bar ∝ V²_bar(R_last) · R_last / G
        # In M☉: M = V²[km/s] * R[kpc] * (1e6 * 3.086e19) / (6.674e-11 * 1.989e30)
        M_bar_proxy = V2_bar[-1] * KMS_TO_MS**2 * r[-1] * KPC_TO_M / (G_NEWTON * MSUN)
        log_M = float(np.log10(max(M_bar_proxy, 1e-10)))

        # Mean surface density (M☉/pc²)
        Sigma = V2_bar * KMS_TO_MS**2 / (G_NEWTON * r * KPC_TO_M) / 2.089e-3
        Sigma_mean = float(np.mean(Sigma))
        log_Sigma = float(np.log10(max(Sigma_mean, 1e-10)))

        # Gas fraction: f_gas = V²_gas / V²_bar (mean)
        V2_gas = g["Vgas"]**2
        f_gas = float(np.mean(V2_gas / np.maximum(V2_bar, 1e-10)))

        # Disk scale length proxy: radius at half-max V_bar
        V_bar_max = np.max(V_bar)
        half_max_idx = np.argmin(np.abs(V_bar - 0.5 * V_bar_max))
        R_half = float(r[max(half_max_idx, 0)])

        # Mean density proxy: ρ ∝ M / R³
        log_rho = log_M - 3 * np.log10(max(R_last, 0.1))

        # A_gal from previous fit
        A = agal_data.get(name, {}).get("A_gal", None)
        if A is None:
            continue

        props[name] = {
            "A_gal": A,
            "log_A_abs": float(np.log10(max(abs(A), 1e-10))) * np.sign(A),
            "V_max": V_max,
            "log_V_max": float(np.log10(max(V_max, 1))),
            "R_last": R_last,
            "log_R_last": float(np.log10(max(R_last, 0.01))),
            "log_M": log_M,
            "log_Sigma": log_Sigma,
            "f_gas": f_gas,
            "log_g_mean": log_g_mean,
            "R_half": R_half,
            "log_rho": log_rho,
            "regime": regimes.get(name, "UNKNOWN"),
            "n_points": n,
        }

    n_gal = len(props)
    print(f"  {n_gal} galaxies with A_gal values")

    # Arrays
    names = sorted(props.keys())
    A_arr = np.array([props[n]["A_gal"] for n in names])

    observables = {
        "log(M_bar)": np.array([props[n]["log_M"] for n in names]),
        "log(V_max)": np.array([props[n]["log_V_max"] for n in names]),
        "log(R_last)": np.array([props[n]["log_R_last"] for n in names]),
        "log(Σ)": np.array([props[n]["log_Sigma"] for n in names]),
        "f_gas": np.array([props[n]["f_gas"] for n in names]),
        "log(g_mean)": np.array([props[n]["log_g_mean"] for n in names]),
        "log(ρ)": np.array([props[n]["log_rho"] for n in names]),
    }

    # ══════════════════════════════════════════════════════════════════════
    # 1. CORRELATIONS
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. A_gal CORRELATIONS WITH OBSERVABLES")
    print("=" * 80)

    print(f"\n  {'Observable':<15} {'Spearman ρ':>12} {'p-value':>12} {'Pearson r':>12} {'p-value':>12}")
    print("  " + "-" * 65)

    correlations = {}
    for label, arr in observables.items():
        rho_s, p_s = spearmanr(arr, A_arr)
        rho_p, p_p = pearsonr(arr, A_arr)
        marker = " ***" if p_s < 0.001 else (" **" if p_s < 0.01 else (" *" if p_s < 0.05 else ""))
        print(f"  {label:<15} {rho_s:>+12.4f} {p_s:>12.2e} {rho_p:>+12.4f} {p_p:>12.2e}{marker}")
        correlations[label] = {"spearman_rho": float(rho_s), "spearman_p": float(p_s),
                                "pearson_r": float(rho_p), "pearson_p": float(p_p)}

    # ══════════════════════════════════════════════════════════════════════
    # 2. MULTIPLE REGRESSION
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("2. MULTIPLE REGRESSION: A_gal ~ observables")
    print("=" * 80)

    # Best single predictor
    best_single = max(correlations.items(), key=lambda x: abs(x[1]["spearman_rho"]))
    print(f"\n  Best single predictor: {best_single[0]} "
          f"(ρ = {best_single[1]['spearman_rho']:+.4f})")

    # OLS with top predictors
    sig_predictors = [(k, observables[k]) for k, v in correlations.items()
                      if v["spearman_p"] < 0.05]

    if sig_predictors:
        print(f"\n  Significant predictors (p<0.05): {[k for k, _ in sig_predictors]}")

        # Full regression with significant predictors
        X_cols = [arr for _, arr in sig_predictors]
        X = np.column_stack([np.ones(len(A_arr))] + X_cols)
        try:
            beta = np.linalg.lstsq(X, A_arr, rcond=None)[0]
            A_pred = X @ beta
            ss_res = np.sum((A_arr - A_pred)**2)
            ss_tot = np.sum((A_arr - np.mean(A_arr))**2)
            R2 = 1 - ss_res / ss_tot
            residuals = A_arr - A_pred

            print(f"\n  Multi-regression R² = {R2:.4f}")
            print(f"  Coefficients:")
            print(f"    intercept = {beta[0]:+.1f}")
            for i, (label, _) in enumerate(sig_predictors):
                print(f"    {label}: {beta[i+1]:+.1f}")

            # Single-variable R² for comparison
            for label, arr in sig_predictors:
                X1 = np.column_stack([np.ones(len(A_arr)), arr])
                b1 = np.linalg.lstsq(X1, A_arr, rcond=None)[0]
                pred1 = X1 @ b1
                R2_1 = 1 - np.sum((A_arr - pred1)**2) / ss_tot
                print(f"    R²({label} alone) = {R2_1:.4f}")

        except Exception as e:
            print(f"  Regression failed: {e}")
            R2 = 0
            residuals = A_arr
    else:
        print("\n  No significant predictors found!")
        R2 = 0
        residuals = A_arr

    # ══════════════════════════════════════════════════════════════════════
    # 3. PER-REGIME A_gal ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("3. A_gal BY REGIME")
    print("=" * 80)

    for regime in ["FLOW", "TRANSITION", "LATENT"]:
        r_A = [props[n]["A_gal"] for n in names if props[n]["regime"] == regime]
        if not r_A:
            continue
        arr = np.array(r_A)
        print(f"\n  {regime} (n={len(arr)}):")
        print(f"    Mean:   {np.mean(arr):+8.0f} (km/s)²")
        print(f"    Median: {np.median(arr):+8.0f} (km/s)²")
        print(f"    Std:    {np.std(arr):8.0f} (km/s)²")
        print(f"    Frac <0: {np.mean(arr < 0):.1%}")

        # Within-regime correlations with best predictor
        if best_single:
            r_obs = [props[n][{
                "log(M_bar)": "log_M", "log(V_max)": "log_V_max",
                "log(R_last)": "log_R_last", "log(Σ)": "log_Sigma",
                "f_gas": "f_gas", "log(g_mean)": "log_g_mean",
                "log(ρ)": "log_rho",
            }[best_single[0]]] for n in names if props[n]["regime"] == regime]
            if len(r_obs) >= 5:
                rho, p = spearmanr(r_obs, r_A)
                print(f"    Within-regime {best_single[0]} vs A: ρ={rho:+.3f}, p={p:.2e}")

    # ══════════════════════════════════════════════════════════════════════
    # 4. CAN A_gal BE PREDICTED? (the key question)
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("4. CAN A_gal BE PREDICTED FROM OBSERVABLES?")
    print("=" * 80)

    if R2 > 0.5:
        print(f"\n  R² = {R2:.3f} → YES: A_gal is largely predictable")
        print("  → Can build UNIVERSAL model (A_gal from baryonic properties)")
        print("  → This would be a 0-free-parameter model that works!")
    elif R2 > 0.3:
        print(f"\n  R² = {R2:.3f} → PARTIAL: A_gal is partially predictable")
        print("  → Some structure, but significant residual scatter")
        print("  → Universal model would be approximate, not exact")
    elif R2 > 0.1:
        print(f"\n  R² = {R2:.3f} → WEAK: A_gal has weak observable correlations")
        print("  → Mostly unpredictable from baryonic properties alone")
        print("  → A_gal represents genuinely new information")
    else:
        print(f"\n  R² = {R2:.3f} → NO: A_gal is uncorrelated with observables")
        print("  → It's a genuinely free parameter")
        print("  → Like NFW's V200 — reflects something beyond baryons")

    # ══════════════════════════════════════════════════════════════════════
    # 5. DIMENSIONAL ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("5. DIMENSIONAL ANALYSIS")
    print("=" * 80)

    print(f"\n  A_gal has units: (km/s)²")
    print(f"  In the model: V² = V²_bar·μ + A·r/(r+r₀)")
    print(f"  So A is a velocity² scale that sets the additive dark amplitude")
    print(f"\n  Physical candidates:")
    print(f"    V²_200 (halo virial velocity²): NFW equivalent")
    print(f"    G·M_halo/r_s: gravitational potential scale")
    print(f"    a₀·R (MOND): acceleration × size → velocity²")

    # Test: does A_gal ∝ a₀ · R?
    a0 = 1.2e-10  # m/s²
    a0_R = a0 * np.array([props[n]["R_last"] for n in names]) * KPC_TO_M / KMS_TO_MS**2
    rho_aR, p_aR = spearmanr(a0_R, A_arr)
    print(f"\n  Test: A_gal vs a₀·R_last:")
    print(f"    ρ = {rho_aR:+.4f}, p = {p_aR:.2e}")

    # Test: does A_gal ∝ V²_max?
    V2max = np.array([props[n]["V_max"] for n in names])**2
    rho_V2, p_V2 = spearmanr(V2max, A_arr)
    print(f"\n  Test: A_gal vs V²_max:")
    print(f"    ρ = {rho_V2:+.4f}, p = {p_V2:.2e}")

    # Test: does |A_gal| ∝ V²_max?
    rho_absV2, p_absV2 = spearmanr(V2max, np.abs(A_arr))
    print(f"\n  Test: |A_gal| vs V²_max:")
    print(f"    ρ = {rho_absV2:+.4f}, p = {p_absV2:.2e}")

    # ══════════════════════════════════════════════════════════════════════
    # SUMMARY
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    # Top 3 correlations
    sorted_corr = sorted(correlations.items(),
                         key=lambda x: abs(x[1]["spearman_rho"]), reverse=True)
    print(f"\n  Top correlates of A_gal:")
    for i, (label, c) in enumerate(sorted_corr[:3]):
        print(f"    {i+1}. {label}: ρ = {c['spearman_rho']:+.4f} (p = {c['spearman_p']:.2e})")

    print(f"\n  Multi-regression R² = {R2:.4f}")
    print(f"  A_gal mean = {np.mean(A_arr):+.0f}, std = {np.std(A_arr):.0f} (km/s)²")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {
            "experiment": "A_gal correlation analysis",
            "date": datetime.datetime.now().isoformat(),
            "n_galaxies": n_gal,
        },
        "correlations": correlations,
        "regression_R2": float(R2),
        "per_galaxy": {
            name: {
                "A_gal": props[name]["A_gal"],
                "V_max": props[name]["V_max"],
                "log_M": props[name]["log_M"],
                "log_Sigma": props[name]["log_Sigma"],
                "f_gas": props[name]["f_gas"],
                "regime": props[name]["regime"],
            }
            for name in names
        },
    }
    with open(OUTPUT_DIR / "agal_analysis.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to {OUTPUT_DIR}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
