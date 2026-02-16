#!/usr/bin/env python3
"""
Run all five kill tests and display results.

Reproduces the kill-test summary table from:
  "Discrete Entropic Gravity on a Cubic Graph: Emergent Newtonian
   and MOND Regimes with Λ-Locked Screening"
  Magnusson (2026), doi:10.6084/m9.figshare.31348411
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kill_tests import run_all_kill_tests
from src.aqual_operator import mu_interpolation, deep_mond_prediction, effective_a0
from src.lambda_screening import screening_length, acceleration_scale


def main():
    print("=" * 70)
    print("Discrete Entropic Gravity — Kill Test Suite")
    print("=" * 70)
    print()

    # Run all kill tests
    results = run_all_kill_tests()

    for kt in results:
        status = "PASS" if kt.result == "PASS" else kt.result
        print(f"  [{status:>22s}]  {kt.id}: {kt.name}")
        if kt.measured_value is not None:
            print(f"{'':>28s}  Measured: {kt.measured_value}")
        if kt.expected_value is not None:
            print(f"{'':>28s}  Expected: {kt.expected_value}")
        if kt.notes:
            print(f"{'':>28s}  {kt.notes}")
        print()

    # Summary
    passed = sum(1 for r in results if r.result == "PASS")
    print(f"  {passed}/5 passed, "
          f"{sum(1 for r in results if r.result == 'STRUCTURAL_DEPARTURE')}/5 structural departure")
    print()

    # Supplementary calculations
    print("-" * 70)
    print("Supplementary Calculations")
    print("-" * 70)
    print()

    # Interpolating function examples
    print("  μ(x) = x / √(1 + x²)")
    for x in [0.01, 0.1, 1.0, 10.0, 100.0]:
        print(f"    μ({x:6.2f}) = {mu_interpolation(x):.6f}")
    print()

    # Prefactor and effective a₀
    C = 2.32
    print(f"  Prefactor C = {C}")
    print(f"  a₀,eff / a₀ = C² = {C**2:.2f}")
    print()

    # Λ-locked scales
    L = screening_length()
    a0 = acceleration_scale()
    print(f"  L_Λ = 1/√Λ = {L:.3e} m")
    print(f"  a₀ = c²√Λ  = {a0:.3e} m/s²")
    print(f"  a₀,eff      = {C**2 * a0:.3e} m/s²")
    print()

    # Deep MOND example
    g_N = 1e-10  # m/s²
    g_mond_std = (a0 * g_N) ** 0.5
    g_mond_graph = deep_mond_prediction(a0, g_N, C)
    print(f"  Deep MOND (g_N = {g_N:.1e} m/s²):")
    print(f"    Standard:  g = √(a₀ g_N) = {g_mond_std:.3e} m/s²")
    print(f"    Graph:     g = C√(a₀ g_N) = {g_mond_graph:.3e} m/s²")
    print(f"    Ratio:     {g_mond_graph / g_mond_std:.2f}")


if __name__ == "__main__":
    main()
