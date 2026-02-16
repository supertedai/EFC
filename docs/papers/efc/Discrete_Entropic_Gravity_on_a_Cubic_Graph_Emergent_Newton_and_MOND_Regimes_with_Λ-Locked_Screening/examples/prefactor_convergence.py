#!/usr/bin/env python3
"""
Prefactor convergence analysis: C vs lattice size N.

Demonstrates that the discrete renormalization prefactor C = g_AQUAL / √(a₀ g_N)
converges to ~2.32 as N → ∞, independent of binning geometry (cubic vs spherical).

Data from:
  "Discrete Entropic Gravity on a Cubic Graph: Emergent Newtonian
   and MOND Regimes with Λ-Locked Screening"
  Magnusson (2026), doi:10.6084/m9.figshare.31348411
"""

import json
import os


def load_convergence_data():
    """Load convergence data from JSON."""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "convergence_table.json")
    with open(data_path) as f:
        return json.load(f)


def display_convergence_table(data: dict):
    """Print convergence table."""
    print("=" * 60)
    print("Prefactor Convergence: C = g_AQUAL / √(a₀ g_N)")
    print("=" * 60)
    print()
    print(f"  {'N':>5s}  {'N³':>8s}  {'C_cubic':>8s}  {'C_sphere':>8s}  {'|Δ|':>6s}  {'C²':>6s}")
    print(f"  {'—'*5}  {'—'*8}  {'—'*8}  {'—'*8}  {'—'*6}  {'—'*6}")

    for row in data["data"]:
        N = row["N"]
        print(f"  {N:5d}  {N**3:8d}  {row['C_cubic']:8.3f}  {row['C_sphere']:8.3f}"
              f"  {row['C_difference']:6.3f}  {row['C_cubic']**2:6.2f}")

    print()
    ext = data["extrapolated_limit"]
    print(f"  Extrapolated (N → ∞): C = {ext['C_infinity']}")
    print(f"  a₀,eff / a₀ = C² = {ext['a0_eff_ratio_infinity']}")
    print()
    print(f"  Note: {ext['note']}")


def display_implications():
    """Print physical implications of C ≠ 1."""
    C = 2.32
    print()
    print("-" * 60)
    print("Physical Implications")
    print("-" * 60)
    print()
    print(f"  Standard MOND deep-regime:   g = √(a₀ g_N)")
    print(f"  Graph deep-regime:           g = {C} √(a₀ g_N)")
    print()
    print(f"  Equivalently:")
    print(f"    a₀,eff = C² × a₀ = {C**2:.2f} × a₀")
    print()
    print(f"  This means:")
    print(f"    - The graph operator enhances the deep-MOND response")
    print(f"      by a factor C = {C} relative to standard MOND")
    print(f"    - Any phenomenological comparison must use a₀,eff, not a₀")
    print(f"    - C is NOT a numerical artifact — it persists under")
    print(f"      resolution refinement and across binning geometries")
    print(f"    - It represents discrete renormalization of the")
    print(f"      infrared gravitational response")


def main():
    data = load_convergence_data()
    display_convergence_table(data)
    display_implications()


if __name__ == "__main__":
    main()
