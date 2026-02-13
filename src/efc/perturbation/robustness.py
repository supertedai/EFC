"""
EFC Growth-Sector Robustness Utilities
=======================================

Leave-one-out analysis tools and observational data compilations
for the MVP-G1 Hubble-Friction channel.

Reference: Robustness of the EFC Growth-Sector Signal
    DOI: 10.6084/m9.figshare.31332730
"""

import numpy as np


# ── Observational data compilations ──────────────────────────────────────

FSIGMA8_DATA = [
    {"survey": "6dFGS",     "z": 0.02, "fsigma8": 0.360, "error": 0.040},
    {"survey": "SDSS MGS",  "z": 0.15, "fsigma8": 0.490, "error": 0.055},
    {"survey": "BOSS DR12", "z": 0.38, "fsigma8": 0.430, "error": 0.054},
    {"survey": "BOSS DR12", "z": 0.51, "fsigma8": 0.452, "error": 0.057},
    {"survey": "BOSS DR12", "z": 0.61, "fsigma8": 0.457, "error": 0.052},
    {"survey": "VIPERS",    "z": 0.77, "fsigma8": 0.420, "error": 0.060},
    {"survey": "FastSound",  "z": 0.85, "fsigma8": 0.380, "error": 0.080},
]

# N2a nuisance configuration
N2A_PRIORS = {
    "r_d": 147.09,              # Mpc, fixed (Planck 2018)
    "Omega_m": (0.315, 0.007),  # (mean, sigma)
    "sigma_8": (0.81, 0.02),    # (mean, sigma) tight prior
    "H0": (67.4, 0.5),          # km/s/Mpc (mean, sigma)
}

# Reference fit result
REFERENCE_FIT = {
    "alpha": -1.00,
    "sigma": 0.46,
    "significance_sigma": 2.20,
    "delta_AIC": -2.91,
    "delta_BIC": -0.91,
    "p_value_one_sided": 0.028,
}

# LOO results from Table 1
LOO_RESULTS = [
    {"drop": 0, "z": 0.02, "alpha": -0.88, "sigma": 0.48, "significance": 1.84,
     "delta_AIC": -1.59, "delta_BIC": -0.59, "r_alpha_Omega_m": 0.622, "passed": True},
    {"drop": 1, "z": 0.15, "alpha": -1.11, "sigma": 0.46, "significance": 2.42,
     "delta_AIC": -3.97, "delta_BIC": -2.97, "r_alpha_Omega_m": 0.598, "passed": True},
    {"drop": 2, "z": 0.38, "alpha": -0.98, "sigma": 0.46, "significance": 2.12,
     "delta_AIC": -2.58, "delta_BIC": -1.58, "r_alpha_Omega_m": 0.586, "passed": True},
    {"drop": 3, "z": 0.51, "alpha": -1.03, "sigma": 0.47, "significance": 2.22,
     "delta_AIC": -2.97, "delta_BIC": -1.97, "r_alpha_Omega_m": 0.588, "passed": True},
    {"drop": 4, "z": 0.61, "alpha": -1.04, "sigma": 0.48, "significance": 2.19,
     "delta_AIC": -3.20, "delta_BIC": -2.21, "r_alpha_Omega_m": 0.608, "passed": True},
    {"drop": 5, "z": 0.77, "alpha": -1.00, "sigma": 0.47, "significance": 2.12,
     "delta_AIC": -2.70, "delta_BIC": -1.71, "r_alpha_Omega_m": 0.583, "passed": True},
    {"drop": 6, "z": 0.85, "alpha": -0.97, "sigma": 0.46, "significance": 2.09,
     "delta_AIC": -2.54, "delta_BIC": -1.54, "r_alpha_Omega_m": 0.594, "passed": True},
]


# ── Helper functions ─────────────────────────────────────────────────────

def get_fsigma8_arrays():
    """
    Return observational fσ₈ data as numpy arrays.

    Returns
    -------
    dict
        {"z": ndarray, "fsigma8": ndarray, "error": ndarray, "surveys": list}
    """
    return {
        "z": np.array([d["z"] for d in FSIGMA8_DATA]),
        "fsigma8": np.array([d["fsigma8"] for d in FSIGMA8_DATA]),
        "error": np.array([d["error"] for d in FSIGMA8_DATA]),
        "surveys": [d["survey"] for d in FSIGMA8_DATA],
    }


def chi2_fsigma8(model_fsigma8, observed=None):
    """
    Compute χ² for fσ₈ data (diagonal covariance).

    Parameters
    ----------
    model_fsigma8 : array_like
        Model predictions at the 7 data redshifts.
    observed : dict or None
        Observational data (default: FSIGMA8_DATA compilation).

    Returns
    -------
    float
        χ² value.
    """
    if observed is None:
        observed = get_fsigma8_arrays()
    obs = np.asarray(observed["fsigma8"])
    err = np.asarray(observed["error"])
    mod = np.asarray(model_fsigma8)
    return np.sum(((obs - mod) / err) ** 2)


def leave_one_out_indices():
    """
    Generate LOO index sets for the 7 fσ₈ data points.

    Yields
    ------
    tuple
        (drop_index, train_indices) for each LOO iteration.
    """
    n = len(FSIGMA8_DATA)
    for i in range(n):
        train = [j for j in range(n) if j != i]
        yield i, train


def loo_pass_criterion(alpha, sigma, delta_AIC, threshold_sigma=1.7):
    """
    Check if a LOO run passes the robustness criterion.

    Criterion: |α|/σ ≥ threshold AND ΔAIC ≤ 0.

    Parameters
    ----------
    alpha : float
        Best-fit α from LOO run.
    sigma : float
        Uncertainty on α.
    delta_AIC : float
        ΔAIC relative to ΛCDM.
    threshold_sigma : float
        Minimum significance threshold (default 1.7).

    Returns
    -------
    bool
        True if criterion is satisfied.
    """
    return abs(alpha) / sigma >= threshold_sigma and delta_AIC <= 0


def summarise_loo():
    """
    Summarise the LOO robustness results.

    Returns
    -------
    dict
        Summary with pass rate, alpha range, and stability metrics.
    """
    alphas = [r["alpha"] for r in LOO_RESULTS]
    passed = sum(1 for r in LOO_RESULTS if r["passed"])
    correlations = [r["r_alpha_Omega_m"] for r in LOO_RESULTS]

    return {
        "total": len(LOO_RESULTS),
        "passed": passed,
        "pass_rate": passed / len(LOO_RESULTS),
        "alpha_min": min(alphas),
        "alpha_max": max(alphas),
        "alpha_spread": max(alphas) - min(alphas),
        "mean_r_alpha_Omega_m": np.mean(correlations),
        "all_passed": passed == len(LOO_RESULTS),
    }
