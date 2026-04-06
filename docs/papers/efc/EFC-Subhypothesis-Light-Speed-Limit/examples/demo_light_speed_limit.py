#!/usr/bin/env python3
"""
Demo: EFC Subhypothesis -- Light Speed Limit
==============================================
Demonstrates how the speed of light emerges as a thermodynamic
limit from grid resistance and entropy-flow coupling.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.light_speed_limit import (
    GridResistance,
    LightSpeedLimit,
    ThermodynamicSpeedAnalyzer,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "light_speed_limit.json")
    with open(data_path) as f:
        raw = json.load(f)

    regions = [GridResistance(**r) for r in raw["regions"]]
    analyzer = ThermodynamicSpeedAnalyzer(regions=regions)

    print("=== EFC Light Speed Limit Demo ===\n")

    print("Grid Resistance Regions:")
    for r in regions:
        print(f"  R_grid={r.R_grid:.4f}  v_eff={r.effective_speed:.1f} m/s  "
              f"ratio={r.speed_ratio:.6f}")

    print("\nLimit Scenarios:")
    for s in raw["limit_scenarios"]:
        lsl = LightSpeedLimit(**s)
        print(f"  grad_S={lsl.entropy_gradient:.2f}  coupling={lsl.flow_coupling:.2f}  "
              f"R={lsl.R_grid:.2f}  => v_limit={lsl.v_limit:.1f} m/s  "
              f"dev={lsl.deviation_from_c:.6e}")

    print("\nEntropy perturbation example:")
    base = LightSpeedLimit(entropy_gradient=0.0, flow_coupling=1.0, R_grid=1.0)
    perturbed = base.with_entropy_perturbation(0.05)
    print(f"  Base:      v={base.v_limit:.1f} m/s")
    print(f"  Perturbed: v={perturbed.v_limit:.1f} m/s  "
          f"(delta={base.v_limit - perturbed.v_limit:.1f} m/s)")

    print("\n--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
