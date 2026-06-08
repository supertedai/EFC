"""jwst_hmf_prereg_v4.py

Reference implementation of the EFC halo mass function prediction chain
from Magnusson (2026) Pre-Registration: EFC dN/dM (z>7).

Chain: g(a) -> mu(a) -> D(a) -> sigma(M,z) -> n(M,z)

Equations follow the paper exactly (Eqs. 1-3 and the five-step chain).
"""
import numpy as np
from scipy.integrate import solve_ivp, quad
from scipy.interpolate import interp1d
from typing import Tuple, Optional

# --------------- cosmological constants (Planck 2018 flat LCDM baseline) -------
OM0 = 0.3111          # Omega_matter_0
OL0 = 1.0 - OM0       # Omega_Lambda_0
H0 = 67.66            # km/s/Mpc
NS = 0.9665           # spectral index
SIGMA8 = 0.8102       # sigma_8 LCDM normalisation
RHO_CRIT0 = 2.775e11  # h^2 Msun / Mpc^3  (critical density today)
H0_H = H0 / 100.0     # h = H0/100
RHO_M0 = OM0 * RHO_CRIT0  # mean matter density in h^2 Msun/Mpc^3
DELTA_C = 1.686        # spherical collapse threshold

# --------------- EFC gate parameters (placeholders until joint S(z)-fit) -------
# These are to be replaced once vc 4ea464e38b5f posterior is available.
B_DEFAULT = 0.04      # perturbation channel amplitude
ZT_DEFAULT = 3.0      # transition redshift
N_DEFAULT = 4.0       # gate steepness exponent


# =============================================================================
# Step 1: Gate function  g(a)
# =============================================================================
def gate_function(a: float, zt: float = ZT_DEFAULT, n: float = N_DEFAULT) -> float:
    """EFC gate function g(a) = 1 / (1 + (zt/z(a))^n), Eq. (2)."""
    z = 1.0 / a - 1.0
    if z <= 0:
        return 0.0
    return 1.0 / (1.0 + (zt / z) ** n)


def gate_function_arr(a_arr: np.ndarray, zt: float = ZT_DEFAULT, n: float = N_DEFAULT) -> np.ndarray:
    """Vectorised gate function."""
    z_arr = 1.0 / a_arr - 1.0
    with np.errstate(divide='ignore', invalid='ignore'):
        result = np.where(z_arr > 0, 1.0 / (1.0 + (zt / z_arr) ** n), 0.0)
    return result


# =============================================================================
# Step 2: Effective gravitational coupling  mu(a)
# =============================================================================
def mu_eff(a: float, B: float = B_DEFAULT, zt: float = ZT_DEFAULT, n: float = N_DEFAULT) -> float:
    """EFC effective gravitational coupling mu(a) = 1 - B*g(a), Eq. (3)."""
    return 1.0 - B * gate_function(a, zt, n)


# =============================================================================
# Step 3: Modified linear growth factor  D(a)
# =============================================================================
def _E2(a: float) -> float:
    """Dimensionless Hubble parameter squared E^2(a) = H^2/H0^2 (flat LCDM)."""
    return OM0 * a**(-3) + OL0


def _E(a: float) -> float:
    return np.sqrt(_E2(a))


def growth_ode(ln_a: float, y: np.ndarray, B: float, zt: float, n_gate: float) -> list:
    """ODE for linear growth: D and f = d ln D / d ln a.

    Variables: y = [D, f] with f = a/D * dD/da = d ln D / d ln a.
    Independent variable: ln(a).

    d f / d ln a = -f^2 - (2 + dln E / d ln a) f + 3/2 Omega_m(a) mu(a)
    d D / d ln a = f * D
    """
    a = np.exp(ln_a)
    D_val, f_val = y
    E2 = _E2(a)
    Om_a = OM0 * a**(-3) / E2
    # d ln E / d ln a
    dE2_dlna = -3.0 * OM0 * a**(-3)  # derivative of E^2 w.r.t. ln a
    dlnE_dlna = 0.5 * dE2_dlna / E2
    mu_val = mu_eff(a, B, zt, n_gate)
    df_dlna = -f_val**2 - (2.0 + dlnE_dlna) * f_val + 1.5 * Om_a * mu_val
    dD_dlna = f_val * D_val
    return [dD_dlna, df_dlna]


def compute_growth(B: float = B_DEFAULT, zt: float = ZT_DEFAULT, n_gate: float = N_DEFAULT,
                   a_start: float = 1e-3, a_end: float = 1.0,
                   n_points: int = 2000) -> Tuple[np.ndarray, np.ndarray]:
    """Solve modified growth ODE and return (a_array, D_array) normalised so D(a=1)=1 for LCDM."""
    ln_a_span = (np.log(a_start), np.log(a_end))
    ln_a_eval = np.linspace(*ln_a_span, n_points)
    # Initial conditions deep in matter domination: D ~ a, f ~ 1
    y0 = [a_start, 1.0]
    sol = solve_ivp(growth_ode, ln_a_span, y0, args=(B, zt, n_gate),
                    t_eval=ln_a_eval, rtol=1e-10, atol=1e-12, method='RK45')
    a_arr = np.exp(sol.t)
    D_arr = sol.y[0]
    # Normalise: compute LCDM growth to get D_LCDM(1) for reference
    sol_lcdm = solve_ivp(growth_ode, ln_a_span, y0, args=(0.0, zt, n_gate),
                         t_eval=ln_a_eval, rtol=1e-10, atol=1e-12, method='RK45')
    D_lcdm = sol_lcdm.y[0]
    # Normalise both so that LCDM D(1) = 1
    norm = D_lcdm[-1]
    D_arr = D_arr / norm
    D_lcdm_normed = D_lcdm / norm
    return a_arr, D_arr


# =============================================================================
# Step 4: Variance sigma(M, z)
# =============================================================================
def _top_hat_W(k: np.ndarray, R: float) -> np.ndarray:
    """Fourier-space top-hat window function."""
    x = k * R
    return 3.0 * (np.sin(x) - x * np.cos(x)) / x**3


def _transfer_EH(k: np.ndarray) -> np.ndarray:
    """Eisenstein-Hu (1998) approximate transfer function (no BAO wiggles)."""
    Ob0 = 0.0490
    h = H0_H
    Theta27 = 2.725 / 2.7
    s = 44.5 * np.log(9.83 / (OM0 * h**2)) / np.sqrt(1 + 10 * (Ob0 * h**2)**0.75)
    Gamma_eff = OM0 * h * (0.7212 - 0.0223 * (Ob0 / OM0))
    q = k / (Gamma_eff * h) * Theta27**2
    L0 = np.log(2 * np.e + 1.8 * q)
    C0 = 14.2 + 731.0 / (1 + 62.5 * q)
    return L0 / (L0 + C0 * q**2)


def _Pk_unnorm(k: np.ndarray) -> np.ndarray:
    """Un-normalised linear P(k) ~ k^ns * T(k)^2."""
    return k**NS * _transfer_EH(k)**2


def sigma_M(M: float, D_z: float, Pk_norm: float) -> float:
    """sigma(M, z) = D(z) * sigma(M, z=0). M in h^-1 Msun."""
    R = (3.0 * M / (4.0 * np.pi * RHO_M0))**(1.0 / 3.0)  # Mpc/h
    def integrand(lnk: float) -> float:
        k = np.exp(lnk)
        return k**3 * _Pk_unnorm(np.array([k]))[0] * _top_hat_W(np.array([k]), R)[0]**2
    val, _ = quad(integrand, np.log(1e-4), np.log(1e2), limit=200)
    sigma0_sq = val / (2.0 * np.pi**2)
    sigma0 = np.sqrt(sigma0_sq * Pk_norm)
    return D_z * sigma0


def calibrate_Pk_norm() -> float:
    """Return Pk normalisation constant so that sigma(R=8 Mpc/h, z=0)=SIGMA8."""
    R8 = 8.0  # Mpc/h
    def integrand(lnk: float) -> float:
        k = np.exp(lnk)
        return k**3 * _Pk_unnorm(np.array([k]))[0] * _top_hat_W(np.array([k]), R8)[0]**2
    val, _ = quad(integrand, np.log(1e-4), np.log(1e2), limit=200)
    return SIGMA8**2 / (val / (2.0 * np.pi**2))


# =============================================================================
# Step 5: Halo Mass Function  n(M, z)
# =============================================================================
def f_PS(sigma: float) -> float:
    """Press-Schechter multiplicity function."""
    nu = DELTA_C / sigma
    return np.sqrt(2.0 / np.pi) * nu * np.exp(-0.5 * nu**2)


def f_ST(sigma: float, A_st: float = 0.3222, a_st: float = 0.707, p_st: float = 0.3) -> float:
    """Sheth-Tormen multiplicity function."""
    nu = DELTA_C / sigma
    nu2 = a_st * nu**2
    return A_st * np.sqrt(2.0 * nu2 / np.pi) * (1.0 + nu2**(-p_st)) * np.exp(-0.5 * nu2)


def f_Tinker(sigma: float, z: float = 0.0) -> float:
    """Tinker et al. (2008) multiplicity function for Delta=200."""
    A0, a0, b0, c0 = 0.186, 1.47, 2.57, 1.19
    alpha = 10.0 ** (-(0.75 / np.log10(200.0 / 75.0))**1.2)
    A = A0 * (1.0 + z)**(-0.14)
    a = a0 * (1.0 + z)**(-0.06)
    b = b0 * (1.0 + z)**(-alpha)
    c = c0
    return A * ((sigma / b)**(-a) + 1.0) * np.exp(-c / sigma**2)


def dndlnM(M: float, z: float, D_z: float, Pk_norm: float,
           prescription: str = 'ST') -> float:
    """Halo mass function dn/dlnM  [h^3 Mpc^-3].

    Parameters
    ----------
    M : halo mass in h^-1 Msun
    z : redshift
    D_z : growth factor at z
    Pk_norm : power spectrum normalisation
    prescription : 'PS', 'ST', or 'Tinker'
    """
    sig = sigma_M(M, D_z, Pk_norm)
    # d ln sigma^{-1} / d ln M  via finite difference
    eps = 0.01
    sig_p = sigma_M(M * (1 + eps), D_z, Pk_norm)
    sig_m = sigma_M(M * (1 - eps), D_z, Pk_norm)
    dlnsigma_inv_dlnM = -(np.log(sig_p) - np.log(sig_m)) / (np.log(M*(1+eps)) - np.log(M*(1-eps)))
    if prescription == 'PS':
        f_val = f_PS(sig)
    elif prescription == 'ST':
        f_val = f_ST(sig)
    elif prescription == 'Tinker':
        f_val = f_Tinker(sig, z)
    else:
        raise ValueError(f'Unknown prescription {prescription}')
    return RHO_M0 / M * f_val * abs(dlnsigma_inv_dlnM)


# =============================================================================
# Convenience: full chain for a set of redshifts
# =============================================================================
def compute_hmf_table(z_arr: np.ndarray, logM_arr: np.ndarray,
                      B: float = B_DEFAULT, zt: float = ZT_DEFAULT,
                      n_gate: float = N_DEFAULT,
                      prescription: str = 'ST') -> np.ndarray:
    """Return 2-D array of dn/dlnM [h^3 Mpc^-3] with shape (len(z_arr), len(logM_arr))."""
    a_grid, D_grid = compute_growth(B, zt, n_gate)
    D_interp = interp1d(a_grid, D_grid, kind='cubic', fill_value='extrapolate')
    Pk_norm = calibrate_Pk_norm()
    table = np.zeros((len(z_arr), len(logM_arr)))
    for i, z in enumerate(z_arr):
        a = 1.0 / (1.0 + z)
        Dz = D_interp(a)
        for j, lgM in enumerate(logM_arr):
            M = 10.0**lgM
            table[i, j] = dndlnM(M, z, Dz, Pk_norm, prescription)
    return table


# =============================================================================
# Self-test
# =============================================================================
if __name__ == '__main__':
    print('=== Self-test: jwst_hmf_prereg_v4 ===')
    # Gate function check
    a_test = 1.0 / (1.0 + 8.0)  # z=8
    g_val = gate_function(a_test)
    mu_val = mu_eff(a_test)
    print(f'z=8 : g(a)={g_val:.6f}, mu(a)={mu_val:.6f}')
    # Growth factor
    a_arr, D_arr = compute_growth()
    D_interp = interp1d(a_arr, D_arr, kind='cubic')
    for z in [7, 8, 9, 10, 11, 12]:
        a = 1.0 / (1.0 + z)
        print(f'  z={z:2d}  D(z)={D_interp(a):.6e}')
    # Pk normalisation
    Pk_norm = calibrate_Pk_norm()
    print(f'Pk normalisation constant = {Pk_norm:.6e}')
    # Single HMF value
    val = dndlnM(1e11, 8.0, D_interp(1.0/9.0), Pk_norm, 'ST')
    print(f'dn/dlnM(M=1e11, z=8, ST) = {val:.6e} h^3 Mpc^-3')
    print('Self-test complete.')
