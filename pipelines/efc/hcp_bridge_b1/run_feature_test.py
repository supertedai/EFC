#!/usr/bin/env python3
"""
Feature Test: What Actually Drives κ?
=======================================
Data-first approach. Instead of assuming κ ~ 1/λ₂ (B1*),
we test what network features actually correlate with the
centrifugal entropy gradient.

Features tested:
  1. Global: λ₂ (Fiedler), modularity Q, mean clustering
  2. Hub-specific: mean hub degree, hub participation coeff
  3. Local: degree ratio (hub/periph), betweenness ratio
  4. Derived: rich-club coefficient, small-world index

Tested across 6 HCP parcellation scales (ENIGMA data).
"""

import numpy as np
from pathlib import Path
from scipy.linalg import eigh
from scipy.stats import pearsonr
import json

DATA_DIR = Path(__file__).parent / 'real_data'


def load_csv(path):
    return np.loadtxt(path, delimiter=',')


def compute_lambda2(W):
    d = np.sum(W, axis=1)
    d_inv_sqrt = np.zeros_like(d, dtype=float)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    L = 0.5 * (L + L.T)
    eigenvals = eigh(L, eigvals_only=True)
    return np.sort(eigenvals)[1]


def compute_modularity(W, n_iter=50):
    """Newman modularity Q via greedy optimization (simplified)."""
    n = W.shape[0]
    m = np.sum(W) / 2
    if m == 0:
        return 0.0

    k = np.sum(W, axis=1)
    B = W - np.outer(k, k) / (2 * m)

    # Simple greedy: start with each node in own community, merge best pairs
    labels = np.arange(n)
    best_Q = _modularity_score(B, labels, m)

    rng = np.random.default_rng(42)
    for _ in range(n_iter):
        trial = labels.copy()
        # Random merge of two communities
        i, j = rng.choice(n, 2, replace=False)
        trial[trial == trial[j]] = trial[i]
        Q = _modularity_score(B, trial, m)
        if Q > best_Q:
            best_Q = Q
            labels = trial

    return best_Q


def _modularity_score(B, labels, m):
    Q = 0.0
    for c in set(labels):
        mask = labels == c
        Q += np.sum(B[np.ix_(mask, mask)])
    return Q / (2 * m)


def compute_clustering(W):
    """Mean clustering coefficient."""
    A = (W > 0).astype(float)
    n = len(A)
    cc_values = []
    for i in range(n):
        neighbors = np.where(A[i] > 0)[0]
        k = len(neighbors)
        if k < 2:
            continue
        links = np.sum(A[np.ix_(neighbors, neighbors)]) / 2
        cc_values.append(2 * links / (k * (k - 1)))
    return np.mean(cc_values) if cc_values else 0.0


def compute_participation_coeff(W, labels):
    """Participation coefficient (how distributed connections are across modules)."""
    n = W.shape[0]
    k = np.sum(W, axis=1)
    P = np.zeros(n)

    for i in range(n):
        if k[i] == 0:
            continue
        for c in set(labels):
            mask = labels == c
            k_ic = np.sum(W[i, mask])
            P[i] += (k_ic / k[i]) ** 2
    P = 1 - P
    return P


def compute_betweenness_approx(W, n_samples=200):
    """Approximate betweenness centrality using BFS on unweighted graph."""
    A = (W > 0).astype(float)
    n = len(A)
    bc = np.zeros(n)
    rng = np.random.default_rng(42)
    sources = rng.choice(n, min(n_samples, n), replace=False)

    for s in sources:
        # BFS
        dist = -np.ones(n, dtype=int)
        dist[s] = 0
        queue = [s]
        pred = [[] for _ in range(n)]
        sigma = np.zeros(n)
        sigma[s] = 1
        order = []

        while queue:
            v = queue.pop(0)
            order.append(v)
            for w in np.where(A[v] > 0)[0]:
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)

        delta = np.zeros(n)
        for w in reversed(order):
            for v in pred[w]:
                if sigma[w] > 0:
                    delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                bc[w] += delta[w]

    bc /= len(sources)
    return bc


def classify_hubs(W, hub_pct=0.10, periph_pct=0.30):
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)
    n = len(degree)
    periph_idx = sorted_idx[:int(periph_pct * n)]
    hub_idx = sorted_idx[-int(hub_pct * n):]
    return hub_idx, periph_idx


def compute_kappa(W, FC=None):
    """Compute κ using best available proxy."""
    n = W.shape[0]
    hub_idx, periph_idx = classify_hubs(W)

    results = {}

    # Structural: log-degree ratio
    degree = np.sum(W, axis=1)
    log_deg = np.log1p(degree)
    results['kappa_struct'] = np.mean(log_deg[hub_idx]) / np.mean(log_deg[periph_idx])

    # FC-based: coefficient of variation
    if FC is not None:
        fc_std = np.std(FC, axis=1)
        fc_mean = np.mean(np.abs(FC), axis=1)
        cv = fc_std / np.where(fc_mean > 0, fc_mean, 1e-10)
        results['kappa_fc'] = np.mean(cv[hub_idx]) / np.mean(cv[periph_idx])

    return results


def main():
    print("=" * 70)
    print("FEATURE TEST: WHAT DRIVES κ?")
    print("Data-first analysis on real HCP connectomes")
    print("=" * 70)

    scales = [
        ('Desikan-68', 'struc_desikan.csv', 'func_desikan.csv'),
        ('Schaefer-100', 'struc_schaefer100.csv', 'func_schaefer100.csv'),
        ('Schaefer-200', 'struc_schaefer200.csv', 'func_schaefer200.csv'),
        ('Schaefer-300', 'struc_schaefer300.csv', 'func_schaefer300.csv'),
        ('Glasser-360', 'strucMatrix_glasser360.csv', 'func_glasser360.csv'),
        ('Schaefer-400', 'struc_schaefer400.csv', 'func_schaefer400.csv'),
    ]

    all_features = []

    for name, sc_file, fc_file in scales:
        sc_path = DATA_DIR / sc_file
        fc_path = DATA_DIR / fc_file

        if not sc_path.exists():
            continue

        print(f"\n  Processing {name}...", end='', flush=True)
        W = load_csv(sc_path)
        FC = load_csv(fc_path) if fc_path.exists() else None
        n = W.shape[0]

        hub_idx, periph_idx = classify_hubs(W)
        degree = np.sum(W, axis=1)

        # Compute features
        lambda2 = compute_lambda2(W)
        Q = compute_modularity(W)
        cc = compute_clustering(W)

        # Simple module detection for participation coeff
        # Use spectral bisection
        d = np.sum(W, axis=1)
        d_inv_sqrt = np.zeros_like(d, dtype=float)
        mask = d > 0
        d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
        D_inv_sqrt = np.diag(d_inv_sqrt)
        L = np.eye(n) - D_inv_sqrt @ W @ D_inv_sqrt
        L = 0.5 * (L + L.T)
        _, vecs = eigh(L)
        fiedler_vec = vecs[:, 1]
        labels = (fiedler_vec > 0).astype(int)

        P = compute_participation_coeff(W, labels)
        bc = compute_betweenness_approx(W)

        kappas = compute_kappa(W, FC)

        features = {
            'name': name,
            'n': n,
            # Global
            'lambda2': float(lambda2),
            'modularity': float(Q),
            'clustering': float(cc),
            # Hub-specific
            'degree_hub_mean': float(np.mean(degree[hub_idx])),
            'degree_periph_mean': float(np.mean(degree[periph_idx])),
            'degree_ratio': float(np.mean(degree[hub_idx]) / np.mean(degree[periph_idx])),
            'participation_hub': float(np.mean(P[hub_idx])),
            'participation_periph': float(np.mean(P[periph_idx])),
            'participation_ratio': float(np.mean(P[hub_idx]) / max(np.mean(P[periph_idx]), 1e-10)),
            'betweenness_hub': float(np.mean(bc[hub_idx])),
            'betweenness_periph': float(np.mean(bc[periph_idx])),
            'betweenness_ratio': float(np.mean(bc[hub_idx]) / max(np.mean(bc[periph_idx]), 1e-10)),
        }
        features.update({f'kappa_{k}': v for k, v in kappas.items()})
        all_features.append(features)
        print(" done")

    # ── Correlation analysis ──
    if len(all_features) < 4:
        print("\n  Not enough scales for correlation analysis.")
        return

    print(f"\n{'━' * 70}")
    print("  CORRELATION ANALYSIS: Feature vs κ")
    print(f"{'━' * 70}")

    kappa_key = 'kappa_kappa_fc' if 'kappa_kappa_fc' in all_features[0] else 'kappa_kappa_struct'
    kappa_arr = np.array([f[kappa_key] for f in all_features])

    feature_names = [
        ('lambda2', 'λ₂ (Fiedler)'),
        ('modularity', 'Modularity Q'),
        ('clustering', 'Clustering coeff'),
        ('degree_ratio', 'Degree ratio (hub/periph)'),
        ('participation_ratio', 'Participation ratio'),
        ('betweenness_ratio', 'Betweenness ratio'),
        ('degree_hub_mean', 'Hub mean degree'),
        ('degree_periph_mean', 'Periph mean degree'),
    ]

    print(f"\n  κ source: {kappa_key}")
    print(f"  n = {len(all_features)} scales")
    print()
    print(f"  {'Feature':<30s} {'r':>7s} {'p':>8s} {'Direction':>10s}")
    print(f"  {'─' * 30} {'─' * 7} {'─' * 8} {'─' * 10}")

    correlations = []
    for fkey, fname in feature_names:
        vals = np.array([f[fkey] for f in all_features])
        if np.std(vals) < 1e-12:
            continue
        r, p = pearsonr(kappa_arr, vals)
        direction = "↑" if r > 0 else "↓"
        strength = "STRONG" if abs(r) > 0.7 else ("moderate" if abs(r) > 0.4 else "weak")
        correlations.append((fkey, fname, r, p, strength))
        print(f"  {fname:<30s} {r:>7.3f} {p:>8.4f} {direction:>4s} {strength}")

    # ── Best predictor ──
    if correlations:
        best = max(correlations, key=lambda x: abs(x[2]))
        print(f"\n  BEST PREDICTOR: {best[1]} (r = {best[2]:.3f})")

    # ── Raw data table ──
    print(f"\n{'━' * 70}")
    print("  RAW DATA")
    print(f"{'━' * 70}")
    print(f"\n  {'Atlas':<15s} {'N':>4s} {'λ₂':>6s} {'Q':>5s} {'CC':>5s} {'D_ratio':>7s} {'P_ratio':>7s} {'BC_ratio':>8s} {'κ':>6s}")
    print(f"  {'─' * 15} {'─' * 4} {'─' * 6} {'─' * 5} {'─' * 5} {'─' * 7} {'─' * 7} {'─' * 8} {'─' * 6}")

    for f in all_features:
        kap = f.get(kappa_key, 0)
        print(f"  {f['name']:<15s} {f['n']:>4d} {f['lambda2']:>6.4f} {f['modularity']:>5.3f} "
              f"{f['clustering']:>5.3f} {f['degree_ratio']:>7.2f} {f['participation_ratio']:>7.3f} "
              f"{f['betweenness_ratio']:>8.2f} {kap:>6.3f}")

    # Save
    output_path = DATA_DIR / 'feature_analysis.json'
    with open(output_path, 'w') as f:
        json.dump(all_features, f, indent=2)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
