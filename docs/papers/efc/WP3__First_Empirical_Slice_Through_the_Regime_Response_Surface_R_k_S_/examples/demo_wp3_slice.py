#!/usr/bin/env python3
"""Demo: WP3 First Empirical Slice Through R(k,S).

Shows the RSD-based empirical mapping of one trajectory through the
regime response surface, and model comparison with LCDM.

Author: Morten Magnusson (ORCID 0009-0002-4860-5095)
License: CC-BY-4.0
"""

import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.wp3_rks_slice import RSDMeasurement, WP3Trajectory, ModelComparison


def main():
    print("=" * 65)
    print("WP3 -- First Empirical R(k,S) Slice: Demo")
    print("=" * 65)

    # Load data
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "rsd_measurements.json")
    with open(data_path) as f:
        data = json.load(f)

    # Build trajectory from data
    trajectory = WP3Trajectory()
    for entry in data["measurements"]:
        m = RSDMeasurement(
            survey=entry["survey"],
            z=entry["z"],
            fsigma8=entry["fsigma8"],
            error=entry["error"],
        )
        trajectory.add(m)

    print(f"\nTrajectory: {trajectory}")
    print(f"N points:   {trajectory.n_points()}")
    print(f"z range:    {trajectory.z_range()}")
    print(f"k range:    {trajectory.k_range()}")
    print(f"S range:    {trajectory.S_range()}")

    # Show measurements with structural maturity
    print(f"\n{'Survey':<15} {'z':>6} {'fsig8':>7} {'err':>6} {'k_eff':>6} {'S(z)':>6}")
    print("-" * 52)
    for m in trajectory.measurements:
        print(f"{m.survey:<15} {m.z:6.3f} {m.fsigma8:7.3f} {m.error:6.3f} "
              f"{m.effective_k():6.3f} {m.structural_maturity():6.3f}")

    # Model comparison
    print("\n--- Model Comparison ---")
    comparison = ModelComparison(chi2_lcdm=9.36, chi2_rks=9.12,
                                n_params_lcdm=3, n_params_rks=5)
    summary = comparison.summary()
    for key, val in summary.items():
        print(f"  {key}: {val}")

    # Key result
    print(f"\n--- Key Result ---")
    print(f"R(k~0.13, S~0.30) ~ +0.30")
    print(f"Verdict: {comparison.verdict()}")
    print(f"Epistemic status: cartography (not validation)")

    # Verification
    print("\n--- Verification ---")
    assert trajectory.n_points() == 12, f"Expected 12 points, got {trajectory.n_points()}"
    z_min, z_max = trajectory.z_range()
    assert z_min < 0.4, "Should include low-z data"
    assert z_max > 1.4, "Should include high-z data"

    S_min, S_max = trajectory.S_range()
    assert S_min > 0, "All S values must be positive"
    assert S_max < 1, "All S values must be < 1"

    assert comparison.preferred_model() == "LCDM", "LCDM should be preferred"
    assert comparison.delta_aic() < 0, "ΔAIC should be negative (LCDM preferred)"

    chi2 = trajectory.chi2_lcdm()
    assert chi2 > 0, "Chi-squared must be positive"

    # Test individual measurement
    m0 = trajectory.measurements[0]
    assert m0.structural_maturity() > 0
    assert m0.effective_k() > 0

    print("All checks passed.")
    print("=" * 65)


if __name__ == "__main__":
    main()
