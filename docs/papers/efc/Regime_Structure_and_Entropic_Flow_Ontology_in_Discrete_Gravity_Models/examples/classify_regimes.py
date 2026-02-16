#!/usr/bin/env python3
"""
Classify physical systems by regime using the dimensionless ratios (ξ, η).

From: "Regime Structure and Entropic Flow Ontology in Discrete Gravity Models"
      Magnusson (2026), Section 4, Eq. 9
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.regime_classifier import classify_regime, transition_scales, screening_length
from src.interpolating_function import mu, mu_table


def main():
    print("=" * 70)
    print("Regime Structure and Entropic Flow Ontology")
    print("in Discrete Gravity Models")
    print("=" * 70)
    print()

    # --- Interpolating function ---
    print("-" * 70)
    print("Interpolating Function μ(x) = x / √(1 + x²)")
    print("-" * 70)
    print()
    print(f"  {'x':>10s}  {'μ(x)':>10s}  {'Regime':>25s}")
    print(f"  {'─' * 10}  {'─' * 10}  {'─' * 25}")
    for entry in mu_table([0.001, 0.01, 0.1, 0.5, 1.0, 2.0, 10.0, 100.0]):
        print(f"  {entry['x']:10.3f}  {entry['mu']:10.6f}  {entry['regime']:>25s}")
    print()
    print(f"  μ(1) = 1/√2 = {mu(1.0):.6f} (transition point)")
    print()

    # --- Regime classification ---
    print("-" * 70)
    print("Regime Classification: Physical Examples")
    print("-" * 70)
    print()
    print("  Dimensionless ratios:")
    print("    ξ = |∇Φ| / a₀      (gradient strength)")
    print("    η = μ_Λ Φ / |∇²Φ|  (bulk strength)")
    print()

    examples = [
        ("Solar system",        1e8,    1e-20),
        ("Earth surface",       1e12,   1e-25),
        ("Galaxy core",         1e3,    1e-10),
        ("Galaxy outskirts",    0.1,    1e-5),
        ("LSB galaxy",          0.01,   1e-6),
        ("Cluster outskirts",   0.5,    0.01),
        ("Void boundary",       0.001,  0.5),
        ("Super-Hubble",        0.0001, 100.0),
        ("Horizon scale",       0.001,  1000.0),
    ]

    print(f"  {'System':<22s}  {'ξ':>10s}  {'η':>10s}  {'Regime':<25s}  {'Behaviour'}")
    print(f"  {'─' * 22}  {'─' * 10}  {'─' * 10}  {'─' * 25}  {'─' * 20}")

    for name, xi, eta in examples:
        result = classify_regime(xi, eta)
        print(f"  {name:<22s}  {xi:10.1e}  {eta:10.1e}  {result.regime:<25s}  {result.behaviour}")

    print()

    # --- Regime dominance map ---
    print("-" * 70)
    print("Regime Dominance Map (Table from Section 4)")
    print("-" * 70)
    print()
    print(f"  {'Regime':<20s}  {'ξ':>8s}  {'η':>8s}  {'Behaviour':<25s}  {'Dominant sector'}")
    print(f"  {'─' * 20}  {'─' * 8}  {'─' * 8}  {'─' * 25}  {'─' * 20}")
    print(f"  {'UV (Newtonian)':<20s}  {'>> 1':>8s}  {'<< 1':>8s}  {'g ∝ r⁻²':<25s}  {'gradient (linear)'}")
    print(f"  {'IR (MOND-like)':<20s}  {'<< 1':>8s}  {'<< 1':>8s}  {'g ∝ r⁻¹':<25s}  {'gradient (nonlinear)'}")
    print(f"  {'Cosmological':<20s}  {'any':>8s}  {'>> 1':>8s}  {'Yukawa screening':<25s}  {'bulk'}")
    print()
    print("  Transitions:")
    print("    UV → IR:            ξ ~ 1  (g ~ a₀)")
    print("    IR → Cosmological:  η ~ 1  (scales approaching L_Λ)")
    print()

    # --- Transition scales ---
    print("-" * 70)
    print("Physical Transition Scales")
    print("-" * 70)
    print()
    scales = transition_scales()
    print(f"  UV → IR transition:")
    print(f"    {scales['UV_to_IR']['condition']}")
    print(f"    a₀ = {scales['UV_to_IR']['a0_m_s2']:.1e} m/s²")
    print()
    print(f"  IR → Cosmological transition:")
    print(f"    {scales['IR_to_Cosmological']['condition']}")
    print(f"    L_Λ ≈ {scales['IR_to_Cosmological']['L_Lambda_Gpc']} Gpc")
    print()
    print(f"  Dual role of Λ:")
    print(f"    Local:  a₀ ∝ c² √Λ = {scales['lambda_dual_role']['a0_from_Lambda']:.2e} m/s²")
    print(f"    Global: L_Λ ∝ Λ⁻¹/² ≈ {scales['lambda_dual_role']['L_Lambda_Gpc']} Gpc ≈ H₀⁻¹")
    print(f"    Both from single parameter μ_Λ ∝ Λ — not tuned")
    print()

    # --- Key structural features ---
    print("-" * 70)
    print("Key Structural Features")
    print("-" * 70)
    print()
    print("  1. Three regimes are EXHAUSTIVE: for any (ξ, η), exactly one dominates")
    print("  2. Transitions are SMOOTH: governed by μ(x) = x/√(1+x²)")
    print("  3. No free functions beyond μ(x) and μ_Λ ∝ Λ")
    print("  4. Entire framework on GRAPH TOPOLOGY; no continuum metric assumed")
    print("  5. Time is NOT fundamental: δF/δΦ_i = 0 is equilibrium")


if __name__ == "__main__":
    main()
