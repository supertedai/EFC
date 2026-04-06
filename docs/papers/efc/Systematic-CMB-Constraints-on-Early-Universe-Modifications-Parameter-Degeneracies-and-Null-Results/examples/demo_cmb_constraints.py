#!/usr/bin/env python3
"""
Demo: Systematic CMB Constraints on EFC

Demonstrates:
1. Kappa-dot mechanism test (REJECTED)
2. H(z) mechanism: 1D artifact vs 2D truth
3. Kappa-dot modification function
4. H(z) energy injection profile
5. Regime interpretation
6. Full summary verification
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cmb_constraints import (
    KappaDotResult,
    HzSweepResult,
    RegimeInterpretation,
    CMBConstraintsSummary,
    kappa_dot_modification,
    hz_energy_injection,
    KAPPA_DOT_RESULTS,
    HZ_RESULT,
    CMB_DATA,
    REGIME,
    SUMMARY,
)


def demo_kappa_dot():
    """Demo 1: Kappa-dot mechanism is REJECTED."""
    print("=" * 60)
    print("Demo 1: Kappa-Dot Mechanism Test")
    print("=" * 60)

    print(f"  {'Boost %':>8s} {'chi2/dof':>10s} {'delta_chi2':>11s} {'Status':>10s}")
    for r in KAPPA_DOT_RESULTS:
        status = "MINIMUM" if r.boost_percent == 0 else "Worse"
        print(f"  {r.boost_percent:8.1f} {r.chi2_per_dof:10.4f} "
              f"{r.delta_chi2:11.1f} {status:>10s}")

    # boost=0 should be the minimum
    min_result = min(KAPPA_DOT_RESULTS, key=lambda x: x.delta_chi2)
    assert min_result.boost_percent == 0.0, "Minimum should be at boost=0"
    assert min_result.delta_chi2 == 0.0

    # All non-zero boosts should worsen fit
    for r in KAPPA_DOT_RESULTS:
        if r.boost_percent != 0:
            assert r.delta_chi2 > 0, f"boost={r.boost_percent}% should worsen fit"

    print("  PASS: kappa-dot mechanism REJECTED -- boost=0 is minimum\n")


def demo_hz_artifact():
    """Demo 2: H(z) 1D artifact vs 2D truth."""
    print("=" * 60)
    print("Demo 2: H(z) Mechanism -- 1D Artifact vs 2D Truth")
    print("=" * 60)

    hz = HZ_RESULT
    print(f"  1D artifact: epsilon={hz.epsilon_1d_artifact}%, "
          f"delta_chi2={hz.delta_chi2_1d_artifact}")
    print(f"  2D true min: epsilon={hz.epsilon_true_min}%, "
          f"h={hz.h_true_min}, delta_chi2={hz.delta_chi2_true_min}")
    print(f"  Status: {hz.status}")
    print(f"  Is artifact? {hz.is_artifact}")

    assert hz.status == "REJECTED"
    assert hz.is_artifact
    # True minimum is much less significant than 1D artifact
    assert abs(hz.delta_chi2_true_min) < abs(hz.delta_chi2_1d_artifact)
    assert abs(hz.delta_chi2_true_min) < 2.0, \
        "True delta_chi2 should be negligible"
    print("  PASS: 1D 'signal' confirmed as degeneracy artifact\n")


def demo_kappa_dot_function():
    """Demo 3: Kappa-dot modification function."""
    print("=" * 60)
    print("Demo 3: Kappa-Dot Modification Function")
    print("=" * 60)

    boost = 0.01  # 1%
    print(f"  Boost = {boost*100}%")
    print(f"  {'z':>8s} {'Modification factor':>20s}")
    for z in [100, 300, 500, 700, 900, 1100, 1500]:
        factor = kappa_dot_modification(z, boost)
        print(f"  {z:8d} {factor:20.6f}")

    # At z=700 (center), tanh(0)=0, so factor should be 1.0
    assert abs(kappa_dot_modification(700, boost) - 1.0) < 1e-10
    # At z >> 700, factor should approach 1 + boost
    assert abs(kappa_dot_modification(2000, boost) - 1.01) < 0.001
    # At z << 700, factor should approach 1 - boost
    assert abs(kappa_dot_modification(0, boost) - 0.99) < 0.001
    print("  PASS: Kappa-dot function correct\n")


def demo_hz_injection():
    """Demo 4: H(z) energy injection profile."""
    print("=" * 60)
    print("Demo 4: H(z) Energy Injection Profile")
    print("=" * 60)

    epsilon = 0.03  # 3%
    a_t = 1.0 / 1100.0  # recombination
    delta = 5e-5

    print(f"  epsilon = {epsilon*100}%, a_t = {a_t:.6f}, delta = {delta}")
    print(f"  {'a':>12s} {'z':>8s} {'injection':>12s}")
    for z in [1200, 1150, 1100, 1050, 1000, 500, 0]:
        a = 1.0 / (1.0 + z)
        inj = hz_energy_injection(a, epsilon, a_t, delta)
        print(f"  {a:12.6f} {z:8d} {inj:12.6f}")

    # Peak should be at a_t
    peak = hz_energy_injection(a_t, epsilon, a_t, delta)
    assert abs(peak - epsilon) < 1e-10, "Peak should equal epsilon"

    # Far from recombination, injection should be negligible
    inj_far = hz_energy_injection(0.5, epsilon, a_t, delta)
    assert inj_far < 1e-100, "Injection far from a_t should be ~0"
    print("  PASS: Energy injection profile correct\n")


def demo_regime():
    """Demo 5: Regime interpretation."""
    print("=" * 60)
    print("Demo 5: Regime Interpretation")
    print("=" * 60)

    r = REGIME
    print(f"  {r.describe()}")

    assert r.cmb_epoch == "L0-L1"
    assert "Standard" in r.expected_physics or "LCDM" in r.expected_physics
    assert "Consistent" in r.implication
    print("  PASS: Regime interpretation correct\n")


def demo_full_summary():
    """Demo 6: Full summary verification."""
    print("=" * 60)
    print("Demo 6: Full Constraint Summary")
    print("=" * 60)

    s = SUMMARY
    print(f"  kappa-dot: {s.kappa_dot_status}")
    print(f"  H(z):      {s.hz_status}")
    print(f"  Both rejected? {s.both_rejected}")
    print(f"  Lesson: {s.key_lesson}")

    assert s.both_rejected
    assert "degenerac" in s.key_lesson.lower()
    assert len(s.kappa_dot_results) == 5
    assert s.hz_result.status == "REJECTED"

    # CMB data check
    assert CMB_DATA.n_points == 2507
    assert CMB_DATA.ell_min == 2
    assert CMB_DATA.ell_max == 2508
    print("  PASS: Full summary verified\n")


if __name__ == "__main__":
    demo_kappa_dot()
    demo_hz_artifact()
    demo_kappa_dot_function()
    demo_hz_injection()
    demo_regime()
    demo_full_summary()
    print("All 6 demos passed.")
