"""
Demo: Entropy-Bounded Empiricism (EBE) SPARC175 Analysis.

Demonstrates regime classification, success rate computation,
and statistical summary for galaxy rotation curve analysis.

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
License: CC-BY-4.0
"""

import json
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ebe_sparc175 import (
    EntropyBoundedEmpiricism,
    Galaxy,
    Regime,
    RegimeClassifier,
    RegimeThresholds,
)


def load_example_galaxies() -> list[Galaxy]:
    """Load example galaxies from the data file."""
    data_path = os.path.join(
        os.path.dirname(__file__), "..", "data", "ebe_sparc175_data.json"
    )
    with open(data_path) as f:
        data = json.load(f)
    galaxies = []
    for g in data["example_galaxies"]:
        galaxies.append(
            Galaxy(
                name=g["name"],
                L_value=g["L_value"],
                S_estimate=g["S_estimate"],
                chi2_efc=g["chi2_efc"],
                chi2_lcdm=g["chi2_lcdm"],
            )
        )
    return galaxies


def main():
    print("=" * 60)
    print("Entropy-Bounded Empiricism (EBE) - SPARC175 Demo")
    print("=" * 60)

    # 1. Demonstrate regime classification
    print("\n--- Regime Classification ---")
    classifier = RegimeClassifier()
    test_L_values = [0.15, 0.30, 0.38, 0.45, 0.60]
    for L in test_L_values:
        regime = classifier.classify(L)
        S = classifier.L_to_S(L)
        valid = classifier.is_empirically_valid(S)
        print(f"  L={L:.2f} -> {regime.value:12s}  S={S:.3f}  valid={valid}")

    # 2. Load example galaxies and run full analysis
    print("\n--- Example Galaxy Analysis ---")
    galaxies = load_example_galaxies()
    ebe = EntropyBoundedEmpiricism(galaxies=galaxies)

    classified = ebe.classify_all()
    for regime, gals in classified.items():
        names = ", ".join(g.name for g in gals)
        print(f"  {regime.value}: {names or '(none)'}")

    # 3. Success rates
    print("\n--- Success Rates ---")
    for regime in Regime:
        efc_rate = ebe.success_rate(regime, "efc")
        lcdm_rate = ebe.success_rate(regime, "lcdm")
        print(f"  {regime.value:12s}  EFC={efc_rate:.1%}  LCDM={lcdm_rate:.1%}")

    # 4. Regime summary
    print("\n--- Regime Summary ---")
    summary = ebe.regime_summary()
    for regime_name, stats in summary.items():
        print(f"  {regime_name}: n={stats['n']}, "
              f"EFC success={stats['efc_success_rate']:.1%}, "
              f"mean_L={stats['mean_L']:.3f}")

    # 5. Effect size
    print("\n--- Effect Size (Cliff's delta) ---")
    flow_chi2 = [g.chi2_efc for g in classified[Regime.FLOW]]
    other_chi2 = [
        g.chi2_efc
        for r in [Regime.TRANSITION, Regime.LATENT]
        for g in classified[r]
    ]
    if flow_chi2 and other_chi2:
        delta = EntropyBoundedEmpiricism.cliffs_delta(flow_chi2, other_chi2)
        print(f"  Cliff's delta (FLOW vs others): {delta:.3f}")

    # 6. Thresholds
    print("\n--- Regime Thresholds ---")
    t = classifier.thresholds
    print(f"  L1={t.L1}, L2={t.L2}")
    print(f"  S bounds=[{t.S_lower}, {t.S_upper}]")

    print("\n" + "=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
