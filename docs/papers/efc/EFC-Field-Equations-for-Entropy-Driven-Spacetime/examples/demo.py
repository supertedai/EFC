#!/usr/bin/env python3
"""Demo for EFC Field Equations for Entropy-Driven Spacetime package.

Constructs a simple field-equation system, adds components, and
evaluates entropy-flow contributions to spacetime dynamics.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.field_equations import FieldEquationSystem, MetricComponent


def main() -> None:
    fes = FieldEquationSystem(alpha=1e-3, Lambda=1.1e-52)

    # Add diagonal field-equation components (simplified example)
    # (mu, nu, G_mn, T_mn [J/m^3], S_mn [J/(K m^3)])
    fes.add_equation(0, 0, G_mn=-1e-52, T_mn=1e10, S_mn=1e7)
    fes.add_equation(1, 1, G_mn=1e-52, T_mn=5e9, S_mn=5e6)
    fes.add_equation(2, 2, G_mn=1e-52, T_mn=5e9, S_mn=5e6)
    fes.add_equation(3, 3, G_mn=1e-52, T_mn=5e9, S_mn=5e6)

    print(fes.summary())

    # Show metric with entropy corrections
    print("\nDiagonal metric components:")
    for m in fes.metric:
        if m.mu == m.nu:
            print(f"  {m.summary()}")

    print(f"\nkappa = {fes.kappa:.3e} m/J")
    frac = fes.entropy_contribution_fraction()
    if frac is not None:
        print(f"Entropy fraction of RHS: {frac:.4%}")

    print("\nDone.")


if __name__ == "__main__":
    main()
