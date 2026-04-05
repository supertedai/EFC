#!/usr/bin/env python3
"""
Bridge B1* Test on Real HCP Group-Average Data
================================================
Uses ENIGMA HCP group-average connectomes (Schaefer-200, Glasser-360)
to test the EFC prediction.

This is a GROUP-AVERAGE test (single connectome, not individual subjects).
It tests:
  1. Whether κ from functional connectivity has the right magnitude
  2. Whether the absolute prediction κ = C/(1 + λ₂·τ_c) is in range

For a full individual-subject correlation test, per-subject connectomes
are needed (see Czech/OSF dataset or Lausanne/Zenodo dataset).
"""

import numpy as np
from pathlib import Path
import sys
import json

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))

from efc_model_comparison import C_FIXED, TAU_C_LITERATURE

DATA_DIR = Path(__file__).parent / 'real_data'


def load_csv_matrix(path):
    """Load a CSV connectivity matrix."""
    return np.loadtxt(path, delimiter=',')


def compute_lambda2(W):
    """Fiedler value of normalized graph Laplacian."""
    from scipy.linalg import eigh
    d = np.sum(W, axis=1)
    d_inv_sqrt = np.zeros_like(d, dtype=float)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_sym = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    L_sym = 0.5 * (L_sym + L_sym.T)
    eigenvals = eigh(L_sym, eigvals_only=True)
    return np.sort(eigenvals)[1]


def entropy_from_functional(FC, W_struct):
    """
    Estimate entropy proxy from functional connectivity.

    Uses the variability (std across connections) of FC per node as proxy
    for temporal complexity. Nodes with more diverse functional connections
    have higher "entropy" in the information-theoretic sense.

    Also computes: strength diversity = std(FC_i) / mean(FC_i)
    """
    # Method 1: FC strength variability (coefficient of variation)
    fc_std = np.std(FC, axis=1)
    fc_mean = np.mean(np.abs(FC), axis=1)
    entropy_cv = fc_std / np.where(fc_mean > 0, fc_mean, 1e-10)

    # Method 2: Participation coefficient (functional diversity)
    # How evenly distributed are a node's functional connections?
    FC_abs = np.abs(FC)
    FC_norm = FC_abs / np.sum(FC_abs, axis=1, keepdims=True)
    FC_norm = np.where(np.isfinite(FC_norm), FC_norm, 0)
    # Shannon entropy of normalized FC
    with np.errstate(divide='ignore', invalid='ignore'):
        entropy_shannon = -np.nansum(FC_norm * np.log(FC_norm + 1e-15), axis=1)

    return {
        'cv': entropy_cv,
        'shannon': entropy_shannon,
    }


def classify_hubs(W, hub_pct=0.10, periph_pct=0.30):
    """Classify by structural degree."""
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)
    n = len(degree)
    periph_idx = sorted_idx[:int(periph_pct * n)]
    hub_idx = sorted_idx[-int(hub_pct * n):]
    return hub_idx, periph_idx


def kappa_predicted(lambda2):
    """B1* prediction."""
    return C_FIXED / (1.0 + lambda2 * TAU_C_LITERATURE)


def run_test(name, W_struct, FC=None):
    """Run B1* test on one parcellation."""
    n = W_struct.shape[0]

    print(f"\n{'━' * 60}")
    print(f"  {name} ({n} regions)")
    print(f"{'━' * 60}")

    # Network properties
    lambda2 = compute_lambda2(W_struct)
    density = np.sum(W_struct > 0) / (n * (n - 1))
    mean_degree = np.mean(np.sum(W_struct > 0, axis=1))

    print(f"\n  Network properties:")
    print(f"    λ₂ (Fiedler):   {lambda2:.4f}")
    print(f"    Density:         {density:.4f}")
    print(f"    Mean degree:     {mean_degree:.1f}")

    # B1* prediction
    kappa_pred = kappa_predicted(lambda2)
    print(f"\n  B1* prediction:")
    print(f"    C = {C_FIXED} (from SPARC galaxies)")
    print(f"    τ_c = {TAU_C_LITERATURE} s (literature)")
    print(f"    κ_pred = C / (1 + λ₂·τ_c) = {kappa_pred:.3f}")

    # Hub/periphery
    hub_idx, periph_idx = classify_hubs(W_struct)
    hub_degree = np.mean(np.sum(W_struct > 0, axis=1)[hub_idx])
    periph_degree = np.mean(np.sum(W_struct > 0, axis=1)[periph_idx])
    print(f"\n  Hub/periphery classification:")
    print(f"    Hub nodes:     {len(hub_idx)} (top 10%, mean degree = {hub_degree:.1f})")
    print(f"    Periph nodes:  {len(periph_idx)} (bottom 30%, mean degree = {periph_degree:.1f})")

    results = {
        'name': name,
        'n_regions': n,
        'lambda2': float(lambda2),
        'density': float(density),
        'mean_degree': float(mean_degree),
        'kappa_pred': float(kappa_pred),
        'n_hub': len(hub_idx),
        'n_periph': len(periph_idx),
    }

    if FC is not None:
        # Compute entropy proxies
        entropy_proxies = entropy_from_functional(FC, W_struct)

        print(f"\n  Entropy proxies from functional connectivity:")

        for proxy_name, entropy in entropy_proxies.items():
            s_hub = np.mean(entropy[hub_idx])
            s_periph = np.mean(entropy[periph_idx])
            kappa_obs = s_hub / s_periph if s_periph > 0 else float('nan')

            deviation = abs(kappa_obs - kappa_pred) / kappa_pred * 100

            print(f"\n    [{proxy_name}]")
            print(f"      S_hub:      {s_hub:.4f}")
            print(f"      S_periph:   {s_periph:.4f}")
            print(f"      κ_obs:      {kappa_obs:.3f}")
            print(f"      κ_pred:     {kappa_pred:.3f}")
            print(f"      Deviation:  {deviation:.1f}%")

            if kappa_obs > 1.0:
                print(f"      ✓ Centrifugal gradient confirmed (hub > periphery)")
            else:
                print(f"      ✗ No centrifugal gradient (hub ≤ periphery)")

            results[f'kappa_obs_{proxy_name}'] = float(kappa_obs)
            results[f'deviation_{proxy_name}'] = float(deviation)

    # Structural entropy (from degree distribution)
    degree = np.sum(W_struct, axis=1)
    log_degree = np.log1p(degree)
    s_hub_struct = np.mean(log_degree[hub_idx])
    s_periph_struct = np.mean(log_degree[periph_idx])
    kappa_struct = s_hub_struct / s_periph_struct

    print(f"\n    [structural degree proxy]")
    print(f"      log(1+degree)_hub:    {s_hub_struct:.4f}")
    print(f"      log(1+degree)_periph: {s_periph_struct:.4f}")
    print(f"      κ_struct:             {kappa_struct:.3f}")
    results['kappa_struct'] = float(kappa_struct)

    return results


def main():
    print("=" * 60)
    print("BRIDGE B1* TEST ON REAL HCP DATA")
    print("ENIGMA HCP Group-Average Connectomes")
    print("=" * 60)

    all_results = []

    # ── Schaefer 200 ──
    sc200_path = DATA_DIR / 'strucMatrix_schaefer200.csv'
    fc200_path = DATA_DIR / 'funcMatrix_schaefer200.csv'

    if sc200_path.exists():
        W200 = load_csv_matrix(sc200_path)
        FC200 = load_csv_matrix(fc200_path) if fc200_path.exists() else None
        res = run_test("HCP Schaefer-200", W200, FC200)
        all_results.append(res)

    # ── Glasser 360 ──
    sc360_path = DATA_DIR / 'strucMatrix_glasser360.csv'
    fc360_path = DATA_DIR / 'funcMatrix_glasser360.csv'

    if sc360_path.exists():
        W360 = load_csv_matrix(sc360_path)
        FC360 = load_csv_matrix(fc360_path) if fc360_path.exists() else None
        res = run_test("HCP Glasser-360 (MMP1.0)", W360, FC360)
        all_results.append(res)

    # ── Summary ──
    print(f"\n{'═' * 60}")
    print("SUMMARY")
    print(f"{'═' * 60}")
    print()
    print(f"  {'Atlas':<25s} {'λ₂':>6s} {'κ_pred':>7s} {'κ_obs':>7s} {'Dev':>6s}")
    print(f"  {'─' * 25} {'─' * 6} {'─' * 7} {'─' * 7} {'─' * 6}")

    for r in all_results:
        # Use best entropy proxy: CV first, then structural
        kappa_obs = r.get('kappa_obs_cv', r.get('kappa_struct', None))
        dev = r.get('deviation_cv', None)
        if kappa_obs is not None and dev is not None:
            print(f"  {r['name']:<25s} {r['lambda2']:>6.4f} {r['kappa_pred']:>7.3f} "
                  f"{kappa_obs:>7.3f} {dev:>5.1f}%")
        else:
            print(f"  {r['name']:<25s} {r['lambda2']:>6.4f} {r['kappa_pred']:>7.3f} "
                  f"  {'—':>5s}   {'—':>4s}")

    print()
    print("  INTERPRETATION:")
    print("  This is a GROUP-AVERAGE test (n=1). It tests absolute level only.")
    print("  The correlation test r(κ, 1/λ₂) requires individual subjects.")
    print("  For individual subjects, use the Czech/OSF (88 subj) or")
    print("  Lausanne/Zenodo (70 subj) datasets.")

    # Save
    output_path = DATA_DIR / 'results_real_hcp.json'
    with open(output_path, 'w') as f:
        json.dump(all_results, f, indent=2)
    print(f"\n  Results saved to {output_path}")


if __name__ == "__main__":
    main()
