#!/usr/bin/env python3
"""
Demo: EFC Phenomenology vs DESI DR2 BAO

Demonstrates EFC w(z) parameterization, model comparison, and BAO fit analysis.
"""

import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from efc_desi_bao import (
    DESIComparison,
    EFCParameters,
    CPLParameters,
    DESI_DR2_BAO,
)


def main():
    print("=" * 60)
    print("EFC vs DESI DR2 BAO -- COMPARATIVE FIT ANALYSIS")
    print("=" * 60)

    comp = DESIComparison()

    # --- Demo 1: EFC w(z) equation of state ---
    print("\n1. EFC-INSPIRED w(z) EQUATION OF STATE")
    print("-" * 40)

    efc = EFCParameters()
    z_samples = [0.0, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
    print(f"  w(z) = {efc.w_late} + ({efc.w_early} - {efc.w_late})"
          f" * tanh[(z - {efc.z_trans}) / {efc.delta_z}]")
    print()
    for z in z_samples:
        w = efc.w(z)
        print(f"  z = {z:.1f}:  w = {w:.4f}")

    # w(z) transitions from near w_late at low z to w_early at high z
    # At z=0, tanh(-z_trans/dz) is large negative, so w(0) is shifted toward w_late side
    w0 = efc.w(0.0)
    w_high = efc.w(5.0)
    assert w0 > w_high, f"w(0)={w0} should exceed w(5)={w_high} since w_early < w_late"
    assert abs(w_high - efc.w_early) < 0.05, f"w(5) = {w_high} not near w_early"
    print("  [PASS] w(z) transitions correctly with redshift")

    # --- Demo 2: Model chi-squared ranking ---
    print("\n2. MODEL CHI-SQUARED RANKING")
    print("-" * 40)

    ranking = comp.model_ranking()
    for i, r in enumerate(ranking, 1):
        print(f"  {i}. {r.model:30s}  chi2 = {r.chi2:.2f}  ({r.assessment})")

    assert ranking[0].model == "EFC (best-fit)"
    assert ranking[-1].model == "LCDM"
    print("  [PASS] EFC ranks first, LCDM ranks last")

    # --- Demo 3: Delta chi-squared comparisons ---
    print("\n3. DELTA CHI-SQUARED")
    print("-" * 40)

    d_efc_lcdm = comp.delta_chi2("EFC", "LCDM")
    d_efc_cpl = comp.delta_chi2("EFC", "w0waCDM")
    d_cpl_lcdm = comp.delta_chi2("w0waCDM", "LCDM")

    print(f"  EFC vs LCDM:    delta_chi2 = {d_efc_lcdm:.2f}")
    print(f"  EFC vs w0waCDM: delta_chi2 = {d_efc_cpl:.2f}")
    print(f"  w0waCDM vs LCDM: delta_chi2 = {d_cpl_lcdm:.2f}")

    assert d_efc_lcdm < -20.0
    assert d_efc_cpl < 0.0
    print("  [PASS] EFC shows strong improvement over LCDM")

    # --- Demo 4: DESI DR2 BAO data points ---
    print("\n4. DESI DR2 BAO DATA POINTS")
    print("-" * 40)

    print(f"  {'z_eff':>6s}  {'Observable':>8s}  {'Value':>8s}  {'Error':>6s}")
    for dp in DESI_DR2_BAO:
        print(f"  {dp.z_eff:6.2f}  {dp.observable:>8s}  {dp.value:8.2f}  {dp.error:6.2f}")

    assert len(DESI_DR2_BAO) == 7
    assert DESI_DR2_BAO[0].z_eff == 0.30
    assert DESI_DR2_BAO[-1].z_eff == 2.33
    print("  [PASS] 7 BAO data points spanning z = 0.30 to 2.33")

    # --- Demo 5: w(z) at data redshifts comparison ---
    print("\n5. w(z) AT DATA REDSHIFTS")
    print("-" * 40)

    w_table = comp.efc_w_at_data_redshifts()
    print(f"  {'z':>6s}  {'w_EFC':>8s}  {'w_LCDM':>8s}  {'w_CPL':>8s}")
    for row in w_table:
        print(f"  {row['z']:6.2f}  {row['w_efc']:8.4f}  {row['w_lcdm']:8.4f}"
              f"  {row['w_cpl']:8.4f}")

    # EFC should differ from LCDM at transition region
    z1_row = [r for r in w_table if r["z"] == 0.93][0]
    assert z1_row["w_efc"] != z1_row["w_lcdm"]
    print("  [PASS] EFC w(z) differs from LCDM near transition")

    # --- Demo 6: Summary output ---
    print("\n6. FULL SUMMARY")
    print("-" * 40)
    print(comp.summary())

    print("\n" + "=" * 60)
    print("ALL DEMOS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
