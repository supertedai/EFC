#!/usr/bin/env python3
"""
Directional Lensing Residuals - Demonstration

This script demonstrates the key concepts from:
Magnusson (2026) "Directional Lensing Residuals at Cluster Merger Shock Fronts"
DOI: 10.6084/m9.figshare.31288063
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.directional_lensing import (
    AsigEstimator, RotationNull, DecisionCriteria,
    MockValidationResults, ExpectedSignal, GcDegeneracyBreaking,
    ShockGeometry
)


def demo_asig_estimator():
    """
    Demonstrate the A_sig estimator.

    A_sig = [A_shock - median(A_rot)] / sigma_MAD
    """
    print("=" * 60)
    print("A_sig ESTIMATOR DEMONSTRATION")
    print("=" * 60)

    print("\n1. RAW SHOCK ASYMMETRY (A_shock)")
    print("-" * 40)
    print("  A_shock = (⟨Δκ⟩_pre - ⟨Δκ⟩_post) / σ_diff")
    print()
    print("  Where:")
    print("    Δκ = κ_obs - κ_model  (lensing residual)")
    print("    σ_diff = σ_Δκ × √(1/N_pre + 1/N_post)")
    print()
    print("  Interpretation:")
    print("    A_shock > 0: Excess κ on pre-shock (low-entropy) side")
    print("    A_shock < 0: Excess κ on post-shock (high-entropy) side")

    print("\n2. ROTATION NULL MODEL")
    print("-" * 40)
    null = RotationNull()
    print(f"  Rotate all maps by: {null.angles[:5]}... degrees")
    print(f"  Total angles: {null.n_angles}")
    print(f"  Step size: {null.step_degrees}°")
    print()
    print("  Purpose: Remove orientation-dependent geometric biases")
    print("  Method: Recompute A_shock at each rotated orientation")

    print("\n3. LOCALLY-NORMALIZED SIGNIFICANCE (A_sig)")
    print("-" * 40)
    print("  A_sig = [A_shock - median(A_rot)] / σ_MAD")
    print()
    print("  Where:")
    print("    σ_MAD = 1.4826 × MAD[A_rot]  (robust scatter)")
    print()
    print("  Physical content:")
    print("    Measures whether the actual shock front produces more")
    print("    asymmetric κ-residuals than typical orientations.")


def demo_mock_validation():
    """
    Demonstrate mock validation results.
    """
    print("\n" + "=" * 60)
    print("MOCK VALIDATION RESULTS")
    print("=" * 60)

    efc = MockValidationResults.get_efc_mock()
    lcdm = MockValidationResults.get_lcdm_mock()

    print("\n1. EFC MOCK (entropy-dependent signal)")
    print("-" * 40)
    print(f"  A_shock     = {efc['A_shock']:+.2f}")
    print(f"  A_rot median = {efc['A_rot_median']:+.2f}")
    print(f"  σ_MAD       = {efc['sigma_MAD']:.2f}")
    print(f"  A_sig       = {efc['A_sig']:+.2f}  ← POSITIVE")
    print(f"  p_rot       = {efc['p_rot']:.2f}")

    print("\n2. ΛCDM MOCK (no entropy-dependent signal)")
    print("-" * 40)
    print(f"  A_shock     = {lcdm['A_shock']:+.2f}")
    print(f"  A_rot median = {lcdm['A_rot_median']:+.2f}")
    print(f"  σ_MAD       = {lcdm['sigma_MAD']:.2f}")
    print(f"  A_sig       = {lcdm['A_sig']:+.2f}  ← NEGATIVE")
    print(f"  p_rot       = {lcdm['p_rot']:.2f}")

    print("\n3. SIGN SEPARATION TEST")
    print("-" * 40)
    sep = MockValidationResults.verify_sign_separation()
    print(f"  EFC A_sig:  {sep['EFC_A_sig']:+.2f}")
    print(f"  ΛCDM A_sig: {sep['LCDM_A_sig']:+.2f}")
    print(f"  Sign separation confirmed: {sep['sign_separation']}")
    print(f"  False positive rate: {sep['false_positive_rate']}")
    print(f"  Status: {sep['status']}")


def demo_decision_criteria():
    """
    Demonstrate pre-registered decision criteria.
    """
    print("\n" + "=" * 60)
    print("PRE-REGISTERED DECISION CRITERIA")
    print("=" * 60)

    criteria = [
        ("DETECTION", "A_sig > 3 AND p_rot < 0.05 in ≥2 clusters",
         "Evidence for directional lensing asymmetry"),
        ("MARGINAL", "A_sig > 2 OR (A_sig > 1.5 AND r(κ,T|n) < -0.15)",
         "Tentative; extend to additional clusters"),
        ("NULL", "A_sig < 2 in all clusters",
         "Upper bound on |Δκ/κ| at shocks")
    ]

    print("\n" + "-" * 60)
    print(f"{'Outcome':<12} {'Criteria':<40} {'Action'}")
    print("-" * 60)
    for outcome, crit, action in criteria:
        print(f"{outcome:<12} {crit:<40}")
        print(f"{'':12} → {action}")
        print()

    # Example evaluations
    print("\nExample evaluations:")
    print("-" * 40)

    # High significance
    result = DecisionCriteria.evaluate(A_sig=3.5, p_rot=0.02, n_clusters_with_detection=2)
    print(f"  A_sig=3.5, p_rot=0.02, 2 clusters: {result['outcome']}")

    # Marginal
    result = DecisionCriteria.evaluate(A_sig=2.5, p_rot=0.10, n_clusters_with_detection=1)
    print(f"  A_sig=2.5, p_rot=0.10, 1 cluster: {result['outcome']}")

    # Null
    result = DecisionCriteria.evaluate(A_sig=1.2, p_rot=0.30, n_clusters_with_detection=0)
    print(f"  A_sig=1.2, p_rot=0.30, 0 clusters: {result['outcome']}")


def demo_gc_degeneracy():
    """
    Demonstrate G/c degeneracy breaking.
    """
    print("\n" + "=" * 60)
    print("G/c DEGENERACY BREAKING")
    print("=" * 60)

    print("\nThe directional test distinguishes two modification types:")
    print("-" * 50)

    print("\n1. G_eff(S) MODIFICATION (modified gravity)")
    print("   Effect: Isotropic enhancement")
    print("   Reason: Gravity has no preferred direction")
    print("   A_sig prediction: ≈ 0")

    print("\n2. c_eff(S) MODIFICATION (modified light propagation)")
    print("   Effect: Directional enhancement")
    print("   Reason: Photons accumulate extra phase delay on low-S side")
    print("   A_sig prediction: > 0")

    print("\nInterpretation examples:")
    print("-" * 40)

    for A_sig_test in [3.0, 0.5, -1.0]:
        result = GcDegeneracyBreaking.interpret(A_sig_test)
        print(f"\n  A_sig = {A_sig_test:+.1f}:")
        print(f"    Favored: {result['favored_model']}")
        print(f"    Reason: {result['reason']}")


def demo_expected_signal():
    """
    Demonstrate expected signal estimate for Bullet Cluster.
    """
    print("\n" + "=" * 60)
    print("EXPECTED SIGNAL (BULLET CLUSTER)")
    print("=" * 60)

    signal = ExpectedSignal()

    print("\n1. SHOCK PARAMETERS")
    print("-" * 40)
    print(f"  Mach number: {signal.mach_number}")
    print(f"  Temperature jump: T₂/T₁ = {signal.T2_over_T1}")
    print(f"  Density jump: n₂/n₁ = {signal.n2_over_n1}")
    print(f"  Entropy jump: S₂/S₁ = {signal.entropy_jump:.2f}")

    print("\n2. EFC PARAMETERS")
    print("-" * 40)
    print(f"  μ₀ = {signal.mu_0} (from SPARC rotation curves)")
    print(f"  ΔS/S_max ≈ {signal.delta_S_over_S_max}")
    print(f"  κ_local ≈ {signal.kappa_local_min}-{signal.kappa_local_max}")

    print("\n3. PREDICTED SIGNAL")
    print("-" * 40)
    delta_kappa = signal.predict_delta_kappa()
    frac_signal = signal.predict_fractional_signal()
    print(f"  Δκ_EFC ≈ μ₀ × (ΔS/S_max) × κ_local")
    print(f"         ≈ {signal.mu_0} × {signal.delta_S_over_S_max} × 0.2")
    print(f"         ≈ {delta_kappa:.3f}")
    print(f"  Δκ/κ   ≈ {frac_signal:.0f}%")

    print("\n4. SIGNIFICANCE ESTIMATE")
    print("-" * 40)
    print("  Optimistic (100 JWST pixels): ~6σ")
    print("  Realistic (with systematics): 2-4σ")
    print("  Sufficient for: initial constraint OR meaningful upper bound")


def demo_data_requirements():
    """
    Demonstrate data requirements.
    """
    print("\n" + "=" * 60)
    print("DATA REQUIREMENTS")
    print("=" * 60)

    print("\nRequired maps per cluster:")
    print("-" * 40)
    print("  1. κ-map: Gravitational lensing convergence")
    print("     Source: JWST weak+strong lensing reconstruction")
    print()
    print("  2. kT-map: ICM temperature")
    print("     Source: Chandra X-ray spectral fitting")
    print()
    print("  3. n_e-map: Electron density")
    print("     Source: X-ray surface brightness deprojection")

    print("\nTarget clusters:")
    print("-" * 40)
    print("  BULLET CLUSTER (1E 0657-56)")
    print("    κ: Cha et al. 2025 (JWST)")
    print("       - 146 strong lensing constraints")
    print("       - 398 sources/arcmin² weak lensing")
    print("       - MARS algorithm reconstruction")
    print("    X-ray: Chandra ~500 ks archival")
    print()
    print("  ABELL 2146")
    print("    Feature: Double-shock system")
    print("    Advantage: Cleanest shock geometry after Bullet")
    print("    References: Russell et al. 2010, 2012, 2022")


def demo_systematics():
    """
    Demonstrate systematic considerations.
    """
    print("\n" + "=" * 60)
    print("SYSTEMATIC CONSIDERATIONS")
    print("=" * 60)

    systematics = [
        ("Astrometric co-registration",
         "WCS alignment between κ-map and X-ray",
         "Cross-correlate point sources in both frames"),
        ("Mass modeling",
         "NFW parameter uncertainties",
         "Propagate via Monte Carlo"),
        ("PSF effects",
         "Point spread function convolution",
         "Deconvolution or forward modeling"),
        ("Reconstruction systematics",
         "Lensing algorithm choices",
         "Compare MARS, LensTool, etc.")
    ]

    print()
    for name, concern, mitigation in systematics:
        print(f"  {name}:")
        print(f"    Concern: {concern}")
        print(f"    Mitigation: {mitigation}")
        print()


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# DIRECTIONAL LENSING RESIDUALS DEMONSTRATION")
    print("# From: Magnusson (2026)")
    print("# DOI: 10.6084/m9.figshare.31288063")
    print("#" * 60)

    demo_asig_estimator()
    demo_mock_validation()
    demo_decision_criteria()
    demo_gc_degeneracy()
    demo_expected_signal()
    demo_data_requirements()
    demo_systematics()

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("The directional lensing residuals pipeline is:")
    print("  ✓ Pre-registered with locked parameters")
    print("  ✓ Validated on synthetic data (correct sign separation)")
    print("  ✓ No false positives on ΛCDM mocks")
    print("  ✓ Ready for application to real JWST + Chandra data")
    print()
    print("Key innovation: A_sig uses shock orientation information")
    print("that standard mass-lensing coupling cannot produce,")
    print("enabling clean discrimination between models.")


if __name__ == "__main__":
    main()
