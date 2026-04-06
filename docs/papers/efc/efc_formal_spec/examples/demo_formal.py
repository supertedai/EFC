#!/usr/bin/env python3
"""Demonstration: EFC Formal Specification.

Tests formal notation, field equations, entropy boundary conditions,
thermodynamic constraints, and grid field properties.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_formal import (
    EFCFormalSpec, FormalFieldEquation, FormalEntropySigmoid,
    GridFieldSpec, symbol_table, constraint_set,
)


def demo_symbol_table():
    """Demo 1: Canonical symbol table."""
    print("=" * 70)
    print("DEMO 1: Formal Symbol Table")
    print("=" * 70)
    syms = symbol_table()
    print(f"  Symbols defined: {len(syms)}")
    for key, s in syms.items():
        print(f"  - {s.symbol}: {s.name} ({s.domain})")
    assert len(syms) == 10, f"Expected 10 symbols, got {len(syms)}"
    assert "beta" in syms
    assert "G_uv" in syms
    assert "mu_a" in syms
    assert syms["beta"].domain == "R >= 0"
    print("  [PASSED]\n")


def demo_field_equation():
    """Demo 2: Formal field equation structure."""
    print("=" * 70)
    print("DEMO 2: Formal Field Equation")
    print("=" * 70)
    fe = FormalFieldEquation()
    print(f"  {fe.equation_string()}")
    print(f"  Terms on RHS: {fe.term_count()}")
    print(f"  GR recovery: {fe.reduces_to_GR()}")
    assert fe.term_count() == 3, "Expected 3 RHS terms"
    assert "G_{mu nu}" in fe.equation_string()
    assert "T^{(E_f)}" in fe.equation_string()
    print("  [PASSED]\n")


def demo_entropy_boundaries():
    """Demo 3: Entropy sigmoid boundary conditions."""
    print("=" * 70)
    print("DEMO 3: Entropy Sigmoid Boundary Conditions")
    print("=" * 70)
    S = FormalEntropySigmoid()
    bc = S.boundary_conditions()
    for k, v in bc.items():
        print(f"  {k}: {v}")
    print(f"  S(0.001) = {S.evaluate(0.001):.6f}")
    print(f"  S(a_t)   = {S.evaluate(S.a_t):.4f}")
    print(f"  S(100)   = {S.evaluate(100.0):.6f}")
    assert S.verify_boundary(), "Boundary conditions must hold"
    # Derivative should peak at transition
    d_at = S.derivative(S.a_t)
    d_early = S.derivative(0.01)
    d_late = S.derivative(10.0)
    print(f"  dS/dlna at a_t: {d_at:.4f}")
    assert d_at > d_early, "Derivative should peak near transition"
    assert d_at > d_late, "Derivative should peak near transition"
    print("  [PASSED]\n")


def demo_constraints():
    """Demo 4: Thermodynamic constraint set."""
    print("=" * 70)
    print("DEMO 4: Thermodynamic Constraints")
    print("=" * 70)
    constraints = constraint_set()
    print(f"  Number of constraints: {len(constraints)}")
    for c in constraints:
        print(f"  - {c.name}: {c.formal_statement}")
    assert len(constraints) == 5, "Expected 5 constraints"
    names = [c.name for c in constraints]
    assert any("monotonicity" in n for n in names)
    assert any("GR limit" in n for n in names)
    print("  [PASSED]\n")


def demo_grid_field():
    """Demo 5: Grid field formal structure."""
    print("=" * 70)
    print("DEMO 5: Grid Field Formal Structure")
    print("=" * 70)
    grid = GridFieldSpec()
    print(f"  Symbol: {grid.symbol}")
    print(f"  Dimensionality: {grid.dimensionality}")
    print(f"  Signature: {grid.signature}")
    print(f"  Topology: {grid.topology}")
    print(f"  Metric DOF: {grid.degrees_of_freedom()}")
    print(f"  Emergent condition: {grid.emergent_metric_condition()}")
    assert grid.dimensionality == 4
    assert grid.signature == (-1, 1, 1, 1)
    assert grid.degrees_of_freedom() == 10
    print("  [PASSED]\n")


def demo_full_spec():
    """Demo 6: Full formal specification summary."""
    print("=" * 70)
    print("DEMO 6: Full Formal Specification")
    print("=" * 70)
    spec = EFCFormalSpec()
    print(spec.summary())
    assert spec.symbol_count() == 10
    assert spec.constraint_count() == 5
    assert spec.version == "1.0"
    print("\n  [PASSED]\n")


if __name__ == "__main__":
    demo_symbol_table()
    demo_field_equation()
    demo_entropy_boundaries()
    demo_constraints()
    demo_grid_field()
    demo_full_spec()
    print("All demos passed!")
