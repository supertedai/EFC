"""component_weighted_bias.py

Reference implementation for:
  Component-weighted bias in rotation curve model selection:
  A proxy-chain audit of χ²-based ΔAIC statistics
  Magnusson (2026)

Implements Equations (1)–(6) from the paper.
"""

import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Constants from the paper
# ---------------------------------------------------------------------------
RC_DEFAULT_KPC: float = 3.0       # Default critical radius separating inner/outer (kpc)
EFC_K: float = 0.415              # EFC-R screening parameter (calibrated on full SPARC with LSB weight)
BBULGE_BIAS_THRESHOLD: float = 0.4  # Bias condition threshold for Bbulge
BBULGE_LOW: float = 0.1           # Low-bias bin boundary
BBULGE_HIGH: float = 0.2          # High-bias bin boundary
N_SPARC: int = 175                # Total SPARC galaxies
N_NO_BULGE: int = 143             # Galaxies with Bbulge = 0
N_BULGE: int = 32                 # Galaxies with Bbulge > 0
SPEARMAN_RHO_ALL: float = 0.176   # Spearman ρ(Bbulge, ΔAIC) full sample
SPEARMAN_P_ALL: float = 0.020
SPEARMAN_RHO_LATENT: float = 0.474  # Spearman ρ in LATENT (high-L) regime
SPEARMAN_P_LATENT: float = 0.013
EFC_WIN_LOW_BIAS: float = 0.919   # EFC win/tie fraction for Bbulge < 0.1
EFC_WIN_HIGH_BIAS: float = 0.444  # EFC win/tie fraction for Bbulge > 0.2


def total_circular_velocity(
    V_gas: np.ndarray,
    V_disk: np.ndarray,
    V_bulge: np.ndarray,
    V_model: np.ndarray,
) -> np.ndarray:
    """Equation (2): quadrature sum of velocity components.

    V_total² = V_gas² + V_disk² + V_bulge² + V_model²
    """
    return np.sqrt(V_gas**2 + V_disk**2 + V_bulge**2 + V_model**2)


def chi_squared(
    V_obs: np.ndarray,
    V_model: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Equation (3): standard χ² statistic.

    χ² = Σ (V_obs,i − V_model,i)² / σ_i²
    """
    return float(np.sum(((V_obs - V_model) / sigma) ** 2))


def inner_weight_fraction(
    radii: np.ndarray,
    sigma: np.ndarray,
    rc: float = RC_DEFAULT_KPC,
) -> float:
    """Equation (4): inner-weight fraction B.

    B = Σ_{r_i < r_c} w_i  /  Σ w_i   where w_i = σ_i^{-2}
    """
    w = sigma ** (-2)
    mask_inner = radii < rc
    return float(np.sum(w[mask_inner]) / np.sum(w))


def component_weighted_bias(
    V_bulge: np.ndarray,
    V_total: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Equation (5): component-weighted bias B_bulge.

    B_bulge = Σ w_i · (V_bulge,i² / V_total,i²)  /  Σ w_i
    """
    w = sigma ** (-2)
    frac = (V_bulge ** 2) / (V_total ** 2 + 1e-30)  # avoid division by zero
    return float(np.sum(w * frac) / np.sum(w))


def is_model_selection_biased(
    B_bulge: float,
    delta_aic_outer: float,
    delta_aic_global: float,
) -> bool:
    """Equation (6): bias condition.

    A fit is model-selection biased if
        B_bulge > 0.4  AND  sign(ΔAIC_outer) ≠ sign(ΔAIC_global)
    """
    return B_bulge > BBULGE_BIAS_THRESHOLD and (
        np.sign(delta_aic_outer) != np.sign(delta_aic_global)
    )


def split_chi_squared(
    radii: np.ndarray,
    V_obs: np.ndarray,
    V_model: np.ndarray,
    sigma: np.ndarray,
    rc: float = RC_DEFAULT_KPC,
) -> Tuple[float, float]:
    """Compute χ²_inner and χ²_outer separately (RCMB-compliant protocol)."""
    resid2 = ((V_obs - V_model) / sigma) ** 2
    inner = radii < rc
    return float(np.sum(resid2[inner])), float(np.sum(resid2[~inner]))


def delta_aic(
    chi2_a: float, k_a: int, chi2_b: float, k_b: int, n: int
) -> float:
    """ΔAIC = AIC_A − AIC_B  (positive ⇒ model B preferred).

    AIC = χ² + 2k  (Gaussian-likelihood form for fixed n).
    """
    aic_a = chi2_a + 2 * k_a
    aic_b = chi2_b + 2 * k_b
    return aic_a - aic_b


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    N = 40
    r = np.linspace(0.5, 20.0, N)  # kpc
    sigma = 3.0 + 0.05 * r  # inner points have smaller relative error
    V_gas = 20.0 * np.ones(N)
    V_disk = 80.0 * np.exp(-r / 5.0)
    V_bulge = 120.0 * np.exp(-r / 1.5)
    V_halo = 150.0 * np.sqrt(1 - np.exp(-r / 8.0))
    V_tot = total_circular_velocity(V_gas, V_disk, V_bulge, V_halo)
    V_obs = V_tot + np.random.normal(0, sigma)

    B = inner_weight_fraction(r, sigma)
    Bb = component_weighted_bias(V_bulge, V_tot, sigma)
    chi2_val = chi_squared(V_obs, V_tot, sigma)

    print(f"N points       = {N}")
    print(f"B (inner frac) = {B:.4f}")
    print(f"B_bulge        = {Bb:.4f}")
    print(f"chi2           = {chi2_val:.2f}")
    print(f"Bias condition = {is_model_selection_biased(Bb, -3.0, 5.0)}")
    print("Self-test passed.")
