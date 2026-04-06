#!/usr/bin/env python3
"""Demonstration: EFC Mathematical Framework for Energy Flow in Space-Time.

Shows:
  1. Scalar field operations (gradient, Laplacian, integral)
  2. Energy-flow equation dynamics
  3. Entropy production and second law
  4. Gate function profile
  5. Density evolution simulation

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from math_framework import (
    ScalarField,
    EnergyFlowEquation,
    EntropyFieldEquation,
    GateFunction,
    MathFrameworkModel,
)


def demo_scalar_field():
    """1. Scalar field operations."""
    print("=" * 60)
    print("1. SCALAR FIELD OPERATIONS")
    print("=" * 60)

    # Quadratic field: phi = x^2
    vals = [float(i ** 2) for i in range(7)]
    sf = ScalarField(values=vals, dx=1.0, label="x^2")

    grad = sf.gradient()
    lap = sf.laplacian()

    print(f"\n  Field ({sf.label}): {sf.values}")
    print(f"  Gradient:           {[round(g, 3) for g in grad]}")
    print(f"  Laplacian:          {[round(l, 3) for l in lap]}")
    print(f"  Integral:           {sf.integral():.3f}")
    print(f"  L2 norm:            {sf.norm_l2():.3f}")

    # Sinusoidal field
    import math as _m
    sin_vals = [_m.sin(i * 0.5) for i in range(10)]
    sf2 = ScalarField(values=sin_vals, dx=0.5, label="sin(x)")
    print(f"\n  Field ({sf2.label}): {[round(v, 3) for v in sf2.values]}")
    print(f"  Gradient:           {[round(g, 3) for g in sf2.gradient()]}")
    print(f"  Integral:           {sf2.integral():.3f}")


def demo_energy_flow_eq():
    """2. Energy-flow equation dynamics."""
    print("\n" + "=" * 60)
    print("2. ENERGY-FLOW EQUATION")
    print("   d(rho)/dt + div J = -R*rho + Q")
    print("=" * 60)

    for R in [0.01, 0.1, 1.0]:
        eq = EnergyFlowEquation(grid_resistance=R, source_strength=1.0)
        rho_ss = eq.steady_state_density()
        tau = eq.characteristic_time()
        rhs = eq.rhs(rho=rho_ss, div_j=0.0)
        print(f"\n  R = {R}  Q = 1.0:")
        print(f"    rho_ss = {rho_ss:.3f}  tau = {tau:.3f}  rhs(rho_ss) = {rhs:.6f}")


def demo_entropy_production():
    """3. Entropy production and second law."""
    print("\n" + "=" * 60)
    print("3. ENTROPY PRODUCTION")
    print("   sigma = J * |nabla T| / T^2")
    print("=" * 60)

    ent_eq = EntropyFieldEquation()
    cases = [
        (1e10, 100.0, 3000.0),
        (1e10, 10.0, 300.0),
        (1e8, 1.0, 30.0),
    ]

    for J, grad_T, T in cases:
        sigma = ent_eq.production_rate(J, grad_T, T)
        ok = ent_eq.is_second_law_satisfied(sigma)
        print(f"  J={J:.0e}  |nabla T|={grad_T}  T={T}  "
              f"sigma={sigma:.3e}  2nd law: {ok}")


def demo_gate_function():
    """4. Gate function profile."""
    print("\n" + "=" * 60)
    print("4. GATE FUNCTION g(mu) = 1 + alpha*(1 - exp(-mu/mu_0))")
    print("=" * 60)

    model = MathFrameworkModel(gate_alpha=0.1, gate_mu0=1.0)
    mu_vals = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 100.0]
    profile = model.gate_profile(mu_vals)

    print(f"\n  alpha = {model.gate.alpha}  mu_0 = {model.gate.mu_0}")
    print(f"  g(0) = {model.gate.limit_low_mu():.3f}  "
          f"g(inf) = {model.gate.limit_high_mu():.3f}")
    print(f"\n  {'mu':>8}  {'g(mu)':>8}  {'dg/dmu':>10}")
    print("  " + "-" * 30)
    for p in profile:
        print(f"  {p['mu']:8.2f}  {p['g']:8.5f}  {p['dg']:10.6f}")


def demo_density_evolution():
    """5. Density evolution simulation."""
    print("\n" + "=" * 60)
    print("5. DENSITY EVOLUTION (Euler integration)")
    print("=" * 60)

    model = MathFrameworkModel(grid_resistance=0.1)
    model.flow_eq.source_strength = 1.0
    print(f"\n{model.summary()}\n")

    results = model.evolve_density(rho_initial=0.0, div_j=0.0,
                                   n_steps=8, dt=1.0)

    rho_ss = model.flow_eq.steady_state_density()
    print(f"  Expected rho_ss = {rho_ss:.3f}\n")

    print(f"  {'Step':>4}  {'rho':>10}  {'drho/dt':>10}")
    print("  " + "-" * 28)
    for r in results:
        print(f"  {r['step']:4d}  {r['rho']:10.5f}  {r['drho_dt']:10.5f}")


if __name__ == "__main__":
    print("EFC Mathematical Framework for Energy Flow in Space-Time")
    print("Magnusson (2026)")
    print()

    demo_scalar_field()
    demo_energy_flow_eq()
    demo_entropy_production()
    demo_gate_function()
    demo_density_evolution()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
