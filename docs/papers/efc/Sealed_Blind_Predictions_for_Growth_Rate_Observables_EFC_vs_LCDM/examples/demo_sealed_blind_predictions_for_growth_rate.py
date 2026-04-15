#!/usr/bin/env python3
"""demo_sealed_blind_predictions_for_growth_rate.py

Demonstrate the EFC vs LCDM growth-rate predictions from
DOI: 10.6084/m9.figshare.32013156
"""
import numpy as np
from sealed_blind_predictions_for_growth_rate import (
    solve_growth, fsigma8, DH_over_rd,
    ALPHA_PRIMARY, ALPHA_SECONDARY, SIGMA8_0, OMEGA_M0,
    PREDICTIONS,
)

# ---- Observational baseline (Table 4) ------------------------------------
obs_z = np.array([0.067, 0.320, 0.510, 0.510, 0.610, 0.700,
                  0.706, 0.850, 0.930, 1.317, 1.480, 1.491])
obs_fs8 = np.array([0.423, 0.427, 0.458, 0.449, 0.436, 0.473,
                    0.413, 0.315, 0.381, 0.396, 0.462, 0.318])
obs_err = np.array([0.055, 0.056, 0.038, 0.032, 0.034, 0.041,
                    0.029, 0.095, 0.034, 0.062, 0.045, 0.076])

# ---- Compute theory curves -----------------------------------------------
z_grid = np.linspace(0.01, 2.5, 300)
fs8_lcdm = np.array([fsigma8(z, alpha=0.0) for z in z_grid])
fs8_efc1 = np.array([fsigma8(z, alpha=ALPHA_PRIMARY) for z in z_grid])
fs8_efc2 = np.array([fsigma8(z, alpha=ALPHA_SECONDARY) for z in z_grid])

# ---- Print key sealed predictions ----------------------------------------
print("=" * 60)
print("Sealed Blind Predictions — EFC vs LCDM")
print("=" * 60)
for key, vals in PREDICTIONS.items():
    print(f"  {key:18s}  EFC={vals['efc']:.3f}  LCDM={vals['lcdm']:.3f}"
          f"  ({vals['separation_sigma']:.1f}σ)")

print("\nComputed f*sigma8 at key redshifts:")
for z_test in [0.7, 1.0, 2.042]:
    v_lcdm = fsigma8(z_test, alpha=0.0)
    v_efc = fsigma8(z_test, alpha=ALPHA_PRIMARY)
    print(f"  z={z_test:.3f}  LCDM={v_lcdm:.4f}  EFC(alpha={ALPHA_PRIMARY})={v_efc:.4f}")

print(f"\nDH/rd(z=0.7) LCDM = {DH_over_rd(0.7):.3f}")
print(f"DH/rd(z=1.0) LCDM = {DH_over_rd(1.0):.3f}")

# ---- Optional plot --------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.errorbar(obs_z, obs_fs8, yerr=obs_err, fmt='ko', ms=4, capsize=2,
                label='Observed (Table 4)', zorder=5)
    ax.plot(z_grid, fs8_lcdm, 'b-', lw=2, label=r'$\Lambda$CDM ($\alpha=0$)')
    ax.plot(z_grid, fs8_efc1, 'r--', lw=2,
            label=f'EFC primary ($\\alpha={ALPHA_PRIMARY}$)')
    ax.plot(z_grid, fs8_efc2, 'r:', lw=1.5,
            label=f'EFC secondary ($\\alpha={ALPHA_SECONDARY}$)')
    # Mark sealed predictions
    ax.axvline(0.7, color='grey', ls=':', alpha=0.5)
    ax.plot(0.7, 0.430, 'r*', ms=14, zorder=10, label='EFC prediction z=0.7')
    ax.plot(0.7, 0.449, 'b*', ms=14, zorder=10, label=r'$\Lambda$CDM z=0.7')
    ax.set_xlabel('Redshift $z$', fontsize=13)
    ax.set_ylabel(r'$f\sigma_8(z)$', fontsize=13)
    ax.set_title('EFC vs $\\Lambda$CDM: Sealed Growth-Rate Predictions',
                 fontsize=13)
    ax.legend(fontsize=9, loc='upper right')
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0.2, 0.6)
    fig.tight_layout()
    fig.savefig('efc_growth_rate_predictions.png', dpi=150)
    print("\nPlot saved to efc_growth_rate_predictions.png")
except ImportError:
    print("\nMatplotlib not available — skipping plot.")
