#!/usr/bin/env python3
"""
Demo: E_G(k) bump prediction from the Scale-Localised Modified Gravity model.

Reproduces Table 2 from DOI: 10.6084/m9.figshare.31985313.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import numpy as np
from scale_localised_gravity import (
    stiffness_response, mu, eta, sigma, E_G, E_G_GR, K_C
)

print("=== Scale-Localised Modified Gravity: E_G(k) Forecast ===\n")

# Reference point
z_ref = 0.0
k_ref = K_C
print(f"Reference point (k_c={k_ref}, z={z_ref}):")
print(f"  mu  = {mu(k_ref, z_ref):.3f}")
print(f"  eta = {eta(k_ref, z_ref):.3f}")
print(f"  Sigma = {sigma(k_ref, z_ref):.3f}")

# Table 2: E_G(k) at z=0.3
z = 0.3
k_vals = [0.01, 0.03, 0.05, 0.10, 0.20]
eg_gr = E_G_GR(z)

print(f"\nTable 2: E_G(k) at z = {z}")
print(f"{'k [h/Mpc]':>12} {'E_G^GR':>8} {'E_G^EFC':>9} {'Delta%':>8} {'Sigma/mu':>10}")
print("-" * 52)
for k in k_vals:
    eg_efc = E_G(k, z)
    delta = (eg_efc / eg_gr - 1) * 100
    sig_mu = sigma(k, z) / mu(k, z)
    marker = " <-- peak" if k == K_C else ""
    print(f"{k:>12.2f} {eg_gr:>8.3f} {eg_efc:>9.3f} {delta:>+7.1f}% {sig_mu:>10.3f}{marker}")

# Detection forecast
print(f"\nPeak bump: ~7.4% at k = {K_C} h/Mpc")
print("Detection significance: ~2.5-3.5 sigma with DESI x Planck")
print("\nDone.")
