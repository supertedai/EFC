#!/usr/bin/env python3
"""
A_gal vs NFW Parameter Space — Is the hybrid just a reparametrisation?

Key question: Does A_gal map onto NFW's (V200, c)?
If A_gal ~ V200 and ignores c → hybrid compresses 2D NFW into 1D.
If A_gal ~ both → just reparametrisation (weaker claim).
If A_gal ~ neither → genuinely different representation.
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import differential_evolution
from scipy.stats import spearmanr, pearsonr
from collections import defaultdict
import datetime

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sparc"
SPARC_DAT = DATA_DIR / "sparc_rotation_curves.dat"
CLASSIFIED_JSON = DATA_DIR / "sparc175_classified.json"
ONE_PARAM_DIR = Path(__file__).resolve().parent / "sparc175_one_param_results"
OUTPUT_DIR = Path(__file__).resolve().parent / "sparc175_agal_vs_nfw"

UPSILON_DISK = 0.5
UPSILON_BULGE = 0.7
MIN_ERROR = 1.0


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


def fit_nfw(r, Vobs, eV, V2_bar):
    """Fit NFW+baryons, return (V200, c, chi2)."""
    def chi2_func(params):
        V200, c = params
        r200 = V200 / (10.0 * 0.0724)
        x = np.maximum(r * c / r200, 1e-10)
        f_c = np.log(1.0 + c) - c / (1.0 + c)
        f_x = np.log(1.0 + x) - x / (1.0 + x)
        V2_halo = V200**2 * f_x / (f_c * x)
        V_pred = np.sqrt(np.maximum(V2_bar + V2_halo, 0.0))
        return np.sum(((Vobs - V_pred) / eV)**2)

    try:
        res = differential_evolution(chi2_func, bounds=[(10, 400), (1, 50)],
                                     seed=42, maxiter=300, tol=1e-4)
        return {"V200": res.x[0], "c": res.x[1], "chi2": res.fun}
    except Exception:
        return None


def main():
    print("=" * 80)
    print("A_gal vs NFW PARAMETER SPACE")
    print("Is the hybrid model a reparametrisation of NFW?")
    print("=" * 80)

    galaxies = load_sparc()
    regimes = load_regimes()

    # Load A_gal
    with open(ONE_PARAM_DIR / "one_param_results.json") as f:
        prev = json.load(f)
    agal_data = prev["results_per_galaxy"]

    # Fit NFW to get (V200, c) per galaxy
    print(f"\n[NFW] Fitting {len(galaxies)} galaxies for (V200, c)...")
    results = {}
    for i, (name, g) in enumerate(sorted(galaxies.items())):
        if (i + 1) % 50 == 0:
            print(f"  {i+1}/{len(galaxies)}...")

        A = agal_data.get(name, {}).get("A_gal")
        if A is None:
            continue

        V2_bar = g["Vgas"]**2 + UPSILON_DISK * g["Vdisk"]**2 + UPSILON_BULGE * g["Vbul"]**2
        V2_bar = np.maximum(V2_bar, 1e-10)

        nfw = fit_nfw(g["r"], g["Vobs"], g["eV"], V2_bar)
        if nfw is None:
            continue

        results[name] = {
            "A_gal": A,
            "V200": nfw["V200"],
            "c": nfw["c"],
            "V200_sq": nfw["V200"]**2,
            "log_V200": float(np.log10(nfw["V200"])),
            "log_c": float(np.log10(nfw["c"])),
            "regime": regimes.get(name, "UNKNOWN"),
            "chi2_nfw": nfw["chi2"],
        }

    n = len(results)
    print(f"  {n} galaxies with both A_gal and NFW params")

    # Arrays (ensure 1D)
    names = sorted(results.keys())
    A = np.array([float(results[n]["A_gal"]) for n in names])
    V200 = np.array([float(results[n]["V200"]) for n in names])
    c_arr = np.array([float(results[n]["c"]) for n in names])
    V200_sq = V200**2
    log_V200 = np.log10(V200)
    log_c = np.log10(c_arr)

    # ══════════════════════════════════════════════════════════════════════
    # 1. CORRELATIONS: A_gal vs NFW params
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("1. A_gal vs NFW PARAMETERS")
    print("=" * 80)

    tests = [
        ("A_gal vs V200", A, V200),
        ("A_gal vs V200²", A, V200_sq),
        ("A_gal vs log(V200)", A, log_V200),
        ("A_gal vs c", A, c_arr),
        ("A_gal vs log(c)", A, log_c),
        ("|A_gal| vs V200", np.abs(A), V200),
        ("|A_gal| vs V200²", np.abs(A), V200_sq),
        ("|A_gal| vs c", np.abs(A), c_arr),
    ]

    print(f"\n  {'Test':<25} {'Spearman ρ':>12} {'p-value':>12} {'Pearson r':>12} {'p-value':>12}")
    print("  " + "-" * 75)

    for label, x, y in tests:
        rho_s, p_s = spearmanr(x, y)
        rho_p, p_p = pearsonr(x, y)
        marker = " ***" if p_s < 0.001 else (" **" if p_s < 0.01 else (" *" if p_s < 0.05 else ""))
        print(f"  {label:<25} {rho_s:>+12.4f} {p_s:>12.2e} {rho_p:>+12.4f} {p_p:>12.2e}{marker}")

    # ══════════════════════════════════════════════════════════════════════
    # 2. REGRESSION: Can A_gal be predicted from (V200, c)?
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("2. REGRESSION: A_gal ~ f(V200, c)")
    print("=" * 80)

    # A_gal ~ V200
    X1 = np.column_stack([np.ones(n), log_V200])
    b1 = np.linalg.lstsq(X1, A, rcond=None)[0]
    pred1 = X1 @ b1
    ss_tot = np.sum((A - np.mean(A))**2)
    R2_V200 = 1 - np.sum((A - pred1)**2) / ss_tot

    # A_gal ~ c
    X2 = np.column_stack([np.ones(n), log_c])
    b2 = np.linalg.lstsq(X2, A, rcond=None)[0]
    pred2 = X2 @ b2
    R2_c = 1 - np.sum((A - pred2)**2) / ss_tot

    # A_gal ~ V200 + c
    X3 = np.column_stack([np.ones(n), log_V200, log_c])
    b3 = np.linalg.lstsq(X3, A, rcond=None)[0]
    pred3 = X3 @ b3
    R2_both = 1 - np.sum((A - pred3)**2) / ss_tot

    # |A_gal| ~ V200 + c
    X4 = np.column_stack([np.ones(n), log_V200, log_c])
    b4 = np.linalg.lstsq(X4, np.abs(A), rcond=None)[0]
    pred4 = X4 @ b4
    ss_tot_abs = np.sum((np.abs(A) - np.mean(np.abs(A)))**2)
    R2_abs = 1 - np.sum((np.abs(A) - pred4)**2) / ss_tot_abs

    print(f"\n  R²(A_gal ~ log V200):          {R2_V200:.4f}")
    print(f"  R²(A_gal ~ log c):             {R2_c:.4f}")
    print(f"  R²(A_gal ~ log V200 + log c):  {R2_both:.4f}")
    print(f"  R²(|A_gal| ~ log V200 + log c): {R2_abs:.4f}")

    # ══════════════════════════════════════════════════════════════════════
    # 3. PER-REGIME ANALYSIS
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("3. PER-REGIME: A_gal vs V200")
    print("=" * 80)

    for regime in ["FLOW", "TRANSITION", "LATENT"]:
        r_data = [(results[n]["A_gal"], results[n]["V200"], results[n]["c"])
                  for n in names if results[n]["regime"] == regime]
        if len(r_data) < 5:
            continue
        r_A = np.array([x[0] for x in r_data])
        r_V = np.array([x[1] for x in r_data])
        r_c = np.array([x[2] for x in r_data])

        rho_V, p_V = spearmanr(r_A, r_V)
        rho_c, p_c = spearmanr(r_A, r_c)
        rho_absV, p_absV = spearmanr(np.abs(r_A), r_V)

        print(f"\n  {regime} (n={len(r_data)}):")
        print(f"    A vs V200:   ρ = {rho_V:+.4f} (p = {p_V:.2e})")
        print(f"    A vs c:      ρ = {rho_c:+.4f} (p = {p_c:.2e})")
        print(f"    |A| vs V200: ρ = {rho_absV:+.4f} (p = {p_absV:.2e})")

    # ══════════════════════════════════════════════════════════════════════
    # 4. RESIDUAL COMPARISON
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("4. RESIDUAL STRUCTURE: Hybrid vs NFW")
    print("=" * 80)

    from scipy.optimize import minimize_scalar
    G_CONV = 1e6 / 3.0857e19
    g_dag = prev["metadata"]["g_dag"]
    r0 = prev["metadata"]["r0_kpc"]

    hybrid_resid_all = []
    nfw_resid_all = []
    hybrid_resid_flow = []
    nfw_resid_flow = []

    for name, g in galaxies.items():
        if name not in results:
            continue

        r = g["r"]
        Vobs = g["Vobs"]
        eV = g["eV"]
        V2_bar = g["Vgas"]**2 + UPSILON_DISK * g["Vdisk"]**2 + UPSILON_BULGE * g["Vbul"]**2
        V2_bar = np.maximum(V2_bar, 1e-10)
        n_pts = len(r)

        # Hybrid prediction
        A_gal = results[name]["A_gal"]
        g_bar = V2_bar * G_CONV / np.maximum(r, 1e-10)
        mu = (1.0 + g_dag / np.maximum(g_bar, 1e-30))**0.415
        V2_hyb = V2_bar * mu + A_gal * r / (r + r0)
        V_hyb = np.sqrt(np.maximum(V2_hyb, 0.0))

        # NFW prediction
        V200 = results[name]["V200"]
        c = results[name]["c"]
        r200 = V200 / (10.0 * 0.0724)
        x = np.maximum(r * c / r200, 1e-10)
        f_c = np.log(1.0 + c) - c / (1.0 + c)
        f_x = np.log(1.0 + x) - x / (1.0 + x)
        V2_halo = V200**2 * f_x / (f_c * x)
        V_nfw = np.sqrt(np.maximum(V2_bar + V2_halo, 0.0))

        # Fractional residuals
        frac_hyb = (Vobs - V_hyb) / np.maximum(Vobs, 1)
        frac_nfw = (Vobs - V_nfw) / np.maximum(Vobs, 1)

        hybrid_resid_all.extend(frac_hyb.tolist())
        nfw_resid_all.extend(frac_nfw.tolist())

        if results[name]["regime"] == "FLOW":
            hybrid_resid_flow.extend(frac_hyb.tolist())
            nfw_resid_flow.extend(frac_nfw.tolist())

    hyb_all = np.array(hybrid_resid_all)
    nfw_all = np.array(nfw_resid_all)
    hyb_flow = np.array(hybrid_resid_flow)
    nfw_flow = np.array(nfw_resid_flow)

    print(f"\n  ALL GALAXIES ({len(hyb_all)} points):")
    print(f"    Hybrid: mean={np.mean(hyb_all):+.4f}, std={np.std(hyb_all):.4f}, "
          f"|mean|={np.mean(np.abs(hyb_all)):.4f}")
    print(f"    NFW:    mean={np.mean(nfw_all):+.4f}, std={np.std(nfw_all):.4f}, "
          f"|mean|={np.mean(np.abs(nfw_all)):.4f}")

    print(f"\n  FLOW ONLY ({len(hyb_flow)} points):")
    print(f"    Hybrid: mean={np.mean(hyb_flow):+.4f}, std={np.std(hyb_flow):.4f}, "
          f"|mean|={np.mean(np.abs(hyb_flow)):.4f}")
    print(f"    NFW:    mean={np.mean(nfw_flow):+.4f}, std={np.std(nfw_flow):.4f}, "
          f"|mean|={np.mean(np.abs(nfw_flow)):.4f}")

    # ══════════════════════════════════════════════════════════════════════
    # VERDICT
    # ══════════════════════════════════════════════════════════════════════
    print("\n" + "=" * 80)
    print("VERDICT: REPARAMETRISATION OR GENUINELY DIFFERENT?")
    print("=" * 80)

    # Rebuild arrays from consistent name ordering
    verdict_names = sorted(results.keys())
    A_v = np.array([float(results[nm]["A_gal"]) for nm in verdict_names])
    V200_v = np.array([float(results[nm]["V200"]) for nm in verdict_names])
    c_v = np.array([float(results[nm]["c"]) for nm in verdict_names])

    rho_AV, p_AV = spearmanr(A_v, V200_v)
    rho_Ac, p_Ac = spearmanr(A_v, c_v)
    rho_absV, p_absV = spearmanr(np.abs(A_v), V200_v)

    strong_V200 = abs(rho_absV) > 0.4 and p_absV < 0.001
    weak_c = abs(rho_Ac) < 0.3

    if strong_V200 and weak_c:
        print("\n  ═══════════════════════════════════════════════════")
        print("  COMPRESSION: Hybrid compresses 2D NFW → 1D")
        print(f"  |A_gal| tracks V200 (ρ={rho_absV:+.3f})")
        print(f"  A_gal ignores c (ρ={rho_Ac:+.3f})")
        print("  → A_gal ≈ effective halo amplitude")
        print("  → Concentration c is redundant given μ(g)")
        print("  ═══════════════════════════════════════════════════")
    elif strong_V200 and not weak_c:
        print("\n  PARTIAL: A_gal maps to both V200 and c")
        print("  → Closer to reparametrisation")
    else:
        print("\n  DIFFERENT: A_gal does not map onto NFW params")
        print("  → Genuinely different representation")

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output = {
        "metadata": {"date": datetime.datetime.now().isoformat(), "n": n},
        "correlations": {
            "A_vs_V200": {"rho": float(rho_AV), "p": float(p_AV)},
            "A_vs_c": {"rho": float(rho_Ac), "p": float(p_Ac)},
            "absA_vs_V200": {"rho": float(rho_absV), "p": float(p_absV)},
        },
        "regression": {
            "R2_V200": float(R2_V200),
            "R2_c": float(R2_c),
            "R2_both": float(R2_both),
            "R2_abs_both": float(R2_abs),
        },
        "residuals": {
            "hybrid_all_mean_abs": float(np.mean(np.abs(hyb_all))),
            "nfw_all_mean_abs": float(np.mean(np.abs(nfw_all))),
            "hybrid_flow_mean_abs": float(np.mean(np.abs(hyb_flow))),
            "nfw_flow_mean_abs": float(np.mean(np.abs(nfw_flow))),
        },
    }
    with open(OUTPUT_DIR / "agal_vs_nfw.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\n  Saved to {OUTPUT_DIR}/")
    print("=" * 80)


if __name__ == "__main__":
    main()
