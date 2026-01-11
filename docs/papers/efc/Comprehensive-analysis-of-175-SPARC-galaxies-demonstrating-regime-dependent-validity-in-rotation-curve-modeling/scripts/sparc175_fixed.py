"""
SPARC175 - Fixed optimizer with better initial guesses
"""
import numpy as np
from scipy.optimize import minimize, differential_evolution
import json

# Load data
galaxies = {}
with open('/home/claude/sparc-data/sparc_rotation_curves.dat') as f:
    from collections import defaultdict
    temp = defaultdict(lambda: {'r': [], 'v_obs': [], 'v_err': []})
    
    for line in f:
        parts = line.split()
        if len(parts) < 9:
            continue
        try:
            name = parts[0]
            temp[name]['r'].append(float(parts[2]))
            temp[name]['v_obs'].append(float(parts[3]))
            temp[name]['v_err'].append(float(parts[4]))
        except:
            continue
    
    for name in temp:
        galaxies[name] = {k: np.array(v) for k, v in temp[name].items()}

print(f"Loaded {len(galaxies)} galaxies")

# Formula B
def v_efc(r, A_Ef, grad_S, r_entropy, alpha):
    S = 0.05 + 0.90 * (1 - np.exp(-grad_S * r))
    radial = 1 - np.exp(-r / r_entropy)
    entropy = (1 - S)**alpha
    return np.sqrt(np.maximum(A_Ef * radial * entropy, 0))

# Test on NGC6503 (known to work from N=20)
g = galaxies['NGC6503']
r, v_obs, v_err = g['r'], g['v_obs'], g['v_err']

print(f"\nTesting on NGC6503 (N={len(r)})...")
print(f"v_obs range: {v_obs.min():.1f} - {v_obs.max():.1f} km/s")

# Use differential_evolution (global optimizer)
bounds = [(30, 150), (0.01, 0.15), (1, 25), (0.3, 3.0)]

def chi2(params):
    v_model = v_efc(r, *params)
    return np.sum(((v_obs - v_model) / v_err)**2)

result = differential_evolution(chi2, bounds, maxiter=500, seed=42, workers=1)

A_Ef, grad_S, r_entropy, alpha = result.x
chi2_val = result.fun
chi2_red = chi2_val / (len(r) - 4)

print(f"\nResult:")
print(f"  χ² = {chi2_val:.2f}")
print(f"  χ²/dof = {chi2_red:.2f}")
print(f"  A_Ef = {A_Ef:.1f} (km/s)²")
print(f"  ∇S = {grad_S:.4f} kpc⁻¹")
print(f"  r_entropy = {r_entropy:.1f} kpc")
print(f"  α = {alpha:.3f}")

# Compare to N=20 paper result
print(f"\nN=20 paper reported: χ²_red = 4.34")
print(f"Match? {abs(chi2_red - 4.34) < 1}")

