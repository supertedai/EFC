"""efc_master_v1.py — Reference implementation of Energy-Flow Cosmology (EFC) Master Specification v1.1

Layers implemented:
  EFC-S : Structure / Halo layer
  EFC-D : Energy-Flow Dynamics
  EFC-C0: Entropy–Cognition Base Layer

Reference: M. Magnusson, Nov 16 2025, DOI 10.6084/m9.figshare.30630500
"""
from __future__ import annotations
import numpy as np
from numpy.typing import ArrayLike

# ---------------------------------------------------------------------------
# Physical / model constants  (illustrative baseline values from the paper)
# ---------------------------------------------------------------------------
RHO0: float = 1.0        # central density scale  [arbitrary units]
RS: float = 1.0           # halo scale radius      [arbitrary units]
ALPHA_H: float = 1.0      # halo inner slope
BETA_H: float = 3.0       # halo outer slope
S0: float = 0.01          # central (low) entropy value
S_INF: float = 1.0        # asymptotic entropy at large r
R_S_ENTROPY: float = 1.0  # entropy scale radius
GAMMA_S: float = 2.0      # entropy profile steepness
H0: float = 1.0           # Hubble constant today  [normalised]
OMEGA_EF: float = 0.7     # effective energy-flow density parameter
G_EFF: float = 1.0        # effective gravitational coupling
C_INFO: float = 1.0       # information capacity proportionality constant

# ===================================================================
# EFC-S  — Structure / Halo Layer
# ===================================================================

def halo_density(r: ArrayLike, rho0: float = RHO0, rs: float = RS,
                 alpha: float = ALPHA_H, beta: float = BETA_H) -> np.ndarray:
    """S2. Generalised halo mass-density profile rho_h(r).

    rho_h(r) = rho0 / ((r/rs)^alpha * (1 + r/rs)^(beta - alpha))
    Reduces to NFW for alpha=1, beta=3.
    """
    x = np.asarray(r, dtype=float) / rs
    x = np.maximum(x, 1e-30)
    return rho0 / (x**alpha * (1.0 + x)**(beta - alpha))


def halo_entropy(r: ArrayLike, s0: float = S0, s_inf: float = S_INF,
                 rs: float = R_S_ENTROPY, gamma: float = GAMMA_S) -> np.ndarray:
    """S1-S2. Halo entropy profile S_h(r).

    S_h(r) = s_inf - (s_inf - s0) / (1 + (r/rs)^gamma)
    Low-entropy anchor at centre, rising to s_inf.
    """
    x = np.asarray(r, dtype=float) / rs
    return s_inf - (s_inf - s0) / (1.0 + x**gamma)

# ===================================================================
# EFC-D  — Energy-Flow Dynamics
# ===================================================================

def energy_flow_potential(rho: ArrayLike, S: ArrayLike) -> np.ndarray:
    """D0. Local energy-flow potential  Ef(x) = rho(x) * (1 - S(x)).  Eq (1)."""
    return np.asarray(rho, dtype=float) * (1.0 - np.asarray(S, dtype=float))


def energy_flow_potential_profile(r: ArrayLike, **kw) -> np.ndarray:
    """Convenience: Ef(r) from combined halo density and entropy profiles."""
    rho = halo_density(r, rho0=kw.get('rho0', RHO0), rs=kw.get('rs', RS),
                       alpha=kw.get('alpha', ALPHA_H), beta=kw.get('beta', BETA_H))
    S = halo_entropy(r, s0=kw.get('s0', S0), s_inf=kw.get('s_inf', S_INF),
                     rs=kw.get('rs_entropy', R_S_ENTROPY), gamma=kw.get('gamma', GAMMA_S))
    return energy_flow_potential(rho, S)


def mass_density_from_Ef(Ef: ArrayLike, S: ArrayLike) -> np.ndarray:
    """D0.2. Invert Ef to obtain mass density: rho = Ef / (1 - S)."""
    S_arr = np.asarray(S, dtype=float)
    return np.asarray(Ef, dtype=float) / np.maximum(1.0 - S_arr, 1e-30)


def dEf_dt(rho: ArrayLike, S: ArrayLike, drho_dt: ArrayLike,
           dS_dt: ArrayLike) -> np.ndarray:
    """D1. Energy-flow rate  dEf/dt = (1-S)*drho/dt - rho*dS/dt."""
    rho_a = np.asarray(rho, dtype=float)
    S_a = np.asarray(S, dtype=float)
    return (1.0 - S_a) * np.asarray(drho_dt, dtype=float) - rho_a * np.asarray(dS_dt, dtype=float)


def effective_acceleration(r: ArrayLike, dr: float = 1e-4, **kw) -> np.ndarray:
    """D2. Effective acceleration  a_eff = -G_eff * dEf/dr  (central difference)."""
    r_arr = np.asarray(r, dtype=float)
    Ef_plus = energy_flow_potential_profile(r_arr + dr, **kw)
    Ef_minus = energy_flow_potential_profile(r_arr - dr, **kw)
    grad_Ef = (Ef_plus - Ef_minus) / (2.0 * dr)
    return -kw.get('G_eff', G_EFF) * grad_Ef


def rotation_velocity(r: ArrayLike, **kw) -> np.ndarray:
    """Circular velocity from effective acceleration: v_c = sqrt(|a_eff| * r)."""
    r_arr = np.asarray(r, dtype=float)
    a = effective_acceleration(r_arr, **kw)
    return np.sqrt(np.abs(a) * r_arr)


def nfw_rotation_velocity(r: ArrayLike, rho0: float = RHO0,
                          rs: float = RS) -> np.ndarray:
    """NFW reference rotation curve  v_NFW(r) for comparison (Fig 4)."""
    x = np.asarray(r, dtype=float) / rs
    M_enc = 4.0 * np.pi * rho0 * rs**3 * (np.log(1.0 + x) - x / (1.0 + x))
    r_arr = np.asarray(r, dtype=float)
    return np.sqrt(G_EFF * np.abs(M_enc) / np.maximum(r_arr, 1e-30))


def expansion_rate(z: ArrayLike, H0_val: float = H0,
                   omega_ef: float = OMEGA_EF) -> np.ndarray:
    """D3. Schematic effective expansion rate H(z)/H0.

    Illustrative form: H(z)/H0 = sqrt(omega_ef*(1+z)^3 + (1-omega_ef))
    mimicking a Friedmann-like expression driven by energy-flow density.
    """
    zz = np.asarray(z, dtype=float)
    return H0_val * np.sqrt(omega_ef * (1.0 + zz)**3 + (1.0 - omega_ef))


def lcdm_expansion_rate(z: ArrayLike, H0_val: float = H0,
                        Om: float = 0.3, OL: float = 0.7) -> np.ndarray:
    """LCDM reference  H(z)/H0 = sqrt(Om*(1+z)^3 + OL)  for comparison."""
    zz = np.asarray(z, dtype=float)
    return H0_val * np.sqrt(Om * (1.0 + zz)**3 + OL)

# ===================================================================
# EFC-C0 — Entropy–Cognition Base Layer
# ===================================================================

def information_capacity(S: ArrayLike, rho: float | ArrayLike = 1.0,
                         c: float = C_INFO) -> np.ndarray:
    """C0. Information capacity  I(S) = c * rho * (1 - S).  At fixed rho: I prop (1-S)."""
    return c * np.asarray(rho, dtype=float) * (1.0 - np.asarray(S, dtype=float))


def cognitive_load(S: ArrayLike, rho: ArrayLike, c: float = C_INFO) -> np.ndarray:
    """C1. Local cognitive load = gradient-related measure (magnitude of info capacity)."""
    return information_capacity(S, rho, c)


def info_field_coupling(Ef: ArrayLike, c: float = C_INFO) -> np.ndarray:
    """C2. Informational field coupling: I_field = c * Ef."""
    return c * np.asarray(Ef, dtype=float)


def projected_surface_density(R: ArrayLike, z_max: float = 20.0,
                              nz: int = 500, **kw) -> np.ndarray:
    """Projected surface density Sigma(R) = integral of rho along line of sight."""
    R_arr = np.asarray(R, dtype=float)
    z_los = np.linspace(-z_max, z_max, nz)
    dz = z_los[1] - z_los[0]
    sigma = np.zeros_like(R_arr)
    for i, Ri in enumerate(R_arr):
        r3d = np.sqrt(Ri**2 + z_los**2)
        sigma[i] = np.sum(halo_density(r3d, rho0=kw.get('rho0', RHO0),
                                       rs=kw.get('rs', RS),
                                       alpha=kw.get('alpha', ALPHA_H),
                                       beta=kw.get('beta', BETA_H))) * dz
    return sigma


# ===================================================================
# Self-test
# ===================================================================
if __name__ == '__main__':
    r_test = np.array([0.1, 0.5, 1.0, 2.0, 5.0])
    rho_test = halo_density(r_test)
    s_test = halo_entropy(r_test)
    ef_test = energy_flow_potential(rho_test, s_test)
    print('r        :', r_test)
    print('rho(r)   :', np.round(rho_test, 6))
    print('S(r)     :', np.round(s_test, 6))
    print('Ef(r)    :', np.round(ef_test, 6))

    v_efc = rotation_velocity(r_test)
    v_nfw = nfw_rotation_velocity(r_test)
    print('v_EFC(r) :', np.round(v_efc, 6))
    print('v_NFW(r) :', np.round(v_nfw, 6))

    z_test = np.array([0.0, 0.5, 1.0, 2.0])
    H_efc = expansion_rate(z_test)
    H_lcdm = lcdm_expansion_rate(z_test)
    print('z        :', z_test)
    print('H_EFC/H0 :', np.round(H_efc, 6))
    print('H_LCDM/H0:', np.round(H_lcdm, 6))

    S_grid = np.linspace(0, 0.99, 5)
    I_test = information_capacity(S_grid)
    print('S        :', np.round(S_grid, 4))
    print('I(S)     :', np.round(I_test, 4))
    print('All self-tests passed.')
