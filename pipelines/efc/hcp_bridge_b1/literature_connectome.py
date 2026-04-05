#!/usr/bin/env python3
"""
Literature-Based Connectome Generator
=======================================
Generates realistic connectome matrices based on published HCP statistics,
as an alternative to downloading full HCP data.

Uses published values from:
- Hagmann et al. (2008): Small-world properties of structural connectome
- van den Heuvel & Sporns (2011): Rich-club organization
- Gu et al. (2015): Controllability and Fiedler values
- Betzel et al. (2016): Generative models of connectome

This is NOT a substitute for real data. It generates networks with
statistically matched properties for pipeline validation.

For the real test, use actual HCP connectomes.
"""

import numpy as np
from scipy.linalg import eigh


# ══════════════════════════════════════════
# PUBLISHED HCP NETWORK STATISTICS
# ══════════════════════════════════════════

# From Gu et al. 2015, Betzel et al. 2016, and HCP 1200 Release
HCP_STATS = {
    'n_regions': 360,         # MMP1.0 atlas
    'density': 0.12,          # ~12% connection density
    'mean_degree': 43,        # average degree per node
    'clustering': 0.45,       # clustering coefficient
    'char_path_length': 2.5,  # characteristic path length
    'modularity': 0.55,       # Newman modularity (Q)
    'n_modules': 7,           # approximate number of modules
    'lambda2_range': (0.25, 0.85),  # Fiedler value range across subjects
    'lambda2_mean': 0.52,
    'lambda2_std': 0.11,
    'rich_club_nodes': 36,    # ~10% are rich-club hubs
}

# Approximate module assignment (based on Yeo 7-network parcellation)
# Module sizes roughly proportional to Yeo network sizes
MODULE_SIZES = {
    'visual': 0.15,
    'somatomotor': 0.14,
    'dorsal_attention': 0.12,
    'ventral_attention': 0.08,
    'limbic': 0.06,
    'frontoparietal': 0.18,
    'default_mode': 0.27,
}


def generate_hcp_like_connectome(n=360, target_lambda2=None, seed=None):
    """
    Generate a single connectome with HCP-like properties.

    Uses a stochastic block model with rich-club structure.

    Parameters
    ----------
    n : int
        Number of regions.
    target_lambda2 : float or None
        Target Fiedler value. If None, drawn from HCP distribution.
    seed : int or None

    Returns
    -------
    W : ndarray (n, n)
        Weighted symmetric adjacency matrix.
    metadata : dict
        Network properties.
    """
    rng = np.random.default_rng(seed)

    if target_lambda2 is None:
        target_lambda2 = np.clip(
            rng.normal(HCP_STATS['lambda2_mean'], HCP_STATS['lambda2_std']),
            0.15, 1.0
        )

    # Assign modules
    module_labels = _assign_modules(n, rng)
    n_modules = len(set(module_labels))

    # Build probability matrix (stochastic block model)
    # Intra-module probability >> inter-module
    p_intra = 0.35
    # Scale inter-module probability to hit target lambda2
    # Higher inter = more connected = higher lambda2
    p_inter_base = 0.02 + 0.08 * (target_lambda2 / 0.8)
    p_inter_base = np.clip(p_inter_base, 0.01, 0.15)

    W = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            if module_labels[i] == module_labels[j]:
                p = p_intra
            else:
                p = p_inter_base

            if rng.random() < p:
                # Log-normal weights (realistic for streamline counts)
                w = rng.lognormal(mean=0.5, sigma=0.8)
                W[i, j] = w
                W[j, i] = w

    # Add rich-club structure (top 10% nodes get extra connections)
    degree = np.sum(W > 0, axis=1)
    rich_idx = np.argsort(degree)[-int(0.10 * n):]

    for i in rich_idx:
        for j in rich_idx:
            if i < j and W[i, j] == 0:
                if rng.random() < 0.5:  # rich-club interconnection
                    w = rng.lognormal(mean=1.0, sigma=0.5)
                    W[i, j] = w
                    W[j, i] = w

    # Compute actual properties
    actual_lambda2 = _compute_lambda2(W)
    actual_density = np.sum(W > 0) / (n * (n - 1))
    actual_degree = np.mean(np.sum(W > 0, axis=1))

    metadata = {
        'n': n,
        'target_lambda2': target_lambda2,
        'actual_lambda2': actual_lambda2,
        'density': actual_density,
        'mean_degree': actual_degree,
        'n_modules': n_modules,
        'module_labels': module_labels.tolist(),
    }

    return W, metadata


def generate_cohort(n_subjects=50, n_regions=360, seed=42):
    """
    Generate a cohort of HCP-like connectomes with realistic inter-subject
    variability in lambda_2.

    Returns
    -------
    connectomes : list of ndarray
        List of (n, n) adjacency matrices.
    metadata_list : list of dict
        Per-subject metadata.
    """
    rng = np.random.default_rng(seed)

    # Draw target lambda2 from HCP distribution
    target_lambda2s = np.clip(
        rng.normal(HCP_STATS['lambda2_mean'], HCP_STATS['lambda2_std'],
                   n_subjects),
        0.15, 1.0
    )

    connectomes = []
    metadata_list = []

    for i, target_l2 in enumerate(target_lambda2s):
        W, meta = generate_hcp_like_connectome(
            n=n_regions,
            target_lambda2=target_l2,
            seed=seed + i + 1
        )
        meta['subject_id'] = f'hcp_lit_{i:03d}'
        connectomes.append(W)
        metadata_list.append(meta)

    return connectomes, metadata_list


def generate_bold_timeseries(W, T=1200, TR=0.72, seed=None):
    """
    Generate synthetic BOLD-like time series using a simple neural mass model.

    The model: each node has intrinsic dynamics + network coupling.

    x_i(t+1) = (1-alpha)*x_i(t) + alpha * sum_j W_ij * x_j(t) + noise

    This produces time series where hub nodes (high degree) have:
    - Higher temporal complexity (more inputs = richer dynamics)
    - Correlated activity with connected nodes

    Parameters
    ----------
    W : ndarray (N, N)
        Adjacency matrix.
    T : int
        Number of time points (default: 1200, matching HCP 3T REST1).
    TR : float
        Repetition time in seconds.
    seed : int or None

    Returns
    -------
    timeseries : ndarray (T, N)
        Simulated BOLD time series.
    """
    rng = np.random.default_rng(seed)
    n = W.shape[0]

    # Normalize W for stable dynamics
    d = np.sum(W, axis=1)
    d_safe = np.where(d > 0, d, 1.0)
    W_norm = W / d_safe[:, None]

    # Coupling strength (controls how much network structure affects dynamics)
    alpha = 0.15

    # Neural dynamics
    x = rng.normal(0, 0.1, (T, n))
    for t in range(1, T):
        coupling = W_norm @ x[t - 1]
        x[t] = (1 - alpha) * x[t - 1] + alpha * coupling + rng.normal(0, 0.3, n)

    # Hemodynamic response (simple convolution)
    # Balloon model approximation: 6s peak
    hrf_len = int(30 / TR)
    t_hrf = np.arange(hrf_len) * TR
    hrf = t_hrf * np.exp(-t_hrf / 1.5) / 1.5  # gamma function approximation
    hrf /= np.sum(hrf)

    bold = np.zeros((T, n))
    for i in range(n):
        bold[:, i] = np.convolve(x[:, i], hrf, mode='same')

    # Add measurement noise
    bold += rng.normal(0, 0.05 * np.std(bold), bold.shape)

    return bold


def _assign_modules(n, rng):
    """Assign nodes to modules based on Yeo-7 proportions."""
    labels = np.zeros(n, dtype=int)
    sizes = list(MODULE_SIZES.values())
    # Normalize
    sizes = [s / sum(sizes) for s in sizes]

    idx = 0
    for mod_id, frac in enumerate(sizes):
        n_mod = int(round(frac * n))
        if mod_id == len(sizes) - 1:
            n_mod = n - idx  # last module gets remainder
        labels[idx:idx + n_mod] = mod_id
        idx += n_mod

    # Shuffle to avoid artificial spatial ordering
    rng.shuffle(labels)
    return labels


def _compute_lambda2(W):
    """Fiedler value of normalized graph Laplacian."""
    d = np.sum(W, axis=1)
    d_inv_sqrt = np.zeros_like(d, dtype=float)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_sym = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    L_sym = 0.5 * (L_sym + L_sym.T)
    eigenvals = eigh(L_sym, eigvals_only=True)
    return np.sort(eigenvals)[1]


# ══════════════════════════════════════════
# MAIN: Generate and save
# ══════════════════════════════════════════

if __name__ == "__main__":
    import os
    import json
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate HCP-like connectomes from literature statistics')
    parser.add_argument('--n-subjects', type=int, default=30)
    parser.add_argument('--n-regions', type=int, default=360)
    parser.add_argument('--output-dir', type=str, default='generated_data')
    parser.add_argument('--with-bold', action='store_true',
                        help='Also generate synthetic BOLD time series')
    args = parser.parse_args()

    out = Path(args.output_dir) if 'Path' in dir() else __import__('pathlib').Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / 'connectomes').mkdir(exist_ok=True)
    if args.with_bold:
        (out / 'timeseries').mkdir(exist_ok=True)

    print(f"Generating {args.n_subjects} HCP-like connectomes "
          f"({args.n_regions} regions)...")

    connectomes, metadata = generate_cohort(
        args.n_subjects, args.n_regions, seed=42)

    for i, (W, meta) in enumerate(zip(connectomes, metadata)):
        sid = meta['subject_id']
        np.save(str(out / 'connectomes' / f'{sid}.npy'), W)

        if args.with_bold:
            print(f"  [{i+1}/{args.n_subjects}] {sid}: "
                  f"λ₂={meta['actual_lambda2']:.4f}, generating BOLD...",
                  end='', flush=True)
            bold = generate_bold_timeseries(W, seed=42 + i)
            np.save(str(out / 'timeseries' / f'{sid}.npy'), bold)
            print(" done")
        else:
            print(f"  [{i+1}/{args.n_subjects}] {sid}: "
                  f"λ₂={meta['actual_lambda2']:.4f}")

    # Save metadata
    # Convert non-serializable items
    for m in metadata:
        m['actual_lambda2'] = float(m['actual_lambda2'])
        m['density'] = float(m['density'])
        m['mean_degree'] = float(m['mean_degree'])

    with open(str(out / 'metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=2)

    lambda2s = [m['actual_lambda2'] for m in metadata]
    print(f"\nDone. λ₂ range: [{min(lambda2s):.3f}, {max(lambda2s):.3f}]")
    print(f"Output in: {out}")
