"""
PREDICTION TEST: MACS J0025 and Abell 520
==========================================

Using LOCKED parameters from Bullet Cluster:
  - η = 66.2 (global, NO recalibration)
  - c = 0.8 (L₀ = c × R_core)
  - σ_v = 500 km/s (conservative fixed value for all)

Goal: Predict w from non-lensing observables, then check if κ geometry works.
"""

import numpy as np

# =============================================================================
# LOCKED GLOBAL PARAMETERS (from Bullet calibration)
# =============================================================================

ETA = 66.2          # Global mixing parameter (LOCKED)
C_CORE = 0.8        # L₀/R_core ratio (LOCKED)
SIGMA_V = 500       # km/s - fixed for all clusters (conservative)

print("=" * 70)
print("EFC PREDICTION TEST: MACS J0025 & ABELL 520")
print("=" * 70)
print()
print("LOCKED GLOBAL PARAMETERS (from Bullet Cluster):")
print(f"  η = {ETA} (mixing timescale factor)")
print(f"  c = {C_CORE} (L₀ = c × R_core)")
print(f"  σ_v = {SIGMA_V} km/s (turbulent velocity, fixed)")
print()

# =============================================================================
# PHYSICAL MODEL
# =============================================================================

def compression_ratio(M, gamma=5/3):
    """Rankine-Hugoniot compression ratio."""
    return (gamma + 1) * M**2 / ((gamma - 1) * M**2 + 2)

def predict_w(M, t_Myr, R_core_kpc):
    """
    Predict w using saturating model with LOCKED parameters.
    
    w = r(M) × (1 + t/τ_mix)
    τ_mix = η × L₀ / σ_v
    L₀ = c × R_core
    """
    r = compression_ratio(M)
    L0 = C_CORE * R_core_kpc
    tau_mix = ETA * L0 / SIGMA_V
    w = r * (1 + t_Myr / tau_mix)
    return w, L0, tau_mix, r

# =============================================================================
# CLUSTER DATA (from literature)
# =============================================================================

print("=" * 70)
print("CLUSTER PARAMETERS (from literature)")
print("=" * 70)
print()

clusters = {
    'Bullet': {
        'M': 3.0,           # Markevitch+ 2006
        't_Myr': 150,       # Estimated from separation/velocity
        'R_core_kpc': 250,  # X-ray core radius
        'source': 'Markevitch+ 2006, Clowe+ 2006'
    },
    'MACS_J0025': {
        'M': 2.0,           # Bradač+ 2008 - weaker shock
        't_Myr': 150,       # Similar geometry to Bullet
        'R_core_kpc': 150,  # Smaller cluster
        'source': 'Bradač+ 2008'
    },
    'Abell_520': {
        'M': 2.5,           # Multiple shocks, estimate
        't_Myr': 200,       # Older, more relaxed
        'R_core_kpc': 200,  # X-ray core
        'source': 'Mahdavi+ 2007, Jee+ 2012'
    }
}

for name, params in clusters.items():
    print(f"{name}:")
    print(f"  M = {params['M']} (Mach number)")
    print(f"  t = {params['t_Myr']} Myr (time since collision)")
    print(f"  R_core = {params['R_core_kpc']} kpc")
    print(f"  Source: {params['source']}")
    print()

# =============================================================================
# PREDICTIONS
# =============================================================================

print("=" * 70)
print("PREDICTIONS (η = {}, c = {}, σ_v = {} km/s LOCKED)".format(ETA, C_CORE, SIGMA_V))
print("=" * 70)
print()

print(f"{'Cluster':<15} {'M':<5} {'t':<6} {'R_core':<8} {'L₀':<8} {'τ_mix':<8} {'r(M)':<6} {'w_pred':<8}")
print("-" * 75)

results = {}
for name, params in clusters.items():
    w, L0, tau, r = predict_w(params['M'], params['t_Myr'], params['R_core_kpc'])
    results[name] = {'w': w, 'L0': L0, 'tau': tau, 'r': r}
    
    flag = " ← calibration" if name == 'Bullet' else ""
    print(f"{name:<15} {params['M']:<5} {params['t_Myr']:<6} {params['R_core_kpc']:<8} {L0:<8.0f} {tau:<8.0f} {r:<6.2f} {w:<8.1f}{flag}")

print()

# =============================================================================
# COMPARISON TABLE
# =============================================================================

print("=" * 70)
print("SUMMARY: PREDICTED PARAMETERS FOR EFC v1.1 TEST")
print("=" * 70)
print()

print("To test EFC on these clusters, use:")
print()
print(f"{'Cluster':<15} {'w':<10} {'L₀ (kpc)':<12} {'α':<10} {'β':<10}")
print("-" * 55)

# α and β are the other v1.1 parameters
# From Bullet fit: α ≈ 1.5, β = 0.3 (fixed)
ALPHA = 1.5  # Could also be predicted, but keep simple for now
BETA = 0.3   # Fixed

for name in clusters:
    w = results[name]['w']
    L0 = results[name]['L0']
    print(f"{name:<15} {w:<10.1f} {L0:<12.0f} {ALPHA:<10} {BETA:<10}")

print()
print("These are PREDICTIONS, not fits.")
print("Test: Does EFC with these parameters produce correct κ geometry?")
print()

# =============================================================================
# WHAT SUCCESS LOOKS LIKE
# =============================================================================

print("=" * 70)
print("SUCCESS CRITERIA")
print("=" * 70)
print()
print("For each cluster, EFC v1.1 with predicted (w, L₀) should produce:")
print("  1. Two κ peaks (for merging systems)")
print("  2. Peaks offset from gas centroids")
print("  3. Peaks near stellar/galaxy centroids")
print("  4. Peak ratio consistent with observations")
print()
print("If this works WITHOUT adjusting w or L₀ per-cluster,")
print("then EFC has predictive power, not just curve-fitting ability.")
print()

# =============================================================================
# UNCERTAINTIES
# =============================================================================

print("=" * 70)
print("UNCERTAINTY ANALYSIS")
print("=" * 70)
print()

# Vary t by ±50 Myr and see impact
print("Impact of ±50 Myr uncertainty in merger age:")
print()

for name, params in clusters.items():
    if name == 'Bullet':
        continue
    
    t_low = params['t_Myr'] - 50
    t_mid = params['t_Myr']
    t_high = params['t_Myr'] + 50
    
    w_low, _, _, _ = predict_w(params['M'], t_low, params['R_core_kpc'])
    w_mid, _, _, _ = predict_w(params['M'], t_mid, params['R_core_kpc'])
    w_high, _, _, _ = predict_w(params['M'], t_high, params['R_core_kpc'])
    
    delta_pct = (w_high - w_low) / w_mid * 100 / 2
    
    print(f"{name}:")
    print(f"  t = {t_low} Myr → w = {w_low:.1f}")
    print(f"  t = {t_mid} Myr → w = {w_mid:.1f}")  
    print(f"  t = {t_high} Myr → w = {w_high:.1f}")
    print(f"  Uncertainty: ±{delta_pct:.0f}%")
    print()

print("With saturating model, uncertainties are manageable (~20-30%).")
