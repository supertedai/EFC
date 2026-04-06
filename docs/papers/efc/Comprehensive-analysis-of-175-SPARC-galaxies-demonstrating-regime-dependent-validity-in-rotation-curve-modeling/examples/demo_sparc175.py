#!/usr/bin/env python3
"""
SPARC175 Regime Analysis Demo
==============================
Demonstrates EFC rotation curve fitting, NFW comparison,
latent proxy computation, and regime classification.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import sys
import os
import json
import math

# Add package root to path
_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.sparc175 import (
    EFCRotationCurve,
    NFWRotationCurve,
    LatentProxy,
    RegimeClassifier,
    REGIME_FLOW,
    REGIME_TRANSITION,
    REGIME_LATENT,
)


def demo_efc_rotation_curve():
    """Demo 1: EFC rotation curve model evaluation."""
    print("=" * 60)
    print("Demo 1: EFC Rotation Curve Model")
    print("=" * 60)

    # DDO154-like low-surface-brightness galaxy (FLOW regime)
    model = EFCRotationCurve(v_flat=55.0, r_turnon=2.1, sharpness=1.8)
    print(f"Model: {model}")

    radii = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0]
    velocities = model.velocity_array(radii)

    print("\n  r [kpc]   v(r) [km/s]")
    print("  -------   -----------")
    for r, v in zip(radii, velocities):
        print(f"  {r:7.1f}   {v:11.2f}")

    # Velocity should be monotonically increasing and approach v_flat
    for i in range(1, len(velocities)):
        assert velocities[i] >= velocities[i - 1], (
            f"Velocity not monotonic at r={radii[i]}"
        )
    assert velocities[-1] < model.v_flat, "Velocity must approach but not exceed v_flat"
    assert velocities[-1] > 0.9 * model.v_flat, "Far-out velocity should be near v_flat"

    # Parameter bounds check
    for name, (lo, hi) in EFCRotationCurve.PARAM_BOUNDS.items():
        val = getattr(model, name)
        assert lo <= val <= hi, f"Parameter {name}={val} out of bounds [{lo}, {hi}]"

    print("\n  [PASS] EFC model produces valid, monotonic rotation curve")
    print(f"  [PASS] Asymptotic velocity {velocities[-1]:.1f} km/s approaches v_flat={model.v_flat}")
    return True


def demo_nfw_comparison():
    """Demo 2: NFW model and AIC comparison with EFC."""
    print("\n" + "=" * 60)
    print("Demo 2: NFW Comparison and AIC")
    print("=" * 60)

    # Synthetic observation data for a FLOW-regime galaxy
    r_obs = [0.5, 1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 20.0]
    v_obs = [20.0, 35.0, 48.0, 52.0, 54.0, 54.5, 55.0, 55.0, 55.0]
    v_err = [3.0, 3.0, 2.5, 2.5, 2.0, 2.0, 2.0, 2.0, 2.0]

    efc = EFCRotationCurve(v_flat=55.0, r_turnon=2.1, sharpness=1.8)
    nfw = NFWRotationCurve(v_200=120.0, r_s=8.0, concentration=10.0)

    chi2_efc = efc.chi2_reduced(r_obs, v_obs, v_err)
    chi2_nfw = nfw.chi2_reduced(r_obs, v_obs, v_err)
    aic_efc = efc.aic(r_obs, v_obs, v_err)
    aic_nfw = nfw.aic(r_obs, v_obs, v_err)
    delta_aic = aic_efc - aic_nfw

    print(f"\n  EFC: chi2_red = {chi2_efc:.2f}, AIC = {aic_efc:.1f}")
    print(f"  NFW: chi2_red = {chi2_nfw:.2f}, AIC = {aic_nfw:.1f}")
    print(f"  delta_AIC (EFC - NFW) = {delta_aic:.1f}")

    assert chi2_efc >= 0, "Chi-squared must be non-negative"
    assert chi2_nfw >= 0, "Chi-squared must be non-negative"
    assert isinstance(delta_aic, float), "delta_AIC must be numeric"
    # EFC should fit this FLOW-like data well
    assert chi2_efc < 50, f"EFC chi2_red={chi2_efc} too high for FLOW-like data"

    print(f"\n  [PASS] Both models produce valid chi-squared and AIC values")
    print(f"  [PASS] delta_AIC = {delta_aic:.1f} (negative favors EFC)")
    return True


def demo_latent_proxy():
    """Demo 3: Latent proxy L computation for different galaxy types."""
    print("\n" + "=" * 60)
    print("Demo 3: Latent Proxy Computation")
    print("=" * 60)

    # FLOW galaxy: low residual trend, low oscillation, low chi2
    flow_proxy = LatentProxy(rho_radial=0.05, sign_rate=0.1, chi2_red=2.0)
    # TRANSITION galaxy: moderate complexity
    trans_proxy = LatentProxy(rho_radial=0.3, sign_rate=0.3, chi2_red=8.0)
    # LATENT galaxy: strong residual trend, high oscillation, high chi2
    latent_proxy = LatentProxy(rho_radial=0.8, sign_rate=0.5, chi2_red=150.0)

    print(f"\n  FLOW galaxy:       L = {flow_proxy.L:.3f}")
    print(f"  TRANSITION galaxy: L = {trans_proxy.L:.3f}")
    print(f"  LATENT galaxy:     L = {latent_proxy.L:.3f}")

    # L should increase with complexity
    assert flow_proxy.L < trans_proxy.L, (
        f"FLOW L={flow_proxy.L} should be < TRANSITION L={trans_proxy.L}"
    )
    assert trans_proxy.L < latent_proxy.L, (
        f"TRANSITION L={trans_proxy.L} should be < LATENT L={latent_proxy.L}"
    )

    # L should be in [0, 1]
    for name, proxy in [("FLOW", flow_proxy), ("TRANSITION", trans_proxy), ("LATENT", latent_proxy)]:
        assert 0.0 <= proxy.L <= 1.0, f"{name} proxy L={proxy.L} out of [0,1]"

    # Components should be accessible
    comps = flow_proxy.components
    assert "radial_trend" in comps
    assert "oscillation" in comps
    assert "chi2_normalized" in comps

    print(f"\n  Components (FLOW): {flow_proxy.components}")
    print(f"\n  [PASS] Latent proxy orders correctly: FLOW < TRANSITION < LATENT")
    print(f"  [PASS] All L values in [0, 1]")
    return True


def demo_regime_classification():
    """Demo 4: Regime classification of galaxy sample."""
    print("\n" + "=" * 60)
    print("Demo 4: Regime Classification")
    print("=" * 60)

    classifier = RegimeClassifier()

    # Test individual classifications
    test_cases = [
        {"delta_aic": -25.0, "chi2_red": 2.0, "expected": REGIME_FLOW},
        {"delta_aic": -15.0, "chi2_red": 5.0, "expected": REGIME_FLOW},
        {"delta_aic": 0.0, "chi2_red": 10.0, "expected": REGIME_TRANSITION},
        {"delta_aic": -5.0, "chi2_red": 30.0, "expected": REGIME_TRANSITION},
        {"delta_aic": 42.0, "chi2_red": 185.0, "expected": REGIME_LATENT},
        {"delta_aic": 5.0, "chi2_red": 80.0, "expected": REGIME_LATENT},
    ]

    print("\n  delta_AIC  chi2_red  Expected     Got")
    print("  ---------  --------  -----------  -----------")
    for tc in test_cases:
        regime = classifier.classify(tc["delta_aic"], tc["chi2_red"])
        match = "OK" if regime == tc["expected"] else "FAIL"
        print(f"  {tc['delta_aic']:9.1f}  {tc['chi2_red']:8.1f}  {tc['expected']:<11s}  {regime:<11s}  {match}")
        assert regime == tc["expected"], (
            f"Classification failed: got {regime}, expected {tc['expected']}"
        )

    print(f"\n  [PASS] All 6 classification cases correct")
    return True


def demo_batch_classification():
    """Demo 5: Batch classification and summary statistics."""
    print("\n" + "=" * 60)
    print("Demo 5: Batch Classification and Summary")
    print("=" * 60)

    # Load sample data
    data_path = os.path.join(_pkg, "data", "sparc175_regime_summary.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    galaxies = data["sample_galaxies"]
    classifier = RegimeClassifier()

    entries = [{"delta_aic": g["delta_aic"], "chi2_red": g["chi2_red"]} for g in galaxies]
    summary = classifier.summary(entries)

    print("\n  Regime       Count  Percentage")
    print("  ----------   -----  ----------")
    for regime in [REGIME_FLOW, REGIME_TRANSITION, REGIME_LATENT]:
        s = summary[regime]
        print(f"  {regime:<12s}  {s['count']:5d}  {s['percentage']:9.1f}%")

    # Verify against expected regimes from data
    batch_result = classifier.classify_batch(entries)
    for i, g in enumerate(galaxies):
        expected = g["regime"]
        got = classifier.classify(g["delta_aic"], g["chi2_red"])
        assert got == expected, (
            f"Galaxy {g['name']}: expected {expected}, got {got}"
        )

    total = sum(s["count"] for s in summary.values())
    assert total == len(galaxies), f"Total {total} != sample size {len(galaxies)}"

    print(f"\n  [PASS] All {len(galaxies)} sample galaxies classified correctly")
    print(f"  [PASS] Total count {total} matches sample size")
    return True


def demo_full_analysis_pipeline():
    """Demo 6: End-to-end analysis pipeline for a single galaxy."""
    print("\n" + "=" * 60)
    print("Demo 6: Full Analysis Pipeline")
    print("=" * 60)

    # Synthetic FLOW-regime galaxy data
    r_obs = [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 8.0, 12.0, 16.0, 20.0]
    v_obs = [18.0, 33.0, 42.0, 48.0, 52.5, 54.0, 54.8, 55.0, 55.0, 55.0]
    v_err = [3.0, 3.0, 2.5, 2.5, 2.0, 2.0, 2.0, 2.0, 2.0, 2.0]

    # Step 1: Fit EFC model
    efc = EFCRotationCurve(v_flat=55.0, r_turnon=2.1, sharpness=1.8)
    nfw = NFWRotationCurve(v_200=120.0, r_s=8.0)

    chi2_efc = efc.chi2_reduced(r_obs, v_obs, v_err)
    chi2_nfw = nfw.chi2_reduced(r_obs, v_obs, v_err)
    delta_aic = efc.aic(r_obs, v_obs, v_err) - nfw.aic(r_obs, v_obs, v_err)

    print(f"\n  Step 1 - Fitting:")
    print(f"    EFC chi2_red = {chi2_efc:.2f}")
    print(f"    NFW chi2_red = {chi2_nfw:.2f}")
    print(f"    delta_AIC = {delta_aic:.1f}")

    # Step 2: Compute residuals and latent proxy
    residuals = [vo - efc.velocity(r) for r, vo in zip(r_obs, v_obs)]
    sign_changes = sum(
        1 for i in range(1, len(residuals))
        if residuals[i] * residuals[i - 1] < 0
    )
    sign_rate = sign_changes / max(len(residuals) - 1, 1)

    # Simple rank correlation proxy
    n = len(residuals)
    rank_r = sorted(range(n), key=lambda i: r_obs[i])
    rank_res = sorted(range(n), key=lambda i: abs(residuals[i]))
    d_sq = sum((rank_r[i] - rank_res[i]) ** 2 for i in range(n))
    rho = 1.0 - 6.0 * d_sq / (n * (n ** 2 - 1))

    proxy = LatentProxy(rho_radial=rho, sign_rate=sign_rate, chi2_red=chi2_efc)
    print(f"\n  Step 2 - Latent Proxy:")
    print(f"    rho_radial = {rho:.3f}")
    print(f"    sign_rate = {sign_rate:.3f}")
    print(f"    L = {proxy.L:.3f}")

    # Step 3: Classify
    classifier = RegimeClassifier()
    regime = classifier.classify(delta_aic, chi2_efc)
    print(f"\n  Step 3 - Classification: {regime}")

    # Assertions
    assert chi2_efc < 20, f"FLOW-like data should have low chi2: {chi2_efc}"
    assert 0.0 <= proxy.L <= 1.0, f"L out of range: {proxy.L}"
    assert regime in (REGIME_FLOW, REGIME_TRANSITION, REGIME_LATENT), (
        f"Invalid regime: {regime}"
    )

    print(f"\n  [PASS] Full pipeline completed: {regime} regime with L={proxy.L:.3f}")
    return True


if __name__ == "__main__":
    results = []
    results.append(("Demo 1: EFC Rotation Curve", demo_efc_rotation_curve()))
    results.append(("Demo 2: NFW Comparison", demo_nfw_comparison()))
    results.append(("Demo 3: Latent Proxy", demo_latent_proxy()))
    results.append(("Demo 4: Regime Classification", demo_regime_classification()))
    results.append(("Demo 5: Batch Classification", demo_batch_classification()))
    results.append(("Demo 6: Full Pipeline", demo_full_analysis_pipeline()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  {sum(1 for _, p in results if p)}/{len(results)} demos passed")
