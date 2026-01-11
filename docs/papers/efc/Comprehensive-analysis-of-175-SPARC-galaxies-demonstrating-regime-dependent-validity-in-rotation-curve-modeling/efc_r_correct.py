#!/usr/bin/env python3
"""
EFC-R: Correct implementation from mathematical core

Core equation:
v²/r = dΦ_N/dr * (1 + α*S) + α*Φ_N * dS/dr

Where:
- Φ_N: Newtonian potential from baryons
- S(r): Entropy field profile
- α: Single dimensionless coupling
"""

import numpy as np
from scipy.optimize import minimize

# Constants
G = 4.302e-6  # kpc (km/s)^2 / M_sun

def entropy_profile(r, S_c, S_inf, r_S):
    """
    S(r) = S_c + (S_inf - S_c) * [1 - exp(-r/r_S)]
    
    S_c: core entropy (low, ~0.1)
    S_inf: asymptotic entropy (high, ~0.9)
    r_S: entropy scale length
    """
    return S_c + (S_inf - S_c) * (1 - np.exp(-r / r_S))


def dS_dr(r, S_c, S_inf, r_S):
    """Entropy gradient dS/dr"""
    return (S_inf - S_c) / r_S * np.exp(-r / r_S)


def newtonian_potential(r, M_baryon):
    """
    Φ_N = -G * M(<r) / r
    
    For simplicity: M(<r) approximated from V_baryon²
    Since V_baryon² = G * M(<r) / r
    => Φ_N = -V_baryon² 
    """
    # This is the KEY: we use observed baryonic velocity
    # to infer Φ_N without assuming mass profile
    return -M_baryon / r  # Returns G*M/r implicitly


def compute_phi_N(r, V_baryon):
    """
    GAUGE-INVARIANT: Compute relative Newtonian potential
    
    ΔΦ_N(r) = Φ_N(r) - Φ_N(r_max)
    
    This removes arbitrary gauge constant from entering
    the physics in the term α·ΔΦ_N·dS/dr
    
    Key insight: Only potential DIFFERENCES matter physically.
    Setting Φ_N(r_max) as reference makes this explicit.
    
    Returns:
    --------
    Delta_Phi_N : array
        Relative potential [ΔΦ_N(r_max) = 0 by construction]
    """
    # Acceleration field g_N = v_b²/r
    g_N = V_baryon**2 / r
    
    # Integrate relative to r_max: ΔΦ_N(r) = ∫[r to r_max] g_N(r') dr'
    Delta_Phi_N = np.zeros_like(r)
    
    # Trapezoid rule integration from r_max downward
    for i in range(len(r)-2, -1, -1):
        dr = r[i+1] - r[i]
        Delta_Phi_N[i] = Delta_Phi_N[i+1] + 0.5 * (g_N[i] + g_N[i+1]) * dr
    
    # By construction: Delta_Phi_N[-1] = 0
    # Inner radii have Delta_Phi_N > 0 (deeper potential well relative to edge)
    
    return Delta_Phi_N


def velocity_efc_r(r, V_baryon, alpha, S_c, S_inf, r_S):
    """
    GAUGE-INVARIANT EFC-R implementation:
    
    Core equation:
    v²/r = dΦ_N/dr(1+αS) + α·ΔΦ_N·dS/dr
    
    Where ΔΦ_N(r) = Φ_N(r) - Φ_N(r_max) is gauge-invariant
    
    [L3 METHODOLOGY]: Using relative potential removes arbitrary
    gauge constant from physics while preserving all dynamics.
    
    Parameters:
    -----------
    r : array
        Radius [kpc] [L0]
    V_baryon : array  
        Baryonic velocity [km/s] [L0]
    alpha : float
        EFC coupling constant [L1]
    S_c, S_inf, r_S : float
        Entropy profile parameters [L1]
    
    Returns:
    --------
    v : array
        Rotation velocity [km/s] [L1]
    """
    
    # [L1] Entropy field and gradient
    S = entropy_profile(r, S_c, S_inf, r_S)
    dS = dS_dr(r, S_c, S_inf, r_S)
    
    # [L1] GAUGE-INVARIANT: Relative potential
    Delta_Phi_N = compute_phi_N(r, V_baryon)
    
    # [L1] Newtonian acceleration field (gauge-invariant)
    dPhi_N_dr = V_baryon**2 / r
    
    # [L1] EFC-R: dΦ_eff/dr with gauge-invariant formulation
    dPhi_eff_dr = dPhi_N_dr * (1 + alpha * S) + alpha * Delta_Phi_N * dS
    
    # [L1] v²/r = dΦ_eff/dr => v² = r * dΦ_eff/dr
    v_squared = r * dPhi_eff_dr
    v_squared = np.maximum(v_squared, 0)
    
    return np.sqrt(v_squared)


def chi_squared(params, r, V_obs, V_err, V_baryon):
    """Chi-squared for fitting"""
    alpha, S_c, S_inf, r_S = params
    
    V_model = velocity_efc_r(r, V_baryon, alpha, S_c, S_inf, r_S)
    
    return np.sum(((V_obs - V_model) / V_err)**2)


def fit_efc_r(r, V_obs, V_err, V_baryon):
    """
    Fit EFC-R model to rotation curve
    
    Free parameters:
    - alpha: coupling strength
    - S_c: core entropy  
    - S_inf: asymptotic entropy
    - r_S: entropy scale length
    """
    
    # Initial guess
    r_max = r.max()
    params_init = [
        0.5,        # alpha: order unity
        0.1,        # S_c: low core entropy
        0.9,        # S_inf: high outer entropy  
        r_max / 3   # r_S: scale with galaxy size
    ]
    
    # Bounds
    bounds = [
        (0.01, 2.0),     # alpha: positive coupling
        (0.0, 0.3),      # S_c: low order core
        (0.7, 1.0),      # S_inf: high order exterior
        (0.1, r_max)     # r_S: must be within galaxy
    ]
    
    # Minimize
    result = minimize(
        chi_squared,
        params_init,
        args=(r, V_obs, V_err, V_baryon),
        bounds=bounds,
        method='L-BFGS-B',
        options={'maxiter': 1000}
    )
    
    return result.x, result.fun


# Test
if __name__ == "__main__":
    # Test data
    r = np.linspace(1, 20, 20)
    V_baryon = 80 * np.ones(20)
    V_obs = 150 * np.ones(20)  # Needs boost
    V_err = 10 * np.ones(20)
    
    print("Testing EFC-R core implementation")
    print("="*50)
    
    # Fit
    params, chi2 = fit_efc_r(r, V_obs, V_err, V_baryon)
    alpha, S_c, S_inf, r_S = params
    
    print(f"Best fit:")
    print(f"  α = {alpha:.3f}")
    print(f"  S_c = {S_c:.3f}")
    print(f"  S_inf = {S_inf:.3f}")  
    print(f"  r_S = {r_S:.2f} kpc")
    print(f"\nχ² = {chi2:.2f}")
    print(f"χ²/dof = {chi2/16:.2f}")
    
    # Check velocity
    V_model = velocity_efc_r(r, V_baryon, alpha, S_c, S_inf, r_S)
    print(f"\nV_baryon = {V_baryon[0]:.1f} km/s")
    print(f"V_obs = {V_obs[0]:.1f} km/s")
    print(f"V_model = {V_model[0]:.1f} km/s")
