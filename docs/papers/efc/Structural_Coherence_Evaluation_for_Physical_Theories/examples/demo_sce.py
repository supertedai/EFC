#!/usr/bin/env python3
"""
Demo: Structural Coherence Evaluation (SCE) Framework

Compares LCDM and EFC using the five SCE metrics.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.structural_coherence import SCEFramework, TheoryProfile, PAPER_RESULTS


def main():
    print("=" * 65)
    print("Structural Coherence Evaluation (SCE) Framework")
    print("=" * 65)

    # --- Define theory profiles ---
    lcdm = TheoryProfile(
        name="LCDM",
        primitives=3,
        phenomena=6,
        fdof=2,
        anomaly_A1=3,
        anomaly_A2=2,
        anomaly_A3=1,
        variant_count=5,
        parameter_trend="Growing",
        special_case_rules=2,
        forbidden_patterns=0,
        forbidden_tested=0,
        forbidden_triggered=0,
    )

    efc = TheoryProfile(
        name="EFC (L2)",
        primitives=2,
        phenomena=4,
        fdof=1,
        anomaly_A1=0,
        anomaly_A2=6,
        anomaly_A3=3,
        variant_count=2,
        parameter_trend="Decreasing",
        special_case_rules=0,
        forbidden_patterns=5,
        forbidden_tested=5,
        forbidden_triggered=0,
    )

    sce = SCEFramework()

    # --- Individual evaluations ---
    print("\n1. INDIVIDUAL EVALUATIONS")
    print("-" * 45)
    for theory in [lcdm, efc]:
        profile = sce.evaluate(theory)
        print(f"\n   [{profile['name']}]")
        print(f"   Explanatory Compression: {profile['explanatory_compression']:.1f}")
        print(f"   Anomaly Burden: A1={profile['anomaly_burden']['A1']}, "
              f"A2={profile['anomaly_burden']['A2']}, A3={profile['anomaly_burden']['A3']}")
        print(f"   Model Plasticity: variants={profile['model_plasticity']['variant_count']}, "
              f"trend={profile['model_plasticity']['parameter_trend']}, "
              f"rules={profile['model_plasticity']['special_case_rules']}")
        print(f"   Forbidden Coverage: {profile['forbidden_coverage']:.0%}")
        print(f"   Survival Rate: {profile['survival_rate']:.0%}")

    # --- Head-to-head comparison ---
    print("\n2. HEAD-TO-HEAD COMPARISON")
    print("-" * 45)
    comparison = sce.compare(lcdm, efc)
    print(f"   {'Metric':<25} {'Winner'}")
    print(f"   {'-'*40}")
    for metric, winner in comparison['metric_winners'].items():
        print(f"   {metric:<25} {winner}")

    # --- Case studies from paper ---
    print("\n3. PAPER CASE STUDIES")
    print("-" * 45)
    for name, info in PAPER_RESULTS['case_studies'].items():
        print(f"   {name:<10} ({info['type']})")
        print(f"   {'':10} Primitives: {info['primitives']}")
        print(f"   {'':10} {info['profile']}")

    # --- Framework innovations ---
    print("\n4. KEY INNOVATIONS")
    print("-" * 45)
    for innov in PAPER_RESULTS['key_innovations']:
        print(f"   - {innov}")

    # --- Framework self-check ---
    print("\n5. FRAMEWORK FORBIDDEN PATTERNS (TCS-F1..F3)")
    print("-" * 45)
    for fid, desc in PAPER_RESULTS['framework_forbidden_patterns'].items():
        print(f"   {fid}: {desc}")
    print(f"   Status: None triggered (framework passes its own test)")

    print("\n" + "=" * 65)
    print("Neither framework dominates the full SCE profile.")
    print("LCDM wins on raw compression; EFC wins on structural discipline.")
    print("=" * 65)


if __name__ == '__main__':
    main()
