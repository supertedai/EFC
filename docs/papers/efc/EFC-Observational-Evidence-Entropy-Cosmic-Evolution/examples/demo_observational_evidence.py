#!/usr/bin/env python3
"""Demonstration: EFC Observational Evidence for Entropy in Cosmic Evolution.

Shows:
  1. CMB observables and entropy fluctuations
  2. Structure formation metrics
  3. Galaxy rotation curve analysis
  4. CMB consistency check

Author: Morten Magnusson, ORCID 0009-0002-4860-5095
License: CC-BY-4.0
"""

import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from observational_evidence import (
    CMBObservable,
    StructureFormationMetric,
    GalaxyRotationCurve,
    ObservationalEvidenceModel,
    CMB_TEMPERATURE,
    CMB_ANISOTROPY,
)


def demo_cmb_observables():
    """1. CMB observables and entropy fluctuations."""
    print("=" * 60)
    print("1. CMB OBSERVABLES AND ENTROPY FLUCTUATIONS")
    print("=" * 60)

    for level in [1e-6, 1e-5, 5e-5, 1e-4]:
        obs = CMBObservable(anisotropy_level=level)
        print(f"\n  dT/T = {level:.0e}:")
        print(f"    delta T     = {obs.temperature_fluctuation():.6e} K")
        print(f"    delta s     = {obs.entropy_fluctuation():.6e} J/K")
        print(f"    EFC match:  {obs.is_consistent_with_efc(CMB_ANISOTROPY)}")


def demo_structure_formation():
    """2. Structure formation metrics."""
    print("\n" + "=" * 60)
    print("2. STRUCTURE FORMATION METRICS")
    print("=" * 60)

    metrics = [
        StructureFormationMetric(scale_mpc=8.0, density_contrast=0.01, redshift=0.0),
        StructureFormationMetric(scale_mpc=8.0, density_contrast=0.005, redshift=0.5),
        StructureFormationMetric(scale_mpc=8.0, density_contrast=0.001, redshift=2.0),
        StructureFormationMetric(scale_mpc=8.0, density_contrast=0.0001, redshift=10.0),
    ]

    print(f"\n  {'z':>6}  {'delta':>8}  {'D(z)':>8}  {'sigma_8(z)':>10}")
    print("  " + "-" * 36)
    for m in metrics:
        D = m.growth_factor()
        s8 = m.evolved_sigma_8()
        print(f"  {m.redshift:6.1f}  {m.density_contrast:8.4f}  "
              f"{D:8.4f}  {s8:10.4f}")


def demo_rotation_curves():
    """3. Galaxy rotation curve analysis."""
    print("\n" + "=" * 60)
    print("3. GALAXY ROTATION CURVE ANALYSIS")
    print("=" * 60)

    # Load sample data from data file
    data_path = os.path.join(os.path.dirname(__file__), '..', 'data',
                             'observational_evidence.json')
    with open(data_path) as f:
        data = json.load(f)

    model = ObservationalEvidenceModel()

    for pt in data["sample_rotation_curve"]:
        model.add_rotation_point(
            pt["radius_kpc"], pt["v_obs_km_s"], pt["v_newton_km_s"])

    print(f"\n  {'r (kpc)':>8}  {'v_obs':>8}  {'v_N':>8}  "
          f"{'excess':>8}  {'ratio':>6}  {'needs corr':>10}")
    print("  " + "-" * 55)

    for p in model.rotation_curves:
        print(f"  {p.radius_kpc:8.1f}  {p.velocity_obs_km_s:8.1f}  "
              f"{p.velocity_newton_km_s:8.1f}  {p.velocity_excess():8.1f}  "
              f"{p.excess_ratio():6.2f}  "
              f"{str(p.requires_entropy_correction()):>10s}")

    analysis = model.rotation_curve_analysis()
    print(f"\n  Total points:         {analysis['total_points']}")
    print(f"  Needing correction:   {analysis['needing_correction']}")
    print(f"  Fraction:             {analysis['fraction']:.2%}")
    print(f"  Max excess ratio:     {analysis['max_excess_ratio']:.2f}")


def demo_cmb_consistency():
    """4. CMB consistency check."""
    print("\n" + "=" * 60)
    print("4. CMB CONSISTENCY CHECK")
    print("=" * 60)

    model = ObservationalEvidenceModel()
    for l_val in [2, 10, 100, 500, 1000, 2000]:
        model.add_cmb(multipole=l_val, cl=float(l_val) * 10.0)

    result = model.cmb_consistency(predicted_anisotropy=CMB_ANISOTROPY)
    print(f"\n  Predicted dT/T = {CMB_ANISOTROPY:.0e}")
    print(f"  All consistent: {result['all_consistent']}")
    for r in result["checks"]:
        print(f"    l = {r['multipole']:>5d}  consistent: {r['consistent']}")


if __name__ == "__main__":
    print("EFC: Observational Evidence for Entropy in Cosmic Evolution")
    print("Magnusson (2026)")
    print()

    demo_cmb_observables()
    demo_structure_formation()
    demo_rotation_curves()
    demo_cmb_consistency()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully.")
    print("=" * 60)
