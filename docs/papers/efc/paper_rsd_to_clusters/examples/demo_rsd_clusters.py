#!/usr/bin/env python3
"""
Demo: RSD to Clusters Parameter-Locked Cross-Probe Test

Shows cluster abundance predictions propagated from RSD constraints.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.rsd_to_clusters import RSDToClusterTest, PAPER_RESULTS
import numpy as np


def main():
    print("=" * 65)
    print("From RSD to Clusters: Parameter-Locked Test")
    print("=" * 65)

    test = RSDToClusterTest(alpha_L2=0.34, alpha_L2_err=0.16)

    # --- Input constraint ---
    print("\n1. INPUT CONSTRAINT (from RSD)")
    print("-" * 45)
    inp = PAPER_RESULTS['input_constraint']
    print(f"   alpha_L2 = {inp['alpha_L2']} +/- {inp['alpha_L2_err']}")
    print(f"   Source: {inp['source']}")
    print(f"   mu_EFC(a) = 1 + alpha_L2 * f_transition(a)")

    # --- Abundance prediction ---
    print("\n2. CLUSTER ABUNDANCE PREDICTION")
    print("-" * 45)
    result = test.predict_abundance()
    print(f"   N_EFC / N_LCDM = {result['abundance_ratio']:.3f} +/- {result['abundance_ratio_err']}")
    print(f"   Excess: {result['excess_percent']:+.1f}%")
    print(f"   Key: No parameters fit to cluster data")

    # --- Growth enhancement ---
    print("\n3. GROWTH FACTOR ENHANCEMENT D_EFC/D_LCDM")
    print("-" * 45)
    growth = PAPER_RESULTS['growth_enhancement']
    for z_key, vals in growth.items():
        print(f"   {z_key}: D_ratio = {vals['D_ratio']:.3f} ({vals['delta']})")

    # --- Shape signature ---
    print("\n4. SHAPE SIGNATURE R(z)")
    print("-" * 45)
    shape = test.shape_signature()
    print(f"   {'z':<8} {'R(z)':<8}")
    print(f"   {'-'*16}")
    for z, R in zip(shape['z'], shape['R']):
        marker = " <-- crossover" if abs(R - 1.0) < 0.015 else ""
        print(f"   {z:<8.2f} {R:<8.3f}{marker}")
    print(f"\n   Gradient: {shape['gradient_sign']}")
    print(f"   Crossover at z ~ {shape['crossover_z']:.2f}")
    print(f"   Robust against uniform mass-calibration systematics")

    # --- Falsification ---
    print("\n5. FALSIFICATION CHECK")
    print("-" * 45)
    criteria = test.falsification_check()
    for name, info in criteria.items():
        print(f"   {name}: {info['status']}")

    # --- Target survey ---
    print("\n6. TARGET SURVEY")
    print("-" * 45)
    print(f"   Survey: {PAPER_RESULTS['target_survey']}")
    print(f"   Statistical power: ~2-3 sigma discrimination")

    print("\n" + "=" * 65)
    print("Parameter-locked prediction: +6.4% clusters, negative dR/dz.")
    print("=" * 65)


if __name__ == '__main__':
    main()
