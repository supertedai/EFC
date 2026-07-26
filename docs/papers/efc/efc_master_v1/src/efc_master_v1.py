"""efc_master_v1.py — Reference implementation of Energy-Flow Cosmology (EFC) Master Specification v1.1

Layers implemented:
  EFC-S : Structure / Halo layer (S0–S2)
  EFC-D : Energy-Flow Dynamics  (D0–D3)
  EFC-C0: Entropy–Cognition Base Layer (C0–C2)

Reference: M. Magnusson, EFC Master Specification v1.1, Nov 2025
           DOI 10.6084/m9.figshare.30630500
"""
from __future__ import annotations
import numpy as np
from typing import Tuple

# ---------------------------------------------------------------------------
# Physical / model constants (illustrative defaults from the paper)
# ---------------------------------------------------------------------------
G_N = 6.67430e-11          # Newton's gravitational constant [m^3 kg^-1 s^-2]
H0_DEFAULT = 67.4           # Hubble constant [km/s/Mpc] (fiducial)
RHO0_HALO = 1.0e6           # Central halo density scale [M_sun / kpc^3]
R_S_DEFAULT = 20.0           # Halo scale radius [kpc]
S_CORE = 0.05                # Core entropy (low-entropy anchor)
S_EDGE = 0.95                # Edge / virial entropy
ALPHA_ENT = 2.0              # Entropy profile steepness exponent
KAPPA_I = 1.0                # Information capacity proportionality constant

# ---------------------------------------------------------------------------
# EFC-D: D0 — Local energy-flow potential  Eq. (1)
# ---------------------------------------------------------------------------
def energy_flow_potential(rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Ef(x) = rho(x) * (1 - S(x))   [Eq. 1]"""
    return rho * (1.0 - S)

# ---------------------------------------------------------------------------
# EFC-S: S1–S2 — Halo profiles
# ---------------------------------------------------------------------------
def halo_density(r: np.ndarray, rho0: float = RHO0_HALO,
                 r_s: float = R_S_DEFAULT) -> np.ndarray:
    """Hernquist-like halo mass-density profile.
    rho_h(r) = rho0 / [(r/r_s)(1 + r/r_s)^3]
    """
    x = r / r_s
    return rho0 / (x * (1.0 + x) ** 3 + 1e-30)

def halo_entropy(r: np.ndarray, S_core: float = S_CORE,
                 S_edge: float = S_EDGE, r_s: float = R_S_DEFAULT,
                 alpha: float = ALPHA_ENT) -> np.ndarray:
    """Monotonically rising entropy profile from core to virial radius.
    S_h(r) = S_core + (S_edge - S_core) * [1 - exp(-(r/r_s)^alpha)]
    """
    return S_core + (S_edge - S_core) * (1.0 - np.exp(-(r / r_s) ** alpha))

# ---------------------------------------------------------------------------
# EFC-D: D0.2 — Effective mass density derived from Ef
# ---------------------------------------------------------------------------
def effective_mass_density(Ef: np.ndarray) -> np.ndarray:
    """In EFC the dynamically relevant density is Ef itself (units of rho)."""
    return Ef

# ---------------------------------------------------------------------------
# EFC-D: D1 — Energy-flow rate / temporal evolution
# ---------------------------------------------------------------------------
def energy_flow_rate(rho: np.ndarray, S: np.ndarray,
                    dS_dt: np.ndarray) -> np.ndarray:
    """dEf/dt = drho/dt*(1-S) + rho*(-dS/dt).  For static rho: = -rho*dS/dt"""
    return -rho * dS_dt

# ---------------------------------------------------------------------------
# EFC-D: D2 — Spatial gradient → effective acceleration
# ---------------------------------------------------------------------------
def effective_acceleration(r: np.ndarray, rho0: float = RHO0_HALO,
                           r_s: float = R_S_DEFAULT,
                           S_core: float = S_CORE,
                           S_edge: float = S_EDGE,
                           alpha: float = ALPHA_ENT,
                           dr: float | None = None) -> np.ndarray:
    """a_eff(r) = -dEf/dr  computed numerically from the halo profiles."""
    if dr is None:
        dr = r_s * 1e-4
    rho_p = halo_density(r + dr, rho0, r_s)
    rho_m = halo_density(r - dr, rho0, r_s)
    S_p = halo_entropy(r + dr, S_core, S_edge, r_s, alpha)
    S_m = halo_entropy(r - dr, S_core, S_edge, r_s, alpha)
    Ef_p = energy_flow_potential(rho_p, S_p)
    Ef_m = energy_flow_potential(rho_m, S_m)
    return -(Ef_p - Ef_m) / (2.0 * dr)

# ---------------------------------------------------------------------------
# EFC-D: D2 — Rotation curve from enclosed Ef
# ---------------------------------------------------------------------------
def rotation_curve(r: np.ndarray, rho0: float = RHO0_HALO,
                   r_s: float = R_S_DEFAULT,
                   S_core: float = S_CORE, S_edge: float = S_EDGE,
                   alpha: float = ALPHA_ENT,
                   n_shell: int = 300) -> np.ndarray:
    """v_c(r) = sqrt(G M_eff(<r) / r)  where M_eff is the Ef-weighted mass."""
    kpc_to_m = 3.0857e19
    Msun_to_kg = 1.9885e30
    v = np.zeros_like(r)
    for i, ri in enumerate(r):
        r_int = np.linspace(1e-3, ri, n_shell)
        rho_int = halo_density(r_int, rho0, r_s)
        S_int = halo_entropy(r_int, S_core, S_edge, r_s, alpha)
        Ef_int = energy_flow_potential(rho_int, S_int)
        M_eff = np.trapz(4.0 * np.pi * r_int ** 2 * Ef_int, r_int)
        M_eff_kg = M_eff * Msun_to_kg
        ri_m = ri * kpc_to_m
        v[i] = np.sqrt(G_N * M_eff_kg / ri_m) * 1e-3  # km/s
    return v

# ---------------------------------------------------------------------------
# NFW reference rotation curve (for comparison)
# ---------------------------------------------------------------------------
def nfw_rotation_curve(r: np.ndarray, rho0: float = RHO0_HALO,
                       r_s: float = R_S_DEFAULT) -> np.ndarray:
    kpc_to_m = 3.0857e19
    Msun_to_kg = 1.9885e30
    v = np.zeros_like(r)
    for i, ri in enumerate(r):
        x = ri / r_s
        M_nfw = 4.0 * np.pi * rho0 * r_s ** 3 * (np.log(1 + x) - x / (1 + x))
        v[i] = np.sqrt(G_N * M_nfw * Msun_to_kg / (ri * kpc_to_m)) * 1e-3
    return v

# ---------------------------------------------------------------------------
# EFC-D: D3 — Expansion rate H(z)
# ---------------------------------------------------------------------------
def expansion_rate_efc(z: np.ndarray, H0: float = H0_DEFAULT,
                       S0: float = 0.7, beta: float = 0.4) -> np.ndarray:
    """Schematic EFC expansion history.
    H(z)/H0 = (1+z)^{3/2} * (1 - S0*(1-(1+z)^{-beta}))
    """
    return H0 * (1.0 + z) ** 1.5 * (1.0 - S0 * (1.0 - (1.0 + z) ** (-beta)))

def expansion_rate_lcdm(z: np.ndarray, H0: float = H0_DEFAULT,
                        Om: float = 0.3, OL: float = 0.7) -> np.ndarray:
    """Standard LCDM expansion for comparison."""
    return H0 * np.sqrt(Om * (1 + z) ** 3 + OL)

# ---------------------------------------------------------------------------
# EFC-C0: C0–C2 — Information capacity
# ---------------------------------------------------------------------------
def information_capacity(rho: np.ndarray, S: np.ndarray,
                         kappa: float = KAPPA_I) -> np.ndarray:
    """I(rho, S) = kappa * rho * (1 - S)   [EFC-C0 baseline]"""
    return kappa * rho * (1.0 - S)

def cognitive_load(I: np.ndarray) -> np.ndarray:
    """C1 — Local cognitive load  L = dI/dt  (placeholder: returns I itself)."""
    return I

def informational_field_coupling(Ef: np.ndarray,
                                  kappa: float = KAPPA_I) -> np.ndarray:
    """C2 — Coupling between Ef and information field: phi_I = kappa * Ef."""
    return kappa * Ef

# ---------------------------------------------------------------------------
# Projected surface density  Sigma(R)
# ---------------------------------------------------------------------------
def projected_surface_density(R: np.ndarray, rho0: float = RHO0_HALO,
                               r_s: float = R_S_DEFAULT,
                               z_max: float = 200.0,
                               n_z: int = 500) -> np.ndarray:
    """Sigma(R) = integral of rho_h along line-of-sight."""
    Sigma = np.zeros_like(R)
    for i, Ri in enumerate(R):
        z_arr = np.linspace(0, z_max, n_z)
        r3d = np.sqrt(Ri ** 2 + z_arr ** 2)
        rho_arr = halo_density(r3d, rho0, r_s)
        Sigma[i] = 2.0 * np.trapz(rho_arr, z_arr)
    return Sigma

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    r = np.linspace(0.5, 100.0, 50)
    rho = halo_density(r)
    S = halo_entropy(r)
    Ef = energy_flow_potential(rho, S)
    v_efc = rotation_curve(r)
    v_nfw = nfw_rotation_curve(r)
    z = np.linspace(0, 3, 30)
    H_efc = expansion_rate_efc(z)
    H_lcdm = expansion_rate_lcdm(z)
    I = information_capacity(rho, S)
    print('Self-test passed.')
    print(f'  Ef  range : {Ef.min():.2e} – {Ef.max():.2e}')
    print(f'  v_efc max : {v_efc.max():.1f} km/s')
    print(f'  I   range : {I.min():.2e} – {I.max():.2e}')
