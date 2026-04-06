#!/usr/bin/env python3
"""
Demo: Regime-Dependent Breakdown of LCDM Across Cosmic Time

Demonstrates:
1. High-z galaxy excess data
2. Statistical test (chi2=47.3, p<1e-8)
3. Behroozi SMHM ratio evolution
4. Halo mass function excess computation
5. Disclaimer verification (scientific caution)
6. Full summary properties
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lcdm_breakdown import (
    HighZExcess,
    StatisticalTest,
    behroozi_smhm_ratio,
    halo_mass_function_excess,
    chi_squared_regime_test,
    HIGH_Z_EXCESS_DATA,
    STATISTICAL_TEST,
    DATA_SOURCES,
    DISCLAIMERS,
    SUMMARY,
)


def demo_high_z_excess():
    """Demo 1: High-z galaxy excess."""
    print("=" * 60)
    print("Demo 1: High-Redshift Galaxy Excess")
    print("=" * 60)

    print(f"  {'z range':>10s} {'vs Behroozi':>13s} {'vs Halo Lim':>13s} {'Significant':>12s}")
    for e in HIGH_Z_EXCESS_DATA:
        print(f"  {e.z_label:>10s} {e.ratio_behroozi:13.0f}x "
              f"{e.ratio_halo_limit:12.1f}x {'Yes' if e.excess_significant else 'No':>12s}")

    # Excess should increase with redshift
    for i in range(len(HIGH_Z_EXCESS_DATA) - 1):
        assert HIGH_Z_EXCESS_DATA[i].ratio_behroozi < HIGH_Z_EXCESS_DATA[i + 1].ratio_behroozi, \
            "Behroozi excess should increase with redshift"

    # All bins at z>7 should be significant against halo limit
    for e in HIGH_Z_EXCESS_DATA:
        if e.z_min >= 7:
            assert e.excess_significant, \
                f"{e.z_label} should be significant"

    print("  PASS: High-z excess increases with redshift\n")


def demo_statistical_test():
    """Demo 2: Chi-squared test for regime clustering."""
    print("=" * 60)
    print("Demo 2: Statistical Significance")
    print("=" * 60)

    st = STATISTICAL_TEST
    print(f"  chi2 = {st.chi2}")
    print(f"  df   = {st.df}")
    print(f"  p    = {st.p_value:.1e}")
    print(f"  Confidence: {st.confidence_percent:.4f}%")
    print(f"  Significant? {st.significant}")

    assert st.chi2 == 47.3
    assert st.df == 4
    assert st.p_value < 1e-8
    assert st.significant
    assert st.confidence_percent > 99.99
    print("  PASS: chi2=47.3, df=4, p<1e-8 confirmed\n")


def demo_behroozi():
    """Demo 3: Behroozi SMHM ratio evolution."""
    print("=" * 60)
    print("Demo 3: Behroozi SMHM Ratio vs Redshift")
    print("=" * 60)

    print(f"  {'z':>5s} {'M*/M_halo':>12s}")
    prev_ratio = 1.0
    for z in [0, 1, 2, 4, 6, 8, 10]:
        ratio = behroozi_smhm_ratio(z)
        print(f"  {z:5d} {ratio:12.6f}")
        if z > 0:
            assert ratio < prev_ratio, "SMHM ratio should decrease with z"
        prev_ratio = ratio

    # At z=0, ratio should be ~2.3%
    r0 = behroozi_smhm_ratio(0.0)
    assert abs(r0 - 0.023) < 0.001
    # At z=10, ratio should be very small
    r10 = behroozi_smhm_ratio(10.0)
    assert r10 < 0.001
    print("  PASS: SMHM ratio declines with redshift\n")


def demo_excess_function():
    """Demo 4: Halo mass function excess computation."""
    print("=" * 60)
    print("Demo 4: Excess Ratio Computation")
    print("=" * 60)

    # Simulate different observed/predicted ratios
    test_cases = [
        (100, 100, 1.0),   # no excess
        (230, 10,  23.0),  # z~5-6 Behroozi
        (529, 1,   529.0), # z~9-10 Behroozi
    ]

    for n_obs, n_pred, expected in test_cases:
        ratio = halo_mass_function_excess(5.0, n_obs, n_pred)
        print(f"  n_obs={n_obs}, n_pred={n_pred} -> ratio={ratio:.1f} (expected {expected})")
        assert abs(ratio - expected) < 0.1

    # Edge case: zero predicted
    ratio_inf = halo_mass_function_excess(5.0, 100, 0)
    assert ratio_inf == float("inf")
    print("  PASS: Excess ratios computed correctly\n")


def demo_disclaimers():
    """Demo 5: Scientific disclaimers."""
    print("=" * 60)
    print("Demo 5: Scientific Disclaimers")
    print("=" * 60)

    for i, d in enumerate(DISCLAIMERS, 1):
        print(f"  {i}. {d}")

    assert len(DISCLAIMERS) == 3
    assert any("NOT falsify" in d for d in DISCLAIMERS)
    assert any("NOT propose" in d for d in DISCLAIMERS)
    assert any("NOT identify" in d for d in DISCLAIMERS)
    print("  PASS: All disclaimers present (scientific caution maintained)\n")


def demo_summary():
    """Demo 6: Full summary properties."""
    print("=" * 60)
    print("Demo 6: Full Summary")
    print("=" * 60)

    s = SUMMARY
    print(f"  Max excess (Behroozi): {s.max_excess_behroozi}x")
    print(f"  Max excess (halo lim): {s.max_excess_halo}x")
    print(f"  Significant bins: {s.n_significant_bins}/{len(s.high_z_excess)}")
    print(f"  Data sources: {len(s.data_sources)}")
    for ds in s.data_sources:
        print(f"    - {ds.name}: {ds.n_objects} objects at {ds.z_range}")

    assert s.max_excess_behroozi == 529.0
    assert s.max_excess_halo == 10.6
    assert s.n_significant_bins >= 3
    assert len(s.data_sources) == 2

    # Total galaxies
    total = sum(ds.n_objects for ds in s.data_sources)
    assert total == 175 + 26288
    print(f"  Total objects: {total}")
    print("  PASS: Summary verified\n")


if __name__ == "__main__":
    demo_high_z_excess()
    demo_statistical_test()
    demo_behroozi()
    demo_excess_function()
    demo_disclaimers()
    demo_summary()
    print("All 6 demos passed.")
