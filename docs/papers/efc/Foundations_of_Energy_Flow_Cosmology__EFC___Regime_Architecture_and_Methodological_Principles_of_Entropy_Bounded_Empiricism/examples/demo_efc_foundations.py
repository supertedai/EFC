"""
Demo: Foundations of Energy-Flow Cosmology (EFC).

Demonstrates the regime architecture (L0-L3), effective gravitational
coupling equation, regime response surface, and methodological principles.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc_foundations import (
    EFCFoundations,
    EFCParameters,
    EffectiveGravitationalCoupling,
    RegimeLevel,
)


def main():
    print("=" * 60)
    print("Foundations of Energy-Flow Cosmology (EFC) - Demo")
    print("=" * 60)

    # Load reference data
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "efc_foundations_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)

    # 1. Core equations
    print("\n--- Core Equations ---")
    for eq in data["core_equations"]:
        print(f"  {eq['name']}: {eq['formula']}")
        print(f"    {eq['description']}")

    # 2. Initialise framework with reference parameters
    print("\n--- Framework Initialisation ---")
    params = EFCParameters(
        beta=data["core_parameters"]["beta"],
        S_threshold=data["core_parameters"]["S_threshold"],
    )
    efc = EFCFoundations(params=params)
    print(f"  beta = {params.beta}")
    print(f"  S_threshold = {params.S_threshold}")

    # 3. Effective gravitational coupling scan
    print("\n--- Effective Gravitational Coupling mu(S) ---")
    S_values = [0.0, 0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9, 1.0]
    for result in efc.scan_entropy(S_values):
        print(f"  S={result['S']:.2f}  mu={result['mu']:.4f}  regime={result['regime']}")

    # 4. Regime architecture
    print("\n--- Regime Architecture (L0-L3) ---")
    for level, spec in efc.regime_specs.items():
        print(f"  {level.value}: S in {spec.S_range}")
        print(f"    {spec.validity}")

    # 5. Regime Response Surface (small sample)
    print("\n--- Regime Response Surface mu(k, S) ---")
    grid = efc.response_surface_grid(
        k_range=(0.0, 2.0, 3),
        S_range=(0.0, 1.0, 4),
    )
    for point in grid:
        print(f"  k={point['k']:.2f}  S={point['S']:.2f}  mu={point['mu']:.6f}")

    # 6. Methodological principles
    print("\n--- Methodological Principles ---")
    for i, principle in enumerate(efc.METHODOLOGICAL_PRINCIPLES, 1):
        print(f"  {i}. {principle}")

    # 7. Summary
    print("\n--- Framework Summary ---")
    summary = efc.summary()
    print(f"  beta: {summary['beta']}")
    print(f"  Regime levels: {list(summary['regime_levels'].keys())}")
    print(f"  Principles: {len(summary['methodological_principles'])}")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
