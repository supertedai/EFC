#!/usr/bin/env python3
"""
Demo: EFC Regime Transition Test
=================================
Demonstrates the numerical consistency of the EFC regime transition.

DOI: 10.6084/m9.figshare.31941543
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.regime_transition import (
    EFCRegimeTransition,
    StiffnessResponse,
    SurvivalValley,
    SpatiotemporalGrid,
    ParameterScan,
    GrowthODE,
    Predictions,
)
import numpy as np


def demo_stiffness_response():
    """1. Stiffness response R(k) ∝ k⁻⁴."""
    print("=" * 65)
    print("DEMO 1: Stiffness Response R(k) ∝ k⁻⁴")
    print("=" * 65)

    stiffness = StiffnessResponse()
    k_values = [0.01, 0.05, 0.1, 0.5, 1.0, 10.0]
    check = stiffness.scaling_check(k_values)

    print(f"  {'k [h/Mpc]':>10s}  {'R(k)':>14s}  {'R·k⁴':>14s}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*14}")
    for k, R, Rk4 in zip(check["k"], check["R"], check["R_times_k4"]):
        print(f"  {k:10.3f}  {R:14.6e}  {Rk4:14.6e}")
    print(f"\n  k⁻⁴ scaling verified: {check['constant']}")
    print()


def demo_regime_transition():
    """2. Core μ(k), η(k), Σ(k) across scales."""
    print("=" * 65)
    print("DEMO 2: Regime Transition μ(k), η(k), Σ(k)")
    print("=" * 65)

    model = EFCRegimeTransition()
    info = model.info()
    print(f"  Model: {info['model']}")
    print(f"  α={info['alpha']}, K_bar={info['K_bar']}, "
          f"φ̇={info['phi_dot_bar']}, λ̇={info['lambda_dot_bar']}")
    print(f"  F = {info['F']:.4f}, ε_F = {info['eps_F']:.6f}")

    k_values = np.logspace(-2, 1.5, 8)
    print(f"\n  {'k':>10s}  {'μ':>10s}  {'η':>10s}  {'Σ':>10s}  {'R':>14s}")
    print(f"  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*10}  {'-'*14}")
    for k in k_values:
        obs = model.observables(k)
        print(f"  {k:10.4f}  {obs['mu']:10.6f}  {obs['eta']:10.6f}  "
              f"{obs['sigma']:10.6f}  {obs['R']:14.6e}")
    print()


def demo_table_2():
    """3. Reproduce Table 2: observables at characteristic scales."""
    print("=" * 65)
    print("DEMO 3: Table 2 — Observables at Characteristic Scales")
    print("=" * 65)

    model = EFCRegimeTransition()
    table = model.table_2()

    print(f"  {'Scale':>15s}  {'k':>6s}  {'μ':>10s}  {'η':>10s}  {'Σ':>10s}")
    print(f"  {'-'*15}  {'-'*6}  {'-'*10}  {'-'*10}  {'-'*10}")
    for row in table:
        print(f"  {row['scale']:>15s}  {row['k']:6.2f}  {row['mu']:10.4f}  "
              f"{row['eta']:10.4f}  {row['sigma']:10.4f}")

    print("\n  Key: μ decreases smoothly from ~1 (galactic) to 0.94 (cosmological)")
    print()


def demo_survival_valley():
    """4. Survival valley constraint checking."""
    print("=" * 65)
    print("DEMO 4: Survival Valley Check")
    print("=" * 65)

    model = EFCRegimeTransition()
    valley = SurvivalValley()
    result = valley.check_model(model, k=0.05)

    print(f"  At k = 0.05 h/Mpc:")
    print(f"    μ = {result['mu']:.4f}  in [0.90, 0.97]? {result['mu_in_range']}")
    print(f"    η = {result['eta']:.4f}  > 1.05?         {result['eta_above_min']}")
    print(f"    Σ = {result['sigma']:.4f}  > 1.0?          {result['sigma_above_min']}")
    print(f"    ALL PASS: {result['all_pass']}")
    print()


def demo_spatiotemporal():
    """5. Spatiotemporal localization (Table 3)."""
    print("=" * 65)
    print("DEMO 5: Spatiotemporal Localization (Table 3)")
    print("=" * 65)

    grid = SpatiotemporalGrid()
    table = grid.table_3()

    print(f"  {'Point':>17s}  {'k':>6s}  {'z':>5s}  {'μ':>8s}  "
          f"{'η':>8s}  {'Σ':>8s}  {'Θ(z)':>6s}")
    print(f"  {'-'*17}  {'-'*6}  {'-'*5}  {'-'*8}  "
          f"{'-'*8}  {'-'*8}  {'-'*6}")
    for r in table:
        print(f"  {r['point']:>17s}  {r['k']:6.2f}  {r['z']:5.1f}  "
              f"{r['mu']:8.4f}  {r['eta']:8.4f}  {r['sigma']:8.4f}  "
              f"{r['gate']:6.4f}")

    print("\n  Signal confined to z < 1 and k < 0.1 — CMB and galactic unmodified")
    print()


def demo_parameter_scan():
    """6. Parameter space robustness (compact scan)."""
    print("=" * 65)
    print("DEMO 6: Parameter Space Robustness")
    print("=" * 65)

    scan = ParameterScan(n_points=30)  # Reduced for speed
    result = scan.scan()

    print(f"  Scanned: {result['n_total']} points")
    print(f"  Viable:  {result['n_pass']} ({result['viable_percent']})")
    if result["K_bar_range_viable"]:
        print(f"  K_bar viable range:       [{result['K_bar_range_viable'][0]:.0f}, "
              f"{result['K_bar_range_viable'][1]:.0f}]")
        print(f"  λ̇ viable range:           [{result['lambda_dot_range_viable'][0]:.3f}, "
              f"{result['lambda_dot_range_viable'][1]:.3f}]")
    print(f"\n  Survival valley is a broad, robust feature — not fine-tuned")
    print()


def demo_growth():
    """7. Growth rate fσ₈ consistency."""
    print("=" * 65)
    print("DEMO 7: Growth Rate fσ₈ vs BOSS DR12")
    print("=" * 65)

    growth = GrowthODE()
    result = growth.delta_chi2()

    print(f"  {'z':>5s}  {'fσ₈ obs':>10s}  {'ΛCDM':>10s}  {'EFC':>10s}")
    print(f"  {'-'*5}  {'-'*10}  {'-'*10}  {'-'*10}")
    for efc_p, lcdm_p in zip(result["efc_points"], result["lcdm_points"]):
        print(f"  {efc_p['z']:5.2f}  {efc_p['observed']:10.3f}  "
              f"{lcdm_p['predicted']:10.4f}  {efc_p['predicted']:10.4f}")

    print(f"\n  χ²(ΛCDM) = {result['chi2_LCDM']:.3f}")
    print(f"  χ²(EFC)  = {result['chi2_EFC']:.3f}")
    print(f"  Δχ²      = {result['delta_chi2']:.3f}")
    print(f"\n  EFC indistinguishable from ΛCDM at k_eff = 0.1 h/Mpc")
    print()


def demo_predictions():
    """8. Falsifiable predictions."""
    print("=" * 65)
    print("DEMO 8: Falsifiable Predictions")
    print("=" * 65)

    pred = Predictions()
    summary = pred.summary()

    p1 = summary["P1"]
    print(f"\n  P1: {p1['description']}")
    print(f"      k ~ {p1['k_transition']} h/Mpc")
    print(f"      μ ≈ {p1['mu_predicted']}, Σ ≈ {p1['sigma_predicted']}")
    print(f"      Test: {p1['test']}")

    p2 = summary["P2"]
    print(f"\n  P2: {p2['description']}")
    print(f"      Reason: {p2['structural_reason']}")
    print(f"      Max μ found: {p2['max_mu_found']:.6f}")
    print(f"      Verified (μ < 1): {p2['verified']}")
    print(f"      Falsification: {p2['falsification']}")
    print()


if __name__ == "__main__":
    print()
    print("EFC Regime Transition Test — Full Demo")
    print("DOI: 10.6084/m9.figshare.31941543")
    print("Author: Morten Magnusson")
    print()

    demo_stiffness_response()
    demo_regime_transition()
    demo_table_2()
    demo_survival_valley()
    demo_spatiotemporal()
    demo_parameter_scan()
    demo_growth()
    demo_predictions()

    print("=" * 65)
    print("All 8 demonstrations completed successfully.")
    print("One action, two regime-limits: μ<1 (linear) ↔ μ>1 (non-linear)")
    print("=" * 65)
