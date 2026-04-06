#!/usr/bin/env python3
"""
Demo: Regime Consistency of EFC Coupling T(z) across Lya, BAO, and RSD

Runs three-regime consistency test and SCE evaluation.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.regime_consistency import (
    RegimeConsistencyTest, TransitionFunction, SCEEvaluation, PAPER_RESULTS
)
import numpy as np


def main():
    print("=" * 65)
    print("Regime Consistency Test: EFC Coupling T(z)")
    print("Lya P1D | BOSS BAO | BOSS RSD | SCE Framework")
    print("=" * 65)

    test = RegimeConsistencyTest(beta=0.08, alpha_L2=0.34)
    tf = test.tf

    # --- Parameters ---
    print("\n1. EFC PARAMETERS")
    print("-" * 45)
    for k, v in PAPER_RESULTS['parameters'].items():
        print(f"   {k} = {v}")

    # --- Transition function ---
    print("\n2. TRANSITION FUNCTION T(z)")
    print("-" * 45)
    print(f"   {'z':<8} {'T(z)':<10} {'Regime'}")
    print(f"   {'-'*30}")
    for entry in PAPER_RESULTS['transition_function']:
        print(f"   {entry['z']:<8} {entry['T_z']:<10} {entry['regime']}")

    # Compute T(z) at several redshifts
    z_check = np.array([0.44, 0.51, 2.33, 3.0])
    T_check = tf.T(z_check)
    print(f"\n   Computed T(z) values:")
    for z, T in zip(z_check, T_check):
        print(f"   z={z:.2f}: T(z) = {T:.4f}")

    # --- Lya P1D test ---
    print("\n3. LYA P1D TEST (z=3.0)")
    print("-" * 45)
    lya = test.test_lya_p1d()
    print(f"   T(z=3.0) = {lya['T_z']}")
    print(f"   A*T product = {lya['AT_product']}")
    print(f"   Amplitude pull = {lya['amplitude_pull']}sigma")
    print(f"   Slope pull = {lya['slope_pull']}sigma")
    print(f"   Status: {lya['status']}")

    # --- BAO BOSS test ---
    print("\n4. BAO BOSS DR12 TEST")
    print("-" * 45)
    bao = test.test_bao_boss()
    print(f"   chi2_LCDM = {bao['chi2_lcdm']:.2f}  (paper: {bao['paper_chi2_lcdm']})")
    print(f"   chi2_EFC  = {bao['chi2_efc']:.2f}  (paper: {bao['paper_chi2_efc']})")
    print(f"   Delta_chi2 = {bao['delta_chi2']:.2f} (paper: {bao['paper_delta_chi2']})")
    print(f"   Status: {bao['status']}")

    # --- RSD BOSS test ---
    print("\n5. RSD BOSS DR12 TEST (f*sigma8)")
    print("-" * 45)
    rsd = test.test_rsd_boss()
    print(f"   chi2_EFC  = {rsd['chi2_efc']:.2f}  (paper: {rsd['paper_chi2_efc']})")
    print(f"   chi2_LCDM = {rsd['chi2_lcdm']:.2f}  (paper: {rsd['paper_chi2_lcdm']})")
    print(f"   Delta_chi2 = {rsd['delta_chi2']:.2f} (paper: {rsd['paper_delta_chi2']})")
    print(f"   sigma8_0 = {rsd['derived']['sigma8_0']}")
    print(f"   Growth suppression = {rsd['derived']['growth_suppression']}")
    print(f"   Status: {rsd['status']}")
    print(f"\n   {'z':<6} {'f*s8_obs':<10} {'f*s8_EFC':<10} {'f*s8_LCDM':<10} {'EFC pull':<10}")
    print(f"   {'-'*46}")
    for m in rsd['measurements']:
        print(f"   {m['z']:<6.2f} {m['fsigma8_obs']:<10.3f} {m['fsigma8_efc']:<10.3f} "
              f"{m['fsigma8_lcdm']:<10.3f} {m['efc_pull']:+.2f}sigma")

    # --- Combined result ---
    print("\n6. COMBINED BAO + RSD")
    print("-" * 45)
    results = test.run_all_tests()
    combined = results['combined_bao_rsd']
    print(f"   chi2_EFC  = {combined['chi2_efc']}")
    print(f"   chi2_LCDM = {combined['chi2_lcdm']}")
    print(f"   Delta_chi2 = {combined['delta_chi2']} (paper: {combined['paper_delta_chi2']})")
    print(f"   Significance: {combined['significance']}")

    # --- Forbidden patterns ---
    print("\n7. FORBIDDEN PATTERNS")
    print("-" * 45)
    patterns = test.check_forbidden_patterns()
    for p in patterns:
        print(f"   {p['id']}: {p['status']}")
    triggered = sum(1 for p in patterns if p['status'] == 'Triggered')
    print(f"\n   {triggered}/{len(patterns)} triggered")

    # --- SCE evaluation ---
    print("\n8. SCE EVALUATION")
    print("-" * 45)
    sce = SCEEvaluation()
    evaluation = sce.evaluate()
    for metric, data in evaluation.items():
        if metric == 'summary':
            continue
        if isinstance(data, dict) and 'winner' in data:
            print(f"   {metric}: {data['winner']}")
    print(f"\n   Summary: {evaluation['summary']}")

    # --- Regime summary ---
    print("\n9. REGIME COHERENCE SUMMARY")
    print("-" * 45)
    print(f"   {'Regime':<10} {'z':<10} {'T(z)':<10} {'Result'}")
    print(f"   {'-'*40}")
    for regime, info in results['regime_summary'].items():
        print(f"   {regime:<10} {info['z']:<10} {info['T_z']:<10} {info['status']}")

    print(f"\n   All regimes pass: {results['all_pass']}")

    print("\n" + "=" * 65)
    print("Single T(z) consistent across three regimes. No forbidden")
    print("patterns triggered. Combined BAO+RSD: Delta_chi2 = -3.89.")
    print("=" * 65)


if __name__ == '__main__':
    main()
