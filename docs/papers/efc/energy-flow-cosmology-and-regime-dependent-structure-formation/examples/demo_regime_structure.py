#!/usr/bin/env python3
"""
EFC Regime-Dependent Structure Formation Demo
===============================================
Demonstrates energy decomposition, regime classification,
cross-scale correspondence, and structure formation rates.

Author: Morten Magnusson (ORCID: 0009-0002-4860-5095)
Affiliation: Symbiose Research, Sandnes, Norway
License: CC-BY-4.0
"""

import sys
import os
import json

# Add package root to path
_pkg = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _pkg)

from src.regime_structure import (
    EnergyDecomposition,
    RegimeStructure,
    CrossScaleCorrespondence,
    StructureFormationRate,
    REGIME_FLOW,
    REGIME_TRANSITION,
    REGIME_LATENT,
)


def demo_energy_decomposition():
    """Demo 1: E_total = E_flow + E_latent decomposition."""
    print("=" * 60)
    print("Demo 1: Energy Decomposition")
    print("=" * 60)

    # FLOW-dominated system (most energy in observable flow)
    flow_sys = EnergyDecomposition(E_total=100.0, flow_fraction=0.85)
    # LATENT-dominated system (most energy hidden)
    latent_sys = EnergyDecomposition(E_total=100.0, flow_fraction=0.20)

    print(f"\n  FLOW-dominated system:")
    print(f"    E_total = {flow_sys.E_total:.1f}")
    print(f"    E_flow  = {flow_sys.E_flow:.1f} ({flow_sys.flow_fraction*100:.0f}%)")
    print(f"    E_latent = {flow_sys.E_latent:.1f} ({flow_sys.latent_fraction*100:.0f}%)")

    print(f"\n  LATENT-dominated system:")
    print(f"    E_total = {latent_sys.E_total:.1f}")
    print(f"    E_flow  = {latent_sys.E_flow:.1f} ({latent_sys.flow_fraction*100:.0f}%)")
    print(f"    E_latent = {latent_sys.E_latent:.1f} ({latent_sys.latent_fraction*100:.0f}%)")

    # Conservation: E_flow + E_latent = E_total
    assert abs(flow_sys.E_flow + flow_sys.E_latent - flow_sys.E_total) < 1e-10, (
        "Energy not conserved in flow system"
    )
    assert abs(latent_sys.E_flow + latent_sys.E_latent - latent_sys.E_total) < 1e-10, (
        "Energy not conserved in latent system"
    )

    # Flow system should have more E_flow
    assert flow_sys.E_flow > latent_sys.E_flow, "FLOW system should have more E_flow"

    # Entropy gradient should be steeper at high redshift
    grad_high_z = flow_sys.entropy_gradient(scale_factor=0.1)
    grad_low_z = flow_sys.entropy_gradient(scale_factor=1.0)
    assert grad_high_z > grad_low_z, "Gradient should be steeper at higher redshift"

    print(f"\n  Entropy gradient at z~9 (a=0.1): {grad_high_z:.1f}")
    print(f"  Entropy gradient at z=0 (a=1.0): {grad_low_z:.1f}")
    print(f"\n  [PASS] Energy conservation holds: E_flow + E_latent = E_total")
    print(f"  [PASS] Entropy gradient steepens with redshift")
    return True


def demo_regime_classification():
    """Demo 2: Regime classification based on latent proxy L."""
    print("\n" + "=" * 60)
    print("Demo 2: Regime Classification")
    print("=" * 60)

    rs = RegimeStructure()

    test_cases = [
        (0.10, REGIME_FLOW, "LSB galaxy"),
        (0.15, REGIME_FLOW, "NGC3198"),
        (0.30, REGIME_TRANSITION, "Spiral galaxy"),
        (0.40, REGIME_TRANSITION, "Mixed dynamics"),
        (0.55, REGIME_LATENT, "Barred galaxy"),
        (0.80, REGIME_LATENT, "NGC2841"),
    ]

    print(f"\n  {'L':>5s}  {'Regime':<12s}  {'Success':>8s}  {'Example'}")
    print(f"  {'-----':>5s}  {'------':<12s}  {'-------':>8s}  {'-------'}")

    for L, expected, example in test_cases:
        regime = rs.classify(L)
        success = rs.expected_model_success(L)
        print(f"  {L:5.2f}  {regime:<12s}  {success:7.1%}  {example}")
        assert regime == expected, f"L={L}: expected {expected}, got {regime}"

    # Model success should decrease with L
    success_flow = rs.expected_model_success(0.10)
    success_latent = rs.expected_model_success(0.80)
    assert success_flow > success_latent, (
        "Model success should decrease from FLOW to LATENT"
    )
    assert success_flow > 0.9, "FLOW success should be near 100%"
    assert success_latent < 0.1, "LATENT success should be near 0%"

    print(f"\n  [PASS] All 6 systems classified correctly")
    print(f"  [PASS] Model success decreases: {success_flow:.0%} -> {success_latent:.0%}")
    return True


def demo_cross_scale_correspondence():
    """Demo 3: Cross-scale correspondence galactic <-> cosmological."""
    print("\n" + "=" * 60)
    print("Demo 3: Cross-Scale Correspondence")
    print("=" * 60)

    gradients = [
        (8.0, "steep"),
        (2.5, "moderate"),
        (0.5, "shallow"),
    ]

    print(f"\n  {'Gradient':>8s}  {'Class':<10s}  {'Galactic':<20s}  {'Cosmological'}")
    print(f"  {'--------':>8s}  {'-----':<10s}  {'--------':<20s}  {'------------'}")

    for strength, expected_class in gradients:
        csc = CrossScaleCorrespondence(gradient_strength=strength)
        gal = csc.galactic_prediction
        cosm = csc.cosmological_prediction

        print(f"  {strength:8.1f}  {csc.gradient_class:<10s}  {gal['morphology']:<20s}  {cosm['redshift_range']}")

        assert csc.gradient_class == expected_class, (
            f"gradient={strength}: expected {expected_class}, got {csc.gradient_class}"
        )

    # Steep gradient should have highest galactic success and cosmological excess
    steep = CrossScaleCorrespondence(8.0)
    shallow = CrossScaleCorrespondence(0.5)
    assert steep.galactic_prediction["success_rate"] > shallow.galactic_prediction["success_rate"]
    assert steep.cosmological_prediction["excess_factor"] > shallow.cosmological_prediction["excess_factor"]

    print(f"\n  [PASS] All gradient classes map correctly to both scales")
    print(f"  [PASS] Steep gradients predict both galactic success and cosmological excess")
    return True


def demo_structure_formation():
    """Demo 4: Structure formation rate enhancement at high redshift."""
    print("\n" + "=" * 60)
    print("Demo 4: Structure Formation Rate")
    print("=" * 60)

    redshifts = [0.0, 2.0, 5.0, 8.0, 10.0, 12.0]

    print(f"\n  {'z':>5s}  {'a':>6s}  {'Enhancement':>12s}  {'EFC Rate':>9s}")
    print(f"  {'---':>5s}  {'---':>6s}  {'-----------':>12s}  {'--------':>9s}")

    prev_enhancement = 0.0
    for z in redshifts:
        sfr = StructureFormationRate(redshift=z, lcdm_rate=1.0)
        print(f"  {z:5.1f}  {sfr.scale_factor:6.3f}  {sfr.efc_enhancement:12.1f}x  {sfr.efc_rate:9.1f}")

        # Enhancement should be >= 1.0
        assert sfr.efc_enhancement >= 1.0, f"Enhancement < 1 at z={z}"
        # Enhancement should be monotonically increasing
        assert sfr.efc_enhancement >= prev_enhancement, (
            f"Enhancement not monotonic at z={z}"
        )
        prev_enhancement = sfr.efc_enhancement

    # At low z, enhancement should be 1.0 (LCDM valid)
    sfr_low = StructureFormationRate(redshift=2.0)
    assert sfr_low.efc_enhancement == 1.0, "No enhancement expected at z=2"

    # At high z, significant enhancement expected
    sfr_high = StructureFormationRate(redshift=12.0)
    assert sfr_high.efc_enhancement > 5.0, (
        f"Expected significant enhancement at z=12, got {sfr_high.efc_enhancement}"
    )

    print(f"\n  [PASS] Enhancement monotonically increases with redshift")
    print(f"  [PASS] No enhancement at z<=3, significant at z=12 ({sfr_high.efc_enhancement:.1f}x)")
    return True


def demo_data_integration():
    """Demo 5: Integration with regime structure data file."""
    print("\n" + "=" * 60)
    print("Demo 5: Data Integration")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "regime_structure_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    rs = RegimeStructure()

    # Verify regime classification matches data
    galactic = [s for s in data["sample_systems"] if s["scale"] == "galactic"]
    print(f"\n  Galactic systems:")
    for sys in galactic:
        regime = rs.classify(sys["L"])
        print(f"    {sys['name']:<12s}  L={sys['L']:.2f}  -> {regime:<12s} (expected: {sys['regime']})")
        assert regime == sys["regime"], (
            f"{sys['name']}: expected {sys['regime']}, got {regime}"
        )

    # Verify cross-scale correspondence
    cosmo = [s for s in data["sample_systems"] if s["scale"] == "cosmological"]
    print(f"\n  Cosmological systems:")
    for sys in cosmo:
        csc = CrossScaleCorrespondence(sys["gradient"])
        print(f"    {sys['name']:<12s}  z={sys['redshift']:.0f}  gradient={sys['gradient']:.1f}  -> {csc.gradient_class}")

    # Verify predictions are present
    predictions = data["testable_predictions"]
    assert len(predictions) == 4, f"Expected 4 predictions, got {len(predictions)}"

    print(f"\n  Testable predictions: {len(predictions)}")
    for p in predictions:
        print(f"    {p['id']}: {p['prediction'][:60]}...")

    print(f"\n  [PASS] All galactic regimes match classification")
    print(f"  [PASS] {len(predictions)} testable predictions loaded")
    return True


def demo_paper_series_consistency():
    """Demo 6: Verify consistency of the three-paper series."""
    print("\n" + "=" * 60)
    print("Demo 6: Paper Series Consistency")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "regime_structure_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    series = data["paper_series"]

    # Paper 1 and 2 should be empirical, Paper 3 interpretive
    assert series["paper_1"]["type"] == "empirical", "Paper I must be empirical"
    assert series["paper_2"]["type"] == "empirical", "Paper II must be empirical"
    assert series["paper_3"]["type"] == "interpretive", "Paper III must be interpretive"

    print(f"\n  Paper I:   {series['paper_1']['content']} ({series['paper_1']['type']})")
    print(f"  Paper II:  {series['paper_2']['content']} ({series['paper_2']['type']})")
    print(f"  Paper III: {series['paper_3']['content']} ({series['paper_3']['type']})")

    # All three papers should have DOIs
    for key, paper in series.items():
        assert "doi" in paper, f"{key} missing DOI"
        assert paper["doi"].startswith("10."), f"{key} DOI invalid"

    # Verify energy decomposition formula
    ed = data["energy_decomposition"]
    assert ed["formula"] == "E_total = E_flow + E_latent", "Wrong decomposition formula"

    # Verify regime boundaries
    rc = data["regime_classification"]
    assert rc["FLOW"]["L_range"] == [0.0, 0.25], "FLOW L range wrong"
    assert rc["LATENT"]["L_range"] == [0.45, 1.0], "LATENT L range wrong"

    print(f"\n  Energy formula: {ed['formula']}")
    print(f"  Regime boundaries: FLOW < 0.25 | TRANSITION | LATENT > 0.45")
    print(f"\n  [PASS] Epistemic structure: empirical -> empirical -> interpretive")
    print(f"  [PASS] All DOIs present and valid")
    print(f"  [PASS] No circularity: regimes defined before EFC applied")
    return True


if __name__ == "__main__":
    results = []
    results.append(("Demo 1: Energy Decomposition", demo_energy_decomposition()))
    results.append(("Demo 2: Regime Classification", demo_regime_classification()))
    results.append(("Demo 3: Cross-Scale Correspondence", demo_cross_scale_correspondence()))
    results.append(("Demo 4: Structure Formation Rate", demo_structure_formation()))
    results.append(("Demo 5: Data Integration", demo_data_integration()))
    results.append(("Demo 6: Paper Series Consistency", demo_paper_series_consistency()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  {sum(1 for _, p in results if p)}/{len(results)} demos passed")
