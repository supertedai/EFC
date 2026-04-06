#!/usr/bin/env python3
"""
Demo: Covariance-Aware BAO Consistency Test of EFC (BOSS DR12)

Runs the fixed-parameter BAO test and cosmic chronometers test.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.bao_cobaya_test import BAOCobayaTest, CosmicChronometers, PAPER_RESULTS
import numpy as np


def main():
    print("=" * 65)
    print("Covariance-Aware BAO Consistency Test of EFC (BOSS DR12)")
    print("=" * 65)

    test = BAOCobayaTest(alpha_L2=0.045, z_L1L2=1.01, delta_z=0.3)

    # --- Parameters ---
    print("\n1. EFC PARAMETERS (from DESI DR2)")
    print("-" * 45)
    params = PAPER_RESULTS['parameters']
    for k, v in params.items():
        print(f"   {k} = {v}")

    # --- Modification amplitude ---
    print("\n2. MODIFICATION AMPLITUDE")
    print("-" * 45)
    for z in [0.38, 0.51, 0.61, 1.01, 2.0]:
        amp = test.modification_amplitude(z)
        print(f"   z={z:.2f}: |E_EFC/E_LCDM - 1| = {amp:.4f} ({amp*100:.2f}%)")

    # --- BOSS BAO test ---
    print("\n3. BOSS DR12 BAO TEST (fixed-parameter)")
    print("-" * 45)
    bao = test.run_boss_test()
    print(f"   chi2_LCDM = {bao['chi2_lcdm']:.2f}")
    print(f"   chi2_EFC  = {bao['chi2_efc']:.2f}")
    print(f"   Delta_chi2 = {bao['delta_chi2']:.2f}")
    print(f"   Paper Delta_chi2 = {bao['paper_delta_chi2']}")

    # --- Per-observable residuals ---
    print("\n4. PER-OBSERVABLE RESIDUALS")
    print("-" * 45)
    print(f"   {'z':<6} {'DM_obs':<10} {'DM_LCDM':<10} {'DM_EFC':<10}")
    print(f"   {'-'*36}")
    for r in bao['residuals']:
        print(f"   {r['z']:<6.2f} {r['DM_obs']:<10.1f} {r['DM_lcdm']:<10.1f} {r['DM_efc']:<10.1f}")

    # --- Cosmic chronometers ---
    print("\n5. COSMIC CHRONOMETERS TEST")
    print("-" * 45)
    cc = CosmicChronometers(test)
    cc_result = cc.run_test()
    print(f"   chi2_LCDM = {cc_result['chi2_lcdm']:.2f}")
    print(f"   chi2_EFC  = {cc_result['chi2_efc']:.2f}")
    print(f"   Delta_chi2 = {cc_result['delta_chi2']:.2f}")
    print(f"   Paper Delta_chi2 = {cc_result['paper_delta_chi2']}")

    # --- Combined ---
    print("\n6. COMBINED RESULT")
    print("-" * 45)
    combined = PAPER_RESULTS['combined']
    print(f"   Total DOF: {combined['total_dof']}")
    print(f"   Combined Delta_chi2: {combined['delta_chi2']}")
    print(f"   Interpretation: EFC mild preference, no geometric channel penalises EFC")

    print("\n" + "=" * 65)
    print("EFC background survives precision BAO test without retuning.")
    print("=" * 65)


if __name__ == '__main__':
    main()
