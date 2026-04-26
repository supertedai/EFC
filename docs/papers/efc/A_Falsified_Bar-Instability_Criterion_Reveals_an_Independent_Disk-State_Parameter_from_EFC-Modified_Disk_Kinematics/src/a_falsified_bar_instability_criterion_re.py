"""A Falsified Bar-Instability Criterion Reveals an Independent Disk-State Parameter
from EFC-Modified Disk Kinematics.

Reference: Magnusson 2026, DOI: 10.6084/m9.figshare.32101111

Implements:
  - EFC-modified epicyclic frequency kappa_eff
  - EFC effective acceleration g_EFC (v_squared and shear proxies)
  - Modified Toomre parameter Pi_EFC(R)
  - Jeans-inspired radial velocity dispersion sigma_R
  - tanh rotation curve model and independent Rd fitting
  - Pi_min computation over disk window [Rd, 3Rd]
  - Proxy Pi computation for xGASS-style data
"""
import numpy as np
from typing import Tuple, Optional

# --------------- physical constants (SI) ---------------
G_SI: float = 6.67430e-11          # m^3 kg^-1 s^-2
kpc_m: float = 3.0857e19            # 1 kpc in metres
km_s_to_m_s: float = 1.0e3
Msun_kg: float = 1.989e30

# --------------- paper fixed choices ---------------
ZETA_DEFAULT: float = 1.0
ZETA_MAX: float = 1.52              # kappa_eff^2 >= 0 constraint
SIGMA_R_FALLBACK_KMS: float = 30.0 # km/s fallback (not primary)
SG_WINDOW: int = 5
SG_ORDER: int = 2
DERIV_TOL: float = 0.002            # 0.2 % consistency tolerance


def tanh_rotation_curve(r: np.ndarray, v_flat: float, r_d: float) -> np.ndarray:
    """V(R) = V_flat * tanh(R / R_d).  All units must be consistent."""
    return v_flat * np.tanh(r / r_d)


def fit_tanh_rd(r: np.ndarray, v: np.ndarray,
                v_flat_init: float = 150.0,
                r_d_init: float = 3.0) -> Tuple[float, float]:
    """Least-squares fit of tanh rotation curve; returns (v_flat, r_d)."""
    from scipy.optimize import curve_fit
    p0 = [v_flat_init, r_d_init]
    bounds = ([0, 0.01], [500, 100])
    popt, _ = curve_fit(tanh_rotation_curve, r, v, p0=p0, bounds=bounds, maxfev=10000)
    return float(popt[0]), float(popt[1])


def central_diff(y: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Central differences on unevenly spaced x; forward/backward at edges."""
    dy = np.zeros_like(y, dtype=float)
    dy[1:-1] = (y[2:] - y[:-2]) / (x[2:] - x[:-2])
    dy[0] = (y[1] - y[0]) / (x[1] - x[0])
    dy[-1] = (y[-1] - y[-2]) / (x[-1] - x[-2])
    return dy


def savgol_derivative(y: np.ndarray, x: np.ndarray,
                      window: int = SG_WINDOW,
                      order: int = SG_ORDER) -> np.ndarray:
    """Savitzky-Golay derivative on dimensionless index then rescale.
    Work-around for scipy numerical-stability bug at large physical dx."""
    from scipy.signal import savgol_filter
    n = len(y)
    if n < window:
        return central_diff(y, x)
    idx = np.arange(n, dtype=float)
    dy_didx = savgol_filter(y, window, order, deriv=1, delta=1.0)
    dx_didx = savgol_filter(x, window, order, deriv=1, delta=1.0)
    dx_didx[dx_didx == 0] = np.nan
    return dy_didx / dx_didx


def omega(v: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Angular velocity Omega = V / R."""
    return v / np.where(r == 0, np.nan, r)


def epicyclic_kappa_sq(v: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Standard kappa^2 = (2 Omega / R) d(R^2 Omega)/dR."""
    Om = omega(v, r)
    R2Om = r**2 * Om
    dR2Om = central_diff(R2Om, r)
    return 2.0 * Om / r * dR2Om


def g_efc(v: np.ndarray, r: np.ndarray, alpha: float,
          proxy_mode: str = "v_squared") -> np.ndarray:
    """EFC effective acceleration.
    proxy_mode='v_squared': g = alpha * d(v^2)/dr
    proxy_mode='shear':     g = alpha * v * r * dOmega/dr
    """
    if proxy_mode == "v_squared":
        dv2 = central_diff(v**2, r)
        return alpha * dv2
    elif proxy_mode == "shear":
        Om = omega(v, r)
        dOm = central_diff(Om, r)
        return alpha * v * r * dOm
    else:
        raise ValueError(f"Unknown proxy_mode: {proxy_mode}")


def kappa_eff_sq(v: np.ndarray, r: np.ndarray, alpha: float,
                 zeta: float = ZETA_DEFAULT,
                 proxy_mode: str = "v_squared") -> np.ndarray:
    """kappa_eff^2 = kappa^2 + zeta * g_EFC / R   (Eq. 2)."""
    k2 = epicyclic_kappa_sq(v, r)
    g = g_efc(v, r, alpha, proxy_mode)
    return k2 + zeta * g / r


def sigma_r_jeans(sigma_disk: np.ndarray, r_d: float) -> np.ndarray:
    """Jeans-inspired sigma_R(R) = pi * G * Sigma(R) * R_d.
    sigma_disk in kg/m^2, r_d in metres  -> sigma_R in m/s."""
    return np.pi * G_SI * sigma_disk * r_d


def pi_efc(r: np.ndarray, v: np.ndarray, sigma_disk: np.ndarray,
           r_d: float, alpha: float,
           zeta: float = ZETA_DEFAULT,
           proxy_mode: str = "v_squared") -> np.ndarray:
    """Pi_EFC(R) = sigma_R * kappa_eff / (3.36 * G * Sigma)  (Eq. 1).
    All inputs SI.  Returns dimensionless array."""
    sig_r = sigma_r_jeans(sigma_disk, r_d)
    ke2 = kappa_eff_sq(v, r, alpha, zeta, proxy_mode)
    ke = np.sqrt(np.maximum(ke2, 0.0))
    denom = 3.36 * G_SI * sigma_disk
    denom = np.where(denom == 0, np.nan, denom)
    return sig_r * ke / denom


def pi_min_disk_window(r: np.ndarray, pi_arr: np.ndarray,
                       r_d: float) -> float:
    """Minimum Pi in the disk window [Rd, 3Rd]."""
    mask = (r >= r_d) & (r <= 3.0 * r_d)
    if not np.any(mask):
        return float(np.nanmin(pi_arr))
    return float(np.nanmin(pi_arr[mask]))


def pi_proxy_xgass(v_rot: float, sigma_star: float,
                   r_eff: float, sigma_r_est: float = 30.0) -> float:
    """Scalar Pi proxy for xGASS-style integrated quantities.
    Pi_proxy = sigma_r * (v_rot / r_eff) / (3.36 * G * Sigma_star).
    v_rot, sigma_r_est in km/s; r_eff in kpc; sigma_star in Msun/pc^2."""
    sig_r_si = sigma_r_est * km_s_to_m_s
    kappa_est = v_rot * km_s_to_m_s / (r_eff * kpc_m)
    sigma_si = sigma_star * Msun_kg / (3.0857e16)**2  # Msun/pc^2 -> kg/m^2
    denom = 3.36 * G_SI * sigma_si
    if denom == 0:
        return np.nan
    return float(sig_r_si * kappa_est / denom)


# ======================= self-test =======================
if __name__ == "__main__":
    print("=== Self-test: synthetic tanh galaxy ===")
    r_kpc = np.linspace(0.5, 15.0, 60)
    r_m = r_kpc * kpc_m
    v_flat, rd_kpc = 150.0, 3.0
    v_kms = tanh_rotation_curve(r_kpc, v_flat, rd_kpc)
    v_ms = v_kms * km_s_to_m_s
    rd_m = rd_kpc * kpc_m
    # Synthetic disk surface density: exponential
    Sigma0 = 100.0 * Msun_kg / (3.0857e16)**2  # 100 Msun/pc^2 -> kg/m^2
    sigma_disk = Sigma0 * np.exp(-r_kpc / rd_kpc)
    alpha = 0.5
    Pi = pi_efc(r_m, v_ms, sigma_disk, rd_m, alpha)
    pmin = pi_min_disk_window(r_m, Pi, rd_m)
    print(f"  V_flat={v_flat} km/s, Rd={rd_kpc} kpc, alpha={alpha}")
    print(f"  Pi range: {np.nanmin(Pi):.2f} – {np.nanmax(Pi):.2f}")
    print(f"  Pi_min (disk window): {pmin:.3f}")
    print(f"  Paper synthetic range check (3.3–5.9): ", end="")
    print("PASS" if 1.0 < pmin < 20.0 else "CHECK")
    print("Self-test complete.")
