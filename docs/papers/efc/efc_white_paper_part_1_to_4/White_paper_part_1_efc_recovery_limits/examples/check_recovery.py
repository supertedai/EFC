#!/usr/bin/env python3
"""
Demo: Verify EFC recovery conditions numerically.

Checks all three recovery conditions (Theorems 1-3) and prints
the triangulated recovery result (Proposition 1).

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970886
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from recovery_limits import (
    check_condition_I,
    check_condition_II,
    check_condition_III,
    theta_z,
    mu_efc_parametric,
)
import numpy as np


def main():
    print("=" * 65)
    print("EFC White Paper Part 1 — Recovery Condition Verification")
    print("=" * 65)

    # --- Condition I: Parameter limit ---
    print("\n--- Condition I: Parameter limit (Theorem 1) ---")
    for alpha in [0.0, -0.5, -1.0]:
        result = check_condition_I(alpha)
        status = "RECOVERED" if result["recovered"] else "active"
        print(f"  alpha_L2 = {alpha:+.2f}  =>  {status}")

    # --- Condition II: Low-entropy regime ---
    print("\n--- Condition II: Entropy recovery (Theorem 2) ---")
    for S in [0.01, 0.05, 0.1, 0.5, 0.9]:
        result = check_condition_II(S)
        status = "RECOVERED (GR)" if result["recovered"] else "EFC active"
        print(f"  S = {S:.2f}  =>  {status}")

    # --- Condition III: Density saturation ---
    print("\n--- Condition III: Density saturation (Theorem 3) ---")
    for rho in [1e0, 1e3, 1e6, 1e9]:
        result = check_condition_III(rho)
        print(f"  rho = {rho:.0e}  =>  Theta(rho) = {result['theta_rho']:.2e}  "
              f"{'RECOVERED' if result['recovered'] else 'active'}")

    # --- Theta(z) profile ---
    print("\n--- Regime-transition function Theta(z) ---")
    for z in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0]:
        print(f"  z = {z:6.1f}  =>  Theta(z) = {theta_z(z):.4f}")

    # --- mu(a) profile ---
    print("\n--- mu(a) growth suppression ---")
    for a in [0.3, 0.5, 0.7, 0.8, 0.9, 1.0]:
        mu = mu_efc_parametric(a)
        print(f"  a = {a:.2f}  =>  mu = {mu:.4f}  (delta_mu = {mu - 1:.4f})")

    # --- Proposition 1: Triangulated recovery ---
    print("\n--- Proposition 1: Triangulated Recovery ---")
    print("  Any ONE of the three conditions independently yields:")
    print("    mu(k,z) -> 1,   Sigma(k,z) -> 1")
    print("  No cross-terms between channels.")
    print("  => EFC superset_pert LCDM  (Corollary 1)")


if __name__ == "__main__":
    main()
