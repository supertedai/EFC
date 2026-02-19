#!/usr/bin/env python3
"""
Demo: EFC CMB Localization Study
DOI: 10.6084/m9.figshare.31368433

Usage: python localization_demo.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.cmb_localization import (
    BackgroundGate, MuSigmaValley, ALDegeneracy,
    GrowthSignTest, SurvivingSignalSpec,
)

def main():
    print("EFC CMB Localization Study — Demo")
    print("DOI: 10.6084/m9.figshare.31368433\n")

    # Phase 1
    gate = BackgroundGate()
    print(gate.joint_fit_summary())
    print()

    # Phase 2
    valley = MuSigmaValley()
    sp = valley.sweet_spot()
    print(f"Phase 2 sweet spot: mu={sp.mu}, Sigma={sp.sigma_mg}, dchi2={sp.delta_chi2}")
    print(f"Lensing fit: Sigma_min = {valley.sigma_lensing_fit} +/- {valley.sigma_lensing_uncertainty}")
    print()

    # Phase 3
    al = ALDegeneracy()
    print(al.summary())
    print()

    # Phase 4
    b0 = GrowthSignTest()
    print(b0.sign_constraint_summary())
    print()

    # Phase 5
    spec = SurvivingSignalSpec()
    print(spec.summary())

if __name__ == "__main__":
    main()
