#!/usr/bin/env python3
"""
Lensing Response Model - Demonstration

This script demonstrates the key concepts from:
Magnusson (2026) "A Regime-Activated Lensing Response Improves the Fit to
KiDS-1000 Cosmic Shear and Reframes the S8 Tension"
DOI: 10.6084/m9.figshare.31271917
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.lensing_response import (
    LensingResponse, S8Reframing, TomographicFingerprint, LikelihoodAnalysis
)


def demo_lensing_response():
    """
    Demonstrate the lensing response Σ(k,z).

    The model modifies the effective power spectrum:
        P_eff(k,z) = P_ΛCDM(k,z) × Σ²(k,z)
    """
    print("=" * 60)
    print("LENSING RESPONSE Σ(k,z) DEMONSTRATION")
    print("=" * 60)

    # Initialize with best-fit parameters
    model = LensingResponse(alpha=0.10, k_trans=0.1, z_activ=0.5)

    print("\nBest-fit parameters:")
    print(f"  α = {model.params.alpha}")
    print(f"  k_trans = {model.params.k_trans} h/Mpc")
    print(f"  z_activ = {model.params.z_activ}")

    # Pivot point values
    k_pivot, z_pivot = 0.3, 0.3
    sigma_pivot = model.sigma(k_pivot, z_pivot)
    power_ratio = model.power_ratio(k_pivot, z_pivot)

    print(f"\nAt pivot point (k={k_pivot} h/Mpc, z={z_pivot}):")
    print(f"  Σ(k,z) = {sigma_pivot:.4f}")
    print(f"  P_eff/P_ΛCDM = Σ² = {power_ratio:.4f}")

    # Scale dependence
    print("\n" + "-" * 40)
    print("Scale dependence Σ_k(k) at z=0:")
    print("-" * 40)
    print(f"{'k [h/Mpc]':>12}  {'Σ_k':>8}")
    print("-" * 22)
    for k in [0.01, 0.05, 0.10, 0.15, 0.20, 0.30, 0.50]:
        sigma_k = model.sigma_k(k)
        marker = " ← k_trans" if abs(k - 0.1) < 0.01 else ""
        print(f"{k:>12.2f}  {sigma_k:>8.4f}{marker}")

    # Redshift dependence
    print("\n" + "-" * 40)
    print("Redshift dependence Σ_z(z) at k >> k_trans:")
    print("-" * 40)
    print(f"{'z':>8}  {'Σ_z':>8}")
    print("-" * 18)
    for z in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.7, 1.0]:
        sigma_z = model.sigma_z(z)
        marker = " ← z_activ" if abs(z - 0.5) < 0.01 else ""
        print(f"{z:>8.1f}  {sigma_z:>8.4f}{marker}")

    print("\nKey insight: Σ > 1 at low z and high k (nonlinear, late-time regime)")


def demo_s8_reframing():
    """
    Demonstrate how the S8 tension is reframed.

    Standard view: S8 = σ8 × √(Ωm/0.3), with WL and CMB disagreeing.
    Reframed view: S_WL = σ8 × Σ, tension dissolves when Σ ≈ 1.13.
    """
    print("\n" + "=" * 60)
    print("S8 TENSION REFRAMING")
    print("=" * 60)

    reframe = S8Reframing()

    # Standard tension analysis
    print("\n1. STANDARD ANALYSIS (assuming Σ=1)")
    print("-" * 40)

    tension = reframe.standard_tension()
    print(f"  KiDS-1000 S8 = {tension['s8_wl']:.3f} ± 0.024")
    print(f"  Planck S8    = {tension['s8_cmb']:.3f} ± 0.016")
    print(f"  Difference   = {tension['difference']:.3f}")
    print(f"  Tension      = {tension['tension_sigma']:.1f}σ")
    print("  → Significant tension!")

    # Reframed analysis
    print("\n2. REFRAMED ANALYSIS (with Σ correction)")
    print("-" * 40)

    reconciled = reframe.reconcile()
    print(f"  True σ8          = {reconciled['sigma8_true']:.3f}")
    print(f"  Σ at pivot       = {reconciled['sigma_pivot']:.2f}")
    print(f"  S_WL = σ8 × Σ    = {reconciled['sigma8_true']:.3f} × {reconciled['sigma_pivot']:.2f}")
    print(f"                   = {reconciled['s_wl_reframed']:.3f}")
    print(f"  Planck S8        = {reconciled['planck_s8']:.3f}")
    print(f"  Residual tension = {reconciled['residual_tension_sigma']:.1f}σ")
    print(f"  → Tension resolved: {reconciled['tension_resolved']}")

    # Physical interpretation
    print("\n3. PHYSICAL INTERPRETATION")
    print("-" * 40)
    print("  The S8 tension is NOT a discrepancy in σ8.")
    print("  It's a misattribution caused by assuming Σ=1.")
    print("  When lensing response is included, σ8 = 0.734")
    print("  and the 'amplified' WL signal gives S_WL ≈ 0.83.")


def demo_tomographic_fingerprint():
    """
    Demonstrate the tomographic fingerprint of the model.

    Key prediction: Improvement should be strongest at low redshift
    where structures are most evolved.
    """
    print("\n" + "=" * 60)
    print("TOMOGRAPHIC FINGERPRINT")
    print("=" * 60)

    fingerprint = TomographicFingerprint()

    print("\nImprovement per datapoint by redshift bin:")
    print("-" * 40)
    print(f"{'Redshift range':>18}  {'Improvement factor':>20}")
    print("-" * 40)
    print(f"{'Low-z (0.1-0.5)':>18}  {fingerprint.low_z_factor:>20.1f}×")
    print(f"{'High-z (0.7-1.2)':>18}  {fingerprint.high_z_factor:>20.1f}×")

    # Check prediction
    result = fingerprint.prediction_matches()
    print(f"\nRatio: {result['ratio']:.1f}×")
    print(f"Prediction (low-z > high-z): {result['matches_prediction']}")

    print("\nPhysical reason:")
    print("  At low z, structures are more evolved → larger entropy gradients")
    print("  → stronger lensing response modification")
    print("  This is exactly what EFC predicts!")


def demo_likelihood_analysis():
    """
    Demonstrate the likelihood improvement analysis.
    """
    print("\n" + "=" * 60)
    print("LIKELIHOOD ANALYSIS")
    print("=" * 60)

    like = LikelihoodAnalysis()
    summary = like.summary()

    print("\nModel comparison: ΛCDM vs ΛCDM+Σ(k,z)")
    print("-" * 40)
    print(f"  Δ(-2lnL)              = {summary['delta_minus2lnL']:>8.1f}")
    print(f"  Additional parameters = {summary['additional_parameters']:>8d}")
    print(f"  ΔAIC                  = {summary['delta_AIC']:>8.1f}")
    print(f"  ΔBIC                  = {summary['delta_BIC']:>8.1f}")
    print(f"\n  Preferred model: {summary['preferred_model']}")

    print("\nInterpretation:")
    print("  ΔAIC < 0: Model preferred even with parameter penalty")
    print("  ΔBIC < 0: Model preferred even with stronger penalty")
    print("  |Δ(-2lnL)| >> 2×3: Strong evidence for lensing response")


def demo_model_comparison():
    """
    Compare ΛCDM and ΛCDM+Σ model performance.
    """
    print("\n" + "=" * 60)
    print("MODEL COMPARISON SUMMARY")
    print("=" * 60)

    comparison = [
        ("Observable", "ΛCDM", "ΛCDM+Σ"),
        ("-" * 25, "-" * 12, "-" * 12),
        ("Free parameters", "6", "9"),
        ("KiDS-1000 fit", "Reference", "Δχ²=-50.9"),
        ("S8 tension", "2-3σ", "< 1σ"),
        ("Tomographic pattern", "None", "Predicted"),
        ("Physical motivation", "None", "EFC entropy"),
    ]

    print(f"\n{'':>25} {'':>12} {'':>12}")
    for row in comparison:
        print(f"{row[0]:>25} {row[1]:>12} {row[2]:>12}")

    print("\nKey advantage: ΛCDM+Σ provides physical explanation,")
    print("not just better fit. The tomographic fingerprint")
    print("(stronger improvement at low-z) is a prediction, not a tuning.")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# LENSING RESPONSE MODEL DEMONSTRATION")
    print("# From: Magnusson (2026)")
    print("# DOI: 10.6084/m9.figshare.31271917")
    print("#" * 60)

    demo_lensing_response()
    demo_s8_reframing()
    demo_tomographic_fingerprint()
    demo_likelihood_analysis()
    demo_model_comparison()

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("The S8 tension between weak lensing and CMB is resolved by")
    print("recognizing that lensing amplitude depends on Σ(k,z), not just σ8.")
    print("\nWith best-fit α=0.10, k_trans=0.1, z_activ=0.5:")
    print("  • Σ ≈ 1.13 at the pivot")
    print("  • S_WL = σ8 × Σ = 0.734 × 1.13 ≈ 0.83 ≈ Planck")
    print("  • Tomographic pattern matches EFC prediction")
    print("\nThe tension is not in σ8; it's in our assumption that Σ=1.")


if __name__ == "__main__":
    main()
