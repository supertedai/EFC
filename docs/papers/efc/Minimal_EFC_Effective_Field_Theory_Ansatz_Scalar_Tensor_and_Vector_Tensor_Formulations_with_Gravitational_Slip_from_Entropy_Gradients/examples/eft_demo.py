#!/usr/bin/env python3
"""
Demo: EFC EFT Ansatz — Scalar-Tensor and Vector-Tensor Formulations
DOI: 10.6084/m9.figshare.31368433

Usage: python eft_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from src.efc_eft_ansatz import (
    EntropyField, TargetSignature, ScalarTensorEFT,
    VectorTensorEFT, print_comparison,
)

def main():
    print("EFC EFT Ansatz — Demo")
    print("DOI: 10.6084/m9.figshare.31368433\n")

    # Target signature
    target = TargetSignature()
    print(target.summary())
    print()

    # Entropy field
    S = EntropyField(a_t=0.30, Delta=0.3)
    a_vals = np.array([0.1, 0.2, 0.3, 0.5, 0.7, 1.0])
    print("Entropy Field S(a):")
    print(f"{'a':>6} {'z':>6} {'S(a)':>8} {'dS/dlna':>10} {'mu_growth':>10}")
    for a in a_vals:
        z = 1.0 / a - 1.0
        print(f"{a:>6.2f} {z:>6.1f} {S(a):>8.4f} {S.dS_dlna(a):>10.4f} {S.mu_growth(a):>10.4f}")
    print()

    # Scalar-tensor EFT
    st = ScalarTensorEFT(B0=1.0, M0=1.0, a_t=0.30, Delta=0.3)
    print(st.summary())
    print()

    print("Alpha functions across transition:")
    print(f"{'a':>6} {'alpha_B':>10} {'alpha_M':>10} {'Q_S':>10}")
    for a in a_vals:
        print(f"{a:>6.2f} {st.alpha_B(a):>10.4f} {st.alpha_M(a):>10.4f} {st.no_ghost_QS(a):>10.4f}")
    print()

    # Vector-tensor EFT
    vt = VectorTensorEFT(beta=1.0, m2=1.0, a_t=0.30, Delta=0.3)
    print(vt.summary())
    print()

    print("Slip estimate (schematic) across transition:")
    print(f"{'a':>6} {'eta-1 estimate':>16}")
    for a in a_vals:
        print(f"{a:>6.2f} {vt.slip_estimate(a):>16.6f}")
    print()

    # Comparison
    print(print_comparison())

if __name__ == "__main__":
    main()
