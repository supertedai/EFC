"""
EFC Lensing Postulate v1.3 - COMPONENT SEPARATION
==================================================

Hypothesis: Collisionless component (stellar/galaxies) carries 
entropy-gravity coupling differently than collisional gas.

POSTULATE v1.3:
    Σ_eff = Σ_stellar × G_eff_stellar + Σ_gas × G_eff_gas
    
    G_eff_stellar = 1 + α_s × L₀ × |∇ln(Σ_stellar)|
    G_eff_gas = 1 + α_g × L₀ × |∇ln(Σ_gas)|
    
With constraint: α_s >> α_g (collisionless dominates)

This is the "EFC explanation" for Bullet Cluster:
- Galaxies passed through (collisionless) → retain entropy structure
- Gas collided (collisional) → lost/redistributed entropy
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

from efc_lensing_test import (
    PIXEL_SCALE_KPC, SIGMA_C, TestResult,
    generate_bullet_cluster_data, find_peaks, compute_chi2
)


@dataclass
class TestResultV13:
    """Results with component separation parameters."""
    alpha_stellar: float
    alpha_gas: float
    L0_kpc: float
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


def compute_kappa_EFC_v13(Sigma_stellar: np.ndarray, 
                          Sigma_gas: np.ndarray,
                          alpha_stellar: float, 
                          alpha_gas: float,
                          L0_kpc: float,
                          pixel_scale: float = PIXEL_SCALE_KPC,
                          smoothing_sigma: float = 1.5) -> np.ndarray:
    """
    Compute EFC convergence with COMPONENT SEPARATION.
    
    POSTULATE v1.3:
        G_eff_s = 1 + α_s × L₀ × |∇ln(Σ_stellar)|
        G_eff_g = 1 + α_g × L₀ × |∇ln(Σ_gas)|
        Σ_eff = Σ_stellar × G_eff_s + Σ_gas × G_eff_g
        κ_EFC = Σ_eff / Σ_c
    """
    
    # Stellar component
    Sigma_s_safe = np.maximum(Sigma_stellar, 1e-10)
    ln_Sigma_s = np.log(Sigma_s_safe)
    grad_y_s, grad_x_s = np.gradient(ln_Sigma_s)
    grad_ln_Sigma_s = np.sqrt(grad_x_s**2 + grad_y_s**2) / pixel_scale
    G_eff_stellar = 1.0 + alpha_stellar * L0_kpc * grad_ln_Sigma_s
    
    # Gas component
    Sigma_g_safe = np.maximum(Sigma_gas, 1e-10)
    ln_Sigma_g = np.log(Sigma_g_safe)
    grad_y_g, grad_x_g = np.gradient(ln_Sigma_g)
    grad_ln_Sigma_g = np.sqrt(grad_x_g**2 + grad_y_g**2) / pixel_scale
    G_eff_gas = 1.0 + alpha_gas * L0_kpc * grad_ln_Sigma_g
    
    # Combined effective surface density
    Sigma_eff = Sigma_stellar * G_eff_stellar + Sigma_gas * G_eff_gas
    
    # Convergence
    kappa_EFC = Sigma_eff / SIGMA_C
    
    # Apply smoothing
    kappa_EFC = ndimage.gaussian_filter(kappa_EFC, sigma=smoothing_sigma)
    
    return kappa_EFC


def run_v13_test(data: Dict, alpha_s: float, alpha_g: float, L0_kpc: float) -> TestResultV13:
    """Run test with v1.3 component separation model."""
    
    size = data['size']
    center = size // 2
    
    kappa_EFC = compute_kappa_EFC_v13(
        data['Sigma_stellar'],
        data['Sigma_gas'],
        alpha_stellar=alpha_s,
        alpha_gas=alpha_g,
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
    
    return TestResultV13(
        alpha_stellar=alpha_s,
        alpha_gas=alpha_g,
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
    print("EFC LENSING POSTULATE v1.3 - COMPONENT SEPARATION TEST")
    print("G_eff_stellar = 1 + α_s × L₀ × |∇ln(Σ_stellar)|")
    print("G_eff_gas = 1 + α_g × L₀ × |∇ln(Σ_gas)|")
    print("With constraint: α_s >> α_g")
    print("=" * 60)
    print()
    
    data = generate_bullet_cluster_data()
    
    # Parameter scan
    # Key hypothesis: α_stellar >> α_gas
    alpha_stellar_values = np.array([1.0, 5.0, 10.0, 20.0, 50.0, 100.0])
    alpha_gas_values = np.array([0.0, 0.01, 0.1, 0.5])  # Much smaller
    L0_values = np.array([50, 100, 200, 500])
    
    print(f"α_stellar range: {alpha_stellar_values}")
    print(f"α_gas range: {alpha_gas_values}")
    print(f"L₀ range: {L0_values} kpc")
    print()
    
    results = []
    for alpha_s in alpha_stellar_values:
        for alpha_g in alpha_gas_values:
            for L0 in L0_values:
                # Only test if stellar dominates
                if alpha_s >= alpha_g * 10:
                    result = run_v13_test(data, alpha_s, alpha_g, L0)
                    results.append(result)
    
    passing_results = [r for r in results if r.overall_pass]
    best_chi2_result = min(results, key=lambda r: r.chi2)
    
    # Also find best galaxy proximity
    best_gal_result = min(results, key=lambda r: min(r.galaxy_offsets_kpc) if r.galaxy_offsets_kpc else 9999)
    
    print("RESULTS SUMMARY")
    print("-" * 40)
    print(f"Total tests: {len(results)}")
    print(f"Passing tests: {len(passing_results)}")
    print()
    
    print(f"Best χ²: {best_chi2_result.chi2:.4f}")
    print(f"  α_stellar = {best_chi2_result.alpha_stellar}")
    print(f"  α_gas = {best_chi2_result.alpha_gas}")
    print(f"  L₀ = {best_chi2_result.L0_kpc} kpc")
    print(f"  Galaxy offsets: {best_chi2_result.galaxy_offsets_kpc}")
    print()
    
    print(f"Best galaxy proximity:")
    print(f"  α_stellar = {best_gal_result.alpha_stellar}")
    print(f"  α_gas = {best_gal_result.alpha_gas}")
    print(f"  L₀ = {best_gal_result.L0_kpc} kpc")
    print(f"  Galaxy offsets: {[f'{d:.1f}' for d in best_gal_result.galaxy_offsets_kpc]} kpc")
    print(f"  Gas offsets: {[f'{d:.1f}' for d in best_gal_result.gas_offsets_kpc]} kpc")
    print(f"  Peak ratio: {best_gal_result.peak_ratio:.3f}")
    print(f"  χ²: {best_gal_result.chi2:.4f}")
    print()
    
    if passing_results:
        print("✓ PASSING COMBINATIONS:")
        for r in passing_results:
            print(f"  α_s={r.alpha_stellar}, α_g={r.alpha_gas}, L₀={r.L0_kpc} kpc")
    else:
        print("✗ NO PASSING COMBINATIONS")
    
    print()
    print("-" * 40)
    print("PASS/FAIL breakdown for best galaxy proximity:")
    print(f"  pass_peak_count: {best_gal_result.pass_peak_count}")
    print(f"  pass_gas_offset: {best_gal_result.pass_gas_offset}")
    print(f"  pass_galaxy_proximity: {best_gal_result.pass_galaxy_proximity}")
    print(f"  pass_peak_ratio: {best_gal_result.pass_peak_ratio}")
    print(f"  OVERALL: {best_gal_result.overall_pass}")
