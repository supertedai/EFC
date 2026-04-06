#!/usr/bin/env python3
"""Demonstration: EFC Master Specification.

Tests canonical parameters, core equations, regime architecture,
consistency rules, and cognitive layer.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_master_spec import (
    EFCCanonicalParameters, EFCMasterSpec,
    entropy_sigmoid, mu, hubble_ratio_squared,
    master_regimes, consistency_rules,
)


def demo_canonical_parameters():
    """Demo 1: Canonical parameter values."""
    print("=" * 70)
    print("DEMO 1: Canonical Parameters")
    print("=" * 70)
    p = EFCCanonicalParameters()
    d = p.as_dict()
    for key, val in d.items():
        print(f"  {key}: {val}")
    assert p.beta == 0.16
    assert p.a_t == 0.55
    assert p.sigma == 0.10
    assert p.H0 == 67.4
    assert p.Omega_m == 0.315
    assert abs(p.z_t - (1.0 / p.a_t - 1.0)) < 0.01
    print("  [PASSED]\n")


def demo_core_equations():
    """Demo 2: Entropy sigmoid and mu(a)."""
    print("=" * 70)
    print("DEMO 2: Core Equations (S(a), mu(a))")
    print("=" * 70)
    p = EFCCanonicalParameters()
    a_values = [0.01, 0.1, 0.3, 0.55, 0.7, 1.0]
    print(f"  {'a':>6s}  {'S(a)':>8s}  {'mu(a)':>8s}")
    print("  " + "-" * 26)
    for a in a_values:
        print(f"  {a:6.2f}  {entropy_sigmoid(a, p):8.4f}  {mu(a, p):8.4f}")
    # Checks
    assert abs(entropy_sigmoid(0.55, p) - 0.5) < 0.01
    assert entropy_sigmoid(1.0, p) > 0.99
    assert abs(mu(0.01, p) - 1.0) < 0.01
    assert abs(mu(1.0, p) - 1.16) < 0.01
    print("  [PASSED]\n")


def demo_hubble():
    """Demo 3: Modified Friedmann dynamics."""
    print("=" * 70)
    print("DEMO 3: (H/H0)^2 at Various Scale Factors")
    print("=" * 70)
    p = EFCCanonicalParameters()
    a_values = [0.1, 0.3, 0.5, 0.7, 1.0]
    print(f"  {'a':>6s}  {'(H/H0)^2':>12s}")
    print("  " + "-" * 20)
    for a in a_values:
        print(f"  {a:6.2f}  {hubble_ratio_squared(a, p):12.4f}")
    # At a=1, should be close to 1
    h2 = hubble_ratio_squared(1.0, p)
    assert abs(h2 - 1.0) < 0.2, f"(H/H0)^2 at a=1 should be ~1, got {h2}"
    # At early times, radiation dominates -> large
    assert hubble_ratio_squared(0.001, p) > 100
    print("  [PASSED]\n")


def demo_regimes():
    """Demo 4: Regime architecture."""
    print("=" * 70)
    print("DEMO 4: Master Regime Architecture")
    print("=" * 70)
    regimes = master_regimes()
    print(f"  Number of regimes: {len(regimes)}")
    for r in regimes:
        print(f"  {r.label}: {r.name}")
        print(f"    Dominant: {', '.join(r.dominant_fields)}")
        print(f"    Transition: {r.transition_condition}")
    assert len(regimes) == 4
    labels = [r.label for r in regimes]
    assert labels == ["L0", "L1", "L2", "L3"]
    print("  [PASSED]\n")


def demo_consistency_rules():
    """Demo 5: Cross-field consistency rules."""
    print("=" * 70)
    print("DEMO 5: Consistency Rules")
    print("=" * 70)
    rules = consistency_rules()
    print(f"  Number of rules: {len(rules)}")
    for r in rules:
        print(f"  {r.id}: {r.statement}")
    assert len(rules) == 6
    ids = [r.id for r in rules]
    assert "CR1" in ids and "CR6" in ids
    # Verify GR recovery rule exists
    gr_rules = [r for r in rules if "GR" in r.name]
    assert len(gr_rules) >= 1
    print("  [PASSED]\n")


def demo_master_summary():
    """Demo 6: Full master specification summary."""
    print("=" * 70)
    print("DEMO 6: Master Specification Summary")
    print("=" * 70)
    spec = EFCMasterSpec()
    print(spec.summary())
    assert spec.version == "1.0"
    assert spec.regime_count() == 4
    assert spec.rule_count() == 6
    assert spec.entropy_at(0.55) - 0.5 < 0.01
    assert abs(spec.mu_at(1.0) - 1.16) < 0.01
    print("\n  [PASSED]\n")


if __name__ == "__main__":
    demo_canonical_parameters()
    demo_core_equations()
    demo_hubble()
    demo_regimes()
    demo_consistency_rules()
    demo_master_summary()
    print("All demos passed!")
