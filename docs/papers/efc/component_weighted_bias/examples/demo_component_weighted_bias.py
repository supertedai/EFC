"""demo_component_weighted_bias.py

Demonstrates the key results of Magnusson (2026):
  • Compute B and Bbulge for synthetic SPARC-like galaxies
  • Reproduce the Spearman correlation between Bbulge and ΔAIC
  • Show the EFC win-rate split by Bbulge threshold
  • Optionally plot Bbulge vs ΔAIC
"""

import numpy as np
from scipy import stats

from component_weighted_bias import (
    total_velocity_squared,
    inner_weight_fraction,
    component_weighted_bias,
    chi_squared,
    delta_aic,
    bias_condition,
    split_delta_aic,
    RC_DEFAULT_KPC,
    EFC_K,
)

np.random.seed(2026)

# ------------------------------------------------------------------
# 1. Generate a synthetic SPARC-like sample (175 galaxies)
# ------------------------------------------------------------------
N_GAL = 175
N_PTS = 40  # data points per galaxy

bbulge_arr = np.zeros(N_GAL)
daic_arr = np.zeros(N_GAL)

for g in range(N_GAL):
    r = np.linspace(0.3, 18.0, N_PTS)
    sig = np.random.uniform(3, 8, N_PTS) + 2.0 * (r < RC_DEFAULT_KPC)

    # Random bulge strength (81.7 % have zero bulge per the paper)
    has_bulge = np.random.rand() > 0.817
    bulge_amp = np.random.uniform(80, 200) if has_bulge else 0.0
    vb = bulge_amp * np.exp(-r / 1.2)
    vd = np.random.uniform(60, 130) * np.exp(-r / 4.0)
    vg = np.random.uniform(10, 30) * np.ones(N_PTS)

    # Model A (NFW-like, 2 free params); Model B (EFC-like, 1 free param)
    v_halo_a = np.random.uniform(100, 180) * np.sqrt(1 - np.exp(-r / np.random.uniform(3, 8)))
    v_halo_b = np.random.uniform(100, 180) * np.sqrt(1 - np.exp(-r / (EFC_K * 10)))

    vtot_a = np.sqrt(total_velocity_squared(vg, vd, vb, v_halo_a))
    vtot_b = np.sqrt(total_velocity_squared(vg, vd, vb, v_halo_b))

    # Observed = truth (model B) + noise
    vobs = vtot_b + np.random.normal(0, 4, N_PTS)

    chi2_a = chi_squared(vobs, vtot_a, sig)
    chi2_b = chi_squared(vobs, vtot_b, sig)
    daic = delta_aic(chi2_a, 2, chi2_b, 1)  # positive => B (EFC) preferred

    bb = component_weighted_bias(vb, vtot_b + 1e-10, sig)
    bbulge_arr[g] = bb
    daic_arr[g] = daic

# ------------------------------------------------------------------
# 2. Spearman correlation (paper reports ρ = 0.176, p = 0.020)
# ------------------------------------------------------------------
rho_all, p_all = stats.spearmanr(bbulge_arr, daic_arr)
print("=== Full sample (N=175) ===")
print(f"  Spearman ρ = {rho_all:.3f}  (paper: 0.176)")
print(f"  p-value     = {p_all:.4f}  (paper: 0.020)")

# LATENT (high-L) regime: top quartile by Bbulge among non-zero
nz = bbulge_arr > 0
if np.sum(nz) > 5:
    thresh = np.percentile(bbulge_arr[nz], 75)
    latent = bbulge_arr >= thresh
    if np.sum(latent) > 3:
        rho_lat, p_lat = stats.spearmanr(bbulge_arr[latent], daic_arr[latent])
        print(f"\n=== LATENT regime (N={np.sum(latent)}) ===")
        print(f"  Spearman ρ = {rho_lat:.3f}  (paper: 0.474)")
        print(f"  p-value     = {p_lat:.4f}  (paper: 0.013)")

# ------------------------------------------------------------------
# 3. EFC win-rate by Bbulge bin (paper: 91.9 % vs 44.4 %)
# ------------------------------------------------------------------
low_mask = bbulge_arr < 0.1
high_mask = bbulge_arr > 0.2
efc_wins_low = np.mean(daic_arr[low_mask] >= 0) * 100 if np.sum(low_mask) > 0 else float('nan')
efc_wins_high = np.mean(daic_arr[high_mask] >= 0) * 100 if np.sum(high_mask) > 0 else float('nan')
print(f"\n=== EFC win/tie rate ===")
print(f"  Bbulge < 0.1 : {efc_wins_low:.1f}%  (paper: 91.9%)")
print(f"  Bbulge > 0.2 : {efc_wins_high:.1f}%  (paper: 44.4%)")

# ------------------------------------------------------------------
# 4. RCMP-compliant split ΔAIC for one example galaxy
# ------------------------------------------------------------------
r_ex = np.linspace(0.3, 18.0, N_PTS)
sig_ex = 5.0 * np.ones(N_PTS)
vobs_ex = 150 * np.sqrt(1 - np.exp(-r_ex / 4)) + np.random.normal(0, 3, N_PTS)
va_ex = 150 * np.sqrt(1 - np.exp(-r_ex / 3.5))
vb_ex = 150 * np.sqrt(1 - np.exp(-r_ex / 4.2))
daic_in, daic_out, daic_gl = split_delta_aic(r_ex, vobs_ex, sig_ex, va_ex, 2, vb_ex, 1)
print(f"\n=== RCMP split (example galaxy) ===")
print(f"  ΔAIC_inner  = {daic_in:+.2f}")
print(f"  ΔAIC_outer  = {daic_out:+.2f}")
print(f"  ΔAIC_global = {daic_gl:+.2f}")

# ------------------------------------------------------------------
# 5. Optional plot
# ------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7, 5))
    sc = ax.scatter(bbulge_arr, daic_arr, c=bbulge_arr, cmap="plasma",
                    edgecolors="k", linewidths=0.3, s=30, alpha=0.8)
    ax.axhline(0, color="grey", ls="--", lw=0.8)
    ax.axvline(0.1, color="blue", ls=":", lw=0.8, label="Bbulge = 0.1")
    ax.axvline(0.2, color="red", ls=":", lw=0.8, label="Bbulge = 0.2")
    ax.set_xlabel(r"$B_{\rm bulge}$", fontsize=13)
    ax.set_ylabel(r"$\Delta$AIC  (positive $\Rightarrow$ EFC preferred)", fontsize=13)
    ax.set_title("Component-weighted bias vs ΔAIC (synthetic SPARC-175)")
    ax.legend(fontsize=10)
    plt.colorbar(sc, ax=ax, label=r"$B_{\rm bulge}$")
    plt.tight_layout()
    plt.savefig("bbulge_vs_daic.png", dpi=150)
    print("\nPlot saved to bbulge_vs_daic.png")
except ImportError:
    print("\nmatplotlib not available – skipping plot.")
