#!/usr/bin/env python3
"""
Demonstrate sector dominance transitions in the discrete entropic functional.

Shows how the gradient, bulk, and source sectors compete as
physical conditions change across regimes.

From: "Regime Structure and Entropic Flow Ontology in Discrete Gravity Models"
      Magnusson (2026), Section 2 (Eq. 1)
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.discrete_functional import (
    gradient_sector, bulk_sector, source_sector,
    sector_decomposition, SectorContribution
)
from src.interpolating_function import mu, aqual_integrand


def main():
    print("=" * 70)
    print("Sector Dominance in the Discrete Entropic Functional")
    print("=" * 70)
    print()
    print("  F[Φ] = [Gradient] + [Bulk] + [Source]")
    print()

    # Parameters
    a0 = 1.2e-10        # m/s²
    mu_lambda = 1.11e-52  # proportional to Λ
    phi_v = 0.0          # reference potential

    # --- Scenario 1: Strong field (Solar system) ---
    print("-" * 70)
    print("Scenario 1: Strong Field (Solar System)")
    print("  |∇Φ| >> a₀, bulk negligible")
    print("-" * 70)
    phi_i = 1e10
    phi_j = 1e10 - 1e-2   # large gradient
    rho = 1e3              # kg/m³

    sectors = sector_decomposition(phi_i, phi_j, phi_v, rho, a0, mu_lambda)
    _print_sectors(sectors)
    print(f"  → Gradient dominates: UV (Newtonian) regime")
    print(f"    μ(x) = {mu(abs(phi_i - phi_j) / a0):.6f} ≈ 1")
    print()

    # --- Scenario 2: Weak field (Galaxy outskirts) ---
    print("-" * 70)
    print("Scenario 2: Weak Field (Galaxy Outskirts)")
    print("  |∇Φ| << a₀, bulk still small")
    print("-" * 70)
    phi_i = 1e-12
    phi_j = 1e-12 - 1e-22  # tiny gradient
    rho = 1e-22             # very low density

    sectors = sector_decomposition(phi_i, phi_j, phi_v, rho, a0, mu_lambda)
    _print_sectors(sectors)
    x = abs(phi_i - phi_j) / a0
    print(f"  → Gradient (nonlinear) dominates: IR (MOND-like) regime")
    print(f"    μ(x) = {mu(x):.2e} ~ x (MOND scaling)")
    print()

    # --- Scenario 3: Cosmological scale ---
    print("-" * 70)
    print("Scenario 3: Cosmological Scale (Super-Hubble)")
    print("  Bulk term dominates over gradient")
    print("-" * 70)
    phi_i = 1e20           # large potential at cosmological scales
    phi_j = 1e20 - 1e5     # small relative gradient
    rho = 1e-26            # cosmic mean density
    mu_lambda_cosmo = 1e-35  # enhanced for illustration

    sectors = sector_decomposition(phi_i, phi_j, phi_v, rho, a0, mu_lambda_cosmo)
    _print_sectors(sectors)
    print(f"  → Bulk dominates: Cosmological (Yukawa) regime")
    print(f"    L_Λ = 1/√μ_Λ screening active")
    print()

    # --- AQUAL integrand ---
    print("-" * 70)
    print("AQUAL Kinetic Integrand F(x) = √(1+x²) − 1")
    print("-" * 70)
    print()
    print(f"  {'x':>10s}  {'F(x)':>12s}  {'μ(x)':>10s}  {'Note'}")
    print(f"  {'─' * 10}  {'─' * 12}  {'─' * 10}  {'─' * 25}")
    for x in [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]:
        f_val = aqual_integrand(x)
        mu_val = mu(x)
        if x < 0.1:
            note = "MOND: F ~ x²/2"
        elif x > 10:
            note = "Newton: F ~ x"
        else:
            note = "transition"
        print(f"  {x:10.3f}  {f_val:12.6f}  {mu_val:10.6f}  {note}")
    print()

    # --- Circuit analogy ---
    print("-" * 70)
    print("Circuit Analogy (from Section 7)")
    print("-" * 70)
    print()
    print("  Gradient sector  ↔  Nonlinear resistor network")
    print("    • Linear (Ohmic) at high voltage  →  Newtonian")
    print("    • Nonlinear at low voltage         →  MOND")
    print()
    print("  Bulk sector      ↔  Global capacitor (Λ-term)")
    print("    • Return path to reference potential Φ_V")
    print("    • Capacitance ~ 1/Λ (screening length L_Λ)")
    print()
    print("  Source sector    ↔  Current sources (matter)")
    print("    • Drive the potential distribution")
    print()
    print("  The regime is determined by which component")
    print("  dominates the impedance at a given scale.")


def _print_sectors(sectors):
    """Print sector decomposition table."""
    print()
    print(f"    {'Sector':<12s}  {'Value':>14s}  {'Fraction':>10s}  {'Bar'}")
    print(f"    {'─' * 12}  {'─' * 14}  {'─' * 10}  {'─' * 25}")
    for s in sectors:
        bar = "█" * int(s.fraction * 25)
        print(f"    {s.name:<12s}  {s.value:14.4e}  {s.fraction:10.1%}  {bar}")
    print()


if __name__ == "__main__":
    main()
