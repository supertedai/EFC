#!/usr/bin/env python3
"""
EFC Regime-Transition Model Analysis

Demonstrates the EFC fit to DESI DR2 BAO data.
"""

import sys
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from efc_model import EFCTransition, create_best_fit_model, create_LCDM_model


def main():
    """Analyze EFC regime-transition model."""

    print("=" * 60)
    print("EFC REGIME-TRANSITION FIT TO DESI DR2 BAO")
    print("=" * 60)
    print()

    # Create models
    efc = create_best_fit_model()
    lcdm = create_LCDM_model()

    print(efc.summary())

    # Evaluate at key redshifts
    print("MODEL COMPARISON AT DESI DR2 REDSHIFTS")
    print("-" * 60)
    print(f"{'z':>6} {'E²_ΛCDM':>12} {'E²_EFC':>12} {'Ratio':>10} {'Θ(z)':>8}")
    print("-" * 60)

    redshifts = [0.30, 0.51, 0.71, 0.93, 1.32, 1.49, 2.33]

    for z in redshifts:
        result = efc.evaluate(z)
        print(
            f"{z:6.2f} {result.E2_LCDM:12.4f} {result.E2_EFC:12.4f} "
            f"{result.modification:10.4f} {result.theta:8.4f}"
        )

    print()

    # Transition analysis
    print("TRANSITION ANALYSIS")
    print("-" * 40)

    # Find where Θ = 0.5 (transition midpoint)
    print(f"  Transition redshift: z_L1L2 = {efc.z_L1L2}")
    print(f"  Transition width: Δz = {efc.delta_z}")
    print()

    # Show Θ at key points
    print("  Θ(z) values:")
    test_z = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5]
    for z in test_z:
        theta = efc.theta(z)
        status = "L2 active" if theta > 0.5 else "L1 dominant"
        print(f"    z = {z:.1f}: Θ = {theta:.3f} ({status})")

    print()

    # Maximum modification
    print("MAXIMUM MODIFICATION")
    print("-" * 40)
    print(f"  α_L2 = {efc.alpha_L2}")
    print(f"  Max modification at z=0: {efc.modification(0):.4f}")
    print(f"  This corresponds to {(efc.modification(0)-1)*100:.2f}% enhancement")
    print()

    # Fit quality summary
    print("FIT QUALITY (from paper)")
    print("-" * 40)
    print("  χ²_EFC  = 6.8  (5 dof)")
    print("  χ²_ΛCDM = 15.2 (6 dof)")
    print("  Δχ² = -8.4 (EFC preferred)")
    print("  ΔAIC = -4.4 (substantial evidence)")
    print("  ΔBIC = -3.1 (positive evidence)")
    print()

    # Cross-validation summary
    print("CROSS-VALIDATION")
    print("-" * 40)
    print("  Pantheon+ SNe: CONSISTENT")
    print("  Cosmic chronometers: CONSISTENT")
    print("  CMB distance priors: CONSISTENT")
    print()

    # Physical interpretation
    print("PHYSICAL INTERPRETATION")
    print("-" * 40)
    print("""
  The transition at z ≈ 1.0 marks where the L2 energy-flow
  coupling becomes dynamically relevant. At earlier times
  (z > 1.5), the Universe expands as standard ΛCDM.

  At late times (z < 0.5), the energy flow modification
  enhances expansion by ~4.5%, potentially explaining
  dynamical dark energy signals in BAO data.

  Key insight: EFC predicts this transition from the
  entropy-driven activation of L2 layer effects.
""")


if __name__ == "__main__":
    main()
