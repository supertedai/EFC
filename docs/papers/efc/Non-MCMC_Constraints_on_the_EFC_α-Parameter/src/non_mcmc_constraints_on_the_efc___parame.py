# non_mcmc_constraints_on_the_efc___parame.py
"""
Non-MCMC constraints on the EFC alpha-parameter (Validation Note EFC-VAL-2026-005)

Implements the actual statistical equations used in the paper excerpt:
- Gaussian chi-square evaluation
- Likelihood-ratio as Delta-chi^2
- Akaike Information Criterion (AIC) and Delta AIC
- Reduced chi-square
- k-fold and leave-one-out (LOO) cross-validation tallies
- Significance (z-score) of alpha relative to reference

This module encodes the reported numerical outcomes as constants and
exposes helpers to recompute standard metrics from raw vectors if provided.

Reference:
- Title: Non Mcmc Constraints On The Efc Α Parameter
- DOI: 10.6084/m9.figshare.32101213
- Version: 1.0 (2026-04-26)
- Author: Morten Magnusson (CC BY 4.0)

Note: The excerpt provides non-MCMC summary statistics but does not specify
an explicit forward model for how EFC alpha maps to observables. Accordingly,
this implementation focuses on the actual equations used to compute the
reported metrics (chi-square, Delta-chi^2, AIC, cross-validation tallies),
and registers the paper's numerical results as constants for reproducibility.
"""
from __future__ import annotations

from typing import Iterable, Sequence, Tuple, Dict, List
import numpy as np

# -------------------------------
# Paper-reported constants
# -------------------------------
TITLE: str = "Non Mcmc Constraints On The Efc Α Parameter"
DOI: str = "10.6084/m9.figshare.32101213"
VERSION: str = "1.0"
DATE_ISO: str = "2026-04-26"

# Data-level outcomes (Delta chi^2, AIC, etc.)
DELTA_CHI2_DESI_Y1: float = -22.01  # EFC vs LCDM (EFC preferred)
DELTA_CHI2_BOSS_DR12: float = -7.77  # EFC vs LCDM (keff=0)
DELTA_CHI2_CC_HZ: float = -0.17  # Cosmic chronometer H(z)

# Growth-rate (f sigma8) non-MCMC result
ALPHA_FS8_MEAN: float = -1.00
ALPHA_FS8_SIGMA: float = 0.46
ALPHA_FS8_REPORTED_SIGMA_LEVEL: float = 2.20  # as stated in the note
DELTA_AIC_FS8: float = -2.91
LOO_FS8_N: int = 7
LOO_FS8_VOTES_FOR_EFC: int = 7

# BOSS keff statement
KEFF_BOSS_MINUS_LCDM: int = 0

# IllustrisTNG cluster statistic (proxy data) caveat result
CLUSTERS_TNG_CHI2_REDUCED_APPROX: float = 0.0

# MCMC (degeneracy-limited) posterior summary for alpha
MCMC_ALPHA_MEAN: float = -0.101
MCMC_ALPHA_SIGMA: float = 0.212
MCMC_ALPHA_SIG_LEVEL: float = 0.479
MCMC_DELTA_AIC: float = +1.763
MCMC_CHAIN_DIAG: str = "STOPPED_DEGENERACY_PERSISTS"
MCMC_CONSECUTIVE_RUNS: int = 10

# Pre-registered sealed predictions (two values stated)
SEALED_PREDICTIONS_ALPHA: Tuple[float, float] = (-0.702, -0.689)

# Other numerical statements
NUM_DATASETS_REPORTED: int = 5
CV_FOLDS_DESI: int = 5
DETECTION_THRESHOLD_SIGMA: float = 3.0
FRAMEWORK_TENSION_SIGMA_APPROX: float = 2.8  # MCMC posterior vs same priors
NON_MCMC_VS_PREDICTIONS_AGREEMENT_SIGMA_APPROX: float = 0.7

# -------------------------------
# Core statistical equations
# -------------------------------

def gaussian_chi2(residuals: np.ndarray, cov: np.ndarray | Sequence[float]) -> float:
    """
    Compute Gaussian chi-square: chi2 = r^T C^{-1} r
    - residuals: d - m (shape: N)
    - cov: either a 1D array of standard deviations (sigma) or a 2D covariance matrix (NxN)
    Returns chi2 as a float.
    """
    r = np.asarray(residuals, dtype=float).reshape(-1)
    C = np.asarray(cov, dtype=float)
    if C.ndim == 1:
        sigma = C.reshape(-1)
        if sigma.shape != r.shape:
            raise ValueError("sigma and residuals must have the same length")
        chi2 = float(np.sum((r / sigma) ** 2))
        return chi2
    elif C.ndim == 2:
        if C.shape[0] != C.shape[1] or C.shape[0] != r.size:
            raise ValueError("covariance matrix must be square and match residual length")
        # Solve C x = r, then r^T x
        x = np.linalg.solve(C, r)
        chi2 = float(r @ x)
        return chi2
    else:
        raise ValueError("cov must be 1D (sigma) or 2D (covariance matrix)")


def delta_chi2(chi2_model: float, chi2_reference: float) -> float:
    """Return Delta chi^2 = chi2_model - chi2_reference (negative favors 'model')."""
    return float(chi2_model - chi2_reference)


def aic(chi2: float, k: int) -> float:
    """
    Akaike Information Criterion under Gaussian likelihood: AIC = chi2 + 2k.
    Here chi2 approximates -2 ln L up to an additive constant.
    """
    return float(chi2 + 2 * k)


def delta_aic(chi2_model: float, k_model: int, chi2_reference: float, k_reference: int) -> float:
    """
    Return Delta AIC = AIC(model) - AIC(reference) = (chi2_m - chi2_r) + 2(k_m - k_r).
    Negative values favor 'model'.
    """
    return float((chi2_model - chi2_reference) + 2 * (k_model - k_reference))


def reduced_chi2(chi2: float, dof: int) -> float:
    """Reduced chi-square: chi2_red = chi2 / dof (dof > 0)."""
    if dof <= 0:
        raise ValueError("Degrees of freedom must be positive")
    return float(chi2 / dof)


def significance_z(value: float, sigma: float, reference: float = 0.0) -> float:
    """Return |value - reference| / sigma as a z-score (significance in sigma)."""
    if sigma <= 0:
        raise ValueError("sigma must be positive")
    return float(abs(value - reference) / sigma)


def cv_all_folds_prefer_model(delta_chi2_per_fold: Iterable[float]) -> bool:
    """
    Return True if all folds prefer the model over the reference, i.e., all Delta chi^2 < 0.
    """
    arr = np.asarray(list(delta_chi2_per_fold), dtype=float)
    return bool(np.all(arr < 0))


def loo_votes(delta_chi2_per_epoch: Iterable[float]) -> Tuple[int, int]:
    """
    Count preference votes in Leave-One-Out (LOO):
    - Input is an iterable of Delta chi^2 per held-out epoch (model - reference).
    - Returns (votes_for_model, total_epochs).
    """
    arr = np.asarray(list(delta_chi2_per_epoch), dtype=float)
    return int(np.sum(arr < 0.0)), int(arr.size)


def combine_independent_delta_chi2(deltas: Iterable[float]) -> float:
    """
    For independent datasets, combined evidence (log-likelihood ratio) adds:
    Delta chi^2_combined = sum_i Delta chi^2_i.
    """
    return float(np.sum(np.asarray(list(deltas), dtype=float)))


# -------------------------------
# Paper-specific helpers
# -------------------------------

def paper_reported_combined_delta_chi2(include_hz: bool = True) -> float:
    """
    Combine reported Delta chi^2 across independent datasets that carry weight
    in the note. H(z) is stated as sub-statistical (optional inclusion).
    Always includes the two BAO entries; optionally includes H(z).
    """
    deltas = [DELTA_CHI2_DESI_Y1, DELTA_CHI2_BOSS_DR12]
    if include_hz:
        deltas.append(DELTA_CHI2_CC_HZ)
    return combine_independent_delta_chi2(deltas)


def paper_summary() -> Dict[str, float | int | str]:
    """
    Return a flat summary of the most salient reported numbers plus a few derived checks.
    """
    z_fs8_computed = significance_z(ALPHA_FS8_MEAN, ALPHA_FS8_SIGMA)
    combined_bao_hz = paper_reported_combined_delta_chi2(include_hz=True)
    combined_bao_only = paper_reported_combined_delta_chi2(include_hz=False)
    return {
        "title": TITLE,
        "doi": DOI,
        "version": VERSION,
        "date_iso": DATE_ISO,
        "delta_chi2_desi_y1": DELTA_CHI2_DESI_Y1,
        "delta_chi2_boss_dr12": DELTA_CHI2_BOSS_DR12,
        "delta_chi2_hz": DELTA_CHI2_CC_HZ,
        "combined_delta_chi2_bao_only": combined_bao_only,
        "combined_delta_chi2_bao_plus_hz": combined_bao_hz,
        "alpha_fs8_mean": ALPHA_FS8_MEAN,
        "alpha_fs8_sigma": ALPHA_FS8_SIGMA,
        "alpha_fs8_z_reported": ALPHA_FS8_REPORTED_SIGMA_LEVEL,
        "alpha_fs8_z_computed": z_fs8_computed,
        "delta_aic_fs8": DELTA_AIC_FS8,
        "keff_boss_minus_lcdm": KEFF_BOSS_MINUS_LCDM,
        "mcmc_alpha_mean": MCMC_ALPHA_MEAN,
        "mcmc_alpha_sigma": MCMC_ALPHA_SIGMA,
        "mcmc_alpha_z": MCMC_ALPHA_SIG_LEVEL,
        "mcmc_delta_aic": MCMC_DELTA_AIC,
        "sealed_predictions_alpha_0": SEALED_PREDICTIONS_ALPHA[0],
        "sealed_predictions_alpha_1": SEALED_PREDICTIONS_ALPHA[1],
        "cv_folds_desi": CV_FOLDS_DESI,
        "loo_fs8_votes_for_efc": LOO_FS8_VOTES_FOR_EFC,
        "loo_fs8_total": LOO_FS8_N,
        "clusters_tng_chi2_reduced_approx": CLUSTERS_TNG_CHI2_REDUCED_APPROX,
        "detection_threshold_sigma": DETECTION_THRESHOLD_SIGMA,
        "framework_tension_sigma_approx": FRAMEWORK_TENSION_SIGMA_APPROX,
        "non_mcmc_vs_predictions_agreement_sigma_approx": NON_MCMC_VS_PREDICTIONS_AGREEMENT_SIGMA_APPROX,
    }


# -------------------------------
# Self-test when executed directly
# -------------------------------
if __name__ == "__main__":
    s = paper_summary()

    # Check: fs8 significance roughly matches the reported 2.20 sigma (tolerance ~0.05)
    z_cmp = s["alpha_fs8_z_computed"]
    assert abs(z_cmp - ALPHA_FS8_REPORTED_SIGMA_LEVEL) < 0.05, (
        f"Computed z={z_cmp:.3f} deviates from reported {ALPHA_FS8_REPORTED_SIGMA_LEVEL:.2f}")

    # Check: BOSS keff condition implies Delta AIC equals Delta chi^2
    delta_aic_boss = DELTA_CHI2_BOSS_DR12 + 2 * KEFF_BOSS_MINUS_LCDM
    assert abs(delta_aic_boss - DELTA_CHI2_BOSS_DR12) < 1e-12

    # Check: Combined Delta chi^2 simple sum for independent datasets
    combo = paper_reported_combined_delta_chi2(include_hz=True)
    expected_combo = DELTA_CHI2_DESI_Y1 + DELTA_CHI2_BOSS_DR12 + DELTA_CHI2_CC_HZ
    assert abs(combo - expected_combo) < 1e-12

    # Demonstrate core equations with a tiny synthetic example
    r = np.array([1.0, -2.0, 0.5])
    sigma = np.array([1.0, 2.0, 0.5])
    chi2_val = gaussian_chi2(r, sigma)
    _ = aic(chi2_val, k=1)

    print("Self-test passed. Key summaries:")
    for k in [
        "delta_chi2_desi_y1",
        "delta_chi2_boss_dr12",
        "delta_chi2_hz",
        "combined_delta_chi2_bao_only",
        "combined_delta_chi2_bao_plus_hz",
        "alpha_fs8_mean",
        "alpha_fs8_sigma",
        "alpha_fs8_z_computed",
        "delta_aic_fs8",
    ]:
        print(f"  {k}: {s[k]}")
