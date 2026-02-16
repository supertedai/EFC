#!/usr/bin/env python3
"""
Reproduce the σ₈ results table from:
  "Cosmological Growth Constraints on Λ-Locked Discrete Entropic Gravity"
  Magnusson (2026)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.scenario_runner import run_all_scenarios, compare_table, SCENARIOS
from src.geff_coupling import geff_ratio, lambda_locked_scale
from src.growth_equation import SIGMA8_LCDM


def main():
    print("=" * 70)
    print("Cosmological Growth Constraints on Λ-Locked Discrete Entropic Gravity")
    print("=" * 70)
    print()

    # Display Λ-locked scale
    L = lambda_locked_scale()
    print(f"  Λ-locked screening length: L_Λ ≈ {L:.1f} Gpc ≈ H₀⁻¹")
    print(f"  ΛCDM σ₈ = {SIGMA8_LCDM}")
    print()

    # Show G_eff/G screening for each scenario
    print("-" * 70)
    print("G_eff(k)/G at structure-formation scales")
    print("-" * 70)
    print()

    k_test = 0.1  # h/Mpc — typical BAO scale
    for s in SCENARIOS:
        ratio = geff_ratio(k_test, s.k_transition)
        screened = "SCREENED" if ratio < 1.01 else f"ENHANCED (×{ratio:.1f})"
        print(f"  Scenario {s.id} ({s.name:>10s}): "
              f"k_trans = {s.k_transition:.4f} h/Mpc  →  "
              f"G_eff/G at k=0.1 = {ratio:.4f}  [{screened}]")
    print()

    # Main results table
    print("-" * 70)
    print("σ₈ Results (from paper Table, Section 5)")
    print("-" * 70)
    print()
    print(compare_table())
    print()

    # Interpretation
    print("-" * 70)
    print("Interpretation")
    print("-" * 70)
    print()
    print("  • Λ-locking (Scenario A): σ₈ = 0.814, within 0.4% of ΛCDM")
    print("    → Cosmologically SAFE")
    print()
    print("  • 10 Mpc transition (B): σ₈ = 367 → ×452 overgrowth")
    print("    → CATASTROPHIC")
    print()
    print("  • 1 Mpc transition (C): σ₈ = 24,098 → ×29,714 overgrowth")
    print("    → CATASTROPHIC")
    print()
    print("  Conclusion: Λ-locking is a NECESSARY CONDITION for")
    print("  cosmological consistency of infrared-enhanced gravity.")
    print()
    print("  Viability condition: L_Λ ≳ H₀⁻¹")
    print("  (Not tuned — follows from L_Λ ∝ Λ^{-1/2})")


if __name__ == "__main__":
    main()
