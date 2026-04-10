#!/usr/bin/env python3
"""
Demo: Compute EFC observable predictions.

Evaluates coupling mu(a), growth rate f*sigma_8, and S_8 suppression
from the EFC field equations.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970898
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from field_equations import (
    mu_sigmoid,
    mu_coupling,
    entropy_field_S,
    f_sigma8,
    S8_suppression,
    response_surface,
)
import numpy as np


def main():
    print("=" * 65)
    print("EFC White Paper Part 2 — Observable Mapping Demo")
    print("=" * 65)

    # --- Entropy field S(a) ---
    print("\n--- Entropy field S(a) ---")
    for a in [0.1, 0.3, 0.5, 0.7, 1.0]:
        print(f"  a = {a:.2f}  =>  S(a) = {entropy_field_S(a):.4f}")

    # --- Coupling mu(a) —  two parameterisations ---
    print("\n--- Coupling mu(a) ---")
    print(f"  {'a':>5}  {'mu_derived':>12}  {'mu_sigmoid':>12}")
    for a in [0.3, 0.5, 0.7, 0.8, 0.9, 1.0]:
        md = mu_coupling(a)
        ms = mu_sigmoid(a)
        print(f"  {a:5.2f}  {md:12.6f}  {ms:12.6f}")

    # --- Growth rate f*sigma_8 ---
    print("\n--- Growth rate f*sigma_8(z) ---")
    print("  Using sigmoid parameterisation (B=0.06, a_t=0.7, n=2)")
    for z in [0.3, 0.5, 0.7, 1.0]:
        try:
            fs8 = f_sigma8(z, mu_func=mu_sigmoid)
            print(f"  z = {z:.1f}  =>  f*sigma_8 = {fs8:.4f}")
        except Exception as e:
            print(f"  z = {z:.1f}  =>  [computation error: {e}]")

    # LCDM comparison
    print("\n  LCDM reference (mu=1):")
    mu_one = lambda a: 1.0
    for z in [0.3, 0.5, 0.7, 1.0]:
        try:
            fs8 = f_sigma8(z, mu_func=mu_one)
            print(f"  z = {z:.1f}  =>  f*sigma_8 = {fs8:.4f}")
        except Exception as e:
            print(f"  z = {z:.1f}  =>  [computation error: {e}]")

    # --- S_8 suppression ---
    print("\n--- S_8 suppression (Eqs. 10-11) ---")
    mu_0 = 0.94
    delta = S8_suppression(mu_0)
    print(f"  mu_0 = {mu_0:.2f}  =>  Delta_sigma_8 ~ {delta:.4f}")

    # --- Response surface R(k, S) ---
    print("\n--- Response surface R(k, S) slices ---")
    for S in [0.0, 0.1, 0.3, 0.5, 0.9]:
        R = response_surface(k=0.1, S=S)
        print(f"  S = {S:.1f}  =>  R(k=0.1, S) = G_eff/G_N = {R:.4f}")

    print("\n--- Structural hierarchy ---")
    print("  1. S(a)                     [fundamental]")
    print("  2. mu(a) = 1 + beta*S(a)    [derived]")
    print("  3. Growth ODE with mu(a)    [dynamical]")
    print("  4. f*sigma_8, S_8, Sigma    [empirical]")
    print("  5. R(k,S)                   [unifying]")


if __name__ == "__main__":
    main()
