#!/usr/bin/env python3
"""
Landau Equation Solver for EFC Regime Transitions
==================================================

Solves the Landau equation for order parameter φ(z) to compute
gating function G(z) for regime transitions.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
Date: 2026-01-20
License: MIT
"""

import numpy as np
from scipy.integrate import solve_ivp
import json

# Planck 2018 cosmology
H0 = 67.36  # km/s/Mpc
omega_b = 0.0494
omega_c = 0.2646
omega_lambda = 0.685
omega_r = 9e-5

def H(z):
    """Hubble parameter H(z) in units where H0=1"""
    return np.sqrt(omega_r*(1+z)**4 + (omega_b+omega_c)*(1+z)**3 + omega_lambda)

def chi(z, chi_early=0.2, chi_late=2.5, z_t=50, dz=30):
    """Control parameter χ(z)"""
    chi_mid = (chi_early + chi_late) / 2
    chi_amp = (chi_late - chi_early) / 2
    return chi_mid - chi_amp * np.tanh((z - z_t) / dz)

def landau_coefficient(chi_val, chi_c=1.0, alpha=10.0):
    """Landau coefficient a(χ) = α(χ_c - χ)"""
    return alpha * (chi_c - chi_val)

def dphi_dz(z, phi, params):
    """
    Differential equation for φ(z):
    dφ/dz = [a(χ)φ + bφ³] / [(1+z)H(z)τ]
    """
    alpha, chi_c, b, tau, chi_early, chi_late, z_t, dz = params
    
    chi_val = chi(z, chi_early, chi_late, z_t, dz)
    a = landau_coefficient(chi_val, chi_c, alpha)
    Hz = H(z)
    
    return (a * phi + b * phi**3) / ((1 + z) * Hz * tau)

def gating_function(phi, phi0=1.0):
    """Gating function G(φ) = φ²/(φ² + φ₀²)"""
    return phi**2 / (phi**2 + phi0**2)

def solve_landau_equation(z_min=0, z_max=3000, n_points=15000,
                         alpha=10.0, chi_c=1.0, b=1.0, tau=0.1,
                         chi_early=0.2, chi_late=2.5, z_t=50, dz=30,
                         phi_init=1e-6):
    """
    Solve Landau equation from z_max to z_min
    
    Returns:
        z: array of redshifts
        phi: array of φ(z) values
        G: array of G(φ) values
    """
    params = (alpha, chi_c, b, tau, chi_early, chi_late, z_t, dz)
    
    # Integration
    z_eval = np.linspace(z_max, z_min, n_points)
    
    print(f"Solving Landau equation...")
    print(f"  z range: {z_max} → {z_min}")
    print(f"  Points: {n_points}")
    print(f"  Parameters: α={alpha}, χ_c={chi_c}, b={b}, τ={tau}")
    
    sol = solve_ivp(
        lambda z, y: dphi_dz(z, y[0], params),
        [z_max, z_min],
        [phi_init],
        t_eval=z_eval,
        method='RK45',
        rtol=1e-10,
        atol=1e-12
    )
    
    z = sol.t
    phi = sol.y[0]
    G = gating_function(phi)
    
    print(f"✓ Integration complete")
    print(f"  φ(z={z_max:.0f}) = {phi[0]:.3e}")
    print(f"  φ(z={z_min:.0f}) = {phi[-1]:.3e}")
    print(f"  G(z={z_max:.0f}) = {G[0]:.3e}")
    print(f"  G(z={z_min:.0f}) = {G[-1]:.6f}")
    
    return z, phi, G

def verify_cmb_safety(z, G, z_cmb=1100, threshold=1e-4):
    """Verify CMB safety: G(z_CMB) ≪ threshold"""
    idx = np.argmin(np.abs(z - z_cmb))
    G_cmb = G[idx]
    
    print(f"\nCMB Safety Verification:")
    print(f"  G(z={z_cmb}) = {G_cmb:.3e}")
    print(f"  Threshold = {threshold:.3e}")
    print(f"  Margin = {threshold/G_cmb:.1e} (orders of magnitude)")
    
    if G_cmb < threshold:
        print(f"  ✓ CMB SAFE")
        return True
    else:
        print(f"  ✗ CMB UNSAFE!")
        return False

def save_results(z, phi, G, filename='../data/gz_solution.csv'):
    """Save solution to CSV"""
    chi_vals = chi(z)
    data = np.column_stack([z, chi_vals, phi, G])
    header = "z,chi(z),phi(z),G(phi)"
    np.savetxt(filename, data, delimiter=',', header=header, comments='')
    print(f"\n✓ Results saved to {filename}")

if __name__ == '__main__':
    print("="*70)
    print("EFC REGIME TRANSITION - LANDAU SOLVER")
    print("="*70)
    
    # Solve
    z, phi, G = solve_landau_equation()
    
    # Verify CMB safety
    is_safe = verify_cmb_safety(z, G)
    
    # Save
    save_results(z, phi, G)
    
    # Key results
    print("\nKey Results:")
    for z_val in [3000, 1100, 100, 50, 10, 2, 0]:
        idx = np.argmin(np.abs(z - z_val))
        print(f"  z={z_val:4d}: χ={chi(z_val):.3f}, φ={phi[idx]:.3e}, G={G[idx]:.3e}")
    
    print("\n" + "="*70)
    print("Done! Run plotting scripts to generate figures.")
    print("="*70)
