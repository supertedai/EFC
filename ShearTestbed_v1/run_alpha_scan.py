#!/usr/bin/env python
"""
EFC α_L2 Parameter Scan
=======================
Tests different EFC strength parameters to find optimal fit.
"""

import subprocess
import re
import os

os.chdir('/home/user/EFC/ShearTestbed_v1/kcap')

# α values to test
alpha_values = [0.00, 0.01, 0.02, 0.03, 0.05, 0.07, 0.10]

results = []

print("=" * 70)
print("EFC α_L2 PARAMETER SCAN")
print("=" * 70)
print(f"Testing α_L2 = {alpha_values}")
print("-" * 70)

for alpha in alpha_values:
    # Run cosmosis with modified alpha
    cmd = [
        'cosmosis',
        'runs/config/KiDS1000_Flinc_EFC.ini',
        '-p', f'efc_projection.efc_alpha={alpha}'
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    output = result.stdout + result.stderr

    # Extract likelihood
    match = re.search(r'Likelihood kids1000_flinc = (-?\d+\.?\d*)', output)
    if match:
        lnL = float(match.group(1))
        chi2 = -2 * lnL
        results.append((alpha, lnL, chi2))
        print(f"α_L2 = {alpha:.2f}: -ln(L) = {lnL:.2f}, χ² = {chi2:.1f}")
    else:
        print(f"α_L2 = {alpha:.2f}: FAILED")

print("-" * 70)
print("\nSUMMARY TABLE:")
print("-" * 70)
print(f"{'α_L2':>8} {'−ln(L)':>12} {'χ²':>10} {'Δχ² vs α=0':>14}")
print("-" * 70)

if results:
    baseline_chi2 = results[0][2] if results[0][0] == 0.0 else None

    for alpha, lnL, chi2 in results:
        delta = chi2 - baseline_chi2 if baseline_chi2 else 0
        print(f"{alpha:>8.2f} {lnL:>12.2f} {chi2:>10.1f} {delta:>14.1f}")

    # Find best
    best = min(results, key=lambda x: x[1])
    print("-" * 70)
    print(f"BEST FIT: α_L2 = {best[0]:.2f}, -ln(L) = {best[1]:.2f}")
    print(f"Improvement over ΛCDM: Δχ² = {best[2] - results[0][2]:.1f}")
