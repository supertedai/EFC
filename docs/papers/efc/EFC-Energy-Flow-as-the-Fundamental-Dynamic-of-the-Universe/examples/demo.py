#!/usr/bin/env python3
"""Demo for EFC Energy Flow as the Fundamental Dynamic package.

Shows core principles, predictions, and Ef field evaluation.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.fundamental_dynamic import EnergyFlowField, FundamentalDynamics


def main() -> None:
    fd = FundamentalDynamics()

    print(fd.summary())

    # Create and evaluate an Ef field
    ef = EnergyFlowField(ef_x=1e-8, ef_y=2e-8, ef_z=0.5e-8)
    print(f"\n{ef.summary()}")
    print(f"Direction: {ef.direction}")
    print(f"Entropy gradient proxy (T=2.725K): {ef.entropy_gradient_proxy(2.725):.3e}")

    # Evaluate via the framework
    result = fd.evaluate_ef(1e-10, 0, 0, temperature=1e4)
    print(f"\nEf evaluation at T=10^4 K: {result}")

    print("\nDone.")


if __name__ == "__main__":
    main()
