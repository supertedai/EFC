#!/usr/bin/env python3
"""
Demo: EFC-R SPARC Regime Validity
==================================
Loads sample SPARC galaxy data and demonstrates regime-dependent
validity analysis including EFC-R energy decomposition.

Author : Morten Magnusson
ORCID  : 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.sparc_regime import GalaxyRegime, EFCRDecomposition, SPARCAnalyzer


def main() -> None:
    data_path = os.path.join(_pkg, "data", "sparc_regime.json")
    with open(data_path) as f:
        raw = json.load(f)

    galaxies = [GalaxyRegime(**g) for g in raw["galaxies"]]
    analyzer = SPARCAnalyzer(galaxies=galaxies)

    print("=== EFC-R SPARC Regime Validity Demo ===\n")

    for g in galaxies:
        print(f"  {g.name:10s}  morph={g.morphology:18s}  "
              f"chi2_ratio={g.chi2_ratio:.2f}  regime={g.regime_label}")

    print("\n--- EFC-R Energy Decomposition Example (F568-3) ---")
    decomp = EFCRDecomposition(E_total=100.0, alpha=0.95)
    print(f"  E_total={decomp.E_total}, E_flow={decomp.E_flow:.1f}, "
          f"E_latent={decomp.E_latent:.1f}")
    shifted = decomp.regime_transition(0.25)
    print(f"  After regime shift: E_flow={shifted.E_flow:.1f}, "
          f"E_latent={shifted.E_latent:.1f}")

    print("\n--- Summary ---")
    summary = analyzer.summary()
    for k, v in summary.items():
        if isinstance(v, dict):
            print(f"  {k}:")
            for kk, vv in v.items():
                print(f"    {kk}: {vv}")
        else:
            print(f"  {k}: {v}")

    print("\nDone.")


if __name__ == "__main__":
    main()
