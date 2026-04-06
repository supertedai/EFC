#!/usr/bin/env python3
"""
Demo: EFC Cosmic Dipole Working Note
======================================
Demonstrates the regime-dependent anisotropy mechanism for the cosmic dipole excess.

DOI: 10.6084/m9.figshare.31942731
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cosmic_dipole import (
    KinematicDipole, EntropyGradient, DipoleAmplitude,
    DipoleExcess, RegimeDependentIsotropy, Predictions,
)


def demo_kinematic():
    """1. Standard kinematic dipole."""
    print("=" * 65)
    print("DEMO 1: Kinematic Dipole")
    print("=" * 65)
    kin = KinematicDipole()
    info = kin.info()
    print(f"  v_peculiar = {info['v_peculiar_km_s']} km/s")
    print(f"  D_kin = 2v/c = {info['D_kinematic']:.5f}")
    print(f"  Mechanism: {info['mechanism']}")
    print()


def demo_observations():
    """2. Observed dipole excess."""
    print("=" * 65)
    print("DEMO 2: Observed Dipole Excess (2-3× kinematic)")
    print("=" * 65)
    excess = DipoleExcess()
    results = excess.excess()
    print(f"  {'Survey':>20s}  {'D_obs':>8s}  {'D_kin':>8s}  {'D_excess':>10s}  {'Ratio':>6s}")
    print(f"  {'-'*20}  {'-'*8}  {'-'*8}  {'-'*10}  {'-'*6}")
    for r in results:
        print(f"  {r['survey']:>20s}  {r['D_obs']:8.4f}  {r['D_kin']:8.5f}  "
              f"{r['D_excess']:10.5f}  {r['ratio_obs_kin']:6.1f}×")
    print(f"\n  Mean excess: {excess.mean_excess():.5f}")
    print()


def demo_regime_isotropy():
    """3. Regime-dependent isotropy."""
    print("=" * 65)
    print("DEMO 3: Isotropy as Regime Condition")
    print("=" * 65)
    rdi = RegimeDependentIsotropy()
    for r in rdi.regime_table():
        print(f"  {r['regime']:>4s} ({r['epoch']:>25s}): {r['isotropy']}")
    insight = rdi.key_insight()
    print(f"\n  Key insight: {insight['insight']}")
    print(f"  Mechanism: {insight['mechanism']}")
    print()


def demo_entropy_gradient():
    """4. Entropy gradient mechanism."""
    print("=" * 65)
    print("DEMO 4: Entropy Gradient Mechanism")
    print("=" * 65)
    eg = EntropyGradient()
    print(f"  |∇S|L_grad/S̄ = {eg.grad_S_over_S}")
    print(f"  Entropy variation: ~{eg.variation_percent():.1f}%")
    print(f"  ΔG_eff/G_N = {eg.delta_G_eff_fractional():.5f}")

    # Required gradient for different excesses
    print(f"\n  Required gradient for different excesses:")
    for D_exc in [0.005, 0.007, 0.010]:
        req = eg.required_gradient(D_exc)
        print(f"    D_excess = {D_exc:.3f} → |∇S|L/S̄ = {req:.4f} ({req*100:.1f}%)")

    # CMB consistency
    cmb = eg.cmb_consistency()
    print(f"\n  CMB consistency:")
    print(f"    CMB anisotropy: {cmb['cmb_anisotropy']:.0e}")
    print(f"    Growth factor: ~{cmb['growth_factor']:.0e}")
    print(f"    Expected late-time: {cmb['expected_late_time_variation']:.3f}")
    print(f"    Required: {cmb['required_variation']:.3f}")
    print(f"    Ratio: {cmb['ratio']:.1f}× (consistent: {cmb['consistent']})")
    print()


def demo_dipole_amplitude():
    """5. EFC dipole amplitude."""
    print("=" * 65)
    print("DEMO 5: EFC Dipole Amplitude (Eq. 4)")
    print("=" * 65)
    amp = DipoleAmplitude()
    print(f"  Parameters: b_eff={amp.b_eff}, μ₀={amp.mu_0}, |f'|={amp.f_prime}")
    print(f"  D_EFC = {amp.D_EFC():.5f}")
    print(f"  D_total = D_kin + D_EFC = {amp.D_total():.5f}")

    print(f"\n  Scan across tracer biases:")
    print(f"  {'b_eff':>6s}  {'D_EFC':>8s}  {'D_total':>8s}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}")
    for row in amp.scan_bias([1.0, 1.5, 2.0, 2.5, 3.0]):
        print(f"  {row['b_eff']:6.1f}  {row['D_EFC']:8.5f}  {row['D_total']:8.5f}")
    print()


def demo_predictions():
    """6. Predictions and open gaps."""
    print("=" * 65)
    print("DEMO 6: Predictions (P1-P4) and Open Gaps (G1-G4)")
    print("=" * 65)
    pred = Predictions()
    s = pred.summary()

    print("\n  Predictions:")
    for pid in ["P1", "P2", "P3", "P4"]:
        p = s["predictions"][pid]
        print(f"    {p['id']}: {p['description']}")
        print(f"         {p['prediction']}")

    print("\n  Open Gaps:")
    for g in s["gaps"]:
        print(f"    {g['id']}: {g['description']} [{g['status']}]")

    print(f"\n  Status: {s['status']}")
    print()


if __name__ == "__main__":
    print()
    print("EFC Cosmic Dipole Working Note — Full Demo")
    print("DOI: 10.6084/m9.figshare.31942731")
    print("Author: Morten Magnusson")
    print()

    demo_kinematic()
    demo_observations()
    demo_regime_isotropy()
    demo_entropy_gradient()
    demo_dipole_amplitude()
    demo_predictions()

    print("=" * 65)
    print("All 6 demonstrations completed successfully.")
    print("Isotropy = regime condition → ∇S → directional G_eff → dipole")
    print("=" * 65)
