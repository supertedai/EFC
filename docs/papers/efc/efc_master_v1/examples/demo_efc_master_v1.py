#!/usr/bin/env python
"""demo_efc_master_v1.py — Demonstration of Energy-Flow Cosmology (EFC) v1.1

Generates the seven schematic figures described in the paper's §3:
  1. Ef(rho, S) heatmap
  2. Halo density profile
  3. Halo entropy profile
  4. Rotation curves (EFC vs NFW-like)
  5. Projected surface density
  6. Expansion history H(z)/H0
  7. Information capacity I(S)
"""
import numpy as np
import sys

try:
    from efc_master_v1 import (
        energy_flow_potential, halo_density, halo_entropy,
        rotation_velocity, projected_surface_density,
        expansion_rate, information_capacity, effective_acceleration,
    )
except ImportError:
    sys.path.insert(0, ".")
    from efc_master_v1 import (
        energy_flow_potential, halo_density, halo_entropy,
        rotation_velocity, projected_surface_density,
        expansion_rate, information_capacity, effective_acceleration,
    )

# --- radial grid --------------------------------------------------------
r = np.linspace(0.1, 100.0, 600)
rho = halo_density(r)
S = halo_entropy(r)
Ef = energy_flow_potential(rho, S)
v_efc = rotation_velocity(r, Ef)

# NFW-like reference rotation curve (v ∝ sqrt(ln(1+x)-x/(1+x)) / x)
rs_nfw = 10.0
x_nfw = r / rs_nfw
M_nfw = np.log(1.0 + x_nfw) - x_nfw / (1.0 + x_nfw)
v_nfw = np.sqrt(M_nfw / r) * 15.0  # arbitrary normalisation

# projected surface density
R_proj = np.linspace(0.5, 80.0, 200)
Sigma = projected_surface_density(R_proj, r, rho)

# expansion history
z = np.linspace(0, 3.0, 300)
H_efc = expansion_rate(z, H0=1.0, Omega_m=0.30, Omega_ef=0.70, w_ef=-0.95)
H_lcdm = expansion_rate(z, H0=1.0, Omega_m=0.30, Omega_ef=0.70, w_ef=-1.00)

# information capacity
S_arr = np.linspace(0.0, 1.0, 300)
I_arr = information_capacity(S_arr)

# --- print summary ------------------------------------------------------
print("=== EFC Master Spec v1.1 — Demo ===")
print(f"Ef at centre : {Ef[0]:.4f}")
print(f"Ef at edge   : {Ef[-1]:.6f}")
print(f"v_rot peak   : {v_efc.max():.4f}  at r = {r[np.argmax(v_efc)]:.1f}")
print(f"H(z=0) EFC   : {H_efc[0]:.4f}")
print(f"H(z=0) LCDM  : {H_lcdm[0]:.4f}")
print(f"Sigma(R=1)   : {Sigma[0]:.4f}")

# --- optional plotting ---------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(3, 3, figsize=(14, 12))
    fig.suptitle("EFC Master Specification v1.1 — Schematic Figures", fontsize=14)

    # 1 — Ef heatmap
    rho_g = np.linspace(0.01, 2.0, 200)
    S_g = np.linspace(0.0, 1.0, 200)
    RR, SS = np.meshgrid(rho_g, S_g)
    EF_map = energy_flow_potential(RR, SS)
    ax = axes[0, 0]; im = ax.contourf(RR, SS, EF_map, 40, cmap="inferno")
    fig.colorbar(im, ax=ax); ax.set_xlabel("ρ"); ax.set_ylabel("S"); ax.set_title("Ef(ρ,S)")

    # 2 — halo density
    ax = axes[0, 1]; ax.loglog(r, rho); ax.set_xlabel("r"); ax.set_ylabel("ρ_h"); ax.set_title("Halo density")

    # 3 — halo entropy
    ax = axes[0, 2]; ax.plot(r, S); ax.set_xlabel("r"); ax.set_ylabel("S_h"); ax.set_title("Halo entropy")

    # 4 — rotation curves
    ax = axes[1, 0]; ax.plot(r, v_efc, label="EFC"); ax.plot(r, v_nfw, "--", label="NFW-like")
    ax.set_xlabel("r"); ax.set_ylabel("v_rot"); ax.set_title("Rotation curves"); ax.legend()

    # 5 — projected surface density
    ax = axes[1, 1]; ax.semilogy(R_proj, Sigma); ax.set_xlabel("R"); ax.set_ylabel("Σ(R)"); ax.set_title("Surface density")

    # 6 — expansion history
    ax = axes[1, 2]; ax.plot(z, H_efc, label="EFC (w=-0.95)"); ax.plot(z, H_lcdm, "--", label="ΛCDM")
    ax.set_xlabel("z"); ax.set_ylabel("H/H₀"); ax.set_title("H(z)/H₀"); ax.legend()

    # 7 — information capacity
    ax = axes[2, 0]; ax.plot(S_arr, I_arr); ax.set_xlabel("S"); ax.set_ylabel("I(S)"); ax.set_title("Info capacity")

    # 8 — Ef profile
    ax = axes[2, 1]; ax.semilogy(r, Ef); ax.set_xlabel("r"); ax.set_ylabel("Ef(r)"); ax.set_title("Ef radial profile")

    # 9 — acceleration
    dr = r[1] - r[0]
    a_eff = effective_acceleration(Ef, dr)
    ax = axes[2, 2]; ax.plot(r, np.abs(a_eff)); ax.set_xlabel("r"); ax.set_ylabel("|a_eff|"); ax.set_title("Effective accel.")

    plt.tight_layout(rect=[0, 0, 1, 0.96])
    plt.savefig("efc_demo_output.png", dpi=150)
    print("\nFigure saved → efc_demo_output.png")
except Exception as e:
    print(f"\nPlotting skipped ({e})")
