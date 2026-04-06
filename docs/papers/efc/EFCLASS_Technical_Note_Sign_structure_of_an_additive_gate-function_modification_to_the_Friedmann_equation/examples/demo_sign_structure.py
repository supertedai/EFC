#!/usr/bin/env python3
"""
Demo: Sign Structure of Gate-Function Modification to Friedmann Equation

Demonstrates the sign lemma, gate function, closure verification,
and growth signature from EFCLASS Technical Note I.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sign_structure import (
    SignStructureAnalysis,
    CosmologicalParameters,
    CLASS_VERIFICATION_DATA,
    GROWTH_SIGNATURE_DATA,
)


def main():
    print("=" * 60)
    print("EFCLASS TECHNICAL NOTE I: SIGN STRUCTURE DEMO")
    print("Gate-Function Modification to the Friedmann Equation")
    print("=" * 60)

    params = CosmologicalParameters()
    analysis = SignStructureAnalysis(params)

    # --- Demo 1: Gate function behaviour ---
    print("\n1. GATE FUNCTION g(z)")
    print("-" * 40)
    print(f"  g(z) = 1 / (1 + (a_t/a)^n)")
    print(f"  a_t = 1/(1+z_t) = {params.a_t:.4f},  n = {params.n}")
    print()

    z_values = [0.0, 0.3, 0.5, 1.0, 1.5, 2.0, 5.0, 10.0, 100.0, 1100.0]
    for z in z_values:
        g = params.gate(z)
        print(f"  z = {z:7.1f}:  g = {g:.6e}")

    assert params.gate(0.0) > 0.9, "g(0) should be near 1"
    assert params.gate(1100.0) < 1e-10, "g(1100) should be suppressed"
    print("  [PASS] Gate activates at late times, suppressed at CMB")

    # --- Demo 2: Sign lemma verification ---
    print("\n2. SIGN LEMMA: Delta E^2 <= 0 for z > 0")
    print("-" * 40)

    verification = analysis.verify_sign_lemma()
    all_ok = True
    for v in verification:
        status = "OK" if v["sign_ok"] else "FAIL"
        if not v["sign_ok"]:
            all_ok = False
        print(f"  z = {v['z']:6.1f}:  Delta E^2 = {v['delta_E2']:+.4e}  [{status}]")

    assert all_ok, "Sign lemma violated!"
    print("  [PASS] Lemma 1 confirmed: Delta E^2 <= 0 everywhere")

    # --- Demo 3: Closure condition ---
    print("\n3. CLOSURE CONDITION: E_EFC(0) = 1")
    print("-" * 40)

    closure = analysis.verify_closure()
    print(f"  E^2_EFC(0) = {closure['E2_efc_at_0']:.12f}")
    print(f"  Omega'_Lambda = {closure['Omega_Lambda_prime']:.6f}")
    print(f"  g(0) = {closure['g_0']:.6f}")
    print(f"  Closure: {'SATISFIED' if closure['closure_satisfied'] else 'FAILED'}")

    assert closure["closure_satisfied"], "Closure condition not satisfied"
    print("  [PASS] Closure condition E_EFC(0) = 1 verified")

    # --- Demo 4: CMB gate suppression ---
    print("\n4. CMB SAFETY: GATE SUPPRESSION AT z=1100")
    print("-" * 40)

    cmb = analysis.gate_suppression_at_cmb()
    print(f"  g(z=1100) = {cmb['g_z1100']:.2e}")
    print(f"  Delta E^2(z=1100) = {cmb['delta_E2_z1100']:.2e}")
    print(f"  Fully suppressed: {cmb['fully_suppressed']}")

    assert cmb["fully_suppressed"], "Gate not suppressed at CMB"
    print("  [PASS] Gate fully suppressed at recombination")

    # --- Demo 5: Growth enhancement (Delta H/H) ---
    print("\n5. GROWTH ENHANCEMENT: Delta H/H")
    print("-" * 40)

    growth = analysis.growth_enhancement()
    print(f"  {'z':>5s}  {'DeltaH/H [%]':>14s}  {'g(z)':>10s}")
    for row in growth:
        print(f"  {row['z']:5.1f}  {row['delta_H_over_H_pct']:+14.4f}  {row['gate_value']:10.6f}")

    # All should be negative (reduced Hubble friction)
    for row in growth:
        assert row["delta_H_over_H_pct"] <= 0, f"Positive DeltaH/H at z={row['z']}"
    print("  [PASS] H_EFC < H_LCDM at all z > 0 (reduced Hubble friction)")

    # --- Demo 6: Comparison with CLASS data ---
    print("\n6. COMPARISON WITH CLASS VERIFICATION DATA")
    print("-" * 40)

    print(f"  {'z':>5s}  {'CLASS DeltaH/H%':>16s}  {'Published':>12s}")
    for pt in CLASS_VERIFICATION_DATA:
        if pt.z > 0:
            print(f"  {pt.z:5.1f}  {pt.delta_H_over_H_pct:16.3f}  "
                  f"{pt.delta_H2_class:12.3e}")

    # Check fsigma8 growth signature
    print()
    print("  f*sigma_8 growth signature (BOSS DR12 redshifts):")
    print(f"  {'z':>5s}  {'LCDM':>8s}  {'EFC':>8s}  {'Change':>8s}")
    for gp in GROWTH_SIGNATURE_DATA:
        print(f"  {gp.z:5.2f}  {gp.fsigma8_LCDM:8.4f}  "
              f"{gp.fsigma8_EFC:8.4f}  {gp.delta_pct:+7.2f}%")
        assert gp.delta_pct > 0, "EFC should enhance growth"

    print("  [PASS] Growth enhanced -- opposite direction from S8 suppression")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(analysis.summary())

    print("\n" + "=" * 60)
    print("ALL DEMOS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
