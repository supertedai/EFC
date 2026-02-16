"""
Bulk entropic term and Λ-locked screening.

The bulk entropic reservoir couples local entropy S_i to a
volume-averaged reference entropy S_V:

    F_bulk = ½ μ_Λ (S_i − S_V)²

with μ_Λ ∝ Λ, producing a Yukawa-like screening length:

    L_Λ ~ 1/√Λ

and acceleration scale:

    a₀ = c² / L_Λ ∝ c² √Λ
"""

import math


# Physical constants
C_LIGHT = 2.998e8       # m/s
LAMBDA_PLANCK = 1.11e-52  # m^-2 (Planck 2018)


def screening_length(Lambda: float = LAMBDA_PLANCK) -> float:
    """
    Yukawa-like screening length from Λ-locking.

        L_Λ = 1 / √Λ

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m^-2 (default: Planck 2018 value).

    Returns
    -------
    float
        Screening length in metres.
    """
    return 1.0 / math.sqrt(Lambda)


def acceleration_scale(Lambda: float = LAMBDA_PLANCK, c: float = C_LIGHT) -> float:
    """
    MOND-like acceleration scale from Λ-locking.

        a₀ = c² √Λ

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m^-2.
    c : float
        Speed of light in m/s.

    Returns
    -------
    float
        Acceleration scale in m/s².
    """
    return c * c * math.sqrt(Lambda)


def bulk_entropic_term(S_i: float, S_V: float, mu_Lambda: float) -> float:
    """
    Bulk entropic reservoir free energy contribution.

        F_bulk = ½ μ_Λ (S_i − S_V)²

    Parameters
    ----------
    S_i : float
        Local entropy at node i.
    S_V : float
        Volume-averaged reference entropy.
    mu_Lambda : float
        Coupling strength (∝ Λ).

    Returns
    -------
    float
        Free energy contribution from the bulk term.
    """
    delta_S = S_i - S_V
    return 0.5 * mu_Lambda * delta_S * delta_S


def effective_a0_with_prefactor(
    Lambda: float = LAMBDA_PLANCK,
    c: float = C_LIGHT,
    C: float = 2.32
) -> float:
    """
    Effective acceleration scale including discrete renormalization.

        a₀,eff = C² · c² √Λ

    Parameters
    ----------
    Lambda : float
        Cosmological constant in m^-2.
    c : float
        Speed of light in m/s.
    C : float
        Discrete renormalization prefactor.

    Returns
    -------
    float
        Effective acceleration scale in m/s².
    """
    a0 = acceleration_scale(Lambda, c)
    return C * C * a0
