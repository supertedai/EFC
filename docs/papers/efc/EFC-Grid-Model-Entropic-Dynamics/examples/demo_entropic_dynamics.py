#!/usr/bin/env python3
"""
Entropic Dynamics Demo

Demonstrates how structure forms through Grid-S-Ef field interactions.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from entropic_dynamics import GridField, EntropicFlow, EntropicDynamicsModel


def main():
    print("=" * 60)
    print("EFC Grid Model for Entropic Dynamics Demo")
    print("=" * 60)
    print()

    # Grid field
    grid = GridField(g0=1.0, sigma=2.0)
    print("Grid Field G(x):")
    for x in [-4.0, -2.0, 0.0, 2.0, 4.0]:
        print(f"  G({x:5.1f}) = {grid.value(x):.4f}, "
              f"dG/dx = {grid.gradient(x):.4f}")
    print()

    # Entropic flow
    eflow = EntropicFlow(diffusion=1.0, grid=grid)
    grad_s = 0.5
    print(f"Entropic Flow (grad_S = {grad_s}):")
    for x in [-4.0, -2.0, 0.0, 2.0, 4.0]:
        j = eflow.flow(x, grad_s)
        sigma_s = eflow.entropy_production(x, grad_s)
        print(f"  x={x:5.1f}: J = {j:8.4f}, "
              f"sigma_S = {sigma_s:.4f}")
    print()

    # Full model
    model = EntropicDynamicsModel(
        g0=1.0, sigma=2.0, diffusion=1.0, s0=1.0, grad_s=0.5
    )
    print(model.summary())
    print()

    # Dynamics profile
    x_values = [-4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]
    profile = model.dynamics_profile(x_values)
    print("Dynamics Profile:")
    print(f"  {'x':>6}  {'G(x)':>8}  {'S(x)':>8}  "
          f"{'J(x)':>8}  {'sigma_S':>8}")
    for p in profile:
        print(f"  {p['x']:6.2f}  {p['grid']:8.4f}  "
              f"{p['entropy']:8.4f}  {p['flow']:8.4f}  "
              f"{p['production']:8.4f}")
    print()

    # Equilibrium check at x=0
    j, sig = model.equilibrium_condition(0.0)
    print(f"Equilibrium check at x=0: flow = {j:.4f}, "
          f"production = {sig:.4f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
