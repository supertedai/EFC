#!/usr/bin/env python3
"""
Display G_eff(k)/G profiles for each scenario.

Shows how the Lorentzian window function behaves across wavenumbers
for the three transition-scale scenarios tested in the paper.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.geff_coupling import geff_ratio, GeffModel


def main():
    print("=" * 70)
    print("G_eff(k)/G Profiles: Lorentzian Window Function")
    print("=" * 70)
    print()
    print("  Formula: G_eff(k)/G = 1 + (C²−1) / (1 + (k/k_Λ)²)")
    print(f"  C = 2.32,  C² − 1 = {2.32**2 - 1:.4f}")
    print()

    scenarios = [
        GeffModel(C=2.32, k_transition=0.0014),   # Λ-locked
        GeffModel(C=2.32, k_transition=0.1),       # 10 Mpc
        GeffModel(C=2.32, k_transition=1.0),       # 1 Mpc
    ]
    names = ["A: Λ-locked (4.4 Gpc)", "B: 10 Mpc", "C: 1 Mpc"]

    k_values = [0.0001, 0.001, 0.01, 0.05, 0.1, 0.5, 1.0, 10.0]

    # Header
    header = f"  {'k (h/Mpc)':>12s}"
    for name in names:
        header += f"  {name:>22s}"
    print(header)
    print(f"  {'─' * 12}" + f"  {'─' * 22}" * 3)

    # Rows
    for k in k_values:
        row = f"  {k:12.4f}"
        for model in scenarios:
            ratio = model.ratio(k)
            row += f"  {ratio:22.4f}"
        print(row)

    print()
    print("  Key observations:")
    print("  • Scenario A: G_eff/G ≈ 1.00 for all k > 0.01 h/Mpc (all structure scales screened)")
    print("  • Scenario B: G_eff/G ≈ 5.38 at k = 0.01 (enhancement covers growth scales)")
    print("  • Scenario C: G_eff/G ≈ 5.38 at k = 0.1  (enhancement deep into nonlinear regime)")
    print()

    # Screening boundary
    print("-" * 70)
    print("Screening boundary (G_eff/G − 1 < 1% of max enhancement)")
    print("-" * 70)
    print()
    for model, name in zip(scenarios, names):
        # Find k where enhancement drops below 1%
        for k_test in [0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]:
            r = model.ratio(k_test)
            frac = (r - 1.0) / model.enhancement
            if frac < 0.01:
                print(f"  {name}: screened at k ≈ {k_test} h/Mpc (L ≈ {1.0/k_test:.0f} Mpc)")
                break


if __name__ == "__main__":
    main()
