#!/usr/bin/env python3
"""
ISW Revision Patch - Demonstration

This script demonstrates the key corrections from:
Magnusson (2026) "ISW Paper Revision Patch: Proposed Corrections to
ISW Cross-Correlation Predictions for EFC with DESI DR1 Tracers"
DOI: 10.6084/m9.figshare.31329082
"""

import sys
sys.path.insert(0, '..')

from src.isw_revision import (
    RevisedISWPredictions, ChannelComparison, FalsificationCriteria,
    ValidationLedgerUpdate, MuParameters
)


def demo_revised_predictions():
    """
    Demonstrate the revised A_ISW predictions.

    Key finding: Original z-dependent suppression (44-85%) is replaced
    with uniform ~11% suppression across all tracers.
    """
    print("=" * 60)
    print("REVISED A_ISW PREDICTIONS")
    print("=" * 60)

    predictions = RevisedISWPredictions()

    print("\nComparison of Original vs Revised:")
    print("-" * 50)
    print(predictions.comparison_table())

    # Summary statistics
    summary = predictions.summary()

    print("\n" + "-" * 50)
    print("Summary Statistics:")
    print("-" * 50)
    print(f"  Original A_ISW range:  {summary['A_ISW_original_range'][0]:.2f} – {summary['A_ISW_original_range'][1]:.2f}")
    print(f"  Original suppression:  {summary['suppression_original_percent']:.0f}%")
    print(f"  Revised A_ISW range:   {summary['A_ISW_revised_range'][0]:.2f} – {summary['A_ISW_revised_range'][1]:.2f}")
    print(f"  Revised mean:          {summary['A_ISW_revised_mean']:.2f} ± {summary['A_ISW_revised_std']:.2f}")
    print(f"  Revised suppression:   {summary['suppression_revised_percent']:.0f}%")
    print(f"  z-dependence:          {summary['z_dependence']}")

    print("\nKey insight:")
    print("  The original claim of strong z-dependent suppression (0.56 → 0.15)")
    print("  is NOT reproduced under self-consistent computation.")
    print("  The revised prediction is a UNIFORM ~11% suppression.")


def demo_channel_comparison():
    """
    Demonstrate the two channel interpretations.

    The Audit revealed that growth-driven and potential-driven give
    qualitatively different predictions.
    """
    print("\n" + "=" * 60)
    print("μ-CHANNEL INTERPRETATION")
    print("=" * 60)

    channels = ChannelComparison()
    comparison = channels.comparison_summary()

    print("\n1. GROWTH-DRIVEN (adopted interpretation):")
    print("-" * 50)
    gd = comparison["growth_driven"]
    print(f"  Potential:        {gd['potential_relation']}")
    print(f"  μ role:           {gd['mu_role']}")
    print(f"  ISW source:       {gd['isw_source']}")
    print(f"  A_ISW prediction: {gd['A_ISW']}")
    print(f"  z-dependence:     {gd['z_dependence']}")
    print(f"  Cancellation C:   {gd['cancellation_metric']}")

    print("\n2. POTENTIAL-DRIVEN (MG-type, disfavoured):")
    print("-" * 50)
    pd = comparison["potential_driven"]
    print(f"  Potential:        {pd['potential_relation']}")
    print(f"  Additional term:  {pd['additional_term']}")
    print(f"  Low-z prediction: {pd['prediction_low_z']}")
    print(f"  High-z prediction:{pd['prediction_high_z']}")
    print(f"  Status:           {pd['status']}")

    print("\nKey insight:")
    print("  The potential-driven interpretation predicts ANTI-CORRELATION")
    print("  at z > 0.6, which contradicts existing positive ISW detections.")


def demo_mu_parameterisation():
    """
    Demonstrate the μ(a) parameterisation (unchanged).
    """
    print("\n" + "=" * 60)
    print("μ(a) PARAMETERISATION (unchanged)")
    print("=" * 60)

    mu = MuParameters()

    print(f"\nParameters:")
    print(f"  β   = {mu.beta}")
    print(f"  a_t = {mu.a_t}")
    print(f"  σ   = {mu.sigma}")

    print(f"\nEquation:")
    print(f"  μ(a) = 1 + β × exp[-(a - a_t)² / (2σ²)]")

    print(f"\nSample values:")
    print(f"  {'a':>6}  {'z':>6}  {'μ(a)':>8}  {'dμ/dlna':>10}")
    print(f"  {'-'*6}  {'-'*6}  {'-'*8}  {'-'*10}")

    for a in [0.3, 0.4, 0.5, 0.55, 0.6, 0.7, 0.8, 1.0]:
        z = 1/a - 1
        mu_val = mu.mu(a)
        dmu = mu.dmu_dlna(a)
        print(f"  {a:>6.2f}  {z:>6.2f}  {mu_val:>8.4f}  {dmu:>10.4f}")

    print(f"\n  Peak μ occurs at a = a_t = {mu.a_t} (z ≈ {1/mu.a_t - 1:.2f})")
    print(f"  Peak value: μ_max = 1 + β = {1 + mu.beta:.2f}")


def demo_falsification():
    """
    Demonstrate the revised falsification criteria.
    """
    print("\n" + "=" * 60)
    print("FALSIFICATION CRITERIA")
    print("=" * 60)

    criteria = FalsificationCriteria()
    summary = criteria.summary()

    print("\n1. ORIGINAL CRITERIA (deprecated):")
    print("-" * 50)
    orig = summary["original_deprecated"]
    print(f"  C threshold: > {orig['C_threshold']}")
    print(f"  A threshold: < {orig['A_threshold']} at z_t")
    print(f"  Note: {orig['note']}")

    print("\n2. REVISED CRITERIA:")
    print("-" * 50)
    rev = summary["revised"]
    print(f"  Exclusion: {rev['exclusion']}")
    print(f"  Level:     {rev['exclusion_level']}")
    print(f"  Positive:  {rev['positive_evidence']}")
    print(f"  Key test:  {rev['key_discriminator']}")

    # Test some scenarios
    print("\n3. SCENARIO TESTS:")
    print("-" * 50)

    scenarios = [
        (1.02, 0.05, "Consistent with ΛCDM"),
        (0.95, 0.05, "Marginal"),
        (0.88, 0.05, "Consistent with EFC"),
        (0.85, 0.03, "Strong EFC evidence"),
    ]

    for A_obs, unc, label in scenarios:
        excluded, msg1 = criteria.is_excluded(A_obs, unc)
        positive, msg2 = criteria.is_positive_evidence(A_obs)

        if excluded:
            result = "EFC EXCLUDED"
        elif positive:
            result = "EFC SUPPORTED"
        else:
            result = "Inconclusive"

        print(f"  A_ISW = {A_obs:.2f} ± {unc:.2f}: {result}")


def demo_ledger_update():
    """
    Demonstrate the validation ledger update.
    """
    print("\n" + "=" * 60)
    print("VALIDATION LEDGER UPDATE")
    print("=" * 60)

    changes = ValidationLedgerUpdate.changes()

    print(f"\nVersion: {changes['version_from']} → {changes['version_to']}")
    print("-" * 50)
    print(f"{'Field':<20} {'From':<30} {'To':<30}")
    print("-" * 80)

    for field, values in changes['field_changes'].items():
        from_val = values['from'][:28] if len(values['from']) > 28 else values['from']
        to_val = values['to'][:28] if len(values['to']) > 28 else values['to']
        print(f"{field:<20} {from_val:<30} {to_val:<30}")


def demo_key_findings():
    """
    Summarize the key findings of the revision patch.
    """
    print("\n" + "=" * 60)
    print("KEY FINDINGS SUMMARY")
    print("=" * 60)

    findings = [
        ("1. Original values withdrawn",
         "A_ISW = 0.56 → 0.15 cannot be reproduced under self-consistent computation"),
        ("2. Revised prediction",
         "A_ISW ≈ 0.89 ± 0.03 (uniform ~11% suppression, z-independent)"),
        ("3. Channel clarification",
         "Growth-driven (adopted) vs potential-driven (disfavoured)"),
        ("4. Cancellation metric",
         "Not applicable under growth-driven interpretation"),
        ("5. Falsification revised",
         "A_ISW = 1.00 ± 0.05 → EFC excluded at >2σ"),
        ("6. Preserved elements",
         "Growth ODE, μ(a) params, Limber approx, tracers, H(a)"),
    ]

    for title, detail in findings:
        print(f"\n{title}:")
        print(f"  {detail}")


def main():
    """Run all demonstrations."""
    print("\n" + "#" * 60)
    print("# ISW REVISION PATCH DEMONSTRATION")
    print("# DOI: 10.6084/m9.figshare.31329082")
    print("#" * 60)

    demo_revised_predictions()
    demo_channel_comparison()
    demo_mu_parameterisation()
    demo_falsification()
    demo_ledger_update()
    demo_key_findings()

    print("\n" + "=" * 60)
    print("CONCLUSION")
    print("=" * 60)
    print("The ISW Consistency Audit revealed that the original paper's")
    print("strong z-dependent suppression was not reproducible.")
    print("\nThe CORRECTED EFC prediction is:")
    print("  • A_ISW ≈ 0.89 ± 0.03 across ALL DESI DR1 tracer bins")
    print("  • Uniform ~11% suppression relative to ΛCDM")
    print("  • NO significant z-dependence")
    print("\nThis is testable with combined multi-tracer ISW analysis.")


if __name__ == "__main__":
    main()
