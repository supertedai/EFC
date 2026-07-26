"""demo_efc_master.py — Demonstration of the EFC Master Specification module.

Generates:
  1. Expansion rate H(Ef, S) surface plot
  2. Effective light speed c(S) curve
  3. Toy galaxy rotation curve from entropy-driven potential

Requires: numpy, matplotlib (optional for plots).
"""
import numpy as np
from efc_master import (
    effective_potential, expansion_rate, rotation_velocity,
    effective_light_speed, potential_gradient_1d, structural_regime,
    energy_flow_field, c_min,
    C0, A_PHI, BETA, A_EDGE, S0, S1, S_MID,
)

# ------------------------------------------------------------------
# 1.  Expansion-rate surface  H(Ef, S)
# ------------------------------------------------------------------
Ef_lin = np.linspace(0.01, 5.0, 200)
S_lin = np.linspace(S0, S1, 200)
Ef_grid, S_grid = np.meshgrid(Ef_lin, S_lin)
H_grid = expansion_rate(Ef_grid, S_grid)

print('--- Expansion Rate H(Ef, S) ---')
print(f'  H range: [{H_grid.min():.4f}, {H_grid.max():.4f}]')
print(f'  H at Ef=1, S=0.5: {expansion_rate(1.0, 0.5):.6f}')
print()

# ------------------------------------------------------------------
# 2.  Effective light speed c(S)
# ------------------------------------------------------------------
S_arr = np.linspace(S0, S1, 500)
c_arr = effective_light_speed(S_arr)

print('--- Effective Light Speed c(S) ---')
print(f'  c(S0)   = {effective_light_speed(S0):.3f} km/s')
print(f'  c(Smid) = {effective_light_speed(S_MID):.3f} km/s  (minimum = c0)')
print(f'  c(S1)   = {effective_light_speed(S1):.3f} km/s')
print(f'  c_min   = {c_min():.3f} km/s')
print()

# ------------------------------------------------------------------
# 3.  Toy rotation curve
# ------------------------------------------------------------------
r = np.linspace(1.0, 50.0, 500)          # kpc (arbitrary)
Ef_r = 6.0 * np.exp(-r / 12.0)           # declining energy flow
S_r = 0.2 + 0.6 * (1 - np.exp(-r / 20.0))  # rising entropy

dPhi_dr = potential_gradient_1d(Ef_r, S_r, r, A_phi=A_PHI, beta=BETA)
v_rot = rotation_velocity(r, dPhi_dr)

print('--- Toy Rotation Curve ---')
for ri in [5, 10, 20, 30, 40]:
    idx = np.searchsorted(r, ri)
    print(f'  v(r={ri:2d} kpc) = {v_rot[idx]:.4f}  (arb. units)')

regimes = structural_regime(S_r)
focus_frac = np.mean(regimes == 'focusing')
trans_frac = np.mean(regimes == 'transition')
defoc_frac = np.mean(regimes == 'defocusing')
print(f'\n  Regime fractions:  focusing={focus_frac:.2f}  '
      f'transition={trans_frac:.2f}  defocusing={defoc_frac:.2f}')
print()

# ------------------------------------------------------------------
# 4.  (Optional) Plots
# ------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # 4a – H surface
    ax = axes[0]
    cs = ax.contourf(Ef_grid, S_grid, H_grid, levels=30, cmap='viridis')
    fig.colorbar(cs, ax=ax, label='H')
    ax.set_xlabel('Ef');  ax.set_ylabel('S')
    ax.set_title('Expansion Rate  H(Ef, S)')

    # 4b – c(S)
    ax = axes[1]
    ax.plot(S_arr, c_arr, 'b-', lw=2)
    ax.axvline(S_MID, ls='--', color='grey', label='S_mid')
    ax.set_xlabel('S');  ax.set_ylabel('c(S)  [km/s]')
    ax.set_title('Effective Light Speed')
    ax.legend()

    # 4c – Rotation curve
    ax = axes[2]
    ax.plot(r, v_rot, 'r-', lw=2)
    ax.set_xlabel('r  [kpc]');  ax.set_ylabel('v(r)  [arb.]')
    ax.set_title('Toy Rotation Curve (no dark matter)')

    plt.tight_layout()
    plt.savefig('efc_master_demo.png', dpi=150)
    print('Plot saved to efc_master_demo.png')
    plt.show()
except ImportError:
    print('matplotlib not available — skipping plots.')
