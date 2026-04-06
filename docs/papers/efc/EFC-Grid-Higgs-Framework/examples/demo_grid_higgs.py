#!/usr/bin/env python3
"""
Grid-Higgs Framework Demo

Demonstrates mass emergence from grid resistance and entropy gradients.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from grid_higgs import GridResistance, EffectiveMass, GridHiggsModel


def main():
    print("=" * 60)
    print("EFC Grid-Higgs Framework Demo")
    print("=" * 60)
    print()

    # Grid resistance
    resistance = GridResistance(r0=1.0, alpha=0.5)
    print("Grid Resistance R(S) = R0 * (1 + alpha * S):")
    for s in [0.0, 1.0, 2.0, 3.0]:
        print(f"  R({s}) = {resistance.resistance(s):.4f}")
    print()

    # Effective mass
    eff_mass = EffectiveMass(kappa=1.0, resistance=resistance)
    ef = 10.0
    print(f"Effective Mass (Ef = {ef}):")
    for s in [0.0, 1.0, 2.0, 3.0]:
        m = eff_mass.mass(s, ef)
        inertia = eff_mass.inertia(s, ef)
        print(f"  S={s}: m_eff = {m:.4f}, inertia = {inertia:.4f}")
    print()

    # Full model
    model = GridHiggsModel(r0=1.0, alpha=0.5, kappa=1.0, ef_0=10.0)
    print(model.summary())
    print()

    # Mass spectrum
    s_values = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    spectrum = model.mass_spectrum(s_values)
    print("Mass Spectrum:")
    print(f"  {'S':>6}  {'R(S)':>8}  {'m_eff':>8}  {'inertia':>8}")
    for p in spectrum:
        print(f"  {p['s']:6.2f}  {p['resistance']:8.4f}  "
              f"{p['mass']:8.4f}  {p['inertia']:8.4f}")
    print()
    print(f"Critical entropy (mass doubling): S_c = {model.critical_entropy():.4f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
