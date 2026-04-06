#!/usr/bin/env python3
"""
Demo: EFC Technical Documentation -- Energy Flow in Space-Time
===============================================================
Loads a 1-D spacetime field, computes entropy gradients and
divergence, then runs a simple forward-Euler integration.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.energy_flow_spacetime import (
    SpacetimePoint,
    EnergyFlowField,
    EFCIntegrator,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "energy_flow_spacetime.json")
    with open(data_path) as f:
        raw = json.load(f)

    points = [SpacetimePoint(**p) for p in raw["points"]]
    efield = EnergyFlowField(points=points)

    print("=== EFC Energy Flow in Space-Time Demo ===\n")

    print("Initial field:")
    for p in points:
        print(f"  x={p.x:.1f} kpc  S={p.S:.2f}  Jx={p.Jx:.2f}  R={p.R_grid:.2f}")

    grads = efield.entropy_gradient()
    divs = efield.divergence_J()
    print("\nEntropy gradient dS/dx and divergence div(J):")
    for i, p in enumerate(points):
        print(f"  x={p.x:.1f}  dS/dx={grads[i]:.4f}  div(J)={divs[i]:.4f}")

    params = raw["integration"]
    integrator = EFCIntegrator(
        field=efield, sigma=params["sigma"], dt=params["dt"]
    )
    history = integrator.run(params["n_steps"])

    print(f"\nIntegration: {params['n_steps']} steps, dt={params['dt']}, "
          f"sigma={params['sigma']}")
    print(f"  Total S: {history[0]:.4f} -> {history[-1]:.4f}")

    print("\nFinal field:")
    for p in points:
        print(f"  x={p.x:.1f} kpc  S={p.S:.4f}  t={p.t:.3f} Gyr")

    print("\nDone.")


if __name__ == "__main__":
    main()
