"""
Scale-Localised Modified Gravity — Band-Pass Model Implementation.

Implements the stiffness response R(k,a), observables mu, eta, Sigma,
and the E_G forecast from DOI: 10.6084/m9.figshare.31985313.
"""

import numpy as np


# --- Fixed parameters ---
R_0 = 0.510           # Stiffness amplitude
K_C = 0.05            # Characteristic scale [h/Mpc]
F = 1.00005           # F = 1 + alpha * phi_bar
EPS_TOT = 0.40        # Slip amplitude (viable: 0.38-0.42)
OMEGA_M = 0.315       # Matter density parameter


def stiffness_response(k, a, R0=R_0, kc=K_C):
    """Band-pass stiffness response R(k,a) — Eq. 1."""
    x = k / kc
    return R0 * x**2 / (1 + x**2)**3 * a**4


def mu(k, z, R0=R_0, kc=K_C):
    """Effective gravitational coupling mu(k,z) — Eq. 2."""
    a = 1.0 / (1.0 + z)
    R = stiffness_response(k, a, R0, kc)
    return 1.0 / (F * (1.0 + R))


def eta(k, z, eps_tot=EPS_TOT, kc=K_C):
    """Gravitational slip eta(k,z) — Eq. 3."""
    a = 1.0 / (1.0 + z)
    x = k / kc
    return 1.0 + 2.0 * eps_tot * x**2 / (1.0 + x**2)**2 * a**2


def sigma(k, z, R0=R_0, kc=K_C, eps_tot=EPS_TOT):
    """Lensing combination Sigma(k,z) = mu*(1+eta)/2 — Eq. 4."""
    mu_val = mu(k, z, R0, kc)
    eta_val = eta(k, z, eps_tot, kc)
    return mu_val * (1.0 + eta_val) / 2.0


def E_G(k, z, f_z=None, omega_m=OMEGA_M, R0=R_0, kc=K_C, eps_tot=EPS_TOT):
    """E_G statistic — Eq. 5.

    Parameters
    ----------
    k : float or array
        Wavenumber [h/Mpc].
    z : float
        Redshift.
    f_z : float, optional
        Growth rate f(z). If None, uses LCDM approximation f ~ Omega_m(z)^0.55.
    """
    if f_z is None:
        a = 1.0 / (1.0 + z)
        E2 = omega_m * a**(-3) + (1.0 - omega_m)
        omega_m_z = omega_m * a**(-3) / E2
        f_z = omega_m_z**0.55

    sigma_val = sigma(k, z, R0, kc, eps_tot)
    mu_val = mu(k, z, R0, kc)
    return omega_m / f_z * sigma_val / mu_val


def E_G_GR(z, omega_m=OMEGA_M):
    """E_G in GR (scale-independent): Omega_m / f(z)."""
    a = 1.0 / (1.0 + z)
    E2 = omega_m * a**(-3) + (1.0 - omega_m)
    omega_m_z = omega_m * a**(-3) / E2
    f_z = omega_m_z**0.55
    return omega_m / f_z
