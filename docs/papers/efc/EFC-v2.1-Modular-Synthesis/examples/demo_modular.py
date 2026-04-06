#!/usr/bin/env python3
"""Demonstration: EFC v2.1 Modular Synthesis.

Tests the modular decomposition, module interfaces, and cross-module
consistency checks.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_modular import (
    ModuleInterface, StructuralModule, DynamicalModule,
    EntropicModule, InformationalModule, ModularArchitecture,
)


def demo_module_count():
    """Demo 1: Verify four modules exist."""
    print("=" * 70)
    print("DEMO 1: Module Count and Labels")
    print("=" * 70)
    arch = ModularArchitecture()
    modules = arch.modules()
    print(f"  Number of modules: {arch.module_count()}")
    for label, mod in modules.items():
        print(f"  - {label}: {mod.name}")
    assert arch.module_count() == 4
    assert "M1_Structural" in modules
    assert "M2_Dynamical" in modules
    assert "M3_Entropic" in modules
    assert "M4_Informational" in modules
    print("  [PASSED]\n")


def demo_interfaces():
    """Demo 2: Module interfaces have proper inputs/outputs."""
    print("=" * 70)
    print("DEMO 2: Module Interfaces")
    print("=" * 70)
    arch = ModularArchitecture()
    imap = arch.interface_map()
    for label, iface in imap.items():
        print(f"  {label}:")
        print(iface.summary())
    # Entropic outputs feed into Dynamical inputs
    assert "entropy_state" in imap["M3"].outputs
    assert "entropy_state" in imap["M2"].inputs
    # Structural outputs feed into Dynamical
    assert "metric_tensor" in imap["M1"].outputs
    assert "metric_tensor" in imap["M2"].inputs
    # Informational needs entropy
    assert "entropy_state" in imap["M4"].inputs
    print("  [PASSED]\n")


def demo_entropy_second_law():
    """Demo 3: Entropic module satisfies the second law."""
    print("=" * 70)
    print("DEMO 3: Entropy Second Law Check")
    print("=" * 70)
    em = EntropicModule()
    a_values = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 0.9, 1.0]
    print(f"  {'a':>6s}  {'S(a)':>8s}  {'dS/dlna':>10s}")
    print("  " + "-" * 28)
    for a in a_values:
        print(f"  {a:6.2f}  {em.S(a):8.4f}  {em.dS_dlna(a):10.4f}")
    assert em.satisfies_second_law(a_values), "Second law must hold"
    print("  Second law satisfied: YES")
    print("  [PASSED]\n")


def demo_cross_module_consistency():
    """Demo 4: Cross-module entropy-dynamics consistency."""
    print("=" * 70)
    print("DEMO 4: Cross-Module Consistency (Entropy -> Dynamics)")
    print("=" * 70)
    arch = ModularArchitecture()
    a_values = [0.1, 0.3, 0.55, 0.7, 1.0]
    print(f"  {'a':>6s}  {'S(a)':>8s}  {'(H/H0)^2':>10s}")
    print("  " + "-" * 28)
    for a in a_values:
        result = arch.check_entropy_dynamics_consistency(a)
        print(f"  {result['a']:6.2f}  {result['S(a)']:8.4f}  {result['(H/H0)^2']:10.4f}")
    # At a=1, (H/H0)^2 should be close to 1
    r = arch.check_entropy_dynamics_consistency(1.0)
    assert abs(r["(H/H0)^2"] - 1.0) < 0.2, "(H/H0)^2 at a=1 should be ~1"
    print("  [PASSED]\n")


def demo_landauer():
    """Demo 5: Informational module Landauer bound."""
    print("=" * 70)
    print("DEMO 5: Landauer Bound (Informational Module)")
    print("=" * 70)
    im = InformationalModule()
    T_cmb = 2.725  # K (CMB temperature today)
    cost_1bit = im.landauer_cost(T_cmb, 1)
    print(f"  T = {T_cmb} K (CMB temperature)")
    print(f"  Landauer cost for 1 bit: {cost_1bit:.4e} J")
    print(f"  Landauer cost for 1e20 bits: {im.landauer_cost(T_cmb, int(1e20)):.4e} J")
    max_bits = im.max_bits_from_energy(1.0, T_cmb)
    print(f"  Max bits from 1 J at T_CMB: {max_bits:.4e}")
    assert cost_1bit > 0, "Landauer cost must be positive"
    assert max_bits > 0, "Max bits must be positive"
    # Round-trip: cost of max_bits should be ~1 J
    roundtrip = im.landauer_cost(T_cmb, int(max_bits))
    assert abs(roundtrip - 1.0) < 0.01, "Round-trip should give ~1 J"
    print("  [PASSED]\n")


def demo_structural():
    """Demo 6: Structural module properties."""
    print("=" * 70)
    print("DEMO 6: Structural Module Properties")
    print("=" * 70)
    sm = StructuralModule()
    sig = sm.metric_signature()
    dof = sm.degrees_of_freedom()
    print(f"  Metric signature: {sig}")
    print(f"  Degrees of freedom: {dof}")
    print(f"  Description: {sm.description}")
    assert sig == (-1, 1, 1, 1), "Lorentzian signature required"
    assert dof == 10, "4D symmetric tensor has 10 components"
    print("  [PASSED]\n")


if __name__ == "__main__":
    demo_module_count()
    demo_interfaces()
    demo_entropy_second_law()
    demo_cross_module_consistency()
    demo_landauer()
    demo_structural()
    print("All demos passed!")
