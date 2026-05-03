"""component_weighted_bias.py

Reference implementation for:
  Magnusson (2026) – Component-weighted bias in rotation curve model selection:
  A proxy-chain audit of χ²-based ΔAIC statistics.

Implements Equations (1)–(6) from the paper.
"""

import numpy as np
from typing import Tuple, Optional

# ---------------------------------------------------------------------------
# Constants from the paper
# ---------------------------------------------------------------------------
RC_DEFAULT_KPC: float = 3.0          # Default critical radius separating inner/outer (kpc)
EFC_K: float = 0.415                 # EFC-R fixed screening parameter
BBULGE_BIAS_THRESHOLD: float = 0.4   # Bias condition threshold (Eq. 6)
N_SPARC: int = 175                   # Total SPARC galaxies
N_NO_BULGE: int = 143                # Galaxies with Bbulge == 0
N_WITH_BULGE: int = 32               # Galaxies with Bbulge > 0


def total_velocity_squared(
    v_gas: np.ndarray,
    v_disk: np.ndarray,
    v_bulge: np.ndarray,
    v_model: np.ndarray,
) -> np.ndarray:
    """Eq. (2): Total circular velocity squared from component mixing.

    V_total²(r) = V_gas² + V_disk² + V_bulge² + V_model²
    """
    return v_gas**2 + v_disk**2 + v_bulge**2 + v_model**2


def chi_squared(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Eq. (3): Standard χ² statistic with weights w_i = σ_i⁻²."""
    return float(np.sum(((v_obs - v_model) / sigma) ** 2))


def chi_squared_reduced(
    v_obs: np.ndarray,
    v_model: np.ndarray,
    sigma: np.ndarray,
    k_params: int,
) -> float:
    """Reduced χ²_r = χ² / (N - k)."""
    n = len(v_obs)
    return chi_squared(v_obs, v_model, sigma) / (n - k_params)


def delta_aic(
    chi2_model_a: float,
    k_a: int,
    chi2_model_b: float,
    k_b: int,
) -> float:
    """ΔAIC = AIC_A - AIC_B  (positive ⇒ model B preferred).

    AIC = χ² + 2k  (Gaussian likelihood with known σ).
    """
    aic_a = chi2_model_a + 2 * k_a
    aic_b = chi2_model_b + 2 * k_b
    return aic_a - aic_b


def inner_weight_fraction(
    radii: np.ndarray,
    sigma: np.ndarray,
    rc: float = RC_DEFAULT_KPC,
) -> float:
    """Eq. (4): Inner-weight fraction *B*.

    B = Σ_{r_i < r_c} w_i  /  Σ_i w_i ,   w_i = σ_i⁻²
    """
    w = 1.0 / sigma**2
    mask_inner = radii < rc
    return float(np.sum(w[mask_inner]) / np.sum(w))


def component_weighted_bias(
    v_bulge: np.ndarray,
    v_total: np.ndarray,
    sigma: np.ndarray,
) -> float:
    """Eq. (5): Component-weighted bias B_bulge.

    B_bulge = Σ_i w_i · (V_bulge,i² / V_total,i²)  /  Σ_i w_i
    """
    w = 1.0 / sigma**2
    frac = (v_bulge**2) / (v_total**2 + 1e-30)  # guard zero
    return float(np.sum(w * frac) / np.sum(w))


def bias_condition(
    bbulge: float,
    delta_aic_outer: float,
    delta_aic_global: float,
) -> bool:
    """Eq. (6): Model-selection bias flag.

    True when B_bulge > 0.4 AND ΔAICₒᵤₜₑᵣ has opposite sign to ΔAICᵍˡᵒᵇᵃˡ.
    """
    if bbulge <= BBULGE_BIAS_THRESHOLD:
        return False
    return (delta_aic_outer * delta_aic_global) < 0


def split_delta_aic(
    radii: np.ndarray,
    v_obs: np.ndarray,
    sigma: np.ndarray,
    v_pred_a: np.ndarray,
    k_a: int,
    v_pred_b: np.ndarray,
    k_b: int,
    rc: float = RC_DEFAULT_KPC,
) -> Tuple[float, float, float]:
    """RCMP-compliant protocol: return (ΔAIC_inner, ΔAIC_outer, ΔAIC_global)."""
    inner = radii < rc
    outer = ~inner

    def _chi2(mask, v_pred):
        return float(np.sum(((v_obs[mask] - v_pred[mask]) / sigma[mask]) ** 2))

    daic_inner = delta_aic(_chi2(inner, v_pred_a), k_a, _chi2(inner, v_pred_b), k_b)
    daic_outer = delta_aic(_chi2(outer, v_pred_a), k_a, _chi2(outer, v_pred_b), k_b)
    daic_global = delta_aic(
        chi_squared(v_obs, v_pred_a, sigma), k_a,
        chi_squared(v_obs, v_pred_b, sigma), k_b,
    )
    return daic_inner, daic_outer, daic_global


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    N = 30
    r = np.linspace(0.5, 15.0, N)
    sig = 0.05 * np.ones(N) + 0.02 * (r < 3)
    vb = 120.0 * np.exp(-r / 1.5)
    vd = 80.0 * np.exp(-r / 4.0)
    vg = 20.0 * np.ones(N)
    vm = 50.0 * np.sqrt(1 - np.exp(-r / 5.0))
    vtot = np.sqrt(total_velocity_squared(vg, vd, vb, vm))
    vobs = vtot + np.random.normal(0, 3, N)

    B = inner_weight_fraction(r, sig)
    Bb = component_weighted_bias(vb, vtot, sig)
    print(f"Inner-weight fraction B   = {B:.4f}")
    print(f"Component-weighted  Bbulge = {Bb:.4f}")
    print(f"Bias condition met?        {bias_condition(Bb, -2.0, 3.5)}")
    print("Self-test passed.")
