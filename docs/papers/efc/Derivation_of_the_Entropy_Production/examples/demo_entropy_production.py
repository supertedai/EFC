#!/usr/bin/env python3
"""
Demo: Derivation of Γ(ρ) from Grid-Mode Bose-Einstein Statistics
DOI: 10.6084/m9.figshare.31942821

Demonstrates the first-principles derivation of the entropy production function.
"""

import sys, os, math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.entropy_production import (
    BEOccupation,
    VonNeumannEntropy,
    GammaDerivation,
    DoubleCounting,
    ScenarioClassification,
    Predictions,
)


def demo_1_be_occupation():
    """BE occupation number and its derivatives."""
    print("=" * 65)
    print("Demo 1: Bose-Einstein Occupation Number")
    print("=" * 65)
    print("n(x) = 1/(e^x - 1),  x = √(βρ/a₀)\n")

    be = BEOccupation()

    print(f"{'x':<10} {'n(x)':<15} {'1/x (low-x)':<15} {'dn/dx':<15} {'-n(n+1)'}")
    print("-" * 65)
    for x in [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0]:
        n = be.occupation(x)
        approx = be.low_x_approx(x)
        dn = be.dn_dx(x)
        nn1 = -n * (n + 1)
        print(f"{x:<10.2f} {n:<15.4f} {approx:<15.4f} {dn:<15.4f} {nn1:<.4f}")

    # Verify low-x: n ≈ 1/x
    n_low = be.occupation(0.01)
    assert abs(n_low - 100.0) / 100.0 < 0.01
    # Verify derivative identity
    n1 = be.occupation(1.0)
    assert abs(be.dn_dx(1.0) - (-n1 * (n1 + 1))) < 1e-10
    print("\n✓ BE occupation and derivative identity verified")


def demo_2_von_neumann_entropy():
    """Von Neumann entropy and the key marginal identity ds/dn = x."""
    print("\n" + "=" * 65)
    print("Demo 2: Von Neumann Entropy & Marginal Identity")
    print("=" * 65)
    print("s(n) = (1+n)ln(1+n) - n ln(n)")
    print("KEY RESULT: ds/dn = x  for BE distribution (Eq. 11)\n")

    vn = VonNeumannEntropy()

    print(f"{'x':<10} {'n(x)':<12} {'s(n)':<12} {'ds/dn':<12} {'x (should match)':<18} {'|error|'}")
    print("-" * 70)
    for x in [0.1, 0.5, 1.0, 2.0, 5.0]:
        n = 1.0 / (math.exp(x) - 1.0)
        s = vn.entropy_per_mode(n)
        ds = vn.ds_dn(n)
        err = vn.verify_marginal_identity(x)
        print(f"{x:<10.1f} {n:<12.4f} {s:<12.4f} {ds:<12.6f} {x:<18.6f} {err:<.2e}")

    # Verify marginal identity for several x values
    for x in [0.1, 0.5, 1.0, 2.0, 5.0]:
        err = vn.verify_marginal_identity(x)
        assert err < 1e-10, f"Marginal identity failed at x={x}: error={err}"

    print("\n✓ ds/dn = x identity verified to machine precision")


def demo_3_derivation_chain():
    """Full derivation chain: all intermediate quantities."""
    print("\n" + "=" * 65)
    print("Demo 3: Full Derivation Chain")
    print("=" * 65)
    print("Γ = (ds/dn) · (dn/dρ) → per-mode: |Γ| = (β/(2a₀)) n(n+1)\n")

    gd = GammaDerivation()

    for x in [0.1, 0.5, 1.0, 2.0, 5.0]:
        chain = gd.derivation_chain(x)
        print(f"x = {x:.1f}:")
        print(f"  n(x) = {chain['n(x)']:.4f}")
        print(f"  s(n) = {chain['s(n)']:.4f}")
        print(f"  ds/dn = {chain['ds/dn']:.4f}  (should = x = {chain['ds/dn (BE identity)']:.4f})")
        print(f"  n(n+1) = {chain['n(n+1)']:.4f}")
        print()

    # Verify ds/dn matches x
    chain = gd.derivation_chain(1.0)
    assert abs(chain["ds/dn"] - chain["ds/dn (BE identity)"]) < 1e-10
    print("✓ Derivation chain verified")


def demo_4_gamma_total():
    """Total Γ(ρ): derived ρ^(3/2)/(ρ+ρ_crit) vs phenomenological ρ/(ρ+ρ_crit)."""
    print("\n" + "=" * 65)
    print("Demo 4: Total Γ(ρ) — Main Result (Eq. 37)")
    print("=" * 65)
    print("Derived:         Γ ∝ ρ^(3/2)/(ρ + ρ_crit)")
    print("Phenomenological: Γ = Γ₀ ρ/(ρ + ρ_crit)\n")

    gd = GammaDerivation()

    print(f"{'ρ/ρ_crit':<12} {'Γ_derived':<12} {'Γ_phenom':<12} {'Δ (%)'}")
    print("-" * 50)
    for x in [0.01, 0.05, 0.1, 0.3, 0.5, 1.0, 3.0, 10.0]:
        gder = gd.gamma_total(x)
        gph = gd.gamma_phenomenological(x)
        diff = gd.relative_difference(x) * 100
        print(f"{x:<12.3f} {gder:<12.4f} {gph:<12.4f} {diff:+.1f}")

    # At ρ = ρ_crit: both should give 0.5 (normalisation)
    assert abs(gd.gamma_total(1.0) - 0.5) < 0.01
    assert abs(gd.gamma_phenomenological(1.0) - 0.5) < 0.01

    # Derived < phenom at low ρ (ρ^(3/2) < ρ for ρ < 1)
    assert gd.gamma_total(0.5) < gd.gamma_phenomenological(0.5)
    # Derived > phenom at high ρ (ρ^(3/2) > ρ for ρ > 1, grows as √ρ not const)
    assert gd.gamma_total(5.0) > gd.gamma_phenomenological(5.0)

    print("\n✓ Γ_derived matches at ρ=ρ_crit; weaker at low ρ, stronger at high ρ")


def demo_5_double_counting():
    """Resolution: μ_BE (static) vs Γ (dynamical)."""
    print("\n" + "=" * 65)
    print("Demo 5: Double-Counting Resolution")
    print("=" * 65)
    print("μ_BE = n(x) — static occupation (gravitational response)")
    print("Γ   ∝ n(n+1) — dynamical rate (entropy production)\n")

    dc = DoubleCounting()

    print(f"{'x':<10} {'μ_BE = n(x)':<15} {'Γ ∝ n(n+1)':<15} {'Distinct?'}")
    print("-" * 50)
    for x in [0.1, 0.5, 1.0, 2.0, 5.0]:
        mu = dc.mu_be(x)
        gamma = dc.gamma_rate(x)
        distinct = dc.are_distinct(x)
        print(f"{x:<10.1f} {mu:<15.4f} {gamma:<15.4f} {distinct}")

    # At all physical x, μ ≠ Γ contribution
    for x in [0.1, 0.5, 1.0, 2.0]:
        assert dc.are_distinct(x), f"Should be distinct at x={x}"

    print("\n✓ μ_BE and Γ are physically distinct at all relevant scales")


def demo_6_scenario():
    """Scenario B classification and path to A."""
    print("\n" + "=" * 65)
    print("Demo 6: Scenario Classification & Requirements")
    print("=" * 65)

    sc = ScenarioClassification()

    print(f"\nClassification: Scenario {sc.scenario}")
    print(f"\nRequirement Check (Table 1):")
    print(f"{'ID':<6} {'Target':<30} {'Result':<40} {'Status'}")
    print("-" * 85)
    for r in sc.requirements:
        print(f"{r.id:<6} {r.target:<30} {r.result:<40} {r.status}")

    print(f"\nPath to Scenario A:")
    for step in sc.path_to_scenario_a():
        print(f"  {step}")

    pred = Predictions()
    print(f"\nStructural implications:")
    for p in pred.predictions:
        print(f"  {p.id}: {p.description}")

    assert sc.scenario == "B"
    assert len(pred.predictions) == 4
    print("\n✓ Scenario B classification confirmed")


if __name__ == "__main__":
    print("Derivation of Γ(ρ) from Grid-Mode BE Statistics — Demo")
    print("DOI: 10.6084/m9.figshare.31942821\n")

    demo_1_be_occupation()
    demo_2_von_neumann_entropy()
    demo_3_derivation_chain()
    demo_4_gamma_total()
    demo_5_double_counting()
    demo_6_scenario()

    print("\n" + "=" * 65)
    print("All demos passed successfully.")
    print("=" * 65)
