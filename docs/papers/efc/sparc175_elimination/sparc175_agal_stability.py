#!/usr/bin/env python3
"""
A_gal Stability & Robustness Tests

Two critical tests:

1. STABILITY: Fit A_gal on inner half vs outer half of each galaxy.
   If A_gal is stable → it's a real galaxy property.
   If it changes dramatically → model artifact / overfitting.

2. SIGN DETERMINANT: What determines the sign of A_gal?
   Check: morphological type (via gas fraction proxy),
   V_obs shape (rising vs flat vs declining), inner vs outer dominance.

3. LEAVE-ONE-OUT: How sensitive is A_gal to individual data points?
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar
from scipy.stats import spearmanr, pearsonr
from collections import defaultdict, Counter
import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sparc"
SPARC_DAT = DATA_DIR / "sparc_rotation_curves.dat"
CLASSIFIED_JSON = DATA_DIR / "sparc175_classified.json"
ONE_PARAM_DIR = Path(__file__).resolve().parent / "sparc175_one_param_results"
OUTPUT_DIR = Path(__file__).resolve().parent / "sparc175_agal_stability"

UPSILON_DISK = 0.5
UPSILON_BULGE = 0.7
MIN_ERROR = 1.0
K_LOCKED = 0.415
G_CONV = 1e6 / 3.0857e19


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


def fit_agal(r, Vobs, eV, Vgas, Vdisk, Vbul, g_dag, r0):
    """Fit A_gal for a subset of data points."""
    V2_bar = Vgas**2 + UPSILON_DISK * Vdisk**2 + UPSILON_BULGE * Vbul**2
    V2_bar = np.maximum(V2_bar, 1e-10)
    g_bar = V2_bar * G_CONV / np.maximum(r, 1e-10)
    mu = (1.0 + g_dag / np.maximum(g_bar, 1e-30))**K_LOCKED
    V2_screening = V2_bar * mu
    profile = r / (r + r0)

    def chi2_A(A):
        V2_total = V2_screening + A * profile
        V_pred = np.sqrt(np.maximum(V2_total, 0.0))
        return np.sum(((Vobs - V_pred) / eV)**2)

    A_max = float(np.max(Vobs**2)) * 5
    res = minimize_scalar(chi2_A, bounds=(-A_max, A_max), method='bounded')
    return res.x, res.fun


def main():
    print("=" * 80)
    print("A_gal STABILITY & ROBUSTNESS TESTS")
    print("=" * 80)

    galaxies = load_sparc()
    regimes = load_regimes()

    # Load previous results
    with open(ONE_PARAM_DIR / "one_param_results.json") as f:
        prev = json.load(f)
    g_dag = prev["metadata"]["g_dag"]
    r0 = prev["metadata"]["r0_kpc"]

    print(f"\n  g† = {g_dag:.4e}, r₀ = {r0:.2f} kpc")
    print(f"  {len(galaxies)} galaxies")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 1: INNER vs OUTER STABILITY
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("TEST 1: INNER vs OUTER HALF STABILITY")
    print("=" * 80)

    stability = {}
    for name, g in sorted(galaxies.items()):
        n = len(g["r"])
        if n < 8:  # Need at least 4 points per half
            continue

        mid = n // 2

        # Full fit
        A_full, _ = fit_agal(g["r"], g["Vobs"], g["eV"],
                             g["Vgas"], g["Vdisk"], g["Vbul"], g_dag, r0)

        # Inner half
        A_inner, _ = fit_agal(g["r"][:mid], g["Vobs"][:mid], g["eV"][:mid],
                              g["Vgas"][:mid], g["Vdisk"][:mid], g["Vbul"][:mid],
                              g_dag, r0)

        # Outer half
        A_outer, _ = fit_agal(g["r"][mid:], g["Vobs"][mid:], g["eV"][mid:],
                              g["Vgas"][mid:], g["Vdisk"][mid:], g["Vbul"][mid:],
                              g_dag, r0)

        stability[name] = {
            "A_full": A_full,
            "A_inner": A_inner,
            "A_outer": A_outer,
            "regime": regimes.get(name, "UNKNOWN"),
            "n": n,
        }

    n_stable = len(stability)
    print(f"\n  {n_stable} galaxies with ≥8 points (inner/outer split)")

    # Correlation: inner vs outer
    A_inner = np.array([s["A_inner"] for s in stability.values()])
    A_outer = np.array([s["A_outer"] for s in stability.values()])
    A_full = np.array([s["A_full"] for s in stability.values()])

    rho_io, p_io = spearmanr(A_inner, A_outer)
    r_io, p_io_p = pearsonr(A_inner, A_outer)

    print(f"\n  Inner vs Outer A_gal:")
    print(f"    Spearman: ρ = {rho_io:+.4f}, p = {p_io:.2e}")
    print(f"    Pearson:  r = {r_io:+.4f}, p = {p_io_p:.2e}")

    # Sign agreement
    same_sign = np.mean(np.sign(A_inner) == np.sign(A_outer))
    print(f"    Sign agreement: {100*same_sign:.1f}%")

    # Relative change
    rel_change = np.abs(A_inner - A_outer) / (np.abs(A_full) + 1)
    print(f"    Relative |A_inner - A_outer| / |A_full|:")
    print(f"      Median: {np.median(rel_change):.2f}")
    print(f"      Mean:   {np.mean(rel_change):.2f}")
    print(f"      Frac < 1: {np.mean(rel_change < 1):.1%}")
    print(f"      Frac < 2: {np.mean(rel_change < 2):.1%}")

    # Per-regime stability
    print(f"\n  Per-regime stability:")
    for regime in ["FLOW", "TRANSITION", "LATENT"]:
        r_stab = [(s["A_inner"], s["A_outer"], s["A_full"])
                  for s in stability.values() if s["regime"] == regime]
        if len(r_stab) < 5:
            continue
        r_in = np.array([x[0] for x in r_stab])
        r_out = np.array([x[1] for x in r_stab])
        r_full = np.array([x[2] for x in r_stab])
        rho, p = spearmanr(r_in, r_out)
        ss = np.mean(np.sign(r_in) == np.sign(r_out))
        rc = np.median(np.abs(r_in - r_out) / (np.abs(r_full) + 1))
        print(f"    {regime:>11} (n={len(r_stab)}): ρ_io={rho:+.3f}, "
              f"sign_agree={100*ss:.0f}%, med_change={rc:.2f}")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 2: SIGN DETERMINANTS
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("TEST 2: WHAT DETERMINES THE SIGN OF A_gal?")
    print("=" * 80)

    # Compute additional galaxy properties
    sign_data = []
    for name, g in galaxies.items():
        A = prev["results_per_galaxy"].get(name, {}).get("A_gal")
        if A is None:
            continue

        r = g["r"]
        Vobs = g["Vobs"]
        n = len(r)
        if n < 4:
            continue

        V2_bar = g["Vgas"]**2 + UPSILON_DISK * g["Vdisk"]**2 + UPSILON_BULGE * g["Vbul"]**2

        # Rotation curve shape: slope of V_obs in outer half
        mid = n // 2
        if n - mid >= 2:
            slope = np.polyfit(r[mid:], Vobs[mid:], 1)[0]
        else:
            slope = 0

        # Rising / flat / declining classification
        if slope > 1:
            shape = "RISING"
        elif slope < -1:
            shape = "DECLINING"
        else:
            shape = "FLAT"

        # Gas dominance
        f_gas = np.mean(g["Vgas"]**2 / np.maximum(V2_bar, 1e-10))

        # Concentration: V_obs(inner) / V_obs(outer)
        V_inner = np.mean(Vobs[:mid]) if mid > 0 else Vobs[0]
        V_outer = np.mean(Vobs[mid:]) if mid < n else Vobs[-1]
        concentration = V_inner / max(V_outer, 1)

        sign_data.append({
            "name": name,
            "A_gal": A,
            "sign": "+" if A >= 0 else "-",
            "slope": slope,
            "shape": shape,
            "f_gas": f_gas,
            "concentration": concentration,
            "regime": regimes.get(name, "UNKNOWN"),
            "V_max": float(np.max(Vobs)),
        })

    # Shape vs sign
    print(f"\n  Rotation curve shape vs A_gal sign:")
    for shape in ["RISING", "FLAT", "DECLINING"]:
        subset = [s for s in sign_data if s["shape"] == shape]
        if not subset:
            continue
        n_pos = sum(1 for s in subset if s["A_gal"] >= 0)
        n_neg = len(subset) - n_pos
        med_A = np.median([s["A_gal"] for s in subset])
        print(f"    {shape:>10} (n={len(subset):>3}): "
              f"+{n_pos:>3} / -{n_neg:>3}, "
              f"med A={med_A:+8.0f}")

    # Slope vs A_gal
    slopes = np.array([s["slope"] for s in sign_data])
    A_signs = np.array([s["A_gal"] for s in sign_data])
    rho_slope, p_slope = spearmanr(slopes, A_signs)
    print(f"\n  Outer slope vs A_gal: ρ = {rho_slope:+.4f}, p = {p_slope:.2e}")

    # Concentration vs A_gal
    conc = np.array([s["concentration"] for s in sign_data])
    rho_conc, p_conc = spearmanr(conc, A_signs)
    print(f"  Concentration vs A_gal: ρ = {rho_conc:+.4f}, p = {p_conc:.2e}")

    # Gas fraction vs sign
    fgas = np.array([s["f_gas"] for s in sign_data])
    rho_fgas, p_fgas = spearmanr(fgas, A_signs)
    print(f"  Gas fraction vs A_gal: ρ = {rho_fgas:+.4f}, p = {p_fgas:.2e}")

    # ══════════════════════════════════════════════════════════════════════
    # TEST 3: LEAVE-ONE-OUT SENSITIVITY
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("TEST 3: LEAVE-ONE-OUT SENSITIVITY (20 random galaxies)")
    print("=" * 80)

    rng = np.random.RandomState(42)
    sample = rng.choice([n for n in galaxies if len(galaxies[n]["r"]) >= 10],
                        size=min(20, len(galaxies)), replace=False)

    loo_results = []
    for name in sample:
        g = galaxies[name]
        n = len(g["r"])

        # Full fit
        A_full, _ = fit_agal(g["r"], g["Vobs"], g["eV"],
                             g["Vgas"], g["Vdisk"], g["Vbul"], g_dag, r0)

        # LOO: remove each point, refit
        A_loo = []
        for i in range(n):
            mask = np.ones(n, dtype=bool)
            mask[i] = False
            A_i, _ = fit_agal(g["r"][mask], g["Vobs"][mask], g["eV"][mask],
                              g["Vgas"][mask], g["Vdisk"][mask], g["Vbul"][mask],
                              g_dag, r0)
            A_loo.append(A_i)

        A_loo = np.array(A_loo)
        cv = np.std(A_loo) / max(abs(A_full), 1)

        loo_results.append({
            "name": name,
            "A_full": A_full,
            "A_loo_mean": float(np.mean(A_loo)),
            "A_loo_std": float(np.std(A_loo)),
            "cv": cv,
            "sign_flips": int(np.sum(np.sign(A_loo) != np.sign(A_full))),
            "n": n,
        })

    cv_arr = np.array([r["cv"] for r in loo_results])
    flip_arr = np.array([r["sign_flips"] / r["n"] for r in loo_results])

    print(f"\n  LOO coefficient of variation (CV = std/|A|):")
    print(f"    Median CV: {np.median(cv_arr):.3f}")
    print(f"    Mean CV:   {np.mean(cv_arr):.3f}")
    print(f"    Max CV:    {np.max(cv_arr):.3f}")

    print(f"\n  Sign flip rate (fraction of LOO iterations that flip sign):")
    print(f"    Median: {np.median(flip_arr):.1%}")
    print(f"    Mean:   {np.mean(flip_arr):.1%}")
    print(f"    Galaxies with >20% flips: {np.sum(flip_arr > 0.2)}/{len(loo_results)}")

    # Show a few examples
    print(f"\n  Examples:")
    print(f"  {'Galaxy':<15} {'A_full':>10} {'A_loo_mean':>12} {'CV':>6} {'Flips':>6}")
    for r in sorted(loo_results, key=lambda x: x["cv"])[:5]:
        print(f"  {r['name']:<15} {r['A_full']:>+10.0f} {r['A_loo_mean']:>+12.0f} "
              f"{r['cv']:>6.3f} {r['sign_flips']:>4}/{r['n']}")
    print("  ...")
    for r in sorted(loo_results, key=lambda x: x["cv"])[-3:]:
        print(f"  {r['name']:<15} {r['A_full']:>+10.0f} {r['A_loo_mean']:>+12.0f} "
              f"{r['cv']:>6.3f} {r['sign_flips']:>4}/{r['n']}")

    # ══════════════════════════════════════════════════════════════════════
    # VERDICT
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    # Stability
    stable = rho_io > 0.5 and same_sign > 0.6
    print(f"\n  Inner/Outer stability:   {'PASS' if stable else 'FAIL'} "
          f"(ρ={rho_io:+.3f}, sign={100*same_sign:.0f}%)")

    # LOO robustness
    robust = np.median(cv_arr) < 0.5 and np.median(flip_arr) < 0.2
    print(f"  LOO robustness:          {'PASS' if robust else 'FAIL'} "
          f"(CV={np.median(cv_arr):.3f}, flips={np.median(flip_arr):.1%})")

    # Sign determinant
    sign_found = abs(rho_slope) > 0.3 and p_slope < 0.01
    print(f"  Sign determinant found:  {'YES' if sign_found else 'NO'} "
          f"(slope: ρ={rho_slope:+.3f})")

    if stable and robust:
        print("\n  → A_gal is a REAL, STABLE galaxy property")
        if sign_found:
            print("  → Sign is determined by rotation curve shape")
            print("  → Physical: A_gal corrects for profile mismatch")
        else:
            print("  → Sign is NOT predictable from simple observables")
            print("  → A_gal represents genuinely hidden information")
    elif not stable:
        print("\n  → A_gal is UNSTABLE — changes with radial range")
        print("  → Likely a model artifact, not a real galaxy property")
    elif not robust:
        print("\n  → A_gal is SENSITIVE to individual data points")
        print("  → Fitting noise, not structure")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {"date": datetime.datetime.now().isoformat()},
        "stability": {
            "inner_outer_spearman": float(rho_io),
            "inner_outer_pearson": float(r_io),
            "sign_agreement": float(same_sign),
            "median_relative_change": float(np.median(rel_change)),
        },
        "sign_determinants": {
            "slope_vs_A": {"rho": float(rho_slope), "p": float(p_slope)},
            "concentration_vs_A": {"rho": float(rho_conc), "p": float(p_conc)},
            "fgas_vs_A": {"rho": float(rho_fgas), "p": float(p_fgas)},
        },
        "loo": {
            "median_cv": float(np.median(cv_arr)),
            "mean_cv": float(np.mean(cv_arr)),
            "median_sign_flip_rate": float(np.median(flip_arr)),
        },
    }
    with open(OUTPUT_DIR / "stability_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to {OUTPUT_DIR}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
