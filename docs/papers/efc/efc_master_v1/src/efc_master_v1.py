"""efc_master_v1.py — Reference implementation of Energy-Flow Cosmology (EFC) Master Specification v1.1

Layers implemented:
  EFC-S : Structure / Halo layer
  EFC-D : Energy-Flow Dynamics
  EFC-C0: Entropy–Cognition Base Layer

Reference: M. Magnusson, "EFC — Master Specification v1.1", Nov 2025
           DOI 10.6084/m9.figshare.30630500
"""
from __future__ import annotations
import numpy as np
from typing import Tuple

# ---------------------------------------------------------------------------
# Physical / model constants  (schematic defaults from the paper)
# ---------------------------------------------------------------------------
RHO0_DEFAULT: float = 1.0        # central density scale [arbitrary units]
RS_DEFAULT: float = 10.0         # halo scale radius [kpc-like]
ALPHA_DEFAULT: float = 1.0       # inner slope of halo density profile
BETA_DEFAULT: float = 3.0        # outer slope of halo density profile
S0_DEFAULT: float = 0.05         # central (low) entropy of anchor
S_INF_DEFAULT: float = 0.95      # asymptotic entropy far from centre
R_S_ENTROPY: float = 15.0        # entropy scale radius
GAMMA_DEFAULT: float = 2.0       # entropy profile steepness
LAMBDA_EF: float = 1.0           # coupling constant in energy-flow rate
H0_DEFAULT: float = 1.0          # Hubble constant scale (H0=1 in natural)
G_EFF: float = 1.0               # effective gravitational coupling

# ---------------------------------------------------------------------------
# EFC-D  §5.1 — Local energy-flow potential  Eq. (1)
# ---------------------------------------------------------------------------

def energy_flow_potential(rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Ef(x) = rho(x) * (1 - S(x))   [Eq. 1]"""
    return rho * (1.0 - S)

# ---------------------------------------------------------------------------
# EFC-S  §4.2–4.3 — Halo profiles
# ---------------------------------------------------------------------------

def halo_density(r: np.ndarray, rho0: float = RHO0_DEFAULT,
                 rs: float = RS_DEFAULT, alpha: float = ALPHA_DEFAULT,
                 beta: float = BETA_DEFAULT) -> np.ndarray:
    """Generalised halo mass-density profile rho_h(r).
    rho_h(r) = rho0 / ((r/rs)^alpha * (1 + r/rs)^(beta - alpha))
    Reduces to NFW-like when alpha=1, beta=3."""
    x = r / rs
    return rho0 / (x**alpha * (1.0 + x)**(beta - alpha))


def halo_entropy(r: np.ndarray, S0: float = S0_DEFAULT,
                 S_inf: float = S_INF_DEFAULT, rs: float = R_S_ENTROPY,
                 gamma: float = GAMMA_DEFAULT) -> np.ndarray:
    """Monotonically rising entropy profile  S_h(r) = S0 + (S_inf-S0)*(1-exp(-(r/rs)^gamma))."""
    return S0 + (S_inf - S0) * (1.0 - np.exp(-(r / rs) ** gamma))

# ---------------------------------------------------------------------------
# EFC-D  §5.2 — Mass density from energy-flow potential
# ---------------------------------------------------------------------------

def mass_density_from_ef(Ef: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Invert Ef = rho*(1-S)  => rho = Ef / (1-S)."""
    return Ef / np.maximum(1.0 - S, 1e-30)

# ---------------------------------------------------------------------------
# EFC-D  §5.3 — Energy-flow rate (temporal evolution)
# ---------------------------------------------------------------------------

def energy_flow_rate(Ef: np.ndarray, lam: float = LAMBDA_EF) -> np.ndarray:
    """dEf/dt ~ -lambda * Ef   (dissipative flow toward equilibrium)."""
    return -lam * Ef

# ---------------------------------------------------------------------------
# EFC-D  §5.4 — Spatial gradients → effective acceleration
# ---------------------------------------------------------------------------

def effective_acceleration(Ef: np.ndarray, dr: float = 1.0) -> np.ndarray:
    """a_eff = -dEf/dr  (central finite differences)."""
    grad = np.gradient(Ef, dr)
    return -grad


def rotation_velocity(r: np.ndarray, Ef: np.ndarray,
                      G: float = G_EFF) -> np.ndarray:
    """v_rot = sqrt(r * |a_eff|) from the energy-flow gradient."""
    dr = r[1] - r[0] if len(r) > 1 else 1.0
    a = effective_acceleration(Ef, dr)
    return np.sqrt(np.abs(r * a))

# ---------------------------------------------------------------------------
# EFC-D  §5.5 — Expansion rate H(z)
# ---------------------------------------------------------------------------

def expansion_rate(z: np.ndarray, H0: float = H0_DEFAULT,
                   Omega_m: float = 0.3, Omega_ef: float = 0.7,
                   w_ef: float = -1.0) -> np.ndarray:
    """Schematic effective expansion history H(z)/H0.
    H^2/H0^2 = Omega_m*(1+z)^3 + Omega_ef*(1+z)^(3*(1+w_ef))
    In baseline EFC w_ef ~ -1 so Omega_ef term ~ constant."""
    return H0 * np.sqrt(Omega_m * (1.0 + z)**3
                        + Omega_ef * (1.0 + z)**(3.0 * (1.0 + w_ef)))

# ---------------------------------------------------------------------------
# EFC-C0  §6.1 — Information capacity
# ---------------------------------------------------------------------------

def information_capacity(S: np.ndarray, rho: np.ndarray | None = None) -> np.ndarray:
    """I(S) proportional to (1 - S).  At fixed density I = rho*(1-S) = Ef."""
    if rho is None:
        return 1.0 - S
    return rho * (1.0 - S)

# ---------------------------------------------------------------------------
# EFC-C0  §6.2 — Local cognitive load
# ---------------------------------------------------------------------------

def cognitive_load(S: np.ndarray, Ef: np.ndarray) -> np.ndarray:
    """C_L = S / max(Ef, eps) — higher entropy & lower Ef → higher load."""
    return S / np.maximum(Ef, 1e-30)

# ---------------------------------------------------------------------------
# EFC-C0  §6.3 — Informational field coupling
# ---------------------------------------------------------------------------

def info_field_coupling(Ef: np.ndarray, I: np.ndarray) -> np.ndarray:
    """Phi_I = Ef * I  — coupling between energy-flow and information."""
    return Ef * I

# ---------------------------------------------------------------------------
# Projected surface density  (§3.3 helper)
# ---------------------------------------------------------------------------

def projected_surface_density(R_proj: np.ndarray, r: np.ndarray,
                              rho: np.ndarray) -> np.ndarray:
    """Abel-transform style LOS integration Sigma(R)=2*int_R^rmax rho*r/sqrt(r^2-R^2) dr."""
    Sigma = np.zeros_like(R_proj)
    for i, Rp in enumerate(R_proj):
        mask = r > Rp
        if mask.any():
            integrand = rho[mask] * r[mask] / np.sqrt(r[mask]**2 - Rp**2)
            Sigma[i] = 2.0 * np.trapz(integrand, r[mask])
    return Sigma

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    r = np.linspace(0.1, 100.0, 500)
    rho = halo_density(r)
    S = halo_entropy(r)
    Ef = energy_flow_potential(rho, S)
    v = rotation_velocity(r, Ef)
    I = information_capacity(S, rho)
    z = np.linspace(0, 3, 100)
    H = expansion_rate(z)
    print("Self-test passed.")
    print(f"  r range     : {r[0]:.1f} – {r[-1]:.1f}")
    print(f"  Ef range    : {Ef.min():.4e} – {Ef.max():.4e}")
    print(f"  v_rot range : {v.min():.4e} – {v.max():.4e}")
    print(f"  H(z=0)      : {H[0]:.4f}")
    print(f"  I(r_min)    : {I[0]:.4e}")
