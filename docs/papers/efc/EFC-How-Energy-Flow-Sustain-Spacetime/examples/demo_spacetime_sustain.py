#!/usr/bin/env python3
"""
Spacetime Sustain Demo

Demonstrates how continuous energy flow maintains spacetime
structure and stability within the EFC framework.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from spacetime_sustain import (
    EnergyFlowNetwork,
    SpacetimeStability,
    SpacetimeSustainModel,
)


def main():
    print("=" * 60)
    print("EFC Spacetime Sustain Demo")
    print("=" * 60)
    print()

    # Energy flow network
    network = EnergyFlowNetwork(ef_0=10.0, r_c=1.0, n_nodes=10)
    print("Energy Flow Network:")
    for r in [0.0, 0.5, 1.0, 2.0, 5.0, 10.0]:
        print(f"  Ef({r:5.1f}) = {network.flow_density(r):.4f}")
    total = network.total_flow(r_max=10.0)
    print(f"  Total flow (r<10): {total:.4f}")
    print()

    # Stability criterion
    stability = SpacetimeStability(r_threshold=1.0)
    print("Stability Criterion (Ef * grad_S >= R_threshold):")
    test_cases = [(10.0, 0.5), (5.0, 0.3), (1.0, 0.5), (0.5, 0.1)]
    for ef, gs in test_cases:
        sigma = stability.stability_parameter(ef, gs)
        stable = stability.is_stable(ef, gs)
        print(f"  Ef={ef:5.1f}, grad_S={gs:.1f}: "
              f"sigma={sigma:.4f}, stable={stable}")
    print()

    # Full model
    model = SpacetimeSustainModel(
        ef_0=10.0, r_c=1.0, n_nodes=10,
        r_threshold=1.0, grad_s_0=0.5
    )
    print(model.summary())
    print()

    # Stability profile
    r_values = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0]
    profile = model.stability_profile(r_values)
    print("Stability Profile:")
    print(f"  {'r':>6}  {'Ef':>8}  {'grad_S':>8}  "
          f"{'sigma':>8}  {'stable':>6}")
    for p in profile:
        print(f"  {p['r']:6.2f}  {p['flow']:8.4f}  "
              f"{p['grad_s']:8.4f}  {p['stability_param']:8.4f}  "
              f"{str(p['is_stable']):>6}")
    print()

    horizon = model.find_stability_horizon()
    print(f"Stability horizon: r ~ {horizon:.2f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
