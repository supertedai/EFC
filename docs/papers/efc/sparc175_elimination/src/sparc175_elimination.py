"""sparc175_elimination.py

Reference implementation of key equations from:
  Magnusson (2026) "Sparc175 Elimination"
  DOI: 10.6084/m9.figshare.32029704

Implements the multiplicative mu-functions, additive dark components,
and the hybrid model for galaxy rotation curves on the SPARC 175 sample.
"""
import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Global constants from the paper
# ---------------------------------------------------------------------------
UPSILON_DISK: float = 0.5    # M_sun / L_sun at 3.6 um
UPSILON_BUL: float = 0.7     # M_sun / L_sun at 3.6 um
SCREENING_K: float = 0.415    # locked power-law index  (Eq 3)
DELTA_AIC_DECISIVE: float = 10.0
SIGMA_FLOOR: float = 1.0      # km/s minimum uncertainty

# ---------------------------------------------------------------------------
# Baryonic velocity (Eq 1)
# ---------------------------------------------------------------------------
def V_baryonic(V_gas: np.ndarray, V_disk: np.ndarray, V_bul: np.ndarray,
               Upsilon_d: float = UPSILON_DISK,
               Upsilon_b: float = UPSILON_BUL) -> np.ndarray:
    """Compute V_bar^2 = V_gas^2 + Upsilon_d * V_disk^2 + Upsilon_b * V_bul^2."""
    Vbar2 = V_gas**2 + Upsilon_d * V_disk**2 + Upsilon_b * V_bul**2
    return np.sqrt(np.maximum(Vbar2, 0.0))


def g_from_V(V: np.ndarray, r: np.ndarray) -> np.ndarray:
    """Centripetal acceleration g = V^2 / r  (units consistent with input)."""
    return V**2 / np.maximum(r, 1e-30)

# ---------------------------------------------------------------------------
# Multiplicative mu-functions
# ---------------------------------------------------------------------------
def mu_bose_einstein(g: np.ndarray, a0: float) -> np.ndarray:
    """Bose-Einstein interpolation function (Eq 2).
    mu_BE = 1 + 1 / (exp(sqrt(g/a0)) - 1)
    """
    x = np.sqrt(np.maximum(g / a0, 0.0))
    denom = np.expm1(x)  # exp(x) - 1
    denom = np.where(np.abs(denom) < 1e-30, 1e-30, denom)
    return 1.0 + 1.0 / denom


def mu_screening(g: np.ndarray, g_dagger: float,
                 k: float = SCREENING_K) -> np.ndarray:
    """Screening / power-law interpolation function (Eq 3).
    mu_scr = 1 + (g_dagger / g)^k
    """
    ratio = g_dagger / np.maximum(g, 1e-30)
    return 1.0 + ratio**k


def mu_regularised_A(g: np.ndarray, a0: float,
                     eps: float = 1e-3) -> np.ndarray:
    """Regularised BE form A: mu = 1 + 1/(exp(sqrt(g/a0)) - 1 + eps)."""
    x = np.sqrt(np.maximum(g / a0, 0.0))
    return 1.0 + 1.0 / (np.expm1(x) + eps)


def mu_gradient(g: np.ndarray, g_dagger: float, Lg: np.ndarray,
               L0: float, beta: float,
               k: float = SCREENING_K) -> np.ndarray:
    """Gradient-dependent mu (Section 2, gradient-dependent).
    mu = mu_scr * [1 + (Lg/L0)^beta]^{-1}
    """
    base = mu_screening(g, g_dagger, k)
    grad_factor = (1.0 + (Lg / L0)**beta)**(-1)
    return base * grad_factor


def mu_surface_density(g: np.ndarray, g_dagger: float,
                       Sigma: np.ndarray, k0: float,
                       k_Sigma: float, log_Sigma0: float,
                       delta: float) -> np.ndarray:
    """Surface-density-dependent mu.
    k_eff = k0 * (1 + k_Sigma * tanh((log Sigma - log Sigma0)/delta))
    mu = (1 + g_dagger/g)^k_eff
    """
    log_S = np.log10(np.maximum(Sigma, 1e-30))
    k_eff = k0 * (1.0 + k_Sigma * np.tanh((log_S - log_Sigma0) / delta))
    ratio = g_dagger / np.maximum(g, 1e-30)
    return (1.0 + ratio)**k_eff

# ---------------------------------------------------------------------------
# Additive dark-component models
# ---------------------------------------------------------------------------
def V2_isothermal(r: np.ndarray, V0: float) -> np.ndarray:
    """Isothermal sphere: V_extra^2 = V0^2."""
    return np.full_like(r, V0**2, dtype=float)


def V2_cored(r: np.ndarray, V0: float, rc: float) -> np.ndarray:
    """Cored halo: V_extra^2 = V0^2 * r^2 / (r^2 + rc^2)."""
    return V0**2 * r**2 / (r**2 + rc**2)


def V2_logarithmic(r: np.ndarray, V0: float, rs: float) -> np.ndarray:
    """Logarithmic halo: V_extra^2 = V0^2 * ln(1 + r/rs)."""
    return V0**2 * np.log(1.0 + r / rs)

# ---------------------------------------------------------------------------
# NFW reference profile (2 params per galaxy: V200, c)
# ---------------------------------------------------------------------------
def V2_nfw(r: np.ndarray, V200: float, c: float) -> np.ndarray:
    """NFW halo rotation curve V^2(r)."""
    r200 = V200 / 1.0  # placeholder normalisation; caller provides physical r200
    # Standard NFW: V^2 = V200^2 * [ln(1+cx)-cx/(1+cx)] / [x*(ln(1+c)-c/(1+c))]
    x = r / (r200 / c * c)  # x = r/r_s where r_s = r200/c
    x = r * c / r200
    fx = np.log(1.0 + x) - x / (1.0 + x)
    fc = np.log(1.0 + c) - c / (1.0 + c)
    return V200**2 * fx / (x * fc + 1e-30)

# ---------------------------------------------------------------------------
# Hybrid model  (Eq 4) — 1 free parameter per galaxy
# ---------------------------------------------------------------------------
def V2_hybrid(r: np.ndarray, Vbar: np.ndarray, g_dagger: float,
              r0: float, A_gal: float,
              k: float = SCREENING_K) -> np.ndarray:
    """Hybrid model (Eq 4).
    V^2 = Vbar^2 * mu_scr(g; g_dagger) + A_gal * r / (r + r0)
    g is derived from Vbar and r.
    """
    g = g_from_V(Vbar, r)
    mu = mu_screening(g, g_dagger, k)
    return Vbar**2 * mu + A_gal * r / (r + r0)


def chi2_per_galaxy(V_obs: np.ndarray, V_model_sq: np.ndarray,
                   sigma_V: np.ndarray) -> float:
    """Reduced chi^2 for one galaxy."""
    sigma = np.maximum(sigma_V, SIGMA_FLOOR)
    V_mod = np.sqrt(np.maximum(V_model_sq, 0.0))
    return float(np.sum(((V_obs - V_mod) / sigma)**2))


def delta_aic(chi2_model: float, chi2_ref: float,
              k_model: int, k_ref: int, n: int) -> float:
    """AIC difference: positive means model is worse than reference."""
    aic_m = chi2_model + 2 * k_model
    aic_r = chi2_ref + 2 * k_ref
    return aic_m - aic_r

# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    r = np.linspace(1.0, 30.0, 50)  # kpc
    Vbar = 80.0 * np.sqrt(r / (r + 5.0))  # toy baryonic curve
    g = g_from_V(Vbar, r)

    a0 = 1.2e-10  # m/s^2 — typical MOND scale
    g_dag = 1.0e-10

    mu_be = mu_bose_einstein(g, a0)
    mu_sc = mu_screening(g, g_dag)
    print("mu_BE  range:", mu_be.min():.4f, mu_be.max():.4f)
    print("mu_scr range:", f"{mu_sc.min():.4f}", f"{mu_sc.max():.4f}")

    V2h = V2_hybrid(r, Vbar, g_dagger=g_dag, r0=3.0, A_gal=500.0)
    print("Hybrid V(r=10 kpc) =", f"{np.sqrt(V2h[np.argmin(np.abs(r-10))]):.2f}", "km/s")
    print("Self-test passed.")
