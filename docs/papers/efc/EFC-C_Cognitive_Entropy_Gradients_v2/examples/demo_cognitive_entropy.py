#!/usr/bin/env python3
"""
Demo: EFC-C v2.0 Cognitive Entropy Gradients
===============================================
Demonstrates centrifugal entropy score kappa and connectome-constrained predictions.

Track 2: Neural Entropy
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cognitive_entropy import (
    CentrifugalEntropyScore,
    BridgeB1Star,
    ConnectomeParameters,
    DisorderPrediction,
    CognitiveCoherenceThreshold,
    EFCC_Framework,
)


def demo_centrifugal_entropy():
    """1. Centrifugal entropy score kappa."""
    print("=" * 65)
    print("DEMO 1: Centrifugal Entropy Score")
    print("=" * 65)

    # Simulated hub and peripheral entropy values
    S_hub = [1.8, 1.9, 1.7, 2.0, 1.85]
    S_periph = [1.1, 1.0, 1.15, 0.95, 1.05, 1.1, 0.98, 1.02]

    ces = CentrifugalEntropyScore(S_hub, S_periph)
    info = ces.info()

    print(f"  Mean S_hub:    {info['mean_S_hub']:.3f} (n={info['n_hub']})")
    print(f"  Mean S_periph: {info['mean_S_periph']:.3f} (n={info['n_periph']})")
    print(f"  kappa:         {info['kappa']:.3f}")
    print(f"  Interpretation: {info['interpretation']}")
    print()

    assert info["kappa"] > 1.0, "Hub entropy should exceed peripheral"
    assert info["interpretation"] == "centrifugal", "Should be centrifugal gradient"
    print("  [PASS] Centrifugal entropy assertions passed\n")


def demo_bridge_b1_star():
    """2. Bridge B1* equation: kappa = C / (1 + lambda_2 * tau_c)."""
    print("=" * 65)
    print("DEMO 2: Bridge B1* Equation")
    print("=" * 65)

    bridge = BridgeB1Star(C=4.4, C_uncertainty=0.6)

    print("  Kappa prediction table (from paper Section 3.1):")
    print(f"  {'lambda_2':>10s}  {'tau_c':>8s}  {'kappa':>8s}")
    print(f"  {'-'*10}  {'-'*8}  {'-'*8}")

    table = bridge.kappa_table()
    for row in table:
        print(f"  {row['lambda_2']:10.1f}  {row['tau_c']:8.1f}  {row['kappa_pred']:8.2f}")
    print()

    # Central prediction: lambda_2=0.5, tau_c=3.5 -> kappa ~ 1.6
    kappa_central = bridge.kappa(0.5, 3.5)
    print(f"  Central prediction: kappa({0.5}, {3.5}) = {kappa_central:.4f}")

    lo, mid, hi = bridge.kappa_range(0.5, 3.5)
    print(f"  With uncertainty:   [{lo:.3f}, {mid:.3f}, {hi:.3f}]")
    print()

    assert abs(kappa_central - 1.6) < 0.01, f"Expected ~1.6, got {kappa_central}"
    assert table[0]["kappa_pred"] == 2.75, "lambda_2=0.3 should give 2.75"
    assert table[2]["kappa_pred"] == 0.88, "lambda_2=0.8 should give 0.88"
    print("  [PASS] Bridge B1* assertions passed\n")


def demo_connectome_parameters():
    """3. Connectome parameters and tau_c derivation."""
    print("=" * 65)
    print("DEMO 3: Connectome Parameters")
    print("=" * 65)

    cp = ConnectomeParameters(lambda_2=0.5, n_regions=360)
    info = cp.info()

    print(f"  lambda_2:  {info['lambda_2']}")
    print(f"  N regions: {info['n_regions']}")
    print(f"  N hub:     {info['n_hub']} (top 10%)")
    print(f"  N periph:  {info['n_periph']} (bottom 30%)")
    print(f"  tau_c:     {info['tau_c_s']:.2f} s (L=5mm, D_eff=3mm/s)")
    print()

    assert info["n_hub"] == 36, f"Expected 36 hub nodes, got {info['n_hub']}"
    assert info["n_periph"] == 108, f"Expected 108 periph nodes, got {info['n_periph']}"
    assert abs(info["tau_c_s"] - 25.0 / 3.0) < 0.01
    print("  [PASS] Connectome parameter assertions passed\n")


def demo_disorder_predictions():
    """4. Disorder-specific kappa predictions (Q2)."""
    print("=" * 65)
    print("DEMO 4: Disorder Predictions")
    print("=" * 65)

    dp = DisorderPrediction()
    results = dp.discrimination_test(tau_c=3.5)

    print(f"  {'Disorder':>15s}  {'lambda_2':>10s}  {'kappa':>8s}  {'delta_kappa':>12s}")
    print(f"  {'-'*15}  {'-'*10}  {'-'*8}  {'-'*12}")
    for name, r in results.items():
        print(f"  {name:>15s}  {r['lambda_2']:10.2f}  {r['kappa_predicted']:8.3f}  {r['delta_kappa']:12.3f}")
    print()

    # Schizophrenia: reduced lambda_2 -> elevated kappa
    scz = results["schizophrenia"]
    healthy = results["healthy"]
    assert scz["kappa_predicted"] > healthy["kappa_predicted"], \
        "Schizophrenia kappa should be elevated (reduced short-circuiting)"

    # MDD: also elevated but different magnitude
    mdd = results["MDD"]
    assert mdd["kappa_predicted"] > healthy["kappa_predicted"], \
        "MDD kappa should be elevated"
    assert scz["kappa_predicted"] > mdd["kappa_predicted"], \
        "Schizophrenia elevation should exceed MDD"

    print("  [PASS] Disorder prediction assertions passed\n")


def demo_coherence_threshold():
    """5. Cognitive coherence threshold (Q3)."""
    print("=" * 65)
    print("DEMO 5: Cognitive Coherence Threshold")
    print("=" * 65)

    threshold = CognitiveCoherenceThreshold(C=4.4, lambda_2_max=1.0, tau_c_max=5.0)
    print(f"  kappa_crit = {threshold.kappa_crit:.4f}")
    print()

    # Healthy: kappa = 1.6, should be above threshold
    r_healthy = threshold.evaluate(1.6)
    print(f"  Healthy (kappa=1.6): below={r_healthy['below_threshold']}, "
          f"interp={r_healthy['interpretation']}")

    # Disorders of consciousness: kappa = 0.5
    r_doc = threshold.evaluate(0.5)
    print(f"  DoC (kappa=0.5):     below={r_doc['below_threshold']}, "
          f"interp={r_doc['interpretation']}")
    print()

    assert abs(threshold.kappa_crit - 0.7333) < 0.01, \
        f"Expected ~0.73, got {threshold.kappa_crit}"
    assert r_healthy["below_threshold"] is False
    assert r_doc["below_threshold"] is True
    print("  [PASS] Coherence threshold assertions passed\n")


def demo_full_framework():
    """6. Complete EFC-C v2 framework."""
    print("=" * 65)
    print("DEMO 6: Full EFC-C v2 Framework")
    print("=" * 65)

    fw = EFCC_Framework(C=4.4, C_uncertainty=0.6)
    report = fw.full_report(lambda_2=0.5, tau_c=3.5)

    q1 = report["Q1_healthy"]
    print(f"  Q1 healthy kappa: {q1['kappa_predicted']} "
          f"(range: {q1['kappa_range']})")

    q2 = report["Q2_disorders"]
    for name, r in q2.items():
        print(f"  Q2 {name}: kappa={r['kappa_predicted']}")

    print(f"  Q3 threshold: {report['Q3_coherence_threshold']:.4f}")
    print()

    assert abs(q1["kappa_predicted"] - 1.6) < 0.01
    assert report["Q3_coherence_threshold"] < 1.0
    print("  [PASS] Full framework assertions passed\n")


if __name__ == "__main__":
    print()
    print("EFC-C v2.0: Cognitive Entropy Gradients Demo")
    print("Track 2: Neural Entropy")
    print()

    demo_centrifugal_entropy()
    demo_bridge_b1_star()
    demo_connectome_parameters()
    demo_disorder_predictions()
    demo_coherence_threshold()
    demo_full_framework()

    print("=" * 65)
    print("ALL DEMOS PASSED")
    print("=" * 65)
