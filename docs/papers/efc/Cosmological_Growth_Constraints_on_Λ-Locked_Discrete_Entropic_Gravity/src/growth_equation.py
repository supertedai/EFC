"""
Linear growth equation for matter perturbations.

    δ'' + (2 + H'/H) δ' − (3/2) Ω_m(a) [G_eff(k)/G] δ = 0

where primes denote d/d(ln a).

Uses Planck 2018 background cosmology (Ω_m = 0.315, H₀ = 67.4 km/s/Mpc).
"""

import math
from dataclasses import dataclass
from typing import Optional


# Planck 2018 baseline
OMEGA_M = 0.315
H0 = 67.4   # km/s/Mpc
SIGMA8_LCDM = 0.811


@dataclass
class GrowthResult:
    """Result of the linear growth computation."""
    model: str
    scenario: Optional[str]
    sigma8: float
    gamma: float
    viable: bool
    sigma8_excess_factor: Optional[float] = None


def omega_m_of_a(a: float, Omega_m0: float = OMEGA_M) -> float:
    """
    Matter density parameter as function of scale factor.

        Ω_m(a) = Ω_m0 / (Ω_m0 + (1 − Ω_m0) a³)

    Parameters
    ----------
    a : float
        Scale factor.
    Omega_m0 : float
        Present-day matter density parameter.

    Returns
    -------
    float
        Ω_m(a).
    """
    Omega_de = 1.0 - Omega_m0
    return Omega_m0 / (Omega_m0 + Omega_de * a ** 3)


def growth_index_approx(Omega_m0: float = OMEGA_M) -> float:
    """
    Approximate growth index γ for ΛCDM-like background.

        γ ≈ 0.55 + 0.05(1 + w)  with w = −1 → γ ≈ 0.55

    Returns
    -------
    float
        Growth index γ.
    """
    return 0.554


def sigma8_excess(sigma8_modified: float) -> float:
    """
    Compute σ₈ excess factor relative to ΛCDM.

    Parameters
    ----------
    sigma8_modified : float
        σ₈ from the modified model.

    Returns
    -------
    float
        Excess factor (σ₈_modified / σ₈_ΛCDM).
    """
    return sigma8_modified / SIGMA8_LCDM


def is_viable(sigma8: float, sigma8_obs: float = SIGMA8_LCDM,
              sigma_obs: float = 0.006) -> bool:
    """
    Check whether σ₈ is within observational bounds.

    Parameters
    ----------
    sigma8 : float
        Computed σ₈.
    sigma8_obs : float
        Observed central value.
    sigma_obs : float
        Observational 1σ uncertainty.

    Returns
    -------
    bool
        True if within 3σ of observed value.
    """
    return abs(sigma8 - sigma8_obs) < 3.0 * sigma_obs
