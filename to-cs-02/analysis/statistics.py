"""
TO-CS-02: Statistical Analysis Module
Implements bootstrap Δd, Cohen's d, and the locked decision tree.

Locked parameters (Appendix B):
- N_bootstrap: 10,000
- Random seed: 42
- Resampling: within-group, paired
- CI method: percentile, 95%
- p-value: one-tailed (proportion of Δd ≤ 0)
- Bonferroni correction: α = 0.05/4 = 0.0125
"""

import numpy as np


BOOTSTRAP_N = 10000
BOOTSTRAP_SEED = 42
ALPHA_BONFERRONI = 0.0125  # 0.05 / 4 comparisons


def cohens_d(group1, group2):
    """
    Compute Cohen's d (unbiased, Hedges' correction for small N).

    Parameters
    ----------
    group1, group2 : np.ndarray, 1D arrays of values per subject

    Returns
    -------
    d : float, Cohen's d
    """
    n1, n2 = len(group1), len(group2)
    mean_diff = np.mean(group1) - np.mean(group2)
    pooled_std = np.sqrt(
        ((n1 - 1) * np.var(group1, ddof=1) + (n2 - 1) * np.var(group2, ddof=1))
        / (n1 + n2 - 2)
    )
    if pooled_std == 0:
        return 0.0
    d = mean_diff / pooled_std
    # Hedges' correction
    correction = 1 - 3 / (4 * (n1 + n2) - 9)
    return d * correction


def bootstrap_delta_d(measure_a_resp, measure_a_drowsy,
                       measure_b_resp, measure_b_drowsy,
                       n_bootstrap=BOOTSTRAP_N, seed=BOOTSTRAP_SEED):
    """
    Bootstrap Δd = d(A) - d(B) to test if measure A beats measure B.

    Parameters
    ----------
    measure_a_resp : np.ndarray, measure A values for responsive subjects
    measure_a_drowsy : np.ndarray, measure A values for drowsy subjects
    measure_b_resp : np.ndarray, measure B values for responsive subjects
    measure_b_drowsy : np.ndarray, measure B values for drowsy subjects

    Returns
    -------
    result : dict with keys:
        'd_A': Cohen's d for measure A
        'd_B': Cohen's d for measure B
        'delta_d': observed Δd
        'delta_d_ci_lower': 2.5th percentile
        'delta_d_ci_upper': 97.5th percentile
        'p_value': one-tailed p (proportion Δd ≤ 0)
        'beats': bool, True if A beats B (Δd > 0 AND CI excludes 0)
    """
    rng = np.random.RandomState(seed)
    n_resp = len(measure_a_resp)
    n_drowsy = len(measure_a_drowsy)

    # Observed effect sizes
    d_A = cohens_d(measure_a_resp, measure_a_drowsy)
    d_B = cohens_d(measure_b_resp, measure_b_drowsy)
    delta_d_obs = d_A - d_B

    # Bootstrap
    delta_d_boot = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        # Resample within group, paired (same indices for A and B)
        idx_resp = rng.choice(n_resp, size=n_resp, replace=True)
        idx_drowsy = rng.choice(n_drowsy, size=n_drowsy, replace=True)

        d_A_boot = cohens_d(
            measure_a_resp[idx_resp], measure_a_drowsy[idx_drowsy]
        )
        d_B_boot = cohens_d(
            measure_b_resp[idx_resp], measure_b_drowsy[idx_drowsy]
        )
        delta_d_boot[i] = d_A_boot - d_B_boot

    # Percentile CI
    ci_lower = np.percentile(delta_d_boot, 2.5)
    ci_upper = np.percentile(delta_d_boot, 97.5)

    # One-tailed p-value
    p_value = np.mean(delta_d_boot <= 0)

    # "Beats" criterion
    beats = (delta_d_obs > 0) and (ci_lower > 0) and (p_value < ALPHA_BONFERRONI)

    return {
        'd_A': d_A,
        'd_B': d_B,
        'delta_d': delta_d_obs,
        'delta_d_ci_lower': ci_lower,
        'delta_d_ci_upper': ci_upper,
        'p_value': p_value,
        'beats': beats,
    }


def compute_c_product(omega_values, kappa_values):
    """Compute C = Omega x Kappa (product measure)."""
    return omega_values * kappa_values


def compute_c_additive(omega_values, kappa_values):
    """Compute C_add = Omega + Kappa (additive control)."""
    return omega_values + kappa_values


def run_all_comparisons(resp_omega_full, drowsy_omega_full,
                         resp_omega_df, drowsy_omega_df,
                         resp_kappa, drowsy_kappa):
    """
    Run all 4 locked primary comparisons (Appendix B.2).

    Parameters
    ----------
    resp_omega_full : np.ndarray, Omega(full band) for responsive subjects
    drowsy_omega_full : np.ndarray, Omega(full band) for drowsy subjects
    resp_omega_df : np.ndarray, Omega(delta-free 4-40Hz) for responsive subjects
    drowsy_omega_df : np.ndarray, Omega(delta-free 4-40Hz) for drowsy subjects
    resp_kappa : np.ndarray, Kappa for responsive subjects
    drowsy_kappa : np.ndarray, Kappa for drowsy subjects

    Returns
    -------
    results : dict with comparison results for (a), (b), (c), (d)
    """
    # Product measures
    resp_C_df = compute_c_product(resp_omega_df, resp_kappa)
    drowsy_C_df = compute_c_product(drowsy_omega_df, drowsy_kappa)
    resp_C_full = compute_c_product(resp_omega_full, resp_kappa)
    drowsy_C_full = compute_c_product(drowsy_omega_full, drowsy_kappa)

    # Additive control
    resp_C_add = compute_c_additive(resp_omega_df, resp_kappa)
    drowsy_C_add = compute_c_additive(drowsy_omega_df, drowsy_kappa)

    results = {}

    # (a) C = Omega(4-40) x kappa vs Omega(4-40) — PRIMARY NOVEL TEST
    results['a'] = bootstrap_delta_d(
        resp_C_df, drowsy_C_df,
        resp_omega_df, drowsy_omega_df
    )
    results['a']['description'] = 'C=Omega(4-40)xKappa vs Omega(4-40) — KEY NOVEL TEST'

    # (b) C = Omega(4-40) x kappa vs kappa alone
    results['b'] = bootstrap_delta_d(
        resp_C_df, drowsy_C_df,
        resp_kappa, drowsy_kappa
    )
    results['b']['description'] = 'C=Omega(4-40)xKappa vs Kappa alone'

    # (c) C = Omega(full) x kappa vs Omega(full)
    results['c'] = bootstrap_delta_d(
        resp_C_full, drowsy_C_full,
        resp_omega_full, drowsy_omega_full
    )
    results['c']['description'] = 'C=Omega(full)xKappa vs Omega(full) — HARD TEST'

    # (d) C_mult vs C_add
    results['d'] = bootstrap_delta_d(
        resp_C_df, drowsy_C_df,
        resp_C_add, drowsy_C_add
    )
    results['d']['description'] = 'C_multiplicative vs C_additive'

    return results


def score_decision_tree(correlation_omega_kappa, comparison_results):
    """
    Apply the locked TO-CS-02 decision tree (Appendix B.5).

    Parameters
    ----------
    correlation_omega_kappa : float, corr(Omega, Kappa) at subject x condition level
    comparison_results : dict from run_all_comparisons

    Returns
    -------
    score : dict with keys:
        'grade': str, one of 'Indeterminate', 'F1', 'F2', 'C1', 'C2', 'C3'
        'explanation': str
        'correlation': float
        'comparisons': dict
    """
    result = {
        'correlation': correlation_omega_kappa,
        'comparisons': comparison_results,
    }

    # Step 1: Dissociation check
    if correlation_omega_kappa > 0.8:
        result['grade'] = 'Indeterminate'
        result['explanation'] = (
            f'corr(Omega, Kappa) = {correlation_omega_kappa:.3f} > 0.8. '
            'Dataset unsuitable — Omega and Kappa are too correlated. STOP.'
        )
        return result

    # Step 2: Comparison (a) — KEY NOVEL TEST
    comp_a = comparison_results['a']
    if not comp_a['beats']:
        result['grade'] = 'F1'
        result['explanation'] = (
            f'Comparison (a) FAILED: C=Omega(4-40)xKappa does not beat Omega(4-40). '
            f'Delta_d = {comp_a["delta_d"]:.3f}, CI = [{comp_a["delta_d_ci_lower"]:.3f}, '
            f'{comp_a["delta_d_ci_upper"]:.3f}], p = {comp_a["p_value"]:.4f}. '
            'Kappa adds nothing novel beyond spectral power.'
        )
        return result

    # Step 3: Comparison (c) — HARD TEST
    comp_c = comparison_results['c']
    if not comp_c['beats']:
        result['grade'] = 'C1'
        result['explanation'] = (
            f'Comparison (a) PASSED but (c) FAILED. '
            f'Kappa captures information beyond spectral power shift (delta-free), '
            f'but not beyond full-band Omega. '
            f'(a) Delta_d = {comp_a["delta_d"]:.3f}, (c) Delta_d = {comp_c["delta_d"]:.3f}. '
            'Score: C1 — partial support for product hypothesis.'
        )
        return result

    # Step 4: Magnitude check for C3
    if comp_c['delta_d'] >= 0.5:
        result['grade'] = 'C3'
        result['explanation'] = (
            f'Both (a) and (c) PASSED with Delta_d(c) = {comp_c["delta_d"]:.3f} >= 0.5. '
            'STRONG support for the product hypothesis. '
            'C = Omega x Kappa substantially exceeds both Omega measures.'
        )
    else:
        result['grade'] = 'C2'
        result['explanation'] = (
            f'Both (a) and (c) PASSED but Delta_d(c) = {comp_c["delta_d"]:.3f} < 0.5. '
            'MODERATE support for the product hypothesis.'
        )

    return result
