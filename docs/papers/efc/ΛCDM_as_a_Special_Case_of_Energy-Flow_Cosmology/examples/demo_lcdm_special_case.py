#!/usr/bin/env python3
"""
Demonstration script for LCDM as a Special Case of Energy-Flow Cosmology.

Six demos exercising the core classes from lcdm_special_case.py.

DOI: 10.6084/m9.figshare.31943361
License: CC-BY-4.0
"""

import sys
import os
import numpy as np

# Add parent directory to path so we can import the src module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.lcdm_special_case import (
    RegimeDriver,
    ConstitutiveLaw,
    EffectiveCoupling,
    LCDMReduction,
    BackgroundModification,
    DESIDR2Result,
    PerturbationValley,
    GasLawAnalogy,
    KillTestSuite,
    HistoricalFalsifications,
)


def demo_1_lcdm_reduction():
    """Demo 1: LCDM reduction -- verify mu, Sigma, eta -> 1 under limit conditions."""
    print("=" * 70)
    print("Demo 1: LCDM Reduction (Eq. 6)")
    print("  K(rho) -> inf, T(a) -> 0, xi >> 1  ==>  mu, Sigma, eta -> 1")
    print("=" * 70)

    reduction = LCDMReduction(K_rho=1e10, T_a=1e-10, xi=1e4)
    result = reduction.verify_reduction(tol=1e-6)

    print(f"  Suppression factor: {result['suppression']:.2e}")
    print(f"  mu  -> 1: {result['mu_to_1']}")
    print(f"  Sigma -> 1: {result['sigma_to_1']}")
    print(f"  eta -> 1: {result['eta_to_1']}")
    print(f"  All pass: {result['all_pass']}")
    print()

    # Print reduction conditions
    for cond in LCDMReduction.conditions():
        print(f"  {cond['parameter']} -> {cond['limit']}: {cond['meaning']}")
    print()

    # Verify with assertions
    assert result["all_pass"], "LCDM reduction failed"
    assert result["suppression"] < 1e-20, "Suppression factor too large"

    # Also verify that the effective coupling approaches 1 for small chi
    ec = EffectiveCoupling()
    chi_small = 1e-8
    mu_val = ec.mu(chi_small, k=1.0)
    assert abs(mu_val - 1.0) < 1e-6, f"mu should be ~1 for tiny chi, got {mu_val}"
    print(f"  Effective coupling at chi={chi_small}: mu = {mu_val:.10f}")
    print("  [PASS] LCDM reduction verified.\n")


def demo_2_desi_dr2_background():
    """Demo 2: DESI DR2 background -- E^2(a) with alpha, show LCDM consistency."""
    print("=" * 70)
    print("Demo 2: DESI DR2 Background Modification (Eq. 7)")
    print("  E^2(a) = Om*a^-3 + (1-Om) + alpha*[g(a) - g(1)]")
    print("=" * 70)

    # EFC model with DESI DR2 best-fit alpha
    efc = BackgroundModification(Omega_m=0.315, alpha=-0.14)
    # LCDM (alpha = 0)
    lcdm = BackgroundModification(Omega_m=0.315, alpha=0.0)

    a_values = np.linspace(0.2, 1.0, 9)

    print(f"  {'a':>6s}  {'E^2_EFC':>10s}  {'E^2_LCDM':>10s}  {'frac_dev':>12s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*12}")

    for a in a_values:
        e2_efc = efc.E_squared(a)
        e2_lcdm = lcdm.E_squared(a)
        frac = efc.fractional_deviation(a)
        print(f"  {a:6.2f}  {e2_efc:10.4f}  {e2_lcdm:10.4f}  {frac:12.6f}")

    # At a=1 (today), E^2 should be ~1 for LCDM
    e2_today_lcdm = lcdm.E_squared(1.0)
    assert abs(e2_today_lcdm - 1.0) < 1e-10, f"E^2(a=1) for LCDM should be 1, got {e2_today_lcdm}"

    # Fractional deviation should be small (alpha is small)
    max_dev = np.max(np.abs(efc.fractional_deviation(a_values)))
    assert max_dev < 0.05, f"Fractional deviation too large: {max_dev}"
    print(f"\n  Max fractional deviation: {max_dev:.6f}")

    # DESI DR2 result summary
    dr2 = DESIDR2Result()
    assert dr2.is_consistent_with_lcdm(), "alpha should be consistent with LCDM"
    assert dr2.delta_aic == 1.59, "delta_AIC should be +1.59"
    print(f"  alpha = {dr2.alpha} +/- {dr2.alpha_uncertainty} ({dr2.significance_sigma} sigma)")
    print(f"  delta_AIC = {dr2.delta_aic} (LCDM preferred: {dr2.lcdm_preferred})")
    print(f"  Pre-DR2 shift: {dr2.alpha_shift():+.2f}")
    print("  [PASS] DESI DR2 background verified.\n")


def demo_3_perturbation_valley():
    """Demo 3: Perturbation survival valley."""
    print("=" * 70)
    print("Demo 3: Perturbation Survival Valley (Eq. 9)")
    print("  mu in [0.93, 0.96], Sigma in [1.03, 1.07], eta != 1")
    print("=" * 70)

    valley = PerturbationValley()
    summary = valley.summary()

    print(f"  mu range:      {summary['mu_range']}")
    print(f"  mu central:    {summary['mu_central']}")
    print(f"  Sigma range:   {summary['sigma_range']}")
    print(f"  Sigma central: {summary['sigma_central']}")
    print(f"  eta central:   {summary['eta_central']}")
    print(f"  eta != 1:      {summary['eta_neq_1']}")
    print(f"  Central in valley: {summary['central_in_valley']}")

    # Test points
    test_points = [
        (0.94, 1.05, True, "Central values"),
        (0.93, 1.03, True, "Lower bounds"),
        (0.96, 1.07, True, "Upper bounds"),
        (0.90, 1.05, False, "mu too low"),
        (0.94, 1.10, False, "Sigma too high"),
        (1.00, 1.00, False, "LCDM point"),
    ]

    print(f"\n  {'mu':>6s}  {'Sigma':>6s}  {'In valley':>10s}  {'Label':>20s}")
    print(f"  {'-'*6}  {'-'*6}  {'-'*10}  {'-'*20}")
    for mu, sigma, expected, label in test_points:
        result = valley.in_valley(mu, sigma)
        status = "OK" if result == expected else "FAIL"
        print(f"  {mu:6.2f}  {sigma:6.2f}  {str(result):>10s}  {label:>20s}  [{status}]")
        assert result == expected, f"Valley test failed for {label}"

    print("  [PASS] Perturbation valley verified.\n")


def demo_4_gas_law_analogy():
    """Demo 4: Gas-law analogy table."""
    print("=" * 70)
    print("Demo 4: Gas-Law Analogy (Table 5)")
    print("  LCDM:EFC :: Ideal Gas Law:Statistical Mechanics")
    print("=" * 70)

    analogy = GasLawAnalogy()
    table = analogy.get_table()

    print(f"\n  {'Aspect':<25s} {'Thermodynamics':<35s} {'Cosmology':<40s}")
    print(f"  {'-'*25} {'-'*35} {'-'*40}")
    for row in table:
        print(f"  {row['aspect']:<25s} {row['thermodynamics']:<35s} {row['cosmology']:<40s}")

    # Verify table completeness
    assert len(table) == 6, f"Expected 6 rows, got {len(table)}"

    # Verify specific mappings
    reduction = analogy.mapping("Reduction")
    assert reduction is not None, "Reduction mechanism row not found"
    assert "K(rho)" in reduction["cosmology"], "Reduction should mention K(rho)"

    print(f"\n  Central thesis: {analogy.central_thesis()}")
    print("  [PASS] Gas-law analogy verified.\n")


def demo_5_kill_test_summary():
    """Demo 5: Kill-test summary."""
    print("=" * 70)
    print("Demo 5: Kill-Test Suite (Table 3)")
    print("  Five structural integrity tests for Graph-AQUAL")
    print("=" * 70)

    kts = KillTestSuite()
    summary = kts.summary()

    print(f"\n  Total tests: {summary['total']}")
    print(f"  PASS:    {summary['pass']}")
    print(f"  OPEN:    {summary['open']}")
    print(f"  PARTIAL: {summary['partial']}")

    print(f"\n  {'ID':<6s} {'Status':<10s} {'Test':<35s} {'Result'}")
    print(f"  {'-'*6} {'-'*10} {'-'*35} {'-'*40}")
    for test in kts.get_tests():
        print(f"  {test['id']:<6s} {test['status']:<10s} {test['test']:<35s} {test['result']}")

    # Verify counts
    assert summary["total"] == 5, f"Expected 5 tests, got {summary['total']}"
    assert summary["pass"] == 3, f"Expected 3 PASS, got {summary['pass']}"
    assert summary["open"] == 1, f"Expected 1 OPEN, got {summary['open']}"
    assert summary["partial"] == 1, f"Expected 1 PARTIAL, got {summary['partial']}"

    # Verify specific statuses
    assert kts.status("KT1") == "PASS", "KT1 should be PASS"
    assert kts.status("KT2") == "PASS", "KT2 should be PASS"
    assert kts.status("KT3") == "OPEN", "KT3 should be OPEN"
    assert kts.status("KT4") == "PASS", "KT4 should be PASS"
    assert kts.status("KT5") == "PARTIAL", "KT5 should be PARTIAL"

    print("  [PASS] Kill-test summary verified.\n")


def demo_6_historical_falsifications():
    """Demo 6: Historical falsification audit."""
    print("=" * 70)
    print("Demo 6: Historical Falsifications (Table 4)")
    print("  Five documented failures with resolutions")
    print("=" * 70)

    hf = HistoricalFalsifications()
    summary = hf.summary()

    print(f"\n  Documented falsifications: {summary['count']}")
    print(f"  All resolved: {summary['all_resolved']}")

    print(f"\n  {'Element':<30s} {'Failure':<45s} {'Resolution'}")
    print(f"  {'-'*30} {'-'*45} {'-'*40}")
    for f in hf.get_failures():
        print(f"  {f['element']:<30s} {f['failure']:<45s} {f['resolution']}")

    # Verify
    assert summary["count"] == 5, f"Expected 5 falsifications, got {summary['count']}"
    assert summary["all_resolved"], "All falsifications should have resolutions"

    # Verify DESI DR2 result is among the diagnostics
    dr2 = DESIDR2Result()
    collapsed = [k for k, v in dr2.diagnostics.items() if v == "COLLAPSED"]
    assert len(collapsed) == 4, f"Expected 4 COLLAPSED diagnostics, got {len(collapsed)}"
    assert "N1" in collapsed, "N1 should be COLLAPSED"
    assert dr2.diagnostics["N5"] == "PASS", "N5 should be PASS"
    assert dr2.diagnostics["N6"] == "SAFETY_FAIL", "N6 should be SAFETY_FAIL"
    assert dr2.diagnostics["N7"] == "MARGINAL", "N7 should be MARGINAL"
    assert dr2.diagnostics["VG"] == "WEAK", "VG should be WEAK"

    print(f"\n  DESI DR2 diagnostics:")
    for diag_id, verdict in dr2.diagnostics.items():
        print(f"    {diag_id}: {verdict} -- {dr2.diagnostic_details[diag_id]}")

    print("  [PASS] Historical falsification audit verified.\n")


def main():
    """Run all six demos."""
    print()
    print("LCDM as a Special Case of Energy-Flow Cosmology")
    print("Magnusson (2026) -- DOI: 10.6084/m9.figshare.31943361")
    print("=" * 70)
    print()

    demo_1_lcdm_reduction()
    demo_2_desi_dr2_background()
    demo_3_perturbation_valley()
    demo_4_gas_law_analogy()
    demo_5_kill_test_summary()
    demo_6_historical_falsifications()

    print("=" * 70)
    print("All demos passed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
