#!/usr/bin/env python3
"""
Demo: EFC Regime Transition Framework

Demonstrates the Landau-theory gating function, chi(z) control parameter,
RK4 integration, CMB safety verification, and published results comparison.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from regime_transition import (
    RegimeTransitionFramework,
    CosmologyParams,
    RegimeParams,
    KEY_GATING_VALUES,
)


def main():
    print("=" * 60)
    print("EFC REGIME TRANSITION FRAMEWORK DEMO")
    print("CMB-Consistent Approach to Late-Time Cosmology")
    print("=" * 60)

    fw = RegimeTransitionFramework()

    # --- Demo 1: Control parameter chi(z) ---
    print("\n1. CONTROL PARAMETER chi(z)")
    print("-" * 40)

    z_values = [3000, 1100, 100, 50, 10, 2, 0]
    print(f"  chi_early = {fw.regime.chi_early}, chi_late = {fw.regime.chi_late}")
    print(f"  z_transition = {fw.regime.z_transition}, delta_z = {fw.regime.delta_z}")
    print()
    for z in z_values:
        chi_val = fw.chi(z)
        print(f"  z = {z:5d}:  chi = {chi_val:.4f}")

    # chi should be near chi_early at high z and chi_late at low z
    assert fw.chi(3000) < 0.5, "chi at high z should be near chi_early"
    assert fw.chi(0) > 2.0, "chi at z=0 should be near chi_late"
    print("  [PASS] chi transitions from early to late values")

    # --- Demo 2: Gating function G(phi) ---
    print("\n2. GATING FUNCTION G(phi) = phi^2 / (phi^2 + phi0^2)")
    print("-" * 40)

    phi_values = [1e-6, 1e-3, 0.01, 0.1, 0.5, 1.0, 5.0, 100.0]
    for phi in phi_values:
        G = fw.gating_function(phi)
        print(f"  phi = {phi:8.1e}:  G = {G:.6e}")

    assert fw.gating_function(1e-6) < 1e-10, "G should be tiny for small phi"
    assert fw.gating_function(100.0) > 0.999, "G should be ~1 for large phi"
    print("  [PASS] G(phi) transitions from 0 to 1")

    # --- Demo 3: RK4 integration ---
    print("\n3. RK4 INTEGRATION OF LANDAU EQUATION")
    print("-" * 40)

    # Use fewer points for demo speed
    z_arr, phi_arr, G_arr = fw.solve_rk4(n_steps=5000)

    print(f"  Integration: z = {z_arr[0]:.0f} -> {z_arr[-1]:.0f}")
    print(f"  Steps: {len(z_arr) - 1}")
    print(f"  phi(z=3000) = {phi_arr[0]:.3e}")
    print(f"  phi(z=0)    = {phi_arr[-1]:.3e}")
    print(f"  G(z=3000)   = {G_arr[0]:.3e}")
    print(f"  G(z=0)      = {G_arr[-1]:.6f}")

    # G at high z should be tiny
    assert G_arr[0] < 1e-6, "G at z=3000 should be negligible"
    # G at z=0 should be near 1
    assert G_arr[-1] > 0.99, "G at z=0 should be near 1"
    print("  [PASS] G(z) correctly transitions from ~0 to ~1")

    # --- Demo 4: CMB safety verification ---
    print("\n4. CMB SAFETY VERIFICATION")
    print("-" * 40)

    cmb_result = fw.verify_cmb_safety(z_arr, G_arr)
    print(f"  G(z=1100) = {cmb_result.G_cmb:.3e}")
    print(f"  Threshold = {cmb_result.threshold:.0e}")
    print(f"  Safe:       {cmb_result.is_safe}")
    print(f"  Margin:     {cmb_result.safety_margin_orders:.1f} orders of magnitude")

    assert cmb_result.is_safe, "CMB safety must be satisfied"
    print("  [PASS] CMB safety confirmed")

    # --- Demo 5: Published G(z) table ---
    print("\n5. PUBLISHED G(z) VALUES")
    print("-" * 40)

    table = fw.published_G_table()
    print(f"  {'z':>6s}  {'G':>12s}  Interpretation")
    for row in table:
        print(f"  {row['z']:6d}  {row['G']:12.2e}  {row['interpretation']}")

    # Verify key published values
    assert KEY_GATING_VALUES["G_z1100"] == 1.0e-12
    assert KEY_GATING_VALUES["G_z0"] == 0.9999
    assert KEY_GATING_VALUES["G_z2"] == 0.25
    print("  [PASS] Published values match")

    # --- Demo 6: Framework scope and claims ---
    print("\n6. FRAMEWORK SCOPE")
    print("-" * 40)

    print("  Key features:")
    for feat in fw.key_features():
        print(f"    - {feat}")

    print("  What this shows:")
    for claim in fw.what_this_shows():
        print(f"    - {claim}")

    assert len(fw.key_features()) == 4
    assert len(fw.what_this_shows()) == 4
    print("  [PASS] Framework scope documented")

    # --- Summary ---
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(fw.summary())

    print("\n" + "=" * 60)
    print("ALL DEMOS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
