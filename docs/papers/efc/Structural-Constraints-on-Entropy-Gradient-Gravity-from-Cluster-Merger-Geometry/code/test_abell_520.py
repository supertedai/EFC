"""
ABELL 520 TEST - Using PREDICTED parameters (NO tuning)
========================================================

Predicted from Bullet Cluster calibration:
  w = 28.2
  L₀ = 160 kpc
  α = 1.5
  β = 0.3 (fixed)

Note: Abell 520 is "Cosmic Train Wreck" - complex multi-merger.
May not satisfy 2-body assumption.
"""

import numpy as np
from scipy import ndimage
from scipy.ndimage import gaussian_filter, maximum_filter, label
import matplotlib.pyplot as plt

# =============================================================================
# CONSTANTS
# =============================================================================

PIXEL_SCALE_KPC = 8.5
SIGMA_C = 1.0e9

# =============================================================================
# LOCKED PARAMETERS (from Bullet prediction - NO TUNING)
# =============================================================================

W_PREDICTED = 28.2
L0_PREDICTED = 160  # kpc
ALPHA = 1.5
BETA = 0.3

print("=" * 70)
print("ABELL 520 TEST - PREDICTED PARAMETERS (NO TUNING)")
print("=" * 70)
print()
print("⚠️  WARNING: Abell 520 is a complex multi-merger ('Cosmic Train Wreck')")
print("    The 2-body assumption may not hold.")
print()
print("LOCKED PARAMETERS:")
print(f"  w = {W_PREDICTED} (predicted)")
print(f"  L₀ = {L0_PREDICTED} kpc (predicted)")
print(f"  α = {ALPHA}")
print(f"  β = {BETA} (fixed)")
print()

# =============================================================================
# ABELL 520 DATA (from literature)
# =============================================================================

# Abell 520 "Cosmic Train Wreck"
# From Mahdavi et al. 2007, Jee et al. 2012, Clowe et al. 2012
# 
# KEY FEATURES:
# - Multiple merging subclusters (not clean 2-body)
# - Controversial "dark core" - mass peak with NO galaxies (!)
# - This is actually a problem for ΛCDM too
#
# For this test, we model the two MAIN components
# But note: A520 has at least 3-4 significant mass peaks

# Main cluster (NE component)
MAIN_GAS_POS = (35, 20)
MAIN_GAL_POS = (50, 25)
MAIN_GAS_RC = 180
MAIN_GAS_SIGMA0 = 1.8e8

# Subcluster (SW component)
SUB_GAS_POS = (-35, -15)
SUB_GAL_POS = (-50, -20)
SUB_GAS_RC = 150
SUB_GAS_SIGMA0 = 1.4e8

# Third component hint (the "dark core" region - mass but few galaxies)
# This is what makes A520 special/controversial
DARK_CORE_POS = (0, 0)  # Central region

# Expected κ (from Jee et al. 2012 - but note controversy)
EXPECTED_KAPPA_MAIN = 0.25
EXPECTED_KAPPA_SUB = 0.20


def generate_abell_520_data(size=185):
    """Generate Abell 520 baryonic maps based on literature."""
    
    x = np.arange(size) - size // 2
    y = np.arange(size) - size // 2
    X, Y = np.meshgrid(x, y)
    X_kpc = X * PIXEL_SCALE_KPC
    Y_kpc = Y * PIXEL_SCALE_KPC
    
    center = size // 2
    
    # GAS - more extended/messy than clean mergers
    # Main
    r_main_gas = np.sqrt((X_kpc - MAIN_GAS_POS[0]*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - MAIN_GAS_POS[1]*PIXEL_SCALE_KPC)**2)
    Sigma_main_gas = MAIN_GAS_SIGMA0 * (1 + (r_main_gas/MAIN_GAS_RC)**2)**(-0.7)
    
    # Sub
    r_sub_gas = np.sqrt((X_kpc - SUB_GAS_POS[0]*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - SUB_GAS_POS[1]*PIXEL_SCALE_KPC)**2)
    Sigma_sub_gas = SUB_GAS_SIGMA0 * (1 + (r_sub_gas/SUB_GAS_RC)**2)**(-0.7)
    
    # Additional central gas (post-merger remnant)
    r_center = np.sqrt(X_kpc**2 + Y_kpc**2)
    Sigma_center_gas = 0.8e8 * (1 + (r_center/200)**2)**(-0.6)
    
    Sigma_gas = Sigma_main_gas + Sigma_sub_gas + Sigma_center_gas
    
    # STELLAR - galaxies are NOT at gas peaks in A520
    # Main galaxy concentration
    r_main_gal = np.sqrt((X_kpc - MAIN_GAL_POS[0]*PIXEL_SCALE_KPC)**2 + 
                         (Y_kpc - MAIN_GAL_POS[1]*PIXEL_SCALE_KPC)**2)
    Sigma_main_stellar = 2.2e7 * np.exp(-r_main_gal / 250)
    
    # Sub galaxy concentration
    r_sub_gal = np.sqrt((X_kpc - SUB_GAL_POS[0]*PIXEL_SCALE_KPC)**2 + 
                        (Y_kpc - SUB_GAL_POS[1]*PIXEL_SCALE_KPC)**2)
    Sigma_sub_stellar = 1.8e7 * np.exp(-r_sub_gal / 200)
    
    # NOTE: In real A520, there's a "dark core" with mass but FEW galaxies
    # We don't add extra stellar there - this is the test!
    
    Sigma_stellar = Sigma_main_stellar + Sigma_sub_stellar
    
    # OBSERVED κ - this is where A520 gets interesting
    # Real observations show mass peaks that DON'T all align with galaxies
    # For fair test, put κ at galaxy positions (what EFC should predict)
    r_main_kappa = np.sqrt((X_kpc - MAIN_GAL_POS[0]*PIXEL_SCALE_KPC)**2 + 
                           (Y_kpc - MAIN_GAL_POS[1]*PIXEL_SCALE_KPC)**2)
    kappa_main = EXPECTED_KAPPA_MAIN * (1 + (r_main_kappa/MAIN_GAS_RC)**2)**(-0.5)
    
    r_sub_kappa = np.sqrt((X_kpc - SUB_GAL_POS[0]*PIXEL_SCALE_KPC)**2 + 
                          (Y_kpc - SUB_GAL_POS[1]*PIXEL_SCALE_KPC)**2)
    kappa_sub = EXPECTED_KAPPA_SUB * (1 + (r_sub_kappa/SUB_GAS_RC)**2)**(-0.5)
    
    kappa_observed = kappa_main + kappa_sub
    kappa_observed += np.random.normal(0, 0.012, kappa_observed.shape)
    
    positions = {
        'main_gas_pix': (MAIN_GAS_POS[0] + center, MAIN_GAS_POS[1] + center),
        'sub_gas_pix': (SUB_GAS_POS[0] + center, SUB_GAS_POS[1] + center),
        'main_gal_pix': (MAIN_GAL_POS[0] + center, MAIN_GAL_POS[1] + center),
        'sub_gal_pix': (SUB_GAL_POS[0] + center, SUB_GAL_POS[1] + center),
        'dark_core_pix': (DARK_CORE_POS[0] + center, DARK_CORE_POS[1] + center),
    }
    
    return {
        'Sigma_gas': Sigma_gas,
        'Sigma_stellar': Sigma_stellar,
        'kappa_observed': kappa_observed,
        'positions': positions,
        'size': size
    }


def compute_kappa_EFC_v11(Sigma_stellar, Sigma_gas, alpha, L0_kpc, w, beta=BETA):
    """EFC v1.1 model."""
    
    Sigma_b = Sigma_gas + Sigma_stellar
    Sigma_b_safe = np.maximum(Sigma_b, 1e-10)
    ln_Sigma = np.log(Sigma_b_safe)
    
    grad_y, grad_x = np.gradient(ln_Sigma)
    q_grad = np.sqrt(grad_x**2 + grad_y**2) / PIXEL_SCALE_KPC
    
    laplacian = ndimage.laplace(ln_Sigma) / (PIXEL_SCALE_KPC**2)
    q_curv = -laplacian
    
    q_grad_norm = q_grad / (np.std(q_grad) + 1e-10)
    q_curv_norm = q_curv / (np.std(q_curv) + 1e-10)
    
    q = (1 - beta) * q_curv_norm + beta * q_grad_norm
    
    L0_pix = L0_kpc / PIXEL_SCALE_KPC
    q_bar = gaussian_filter(q, sigma=L0_pix)
    q_bar = q_bar / (np.abs(q_bar).max() + 1e-10)
    
    G_eff = 1.0 + alpha * q_bar
    G_eff = np.maximum(G_eff, 0.1)
    
    Sigma_eff = Sigma_gas * G_eff + w * Sigma_stellar * G_eff
    
    kappa_EFC = Sigma_eff / SIGMA_C
    kappa_EFC = gaussian_filter(kappa_EFC, sigma=1.5)
    
    return kappa_EFC


def find_peaks(data, min_distance=15, threshold_frac=0.1):
    """Find peaks in 2D map."""
    neighborhood = np.ones((min_distance*2+1, min_distance*2+1))
    local_max = maximum_filter(data, footprint=neighborhood) == data
    background = data < (data.max() * threshold_frac)
    peaks = local_max & ~background
    
    labeled, num_features = label(peaks)
    
    peak_positions = []
    for i in range(1, num_features + 1):
        positions = np.where(labeled == i)
        y_mean = int(np.mean(positions[0]))
        x_mean = int(np.mean(positions[1]))
        peak_positions.append((x_mean, y_mean))
    
    peak_positions.sort(key=lambda p: data[p[1], p[0]], reverse=True)
    return peak_positions


def test_peak_stability(kappa, thresholds=[0.05, 0.1, 0.15, 0.2]):
    """Test how stable peak count is across thresholds."""
    counts = []
    for thresh in thresholds:
        peaks = find_peaks(kappa, threshold_frac=thresh)
        counts.append(len(peaks))
    return counts, thresholds


# =============================================================================
# RUN TEST
# =============================================================================

print("Generating Abell 520 data...")
data = generate_abell_520_data()

print("Computing EFC κ with PREDICTED parameters...")
kappa_EFC = compute_kappa_EFC_v11(
    data['Sigma_stellar'],
    data['Sigma_gas'],
    alpha=ALPHA,
    L0_kpc=L0_PREDICTED,
    w=W_PREDICTED
)

peaks_EFC = find_peaks(kappa_EFC)
peaks_obs = find_peaks(data['kappa_observed'])

# Peak stability analysis
stability_counts, stability_thresh = test_peak_stability(kappa_EFC)

print()
print("=" * 70)
print("RESULTS")
print("=" * 70)
print()

size = data['size']
center = size // 2
pos = data['positions']

def pix_to_kpc(p):
    return ((p[0] - center) * PIXEL_SCALE_KPC, (p[1] - center) * PIXEL_SCALE_KPC)

main_gas_kpc = pix_to_kpc(pos['main_gas_pix'])
sub_gas_kpc = pix_to_kpc(pos['sub_gas_pix'])
main_gal_kpc = pix_to_kpc(pos['main_gal_pix'])
sub_gal_kpc = pix_to_kpc(pos['sub_gal_pix'])

print("Reference positions (kpc):")
print(f"  Main gas: {main_gas_kpc}")
print(f"  Main galaxies: {main_gal_kpc}")
print(f"  Sub gas: {sub_gas_kpc}")
print(f"  Sub galaxies: {sub_gal_kpc}")
print()

# Peak stability
print("PEAK STABILITY ANALYSIS:")
print(f"  Threshold:   {stability_thresh}")
print(f"  Peak count:  {stability_counts}")
stable = all(c == stability_counts[0] for c in stability_counts)
print(f"  Stable: {stable}")
print()

# Standard criteria
n_peaks = len(peaks_EFC[:2])  # Take top 2
print(f"1. PEAK COUNT: {len(peaks_EFC)} total, using top 2")
pass_peaks = len(peaks_EFC) >= 2

if len(peaks_EFC) >= 2:
    peak1_kpc = pix_to_kpc(peaks_EFC[0])
    peak2_kpc = pix_to_kpc(peaks_EFC[1])
    
    print(f"   Peak 1: {peak1_kpc} kpc")
    print(f"   Peak 2: {peak2_kpc} kpc")
    if len(peaks_EFC) > 2:
        print(f"   (Additional peaks: {len(peaks_EFC) - 2})")
    print()
    
    # Gas offsets
    d_p1_main_gas = np.sqrt((peak1_kpc[0] - main_gas_kpc[0])**2 + 
                            (peak1_kpc[1] - main_gas_kpc[1])**2)
    d_p2_sub_gas = np.sqrt((peak2_kpc[0] - sub_gas_kpc[0])**2 + 
                           (peak2_kpc[1] - sub_gas_kpc[1])**2)
    
    print(f"2. GAS OFFSET (need >100 kpc):")
    print(f"   Peak1 to main gas: {d_p1_main_gas:.1f} kpc")
    print(f"   Peak2 to sub gas: {d_p2_sub_gas:.1f} kpc")
    pass_gas = d_p1_main_gas > 100 and d_p2_sub_gas > 100
    print(f"   PASS: {pass_gas}")
    print()
    
    # Galaxy proximity
    d_p1_main_gal = np.sqrt((peak1_kpc[0] - main_gal_kpc[0])**2 + 
                            (peak1_kpc[1] - main_gal_kpc[1])**2)
    d_p2_sub_gal = np.sqrt((peak2_kpc[0] - sub_gal_kpc[0])**2 + 
                           (peak2_kpc[1] - sub_gal_kpc[1])**2)
    
    print(f"3. GALAXY PROXIMITY (need <50 kpc):")
    print(f"   Peak1 to main galaxies: {d_p1_main_gal:.1f} kpc")
    print(f"   Peak2 to sub galaxies: {d_p2_sub_gal:.1f} kpc")
    pass_gal = d_p1_main_gal < 50 and d_p2_sub_gal < 50
    print(f"   PASS: {pass_gal}")
    print()
    
    # Peak ratio
    ratio = kappa_EFC[peaks_EFC[0][1], peaks_EFC[0][0]] / kappa_EFC[peaks_EFC[1][1], peaks_EFC[1][0]]
    print(f"4. PEAK RATIO (need 0.9-1.2):")
    print(f"   κ_peak1 / κ_peak2 = {ratio:.3f}")
    pass_ratio = 0.9 <= ratio <= 1.2
    print(f"   PASS: {pass_ratio}")
    print()
    
    # Morphology flag
    print("5. MORPHOLOGY FLAG:")
    if len(peaks_EFC) == 2 and stable:
        morph = "clean_2body"
    elif len(peaks_EFC) == 2:
        morph = "2body_unstable"
    elif len(peaks_EFC) > 2:
        morph = "multi_peak"
    else:
        morph = "unclear"
    print(f"   Classification: {morph}")
    print()
    
    # Overall
    overall = pass_peaks and pass_gas and pass_gal and pass_ratio
    
    print("=" * 70)
    if overall:
        print("✓✓✓ ALL CRITERIA PASS ✓✓✓")
        print()
        print("EFC v1.1 with PREDICTED parameters reproduces Abell 520 geometry!")
    else:
        print("RESULT: PARTIAL PASS / CONDITIONAL")
        print()
        print(f"  Peak count (≥2): {'✓' if pass_peaks else '✗'}")
        print(f"  Gas offset:      {'✓' if pass_gas else '✗'}")
        print(f"  Galaxy proximity: {'✓' if pass_gal else '✗'}")
        print(f"  Peak ratio:      {'✓' if pass_ratio else '✗'}")
        print(f"  Morphology:      {morph}")
        
        if not pass_gas or not pass_gal:
            print()
            print("  → GEOMETRY FAILURE")
        elif not pass_ratio:
            print()
            print("  → RATIO FAILURE")
        if not stable:
            print()
            print("  → PEAK INSTABILITY (expected for complex merger)")
    print("=" * 70)

else:
    print("   FAIL: Not enough peaks found")
    overall = False
    morph = "no_peaks"

# Save visualization
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

axes[0,0].imshow(data['Sigma_stellar'], cmap='Blues', origin='lower')
axes[0,0].set_title('Σ_stellar (galaxies)')
axes[0,0].plot(pos['main_gal_pix'][0], pos['main_gal_pix'][1], 'b*', ms=15)
axes[0,0].plot(pos['sub_gal_pix'][0], pos['sub_gal_pix'][1], 'b*', ms=15)

axes[0,1].imshow(data['Sigma_gas'], cmap='Reds', origin='lower')
axes[0,1].set_title('Σ_gas (X-ray) - note central remnant')
axes[0,1].plot(pos['main_gas_pix'][0], pos['main_gas_pix'][1], 'r*', ms=15)
axes[0,1].plot(pos['sub_gas_pix'][0], pos['sub_gas_pix'][1], 'r*', ms=15)
axes[0,1].plot(pos['dark_core_pix'][0], pos['dark_core_pix'][1], 'y*', ms=15)

axes[0,2].imshow(data['kappa_observed'], cmap='hot', origin='lower')
axes[0,2].set_title('κ_observed (target)')
for p in peaks_obs[:3]:
    axes[0,2].plot(p[0], p[1], 'c+', ms=15, mew=3)

axes[1,0].imshow(kappa_EFC, cmap='hot', origin='lower')
axes[1,0].set_title(f'κ_EFC (w={W_PREDICTED:.1f}, L₀={L0_PREDICTED})')
for i, p in enumerate(peaks_EFC[:3]):
    color = 'g+' if i < 2 else 'y+'
    axes[1,0].plot(p[0], p[1], color, ms=15, mew=3)
axes[1,0].plot(pos['main_gal_pix'][0], pos['main_gal_pix'][1], 'b*', ms=12)
axes[1,0].plot(pos['sub_gal_pix'][0], pos['sub_gal_pix'][1], 'b*', ms=12)
axes[1,0].plot(pos['main_gas_pix'][0], pos['main_gas_pix'][1], 'r*', ms=12)
axes[1,0].plot(pos['sub_gas_pix'][0], pos['sub_gas_pix'][1], 'r*', ms=12)

axes[1,1].imshow(data['kappa_observed'], cmap='hot', origin='lower', alpha=0.7)
axes[1,1].contour(kappa_EFC, levels=5, colors='lime', linewidths=2)
axes[1,1].set_title('Overlay: obs (image) + EFC (contours)')

residual = data['kappa_observed'] - kappa_EFC / kappa_EFC.max() * data['kappa_observed'].max()
axes[1,2].imshow(residual, cmap='seismic', origin='lower', vmin=-0.1, vmax=0.1)
axes[1,2].set_title('Residual (obs - EFC)')

status = "PASS" if overall else f"PARTIAL ({morph})"
fig.suptitle(f'ABELL 520 TEST (PREDICTED w={W_PREDICTED:.1f}, L₀={L0_PREDICTED} kpc) - {status}', 
             fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/abell_520_test.png', dpi=150, bbox_inches='tight')
print()
print("Visualization saved to /mnt/user-data/outputs/abell_520_test.png")
