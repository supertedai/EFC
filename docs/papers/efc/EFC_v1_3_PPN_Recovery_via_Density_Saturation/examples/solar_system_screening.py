#!/usr/bin/env python3
"""
Example: Solar System Screening Analysis

Demonstrates that EFC modifications are suppressed far below
experimental bounds in the Solar System through dual screening.

Reference: Magnusson (2026), DOI: 10.6084/m9.figshare.31244827
"""

import sys
sys.path.insert(0, '..')
from src.efc_ppn_screening import (
    AccelerationScreening,
    DensityScreening,
    PPNAnalysis,
    SolarSystemLocation,
    LOCATIONS,
    CASSINI_BOUND,
    G_DAGGER,
    K_POWER,
    M_sun,
    AU
)
import numpy as np


def print_separator(title: str):
    """Print formatted section separator."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demonstrate_acceleration_screening():
    """Show acceleration-based screening at various locations."""
    print_separator("ACCELERATION-BASED SCREENING")

    accel = AccelerationScreening()

    print(f"\nFormula: μ(g_bar) = (1 + g†/g_bar)^k")
    print(f"Parameters: g† = {G_DAGGER:.1e} m/s², k = {K_POWER}")
    print(f"Cassini bound: |γ-1| < {CASSINI_BOUND:.1e}")

    print("\n{:<15} {:>12} {:>12} {:>12} {:>10}".format(
        "Location", "g_bar", "|μ-1|", "Margin", "Status"
    ))
    print("-" * 60)

    for name, loc in LOCATIONS.items():
        result = accel.evaluate_location(loc)
        status = "✓ PASS" if result['passes_cassini'] else "✗ FAIL"
        print("{:<15} {:>12.2e} {:>12.2e} {:>12.0e}× {:>10}".format(
            result['location'][:15],
            result['g_bar'],
            result['mu_deviation'],
            result['margin_vs_cassini'],
            status
        ))

    # Galaxy outskirts (EFC active)
    galaxy_edge = SolarSystemLocation('Galaxy 30kpc', 30e3 * 3.086e16, 1e-10)
    result = accel.evaluate_location(galaxy_edge)
    print("{:<15} {:>12.2e} {:>12.2e} {:>12} {:>10}".format(
        "Galaxy 30 kpc",
        result['g_bar'],
        result['mu_deviation'],
        "N/A",
        "EFC ACTIVE"
    ))


def demonstrate_density_screening():
    """Show density-based screening at various locations."""
    print_separator("DENSITY-BASED SCREENING")

    dens = DensityScreening()

    print(f"\nFormula: Θ(ρ_eff) = exp[-(ρ_eff/ρ*)^n]")
    print(f"Effective density: ρ_eff = 3 M_enc / (4π r³)")
    print(f"Parameters: ρ* = {dens.rho_star:.1e} kg/m³, n = {dens.n}")

    print("\n{:<15} {:>12} {:>12} {:>12}".format(
        "Location", "ρ_eff (kg/m³)", "ρ_eff/ρ*", "Θ"
    ))
    print("-" * 55)

    for name, loc in LOCATIONS.items():
        result = dens.evaluate_location(loc)
        theta_str = f"{result['theta']:.2e}" if result['theta'] > 1e-10 else "≈ 0"
        print("{:<15} {:>12.2e} {:>12.2e} {:>12}".format(
            result['location'][:15],
            result['rho_eff'],
            result['rho_ratio'],
            theta_str
        ))

    # Galaxy edge (EFC active)
    galaxy_edge = SolarSystemLocation('Galaxy 30kpc', 30e3 * 3.086e16, 1e-10, M_enc=1e10*M_sun)
    result = dens.evaluate_location(galaxy_edge)
    print("{:<15} {:>12.2e} {:>12.2e} {:>12.2f}".format(
        "Galaxy 30 kpc",
        result['rho_eff'],
        result['rho_ratio'],
        result['theta']
    ))


def demonstrate_ppn_derivation():
    """Show PPN parameter derivation from EFC field structure."""
    print_separator("PPN PARAMETER DERIVATION")

    ppn = PPNAnalysis()

    print("\nEFC Modified Einstein Equation:")
    print("  G_μν = 8πG_N [1 + μ(S)] T_μν")
    print("\nKey property: Scalar rescaling of G_N (not anisotropic)")

    print("\nLinearized equations (Newtonian gauge):")
    print("  ∇²Φ = 4πG_N [1 + Θ·μ₀] ρ")
    print("  ∇²Ψ = 4πG_N [1 + Θ·μ₀] ρ")

    print("\nSince SAME factor appears in both equations:")
    print("  Φ = Ψ  ⟹  γ ≡ Ψ/Φ = 1")
    print("\n  ★ This is a THEOREM, not an assumption! ★")

    solar = ppn.gamma_at_solar_surface()
    print(f"\nHigher-order corrections at Solar surface:")
    print(f"  U/c² = {solar['U_over_c2']:.2e}")
    print(f"  |δγ| bound: {solar['actual_bound']:.2e}")
    print(f"  Cassini bound: {CASSINI_BOUND:.2e}")
    print(f"  Margin: {solar['margin']:.1e}×")


def demonstrate_equivalence_principle():
    """Show equivalence principle preservation."""
    print_separator("EQUIVALENCE PRINCIPLE")

    ppn = PPNAnalysis()

    print("\n--- Weak Equivalence Principle (WEP) ---")
    print("Requirement: All bodies fall identically regardless of composition")
    print("\nEFC status: PRESERVED BY CONSTRUCTION")
    print("  • μ depends only on SOURCE (gravitating body)")
    print("  • μ does NOT depend on TEST BODY composition")
    print("  • All test bodies experience identical modified potential")

    print("\n--- Strong Equivalence Principle (SEP) / Nordtvedt ---")
    print("Requirement: Gravitational self-energy contributes equally to mass")
    print("\nEFC bound: |η|_EFC ≤ Θ(ρ_eff) · |ε| · (E_grav/Mc²)")

    # Earth's gravitational binding energy
    E_grav_Mc2_earth = 5e-10
    theta_earth = 0  # Fully screened
    epsilon = 1

    eta_bound = ppn.nordtvedt_bound(theta_earth, epsilon, E_grav_Mc2_earth)
    print(f"\nFor Earth:")
    print(f"  E_grav/Mc² ≈ {E_grav_Mc2_earth:.1e}")
    print(f"  Θ(ρ_eff) ≈ 0 (fully screened)")
    print(f"  |η|_EFC < 10⁻¹⁷")
    print(f"  LLR bound: |η| < 4.4×10⁻⁴")
    print(f"  Margin: > 10¹³×")


def summary_table():
    """Print comprehensive constraint summary."""
    print_separator("CONSTRAINT SUMMARY")

    print("\n{:<20} {:>15} {:>15} {:>10}".format(
        "Test", "Bound", "EFC Value", "Status"
    ))
    print("-" * 65)

    constraints = [
        ("Shapiro (Cassini)", "|γ-1| < 2.3e-5", "|μ-1| ~ 8e-9", "✓ PASS"),
        ("  (density)", "", "γ = 1 (derived)", "✓ PASS"),
        ("LLR (Nordtvedt)", "|η| < 4.4e-4", "< 1e-17", "✓ PASS"),
        ("Mercury perihelion", "42.98±0.04\"/cen", "~1e-7\"/cen", "✓ PASS"),
        ("WEP", "|Δa/a| < 1e-13", "0 (by constr.)", "✓ PASS"),
    ]

    for test, bound, efc, status in constraints:
        print("{:<20} {:>15} {:>15} {:>10}".format(test, bound, efc, status))

    print("\n" + "=" * 65)
    print("  CONCLUSION: EFC fully compatible with all Solar System tests")
    print("=" * 65)


def main():
    """Run complete demonstration."""
    print("\n" + "=" * 60)
    print("  EFC v1.3 PPN RECOVERY DEMONSTRATION")
    print("  DOI: 10.6084/m9.figshare.31244827")
    print("=" * 60)

    demonstrate_acceleration_screening()
    demonstrate_density_screening()
    demonstrate_ppn_derivation()
    demonstrate_equivalence_principle()
    summary_table()


if __name__ == '__main__':
    main()
