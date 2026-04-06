#!/usr/bin/env python3
"""
Entropy-Structure Coupling - Demonstration

This script demonstrates the key concepts from:
Magnusson (2026) "A Pre-Registered Test of Entropy–Structure Coupling
in Simulated and Observed Galaxy Clusters"
DOI: 10.6084/m9.figshare.31286368
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.entropy_structure_coupling import (
    EntropyProfileModel, AlphaProxy, CoolCoreClassifier, CoolCoreClass,
    CorrelationAnalysis, PreRegisteredTest, InterpretationFramework,
    compute_entropy, classify_cool_core
)


def demo_entropy_profile():
    """
    Demonstrate the Cavagnolo et al. (2009) entropy profile model.

    K(r) = K0 + K100 × (r / 100 kpc)^α
    """
    print("=" * 60)
    print("ENTROPY PROFILE MODEL (Cavagnolo et al. 2009)")
    print("=" * 60)

    # Typical cool-core cluster parameters
    model_cc = EntropyProfileModel(K0=10.0, K100=100.0, alpha=1.1)

    # Typical non-cool-core cluster parameters
    model_ncc = EntropyProfileModel(K0=200.0, K100=80.0, alpha=0.9)

    print("\nCool-core cluster:")
    print(f"  K0 = {model_cc.params.K0} keV cm²")
    print(f"  K100 = {model_cc.params.K100} keV cm²")
    print(f"  α = {model_cc.params.alpha}")

    print("\nNon-cool-core cluster:")
    print(f"  K0 = {model_ncc.params.K0} keV cm²")
    print(f"  K100 = {model_ncc.params.K100} keV cm²")
    print(f"  α = {model_ncc.params.alpha}")

    # Compute entropy at various radii
    print("\n" + "-" * 40)
    print("Entropy profiles K(r) [keV cm²]:")
    print("-" * 40)
    print(f"{'r [kpc]':>10}  {'CC cluster':>12}  {'NCC cluster':>12}")
    print("-" * 36)

    for r in [10, 20, 50, 100, 200, 400]:
        K_cc = model_cc.entropy(r)
        K_ncc = model_ncc.entropy(r)
        print(f"{r:>10}  {K_cc:>12.1f}  {K_ncc:>12.1f}")

    print("\nKey insight: CC clusters have steep gradients (low K0, high α)")
    print("             NCC clusters have flat profiles (high K0, lower α)")


def demo_cool_core_classification():
    """
    Demonstrate cool-core classification following Hudson et al. (2010).
    """
    print("\n" + "=" * 60)
    print("COOL-CORE CLASSIFICATION (Hudson et al. 2010)")
    print("=" * 60)

    classifier = CoolCoreClassifier()

    print("\nClassification thresholds:")
    print("  SCC (Strong Cool-Core):  K0 ≤ 22 keV cm²")
    print("  WCC (Weak Cool-Core):    22 < K0 ≤ 150 keV cm²")
    print("  NCC (Non-Cool-Core):     K0 > 150 keV cm²")

    print("\n" + "-" * 40)
    print("Example classifications:")
    print("-" * 40)

    test_values = [10, 22, 50, 100, 150, 200, 300]
    for K0 in test_values:
        cc_class = classifier.classify(K0)
        print(f"  K0 = {K0:>4} keV cm² → {cc_class.name} ({cc_class.value})")

    # TNG-Cluster population
    print("\n" + "-" * 40)
    print("TNG-Cluster population (352 halos at z=0):")
    print("-" * 40)
    pop = classifier.tng_population()
    print(f"  SCC: {pop['SCC']['count']:>4} ({pop['SCC']['fraction']*100:.0f}%)")
    print(f"  WCC: {pop['WCC']['count']:>4} ({pop['WCC']['fraction']*100:.0f}%)")
    print(f"  NCC: {pop['NCC']['count']:>4} ({pop['NCC']['fraction']*100:.0f}%)")


def demo_alpha_proxy():
    """
    Demonstrate the α_proxy definition for entropy gradient.
    """
    print("\n" + "=" * 60)
    print("ALPHA PROXY DEFINITION")
    print("=" * 60)

    print("\nEntropy slope decomposition:")
    print("  α = d ln K / d ln r = d ln T / d ln r + (2/3) × (-d ln n_e / d ln r)")
    print("\nProxy definition:")
    print("  α_proxy = (2/3) × n_e-slope")
    print("\nPhysical interpretation:")
    print("  - Represents density contribution to entropy gradient")
    print("  - Lower bound on α (assuming T increases with r in cores)")

    print("\n" + "-" * 40)
    print("Example calculations:")
    print("-" * 40)

    ne_slopes = [0.3, 0.5, 1.0, 1.5, 2.0, 2.5]
    print(f"{'n_e-slope':>12}  {'α_proxy':>10}")
    print("-" * 24)
    for ne_slope in ne_slopes:
        alpha_proxy = AlphaProxy.compute(ne_slope)
        print(f"{ne_slope:>12.1f}  {alpha_proxy:>10.3f}")

    print("\nTNG-Cluster α_proxy distribution:")
    print("  Min: -0.23, Max: 1.60, Median: 0.31")
    print("  ACCEPT median α ~ 1.1")


def demo_sign_flip():
    """
    Demonstrate the key finding: sign flip in entropy-structure coupling.
    """
    print("\n" + "=" * 60)
    print("SIGN FLIP: THE KEY FINDING")
    print("=" * 60)

    analysis = CorrelationAnalysis()

    tng = analysis.tng_correlation("ne_slope_vs_K0")
    accept = analysis.accept_correlation()

    print("\nCorrelation between entropy gradient steepness and cool-core state:")
    print("\n" + "-" * 50)
    print(f"{'Dataset':>20}  {'Correlation':>15}  {'Sign':>8}")
    print("-" * 50)
    print(f"{'TNG-Cluster':>20}  ρ = {tng.rho:>+.3f}       {'NEGATIVE':>8}")
    print(f"{'ACCEPT (observed)':>20}  ρ = {accept.rho:>+.3f}       {'POSITIVE':>8}")
    print("-" * 50)

    print("\n⚠️  COMPLETE SIGN REVERSAL!")
    print("\nInterpretation:")
    print("  In OBSERVATIONS: Steeper profiles → higher cooling times")
    print("  In SIMULATIONS:  Steeper profiles → lower cooling times")

    print("\nStatistical significance:")
    print(f"  TNG: p ~ {tng.p_value:.0e} (N = {tng.N})")
    print("  This is NOT a statistical fluctuation!")


def demo_robustness():
    """
    Demonstrate robustness tests for the sign flip.
    """
    print("\n" + "=" * 60)
    print("ROBUSTNESS TESTS")
    print("=" * 60)

    analysis = CorrelationAnalysis()

    print("\n1. MASS CONFOUNDING TEST")
    print("-" * 40)
    summary = analysis.summary()
    print(f"  Raw correlation:     ρ = {summary['tng_rho']:.3f}")
    print(f"  Mass-controlled:     ρ = {summary['partial_rho_mass_controlled']:.3f}")
    print(f"  Mass contribution:   {summary['mass_contribution']}")
    print("  → Mass does NOT explain the sign flip")

    print("\n2. MASS-BINNED ANALYSIS")
    print("-" * 40)
    print(f"{'Mass bin':>15}  {'N':>5}  {'ρ':>8}")
    print("-" * 32)
    for bin_result in analysis.mass_binned_results():
        print(f"{bin_result['bin']:>15}  {bin_result['N']:>5}  {bin_result['rho']:>+8.3f}")
    print("-" * 32)
    print("  → ALL bins show negative correlations")

    print("\n3. DEFINITION MATCHING")
    print("-" * 40)
    print("  Using α_proxy = (2/3) × n_e-slope:")
    print(f"    ρ(α_proxy, K0) raw:       {-0.872:+.3f}")
    print(f"    ρ(α_proxy, K0) partial|M: {-0.880:+.3f}")
    print(f"    ρ(α_proxy, tcool) raw:    {-0.878:+.3f}")
    print("  → Sign flip persists under proxy definition matching")


def demo_pre_registered_test():
    """
    Demonstrate the pre-registered test design.
    """
    print("\n" + "=" * 60)
    print("PRE-REGISTERED TEST DESIGN")
    print("=" * 60)

    test = PreRegisteredTest()

    print("\nTWO-STAGE APPROACH:")

    # Path B
    print("\n1. PATH B: Proxy-Based Pre-Test")
    print("-" * 40)
    path_b = test.path_b_summary()
    print(f"  Status: {path_b['status']}")
    print(f"  Proxy:  {path_b['proxy']}")
    print(f"  Result: {path_b['result']}")
    print(f"  Verdict: {path_b['verdict']}")

    # Path A
    print("\n2. PATH A: Decisive Full Profile Fit")
    print("-" * 40)
    path_a = test.path_a_summary()
    print(f"  Status: {path_a['status']}")
    print(f"  Method: {path_a['description']}")
    print("  Locked parameters:")
    for key, value in path_a['parameters'].items():
        print(f"    {key}: {value}")

    print("\n3. STOP/GO CRITERION")
    print("-" * 40)
    print("  STOP:    ρ(α_fit, K0) > 0 AND ρ(α_fit, tcool) > 0")
    print("           → Sign flip reverses under definition matching")
    print("  GO:      ρ(α_fit, K0) < 0")
    print("           → Sign flip survives (genuine sim-obs mismatch)")
    print("  PARTIAL: Mixed signs → further investigation needed")


def demo_interpretation():
    """
    Demonstrate the interpretation framework.
    """
    print("\n" + "=" * 60)
    print("INTERPRETATION FRAMEWORK")
    print("=" * 60)

    framework = InterpretationFramework()

    print("\nIf sign flip is confirmed by Path A, three explanations:")
    print()

    for i, explanation in enumerate(framework.POSSIBLE_EXPLANATIONS, 1):
        print(f"{i}. {explanation['name'].upper()}")
        print(f"   {explanation['description']}")
        print(f"   Testable via: {explanation['testable']}")
        print()

    print("-" * 60)
    print("KEY IMPLICATION:")
    print("-" * 60)
    print(framework.get_implications())


def demo_ks_test():
    """
    Demonstrate the Kolmogorov-Smirnov test between CC populations.
    """
    print("\n" + "=" * 60)
    print("POPULATION SEPARATION TEST")
    print("=" * 60)

    print("\nKolmogorov-Smirnov test: SCC vs NCC density slopes")
    print("-" * 40)
    print("  D statistic: 1.000")
    print("  p-value:     2.4 × 10⁻³⁰")
    print()
    print("  Interpretation: COMPLETE SEPARATION")
    print("  SCC and NCC clusters have entirely non-overlapping")
    print("  density slope distributions in TNG-Cluster.")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# ENTROPY-STRUCTURE COUPLING DEMONSTRATION")
    print("# From: Magnusson (2026)")
    print("# DOI: 10.6084/m9.figshare.31286368")
    print("#" * 60)

    demo_entropy_profile()
    demo_cool_core_classification()
    demo_alpha_proxy()
    demo_sign_flip()
    demo_robustness()
    demo_pre_registered_test()
    demo_ks_test()
    demo_interpretation()

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
TNG-Cluster shows a STRONG NEGATIVE correlation between entropy
gradient steepness and cool-core state (ρ = -0.87), while ACCEPT
observations show a POSITIVE correlation (ρ = +0.36).

This sign flip is:
  ✓ Not driven by mass confounding
  ✓ Consistent across all mass bins
  ✓ Preserved under proxy definition matching

The pre-registered Path A test will determine whether this represents
a genuine simulation-observation mismatch in ICM physics.

If confirmed, the question arises: Why do modern ΛCDM hydrodynamic
simulations not reproduce the observed entropy-structure coupling
in galaxy clusters?
""")


if __name__ == "__main__":
    main()
