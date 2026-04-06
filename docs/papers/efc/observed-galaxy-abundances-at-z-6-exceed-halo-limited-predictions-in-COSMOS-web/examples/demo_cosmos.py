#!/usr/bin/env python3
"""
COSMOS-Web Galaxy Abundance Excess Demo
=========================================
Demonstrates galaxy sample analysis, halo mass function comparison,
abundance excess computation, and redshift bin analysis.

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

from src.cosmos_abundances import (
    GalaxySample,
    HaloMassFunction,
    AbundanceExcess,
    RedshiftBin,
)


def demo_galaxy_sample():
    """Demo 1: Galaxy sample construction and filtering."""
    print("=" * 60)
    print("Demo 1: Galaxy Sample Analysis")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "cosmos_abundance_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    sample = GalaxySample(data["sample_galaxies"], mass_cut=9.0)
    print(f"\n  Total galaxies: {sample.n_total}")
    print(f"  Mass cut: log M*/Msun > {sample.mass_cut}")

    above_cut = sample.above_mass_cut()
    print(f"  Above mass cut: {len(above_cut)}")

    # All sample galaxies should be above the mass cut
    assert len(above_cut) == sample.n_total, (
        f"Expected all {sample.n_total} above cut, got {len(above_cut)}"
    )

    # Test redshift filtering
    high_z = sample.in_redshift_range(10.0, 15.0)
    print(f"  Galaxies at z > 10: {len(high_z)}")
    assert len(high_z) > 0, "Should have galaxies at z > 10"

    for g in high_z:
        assert g["z_phot"] >= 10.0, f"Galaxy {g['id']} z={g['z_phot']} below z_min"

    # Test bin counting
    bins = [(5.0, 7.0), (7.0, 9.0), (9.0, 11.0), (11.0, 15.0)]
    dist = sample.redshift_distribution(bins)
    total_binned = sum(b["count"] for b in dist)
    assert total_binned == sample.n_total, (
        f"Binned total {total_binned} != sample size {sample.n_total}"
    )

    print(f"\n  Redshift distribution:")
    for b in dist:
        print(f"    z=[{b['z_min']:.0f}, {b['z_max']:.0f}): {b['count']} galaxies")

    print(f"\n  [PASS] All {sample.n_total} galaxies above mass cut")
    print(f"  [PASS] Redshift bins sum to total ({total_binned})")
    return True


def demo_halo_mass_function():
    """Demo 2: Halo mass function LCDM predictions."""
    print("\n" + "=" * 60)
    print("Demo 2: Halo Mass Function Predictions")
    print("=" * 60)

    hmf = HaloMassFunction(survey_area_deg2=0.54, mass_threshold=11.0)
    print(f"\n  {hmf}")

    redshifts = [3.0, 5.0, 7.0, 9.0, 11.0, 13.0]
    print(f"\n  {'z':>5s}  {'Predicted N':>12s}  {'Density':>10s}")
    print(f"  {'---':>5s}  {'-----------':>12s}  {'-------':>10s}")

    prev_count = float("inf")
    for z in redshifts:
        count = hmf.predicted_count(z)
        density = hmf.predicted_density(z)
        print(f"  {z:5.1f}  {count:12.1f}  {density:10.4f}")

        # Predictions should decrease with redshift
        assert count < prev_count, f"Predicted count not decreasing at z={z}"
        assert count > 0, f"Predicted count should be positive at z={z}"
        prev_count = count

    print(f"\n  [PASS] LCDM predictions decrease monotonically with redshift")
    print(f"  [PASS] All predictions positive")
    return True


def demo_abundance_excess():
    """Demo 3: Abundance excess computation."""
    print("\n" + "=" * 60)
    print("Demo 3: Abundance Excess Analysis")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "cosmos_abundance_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    print(f"\n  {'z Range':>12s}  {'Observed':>9s}  {'Predicted':>10s}  {'Excess':>7s}  {'Sigma':>7s}")
    print(f"  {'-'*12}  {'-'*9}  {'-'*10}  {'-'*7}  {'-'*7}")

    prev_factor = 0.0
    for bin_data in data["redshift_bins"]:
        excess = AbundanceExcess(bin_data["observed"], bin_data["predicted_lcdm"])
        z_label = f"[{bin_data['z_min']:.0f}, {bin_data['z_max']:.0f})"
        print(
            f"  {z_label:>12s}  {excess.observed:9.0f}  {excess.predicted:10.1f}  "
            f"{excess.excess_factor:6.1f}x  {excess.excess_sigma:7.1f}"
        )

        assert excess.is_excess, f"Expected excess at z>{bin_data['z_min']}"
        assert excess.excess_factor >= 1.0, f"Excess factor should be >= 1"

    # Excess should grow with redshift (check first and last)
    first = AbundanceExcess(
        data["redshift_bins"][0]["observed"],
        data["redshift_bins"][0]["predicted_lcdm"],
    )
    last = AbundanceExcess(
        data["redshift_bins"][-1]["observed"],
        data["redshift_bins"][-1]["predicted_lcdm"],
    )
    assert last.excess_factor > first.excess_factor, (
        "Excess should grow with redshift"
    )

    print(f"\n  [PASS] All bins show excess (observed > predicted)")
    print(f"  [PASS] Excess grows: {first.excess_factor:.1f}x at z~5.5 -> {last.excess_factor:.1f}x at z~13.5")
    return True


def demo_redshift_bins():
    """Demo 4: RedshiftBin analysis with log excess."""
    print("\n" + "=" * 60)
    print("Demo 4: Redshift Bin Analysis")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "cosmos_abundance_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    bins = []
    for bd in data["redshift_bins"]:
        rb = RedshiftBin(
            z_min=bd["z_min"],
            z_max=bd["z_max"],
            observed_count=bd["observed"],
            predicted_count=bd["predicted_lcdm"],
        )
        bins.append(rb)

    print(f"\n  {'z_mid':>5s}  {'dz':>4s}  {'log(excess)':>12s}  {'Excess':>7s}")
    print(f"  {'-----':>5s}  {'--':>4s}  {'-----------':>12s}  {'------':>7s}")

    for rb in bins:
        print(f"  {rb.z_mid:5.1f}  {rb.dz:4.1f}  {rb.log_excess:12.2f}  {rb.excess.excess_factor:6.1f}x")

    # Log excess should be monotonically increasing
    for i in range(1, len(bins)):
        assert bins[i].log_excess >= bins[i - 1].log_excess, (
            f"Log excess not monotonic: z={bins[i].z_mid} < z={bins[i-1].z_mid}"
        )

    # At z > 10, log excess should be > 1 (factor > 10)
    high_z_bins = [b for b in bins if b.z_mid > 10]
    for b in high_z_bins:
        assert b.log_excess > 1.0, (
            f"At z={b.z_mid}, log excess {b.log_excess:.2f} should be > 1.0"
        )

    print(f"\n  [PASS] Log excess monotonically increases with redshift")
    print(f"  [PASS] z > 10 bins show > 10x excess")
    return True


def demo_full_analysis():
    """Demo 5: Full analysis pipeline combining all components."""
    print("\n" + "=" * 60)
    print("Demo 5: Full Analysis Pipeline")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "cosmos_abundance_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    # Step 1: Build sample
    sample = GalaxySample(data["sample_galaxies"], mass_cut=9.0)
    hmf = HaloMassFunction(survey_area_deg2=0.54)

    print(f"\n  Step 1 - Sample: {sample.n_total} galaxies, mass cut > {sample.mass_cut}")

    # Step 2: Compute excess in bins from data
    total_observed = sum(b["observed"] for b in data["redshift_bins"])
    total_predicted = sum(b["predicted_lcdm"] for b in data["redshift_bins"])
    total_excess = AbundanceExcess(total_observed, total_predicted)

    print(f"\n  Step 2 - Total excess:")
    print(f"    Observed:  {total_observed}")
    print(f"    Predicted: {total_predicted:.0f}")
    print(f"    Factor:    {total_excess.excess_factor:.1f}x")

    assert total_excess.is_excess, "Total should show excess"
    assert total_observed > total_predicted, "More observed than predicted"

    # Step 3: Find the tension threshold
    for bd in data["redshift_bins"]:
        if bd["excess_factor"] > 2.0:
            tension_z = bd["z_min"]
            break
    else:
        tension_z = None

    print(f"\n  Step 3 - Tension threshold: z > {tension_z}")
    assert tension_z is not None, "Should find tension threshold"
    assert tension_z <= 8.0, f"Tension should appear by z=8, got z={tension_z}"

    # Step 4: Verify key findings
    findings = data["key_findings"]
    assert findings["excess_grows_with_redshift"] is True
    assert findings["consistent_with_efc"] is True

    print(f"\n  Step 4 - Key findings verified:")
    print(f"    Excess grows with redshift: {findings['excess_grows_with_redshift']}")
    print(f"    Strongest tension: {findings['strongest_tension']}")

    print(f"\n  [PASS] Pipeline complete: {total_excess.excess_factor:.1f}x total excess")
    print(f"  [PASS] Tension threshold at z > {tension_z}")
    return True


def demo_survey_properties():
    """Demo 6: Survey property validation."""
    print("\n" + "=" * 60)
    print("Demo 6: Survey Property Validation")
    print("=" * 60)

    data_path = os.path.join(_pkg, "data", "cosmos_abundance_data.json")
    with open(data_path, "r") as f:
        data = json.load(f)

    survey = data["survey"]
    print(f"\n  Survey: {survey['name']}")
    print(f"  Instrument: {survey['instrument']}")
    print(f"  Area: {survey['area_deg2']} deg^2")
    print(f"  Sample: {survey['total_sample']} galaxies")
    print(f"  Mass cut: {survey['mass_cut']}")
    print(f"  Redshift: {survey['redshift_range']}")

    assert survey["name"] == "COSMOS-Web", "Wrong survey name"
    assert survey["instrument"] == "JWST", "Wrong instrument"
    assert survey["total_sample"] == 8447, f"Wrong sample size: {survey['total_sample']}"
    assert survey["area_deg2"] > 0, "Area must be positive"

    # Verify sample galaxies have required columns
    required_columns = ["id", "ra", "dec", "z_phot", "mass_med", "sfr_med"]
    for g in data["sample_galaxies"]:
        for col in required_columns:
            assert col in g, f"Galaxy {g.get('id', '?')} missing column {col}"

    # Verify coordinate ranges
    for g in data["sample_galaxies"]:
        assert 0 <= g["ra"] <= 360, f"RA out of range: {g['ra']}"
        assert -90 <= g["dec"] <= 90, f"Dec out of range: {g['dec']}"
        assert g["z_phot"] > 0, f"Redshift must be positive: {g['z_phot']}"
        assert g["mass_med"] >= 9.0, f"Mass below cut: {g['mass_med']}"

    print(f"\n  [PASS] Survey properties match COSMOS-Web specifications")
    print(f"  [PASS] All {len(data['sample_galaxies'])} galaxies have valid coordinates and properties")
    return True


if __name__ == "__main__":
    results = []
    results.append(("Demo 1: Galaxy Sample", demo_galaxy_sample()))
    results.append(("Demo 2: Halo Mass Function", demo_halo_mass_function()))
    results.append(("Demo 3: Abundance Excess", demo_abundance_excess()))
    results.append(("Demo 4: Redshift Bins", demo_redshift_bins()))
    results.append(("Demo 5: Full Pipeline", demo_full_analysis()))
    results.append(("Demo 6: Survey Validation", demo_survey_properties()))

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        print(f"  [{status}] {name}")
    print(f"\n  {sum(1 for _, p in results if p)}/{len(results)} demos passed")
