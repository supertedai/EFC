#!/usr/bin/env python3
"""
Demo: EFC Observational Evidence for Energy Flow
=================================================
Loads sample data and prints a summary of energy-flow signatures,
CMB anisotropy modes, and galaxy cluster flow properties.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

# Ensure the package src directory is importable
_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.observational_evidence import (
    EnergyFlowSignature,
    CMBAnisotropy,
    GalaxyClusterFlow,
    ObservationalEvidenceAnalyzer,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "observational_evidence.json")
    with open(data_path) as f:
        raw = json.load(f)

    sigs = [EnergyFlowSignature(**s) for s in raw["signatures"]]
    cmb = [CMBAnisotropy(**m) for m in raw["cmb_modes"]]
    clusters = [GalaxyClusterFlow(**c) for c in raw["clusters"]]

    analyzer = ObservationalEvidenceAnalyzer(
        signatures=sigs, cmb_modes=cmb, clusters=clusters
    )

    print("=== EFC Observational Evidence Demo ===\n")

    for s in sigs:
        print(f"  {s.name}: flux={s.energy_flux:.2e} W/m2, "
              f"grad_S={s.entropy_gradient:.3f} kpc^-1, "
              f"d_L={s.luminosity_distance:.1f} Mpc")

    print()
    for m in cmb:
        print(f"  CMB l={m.multipole_l}: dT={m.delta_T:.1f} uK, "
              f"EF frac={m.energy_flow_contribution:.2f}, "
              f"scale~{m.angular_scale_deg:.1f} deg")

    print()
    for c in clusters:
        print(f"  {c.cluster_name}: T={c.temperature_keV} keV, "
              f"S_idx={c.entropy_index:.2f}, "
              f"beta={c.flow_parameter:.6f}")

    print("\n--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
