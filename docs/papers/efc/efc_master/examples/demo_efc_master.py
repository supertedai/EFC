"""demo_efc_master.py — Demonstration of the EFC Master Specification module.

Produces:
  1. Rotation curve v(r) from a toy Ef / S radial profile.
  2. Expansion rate H as function of entropy S.
  3. Effective light-speed profile c(S).
  4. Console summary of key derived quantities.

Requires: numpy, matplotlib (optional for plots).
"""

import numpy as np
from efc_master import (
    effective_potential, expansion_rate, effective_light_speed,
    rotation_velocity, dPhi_dr_numerical, entropy_regime,
    stability_band_cmin, c0, S0, S1, S_MID, A_PHI, BETA,
)

# ---------------------------------------------------------------------------
# 1. Radial profiles (toy galaxy-scale model)
# ---------------------------------------------------------------------------
r = np.linspace(1.0, 60.0, 500)          # kpc-like radial coordinate
Ef_r = 12.0 / (1.0 + 0.1 * r)           # decaying energy flow
S_r = 0.2 + 0.012 * r                    # gently rising entropy

Phi_r = effective_potential(Ef_r, S_r, A_PHI, BETA)
dPhi = dPhi_dr_numerical(r, Ef_r, S_r)
v_r = rotation_velocity(r, dPhi)

print('=== EFC-D: Rotation Curve ===')
for ri in [5, 15, 30, 50]:
    vi = np.interp(ri, r, v_r)
    print(f'  v(r={ri:3d}) = {vi:.3f}  [model units]')

# ---------------------------------------------------------------------------
# 2. Expansion rate vs entropy
# ---------------------------------------------------------------------------
S_arr = np.linspace(S0, S1, 300)
Ef_const = 4.0                            # fixed Ef for illustration
H_arr = expansion_rate(Ef_const, S_arr)

print('\n=== EFC-D: Expansion Rate ===')
for s_val in [0.0, 0.25, 0.5, 0.75, 1.0]:
    h_val = expansion_rate(Ef_const, s_val)
    print(f'  H(Ef={Ef_const}, S={s_val:.2f}) = {h_val:.4f}')

# ---------------------------------------------------------------------------
# 3. Effective light speed
# ---------------------------------------------------------------------------
c_arr = effective_light_speed(S_arr)
c_min = stability_band_cmin()

print('\n=== EFC-S: Light Speed ===')
print(f'  c(S0)   = {effective_light_speed(S0):.6e} m/s')
print(f'  c(Smid) = {c_min:.6e} m/s  (stability-band minimum)')
print(f'  c(S1)   = {effective_light_speed(S1):.6e} m/s')

# ---------------------------------------------------------------------------
# 4. Entropy regimes
# ---------------------------------------------------------------------------
print('\n=== EFC-S: Entropy Regimes ===')
test_S = np.array([0.05, 0.33, 0.5, 0.67, 0.95])
for s, lab in zip(test_S, entropy_regime(test_S)):
    print(f'  S = {s:.2f}  →  regime: {lab}')

# ---------------------------------------------------------------------------
# Optional plot
# ---------------------------------------------------------------------------
try:
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5))

    # (a) Rotation curve
    axes[0].plot(r, v_r, 'b-', lw=1.5)
    axes[0].set_xlabel('r  [model units]')
    axes[0].set_ylabel('v(r)')
    axes[0].set_title('EFC Rotation Curve')
    axes[0].grid(True, alpha=0.3)

    # (b) Expansion rate
    axes[1].plot(S_arr, H_arr, 'r-', lw=1.5)
    axes[1].set_xlabel('Entropy S')
    axes[1].set_ylabel('H(Ef, S)')
    axes[1].set_title(f'Expansion Rate  (Ef={Ef_const})')
    axes[1].grid(True, alpha=0.3)

    # (c) Light speed
    axes[2].plot(S_arr, c_arr / c0, 'g-', lw=1.5)
    axes[2].axvline(S_MID, ls='--', color='grey', label='S_mid')
    axes[2].set_xlabel('Entropy S')
    axes[2].set_ylabel('c(S) / c₀')
    axes[2].set_title('Effective Light Speed')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('efc_master_demo.png', dpi=150)
    print('\nPlot saved to efc_master_demo.png')
    plt.show()
except ImportError:
    print('\nmatplotlib not available — skipping plot.')
