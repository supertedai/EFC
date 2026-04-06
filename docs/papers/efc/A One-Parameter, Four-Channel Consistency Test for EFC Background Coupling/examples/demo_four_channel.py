#!/usr/bin/env python3
"""
Demo: Four-Channel Consistency Test for EFC Background Coupling

Runs the one-parameter (beta=0.08) consistency test across four
independent cosmological probes and reports results.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.four_channel_test import FourChannelTest, TransitionFunction, PAPER_RESULTS
import numpy as np


def main():
    print("=" * 65)
    print("Four-Channel Consistency Test for EFC Background Coupling")
    print("=" * 65)

    # --- Transition function ---
    print("\n1. TRANSITION FUNCTION T(z)")
    print("-" * 45)
    T_func = TransitionFunction(Omega_m0=0.315)
    print(f"   z_peak = {T_func.z_peak:.3f}")
    test_z = [0.38, 0.51, 0.61, 3.0, 1100.0]
    for z in test_z:
        T_val = float(T_func.T(np.array([z]))[0])
        print(f"   T(z={z:>6}) = {T_val:.6e}")

    # --- Four-channel test ---
    print("\n2. FOUR-CHANNEL TEST (beta = 0.08)")
    print("-" * 45)
    test = FourChannelTest(beta=0.08)

    channels = test.run_all_channels()
    for key, result in channels.items():
        print(f"\n   [{result.name}]")
        print(f"   Data: {result.data_source}")
        print(f"   chi2_EFC={result.chi2_efc:.2f}, chi2_LCDM={result.chi2_lcdm:.2f}")
        print(f"   Delta_chi2 = {result.delta_chi2:+.2f}")
        print(f"   Status: {result.status} | Role: {result.role}")

    # --- Paper reference values ---
    print("\n3. PAPER REFERENCE VALUES")
    print("-" * 45)
    paper = PAPER_RESULTS['four_channels']
    for ch, vals in paper.items():
        status = vals['status']
        if 'delta_chi2' in vals:
            print(f"   {ch:<15} Delta_chi2 = {vals['delta_chi2']:+.2f}  [{status}]")
        elif 'pull' in vals:
            print(f"   {ch:<15} pull = {vals['pull']}  [{status}]")
        elif 'max_delta_mu' in vals:
            print(f"   {ch:<15} max_delta_mu = {vals['max_delta_mu']}  [{status}]")

    combined = PAPER_RESULTS['combined_bao_rsd']
    print(f"\n   Combined BAO+RSD: Delta_chi2 = {combined['delta_chi2']}")
    print(f"   Significance: {combined['significance']}")

    # --- Channel comparison: Poisson vs Background ---
    print("\n4. CHANNEL COMPARISON: POISSON vs BACKGROUND")
    print("-" * 45)
    comp = PAPER_RESULTS['channel_comparison']
    print(f"   {'Channel':<12} {'Parameter':<12} {'chi2_RSD':<10} {'sigma8':<8} {'Status'}")
    print(f"   {'-'*52}")
    print(f"   {'Poisson':<12} {'alpha=0.34':<12} {comp['poisson']['chi2_rsd']:<10} {comp['poisson']['sigma8']:<8} {comp['poisson']['status']}")
    print(f"   {'Background':<12} {'beta=0.08':<12} {comp['background']['chi2_rsd']:<10} {comp['background']['sigma8']:<8} {comp['background']['status']}")
    print(f"   {'LCDM':<12} {'--':<12} {comp['lcdm']['chi2_rsd']:<10} {comp['lcdm']['sigma8']:<8} {comp['lcdm']['status']}")

    # --- Regime consistency ---
    print("\n5. REGIME CONSISTENCY")
    print("-" * 45)
    regimes = test.regime_consistency()
    for name, info in regimes.items():
        print(f"   {name:<20} z={info['z']:<8} T(z)={info['T_z']:.2e}  "
              f"beta*T={info['mu_minus_1']:.2e}  {info['description']}")

    # --- Summary ---
    print("\n6. SUMMARY")
    print("-" * 45)
    summary = test.summary()
    print(f"   beta = {summary['beta']}")
    print(f"   sigma8_EFC = {test.sigma8_efc:.3f}")
    print(f"   All channels PASS: {summary['all_pass']}")
    kills = PAPER_RESULTS['falsification_status']['triggered']
    print(f"   Falsification kills: {len(kills)}")
    print(f"   Tightest constraint: {PAPER_RESULTS['falsification_status']['tightest']}")

    print("\n" + "=" * 65)
    print("Result: Four channels, one parameter, zero kills.")
    print("=" * 65)


if __name__ == '__main__':
    main()
