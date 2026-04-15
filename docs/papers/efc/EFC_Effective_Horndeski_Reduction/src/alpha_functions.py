"""Closed-form Bellini-Sawicki alpha-functions for EFC in the QS sub-horizon limit.

These mirror Eqs. (alphaM_definition, alphaB_effective, alphaK_effective,
alphaT_zero, stiffness_response) in the paper's ``index.json``.
"""
from __future__ import annotations

import math


def sigmoid(ln_a: float, ln_a_t: float = math.log(0.30), width: float = 0.20) -> float:
    """Logistic transition S(a) used as the entropy sigmoid."""
    return 1.0 / (1.0 + math.exp(-(ln_a - ln_a_t) / width))


def dsigmoid_dlna(ln_a: float, ln_a_t: float = math.log(0.30), width: float = 0.20) -> float:
    """dS/d ln a for the logistic transition."""
    s = sigmoid(ln_a, ln_a_t, width)
    return s * (1.0 - s) / width


def alpha_M(ln_a: float, M0: float = 0.06) -> float:
    """Planck-mass running proportional to S(a)."""
    return M0 * sigmoid(ln_a)


def alpha_B(ln_a: float, B0: float = 0.02) -> float:
    """Effective braiding tracks dS/d ln a."""
    return B0 * dsigmoid_dlna(ln_a)


def alpha_K(K_rho: float, phi_dot: float, M_star_sq: float, H: float) -> float:
    """EFC kineticity sourced by density-dependent kinetic stiffness."""
    if M_star_sq <= 0 or H <= 0:
        raise ValueError("M_star_sq and H must be positive")
    return (K_rho * phi_dot ** 2) / (M_star_sq * H ** 2)


def alpha_T() -> float:
    """Tensor speed excess is zero (c_T = c)."""
    return 0.0


def stiffness_response(K_rho: float, a: float, Gamma_prime: float, phi_dot: float,
                       F: float, k: float, M_Pl: float) -> float:
    """R(k, z) scale-dependent stiffness response (see Eq. stiffness_response)."""
    if F <= 0 or k <= 0 or M_Pl <= 0:
        raise ValueError("F, k, M_Pl must be positive")
    num = K_rho * a ** 4 * Gamma_prime ** 2 * phi_dot ** 2
    den = 2.0 * F * k ** 4 * M_Pl ** 2
    return num / den
