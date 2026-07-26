"""demo_efc_master_v1.py — Demonstration of the EFC Master Specification v1.1 reference code.

Generates the seven schematic figures described in Section 3 of the paper.
Requires: numpy, matplotlib.  Run:  python demo_efc_master_v1.py
"""
import numpy as np
import matplotlib.pyplot as plt
from efc_master_v1 import (
    energy_flow_potential, halo_density, halo_entropy,
    energy_flow_potential_profile, rotation_velocity,
    nfw_rotation_velocity, projected_surface_density,
    expansion_rate, lcdm_expansion_rate, information_capacity,
)

# ---------- Fig 1: Ef(rho, S) heatmap ----------
rho_grid = np.linspace(0.01, 3.0, 200)
S_grid = np.linspace(0.0, 0.99, 200)
RHO, S = np.meshgrid(rho_grid, S_grid)
EF = energy_flow_potential(RHO, S)

fig, ax = plt.subplots(figsize=(6, 5))
cf = ax.contourf(RHO, S, EF, levels=40, cmap='inferno')
plt.colorbar(cf, ax=ax, label=r'$E_f$')
ax.set_xlabel(r'Mass density $\rho$')
ax.set_ylabel(r'Dimensionless entropy $S$')
ax.set_title(r'Fig 1 — Energy-flow potential $E_f(\rho, S)=\rho(1-S)$')
fig.tight_layout(); fig.savefig('fig1_Ef_heatmap.png', dpi=150)

# ---------- Fig 2 & 3: Halo profiles ----------
r = np.linspace(0.01, 10.0, 500)
rho_h = halo_density(r)
S_h = halo_entropy(r)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].semilogy(r, rho_h, 'k-', lw=2)
axes[0].set_xlabel('r'); axes[0].set_ylabel(r'$\rho_h(r)$')
axes[0].set_title('Fig 2 — Halo mass density profile')
axes[1].plot(r, S_h, 'b-', lw=2)
axes[1].set_xlabel('r'); axes[1].set_ylabel(r'$S_h(r)$')
axes[1].set_title('Fig 3 — Halo entropy profile')
fig.tight_layout(); fig.savefig('fig2_3_halo_profiles.png', dpi=150)

# ---------- Fig 4: Rotation curves ----------
v_efc = rotation_velocity(r)
v_nfw = nfw_rotation_velocity(r)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(r, v_efc, 'r-', lw=2, label='EFC-like')
ax.plot(r, v_nfw, 'b--', lw=2, label='NFW-like')
ax.set_xlabel('r'); ax.set_ylabel(r'$v_c(r)$')
ax.set_title('Fig 4 — Rotation curves'); ax.legend()
fig.tight_layout(); fig.savefig('fig4_rotation_curves.png', dpi=150)

# ---------- Fig 5: Projected surface density ----------
R_proj = np.linspace(0.05, 8.0, 200)
Sigma = projected_surface_density(R_proj)

fig, ax = plt.subplots(figsize=(6, 4))
ax.semilogy(R_proj, Sigma, 'k-', lw=2)
ax.set_xlabel('R (projected)'); ax.set_ylabel(r'$\Sigma(R)$')
ax.set_title('Fig 5 — Projected surface density')
fig.tight_layout(); fig.savefig('fig5_surface_density.png', dpi=150)

# ---------- Fig 6: Expansion history ----------
z = np.linspace(0, 3, 300)
H_efc = expansion_rate(z)
H_lcdm = lcdm_expansion_rate(z)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(z, H_efc, 'r-', lw=2, label='EFC-like')
ax.plot(z, H_lcdm, 'b--', lw=2, label=r'$\Lambda$CDM-like')
ax.set_xlabel('z'); ax.set_ylabel(r'$H(z)/H_0$')
ax.set_title('Fig 6 — Expansion history'); ax.legend()
fig.tight_layout(); fig.savefig('fig6_expansion_history.png', dpi=150)

# ---------- Fig 7: Information capacity ----------
S_lin = np.linspace(0, 0.99, 300)
I_cap = information_capacity(S_lin)

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(S_lin, I_cap, 'g-', lw=2)
ax.set_xlabel(r'Entropy $S$'); ax.set_ylabel(r'$I(S)$')
ax.set_title(r'Fig 7 — Information capacity $I(S)\propto(1-S)$')
fig.tight_layout(); fig.savefig('fig7_information_capacity.png', dpi=150)

print('All 7 figures saved to current directory.')

# ---------- Numerical summary ----------
print('\n=== Numerical summary (Table) ===')
for ri in [0.1, 0.5, 1.0, 2.0, 5.0]:
    rho_v = halo_density(ri)
    s_v = halo_entropy(ri)
    ef_v = energy_flow_potential(rho_v, s_v)
    print(f'  r={ri:5.2f}  rho={float(rho_v):.4e}  S={float(s_v):.4f}  Ef={float(ef_v):.4e}')
