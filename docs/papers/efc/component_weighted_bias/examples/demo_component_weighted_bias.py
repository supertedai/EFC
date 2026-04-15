#!/usr/bin/env python
"""demo_component_weighted_bias.py

Demonstrates the component-weighted bias metric from Magnusson (2026)
on a synthetic bulge-dominated galaxy and a disk-dominated galaxy,
reproducing the key qualitative result: bulge-dominated galaxies inflate
ΔAIC in favour of parametrically flexible inner-region models.
"""

import numpy as np
import component_weighted_bias as cwb

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

np.random.seed(2026)


def make_galaxy(N: int, r_max: float, V_bulge_scale: float, label: str):
    """Generate a synthetic SPARC-like galaxy."""
    r = np.linspace(0.5, r_max, N)
    sigma = np.where(r < 3.0, 3.0, 8.0)
    V_gas = 20.0 * np.sqrt(r / r_max)
    V_disk = 90.0 * np.exp(-r / 6.0)
    V_bulge = V_bulge_scale * np.exp(-r / 1.2)
    V_dm = 160.0 * np.sqrt(1.0 - np.exp(-r / 5.0))
    V_tot = cwb.V_total(V_gas, V_disk, V_bulge, V_dm)
    V_obs = V_tot + np.random.normal(0, sigma)
    return r, V_obs, sigma, V_gas, V_disk, V_bulge, V_dm, V_tot


print("=" * 65)
print("  Component-Weighted Bias Demo  (Magnusson 2026)")
print("=" * 65)

results = []
for label, bulge_scale in [("Disk-dominated (Sd)", 10.0),
                            ("Bulge-dominated (Sa)", 180.0)]:
    r, V_obs, sig, Vg, Vd, Vb, Vdm, Vtot = make_galaxy(50, 25.0, bulge_scale, label)

    B = cwb.inner_weight_fraction(r, sig)
    Bb = cwb.B_bulge(Vb, Vtot, sig)

    # Model A: "correct" model (ground truth)
    V_pred_A = Vtot.copy()
    # Model B: slightly worse outer, slightly better inner (extra freedom)
    V_pred_B = Vtot.copy()
    V_pred_B[r < 3.0] -= 1.5        # tiny inner improvement
    V_pred_B[r >= 5.0] *= 0.93      # worse outer

    di, do, dg = cwb.split_delta_aic(r, V_obs, sig, V_pred_A, V_pred_B,
                                      k_A=2, k_B=3)
    biased = cwb.is_model_selection_biased(Bb, do, dg)

    print(f"\n--- {label} ---")
    print(f"  B (inner-weight fraction)   = {B:.4f}")
    print(f"  Bbulge                      = {Bb:.4f}")
    print(f"  ΔAICinner                   = {di:+.2f}")
    print(f"  ΔAICouter                   = {do:+.2f}")
    print(f"  ΔAICglobal                  = {dg:+.2f}")
    print(f"  Model-selection biased?       {biased}")
    results.append((label, r, V_obs, sig, Vb, Vtot, Bb, di, do, dg))

print("\n" + "=" * 65)
print("Key paper thresholds:")
print(f"  Bbulge bias threshold          = {cwb.BBULGE_BIAS_THRESHOLD}")
print(f"  EFC screening parameter k      = {cwb.EFC_K}")
print(f"  Spearman ρ (all, Bbulge–ΔAIC)  = {cwb.SPEARMAN_RHO_ALL}  (p={cwb.SPEARMAN_P_ALL})")
print(f"  Spearman ρ (LATENT regime)     = {cwb.SPEARMAN_RHO_LATENT}  (p={cwb.SPEARMAN_P_LATENT})")
print(f"  EFC win rate Bbulge<0.1        = {cwb.EFC_WIN_LOW_BBULGE*100:.1f}%")
print(f"  EFC win rate Bbulge>0.2        = {cwb.EFC_WIN_HIGH_BBULGE*100:.1f}%")
print("=" * 65)

if HAS_MPL:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    for idx, (label, r, V_obs, sig, Vb, Vtot, Bb, di, do, dg) in enumerate(results):
        ax = axes[idx]
        ax.errorbar(r, V_obs, yerr=sig, fmt='o', ms=3, alpha=0.5, label='V_obs')
        ax.plot(r, Vtot, 'k-', lw=2, label='V_total')
        ax.plot(r, Vb, 'r--', lw=1.5, label='V_bulge')
        ax.axvline(cwb.RC_DEFAULT_KPC, color='grey', ls=':', label=f'r_c={cwb.RC_DEFAULT_KPC} kpc')
        ax.set_title(f"{label}\nBbulge={Bb:.3f}  ΔAICglobal={dg:+.1f}")
        ax.set_xlabel('r  [kpc]')
        ax.set_ylabel('V  [km/s]')
        ax.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig('component_weighted_bias_demo.png', dpi=150)
    print("\nPlot saved to component_weighted_bias_demo.png")
    plt.show()
