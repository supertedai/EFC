#!/usr/bin/env python3
"""Demonstration: EFC Introduction to Energy Flow in Space-Time.

Shows:
  1. Energy flow field properties
  2. Entropy field gradients
  3. Flow convergence analysis
  4. Energy conservation check

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from energy_flow_spacetime import (
    EnergyFlowField,
    EntropyField,
    SpacetimeEnergyFlow,
    SPEED_OF_LIGHT,
)


def demo_flow_field():
    """1. Energy flow field properties."""
    print("=" * 60)
    print("1. ENERGY FLOW FIELD PROPERTIES")
    print("=" * 60)

    for R in [0.0, 0.01, 0.1, 1.0]:
        ff = EnergyFlowField(flux_magnitude=1e10, grid_resistance=R)
        print(f"  R = {R:<5}  J_eff = {ff.effective_flux():.3e}  "
              f"p = {ff.momentum_density():.3e} kg m^-2 s^-1  "
              f"v_info = {ff.information_speed():.3e} m/s")


def demo_entropy_field():
    """2. Entropy field gradients."""
    print("\n" + "=" * 60)
    print("2. ENTROPY FIELD GRADIENTS")
    print("=" * 60)

    # Linearly increasing entropy
    linear = EntropyField(values=[1.0, 2.0, 3.0, 4.0, 5.0], spacing=1.0)
    print(f"\n  Linear field: {linear.values}")
    for i in range(1, 4):
        print(f"    grad[{i}] = {linear.gradient_at(i):.3f}")
    print(f"    max |grad| = {linear.max_gradient():.3f}")
    print(f"    total S    = {linear.total_entropy():.3f}")

    # Non-uniform entropy (peak in centre)
    peaked = EntropyField(values=[1.0, 3.0, 8.0, 3.0, 1.0], spacing=1.0)
    print(f"\n  Peaked field: {peaked.values}")
    for i in range(1, 4):
        print(f"    grad[{i}] = {peaked.gradient_at(i):.3f}")
    print(f"    max |grad| = {peaked.max_gradient():.3f}")


def demo_flow_convergence():
    """3. Flow convergence analysis."""
    print("\n" + "=" * 60)
    print("3. FLOW CONVERGENCE ANALYSIS")
    print("=" * 60)

    model = SpacetimeEnergyFlow(grid_resistance=0.01)
    efield = EntropyField(values=[1.0, 2.0, 5.0, 3.0, 1.5], spacing=1.0)

    results = model.flow_convergence(efield, flux_magnitude=1e10)
    print(f"\n  Entropy: {efield.values}")
    print(f"\n  {'Idx':>4}  {'Gradient':>10}  {'Flux':>12}  {'Eff Flux':>12}")
    print("  " + "-" * 42)
    for r in results:
        print(f"  {r['index']:4d}  {r['gradient']:10.3f}  "
              f"{r['local_flux']:12.3e}  {r['effective_flux']:12.3e}")

    delay = model.propagation_delay(1e6)
    print(f"\n  Propagation delay over 1 Mm: {delay:.6f} s")


def demo_conservation():
    """4. Energy conservation check."""
    print("\n" + "=" * 60)
    print("4. ENERGY CONSERVATION CHECK")
    print("=" * 60)

    model = SpacetimeEnergyFlow()

    # Balanced
    check = model.energy_conservation_check(100.0, 70.0, 30.0)
    print(f"\n  Balanced:  in={check['inflow']}  out={check['outflow']}  "
          f"stored={check['stored_change']}  residual={check['residual']}  "
          f"conserved={check['conserved']}")

    # Imbalanced
    check2 = model.energy_conservation_check(100.0, 70.0, 20.0)
    print(f"  Imbalanced: in={check2['inflow']}  out={check2['outflow']}  "
          f"stored={check2['stored_change']}  residual={check2['residual']}  "
          f"conserved={check2['conserved']}")


if __name__ == "__main__":
    print("EFC Introduction to Energy Flow in Space-Time")
    print("Magnusson (2026)")
    print()

    demo_flow_field()
    demo_entropy_field()
    demo_flow_convergence()
    demo_conservation()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
