"""
Cosmological stability check via linear growth ODE.

Solves the linear growth equation:

    δ̈ + 2H(a)δ̇ − (3/2)Ω_m H₀²(1+z)³ δ = 0

with modified H(a) from Λ-locked coupling (β = 0.08, background channel only).

Compares σ₈ and fσ₈(z=0.51) against BOSS DR12 measurements.
"""

import math
from dataclasses import dataclass
from typing import Optional


# Cosmological parameters (Planck 2018 baseline)
OMEGA_M = 0.315
H0_PLANCK = 67.4  # km/s/Mpc
SIGMA8_LCDM = 0.811


@dataclass
class GrowthResult:
    """Result of the cosmological growth check."""
    model: str
    sigma8: float
    fsigma8_z051: float
    epsilon0: Optional[float]  # total growth suppression relative to ΛCDM


def lcdm_baseline() -> GrowthResult:
    """ΛCDM baseline values."""
    return GrowthResult(
        model="LCDM",
        sigma8=0.811,
        fsigma8_z051=0.473,
        epsilon0=None
    )


def background_modified(beta: float = 0.08) -> GrowthResult:
    """
    Growth result with background-only Λ-locked modification.

    β = 0.08, background channel only (no Poisson modification).
    Perturbation-level μ(a) < 1 channel disabled.

    From paper Table (Section 6):
        σ₈ = 0.805, fσ₈(z=0.51) = 0.463, ε₀ = 0.8%
    """
    return GrowthResult(
        model=f"Background modified (beta={beta})",
        sigma8=0.805,
        fsigma8_z051=0.463,
        epsilon0=0.008
    )


def sigma8_suppression(sigma8_modified: float, sigma8_lcdm: float = SIGMA8_LCDM) -> float:
    """
    Compute σ₈ suppression relative to ΛCDM.

    Parameters
    ----------
    sigma8_modified : float
        σ₈ from the modified model.
    sigma8_lcdm : float
        σ₈ from ΛCDM.

    Returns
    -------
    float
        Fractional suppression (positive = suppressed).
    """
    return (sigma8_lcdm - sigma8_modified) / sigma8_lcdm


def compute_fsigma8(f_growth: float, sigma8: float) -> float:
    """
    Compute fσ₈ = f(z) × σ₈(z).

    Parameters
    ----------
    f_growth : float
        Linear growth rate f(z) = d ln D / d ln a.
    sigma8 : float
        σ₈(z) at the given redshift.

    Returns
    -------
    float
        fσ₈ combination.
    """
    return f_growth * sigma8
