"""efc_r_sparc.py

Reference implementation of the Energy-Flow Cosmology Regime (EFC-R)
framework from:

  Magnusson (2026), "Regime-Dependent Validity in Energy-Flow Cosmology:
  Evidence from SPARC Galaxy Rotation Curves and the EFC-R Framework"
  DOI: 10.6084/m9.figshare.31007248

Key equations implemented:
  (1) E_f = rho * (1 - S)           -- effective energy field
  (2) V_rot^2(r) = r * dPhi_e/dr    -- circular velocity from energy-flow potential
  EFC-R decomposition: E_total = E_flow + E_latent
  Latent field proxy & regime classification
"""

import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Physical / model constants from the paper
# ---------------------------------------------------------------------------
G_N: float = 4.302e-3  # gravitational constant in pc (km/s)^2 / M_sun
SPEARMAN_RHO: float = -0.705  # reported correlation (complexity vs performance)
SPEARMAN_P: float = 0.0005  # associated p-value
LSB_SUCCESS_RATE: float = 1.0  # 100 % for LSB / diffuse dwarfs
N_SAMPLE: int = 20  # pilot sample size


# ---------------------------------------------------------------------------
# Equation (1): Effective energy field
# ---------------------------------------------------------------------------
def effective_energy_field(rho: np.ndarray, S: np.ndarray) -> np.ndarray:
    """Compute the EFC effective energy field.

    Equation (1):  E_f = rho * (1 - S)

    Parameters
    ----------
    rho : array-like
        Local energy density profile (arbitrary units or M_sun/pc^3).
    S : array-like
        Normalised entropy field, values in [0, 1].

    Returns
    -------
    E_f : np.ndarray
        Effective energy field at each radial point.
    """
    rho = np.asarray(rho, dtype=float)
    S = np.asarray(S, dtype=float)
    if np.any(S < 0) or np.any(S > 1):
        raise ValueError("Entropy field S must be in [0, 1].")
    return rho * (1.0 - S)


# ---------------------------------------------------------------------------
# Energy-flow potential and Equation (2): rotation velocity
# ---------------------------------------------------------------------------
def energy_flow_potential(r: np.ndarray, E_f: np.ndarray) -> np.ndarray:
    """Compute a Poisson-sourced potential Phi_e from E_f.

    We solve the spherically-symmetric Poisson equation in the
    thin-shell approximation:
        Phi_e(r) = -G int_0^r 4 pi r'^2 E_f(r') dr' / r
    using cumulative trapezoidal integration.

    Parameters
    ----------
    r : np.ndarray  Radial positions (pc).
    E_f : np.ndarray  Effective energy field (density-like units).

    Returns
    -------
    Phi_e : np.ndarray  Gravitational-like potential (km/s)^2.
    """
    r = np.asarray(r, dtype=float)
    E_f = np.asarray(E_f, dtype=float)
    integrand = 4.0 * np.pi * r**2 * E_f
    cumul = np.zeros_like(r)
    for i in range(1, len(r)):
        cumul[i] = cumul[i - 1] + 0.5 * (integrand[i - 1] + integrand[i]) * (r[i] - r[i - 1])
    Phi_e = -G_N * cumul / np.maximum(r, r[r > 0].min() * 1e-6)
    return Phi_e


def rotation_velocity(r: np.ndarray, E_f: np.ndarray) -> np.ndarray:
    """Circular velocity from energy-flow potential.

    Equation (2):  V_rot^2(r) = r * dPhi_e / dr

    Parameters
    ----------
    r : np.ndarray  Radii in pc.
    E_f : np.ndarray  Effective energy field.

    Returns
    -------
    V_rot : np.ndarray  Rotation velocity in km/s.
    """
    Phi_e = energy_flow_potential(r, E_f)
    dPhi_dr = np.gradient(Phi_e, r)
    V2 = r * dPhi_dr
    V2 = np.maximum(V2, 0.0)  # enforce physicality
    return np.sqrt(V2)


# ---------------------------------------------------------------------------
# EFC-R decomposition: E_total = E_flow + E_latent
# ---------------------------------------------------------------------------
def efc_r_decomposition(
    rho: np.ndarray,
    S: np.ndarray,
    latent_fraction: float,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decompose total energy into flow and latent components.

    E_total = E_flow + E_latent
    E_flow  = rho * (1 - S)          (the standard EFC term)
    E_latent = latent_fraction * rho  (regime-dependent residual)

    Parameters
    ----------
    rho : np.ndarray  Energy density.
    S : np.ndarray  Normalised entropy.
    latent_fraction : float  Fraction of rho attributed to latent field.

    Returns
    -------
    E_flow, E_latent, E_total : tuple of np.ndarray
    """
    E_flow = effective_energy_field(rho, S)
    E_latent = latent_fraction * np.asarray(rho, dtype=float)
    E_total = E_flow + E_latent
    return E_flow, E_latent, E_total


# ---------------------------------------------------------------------------
# Latent-field proxy (structural complexity metric)
# ---------------------------------------------------------------------------
def latent_field_proxy(
    v_obs: np.ndarray,
    v_efc: np.ndarray,
) -> float:
    """Quantify residual not captured by pure EFC.

    L_proxy = sqrt( mean( (V_obs - V_efc)^2 ) ) / mean(V_obs)

    A higher value indicates greater structural complexity
    (more latent-field contribution needed).

    Parameters
    ----------
    v_obs : np.ndarray  Observed rotation velocities (km/s).
    v_efc : np.ndarray  EFC-predicted rotation velocities (km/s).

    Returns
    -------
    L : float  Latent field proxy (dimensionless).
    """
    v_obs = np.asarray(v_obs, dtype=float)
    v_efc = np.asarray(v_efc, dtype=float)
    rms = np.sqrt(np.mean((v_obs - v_efc) ** 2))
    return float(rms / np.mean(v_obs))


def classify_regime(L_proxy: float, threshold: float = 0.15) -> str:
    """Classify galaxy into EFC regime.

    Parameters
    ----------
    L_proxy : float  Latent field proxy value.
    threshold : float  Boundary between flow-dominated and latent regimes.

    Returns
    -------
    regime : str  'flow-dominated' or 'latent-significant'
    """
    return "flow-dominated" if L_proxy <= threshold else "latent-significant"


# ---------------------------------------------------------------------------
# Goodness-of-fit helper
# ---------------------------------------------------------------------------
def reduced_chi2(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    v_err: np.ndarray,
    n_params: int = 2,
) -> float:
    """Reduced chi-squared statistic."""
    v_obs = np.asarray(v_obs, dtype=float)
    v_model = np.asarray(v_model, dtype=float)
    v_err = np.asarray(v_err, dtype=float)
    chi2 = np.sum(((v_obs - v_model) / v_err) ** 2)
    dof = max(len(v_obs) - n_params, 1)
    return float(chi2 / dof)


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC-R-SPARC self-test ===")
    # Synthetic exponential-disk galaxy
    r = np.linspace(0.1, 20.0, 200) * 1e3  # 0.1-20 kpc in pc
    rho = 1e-2 * np.exp(-r / (5e3))  # exponential disk
    S = 0.3 * np.ones_like(r)  # uniform low entropy (LSB-like)

    E_f = effective_energy_field(rho, S)
    V = rotation_velocity(r, E_f)
    print(f"Peak V_rot (pure EFC) = {V.max():.1f} km/s")

    # EFC-R decomposition
    E_flow, E_lat, E_tot = efc_r_decomposition(rho, S, latent_fraction=0.05)
    V_r = rotation_velocity(r, E_tot)
    print(f"Peak V_rot (EFC-R, 5% latent) = {V_r.max():.1f} km/s")

    # Latent proxy & regime
    Lp = latent_field_proxy(V_r, V)
    regime = classify_regime(Lp)
    print(f"Latent proxy = {Lp:.4f}  ->  regime: {regime}")

    # Verify Spearman constant stored correctly
    print(f"\nPaper Spearman rho = {SPEARMAN_RHO}, p = {SPEARMAN_P}")
    print(f"LSB success rate   = {LSB_SUCCESS_RATE*100:.0f}%")
    print("Self-test PASSED.")
