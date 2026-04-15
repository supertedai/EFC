#!/usr/bin/env python
"""demo_component_weighted_bias.py

Demonstrates the main results from Magnusson (2026):
  - Compute B and Bbulge for synthetic SPARC-like galaxies
  - Reproduce the correlation between Bbulge and ΔAIC
  - Show the EFC win-rate dependence on Bbulge
"""

import numpy as np
import json

from component_weighted_bias import (
    total_circular_velocity,
    chi_squared,
    inner_weight_fraction,
    component_weighted_bias,
    is_model_selection_biased,
    split_chi_squared,
    delta_aic,
    RC_DEFAULT_KPC,
    EFC_K,
    N_SPARC,
    N_NO_BULGE,
    N_BULGE,
)

np.random.seed(2026)

# ---- Synthesise a population of 175 SPARC-like galaxies ----
N_GAL = N_SPARC
results = []

for g in range(N_GAL):
    N_pts = np.random.randint(15, 60)
    r = np.sort(np.random.uniform(0.3, 25.0, N_pts))
    sigma = np.random.uniform(2.0, 6.0) + 0.04 * r

    # Decide if galaxy has bulge (32/175 ≈ 18.3 %)
    has_bulge = np.random.rand() < (N_BULGE / N_SPARC)
    V_gas = np.random.uniform(15, 30) * np.ones(N_pts)
    V_disk = np.random.uniform(60, 120) * np.exp(-r / np.random.uniform(3, 7))
    V_bulge = (
        np.random.uniform(80, 160) * np.exp(-r / np.random.uniform(1.0, 2.5))
        if has_bulge
        else np.zeros(N_pts)
    )

    # Two competing halo models: NFW-like (2 free params) vs EFC-like (1 param)
    V_halo_true = np.random.uniform(120, 180) * np.sqrt(1 - np.exp(-r / 8.0))
    V_tot = total_circular_velocity(V_gas, V_disk, V_bulge, V_halo_true)
    V_obs = V_tot + np.random.normal(0, sigma)

    # NFW fit: allow concentration to absorb inner residuals
    c_nfw = np.random.uniform(5, 20)
    V_halo_nfw = V_halo_true * (1 + 0.02 * (c_nfw - 10) * np.exp(-r / 3.0))
    V_pred_nfw = total_circular_velocity(V_gas, V_disk, V_bulge, V_halo_nfw)
    chi2_nfw = chi_squared(V_obs, V_pred_nfw, sigma)

    # EFC fit: fixed k = 0.415, slightly worse inner fit
    V_halo_efc = V_halo_true * (1 + 0.01 * np.sin(r * EFC_K))
    V_pred_efc = total_circular_velocity(V_gas, V_disk, V_bulge, V_halo_efc)
    chi2_efc = chi_squared(V_obs, V_pred_efc, sigma)

    daic = delta_aic(chi2_nfw, k_a=2, chi2_b=chi2_efc, k_b=1, n=N_pts)
    B = inner_weight_fraction(r, sigma)
    Bb = component_weighted_bias(V_bulge, V_tot, sigma)

    chi2_in, chi2_out = split_chi_squared(r, V_obs, V_pred_nfw, sigma)
    chi2_in_e, chi2_out_e = split_chi_squared(r, V_obs, V_pred_efc, sigma)
    daic_inner = delta_aic(chi2_in, 2, chi2_in_e, 1, N_pts)
    daic_outer = delta_aic(chi2_out, 0, chi2_out_e, 0, N_pts)

    results.append(dict(Bbulge=Bb, B=B, dAIC=daic, dAIC_outer=daic_outer, biased=is_model_selection_biased(Bb, daic_outer, daic)))

# ---- Analysis ----
Bb_arr = np.array([r["Bbulge"] for r in results])
daic_arr = np.array([r["dAIC"] for r in results])

from scipy.stats import spearmanr
rho, pval = spearmanr(Bb_arr, daic_arr)

low_mask = Bb_arr < 0.1
high_mask = Bb_arr > 0.2
efc_win_low = np.mean(daic_arr[low_mask] >= 0) if low_mask.any() else float("nan")
efc_win_high = np.mean(daic_arr[high_mask] >= 0) if high_mask.any() else float("nan")

print("=" * 60)
print("Component-weighted bias demo  (Magnusson 2026)")
print("=" * 60)
print(f"Galaxies simulated       : {N_GAL}")
print(f"With bulge               : {sum(1 for r in results if r['Bbulge'] > 0)}")
print(f"Spearman ρ(Bbulge, ΔAIC) : {rho:.3f}  (p = {pval:.4f})")
print(f"Paper value              : ρ = 0.176  (p = 0.020)")
print(f"EFC win rate Bbulge<0.1  : {efc_win_low:.1%}  (paper: 91.9%)")
print(f"EFC win rate Bbulge>0.2  : {efc_win_high:.1%}  (paper: 44.4%)")
print(f"Biased galaxies (Eq.6)   : {sum(1 for r in results if r['biased'])}")
print("=" * 60)

# ---- Optional plot ----
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    ax = axes[0]
    ax.scatter(Bb_arr, daic_arr, s=12, alpha=0.6, edgecolors="none")
    ax.axhline(0, color="grey", ls="--", lw=0.8)
    ax.axvline(0.1, color="red", ls=":", lw=0.8, label="Bbulge = 0.1")
    ax.axvline(0.2, color="red", ls="-.", lw=0.8, label="Bbulge = 0.2")
    ax.set_xlabel(r"$B_{\mathrm{bulge}}$")
    ax.set_ylabel(r"$\Delta$AIC (NFW − EFC)")
    ax.set_title(f"Spearman ρ = {rho:.3f}, p = {pval:.3f}")
    ax.legend(fontsize=8)

    ax = axes[1]
    bins = [0, 0.1, 0.2, 0.5, 1.0]
    labels = ["<0.1", "0.1–0.2", "0.2–0.5", ">0.5"]
    win_rates = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        m = (Bb_arr >= lo) & (Bb_arr < hi)
        win_rates.append(np.mean(daic_arr[m] >= 0) if m.any() else 0)
    ax.bar(labels, win_rates, color=["#2ca02c", "#ff7f0e", "#d62728", "#9467bd"])
    ax.set_ylabel("EFC win/tie fraction")
    ax.set_xlabel(r"$B_{\mathrm{bulge}}$ bin")
    ax.set_title("EFC win rate by bias bin")
    ax.set_ylim(0, 1.05)

    plt.tight_layout()
    plt.savefig("component_weighted_bias_demo.png", dpi=150)
    print("Plot saved to component_weighted_bias_demo.png")
    plt.show()
except ImportError:
    print("matplotlib not available – skipping plot.")
