#!/usr/bin/env python3
"""
Demo: c_eff Parameterization - Compact Demonstrations
======================================================
Demonstrates the core functionality of the EFC c_eff parameterization
with assertions verifying key physical properties.

DOI: 10.6084/m9.figshare.31305421
"""

import sys
import os
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.c_eff import (
    TransitionFunction,
    CEffParameterization,
    DistanceModification,
    CDDRTest,
    DegeneracyBreaker,
    FalsificationCriteria,
)


def demo_1_transition_peak():
    """Demo 1: Transition function peaks at z_peak and is normalized."""
    print("=" * 60)
    print("DEMO 1: Transition Function Peak and Normalization")
    print("=" * 60)

    tf = TransitionFunction(z_peak=0.441, Omega_m=0.3)

    T_peak = tf.T(0.441)
    T_zero = tf.T(0.0)
    T_high = tf.T(5.0)

    print(f"  T(z_peak=0.441) = {T_peak:.6f}")
    print(f"  T(z=0)          = {T_zero:.6f}")
    print(f"  T(z=5)          = {T_high:.6f}")

    # T should be normalized to 1.0 at peak
    assert abs(T_peak - 1.0) < 0.01, f"T(z_peak) should be ~1.0, got {T_peak}"
    # T should be positive everywhere
    assert T_zero > 0, "T(0) must be positive"
    assert T_high > 0, "T(5) must be positive"
    # T should decrease away from peak at high z
    assert T_high < T_peak, "T must decrease at high redshift"
    # T at z=0 should be less than at peak
    assert T_zero < T_peak, "T(0) < T(peak) since peak is at z=0.441"

    print("  [PASS] All transition function assertions passed\n")


def demo_2_c_eff_magnitude():
    """Demo 2: c_eff variation is sub-percent and peaks at z_peak."""
    print("=" * 60)
    print("DEMO 2: c_eff Magnitude and Sub-Percent Variation")
    print("=" * 60)

    ceff = CEffParameterization(beta=0.08, epsilon=0.1)

    dc_peak = ceff.delta_c_over_c(0.441) * 100
    dc_zero = ceff.delta_c_over_c(0.0) * 100
    dc_high = ceff.delta_c_over_c(3.0) * 100

    print(f"  dc/c at z=0.441 (peak): {dc_peak:.4f}%")
    print(f"  dc/c at z=0.0:          {dc_zero:.4f}%")
    print(f"  dc/c at z=3.0:          {dc_high:.4f}%")
    print(f"  c_eff/c_0 at peak:      {ceff.c_eff(0.441):.6f}")

    # Maximum variation should be ~0.8% at peak
    assert 0.5 < dc_peak < 1.0, f"Peak dc/c should be ~0.8%, got {dc_peak:.4f}%"
    # c_eff should exceed c_0
    assert ceff.c_eff(0.441) > 1.0, "c_eff > c_0 at peak"
    # First-order expansion must be valid
    assert ceff.is_valid_expansion(0.441), "Expansion must be valid at peak"
    assert ceff.is_valid_expansion(0.0), "Expansion must be valid at z=0"

    print("  [PASS] All c_eff magnitude assertions passed\n")


def demo_3_numerical_table():
    """Demo 3: Reproduce the numerical table from the paper (Section 2.3)."""
    print("=" * 60)
    print("DEMO 3: Numerical Table Reproduction")
    print("=" * 60)

    ceff = CEffParameterization(beta=0.08, epsilon=0.1)
    table = ceff.table()

    print(f"  {'z':>6s}  {'T(z)':>8s}  {'beta*T':>8s}  {'dc/c %':>10s}  {'c_eff/c_0':>10s}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*10}")
    for row in table:
        print(f"  {row['z']:6.2f}  {row['T_z']:8.3f}  {row['beta_T']:8.4f}  "
              f"{row['dc_over_c_percent']:10.4f}  {row['c_eff_over_c0']:10.6f}")

    # Table should have entries for the standard redshifts
    assert len(table) == 6, f"Expected 6 rows, got {len(table)}"
    # At z=0.44 (near peak), T should be close to 1.0
    row_peak = [r for r in table if abs(r["z"] - 0.44) < 0.01][0]
    assert abs(row_peak["T_z"] - 1.0) < 0.05, "T(z=0.44) should be near 1.0"
    # c_eff/c_0 should always be >= 1.0
    for row in table:
        assert row["c_eff_over_c0"] >= 1.0, f"c_eff/c_0 must be >= 1 at z={row['z']}"

    print("\n  [PASS] All table reproduction assertions passed\n")


def demo_4_distance_shift():
    """Demo 4: Distance modification is small and positive."""
    print("=" * 60)
    print("DEMO 4: Comoving Distance Shift")
    print("=" * 60)

    dm = DistanceModification(
        c_eff_param=CEffParameterization(epsilon=0.1),
        H0=70.0, Omega_m=0.3
    )

    print(f"  {'z':>6s}  {'d_C LCDM':>12s}  {'d_C EFC':>12s}  {'shift':>10s}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*10}")
    for z in [0.5, 1.0, 1.5, 2.0]:
        d_lcdm = dm.comoving_distance_lcdm(z)
        d_efc = dm.comoving_distance(z)
        shift = dm.distance_shift_percent(z)
        print(f"  {z:6.1f}  {d_lcdm:12.1f} Mpc  {d_efc:9.1f} Mpc  {shift:8.4f}%")

    # Shift should be small and positive (c_eff > c_0)
    shift_05 = dm.distance_shift_percent(0.5)
    shift_10 = dm.distance_shift_percent(1.0)
    assert 0 < shift_05 < 1.0, f"Shift at z=0.5 should be small positive, got {shift_05:.4f}%"
    assert 0 < shift_10 < 1.0, f"Shift at z=1.0 should be small positive, got {shift_10:.4f}%"
    # EFC distance should exceed LCDM distance
    assert dm.comoving_distance(1.0) > dm.comoving_distance_lcdm(1.0), \
        "EFC comoving distance must exceed LCDM"

    print("\n  [PASS] All distance shift assertions passed\n")


def demo_5_cddr_cases():
    """Demo 5: CDDR analysis distinguishes metric vs optical-medium cases."""
    print("=" * 60)
    print("DEMO 5: CDDR Case Distinction")
    print("=" * 60)

    cddr = CDDRTest(CEffParameterization(epsilon=0.1))

    print("  Case (i) Metric VSL: eta = 1 identically")
    for z in [0.2, 0.44, 1.0]:
        eta = cddr.eta_metric(z)
        print(f"    z={z:.2f}: eta = {eta:.6f}")
        assert eta == 1.0, "Metric case must have eta = 1 exactly"

    print("\n  Case (ii) Optical-medium: eta varies with z")
    analysis = cddr.sign_change_analysis()
    for r in analysis["values"]:
        print(f"    z={r['z']:.2f}: eta-1 = {r['eta_minus_1']:+.6f}")

    # Case ii should show deviation from 1
    eta_at_peak = cddr.eta_optical_medium(0.44)
    assert eta_at_peak != 1.0, "Optical medium must deviate from eta=1"
    # The deviation at z=0.44 should be positive (T peaks -> c_eff peaks -> eta > 1)
    assert eta_at_peak > 1.0, "eta should be > 1 near peak where c_eff(emit) > c_eff(obs=0)"

    print(f"\n  Sign changes detected: {analysis['n_sign_changes']}")
    print("  [PASS] All CDDR assertions passed\n")


def demo_6_falsification_evaluation():
    """Demo 6: Evaluate falsification criteria."""
    print("=" * 60)
    print("DEMO 6: Falsification Criteria Evaluation")
    print("=" * 60)

    fc = FalsificationCriteria()
    criteria = fc.summary()
    print(f"  Total falsification criteria: {len(criteria)}")
    for c in criteria:
        print(f"    {c['id']}: {c['condition'][:60]}...")

    # Not falsified when condition is not met
    r1 = fc.evaluate("F-ceff-2", condition_met=False)
    assert r1["falsified"] is False, "Should not be falsified when condition not met"

    # Falsified when condition is met
    r2 = fc.evaluate("F-ceff-2", condition_met=True)
    assert r2["falsified"] is True, "Should be falsified when condition met"

    # Check that all 6 criteria are present
    assert len(criteria) == 6, f"Expected 6 falsification criteria, got {len(criteria)}"

    # Verify criterion IDs
    ids = {c["id"] for c in criteria}
    for i in range(1, 7):
        assert f"F-ceff-{i}" in ids, f"Missing criterion F-ceff-{i}"

    print("\n  [PASS] All falsification criteria assertions passed\n")


if __name__ == "__main__":
    print()
    print("c_eff Parameterization - Compact Demo Suite")
    print("DOI: 10.6084/m9.figshare.31305421")
    print()

    demo_1_transition_peak()
    demo_2_c_eff_magnitude()
    demo_3_numerical_table()
    demo_4_distance_shift()
    demo_5_cddr_cases()
    demo_6_falsification_evaluation()

    print("=" * 60)
    print("ALL 6 DEMOS PASSED")
    print("=" * 60)
