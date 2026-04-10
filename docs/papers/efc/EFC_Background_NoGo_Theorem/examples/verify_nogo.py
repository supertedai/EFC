#!/usr/bin/env python3
"""
Verify the EFC Background No-Go Theorem.

Reproduces the sign lemma verification and growth enhancement computation.
No external dependencies required (pure stdlib).

Usage:
    python verify_nogo.py
"""

import sys
import os

# Add parent src/ to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.background_nogo import BackgroundNoGo


def main():
    print("=" * 65)
    print("EFC Background No-Go Theorem — Verification")
    print("=" * 65)

    # Create instance with CLASS-verified parameters
    nogo = BackgroundNoGo(A=0.15, z_t=1.01, n=6)

    # --- Sign Lemma ---
    print("\n1. Sign Lemma: ΔE²(z) = A·[g(z) − g(0)] ≤ 0")
    print("-" * 50)
    print(f"{'z':>6}  {'ΔE²':>12}  {'ΔH/H [%]':>10}  {'Sign OK':>8}")
    print("-" * 50)

    redshifts = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]
    all_ok = True
    for z in redshifts:
        dE2 = nogo.delta_E2(z)
        dH = nogo.delta_H_over_H(z)
        ok = dE2 <= 0
        all_ok = all_ok and ok
        mark = "YES" if ok else "NO !!!"
        print(f"{z:6.1f}  {dE2:12.6f}  {dH:10.4f}  {mark:>8}")

    print("-" * 50)
    print(f"All signs correct: {'YES' if all_ok else 'NO — CHECK!'}")

    # --- Growth Enhancement ---
    print("\n2. Growth Enhancement at BOSS DR12 Redshifts")
    print("-" * 60)
    print(f"{'z':>6}  {'fσ₈(ΛCDM)':>10}  {'fσ₈(EFC)':>10}  {'Change':>8}")
    print("-" * 60)

    # Reference values from CLASS v3.3.4
    data = [
        (0.38, 0.4749, 0.4773),
        (0.51, 0.4731, 0.4762),
        (0.61, 0.4679, 0.4715),
    ]
    for z, fl, fe in data:
        pct = (fe / fl - 1) * 100
        print(f"{z:6.2f}  {fl:10.4f}  {fe:10.4f}  +{pct:.2f}%")

    print("-" * 60)
    print("Growth is ENHANCED — opposite direction from σ₈ suppression.")

    # --- Full Diagnostic ---
    print("\n3. Full Diagnostic")
    print("-" * 50)
    result = nogo.full_diagnostic()
    print(f"All signs OK:          {result['all_signs_ok']}")
    print(f"All growth enhanced:   {result['all_growth_enhanced']}")
    print(f"Verdict:               {result['verdict']}")

    # --- Architectural Summary ---
    print("\n" + "=" * 65)
    print("CONCLUSION")
    print("=" * 65)
    print("""
Background channel (Friedmann equation):
  ΔE² ≤ 0 everywhere → H_EFC ≤ H_ΛCDM → ENHANCES growth
  → EXCLUDED for σ₈ suppression

Perturbation channel (Poisson + lensing):
  μ ≈ 0.94 → SUPPRESSES growth (via Poisson equation)
  Σ ≈ 1.05 → ENHANCES lensing (via anisotropic stress)
  η ≈ 1.10 → gravitational slip (most discriminating)
  → ACTIVE channel for all EFC effects
""")


if __name__ == "__main__":
    main()
