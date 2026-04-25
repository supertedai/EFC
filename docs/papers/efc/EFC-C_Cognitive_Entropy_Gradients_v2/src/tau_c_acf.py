"""
EFC-C v2.1 pipeline module: tau_c_acf.py

Per-subject empirical estimation of cortical entropy redistribution timescale tau_c
via Sokal-window integrated autocorrelation time (PDF v2.1 §4.4).

This converts tau_c from a "free knob" (v2.0 imported from literature) into a
measured covariate. Residual variance enters Layer B falsification bounds.
"""

import math


def autocorrelation(series, lag):
    """Compute autocorrelation at given lag (Pearson normalised)."""
    n = len(series)
    if lag >= n or lag < 0:
        return 0.0
    mean = sum(series) / n
    var = sum((x - mean) ** 2 for x in series)
    if var == 0:
        return 0.0
    cov = sum((series[i] - mean) * (series[i + lag] - mean) for i in range(n - lag))
    return cov / var


def integrated_autocorrelation_time(series, c_window=5.0, max_lag=None):
    """Sokal-window estimator for integrated autocorrelation time tau_int.

    tau_int = 1 + 2 * sum_{k=1}^{M} rho(k), where M is the smallest lag such that
    M >= c_window * tau_int (self-consistent window).

    Parameters
    ----------
    series : list of float
    c_window : float
        Sokal window factor (default 5.0).
    max_lag : int or None
        Maximum lag to consider (default n//4).

    Returns
    -------
    float : tau_int (in units of TR)
    """
    n = len(series)
    if n < 8:
        return 1.0
    if max_lag is None:
        max_lag = n // 4
    tau = 1.0
    rho_sum = 0.0
    for k in range(1, max_lag):
        rho = autocorrelation(series, k)
        if rho < 0:  # truncate at first negative lag
            break
        rho_sum += rho
        tau = 1.0 + 2.0 * rho_sum
        if k >= c_window * tau:
            break
    return tau


def compute_tau_c(bold_timeseries, TR=0.72):
    """Compute subject-level tau_c per PDF v2.1 §4.4 protocol.

    1. For each parcel, compute integrated autocorrelation time tau_ac,i.
    2. Subject-level tau_c = median across parcels.
    3. Returns tau_c in seconds (multiplied by TR).

    Parameters
    ----------
    bold_timeseries : list of list of float
        Per-parcel BOLD signals.
    TR : float
        Repetition time in seconds (default 0.72 for HCP 3T).

    Returns
    -------
    dict : {tau_c_seconds, tau_c_TR, n_parcels, parcel_taus}
    """
    parcel_taus = []
    for series in bold_timeseries:
        tau_int = integrated_autocorrelation_time(series)
        parcel_taus.append(tau_int)
    if not parcel_taus:
        return {"tau_c_seconds": 0.0, "tau_c_TR": 0.0, "n_parcels": 0, "parcel_taus": []}
    sorted_taus = sorted(parcel_taus)
    mid = len(sorted_taus) // 2
    median_tau = (
        sorted_taus[mid] if len(sorted_taus) % 2 == 1
        else (sorted_taus[mid - 1] + sorted_taus[mid]) / 2.0
    )
    return {
        "tau_c_seconds": median_tau * TR,
        "tau_c_TR": median_tau,
        "n_parcels": len(parcel_taus),
        "parcel_taus": parcel_taus,
    }
