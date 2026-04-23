"""A structural closure of growth-sector couplings — reference implementation.

Implements the three coupling classes (A, B, C) for modifying the linear
growth equation, plus background cosmology and observables described in
Magnusson (2026), DOI: 10.6084/m9.figshare.32084670.

Module: a_structural_closure_of_growth_sector_co.py
"""
import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Constants from the paper
# ---------------------------------------------------------------------------
C_EFC: float = 2.32          # Grid-AQUAL discrete-gravity prefactor
OMEGA_M0: float = 0.295      # Fiducial matter density parameter
H0: float = 67.36            # Fiducial Hubble constant [km/s/Mpc]
AT: float = 0.5              # Logistic gate transition scale factor
DELTA_A: float = 0.1         # Logistic gate width
K_LAMBDA: float = 0.2        # Fourier screening scale [h/Mpc]
SIGMA_EFC: float = 1.0       # Sigma = 1 assumption for EG statistic


# ---------------------------------------------------------------------------
# Background expansion  (flat LCDM, Eq. 5)
# ---------------------------------------------------------------------------
def E2(a: float, Om: float = OMEGA_M0) -> float:
    """E^2(a) = H^2(a)/H0^2  for flat LCDM."""
    return Om * a**(-3) + (1.0 - Om)


def E(a: float, Om: float = OMEGA_M0) -> float:
    return np.sqrt(E2(a, Om))


def dE2_da(a: float, Om: float = OMEGA_M0) -> float:
    return -3.0 * Om * a**(-4)


def Eprime_over_E(a: float, Om: float = OMEGA_M0) -> float:
    """E'(a)/E(a) where prime = d/da."""
    return 0.5 * dE2_da(a, Om) / E2(a, Om)


# ---------------------------------------------------------------------------
# Gate functions  (Sec. 2.1)
# ---------------------------------------------------------------------------
def gate_g(a: float, at: float = AT, da: float = DELTA_A) -> float:
    """Logistic gate g(a) — Eq. below (2)."""
    x = (a - at) / da
    return 1.0 / (1.0 + np.exp(-x))


def screen_s(k: float, kL: float = K_LAMBDA) -> float:
    """Low-pass Fourier screen s(k) — Eq. (2)."""
    return 1.0 / (1.0 + (k / kL) ** 2)


def gate_G_integrated(a: float, at: float = AT, da: float = DELTA_A) -> float:
    """Integrated (memory) gate kernel G(a) — Eq. (4)."""
    t1 = np.log(1.0 + np.exp((a - at) / da))
    t0 = np.log(1.0 + np.exp(-at / da))
    return da * (t1 - t0)


# ---------------------------------------------------------------------------
# Geff / G  (Class A, Eq. 2)
# ---------------------------------------------------------------------------
def Geff_over_G(a: float, k: float = 0.0,
                C: float = C_EFC, at: float = AT,
                da: float = DELTA_A, kL: float = K_LAMBDA) -> float:
    """Effective gravitational coupling ratio — Eq. (2)."""
    return 1.0 + (C**2 - 1.0) * gate_g(a, at, da) * screen_s(k, kL)


# ---------------------------------------------------------------------------
# Growth ODE solver  (supports Classes A, B, C)
# ---------------------------------------------------------------------------
def growth_ode(a: float, y: np.ndarray, Om: float,
               coupling: str = 'LCDM', beta: float = 0.0,
               C: float = C_EFC, k: float = 0.0) -> np.ndarray:
    """RHS of the linear growth ODE in d/da form.

    y = [delta, delta'] where prime = d/da.
    coupling in {'LCDM', 'A', 'B', 'C'}.
    """
    delta, deltap = y
    EpE = Eprime_over_E(a, Om)
    coeff_friction = 3.0 / a + EpE
    source_factor = 1.0

    if coupling == 'A':
        source_factor = Geff_over_G(a, k, C)
    elif coupling == 'B':
        coeff_friction += beta * gate_g(a) / a
    elif coupling == 'C':
        coeff_friction += beta * gate_G_integrated(a) / a

    source = 1.5 * Om / (a**5 * E2(a, Om)) * source_factor
    deltapp = -coeff_friction * deltap + source * delta
    return np.array([deltap, deltapp])


def solve_growth(Om: float = OMEGA_M0, coupling: str = 'LCDM',
                 beta: float = 0.0, C: float = C_EFC, k: float = 0.0,
                 a_span: Tuple[float, float] = (1e-3, 1.0),
                 n_eval: int = 500) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve the growth equation, return (a_arr, D(a), f(a)).

    D is normalised so that D(a_init) = a_init  (matter-dominated IC).
    f = d ln D / d ln a.
    """
    ai, af = a_span
    y0 = [ai, 1.0]  # delta = a, delta' = 1 in matter domination
    a_eval = np.linspace(ai, af, n_eval)

    sol = solve_ivp(growth_ode, a_span, y0, t_eval=a_eval, method='RK45',
                    args=(Om, coupling, beta, C, k), rtol=1e-10, atol=1e-12)
    D = sol.y[0]
    Dp = sol.y[1]
    f = sol.t * Dp / D  # f = a delta'/delta = d ln D / d ln a
    return sol.t, D, f


# ---------------------------------------------------------------------------
# Observables
# ---------------------------------------------------------------------------
def fsigma8(a_arr: np.ndarray, D_arr: np.ndarray, f_arr: np.ndarray,
           sigma8_0: float = 0.811) -> np.ndarray:
    """f sigma_8(z) = f(a) * sigma8 * D(a)/D(1)."""
    D_norm = D_arr / D_arr[-1]
    return f_arr * sigma8_0 * D_norm


def EG_statistic(z: float, f_z: float, Om0: float = OMEGA_M0,
                 Sigma: float = SIGMA_EFC) -> float:
    """EG(z) = Sigma * Omega_m0 / f(z)  — Eq. (6)."""
    return Sigma * Om0 / f_z


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    print('=== Self-test: a_structural_closure_of_growth_sector_co ===')

    # LCDM growth
    a, D, f = solve_growth()
    fs8 = fsigma8(a, D, f)
    print(f'LCDM  f*sigma8(z=0) = {fs8[-1]:.4f},  f(z=0) = {f[-1]:.4f}')

    # Class A
    aA, DA, fA = solve_growth(coupling='A', k=0.1)
    fs8A = fsigma8(aA, DA, fA)
    print(f'ClassA f*sigma8(z=0) = {fs8A[-1]:.4f},  f(z=0) = {fA[-1]:.4f}')

    # Class B  beta=0.5
    aB, DB, fB = solve_growth(coupling='B', beta=0.5)
    fs8B = fsigma8(aB, DB, fB)
    print(f'ClassB f*sigma8(z=0) = {fs8B[-1]:.4f},  f(z=0) = {fB[-1]:.4f}')

    # Class C  beta=0.5
    aC, DC, fC = solve_growth(coupling='C', beta=0.5)
    fs8C = fsigma8(aC, DC, fC)
    print(f'ClassC f*sigma8(z=0) = {fs8C[-1]:.4f},  f(z=0) = {fC[-1]:.4f}')

    # Gate checks from paper
    print(f'\nGate checks (at=0.5, da=0.1):')
    print(f'  G(1.0) = {gate_G_integrated(1.0):.3f}   (paper: ~0.50)')
    print(f'  G(0.5) = {gate_G_integrated(0.5):.4f}  (paper: ~0.069)')
    print(f'  G(0.1) = {gate_G_integrated(0.1):.4f}  (paper: ~0.002)')
    g05 = gate_g(0.5)
    G05 = gate_G_integrated(0.5)
    print(f'  g/G at a=0.5: {g05/G05:.1f}  (paper: ~7)')
    g1 = gate_g(1.0)
    G1 = gate_G_integrated(1.0)
    print(f'  g/G at a=1.0: {g1/G1:.1f}  (paper: ~2)')

    # EG statistic check
    eg = EG_statistic(0.0, f[-1])
    print(f'\nEG(z=0) = {eg:.4f}  (Sigma=1)')
    print('=== Self-test complete ===')
