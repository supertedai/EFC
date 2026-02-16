"""
Scale-dependent effective gravitational coupling G_eff(k).

Implements the Lorentzian window function:

    G_eff(k)/G = 1 + (C² − 1) / (1 + (k/k_Λ)²)

For k >> k_Λ: G_eff → G (Newtonian, screened)
For k << k_Λ: G_eff → C² G (full infrared enhancement)
"""

import math
from dataclasses import dataclass


# Constants
C_LIGHT = 2.998e8          # m/s
LAMBDA_PLANCK = 1.11e-52   # m^-2 (Planck 2018)
MPC_IN_METRES = 3.086e22   # metres per Mpc


@dataclass
class GeffModel:
    """Lorentzian G_eff(k) model parameterised by C and k_transition."""
    C: float
    k_transition: float  # h/Mpc

    @property
    def enhancement(self) -> float:
        """Maximum enhancement factor C² − 1."""
        return self.C ** 2 - 1.0

    def ratio(self, k: float) -> float:
        """Compute G_eff(k)/G for wavenumber k in h/Mpc."""
        return 1.0 + self.enhancement / (1.0 + (k / self.k_transition) ** 2)


def geff_ratio(k: float, k_transition: float, C: float = 2.32) -> float:
    """
    Compute G_eff(k)/G using Lorentzian window.

    Parameters
    ----------
    k : float
        Wavenumber in h/Mpc.
    k_transition : float
        Transition wavenumber in h/Mpc.
    C : float
        Discrete renormalization prefactor (default 2.32).

    Returns
    -------
    float
        G_eff(k)/G ratio.
    """
    enhancement = C * C - 1.0
    return 1.0 + enhancement / (1.0 + (k / k_transition) ** 2)


def lambda_locked_scale(Lambda: float = LAMBDA_PLANCK) -> float:
    """
    Compute the Λ-locked screening length L_Λ.

        L_Λ = 1/√Λ

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m^-2.

    Returns
    -------
    float
        Screening length in Gpc.
    """
    L_metres = 1.0 / math.sqrt(Lambda)
    L_Mpc = L_metres / MPC_IN_METRES
    L_Gpc = L_Mpc / 1000.0
    return L_Gpc


def lambda_locked_k(Lambda: float = LAMBDA_PLANCK) -> float:
    """
    Compute the Λ-locked transition wavenumber k_Λ.

        k_Λ = 1/L_Λ  (in h/Mpc, approximate)

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m^-2.

    Returns
    -------
    float
        Transition wavenumber in h/Mpc (approximate).
    """
    L_Gpc = lambda_locked_scale(Lambda)
    L_Mpc = L_Gpc * 1000.0
    # k in 1/Mpc ≈ h/Mpc for h ≈ 0.674
    return 1.0 / L_Mpc


def is_screened(k: float, k_transition: float, threshold: float = 0.01) -> bool:
    """
    Check whether wavenumber k is effectively screened.

    Screened means G_eff/G − 1 < threshold.

    Parameters
    ----------
    k : float
        Wavenumber in h/Mpc.
    k_transition : float
        Transition wavenumber in h/Mpc.
    threshold : float
        Maximum allowed enhancement above G (default 1%).

    Returns
    -------
    bool
        True if k is screened.
    """
    enhancement = geff_ratio(k, k_transition) - 1.0
    max_enhancement = 2.32 ** 2 - 1.0
    return (enhancement / max_enhancement) < threshold
