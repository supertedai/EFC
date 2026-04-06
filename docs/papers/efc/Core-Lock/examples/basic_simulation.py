#!/usr/bin/env python3
"""
Core Lock Basic Simulation Example

Demonstrates the grid state function and beta constraint verification.
"""

import sys
from pathlib import Path

# Add package root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.grid_state_function import GridStateFunction
from src.beta_constraint import BetaConstraint
from src.simulation import CoreLockSimulation, run_verification


def main():
    """Run basic simulation examples."""
    print("=" * 60)
    print("Core Lock Basic Simulation")
    print("=" * 60)
    print()

    # Example 1: Grid State Function
    print("Example 1: Grid State Function")
    print("-" * 40)

    gsf = GridStateFunction(f0=1.0, delta_s=0.5)
    print(gsf.summary())
    print()

    # Evaluate at several points
    print("Evaluation:")
    for s in [0.0, 0.5, 1.0, 1.5, 2.0]:
        f = gsf.evaluate(s)
        print(f"  f({s}) = {f:.4f}")
    print()

    # Example 2: Beta Constraint
    print("Example 2: Beta Constraint")
    print("-" * 40)

    beta = BetaConstraint(delta_s=0.5)
    print(beta.summary())
    print()

    # Verify at a point
    result = beta.verify(s_value=1.0, measured_beta=-2.0, tolerance=0.01)
    print(f"Verification at S=1.0:")
    print(f"  Expected β: {result.expected_beta:.4f}")
    print(f"  Measured β: {result.measured_beta:.4f}")
    print(f"  Passes: {result.passes}")
    print()

    # Example 3: Full Simulation
    print("Example 3: Full Simulation")
    print("-" * 40)

    sim_result = run_verification(
        f0=1.0,
        delta_s=0.5,
        s_range=(0.0, 3.0),
        tolerance=0.01
    )

    print(sim_result.summary)


if __name__ == "__main__":
    main()
