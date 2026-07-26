"""demo_efc_master_v1.py — Demonstration of EFC Master Specification v1.1

Generates the seven schematic figures described in Sec. 3 of the paper:
  Fig 1: Ef(rho, S) heatmap
  Fig 2: Halo density profile
  Fig 3: Halo entropy profile
  Fig 4: Rotation curves (EFC vs NFW)
  Fig 5: Projected surface density
  Fig 6: Expansion history H(z)/H0
  Fig 7: Information capacity I(S)

Requires: numpy, matplotlib, efc_master_v1
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')  # headless-safe
import matplotlib.pyplot as plt

from efc_master_v1 import (
    energy_flow_potential, halo_density, halo_entropy,
    rotation_curve, nfw_rotation_curve, projected_surface_density,
    expansion_rate_efc, expansion_rate_lcdm, information_capacity,
    H0_DEFAULT, S_CORE, S_EDGE, KAPPA_I
)

# ---- Grid definitions ----
r = np.linspace(0.5, 120.0, 200)
z = np.linspace(0.0, 3.0, 200)
rho_grid = np.linspace(1e2, 2e6, 300)
S_grid = np.linspace(0.0, 1.0, 300)
RHO, SS = np.meshgrid(rho_grid, S_grid)

# ---- Compute fields ----
Ef_map = energy_flow_potential(RHO, SS)
rho_h = halo_density(r)
S_h = halo_entropy(r)
v_efc = rotation_curve(r)
v_nfw = nfw_rotation_curve(r)
R_proj = np.linspace(0.5, 100.0, 150)
Sigma = projected_surface_density(R_proj)
H_efc = expansion_rate_efc(z) / H0_DEFAULT
H_lcdm = expansion_rate_lcdm(z) / H0_DEFAULT
S_line = np.linspace(0.0, 1.0, 200)
I_line = KAPPA_I * (1.0 - S_line)

# ---- Print summary ----
print('=== EFC Master v1.1 — Demo ===')
print(f'Peak Ef           : {Ef_map.max():.3e}')
print(f'v_efc  max        : {v_efc.max():.1f} km/s')
print(f'v_nfw  max        : {v_nfw.max():.1f} km/s')
print(f'H_efc(z=0)/H0     : {expansion_rate_efc(np.array([0.0]))[0]/H0_DEFAULT:.4f}')
print(f'H_lcdm(z=0)/H0    : {expansion_rate_lcdm(np.array([0.0]))[0]/H0_DEFAULT:.4f}')

# ---- Plotting ----
fig, axes = plt.subplots(3, 3, figsize=(15, 13))
fig.suptitle('EFC Master Specification v1.1 — Schematic Figures', fontsize=14)

# Fig 1 — Ef heatmap
ax = axes[0, 0]
cf = ax.contourf(rho_grid, S_grid, Ef_map, levels=40, cmap='inferno')
fig.colorbar(cf, ax=ax, label='$E_f$')
ax.set_xlabel(r'$\rho$'); ax.set_ylabel('S'); ax.set_title('Fig 1: $E_f(\\rho, S)$')

# Fig 2 — halo density
ax = axes[0, 1]
ax.semilogy(r, rho_h); ax.set_xlabel('r [kpc]'); ax.set_ylabel(r'$\rho_h$')
ax.set_title('Fig 2: Halo density')

# Fig 3 — halo entropy
ax = axes[0, 2]
ax.plot(r, S_h); ax.set_xlabel('r [kpc]'); ax.set_ylabel('$S_h$')
ax.set_title('Fig 3: Halo entropy')

# Fig 4 — rotation curves
ax = axes[1, 0]
ax.plot(r, v_efc, label='EFC'); ax.plot(r, v_nfw, '--', label='NFW')
ax.set_xlabel('r [kpc]'); ax.set_ylabel('$v_c$ [km/s]'); ax.legend()
ax.set_title('Fig 4: Rotation curves')

# Fig 5 — projected surface density
ax = axes[1, 1]
ax.semilogy(R_proj, Sigma); ax.set_xlabel('R [kpc]'); ax.set_ylabel(r'$\Sigma$')
ax.set_title('Fig 5: Projected $\\Sigma(R)$')

# Fig 6 — expansion history
ax = axes[1, 2]
ax.plot(z, H_efc, label='EFC'); ax.plot(z, H_lcdm, '--', label=r'$\Lambda$CDM')
ax.set_xlabel('z'); ax.set_ylabel('$H(z)/H_0$'); ax.legend()
ax.set_title('Fig 6: Expansion history')

# Fig 7 — information capacity
ax = axes[2, 0]
ax.plot(S_line, I_line); ax.set_xlabel('S'); ax.set_ylabel('$I$')
ax.set_title('Fig 7: Information capacity $I(S)$')

# Extra: Ef halo profile
ax = axes[2, 1]
Ef_halo = energy_flow_potential(rho_h, S_h)
ax.semilogy(r, Ef_halo); ax.set_xlabel('r [kpc]'); ax.set_ylabel('$E_f$')
ax.set_title('Halo $E_f(r)$')

# Extra: effective acceleration
from efc_master_v1 import effective_acceleration
a_eff = effective_acceleration(r)
ax = axes[2, 2]
ax.plot(r, a_eff); ax.set_xlabel('r [kpc]'); ax.set_ylabel('$a_{eff}$')
ax.set_title('Effective acceleration')

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig('efc_master_v1_demo.png', dpi=150)
print('Saved figure: efc_master_v1_demo.png')
