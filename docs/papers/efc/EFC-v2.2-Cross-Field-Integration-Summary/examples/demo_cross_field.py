#!/usr/bin/env python3
"""Demonstration: EFC v2.2 Cross-Field Integration Summary.

Tests field couplings, integration levels, coupling matrix,
and cross-field consistency.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_cross_field import (
    FieldCoupling, CrossFieldIntegration, CouplingMatrix,
    canonical_couplings, integration_levels, entropy_energy_consistency,
    FIELD_NAMES,
)


def demo_field_couplings():
    """Demo 1: Six pairwise field couplings."""
    print("=" * 70)
    print("DEMO 1: Canonical Field Couplings")
    print("=" * 70)
    couplings = canonical_couplings()
    print(f"  Number of couplings: {len(couplings)}")
    for c in couplings:
        print(f"  - {c.label()} [{c.coupling_type}]")
    assert len(couplings) == 6, "Expected 6 pairwise couplings for 4 fields"
    types = {c.coupling_type for c in couplings}
    assert "direct" in types
    assert "mediated" in types
    assert "emergent" in types
    # Energy-Entropy coupling should have beta=0.16
    ee = [c for c in couplings if "Energy" in c.field_a and "Entropy" in c.field_b][0]
    assert ee.strength == 0.16
    print("  [PASSED]\n")


def demo_integration_levels():
    """Demo 2: Multi-level integration hierarchy."""
    print("=" * 70)
    print("DEMO 2: Integration Levels (Micro -> Global)")
    print("=" * 70)
    levels = integration_levels()
    print(f"  Number of levels: {len(levels)}")
    for lv in levels:
        print(f"  - {lv.level}: {lv.name} ({lv.coupling_direction})")
    assert len(levels) == 4
    level_names = [lv.level for lv in levels]
    assert level_names == ["Micro", "Meso", "Macro", "Global"]
    print("  [PASSED]\n")


def demo_coupling_matrix():
    """Demo 3: Coupling matrix is fully connected."""
    print("=" * 70)
    print("DEMO 3: Coupling Matrix")
    print("=" * 70)
    cm = CouplingMatrix()
    mat = cm.matrix()
    print(f"  Fields: {FIELD_NAMES}")
    print(f"  Active couplings: {cm.active_couplings()}")
    print(f"  Fully connected: {cm.is_fully_connected()}")
    # Diagonal should be zero (no self-coupling)
    for f in FIELD_NAMES:
        assert mat[(f, f)] == 0.0, f"Self-coupling should be 0 for {f}"
    # Off-diagonal should all be active
    assert cm.is_fully_connected(), "All field pairs should be coupled"
    assert cm.active_couplings() == 6
    print("  [PASSED]\n")


def demo_entropy_energy_consistency():
    """Demo 4: Cross-field consistency check for entropy-energy coupling."""
    print("=" * 70)
    print("DEMO 4: Entropy-Energy Consistency")
    print("=" * 70)
    test_cases = [
        (0.16, 0.0),   # early universe
        (0.16, 0.5),   # transition
        (0.16, 1.0),   # today
        (0.0, 1.0),    # LCDM limit
    ]
    for beta, S_a in test_cases:
        r = entropy_energy_consistency(beta, S_a)
        print(f"  beta={r['beta']:.2f}, S={r['S(a)']:.2f} => mu={r['mu']:.4f} "
              f"({r['gravity_enhancement_pct']:.1f}% enhancement)")
        assert r["physical"], "mu must be positive"
        assert r["mu"] >= 1.0, "mu should be >= 1 for non-negative beta and S"
    # LCDM recovery at beta=0
    r_lcdm = entropy_energy_consistency(0.0, 1.0)
    assert abs(r_lcdm["mu"] - 1.0) < 1e-10
    print("  [PASSED]\n")


def demo_summary():
    """Demo 5: Full integration summary."""
    print("=" * 70)
    print("DEMO 5: Cross-Field Integration Summary")
    print("=" * 70)
    cfi = CrossFieldIntegration()
    print(cfi.summary())
    assert cfi.version == "2.2"
    assert cfi.coupling_count() == 6
    assert cfi.level_count() == 4
    print("\n  [PASSED]\n")


if __name__ == "__main__":
    demo_field_couplings()
    demo_integration_levels()
    demo_coupling_matrix()
    demo_entropy_energy_consistency()
    demo_summary()
    print("All demos passed!")
