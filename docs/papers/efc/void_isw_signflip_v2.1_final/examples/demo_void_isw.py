#!/usr/bin/env python3
"""
Demo: EFC Void ISW Sign-Flip
==============================
Demonstrates the ISW sign-flip prediction in density-dependent gravity.

DOI: 10.6084/m9.figshare.31942677
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.void_isw import (
    ISWDecomposition,
    ReesSciamaTerm,
    AmplitudeRatio,
    VoidProfile,
    SignFlipAnalysis,
    Predictions,
)


def demo_void_profile():
    """1. Void profile and evolution."""
    print("=" * 65)
    print("DEMO 1: Void Profiles")
    print("=" * 65)

    deltas = [-0.3, -0.5, -0.7, -0.8, -0.9]
    print(f"  {'δ':>6s}  {'ρ/ρ_crit':>10s}  {'dδ/dt':>12s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*12}")
    for d in deltas:
        v = VoidProfile(delta=d)
        print(f"  {d:6.1f}  {v.rho_ratio:10.4f}  {v.d_delta_dt():12.4f}")
    print()


def demo_sign_analysis():
    """2. Sign analysis of the Rees-Sciama term."""
    print("=" * 65)
    print("DEMO 2: Rees-Sciama Sign Analysis")
    print("=" * 65)

    rs = ReesSciamaTerm()
    void = VoidProfile(delta=-0.5)
    result = rs.compute(void)

    print(f"  Void: δ = {result['delta']}, ρ/ρ_crit = {result['rho_ratio']:.4f}")
    print(f"  μ(ρ) = {result['mu']:.4f}")
    print(f"  dμ/dρ = {result['d_mu_d_rho']:.4e}  (positive? {result['sign_analysis']['d_mu_d_rho_positive']})")
    print(f"  dρ/dt = {result['d_rho_dt']:.4e}  (negative? {result['sign_analysis']['d_rho_dt_negative']})")
    print(f"  dμ/dt = {result['d_mu_dt']:.4e}")
    print(f"  RS = δ·dμ/dt = {result['RS']:.4e}  → {result['RS_sign']}")
    print(f"\n  Conclusion: RS > 0 in voids (hot spot), opposing linear ISW (cold spot)")
    print()


def demo_isw_decomposition():
    """3. Full ISW decomposition across void depths."""
    print("=" * 65)
    print("DEMO 3: ISW Decomposition dΦ/dt = μ·dδ/dt + δ·dμ/dt")
    print("=" * 65)

    decomp = ISWDecomposition()
    deltas = [-0.3, -0.5, -0.7, -0.8, -0.9]

    print(f"  {'δ':>6s}  {'ISW_lin':>10s}  {'RS':>10s}  {'Total':>10s}  {'A_total':>8s}  {'Flip?':>6s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*8}  {'-'*6}")
    for d in deltas:
        r = decomp.compute(delta=d)
        flip = "YES" if r["sign_flip"] else "no"
        print(f"  {d:6.1f}  {r['isw_linear']:10.4f}  {r['rees_sciama']:10.4f}  "
              f"{r['total']:10.4f}  {r['A_total']:8.2f}  {flip:>6s}")
    print()


def demo_paper_table():
    """4. Paper Table 1 (exact values)."""
    print("=" * 65)
    print("DEMO 4: Paper Table 1 — ISW Amplitude Ratio")
    print("=" * 65)

    amp = AmplitudeRatio()
    table = amp.paper_table_1()

    print(f"  {'δ':>6s}  {'ρ/ρ_crit':>10s}  {'μ':>6s}  {'RS/ISW':>8s}  {'A_total':>8s}")
    print(f"  {'-'*6}  {'-'*10}  {'-'*6}  {'-'*8}  {'-'*8}")
    for row in table:
        print(f"  {row['delta']:6.1f}  {row['rho_ratio']:10.3f}  {row['mu']:6.2f}  "
              f"{row['rs_over_isw']:8.2f}  {row['A_total']:+8.2f}")

    print(f"\n  Key: A_total crosses zero near δ ≈ -0.7 (sign flip)")
    print(f"       ΛCDM: A_total = 1 for all δ (no turnover)")
    print()


def demo_sign_flip():
    """5. Sign-flip threshold finding."""
    print("=" * 65)
    print("DEMO 5: Sign-Flip Threshold")
    print("=" * 65)

    analysis = SignFlipAnalysis()
    delta_flip = analysis.find_sign_flip()
    print(f"  Sign-flip threshold: δ ≈ {delta_flip}")
    print(f"  Below this depth: void produces HOT spot (not cold)")

    print(f"\n  ΛCDM vs EFC comparison:")
    comparison = analysis.turnover_comparison()
    print(f"  {'δ':>6s}  {'EFC A_total':>12s}  {'EFC signal':>20s}")
    print(f"  {'-'*6}  {'-'*12}  {'-'*20}")
    for row in comparison:
        print(f"  {row['delta']:6.1f}  {row['EFC_A_total']:12.3f}  {row['EFC_signal']:>20s}")
    print()


def demo_predictions():
    """6. Falsifiable predictions."""
    print("=" * 65)
    print("DEMO 6: Falsifiable Predictions")
    print("=" * 65)

    pred = Predictions()
    s = pred.summary()

    for pid in ["P1", "P2", "P3"]:
        p = s[pid]
        print(f"\n  {p['id']}: {p['description']}")
        print(f"       Prediction: {p['prediction']}")
        print(f"       Test: {p['test']}")

    excess = s["ISW_excess"]
    print(f"\n  ISW Excess Anomaly:")
    print(f"       Observed: {excess['observed']}")
    print(f"       EFC predicts: {excess['efc_prediction']}")
    print(f"       Stance: {excess['likely_explanation']}")

    print(f"\n  Falsification: {s['P1']['falsification']}")
    print()


if __name__ == "__main__":
    print()
    print("EFC Void ISW Sign-Flip — Full Demo")
    print("DOI: 10.6084/m9.figshare.31942677")
    print("Author: Morten Magnusson")
    print()

    demo_void_profile()
    demo_sign_analysis()
    demo_isw_decomposition()
    demo_paper_table()
    demo_sign_flip()
    demo_predictions()

    print("=" * 65)
    print("All 6 demonstrations completed successfully.")
    print("Deep voids: cold spot → hot spot (sign flip at δ ≈ -0.7)")
    print("=" * 65)
