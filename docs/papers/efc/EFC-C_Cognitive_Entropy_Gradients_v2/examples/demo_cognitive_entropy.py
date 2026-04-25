#!/usr/bin/env python3
"""
Demo: EFC-C v2.1 Cognitive Entropy Gradients
=============================================
Bridge B1** (degree-heterogeneity formulation): kappa = C_eff * D_ratio^gamma

DOI: 10.6084/m9.figshare.32091700 (v2)
Track 2: Neural Entropy
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.cognitive_entropy import (
    CentrifugalEntropyScore,
    DegreeRatio,
    BridgeB1DoubleStar,
    LayerAPredictions,
    LayerBPredictions,
    EFCC_v21_Framework,
)


def demo_centrifugal_entropy():
    """1. Centrifugal entropy score kappa."""
    print("=" * 65)
    print("DEMO 1: Centrifugal Entropy Score")
    print("=" * 65)

    S_hub = [2.18, 2.25, 2.20, 2.15, 2.22]
    S_periph = [1.05, 0.98, 1.02, 1.00, 1.08, 0.95, 1.01, 1.04]

    ces = CentrifugalEntropyScore(S_hub, S_periph)
    info = ces.info()
    print(f"  Mean S_hub:    {info['mean_S_hub']:.3f} (n={info['n_hub']})")
    print(f"  Mean S_periph: {info['mean_S_periph']:.3f} (n={info['n_periph']})")
    print(f"  kappa:         {info['kappa']:.3f}")
    print(f"  Interpretation: {info['interpretation']}")
    print()
    assert info["kappa"] > 1.0
    assert info["interpretation"] == "centrifugal"
    print("  [PASS] Centrifugal entropy assertions passed\n")


def demo_degree_ratio():
    """2. Hub-to-periphery degree ratio D_ratio."""
    print("=" * 65)
    print("DEMO 2: Degree Ratio")
    print("=" * 65)

    degrees = [120, 110, 100, 95, 88, 82, 75, 70, 65, 60, 55, 48, 40, 32, 25, 18]
    dr = DegreeRatio(degrees)
    print(f"  N parcels: {len(degrees)}")
    print(f"  hub set (top 10%): {len(dr.k_hub)} parcel(s), mean degree {dr.mean_k_hub:.2f}")
    print(f"  periph set (bottom 30%): {len(dr.k_periph)} parcels, mean degree {dr.mean_k_periph:.2f}")
    print(f"  D_ratio:   {dr.D_ratio:.3f}")
    print()
    assert dr.D_ratio > 1.0
    print("  [PASS] D_ratio assertions passed\n")


def demo_bridge_b1_double_star():
    """3. Bridge B1**: kappa = C_eff * D_ratio^gamma."""
    print("=" * 65)
    print("DEMO 3: Bridge B1** (degree-heterogeneity)")
    print("=" * 65)

    bridge = BridgeB1DoubleStar(C_eff=2.0, gamma=0.55)
    print("  kappa(D_ratio) = C_eff * D_ratio^gamma  (C_eff=2.0, gamma=0.55):")
    print(f"  {'D_ratio':>10s}  {'kappa':>8s}")
    print(f"  {'-'*10}  {'-'*8}")
    for row in bridge.kappa_table():
        print(f"  {row['D_ratio']:10.2f}  {row['kappa_pred']:8.3f}")
    print()

    kappa_central = bridge.kappa(1.2)
    lo, mid, hi = bridge.kappa_interval(1.2)
    print(f"  Central prediction (D_ratio=1.2): kappa = {kappa_central:.3f}")
    print(f"  95% propagated interval: [{lo:.3f}, {hi:.3f}]")
    print(f"  EBE-bounded interval (PDF v2.1): [1.7, 2.6]")
    print()

    assert 2.0 <= kappa_central <= 2.4
    assert 1.5 <= lo <= 1.85
    assert 2.55 <= hi <= 2.85
    print("  [PASS] Bridge B1** assertions passed\n")


def demo_layer_predictions():
    """4. Layer A and Layer B predictions."""
    print("=" * 65)
    print("DEMO 4: Layer A and Layer B Predictions")
    print("=" * 65)

    layer_a = LayerAPredictions()
    a1 = layer_a.test_A1(fitted_gamma=0.55, r_loglog=0.78, n=50)
    print(f"  A1 (slope test): fitted_gamma={a1['fitted_gamma']}, r={a1['r_loglog']}")
    print(f"     in falsification window: {a1['in_falsification_window']}, passes: {a1['passes']}")

    a23 = layer_a.test_A2_A3(alpha_AP_groups={"scz": 1.25, "healthy": 1.0, "mdd": 0.85}, auc=0.72)
    print(f"  A2/A3 (alpha_AP discrimination): AUC={a23['AUC']}, passes: {a23['passes']}")

    layer_b = LayerBPredictions()
    b1 = layer_b.test_B1(group_mean_kappa=2.18, n=50)
    print(f"  B1 (kappa interval): group_mean={b1['group_mean_kappa']}, "
          f"interval={b1['interval']}, passes: {b1['passes']}")

    b2 = layer_b.test_B2(kappa_obs=1.6, D_ratio_obs=0.85)
    print(f"  B2 (DoC threshold): kappa={b2['kappa_obs']}, D_ratio={b2['D_ratio_obs']}, "
          f"falsified={b2['falsified']}")
    print()

    assert a1["passes"]
    assert b1["passes"]
    print("  [PASS] Layer A/B assertions passed\n")


def demo_full_framework():
    """5. Complete EFC-C v2.1 framework."""
    print("=" * 65)
    print("DEMO 5: Full EFC-C v2.1 Framework")
    print("=" * 65)

    fw = EFCC_v21_Framework()
    report = fw.full_report(D_ratio=1.2)

    print(f"  Version: {report['version']}")
    print(f"  DOI: {report['doi']}")
    print(f"  C_eff: {report['C_eff']}, gamma: {report['gamma']}")

    b1 = report["B1_healthy"]
    print(f"  B1 healthy kappa: {b1['kappa_predicted']} "
          f"(propagated: {b1['kappa_interval_95']}, "
          f"EBE-bounded: {b1['kappa_interval_EBE_bounded']})")

    print(f"  Layer A predictions: {report['layer_A_predictions']}")
    print(f"  Layer B predictions: {report['layer_B_predictions']}")
    print()
    assert report["version"] == "2.1"
    assert b1["kappa_predicted"] > 2.0
    print("  [PASS] Full framework assertions passed\n")


if __name__ == "__main__":
    print()
    print("EFC-C v2.1: Cognitive Entropy Gradients Demo")
    print("Bridge B1** (degree-heterogeneity formulation)")
    print()

    demo_centrifugal_entropy()
    demo_degree_ratio()
    demo_bridge_b1_double_star()
    demo_layer_predictions()
    demo_full_framework()

    print("=" * 65)
    print("ALL DEMOS PASSED")
    print("=" * 65)
