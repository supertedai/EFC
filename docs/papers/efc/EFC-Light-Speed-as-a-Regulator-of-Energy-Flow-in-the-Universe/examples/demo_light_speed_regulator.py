#!/usr/bin/env python3
"""Demonstration: EFC -- Light Speed as a Regulator of Energy Flow.

Shows:
  1. Propagation regimes and effective speed
  2. Causal horizon computation
  3. Stability analysis of structures
  4. Speed vs. grid resistance table

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from light_speed_regulator import (
    PropagationRegime,
    CausalHorizon,
    StabilityAnalysis,
    LightSpeedRegulatorModel,
    SPEED_OF_LIGHT,
)


def demo_propagation_regimes():
    """1. Propagation regimes."""
    print("=" * 60)
    print("1. PROPAGATION REGIMES")
    print("   v_eff = c / (1 + R)")
    print("=" * 60)

    for R in [0.0, 0.001, 0.01, 0.1, 1.0, 10.0]:
        pr = PropagationRegime(grid_resistance=R)
        print(f"  R = {R:<6}  v_eff = {pr.effective_speed():.6e} m/s  "
              f"ratio = {pr.speed_ratio():.6f}  "
              f"reg = {pr.regulation_strength():.6f}")


def demo_causal_horizon():
    """2. Causal horizon computation."""
    print("\n" + "=" * 60)
    print("2. CAUSAL HORIZON")
    print("   r_H = v_eff * t")
    print("=" * 60)

    for R in [0.0, 0.01, 0.1]:
        pr = PropagationRegime(grid_resistance=R)
        ch = CausalHorizon(regime=pr)
        for t in [1.0, 1e6, 1e10, 4.35e17]:
            r = ch.horizon_radius(t)
            V = ch.horizon_volume(t)
            print(f"  R={R:<5}  t={t:.2e} s  r_H={r:.3e} m  V={V:.3e} m^3")


def demo_stability():
    """3. Stability analysis of structures."""
    print("\n" + "=" * 60)
    print("3. STABILITY ANALYSIS")
    print("   Stable if t_comm < t_dyn")
    print("=" * 60)

    sa = StabilityAnalysis(grid_resistance=0.01)

    structures = [
        ("Atom", 1e-10, 1e-15),
        ("Star", 1e9, 1e15),
        ("Galaxy", 1e21, 1e16),
        ("Galaxy cluster", 1e23, 1e17),
        ("Observable universe", 4.4e26, 4.35e17),
    ]

    print(f"\n  {'Structure':>22s}  {'Size (m)':>10}  {'t_dyn (s)':>10}  "
          f"{'t_comm (s)':>12}  {'Ratio':>8}  {'Stable':>6}")
    print("  " + "-" * 75)

    for name, size, t_dyn in structures:
        t_comm = sa.communication_time(size)
        ratio = sa.stability_ratio(size, t_dyn)
        stable = sa.is_stable(size, t_dyn)
        print(f"  {name:>22s}  {size:10.2e}  {t_dyn:10.2e}  "
              f"{t_comm:12.3e}  {ratio:8.3e}  {str(stable):>6s}")

    L_crit = sa.critical_size(1e16)
    print(f"\n  Critical size for t_dyn = 1e16 s: {L_crit:.3e} m")


def demo_speed_table():
    """4. Speed vs. grid resistance table."""
    print("\n" + "=" * 60)
    print("4. SPEED vs GRID RESISTANCE")
    print("=" * 60)

    model = LightSpeedRegulatorModel(grid_resistance=0.01)
    print(f"\n{model.summary()}\n")

    r_values = [0.0, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
    results = model.speed_vs_resistance(r_values)

    print(f"  {'R':>8}  {'v_eff (m/s)':>14}  {'v/c':>8}  {'Regulation':>10}")
    print("  " + "-" * 45)
    for r in results:
        print(f"  {r['R']:8.3f}  {r['v_eff']:14.6e}  {r['speed_ratio']:8.6f}  "
              f"{r['regulation']:10.6f}")


if __name__ == "__main__":
    print("EFC: Light Speed as a Regulator of Energy Flow in the Universe")
    print("Magnusson (2026)")
    print()

    demo_propagation_regimes()
    demo_causal_horizon()
    demo_stability()
    demo_speed_table()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
