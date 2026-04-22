#!/usr/bin/env python
"""demo_efc_rcmp_test_specification.py

Demonstrates the EFC (μ, Σ) phenomenological parametrization from
Magnusson 2026 (DOI: 10.6084/m9.figshare.32080083).

Produces:
  • Console printout of gate, filter, μ, Σ on a grid
  • A 4-panel figure (saved as efc_demo.png)
"""

import numpy as np
import efc_rcmp_test_specification as efc

# ── grids ──────────────────────────────────────────────────────────────────
a_grid = np.linspace(0.2, 1.0, 300)
k_grid = np.logspace(-3, 1, 400)          # 0.001 … 10 h/Mpc

# ── 1-D curves ─────────────────────────────────────────────────────────────
g_vals = efc.gate_function(a_grid)
fk_vals = efc.scale_filter(k_grid)

# ── 2-D maps at fiducial EFC amplitudes ────────────────────────────────────
A_mu_fid = -0.10
A_Sigma_fid = 0.10
mu_map = efc.mu_efc(k_grid, a_grid, A_mu=A_mu_fid)
sig_map = efc.sigma_efc(k_grid, a_grid, A_Sigma=A_Sigma_fid)
sig_varH = efc.sigma_variant_h(k_grid, a_grid, A_mu=A_mu_fid)

# ── pixel-level check ─────────────────────────────────────────────────────
print("=" * 60)
print("EFC-ΛCDM Comparative Test – Reference Demo")
print("=" * 60)
check = efc.pixel_level_check()
print(f"Pixel-level check (§1.3): {'PASS' if check else 'FAIL'}")
print()

# ── print selected values ──────────────────────────────────────────────────
for a_val in [0.5, 0.7, 0.9, 1.0]:
    z = 1.0 / a_val - 1.0
    g = efc.gate_function(np.array([a_val]))[0]
    print(f"  a={a_val:.2f}  z={z:.3f}  g(a)={g:.6f}")
print()
for k_val in [0.01, 0.05, 0.1, 1.0]:
    f = efc.scale_filter(np.array([k_val]))[0]
    print(f"  k={k_val:.3f} h/Mpc  f_k={f:.6f}")
print()
print(f"S8(sigma8=0.81, Omega_m=0.31) = {efc.S8(0.81, 0.31):.5f}")

# ── plotting (optional) ───────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))

    # Panel (a): gate function
    ax = axes[0, 0]
    ax.plot(a_grid, g_vals, 'k', lw=2)
    ax.axvline(efc.AT, ls='--', color='grey', label=f'$a_t={efc.AT}$')
    ax.set_xlabel('Scale factor $a$')
    ax.set_ylabel('$g(a)$')
    ax.set_title('Eq. 1 – Gate function')
    ax.legend()

    # Panel (b): scale filter
    ax = axes[0, 1]
    ax.semilogx(k_grid, fk_vals, 'k', lw=2)
    ax.axvline(efc.KC, ls='--', color='grey', label=f'$k_c={efc.KC}$ h/Mpc')
    ax.set_xlabel('$k$ [h/Mpc]')
    ax.set_ylabel('$f_k(k)$')
    ax.set_title('Eq. 2 – Scale filter')
    ax.legend()

    # Panel (c): μ(k, a=1)
    ax = axes[1, 0]
    for Am, ls in [(-0.20, '-'), (-0.10, '--'), (0.0, ':')]:
        mu_line = efc.mu_efc(k_grid, np.array([1.0]), A_mu=Am).ravel()
        ax.semilogx(k_grid, mu_line, ls=ls, lw=1.8, label=f'$A_\\mu={Am}$')
    ax.set_xlabel('$k$ [h/Mpc]')
    ax.set_ylabel('$\\mu(k, a{=}1)$')
    ax.set_title('Eq. 3 – $\\mu$ today')
    ax.legend(fontsize=8)

    # Panel (d): Σ(k, a=1)
    ax = axes[1, 1]
    for As, ls in [(0.20, '-'), (0.10, '--'), (0.0, ':')]:
        sig_line = efc.sigma_efc(k_grid, np.array([1.0]), A_Sigma=As).ravel()
        ax.semilogx(k_grid, sig_line, ls=ls, lw=1.8, label=f'$A_\\Sigma={As}$')
    # VariantH overlay
    varH_line = efc.sigma_variant_h(k_grid, np.array([1.0]), A_mu=-0.10).ravel()
    ax.semilogx(k_grid, varH_line, 'r-.', lw=1.4, label='VariantH ($A_\\mu{=}-0.10$)')
    ax.set_xlabel('$k$ [h/Mpc]')
    ax.set_ylabel('$\\Sigma(k, a{=}1)$')
    ax.set_title('Eq. 4 – $\\Sigma$ today')
    ax.legend(fontsize=8)

    fig.suptitle('EFC-ΛCDM Test Specification v1.1 — Magnusson 2026', fontsize=13)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig('efc_demo.png', dpi=150)
    print("\nFigure saved to efc_demo.png")

except ImportError:
    print("\nmatplotlib not available – skipping plot.")
