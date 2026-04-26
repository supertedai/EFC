"""a_falsified_bar_instability_criterion_re.py

Reference implementation of the EFC-modified Toomre-Q stability parameter
from Magnusson (2026), DOI: 10.6084/m9.figshare.32101111

Key equation:
  Pi_EFC(R) = sigma_R(R) * kappa_eff(R) / (3.36 * G * Sigma(R))
  kappa_eff^2 = kappa^2 + zeta * g_EFC / R
  g_EFC = alpha * v * R * dOmega/dR          (shear proxy)
       or alpha * d(v^2)/dR                   (v_squared proxy)
"""
import numpy as np
from numpy.typing import NDArray
from typing import Tuple, Optional, Literal
from scipy.signal import savgol_filter

# --- Physical constants ---
G_CGS = 6.674e-8        # cm^3 g^-1 s^-2
G_SI = 6.674e-11        # m^3 kg^-1 s^-2
kpc_to_m = 3.0857e19    # metres per kpc
km_s_to_m_s = 1.0e3
Msun = 1.989e30         # kg
Msun_per_pc2_to_SI = Msun / (3.0857e16)**2  # kg m^-2

# --- Paper constants ---
TOOMRE_COEFF = 3.36
ZETA_DEFAULT = 1.0
ZETA_MAX = 1.52          # kappa_eff^2 >= 0 constraint
SAVGOL_WINDOW = 5
SAVGOL_ORDER = 2
SIGMA_R_FALLBACK = 30.0  # km/s constant fallback
ALPHA_BOUNDS = (0.05, 0.95)
DISK_WINDOW_INNER = 1.0  # Rd multiplier
DISK_WINDOW_OUTER = 3.0  # Rd multiplier
REVAL_FACTOR = 2.2       # R_eval = 2.2 * Rd


def fit_Rd(r_kpc: NDArray, v_km_s: NDArray) -> Tuple[float, float]:
    """Fit V(R) = Vflat * tanh(R/Rd) to a rotation curve.
    Returns (Vflat_km_s, Rd_kpc)."""
    from scipy.optimize import curve_fit
    def model(r, vflat, rd):
        return vflat * np.tanh(r / rd)
    v0 = np.max(v_km_s)
    rd0 = r_kpc[np.argmin(np.abs(v_km_s - 0.63 * v0))] or r_kpc[1]
    try:
        popt, _ = curve_fit(model, r_kpc, v_km_s, p0=[v0, rd0],
                            bounds=([0, 0.01], [2*v0+50, np.max(r_kpc)*2]),
                            maxfev=10000)
        return float(popt[0]), float(popt[1])
    except RuntimeError:
        return float(v0), float(rd0)


def safe_savgol_derivative(y: NDArray, x: NDArray, window: int = SAVGOL_WINDOW,
                           order: int = SAVGOL_ORDER) -> NDArray:
    """Savitzky-Golay derivative on dimensionless indices, rescaled.
    Workaround for scipy SG numerical-stability bug at large physical dx."""
    n = len(x)
    if n < window:
        return np.gradient(y, x)
    idx = np.arange(n, dtype=float)
    dy_didx = savgol_filter(y, window, order, deriv=1, delta=1.0)
    didx_dx = 1.0 / np.gradient(x, idx)
    # Clamp extreme didx_dx
    didx_dx = np.clip(didx_dx, -1e30, 1e30)
    return dy_didx * didx_dx


def angular_velocity(v: NDArray, r: NDArray) -> NDArray:
    """Omega = v / r, handling r=0."""
    out = np.zeros_like(v)
    mask = r > 0
    out[mask] = v[mask] / r[mask]
    return out


def epicyclic_frequency_sq(v: NDArray, r: NDArray) -> NDArray:
    """Standard kappa^2 = (2 Omega / R) d(R^2 Omega)/dR."""
    omega = angular_velocity(v, r)
    R2Omega = r**2 * omega
    dR2Omega_dR = safe_savgol_derivative(R2Omega, r)
    kappa2 = np.zeros_like(r)
    mask = r > 0
    kappa2[mask] = (2.0 * omega[mask] / r[mask]) * dR2Omega_dR[mask]
    return kappa2


def g_efc(v: NDArray, r: NDArray, alpha: float,
          proxy_mode: Literal['v_squared', 'shear'] = 'shear') -> NDArray:
    """EFC effective acceleration.
    shear:     g_EFC = alpha * v * R * dOmega/dR
    v_squared: g_EFC = alpha * d(v^2)/dR
    """
    if proxy_mode == 'v_squared':
        v2 = v**2
        return alpha * safe_savgol_derivative(v2, r)
    else:  # shear
        omega = angular_velocity(v, r)
        dOmega_dR = safe_savgol_derivative(omega, r)
        return alpha * v * r * dOmega_dR


def kappa_eff_sq(v: NDArray, r: NDArray, alpha: float,
                 zeta: float = ZETA_DEFAULT,
                 proxy_mode: str = 'shear') -> NDArray:
    """kappa_eff^2 = kappa^2 + zeta * g_EFC / R   (Eq. 2)."""
    k2 = epicyclic_frequency_sq(v, r)
    ge = g_efc(v, r, alpha, proxy_mode)
    efc_term = np.zeros_like(r)
    mask = r > 0
    efc_term[mask] = zeta * ge[mask] / r[mask]
    return k2 + efc_term


def sigma_R_jeans(Sigma: NDArray, Rd_kpc: float) -> NDArray:
    """Jeans-inspired radial velocity dispersion:
    sigma_R(R) = pi * G * Sigma(R) * Rd.
    Sigma in Msun/pc^2, Rd in kpc -> sigma_R in km/s."""
    Rd_pc = Rd_kpc * 1000.0
    # sigma_R = pi * G * Sigma * Rd  in cgs then convert
    G_pc = G_SI * Msun / (3.0857e16)**3 * (3.0857e16)  # rough
    # Simpler: work in SI
    Sigma_SI = Sigma * Msun_per_pc2_to_SI  # kg/m^2
    Rd_m = Rd_kpc * kpc_to_m
    sigma_ms = np.pi * G_SI * Sigma_SI * Rd_m  # m/s
    return sigma_ms / km_s_to_m_s  # km/s


def Pi_EFC(r_kpc: NDArray, v_km_s: NDArray, Sigma_Msun_pc2: NDArray,
           Rd_kpc: float, alpha: float, zeta: float = ZETA_DEFAULT,
           proxy_mode: str = 'shear',
           sigma_fallback_kms: float = SIGMA_R_FALLBACK
           ) -> NDArray:
    """Compute Pi_EFC(R) profile (Eq. 1 of the paper)."""
    alpha = np.clip(alpha, *ALPHA_BOUNDS)
    r_m = r_kpc * kpc_to_m
    v_ms = v_km_s * km_s_to_m_s
    sigma_kms = sigma_R_jeans(Sigma_Msun_pc2, Rd_kpc)
    # Fallback for very low Sigma
    sigma_kms = np.where(sigma_kms < 0.1, sigma_fallback_kms, sigma_kms)
    sigma_ms = sigma_kms * km_s_to_m_s
    k2eff = kappa_eff_sq(v_ms, r_m, alpha, zeta, proxy_mode)
    # Enforce non-negative for sqrt
    k2eff_safe = np.clip(k2eff, 0.0, None)
    keff = np.sqrt(k2eff_safe)
    Sigma_SI = Sigma_Msun_pc2 * Msun_per_pc2_to_SI
    denom = TOOMRE_COEFF * G_SI * Sigma_SI
    Pi = np.zeros_like(r_kpc)
    mask = denom > 0
    Pi[mask] = sigma_ms[mask] * keff[mask] / denom[mask]
    return Pi


def Pi_min_disk_window(r_kpc: NDArray, Pi: NDArray,
                       Rd_kpc: float) -> float:
    """Minimum Pi in disk window [Rd, 3Rd]."""
    mask = (r_kpc >= DISK_WINDOW_INNER * Rd_kpc) & (
             r_kpc <= DISK_WINDOW_OUTER * Rd_kpc)
    if not np.any(mask):
        return float(np.min(Pi[Pi > 0])) if np.any(Pi > 0) else float(np.nan)
    return float(np.min(Pi[mask]))


def Pi_proxy_scalar(Vflat_kms: float, Rd_kpc: float,
                    Sigma_disk_Msun_pc2: float,
                    alpha: float, zeta: float = ZETA_DEFAULT) -> float:
    """Quick scalar Pi proxy evaluated at R = 2.2 Rd using tanh model."""
    Reval = REVAL_FACTOR * Rd_kpc
    r = np.array([0.5, 1.0, 1.5, 2.0, 2.2, 2.5, 3.0, 3.5]) * Rd_kpc
    v = Vflat_kms * np.tanh(r / Rd_kpc)
    Sigma_arr = np.full_like(r, Sigma_disk_Msun_pc2)
    pi_arr = Pi_EFC(r, v, Sigma_arr, Rd_kpc, alpha, zeta)
    idx = np.argmin(np.abs(r - Reval))
    return float(pi_arr[idx])


if __name__ == '__main__':
    # Self-test: synthetic tanh rotation curve
    r = np.linspace(0.5, 15.0, 80)  # kpc
    Vflat, Rd = 150.0, 3.0           # km/s, kpc
    v = Vflat * np.tanh(r / Rd)
    Sigma = 100.0 * np.exp(-r / Rd)   # Msun/pc^2
    alpha = 0.6
    pi = Pi_EFC(r, v, Sigma, Rd, alpha, zeta=1.0)
    pmin = Pi_min_disk_window(r, pi, Rd)
    print(f'Synthetic test: Pi range = [{pi.min():.2f}, {pi.max():.2f}]')
    print(f'Pi_min in disk window = {pmin:.2f}')
    assert 1.0 < pmin < 20.0, f'Pi_min out of expected range: {pmin}'
    print('Self-test PASSED.')
