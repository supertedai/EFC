#!/usr/bin/env python3
"""
Demo: Transition Metric Interpretation of Fugaku-DESI Matter Density Offset

Computes Delta_F and checks regime consistency.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.transition_metric import TransitionMetric, TransitionKernel, PAPER_RESULTS
import numpy as np


def main():
    print("=" * 65)
    print("Transition Metric: Fugaku-DESI Matter Density Offset")
    print("=" * 65)

    # --- Setup ---
    tm = TransitionMetric(delta_mu=0.1, a_t=0.55, sigma=0.3)

    # --- mu profile ---
    print("\n1. EFFECTIVE COUPLING mu(a) PROFILE")
    print("-" * 45)
    test_points = [
        ('CMB', 1100),
        ('High-z', 3.0),
        ('Transition', 0.82),
        ('BOSS', 0.51),
        ('Today', 0.0),
    ]
    for label, z in test_points:
        a = 1.0 / (1.0 + z)
        mu = float(tm.kernel.mu(np.array([a]))[0])
        print(f"   {label:<12} z={z:<8} a={a:.6f}  mu={mu:.6f}  mu-1={mu-1:.2e}")

    # --- Transition estimator ---
    print("\n2. TRANSITION ESTIMATOR Delta_F")
    print("-" * 45)
    delta_F = tm.compute_delta_F()
    print(f"   Delta_F = {delta_F:.4f}")
    print(f"   Paper value: {PAPER_RESULTS['delta_F']}")
    print(f"   Interpretation: {PAPER_RESULTS['interpretation']}")

    # --- Regime consistency ---
    print("\n3. REGIME CONSISTENCY CHECK")
    print("-" * 45)
    check = tm.consistency_check()
    for regime, info in check.items():
        print(f"   {regime:<15} z={info.get('z', 'N/A'):<8} "
              f"status: {info['status']}")
        if 'mu' in info:
            print(f"   {'':15} mu={info['mu']:.6f}")
        if 'Delta_F' in info:
            print(f"   {'':15} Delta_F={info['Delta_F']:.4f}")

    # --- Paper reference ---
    print("\n4. PAPER REFERENCE VALUES")
    print("-" * 45)
    for cond in PAPER_RESULTS['consistency_conditions']:
        print(f"   {cond['regime']:<15} {cond['requirement']:<35} [{cond['status']}]")

    # --- Data sources ---
    print("\n5. DATA SOURCES")
    print("-" * 45)
    for src in PAPER_RESULTS['data_sources']:
        print(f"   {src['name']}: {src['reference']}")

    print("\n" + "=" * 65)
    print("Density offset reinterpreted as integrated transition strength.")
    print("=" * 65)


if __name__ == '__main__':
    main()
