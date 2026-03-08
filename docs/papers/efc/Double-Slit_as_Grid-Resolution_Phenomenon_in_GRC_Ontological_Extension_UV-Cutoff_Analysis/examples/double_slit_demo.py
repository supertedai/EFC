#!/usr/bin/env python3
"""
Demo: GRC Double-Slit as Grid-Resolution Phenomenon
Working Note v0.2, March 8, 2026

Usage: python double_slit_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.grc_double_slit import (
    GRCAxioms, EntropyClarity, UVCutoffModel,
    PredictionStatus, OpenGaps, FALSIFICATION_POINTS,
)

def main():
    print("GRC Double-Slit — Demo")
    print("Working Note v0.2, March 8, 2026\n")

    # Axioms
    axioms = GRCAxioms()
    print(axioms.summary())
    print()

    # Entropy-clarity function
    C = EntropyClarity(S_max=1.0)
    print("Clarity Function C(S) = exp(-S/S_max)")
    print("=" * 40)
    for S in [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]:
        print(f"  S = {S:.1f}  ->  C(S) = {C(S):.4f}")
    print()

    # UV cutoff — sub-Planck scale
    print("UV-Cutoff: Sub-Planckian l_g")
    print("=" * 50)
    uv_planck = UVCutoffModel(l_g=1.6e-35, sigma=1e-6)
    print(uv_planck.summary())
    print()

    # UV cutoff — hypothetical accessible scale
    print("UV-Cutoff: Hypothetical l_g = 1e-9 m (nanoscale)")
    print("=" * 50)
    uv_nano = UVCutoffModel(l_g=1e-9, sigma=1e-6)
    print(uv_nano.summary())
    print()

    # Scaling demonstration
    print("Deviation scaling with l_g (sigma = 1e-6 m)")
    print("=" * 50)
    print(f"{'l_g (m)':<14} {'sigma/l_g':<14} {'|Delta A|':<16} {'Accessible?'}")
    print("-" * 56)
    for lg_exp in [-35, -20, -15, -10, -9, -8, -7, -6]:
        lg = 10.0**lg_exp
        uv = UVCutoffModel(l_g=lg, sigma=1e-6)
        dev = uv.deviation_bound()
        print(f"{lg:<14.0e} {1e-6/lg:<14.0e} {dev:<16.2e} {uv.is_accessible()}")
    print()

    # Predictions
    ps = PredictionStatus()
    print(ps.summary())
    print()

    # Falsification points
    print("Falsification Points (Section 6)")
    print("=" * 60)
    for fid, condition, ftype in FALSIFICATION_POINTS:
        print(f"  {fid}: {condition}")
        print(f"      Type: {ftype}")
    print()

    # Open gaps
    gaps = OpenGaps()
    print(gaps.summary())
    print()

    # One-line status
    print("One-line status:")
    print("Geometric cutoff (P2) inaccessible for sub-Planckian l_g.")
    print("Quantum distinction, if any, lies in measurement as entropy")
    print("process (P3/P4), not interference geometry.")

if __name__ == "__main__":
    main()
