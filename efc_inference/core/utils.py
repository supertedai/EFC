"""
Utility functions for EFC inference.

- log-sum-exp
- convergence diagnostics (Gelman-Rubin, autocorrelation)
- chain analysis helpers
"""

import numpy as np
from typing import Optional


def log_sum_exp(log_values: np.ndarray) -> float:
    """Numerically stable log-sum-exp."""
    max_val = np.max(log_values)
    if not np.isfinite(max_val):
        return -np.inf
    return max_val + np.log(np.sum(np.exp(log_values - max_val)))


def gelman_rubin(chains: np.ndarray) -> np.ndarray:
    """
    Gelman-Rubin R-hat diagnostic for convergence.

    Parameters:
        chains: (n_walkers, n_steps, n_params) array

    Returns:
        R-hat per parameter. Values < 1.1 indicate convergence.
    """
    n_chains, n_steps, n_params = chains.shape
    if n_steps < 2:
        return np.full(n_params, np.inf)

    chain_means = np.mean(chains, axis=1)  # (n_chains, n_params)
    chain_vars = np.var(chains, axis=1, ddof=1)  # (n_chains, n_params)

    overall_mean = np.mean(chain_means, axis=0)  # (n_params,)

    B = n_steps * np.var(chain_means, axis=0, ddof=1)  # between-chain
    W = np.mean(chain_vars, axis=0)  # within-chain

    var_hat = ((n_steps - 1) / n_steps) * W + (1.0 / n_steps) * B
    r_hat = np.sqrt(var_hat / np.where(W > 0, W, 1e-30))

    return r_hat


def autocorrelation_time(chain: np.ndarray, c: float = 5.0) -> float:
    """
    Estimate integrated autocorrelation time for a 1D chain.

    Uses the method from Goodman & Weare (2010).

    Parameters:
        chain: (n_steps,) array
        c: window factor (default 5.0)

    Returns:
        Estimated autocorrelation time (float).
    """
    n = len(chain)
    if n < 10:
        return np.inf

    # Normalize
    x = chain - np.mean(chain)
    norm = np.sum(x**2)
    if norm == 0:
        return np.inf

    # FFT-based autocorrelation
    f = np.fft.fft(x, n=2 * n)
    acf = np.fft.ifft(f * np.conj(f))[:n].real
    acf /= acf[0]

    # Integrate with window
    tau = 1.0
    for i in range(1, n):
        tau += 2.0 * acf[i]
        if i >= c * tau:
            break

    return tau


def effective_sample_size(chains: np.ndarray) -> np.ndarray:
    """
    Effective sample size per parameter.

    Parameters:
        chains: (n_walkers, n_steps, n_params)

    Returns:
        ESS per parameter (n_params,)
    """
    n_walkers, n_steps, n_params = chains.shape
    ess = np.zeros(n_params)

    for j in range(n_params):
        taus = []
        for i in range(n_walkers):
            tau = autocorrelation_time(chains[i, :, j])
            if np.isfinite(tau):
                taus.append(tau)
        if taus:
            mean_tau = np.mean(taus)
            ess[j] = n_walkers * n_steps / max(mean_tau, 1.0)
        else:
            ess[j] = 0.0

    return ess


def summary_statistics(flat_chain: np.ndarray,
                       param_names: Optional[list[str]] = None) -> dict:
    """
    Compute summary statistics from flattened posterior samples.

    Parameters:
        flat_chain: (n_samples, n_params)
        param_names: optional list of names

    Returns:
        Dict with median, mean, std, 16th/84th percentiles per parameter.
    """
    n_params = flat_chain.shape[1]
    if param_names is None:
        param_names = [f"p{i}" for i in range(n_params)]

    stats = {}
    for i, name in enumerate(param_names):
        samples = flat_chain[:, i]
        p16, p50, p84 = np.percentile(samples, [16, 50, 84])
        stats[name] = {
            "median": float(p50),
            "mean": float(np.mean(samples)),
            "std": float(np.std(samples)),
            "lo_1sigma": float(p16),
            "hi_1sigma": float(p84),
            "err_minus": float(p50 - p16),
            "err_plus": float(p84 - p50),
        }
    return stats
