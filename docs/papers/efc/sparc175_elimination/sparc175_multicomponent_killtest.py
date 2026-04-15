#!/usr/bin/env python3
"""
SPARC 175 Multi-Component Kill-Test — Bose-Einstein μ + Frozen Υ

Physics model (EFC Covariant EFT, Eq. 15):
    G_eff(g) = G_N · [1 + 1/(exp(√(g/a₀)) - 1)]
    μ(g_bar) = G_eff / G_N

Rotation curve prediction:
    V²_bar(r) = V²_gas + Υ_d · V²_disk + Υ_b · V²_bul
    g_bar(r)  = V²_bar / r
    V²_pred(r) = V²_bar · μ(g_bar)

Global parameters: a₀ (single, from EFT)
Per-galaxy parameters: NONE (Υ_d=0.5, Υ_b=0.7 frozen)

Comparison: NFW halo (2 free params per galaxy: V200, c)

Kill-Test metric: per-galaxy χ², ΔAIC(EFC-NFW), aggregate statistics.
"""

import json
import numpy as np
from pathlib import Path
from scipy.optimize import minimize_scalar, differential_evolution
from collections import defaultdict, Counter
import hashlib
import datetime

# ─── Paths ───────────────────────────────────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "sparc"
SPARC_DAT = DATA_DIR / "sparc_rotation_curves.dat"
CLASSIFIED_JSON = DATA_DIR / "sparc175_classified.json"
OUTPUT_DIR = Path(__file__).resolve().parent / "sparc175_multicomponent_results"

# ─── Frozen parameters ──────────────────────────────────────────────────────
UPSILON_DISK = 0.5    # M☉/L☉ (3.6μm band, standard SPARC)
UPSILON_BULGE = 0.7   # M☉/L☉ (3.6μm band, standard SPARC)
MIN_ERROR = 1.0       # km/s error floor

# ─── Physical constants ─────────────────────────────────────────────────────
# a₀ ~ 1.2e-10 m/s² (MOND scale, consistent with EFC g†)
# Convert to kpc/(km/s)² units for direct use with SPARC data:
#   g [m/s²] = V² [km²/s²] / r [kpc] × (1e6 / 3.086e19)
#   g [m/s²] = V² / r × 3.241e-14
#   So: g/a₀ = V²/(r · a₀) × 3.241e-14
KPC_TO_M = 3.0857e19     # 1 kpc in meters
KMS_TO_MS = 1e3           # 1 km/s in m/s
# g_bar in m/s²: g = (V_bar * 1e3)² / (r * 3.0857e19)
G_CONV = KMS_TO_MS**2 / KPC_TO_M  # = 1e6 / 3.0857e19 = 3.241e-14


# ─── Physics models ─────────────────────────────────────────────────────────

def mu_bose_einstein(g_bar_ms2, a0):
    """
    Bose-Einstein μ-function (EFC Covariant EFT, Eq. 15).

    μ(g) = 1 + 1/(exp(√(g/a₀)) - 1)

    Args:
        g_bar_ms2: baryonic acceleration in m/s²
        a0: critical acceleration in m/s²

    Returns:
        μ enhancement factor (≥1)
    """
    x = np.sqrt(np.maximum(g_bar_ms2 / a0, 1e-30))
    # Clip to avoid overflow in exp
    x_clipped = np.minimum(x, 500.0)
    exp_x = np.exp(x_clipped)
    # For very small x (deep MOND), μ → 1 + 1/x ≈ √(a₀/g)
    # For very large x (Newtonian), μ → 1
    mu = 1.0 + 1.0 / np.maximum(exp_x - 1.0, 1e-30)
    return mu


def v_pred_efc(r, Vgas, Vdisk, Vbul, a0):
    """
    EFC multi-component rotation curve prediction.

    V²_pred = V²_bar · μ(g_bar)
    V²_bar  = V²_gas + Υ_d·V²_disk + Υ_b·V²_bul
    g_bar   = V²_bar / r  (converted to m/s²)
    """
    # Baryonic velocity squared
    V2_bar = Vgas**2 + UPSILON_DISK * Vdisk**2 + UPSILON_BULGE * Vbul**2
    V2_bar = np.maximum(V2_bar, 1e-10)  # avoid zero

    # Baryonic acceleration in m/s²
    g_bar = V2_bar * G_CONV / np.maximum(r, 1e-10)

    # Apply μ
    mu = mu_bose_einstein(g_bar, a0)

    # Predicted velocity
    V2_pred = V2_bar * mu
    return np.sqrt(np.maximum(V2_pred, 0.0))


def v_halo_nfw(r, V200, c):
    """
    NFW dark matter halo contribution to rotation curve.

    v²_halo(r) = V200² · [ln(1+x) - x/(1+x)] / [ln(1+c) - c/(1+c)] / x
    where x = r·c / r200, r200 = V200 / (10·H0)
    """
    H0_kpc = 0.0724  # H0 in km/s/kpc (≈72.4 km/s/Mpc)
    r200 = V200 / (10.0 * H0_kpc)
    x = np.maximum(r * c / r200, 1e-10)
    f_c = np.log(1.0 + c) - c / (1.0 + c)
    f_x = np.log(1.0 + x) - x / (1.0 + x)
    V2_halo = V200**2 * f_x / (f_c * x)
    return V2_halo  # returns V²_halo, not V


def v_pred_nfw_total(r, Vgas, Vdisk, Vbul, V200, c):
    """
    NFW total rotation curve: baryons + dark halo.

    V²_total = V²_bar + V²_halo
    V²_bar   = V²_gas + Υ_d·V²_disk + Υ_b·V²_bul
    """
    V2_bar = Vgas**2 + UPSILON_DISK * Vdisk**2 + UPSILON_BULGE * Vbul**2
    V2_halo = v_halo_nfw(r, V200, c)
    V2_total = V2_bar + np.maximum(V2_halo, 0.0)
    return np.sqrt(np.maximum(V2_total, 0.0))


# ─── Data loading ────────────────────────────────────────────────────────────

def parse_sparc_dat(path):
    """Parse multi-galaxy SPARC rotation curves file.

    Columns: name distance radius Vobs eV Vgas Vdisk Vbul SBdisk SBbul
    """
    galaxies = defaultdict(lambda: {
        "r": [], "Vobs": [], "eV": [],
        "Vgas": [], "Vdisk": [], "Vbul": []
    })

    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 8:
                continue
            try:
                name = parts[0]
                r = float(parts[2])
                Vobs = float(parts[3])
                eV = max(float(parts[4]), MIN_ERROR)
                Vgas = float(parts[5])
                Vdisk = float(parts[6])
                Vbul = float(parts[7])
                galaxies[name]["r"].append(r)
                galaxies[name]["Vobs"].append(Vobs)
                galaxies[name]["eV"].append(eV)
                galaxies[name]["Vgas"].append(Vgas)
                galaxies[name]["Vdisk"].append(Vdisk)
                galaxies[name]["Vbul"].append(Vbul)
            except (ValueError, IndexError):
                continue

    # Convert to numpy
    for name in galaxies:
        for key in galaxies[name]:
            galaxies[name][key] = np.array(galaxies[name][key])

    return dict(galaxies)


# ─── Fitting ─────────────────────────────────────────────────────────────────

def fit_efc_global_a0(galaxies, a0_range=(0.5e-10, 5.0e-10)):
    """
    Find optimal global a₀ by minimizing total χ² across all galaxies.

    EFC has 0 free params per galaxy — only 1 global a₀.
    """
    def total_chi2(log_a0):
        a0 = 10**log_a0
        chi2_sum = 0.0
        for name, g in galaxies.items():
            V_pred = v_pred_efc(g["r"], g["Vgas"], g["Vdisk"], g["Vbul"], a0)
            chi2 = np.sum(((g["Vobs"] - V_pred) / g["eV"])**2)
            chi2_sum += chi2
        return chi2_sum

    result = minimize_scalar(
        total_chi2,
        bounds=(np.log10(a0_range[0]), np.log10(a0_range[1])),
        method='bounded',
        options={'xatol': 1e-6}
    )

    best_a0 = 10**result.x
    best_chi2 = result.fun
    return best_a0, best_chi2


def fit_nfw_single(r, Vobs, eV, Vgas, Vdisk, Vbul):
    """Fit NFW halo + baryons to a single galaxy (2 free params: V200, c)."""
    def chi2_func(params):
        V200, c = params
        V_pred = v_pred_nfw_total(r, Vgas, Vdisk, Vbul, V200, c)
        return np.sum(((Vobs - V_pred) / eV)**2)

    try:
        result = differential_evolution(
            chi2_func,
            bounds=[(10, 400), (1, 50)],
            seed=42,
            maxiter=300,
            tol=1e-4,
        )
        return {
            "success": True,
            "params": {"V200": result.x[0], "c": result.x[1]},
            "chi2": result.fun,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


# ─── Main pipeline ──────────────────────────────────────────────────────────

def main():
    print("=" * 80)
    print("SPARC 175 MULTI-COMPONENT KILL-TEST")
    print("Model: Bose-Einstein μ (EFC EFT Eq. 15) + Frozen Υ")
    print("=" * 80)

    # Load data
    print(f"\nLoading SPARC data from {SPARC_DAT}")
    galaxies = parse_sparc_dat(SPARC_DAT)
    n_gal = len(galaxies)
    n_pts = sum(len(g["r"]) for g in galaxies.values())
    print(f"  {n_gal} galaxies, {n_pts} data points")

    # Load regime classification
    classified = {}
    if CLASSIFIED_JSON.exists():
        with open(CLASSIFIED_JSON) as f:
            cdata = json.load(f)
        for name, info in cdata.get("results", {}).items():
            classified[name] = info.get("regime", "UNKNOWN")
        print(f"  {len(classified)} galaxies classified")

    # ── Step 1: Find global a₀ ──────────────────────────────────────────────
    print("\n[STEP 1] Optimizing global a₀...")
    best_a0, total_chi2_efc = fit_efc_global_a0(galaxies)
    print(f"  Best a₀ = {best_a0:.4e} m/s²")
    print(f"  Total χ² (EFC) = {total_chi2_efc:.1f}")
    print(f"  a₀/a₀_MOND = {best_a0 / 1.2e-10:.3f}")

    # ── Step 2: Per-galaxy EFC predictions with best a₀ ─────────────────────
    print(f"\n[STEP 2] Computing per-galaxy EFC predictions (a₀ = {best_a0:.3e})...")
    efc_results = {}
    for name, g in sorted(galaxies.items()):
        r, Vobs, eV = g["r"], g["Vobs"], g["eV"]
        Vgas, Vdisk, Vbul = g["Vgas"], g["Vdisk"], g["Vbul"]

        V_pred = v_pred_efc(r, Vgas, Vdisk, Vbul, best_a0)

        chi2 = float(np.sum(((Vobs - V_pred) / eV)**2))
        n = len(r)
        k_efc = 1  # Only a₀ (global, shared) — effectively 0 free per galaxy
        # For AIC: count a₀ as 1 global param amortized over N galaxies
        # Per-galaxy effective params = 1/N_gal ≈ 0
        # But for honest comparison, count as 0 per-galaxy free params
        chi2_red = chi2 / max(n - 0, 1)  # 0 free params per galaxy
        aic = chi2 + 2 * 0  # 0 free params per galaxy
        bic = chi2 + 0 * np.log(n)

        efc_results[name] = {
            "chi2": chi2,
            "chi2_red": chi2_red,
            "aic": aic,
            "bic": bic,
            "n_points": n,
        }

    # ── Step 3: Fit NFW per galaxy ──────────────────────────────────────────
    print(f"\n[STEP 3] Fitting NFW to {n_gal} galaxies...")
    nfw_results = {}
    n_success = 0
    for i, (name, g) in enumerate(sorted(galaxies.items())):
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{n_gal}...")

        result = fit_nfw_single(g["r"], g["Vobs"], g["eV"], g["Vgas"], g["Vdisk"], g["Vbul"])
        if result["success"]:
            n = len(g["r"])
            k_nfw = 2
            chi2 = result["chi2"]
            nfw_results[name] = {
                "chi2": chi2,
                "chi2_red": chi2 / max(n - k_nfw, 1),
                "aic": chi2 + 2 * k_nfw,
                "bic": chi2 + k_nfw * np.log(n),
                "n_points": n,
                "params": result["params"],
            }
            n_success += 1
        else:
            nfw_results[name] = {"chi2": np.inf, "aic": np.inf, "failed": True}

    print(f"  NFW: {n_success}/{n_gal} successful fits")

    # ── Step 4: Compute ΔAIC and verdict ────────────────────────────────────
    print("\n[STEP 4] Kill-Test verdict computation...")

    verdicts = {}
    for name in sorted(galaxies.keys()):
        efc = efc_results[name]
        nfw = nfw_results[name]

        if nfw.get("failed"):
            delta_aic = -999  # EFC wins by default
            winner = "EFC_DEFAULT"
        else:
            delta_aic = efc["aic"] - nfw["aic"]
            if delta_aic < -10:
                winner = "EFC"
            elif delta_aic > 10:
                winner = "NFW"
            else:
                winner = "TIE"

        regime = classified.get(name, "UNKNOWN")

        verdicts[name] = {
            "delta_aic": float(delta_aic),
            "winner": winner,
            "regime": regime,
            "efc_chi2": efc["chi2"],
            "efc_chi2_red": efc["chi2_red"],
            "nfw_chi2": nfw["chi2"] if not nfw.get("failed") else None,
            "nfw_chi2_red": nfw.get("chi2_red"),
            "n_points": efc["n_points"],
        }

    # ── Step 5: Aggregate statistics ────────────────────────────────────────
    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)

    valid = {k: v for k, v in verdicts.items() if v["winner"] != "EFC_DEFAULT"}
    winners = Counter(v["winner"] for v in valid.values())

    print(f"\n--- Global model comparison ---")
    print(f"  EFC params:  1 global (a₀ = {best_a0:.3e}), 0 per-galaxy")
    print(f"  NFW params:  0 global, 2 per-galaxy (V200, c)")
    print(f"  Υ_disk = {UPSILON_DISK}, Υ_bulge = {UPSILON_BULGE} (FROZEN)")

    print(f"\n--- Verdict distribution ---")
    n_valid = len(valid)
    for w in ["EFC", "TIE", "NFW"]:
        count = winners.get(w, 0)
        pct = 100 * count / n_valid if n_valid > 0 else 0
        print(f"  {w:>6}: {count:>4} ({pct:5.1f}%)")

    efc_win_rate = (winners.get("EFC", 0) + winners.get("TIE", 0)) / n_valid if n_valid > 0 else 0
    print(f"\n  EFC win+tie rate: {100*efc_win_rate:.1f}%")

    # Aggregate ΔAIC
    daic_arr = np.array([v["delta_aic"] for v in valid.values()])
    print(f"\n--- ΔAIC statistics ---")
    print(f"  Mean ΔAIC:   {np.mean(daic_arr):+.1f}")
    print(f"  Median ΔAIC: {np.median(daic_arr):+.1f}")
    print(f"  Sum ΔAIC:    {np.sum(daic_arr):+.1f}")
    print(f"  Std ΔAIC:    {np.std(daic_arr):.1f}")

    # χ² statistics
    efc_chi2_arr = np.array([v["efc_chi2_red"] for v in valid.values()])
    nfw_chi2_arr = np.array([v["nfw_chi2_red"] for v in valid.values()
                             if v["nfw_chi2_red"] is not None])
    print(f"\n--- χ²/dof statistics ---")
    print(f"  EFC:  mean={np.mean(efc_chi2_arr):.2f}, median={np.median(efc_chi2_arr):.2f}")
    print(f"  NFW:  mean={np.mean(nfw_chi2_arr):.2f}, median={np.median(nfw_chi2_arr):.2f}")

    # Per-regime breakdown
    print(f"\n--- Per-regime breakdown ---")
    for regime in ["FLOW", "TRANSITION", "LATENT", "UNKNOWN"]:
        r_verdicts = {k: v for k, v in valid.items() if v["regime"] == regime}
        if not r_verdicts:
            continue
        r_winners = Counter(v["winner"] for v in r_verdicts.values())
        r_daic = np.array([v["delta_aic"] for v in r_verdicts.values()])
        n_r = len(r_verdicts)
        efc_r = r_winners.get("EFC", 0) + r_winners.get("TIE", 0)
        print(f"\n  {regime} (n={n_r}):")
        print(f"    EFC wins+ties: {efc_r}/{n_r} ({100*efc_r/n_r:.1f}%)")
        print(f"    Mean ΔAIC: {np.mean(r_daic):+.1f}")
        print(f"    NFW wins: {r_winners.get('NFW', 0)}")

    # Mann-Whitney test: FLOW vs LATENT ΔAIC
    from scipy.stats import mannwhitneyu
    flow_daic = [v["delta_aic"] for v in valid.values() if v["regime"] == "FLOW"]
    latent_daic = [v["delta_aic"] for v in valid.values() if v["regime"] == "LATENT"]
    if len(flow_daic) >= 3 and len(latent_daic) >= 3:
        stat, p_mw = mannwhitneyu(flow_daic, latent_daic, alternative='two-sided')
        print(f"\n--- Regime separation test ---")
        print(f"  Mann-Whitney (FLOW vs LATENT): U={stat:.0f}, p={p_mw:.2e}")
        print(f"  Mean ΔAIC FLOW:   {np.mean(flow_daic):+.1f}")
        print(f"  Mean ΔAIC LATENT: {np.mean(latent_daic):+.1f}")

    # ── Step 6: Save results ────────────────────────────────────────────────
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Content hash for reproducibility
    result_str = json.dumps(verdicts, sort_keys=True, default=str)
    content_hash = hashlib.sha256(result_str.encode()).hexdigest()

    summary = {
        "metadata": {
            "test": "SPARC 175 Multi-Component Kill-Test",
            "model": "Bose-Einstein μ (EFC EFT Eq. 15)",
            "formula": "G_eff = G_N · [1 + 1/(exp(√(g/a₀)) - 1)]",
            "upsilon_disk": UPSILON_DISK,
            "upsilon_bulge": UPSILON_BULGE,
            "upsilon_strategy": "FROZEN",
            "efc_free_params_per_galaxy": 0,
            "efc_global_params": 1,
            "nfw_free_params_per_galaxy": 2,
            "best_a0_m_s2": float(best_a0),
            "a0_over_a0_mond": float(best_a0 / 1.2e-10),
            "n_galaxies": n_gal,
            "n_data_points": n_pts,
            "date": datetime.datetime.now().isoformat(),
            "content_hash": content_hash,
        },
        "results": {
            "efc_win": winners.get("EFC", 0),
            "nfw_win": winners.get("NFW", 0),
            "tie": winners.get("TIE", 0),
            "efc_win_rate": float(efc_win_rate),
            "total_chi2_efc": float(total_chi2_efc),
            "mean_delta_aic": float(np.mean(daic_arr)),
            "median_delta_aic": float(np.median(daic_arr)),
            "sum_delta_aic": float(np.sum(daic_arr)),
            "mean_chi2_red_efc": float(np.mean(efc_chi2_arr)),
            "mean_chi2_red_nfw": float(np.mean(nfw_chi2_arr)),
        },
        "verdicts": verdicts,
    }

    summary_path = OUTPUT_DIR / "summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n  Results saved to {summary_path}")

    # Verdict table (TSV for quick inspection)
    table_path = OUTPUT_DIR / "verdict_table.tsv"
    with open(table_path, "w") as f:
        f.write("Galaxy\tRegime\tΔAIC\tWinner\tχ²_EFC\tχ²_NFW\tN_pts\n")
        for name in sorted(verdicts.keys()):
            v = verdicts[name]
            nfw_chi2_str = f"{v['nfw_chi2']:.1f}" if v['nfw_chi2'] is not None else "FAIL"
            f.write(f"{name}\t{v['regime']}\t{v['delta_aic']:+.1f}\t{v['winner']}\t"
                    f"{v['efc_chi2']:.1f}\t{nfw_chi2_str}\t{v['n_points']}\n")
    print(f"  Verdict table saved to {table_path}")

    print(f"\n  Content hash: {content_hash[:16]}...")

    print("\n" + "=" * 80)
    print("KILL-TEST COMPLETE")
    print(f"  a₀ = {best_a0:.4e} m/s² (a₀/a₀_MOND = {best_a0/1.2e-10:.3f})")
    print(f"  EFC (0 free params/galaxy) vs NFW (2 free params/galaxy)")
    print(f"  EFC win+tie rate: {100*efc_win_rate:.1f}%")
    print(f"  Aggregate ΔAIC: {np.sum(daic_arr):+.1f}")
    print("=" * 80)


if __name__ == "__main__":
    main()
