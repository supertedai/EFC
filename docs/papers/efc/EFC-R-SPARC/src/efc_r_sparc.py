"""efc_r_sparc.py

Reference implementation for:
  Regime-Dependent Validity in Energy-Flow Cosmology:
  Evidence from SPARC Galaxy Rotation Curves and the EFC-R Framework
  Magnusson 2026, DOI: 10.6084/m9.figshare.31007248

Key equations
-------------
Eq 1:  E_f = rho * (1 - S)
Eq 2:  V_rot^2(r) = r * dPhi_eff/dr
EFC-R: E_total = E_flow + E_latent
       V_rot^2(r) = r * d/dr [Phi_flow + Phi_latent]

Latent-field proxy  L = 1 - (chi2_EFC / chi2_Newton)
  L ~ 0  => EFC captures almost all dynamics (flow-dominated)
  L >> 0 => significant latent / structural contribution
"""
from __future__ import annotations
import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Physical constants (CGS where needed)
# ---------------------------------------------------------------------------
G_CGS: float = 6.674e-8          # cm^3 g^-1 s^-2
G_SI: float = 6.674e-11           # m^3 kg^-1 s^-2
KPC_TO_CM: float = 3.0857e21      # cm per kpc
KPC_TO_M: float = 3.0857e19       # m per kpc
MSOL_KG: float = 1.989e30         # kg per solar mass

# ---------------------------------------------------------------------------
# Paper-reported thresholds and statistics
# ---------------------------------------------------------------------------
SPEARMAN_RHO: float = 0.705       # correlation L vs EFC residual
SPEARMAN_P: float = 0.0005        # p-value
LSB_SUCCESS_RATE: float = 1.0     # 100 % for LSB / dwarf
N_GALAXIES: int = 20

# Regime boundary (empirical, from pilot study)
LATENT_THRESHOLD: float = 0.30    # L < 0.30 => flow-dominated regime


# ---------------------------------------------------------------------------
# Core EFC equations
# ---------------------------------------------------------------------------

def energy_flow_field(rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Eq 1: E_f = rho * (1 - S).

    Parameters
    ----------
    rho : array  local energy density (arbitrary units)
    S   : array  normalised entropy field, values in [0, 1]

    Returns
    -------
    E_f : array  effective energy-flow field
    """
    S = np.clip(S, 0.0, 1.0)
    return rho * (1.0 - S)


def efc_potential(r_kpc: np.ndarray, rho: np.ndarray, S: np.ndarray,
                  G: float = G_SI) -> np.ndarray:
    """Compute cumulative EFC potential Phi_eff(r) via spherical shell
    integration of E_f.

    Phi_eff(r) = -G * integral_0^r  4 pi r'^2 E_f(r') dr'  /  r
    (analogous to Newtonian shell theorem with E_f replacing rho).
    """
    E_f = energy_flow_field(rho, S)
    r_m = r_kpc * KPC_TO_M
    integrand = 4.0 * np.pi * r_m**2 * E_f
    M_enc = np.cumsum(integrand * np.gradient(r_m))
    Phi = -G * M_enc / r_m
    return Phi


def rotation_velocity_efc(r_kpc: np.ndarray, rho: np.ndarray,
                          S: np.ndarray, G: float = G_SI) -> np.ndarray:
    """Eq 2: V_rot(r) from EFC potential.

    V_rot^2 = r * dPhi_eff / dr
    Returns V_rot in km/s.
    """
    Phi = efc_potential(r_kpc, rho, S, G=G)
    r_m = r_kpc * KPC_TO_M
    dPhi_dr = np.gradient(Phi, r_m)
    v2 = r_m * dPhi_dr
    v2 = np.maximum(v2, 0.0)
    return np.sqrt(v2) / 1.0e3          # m/s -> km/s


# ---------------------------------------------------------------------------
# EFC-R extension: E_total = E_flow + E_latent
# ---------------------------------------------------------------------------

def efc_r_total_energy(E_flow: np.ndarray, E_latent: np.ndarray) -> np.ndarray:
    """EFC-R decomposition: E_total = E_flow + E_latent."""
    return E_flow + E_latent


def rotation_velocity_efc_r(r_kpc: np.ndarray, rho: np.ndarray,
                            S: np.ndarray, E_latent: np.ndarray,
                            G: float = G_SI) -> np.ndarray:
    """Modified velocity including latent-field contribution.

    V_rot^2 = r * d/dr [Phi_flow + Phi_latent]
    """
    E_f = energy_flow_field(rho, S)
    E_total = efc_r_total_energy(E_f, E_latent)
    r_m = r_kpc * KPC_TO_M
    integrand = 4.0 * np.pi * r_m**2 * E_total
    M_enc = np.cumsum(integrand * np.gradient(r_m))
    Phi = -G * M_enc / r_m
    dPhi_dr = np.gradient(Phi, r_m)
    v2 = np.maximum(r_m * dPhi_dr, 0.0)
    return np.sqrt(v2) / 1.0e3


# ---------------------------------------------------------------------------
# Latent-field proxy (Sec 2.4)
# ---------------------------------------------------------------------------

def latent_field_proxy(chi2_efc: float, chi2_newton: float) -> float:
    """L = 1 - chi2_EFC / chi2_Newton.

    L ~ 0  => EFC captures dynamics (flow-dominated)
    L large => latent contribution needed
    """
    if chi2_newton == 0:
        return 0.0
    return 1.0 - chi2_efc / chi2_newton


def classify_regime(L: float, threshold: float = LATENT_THRESHOLD) -> str:
    """Classify galaxy into EFC regime.

    Returns 'flow-dominated' or 'latent-significant'.
    """
    return "flow-dominated" if L < threshold else "latent-significant"


# ---------------------------------------------------------------------------
# Simple parametric models for demonstration
# ---------------------------------------------------------------------------

def exponential_disk_density(r_kpc: np.ndarray, Sigma0: float,
                             Rd: float) -> np.ndarray:
    """Exponential disk surface density -> mid-plane volume density proxy."""
    return Sigma0 * np.exp(-r_kpc / Rd)


def entropy_profile(r_kpc: np.ndarray, S0: float = 0.05,
                    r_s: float = 5.0, alpha: float = 1.0) -> np.ndarray:
    """Phenomenological entropy profile S(r) rising from S0 to ~1."""
    return S0 + (1.0 - S0) * (1.0 - np.exp(-(r_kpc / r_s)**alpha))


# ---------------------------------------------------------------------------
# Chi-squared helper
# ---------------------------------------------------------------------------

def chi_squared(v_obs: np.ndarray, v_model: np.ndarray,
                v_err: Optional[np.ndarray] = None) -> float:
    """Reduced chi-squared."""
    if v_err is None:
        v_err = np.ones_like(v_obs)
    residuals = (v_obs - v_model) / v_err
    return float(np.sum(residuals**2) / max(len(v_obs) - 1, 1))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC-R-SPARC module self-test ===")
    r = np.linspace(0.5, 20.0, 80)
    rho = exponential_disk_density(r, Sigma0=1e-21, Rd=3.0)
    S = entropy_profile(r, S0=0.05, r_s=5.0)
    E_f = energy_flow_field(rho, S)
    assert E_f.shape == r.shape, "shape mismatch"
    assert np.all(E_f >= 0), "E_f must be non-negative"

    v_efc = rotation_velocity_efc(r, rho, S)
    assert v_efc.shape == r.shape
    print(f"  V_efc range: {v_efc.min():.2f} - {v_efc.max():.2f} km/s")

    L = latent_field_proxy(chi2_efc=12.0, chi2_newton=50.0)
    print(f"  Latent proxy L = {L:.3f}  regime = {classify_regime(L)}")

    L2 = latent_field_proxy(chi2_efc=40.0, chi2_newton=50.0)
    print(f"  Latent proxy L = {L2:.3f} regime = {classify_regime(L2)}")

    print(f"  Spearman rho (paper) = {SPEARMAN_RHO}")
    print(f"  LSB success rate      = {LSB_SUCCESS_RATE*100:.0f}%")
    print("Self-test PASSED.")
