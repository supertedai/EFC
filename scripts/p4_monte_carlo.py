#!/usr/bin/env python3
"""
P4* Monte Carlo Pre-Screen
===========================
Tests the robustness of the Bridge B1* prediction:

    η = C / (1 + λ₂ · τ_c)

where:
  C  = k / a_G ≈ 4.4 ± 0.6  (frozen from SPARC galaxy data)
  λ₂ = Fiedler eigenvalue of structural connectome (~0.3–0.8)
  τ_c = entropy redistribution timescale (~2–5 s)

Key question: Is the correlation r(η, 1/λ₂) robust against
realistic biological noise, or is it trivially built-in?

Author: EFC Project
"""

import numpy as np
from scipy.stats import pearsonr, spearmanr
import json
import sys

# ──────────────────────────────────────────────
# PARAMETERS (from literature / EFC Spor 1)
# ──────────────────────────────────────────────
C_MEAN = 4.4       # k/a_G from SPARC fit
C_STD = 0.6        # uncertainty on C

LAMBDA2_MEAN = 0.50   # typical Fiedler value (HCP literature)
LAMBDA2_STD = 0.12    # inter-subject variability

TAU_C_MEAN = 3.5      # cortical diffusion timescale (seconds)
TAU_C_STD = 0.8       # inter-subject variability

MEASUREMENT_NOISE = 0.10  # 10% fMRI measurement noise on η

N_SUBJECTS = 50       # number of synthetic subjects
N_ITERATIONS = 10000   # Monte Carlo iterations
SEED = 42


def eta_model(C, lambda2, tau_c):
    """Bridge B1* prediction: η = C / (1 + λ₂ · τ_c)"""
    return C / (1.0 + lambda2 * tau_c)


def run_single_cohort(n_subjects, rng, add_noise=True):
    """Generate one synthetic cohort and compute correlation."""
    # Draw parameters
    C_vals = rng.normal(C_MEAN, C_STD, n_subjects)
    lambda2_vals = np.abs(rng.normal(LAMBDA2_MEAN, LAMBDA2_STD, n_subjects))
    lambda2_vals = np.clip(lambda2_vals, 0.05, 1.5)  # physical bounds
    tau_c_vals = np.abs(rng.normal(TAU_C_MEAN, TAU_C_STD, n_subjects))
    tau_c_vals = np.clip(tau_c_vals, 0.5, 10.0)

    # Compute true η from model
    eta_true = eta_model(C_vals, lambda2_vals, tau_c_vals)

    if add_noise:
        # Add multiplicative measurement noise
        noise = rng.normal(1.0, MEASUREMENT_NOISE, n_subjects)
        eta_obs = eta_true * noise
    else:
        eta_obs = eta_true

    # Compute correlations
    inv_lambda2 = 1.0 / lambda2_vals
    r_pearson, p_pearson = pearsonr(eta_obs, inv_lambda2)
    r_spearman, p_spearman = spearmanr(eta_obs, inv_lambda2)

    return {
        'eta_obs': eta_obs,
        'lambda2': lambda2_vals,
        'tau_c': tau_c_vals,
        'r_pearson': r_pearson,
        'p_pearson': p_pearson,
        'r_spearman': r_spearman,
        'p_spearman': p_spearman,
        'eta_mean': np.mean(eta_obs),
        'eta_std': np.std(eta_obs),
    }


def sensitivity_analysis(rng):
    """How does correlation degrade as τ_c noise increases?"""
    tau_c_stds = [0.2, 0.5, 0.8, 1.0, 1.5, 2.0, 2.5, 3.0]
    results = []

    for tc_std in tau_c_stds:
        r_vals = []
        for _ in range(1000):
            C_vals = rng.normal(C_MEAN, C_STD, N_SUBJECTS)
            lambda2_vals = np.abs(rng.normal(LAMBDA2_MEAN, LAMBDA2_STD, N_SUBJECTS))
            lambda2_vals = np.clip(lambda2_vals, 0.05, 1.5)
            tau_c_vals = np.abs(rng.normal(TAU_C_MEAN, tc_std, N_SUBJECTS))
            tau_c_vals = np.clip(tau_c_vals, 0.5, 10.0)

            eta = eta_model(C_vals, lambda2_vals, tau_c_vals)
            noise = rng.normal(1.0, MEASUREMENT_NOISE, N_SUBJECTS)
            eta_obs = eta * noise

            r, _ = pearsonr(eta_obs, 1.0 / lambda2_vals)
            r_vals.append(r)

        results.append({
            'tau_c_std': tc_std,
            'r_mean': np.mean(r_vals),
            'r_std': np.std(r_vals),
            'r_5pct': np.percentile(r_vals, 5),
            'r_95pct': np.percentile(r_vals, 95),
            'pct_above_03': np.mean(np.array(r_vals) > 0.3) * 100,
        })

    return results


def null_test(rng, n_iter=5000):
    """Null hypothesis: η is random (no relation to λ₂).
    What's the false positive rate?"""
    false_positives = 0
    for _ in range(n_iter):
        lambda2_vals = np.abs(rng.normal(LAMBDA2_MEAN, LAMBDA2_STD, N_SUBJECTS))
        lambda2_vals = np.clip(lambda2_vals, 0.05, 1.5)
        # Random η, no model
        eta_random = rng.uniform(0.5, 3.0, N_SUBJECTS)
        r, p = pearsonr(eta_random, 1.0 / lambda2_vals)
        if p < 0.05:
            false_positives += 1
    return false_positives / n_iter


def power_analysis(rng):
    """How many subjects needed for different effect sizes?"""
    sample_sizes = [10, 15, 20, 30, 50, 75, 100]
    results = []

    for n in sample_sizes:
        detections = 0
        for _ in range(2000):
            C_vals = rng.normal(C_MEAN, C_STD, n)
            lambda2_vals = np.abs(rng.normal(LAMBDA2_MEAN, LAMBDA2_STD, n))
            lambda2_vals = np.clip(lambda2_vals, 0.05, 1.5)
            tau_c_vals = np.abs(rng.normal(TAU_C_MEAN, TAU_C_STD, n))
            tau_c_vals = np.clip(tau_c_vals, 0.5, 10.0)

            eta = eta_model(C_vals, lambda2_vals, tau_c_vals)
            noise = rng.normal(1.0, MEASUREMENT_NOISE, n)
            eta_obs = eta * noise

            _, p = pearsonr(eta_obs, 1.0 / lambda2_vals)
            if p < 0.05:
                detections += 1

        results.append({
            'n_subjects': n,
            'power': detections / 2000,
        })

    return results


def main():
    rng = np.random.default_rng(SEED)

    print("=" * 70)
    print("P4* MONTE CARLO PRE-SCREEN")
    print("Bridge B1*: η = C / (1 + λ₂ · τ_c)")
    print("=" * 70)
    print()

    # ── 1. Basic statistics ──
    print("─── 1. BASIC STATISTICS (10,000 iterations) ───")
    r_pearson_all = []
    r_spearman_all = []
    eta_means = []

    for _ in range(N_ITERATIONS):
        res = run_single_cohort(N_SUBJECTS, rng)
        r_pearson_all.append(res['r_pearson'])
        r_spearman_all.append(res['r_spearman'])
        eta_means.append(res['eta_mean'])

    r_pearson_all = np.array(r_pearson_all)
    r_spearman_all = np.array(r_spearman_all)
    eta_means = np.array(eta_means)

    print(f"  η (mean ± std):        {np.mean(eta_means):.3f} ± {np.std(eta_means):.3f}")
    print(f"  η range (5-95%):       [{np.percentile(eta_means, 5):.2f}, {np.percentile(eta_means, 95):.2f}]")
    print(f"  Pearson r (mean ± std): {np.mean(r_pearson_all):.3f} ± {np.std(r_pearson_all):.3f}")
    print(f"  Pearson r (5-95%):     [{np.percentile(r_pearson_all, 5):.3f}, {np.percentile(r_pearson_all, 95):.3f}]")
    print(f"  Spearman ρ (mean):      {np.mean(r_spearman_all):.3f}")
    print(f"  % iterations r > 0.3:   {np.mean(r_pearson_all > 0.3) * 100:.1f}%")
    print(f"  % iterations r > 0.4:   {np.mean(r_pearson_all > 0.4) * 100:.1f}%")
    print()

    # ── 2. CRITICAL: Is correlation trivially built-in? ──
    print("─── 2. CIRCULARITY CHECK ───")
    print("  Testing: if τ_c varies A LOT, does r collapse?")
    print("  (If r stays high regardless of τ_c noise → trivially built-in)")
    print()

    sens = sensitivity_analysis(rng)
    print(f"  {'τ_c std':>8s}  {'r (mean)':>8s}  {'r (5%)':>8s}  {'r (95%)':>8s}  {'% > 0.3':>8s}")
    print(f"  {'─' * 8}  {'─' * 8}  {'─' * 8}  {'─' * 8}  {'─' * 8}")
    for s in sens:
        print(f"  {s['tau_c_std']:8.1f}  {s['r_mean']:8.3f}  {s['r_5pct']:8.3f}  {s['r_95pct']:8.3f}  {s['pct_above_03']:7.1f}%")
    print()

    # ── 3. Null hypothesis test ──
    print("─── 3. NULL HYPOTHESIS (η random, no model) ───")
    fp_rate = null_test(rng)
    print(f"  False positive rate (p<0.05): {fp_rate * 100:.1f}%")
    print(f"  Expected under null: ~5%")
    print()

    # ── 4. Power analysis ──
    print("─── 4. POWER ANALYSIS ───")
    print("  How many subjects to detect the signal?")
    print()
    power = power_analysis(rng)
    print(f"  {'n':>6s}  {'power':>8s}")
    print(f"  {'─' * 6}  {'─' * 8}")
    for p in power:
        marker = " ← minimum" if p['power'] >= 0.80 and (power[power.index(p) - 1]['power'] < 0.80 if power.index(p) > 0 else True) else ""
        print(f"  {p['n_subjects']:6d}  {p['power']:8.2f}{marker}")
    print()

    # ── 5. Honest verdict ──
    print("─── 5. VERDICT ───")
    mean_r = np.mean(r_pearson_all)
    if mean_r > 0.5:
        print(f"  Signal strength: STRONG (mean r = {mean_r:.3f})")
    elif mean_r > 0.3:
        print(f"  Signal strength: MODERATE (mean r = {mean_r:.3f})")
    else:
        print(f"  Signal strength: WEAK (mean r = {mean_r:.3f})")

    # Check if it's trivially circular
    high_noise_r = [s for s in sens if s['tau_c_std'] >= 2.5]
    if high_noise_r and high_noise_r[0]['r_mean'] > 0.4:
        print("  ⚠ WARNING: Correlation survives even with extreme τ_c noise.")
        print("    This suggests the signal is partially trivial (built into the formula).")
        print("    The test measures λ₂ sensitivity, not the model's physical validity.")
    else:
        print("  ✓ Correlation degrades with τ_c noise → signal is non-trivial.")

    print()
    print("  KEY INSIGHT:")
    print("  The correlation r(η, 1/λ₂) tests whether η ~ 1/λ₂.")
    print("  Since η = C/(1 + λ₂·τ_c) ≈ C/λ₂τ_c when λ₂τ_c >> 1,")
    print("  the correlation is PARTIALLY BUILT IN.")
    print()
    print("  What makes this non-trivial is:")
    print("  (a) The ABSOLUTE LEVEL of η (~1.3-2.0) being correct")
    print("  (b) The SLOPE matching C = 4.4 from galaxy data")
    print("  (c) The prediction working WITHOUT fitting to neural data")
    print()
    print("  → Focus paper on (b): slope = C/τ_c should be predictable")
    print("    from cosmological parameters alone.")


if __name__ == "__main__":
    main()
