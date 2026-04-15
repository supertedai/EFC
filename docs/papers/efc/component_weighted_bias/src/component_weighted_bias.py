"""component_weighted_bias.py

Reference implementation for:
  Magnusson (2026) — Component-weighted bias in rotation curve model selection:
  A proxy-chain audit of χ²-based ΔAIC statistics.

Implements Equations (1)–(6) from the paper plus helper utilities.
"""

import numpy as np
from typing import Tuple, Optional

# --------------- constants from paper ---------------
RC_DEFAULT_KPC: float = 3.0        # default critical radius (kpc) separating inner/outer
EFC_K: float = 0.415               # EFC-R screening parameter calibrated on full SPARC/LSB
BBULGE_BIAS_THRESHOLD: float = 0.4 # Eq. 6 threshold
B_INNER_BIAS_THRESHOLD: float = 0.5
SPARC_TOTAL: int = 175
SPARC_NO_BULGE: int = 143          # 81.7% have Bbulge == 0
SPARC_WITH_BULGE: int = 32
SPEARMAN_RHO_ALL: float = 0.176
SPEARMAN_P_ALL: float = 0.020
SPEARMAN_RHO_LATENT: float = 0.474
SPEARMAN_P_LATENT: float = 0.013
EFC_WIN_LOW_BBULGE: float = 0.919  # 91.9 %  for Bbulge < 0.1
EFC_WIN_HIGH_BBULGE: float = 0.444 # 44.4 %  for Bbulge > 0.2


# --------------- Eq. 2: total circular velocity ---------------
def V_total(V_gas: np.ndarray, V_disk: np.ndarray,
            V_bulge: np.ndarray, V_model: np.ndarray) -> np.ndarray:
    """Eq. 2 — quadrature sum of baryonic components + model (DM / MG / EFC).

    All velocities may be signed; their squares are summed preserving the
    convention V² can be negative for counter-rotating gas.
    """
    return np.sqrt(V_gas**2 + V_disk**2 + V_bulge**2 + V_model**2)


# --------------- Eq. 3: chi-squared ---------------
def chi_squared(V_obs: np.ndarray, V_pred: np.ndarray,
                sigma: np.ndarray) -> float:
    """Eq. 3 — standard χ² statistic."""
    return float(np.sum(((V_obs - V_pred) / sigma) ** 2))


def chi_squared_reduced(V_obs: np.ndarray, V_pred: np.ndarray,
                        sigma: np.ndarray, k_params: int) -> float:
    """Reduced χ²_r = χ² / (N - k)."""
    N = len(V_obs)
    return chi_squared(V_obs, V_pred, sigma) / (N - k_params)


# --------------- AIC helpers ---------------
def aic(chi2: float, k: int, N: int) -> float:
    """AIC = χ² + 2k  (Gaussian-likelihood form, constant term dropped)."""
    return chi2 + 2.0 * k


def delta_aic(chi2_A: float, k_A: int, chi2_B: float, k_B: int, N: int) -> float:
    """ΔAIC = AIC_A − AIC_B.  Negative ⇒ model A preferred."""
    return aic(chi2_A, k_A, N) - aic(chi2_B, k_B, N)


# --------------- Eq. 4: inner-weight fraction B ---------------
def inner_weight_fraction(r: np.ndarray, sigma: np.ndarray,
                          rc: float = RC_DEFAULT_KPC) -> float:
    """Eq. 4 — fraction of total χ² weight carried by r < r_c."""
    w = 1.0 / sigma**2
    mask_inner = r < rc
    return float(np.sum(w[mask_inner]) / np.sum(w))


# --------------- Eq. 5: component-weighted bias Bbulge ---------------
def B_bulge(V_bulge: np.ndarray, V_total_arr: np.ndarray,
            sigma: np.ndarray) -> float:
    """Eq. 5 — weighted average bulge-fraction of χ² weight."""
    w = 1.0 / sigma**2
    frac = V_bulge**2 / np.maximum(V_total_arr**2, 1e-30)
    return float(np.sum(w * frac) / np.sum(w))


# --------------- Eq. 6: bias condition ---------------
def is_model_selection_biased(Bbulge_val: float,
                              delta_aic_outer: float,
                              delta_aic_global: float) -> bool:
    """Eq. 6 — returns True when the fit is structurally biased."""
    opposite_sign = (delta_aic_outer * delta_aic_global) < 0.0
    return (Bbulge_val > BBULGE_BIAS_THRESHOLD) and opposite_sign


# --------------- split ΔAIC (RCMB protocol) ---------------
def split_delta_aic(r: np.ndarray, V_obs: np.ndarray, sigma: np.ndarray,
                    V_pred_A: np.ndarray, V_pred_B: np.ndarray,
                    k_A: int, k_B: int,
                    rc: float = RC_DEFAULT_KPC
                    ) -> Tuple[float, float, float]:
    """Compute ΔAICinner, ΔAICouter, and ΔAICglobal (RCMB-compliant)."""
    inner = r < rc
    outer = ~inner
    N = len(r)
    c2_A_in = chi_squared(V_obs[inner], V_pred_A[inner], sigma[inner])
    c2_B_in = chi_squared(V_obs[inner], V_pred_B[inner], sigma[inner])
    c2_A_out = chi_squared(V_obs[outer], V_pred_A[outer], sigma[outer])
    c2_B_out = chi_squared(V_obs[outer], V_pred_B[outer], sigma[outer])
    c2_A = c2_A_in + c2_A_out
    c2_B = c2_B_in + c2_B_out
    daic_inner = delta_aic(c2_A_in, k_A, c2_B_in, k_B, int(inner.sum()))
    daic_outer = delta_aic(c2_A_out, k_A, c2_B_out, k_B, int(outer.sum()))
    daic_global = delta_aic(c2_A, k_A, c2_B, k_B, N)
    return daic_inner, daic_outer, daic_global


# --------------- self-test ---------------
if __name__ == "__main__":
    np.random.seed(42)
    N = 40
    r = np.linspace(0.5, 20.0, N)
    sigma = np.where(r < 3.0, 3.0, 8.0)  # inner points have smaller errors
    V_gas = 20.0 * np.sqrt(r / 20.0)
    V_disk = 80.0 * np.exp(-r / 8.0)
    V_bulge = 120.0 * np.exp(-r / 1.5)
    V_dm = 150.0 * np.sqrt(1 - np.exp(-r / 5.0))
    V_tot = V_total(V_gas, V_disk, V_bulge, V_dm)
    V_obs = V_tot + np.random.normal(0, sigma)

    B = inner_weight_fraction(r, sigma)
    Bb = B_bulge(V_bulge, V_tot, sigma)
    print(f"Inner-weight fraction  B      = {B:.4f}")
    print(f"Component-weighted bias Bbulge = {Bb:.4f}")
    print(f"Inner-biased (B>0.5)?          {B > B_INNER_BIAS_THRESHOLD}")

    chi2_val = chi_squared(V_obs, V_tot, sigma)
    print(f"χ²                            = {chi2_val:.2f}")
    print(f"χ²_r (k=2)                    = {chi_squared_reduced(V_obs, V_tot, sigma, 2):.4f}")

    # Fake second model with slightly worse outer fit
    V_pred_B = V_tot.copy()
    V_pred_B[r >= 3.0] *= 0.95
    di, do, dg = split_delta_aic(r, V_obs, sigma, V_tot, V_pred_B, 2, 3)
    print(f"ΔAICinner  = {di:+.2f}")
    print(f"ΔAICouter  = {do:+.2f}")
    print(f"ΔAICglobal = {dg:+.2f}")
    biased = is_model_selection_biased(Bb, do, dg)
    print(f"Model-selection biased (Eq. 6)? {biased}")
    print("Self-test passed.")
