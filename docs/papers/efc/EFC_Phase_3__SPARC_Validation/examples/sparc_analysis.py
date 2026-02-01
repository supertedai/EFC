#!/usr/bin/env python3
"""
SPARC Analysis Example

Demonstrates the EFC screening model fit to SPARC RAR data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from screening_model import EFCScreening, create_canonical_model


def main():
    """Run SPARC analysis demonstration."""

    print("=" * 60)
    print("EFC PHASE 3: SPARC VALIDATION")
    print("Empirical Test Against the Radial Acceleration Relation")
    print("=" * 60)
    print()

    # Create canonical model
    model = create_canonical_model()
    print(model.summary())
    print()

    # Demonstrate at different acceleration regimes
    print("\nGRAVITATIONAL ENHANCEMENT BY REGIME")
    print("-" * 50)
    print(f"{'g_bar (m/s²)':<15} {'μ':<10} {'ln μ':<10} {'ΔΦ':<10}")
    print("-" * 50)

    g_bar_values = [1e-9, 5e-10, 2.5e-10, 1e-10, 5e-11, 1e-11]

    for g_bar in g_bar_values:
        result = model.compute(g_bar)
        print(f"{g_bar:<15.1e} {result.mu:<10.3f} {result.ln_mu:<10.3f} {result.delta_phi:<10.2f}")

    # Cross-scale consistency check
    print("\n" + "=" * 60)
    print("CROSS-SCALE CONSISTENCY CHECK")
    print("=" * 60)

    k = 0.415
    aG = 0.094
    C = k / aG

    print(f"""
From SPARC fit:
  k = {k} ± 0.029 (screening exponent)
  g† = 2.51 × 10⁻¹⁰ m/s²
  σ_int ≈ 0.14 dex

From H₀ analysis (INDEPENDENT):
  a_G = {aG} ± 0.01 (universal coupling)

Derived:
  C = k / a_G = {k} / {aG} = {C:.1f} ± 0.6

Physical interpretation:
  C ≈ 4.4 is the phase-gain parameter connecting
  galactic and cosmological scales.
""")

    # Phase accumulation comparison
    print("=" * 60)
    print("PHASE ACCUMULATION COMPARISON")
    print("=" * 60)

    delta_phi_cosmo = 1.71  # From H₀ analysis

    print(f"""
Cosmological (H₀ analysis):
  ΔΦ_cosmo ≈ {delta_phi_cosmo} (background → structure)

Galactic (at different positions):
""")

    positions = [
        ("Transition (g_bar = g†)", 2.51e-10),
        ("Outer disk (g_bar = 0.1 g†)", 2.51e-11),
        ("Deep MOND (g_bar = 0.01 g†)", 2.51e-12),
    ]

    for name, g_bar in positions:
        delta_phi_gal = model.phase_accumulation(g_bar)
        ratio = delta_phi_gal / delta_phi_cosmo
        print(f"  {name}:")
        print(f"    ΔΦ_gal = {delta_phi_gal:.1f}")
        print(f"    Ratio ΔΦ_gal/ΔΦ_cosmo = {ratio:.1f}")
        print()

    # Status
    print("=" * 60)
    print("EPISTEMIC STATUS")
    print("=" * 60)
    print("""
This is an EMPIRICAL FIT, not a prediction.

✓ EFC screening form fits SPARC RAR (σ_int ≈ 0.14 dex)
✓ Cross-scale consistency: C = k/a_G = 4.4 ± 0.6
✗ g† and C not yet derived from first principles

For parameter-free prediction:
  → Need to derive g† from Core Lock
  → Need to derive C from phase accumulation theory
""")


if __name__ == "__main__":
    main()
