#!/usr/bin/env python3
"""Demonstration: EFC Unified Analysis of BAO, SN Ia, and RSD.

DOI: 10.6084/m9.figshare.31215613
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_unified_bao import (
    UnifiedAnalysis, UnifiedAnalysisParameters,
    entropy_field, mu_eff, a_from_z,
    data_sources, lcdm_result, efc_result, delta_chi2,
)


def demo_parameters():
    """Demo 1: EFC analysis parameters."""
    print("=" * 70)
    print("DEMO 1: Unified Analysis Parameters")
    print("=" * 70)
    p = UnifiedAnalysisParameters()
    for key, val in p.as_dict().items():
        print(f"  {key}: {val}")
    assert p.beta == 0.16, "beta should be 0.16"
    assert p.a_t == 0.55
    assert p.gamma == 0.0, "gamma should be 0 (no background modification)"
    assert abs(p.z_t - (1.0 / p.a_t - 1.0)) < 0.02
    print("  [PASSED]\n")


def demo_mu_profile():
    """Demo 2: mu(a) profile across redshifts."""
    print("=" * 70)
    print("DEMO 2: Effective Gravitational Coupling mu(a)")
    print("=" * 70)
    z_values = [99.0, 2.33, 0.82, 0.43, 0.0]
    print(f"  {'z':>6s}  {'a':>6s}  {'S(a)':>8s}  {'mu(a)':>8s}")
    print("  " + "-" * 34)
    for z in z_values:
        a = a_from_z(z)
        S = entropy_field(a)
        m = mu_eff(a)
        print(f"  {z:6.2f}  {a:6.3f}  {S:8.4f}  {m:8.4f}")
    # Early universe: mu ~ 1
    assert abs(mu_eff(a_from_z(99)) - 1.0) < 0.01
    # Today: mu ~ 1.16
    assert abs(mu_eff(1.0) - 1.16) < 0.01
    # Transition: mu ~ 1.08
    assert abs(mu_eff(0.55) - 1.08) < 0.01
    print("  [PASSED]\n")


def demo_data_sources():
    """Demo 3: Data source compilation."""
    print("=" * 70)
    print("DEMO 3: Data Sources")
    print("=" * 70)
    sources = data_sources()
    total = sum(s.N for s in sources)
    for s in sources:
        print(f"  {s.probe}: {s.survey} ({s.N} points, z={s.z_range()})")
    print(f"  Total: {total} data points")
    assert len(sources) == 3
    assert total == 33
    probes = {s.probe for s in sources}
    assert probes == {"BAO", "SN Ia", "RSD"}
    print("  [PASSED]\n")


def demo_chi_squared():
    """Demo 4: Chi-squared comparison."""
    print("=" * 70)
    print("DEMO 4: Chi-Squared Results")
    print("=" * 70)
    lcdm = lcdm_result()
    efc = efc_result()
    print(f"  {lcdm.summary()}")
    print(f"  {efc.summary()}")
    print(f"  Delta chi2 = {delta_chi2():.2f}")
    # Verify published values
    assert abs(lcdm.chi2_total - 49.35) < 0.01
    assert abs(efc.chi2_total - 51.06) < 0.02
    assert abs(delta_chi2() - 1.71) < 0.02
    # BAO and SN should be identical (gamma=0)
    assert lcdm.chi2_BAO == efc.chi2_BAO
    assert lcdm.chi2_SN == efc.chi2_SN
    # RSD is where the difference lies
    assert efc.chi2_RSD > lcdm.chi2_RSD
    print("  [PASSED]\n")


def demo_verdict():
    """Demo 5: Statistical verdict."""
    print("=" * 70)
    print("DEMO 5: Statistical Verdict")
    print("=" * 70)
    ua = UnifiedAnalysis()
    print(f"  Delta chi2 = {ua.delta_chi2():.2f}")
    print(f"  Verdict: {ua.verdict()}")
    # Delta chi2 = 1.71 < 3.84 (95% CL for 1 DOF)
    assert ua.delta_chi2() < 3.84, "Should be within 95% CL"
    assert "Compatible" in ua.verdict()
    print("  [PASSED]\n")


def demo_full_summary():
    """Demo 6: Full unified analysis summary."""
    print("=" * 70)
    print("DEMO 6: Full Analysis Summary")
    print("=" * 70)
    ua = UnifiedAnalysis()
    print(ua.summary())
    assert ua.total_data_points() == 33
    assert abs(ua.mu_at(1.0) - 1.16) < 0.01
    assert ua.entropy_at(1.0) > 0.99
    assert len(ua.findings) == 4
    print("\n  [PASSED]\n")


if __name__ == "__main__":
    demo_parameters()
    demo_mu_profile()
    demo_data_sources()
    demo_chi_squared()
    demo_verdict()
    demo_full_summary()
    print("All demos passed!")
