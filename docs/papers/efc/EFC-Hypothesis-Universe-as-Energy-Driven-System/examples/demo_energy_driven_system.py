#!/usr/bin/env python3
"""Demonstration: EFC Hypothesis -- Universe as an Energy-Driven System.

Shows:
  1. Grid field properties and damping
  2. Entropy gradient driving forces
  3. Energy flow and structure formation potential
  4. Simplified cosmic timeline evolution

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from energy_driven_system import (
    GridField,
    EntropyGradient,
    EnergyFlow,
    EnergyDrivenUniverse,
)


def demo_grid_field():
    """1. Grid field properties."""
    print("=" * 60)
    print("1. GRID FIELD PROPERTIES")
    print("=" * 60)

    for R in [0.001, 0.01, 0.1, 1.0]:
        gf = GridField(resistance=R)
        v = gf.effective_propagation_speed()
        rho = gf.grid_energy_density(3000.0)
        d = gf.damping_factor(rho)
        print(f"  R = {R:<6}  v_eff = {v:.3e} m/s  "
              f"rho(3000K) = {rho:.3e} J/m^3  D = {d:.6f}")


def demo_entropy_gradient():
    """2. Entropy gradient driving forces."""
    print("\n" + "=" * 60)
    print("2. ENTROPY GRADIENT DRIVING FORCES")
    print("=" * 60)

    for grad_mag in [1e-6, 1e-5, 1e-4]:
        eg = EntropyGradient(gradient_magnitude=grad_mag)
        for T in [300.0, 3000.0, 3e6]:
            F = eg.driving_force(T)
            sigma = eg.entropy_production_rate(1e10, T)
            print(f"  |nabla S| = {grad_mag:.0e}  T = {T:.0e} K  "
                  f"F = {F:.3e}  sigma = {sigma:.3e}")


def demo_energy_flow():
    """3. Energy flow and structure potential."""
    print("\n" + "=" * 60)
    print("3. ENERGY FLOW AND STRUCTURE POTENTIAL")
    print("=" * 60)

    for R in [0.001, 0.01, 0.1]:
        ef = EnergyFlow(
            flux=1e10,
            entropy_gradient=EntropyGradient(gradient_magnitude=1e-5),
            grid=GridField(resistance=R),
        )
        T = 3000.0
        j_net = ef.net_flow_rate(T)
        phi = ef.structure_formation_potential(T)
        budget = ef.energy_budget(T, 1.0)
        print(f"\n  R = {R}:")
        print(f"    J_net = {j_net:.6e} J m^-2 s^-1")
        print(f"    Phi   = {phi:.6e}")
        print(f"    Budget: kinetic={budget['kinetic_fraction']:.3e}  "
              f"grid={budget['grid_stored_fraction']:.3e}")


def demo_cosmic_timeline():
    """4. Simplified cosmic timeline."""
    print("\n" + "=" * 60)
    print("4. COSMIC TIMELINE (simplified)")
    print("=" * 60)

    universe = EnergyDrivenUniverse(
        grid_resistance=0.01,
        entropy_gradient_mag=1e-5,
        energy_flux=1e10,
    )

    print(f"\n{universe.summary()}\n")

    timeline = universe.cosmic_timeline(
        t_start=0.0, t_end=1e10, n_steps=5, t_initial=3000.0,
    )

    print(f"  {'Step':>4}  {'Time':>12}  {'Temp (K)':>10}  "
          f"{'J_net':>12}  {'Sigma*dt':>12}  {'Phi':>12}")
    print("  " + "-" * 70)

    for i, s in enumerate(timeline):
        print(f"  {i:4d}  {s['time']:12.3e}  {s['temperature']:10.2f}  "
              f"{s['net_flow_rate']:12.3e}  {s['entropy_production']:12.3e}  "
              f"{s['structure_potential']:12.3e}")


if __name__ == "__main__":
    print("EFC Hypothesis: Universe as an Energy-Driven System")
    print("Magnusson (2026)")
    print()

    demo_grid_field()
    demo_entropy_gradient()
    demo_energy_flow()
    demo_cosmic_timeline()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
