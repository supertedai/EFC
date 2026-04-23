"""A structural closure of growth-sector couplings – reference implementation.

Implements the three coupling classes (A, B, C) for the linear growth equation
as described in Magnusson (2026), DOI: 10.6084/m9.figshare.32084670.

Key equations:
  (1) LCDM growth ODE
  (2) Class A – multiplicative Geff / G
  (3) Class B – local friction
  (4) Class C – non-local (memory) friction
  (5) Background expansion E^2(a)
  (6) EG statistic
"""
from __future__ import annotations
import numpy as np
from scipy.integrate import solve_ivp
from typing import Tuple, Optional

# ── Physical constants from the paper ────────────────────────────────────────
C_GRID_AQUAL: float = 2.32          # Grid-AQUAL prefactor
OMEGA_M0: float = 0.3               # fiducial matter density parameter
A_T: float = 0.5                    # logistic gate transition scale factor
DELTA_A: float = 0.1                # logistic gate width
K_LAMBDA: float = 0.1               # Fourier low-pass screening scale [h/Mpc]
SIGMA8_FIDU: float = 0.811          # fiducial sigma_8


# ── Background expansion (Eq. 5) ────────────────────────────────────────────
def E2(a: float, Om: float = OMEGA_M0) -> float:
    """Squared Hubble rate normalised to H0: E^2(a) = Om a^{-3} + (1-Om)."""
    return Om * a**(-3) + (1.0 - Om)


def E(a: float, Om: float = OMEGA_M0) -> float:
    return np.sqrt(E2(a, Om))


def dE2_da(a: float, Om: float = OMEGA_M0) -> float:
    return -3.0 * Om * a**(-4)


def Eprime_over_E(a: float, Om: float = OMEGA_M0) -> float:
    """E'/E where prime = d/da."""
    return 0.5 * dE2_da(a, Om) / E2(a, Om)


# ── Gate functions ───────────────────────────────────────────────────────────
def logistic_gate(a: float, at: float = A_T, da: float = DELTA_A) -> float:
    """Logistic temporal gate g(a) (used in all three classes)."""
    return 1.0 / (1.0 + np.exp(-(a - at) / da))


def fourier_screen(k: float, kL: float = K_LAMBDA) -> float:
    """Low-pass Fourier screen s(k)."""
    return 1.0 / (1.0 + (k / kL)**2)


def memory_kernel(a: float, at: float = A_T, da: float = DELTA_A) -> float:
    """Integrated gate kernel G(a) = int_0^a g(a') da'  (Eq. 4)."""
    term1 = da * np.log(1.0 + np.exp((a - at) / da))
    term2 = da * np.log(1.0 + np.exp(-at / da))
    return term1 - term2


# ── Geff / G  (Eq. 2) ───────────────────────────────────────────────────────
def Geff_over_G(a: float, k: float = 0.0, C: float = C_GRID_AQUAL,
                at: float = A_T, da: float = DELTA_A,
                kL: float = K_LAMBDA) -> float:
    """Class A effective gravitational coupling ratio (Eq. 2)."""
    return 1.0 + (C**2 - 1.0) * logistic_gate(a, at, da) * fourier_screen(k, kL)


# ── EG statistic (Eq. 6) ─────────────────────────────────────────────────────
def EG_statistic(z: float, f: float, Sigma: float = 1.0,
                 Om0: float = OMEGA_M0) -> float:
    """EG(z) = Sigma(z) * Omega_{m,0} / f(z)   (Eq. 6)."""
    return Sigma * Om0 / f


# ── Growth ODE integrator ────────────────────────────────────────────────────
def growth_ode(a: float, y: np.ndarray, Om: float,
               coupling_class: str = 'LCDM',
               beta: float = 0.0, C: float = C_GRID_AQUAL,
               k: float = 0.0) -> list:
    """RHS of the growth ODE  delta''(a) for classes LCDM / A / B / C.

    State vector y = [delta, delta'] with prime = d/da.
    """
    delta, delta_p = y
    EpE = Eprime_over_E(a, Om)
    e2 = E2(a, Om)

    # Friction coefficient
    friction = 3.0 / a + EpE
    if coupling_class == 'B':
        friction += beta * logistic_gate(a) / a
    elif coupling_class == 'C':
        friction += beta * memory_kernel(a) / a

    # Source coefficient
    source_coeff = 1.5 * Om / (a**5 * e2)
    if coupling_class == 'A':
        source_coeff *= Geff_over_G(a, k, C)

    delta_pp = -friction * delta_p + source_coeff * delta
    return [delta_p, delta_pp]


def solve_growth(Om: float = OMEGA_M0, coupling_class: str = 'LCDM',
                 beta: float = 0.0, C: float = C_GRID_AQUAL,
                 k: float = 0.0,
                 a_span: Tuple[float, float] = (1e-3, 1.0),
                 n_eval: int = 500) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Solve linear growth ODE and return (a, D(a), f(a)).

    Returns arrays normalised so that D(a_initial) = a_initial (matter-dom IC).
    """
    a_eval = np.linspace(a_span[0], a_span[1], n_eval)
    a0 = a_span[0]
    y0 = [a0, 1.0]  # delta ~ a, delta' ~ 1 in matter domination

    sol = solve_ivp(growth_ode, a_span, y0, t_eval=a_eval, method='RK45',
                    args=(Om, coupling_class, beta, C, k),
                    rtol=1e-10, atol=1e-12)
    D = sol.y[0]
    Dp = sol.y[1]
    a_arr = sol.t
    f = a_arr * Dp / D  # f = d ln D / d ln a
    return a_arr, D, f


def fsigma8(Om: float = OMEGA_M0, sigma8: float = SIGMA8_FIDU,
            coupling_class: str = 'LCDM', beta: float = 0.0,
            C: float = C_GRID_AQUAL, k: float = 0.0,
            z_out: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
    """Compute f*sigma8(z) for a given coupling class."""
    a_arr, D, f = solve_growth(Om, coupling_class, beta, C, k)
    D_norm = D / D[-1]  # D(a=1)=1
    fs8 = f * sigma8 * D_norm
    z_arr = 1.0 / a_arr - 1.0
    if z_out is not None:
        fs8_interp = np.interp(z_out, z_arr[::-1], fs8[::-1])
        return z_out, fs8_interp
    return z_arr[::-1], fs8[::-1]


# ── Self-test ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    # Check memory kernel values stated in the paper (Section 2.1)
    G1 = memory_kernel(1.0);  G05 = memory_kernel(0.5);  G01 = memory_kernel(0.1)
    print(f'Memory kernel  G(1)={G1:.3f}  G(0.5)={G05:.4f}  G(0.1)={G01:.4f}')
    assert abs(G1 - 0.50) < 0.02, f'G(1) mismatch: {G1}'
    assert abs(G05 - 0.069) < 0.005, f'G(0.5) mismatch: {G05}'
    assert abs(G01 - 0.002) < 0.002, f'G(0.1) mismatch: {G01}'

    # Solve LCDM growth
    a, D, f = solve_growth()
    print(f'LCDM  D(1)={D[-1]:.4f}  f(1)={f[-1]:.4f}')

    # Class A with C=2.32, k=0
    a, D_A, f_A = solve_growth(coupling_class='A')
    print(f'Class A  D(1)={D_A[-1]:.4f}  f(1)={f_A[-1]:.4f}')

    # Class B with beta=0.5
    a, D_B, f_B = solve_growth(coupling_class='B', beta=0.5)
    print(f'Class B  D(1)={D_B[-1]:.4f}  f(1)={f_B[-1]:.4f}')

    # Class C with beta=0.5
    a, D_C, f_C = solve_growth(coupling_class='C', beta=0.5)
    print(f'Class C  D(1)={D_C[-1]:.4f}  f(1)={f_C[-1]:.4f}')

    # EG statistic
    eg = EG_statistic(z=0.3, f=f[-1])
    print(f'EG(z=0.3, Sigma=1) = {eg:.4f}')
    print('All self-tests passed.')
