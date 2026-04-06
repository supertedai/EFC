#!/usr/bin/env python3
"""
Demo: EFC The Energy-Flow Interface
=====================================
Demonstrates interface layers, field interactions, and boundary
dynamics relaxation within the EFC framework.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.energy_flow_interface import (
    InterfaceLayer,
    FieldInteraction,
    BoundaryDynamics,
    EnergyFlowInterfaceAnalyzer,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "energy_flow_interface.json")
    with open(data_path) as f:
        raw = json.load(f)

    layers = [InterfaceLayer(**l) for l in raw["layers"]]
    analyzer = EnergyFlowInterfaceAnalyzer(layers=layers)

    print("=== EFC Energy-Flow Interface Demo ===\n")

    print("Interface Layers:")
    for l in layers:
        print(f"  {l.name:15s}  dS={l.entropy_jump:+.2f}  "
              f"Phi={l.interface_flux:.4f}  grad={l.gradient_across:.4f} kpc^-1")

    print("\nField Interactions at mid-layer:")
    for l in layers:
        fi = FieldInteraction(
            S_value=0.5 * (l.S_left + l.S_right),
            J_value=l.J_through,
            R_grid=l.R_grid,
        )
        print(f"  {l.name:15s}  SJ={fi.SJ_coupling:.3f}  "
              f"SR={fi.SR_coupling:.3f}  total={fi.total_interaction:.4f}")

    print("\nBoundary relaxation (core-halo, 2 Gyr):")
    bd = BoundaryDynamics(layer=layers[0], relaxation_rate=raw["relaxation_rate"])
    current = layers[0]
    for step in range(4):
        t = step * 0.5
        print(f"  t={t:.1f} Gyr  S_left={current.S_left:.4f}  "
              f"S_right={current.S_right:.4f}  dS={current.entropy_jump:.4f}")
        bd_step = BoundaryDynamics(layer=current, relaxation_rate=raw["relaxation_rate"])
        current = bd_step.evolve(0.5)

    print("\n--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
