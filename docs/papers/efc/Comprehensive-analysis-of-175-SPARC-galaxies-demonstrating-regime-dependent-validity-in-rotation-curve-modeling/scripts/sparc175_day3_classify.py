"""
SPARC175 HYBRID ANALYSIS - Day 3
Classification into regimes + Latent proxy computation
"""

import numpy as np
import json
from collections import Counter

print("="*80)
print("SPARC175 HYBRID ANALYSIS - DAY 3: REGIME CLASSIFICATION")
print("="*80)

# Load results
with open('/home/claude/sparc175_fits.json') as f:
    data = json.load(f)

results = data['results']

print(f"\nLoaded results for {len(results)} galaxies")

# ============================================================================
# COMPUTE LATENT PROXY L
# ============================================================================

print("\n[PHASE 1] Computing latent proxy L...")
print("-"*80)

latent_proxies = {}

for name, r in results.items():
    if not r['efc']['success']:
        latent_proxies[name] = {
            'L': 1.0,  # Max latent for failures
            'components': {}
        }
        continue
    
    # Component 1: Residual trend (radial correlation)
    rho = abs(r['efc']['residuals']['radial_trend'])
    
    # Component 2: Sign change rate (oscillation)
    sign_rate = r['efc']['residuals']['sign_changes_rate']
    
    # Component 3: Relative chi-squared (how bad is fit)
    chi2_rel = min(r['efc']['chi2_red'] / 10.0, 1.0)  # Normalize to [0,1]
    
    # Simple weighted average
    L = 0.4 * rho + 0.3 * sign_rate + 0.3 * chi2_rel
    
    latent_proxies[name] = {
        'L': float(L),
        'components': {
            'residual_trend': float(rho),
            'oscillation': float(sign_rate),
            'chi2_normalized': float(chi2_rel)
        }
    }

# Add to results
for name in results:
    results[name]['latent'] = latent_proxies[name]

print(f"✓ Latent proxy computed for all galaxies")
print(f"  L range: {min(lp['L'] for lp in latent_proxies.values()):.3f} - {max(lp['L'] for lp in latent_proxies.values()):.3f}")

# ============================================================================
# CLASSIFY INTO 4 REGIMES
# ============================================================================

print("\n[PHASE 2] Classifying into regimes...")
print("-"*80)

def classify_galaxy(name, r):
    """
    Classify into 4 classes (from Svar 1):
    1. Flow-dominert (EFC-domene)
    2. Transition
    3. Latent/struktur-dominert
    4. Data/modell-problem
    """
    
    if not r['efc']['success'] or not r['lcdm']['success']:
        return 'DATA_PROBLEM'
    
    delta_aic = r['comparison']['delta_aic']
    L = r['latent']['L']
    chi2_efc = r['efc']['chi2_red']
    
    # Rule 1: Flow-dominated (EFC domain)
    if delta_aic <= -10 and chi2_efc < 20:
        return 'FLOW'
    
    # Rule 2: Latent-dominated (structure)
    if delta_aic >= 10 or chi2_efc > 50:
        return 'LATENT'
    
    # Rule 3: Data problem
    if chi2_efc > 100:
        return 'DATA_PROBLEM'
    
    # Rule 4: Transition (everything else)
    return 'TRANSITION'

# Classify all
for name, r in results.items():
    r['regime'] = classify_galaxy(name, r)

# Count
regime_counts = Counter(r['regime'] for r in results.values())

print(f"✓ Classification complete:")
for regime, count in regime_counts.most_common():
    print(f"  {regime:20s}: {count:3d} ({100*count/len(results):.1f}%)")

# ============================================================================
# REGIME STATISTICS
# ============================================================================

print("\n[PHASE 3] Regime statistics...")
print("-"*80)

for regime in ['FLOW', 'TRANSITION', 'LATENT', 'DATA_PROBLEM']:
    regime_galaxies = {n: r for n, r in results.items() if r['regime'] == regime}
    
    if not regime_galaxies:
        continue
    
    print(f"\n{regime} regime (N={len(regime_galaxies)}):")
    
    # EFC success rate
    efc_wins = sum(1 for r in regime_galaxies.values() if r['comparison']['winner'] == 'EFC')
    lcdm_wins = sum(1 for r in regime_galaxies.values() if r['comparison']['winner'] == 'LCDM')
    
    print(f"  EFC wins: {efc_wins}/{len(regime_galaxies)} ({100*efc_wins/len(regime_galaxies):.1f}%)")
    
    # Latent proxy
    L_values = [r['latent']['L'] for r in regime_galaxies.values() if 'latent' in r]
    if L_values:
        print(f"  L: {np.mean(L_values):.3f} ± {np.std(L_values):.3f}")
    
    # Chi-squared
    chi2_values = [r['efc']['chi2_red'] for r in regime_galaxies.values() if r['efc']['success']]
    if chi2_values:
        print(f"  χ²/dof: {np.mean(chi2_values):.2f} ± {np.std(chi2_values):.2f}")

# ============================================================================
# REGIME CORRELATION TEST
# ============================================================================

print("\n[PHASE 4] Testing regime structure...")
print("-"*80)

from scipy.stats import spearmanr, mannwhitneyu

# Correlation: ΔAIC vs L
valid_results = [(r['comparison']['delta_aic'], r['latent']['L']) 
                 for r in results.values() 
                 if r['efc']['success'] and np.isfinite(r['comparison']['delta_aic'])]

if valid_results:
    delta_aic_values = [x[0] for x in valid_results]
    L_values = [x[1] for x in valid_results]
    
    rho, p_value = spearmanr(delta_aic_values, L_values)
    
    print(f"ΔAIC vs L correlation:")
    print(f"  Spearman ρ = {rho:.3f}")
    print(f"  p-value = {p_value:.4f}")
    
    if p_value < 0.001:
        print(f"  ✓ HIGHLY SIGNIFICANT (p < 0.001)")
    elif p_value < 0.01:
        print(f"  ✓ Significant (p < 0.01)")
    else:
        print(f"  ⚠ Not significant")

# Test: FLOW vs LATENT separation
flow_L = [r['latent']['L'] for r in results.values() if r['regime'] == 'FLOW']
latent_L = [r['latent']['L'] for r in results.values() if r['regime'] == 'LATENT']

if flow_L and latent_L:
    u_stat, p_value = mannwhitneyu(flow_L, latent_L, alternative='less')
    
    print(f"\nRegime separation test (Mann-Whitney U):")
    print(f"  FLOW L: {np.mean(flow_L):.3f} ± {np.std(flow_L):.3f}")
    print(f"  LATENT L: {np.mean(latent_L):.3f} ± {np.std(latent_L):.3f}")
    print(f"  p-value = {p_value:.4f}")
    
    if p_value < 0.001:
        print(f"  ✓ FLOW and LATENT significantly separated (p < 0.001)")

# ============================================================================
# SAVE CLASSIFIED RESULTS
# ============================================================================

print("\n[SAVE] Writing classified results...")

output = {
    'metadata': {
        'n_galaxies': len(results),
        'regime_counts': dict(regime_counts),
        'model': 'EFC-fit ultra-phenomenological'
    },
    'results': results
}

with open('/home/claude/sparc175_classified.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✓ Results saved: sparc175_classified.json")

print("\n" + "="*80)
print("DAY 3 COMPLETE: Regime classification")
print("="*80)
print("\nNext: Day 4 - Visualization")

