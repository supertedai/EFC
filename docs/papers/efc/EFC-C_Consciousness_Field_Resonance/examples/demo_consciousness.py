#!/usr/bin/env python3
"""
EFC-C Consciousness Field Resonance Demo
==========================================
Demonstrates spectral differentiation, causal integration,
product measure falsification, resonance classification, and balance constraint.

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

from src.consciousness_field import (
    SpectralDifferentiation,
    CausalIntegration,
    ProductMeasure,
    ResonanceRegime,
    BalanceConstraint,
)


def demo_spectral_differentiation():
    """Demo 1: Spectral differentiation Omega for waking vs sedated states."""
    print("=" * 60)
    print("Demo 1: Spectral Differentiation (Omega)")
    print("=" * 60)

    # Waking state: broad, distributed power spectrum -> high entropy
    waking_spectrum = [0.15, 0.20, 0.18, 0.17, 0.15, 0.10, 0.05]
    # Sedated state: concentrated in low frequencies -> low entropy
    sedated_spectrum = [0.60, 0.20, 0.10, 0.05, 0.03, 0.01, 0.01]

    sd_waking = SpectralDifferentiation(waking_spectrum)
    sd_sedated = SpectralDifferentiation(sedated_spectrum)

    print(f"\n  Waking state:  Omega = {sd_waking.omega:.3f}")
    print(f"  Sedated state: Omega = {sd_sedated.omega:.3f}")

    # Waking Omega should be higher than sedated
    assert sd_waking.omega > sd_sedated.omega, (
        f"Waking Omega ({sd_waking.omega:.3f}) should exceed sedated ({sd_sedated.omega:.3f})"
    )
    # Both should be in [0, 1]
    assert 0.0 <= sd_waking.omega <= 1.0, f"Omega out of range: {sd_waking.omega}"
    assert 0.0 <= sd_sedated.omega <= 1.0, f"Omega out of range: {sd_sedated.omega}"
    # Waking should be in typical range (>0.75)
    assert sd_waking.omega > 0.75, f"Waking Omega should be > 0.75: {sd_waking.omega}"

    print(f"\n  [PASS] Waking Omega > Sedated Omega (differentiation tracks consciousness)")
    print(f"  [PASS] Both Omega values in [0, 1]")
    return True


def demo_causal_integration():
    """Demo 2: Causal integration kappa for global and regional measures."""
    print("\n" + "=" * 60)
    print("Demo 2: Causal Integration (kappa)")
    print("=" * 60)

    # Global transfer entropy values (weak effect, d=0.42)
    global_te = [0.15, 0.12, 0.18, 0.14, 0.16, 0.11]
    # Parietal region (stronger, candidate for replication)
    parietal_te = [0.30, 0.28, 0.32, 0.25, 0.35]

    ci_global = CausalIntegration(global_te)
    ci_parietal = CausalIntegration(parietal_te)

    print(f"\n  Global kappa:   {ci_global.kappa:.3f}")
    print(f"  Parietal kappa: {ci_parietal.kappa:.3f}")

    assert ci_global.kappa > 0, "kappa must be positive"
    assert ci_parietal.kappa > ci_global.kappa, (
        "Parietal kappa should exceed global kappa"
    )
    assert len(ci_global.kappa_regional) == len(global_te), (
        "Regional values count mismatch"
    )

    print(f"\n  [PASS] Global and regional kappa computed correctly")
    print(f"  [PASS] Parietal kappa > Global kappa (regional specificity)")
    return True


def demo_product_measure_falsification():
    """Demo 3: Product measure C = Omega x kappa -- falsification test."""
    print("\n" + "=" * 60)
    print("Demo 3: Product Measure Falsification (F1)")
    print("=" * 60)

    # Waking subject: high Omega, low kappa
    waking = ProductMeasure(omega=0.85, kappa=0.15)
    # Sedated subject: low Omega, higher kappa
    sedated = ProductMeasure(omega=0.60, kappa=0.22)

    print(f"\n  Waking:  C = {waking.omega:.2f} x {waking.kappa:.2f} = {waking.C:.4f}")
    print(f"  Sedated: C = {sedated.omega:.2f} x {sedated.kappa:.2f} = {sedated.C:.4f}")

    # The product measure is falsified -- it does not clearly separate states
    # because kappa increases under sedation, partially compensating Omega decrease
    print(f"\n  Waking C  = {waking.C:.4f}")
    print(f"  Sedated C = {sedated.C:.4f}")
    print(f"  Ratio = {waking.C / sedated.C:.2f}x")

    assert waking.is_falsified, "Product measure should be marked as falsified"
    assert ProductMeasure.STATUS == "FALSIFIED", "Status should be FALSIFIED"

    # Omega alone gives much better separation
    omega_ratio = waking.omega / sedated.omega
    c_ratio = waking.C / sedated.C
    print(f"\n  Omega ratio (waking/sedated): {omega_ratio:.2f}x")
    print(f"  C ratio (waking/sedated):     {c_ratio:.2f}x")

    # Omega alone should give better separation than C
    assert omega_ratio > c_ratio, (
        "Omega should separate better than C (the product is falsified)"
    )

    print(f"\n  [PASS] Product measure is falsified (F1)")
    print(f"  [PASS] Omega alone provides better state separation than C")
    return True


def demo_resonance_regime():
    """Demo 4: Resonance continuum classification."""
    print("\n" + "=" * 60)
    print("Demo 4: Resonance Regime Classification")
    print("=" * 60)

    systems = [
        ("Stone", 0.02, 0.0),
        ("Cell", 0.25, 0.01),
        ("Anaesthetised brain", 0.62, 0.22),
        ("Waking brain", 0.83, 0.15),
    ]

    expected_levels = ["near_zero", "low", "reduced", "extreme"]
    expected_fields = ["thermodynamic", "metabolic", "neural", "neural"]

    print(f"\n  {'System':<25s}  {'Omega':>6s}  {'Level':<12s}  {'Field':<15s}")
    print(f"  {'-'*25}  {'-'*6}  {'-'*12}  {'-'*15}")

    for (name, omega, kappa), exp_level, exp_field in zip(systems, expected_levels, expected_fields):
        regime = ResonanceRegime(omega=omega, kappa=kappa)
        print(f"  {name:<25s}  {omega:6.2f}  {regime.resonance_level:<12s}  {regime.field_type:<15s}")

        assert regime.resonance_level == exp_level, (
            f"{name}: expected level {exp_level}, got {regime.resonance_level}"
        )
        assert regime.field_type == exp_field, (
            f"{name}: expected field {exp_field}, got {regime.field_type}"
        )

    # Test Cohen's d between waking and anaesthetised
    waking_r = ResonanceRegime(omega=0.83)
    sedated_r = ResonanceRegime(omega=0.62)
    d = waking_r.cohens_d(sedated_r)
    print(f"\n  Cohen's d (waking vs anaesthetised): {d:.2f}")
    assert d > 1.0, f"Cohen's d should be > 1.0 for consciousness effect: {d}"

    print(f"\n  [PASS] All 4 systems classified correctly on resonance continuum")
    print(f"  [PASS] Cohen's d = {d:.2f} confirms large effect size")
    return True


def demo_balance_constraint():
    """Demo 5: Balance constraint -- negative Omega-kappa correlation."""
    print("\n" + "=" * 60)
    print("Demo 5: Balance Constraint")
    print("=" * 60)

    # Load sample data
    data_path = os.path.join(_pkg, "data", "consciousness_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    subjects = data["sample_subjects"]
    omega_vals = [s["omega"] for s in subjects]
    kappa_vals = [s["kappa"] for s in subjects]

    bc = BalanceConstraint(omega_vals, kappa_vals)

    print(f"\n  N subjects: {len(subjects)}")
    print(f"  corr(Omega, kappa) = {bc.correlation:.3f}")
    print(f"  Balance holds: {bc.is_balanced}")

    assert bc.is_balanced, (
        f"Balance constraint violated: r = {bc.correlation:.3f} (should be < 0)"
    )
    assert bc.correlation < 0, "Correlation must be negative for balance"

    # The correlation should be around -0.27 per the paper
    assert -1.0 <= bc.correlation <= 0.0, f"Correlation out of range: {bc.correlation}"

    print(f"\n  [PASS] Negative correlation confirms balance (not maximisation)")
    print(f"  [PASS] corr(Omega, kappa) = {bc.correlation:.3f} < 0")
    return True


def demo_regional_analysis():
    """Demo 6: Regional parietal analysis -- exploratory candidate."""
    print("\n" + "=" * 60)
    print("Demo 6: Regional Parietal Analysis")
    print("=" * 60)

    # Load parietal data
    data_path = os.path.join(_pkg, "data", "consciousness_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    parietal = data["parietal_data"]
    waking = [s for s in parietal if s["condition"] == "waking"]
    sedated = [s for s in parietal if s["condition"] == "sedated"]

    # Compute regional C for each condition
    waking_C = [s["omega_parietal"] * s["kappa_parietal"] for s in waking]
    sedated_C = [s["omega_parietal"] * s["kappa_parietal"] for s in sedated]

    mean_waking_C = sum(waking_C) / len(waking_C)
    mean_sedated_C = sum(sedated_C) / len(sedated_C)

    print(f"\n  Waking C(parietal):  {mean_waking_C:.4f} (n={len(waking)})")
    print(f"  Sedated C(parietal): {mean_sedated_C:.4f} (n={len(sedated)})")
    print(f"  Ratio: {mean_waking_C / mean_sedated_C:.2f}x")

    # Regional C should separate better than global C
    assert mean_waking_C > mean_sedated_C, (
        "Parietal C should be higher in waking state"
    )

    # Compute pooled SD and Cohen's d
    all_C = waking_C + sedated_C
    mean_all = sum(all_C) / len(all_C)
    var_all = sum((c - mean_all) ** 2 for c in all_C) / len(all_C)
    sd_pooled = math.sqrt(var_all) if var_all > 0 else 0.001
    d = abs(mean_waking_C - mean_sedated_C) / sd_pooled

    print(f"  Cohen's d (parietal C): {d:.2f}")
    assert d > 1.5, f"Parietal C should show large effect size, got d={d:.2f}"

    print(f"\n  [PASS] Regional parietal C separates states (d={d:.2f})")
    print(f"  [PASS] Candidate for replication (R1 prediction)")
    return True


if __name__ == "__main__":
    results = []
    results.append(("Demo 1: Spectral Differentiation", demo_spectral_differentiation()))
    results.append(("Demo 2: Causal Integration", demo_causal_integration()))
    results.append(("Demo 3: Product Falsification", demo_product_measure_falsification()))
    results.append(("Demo 4: Resonance Regime", demo_resonance_regime()))
    results.append(("Demo 5: Balance Constraint", demo_balance_constraint()))
    results.append(("Demo 6: Regional Analysis", demo_regional_analysis()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  {sum(1 for _, p in results if p)}/{len(results)} demos passed")
