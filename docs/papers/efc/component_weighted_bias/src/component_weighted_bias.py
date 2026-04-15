"""component_weighted_bias.py

Reference implementation for:
  Magnusson (2026) – Component-weighted bias in rotation curve model selection:
  A proxy-chain audit of χ²-based ΔAIC statistics.

Key equations:
  Eq 2: V²_total = V²_gas + V²_disk + V²_bulge + V²_model
  Eq 3: χ² = Σ (V_obs,i - V_model,i)² / σ_i²
  Eq 4: B = Σ_{r_i < r_c} w_i / Σ w_i           (inner-weight fraction)
  Eq 5: B_bulge = Σ w_i·(V²_bulge,i/V²_total,i) / Σ w_i  (component-weighted bias)
  Eq 6: Bias condition: B_bulge > 0.4 AND sign(ΔAIC_outer) ≠ sign(ΔAIC_global)
"""

import numpy as np
from typing import Tuple, Optional

# ---------- Constants from the paper ----------
RC_DEFAULT_KPC: float = 3.0        # critical radius separating inner/outer [kpc]
EFC_K: float = 0.415               # EFC screening parameter (calibrated on full SPARC, LSB weight)
BBULGE_THRESHOLD_LOW: float = 0.1  # below this, EFC wins/ties 91.9 %
BBULGE_THRESHOLD_HIGH: float = 0.2 # above this, EFC wins/ties 44.4 %
BBULGE_BIAS_CUTOFF: float = 0.4   # Eq 6 threshold
SPARC_TOTAL: int = 175
SPARC_NO_BULGE: int = 143          # 81.7 % have B_bulge = 0
SPARC_WITH_BULGE: int = 32
SPEARMAN_RHO_ALL: float = 0.176
SPEARMAN_P_ALL: float = 0.020
SPEARMAN_RHO_LATENT: float = 0.474
SPEARMAN_P_LATENT: float = 0.013
EFC_WIN_LOW_BBULGE: float = 0.919  # fraction where EFC wins/ties when B_bulge < 0.1
EFC_WIN_HIGH_BBULGE: float = 0.444 # fraction where EFC wins/ties when B_bulge > 0.2


def total_velocity_squared(
    v_gas: np.ndarray,
    v_disk: np.ndarray,
    v_bulge: np.ndarray,
    v_model: np.ndarray,
) -> np.ndarray:
    """Eq 2: V²_total = V²_gas + V²_disk + V²_bulge + V²_model."""
    return v_gas**2 + v_disk**2 + v_bulge**2 + v_model**2


def chi_squared(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Eq 3: χ² = Σ (V_obs,i - V_model,i)² / σ_i²."""
    return float(np.sum(((v_obs - v_model) / sigma) ** 2))


def weights(sigma: np.ndarray) -> np.ndarray:
    """Compute inverse-variance weights w_i = 1/σ_i²."""
    return 1.0 / sigma**2


def inner_weight_fraction(
    radii: np.ndarray,
    sigma: np.ndarray,
    rc: float = RC_DEFAULT_KPC,
) -> float:
    """Eq 4: B = Σ_{r_i < r_c} w_i  /  Σ w_i."""
    w = weights(sigma)
    mask_inner = radii < rc
    return float(np.sum(w[mask_inner]) / np.sum(w))


def component_weighted_bias(
    v_bulge: np.ndarray,
    v_total: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Eq 5: B_bulge = Σ w_i·(V²_bulge,i / V²_total,i) / Σ w_i.

    Parameters
    ----------
    v_bulge : array – bulge circular-velocity component [km/s]
    v_total : array – total observed circular velocity [km/s]
    sigma   : array – measurement uncertainties [km/s]

    Returns
    -------
    B_bulge : float in [0, 1]
    """
    w = weights(sigma)
    frac = np.where(v_total != 0, (v_bulge / v_total) ** 2, 0.0)
    return float(np.sum(w * frac) / np.sum(w))


def bias_condition(
    bbulge: float,
    delta_aic_outer: float,
    delta_aic_global: float,
) -> bool:
    """Eq 6: model-selection biased if B_bulge > 0.4 AND
    sign(ΔAIC_outer) ≠ sign(ΔAIC_global)."""
    if bbulge <= BBULGE_BIAS_CUTOFF:
        return False
    return np.sign(delta_aic_outer) != np.sign(delta_aic_global)


def delta_aic(
    chi2_model_a: float,
    k_a: int,
    chi2_model_b: float,
    k_b: int,
) -> float:
    """ΔAIC = AIC_A - AIC_B = (χ²_A + 2k_A) - (χ²_B + 2k_B)."""
    aic_a = chi2_model_a + 2.0 * k_a
    aic_b = chi2_model_b + 2.0 * k_b
    return aic_a - aic_b


def split_chi_squared(
    radii: np.ndarray,
    v_obs: np.ndarray,
    v_model: np.ndarray,
    sigma: np.ndarray,
    rc: float = RC_DEFAULT_KPC,
) -> Tuple[float, float]:
    """Return (χ²_inner, χ²_outer) split at critical radius rc."""
    residuals_sq = ((v_obs - v_model) / sigma) ** 2
    inner = radii < rc
    return float(np.sum(residuals_sq[inner])), float(np.sum(residuals_sq[~inner]))


# ---------- Self-test ----------
if __name__ == "__main__":
    np.random.seed(42)
    N = 40
    r = np.linspace(0.5, 20.0, N)
    sigma = np.where(r < 3.0, 3.0, 8.0)
    v_bulge = 120.0 * np.exp(-r / 2.0)
    v_disk = 80.0 * np.sqrt(r / 5.0) * np.exp(-r / 10.0)
    v_gas = 30.0 * np.ones(N)
    v_model = 50.0 * np.sqrt(1 - np.exp(-r / 4.0))
    v_total = np.sqrt(total_velocity_squared(v_gas, v_disk, v_bulge, v_model))
    v_obs = v_total + np.random.normal(0, sigma * 0.3)

    B = inner_weight_fraction(r, sigma)
    Bb = component_weighted_bias(v_bulge, v_total, sigma)
    c2 = chi_squared(v_obs, v_total, sigma)
    c2_in, c2_out = split_chi_squared(r, v_obs, v_total, sigma)

    print(f"N points          = {N}")
    print(f"B (inner-weight)  = {B:.4f}")
    print(f"B_bulge           = {Bb:.4f}")
    print(f"χ² total          = {c2:.2f}")
    print(f"χ² inner / outer  = {c2_in:.2f} / {c2_out:.2f}")
    print(f"Bias condition    = {bias_condition(Bb, -2.0, 3.0)}")
    print("Self-test passed.")
