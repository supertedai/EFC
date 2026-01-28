"""
EFC Lensing Postulate v1.1 - NON-LOCAL + COMPONENT-SENSITIVE
=============================================================

Addresses the edge-detector failure mode with:
1. Combined curvature + gradient signal
2. Non-local convolution (spatial "memory")
3. Component-sensitive coupling (galaxy weighting)

POSTULATE v1.1:
    q_∇ = |∇ln(Σ_b)|           # edge signal
    q_Δ = -∇²ln(Σ_b)           # center signal (positive at peaks)
    q = (1-β)×q_Δ + β×q_∇      # combined, β=0.3 FIXED
    q̄ = K_L₀ * q               # non-local smoothing
    
    Σ_eff = Σ_gas×(1 + α×q̄) + w×Σ_stellar×(1 + α×q̄)
    κ_EFC = Σ_eff / Σ_c

FREE PARAMETERS: α, L₀, w (only 3)
FIXED: β = 0.3
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.ndimage import gaussian_filter
import json
from dataclasses import dataclass
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

from efc_lensing_test import (
    PIXEL_SCALE_KPC, SIGMA_C, 
    generate_bullet_cluster_data, find_peaks, compute_chi2
)

# FIXED parameter
BETA = 0.3  # Edge vs center weighting - LOCKED

@dataclass
class TestResultV11:
    """Results for v1.1 non-local model."""
    alpha: float
    L0_kpc: float
    w: float
    beta: float  # Fixed, but record it
    n_peaks_found: int
    peak_positions_pix: List[Tuple[int, int]]
    peak_positions_kpc: List[Tuple[float, float]]
    gas_offsets_kpc: List[float]
    galaxy_offsets_kpc: List[float]
    peak_ratio: float
    chi2: float
    pass_peak_count: bool
    pass_gas_offset: bool
    pass_galaxy_proximity: bool
    pass_peak_ratio: bool
    overall_pass: bool


def compute_kappa_EFC_v11_nonlocal(
    Sigma_stellar: np.ndarray,
    Sigma_gas: np.ndarray,
    alpha: float,
    L0_kpc: float,
    w: float,
    beta: float = BETA,
    pixel_scale: float = PIXEL_SCALE_KPC,
    smoothing_sigma: float = 1.5
) -> np.ndarray:
    """
    Compute EFC convergence with NON-LOCAL + COMPONENT-SENSITIVE model.
    
    POSTULATE v1.1:
        q_∇ = |∇ln(Σ_b)|
        q_Δ = -∇²ln(Σ_b)
        q = (1-β)×q_Δ + β×q_∇
        q̄ = Gaussian_L₀ * q
        Σ_eff = Σ_gas×(1 + α×q̄) + w×Σ_stellar×(1 + α×q̄)
        κ_EFC = Σ_eff / Σ_c
    """
    
    # Combined baryonic field
    Sigma_b = Sigma_gas + Sigma_stellar
    Sigma_b_safe = np.maximum(Sigma_b, 1e-10)
    ln_Sigma = np.log(Sigma_b_safe)
    
    # Edge signal: |∇ln(Σ_b)|
    grad_y, grad_x = np.gradient(ln_Sigma)
    q_grad = np.sqrt(grad_x**2 + grad_y**2) / pixel_scale  # [1/kpc]
    
    # Center signal: -∇²ln(Σ_b) (positive at peaks)
    laplacian = ndimage.laplace(ln_Sigma) / (pixel_scale**2)  # [1/kpc²]
    q_curv = -laplacian  # Flip sign so positive at density peaks
    
    # Normalize to similar scales
    q_grad_norm = q_grad / (np.std(q_grad) + 1e-10)
    q_curv_norm = q_curv / (np.std(q_curv) + 1e-10)
    
    # Combined signal (β FIXED)
    q = (1 - beta) * q_curv_norm + beta * q_grad_norm
    
    # Non-local convolution with Gaussian kernel
    # L0_kpc -> pixel sigma
    L0_pix = L0_kpc / pixel_scale
    q_bar = gaussian_filter(q, sigma=L0_pix)
    
    # Normalize q_bar to reasonable range
    q_bar = q_bar / (np.abs(q_bar).max() + 1e-10)
    
    # Component-sensitive effective surface density
    # Gas gets weight 1, stellar gets weight w
    G_eff = 1.0 + alpha * q_bar
    G_eff = np.maximum(G_eff, 0.1)  # Keep positive
    
    Sigma_eff = Sigma_gas * G_eff + w * Sigma_stellar * G_eff
    
    # Convergence
    kappa_EFC = Sigma_eff / SIGMA_C
    
    # Final smoothing to match observed map
    kappa_EFC = gaussian_filter(kappa_EFC, sigma=smoothing_sigma)
    
    return kappa_EFC


def run_v11_nonlocal_test(data: Dict, alpha: float, L0_kpc: float, w: float) -> TestResultV11:
    """Run test with v1.1 non-local model."""
    
    size = data['size']
    center = size // 2
    
    kappa_EFC = compute_kappa_EFC_v11_nonlocal(
        data['Sigma_stellar'],
        data['Sigma_gas'],
        alpha=alpha,
        L0_kpc=L0_kpc,
        w=w
    )
    
    peaks_pix = find_peaks(kappa_EFC)
    n_peaks = len(peaks_pix)
    
    peaks_kpc = [(
        (p[0] - center) * PIXEL_SCALE_KPC,
        (p[1] - center) * PIXEL_SCALE_KPC
    ) for p in peaks_pix]
    
    pos = data['positions']
    main_gas_kpc = ((pos['main_gas_pix'][0] - center) * PIXEL_SCALE_KPC,
                    (pos['main_gas_pix'][1] - center) * PIXEL_SCALE_KPC)
    sub_gas_kpc = ((pos['sub_gas_pix'][0] - center) * PIXEL_SCALE_KPC,
                   (pos['sub_gas_pix'][1] - center) * PIXEL_SCALE_KPC)
    main_gal_kpc = ((pos['main_gal_pix'][0] - center) * PIXEL_SCALE_KPC,
                    (pos['main_gal_pix'][1] - center) * PIXEL_SCALE_KPC)
    sub_gal_kpc = ((pos['sub_gal_pix'][0] - center) * PIXEL_SCALE_KPC,
                   (pos['sub_gal_pix'][1] - center) * PIXEL_SCALE_KPC)
    
    gas_offsets = []
    galaxy_offsets = []
    
    if n_peaks >= 2:
        d_main_gas = np.sqrt((peaks_kpc[0][0] - main_gas_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gas_kpc[1])**2)
        d_main_gal = np.sqrt((peaks_kpc[0][0] - main_gal_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gal_kpc[1])**2)
        d_sub_gas = np.sqrt((peaks_kpc[1][0] - sub_gas_kpc[0])**2 + 
                            (peaks_kpc[1][1] - sub_gas_kpc[1])**2)
        d_sub_gal = np.sqrt((peaks_kpc[1][0] - sub_gal_kpc[0])**2 + 
                            (peaks_kpc[1][1] - sub_gal_kpc[1])**2)
        gas_offsets = [d_main_gas, d_sub_gas]
        galaxy_offsets = [d_main_gal, d_sub_gal]
    elif n_peaks == 1:
        d_main_gas = np.sqrt((peaks_kpc[0][0] - main_gas_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gas_kpc[1])**2)
        d_main_gal = np.sqrt((peaks_kpc[0][0] - main_gal_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gal_kpc[1])**2)
        gas_offsets = [d_main_gas]
        galaxy_offsets = [d_main_gal]
    
    if n_peaks >= 2:
        peak_ratio = kappa_EFC[peaks_pix[0][1], peaks_pix[0][0]] / \
                     kappa_EFC[peaks_pix[1][1], peaks_pix[1][0]]
    else:
        peak_ratio = 0.0
    
    chi2 = compute_chi2(kappa_EFC, data['kappa_observed'])
    
    pass_peak_count = (n_peaks == 2)
    pass_gas_offset = all(d > 100 for d in gas_offsets) if gas_offsets else False
    pass_galaxy_proximity = all(d < 50 for d in galaxy_offsets) if galaxy_offsets else False
    pass_peak_ratio = (0.9 <= peak_ratio <= 1.2) if peak_ratio > 0 else False
    
    overall_pass = pass_peak_count and pass_gas_offset and pass_galaxy_proximity and pass_peak_ratio
    
    return TestResultV11(
        alpha=alpha,
        L0_kpc=L0_kpc,
        w=w,
        beta=BETA,
        n_peaks_found=n_peaks,
        peak_positions_pix=peaks_pix,
        peak_positions_kpc=peaks_kpc,
        gas_offsets_kpc=gas_offsets,
        galaxy_offsets_kpc=galaxy_offsets,
        peak_ratio=peak_ratio,
        chi2=chi2,
        pass_peak_count=pass_peak_count,
        pass_gas_offset=pass_gas_offset,
        pass_galaxy_proximity=pass_galaxy_proximity,
        pass_peak_ratio=pass_peak_ratio,
        overall_pass=overall_pass
    )


if __name__ == "__main__":
    print("=" * 70)
    print("EFC LENSING POSTULATE v1.1 - NON-LOCAL + COMPONENT-SENSITIVE")
    print("=" * 70)
    print()
    print("POSTULATE:")
    print("  q = (1-β)×(-∇²ln Σ_b) + β×|∇ln Σ_b|   [β=0.3 FIXED]")
    print("  q̄ = Gaussian(L₀) * q")
    print("  Σ_eff = Σ_gas×(1+α×q̄) + w×Σ_stellar×(1+α×q̄)")
    print()
    print(f"FIXED: β = {BETA}")
    print("FREE:  α, L₀, w  (3 parameters)")
    print()
    
    data = generate_bullet_cluster_data()
    
    # Parameter grid
    alpha_values = np.array([0.5, 1.0, 2.0, 3.0, 5.0])
    L0_values = np.array([50, 100, 200, 500, 1000, 1500])
    w_values = np.array([1.0, 2.0, 5.0, 10.0, 20.0])
    
    print(f"α range: {alpha_values}")
    print(f"L₀ range: {L0_values} kpc")
    print(f"w range: {w_values}")
    print(f"Total combinations: {len(alpha_values) * len(L0_values) * len(w_values)}")
    print()
    
    results = []
    for alpha in alpha_values:
        for L0 in L0_values:
            for w in w_values:
                result = run_v11_nonlocal_test(data, alpha, L0, w)
                results.append(result)
    
    passing_results = [r for r in results if r.overall_pass]
    best_chi2_result = min(results, key=lambda r: r.chi2)
    
    # Find best galaxy proximity
    results_with_2peaks = [r for r in results if r.n_peaks_found == 2]
    if results_with_2peaks:
        best_gal_result = min(results_with_2peaks, 
                              key=lambda r: max(r.galaxy_offsets_kpc))
    else:
        best_gal_result = best_chi2_result
    
    print("=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    print(f"Total tests: {len(results)}")
    print(f"Passing tests: {len(passing_results)}")
    print()
    
    print("BEST χ² RESULT:")
    print(f"  α = {best_chi2_result.alpha}")
    print(f"  L₀ = {best_chi2_result.L0_kpc} kpc")
    print(f"  w = {best_chi2_result.w}")
    print(f"  χ² = {best_chi2_result.chi2:.4f}")
    print(f"  Peaks: {best_chi2_result.n_peaks_found}")
    print(f"  Galaxy offsets: {[f'{d:.1f}' for d in best_chi2_result.galaxy_offsets_kpc]} kpc")
    print(f"  Gas offsets: {[f'{d:.1f}' for d in best_chi2_result.gas_offsets_kpc]} kpc")
    print(f"  Peak ratio: {best_chi2_result.peak_ratio:.3f}")
    print()
    
    print("BEST GALAXY PROXIMITY RESULT:")
    print(f"  α = {best_gal_result.alpha}")
    print(f"  L₀ = {best_gal_result.L0_kpc} kpc")
    print(f"  w = {best_gal_result.w}")
    print(f"  χ² = {best_gal_result.chi2:.4f}")
    print(f"  Galaxy offsets: {[f'{d:.1f}' for d in best_gal_result.galaxy_offsets_kpc]} kpc")
    print(f"  Gas offsets: {[f'{d:.1f}' for d in best_gal_result.gas_offsets_kpc]} kpc")
    print(f"  Peak ratio: {best_gal_result.peak_ratio:.3f}")
    print()
    
    print("-" * 70)
    if passing_results:
        print(f"✓ {len(passing_results)} PASSING COMBINATIONS:")
        for r in passing_results[:10]:  # Show first 10
            print(f"  α={r.alpha}, L₀={r.L0_kpc}, w={r.w}, χ²={r.chi2:.3f}")
        if len(passing_results) > 10:
            print(f"  ... and {len(passing_results) - 10} more")
    else:
        print("✗ NO PASSING COMBINATIONS")
        print()
        print("Failure analysis:")
        # Count failures by criterion
        n_fail_peaks = sum(1 for r in results if not r.pass_peak_count)
        n_fail_gas = sum(1 for r in results if r.pass_peak_count and not r.pass_gas_offset)
        n_fail_gal = sum(1 for r in results if r.pass_peak_count and r.pass_gas_offset and not r.pass_galaxy_proximity)
        n_fail_ratio = sum(1 for r in results if r.pass_peak_count and r.pass_gas_offset and r.pass_galaxy_proximity and not r.pass_peak_ratio)
        print(f"  Failed peak_count: {n_fail_peaks}")
        print(f"  Failed gas_offset (after peak_count): {n_fail_gas}")
        print(f"  Failed galaxy_proximity (after above): {n_fail_gal}")
        print(f"  Failed peak_ratio (after above): {n_fail_ratio}")
    
    print()
    print("=" * 70)
    print("PASS/FAIL for best χ² result:")
    print(f"  pass_peak_count: {best_chi2_result.pass_peak_count}")
    print(f"  pass_gas_offset: {best_chi2_result.pass_gas_offset}")
    print(f"  pass_galaxy_proximity: {best_chi2_result.pass_galaxy_proximity}")
    print(f"  pass_peak_ratio: {best_chi2_result.pass_peak_ratio}")
    print(f"  OVERALL: {best_chi2_result.overall_pass}")
    print("=" * 70)
