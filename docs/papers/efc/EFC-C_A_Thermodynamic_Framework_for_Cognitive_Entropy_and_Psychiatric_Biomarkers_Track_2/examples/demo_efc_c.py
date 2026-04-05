#!/usr/bin/env python3
"""Demonstration: EFC-C Cognitive Entropy Framework.

DOI: 10.6084/m9.figshare.31940505
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_cognition import (
    NeuralEntropyProduction, CentrifugalGradient, DisorderSignature,
    EntropyThreshold, FrameworkComparison,
)

def demo_framework_comparison():
    print("=" * 70)
    print("FRAMEWORK COMPARISON (Table 1)")
    print("=" * 70)
    print()
    print(f"{'Framework':<25s} {'Magn':>6s} {'Topo':>6s} {'Grad':>6s} {'Psych':>10s}")
    print("-" * 57)
    for row in FrameworkComparison.comparison_table():
        m = "Y" if row["magnitude"] is True else ("~" if row["magnitude"] else "N")
        t = "Y" if row["topology"] else "N"
        g = "Y" if row["gradient_dir"] else "N"
        print(f"{row['framework']:<25s} {m:>6s} {t:>6s} {g:>6s} {row['psychiatric']:>10s}")
    print()
    print(f"  Key: {FrameworkComparison.key_distinction()}")
    print()

def demo_centrifugal_gradient():
    print("=" * 70)
    print("P1: CENTRIFUGAL ENTROPY GRADIENT")
    print("=" * 70)
    print()
    gradient = CentrifugalGradient.healthy_gradient()
    print("  Healthy resting-state (relative S_dot):")
    for region, value in gradient.items():
        bar = "#" * int(value * 30)
        print(f"    {region:<30s} {value:.2f}  {bar}")
    print()
    print("  Empirical support:")
    for s in CentrifugalGradient.empirical_support():
        print(f"    - {s}")
    print()

def demo_disorder_signatures():
    print("=" * 70)
    print("P2: DISORDER-SPECIFIC GRADIENT SIGNATURES")
    print("=" * 70)
    print()
    for sig_fn in [DisorderSignature.schizophrenia, DisorderSignature.mdd, DisorderSignature.adhd]:
        sig = sig_fn()
        print(f"  {sig.disorder}:")
        print(f"    Type: {sig.gradient_type()}")
        for region, dev in sig.gradient_deviation.items():
            sign = "+" if dev > 0 else ""
            print(f"      {region:<25s} {sign}{dev:.1f}")
        print(f"    Evidence: {sig.observed_evidence}")
        print()

def demo_entropy_threshold():
    print("=" * 70)
    print("P3: ENTROPY THRESHOLD")
    print("=" * 70)
    print()
    threshold = EntropyThreshold(s_dot_star=1.0)
    test_values = [0.3, 0.6, 1.0, 1.2, 1.8]
    for s in test_values:
        state = threshold.cognitive_state(s)
        above = "above" if threshold.is_above_threshold(s) else "BELOW"
        print(f"    S_dot = {s:.1f}  ({above} threshold)  -> {state}")
    print()
    print(f"  Support: {EntropyThreshold.empirical_support()}")
    print()

def demo_neural_entropy():
    print("=" * 70)
    print("NEURAL ENTROPY PRODUCTION (Eq. 1)")
    print("=" * 70)
    print()
    regions = ["DMN", "Salience", "Frontoparietal", "Attention", "Sensorimotor", "Visual", "Auditory"]
    healthy = [1.0, 0.85, 0.75, 0.60, 0.40, 0.30, 0.30]
    schiz = [0.8, 0.65, 0.55, 0.50, 0.40, 0.30, 0.30]

    nep_h = NeuralEntropyProduction(regions, healthy)
    nep_s = NeuralEntropyProduction(regions, schiz)

    print(f"  Healthy: S_dot_neural = {nep_h.s_dot_neural:.2f}")
    print(f"  Schizophrenia: S_dot_neural = {nep_s.s_dot_neural:.2f}")
    print(f"  Hub/periphery ratio (healthy): {nep_h.hub_periphery_ratio(['DMN', 'Salience'], ['Visual', 'Auditory']):.2f}")
    print(f"  Hub/periphery ratio (schiz):   {nep_s.hub_periphery_ratio(['DMN', 'Salience'], ['Visual', 'Auditory']):.2f}")
    print()

if __name__ == "__main__":
    demo_framework_comparison()
    demo_centrifugal_gradient()
    demo_disorder_signatures()
    demo_entropy_threshold()
    demo_neural_entropy()
    print("All demonstrations complete.")
