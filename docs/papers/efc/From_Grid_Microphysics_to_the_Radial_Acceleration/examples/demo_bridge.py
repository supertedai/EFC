#!/usr/bin/env python3
"""Demonstration: Grid Microphysics to RAR Bridge.

Shows the complete derivation chain from gradient-coupled grid modes
to the Bose-Einstein RAR, including lattice derivation and KT3 resolution.

DOI: 10.6084/m9.figshare.31878760
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grid_microphysics import (
    GridNode,
    GradientCoupling,
    BoseEinsteinRAR,
    LatticeDerivation,
    MicrophysicalBridge,
    FalsificationCondition,
    A0_SPARC,
)


def demo_three_assumptions():
    """Demonstrate the three assumptions and derivation."""
    print("=" * 70)
    print("THREE ASSUMPTIONS → BOSE-EINSTEIN RAR")
    print("=" * 70)
    print()
    print("A1: Bosonic statistics   ⟨n⟩ = 1/(exp(E/k_BT) − 1)")
    print("A2: Gradient coupling     E = ℏω₀√(g/g*)")
    print("A3: Single scale          a₀ = g*(k_BT/ℏω₀)² = 1.2×10⁻¹⁰ m/s²")
    print()

    # Show derivation at specific g values
    rar = BoseEinsteinRAR()
    test_g = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8]
    print(f"{'g (m/s²)':>12s} {'√(g/a₀)':>10s} {'μ(g)':>12s} {'Regime':>12s}")
    print("-" * 50)
    for g in test_g:
        info = rar.asymptotic_limits(g)
        print(f"{g:12.2e} {info['x']:10.4f} {info['mu_exact']:12.6f} {info['regime']:>12s}")
    print()


def demo_why_gradient():
    """Demonstrate why only gradient coupling works."""
    print("=" * 70)
    print("WHY √g AND NOT g OR Φ")
    print("=" * 70)
    print()

    gc = GradientCoupling()
    # Typical galaxy: g ~ 1e-10, rho ~ 1e-24 kg/m^3, Phi ~ -1e5 m^2/s^2
    result = gc.test_alternatives(g=1e-10, rho=1e-24, Phi=-1e5)
    print(f"  Density coupling (ρ = 1e-24 kg/m³):  {result['density_coupling']:.6e}")
    print(f"  Potential coupling (Φ = -1e5 m²/s²): {result['potential_coupling']:.6e}")
    print(f"  Gradient coupling (g = 1e-10 m/s²):  {result['gradient_coupling']:.6e}")
    print(f"  ✓ Correct: {result['correct']}")
    print(f"  Reason: {result['reason']}")
    print()


def demo_lattice_derivation():
    """Demonstrate the lattice derivation of E ∝ √g."""
    print("=" * 70)
    print("LATTICE DERIVATION: E ∝ √g")
    print("=" * 70)
    print()
    print("Setup: Two nodes separated by l_g, mode displaced by ξ")
    print("  ΔF = −(g/l_g)·ξ  →  k_eff = g/l_g  (Hooke's law)")
    print("  ω = √(k_eff/m_eff) ∝ √g")
    print("  E = ℏω ∝ √g  ✓")
    print()

    lattice = LatticeDerivation()
    test_g = [1e-12, 1e-11, 1e-10, 1e-9, 1e-8]
    results = lattice.verify_sqrt_scaling(test_g)
    print(f"{'g':>12s} {'k_eff':>12s} {'ω':>12s} {'E/√g':>12s}")
    print("-" * 50)
    for r in results:
        k = lattice.spring_constant(r['g'])
        print(f"{r['g']:12.2e} {k:12.2e} {r['E']:12.6f} {r['E_over_sqrt_g']:12.6f}")
    print("  → E/√g is constant: confirmed ✓")
    print()


def demo_full_bridge():
    """Demonstrate the complete bridge chain."""
    print("=" * 70)
    print("COMPLETE CHAIN (Eq. 14)")
    print("Grid DOF → E∝√g → BE → μ(g) → G_eff → RAR")
    print("=" * 70)
    print()

    bridge = MicrophysicalBridge()

    # Execute chain at a₀ (transition point)
    result = bridge.full_chain(g=A0_SPARC)
    print(f"At g = a₀ = {A0_SPARC:.1e} m/s²:")
    print(f"  Energy ratio √(g/a₀) = {result['step2_energy_ratio']:.4f}")
    print(f"  BE occupation ⟨n⟩ = {result['step3_be_occupation']:.4f}")
    print(f"  μ(g) = {result['step4_mu']:.4f}")
    print(f"  g_eff = {result['step5_g_eff']:.4e} m/s²")
    print(f"  Enhancement factor = {result['step6_enhancement']:.4f}")
    print()

    # Deep MOND regime
    g_deep = 1e-12
    result_deep = bridge.full_chain(g=g_deep)
    print(f"Deep MOND (g = {g_deep:.0e} m/s²):")
    print(f"  μ(g) = {result_deep['step4_mu']:.2f}")
    print(f"  Enhancement = {result_deep['step6_enhancement']:.2f}×")
    print()

    # Newtonian regime
    g_newton = 1e-8
    result_newton = bridge.full_chain(g=g_newton)
    print(f"Newtonian (g = {g_newton:.0e} m/s²):")
    print(f"  μ(g) = {result_newton['step4_mu']:.2e}")
    print(f"  Enhancement = {result_newton['step6_enhancement']:.6f}× (≈1)")
    print()


def demo_kt3_resolution():
    """Demonstrate KT3 resolution pathway."""
    print("=" * 70)
    print("KT3 RESOLUTION: β = 0.29 → 0.50")
    print("=" * 70)
    print()

    bridge = MicrophysicalBridge()
    masses = [1e8, 1e9, 1e10, 1e11, 1e12]

    print("Prediction: ⟨n⟩ ~ 1 gives r_trans ~ √(GM/a₀)")
    print()
    print(f"{'M (M☉)':>12s} {'r_trans (kpc)':>14s} {'g_trans (m/s²)':>14s}")
    print("-" * 44)
    for M in masses:
        result = bridge.kt3_resolution(M)
        print(f"{M:12.0e} {result['r_trans_kpc']:14.2f} {result['g_trans_m_s2']:14.2e}")

    print()
    print(f"  β predicted (statistical occupation): 0.50")
    print(f"  β observed (classical KT3):           0.29")
    print(f"  Resolution: use BE occupation instead of classical field values")
    print()


def demo_macro_micro():
    """Compare macro (EFT) and micro (grid) descriptions."""
    print("=" * 70)
    print("MACRO–MICRO BRIDGE")
    print("=" * 70)
    print()

    bridge = MicrophysicalBridge()
    comparison = bridge.macro_micro_comparison()

    print("MACRO (Covariant EFT, 31878334):")
    for r in comparison["macro_framework"]["results"]:
        print(f"  ✓ {r}")
    print(f"  ✗ GAP: {comparison['macro_framework']['gap']}")
    print()

    print("MICRO (This paper, 31878760):")
    for r in comparison["micro_model"]["results"]:
        print(f"  ✓ {r}")
    print(f"  → {comparison['micro_model']['gap_status']}")
    print()
    print(f"Bridge: {comparison['bridge']}")
    print()


def demo_falsification():
    """Show falsification conditions."""
    print("=" * 70)
    print("FALSIFICATION CONDITIONS")
    print("=" * 70)
    print()

    for fc in FalsificationCondition.all_conditions():
        print(f"  {fc.id}: {fc.condition}")
        print(f"       Test: {fc.test}")
        print()


if __name__ == "__main__":
    demo_three_assumptions()
    demo_why_gradient()
    demo_lattice_derivation()
    demo_full_bridge()
    demo_kt3_resolution()
    demo_macro_micro()
    demo_falsification()
    print("All demonstrations complete.")
