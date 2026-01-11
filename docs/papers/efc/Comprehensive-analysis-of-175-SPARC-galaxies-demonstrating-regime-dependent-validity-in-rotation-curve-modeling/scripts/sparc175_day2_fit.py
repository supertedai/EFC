"""
SPARC175 HYBRID ANALYSIS - Day 2
Fit all 175 galaxies with residual diagnostics

Using: Simple turnon formula (ultra-phenomenological)
v(r) = v_flat × sqrt(1 - exp(-(r/r_turnon)^sharpness))
"""

import numpy as np
import json
from scipy.optimize import differential_evolution
from scipy.stats import spearmanr
from tqdm import tqdm

print("="*80)
print("SPARC175 HYBRID ANALYSIS - DAY 2: FITTING + DIAGNOSTICS")
print("="*80)

# Load clean data
with open('/home/claude/sparc175_clean.json') as f:
    galaxies = json.load(f)

# Convert to numpy
for name in galaxies:
    for k in galaxies[name]:
        galaxies[name][k] = np.array(galaxies[name][k])

print(f"\nLoaded {len(galaxies)} galaxies")

# ============================================================================
# MODEL DEFINITIONS
# ============================================================================

def efc_simple(r, v_flat, r_turnon, sharpness):
    """
    EFC-fit ultra-phenomenological:
    v(r) = v_flat × sqrt(1 - exp(-(r/r_turnon)^sharpness))
    
    3 free parameters:
    - v_flat: asymptotic velocity [km/s]
    - r_turnon: turnon scale [kpc]
    - sharpness: profile shape
    """
    return v_flat * np.sqrt(np.maximum(1 - np.exp(-(r/r_turnon)**sharpness), 0))

def lcdm_nfw(r, v_200, r_s):
    """
    ΛCDM NFW profile (simplified)
    v²(r) = V_200² × [ln(1+r/r_s) - (r/r_s)/(1+r/r_s)] / [ln(1+c) - c/(1+c)]
    
    2 free parameters:
    - v_200: virial velocity [km/s]  
    - r_s: scale radius [kpc]
    """
    x = r / r_s
    # Concentration c ~ 10 (typical)
    c = 10
    f_c = np.log(1 + c) - c / (1 + c)
    f_x = np.log(1 + x) - x / (1 + x)
    
    v_squared = (v_200**2) * f_x / f_c
    return np.sqrt(np.maximum(v_squared, 0))

print("\n✓ Models defined:")
print("  EFC-fit: Simple turnon (3 params)")
print("  ΛCDM: NFW profile (2 params)")

# ============================================================================
# FITTING FUNCTIONS
# ============================================================================

def fit_single_galaxy(r, v_obs, v_err, model='efc'):
    """Fit single galaxy with residual diagnostics"""
    
    if model == 'efc':
        bounds = [(50, 200), (0.1, 30), (0.5, 5.0)]
        n_params = 3
        model_func = efc_simple
    else:  # lcdm
        bounds = [(50, 200), (0.1, 50)]
        n_params = 2
        model_func = lcdm_nfw
    
    def chi2_func(params):
        v_model = model_func(r, *params)
        return np.sum(((v_obs - v_model) / v_err)**2)
    
    try:
        result = differential_evolution(
            chi2_func, 
            bounds, 
            seed=42, 
            maxiter=300,
            workers=1,
            atol=1e-6,
            tol=1e-4
        )
        
        params = result.x
        chi2 = result.fun
        chi2_red = chi2 / (len(r) - n_params)
        
        # Model prediction
        v_model = model_func(r, *params)
        
        # Residuals
        residuals = v_obs - v_model
        
        # Residual diagnostics
        rho_resid, p_resid = spearmanr(r, residuals)
        
        # Sign changes (oscillation indicator)
        sign_changes = np.sum(np.diff(np.sign(residuals)) != 0)
        
        # RMS residual
        rms_resid = np.sqrt(np.mean(residuals**2))
        
        # AIC/BIC
        n = len(r)
        k = n_params
        aic = chi2 + 2*k
        bic = chi2 + k*np.log(n)
        
        return {
            'success': True,
            'params': params.tolist(),
            'chi2': float(chi2),
            'chi2_red': float(chi2_red),
            'aic': float(aic),
            'bic': float(bic),
            'residuals': {
                'rms': float(rms_resid),
                'radial_trend': float(rho_resid),
                'radial_trend_p': float(p_resid),
                'sign_changes': int(sign_changes),
                'sign_changes_rate': float(sign_changes / len(r))
            }
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

print("\n✓ Fitting functions ready")

# ============================================================================
# FIT ALL GALAXIES
# ============================================================================

print(f"\n[FITTING] Processing {len(galaxies)} galaxies...")
print("(This may take a few minutes)\n")

results = {}

for name in tqdm(sorted(galaxies.keys())):
    g = galaxies[name]
    r = g['r']
    v_obs = g['v_obs']
    v_err = g['v_err']
    
    # Fit both models
    efc_result = fit_single_galaxy(r, v_obs, v_err, model='efc')
    lcdm_result = fit_single_galaxy(r, v_obs, v_err, model='lcdm')
    
    # Compute ΔAIC
    if efc_result['success'] and lcdm_result['success']:
        delta_aic = efc_result['aic'] - lcdm_result['aic']
        delta_bic = efc_result['bic'] - lcdm_result['bic']
        
        # Winner
        if delta_aic < -10:
            winner = 'EFC'
        elif delta_aic > 10:
            winner = 'LCDM'
        else:
            winner = 'TIE'
    else:
        delta_aic = np.nan
        delta_bic = np.nan
        winner = 'FAILED'
    
    results[name] = {
        'n_points': len(r),
        'efc': efc_result,
        'lcdm': lcdm_result,
        'comparison': {
            'delta_aic': float(delta_aic),
            'delta_bic': float(delta_bic),
            'winner': winner
        }
    }

print("\n✓ Fitting complete!")

# ============================================================================
# SUMMARY STATISTICS
# ============================================================================

print("\n[SUMMARY] Global results:")
print("-"*80)

n_success = sum(1 for r in results.values() if r['efc']['success'] and r['lcdm']['success'])
n_failed = len(results) - n_success

print(f"Successful fits: {n_success}/{len(results)}")
print(f"Failed fits: {n_failed}")

if n_success > 0:
    winners = [r['comparison']['winner'] for r in results.values() if r['efc']['success']]
    from collections import Counter
    winner_counts = Counter(winners)
    
    print(f"\nModel preference:")
    print(f"  EFC wins: {winner_counts['EFC']}")
    print(f"  ΛCDM wins: {winner_counts['LCDM']}")
    print(f"  Ties: {winner_counts['TIE']}")
    print(f"  Failed: {winner_counts.get('FAILED', 0)}")
    
    # Chi-squared statistics
    chi2_efc = [r['efc']['chi2_red'] for r in results.values() if r['efc']['success']]
    chi2_lcdm = [r['lcdm']['chi2_red'] for r in results.values() if r['lcdm']['success']]
    
    print(f"\nχ²/dof statistics:")
    print(f"  EFC:  {np.mean(chi2_efc):.2f} ± {np.std(chi2_efc):.2f}")
    print(f"  ΛCDM: {np.mean(chi2_lcdm):.2f} ± {np.std(chi2_lcdm):.2f}")

# ============================================================================
# SAVE RESULTS
# ============================================================================

print("\n[SAVE] Writing results...")

output = {
    'metadata': {
        'n_galaxies': len(results),
        'n_success': n_success,
        'n_failed': n_failed,
        'model': 'EFC-fit ultra-phenomenological (simple turnon)'
    },
    'results': results
}

with open('/home/claude/sparc175_fits.json', 'w') as f:
    json.dump(output, f, indent=2)

print("✓ Results saved: sparc175_fits.json")

print("\n" + "="*80)
print("DAY 2 COMPLETE: All galaxies fitted with residual diagnostics")
print("="*80)
print("\nNext: Day 3 - Classification into regimes")

