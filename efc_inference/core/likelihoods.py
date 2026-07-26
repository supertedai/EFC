"""
Likelihood functions for EFC inference.

Supports:
- Chi-squared (diagonal errors)
- Gaussian with full covariance matrix
"""

import numpy as np
from typing import Optional


def log_likelihood_chi2(observed: np.ndarray, predicted: np.ndarray,
                        errors: np.ndarray) -> float:
    """
    Standard chi-squared log-likelihood (diagonal covariance).

    L = -0.5 * sum((obs - pred)^2 / err^2 + log(2*pi*err^2))

    Parameters:
        observed:  (N,) observed data values
        predicted: (N,) model predictions
        errors:    (N,) 1-sigma measurement uncertainties

    Returns:
        log-likelihood (float)
    """
    if np.any(errors <= 0):
        return -np.inf

    residuals = observed - predicted
    chi2 = np.sum((residuals / errors) ** 2)
    log_det = np.sum(np.log(2 * np.pi * errors**2))
    return -0.5 * (chi2 + log_det)


def log_likelihood_covariance(observed: np.ndarray, predicted: np.ndarray,
                              cov: np.ndarray) -> float:
    """
    Full covariance matrix log-likelihood.

    L = -0.5 * (r^T C^{-1} r + log|C| + N*log(2*pi))

    Parameters:
        observed:  (N,) observed data
        predicted: (N,) model predictions
        cov:       (N, N) covariance matrix

    Returns:
        log-likelihood (float)
    """
    n = len(observed)
    residuals = observed - predicted

    try:
        L = np.linalg.cholesky(cov)
    except np.linalg.LinAlgError:
        return -np.inf

    # Solve L * x = residuals for x
    alpha = np.linalg.solve(L, residuals)
    chi2 = np.dot(alpha, alpha)

    log_det = 2.0 * np.sum(np.log(np.diag(L)))

    return -0.5 * (chi2 + log_det + n * np.log(2 * np.pi))


def chi2_reduced_covariance(observed: np.ndarray, predicted: np.ndarray,
                            cov: np.ndarray, n_params: int) -> float:
    """
    Reduced chi-squared with full covariance matrix.

    chi2_red = r^T C^{-1} r / (N - n_params)

    Uses Cholesky decomposition for numerical stability.
    Falls back to diagonal if Cholesky fails.
    """
    residuals = observed - predicted
    try:
        L = np.linalg.cholesky(cov)
        alpha = np.linalg.solve(L, residuals)
        chi2 = np.dot(alpha, alpha)
    except np.linalg.LinAlgError:
        # Fallback to diagonal
        chi2 = np.sum((residuals / np.sqrt(np.diag(cov))) ** 2)
    dof = len(observed) - n_params
    if dof <= 0:
        return np.inf
    return chi2 / dof


def chi2_reduced(observed: np.ndarray, predicted: np.ndarray,
                 errors: np.ndarray, n_params: int) -> float:
    """
    Reduced chi-squared: chi2 / (N - n_params).

    Returns:
        chi2_red (float). Values near 1.0 indicate good fit.
    """
    residuals = observed - predicted
    chi2 = np.sum((residuals / errors) ** 2)
    dof = len(observed) - n_params
    if dof <= 0:
        return np.inf
    return chi2 / dof


def aic(log_like: float, n_params: int) -> float:
    """Akaike Information Criterion: AIC = -2*logL + 2*k"""
    return -2.0 * log_like + 2.0 * n_params


def bic(log_like: float, n_params: int, n_data: int) -> float:
    """Bayesian Information Criterion: BIC = -2*logL + k*log(N)"""
    return -2.0 * log_like + n_params * np.log(n_data)
