#!/usr/bin/env python3
"""
Energy-Entropy Interrelation Demo

Demonstrates the unified thermodynamic field model where energy
flow and entropy are interdependent.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from energy_entropy_interrelation import (
    UnifiedField,
    InterrelationCoupling,
    EnergyEntropyModel,
)


def main():
    print("=" * 60)
    print("EFC Energy-Entropy Interrelation Demo")
    print("=" * 60)
    print()

    # Unified field
    field = UnifiedField(ef_0=10.0, s_0=1.0, kappa=0.5)
    print("Unified Field Ef(S):")
    for s in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]:
        ef = field.energy_flow(s)
        sigma = field.entropy_production_rate(s, grad_s=0.3)
        v_info = field.information_bound(s, grad_s=0.3)
        print(f"  S={s:4.1f}: Ef={ef:8.4f}, "
              f"sigma_s={sigma:.4f}, v_info={v_info:.4f}")
    print()

    # Coupling dynamics
    coupling = InterrelationCoupling(kappa=0.5, mu=0.1)
    print("Coupling Dynamics:")
    for s in [0.0, 1.0, 2.0, 5.0]:
        k_eff = coupling.coupling_strength(s)
        fb = coupling.feedback_rate(ef=10.0, grad_s=0.3)
        print(f"  S={s:4.1f}: K_eff={k_eff:.4f}, "
              f"feedback_rate={fb:.4f}")
    s_eq = coupling.equilibrium_entropy(ef=10.0)
    print(f"  Equilibrium entropy: {s_eq:.4f}")
    print()

    # Full model
    model = EnergyEntropyModel(ef_0=10.0, s_0=1.0, kappa=0.5, mu=0.1)
    print(model.summary())
    print()

    # Field profile
    s_values = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]
    profile = model.field_profile(s_values)
    print("Field Profile:")
    print(f"  {'S':>6}  {'Ef':>8}  {'K_eff':>8}  {'S_eq':>8}")
    for p in profile:
        print(f"  {p['s']:6.2f}  {p['ef']:8.4f}  "
              f"{p['coupling']:8.4f}  {p['eq_entropy']:8.4f}")
    print()

    # Time evolution
    history = model.evolve(s_init=1.0, grad_s=0.3, n_steps=20, dt=0.01)
    print("Time Evolution (first 20 steps):")
    print(f"  {'t':>6}  {'S':>8}  {'Ef':>8}")
    for h in history:
        print(f"  {h['t']:6.3f}  {h['s']:8.4f}  {h['ef']:8.4f}")
    print()
    print("Demo completed successfully.")


if __name__ == "__main__":
    main()
