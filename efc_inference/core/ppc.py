"""
Posterior Predictive Checks (PPC) for EFC inference.

Validates model fit quality:
- Residual analysis (normalized residuals, distribution)
- Calibration check (fraction within N-sigma bands)
- Bayesian p-value (tail probability)

Supports both diagonal errors and full covariance matrices.
When a module has a _covariance attribute, residuals are Cholesky-whitened
so that they are N(0,1) distributed for a good fit.
"""

import numpy as np
from typing import Optional


def normalized_residuals(observed: np.ndarray, predicted: np.ndarray,
                         errors: np.ndarray) -> np.ndarray:
    """(obs - pred) / err — should be N(0,1) for good fit."""
    return (observed - predicted) / errors


def whitened_residuals(observed: np.ndarray, predicted: np.ndarray,
                       cov: np.ndarray) -> np.ndarray:
    """
    Cholesky-whitened residuals: L^{-1}(obs - pred).

    For a correct model with covariance C = L L^T, the whitened
    residuals w = L^{-1} r should be N(0, I) distributed.

    Parameters:
        observed:  (N,) observed data
        predicted: (N,) model predictions
        cov:       (N, N) covariance matrix

    Returns:
        (N,) whitened residuals — should be N(0,1) for good fit.
    """
    residuals = observed - predicted
    try:
        L = np.linalg.cholesky(cov)
        return np.linalg.solve(L, residuals)
    except np.linalg.LinAlgError:
        # Fallback to diagonal
        return residuals / np.sqrt(np.diag(cov))


def residual_statistics(residuals: np.ndarray) -> dict:
    """Summary statistics of normalized residuals."""
    return {
        "mean": float(np.mean(residuals)),
        "std": float(np.std(residuals)),
        "skewness": float(_skewness(residuals)),
        "kurtosis": float(_kurtosis(residuals)),
        "max_abs": float(np.max(np.abs(residuals))),
        "n_outliers_3sigma": int(np.sum(np.abs(residuals) > 3.0)),
    }


def calibration_check(residuals: np.ndarray) -> dict:
    """
    Fraction of residuals within 1, 2, 3 sigma bands.
    Expected: 68.3%, 95.4%, 99.7%.
    """
    n = len(residuals)
    abs_r = np.abs(residuals)
    return {
        "within_1sigma": float(np.sum(abs_r <= 1.0) / n),
        "within_2sigma": float(np.sum(abs_r <= 2.0) / n),
        "within_3sigma": float(np.sum(abs_r <= 3.0) / n),
        "expected_1sigma": 0.6827,
        "expected_2sigma": 0.9545,
        "expected_3sigma": 0.9973,
    }


def bayesian_p_value(observed: np.ndarray, predicted_samples: np.ndarray,
                     errors: np.ndarray,
                     cov: Optional[np.ndarray] = None) -> float:
    """
    Bayesian p-value: fraction of posterior predictive samples
    with chi2 >= observed chi2.

    Parameters:
        observed:          (N_data,) array
        predicted_samples: (N_posterior, N_data) array — model predictions
                           from posterior samples
        errors:            (N_data,) measurement uncertainties (diagonal)
        cov:               (N_data, N_data) optional full covariance matrix

    Returns:
        p-value in [0, 1]. Values near 0.5 indicate good fit.
    """
    if cov is not None:
        # Full covariance path
        try:
            L = np.linalg.cholesky(cov)
            L_inv_func = lambda r: np.linalg.solve(L, r)
        except np.linalg.LinAlgError:
            # Fallback to diagonal
            diag_err = np.sqrt(np.diag(cov))
            L = np.diag(diag_err)
            L_inv_func = lambda r: r / diag_err

        mean_pred = np.mean(predicted_samples, axis=0)
        w_obs = L_inv_func(observed - mean_pred)
        chi2_obs = np.dot(w_obs, w_obs)

        n_exceed = 0
        n_data = len(observed)
        for pred in predicted_samples:
            rep = pred + L @ np.random.randn(n_data)
            w_rep = L_inv_func(rep - pred)
            chi2_rep = np.dot(w_rep, w_rep)
            if chi2_rep >= chi2_obs:
                n_exceed += 1
    else:
        # Diagonal path (original)
        chi2_obs = np.sum(((observed - np.mean(predicted_samples, axis=0)) / errors) ** 2)

        n_exceed = 0
        for pred in predicted_samples:
            rep = pred + errors * np.random.randn(len(errors))
            chi2_rep = np.sum(((rep - pred) / errors) ** 2)
            if chi2_rep >= chi2_obs:
                n_exceed += 1

    return n_exceed / len(predicted_samples)


def ppc_report(module, params_dict: dict,
               posterior_samples: Optional[np.ndarray] = None,
               n_ppc_samples: int = 200) -> dict:
    """
    Full PPC report for a module.

    Automatically detects covariance-aware modules (those with _covariance
    attribute) and uses Cholesky-whitened residuals + covariance chi2.

    Parameters:
        module:            An inference module with predict() and data
        params_dict:       Best-fit or median parameters
        posterior_samples: (N, ndim) posterior samples for Bayesian p-value
        n_ppc_samples:     Number of samples for p-value computation

    Returns:
        Dict with residual stats, calibration, and p-value.
    """
    # Use ppc_predict() if available (handles nuisance params like M_B),
    # otherwise fall back to predict().
    _predict = getattr(module, "ppc_predict", module.predict)
    predicted = _predict(params_dict)
    observed = module.observed
    errors = module.errors
    cov = getattr(module, "_covariance", None)

    # Compute residuals — whitened if covariance is available
    if cov is not None:
        resid = whitened_residuals(observed, predicted, cov)
    else:
        resid = normalized_residuals(observed, predicted, errors)

    stats = residual_statistics(resid)
    cal = calibration_check(resid)

    # Chi-squared — covariance-aware if available
    n_params = len([k for k in params_dict if not k.startswith("_")])
    if cov is not None:
        from .likelihoods import chi2_reduced_covariance
        chi2_red = chi2_reduced_covariance(observed, predicted, cov, n_params)
    else:
        from .likelihoods import chi2_reduced
        chi2_red = chi2_reduced(observed, predicted, errors, n_params)

    result = {
        "chi2_reduced": float(chi2_red),
        "residuals": stats,
        "calibration": cal,
        "covariance_aware": cov is not None,
    }

    # Bayesian p-value from posterior samples
    if posterior_samples is not None and len(posterior_samples) > 0:
        n_use = min(n_ppc_samples, len(posterior_samples))
        idx = np.random.choice(len(posterior_samples), n_use, replace=False)
        pred_samples = np.array([_predict(
            module._params_from_array(posterior_samples[i]))
            for i in idx])
        p_val = bayesian_p_value(observed, pred_samples, errors, cov=cov)
        result["bayesian_p_value"] = float(p_val)

    return result


# ═══════════════════════════════════════════════════════════════
#  PPC VERDICT — deterministic pass/fail (Fase 2)
# ═══════════════════════════════════════════════════════════════

def ppc_verdict(report: dict, policy_config) -> dict:
    """
    Deterministic PPC pass/fail based on policy thresholds.

    Parameters:
        report:        Output of ppc_report() — chi2_reduced, residuals, calibration, bayesian_p_value
        policy_config: PPCGateConfig with threshold fields

    Returns:
        {"passed": bool, "checks": {name: {passed, value, threshold, ...}}, "reason": str}
    """
    checks = {}
    failures = []

    # 1. Reduced chi-squared
    chi2_r = report.get("chi2_reduced", 999.0)
    ok = chi2_r <= policy_config.chi2_red_max
    checks["chi2_reduced"] = {"passed": ok, "value": round(chi2_r, 4),
                               "threshold": policy_config.chi2_red_max}
    if not ok:
        failures.append(f"chi2_red={chi2_r:.2f} > {policy_config.chi2_red_max}")

    # 2. Bayesian p-value (if computed)
    if "bayesian_p_value" in report:
        p = report["bayesian_p_value"]
        ok = policy_config.p_value_lo <= p <= policy_config.p_value_hi
        checks["bayesian_p_value"] = {
            "passed": ok, "value": round(p, 4),
            "bounds": [policy_config.p_value_lo, policy_config.p_value_hi],
        }
        if not ok:
            failures.append(
                f"p_value={p:.3f} outside [{policy_config.p_value_lo}, {policy_config.p_value_hi}]"
            )

    # 3. Calibration — 1σ band
    cal = report.get("calibration", {})
    obs_1s = cal.get("within_1sigma", 0.0)
    exp_1s = cal.get("expected_1sigma", 0.6827)
    delta = abs(obs_1s - exp_1s)
    ok = delta <= policy_config.calibration_1sigma_tol
    checks["calibration_1sigma"] = {
        "passed": ok, "value": round(obs_1s, 4),
        "expected": exp_1s, "delta": round(delta, 4),
        "tolerance": policy_config.calibration_1sigma_tol,
    }
    if not ok:
        failures.append(
            f"cal_1sigma={obs_1s:.3f} (delta={delta:.3f} > {policy_config.calibration_1sigma_tol})"
        )

    # 4. 3σ outliers
    resid = report.get("residuals", {})
    n_out = resid.get("n_outliers_3sigma", 0)
    ok = n_out <= policy_config.max_outliers_3sigma
    checks["outliers_3sigma"] = {"passed": ok, "value": n_out,
                                  "threshold": policy_config.max_outliers_3sigma}
    if not ok:
        failures.append(f"outliers={n_out} > {policy_config.max_outliers_3sigma}")

    # 5. Residual std
    r_std = resid.get("std", 0.0)
    ok = r_std <= policy_config.residual_std_max
    checks["residual_std"] = {"passed": ok, "value": round(r_std, 4),
                               "threshold": policy_config.residual_std_max}
    if not ok:
        failures.append(f"resid_std={r_std:.3f} > {policy_config.residual_std_max}")

    passed = len(failures) == 0
    reason = "ALL_PASSED" if passed else "; ".join(failures)
    return {"passed": passed, "checks": checks, "reason": reason}


def _skewness(x: np.ndarray) -> float:
    n = len(x)
    if n < 3:
        return 0.0
    m = np.mean(x)
    s = np.std(x, ddof=1)
    if s == 0:
        return 0.0
    return np.mean(((x - m) / s) ** 3)


def _kurtosis(x: np.ndarray) -> float:
    n = len(x)
    if n < 4:
        return 0.0
    m = np.mean(x)
    s = np.std(x, ddof=1)
    if s == 0:
        return 0.0
    return np.mean(((x - m) / s) ** 4) - 3.0
