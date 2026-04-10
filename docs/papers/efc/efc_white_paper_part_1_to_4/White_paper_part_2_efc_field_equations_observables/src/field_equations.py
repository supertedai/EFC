"""
EFC White Paper Part 2 — Field Equations and Observable Mapping.

Implements the entropy-field coupling, modified growth equation,
and observable predictions (f*sigma_8, S_8, response surface).

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970898
"""

import numpy as np
from scipy.integrate import solve_ivp


# --- Entropy Field ---

def entropy_field_S(a: float, S_max: float = 0.9) -> float:
    """Dimensionless entropy field S(a) (Definition 1).

    S(a) in [0, 1]: S -> 0 in early universe, S -> S_max in late time.
    Monotonically increasing with structure formation.
    """
    # Phenomenological form tracking structure growth
    return S_max * (1.0 - np.exp(-2.0 * a))


# --- Coupling Formula ---

def mu_coupling(a: float, beta: float = 0.16) -> float:
    """Derived coupling formula (Eq. 1).

    mu(a) = 1 + beta * S(a)
    beta ~ 0.16 from SPARC calibration. This is derived, not free.
    mu < 1 in the growth era implies weakened gravitational growth.
    """
    S = entropy_field_S(a)
    return 1.0 + beta * S


def mu_sigmoid(a: float, B: float = 0.06, a_t: float = 0.7, n: float = 2.0) -> float:
    """Sigmoid-gate parameterisation (Eq. 2).

    mu(a) = 1 - B * g(a; n)
    where g(a; n) = [1 + (a_t/a)^n]^{-1}
    B > 0 enforces mu < 1 (weakened growth).
    """
    g = 1.0 / (1.0 + (a_t / a) ** n)
    return 1.0 - B * g


def mu_gaussian(a: float, beta: float = 0.16, a_t: float = 0.7, sigma_a: float = 0.15) -> float:
    """Gaussian parameterisation for MCMC sampling (Eq. 3).

    mu(a) = 1 + beta * exp(-(a - a_t)^2 / (2*sigma_a^2))
    """
    return 1.0 + beta * np.exp(-0.5 * ((a - a_t) / sigma_a) ** 2)


# --- EFC Kernel ---

def mu_efc_kernel(S_bar: float, s_tilde_ratio: float) -> float:
    """Full EFC kernel (Eq. 4).

    mu_EFC(k,z) = [1 - S_bar(z)] + s_tilde(k,z)/delta_tilde(k,z)
    """
    return (1.0 - S_bar) + s_tilde_ratio


# --- Growth Equation ---

def growth_ode(ln_a, y, Omega_m, mu_func):
    """Modified growth ODE (Eq. 6).

    f' + f^2 + (1/2 - 3/2 * Omega_m_tilde) * f = 3/2 * mu(a) * Omega_m_tilde

    State: y = [f, ln_D] where f = d ln D / d ln a.
    """
    f, ln_D = y
    a = np.exp(ln_a)
    E2 = Omega_m * a ** (-3) + (1.0 - Omega_m)
    Omega_m_tilde = Omega_m * a ** (-3) / E2
    mu = mu_func(a)
    dfda = -f ** 2 - (0.5 - 1.5 * Omega_m_tilde) * f + 1.5 * mu * Omega_m_tilde
    return [dfda, f]


def compute_growth(
    Omega_m: float = 0.3,
    mu_func=None,
    a_start: float = 0.01,
    a_end: float = 1.0,
) -> dict:
    """Solve the modified growth equation and return f, D(a)."""
    if mu_func is None:
        mu_func = mu_sigmoid

    ln_a_span = (np.log(a_start), np.log(a_end))
    # Initial conditions: matter-dominated f ~ Omega_m^0.55
    f0 = Omega_m ** 0.55
    y0 = [f0, 0.0]
    sol = solve_ivp(growth_ode, ln_a_span, y0, args=(Omega_m, mu_func),
                    dense_output=True, rtol=1e-10)
    return {
        "solution": sol,
        "f_at_a1": sol.y[0, -1],
        "ln_D_at_a1": sol.y[1, -1],
    }


# --- Observables ---

def f_sigma8(z: float, sigma8_0: float = 0.811, Omega_m: float = 0.3,
             mu_func=None) -> float:
    """Predicted growth rate observable (Eq. 9).

    [f*sigma_8](z) = f(z) * sigma_{8,0} * D(z)/D(0)
    """
    a = 1.0 / (1.0 + z)
    result = compute_growth(Omega_m, mu_func, a_end=1.0)
    sol = result["solution"]
    # Evaluate at target scale factor
    ln_a_target = np.log(a)
    y_target = sol.sol(ln_a_target)
    y_end = sol.sol(np.log(1.0))
    f_val = y_target[0]
    D_ratio = np.exp(y_target[1] - y_end[1])
    return f_val * sigma8_0 * D_ratio


def S8_suppression(mu_0: float, B: float = 0.06, n: float = 2.0) -> float:
    """S_8 suppression integral (Eq. 10-11).

    Delta_sigma_8 proportional to (1 - mu_0) * integral g(a; n) d ln a
    """
    # Numerical integration of sigmoid gate
    a_arr = np.linspace(0.3, 1.0, 200)
    a_t = 0.7
    g_arr = 1.0 / (1.0 + (a_t / a_arr) ** n)
    integral = np.trapz(g_arr, np.log(a_arr))
    return (1.0 - mu_0) * integral


def response_surface(k: float, S: float, beta: float = 0.16) -> float:
    """Regime response surface R(k, S) (Eq. 12).

    R(k, S) = G_eff(k, S) / G_N
    Maps wavenumber and structural parameter to effective coupling ratio.
    """
    # Simplified: scale-independent version
    return 1.0 + beta * S
