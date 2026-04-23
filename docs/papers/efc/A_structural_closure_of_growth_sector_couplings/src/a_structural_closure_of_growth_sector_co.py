"""A structural closure of growth-sector couplings — reference implementation.

Implements the three coupling classes (A, B, C) modifying the linear growth
equation, background expansion, observables f*sigma8, and the E_G statistic
as described in Magnusson (2026).

Module: a_structural_closure_of_growth_sector_co.py
"""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Constants from the paper
# ---------------------------------------------------------------------------
C_EFC: float = 2.32          # Grid-AQUAL prefactor
A_T: float = 0.5             # logistic gate centre (scale factor)
DELTA_A: float = 0.1         # logistic gate width
K_LAMBDA: float = 0.1        # Fourier low-pass screen scale [h/Mpc]
SIGMA8_FID: float = 0.811    # Planck 2018 fiducial sigma8
OMEGA_M_FID: float = 0.315   # Planck 2018 fiducial Omega_m
H0_FID: float = 67.4         # Planck 2018 fiducial H0 [km/s/Mpc]

# ---------------------------------------------------------------------------
# Background expansion  (Eq. 5)
# ---------------------------------------------------------------------------

def E_squared(a: float, Omega_m: float = OMEGA_M_FID) -> float:
    """E^2(a) = H(a)^2 / H0^2 for flat LCDM (Eq. 5)."""
    return Omega_m * a**-3 + (1.0 - Omega_m)


def E(a: float, Omega_m: float = OMEGA_M_FID) -> float:
    return np.sqrt(E_squared(a, Omega_m))


def dE_da(a: float, Omega_m: float = OMEGA_M_FID) -> float:
    """dE/da via analytic derivative of E^2."""
    E2 = E_squared(a, Omega_m)
    dE2 = -3.0 * Omega_m * a**-4
    return 0.5 * dE2 / np.sqrt(E2)


def E_prime_over_E(a: float, Omega_m: float = OMEGA_M_FID) -> float:
    """E'/E where prime = d/da."""
    return dE_da(a, Omega_m) / E(a, Omega_m)


# ---------------------------------------------------------------------------
# Gate functions (Section 2.1)
# ---------------------------------------------------------------------------

def logistic_gate(a: float, at: float = A_T, da: float = DELTA_A) -> float:
    """g(a) logistic temporal gate."""
    x = (a - at) / da
    return 1.0 / (1.0 + np.exp(-x))


def fourier_screen(k: float, k_lam: float = K_LAMBDA) -> float:
    """s(k) low-pass Fourier screen."""
    return 1.0 / (1.0 + (k / k_lam)**2)


def accumulated_gate(a: float, at: float = A_T, da: float = DELTA_A) -> float:
    """G(a) = integral_0^a g(a') da'  (Eq. 4)."""
    term1 = da * np.log(1.0 + np.exp((a - at) / da))
    term2 = da * np.log(1.0 + np.exp(-at / da))
    return term1 - term2


# ---------------------------------------------------------------------------
# Geff / G  (Eq. 2) — Class A
# ---------------------------------------------------------------------------

def Geff_over_G(a: float, k: float, C: float = C_EFC,
                at: float = A_T, da: float = DELTA_A,
                k_lam: float = K_LAMBDA) -> float:
    """Effective gravitational coupling ratio (Eq. 2)."""
    return 1.0 + (C**2 - 1.0) * logistic_gate(a, at, da) * fourier_screen(k, k_lam)


# ---------------------------------------------------------------------------
# Growth ODE solver
# ---------------------------------------------------------------------------

def growth_ode(a: float, y: np.ndarray, Omega_m: float,
               coupling: str = 'LCDM', beta: float = 0.0,
               k: float = 0.01, C: float = C_EFC) -> np.ndarray:
    """RHS of d/da [delta, delta'] for the three coupling classes + LCDM.

    y = [delta, delta']  where prime = d/da.
    Implements Eqs. (1), (2), (3) and the Class C variant.
    """
    delta, delta_p = y
    Ep_over_E = E_prime_over_E(a, Omega_m)
    E2 = E_squared(a, Omega_m)

    # friction coefficient (Eq. 1 baseline)
    friction = 3.0 / a + Ep_over_E

    # source coefficient (Eq. 1 baseline)
    source_coeff = 1.5 * Omega_m / (a**5 * E2)

    if coupling == 'A':
        source_coeff *= Geff_over_G(a, k, C)
    elif coupling == 'B':
        friction += beta * logistic_gate(a) / a
    elif coupling == 'C':
        friction += beta * accumulated_gate(a) / a
    # else: LCDM — no modifications

    delta_pp = -friction * delta_p + source_coeff * delta
    return np.array([delta_p, delta_pp])


def solve_growth(Omega_m: float = OMEGA_M_FID, coupling: str = 'LCDM',
                 beta: float = 0.0, k: float = 0.01,
                 C: float = C_EFC,
                 a_span: Tuple[float, float] = (1e-3, 1.0),
                 n_eval: int = 500) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Integrate the linear growth ODE and return (a, D, f).

    Returns
    -------
    a_arr : scale factor array
    D_arr : growth factor D(a) normalised so D(a_i) = a_i (matter-dom IC)
    f_arr : growth rate f = d ln D / d ln a
    """
    a_eval = np.linspace(a_span[0], a_span[1], n_eval)
    a_i = a_span[0]
    y0 = [a_i, 1.0]  # delta = a, delta' = 1 in matter domination

    sol = solve_ivp(growth_ode, a_span, y0, t_eval=a_eval, rtol=1e-10,
                    atol=1e-12, args=(Omega_m, coupling, beta, k, C),
                    method='DOP853')
    D = sol.y[0]
    Dp = sol.y[1]
    a_arr = sol.t
    f_arr = a_arr * Dp / D  # f = a delta'/delta = d ln D / d ln a
    return a_arr, D, f_arr


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------

def fsigma8(a_arr: np.ndarray, D_arr: np.ndarray, f_arr: np.ndarray,
           sigma8: float = SIGMA8_FID) -> np.ndarray:
    """f*sigma8(z) = f(a) * sigma8 * D(a)/D(1)."""
    D_today = np.interp(1.0, a_arr, D_arr)
    return f_arr * sigma8 * D_arr / D_today


def EG_statistic(z: float, f_z: float, Omega_m: float = OMEGA_M_FID,
                 Sigma: float = 1.0) -> float:
    """E_G(z) = Sigma * Omega_{m,0} / f(z)  (Eq. 6)."""
    return Sigma * Omega_m / f_z


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('=== Self-test: growth-sector coupling module ===')
    # Check accumulated gate values from paper
    for a_val, expected in [(1.0, 0.50), (0.5, 0.069), (0.1, 0.002)]:
        G_val = accumulated_gate(a_val)
        print(f'  G({a_val:.1f}) = {G_val:.4f}  (paper: ~{expected})')
        assert abs(G_val - expected) < 0.01, f'Gate mismatch at a={a_val}'

    # Solve LCDM growth
    a, D, f = solve_growth()
    fs8 = fsigma8(a, D, f)
    z_arr = 1.0 / a - 1.0
    idx05 = np.argmin(np.abs(z_arr - 0.5))
    print(f'  LCDM f*sigma8(z=0.5) = {fs8[idx05]:.4f}')

    # Geff/G at a=1, k=0.01
    ratio = Geff_over_G(1.0, 0.01)
    print(f'  Geff/G(a=1, k=0.01) = {ratio:.4f}  (C={C_EFC})')

    # E_G at z=0.3
    f_03 = np.interp(1.0 / 1.3, a, f)
    eg = EG_statistic(0.3, f_03)
    print(f'  E_G(z=0.3, Sigma=1) = {eg:.4f}')

    print('All self-tests passed.')
