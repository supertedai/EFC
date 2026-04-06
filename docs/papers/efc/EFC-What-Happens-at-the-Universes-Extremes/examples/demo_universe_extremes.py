#!/usr/bin/env python3
"""
Demo: EFC What Happens at the Universe's Extremes?
====================================================
Explores entropic boundary behaviour near S=0 and S=1,
regime classifications, and information collapse scenarios.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.universe_extremes import (
    EntropicBoundary,
    ExtremeRegime,
    InformationCollapse,
    ExtremesAnalyzer,
)


def main() -> None:
    data_path = os.path.join(_pkg, "data", "universe_extremes.json")
    with open(data_path) as f:
        raw = json.load(f)

    boundaries = [EntropicBoundary(**b) for b in raw["boundaries"]]
    regimes = [ExtremeRegime(**r) for r in raw["regimes"]]
    analyzer = ExtremesAnalyzer(boundaries=boundaries, regimes=regimes)

    print("=== EFC Universe Extremes Demo ===\n")

    print("Entropic Boundaries:")
    for b in boundaries:
        print(f"  S={b.S:.3f}  regime={b.regime:30s}  "
              f"info_cap={b.information_capacity:.4f}  "
              f"v/c={b.propagation_speed_ratio:.3f}")

    print("\nExtreme Regimes:")
    for r in regimes:
        print(f"  {r.name:20s}  S=[{r.S_min:.2f}, {r.S_max:.2f}]  "
              f"suppression={r.flow_suppression:.2f}")
        print(f"    {r.description}")

    print("\nInformation Collapse Scenarios:")
    for cs in raw["collapse_scenarios"]:
        ic = InformationCollapse(**cs)
        print(f"  S={ic.S_current:.2f} -> {ic.S_target:.1f}  "
              f"rate={ic.collapse_rate}  "
              f"t_collapse~{ic.time_to_collapse:.1f} Gyr  "
              f"info_remaining={ic.information_remaining:.4f}")

    print("\n--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
