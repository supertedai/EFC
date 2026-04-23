#!/usr/bin/env python
"""Demo: structural closure of growth-sector couplings.

Compares f*sigma8(z) predictions for LCDM and the three EFC coupling
classes (A, B, C) described in Magnusson (2026).
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # non-interactive backend
import matplotlib.pyplot as plt

from a_structural_closure_of_growth_sector_co import (
    fsigma8, EG_statistic, solve_growth, memory_kernel,
    C_GRID_AQUAL, OMEGA_M0, SIGMA8_FIDU
)

# ── 1.  f*sigma8 comparison ──────────────────────────────────────────────────
z_grid = np.linspace(0.0, 2.0, 200)

z_lcdm, fs8_lcdm = fsigma8(z_out=z_grid)
z_A, fs8_A       = fsigma8(coupling_class='A', z_out=z_grid)
z_B, fs8_B       = fsigma8(coupling_class='B', beta=0.5, z_out=z_grid)
z_C, fs8_C       = fsigma8(coupling_class='C', beta=0.5, z_out=z_grid)

print('=== f*sigma8 at selected redshifts ===')
for zv in [0.2, 0.5, 1.0, 1.5]:
    idx = np.argmin(np.abs(z_grid - zv))
    print(f'  z={zv:.1f}  LCDM={fs8_lcdm[idx]:.4f}  '
          f'A={fs8_A[idx]:.4f}  B={fs8_B[idx]:.4f}  C={fs8_C[idx]:.4f}')

# ── 2.  Memory kernel check (paper values) ───────────────────────────────────
print('\n=== Memory kernel G(a) ===')
for a_val, expected in [(1.0, 0.50), (0.5, 0.069), (0.1, 0.002)]:
    G = memory_kernel(a_val)
    print(f'  G({a_val}) = {G:.4f}  (paper ≈ {expected})')

# ── 3.  EG statistic at z = 0.3 ─────────────────────────────────────────────
a_arr, D, f_arr = solve_growth()
f_at_z03 = np.interp(1.0 / 1.3, a_arr, f_arr)
eg_val = EG_statistic(z=0.3, f=f_at_z03)
print(f'\nEG(z=0.3, Sigma=1, LCDM) = {eg_val:.4f}')
print(f'  (= Omega_m0 / f  since Sigma=1 carries no independent info)')

# ── 4.  Beta scan for Class B ────────────────────────────────────────────────
print('\n=== Class B beta scan: f*sigma8(z=0.5) ===')
for beta in [0.0, 0.2, 0.5, 1.0, 2.0]:
    _, fs8_b = fsigma8(coupling_class='B', beta=beta, z_out=np.array([0.5]))
    print(f'  beta={beta:.1f}  f*sigma8 = {fs8_b[0]:.4f}')

# ── 5.  Plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(z_lcdm, fs8_lcdm, 'k-',  lw=2,   label=r'$\Lambda$CDM')
ax.plot(z_A,    fs8_A,     'r--', lw=1.5, label=f'Class A  (C={C_GRID_AQUAL})')
ax.plot(z_B,    fs8_B,     'b-.', lw=1.5, label=r'Class B  ($\beta=0.5$)')
ax.plot(z_C,    fs8_C,     'g:',  lw=2,   label=r'Class C  ($\beta=0.5$)')
ax.set_xlabel('Redshift $z$')
ax.set_ylabel(r'$f\sigma_8(z)$')
ax.set_title('Growth-sector coupling classes (Magnusson 2026)')
ax.legend(fontsize=9)
ax.set_xlim(0, 2)
ax.set_ylim(0, 0.65)
plt.tight_layout()
plt.savefig('growth_sector_couplings.png', dpi=150)
print('\nPlot saved to growth_sector_couplings.png')
