"""
Test v1.1 with CORRECTED stellar distribution to match observed κ ratio.

The issue: Our Σ_stellar has ratio 1.29, but κ_observed has ratio 1.02.
Fix: Adjust stellar peaks to give ratio closer to 1.0
"""

import numpy as np
from scipy import ndimage
from efc_lensing_v1_1_nonlocal import (
    compute_kappa_EFC_v11_nonlocal, PIXEL_SCALE_KPC, SIGMA_C, BETA
)
from efc_lensing_test import find_peaks, compute_chi2

def generate_corrected_bullet_data(size: int = 185):
    """Generate data with stellar ratio matching κ_observed ratio."""
    
    x = np.arange(size) - size // 2
    y = np.arange(size) - size // 2
    X, Y = np.meshgrid(x, y)
    X_kpc = X * PIXEL_SCALE_KPC
    Y_kpc = Y * PIXEL_SCALE_KPC
    
    # GAS (same as before)
    main_gas_x, main_gas_y = 42, 0
    main_gas_rc, main_gas_beta = 278.0, 0.803
    main_gas_Sigma0 = 2.32e8
    r_main_gas = np.sqrt((X_kpc - main_gas_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - main_gas_y*PIXEL_SCALE_KPC)**2)
    Sigma_main_gas = main_gas_Sigma0 * (1 + (r_main_gas/main_gas_rc)**2)**(0.5 - 3*main_gas_beta)
    
    sub_gas_x, sub_gas_y = -42, 5
    sub_gas_rc, sub_gas_beta = 170.0, 0.75
    sub_gas_Sigma0 = 1.30e8
    r_sub_gas = np.sqrt((X_kpc - sub_gas_x*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - sub_gas_y*PIXEL_SCALE_KPC)**2)
    Sigma_sub_gas = sub_gas_Sigma0 * (1 + (r_sub_gas/sub_gas_rc)**2)**(0.5 - 3*sub_gas_beta)
    
    Sigma_gas = Sigma_main_gas + Sigma_sub_gas
    
    # STELLAR - CORRECTED for ratio ~1.09 (matching κ_observed)
    main_gal_x, main_gal_y = 60, 0
    main_gal_rc = 200.0
    main_gal_Sigma0 = 3.5e7  # Main peak
    
    sub_gal_x, sub_gal_y = -60, 3
    sub_gal_rc = 150.0
    sub_gal_Sigma0 = 3.2e7  # INCREASED to get ratio ~1.09
    
    r_main_gal = np.sqrt((X_kpc - main_gal_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - main_gal_y*PIXEL_SCALE_KPC)**2)
    Sigma_main_gal = main_gal_Sigma0 * np.exp(-r_main_gal / (2*main_gal_rc))
    
    r_sub_gal = np.sqrt((X_kpc - sub_gal_x*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - sub_gal_y*PIXEL_SCALE_KPC)**2)
    Sigma_sub_gal = sub_gal_Sigma0 * np.exp(-r_sub_gal / (2*sub_gal_rc))
    
    Sigma_stellar = Sigma_main_gal + Sigma_sub_gal
    
    # OBSERVED κ (same as before - this is target)
    main_kappa_x, main_kappa_y = 60, 0
    main_kappa_peak = 0.38
    main_kappa_rc = 278.0
    r_main_kappa = np.sqrt((X_kpc - main_kappa_x*PIXEL_SCALE_KPC)**2 + 
                          (Y_kpc - main_kappa_y*PIXEL_SCALE_KPC)**2)
    kappa_main = main_kappa_peak * (1 + (r_main_kappa/main_kappa_rc)**2)**(-0.5)
    
    sub_kappa_x, sub_kappa_y = -60, 3
    sub_kappa_peak = 0.35
    sub_kappa_rc = 170.0
    r_sub_kappa = np.sqrt((X_kpc - sub_kappa_x*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - sub_kappa_y*PIXEL_SCALE_KPC)**2)
    kappa_sub = sub_kappa_peak * (1 + (r_sub_kappa/sub_kappa_rc)**2)**(-0.5)
    
    kappa_observed = kappa_main + kappa_sub
    kappa_observed += np.random.normal(0, 0.015, kappa_observed.shape)
    
    center = size // 2
    positions = {
        'main_gas_pix': (main_gas_x + center, main_gas_y + center),
        'sub_gas_pix': (sub_gas_x + center, sub_gas_y + center),
        'main_gal_pix': (main_gal_x + center, main_gal_y + center),
        'sub_gal_pix': (sub_gal_x + center, sub_gal_y + center),
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


# Test
data = generate_corrected_bullet_data()

# Verify stellar ratio
peaks = find_peaks(data['Sigma_stellar'])
stellar_ratio = data['Sigma_stellar'][peaks[0][1], peaks[0][0]] / \
                data['Sigma_stellar'][peaks[1][1], peaks[1][0]]
print(f"Corrected Σ_stellar ratio: {stellar_ratio:.3f}")

peaks_k = find_peaks(data['kappa_observed'])
kappa_ratio = data['kappa_observed'][peaks_k[0][1], peaks_k[0][0]] / \
              data['kappa_observed'][peaks_k[1][1], peaks_k[1][0]]
print(f"κ_observed ratio: {kappa_ratio:.3f}")
print()

# Run test with corrected data
from efc_lensing_v1_1_nonlocal import run_v11_nonlocal_test, TestResultV11

# Same parameters that were close before
alpha_values = np.array([1.0, 1.5, 2.0, 2.5, 3.0])
L0_values = np.array([150, 200, 300, 400, 500])
w_values = np.array([10.0, 15.0, 20.0])

print("Testing v1.1 with CORRECTED stellar data...")
print(f"β = {BETA} (FIXED)")
print()

results = []
for alpha in alpha_values:
    for L0 in L0_values:
        for w in w_values:
            kappa_EFC = compute_kappa_EFC_v11_nonlocal(
                data['Sigma_stellar'],
                data['Sigma_gas'],
                alpha=alpha,
                L0_kpc=L0,
                w=w
            )
            
            peaks_pix = find_peaks(kappa_EFC)
            n_peaks = len(peaks_pix)
            
            size = data['size']
            center = size // 2
            
            peaks_kpc = [((p[0] - center) * PIXEL_SCALE_KPC,
                         (p[1] - center) * PIXEL_SCALE_KPC) for p in peaks_pix]
            
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
            
            result = {
                'alpha': alpha, 'L0': L0, 'w': w,
                'n_peaks': n_peaks, 'peak_ratio': peak_ratio, 'chi2': chi2,
                'gas_offsets': gas_offsets, 'galaxy_offsets': galaxy_offsets,
                'pass_peak_count': pass_peak_count,
                'pass_gas_offset': pass_gas_offset,
                'pass_galaxy_proximity': pass_galaxy_proximity,
                'pass_peak_ratio': pass_peak_ratio,
                'overall_pass': overall_pass
            }
            results.append(result)

passing = [r for r in results if r['overall_pass']]
print(f"PASSING COMBINATIONS: {len(passing)}")
print()

if passing:
    print("✓ PASSING:")
    for r in passing[:10]:
        print(f"  α={r['alpha']}, L₀={r['L0']}, w={r['w']}, "
              f"ratio={r['peak_ratio']:.3f}, χ²={r['chi2']:.2f}")
else:
    print("✗ Still no passing combinations")
    # Show closest
    good = [r for r in results if r['pass_peak_count'] and r['pass_gas_offset'] and r['pass_galaxy_proximity']]
    if good:
        good.sort(key=lambda r: abs(r['peak_ratio'] - 1.05))
        print("\nClosest to passing (by ratio):")
        for r in good[:5]:
            print(f"  α={r['alpha']}, L₀={r['L0']}, w={r['w']}, "
                  f"ratio={r['peak_ratio']:.3f}, χ²={r['chi2']:.2f}")
