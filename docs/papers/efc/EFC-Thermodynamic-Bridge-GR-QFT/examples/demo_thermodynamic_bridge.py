#!/usr/bin/env python3
"""
Demo: EFC Thermodynamic Bridge Between GR and QFT
===================================================
Demonstrates the thermodynamic bridge connecting General Relativity
and Quantum Field Theory through entropy flow.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.thermodynamic_bridge import (
    GRSector,
    QFTSector,
    ThermodynamicBridge,
    BridgeAnalyzer,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "thermodynamic_bridge.json")
    with open(data_path) as f:
        raw = json.load(f)

    bridges = []
    for b in raw["bridges"]:
        gr = GRSector(**b["gr"])
        qft = QFTSector(**b["qft"])
        bridge = ThermodynamicBridge(
            gr=gr, qft=qft, J_bridge=b["J_bridge"], R_grid=b["R_grid"]
        )
        bridges.append(bridge)

    analyzer = BridgeAnalyzer(bridges=bridges)

    print("=== EFC Thermodynamic Bridge Demo ===\n")

    for i, b in enumerate(bridges):
        print(f"Bridge {i + 1}:")
        print(f"  GR:  R_curv={b.gr.curvature_R:.2e}  "
              f"rho={b.gr.energy_density:.2e} J/m3  "
              f"Einstein_src={b.gr.einstein_source:.2e} m^-2")
        print(f"  QFT: omega={b.qft.omega:.2e} rad/s  "
              f"n={b.qft.occupation_n}  "
              f"E_n={b.qft.excitation_energy:.2e} J  "
              f"lambda={b.qft.thermal_wavelength:.2e} m")
        eb = b.energy_balance()
        print(f"  Bridge: flux={eb['bridge_flux']:.2e}  "
              f"coupling={eb['coupling_ratio']:.2f}")
        print()

    print("--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
