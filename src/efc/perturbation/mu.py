"""
EFC Perturbation-Level μ(a) Modification
==========================================

Effective gravitational coupling μ(a) = 1 − B g(a) with μ < 1,
which suppresses the gravitational source term in the growth equation.

Reference: EFCLASS Technical Note II
    DOI: 10.6084/m9.figshare.31333600
"""

import numpy as np
from .gate import gate_function, gate_function_z, calibrate_B, DEFAULT_ZT, DEFAULT_N


def mu_of_a(a, B, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Perturbation-level effective gravitational coupling μ(a).

    μ(a) = 1 − B g(a)

    When μ < 1, the gravitational source term in the growth equation
    is weakened, suppressing structure growth and reducing σ₈.

    Parameters
    ----------
    a : float or array_like
        Scale factor.
    B : float
        Perturbation amplitude (B > 0 for suppression).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float or ndarray
        μ(a) values.

    Reference
    ---------
    Eq. (2) of Technical Note II (DOI: 10.6084/m9.figshare.31333600)
    """
    return 1.0 - B * gate_function(a, z_t=z_t, n=n)


def mu_of_z(z, B, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Perturbation-level μ as a function of redshift.

    Parameters
    ----------
    z : float or array_like
        Redshift.
    B : float
        Perturbation amplitude.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float or ndarray
        μ(z) values.
    """
    return 1.0 - B * gate_function_z(z, z_t=z_t, n=n)


def mu_from_mu0(a, mu_0, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Compute μ(a) from a desired present-day value μ₀.

    Internally calibrates B = (1 − μ₀) / g(1; n) and then
    evaluates μ(a) = 1 − B g(a).

    Parameters
    ----------
    a : float or array_like
        Scale factor.
    mu_0 : float
        Desired present-day μ value (μ₀ < 1 for suppression).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float or ndarray
        μ(a) values.
    """
    B = calibrate_B(mu_0, z_t=z_t, n=n)
    return mu_of_a(a, B, z_t=z_t, n=n)


def sigma8_suppression_integral(mu_0, z_t=DEFAULT_ZT, n=DEFAULT_N,
                                a_min=0.1, n_points=1000):
    """
    Compute the σ₈ suppression integral.

    Δσ₈ ∝ (1 − μ₀) ∫_{ln a_min}^{0} g(a; n) d ln a

    This integral determines the magnitude of σ₈ suppression.
    The universal factor-2 arises because this integral approximately
    doubles when n goes from 6 to 2.

    Parameters
    ----------
    mu_0 : float
        Present-day μ value.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    a_min : float
        Lower integration limit in scale factor.
    n_points : int
        Number of integration points.

    Returns
    -------
    float
        Suppression integral value (proportional to Δσ₈).

    Reference
    ---------
    Eq. (5) of Technical Note II (DOI: 10.6084/m9.figshare.31333600)
    """
    ln_a = np.linspace(np.log(a_min), 0.0, n_points)
    a_arr = np.exp(ln_a)
    g_arr = gate_function(a_arr, z_t=z_t, n=n)
    return (1.0 - mu_0) * np.trapezoid(g_arr, ln_a)


def verify_universal_factor_2(mu_0=0.85, z_t=DEFAULT_ZT):
    """
    Verify the universal factor-2: Δσ₈(n=2)/Δσ₈(n=6) ≈ 2.0.

    Parameters
    ----------
    mu_0 : float
        Present-day μ value.
    z_t : float
        Transition redshift.

    Returns
    -------
    dict
        {"ratio": float, "integral_n2": float, "integral_n6": float}

    Reference
    ---------
    Eq. (4) and Table 3 of Technical Note II
    """
    I_n2 = sigma8_suppression_integral(mu_0, z_t=z_t, n=2)
    I_n6 = sigma8_suppression_integral(mu_0, z_t=z_t, n=6)
    ratio = I_n2 / I_n6 if I_n6 != 0 else float("inf")
    return {
        "ratio": ratio,
        "integral_n2": I_n2,
        "integral_n6": I_n6,
    }


# Reference model WP1a parameters (Technical Note II, Eq. 6)
WP1A_REFERENCE = {
    "A": 0.0,
    "B": 0.187,
    "n": 2,
    "z_t": 1.01,
    "mu_0": 0.85,
    "sigma_8": 0.773,
    "S_8": 0.790,
    "gap_closed_percent": 73,
}
