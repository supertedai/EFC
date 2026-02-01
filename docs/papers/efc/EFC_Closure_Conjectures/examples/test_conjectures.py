#!/usr/bin/env python3
"""
Test EFC Closure Conjectures

Demonstrates numerical consistency of the proposed relations.
"""

import sys
import math
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from closure_relations import (
    ClosureConjectures,
    compute_g_dagger,
    compute_C,
    predict_h0,
)


def main():
    """Test the closure conjectures."""

    e = math.e

    print("=" * 60)
    print("EFC CLOSURE CONJECTURES")
    print("Proposed Relations: g† = cH₀/e and C = 2e - 1")
    print("=" * 60)
    print()

    # Initialize
    conj = ClosureConjectures(aG=0.094)

    # Test Conjecture 1: g† = cH₀/e
    print("CONJECTURE 1: g† = c × H₀ / e")
    print("-" * 40)

    h0_values = [67.4, 70.2, 73.0]
    labels = ["Planck", "Mean", "SH0ES"]

    for h0, label in zip(h0_values, labels):
        g_dag = compute_g_dagger(h0)
        print(f"  H₀ = {h0} ({label}): g† = {g_dag:.2e} m/s²")

    print(f"\n  SPARC measured: g† = (2.51 ± 0.60) × 10⁻¹⁰ m/s²")
    print()

    # Test Conjecture 2: C = 2e - 1
    print("CONJECTURE 2: C = 2e - 1")
    print("-" * 40)

    C = compute_C()
    C_observed = 4.4
    C_error = 0.6

    print(f"  Conjectured: C = 2×{e:.4f} - 1 = {C:.3f}")
    print(f"  Observed:    C = {C_observed} ± {C_error}")
    print(f"  Difference:  {abs(C - C_observed):.3f} ({abs(C - C_observed)/C_observed*100:.1f}%)")
    print(f"  Status:      {'✓ CONSISTENT' if abs(C - C_observed) < C_error else '✗ INCONSISTENT'}")
    print()

    # Key prediction: H₀ from SPARC
    print("KEY PREDICTION: H₀ = e × g† / c")
    print("-" * 40)

    g_dagger_sparc = 2.51e-10
    g_dagger_error = 0.60e-10

    H0_pred, H0_err = predict_h0(g_dagger_sparc, g_dagger_error)

    print(f"  Using SPARC g† = ({g_dagger_sparc*1e10:.2f} ± {g_dagger_error*1e10:.2f}) × 10⁻¹⁰ m/s²")
    print(f"  H₀ = {H0_pred:.1f} ± {H0_err:.1f} km/s/Mpc")
    print()

    # Comparison with measurements
    print("  Comparison with measurements:")
    measurements = [
        ("Planck (CMB)", 67.4, 0.5),
        ("SH0ES (local)", 73.04, 1.04),
        ("TRGB", 69.8, 1.7),
    ]

    for name, h0, err in measurements:
        diff = abs(H0_pred - h0)
        sigma = diff / math.sqrt(H0_err**2 + err**2)
        status = "✓" if sigma < 2 else "✗"
        print(f"    {name}: {h0} ± {err} → {sigma:.1f}σ {status}")

    print()

    # What remains free
    print("=" * 60)
    print("IRREDUCIBLE PARAMETER")
    print("=" * 60)
    print(f"""
Even with these conjectures, one parameter remains free:

    a_G ≈ 0.094

All other parameters follow:
    k = a_G × C = {conj.aG} × {C:.3f} = {conj.k:.3f}
    ΔΦ_cosmo ≈ e - 1 = {e - 1:.3f}
    a_H₀ = ½ a_G = {conj.aG / 2:.4f}
""")

    # Falsification conditions
    print("=" * 60)
    print("FALSIFICATION CONDITIONS")
    print("=" * 60)
    print("""
These conjectures are FALSIFIED if:

1. Improved g† measurements (with <10% uncertainty)
   are inconsistent with cH₀/e at >3σ

2. Phase factor C deviates from 2e-1 = 4.437
   by more than 20%

3. Alternative f(S) forms (power-law, Lorentzian)
   fit RAR better without natural factors of e

Current status: CONSISTENT (but large uncertainties)
""")


if __name__ == "__main__":
    main()
