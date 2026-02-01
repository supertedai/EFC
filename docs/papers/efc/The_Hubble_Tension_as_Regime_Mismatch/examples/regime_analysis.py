#!/usr/bin/env python3
"""
Regime Analysis Example

Demonstrates the regime mismatch interpretation of the Hubble tension.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from regime_classifier import RegimeClassifier, Regime
from g_effective import GEffectiveCalculator, GravityRegime


def main():
    """Run regime analysis demonstration."""

    print("=" * 60)
    print("THE HUBBLE TENSION AS REGIME MISMATCH")
    print("Background Gravity vs Structure Gravity")
    print("=" * 60)
    print()

    # Part 1: Classify probes
    print("PART 1: PROBE CLASSIFICATION")
    print("-" * 40)

    classifier = RegimeClassifier()
    print(classifier.summary())
    print()

    # Part 2: Calculate G_eff
    print("\nPART 2: EFFECTIVE GRAVITATIONAL COUPLING")
    print("-" * 40)

    calc = GEffectiveCalculator(aG=0.094, delta_phi=1.71)
    print(calc.summary())

    # Part 3: Predict H₀ by regime
    print("\nPART 3: H₀ PREDICTION BY REGIME")
    print("-" * 40)

    h0_background = 67.4  # km/s/Mpc (Planck)
    enhancement = calc.enhancement()
    h0_structure = h0_background * (enhancement ** 0.5)  # H² ∝ G

    print(f"Background regime:")
    print(f"  G_eff = G₀")
    print(f"  H₀ = {h0_background:.1f} km/s/Mpc (Planck)")
    print()
    print(f"Structure regime:")
    print(f"  G_eff = G₀ × {enhancement:.4f}")
    print(f"  H₀ = {h0_background:.1f} × √{enhancement:.4f}")
    print(f"     = {h0_background:.1f} × {enhancement**0.5:.4f}")
    print(f"     = {h0_structure:.1f} km/s/Mpc")
    print()
    print(f"Observed (SH0ES): 73.0 km/s/Mpc")
    print(f"Deviation: {abs(h0_structure - 73.0) / 73.0 * 100:.1f}%")

    # Part 4: The key insight
    print("\n" + "=" * 60)
    print("KEY INSIGHT")
    print("=" * 60)
    print("""
The Hubble tension is NOT about H₀ changing over time.

It's about different probes seeing different G:
  • CMB, BAO → Background → G₀ → H₀ ~ 67
  • SNe, Cepheids → Structure → G_eff > G₀ → H₀ ~ 73

This is an EXPECTED signature of regime-dependent gravity,
not a cosmological crisis requiring new physics.
""")

    # Part 5: Falsification
    print("=" * 60)
    print("FALSIFICATION CRITERIA")
    print("=" * 60)
    print("""
This hypothesis can be FALSIFIED if:

1. SNe in voids give SAME H₀ as SNe in clusters
   (should differ by ~8% if hypothesis correct)

2. SN Ia magnitude residuals show NO environmental dependence
   (should show ΔM ~ 0.02 mag between void and cluster)

3. a_G from SPARC rotation curves ≠ 0.1 ± 0.02

Current status: Awaiting environment-dependent analysis
""")


if __name__ == "__main__":
    main()
