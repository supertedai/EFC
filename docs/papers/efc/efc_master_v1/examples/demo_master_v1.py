#!/usr/bin/env python3
"""Demonstration: EFC Master Specification v1 (Archive).

Tests the archived v1 formulation: parameters, entropy, regimes,
field definitions, and version comparison.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_master_v1_spec import (
    V1Parameters, EFCMasterV1, VersionComparison,
    v1_entropy, v1_mu, v1_regimes, v1_fields,
)


def demo_v1_parameters():
    """Demo 1: v1 canonical parameters."""
    print("=" * 70)
    print("DEMO 1: v1 Canonical Parameters")
    print("=" * 70)
    p = V1Parameters()
    d = p.as_dict()
    for key, val in d.items():
        print(f"  {key}: {val}")
    assert p.beta == 0.16
    assert p.a_t == 0.55
    assert p.sigma == 0.10
    assert p.H0 == 67.4
    print("  [PASSED]\n")


def demo_v1_entropy():
    """Demo 2: v1 entropy sigmoid."""
    print("=" * 70)
    print("DEMO 2: v1 Entropy Sigmoid")
    print("=" * 70)
    a_values = [0.01, 0.1, 0.3, 0.55, 0.7, 1.0]
    print(f"  {'a':>6s}  {'S(a)':>8s}  {'mu(a)':>8s}")
    print("  " + "-" * 26)
    for a in a_values:
        print(f"  {a:6.2f}  {v1_entropy(a):8.4f}  {v1_mu(a):8.4f}")
    assert abs(v1_entropy(0.55) - 0.5) < 0.01
    assert v1_entropy(1.0) > 0.99
    assert abs(v1_mu(1.0) - 1.16) < 0.01
    assert abs(v1_mu(0.01) - 1.0) < 0.01
    print("  [PASSED]\n")


def demo_v1_regimes():
    """Demo 3: v1 regime architecture."""
    print("=" * 70)
    print("DEMO 3: v1 Regime Architecture")
    print("=" * 70)
    regimes = v1_regimes()
    print(f"  Number of regimes: {len(regimes)}")
    for r in regimes:
        print(f"  {r.label}: {r.name} (dominant: {r.dominant_field})")
    assert len(regimes) == 4
    assert regimes[0].label == "L0"
    assert regimes[3].label == "L3"
    print("  [PASSED]\n")


def demo_v1_fields():
    """Demo 4: v1 field definitions."""
    print("=" * 70)
    print("DEMO 4: v1 Field Definitions")
    print("=" * 70)
    fields = v1_fields()
    print(f"  Number of fields: {len(fields)}")
    for f in fields:
        print(f"  {f.symbol}: {f.name} ({f.introduced_in})")
    assert len(fields) == 4
    symbols = {f.symbol for f in fields}
    assert "E_f" in symbols
    assert "S" in symbols
    assert "G_grid" in symbols
    assert "I" in symbols
    print("  [PASSED]\n")


def demo_version_comparison():
    """Demo 5: Compare v1 with v2 parameters."""
    print("=" * 70)
    print("DEMO 5: Version Comparison (v1 vs v2)")
    print("=" * 70)
    vc = VersionComparison()
    # Core parameters are unchanged from v1 to v2
    print(f"  Parameters unchanged: {vc.parameters_unchanged()}")
    assert vc.parameters_unchanged(), "v1 core params should match v2 defaults"
    # Compare entropy at several scale factors
    for a in [0.1, 0.55, 1.0]:
        comp = vc.compare_entropy(a)
        print(f"  a={comp['a']:.2f}: S_v1={comp['S_v1']:.4f}, "
              f"S_v2={comp['S_v2']:.4f}, delta={comp['delta_S']:.6f}")
        assert abs(comp["delta_S"]) < 1e-10, "v1 and v2 entropy should match"
        assert comp["identical_form"] is True
    print("  [PASSED]\n")


def demo_archive_summary():
    """Demo 6: Full v1 archive summary."""
    print("=" * 70)
    print("DEMO 6: v1 Archive Summary")
    print("=" * 70)
    spec = EFCMasterV1()
    print(spec.summary())
    assert spec.version == "1.0"
    assert spec.status == "archived"
    assert spec.field_count() == 4
    assert spec.regime_count() == 4
    assert abs(spec.entropy_at(0.55) - 0.5) < 0.01
    print("\n  [PASSED]\n")


if __name__ == "__main__":
    demo_v1_parameters()
    demo_v1_entropy()
    demo_v1_regimes()
    demo_v1_fields()
    demo_version_comparison()
    demo_archive_summary()
    print("All demos passed!")
