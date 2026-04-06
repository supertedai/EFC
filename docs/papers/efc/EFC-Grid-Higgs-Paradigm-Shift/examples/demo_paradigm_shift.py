#!/usr/bin/env python3
"""
Grid-Higgs Paradigm Shift Demo

Demonstrates mass and inertia as emergent thermodynamic properties.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from paradigm_shift import ThermodynamicMass, InertiaField, ParadigmShiftModel


def main():
    print("=" * 60)
    print("EFC Grid-Higgs Paradigm Shift Demo")
    print("=" * 60)
    print()

    # Thermodynamic mass
    tm = ThermodynamicMass(lambda_=1.0, gamma=0.3)
    ef = 10.0
    print("Thermodynamic Mass m(S, Ef):")
    for s in [0.0, 1.0, 2.0, 5.0, 10.0]:
        m = tm.mass(s, ef)
        dm = tm.mass_gradient(s, ef)
        print(f"  S={s:5.1f}: m = {m:.4f}, dm/dS = {dm:.4f}")
    print(f"  Saturation mass: {tm.saturation_mass(ef):.4f}")
    print()

    # Inertia field
    inertia = InertiaField(i0=1.0, eta=0.1)
    print("Inertia Field I(S):")
    for s in [0.0, 1.0, 2.0, 5.0, 10.0]:
        print(f"  S={s:5.1f}: I = {inertia.inertia(s):.4f}")
    print()

    # Full model comparison
    model = ParadigmShiftModel(
        lambda_=1.0, gamma=0.3, i0=1.0, eta=0.1, ef_0=10.0
    )
    print(model.summary())
    print()

    # Paradigm comparison table
    s_values = [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 10.0]
    comparison = model.compare_paradigms(s_values)
    print("Paradigm Comparison (classical vs thermodynamic):")
    print(f"  {'S':>6}  {'m_thermo':>10}  {'m_classical':>12}  "
          f"{'ratio':>8}  {'inertia':>8}")
    for c in comparison:
        print(f"  {c['s']:6.2f}  {c['thermo_mass']:10.4f}  "
              f"{c['classical_mass']:12.4f}  {c['mass_ratio']:8.4f}  "
              f"{c['inertia']:8.4f}")
    print()
    print(f"Transition entropy: S_half = {model.transition_entropy():.4f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
