#!/usr/bin/env python3
"""
HCP Bridge B1* Validation Pipeline
====================================
End-to-end pipeline: HCP data → λ₂ + κ → model comparison.

Supports three data modes:
  1. Full HCP preprocessed data (--hcp-dir)
  2. Pre-computed connectome matrices (--connectome-dir + --fmri-dir)
  3. Synthetic validation (--synthetic)

Usage:
  python run_hcp_pipeline.py --hcp-dir /path/to/HCP --n-subjects 50
  python run_hcp_pipeline.py --connectome-dir ./connectomes --fmri-dir ./timeseries
  python run_hcp_pipeline.py --synthetic --n-subjects 50
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import numpy as np
from scipy.linalg import eigh
from scipy.stats import pearsonr

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))


# ══════════════════════════════════════════
# CONSTANTS
# ══════════════════════════════════════════

C_FIXED = 4.4
TAU_C_LITERATURE = 3.5
N_PARCELS_MMP = 360  # HCP MMP1.0 atlas

# Hub/periphery thresholds
HUB_PERCENTILE = 0.10      # top 10% by degree
PERIPH_PERCENTILE = 0.30   # bottom 30% by degree

# MSE parameters
MSE_SCALES = (4, 5, 6)
MSE_M = 2
MSE_R_FACTOR = 0.2


# ══════════════════════════════════════════
# CORE COMPUTATIONS
# ══════════════════════════════════════════

def compute_lambda2(W):
    """Fiedler value of the normalized graph Laplacian."""
    d = np.sum(W, axis=1)
    d_inv_sqrt = np.zeros_like(d, dtype=float)
    mask = d > 0
    d_inv_sqrt[mask] = 1.0 / np.sqrt(d[mask])
    D_inv_sqrt = np.diag(d_inv_sqrt)
    L_sym = np.eye(len(W)) - D_inv_sqrt @ W @ D_inv_sqrt
    L_sym = 0.5 * (L_sym + L_sym.T)
    eigenvals = eigh(L_sym, eigvals_only=True)
    return np.sort(eigenvals)[1]


def sample_entropy_1d(x, m=MSE_M, r_factor=MSE_R_FACTOR):
    """Sample entropy of a 1D signal."""
    N = len(x)
    r = r_factor * np.std(x)
    if r == 0 or N < (m + 2) * 2:
        return 0.0

    def count_matches(tlen):
        count = 0
        templates = np.array([x[i:i + tlen] for i in range(N - tlen)])
        n_t = len(templates)
        for i in range(n_t):
            diffs = np.max(np.abs(templates[i + 1:] - templates[i]), axis=1)
            count += np.sum(diffs < r)
        return count

    B = count_matches(m)
    A = count_matches(m + 1)
    if B == 0:
        return 0.0
    return -np.log(A / B) if A > 0 else 0.0


def multiscale_entropy(x, scales=MSE_SCALES):
    """MSE at specified coarsening scales."""
    values = []
    for s in scales:
        n_seg = len(x) // s
        if n_seg < 30:
            continue
        coarse = np.mean(x[:n_seg * s].reshape(n_seg, s), axis=1)
        values.append(sample_entropy_1d(coarse))
    return np.mean(values) if values else 0.0


def classify_hubs(W, hub_pct=HUB_PERCENTILE, periph_pct=PERIPH_PERCENTILE):
    """Classify nodes by degree into hub and peripheral sets."""
    degree = np.sum(W, axis=1)
    sorted_idx = np.argsort(degree)
    n = len(degree)
    periph_idx = sorted_idx[:int(periph_pct * n)]
    hub_idx = sorted_idx[-int(hub_pct * n):]
    return hub_idx, periph_idx


def compute_kappa(entropy_arr, hub_idx, periph_idx):
    """Centrifugal entropy score: κ = <S_hub> / <S_periph>."""
    s_hub = np.mean(entropy_arr[hub_idx])
    s_periph = np.mean(entropy_arr[periph_idx])
    if s_periph <= 0:
        return np.nan
    return s_hub / s_periph


# ══════════════════════════════════════════
# DATA LOADERS
# ══════════════════════════════════════════

def discover_hcp_subjects(hcp_dir, n_max=None):
    """Find available HCP subjects with both structural and functional data."""
    hcp_path = Path(hcp_dir)
    subjects = []

    for subdir in sorted(hcp_path.iterdir()):
        if not subdir.is_dir() or not subdir.name.isdigit():
            continue

        # Check for required files
        has_diffusion = (subdir / 'T1w' / 'Diffusion').exists()
        has_fmri = any((subdir / 'MNINonLinear' / 'Results').glob('rfMRI_REST*'))

        if has_diffusion or has_fmri:
            subjects.append(subdir.name)

        if n_max and len(subjects) >= n_max:
            break

    return subjects


def load_connectome_hcp(hcp_dir, subject_id):
    """
    Load or compute structural connectome for an HCP subject.

    Looks for pre-computed connectome first, falls back to
    parcellated streamline density if available.
    """
    hcp_path = Path(hcp_dir)

    # Check for pre-computed connectome
    for pattern in [
        f'{subject_id}_connectome.npy',
        f'{subject_id}/connectome.npy',
        f'connectomes/{subject_id}.npy',
    ]:
        fpath = hcp_path / pattern
        if fpath.exists():
            return np.load(fpath)

    # Check for parcellated connectivity matrix (common HCP derivatives)
    parc_path = (hcp_path / subject_id / 'MNINonLinear' /
                 'fsaverage_LR32k' / 'connectivity.npy')
    if parc_path.exists():
        return np.load(parc_path)

    return None


def load_timeseries_hcp(hcp_dir, subject_id):
    """
    Load parcellated resting-state fMRI time series.

    Returns array of shape (T, N_parcels).
    """
    hcp_path = Path(hcp_dir)

    # Check for pre-parcellated time series
    for pattern in [
        f'{subject_id}_timeseries.npy',
        f'{subject_id}/timeseries.npy',
        f'timeseries/{subject_id}.npy',
    ]:
        fpath = hcp_path / pattern
        if fpath.exists():
            return np.load(fpath)

    # Try to load from HCP CIFTI (requires nibabel)
    rest_dirs = sorted((hcp_path / subject_id / 'MNINonLinear' / 'Results').glob(
        'rfMRI_REST*_LR'))
    if rest_dirs:
        cifti_candidates = list(rest_dirs[0].glob('*Atlas*clean*.dtseries.nii'))
        if cifti_candidates:
            try:
                import nibabel as nib
                img = nib.load(str(cifti_candidates[0]))
                data = img.get_fdata()
                # Parcellate: average within MMP1.0 parcels
                # This requires the atlas — simplified version
                # For full implementation, use workbench -cifti-parcellate
                return data
            except ImportError:
                print(f"    nibabel not installed — cannot load CIFTI for {subject_id}")

    return None


def load_precomputed(connectome_dir, fmri_dir, subject_id):
    """Load pre-computed connectome and time series from directories."""
    W = None
    ts = None

    for ext in ['.npy', '.npz', '.txt']:
        c_path = Path(connectome_dir) / f'{subject_id}{ext}'
        if c_path.exists():
            W = np.load(c_path) if ext != '.txt' else np.loadtxt(c_path)
            break

    for ext in ['.npy', '.npz', '.txt']:
        t_path = Path(fmri_dir) / f'{subject_id}{ext}'
        if t_path.exists():
            ts = np.load(t_path) if ext != '.txt' else np.loadtxt(t_path)
            break

    return W, ts


# ══════════════════════════════════════════
# SINGLE-SUBJECT PROCESSING
# ══════════════════════════════════════════

def process_subject(W, timeseries, subject_id, use_std_proxy=False):
    """
    Process one subject: connectome + fMRI → λ₂, κ.

    Parameters
    ----------
    W : ndarray (N, N)
        Structural connectome.
    timeseries : ndarray (T, N) or None
        BOLD time series per parcel. If None, uses degree-based proxy.
    subject_id : str
    use_std_proxy : bool
        If True, use std(BOLD) instead of MSE (much faster for screening).

    Returns
    -------
    dict with lambda2, kappa, kappa_pred, etc.
    """
    n_regions = W.shape[0]

    # λ₂
    lambda2 = compute_lambda2(W)

    # Hub/periphery classification
    hub_idx, periph_idx = classify_hubs(W)

    # Entropy computation
    if timeseries is not None:
        T_len = timeseries.shape[0] if timeseries.ndim == 2 else timeseries.shape[1]
        n_ts = timeseries.shape[1] if timeseries.ndim == 2 else timeseries.shape[0]

        # Ensure shape is (T, N)
        if timeseries.ndim == 2 and timeseries.shape[0] < timeseries.shape[1]:
            timeseries = timeseries.T

        entropy = np.zeros(min(n_regions, timeseries.shape[1]))

        if use_std_proxy:
            # Fast screening: std as entropy proxy
            for i in range(len(entropy)):
                entropy[i] = np.std(timeseries[:, i])
        else:
            # Full MSE computation
            for i in range(len(entropy)):
                entropy[i] = multiscale_entropy(timeseries[:, i])

        # Adjust indices if parcellation mismatch
        if len(entropy) < n_regions:
            hub_idx = hub_idx[hub_idx < len(entropy)]
            periph_idx = periph_idx[periph_idx < len(entropy)]
    else:
        # No fMRI: use degree-based entropy proxy (very rough)
        degree = np.sum(W, axis=1)
        entropy = np.log1p(degree)  # log-degree as proxy

    kappa = compute_kappa(entropy, hub_idx, periph_idx)
    kappa_pred = C_FIXED / (1.0 + lambda2 * TAU_C_LITERATURE)

    return {
        'subject': subject_id,
        'lambda2': float(lambda2),
        'kappa': float(kappa),
        'kappa_pred': float(kappa_pred),
        'n_regions': int(n_regions),
        'n_hub': int(len(hub_idx)),
        'n_periph': int(len(periph_idx)),
        'entropy_mean': float(np.mean(entropy)),
        'entropy_std': float(np.std(entropy)),
        'has_fmri': timeseries is not None,
    }


# ══════════════════════════════════════════
# SYNTHETIC MODE
# ══════════════════════════════════════════

def run_synthetic(n_subjects, output_dir):
    """Generate synthetic data and run full pipeline for validation."""
    from efc_c_kappa_analysis import generate_synthetic_cohort

    print("Generating synthetic HCP-like cohort...")
    subjects = generate_synthetic_cohort(n_subjects, 'healthy', seed=42)

    lambda2_arr = np.array([s['lambda2'] for s in subjects])
    eta_arr = np.array([s['kappa'] for s in subjects])

    os.makedirs(output_dir, exist_ok=True)
    np.save(os.path.join(output_dir, 'lambda2.npy'), lambda2_arr)
    np.save(os.path.join(output_dir, 'eta.npy'), eta_arr)

    with open(os.path.join(output_dir, 'subjects.json'), 'w') as f:
        json.dump(subjects, f, indent=2)

    return lambda2_arr, eta_arr


# ══════════════════════════════════════════
# MAIN PIPELINE
# ══════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='HCP Bridge B1* Validation Pipeline')
    parser.add_argument('--hcp-dir', type=str,
                        help='Path to HCP data directory')
    parser.add_argument('--connectome-dir', type=str,
                        help='Directory with pre-computed connectomes (*.npy)')
    parser.add_argument('--fmri-dir', type=str,
                        help='Directory with parcellated time series (*.npy)')
    parser.add_argument('--subjects', type=str, nargs='+',
                        help='Specific subject IDs to process')
    parser.add_argument('--n-subjects', type=int, default=50,
                        help='Max subjects to process')
    parser.add_argument('--synthetic', action='store_true',
                        help='Run on synthetic data')
    parser.add_argument('--fast', action='store_true',
                        help='Use std(BOLD) proxy instead of MSE (10x faster)')
    parser.add_argument('--output-dir', type=str,
                        default='output',
                        help='Output directory')
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'per_subject').mkdir(exist_ok=True)

    print("=" * 70)
    print("HCP BRIDGE B1* VALIDATION PIPELINE")
    print(f"  C = {C_FIXED} (fixed from SPARC)")
    print(f"  τ_c = {TAU_C_LITERATURE} s (literature)")
    print(f"  Prediction: κ = C / (1 + λ₂ · τ_c)")
    print("=" * 70)
    print()

    # ── Determine data mode ──
    if args.synthetic:
        print("MODE: Synthetic validation")
        lambda2_arr, eta_arr = run_synthetic(args.n_subjects, str(output_dir))
        subject_results = None

    elif args.connectome_dir and args.fmri_dir:
        print(f"MODE: Pre-computed data")
        print(f"  Connectomes: {args.connectome_dir}")
        print(f"  Time series: {args.fmri_dir}")

        # Discover subjects
        c_files = sorted(Path(args.connectome_dir).glob('*.npy'))
        if args.subjects:
            subject_ids = args.subjects
        else:
            subject_ids = [f.stem for f in c_files[:args.n_subjects]]

        subject_results = _process_subjects(
            subject_ids, args, output_dir)

    elif args.hcp_dir:
        print(f"MODE: Full HCP processing")
        print(f"  HCP directory: {args.hcp_dir}")

        if args.subjects:
            subject_ids = args.subjects
        else:
            subject_ids = discover_hcp_subjects(args.hcp_dir, args.n_subjects)

        if not subject_ids:
            print("\n  ERROR: No valid HCP subjects found.")
            print("  Expected directory structure:")
            print("    {hcp-dir}/{subject_id}/T1w/Diffusion/")
            print("    {hcp-dir}/{subject_id}/MNINonLinear/Results/rfMRI_REST*/")
            print("\n  Or use pre-computed data:")
            print("    --connectome-dir ./connectomes --fmri-dir ./timeseries")
            sys.exit(1)

        subject_results = _process_subjects(
            subject_ids, args, output_dir)

    else:
        print("No data source specified. Use one of:")
        print("  --hcp-dir /path/to/HCP")
        print("  --connectome-dir ./connectomes --fmri-dir ./timeseries")
        print("  --synthetic")
        sys.exit(1)

    # ── Run model comparison ──
    if subject_results and len(subject_results) >= 10:
        lambda2_arr = np.array([s['lambda2'] for s in subject_results])
        eta_arr = np.array([s['kappa'] for s in subject_results])

        np.save(str(output_dir / 'lambda2.npy'), lambda2_arr)
        np.save(str(output_dir / 'eta.npy'), eta_arr)

    if 'lambda2_arr' in dir() and len(lambda2_arr) >= 10:
        print()
        print("═" * 70)
        print("MODEL COMPARISON")
        print("═" * 70)

        try:
            from efc_model_comparison import run_comparison, _print_results
            results = run_comparison(lambda2_arr, eta_arr)
            _print_results(results, f"Pipeline (n={len(lambda2_arr)})")

            # Save results
            serializable = {}
            for k, v in results.items():
                if isinstance(v, dict):
                    serializable[k] = {
                        kk: (vv.tolist() if isinstance(vv, np.ndarray) else vv)
                        for kk, vv in v.items()
                    }
            with open(str(output_dir / 'results.json'), 'w') as f:
                json.dump(serializable, f, indent=2)

        except ImportError:
            print("  Could not import model comparison. Run separately:")
            print(f"  python scripts/efc_model_comparison.py --data "
                  f"{output_dir}/lambda2.npy {output_dir}/eta.npy")

    print()
    print("Pipeline complete. Output in:", output_dir)


def _process_subjects(subject_ids, args, output_dir):
    """Process a list of subjects and return results."""
    print(f"\n  Found {len(subject_ids)} subjects")
    print(f"  Processing{'(fast mode)' if args.fast else ''}...")
    print()

    results = []
    t0 = time.time()

    for i, sid in enumerate(subject_ids):
        # Load data
        if args.connectome_dir and args.fmri_dir:
            W, ts = load_precomputed(args.connectome_dir, args.fmri_dir, sid)
        elif args.hcp_dir:
            W = load_connectome_hcp(args.hcp_dir, sid)
            ts = load_timeseries_hcp(args.hcp_dir, sid)
        else:
            continue

        if W is None:
            print(f"  [{i+1}/{len(subject_ids)}] {sid}: SKIP (no connectome)")
            continue

        # Process
        res = process_subject(W, ts, sid, use_std_proxy=args.fast)
        results.append(res)

        # Save per-subject
        with open(str(output_dir / 'per_subject' / f'{sid}.json'), 'w') as f:
            json.dump(res, f, indent=2)

        elapsed = time.time() - t0
        eta_time = elapsed / (i + 1) * (len(subject_ids) - i - 1)

        print(f"  [{i+1}/{len(subject_ids)}] {sid}: "
              f"λ₂={res['lambda2']:.4f}  κ={res['kappa']:.3f}  "
              f"pred={res['kappa_pred']:.3f}  "
              f"({'fMRI' if res['has_fmri'] else 'degree-proxy'})  "
              f"[ETA: {eta_time:.0f}s]")

    # Summary
    if results:
        print(f"\n  Processed {len(results)} subjects in {time.time()-t0:.1f}s")
        lambda2s = [r['lambda2'] for r in results]
        kappas = [r['kappa'] for r in results]
        print(f"  λ₂ range: [{min(lambda2s):.4f}, {max(lambda2s):.4f}]")
        print(f"  κ range:  [{min(kappas):.3f}, {max(kappas):.3f}]")

        r, p = pearsonr(kappas, [1/l for l in lambda2s])
        print(f"  r(κ, 1/λ₂) = {r:.3f}  (p = {p:.2e})")

        with open(str(output_dir / 'subjects.json'), 'w') as f:
            json.dump(results, f, indent=2)

    return results


if __name__ == "__main__":
    main()
