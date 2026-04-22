"""demo_efc_rcmp_test_specification.py

Demonstrates the EFC (μ, Σ) parametrization from the EFC-ΛCDM
Comparative Test Specification v1.1 (Magnusson 2026).

Runs the key calculations, prints results, and optionally saves a plot.
"""
import numpy as np

from efc_rcmp_test_specification import (
    gate_function, scale_filter, mu, sigma,
    sigma_variant_h, S8, pixel_level_check_null,
    pixel_level_check_gate_off, A_T, DELTA_A, K_C
)

# ── 1. Grid setup ──────────────────────────────────────────────────────────
k_grid = np.logspace(-3, 0.5, 300)      # h/Mpc
a_grid = np.linspace(0.3, 1.0, 300)
K, A = np.meshgrid(k_grid, a_grid)

# ── 2. Pixel-level checks ─────────────────────────────────────────────────
print('=== Pixel-Level Verification (§1.3) ===')
print(f'  Null check (Aμ=AΣ=0):   {"PASS" if pixel_level_check_null(K, A) else "FAIL"}')
print(f'  Gate-off check (a_t>>1): {"PASS" if pixel_level_check_gate_off(K, A) else "FAIL"}')

# ── 3. Evaluate μ and Σ for representative EFC amplitudes ─────────────────
A_MU_FIDUCIAL = -0.10   # within prior [-0.20, 0.05]
A_SIGMA_FIDUCIAL = 0.10  # within prior [-0.05, 0.20]

mu_map = mu(K, A, A_mu=A_MU_FIDUCIAL)
sig_map = sigma(K, A, A_sigma=A_SIGMA_FIDUCIAL)
sig_h_map = sigma_variant_h(K, A, A_mu=A_MU_FIDUCIAL)

print('\n=== Representative EFC field values ===')
print(f'  Aμ  = {A_MU_FIDUCIAL},  AΣ = {A_SIGMA_FIDUCIAL}')
print(f'  μ  range on grid : [{mu_map.min():.6f}, {mu_map.max():.6f}]')
print(f'  Σ  range on grid : [{sig_map.min():.6f}, {sig_map.max():.6f}]')
print(f'  Σ_H range on grid: [{sig_h_map.min():.6f}, {sig_h_map.max():.6f}]')

# ── 4. S8 derived parameter demo ──────────────────────────────────────────
print('\n=== S8 Derived Parameter ===')
for s8_val, om_val in [(0.81, 0.30), (0.78, 0.32), (0.84, 0.28)]:
    print(f'  S8(σ8={s8_val}, Ωm={om_val}) = {S8(s8_val, om_val):.4f}')

# ── 5. Gate and filter 1-D profiles ───────────────────────────────────────
a_1d = np.linspace(0.0, 1.0, 500)
k_1d = np.logspace(-3, 1, 500)
g_profile = gate_function(a_1d)
f_profile = scale_filter(k_1d)

print('\n=== Gate function g(a) spot checks ===')
for av in [0.5, 0.62, 0.7, 0.78, 0.9]:
    print(f'  g(a={av}) = {gate_function(np.array([av]))[0]:.6f}')

print('\n=== Scale filter f_k(k) spot checks ===')
for kv in [0.001, 0.01, 0.05, 0.1, 1.0]:
    print(f'  f_k(k={kv} h/Mpc) = {scale_filter(np.array([kv]))[0]:.6f}')

# ── 6. Optional plot ──────────────────────────────────────────────────────
try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    fig.suptitle('EFC-ΛCDM Test Specification v1.1 — Phenomenological Functions',
                 fontsize=13, fontweight='bold')

    # (a) gate
    axes[0, 0].plot(a_1d, g_profile, 'k-', lw=2)
    axes[0, 0].axvline(A_T, ls='--', color='grey', label=f'$a_t={A_T}$')
    axes[0, 0].set(xlabel='Scale factor $a$', ylabel='$g(a)$', title='Gate function (Eq. 1)')
    axes[0, 0].legend()

    # (b) filter
    axes[0, 1].semilogx(k_1d, f_profile, 'k-', lw=2)
    axes[0, 1].axvline(K_C, ls='--', color='grey', label=f'$k_c={K_C}$ h/Mpc')
    axes[0, 1].set(xlabel='$k$  [h/Mpc]', ylabel='$f_k(k)$', title='Scale filter (Eq. 2)')
    axes[0, 1].legend()

    # (c) μ map
    z_grid = 1.0 / a_grid - 1.0
    im = axes[1, 0].pcolormesh(k_grid, z_grid, mu_map, shading='auto', cmap='RdBu_r')
    axes[1, 0].set(xscale='log', xlabel='$k$ [h/Mpc]', ylabel='Redshift $z$',
                   title=f'$\\mu(k,a)$  ($A_\\mu={A_MU_FIDUCIAL}$)')
    fig.colorbar(im, ax=axes[1, 0])

    # (d) Σ map
    im2 = axes[1, 1].pcolormesh(k_grid, z_grid, sig_map, shading='auto', cmap='RdBu_r')
    axes[1, 1].set(xscale='log', xlabel='$k$ [h/Mpc]', ylabel='Redshift $z$',
                   title=f'$\\Sigma(k,a)$  ($A_\\Sigma={A_SIGMA_FIDUCIAL}$)')
    fig.colorbar(im2, ax=axes[1, 1])

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    plt.savefig('efc_rcmp_demo.png', dpi=150)
    print('\n[Plot saved to efc_rcmp_demo.png]')
except ImportError:
    print('\n[matplotlib not available — skipping plot]')
