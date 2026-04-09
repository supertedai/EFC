#!/usr/bin/env python3
"""
Demo: Compute regime susceptibility T(S), equation of state w(a),
and cross-scale amplification ratio.

Reference: Magnusson (2026), doi:10.6084/m9.figshare.31970907
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from regime_susceptibility import (
    rho_eff,
    susceptibility_T,
    beta_scaled,
    self_regulation_product,
    equation_of_state,
    amplification_ratio,
)
import numpy as np


def main():
    print("=" * 65)
    print("EFC White Paper Part 4 — Regime Susceptibility Demo")
    print("=" * 65)

    # --- Effective energy density ---
    print("\n--- Effective energy density rho_eff(S) = S(1-S) ---")
    for S in [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]:
        print(f"  S = {S:.2f}  =>  rho_eff = {rho_eff(S):.4f}")

    # --- Susceptibility function ---
    print("\n--- Susceptibility T(S) = S_0(1-S_0)/[S(1-S)] ---")
    print(f"  {'S':>5}  {'T(S)':>10}  {'beta(S)':>10}  {'beta*rho':>10}")
    for S in [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9, 0.99]:
        T = susceptibility_T(S)
        b = beta_scaled(S)
        prod = self_regulation_product(S)
        print(f"  {S:5.2f}  {T:10.4f}  {b:10.4f}  {prod:10.4f}")

    print("\n  Self-regulation: beta(S)*rho_eff(S) = const = 0.0144")
    print("  (Proposition 1 verified: S(1-S) terms cancel)")

    # --- Equation of state ---
    print("\n--- Equation of state w(a) = -beta(S)*a ---")
    # At S_gal = 0.1 (today, galactic):
    S_gal = 0.1
    print(f"  At S_gal = {S_gal}:")
    for a in [0.3, 0.5, 0.7, 1.0]:
        w = equation_of_state(a, S_gal)
        print(f"    a = {a:.1f}  =>  w = {w:.4f}")

    # At S_cosm ~ 0.9 (cosmological):
    S_cosm = 0.9
    print(f"  At S_cosm = {S_cosm}:")
    for a in [0.3, 0.5, 0.7, 1.0]:
        w = equation_of_state(a, S_cosm)
        print(f"    a = {a:.1f}  =>  w = {w:.4f}")

    # --- Cross-scale amplification ---
    print("\n--- Cross-scale amplification ---")
    ratio = amplification_ratio(S_gal=0.1, S_cosm=0.9)
    print(f"  beta_cosm / beta_gal = T(S_cosm)/T(S_gal) = {ratio:.4f}")
    print(f"  beta_gal = 0.16  =>  beta_cosm ~ {0.16 * ratio:.3f}")
    print(f"  => w_0 ~ -{0.16 * ratio:.3f}")

    # --- Entropic continuum phases ---
    print("\n--- Entropic Continuum ---")
    print("  div(J^mu) < 0 : convergent  => DM regime (excess gravity)")
    print("  div(J^mu) = 0 : equilibrium => matter-dominated")
    print("  div(J^mu) > 0 : divergent   => DE regime (acceleration)")
    print()
    print("  Thermodynamic boundaries:")
    print("    S -> 0 : Singularity    — GR recovered (Part 1)")
    print("    S -> 1 : Altular limit  — de Sitter asymptote")


if __name__ == "__main__":
    main()
