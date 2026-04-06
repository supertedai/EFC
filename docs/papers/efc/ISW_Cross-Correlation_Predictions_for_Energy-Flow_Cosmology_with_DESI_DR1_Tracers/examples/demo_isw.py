#!/usr/bin/env python3
"""
Demo: ISW Cross-Correlation Predictions for EFC with DESI DR1 Tracers

Shows the cancellation metric and ISW amplitude suppression for DESI tracers.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.isw_cross_correlation import ISWCrossCorrelation, PAPER_RESULTS
import numpy as np


def main():
    print("=" * 65)
    print("ISW Cross-Correlation Predictions for EFC with DESI DR1 Tracers")
    print("=" * 65)

    # --- Setup ---
    isw = ISWCrossCorrelation(beta=0.16, a_t=0.55, sigma_cos=0.25)
    print(f"\nParameters: beta={isw.beta}, a_t={isw.a_t}, z_t={isw.z_t:.2f}")

    # --- Transition function ---
    print("\n1. MODIFIED POISSON mu(a)")
    print("-" * 45)
    test_z = [0.0, 0.51, 0.82, 0.93, 1.32, 2.0]
    for z in test_z:
        a = 1.0 / (1.0 + z)
        mu_val = float(isw.mu(np.array([a]))[0])
        S_val = float(isw.S(np.array([a]))[0])
        print(f"   z={z:<5} a={a:.3f}  S(a)={S_val:.4f}  mu(a)={mu_val:.4f}")

    # --- Kernel decomposition ---
    print("\n2. ISW KERNEL DECOMPOSITION")
    print("-" * 45)
    z_grid = np.linspace(0.01, 3.0, 300)
    kernel = isw.isw_kernel(z_grid)
    idx_peak = np.argmax(np.abs(kernel.K_mu_prime))
    z_peak = z_grid[idx_peak]
    print(f"   Peak K_mu' transition contribution at z ~ {z_peak:.2f}")
    print(f"   K_mu (standard) and K_mu' (transition) have opposite signs near z_t")

    # --- Tracer predictions ---
    print("\n3. DESI DR1 TRACER PREDICTIONS")
    print("-" * 45)
    tracers = isw.predict_tracers()
    print(f"   {'Tracer':<12} {'z_eff':<8} {'C':<8} {'A_ISW':<8}")
    print(f"   {'-'*36}")
    for name, result in tracers.items():
        print(f"   {name:<12} {result['z_eff']:<8} {result['C']:<8.2f} {result['A_ISW']:<8.2f}")

    # --- Paper reference values ---
    print("\n4. PAPER REFERENCE VALUES")
    print("-" * 45)
    paper = PAPER_RESULTS['tracer_predictions']
    print(f"   {'Tracer':<12} {'z_eff':<8} {'C':<8} {'A_ISW':<8}")
    print(f"   {'-'*36}")
    for name, vals in paper.items():
        C = vals['C']
        A = vals.get('A_ISW', '--')
        A_str = f"{A:.2f}" if isinstance(A, (int, float)) else str(A)
        print(f"   {name:<12} {vals['z_eff']:<8} {C:<8.2f} {A_str:<8}")

    # --- LCDM comparison ---
    print("\n5. EFC vs LCDM COMPARISON")
    print("-" * 45)
    print(f"   LCDM: C = 0 (no cancellation), A_ISW = 1.0 for all tracers")
    print(f"   EFC:  C increases monotonically with tracer overlap with z_t")
    print(f"   EFC:  A_ISW = 0.29-0.56 (suppressed)")

    # --- Falsification ---
    print("\n6. FALSIFICATION CRITERIA")
    print("-" * 45)
    fals = PAPER_RESULTS['falsification']
    print(f"   EFC falsified if: {fals['EFC_falsified_if']}")
    print(f"   LCDM challenged if: {fals['LCDM_challenged_if']}")

    print("\n" + "=" * 65)
    print("ISW cancellation from EFC transition kernel is a decisive test.")
    print("=" * 65)


if __name__ == '__main__':
    main()
