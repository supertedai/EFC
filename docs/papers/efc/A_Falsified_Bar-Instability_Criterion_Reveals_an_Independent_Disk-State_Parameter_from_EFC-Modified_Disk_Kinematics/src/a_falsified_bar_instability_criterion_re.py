"""A Falsified Bar-Instability Criterion Reveals an Independent Disk-State Parameter
from EFC-Modified Disk Kinematics.

Reference: Magnusson 2026, DOI: 10.6084/m9.figshare.32101111

Implements the EFC-modified Toomre-Q parameter Pi_EFC and associated diagnostics.
"""
import numpy as np
from numpy.typing import NDArray
from scipy.signal import savgol_filter
from typing import Tuple, Optional

# --- Physical constants (SI) ---
G_SI: float = 6.67430e-11          # m^3 kg^-1 s^-2
KPC_M: float = 3.0857e19           # metres per kpc
KMS_MS: float = 1.0e3              # m/s per km/s
MSOL_KG: float = 1.98892e30        # kg per solar mass

# --- Paper-fixed defaults ---
ZETA_DEFAULT: float = 1.0
SIGMA_R_FALLBACK_KMS: float = 30.0  # km/s constant fallback
SG_WINDOW: int = 5
SG_ORDER: int = 2
ALPHA_BOUNDS: Tuple[float, float] = (0.05, 0.95)
ZETA_MAX: float = 1.52              # kappa_eff^2 >= 0 constraint


def alpha_from_latency(L: float) -> float:
    """EFC alpha = 1 - L, clamped to [0.05, 0.95]."""
    return float(np.clip(1.0 - L, *ALPHA_BOUNDS))


def fit_tanh_Rd(r_kpc: NDArray, v_kms: NDArray) -> Tuple[float, float]:
    """Fit V(R) = Vflat * tanh(R/Rd) and return (Vflat_kms, Rd_kpc)."""
    from scipy.optimize import curve_fit
    def model(r: NDArray, vflat: float, rd: float) -> NDArray:
        return vflat * np.tanh(r / rd)
    p0 = [np.max(v_kms), np.median(r_kpc[r_kpc > 0])]
    bounds = ([0.0, 0.01], [1000.0, 500.0])
    popt, _ = curve_fit(model, r_kpc, v_kms, p0=p0, bounds=bounds, maxfev=10000)
    return float(popt[0]), float(popt[1])


def _safe_gradient(y: NDArray, x: NDArray, sg_window: int = SG_WINDOW,
                   sg_order: int = SG_ORDER) -> NDArray:
    """Central-diff derivative with parallel Savitzky-Golay on *index* then rescale.

    The paper notes a scipy savgol_filter numerical-stability bug at large physical dx;
    computing SG on dimensionless indices and rescaling avoids sign-flips.
    """
    n = len(x)
    if n < sg_window:
        return np.gradient(y, x)
    dx = np.gradient(x)  # physical spacing per index
    dy_di = savgol_filter(y, sg_window, sg_order, deriv=1)  # d(y)/d(index)
    return dy_di / dx


def omega(r: NDArray, v: NDArray) -> NDArray:
    """Angular velocity Omega = v / r  (handles r=0 gracefully)."""
    with np.errstate(divide='ignore', invalid='ignore'):
        om = np.where(r > 0, v / r, 0.0)
    return om


def epicyclic_kappa_sq(r: NDArray, v: NDArray) -> NDArray:
    """Classical epicyclic frequency squared: kappa^2 = R dOmega^2/dR + 4 Omega^2."""
    Om = omega(r, v)
    dOm2_dR = _safe_gradient(Om**2, r)
    return r * dOm2_dR + 4.0 * Om**2


def g_efc(r: NDArray, v: NDArray, alpha: float,
         proxy_mode: str = 'v_squared') -> NDArray:
    """EFC effective acceleration.

    proxy_mode='v_squared':  g_EFC = alpha * d(v^2)/dR   (v0.1)
    proxy_mode='shear':      g_EFC = alpha * v * R * dOmega/dR  (v0.2)
    """
    if proxy_mode == 'v_squared':
        return alpha * _safe_gradient(v**2, r)
    elif proxy_mode == 'shear':
        Om = omega(r, v)
        dOm_dR = _safe_gradient(Om, r)
        return alpha * v * r * dOm_dR
    raise ValueError(f"Unknown proxy_mode {proxy_mode!r}")


def kappa_eff_sq(r: NDArray, v: NDArray, alpha: float,
                zeta: float = ZETA_DEFAULT,
                proxy_mode: str = 'v_squared') -> NDArray:
    """Modified epicyclic frequency squared (Eq. 2):
    kappa_eff^2 = kappa^2 + zeta * g_EFC / R
    """
    k2 = epicyclic_kappa_sq(r, v)
    ge = g_efc(r, v, alpha, proxy_mode)
    with np.errstate(divide='ignore', invalid='ignore'):
        correction = np.where(r > 0, zeta * ge / r, 0.0)
    return k2 + correction


def sigma_R_jeans(Sigma: NDArray, Rd: float) -> NDArray:
    """Jeans-inspired radial velocity dispersion: sigma_R = pi * G * Sigma * Rd.

    All quantities SI.  Returns m/s.
    """
    return np.pi * G_SI * Sigma * Rd


def Pi_EFC(r: NDArray, v: NDArray, Sigma: NDArray, Rd: float,
           alpha: float, zeta: float = ZETA_DEFAULT,
           proxy_mode: str = 'v_squared',
           sigma_R: Optional[NDArray] = None) -> NDArray:
    """EFC-modified Toomre parameter (Eq. 1):

    Pi_EFC(R) = sigma_R(R) * kappa_eff(R) / (3.36 * G * Sigma(R))

    Parameters are in SI units (r in m, v in m/s, Sigma in kg/m^2, Rd in m).
    """
    if sigma_R is None:
        sigma_R = sigma_R_jeans(Sigma, Rd)
    ke2 = kappa_eff_sq(r, v, alpha, zeta, proxy_mode)
    ke = np.sqrt(np.maximum(ke2, 0.0))
    with np.errstate(divide='ignore', invalid='ignore'):
        Pi = np.where(Sigma > 0, sigma_R * ke / (3.36 * G_SI * Sigma), np.nan)
    return Pi


def Pi_min_disk_window(r_kpc: NDArray, v_kms: NDArray, Sigma_Msol_pc2: NDArray,
                       Rd_kpc: float, alpha: float,
                       zeta: float = ZETA_DEFAULT,
                       proxy_mode: str = 'v_squared') -> float:
    """Compute Pi_min over the disk window R in [Rd, 3*Rd] (paper prescription).

    Accepts convenient units (kpc, km/s, Msol/pc^2) and converts internally.
    """
    # Unit conversions to SI
    r_si = r_kpc * KPC_M
    v_si = v_kms * KMS_MS
    Sigma_si = Sigma_Msol_pc2 * MSOL_KG / (KPC_M / 1e3)**2  # Msol/pc^2 -> kg/m^2
    Rd_si = Rd_kpc * KPC_M
    Pi = Pi_EFC(r_si, v_si, Sigma_si, Rd_si, alpha, zeta, proxy_mode)
    mask = (r_kpc >= Rd_kpc) & (r_kpc <= 3.0 * Rd_kpc) & np.isfinite(Pi)
    if not np.any(mask):
        return float('nan')
    return float(np.nanmin(Pi[mask]))


# Convenience: Msol/pc^2 -> kg/m^2
MSOL_PC2_TO_SI: float = MSOL_KG / (KPC_M / 1e3)**2


def Pi_proxy(log_Sigma_disk: float, f_gas: float,
             c0: float = 5.0, c1: float = -0.7, c2: float = 0.65) -> float:
    """Linear proxy Pi ~ c0 + c1*log(Sigma) + c2*fgas (indicative only)."""
    return c0 + c1 * log_Sigma_disk + c2 * f_gas


# --------------- self-test ---------------
if __name__ == '__main__':
    # Synthetic tanh rotation curve (NGC 6503-like)
    r_kpc = np.linspace(0.1, 20.0, 200)
    Vflat, Rd = 115.0, 2.5  # km/s, kpc
    v_kms = Vflat * np.tanh(r_kpc / Rd)
    Sigma = 500.0 * np.exp(-r_kpc / Rd)  # Msol/pc^2 exponential disk
    alpha = alpha_from_latency(0.3)
    pmin = Pi_min_disk_window(r_kpc, v_kms, Sigma, Rd, alpha, zeta=1.0)
    print(f"Synthetic galaxy  Vflat={Vflat} km/s  Rd={Rd} kpc")
    print(f"  alpha = {alpha:.2f}   zeta = 1.0")
    print(f"  Pi_min (disk window) = {pmin:.3f}")
    assert 1.0 < pmin < 20.0, f"Pi_min out of expected range: {pmin}"
    print("Self-test PASSED.")
