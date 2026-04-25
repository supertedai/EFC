"""
EFC-C v2.1 pipeline module: layer_analysis.py

Layer A (topological) and Layer B (absolute-scale) tests per PDF v2.1 §3 and §4.5.
"""

import math


def _mean(xs):
    return sum(xs) / len(xs)


def _pearson_r(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = _mean(xs), _mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return 0.0
    return num / (dx * dy)


def _ols_slope(xs, ys):
    """Simple OLS slope through the means."""
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = _mean(xs), _mean(ys)
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((x - mx) ** 2 for x in xs)
    return num / den if den > 0 else 0.0


def run_layer_a(kappa_array, dratio_array,
                gamma_window=(0.5, 0.6),
                gamma_falsification=(0.3, 0.8),
                r_threshold=0.50,
                n_min=30):
    """Layer A test A1: log-log regression of kappa on D_ratio.

    Tests prediction: Delta log kappa = gamma * Delta log D_ratio with slope in [0.5, 0.6].
    Falsification: gamma_hat outside [0.3, 0.8] or r < 0.50 for n >= 30.
    """
    if len(kappa_array) != len(dratio_array):
        raise ValueError("Arrays must have equal length")
    valid = [(k, d) for k, d in zip(kappa_array, dratio_array) if k > 0 and d > 0]
    if len(valid) < 2:
        return {"id": "A1", "passes": False, "reason": "insufficient data"}
    log_k = [math.log(k) for k, _ in valid]
    log_d = [math.log(d) for _, d in valid]
    slope = _ols_slope(log_d, log_k)
    r = _pearson_r(log_d, log_k)
    n = len(valid)
    in_target = gamma_window[0] <= slope <= gamma_window[1]
    in_falsification = gamma_falsification[0] <= slope <= gamma_falsification[1]
    passes = in_falsification and (r >= r_threshold) and (n >= n_min)
    return {
        "id": "A1",
        "n": n,
        "fitted_gamma": slope,
        "r_loglog": r,
        "in_target_window": in_target,
        "in_falsification_window": in_falsification,
        "passes": passes,
    }


def run_layer_b(kappa_obs, kappa_interval=(1.7, 2.6), n=20):
    """Layer B test B1: group-mean kappa within EBE-bounded interval [1.7, 2.6].

    Falsification: group mean outside [1.7, 2.6] for n >= 20.
    """
    lo, hi = kappa_interval
    in_interval = lo <= kappa_obs <= hi
    passes = in_interval and (n >= 20)
    return {
        "id": "B1",
        "kappa_obs": kappa_obs,
        "interval": [lo, hi],
        "in_interval": in_interval,
        "n": n,
        "passes": passes,
    }


def run_alpha_AP_classifier(alpha_AP_scz, alpha_AP_healthy_for_scz,
                             alpha_AP_mdd, alpha_AP_healthy_for_mdd):
    """Layer A tests A2/A3: alpha_AP discriminates schizophrenia (anterior-elevated)
    from MDD (posterior-shifted).
    """
    a2_passes = _mean(alpha_AP_scz) > _mean(alpha_AP_healthy_for_scz)
    a3_passes = _mean(alpha_AP_mdd) < _mean(alpha_AP_healthy_for_mdd)
    return {
        "A2_alpha_AP_scz_gt_healthy": {
            "scz_mean": _mean(alpha_AP_scz),
            "healthy_mean": _mean(alpha_AP_healthy_for_scz),
            "passes": a2_passes,
        },
        "A3_alpha_AP_mdd_lt_healthy": {
            "mdd_mean": _mean(alpha_AP_mdd),
            "healthy_mean": _mean(alpha_AP_healthy_for_mdd),
            "passes": a3_passes,
        },
    }
