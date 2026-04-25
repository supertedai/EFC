"""
EFC-C v2.1 pipeline module: entropy_mse.py

Computes per-parcel multiscale sample entropy S_i and centrifugal entropy score kappa.

PDF v2.1 §4.3: MSE on ICA-FIX-denoised BOLD, scales 4-6, averaged per parcel.
"""

import math


def sample_entropy(series, m=2, r_factor=0.2):
    """Sample entropy SampEn(series, m, r) where r = r_factor * std(series).

    Parameters
    ----------
    series : list of float
        Time series.
    m : int
        Embedding dimension (default 2).
    r_factor : float
        Tolerance as fraction of std (default 0.2).
    """
    n = len(series)
    if n < m + 2:
        return 0.0
    mean = sum(series) / n
    var = sum((x - mean) ** 2 for x in series) / n
    std = math.sqrt(var) if var > 0 else 1.0
    r = r_factor * std

    def _count_matches(template_len):
        count = 0
        templates = [series[i : i + template_len] for i in range(n - template_len + 1)]
        for i in range(len(templates)):
            for j in range(i + 1, len(templates)):
                if all(abs(templates[i][k] - templates[j][k]) <= r for k in range(template_len)):
                    count += 1
        return count

    B = _count_matches(m)
    A = _count_matches(m + 1)
    if B == 0:
        return 0.0
    return -math.log(A / B) if A > 0 else float("inf")


def coarse_grain(series, scale):
    """Coarse-grain series at given scale (non-overlapping average)."""
    n = len(series) // scale
    return [sum(series[i * scale : (i + 1) * scale]) / scale for i in range(n)]


def multiscale_sample_entropy(series, scales=(4, 5, 6)):
    """Multiscale sample entropy averaged over given scales (PDF v2.1 §4.3)."""
    if not series or len(series) < max(scales) * 4:
        return 0.0
    mse_values = []
    for s in scales:
        cg = coarse_grain(series, s)
        if len(cg) >= 4:
            mse_values.append(sample_entropy(cg))
    return sum(mse_values) / len(mse_values) if mse_values else 0.0


def compute_mse_kappa(bold_timeseries, hub_indices, periph_indices, scales=(4, 5, 6)):
    """Compute centrifugal entropy score kappa from per-parcel BOLD time series.

    Parameters
    ----------
    bold_timeseries : list of list of float
        Per-parcel BOLD signals; bold_timeseries[i] is parcel i's time series.
    hub_indices : list of int
    periph_indices : list of int
    scales : tuple of int
        MSE scales (default 4-6 per PDF v2.1).

    Returns
    -------
    dict : {kappa, S_hub_mean, S_periph_mean, n_hub, n_periph}
    """
    S_hub = [multiscale_sample_entropy(bold_timeseries[i], scales) for i in hub_indices]
    S_periph = [multiscale_sample_entropy(bold_timeseries[i], scales) for i in periph_indices]
    mean_hub = sum(S_hub) / len(S_hub) if S_hub else 0.0
    mean_periph = sum(S_periph) / len(S_periph) if S_periph else 0.0
    return {
        "kappa": mean_hub / mean_periph if mean_periph > 0 else float("inf"),
        "S_hub_mean": mean_hub,
        "S_periph_mean": mean_periph,
        "n_hub": len(S_hub),
        "n_periph": len(S_periph),
        "scales": list(scales),
    }
