"""
EFC Background Modification
============================

Background-level gate modification to the Friedmann equation and
the sign structure ΔE² = A[g(z) − g(0)] ≤ 0.

Reference: EFCLASS Technical Note I
    DOI: 10.6084/m9.figshare.31333414

Lemma 1: Under E(0) = 1 closure, ΔE²(z) ≤ 0 for all z > 0,
meaning H_EFC(z) ≤ H_ΛCDM(z) (reduced Hubble friction, enhanced growth).
"""

import numpy as np
from .gate import gate_function, gate_function_z


# Planck 2018 default cosmology
DEFAULT_OMEGA_R = 9.15e-5   # radiation density (approximate)
DEFAULT_OMEGA_M = 0.3134
DEFAULT_H0 = 67.4           # km/s/Mpc


def _omega_lambda(Omega_m, Omega_r=DEFAULT_OMEGA_R):
    """ΛCDM closure: Ω_Λ = 1 − Ω_m − Ω_r."""
    return 1.0 - Omega_m - Omega_r


def E2_lcdm(z, Omega_m=DEFAULT_OMEGA_M, Omega_r=DEFAULT_OMEGA_R):
    """
    Standard ΛCDM dimensionless Hubble parameter squared.

    E²(z) = Ω_r(1+z)⁴ + Ω_m(1+z)³ + Ω_Λ

    Parameters
    ----------
    z : float or array_like
        Redshift.
    Omega_m : float
        Matter density parameter.
    Omega_r : float
        Radiation density parameter.

    Returns
    -------
    float or ndarray
        E²(z) values.
    """
    z = np.asarray(z, dtype=float)
    Omega_L = _omega_lambda(Omega_m, Omega_r)
    return Omega_r * (1 + z)**4 + Omega_m * (1 + z)**3 + Omega_L


def delta_E2(z, A, z_t=1.01, n=6):
    """
    Background modification ΔE²(z) = A[g(z) − g(0)].

    Sign lemma (Lemma 1): This is ≤ 0 for all z > 0 when A > 0
    and g is monotonically non-decreasing in a.

    Parameters
    ----------
    z : float or array_like
        Redshift.
    A : float
        EFC background coupling amplitude (A > 0).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float or ndarray
        ΔE²(z) values (≤ 0 for z > 0).

    Reference
    ---------
    Eq. (5) of Technical Note I (DOI: 10.6084/m9.figshare.31333414)
    """
    g_z = gate_function_z(z, z_t=z_t, n=n)
    g_0 = gate_function(1.0, z_t=z_t, n=n)
    return A * (g_z - g_0)


def E2_efc(z, A, z_t=1.01, n=6, Omega_m=DEFAULT_OMEGA_M,
           Omega_r=DEFAULT_OMEGA_R):
    """
    EFC-modified dimensionless Hubble parameter squared.

    E²_EFC(z) = E²_ΛCDM(z) + ΔE²(z)

    Closure is enforced by adjusting Ω'_Λ = Ω_Λ − A g(0).

    Parameters
    ----------
    z : float or array_like
        Redshift.
    A : float
        EFC background coupling amplitude.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    Omega_m : float
        Matter density parameter.
    Omega_r : float
        Radiation density parameter.

    Returns
    -------
    float or ndarray
        E²_EFC(z) values.
    """
    return E2_lcdm(z, Omega_m, Omega_r) + delta_E2(z, A, z_t, n)


def hubble_efc(z, A, z_t=1.01, n=6, H0=DEFAULT_H0,
               Omega_m=DEFAULT_OMEGA_M, Omega_r=DEFAULT_OMEGA_R):
    """
    EFC-modified Hubble parameter H(z) in km/s/Mpc.

    Parameters
    ----------
    z : float or array_like
        Redshift.
    A : float
        EFC background coupling amplitude.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    H0 : float
        Hubble constant [km/s/Mpc].
    Omega_m : float
        Matter density parameter.
    Omega_r : float
        Radiation density parameter.

    Returns
    -------
    float or ndarray
        H(z) in km/s/Mpc.
    """
    E2 = E2_efc(z, A, z_t, n, Omega_m, Omega_r)
    return H0 * np.sqrt(np.maximum(E2, 0.0))


def verify_sign_lemma(A, z_t=1.01, n=6, z_max=10.0, n_points=500):
    """
    Verify the sign lemma numerically: ΔE²(z) ≤ 0 for all z > 0.

    Parameters
    ----------
    A : float
        Coupling amplitude (must be > 0).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    z_max : float
        Maximum redshift to check.
    n_points : int
        Number of redshift points.

    Returns
    -------
    dict
        {"passed": bool, "max_delta_E2": float, "z_array": ndarray, "delta_E2_array": ndarray}
    """
    z_arr = np.linspace(1e-6, z_max, n_points)
    dE2 = delta_E2(z_arr, A, z_t, n)
    max_val = np.max(dE2)
    return {
        "passed": max_val <= 0,
        "max_delta_E2": max_val,
        "z_array": z_arr,
        "delta_E2_array": dE2,
    }
