#!/usr/bin/env python3
"""
Demo: EFC CMB Thermodynamic Interpretation
============================================
Demonstrates the CMB compatibility and null-test framework.

DOI: 10.6084/m9.figshare.31064929
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cmb_thermodynamic import (
    EntropyProfile,
    CompatibilityTest,
    NullTest,
    PredictionZone,
    JWSTExcess,
    CMBFramework,
)


def demo_entropy_profile():
    """1. Entropy profile S(z) from JWST constraints."""
    print("=" * 65)
    print("DEMO 1: Entropy Profile S(z)")
    print("=" * 65)

    ep = EntropyProfile(S_0=1.0, alpha_S=0.5, n_S=1.5)
    info = ep.info()
    print(f"  S_0     = {info['S_0']}")
    print(f"  alpha_S = {info['alpha_S']}")
    print(f"  n_S     = {info['n_S']}")
    print(f"  z_peak  = {info['z_peak']:.2f}")
    print()

    print(f"  {'z':>6s}  {'S(z)':>10s}  {'dS/dz':>10s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}")
    for z in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0]:
        print(f"  {z:6.1f}  {ep.S(z):10.4f}  {ep.dS_dz(z):10.4f}")
    print()

    # Assertions
    assert ep.S(0) == 1.0, "S(0) must equal S_0"
    assert ep.z_peak() == 2.0, f"z_peak should be 2.0, got {ep.z_peak()}"
    assert ep.S(ep.z_peak()) > ep.S(0), "S should increase before peak"
    assert ep.S(10) < ep.S(ep.z_peak()), "S should decrease after peak"
    print("  [PASS] Entropy profile assertions passed\n")


def demo_compatibility_tests():
    """2. CMB compatibility tests."""
    print("=" * 65)
    print("DEMO 2: Compatibility Tests")
    print("=" * 65)

    ct = CompatibilityTest()

    # theta_s: Planck 2018 measurement
    r1 = ct.test("theta_s", 100.09, 0.10)
    print(f"  theta_s: observed={r1['observed']}, deviation={r1['deviation_sigma']:.3f} sigma, "
          f"within_tolerance={r1['within_tolerance']}")

    # Peak ratio
    r2 = ct.test("peak_ratio_R", 0.43, 0.03)
    print(f"  R:       observed={r2['observed']}, deviation={r2['deviation_sigma']:.3f} sigma, "
          f"within_tolerance={r2['within_tolerance']}")
    print()

    assert r1["within_tolerance"] is True, "theta_s should pass"
    assert r2["within_tolerance"] is True, "peak_ratio should pass"
    print("  [PASS] Compatibility test assertions passed\n")


def demo_null_tests():
    """3. Falsifiable null tests."""
    print("=" * 65)
    print("DEMO 3: Null Tests")
    print("=" * 65)

    # Peak position: should pass (within 0.5%)
    nt1 = NullTest("peak_position")
    r1 = nt1.evaluate(100.20)
    print(f"  Peak position: obs={r1['observed']}, "
          f"dev={r1['deviation_percent']:.4f}%, falsified={r1['falsified']}")

    # Damping: should pass (within 5%)
    nt2 = NullTest("damping_consistency")
    r2 = nt2.evaluate(1040.0)
    print(f"  Damping:       obs={r2['observed']}, "
          f"dev={r2['deviation_percent']:.4f}%, falsified={r2['falsified']}")

    # Lensing: A_L = 0.93 should pass (< 1.0)
    nt3 = NullTest("lensing_growth")
    r3 = nt3.evaluate(0.93)
    print(f"  Lensing:       A_L={r3['observed_A_L']}, falsified={r3['falsified']}")
    print()

    assert r1["falsified"] is False, "Peak position should not be falsified"
    assert r2["falsified"] is False, "Damping should not be falsified"
    assert r3["falsified"] is False, "Lensing should not be falsified"

    # Test falsification case: A_L = 1.05
    r3_fail = nt3.evaluate(1.05)
    assert r3_fail["falsified"] is True, "A_L=1.05 should falsify"
    print("  [PASS] Null test assertions passed\n")


def demo_prediction_zones():
    """4. Prediction zones."""
    print("=" * 65)
    print("DEMO 4: Prediction Zones")
    print("=" * 65)

    pz_al = PredictionZone("A_L")
    r1 = pz_al.check(0.93)
    print(f"  A_L: observed={r1['observed']}, range={r1['predicted_range']}, "
          f"matches={r1['matches_efc']}")

    pz_isw = PredictionZone("ISW_phase")
    r2 = pz_isw.check(0.05)
    print(f"  ISW phase: observed={r2['observed_rad']} rad, "
          f"range={r2['predicted_range_rad']}, matches={r2['matches_efc']}")
    print()

    assert r1["matches_efc"] is True, "A_L=0.93 should match"
    assert r2["matches_efc"] is True, "ISW phase=0.05 should match"
    print("  [PASS] Prediction zone assertions passed\n")


def demo_jwst_excess():
    """5. JWST galaxy excess analysis."""
    print("=" * 65)
    print("DEMO 5: JWST/COSMOS-Web Galaxy Excess")
    print("=" * 65)

    jwst = JWSTExcess()
    summary = jwst.summary()

    print(f"  chi2 = {summary['chi2']}, df = {summary['df']}")
    print(f"  Max excess vs LCDM: {summary['max_excess_vs_lcdm']}x")
    print()

    print(f"  {'z bin':>6s}  {'vs LCDM':>10s}  {'vs Halo':>10s}  {'Status'}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*30}")
    for b in summary["bins"]:
        print(f"  {b['z_bin']:>6s}  {b['ratio_vs_lcdm']:10.0f}  "
              f"{b['ratio_vs_halo']:10.1f}  {b['status']}")
    print()

    assert summary["chi2"] == 47.3
    assert summary["max_excess_vs_lcdm"] == 529.0
    assert len(summary["bins"]) == 4
    print("  [PASS] JWST excess assertions passed\n")


def demo_full_framework():
    """6. Complete CMB framework."""
    print("=" * 65)
    print("DEMO 6: Full CMB Framework")
    print("=" * 65)

    fw = CMBFramework()
    report = fw.full_report(theta_s_obs=100.12, lD_obs=1045.0, A_L_obs=0.93)

    nt = report["null_tests"]
    print(f"  Framework status: {nt['framework_status']}")
    print(f"  Any falsified: {nt['any_falsified']}")
    for name, result in nt["tests"].items():
        print(f"    {name}: falsified={result['falsified']}")
    print()

    assert nt["framework_status"] == "consistent"
    assert nt["any_falsified"] is False
    print("  [PASS] Full framework assertions passed\n")


if __name__ == "__main__":
    print()
    print("CMB Thermodynamic Interpretation - EFC Framework Demo")
    print("DOI: 10.6084/m9.figshare.31064929")
    print()

    demo_entropy_profile()
    demo_compatibility_tests()
    demo_null_tests()
    demo_prediction_zones()
    demo_jwst_excess()
    demo_full_framework()

    print("=" * 65)
    print("ALL DEMOS PASSED")
    print("=" * 65)
