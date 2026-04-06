#!/usr/bin/env python3
"""
Balance and Universal Structures Demo

Demonstrates how opposing gradients and entropic pressures
produce stable large-scale configurations.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from balance_structures import (
    GradientBalance,
    EquilibriumStructure,
    UniversalStructureModel,
)


def main():
    print("=" * 60)
    print("EFC Balance and Universal Structures Demo")
    print("=" * 60)
    print()

    # Gradient balance
    balance = GradientBalance(grad_s=0.5, ef=10.0, resistance=5.0)
    print("Gradient Balance:")
    print(f"  Driving force: {balance.driving_force():.4f}")
    print(f"  Balance ratio: {balance.balance_ratio():.4f}")
    print(f"  Stable: {balance.is_stable()}")
    print()

    # Single equilibrium structure
    eq = EquilibriumStructure(position=0.0, scale=1.0, entropy=1.2, stability=0.5)
    print("Equilibrium Structure:")
    print(f"  Position: {eq.position}")
    print(f"  Scale: {eq.scale}")
    print(f"  Entropy: {eq.entropy}")
    print(f"  Stable: {eq.is_stable()}")
    print(f"  Binding energy: {eq.binding_energy():.4f}")
    print()

    # Full model
    model = UniversalStructureModel(
        ef_0=10.0, s_background=1.0, resistance_base=5.0, n_scales=5
    )
    print(model.summary())
    print()

    # Find equilibria
    x_values = [i * 0.2 for i in range(100)]
    structures = model.find_equilibria(x_values)
    print(f"Found {len(structures)} equilibrium structures:")
    for s in structures[:10]:
        print(f"  x={s.position:6.2f}, scale={s.scale:.4f}, "
              f"S={s.entropy:.4f}, stable={s.is_stable()}")
    if len(structures) > 10:
        print(f"  ... and {len(structures) - 10} more")
    print()

    # Scale hierarchy
    hierarchy = model.hierarchy_spectrum()
    print("Scale Hierarchy:")
    print(f"  {'Level':>5}  {'Scale':>8}  {'S':>8}  "
          f"{'Stability':>10}  {'E_bind':>8}  {'Stable':>6}")
    for h in hierarchy:
        print(f"  {h['level']:5d}  {h['scale']:8.2f}  "
              f"{h['entropy']:8.4f}  {h['stability']:10.4f}  "
              f"{h['binding_energy']:8.4f}  {str(h['stable']):>6}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
