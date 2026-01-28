"""
EFC Lensing Postulate v1.1 - CURVATURE-BASED
=============================================

Alternative formulation using Laplacian (curvature) instead of gradient.

POSTULATE v1.1:
    G_eff = 1 - α × L₀² × ∇²ln(Σ_b)
    
Rationale: Curvature peaks at density maxima, not at edges.
Negative sign because ∇² < 0 at local maxima.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage
from scipy.optimize import minimize
import json
from dataclasses import dataclass
from typing import Tuple, Dict, List
import warnings
warnings.filterwarnings('ignore')

# Import from v1.0
from efc_lensing_test import (
    PIXEL_SCALE_KPC, SIGMA_C, TestResult, 
    generate_bullet_cluster_data, find_peaks, compute_chi2
)

def compute_kappa_EFC_v11(Sigma_b: np.ndarray, alpha: float, L0_kpc: float,
                          pixel_scale: float = PIXEL_SCALE_KPC,
                          smoothing_sigma: float = 1.5) -> np.ndarray:
    """
    Compute EFC convergence using CURVATURE (Laplacian).
    
    POSTULATE v1.1:
        G_eff = 1 - α × L₀² × ∇²ln(Σ_b)
        κ_EFC = (Σ_b × G_eff) / Σ_c
    
    The negative sign ensures G_eff > 1 at density peaks
    (where ∇²ln(Σ) < 0).
    """
    
    Sigma_safe = np.maximum(Sigma_b, 1e-10)
    ln_Sigma = np.log(Sigma_safe)
    
    # Compute Laplacian of ln(Σ_b)
    # Units: 1/pixel² → convert to 1/kpc²
    laplacian = ndimage.laplace(ln_Sigma) / (pixel_scale**2)  # [1/kpc²]
    
    # Compute G_eff (dimensionless)
    # G_eff = 1 - α × L₀² × ∇²ln(Σ_b)
    # Negative sign: at peaks, ∇² < 0, so G_eff > 1
    G_eff = 1.0 - alpha * (L0_kpc**2) * laplacian
    
    # Ensure G_eff stays positive
    G_eff = np.maximum(G_eff, 0.1)
    
    # Effective surface density
    Sigma_eff = Sigma_b * G_eff
    
    # Convergence
    kappa_EFC = Sigma_eff / SIGMA_C
    
    # Apply smoothing
    kappa_EFC = ndimage.gaussian_filter(kappa_EFC, sigma=smoothing_sigma)
    
    return kappa_EFC


def run_v11_test(data: Dict, alpha: float, L0_kpc: float) -> TestResult:
    """Run test with v1.1 curvature-based model."""
    
    size = data['size']
    center = size // 2
    
    kappa_EFC = compute_kappa_EFC_v11(
        data['Sigma_baryon'],
        alpha=alpha,
        L0_kpc=L0_kpc
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
    
    return TestResult(
        alpha=alpha,
        L0_kpc=L0_kpc,
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
    print("=" * 60)
    print("EFC LENSING POSTULATE v1.1 - CURVATURE-BASED TEST")
    print("G_eff = 1 - α × L₀² × ∇²ln(Σ_b)")
    print("=" * 60)
    print()
    
    data = generate_bullet_cluster_data()
    
    # Parameter scan - adjusted for curvature (L₀² makes smaller values relevant)
    alpha_values = np.array([0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0])
    L0_values = np.array([10, 20, 50, 100, 200, 500])
    
    print(f"α range: {alpha_values}")
    print(f"L₀ range: {L0_values} kpc")
    print()
    
    results = []
    for alpha in alpha_values:
        for L0 in L0_values:
            result = run_v11_test(data, alpha, L0)
            results.append(result)
    
    passing_results = [r for r in results if r.overall_pass]
    best_chi2_result = min(results, key=lambda r: r.chi2)
    
    print("RESULTS SUMMARY")
    print("-" * 40)
    print(f"Total tests: {len(results)}")
    print(f"Passing tests: {len(passing_results)}")
    print(f"Best χ²: {best_chi2_result.chi2:.4f}")
    print(f"  α = {best_chi2_result.alpha}")
    print(f"  L₀ = {best_chi2_result.L0_kpc} kpc")
    print()
    
    if passing_results:
        print("✓ PASSING COMBINATIONS:")
        for r in passing_results:
            print(f"  α={r.alpha}, L₀={r.L0_kpc} kpc, χ²={r.chi2:.4f}")
    else:
        print("✗ NO PASSING COMBINATIONS")
    
    print()
    print("Best result details:")
    print(f"  Peaks found: {best_chi2_result.n_peaks_found}")
    print(f"  Peak positions (kpc): {best_chi2_result.peak_positions_kpc}")
    print(f"  Gas offsets (kpc): {best_chi2_result.gas_offsets_kpc}")
    print(f"  Galaxy offsets (kpc): {best_chi2_result.galaxy_offsets_kpc}")
    print(f"  Peak ratio: {best_chi2_result.peak_ratio:.3f}")
    print()
    print(f"  pass_peak_count: {best_chi2_result.pass_peak_count}")
    print(f"  pass_gas_offset: {best_chi2_result.pass_gas_offset}")
    print(f"  pass_galaxy_proximity: {best_chi2_result.pass_galaxy_proximity}")
    print(f"  pass_peak_ratio: {best_chi2_result.pass_peak_ratio}")
    print(f"  OVERALL: {best_chi2_result.overall_pass}")
