"""
EFC White Paper Part 1 — Recovery Conditions and the LCDM Limit.

Implements the three recovery conditions (Theorems 1-3) and the
regime-transition function Theta(z).

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970886
"""

import numpy as np


def theta_z(z: float, z_L1L2: float = 1.0, delta_z: float = 0.3) -> float:
    """Regime-transition function (Eq. 2).

    Theta(z) -> 1 in late-time structure-dominated regime (L2).
    Theta(z) -> 0 at high redshift (L0/L1), ensuring CMB safety.
    """
    return 0.5 * (1.0 + np.tanh((z_L1L2 - z) / delta_z))


def sigmoid_gate(a: float, a_t: float = 0.7, n: float = 2.0) -> float:
    """Sigmoid gate function g(a; n) (below Eq. 3).

    g(a; n) = [1 + (a_t/a)^n]^{-1}
    """
    return 1.0 / (1.0 + (a_t / a) ** n)


def mu_efc_parametric(
    a: float,
    B: float = 0.06,
    a_t: float = 0.7,
    n: float = 2.0,
) -> float:
    """Modified gravitational coupling mu(a) (Eq. 3).

    mu = 1 - B * g(a; n)
    In the limit B -> 0 (or equivalently alpha_L2 -> 0), mu -> 1.
    """
    return 1.0 - B * sigmoid_gate(a, a_t, n)


def mu_efc_kernel(
    S_bar: float,
    s_tilde_over_delta: float,
) -> float:
    """Full EFC kernel mu_EFC(k,z) (Eq. 5).

    mu_EFC = (1 - S_bar) + s_tilde/delta_tilde
    In the limit S_bar -> 0 and s_tilde -> 0, mu_EFC -> 1 (GR).
    """
    return (1.0 - S_bar) + s_tilde_over_delta


def theta_density(rho: float, rho_crit: float = 1e3) -> float:
    """Density-saturation screening function Theta(rho).

    Theta(rho) -> 0 when rho >> rho_crit (chameleon-type screening).
    This ensures G_eff -> G_N in high-density environments.
    """
    return 1.0 / (1.0 + (rho / rho_crit) ** 2)


def check_condition_I(alpha_L2: float, tol: float = 1e-10) -> dict:
    """Theorem 1: Parameter recovery.

    If alpha_L2 -> 0, EFC reduces to LCDM in the perturbation sector.
    """
    mu = 1.0  # alpha_L2 = 0 implies no correction
    sigma = 1.0
    recovered = abs(alpha_L2) < tol
    return {
        "condition": "I",
        "alpha_L2": alpha_L2,
        "mu": mu if recovered else 1.0 + alpha_L2,
        "sigma": sigma if recovered else 1.0 + alpha_L2,
        "recovered": recovered,
    }


def check_condition_II(S: float, S_c: float = 0.1) -> dict:
    """Theorem 2: Entropy recovery.

    If S < S_c, all EFC corrections vanish and GR is recovered.
    """
    recovered = S < S_c
    mu = 1.0 if recovered else mu_efc_kernel(S, 0.0)
    return {
        "condition": "II",
        "S": S,
        "S_c": S_c,
        "mu": mu,
        "sigma": 1.0 if recovered else mu,
        "recovered": recovered,
    }


def check_condition_III(rho: float, rho_crit: float = 1e3) -> dict:
    """Theorem 3: Density recovery.

    If rho >> rho_crit, Theta(rho) -> 0 and G_eff -> G_N.
    """
    theta = theta_density(rho, rho_crit)
    recovered = theta < 1e-6
    return {
        "condition": "III",
        "rho": rho,
        "rho_crit": rho_crit,
        "theta_rho": theta,
        "G_eff_over_G_N": 1.0 + theta * 0.06,  # illustrative
        "recovered": recovered,
    }


def background_expansion(z: float, alpha_L2: float, Omega_m: float = 0.3) -> float:
    """Modified Friedmann equation E^2(z) (Eq. 1).

    E^2(z) = E^2_LCDM(z) * [1 + alpha_L2 * f(z) * Theta(z)]
    Note: background alpha-gate is COLLAPSED — inconsistent with CMB+BAO.
    This function is included for reference only.
    """
    E2_lcdm = Omega_m * (1 + z) ** 3 + (1.0 - Omega_m)
    f_z = 1.0  # placeholder
    Theta = theta_z(z)
    return E2_lcdm * (1.0 + alpha_L2 * f_z * Theta)
