"""
EFC Lensing Postulate v1.0 - Bullet Cluster Test
=================================================

Test whether EFC entropy-gradient gravity can reproduce the Bullet Cluster
κ-map without dark matter particles.

POSTULATE (locked):
    S = ln(ρ_b)
    G_eff = 1 + α × L₀ × |∇ln(ρ_b)|
    Σ_eff = Σ_b × G_eff  (2D approximation)
    κ_EFC = Σ_eff / Σ_c

FREE PARAMETERS: α (dimensionless), L₀ (kpc)
BARYONIC: ρ_b = ρ_gas + ρ_stellar

PASS CRITERIA:
    - 2 peaks in κ_EFC
    - Peaks offset > 100 kpc from gas peaks
    - Peaks < 50 kpc from galaxy positions
    - Peak ratio 0.9-1.2
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

# ============================================================
# PHYSICAL CONSTANTS
# ============================================================

PIXEL_SCALE_KPC = 8.5  # kpc per pixel (from Brownstein & Moffat 2007)
SIGMA_C = 3.1e9  # M_sun/kpc² critical surface density at z=0.296

# ============================================================
# DATA STRUCTURES
# ============================================================

@dataclass
class TestResult:
    """Results from EFC lensing test"""
    alpha: float
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
    
    def to_dict(self) -> dict:
        return {
            'parameters': {'alpha': float(self.alpha), 'L0_kpc': float(self.L0_kpc)},
            'peaks': {
                'count': int(self.n_peaks_found),
                'positions_pix': [(int(p[0]), int(p[1])) for p in self.peak_positions_pix],
                'positions_kpc': [(float(p[0]), float(p[1])) for p in self.peak_positions_kpc],
                'gas_offsets_kpc': [float(d) for d in self.gas_offsets_kpc],
                'galaxy_offsets_kpc': [float(d) for d in self.galaxy_offsets_kpc],
                'ratio': float(self.peak_ratio)
            },
            'chi2': float(self.chi2),
            'pass_criteria': {
                'peak_count': bool(self.pass_peak_count),
                'gas_offset': bool(self.pass_gas_offset),
                'galaxy_proximity': bool(self.pass_galaxy_proximity),
                'peak_ratio': bool(self.pass_peak_ratio),
                'OVERALL': bool(self.overall_pass)
            }
        }

# ============================================================
# BULLET CLUSTER DATA (reconstructed from Brownstein & Moffat 2007)
# ============================================================

def generate_bullet_cluster_data(size: int = 185) -> Dict[str, np.ndarray]:
    """
    Generate Bullet Cluster baryonic distributions.
    
    Returns Σ_gas and Σ_stellar maps based on published parameters.
    Units: M_sun/kpc² (surface density)
    """
    
    # Create coordinate grid
    x = np.arange(size) - size // 2
    y = np.arange(size) - size // 2
    X, Y = np.meshgrid(x, y)
    
    # Convert to physical units (kpc)
    X_kpc = X * PIXEL_SCALE_KPC
    Y_kpc = Y * PIXEL_SCALE_KPC
    
    # ===========================================
    # GAS DISTRIBUTION (from X-ray)
    # King β-model profiles
    # ===========================================
    
    # Main cluster gas
    main_gas_x, main_gas_y = 42, 0  # pixels from center (offset west)
    main_gas_rc = 278.0  # kpc core radius
    main_gas_beta = 0.803
    main_gas_Sigma0 = 2.32e8  # M_sun/kpc² peak
    
    r_main_gas = np.sqrt((X_kpc - main_gas_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - main_gas_y*PIXEL_SCALE_KPC)**2)
    Sigma_main_gas = main_gas_Sigma0 * (1 + (r_main_gas/main_gas_rc)**2)**(0.5 - 3*main_gas_beta)
    
    # Subcluster gas (the "bullet")
    sub_gas_x, sub_gas_y = -42, 5  # pixels (offset east)
    sub_gas_rc = 170.0  # kpc
    sub_gas_beta = 0.75
    sub_gas_Sigma0 = 1.30e8  # M_sun/kpc²
    
    r_sub_gas = np.sqrt((X_kpc - sub_gas_x*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - sub_gas_y*PIXEL_SCALE_KPC)**2)
    Sigma_sub_gas = sub_gas_Sigma0 * (1 + (r_sub_gas/sub_gas_rc)**2)**(0.5 - 3*sub_gas_beta)
    
    Sigma_gas = Sigma_main_gas + Sigma_sub_gas
    
    # ===========================================
    # STELLAR/GALAXY DISTRIBUTION
    # Based on optical light, offset from gas
    # ===========================================
    
    # Main cluster galaxies (8σ offset from gas toward west)
    # Offset ~150 kpc = ~18 pixels
    main_gal_x, main_gal_y = 60, 0  # pixels (further west than gas)
    main_gal_rc = 200.0  # kpc (more concentrated than gas)
    main_gal_Sigma0 = 3.5e7  # M_sun/kpc² (lower than gas, but higher M/L)
    
    r_main_gal = np.sqrt((X_kpc - main_gal_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - main_gal_y*PIXEL_SCALE_KPC)**2)
    Sigma_main_gal = main_gal_Sigma0 * np.exp(-r_main_gal / (2*main_gal_rc))
    
    # Subcluster galaxies (ahead of bullet gas)
    sub_gal_x, sub_gal_y = -60, 3  # pixels (further east)
    sub_gal_rc = 150.0  # kpc
    sub_gal_Sigma0 = 2.5e7  # M_sun/kpc²
    
    r_sub_gal = np.sqrt((X_kpc - sub_gal_x*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - sub_gal_y*PIXEL_SCALE_KPC)**2)
    Sigma_sub_gal = sub_gal_Sigma0 * np.exp(-r_sub_gal / (2*sub_gal_rc))
    
    Sigma_stellar = Sigma_main_gal + Sigma_sub_gal
    
    # ===========================================
    # OBSERVED κ-MAP (for comparison)
    # Mass follows galaxies, not gas
    # ===========================================
    
    # Main cluster mass peak (at galaxy position)
    main_kappa_x, main_kappa_y = 60, 0
    main_kappa_peak = 0.38
    main_kappa_rc = 278.0
    
    r_main_kappa = np.sqrt((X_kpc - main_kappa_x*PIXEL_SCALE_KPC)**2 + 
                          (Y_kpc - main_kappa_y*PIXEL_SCALE_KPC)**2)
    kappa_main = main_kappa_peak * (1 + (r_main_kappa/main_kappa_rc)**2)**(-0.5)
    
    # Subcluster mass peak
    sub_kappa_x, sub_kappa_y = -60, 3
    sub_kappa_peak = 0.35
    sub_kappa_rc = 170.0
    
    r_sub_kappa = np.sqrt((X_kpc - sub_kappa_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - sub_kappa_y*PIXEL_SCALE_KPC)**2)
    kappa_sub = sub_kappa_peak * (1 + (r_sub_kappa/sub_kappa_rc)**2)**(-0.5)
    
    kappa_observed = kappa_main + kappa_sub
    
    # Add realistic noise
    noise_level = 0.015
    kappa_observed += np.random.normal(0, noise_level, kappa_observed.shape)
    
    # Store key positions
    positions = {
        'main_gas_pix': (main_gas_x + size//2, main_gas_y + size//2),
        'sub_gas_pix': (sub_gas_x + size//2, sub_gas_y + size//2),
        'main_gal_pix': (main_gal_x + size//2, main_gal_y + size//2),
        'sub_gal_pix': (sub_gal_x + size//2, sub_gal_y + size//2),
        'main_kappa_pix': (main_kappa_x + size//2, main_kappa_y + size//2),
        'sub_kappa_pix': (sub_kappa_x + size//2, sub_kappa_y + size//2),
    }
    
    return {
        'Sigma_gas': Sigma_gas,
        'Sigma_stellar': Sigma_stellar,
        'Sigma_baryon': Sigma_gas + Sigma_stellar,
        'kappa_observed': kappa_observed,
        'positions': positions,
        'size': size,
        'pixel_scale_kpc': PIXEL_SCALE_KPC
    }

# ============================================================
# EFC LENSING MODEL (Postulate v1.0)
# ============================================================

def compute_kappa_EFC(Sigma_b: np.ndarray, alpha: float, L0_kpc: float,
                      pixel_scale: float = PIXEL_SCALE_KPC,
                      smoothing_sigma: float = 1.5) -> np.ndarray:
    """
    Compute EFC convergence map from baryonic surface density.
    
    POSTULATE v1.0:
        G_eff = 1 + α × L₀ × |∇ln(Σ_b)|
        κ_EFC = (Σ_b × G_eff) / Σ_c
    
    Parameters
    ----------
    Sigma_b : array
        Baryonic surface density [M_sun/kpc²]
    alpha : float
        Entropy-gravity coupling (dimensionless)
    L0_kpc : float
        Length scale [kpc]
    pixel_scale : float
        kpc per pixel
    smoothing_sigma : float
        Gaussian smoothing in pixels (match observed map)
    
    Returns
    -------
    kappa_EFC : array
        Predicted convergence map
    """
    
    # Avoid log(0)
    Sigma_safe = np.maximum(Sigma_b, 1e-10)
    
    # Compute ln(Σ_b)
    ln_Sigma = np.log(Sigma_safe)
    
    # Compute gradient of ln(Σ_b)
    # Units: 1/pixel → convert to 1/kpc
    grad_y, grad_x = np.gradient(ln_Sigma)
    grad_ln_Sigma = np.sqrt(grad_x**2 + grad_y**2) / pixel_scale  # [1/kpc]
    
    # Compute G_eff (dimensionless)
    # G_eff = 1 + α × L₀ × |∇ln(Σ_b)|
    G_eff = 1.0 + alpha * L0_kpc * grad_ln_Sigma
    
    # Effective surface density
    Sigma_eff = Sigma_b * G_eff
    
    # Convergence
    kappa_EFC = Sigma_eff / SIGMA_C
    
    # Apply same smoothing as observed map
    kappa_EFC = ndimage.gaussian_filter(kappa_EFC, sigma=smoothing_sigma)
    
    return kappa_EFC

def find_peaks(kappa_map: np.ndarray, min_separation_pix: int = 20,
               threshold_fraction: float = 0.3) -> List[Tuple[int, int]]:
    """
    Find peaks in convergence map.
    
    Returns list of (x, y) pixel coordinates of peaks.
    """
    from scipy.ndimage import maximum_filter, label
    
    # Local maximum filter
    data_max = maximum_filter(kappa_map, size=min_separation_pix)
    
    # Threshold
    threshold = kappa_map.max() * threshold_fraction
    
    # Find peaks
    peaks_mask = (kappa_map == data_max) & (kappa_map > threshold)
    
    # Label connected regions
    labeled, num_features = label(peaks_mask)
    
    # Get peak positions
    peaks = []
    for i in range(1, num_features + 1):
        peak_points = np.where(labeled == i)
        # Centroid of peak region
        y_cen = int(np.mean(peak_points[0]))
        x_cen = int(np.mean(peak_points[1]))
        peaks.append((x_cen, y_cen))
    
    # Sort by peak value (highest first)
    peaks = sorted(peaks, key=lambda p: kappa_map[p[1], p[0]], reverse=True)
    
    return peaks[:2]  # Return at most 2 peaks

def compute_chi2(kappa_EFC: np.ndarray, kappa_obs: np.ndarray,
                 sigma: float = 0.05) -> float:
    """Compute χ² between EFC prediction and observed κ-map."""
    residual = kappa_obs - kappa_EFC
    chi2 = np.sum((residual / sigma)**2) / kappa_obs.size
    return chi2

# ============================================================
# TEST RUNNER
# ============================================================

def run_efc_test(data: Dict, alpha: float, L0_kpc: float) -> TestResult:
    """
    Run EFC lensing test with given parameters.
    
    Returns TestResult with pass/fail on all criteria.
    """
    
    size = data['size']
    center = size // 2
    
    # Compute EFC κ-map
    kappa_EFC = compute_kappa_EFC(
        data['Sigma_baryon'],
        alpha=alpha,
        L0_kpc=L0_kpc
    )
    
    # Find peaks
    peaks_pix = find_peaks(kappa_EFC)
    n_peaks = len(peaks_pix)
    
    # Convert to kpc relative to center
    peaks_kpc = [(
        (p[0] - center) * PIXEL_SCALE_KPC,
        (p[1] - center) * PIXEL_SCALE_KPC
    ) for p in peaks_pix]
    
    # Get reference positions
    pos = data['positions']
    main_gas_kpc = ((pos['main_gas_pix'][0] - center) * PIXEL_SCALE_KPC,
                    (pos['main_gas_pix'][1] - center) * PIXEL_SCALE_KPC)
    sub_gas_kpc = ((pos['sub_gas_pix'][0] - center) * PIXEL_SCALE_KPC,
                   (pos['sub_gas_pix'][1] - center) * PIXEL_SCALE_KPC)
    main_gal_kpc = ((pos['main_gal_pix'][0] - center) * PIXEL_SCALE_KPC,
                    (pos['main_gal_pix'][1] - center) * PIXEL_SCALE_KPC)
    sub_gal_kpc = ((pos['sub_gal_pix'][0] - center) * PIXEL_SCALE_KPC,
                   (pos['sub_gal_pix'][1] - center) * PIXEL_SCALE_KPC)
    
    # Compute offsets
    gas_offsets = []
    galaxy_offsets = []
    
    if n_peaks >= 2:
        # Peak 1 (main)
        d_main_gas = np.sqrt((peaks_kpc[0][0] - main_gas_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gas_kpc[1])**2)
        d_main_gal = np.sqrt((peaks_kpc[0][0] - main_gal_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gal_kpc[1])**2)
        
        # Peak 2 (sub)
        d_sub_gas = np.sqrt((peaks_kpc[1][0] - sub_gas_kpc[0])**2 + 
                            (peaks_kpc[1][1] - sub_gas_kpc[1])**2)
        d_sub_gal = np.sqrt((peaks_kpc[1][0] - sub_gal_kpc[0])**2 + 
                            (peaks_kpc[1][1] - sub_gal_kpc[1])**2)
        
        gas_offsets = [d_main_gas, d_sub_gas]
        galaxy_offsets = [d_main_gal, d_sub_gal]
    elif n_peaks == 1:
        # Check distance to both
        d_main_gas = np.sqrt((peaks_kpc[0][0] - main_gas_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gas_kpc[1])**2)
        d_main_gal = np.sqrt((peaks_kpc[0][0] - main_gal_kpc[0])**2 + 
                             (peaks_kpc[0][1] - main_gal_kpc[1])**2)
        gas_offsets = [d_main_gas]
        galaxy_offsets = [d_main_gal]
    
    # Peak ratio
    if n_peaks >= 2:
        peak_ratio = kappa_EFC[peaks_pix[0][1], peaks_pix[0][0]] / \
                     kappa_EFC[peaks_pix[1][1], peaks_pix[1][0]]
    else:
        peak_ratio = 0.0
    
    # χ²
    chi2 = compute_chi2(kappa_EFC, data['kappa_observed'])
    
    # Pass/fail criteria
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

# ============================================================
# PARAMETER SCAN
# ============================================================

def scan_parameters(data: Dict, 
                   alpha_range: np.ndarray,
                   L0_range: np.ndarray) -> List[TestResult]:
    """Scan parameter space and return all results."""
    
    results = []
    for alpha in alpha_range:
        for L0 in L0_range:
            result = run_efc_test(data, alpha, L0)
            results.append(result)
    
    return results

# ============================================================
# VISUALIZATION
# ============================================================

def plot_test_results(data: Dict, result: TestResult, save_path: str = None):
    """Create comprehensive visualization of test results."""
    
    # Recompute κ_EFC for plotting
    kappa_EFC = compute_kappa_EFC(
        data['Sigma_baryon'],
        alpha=result.alpha,
        L0_kpc=result.L0_kpc
    )
    
    fig = plt.figure(figsize=(20, 16))
    
    size = data['size']
    extent_kpc = [-size//2 * PIXEL_SCALE_KPC, size//2 * PIXEL_SCALE_KPC,
                  -size//2 * PIXEL_SCALE_KPC, size//2 * PIXEL_SCALE_KPC]
    
    # Row 1: Input data
    ax1 = fig.add_subplot(3, 3, 1)
    im1 = ax1.imshow(data['Sigma_gas'], cmap='Reds', origin='lower', extent=extent_kpc)
    ax1.set_title('Σ_gas (X-ray ICM)', fontsize=12, fontweight='bold')
    ax1.set_xlabel('x [kpc]')
    ax1.set_ylabel('y [kpc]')
    plt.colorbar(im1, ax=ax1, label='M☉/kpc²')
    
    ax2 = fig.add_subplot(3, 3, 2)
    im2 = ax2.imshow(data['Sigma_stellar'], cmap='Blues', origin='lower', extent=extent_kpc)
    ax2.set_title('Σ_stellar (Galaxies)', fontsize=12, fontweight='bold')
    ax2.set_xlabel('x [kpc]')
    plt.colorbar(im2, ax=ax2, label='M☉/kpc²')
    
    ax3 = fig.add_subplot(3, 3, 3)
    im3 = ax3.imshow(data['Sigma_baryon'], cmap='Purples', origin='lower', extent=extent_kpc)
    ax3.set_title('Σ_baryon = Σ_gas + Σ_stellar', fontsize=12, fontweight='bold')
    ax3.set_xlabel('x [kpc]')
    plt.colorbar(im3, ax=ax3, label='M☉/kpc²')
    
    # Row 2: κ-maps comparison
    ax4 = fig.add_subplot(3, 3, 4)
    im4 = ax4.imshow(data['kappa_observed'], cmap='hot', origin='lower', extent=extent_kpc,
                     vmin=0, vmax=0.5)
    ax4.set_title('κ_observed (Lensing)', fontsize=12, fontweight='bold')
    ax4.set_xlabel('x [kpc]')
    ax4.set_ylabel('y [kpc]')
    # Mark observed peaks
    pos = data['positions']
    center = size // 2
    ax4.scatter((pos['main_kappa_pix'][0]-center)*PIXEL_SCALE_KPC, 
                (pos['main_kappa_pix'][1]-center)*PIXEL_SCALE_KPC, 
                c='cyan', s=100, marker='x', linewidths=2, label='Observed peaks')
    ax4.scatter((pos['sub_kappa_pix'][0]-center)*PIXEL_SCALE_KPC, 
                (pos['sub_kappa_pix'][1]-center)*PIXEL_SCALE_KPC, 
                c='cyan', s=100, marker='x', linewidths=2)
    ax4.legend(loc='upper right')
    plt.colorbar(im4, ax=ax4, label='κ')
    
    ax5 = fig.add_subplot(3, 3, 5)
    im5 = ax5.imshow(kappa_EFC, cmap='hot', origin='lower', extent=extent_kpc,
                     vmin=0, vmax=0.5)
    ax5.set_title(f'κ_EFC (α={result.alpha:.2f}, L₀={result.L0_kpc:.0f} kpc)', 
                  fontsize=12, fontweight='bold')
    ax5.set_xlabel('x [kpc]')
    # Mark EFC peaks
    for i, p in enumerate(result.peak_positions_kpc):
        ax5.scatter(p[0], p[1], c='lime', s=100, marker='+', linewidths=2,
                   label='EFC peaks' if i==0 else '')
    ax5.legend(loc='upper right')
    plt.colorbar(im5, ax=ax5, label='κ')
    
    ax6 = fig.add_subplot(3, 3, 6)
    residual = data['kappa_observed'] - kappa_EFC
    im6 = ax6.imshow(residual, cmap='seismic', origin='lower', extent=extent_kpc,
                     vmin=-0.2, vmax=0.2)
    ax6.set_title(f'Residual (obs - EFC), χ²={result.chi2:.3f}', fontsize=12, fontweight='bold')
    ax6.set_xlabel('x [kpc]')
    plt.colorbar(im6, ax=ax6, label='Δκ')
    
    # Row 3: Pass/fail summary and profiles
    ax7 = fig.add_subplot(3, 3, 7)
    ax7.axis('off')
    
    # Create pass/fail table
    criteria_text = f"""
    EFC LENSING TEST RESULTS
    ========================
    
    Parameters:
      α = {result.alpha:.3f} (dimensionless)
      L₀ = {result.L0_kpc:.1f} kpc
    
    Peak Detection:
      Peaks found: {result.n_peaks_found}  {'✓ PASS' if result.pass_peak_count else '✗ FAIL'} (need 2)
    
    Peak Positions (kpc):"""
    
    for i, (p_kpc, d_gas, d_gal) in enumerate(zip(
            result.peak_positions_kpc, 
            result.gas_offsets_kpc,
            result.galaxy_offsets_kpc)):
        criteria_text += f"""
      Peak {i+1}: ({p_kpc[0]:.0f}, {p_kpc[1]:.0f})
        → Gas offset: {d_gas:.0f} kpc  {'✓' if d_gas > 100 else '✗'} (need >100)
        → Galaxy offset: {d_gal:.0f} kpc  {'✓' if d_gal < 50 else '✗'} (need <50)"""
    
    criteria_text += f"""
    
    Peak Ratio: {result.peak_ratio:.2f}  {'✓ PASS' if result.pass_peak_ratio else '✗ FAIL'} (need 0.9-1.2)
    
    χ² = {result.chi2:.4f}
    
    ================================
    OVERALL: {'✓✓✓ PASS ✓✓✓' if result.overall_pass else '✗✗✗ FAIL ✗✗✗'}
    ================================
    """
    
    ax7.text(0.1, 0.95, criteria_text, transform=ax7.transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat' if result.overall_pass else 'lightcoral',
                      alpha=0.5))
    
    # 1D profile comparison
    ax8 = fig.add_subplot(3, 3, 8)
    center_y = size // 2
    x_kpc = (np.arange(size) - center_y) * PIXEL_SCALE_KPC
    
    ax8.plot(x_kpc, data['kappa_observed'][center_y, :], 'k-', lw=2, label='κ_observed')
    ax8.plot(x_kpc, kappa_EFC[center_y, :], 'r--', lw=2, label='κ_EFC')
    ax8.axhline(0, color='gray', linestyle=':')
    ax8.set_xlabel('x [kpc]')
    ax8.set_ylabel('κ')
    ax8.set_title('Central slice (y=0)', fontsize=12, fontweight='bold')
    ax8.legend()
    ax8.grid(True, alpha=0.3)
    
    # G_eff visualization
    ax9 = fig.add_subplot(3, 3, 9)
    
    # Compute G_eff
    Sigma_safe = np.maximum(data['Sigma_baryon'], 1e-10)
    ln_Sigma = np.log(Sigma_safe)
    grad_y, grad_x = np.gradient(ln_Sigma)
    grad_ln_Sigma = np.sqrt(grad_x**2 + grad_y**2) / PIXEL_SCALE_KPC
    G_eff = 1.0 + result.alpha * result.L0_kpc * grad_ln_Sigma
    
    im9 = ax9.imshow(G_eff, cmap='viridis', origin='lower', extent=extent_kpc)
    ax9.set_title('G_eff = 1 + α×L₀×|∇ln(Σ_b)|', fontsize=12, fontweight='bold')
    ax9.set_xlabel('x [kpc]')
    ax9.set_ylabel('y [kpc]')
    plt.colorbar(im9, ax=ax9, label='G_eff')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"Saved: {save_path}")
    
    return fig

# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("EFC LENSING POSTULATE v1.0 - BULLET CLUSTER TEST")
    print("=" * 60)
    print()
    
    # Generate data
    print("1. Generating Bullet Cluster baryonic data...")
    data = generate_bullet_cluster_data()
    print(f"   Map size: {data['size']}×{data['size']} pixels")
    print(f"   Pixel scale: {PIXEL_SCALE_KPC} kpc/pixel")
    print(f"   Field: {data['size']*PIXEL_SCALE_KPC:.0f}×{data['size']*PIXEL_SCALE_KPC:.0f} kpc")
    print()
    
    # Parameter scan
    print("2. Scanning parameter space...")
    alpha_values = np.array([0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0])
    L0_values = np.array([10, 50, 100, 200, 500, 1000])
    
    print(f"   α range: {alpha_values}")
    print(f"   L₀ range: {L0_values} kpc")
    print()
    
    results = scan_parameters(data, alpha_values, L0_values)
    
    # Find best result
    passing_results = [r for r in results if r.overall_pass]
    best_chi2_result = min(results, key=lambda r: r.chi2)
    
    print("3. Results Summary")
    print("-" * 40)
    print(f"   Total tests: {len(results)}")
    print(f"   Passing tests: {len(passing_results)}")
    print(f"   Best χ²: {best_chi2_result.chi2:.4f} (α={best_chi2_result.alpha}, L₀={best_chi2_result.L0_kpc})")
    print()
    
    if passing_results:
        print("   ✓ PASSING PARAMETER COMBINATIONS:")
        for r in passing_results:
            print(f"     α={r.alpha:.1f}, L₀={r.L0_kpc:.0f} kpc, χ²={r.chi2:.4f}")
    else:
        print("   ✗ NO PARAMETER COMBINATION PASSES ALL CRITERIA")
    print()
    
    # Detailed best result
    print("4. Best χ² Result Details:")
    print(json.dumps(best_chi2_result.to_dict(), indent=2))
    print()
    
    # Save results
    print("5. Generating visualization...")
    fig = plot_test_results(data, best_chi2_result, 'efc_bullet_cluster_test.png')
    
    # Save JSON results
    all_results = {
        'test_name': 'EFC Lensing Postulate v1.0 - Bullet Cluster',
        'date': '2026-01-28',
        'postulate': {
            'entropy_field': 'S = ln(ρ_b)',
            'G_eff': 'G_eff = 1 + α × L₀ × |∇ln(Σ_b)|',
            'convergence': 'κ_EFC = Σ_eff / Σ_c',
            'baryonic_def': 'ρ_b = ρ_gas + ρ_stellar'
        },
        'pass_criteria': {
            'peak_count': 2,
            'gas_offset_min_kpc': 100,
            'galaxy_proximity_max_kpc': 50,
            'peak_ratio_range': [0.9, 1.2]
        },
        'parameter_scan': {
            'alpha_values': [float(x) for x in alpha_values],
            'L0_values': [float(x) for x in L0_values]
        },
        'summary': {
            'total_tests': len(results),
            'passing_tests': len(passing_results),
            'best_chi2': best_chi2_result.chi2,
            'best_params': {'alpha': best_chi2_result.alpha, 'L0_kpc': best_chi2_result.L0_kpc}
        },
        'best_result': best_chi2_result.to_dict(),
        'all_passing': [r.to_dict() for r in passing_results]
    }
    
    with open('efc_bullet_cluster_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    print("   Saved: efc_bullet_cluster_results.json")
    
    print()
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
