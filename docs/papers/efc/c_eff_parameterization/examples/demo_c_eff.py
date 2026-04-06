#!/usr/bin/env python3
"""
Demo: EFC c_eff Parameterization
===================================
Demonstrates the effective speed of sound parameterization
c_eff(a) = c_0 * [1 + epsilon * beta * T(a)].

DOI: 10.6084/m9.figshare.31305421
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.c_eff import (
    TransitionFunction,
    CEffParameterization,
    DistanceModification,
    CDDRTest,
    DegeneracyBreaker,
    FalsificationCriteria,
)


def demo_transition_function():
    """1. EFC transition function T(z)."""
    print("=" * 65)
    print("DEMO 1: Transition Function T(z)")
    print("=" * 65)

    tf = TransitionFunction(z_peak=0.441)
    info = tf.info()

    print(f"  z_peak  = {info['z_peak']}")
    print(f"  T(peak) = {info['T_at_peak']:.4f}")
    print(f"  T(0)    = {info['T_at_0']:.4f}")
    print(f"  T(1)    = {info['T_at_1']:.4f}")
    print(f"  T(3)    = {info['T_at_3']:.4f}")
    print()

    print(f"  {'z':>6s}  {'T(z)':>8s}")
    print(f"  {'-'*6}  {'-'*8}")
    for z in [0.0, 0.2, 0.44, 0.51, 1.0, 2.0, 3.0, 5.0]:
        print(f"  {z:6.2f}  {tf.T(z):8.4f}")
    print()

    # T should peak at z_peak (normalized to 1.0)
    assert abs(tf.T(0.441) - 1.0) < 0.01, f"T(z_peak) should be ~1.0, got {tf.T(0.441)}"
    # T should decrease at high z
    assert tf.T(3.0) < tf.T(0.441), "T should decrease at z=3"
    # T should be positive
    assert tf.T(0.0) > 0, "T(0) should be positive"
    print("  [PASS] Transition function assertions passed\n")


def demo_c_eff_parameterization():
    """2. c_eff(a) = c_0 * [1 + epsilon * beta * T(a)]."""
    print("=" * 65)
    print("DEMO 2: c_eff Parameterization")
    print("=" * 65)

    # Default: beta=0.08, epsilon=0.1
    ceff = CEffParameterization(beta=0.08, epsilon=0.1)
    info = ceff.info()

    print(f"  beta    = {info['beta']}")
    print(f"  epsilon = {info['epsilon']}")
    print(f"  Max dc/c = {info['max_dc_over_c_percent']:.4f}%")
    print()

    table = ceff.table()
    print(f"  {'z':>6s}  {'T(z)':>8s}  {'beta*T':>8s}  {'dc/c %':>10s}  {'c_eff/c_0':>10s}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*10}")
    for row in table:
        print(f"  {row['z']:6.2f}  {row['T_z']:8.3f}  {row['beta_T']:8.4f}  "
              f"{row['dc_over_c_percent']:10.4f}  {row['c_eff_over_c0']:10.6f}")
    print()

    # c_eff should be > c_0 (since T > 0 and epsilon > 0)
    assert ceff.c_eff(0.44) > 1.0, "c_eff should exceed c_0 at z_peak"
    # Maximum variation should be at z_peak ~ 0.8%
    max_dc = ceff.delta_c_over_c(0.44)
    assert 0.005 < max_dc < 0.01, f"Expected max dc/c ~ 0.8%, got {max_dc*100:.3f}%"
    # Expansion should be valid
    assert ceff.is_valid_expansion(0.44), "Expansion should be valid"
    print("  [PASS] c_eff parameterization assertions passed\n")


def demo_epsilon_comparison():
    """3. Compare epsilon = 0.1 vs epsilon = 0.01."""
    print("=" * 65)
    print("DEMO 3: Epsilon Comparison")
    print("=" * 65)

    ceff_high = CEffParameterization(epsilon=0.1)
    ceff_low = CEffParameterization(epsilon=0.01)

    print(f"  {'z':>6s}  {'dc/c (eps=0.1)':>16s}  {'dc/c (eps=0.01)':>16s}")
    print(f"  {'-'*6}  {'-'*16}  {'-'*16}")
    for z in [0.0, 0.44, 1.0, 2.0]:
        dc_high = ceff_high.delta_c_over_c(z) * 100
        dc_low = ceff_low.delta_c_over_c(z) * 100
        print(f"  {z:6.2f}  {dc_high:16.4f}%  {dc_low:16.4f}%")
    print()

    # Linear in epsilon: ratio should be ~10
    ratio = ceff_high.delta_c_over_c(0.44) / ceff_low.delta_c_over_c(0.44)
    assert abs(ratio - 10.0) < 0.01, f"Expected ratio ~10, got {ratio}"
    print("  [PASS] Epsilon comparison assertions passed\n")


def demo_distance_modification():
    """4. Modified comoving distances."""
    print("=" * 65)
    print("DEMO 4: Distance Modification")
    print("=" * 65)

    dm = DistanceModification(
        c_eff_param=CEffParameterization(epsilon=0.1),
        H0=70.0, Omega_m=0.3
    )

    print(f"  {'z':>6s}  {'d_C (LCDM)':>12s}  {'d_C (EFC)':>12s}  {'shift %':>10s}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*12}  {'-'*10}")
    for z in [0.5, 1.0, 2.0]:
        d_lcdm = dm.comoving_distance_lcdm(z)
        d_efc = dm.comoving_distance(z)
        shift = dm.distance_shift_percent(z)
        print(f"  {z:6.1f}  {d_lcdm:12.1f}  {d_efc:12.1f}  {shift:10.4f}%")
    print()

    # Distance shift should be positive and small
    shift_1 = dm.distance_shift_percent(1.0)
    assert 0 < shift_1 < 1.0, f"Expected small positive shift, got {shift_1:.4f}%"
    print("  [PASS] Distance modification assertions passed\n")


def demo_cddr():
    """5. CDDR analysis for Case i and Case ii."""
    print("=" * 65)
    print("DEMO 5: CDDR Analysis")
    print("=" * 65)

    cddr = CDDRTest(CEffParameterization(epsilon=0.1))

    # Case i: always eta = 1
    print("  Case (i) Metric VSL: eta = 1 always")
    for z in [0.3, 0.44, 0.8]:
        print(f"    z={z}: eta = {cddr.eta_metric(z):.4f}")
    print()

    # Case ii: eta varies
    print("  Case (ii) Optical-medium:")
    analysis = cddr.sign_change_analysis()
    for r in analysis["values"]:
        print(f"    z={r['z']:.2f}: eta = {r['eta']:.6f}, eta-1 = {r['eta_minus_1']:.6f}")
    print()

    # Case i should always be exactly 1
    assert cddr.eta_metric(0.44) == 1.0
    # Case ii should deviate from 1
    eta_peak = cddr.eta_optical_medium(0.44)
    eta_0 = cddr.eta_optical_medium(0.1)
    assert eta_peak != 1.0 or eta_0 != 1.0, "Optical medium should show CDDR deviation"
    print("  [PASS] CDDR assertions passed\n")


def demo_degeneracy_tests():
    """6. Degeneracy-breaking tests."""
    print("=" * 65)
    print("DEMO 6: Degeneracy-Breaking Tests")
    print("=" * 65)

    db = DegeneracyBreaker()

    for name, test in db.info().items():
        print(f"  {test['id']}: {name}")
        print(f"    {test['description']}")
        print(f"    Applies to: {test['applies_to']}")
        print()

    # Beta-split test example
    result = db.beta_split_test(
        beta_distance=0.082, beta_growth=0.078,
        sigma_distance=0.005, sigma_growth=0.005
    )
    print(f"  Beta-split example:")
    print(f"    beta_distance = {result['beta_distance']}")
    print(f"    beta_growth   = {result['beta_growth']}")
    print(f"    significance  = {result['significance_sigma']} sigma")
    print(f"    epsilon != 0? {result['epsilon_nonzero']}")
    print()

    assert result["significance_sigma"] >= 0
    assert isinstance(result["epsilon_nonzero"], bool)
    print("  [PASS] Degeneracy test assertions passed\n")


def demo_falsification():
    """7. Falsification criteria."""
    print("=" * 65)
    print("DEMO 7: Falsification Criteria")
    print("=" * 65)

    fc = FalsificationCriteria()

    for c in fc.summary():
        print(f"  {c['id']}: {c['condition']}")
        print(f"    -> {c['meaning']} ({c['applies_to']})")

    print()

    # Evaluate F-ceff-2: beta agreement to <1%
    r = fc.evaluate("F-ceff-2", condition_met=False)
    assert r["falsified"] is False, "Not falsified if betas differ"

    r2 = fc.evaluate("F-ceff-4", condition_met=False)
    assert r2["falsified"] is False, "No local c variation observed -> not falsified"
    print("  [PASS] Falsification criteria assertions passed\n")


if __name__ == "__main__":
    print()
    print("c_eff Parameterization - EFC Framework Demo")
    print("DOI: 10.6084/m9.figshare.31305421")
    print()

    demo_transition_function()
    demo_c_eff_parameterization()
    demo_epsilon_comparison()
    demo_distance_modification()
    demo_cddr()
    demo_degeneracy_tests()
    demo_falsification()

    print("=" * 65)
    print("ALL DEMOS PASSED")
    print("=" * 65)
