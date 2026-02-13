"""
EFC Gate Function
=================

Sigmoid gate g(a) = 1 / (1 + (a_t / a)^n) used in both background
and perturbation modifications.

Reference: EFCLASS Technical Notes I & II
    DOI: 10.6084/m9.figshare.31333414
    DOI: 10.6084/m9.figshare.31333600
"""

import numpy as np


# Default parameters
DEFAULT_ZT = 1.01
DEFAULT_N = 6


def gate_function(a, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Sigmoid gate function in terms of scale factor.

    g(a) = 1 / (1 + (a_t / a)^n)

    Parameters
    ----------
    a : float or array_like
        Scale factor (a = 1 today, a = 1/(1+z)).
    z_t : float
        Transition redshift (default 1.01).
    n : float
        Steepness exponent (default 6).

    Returns
    -------
    float or ndarray
        Gate function value(s) in [0, 1].
    """
    a = np.asarray(a, dtype=float)
    a_t = 1.0 / (1.0 + z_t)
    return 1.0 / (1.0 + (a_t / a) ** n)


def gate_function_z(z, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Sigmoid gate function in terms of redshift.

    Parameters
    ----------
    z : float or array_like
        Redshift.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float or ndarray
        Gate function value(s).
    """
    a = 1.0 / (1.0 + np.asarray(z, dtype=float))
    return gate_function(a, z_t=z_t, n=n)


def calibrate_B(mu_0, z_t=DEFAULT_ZT, n=DEFAULT_N):
    """
    Calibrate amplitude B so that μ(z=0) = μ₀.

    B = (1 - μ₀) / g(1; n)

    This isolates the effect of gate width (n) from amplitude
    when scanning steepness at fixed present-day μ₀.

    Parameters
    ----------
    mu_0 : float
        Desired present-day value of μ (must be < 1 for suppression).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float
        Calibrated B value.

    Reference
    ---------
    Eq. (3) of EFCLASS Technical Note II (DOI: 10.6084/m9.figshare.31333600)
    """
    g_at_1 = gate_function(1.0, z_t=z_t, n=n)
    if g_at_1 == 0:
        raise ValueError("Gate function is zero at a=1; cannot calibrate B.")
    return (1.0 - mu_0) / g_at_1


def gate_support(z_t=DEFAULT_ZT, n=DEFAULT_N, a_min=0.1, n_points=1000):
    """
    Compute the temporal support integral of the gate.

    Support = ∫_{ln a_min}^{0} |1 - μ(a)| d ln a

    This integral controls the magnitude of σ₈ suppression.

    Parameters
    ----------
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
        Temporal support integral value.
    """
    ln_a = np.linspace(np.log(a_min), 0.0, n_points)
    a_arr = np.exp(ln_a)
    g_arr = gate_function(a_arr, z_t=z_t, n=n)
    return np.trapezoid(g_arr, ln_a)
