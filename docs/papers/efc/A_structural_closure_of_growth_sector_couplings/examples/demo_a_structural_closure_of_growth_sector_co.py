"""Demo: structural closure of growth-sector couplings.

Runs the three coupling classes (A, B, C) from Magnusson (2026) and
compares f*sigma8(z) predictions against LCDM.
"""

import numpy as np
from a_structural_closure_of_growth_sector_co import (
    solve_growth, fsigma8, EG_statistic, Geff_over_G,
    accumulated_gate, logistic_gate,
    C_EFC, OMEGA_M_FID, SIGMA8_FID
)

try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

# ---------------------------------------------------------------
# 1. Solve growth for LCDM and three coupling classes
# ---------------------------------------------------------------
z_targets = np.array([0.15, 0.38, 0.51, 0.70, 0.85, 1.0, 1.5, 2.0])

results = {}
for label, coupling, beta in [
    ('LCDM',    'LCDM', 0.0),
    ('Class A', 'A',     0.0),
    ('Class B', 'B',     1.0),
    ('Class C', 'C',     1.0),
]:
    a, D, f = solve_growth(coupling=coupling, beta=beta)
    fs8 = fsigma8(a, D, f)
    z_arr = 1.0 / a - 1.0
    results[label] = (a, z_arr, D, f, fs8)
    print(f'\n--- {label} (beta={beta}) ---')
    for zt in z_targets:
        idx = np.argmin(np.abs(z_arr - zt))
        print(f'  z={zt:.2f}  f*sigma8={fs8[idx]:.4f}  f={f[idx]:.4f}')

# ---------------------------------------------------------------
# 2. E_G statistic comparison
# ---------------------------------------------------------------
print('\n--- E_G statistic (Sigma=1) ---')
for label in results:
    a_arr, z_arr, D, f, fs8 = results[label]
    for zt in [0.27, 0.57, 0.70]:
        f_z = np.interp(1.0 / (1.0 + zt), a_arr, f)
        eg = EG_statistic(zt, f_z)
        print(f'  {label:10s}  z={zt:.2f}  E_G={eg:.4f}')

# ---------------------------------------------------------------
# 3. Gate function values (Table from paper)
# ---------------------------------------------------------------
print('\n--- Gate function check ---')
for a_val in [0.1, 0.5, 1.0]:
    g = logistic_gate(a_val)
    G = accumulated_gate(a_val)
    ratio = g / G if G > 1e-10 else float('inf')
    print(f'  a={a_val:.1f}  g={g:.4f}  G={G:.4f}  g/G={ratio:.1f}')

# ---------------------------------------------------------------
# 4. Geff/G scan
# ---------------------------------------------------------------
print(f'\n--- Geff/G at k=0.01 h/Mpc, C={C_EFC} ---')
for a_val in [0.3, 0.5, 0.7, 1.0]:
    ratio = Geff_over_G(a_val, k=0.01)
    print(f'  a={a_val:.1f}  Geff/G = {ratio:.4f}')

# ---------------------------------------------------------------
# 5. Plot (optional)
# ---------------------------------------------------------------
if HAS_MPL:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Panel 1: f*sigma8
    ax = axes[0]
    for label, style in [('LCDM', 'k-'), ('Class A', 'r--'),
                          ('Class B', 'b-.'), ('Class C', 'g:')]:
        a_arr, z_arr, D, f, fs8 = results[label]
        mask = (z_arr > 0) & (z_arr < 2.5)
        ax.plot(z_arr[mask], fs8[mask], style, lw=2, label=label)
    ax.set_xlabel('z')
    ax.set_ylabel(r'$f\sigma_8(z)$')
    ax.set_title('Growth-rate observable')
    ax.legend()
    ax.invert_xaxis()
    ax.set_xlim(2.0, 0.0)

    # Panel 2: Geff/G vs a for several k
    ax = axes[1]
    a_plot = np.linspace(0.1, 1.0, 200)
    for k_val, ls in [(0.01, '-'), (0.05, '--'), (0.2, ':')]:
        geff = [Geff_over_G(a, k_val) for a in a_plot]
        ax.plot(a_plot, geff, ls, lw=2, label=f'k={k_val} h/Mpc')
    ax.set_xlabel('a')
    ax.set_ylabel(r'$G_{\rm eff}/G$')
    ax.set_title(f'Class A: Geff/G  (C={C_EFC})')
    ax.legend()
    ax.axhline(1.0, color='grey', lw=0.5)

    plt.tight_layout()
    plt.savefig('growth_sector_couplings.png', dpi=150)
    print('\nPlot saved to growth_sector_couplings.png')
    plt.show()
else:
    print('\nMatplotlib not available — skipping plot.')

print('\nDone.')
