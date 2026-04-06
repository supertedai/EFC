#!/usr/bin/env python3
"""Demonstration: EFC Introduction to Entropy in Cosmic Evolution.

Shows:
  1. Cosmic epochs and thermal properties
  2. Entropy budget analysis
  3. Temperature-entropy curve across cosmic history
  4. Entropy growth ratios between epochs

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from entropy_cosmic_evolution import (
    CosmicEpoch,
    EntropyBudget,
    CosmicEntropyEvolution,
    CMB_TEMPERATURE,
)


def demo_cosmic_epochs():
    """1. Cosmic epochs and thermal properties."""
    print("=" * 60)
    print("1. COSMIC EPOCHS AND THERMAL PROPERTIES")
    print("=" * 60)

    model = CosmicEntropyEvolution()
    model.load_standard_epochs()

    print(f"\n{model.summary()}\n")

    for e in model.epochs:
        u = e.thermal_energy_density()
        s_ph = e.entropy_per_photon()
        cf = e.cooling_factor(model.epochs[0].temperature)
        print(f"  {e.name:<20s}  u={u:.3e} W/m^2  "
              f"s/photon={s_ph:.3e} J/K  cool={cf:.3e}")


def demo_entropy_budget():
    """2. Entropy budget analysis."""
    print("\n" + "=" * 60)
    print("2. ENTROPY BUDGET ANALYSIS")
    print("=" * 60)

    budgets = [
        ("Early universe", EntropyBudget(radiation_entropy=1e88, matter_entropy=1e80, structure_entropy=0)),
        ("Post-recombination", EntropyBudget(radiation_entropy=1e80, matter_entropy=1e78, structure_entropy=1e70)),
        ("Present day", EntropyBudget(radiation_entropy=1e80, matter_entropy=1e78, structure_entropy=1e104)),
    ]

    for name, b in budgets:
        f = b.fractions()
        print(f"\n  {name}:")
        print(f"    Total:      {b.total():.3e} J/K")
        print(f"    Radiation:  {f['radiation']:.4%}")
        print(f"    Matter:     {f['matter']:.4%}")
        print(f"    Structure:  {f['structure']:.4%}")
        print(f"    Dominated:  {b.dominated_by()}")


def demo_temperature_entropy_curve():
    """3. Temperature-entropy curve."""
    print("\n" + "=" * 60)
    print("3. TEMPERATURE-ENTROPY CURVE")
    print("=" * 60)

    model = CosmicEntropyEvolution()
    model.load_standard_epochs()

    curve = model.temperature_entropy_curve()
    print(f"\n  {'Temperature (K)':>16}  {'Entropy density':>16}")
    print("  " + "-" * 36)
    for T, s in curve:
        print(f"  {T:16.3e}  {s:16.3e}")


def demo_growth_ratios():
    """4. Entropy growth ratios between epochs."""
    print("\n" + "=" * 60)
    print("4. ENTROPY GROWTH RATIOS")
    print("=" * 60)

    model = CosmicEntropyEvolution()
    model.load_standard_epochs()

    pairs = [
        ("planck", "inflation_end"),
        ("inflation_end", "nucleosynthesis"),
        ("nucleosynthesis", "recombination"),
        ("recombination", "present"),
    ]

    for a, b in pairs:
        ratio = model.entropy_growth_ratio(a, b)
        print(f"  {a:>20s} / {b:<20s} = {ratio:.3e}")


if __name__ == "__main__":
    print("EFC Introduction to Entropy in Cosmic Evolution")
    print("Magnusson (2026)")
    print()

    demo_cosmic_epochs()
    demo_entropy_budget()
    demo_temperature_entropy_curve()
    demo_growth_ratios()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
