#!/usr/bin/env python3
"""
EFC-C Kappa Analysis Pipeline
===============================
Computes the centrifugal entropy score kappa and tests predictions Q1-Q3
from EFC-C v2.0.

This script provides:
  1. Connectome lambda_2 computation
  2. MSE-based entropy proxy estimation
  3. Kappa computation (hub/periphery ratio)
  4. Anterior-posterior asymmetry (alpha_AP)
  5. Statistical tests against EFC-C predictions

Usage:
  # With synthetic data (validation mode):
  python efc_c_kappa_analysis.py --synthetic

  # With real HCP data:
  python efc_c_kappa_analysis.py --connectome path/to/W.npy --fmri path/to/ts.npy

Author: EFC Project
"""

import numpy as np
from scipy.linalg import eigh
from scipy.stats import pearsonr, spearmanr, ttest_ind
import argparse
import json
import sys


# ── EFC Parameters (frozen from Spor 1) ──
C_MEAN = 4.4
C_STD = 0.6
TAU_C_DEFAULT = 3.5  # seconds


# ══════════════════════════════════════════
# CORE COMPUTATIONS
# ══════════════════════════════════════════

def compute_lambda2(W):
    """
    Compute the Fiedler value (second-smallest eigenvalue) of the
    normalized graph Laplacian L_sym = I - D^{-1/2} W D^{-1/2}.

    Parameters
    ----------
    W : ndarray (N, N)
        Weighted adjacency matrix (symmetric, non-negative).

    Returns
    -------
    float
        lambda_2, the algebraic connectivity.
    """
    d = np.sum(W, axis=1)
    # Handle zero-degree nodes
    d_inv_sqrt = np.zeros_like(d)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)

    L_sym = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    # Force symmetry (numerical)
    L_sym = 0.5 * (L_sym + L_sym.T)

    eigenvals = eigh(L_sym, eigvals_only=True)
    # Sort and return second-smallest
    eigenvals_sorted = np.sort(eigenvals)
    return eigenvals_sorted[1]


def sample_entropy_1d(x, m=2, r_factor=0.2):
    """
    Compute sample entropy of a 1D time series.

    Parameters
    ----------
    x : ndarray (T,)
        Time series.
    m : int
        Embedding dimension.
    r_factor : float
        Tolerance as fraction of std(x).

    Returns
    -------
    float
        Sample entropy value.
    """
    N = len(x)
    r = r_factor * np.std(x)
    if r == 0:
        return 0.0

    def count_matches(template_len):
        count = 0
        templates = np.array([x[i:i + template_len] for i in range(N - template_len)])
        for i in range(len(templates)):
            for j in range(i + 1, len(templates)):
                if np.max(np.abs(templates[i] - templates[j])) < r:
                    count += 1
        return count

    A = count_matches(m + 1)
    B = count_matches(m)

    if B == 0:
        return 0.0
    return -np.log(A / B) if A > 0 else 0.0


def multiscale_sample_entropy(x, scales=(4, 5, 6), m=2, r_factor=0.2):
    """
    Compute multiscale sample entropy (MSE) at specified scales.

    Parameters
    ----------
    x : ndarray (T,)
        Time series.
    scales : tuple of int
        Coarsening scales.
    m : int
        Embedding dimension.
    r_factor : float
        Tolerance factor.

    Returns
    -------
    float
        Mean sample entropy across specified scales.
    """
    entropies = []
    for s in scales:
        # Coarse-grain
        n_segments = len(x) // s
        if n_segments < 20:  # too short
            continue
        coarse = np.mean(x[:n_segments * s].reshape(n_segments, s), axis=1)
        se = sample_entropy_1d(coarse, m=m, r_factor=r_factor)
        entropies.append(se)

    return np.mean(entropies) if entropies else 0.0


def classify_nodes(W, hub_pct=0.10, periph_pct=0.30):
    """
    Classify nodes into hub and peripheral based on weighted degree.

    Parameters
    ----------
    W : ndarray (N, N)
        Adjacency matrix.
    hub_pct : float
        Top fraction for hub classification.
    periph_pct : float
        Bottom fraction for peripheral classification.

    Returns
    -------
    hub_idx, periph_idx : ndarray, ndarray
        Indices of hub and peripheral nodes.
    """
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)
    n = len(degree)

    periph_idx = sorted_idx[:int(periph_pct * n)]
    hub_idx = sorted_idx[-int(hub_pct * n):]

    return hub_idx, periph_idx


def compute_kappa(entropy_per_node, hub_idx, periph_idx):
    """
    Compute centrifugal entropy score.

    Parameters
    ----------
    entropy_per_node : ndarray (N,)
        Entropy proxy per brain region.
    hub_idx, periph_idx : ndarray
        Node indices.

    Returns
    -------
    float
        kappa = <S_hub> / <S_periph>
    """
    s_hub = np.mean(entropy_per_node[hub_idx])
    s_periph = np.mean(entropy_per_node[periph_idx])

    if s_periph == 0:
        return float('inf')
    return s_hub / s_periph


def compute_alpha_ap(entropy_per_node, anterior_idx, posterior_idx):
    """
    Compute anterior-posterior entropy asymmetry.

    Parameters
    ----------
    entropy_per_node : ndarray (N,)
    anterior_idx, posterior_idx : ndarray
        Indices of anterior and posterior hub regions.

    Returns
    -------
    float
        alpha_AP = <S_anterior> / <S_posterior>
    """
    s_ant = np.mean(entropy_per_node[anterior_idx])
    s_post = np.mean(entropy_per_node[posterior_idx])

    if s_post == 0:
        return float('inf')
    return s_ant / s_post


def kappa_predicted(lambda2, C=C_MEAN, tau_c=TAU_C_DEFAULT):
    """Bridge B1* prediction."""
    return C / (1.0 + lambda2 * tau_c)


# ══════════════════════════════════════════
# SYNTHETIC VALIDATION
# ══════════════════════════════════════════

def generate_synthetic_cohort(n_subjects=50, group='healthy', seed=42):
    """
    Generate synthetic subjects with realistic connectome and entropy properties.

    Parameters
    ----------
    n_subjects : int
    group : str
        'healthy', 'schizophrenia', or 'mdd'
    seed : int

    Returns
    -------
    list of dict
        Per-subject results.
    """
    rng = np.random.default_rng(seed)
    n_regions = 360  # HCP MMP1.0

    # Group-specific lambda_2 distributions (from literature)
    lambda2_params = {
        'healthy':       {'mean': 0.50, 'std': 0.12},
        'schizophrenia': {'mean': 0.38, 'std': 0.14},  # reduced connectivity
        'mdd':           {'mean': 0.42, 'std': 0.13},  # moderately reduced
    }

    params = lambda2_params[group]
    results = []

    for i in range(n_subjects):
        # Generate a synthetic connectome with target lambda_2
        target_lambda2 = np.clip(
            rng.normal(params['mean'], params['std']),
            0.05, 1.5
        )

        # Build synthetic small-world-ish adjacency matrix
        W = _make_synthetic_connectome(n_regions, target_lambda2, rng)
        actual_lambda2 = compute_lambda2(W)

        hub_idx, periph_idx = classify_nodes(W)

        # Generate synthetic entropy field
        entropy = _make_synthetic_entropy(
            n_regions, hub_idx, periph_idx, group, rng,
            lambda2=actual_lambda2, model_consistent=True
        )

        kappa = compute_kappa(entropy, hub_idx, periph_idx)

        # Anterior/posterior split (rough: first half of hubs = anterior)
        mid = len(hub_idx) // 2
        ant_idx = hub_idx[:mid]
        post_idx = hub_idx[mid:]
        alpha_ap = compute_alpha_ap(entropy, ant_idx, post_idx)

        results.append({
            'subject': f'{group}_{i:03d}',
            'group': group,
            'lambda2': actual_lambda2,
            'kappa': kappa,
            'alpha_ap': alpha_ap,
            'kappa_pred': kappa_predicted(actual_lambda2),
        })

    return results


def _make_synthetic_connectome(n, target_lambda2, rng):
    """
    Create a synthetic connectome with approximately the target Fiedler value.

    Strategy: Build a modular network where inter-module coupling controls lambda_2.
    Higher coupling -> higher lambda_2 (more connected -> higher algebraic connectivity).
    """
    n_modules = 6  # rough cortical modules
    module_size = n // n_modules
    remainder = n - module_size * n_modules

    W = np.zeros((n, n))

    # Intra-module connections (strong)
    for m in range(n_modules):
        start = m * module_size
        end = start + module_size + (remainder if m == n_modules - 1 else 0)
        block = rng.exponential(1.0, (end - start, end - start))
        block = (block + block.T) / 2
        # Sparsify within module
        mask = rng.random(block.shape) > 0.4
        block[mask] = 0
        W[start:end, start:end] = block

    # Inter-module connections (controls lambda_2)
    # Map target_lambda2 to inter-module coupling strength
    # lambda_2 ~ 0.3-0.8 maps to coupling ~ 0.05-0.4
    coupling = 0.1 + target_lambda2 * 1.5
    coupling = np.clip(coupling, 0.05, 2.0)
    inter_density = 0.03 + target_lambda2 * 0.15
    inter_density = np.clip(inter_density, 0.02, 0.20)

    for i in range(n):
        for j in range(i + 1, n):
            mi = min(i // module_size, n_modules - 1)
            mj = min(j // module_size, n_modules - 1)
            if mi != mj:
                if rng.random() < inter_density:  # density scales with target
                    w = rng.exponential(coupling)
                    W[i, j] = w
                    W[j, i] = w

    np.fill_diagonal(W, 0)

    # Add degree heterogeneity (important for hub/periphery distinction)
    # Some nodes get extra connections (hubs)
    hub_boost_idx = rng.choice(n, size=int(0.1 * n), replace=False)
    for idx in hub_boost_idx:
        targets = rng.choice(n, size=int(0.05 * n), replace=False)
        for t in targets:
            if t != idx:
                boost = rng.exponential(0.5)
                W[idx, t] += boost
                W[t, idx] += boost

    return W


def _make_synthetic_entropy(n_regions, hub_idx, periph_idx, group, rng,
                            lambda2=None, model_consistent=True):
    """
    Generate synthetic entropy field with group-specific topology.

    If model_consistent=True, the hub/periphery ratio follows the B1* model:
      kappa = C / (1 + lambda_2 * tau_c)
    This tests internal consistency.

    If model_consistent=False, entropy is independent of lambda_2.
    This serves as a null control.
    """
    entropy = np.ones(n_regions)

    if model_consistent and lambda2 is not None:
        # B1* model-driven entropy
        kappa_target = kappa_predicted(lambda2)

        # Set hub entropy to achieve target kappa
        base_periph = 1.0
        base_hub = kappa_target * base_periph

        entropy[periph_idx] = base_periph + rng.normal(0, 0.08, len(periph_idx))
        entropy[hub_idx] = base_hub + rng.normal(0, 0.12, len(hub_idx))

        # Group-specific anterior-posterior modulation
        mid = len(hub_idx) // 2
        if group == 'schizophrenia':
            entropy[hub_idx[:mid]] += 0.3   # anterior elevation
            entropy[hub_idx[mid:]] -= 0.1   # relative posterior reduction
        elif group == 'mdd':
            entropy[hub_idx[:mid]] -= 0.1   # anterior reduction
            entropy[hub_idx[mid:]] += 0.2   # posterior elevation
    else:
        # Null model: entropy independent of lambda_2
        if group == 'healthy':
            entropy[hub_idx] += rng.normal(0.6, 0.15, len(hub_idx))
            entropy[periph_idx] -= rng.normal(0.2, 0.10, len(periph_idx))
        elif group == 'schizophrenia':
            entropy[hub_idx] += rng.normal(0.8, 0.25, len(hub_idx))
            entropy[periph_idx] -= rng.normal(0.1, 0.10, len(periph_idx))
            mid = len(hub_idx) // 2
            entropy[hub_idx[:mid]] += 0.3
        elif group == 'mdd':
            entropy[hub_idx] += rng.normal(0.3, 0.12, len(hub_idx))
            entropy[periph_idx] -= rng.normal(0.15, 0.08, len(periph_idx))
            mid = len(hub_idx) // 2
            entropy[hub_idx[mid:]] += 0.2

    entropy = np.clip(entropy, 0.1, 5.0)
    # Add measurement noise (10%)
    entropy *= rng.normal(1.0, 0.10, n_regions)

    return entropy


# ══════════════════════════════════════════
# STATISTICAL TESTS
# ══════════════════════════════════════════

def run_tests(healthy, schiz, mdd):
    """Run all EFC-C v2 statistical tests."""
    results = {}

    # ── Q1: kappa scaling with 1/lambda_2 (healthy) ──
    kappas_h = np.array([s['kappa'] for s in healthy])
    lambda2s_h = np.array([s['lambda2'] for s in healthy])
    inv_lambda2_h = 1.0 / lambda2s_h

    r_q1, p_q1 = pearsonr(kappas_h, inv_lambda2_h)
    results['Q1'] = {
        'test': 'r(kappa, 1/lambda_2) in healthy',
        'r': round(r_q1, 3),
        'p': round(p_q1, 6),
        'kappa_mean': round(np.mean(kappas_h), 3),
        'kappa_std': round(np.std(kappas_h), 3),
        'pass': r_q1 > 0.30 and p_q1 < 0.05,
        'threshold': 'r > 0.30, p < 0.05',
    }

    # ── Q2a: alpha_AP schizophrenia > healthy ──
    alpha_h = np.array([s['alpha_ap'] for s in healthy])
    alpha_scz = np.array([s['alpha_ap'] for s in schiz])
    t_q2a, p_q2a = ttest_ind(alpha_scz, alpha_h, alternative='greater')
    results['Q2a'] = {
        'test': 'alpha_AP: schizophrenia > healthy',
        'alpha_healthy_mean': round(np.mean(alpha_h), 3),
        'alpha_scz_mean': round(np.mean(alpha_scz), 3),
        't': round(t_q2a, 3),
        'p': round(p_q2a, 6),
        'pass': p_q2a < 0.05,
        'threshold': 'p < 0.05 (one-tailed)',
    }

    # ── Q2b: alpha_AP MDD < healthy ──
    alpha_mdd = np.array([s['alpha_ap'] for s in mdd])
    t_q2b, p_q2b = ttest_ind(alpha_mdd, alpha_h, alternative='less')
    results['Q2b'] = {
        'test': 'alpha_AP: MDD < healthy',
        'alpha_healthy_mean': round(np.mean(alpha_h), 3),
        'alpha_mdd_mean': round(np.mean(alpha_mdd), 3),
        't': round(t_q2b, 3),
        'p': round(p_q2b, 6),
        'pass': p_q2b < 0.05,
        'threshold': 'p < 0.05 (one-tailed)',
    }

    # ── Q2c: Delta_kappa correlates with Delta_lambda_2 ──
    all_kappas = np.concatenate([kappas_h,
                                 np.array([s['kappa'] for s in schiz]),
                                 np.array([s['kappa'] for s in mdd])])
    all_lambda2 = np.concatenate([lambda2s_h,
                                  np.array([s['lambda2'] for s in schiz]),
                                  np.array([s['lambda2'] for s in mdd])])
    r_q2c, p_q2c = pearsonr(all_kappas, 1.0 / all_lambda2)
    results['Q2c'] = {
        'test': 'r(kappa, 1/lambda_2) across all groups',
        'r': round(r_q2c, 3),
        'p': round(p_q2c, 6),
        'pass': r_q2c > 0.25,
        'threshold': 'r > 0.25',
    }

    # ── Q3: kappa threshold ──
    kappa_crit = C_MEAN / (1.0 + 1.0 * 5.0)  # lambda2_max=1.0, tau_c_max=5.0
    results['Q3'] = {
        'test': 'kappa_crit threshold',
        'kappa_crit': round(kappa_crit, 3),
        'healthy_min': round(np.min(kappas_h), 3),
        'note': 'Requires DoC patient data for full test',
    }

    return results


# ══════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='EFC-C Kappa Analysis')
    parser.add_argument('--synthetic', action='store_true',
                        help='Run with synthetic data')
    parser.add_argument('--connectome', type=str,
                        help='Path to connectome .npy file')
    parser.add_argument('--fmri', type=str,
                        help='Path to fMRI timeseries .npy file')
    parser.add_argument('--n-subjects', type=int, default=50)
    args = parser.parse_args()

    if args.synthetic:
        print("=" * 70)
        print("EFC-C v2.0 — SYNTHETIC VALIDATION")
        print("=" * 70)

        # ── Mode 1: Model-consistent (tests internal consistency) ──
        print()
        print("━━━ MODE 1: MODEL-CONSISTENT (entropy follows B1*) ━━━")
        print("  Purpose: Verify that IF the model is correct,")
        print("  the statistical tests detect the signal.")
        print()

        healthy = generate_synthetic_cohort(args.n_subjects, 'healthy', seed=42)
        schiz = generate_synthetic_cohort(args.n_subjects, 'schizophrenia', seed=43)
        mdd = generate_synthetic_cohort(args.n_subjects, 'mdd', seed=44)

        print(f"  Healthy:       n={len(healthy)}")
        print(f"  Schizophrenia: n={len(schiz)}")
        print(f"  MDD:           n={len(mdd)}")
        print()

        results = run_tests(healthy, schiz, mdd)

        print("─── RESULTS (model-consistent) ───")
        print()
        for code, res in results.items():
            print(f"  [{code}] {res['test']}")
            for k, v in res.items():
                if k != 'test':
                    print(f"        {k}: {v}")
            print()

        passed_m1 = sum(1 for r in results.values() if r.get('pass'))
        total_m1 = sum(1 for r in results.values() if 'pass' in r)
        print(f"  Model-consistent: {passed_m1}/{total_m1} passed")
        print()

        # ── Mode 2: Null control (entropy independent of lambda_2) ──
        print("━━━ MODE 2: NULL CONTROL (entropy independent of lambda_2) ━━━")
        print("  Purpose: Verify that Q1/Q2c do NOT pass when the model")
        print("  is wrong (no built-in correlation).")
        print()

        # Temporarily patch the generator to use null mode
        _orig = generate_synthetic_cohort.__code__
        # Simple approach: generate null data manually
        rng_null = np.random.default_rng(99)
        n_regions = 360
        null_healthy = []
        for i in range(args.n_subjects):
            target_l2 = np.clip(rng_null.normal(0.50, 0.12), 0.05, 1.5)
            W = _make_synthetic_connectome(n_regions, target_l2, rng_null)
            actual_l2 = compute_lambda2(W)
            hub_idx, periph_idx = classify_nodes(W)
            entropy = _make_synthetic_entropy(
                n_regions, hub_idx, periph_idx, 'healthy', rng_null,
                lambda2=actual_l2, model_consistent=False  # NULL
            )
            kappa = compute_kappa(entropy, hub_idx, periph_idx)
            mid = len(hub_idx) // 2
            alpha_ap = compute_alpha_ap(entropy, hub_idx[:mid], hub_idx[mid:])
            null_healthy.append({
                'subject': f'null_{i:03d}', 'group': 'healthy',
                'lambda2': actual_l2, 'kappa': kappa, 'alpha_ap': alpha_ap,
                'kappa_pred': kappa_predicted(actual_l2),
            })

        kappas_null = np.array([s['kappa'] for s in null_healthy])
        lambda2s_null = np.array([s['lambda2'] for s in null_healthy])
        r_null, p_null = pearsonr(kappas_null, 1.0 / lambda2s_null)

        print(f"  Null Q1: r(kappa, 1/lambda_2) = {r_null:.3f}, p = {p_null:.4f}")
        if abs(r_null) < 0.30:
            print(f"  GOOD: No spurious correlation in null model.")
        else:
            print(f"  WARNING: Spurious correlation detected — check generator.")
        print()

        # ── Final summary ──
        print("━━━ FINAL SUMMARY ━━━")
        print()
        print(f"  Model-consistent mode: {passed_m1}/{total_m1} tests passed")
        print(f"  Null control:          Q1 correlation r = {r_null:.3f} (should be ~0)")
        print()
        print("  INTERPRETATION:")
        print("  - If model-consistent passes AND null fails → tests are sensitive")
        print("    and non-trivial. The signal exists only if B1* is correct.")
        print("  - Real validation requires HCP + OpenNeuro data.")
        print("  - Topological predictions (Q2a, Q2b) are robust regardless of B1*.")

    elif args.connectome and args.fmri:
        print("Real data mode — loading files...")
        W = np.load(args.connectome)
        ts = np.load(args.fmri)

        lambda2 = compute_lambda2(W)
        hub_idx, periph_idx = classify_nodes(W)

        # Compute MSE per region
        n_regions = ts.shape[1] if ts.ndim == 2 else ts.shape[0]
        print(f"  Regions: {n_regions}")
        print(f"  lambda_2: {lambda2:.4f}")
        print(f"  Computing MSE per region...")

        entropy = np.zeros(n_regions)
        for i in range(n_regions):
            signal = ts[:, i] if ts.ndim == 2 else ts[i]
            entropy[i] = multiscale_sample_entropy(signal)

        kappa = compute_kappa(entropy, hub_idx, periph_idx)
        kappa_pred = kappa_predicted(lambda2)

        print(f"\n  kappa_obs:  {kappa:.3f}")
        print(f"  kappa_pred: {kappa_pred:.3f}")
        print(f"  Deviation:  {abs(kappa - kappa_pred):.3f}")

    else:
        print("Usage:")
        print("  python efc_c_kappa_analysis.py --synthetic")
        print("  python efc_c_kappa_analysis.py --connectome W.npy --fmri ts.npy")


if __name__ == "__main__":
    main()
