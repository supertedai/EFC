"""
EFC Growth Equation Solver
===========================

Solves the modified linear growth ODE with μ(a) ≠ 1 and
optionally modified background H(z).

Growth equation:
    f' + f² + (1/2 − 3/2 Ω̃_m) f = 3/2 μ(a) Ω̃_m

where f = d ln D / d ln a and Ω̃_m(a) = Ω_m a^{-3} / E²(a).

References:
    DOI: 10.6084/m9.figshare.31333414 (Technical Note I)
    DOI: 10.6084/m9.figshare.31333600 (Technical Note II)
"""

import numpy as np
from .background import E2_lcdm, E2_efc, DEFAULT_OMEGA_M, DEFAULT_H0
from .mu import mu_of_a


DEFAULT_SIGMA8_LCDM = 0.811


def _omega_m_tilde(a, E2_val, Omega_m=DEFAULT_OMEGA_M):
    """Effective matter fraction Ω̃_m(a) = Ω_m a^{-3} / E²(a)."""
    return Omega_m * a**(-3) / E2_val


def growth_ode(ln_a, f, Omega_m=DEFAULT_OMEGA_M, A=0.0, B=0.0,
               z_t=1.01, n=6):
    """
    Right-hand side of the growth rate ODE: df/d(ln a).

    f' = −f² − (1/2 − 3/2 Ω̃_m) f + 3/2 μ(a) Ω̃_m

    Parameters
    ----------
    ln_a : float
        Natural log of scale factor.
    f : float
        Growth rate f = d ln D / d ln a.
    Omega_m : float
        Matter density parameter.
    A : float
        Background gate amplitude (0 for pure μ-model).
    B : float
        Perturbation amplitude.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.

    Returns
    -------
    float
        df / d(ln a).
    """
    a = np.exp(ln_a)
    z = 1.0 / a - 1.0

    if A != 0:
        E2_val = E2_efc(z, A, z_t, n, Omega_m)
    else:
        E2_val = E2_lcdm(z, Omega_m)

    E2_val = max(E2_val, 1e-30)
    Om_tilde = _omega_m_tilde(a, E2_val, Omega_m)
    mu = mu_of_a(a, B, z_t=z_t, n=n) if B != 0 else 1.0

    return -f**2 - (0.5 - 1.5 * Om_tilde) * f + 1.5 * mu * Om_tilde


def solve_growth(Omega_m=DEFAULT_OMEGA_M, A=0.0, B=0.0, z_t=1.01, n=6,
                 z_init=50.0, n_points=2000):
    """
    Solve the growth equation from z_init to z=0.

    Uses a simple RK4 integrator. Initial condition: f ≈ Ω_m(z_init)^0.55
    (matter-dominated approximation).

    Parameters
    ----------
    Omega_m : float
        Matter density parameter.
    A : float
        Background gate amplitude (0 for ΛCDM geometry).
    B : float
        Perturbation amplitude (0 for no μ modification).
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    z_init : float
        Initial redshift for integration.
    n_points : int
        Number of integration steps.

    Returns
    -------
    dict
        {"z": ndarray, "a": ndarray, "f": ndarray, "ln_D": ndarray}
        where ln_D is the integrated log growth factor.
    """
    a_init = 1.0 / (1.0 + z_init)
    ln_a_arr = np.linspace(np.log(a_init), 0.0, n_points)
    h = ln_a_arr[1] - ln_a_arr[0]

    E2_init = E2_lcdm(z_init, Omega_m)
    Om_init = _omega_m_tilde(a_init, E2_init, Omega_m)
    f_val = Om_init ** 0.55

    f_arr = np.zeros(n_points)
    ln_D_arr = np.zeros(n_points)
    f_arr[0] = f_val
    ln_D_arr[0] = 0.0

    def rhs(ln_a, f):
        return growth_ode(ln_a, f, Omega_m, A, B, z_t, n)

    for i in range(1, n_points):
        ln_a_i = ln_a_arr[i - 1]
        k1 = rhs(ln_a_i, f_val)
        k2 = rhs(ln_a_i + 0.5 * h, f_val + 0.5 * h * k1)
        k3 = rhs(ln_a_i + 0.5 * h, f_val + 0.5 * h * k2)
        k4 = rhs(ln_a_i + h, f_val + h * k3)
        f_val = f_val + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
        f_arr[i] = f_val
        ln_D_arr[i] = ln_D_arr[i - 1] + f_val * h

    a_arr = np.exp(ln_a_arr)
    z_arr = 1.0 / a_arr - 1.0

    return {
        "z": z_arr,
        "a": a_arr,
        "f": f_arr,
        "ln_D": ln_D_arr,
    }


def compute_fsigma8(z_eval, Omega_m=DEFAULT_OMEGA_M, A=0.0, B=0.0,
                    z_t=1.01, n=6, sigma8_0=DEFAULT_SIGMA8_LCDM):
    """
    Compute fσ₈(z) at specified redshifts.

    fσ₈(z) = f(z) × σ₈(z) = f(z) × σ₈,₀ × D(z)/D(0)

    Parameters
    ----------
    z_eval : float or array_like
        Redshifts at which to evaluate fσ₈.
    Omega_m : float
        Matter density parameter.
    A : float
        Background gate amplitude.
    B : float
        Perturbation amplitude.
    z_t : float
        Transition redshift.
    n : float
        Steepness exponent.
    sigma8_0 : float
        Present-day σ₈ value.

    Returns
    -------
    dict
        {"z": ndarray, "fsigma8": ndarray, "f": ndarray, "sigma8_z": ndarray}
    """
    z_eval = np.atleast_1d(np.asarray(z_eval, dtype=float))
    sol = solve_growth(Omega_m, A, B, z_t, n)

    f_interp = np.interp(z_eval, sol["z"][::-1], sol["f"][::-1])
    ln_D_interp = np.interp(z_eval, sol["z"][::-1], sol["ln_D"][::-1])
    ln_D_0 = sol["ln_D"][-1]

    D_ratio = np.exp(ln_D_interp - ln_D_0)
    sigma8_z = sigma8_0 * D_ratio
    fsigma8 = f_interp * sigma8_z

    return {
        "z": z_eval,
        "fsigma8": fsigma8,
        "f": f_interp,
        "sigma8_z": sigma8_z,
    }
