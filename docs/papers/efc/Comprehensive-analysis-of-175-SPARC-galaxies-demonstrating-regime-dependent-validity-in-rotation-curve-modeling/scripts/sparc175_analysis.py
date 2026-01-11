"""
SPARC175 Full Analysis
Implements EFC-fit (Formula B) on complete SPARC database

Goal: Validate regime structure on N=175 sample
"""

import numpy as np
from scipy.optimize import minimize
import json
from collections import defaultdict

print("="*70)
print("SPARC175 FULL ANALYSIS")
print("="*70)

# ----- STEP 1: Load SPARC data -----
print("\n[STEP 1] Loading SPARC database...")

def load_sparc_data(filepath='/home/claude/sparc-data/sparc_rotation_curves.dat'):
    """Load complete SPARC database"""
    galaxies = defaultdict(lambda: {
        'r': [], 'v_obs': [], 'v_err': [], 
        'v_gas': [], 'v_disk': [], 'v_bulge': []
    })
    
    with open(filepath) as f:
        for line in f:
            parts = line.split()
            if len(parts) < 9:
                continue
            
            name = parts[0]
            try:
                galaxies[name]['r'].append(float(parts[2]))
                galaxies[name]['v_obs'].append(float(parts[3]))
                galaxies[name]['v_err'].append(float(parts[4]))
                galaxies[name]['v_gas'].append(float(parts[5]))
                galaxies[name]['v_disk'].append(float(parts[6]))
                galaxies[name]['v_bulge'].append(float(parts[7]))
            except (ValueError, IndexError):
                continue
    
    # Convert to numpy arrays
    for name in galaxies:
        for key in galaxies[name]:
            galaxies[name][key] = np.array(galaxies[name][key])
    
    return dict(galaxies)

galaxies = load_sparc_data()
print(f"✓ Loaded {len(galaxies)} galaxies")

# Quick stats
n_points = [len(g['r']) for g in galaxies.values()]
print(f"  Total data points: {sum(n_points)}")
print(f"  Points per galaxy: {np.mean(n_points):.1f} ± {np.std(n_points):.1f}")
print(f"  Min: {min(n_points)}, Max: {max(n_points)}")


# ----- STEP 2: Implement EFC-fit (Formula B) -----
print("\n[STEP 2] Implementing EFC-fit formula...")

def S_profile(r, grad_S, S0=0.05, S1=0.95):
    """
    Entropy profile from methods_pipeline.md:
    S(r) = S₀ + (S₁ - S₀) × (1 - exp(-∇S × r))
    """
    return S0 + (S1 - S0) * (1 - np.exp(-grad_S * r))

def v_efc_fit(r, A_Ef, grad_S, r_entropy, alpha):
    """
    EFC-fit formula (Formula B from methods_pipeline.md):
    V²_EFC(r) = A_Ef × (1 - exp(-r/r_entropy)) × (1 - S(r))^α
    
    Parameters:
    - A_Ef: Energy-flow amplitude [(km/s)²] - FREE parameter
    - grad_S: Entropy gradient [kpc⁻¹]
    - r_entropy: Entropy scale radius [kpc]
    - alpha: Power-law index
    """
    S = S_profile(r, grad_S)
    
    radial_term = 1 - np.exp(-r / r_entropy)
    entropy_term = (1 - S)**alpha
    
    v_squared = A_Ef * radial_term * entropy_term
    v_squared = np.maximum(v_squared, 0)  # Ensure non-negative
    
    return np.sqrt(v_squared)

print("✓ EFC-fit formula implemented")

# ----- STEP 3: Fitting function -----
print("\n[STEP 3] Setting up fitting procedure...")

def fit_efc_single_galaxy(r, v_obs, v_err):
    """
    Fit EFC-fit model to single galaxy
    
    Returns: (params, chi2, success)
    """
    
    # Parameter bounds from methods_pipeline.md (Table in section 2.2)
    bounds = [
        (30, 150),      # A_Ef: Energy-flow amplitude (km/s)²
        (0.01, 0.15),   # grad_S: Entropy gradient kpc⁻¹
        (1, 25),        # r_entropy: Scale radius kpc
        (0.3, 3.0)      # alpha: Power-law index
    ]
    
    # Initial guess
    r_max = r.max()
    v_max = v_obs.max()
    
    params_init = [
        v_max**2 * 0.5,  # A_Ef ~ v²
        0.05,            # grad_S
        r_max / 3,       # r_entropy
        1.5              # alpha
    ]
    
    # Chi-squared objective
    def chi2_func(params):
        A_Ef, grad_S, r_entropy, alpha = params
        v_model = v_efc_fit(r, A_Ef, grad_S, r_entropy, alpha)
        return np.sum(((v_obs - v_model) / v_err)**2)
    
    # Optimize
    try:
        result = minimize(
            chi2_func, 
            params_init, 
            bounds=bounds,
            method='L-BFGS-B',
            options={'maxiter': 1000, 'ftol': 1e-6}
        )
        
        return result.x, result.fun, result.success
    
    except Exception as e:
        return None, np.inf, False

print("✓ Fitting procedure ready")

# ----- STEP 4: Fit first 5 galaxies as test -----
print("\n[STEP 4] Testing on first 5 galaxies...")

test_names = list(galaxies.keys())[:5]
test_results = {}

for name in test_names:
    g = galaxies[name]
    r = g['r']
    v_obs = g['v_obs']
    v_err = g['v_err']
    
    n = len(r)
    
    params, chi2, success = fit_efc_single_galaxy(r, v_obs, v_err)
    
    if success:
        chi2_red = chi2 / (n - 4)
        A_Ef, grad_S, r_entropy, alpha = params
        
        print(f"\n{name}:")
        print(f"  N={n}, χ²={chi2:.2f}, χ²/dof={chi2_red:.2f}")
        print(f"  A_Ef={A_Ef:.1f}, ∇S={grad_S:.4f}, r_ent={r_entropy:.1f}, α={alpha:.2f}")
        
        test_results[name] = {
            'n': n,
            'chi2': chi2,
            'chi2_red': chi2_red,
            'params': {
                'A_Ef': A_Ef,
                'grad_S': grad_S,
                'r_entropy': r_entropy,
                'alpha': alpha
            },
            'success': True
        }
    else:
        print(f"\n{name}: FAILED")
        test_results[name] = {'success': False}

print("\n✓ Test complete")
print(f"  Success rate: {sum(1 for r in test_results.values() if r['success'])}/{len(test_results)}")

