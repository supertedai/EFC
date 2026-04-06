#!/usr/bin/env python3
"""
H₀ Prediction Example

Demonstrates predicting the Hubble constant from MOND/RAR data
using the EFC framework.

Key insight: a_G ≈ 0.1 from galaxy dynamics predicts H₀ ≈ 74 km/s/Mpc,
matching the observed Hubble tension.
"""

import math
import sys
from pathlib import Path

# Add package root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.entropy_mapping import EntropyMapping
from src.phase_calculator import PhaseCalculator
from src.mond_interpolation import MONDInterpolator, compute_aG_from_mond
from src.h0_predictor import H0Predictor, predict_h0


def main():
    """Run H₀ prediction demonstration."""
    print("=" * 60)
    print("H₀ Prediction from MOND/RAR Data")
    print("=" * 60)
    print()

    # Step 1: Setup entropy mapping
    print("Step 1: Entropy Mapping S(z)")
    print("-" * 40)
    mapping = EntropyMapping(z_trans=3.0, delta=0.5)
    print(f"  S(z=0, today) = {mapping.S(0):.4f}")
    print(f"  S(z=1100, CMB) = {mapping.S(1100):.6f}")
    print()

    # Step 2: Compute phase difference
    print("Step 2: Phase Difference ΔΦ")
    print("-" * 40)
    calc = PhaseCalculator()
    delta_phi = calc.delta_phi_cmb_today()
    print(f"  Φ(today) = {calc.phi_at_z(0):.4f}")
    print(f"  Φ(CMB) = {calc.phi_at_z(1100):.6f}")
    print(f"  ΔΦ = {delta_phi:.4f}")
    print()

    # Step 3: Get a_G from MOND transition zone
    print("Step 3: a_G from MOND Transition Zone")
    print("-" * 40)
    interp = MONDInterpolator(delta_phi=delta_phi)

    print("  MOND interpolation table:")
    for g_ratio in [1.0, 2.0, 5.0, 10.0]:
        point = interp.get_point(g_ratio)
        marker = " ← transition zone" if g_ratio == 5.0 else ""
        print(f"    g/a₀={g_ratio:4.1f}: μ={point.mu:.3f}, "
              f"μ⁻¹={point.mu_inverse:.3f}, a_G={point.implied_aG:.3f}{marker}")

    aG_mond = compute_aG_from_mond(5.0, delta_phi)
    print(f"\n  Using g_bar/a₀ = 5 (cosmic web average):")
    print(f"  a_G = {aG_mond:.4f}")
    print()

    # Step 4: Predict H₀
    print("Step 4: Predict H₀")
    print("-" * 40)
    h0_cmb = 67.4  # Planck
    h0_obs = 73.0  # SH0ES

    predictor = H0Predictor(h0_cmb=h0_cmb, h0_local=h0_obs, delta_phi=delta_phi)

    # Using Friedmann constraint: a_H₀ = ½ a_G
    aH0 = aG_mond / 2
    print(f"  Friedmann constraint: a_H₀ = ½ a_G = {aH0:.4f}")
    print()

    h0_pred = h0_cmb * math.exp(aH0 * delta_phi)
    print(f"  H₀_pred = H₀_CMB × exp(a_H₀ × ΔΦ)")
    print(f"  H₀_pred = {h0_cmb} × exp({aH0:.4f} × {delta_phi})")
    print(f"  H₀_pred = {h0_pred:.1f} km/s/Mpc")
    print()

    # Step 5: Compare with observation
    print("Step 5: Comparison with Observation")
    print("-" * 40)
    deviation = abs(h0_pred - h0_obs) / h0_obs * 100
    print(f"  H₀ predicted: {h0_pred:.1f} km/s/Mpc")
    print(f"  H₀ observed:  {h0_obs:.1f} km/s/Mpc (SH0ES)")
    print(f"  Deviation:    {deviation:.1f}%")
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"  From MOND (g/a₀=5): a_G = {aG_mond:.3f}")
    print(f"  Predicted H₀: {h0_pred:.1f} km/s/Mpc")
    print(f"  Observed H₀:  {h0_obs:.1f} km/s/Mpc")
    print(f"  Agreement:    {100-deviation:.1f}%")
    print()
    print("  The Hubble tension is explained by entropy-driven")
    print("  gravity modification with a_G ≈ 0.1")


if __name__ == "__main__":
    main()
