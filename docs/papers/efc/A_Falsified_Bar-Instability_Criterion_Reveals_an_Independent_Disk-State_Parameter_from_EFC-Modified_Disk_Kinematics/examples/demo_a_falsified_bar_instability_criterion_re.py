#!/usr/bin/env python3
"""Demo: EFC-modified Toomre parameter for synthetic galaxies.

Reproduces the key calculation of Magnusson 2026
(DOI: 10.6084/m9.figshare.32101111).
"""
import numpy as np
import sys

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

from a_falsified_bar_instability_criterion_re import (
    Pi_EFC, Pi_min_disk_window, alpha_from_latency,
    KPC_M, KMS_MS, MSOL_PC2_TO_SI, ZETA_MAX,
    fit_tanh_Rd, sigma_R_jeans, G_SI
)

# ---- Define three template galaxies (paper §3.1) ----
templates = [
    {'name': 'NGC 6503-like', 'Vflat': 115.0, 'Rd': 2.5, 'Sigma0': 500.0, 'L': 0.30},
    {'name': 'NGC 3198-like', 'Vflat': 150.0, 'Rd': 3.2, 'Sigma0': 350.0, 'L': 0.45},
    {'name': 'NGC 2841-like', 'Vflat': 290.0, 'Rd': 4.0, 'Sigma0': 800.0, 'L': 0.15},
]

print("=" * 65)
print("EFC-Modified Toomre-Q (Pi_EFC) — Synthetic Galaxy Demo")
print("=" * 65)

results = []
for gal in templates:
    r_kpc = np.linspace(0.1, 25.0, 300)
    v_kms = gal['Vflat'] * np.tanh(r_kpc / gal['Rd'])
    Sigma_Mpc2 = gal['Sigma0'] * np.exp(-r_kpc / gal['Rd'])
    alpha = alpha_from_latency(gal['L'])

    # Pi profile in SI
    r_si = r_kpc * KPC_M
    v_si = v_kms * KMS_MS
    Sigma_si = Sigma_Mpc2 * MSOL_PC2_TO_SI
    Rd_si = gal['Rd'] * KPC_M
    sR = sigma_R_jeans(Sigma_si, Rd_si)
    Pi = Pi_EFC(r_si, v_si, Sigma_si, Rd_si, alpha, zeta=1.0)

    pmin = Pi_min_disk_window(r_kpc, v_kms, Sigma_Mpc2, gal['Rd'], alpha, zeta=1.0)
    results.append((gal, r_kpc, Pi, pmin, alpha))

    print(f"\n{gal['name']}:")
    print(f"  Vflat = {gal['Vflat']:.0f} km/s, Rd = {gal['Rd']:.1f} kpc, "
          f"Sigma0 = {gal['Sigma0']:.0f} Msol/pc^2")
    print(f"  alpha = {alpha:.2f} (L = {gal['L']:.2f})")
    print(f"  Pi_min (disk window [Rd,3Rd]) = {pmin:.3f}")

print("\n" + "-" * 65)
print(f"zeta_max (kappa_eff^2 >= 0 constraint) = {ZETA_MAX:.2f}")

# ---- Zeta scan for first galaxy ----
print("\nZeta scan for", templates[0]['name'])
zetas = np.linspace(0.0, ZETA_MAX, 8)
for z in zetas:
    pm = Pi_min_disk_window(
        results[0][1],  # r_kpc
        templates[0]['Vflat'] * np.tanh(results[0][1] / templates[0]['Rd']),
        templates[0]['Sigma0'] * np.exp(-results[0][1] / templates[0]['Rd']),
        templates[0]['Rd'], results[0][4], zeta=z)
    print(f"  zeta = {z:.2f}  ->  Pi_min = {pm:.3f}")

# ---- Paper key statistics (reproduced from text) ----
print("\n" + "=" * 65)
print("Key reported statistics from the paper:")
print("  AUC (v0.1 local)   = 0.22  (bar prediction — falsified)")
print("  AUC (v0.2 global)  = 0.31  (bar prediction — falsified)")
print("  rho(Pi_min, log Sigma_disk) = -0.71  (SPARC N=112)")
print("  rho(Pi_min, fgas)           = +0.65  (SPARC N=112)")
print("  rho(Pi_proxy, log Sigma*)   = -0.49  (xGASS N=98)")
print("  rho(Pi_proxy, fgas)         = +0.67  (xGASS N=98)")
print("  rho(Pi_min, MHI/(MHI+M*))  = +0.53  (independent fgas)")

# ---- Optional plot ----
if HAS_MPL:
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    for ax, (gal, r, Pi, pmin, alpha) in zip(axes, results):
        mask = np.isfinite(Pi) & (Pi > 0) & (Pi < 50)
        ax.plot(r[mask], Pi[mask], 'b-', lw=1.5)
        ax.axhline(1.0, color='red', ls='--', lw=1, label='Pi=1')
        ax.axvspan(gal['Rd'], 3 * gal['Rd'], alpha=0.15, color='green',
                   label=f'disk window')
        ax.set_title(f"{gal['name']}\nPi_min={pmin:.2f}", fontsize=10)
        ax.set_xlabel('R  [kpc]')
        ax.legend(fontsize=8)
    axes[0].set_ylabel(r'$\Pi_{\rm EFC}$')
    fig.suptitle('EFC-Modified Toomre Parameter (zeta=1.0)', fontsize=12)
    plt.tight_layout()
    plt.savefig('demo_Pi_EFC_profiles.png', dpi=150)
    print("\nPlot saved to demo_Pi_EFC_profiles.png")
else:
    print("\n(matplotlib not available — skipping plot)")

print("\nDone.")
