#!/usr/bin/env python3
"""
EFC-C Model Comparison: EFC vs Power-Law vs Linear
====================================================
The decisive test: does the EFC Bridge B1* formula explain neural
entropy-connectivity data better than generic alternatives?

Three models compete on the same data:

  1. EFC:       η = C / (1 + λ₂ · τ_c)     [C=4.4 fixed, τ_c = 1 param]
  2. Power-law: η = A · (1/λ₂)^α + B       [3 params]
  3. Linear:    η = a + b · (1/λ₂)          [2 params]

Two EFC variants:
  A. τ_c FIXED (=3.5s from literature) → 0 free params → strongest claim
  B. τ_c FIT                           → 1 free param  → best EFC fit

Winner is determined by AIC/BIC (penalises overfitting).

If EFC wins → the cosmological parameter C=4.4 adds real information.
If power-law wins → generic network scaling, not EFC-specific.

Author: EFC Project
"""

import numpy as np
from scipy.optimize import curve_fit
from scipy.stats import pearsonr
import json
import sys

# ── EFC Constants ──
C_FIXED = 4.4
TAU_C_LITERATURE = 3.5  # seconds (from Sanz-Leon et al. 2015)


# ══════════════════════════════════════════
# MODEL DEFINITIONS
# ══════════════════════════════════════════

def efc_fixed(lambda2, C=C_FIXED, tau_c=TAU_C_LITERATURE):
    """EFC B1* with ALL parameters fixed. Zero free params."""
    return C / (1.0 + lambda2 * tau_c)


def efc_fit_tau(lambda2, tau_c):
    """EFC B1* with C fixed, tau_c as single free parameter."""
    return C_FIXED / (1.0 + lambda2 * tau_c)


def power_law(inv_lambda2, A, alpha, B):
    """Generic power-law: η = A · (1/λ₂)^α + B"""
    return A * np.power(inv_lambda2, alpha) + B


def linear(inv_lambda2, a, b):
    """Linear baseline: η = a + b · (1/λ₂)"""
    return a + b * inv_lambda2


# ══════════════════════════════════════════
# INFORMATION CRITERIA
# ══════════════════════════════════════════

def aic(y_obs, y_pred, k):
    """Akaike Information Criterion. Lower = better."""
    n = len(y_obs)
    sse = np.sum((y_obs - y_pred) ** 2)
    if sse <= 0:
        return -np.inf
    return n * np.log(sse / n) + 2 * k


def bic(y_obs, y_pred, k):
    """Bayesian Information Criterion. Lower = better."""
    n = len(y_obs)
    sse = np.sum((y_obs - y_pred) ** 2)
    if sse <= 0:
        return -np.inf
    return n * np.log(sse / n) + k * np.log(n)


def r_squared(y_obs, y_pred):
    """Coefficient of determination."""
    ss_res = np.sum((y_obs - y_pred) ** 2)
    ss_tot = np.sum((y_obs - np.mean(y_obs)) ** 2)
    if ss_tot == 0:
        return 0.0
    return 1.0 - ss_res / ss_tot


# ══════════════════════════════════════════
# MODEL COMPARISON ENGINE
# ══════════════════════════════════════════

def run_comparison(lambda2_arr, eta_obs):
    """
    Run full model comparison.

    Parameters
    ----------
    lambda2_arr : ndarray
        Fiedler values per subject.
    eta_obs : ndarray
        Observed kappa (entropy ratio) per subject.

    Returns
    -------
    dict
        Complete results including fits, AIC, BIC, and verdict.
    """
    n = len(lambda2_arr)
    inv_lambda2 = 1.0 / lambda2_arr
    results = {}

    # ── 1. EFC Fixed (0 free params) ──
    eta_efc_fixed = efc_fixed(lambda2_arr)
    results['efc_fixed'] = {
        'name': 'EFC (C=4.4, τ_c=3.5 fixed)',
        'n_params': 0,
        'params': {'C': C_FIXED, 'tau_c': TAU_C_LITERATURE},
        'aic': aic(eta_obs, eta_efc_fixed, 0),
        'bic': bic(eta_obs, eta_efc_fixed, 0),
        'r2': r_squared(eta_obs, eta_efc_fixed),
        'rmse': np.sqrt(np.mean((eta_obs - eta_efc_fixed) ** 2)),
        'eta_pred': eta_efc_fixed,
    }

    # ── 2. EFC Fit τ_c (1 free param) ──
    try:
        popt_efc, pcov_efc = curve_fit(efc_fit_tau, lambda2_arr, eta_obs,
                                        p0=[TAU_C_LITERATURE],
                                        bounds=(0.1, 20.0))
        tau_c_fit = popt_efc[0]
        tau_c_err = np.sqrt(pcov_efc[0, 0])
        eta_efc_fit = efc_fit_tau(lambda2_arr, tau_c_fit)
        results['efc_fit'] = {
            'name': f'EFC (C=4.4 fixed, τ_c={tau_c_fit:.2f}±{tau_c_err:.2f} fit)',
            'n_params': 1,
            'params': {'C': C_FIXED, 'tau_c': tau_c_fit, 'tau_c_err': tau_c_err},
            'aic': aic(eta_obs, eta_efc_fit, 1),
            'bic': bic(eta_obs, eta_efc_fit, 1),
            'r2': r_squared(eta_obs, eta_efc_fit),
            'rmse': np.sqrt(np.mean((eta_obs - eta_efc_fit) ** 2)),
            'eta_pred': eta_efc_fit,
        }
    except RuntimeError:
        results['efc_fit'] = {'name': 'EFC fit', 'error': 'fit failed'}

    # ── 3. Power-law (3 free params) ──
    try:
        popt_pow, pcov_pow = curve_fit(power_law, inv_lambda2, eta_obs,
                                        p0=[1.0, 0.5, 0.5],
                                        maxfev=10000)
        eta_pow = power_law(inv_lambda2, *popt_pow)
        results['power_law'] = {
            'name': f'Power-law (A={popt_pow[0]:.3f}, α={popt_pow[1]:.3f}, B={popt_pow[2]:.3f})',
            'n_params': 3,
            'params': {'A': popt_pow[0], 'alpha': popt_pow[1], 'B': popt_pow[2]},
            'aic': aic(eta_obs, eta_pow, 3),
            'bic': bic(eta_obs, eta_pow, 3),
            'r2': r_squared(eta_obs, eta_pow),
            'rmse': np.sqrt(np.mean((eta_obs - eta_pow) ** 2)),
            'eta_pred': eta_pow,
        }
    except RuntimeError:
        results['power_law'] = {'name': 'Power-law', 'error': 'fit failed'}

    # ── 4. Linear (2 free params) ──
    try:
        popt_lin, pcov_lin = curve_fit(linear, inv_lambda2, eta_obs, p0=[1.0, 0.5])
        eta_lin = linear(inv_lambda2, *popt_lin)
        results['linear'] = {
            'name': f'Linear (a={popt_lin[0]:.3f}, b={popt_lin[1]:.3f})',
            'n_params': 2,
            'params': {'a': popt_lin[0], 'b': popt_lin[1]},
            'aic': aic(eta_obs, eta_lin, 2),
            'bic': bic(eta_obs, eta_lin, 2),
            'r2': r_squared(eta_obs, eta_lin),
            'rmse': np.sqrt(np.mean((eta_obs - eta_lin) ** 2)),
            'eta_pred': eta_lin,
        }
    except RuntimeError:
        results['linear'] = {'name': 'Linear', 'error': 'fit failed'}

    # ── Correlations ──
    r_pearson, p_pearson = pearsonr(eta_obs, inv_lambda2)
    results['correlation'] = {
        'r_pearson': r_pearson,
        'p_pearson': p_pearson,
        'n_subjects': n,
    }

    # ── Verdict ──
    valid = {k: v for k, v in results.items()
             if k not in ('correlation',) and 'error' not in v}
    if valid:
        aic_ranking = sorted(valid.items(), key=lambda x: x[1]['aic'])
        bic_ranking = sorted(valid.items(), key=lambda x: x[1]['bic'])
        results['verdict'] = {
            'aic_winner': aic_ranking[0][0],
            'bic_winner': bic_ranking[0][0],
            'aic_ranking': [(k, v['aic']) for k, v in aic_ranking],
            'bic_ranking': [(k, v['bic']) for k, v in bic_ranking],
        }

    return results


# ══════════════════════════════════════════
# SYNTHETIC TEST
# ══════════════════════════════════════════

def synthetic_test():
    """Run model comparison on synthetic data to validate the pipeline."""
    rng = np.random.default_rng(42)
    n = 50

    print("=" * 70)
    print("MODEL COMPARISON: EFC vs Power-Law vs Linear")
    print("=" * 70)
    print()

    # ── Scenario A: Data generated by EFC model ──
    print("━━━ SCENARIO A: Data follows EFC (B1* ground truth) ━━━")
    print()

    lambda2_a = np.clip(rng.normal(0.50, 0.15, n), 0.10, 1.20)
    tau_c_true = 3.5
    eta_true_a = C_FIXED / (1.0 + lambda2_a * tau_c_true)
    eta_obs_a = eta_true_a * rng.normal(1.0, 0.10, n)  # 10% noise

    res_a = run_comparison(lambda2_a, eta_obs_a)
    _print_results(res_a, "Scenario A")

    # ── Scenario B: Data follows power-law (EFC should lose) ──
    print()
    print("━━━ SCENARIO B: Data follows power-law (EFC should lose) ━━━")
    print()

    lambda2_b = np.clip(rng.normal(0.50, 0.15, n), 0.10, 1.20)
    inv_l2_b = 1.0 / lambda2_b
    eta_true_b = 0.5 * inv_l2_b ** 0.7 + 0.3  # power-law ground truth
    eta_obs_b = eta_true_b * rng.normal(1.0, 0.10, n)

    res_b = run_comparison(lambda2_b, eta_obs_b)
    _print_results(res_b, "Scenario B")

    # ── Scenario C: Random data (all should be bad) ──
    print()
    print("━━━ SCENARIO C: Random data (no model should win) ━━━")
    print()

    lambda2_c = np.clip(rng.normal(0.50, 0.15, n), 0.10, 1.20)
    eta_obs_c = rng.uniform(0.8, 2.5, n)

    res_c = run_comparison(lambda2_c, eta_obs_c)
    _print_results(res_c, "Scenario C")

    # ── Summary ──
    print()
    print("━━━ INTERPRETATION GUIDE ━━━")
    print()
    print("  When you run this on REAL HCP data:")
    print()
    print("  Case 1: EFC wins AIC AND BIC")
    print("    → C=4.4 from galaxies genuinely predicts brain entropy")
    print("    → Strong evidence for shared gradient-flow class")
    print("    → Publishable in Entropy / PRE / NeuroImage")
    print()
    print("  Case 2: EFC ≈ Linear (similar AIC/BIC)")
    print("    → Structure is correct but not uniquely EFC")
    print("    → Still publishable (scaling law holds)")
    print("    → But C=4.4 doesn't add much over generic linear fit")
    print()
    print("  Case 3: Power-law wins")
    print("    → Generic network scaling, not EFC-specific")
    print("    → Bridge B1* fails as a cross-domain prediction")
    print("    → Topological predictions (Q2a/Q2b) may still hold")
    print()
    print("  Case 4: All models bad (R² < 0.15)")
    print("    → η and λ₂ are not strongly coupled")
    print("    → Fundamental assumption of B1* is wrong")


def _print_results(results, label):
    """Pretty-print comparison results."""
    print(f"  Results for {label}:")
    print(f"  {'─' * 60}")
    print(f"  {'Model':<45s} {'k':>3s} {'AIC':>8s} {'BIC':>8s} {'R²':>6s} {'RMSE':>6s}")
    print(f"  {'─' * 60}")

    for key in ['efc_fixed', 'efc_fit', 'power_law', 'linear']:
        if key in results and 'error' not in results[key]:
            r = results[key]
            print(f"  {r['name']:<45s} {r['n_params']:>3d} {r['aic']:>8.2f} {r['bic']:>8.2f} {r['r2']:>6.3f} {r['rmse']:>6.3f}")

    if 'verdict' in results:
        v = results['verdict']
        print(f"  {'─' * 60}")
        print(f"  AIC winner: {v['aic_winner']}")
        print(f"  BIC winner: {v['bic_winner']}")

    if 'correlation' in results:
        c = results['correlation']
        print(f"  Pearson r(η, 1/λ₂) = {c['r_pearson']:.3f} (p={c['p_pearson']:.2e})")


# ══════════════════════════════════════════
# REAL DATA ENTRY POINT
# ══════════════════════════════════════════

def run_on_data(lambda2_arr, eta_obs, output_path=None):
    """
    Run comparison on real data and optionally save results.

    Parameters
    ----------
    lambda2_arr : ndarray
        Fiedler values.
    eta_obs : ndarray
        Observed kappa values.
    output_path : str, optional
        Path to save JSON results.
    """
    print("=" * 70)
    print("MODEL COMPARISON ON REAL DATA")
    print(f"n = {len(lambda2_arr)} subjects")
    print("=" * 70)
    print()

    results = run_comparison(lambda2_arr, eta_obs)
    _print_results(results, "HCP Data")

    # Save machine-readable results
    if output_path:
        serializable = {}
        for k, v in results.items():
            if isinstance(v, dict):
                serializable[k] = {
                    kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv)
                    for kk, vv in v.items()
                }
        with open(output_path, 'w') as f:
            json.dump(serializable, f, indent=2)
        print(f"\n  Results saved to {output_path}")

    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == '--data':
        # Usage: python model_comparison.py --data lambda2.npy eta.npy [output.json]
        lambda2_arr = np.load(sys.argv[2])
        eta_arr = np.load(sys.argv[3])
        output = sys.argv[4] if len(sys.argv) > 4 else None
        run_on_data(lambda2_arr, eta_arr, output)
    else:
        synthetic_test()
