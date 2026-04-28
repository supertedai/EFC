"""efc_redshift_decomposition.py

Reference implementation of the three-window redshift decomposition
from Energy-Flow Cosmology (EFC).

Paper: A Three-Window Decomposition of Cosmological Redshift in EFC
DOI:   10.6084/m9.figshare.32113399
Author: Morten Magnusson (re-implementation)

Key equations
-------------
Eq (1)  ln(1+z_obs) = integral_gamma F(alpha, S_eff, k^mu nabla_mu S_eff) dlambda
Eq (2)  S_eff = P_xi(S_flow, S_latent)
Eq (3)  S_eff ~ S_flow + xi * S_latent   (first-order additive projection)
Table 1 regime projections:
    a_H0 = a_G / 2      (Hubble / Friedmann)
    a_c  = a_G / 4      (photon propagation / Core Lock)
    g/a0 ~ 5            (galactic acceleration, SPARC, open)
    C_eff = k^2 / a_G   (perturbation amplitude)
"""

from __future__ import annotations
import numpy as np
from typing import Callable, Optional, Tuple

# ---------------------------------------------------------------------------
# Fundamental EFC scale (Table 1)
# ---------------------------------------------------------------------------
A_G: float = 0.1  # gravitational coupling coefficient (~0.1)

# Regime-specific projections (Table 1, exact rational fractions)
A_H0: float = A_G / 2.0   # Hubble structure
A_C: float = A_G / 4.0    # photon propagation (Core Lock)
MOND_RATIO: float = 5.0   # g/a0 ratio (open tension, ~5x discrepancy)


# ---------------------------------------------------------------------------
# Eq (3): Effective entropy field  (first-order additive projection)
# ---------------------------------------------------------------------------
def s_eff(
    s_flow: np.ndarray,
    s_latent: np.ndarray,
    xi: float = 0.0,
) -> np.ndarray:
    """Effective entropy field along the photon path.

    Parameters
    ----------
    s_flow : array  – cosmological entropy field (L0-L1)
    s_latent : array – perturbation-sector entropy (L2-L3)
    xi : float – screening parameter (0 = unscreened cosmological regime)

    Returns
    -------
    S_eff : array
    """
    return s_flow + xi * s_latent


# ---------------------------------------------------------------------------
# Integrand F  (dimensionless scalar functional)
# ---------------------------------------------------------------------------
def integrand_F(
    alpha: np.ndarray,
    seff: np.ndarray,
    k_grad_seff: np.ndarray,
    a_g: float = A_G,
) -> np.ndarray:
    """Dimensionless integrand F(alpha, S_eff, k^mu nabla_mu S_eff).

    In the LCDM limit grad S_eff -> 0 the integrand reduces to
    d ln(a)/dlambda, i.e. standard metric redshift.  The leading
    EFC correction is proportional to a_c = a_G/4 times the
    directional derivative of S_eff (Core-Lock sector).

    Parameters
    ----------
    alpha, seff, k_grad_seff : arrays of equal shape
    a_g : float – underlying structural scale

    Returns
    -------
    F : array  (dimensionless)
    """
    a_c = a_g / 4.0
    # LCDM baseline: alpha acts as d ln a / dlambda
    # EFC correction: a_c * k^mu nabla_mu S_eff
    return alpha + a_c * k_grad_seff


# ---------------------------------------------------------------------------
# Eq (1): Line-integral redshift along a null geodesic
# ---------------------------------------------------------------------------
def redshift_integral(
    lam: np.ndarray,
    alpha: np.ndarray,
    seff: np.ndarray,
    k_grad_seff: np.ndarray,
    a_g: float = A_G,
) -> float:
    """Evaluate ln(1+z_obs) via trapezoidal integration of Eq (1).

    Parameters
    ----------
    lam : 1-d array – affine parameter values along gamma
    alpha, seff, k_grad_seff : 1-d arrays (same length as lam)
    a_g : float

    Returns
    -------
    ln_one_plus_z : float
    """
    f_vals = integrand_F(alpha, seff, k_grad_seff, a_g)
    return float(np.trapz(f_vals, lam))


# ---------------------------------------------------------------------------
# LCDM limit:  grad S_eff -> 0
# ---------------------------------------------------------------------------
def redshift_lcdm(
    a_emit: float,
    a_obs: float = 1.0,
) -> float:
    """Standard LCDM redshift  1+z = a_obs / a_emit."""
    return a_obs / a_emit - 1.0


# ---------------------------------------------------------------------------
# Window 1 – Thermal:  T_CMB(z) scaling
# ---------------------------------------------------------------------------
def t_cmb_efc(
    z: np.ndarray,
    t0: float = 2.7255,
    a_g: float = A_G,
    delta_s: float = 0.0,
) -> np.ndarray:
    """CMB temperature as a function of redshift in EFC.

    In LCDM: T(z) = T0 (1+z).  The EFC thermal window introduces
    a correction from partial_S F, parameterised here to leading order
    as  T(z) = T0 (1+z) [1 + (a_G/4) delta_S ln(1+z)].

    delta_s = 0 recovers LCDM.
    """
    z = np.asarray(z, dtype=float)
    correction = 1.0 + (a_g / 4.0) * delta_s * np.log1p(z)
    return t0 * (1.0 + z) * correction


# ---------------------------------------------------------------------------
# Window 2 – Geometric:  CDDR  eta(z)
# ---------------------------------------------------------------------------
def cddr_eta(
    z: np.ndarray,
    a_g: float = A_G,
    epsilon: float = 0.0,
    beta: float = 0.0,
) -> np.ndarray:
    """Cosmic Distance Duality Ratio eta(z) in EFC.

    eta = d_L / [ d_A (1+z)^2 ].  LCDM => eta=1.
    EFC correction via c_eff(a) parameterisation:
        eta(z) = 1 + epsilon * (a_G/2) * (1+z)^beta - 1) / beta
    with beta anchored to BAO+RSD.  epsilon=0 or beta=0 => LCDM.
    """
    z = np.asarray(z, dtype=float)
    if abs(beta) < 1e-12:
        return np.ones_like(z)
    a_h0 = a_g / 2.0
    return 1.0 + epsilon * a_h0 * ((1.0 + z) ** beta - 1.0) / beta


# ---------------------------------------------------------------------------
# Window 3 – Structural:  S(z) single-parameter consistency
# ---------------------------------------------------------------------------
def s_z_consistency(
    z: np.ndarray,
    a_g: float = A_G,
    s0: float = 1.0,
) -> np.ndarray:
    """Entropy profile S(z) used for JWST <-> CMB structural consistency.

    Leading-order model: S(z) = s0 / (1 + a_G * z) which flattens
    relative to LCDM at high z, producing the tension-relieving
    early-galaxy abundance.
    """
    z = np.asarray(z, dtype=float)
    return s0 / (1.0 + a_g * z)


# ---------------------------------------------------------------------------
# Perturbation amplitude convenience
# ---------------------------------------------------------------------------
def c_eff(k: np.ndarray, a_g: float = A_G) -> np.ndarray:
    """Effective perturbation coefficient C_eff = k^2 / a_G  (Table 1)."""
    return np.asarray(k, dtype=float) ** 2 / a_g


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=== EFC Redshift Decomposition – self-test ===")
    # 1. Regime projections
    assert np.isclose(A_H0, 0.05), f"a_H0 = {A_H0}"
    assert np.isclose(A_C, 0.025), f"a_c  = {A_C}"
    print(f"a_G  = {A_G}")
    print(f"a_H0 = {A_H0}  (a_G/2)")
    print(f"a_c  = {A_C}  (a_G/4)")

    # 2. LCDM limit of integral
    N = 500
    a_e, a_o = 0.5, 1.0
    lam = np.linspace(0, 1, N)
    alpha = np.full(N, np.log(a_o / a_e))  # constant integrand
    seff_arr = np.ones(N)
    grad_zero = np.zeros(N)
    ln1z = redshift_integral(lam, alpha, seff_arr, grad_zero)
    z_efc = np.exp(ln1z) - 1.0
    z_lcdm = redshift_lcdm(a_e, a_o)
    assert np.isclose(z_efc, z_lcdm, atol=1e-6), f"{z_efc} vs {z_lcdm}"
    print(f"LCDM limit check: z_EFC={z_efc:.6f}, z_LCDM={z_lcdm:.6f}  OK")

    # 3. T_CMB window
    z_test = np.array([0, 1, 2, 3])
    t_lcdm = 2.7255 * (1 + z_test)
    t_efc = t_cmb_efc(z_test, delta_s=0.0)
    assert np.allclose(t_lcdm, t_efc)
    print(f"T_CMB LCDM limit: {t_efc}  OK")

    # 4. CDDR window
    eta_lcdm = cddr_eta(z_test, epsilon=0.0)
    assert np.allclose(eta_lcdm, 1.0)
    print(f"CDDR LCDM limit: eta={eta_lcdm}  OK")

    print("\nAll self-tests passed.")
