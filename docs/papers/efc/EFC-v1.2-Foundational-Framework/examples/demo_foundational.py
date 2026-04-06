#!/usr/bin/env python3
"""Demonstration: EFC v1.2 Foundational Framework.

DOI: 10.6084/m9.figshare.30563738
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_foundational import (
    FoundationalFramework, canonical_fields, regime_architecture,
    thermodynamic_principles, structural_relationships, entropy_sigmoid,
)


def demo_fields():
    """Demo 1: Verify the four canonical EFC fields."""
    print("=" * 70)
    print("DEMO 1: Canonical EFC Fields")
    print("=" * 70)
    fields = canonical_fields()
    print(f"  Number of fields: {len(fields)}")
    for key, f in fields.items():
        print(f"  - {f.name} ({f.symbol}): {f.role}")
    assert len(fields) == 4, "Expected 4 canonical fields"
    assert "energy_flow" in fields
    assert "entropy" in fields
    assert "grid" in fields
    assert "information" in fields
    assert fields["energy_flow"].symbol == "E_f"
    assert fields["entropy"].symbol == "S"
    print("  [PASSED]\n")


def demo_regimes():
    """Demo 2: Verify the four-level regime architecture."""
    print("=" * 70)
    print("DEMO 2: Regime Architecture (L0-L3)")
    print("=" * 70)
    regimes = regime_architecture()
    print(f"  Number of regimes: {len(regimes)}")
    for key, r in regimes.items():
        print(f"  - {r.label} ({r.name}): {r.dominant_physics}")
    assert len(regimes) == 4, "Expected 4 regimes"
    assert "L0" in regimes and "L1" in regimes
    assert "L2" in regimes and "L3" in regimes
    assert regimes["L0"].label == "L0"
    assert regimes["L3"].label == "L3"
    print("  [PASSED]\n")


def demo_entropy_sigmoid():
    """Demo 3: Verify entropy sigmoid behaviour."""
    print("=" * 70)
    print("DEMO 3: Entropy Sigmoid S(a)")
    print("=" * 70)
    # At transition point a_t=0.55, S should be ~0.5
    S_at_transition = entropy_sigmoid(0.55)
    print(f"  S(a=0.55) = {S_at_transition:.4f}  (expected ~0.50)")
    assert abs(S_at_transition - 0.5) < 0.01, f"S at transition should be ~0.5, got {S_at_transition}"

    # At a=1 (today), S should be high (close to S_inf=1)
    S_today = entropy_sigmoid(1.0)
    print(f"  S(a=1.0)  = {S_today:.4f}  (expected > 0.99)")
    assert S_today > 0.99, f"S today should be > 0.99, got {S_today}"

    # At early times (a << a_t), S should be near 0
    S_early = entropy_sigmoid(0.01)
    print(f"  S(a=0.01) = {S_early:.6f}  (expected ~0)")
    assert S_early < 0.01, f"S at early times should be ~0, got {S_early}"

    # Monotonicity check
    a_values = [0.01, 0.1, 0.3, 0.55, 0.7, 1.0]
    S_values = [entropy_sigmoid(a) for a in a_values]
    for i in range(1, len(S_values)):
        assert S_values[i] >= S_values[i - 1], "Entropy must be non-decreasing"
    print("  Monotonicity: PASSED")
    print("  [PASSED]\n")


def demo_thermodynamic_principles():
    """Demo 4: Verify thermodynamic foundations."""
    print("=" * 70)
    print("DEMO 4: Thermodynamic Principles")
    print("=" * 70)
    principles = thermodynamic_principles()
    print(f"  Number of principles: {len(principles)}")
    for p in principles:
        print(f"  - {p.principle}: {p.efc_role}")
    assert len(principles) == 4, "Expected 4 thermodynamic principles"
    names = [p.principle for p in principles]
    assert any("Second Law" in n for n in names)
    assert any("Landauer" in n for n in names)
    print("  [PASSED]\n")


def demo_framework_summary():
    """Demo 5: Full framework summary."""
    print("=" * 70)
    print("DEMO 5: Framework Summary")
    print("=" * 70)
    fw = FoundationalFramework()
    print(fw.summary())
    assert fw.field_count() == 4
    assert fw.regime_count() == 4
    assert fw.version == "1.2"
    # Check entropy computation through the framework
    S = fw.entropy_at(1.0)
    assert S > 0.99, f"Framework entropy at a=1 should be > 0.99, got {S}"
    print("\n  [PASSED]\n")


def demo_structural_relations():
    """Demo 6: Structural relationships between fields."""
    print("=" * 70)
    print("DEMO 6: Structural Relationships")
    print("=" * 70)
    rels = structural_relationships()
    print(f"  Number of relationships: {len(rels)}")
    for r in rels:
        print(f"  - {r.name}: {' <-> '.join(r.fields)}")
    assert len(rels) == 4, "Expected 4 structural relationships"
    rel_names = [r.name for r in rels]
    assert any("Energy-Entropy" in n for n in rel_names)
    assert any("Information-Entropy" in n for n in rel_names)
    print("  [PASSED]\n")


if __name__ == "__main__":
    demo_fields()
    demo_regimes()
    demo_entropy_sigmoid()
    demo_thermodynamic_principles()
    demo_framework_summary()
    demo_structural_relations()
    print("All demos passed!")
