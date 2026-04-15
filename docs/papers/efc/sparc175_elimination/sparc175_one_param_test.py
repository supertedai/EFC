#!/usr/bin/env python3
"""
SPARC 175 One-Parameter-Per-Galaxy Test — The Definitive Test

After eliminating all 0-per-galaxy models, test whether ONE free parameter
per galaxy is sufficient, or whether NFW's TWO are necessary.

Model: V² = V²_bar · μ(g; a₀) + A_gal · r/(r + r₀)
    - μ(g; a₀): screening with global a₀ (locked from previous fits)
    - A_gal: single free amplitude per galaxy (fitted)
    - r₀: global scale radius (fitted once)
    - f(r) = r/(r+r₀): cored profile (rises linearly, flattens)

Total: 1 global (r₀) + 1 per galaxy (A_gal) = N+1 params
NFW:   0 global + 2 per galaxy = 2N params

If 1 param/galaxy ≈ NFW performance → EFC wins on parsimony.
If 1 param/galaxy << NFW → need 2 degrees of freedom.
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar, minimize, differential_evolution
from collections import defaultdict, Counter
from scipy.stats import mannwhitneyu
import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sparc"
SPARC_DAT = DATA_DIR / "sparc_rotation_curves.dat"
CLASSIFIED_JSON = DATA_DIR / "sparc175_classified.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "sparc175_one_param_results"

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


def v2_bar(g):
    return g["Vgas"]**2 + UPSILON_DISK * g["Vdisk"]**2 + UPSILON_BULGE * g["Vbul"]**2


# ═══════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════

def fit_hybrid_single(r, Vobs, eV, V2b, g_dag, r0):
    """
    Fit single galaxy: V² = V²_bar·μ(g) + A·r/(r+r₀)
    Free: A_gal only (1 param).
    """
    g_bar = V2b * G_CONV / np.maximum(r, 1e-10)
    mu = (1.0 + g_dag / np.maximum(g_bar, 1e-30))**K_LOCKED
    V2_screening = V2b * mu

    # Profile shape (fixed by global r₀)
    profile = r / (r + r0)

    # Optimal A: minimize χ² = Σ((Vobs - sqrt(V2_screening + A·profile))/eV)²
    # This is nonlinear in A, use scalar optimization
    def chi2_A(A):
        V2_total = V2_screening + A * profile
        V_pred = np.sqrt(np.maximum(V2_total, 0.0))
        return np.sum(((Vobs - V_pred) / eV)**2)

    # Search range for A: 0 to max(Vobs²)
    A_max = float(np.max(Vobs**2)) * 5
    res = minimize_scalar(chi2_A, bounds=(-A_max, A_max), method='bounded')
    return res.x, res.fun


def fit_nfw_single(r, Vobs, eV, V2b):
    """NFW + baryons (2 params: V200, c)."""
    def chi2_func(params):
        V200, c = params
        r200 = V200 / (10.0 * 0.0724)
        x = np.maximum(r * c / r200, 1e-10)
        f_c = np.log(1.0 + c) - c / (1.0 + c)
        f_x = np.log(1.0 + x) - x / (1.0 + x)
        V2_halo = V200**2 * f_x / (f_c * x)
        V_pred = np.sqrt(np.maximum(V2b + V2_halo, 0.0))
        return np.sum(((Vobs - V_pred) / eV)**2)

    try:
        res = differential_evolution(chi2_func, bounds=[(10, 400), (1, 50)],
                                     seed=42, maxiter=300, tol=1e-4)
        return res.fun
    except Exception:
        return np.inf


def fit_screening_single(r, Vobs, eV, V2b, g_dag):
    """Pure screening (0 per-galaxy params)."""
    g_bar = V2b * G_CONV / np.maximum(r, 1e-10)
    mu = (1.0 + g_dag / np.maximum(g_bar, 1e-30))**K_LOCKED
    V_pred = np.sqrt(V2b * mu)
    return float(np.sum(((Vobs - V_pred) / eV)**2))


# ═══════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════

def main():
    print("=" * 80)
    print("ONE-PARAMETER-PER-GALAXY TEST")
    print("V² = V²_bar·μ(g) + A_gal·r/(r+r₀)")
    print("1 param/galaxy vs NFW's 2 params/galaxy")
    print("=" * 80)

    galaxies = load_sparc()
    regimes = load_regimes()
    n_gal = len(galaxies)
    print(f"\n  {n_gal} galaxies")

    # Precompute V²_bar
    gal_list = sorted(galaxies.keys())
    V2b_all = {n: np.maximum(v2_bar(galaxies[n]), 1e-10) for n in gal_list}

    # Global g† from screening
    print("\n[GLOBAL] Fitting screening g†...")
    def total_screening_chi2(log_gdag):
        g_dag = 10**log_gdag
        chi2 = 0.0
        for n in gal_list:
            chi2 += fit_screening_single(galaxies[n]["r"], galaxies[n]["Vobs"],
                                          galaxies[n]["eV"], V2b_all[n], g_dag)
        return chi2
    res_gdag = minimize_scalar(total_screening_chi2, bounds=(-11, -8), method='bounded')
    g_dag = 10**res_gdag.x
    print(f"  g† = {g_dag:.4e}")

    # Optimize global r₀ (outer loop) with per-galaxy A (inner loop)
    print("\n[HYBRID] Optimizing global r₀ + per-galaxy A...")

    def total_hybrid_chi2(log_r0):
        r0 = 10**log_r0
        chi2 = 0.0
        for n in gal_list:
            _, c = fit_hybrid_single(galaxies[n]["r"], galaxies[n]["Vobs"],
                                      galaxies[n]["eV"], V2b_all[n], g_dag, r0)
            chi2 += c
        return chi2

    # Grid search first for r₀
    best_chi2 = np.inf
    best_log_r0 = 0
    for log_r0 in np.linspace(-1, 2, 30):  # r₀ from 0.1 to 100 kpc
        c = total_hybrid_chi2(log_r0)
        if c < best_chi2:
            best_chi2 = c
            best_log_r0 = log_r0

    # Polish
    res_r0 = minimize_scalar(total_hybrid_chi2,
                              bounds=(best_log_r0 - 0.5, best_log_r0 + 0.5),
                              method='bounded')
    r0 = 10**res_r0.x
    print(f"  r₀ = {r0:.2f} kpc, total χ² = {res_r0.fun:.0f}")

    # ── Full per-galaxy fits ────────────────────────────────────────────────
    print(f"\n[PER-GALAXY] Fitting all three models...")

    results = {}
    for i, name in enumerate(gal_list):
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{n_gal}...")

        g = galaxies[name]
        r = g["r"]
        Vobs = g["Vobs"]
        eV = g["eV"]
        V2b = V2b_all[name]
        n = len(r)

        # Screening (0 params/galaxy)
        chi2_scr = fit_screening_single(r, Vobs, eV, V2b, g_dag)

        # Hybrid (1 param/galaxy)
        A_gal, chi2_hyb = fit_hybrid_single(r, Vobs, eV, V2b, g_dag, r0)

        # NFW (2 params/galaxy)
        chi2_nfw = fit_nfw_single(r, Vobs, eV, V2b)

        # AIC: screening has 0 per-gal params, hybrid has 1, NFW has 2
        aic_scr = chi2_scr
        aic_hyb = chi2_hyb + 2 * 1
        aic_nfw = chi2_nfw + 2 * 2

        # Winners
        daic_hyb_nfw = aic_hyb - aic_nfw

        results[name] = {
            "chi2_scr": chi2_scr,
            "chi2_hyb": chi2_hyb,
            "chi2_nfw": chi2_nfw,
            "A_gal": float(A_gal),
            "aic_hyb": aic_hyb,
            "aic_nfw": aic_nfw,
            "daic_hyb_nfw": float(daic_hyb_nfw),
            "winner_hyb_nfw": "HYBRID" if daic_hyb_nfw < -10 else
                              ("NFW" if daic_hyb_nfw > 10 else "TIE"),
            "daic_scr_nfw": chi2_scr - aic_nfw,
            "winner_scr_nfw": "EFC" if (chi2_scr - aic_nfw) < -10 else
                              ("NFW" if (chi2_scr - aic_nfw) > 10 else "TIE"),
            "chi2_red_hyb": chi2_hyb / max(n - 1, 1),
            "chi2_red_nfw": chi2_nfw / max(n - 2, 1),
            "chi2_red_scr": chi2_scr / max(n, 1),
            "regime": regimes.get(name, "UNKNOWN"),
            "n": n,
        }

    # ── RESULTS ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    # Overall
    for model, chi2_key, win_key in [
        ("Screening (0/gal)", "chi2_red_scr", "winner_scr_nfw"),
        ("Hybrid (1/gal)", "chi2_red_hyb", "winner_hyb_nfw"),
    ]:
        w = Counter(r[win_key] for r in results.values())
        pos_key = "EFC" if "scr" in win_key else "HYBRID"
        wins = w.get(pos_key, 0) + w.get("TIE", 0)
        chi2_arr = np.array([r[chi2_key] for r in results.values()])
        total_chi2 = sum(r[chi2_key.replace("red_", "")] for r in results.values())
        print(f"\n  {model}:")
        print(f"    Win vs NFW: {100*wins/n_gal:.1f}% ({wins}/{n_gal})")
        print(f"    Med χ²/dof: {np.median(chi2_arr):.2f}")
        print(f"    Total χ²:   {total_chi2:.0f}")

    nfw_chi2_arr = np.array([r["chi2_red_nfw"] for r in results.values()])
    print(f"\n  NFW (2/gal):")
    print(f"    Med χ²/dof: {np.median(nfw_chi2_arr):.2f}")

    # ── REGIME BREAKDOWN ────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("REGIME BREAKDOWN")
    print("=" * 80)

    for regime in ["FLOW", "TRANSITION", "LATENT"]:
        rv = {n: r for n, r in results.items() if r["regime"] == regime}
        if not rv:
            continue
        n_r = len(rv)

        w_scr = Counter(r["winner_scr_nfw"] for r in rv.values())
        w_hyb = Counter(r["winner_hyb_nfw"] for r in rv.values())

        scr_wins = w_scr.get("EFC", 0) + w_scr.get("TIE", 0)
        hyb_wins = w_hyb.get("HYBRID", 0) + w_hyb.get("TIE", 0)

        chi2_scr = np.median([r["chi2_red_scr"] for r in rv.values()])
        chi2_hyb = np.median([r["chi2_red_hyb"] for r in rv.values()])
        chi2_nfw = np.median([r["chi2_red_nfw"] for r in rv.values()])

        print(f"\n  {regime} (n={n_r}):")
        print(f"    Screening (0/gal): {100*scr_wins/n_r:5.1f}% win, "
              f"med χ²/dof={chi2_scr:.2f}")
        print(f"    Hybrid    (1/gal): {100*hyb_wins/n_r:5.1f}% win, "
              f"med χ²/dof={chi2_hyb:.2f}")
        print(f"    NFW       (2/gal): reference,      "
              f"med χ²/dof={chi2_nfw:.2f}")

    # ── KEY DIAGNOSTIC ──────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("KEY DIAGNOSTIC: 1 PARAM vs 2 PARAMS IN FLOW")
    print("=" * 80)

    flow_results = {n: r for n, r in results.items() if r["regime"] == "FLOW"}
    if flow_results:
        n_flow = len(flow_results)
        hyb_flow_wins = sum(1 for r in flow_results.values()
                           if r["winner_hyb_nfw"] in ("HYBRID", "TIE"))
        scr_flow_wins = sum(1 for r in flow_results.values()
                           if r["winner_scr_nfw"] in ("EFC", "TIE"))

        print(f"\n  FLOW (n={n_flow}):")
        print(f"    Screening vs NFW:  {100*scr_flow_wins/n_flow:.1f}%")
        print(f"    Hybrid vs NFW:     {100*hyb_flow_wins/n_flow:.1f}%")
        print(f"    Δ:                 {100*(hyb_flow_wins-scr_flow_wins)/n_flow:+.1f}pp")

        # A_gal distribution in FLOW
        A_flow = np.array([r["A_gal"] for r in flow_results.values()])
        print(f"\n  A_gal in FLOW:")
        print(f"    Mean:   {np.mean(A_flow):+.0f} (km/s)²")
        print(f"    Median: {np.median(A_flow):+.0f} (km/s)²")
        print(f"    Std:    {np.std(A_flow):.0f} (km/s)²")
        print(f"    Range:  [{np.min(A_flow):.0f}, {np.max(A_flow):.0f}]")

    # A_gal distribution by regime
    print(f"\n  A_gal by regime:")
    for regime in ["FLOW", "TRANSITION", "LATENT"]:
        rv = [r["A_gal"] for r in results.values() if r["regime"] == regime]
        if rv:
            arr = np.array(rv)
            print(f"    {regime:>11}: median={np.median(arr):+8.0f}, "
                  f"mean={np.mean(arr):+8.0f} (km/s)²")

    # ── VERDICT ─────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("VERDICT")
    print("=" * 80)

    if flow_results:
        flow_improvement = 100*(hyb_flow_wins - scr_flow_wins)/n_flow

        lat_results = {n: r for n, r in results.items() if r["regime"] == "LATENT"}
        if lat_results:
            hyb_lat_wins = sum(1 for r in lat_results.values()
                              if r["winner_hyb_nfw"] in ("HYBRID", "TIE"))
            n_lat = len(lat_results)
            lat_pct = 100 * hyb_lat_wins / n_lat
        else:
            lat_pct = 0

        print(f"\n  FLOW improvement: {flow_improvement:+.1f}pp (0→1 param)")

        if flow_improvement > 20 and lat_pct > 60:
            print("\n  ═══════════════════════════════════════════════════")
            print("  ONE PARAMETER IS SUFFICIENT")
            print("  EFC + A_gal beats NFW in parsimony")
            print("  ═══════════════════════════════════════════════════")
        elif flow_improvement > 10:
            print("\n  ═══════════════════════════════════════════════════")
            print("  ONE PARAMETER HELPS BUT MAY NOT SUFFICE")
            print("  ═══════════════════════════════════════════════════")
        else:
            print("\n  ═══════════════════════════════════════════════════")
            print("  ONE PARAMETER IS NOT ENOUGH")
            print("  Need ≥2 per-galaxy degrees of freedom")
            print("  ═══════════════════════════════════════════════════")

    # ── COMPLETE TABLE ──────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print("COMPLETE MODEL HIERARCHY")
    print("=" * 80)
    print(f"\n  {'Model':<35} {'Params/gal':>10} {'FLOW%':>7} {'LATENT%':>8}")
    print("  " + "-" * 65)

    # Screening
    flow_scr = sum(1 for r in flow_results.values()
                   if r["winner_scr_nfw"] in ("EFC", "TIE"))
    lat_scr = sum(1 for r in lat_results.values()
                  if r["winner_scr_nfw"] in ("EFC", "TIE")) if lat_results else 0
    print(f"  {'Screening μ(g)':<35} {'0':>10} {100*flow_scr/n_flow:>6.1f}% "
          f"{100*lat_scr/n_lat:>7.1f}%")

    print(f"  {'Hybrid μ(g) + A·f(r)':<35} {'1':>10} "
          f"{100*hyb_flow_wins/n_flow:>6.1f}% {lat_pct:>7.1f}%")

    # NFW is reference (always 100% by definition of comparison)
    print(f"  {'NFW + baryons':<35} {'2':>10} {'ref':>7} {'ref':>8}")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {
            "experiment": "1-parameter-per-galaxy test",
            "date": datetime.datetime.now().isoformat(),
            "g_dag": float(g_dag),
            "r0_kpc": float(r0),
            "n_galaxies": n_gal,
        },
        "results_per_galaxy": {
            name: {k: v for k, v in r.items() if k != "regime"}
            for name, r in results.items()
        },
    }
    with open(OUTPUT_DIR / "one_param_results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to {OUTPUT_DIR}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
