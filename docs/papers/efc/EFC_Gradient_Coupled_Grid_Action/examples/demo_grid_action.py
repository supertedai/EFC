#!/usr/bin/env python3
"""
Demo: EFC Gradient-Coupled Grid Action
=======================================
Demonstrates the minimal Lagrangian derivation of E ∝ √g.

DOI: 10.6084/m9.figshare.31941465
"""

import sys
import os

# Add parent src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.grid_action import (
    GridAction,
    EffectiveStiffness,
    DispersionRelation,
    GradientCouplingTheorem,
    OperatorElimination,
    RegimeAnalysis,
    BosonicQuantisation,
    FalsifiablePredictions,
)
import numpy as np


def demo_grid_action():
    """1. Three-term Lagrangian S_grid."""
    print("=" * 65)
    print("DEMO 1: Grid Action S_grid (Three-Term Lagrangian)")
    print("=" * 65)

    action = GridAction(m_eff=1.0, kappa_0=1e-12, alpha=1.0)
    info = action.info()
    print(f"  Action:   {info['action']}")
    print(f"  Terms:    {info['terms']}")
    print(f"  Equation: {info['equation']}")

    # Evaluate at different gravitational accelerations
    g_values = [1e-12, 1e-11, 1e-10, 1e-9]
    print(f"\n  {'g [m/s²]':>12s}  {'L_density':>14s}  {'κ_eff':>14s}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*14}")
    for g in g_values:
        L = action.lagrangian(dxi_dt=0.1, grad_xi=0.05, g_local=g)
        keff = action.effective_stiffness(g)
        print(f"  {g:12.2e}  {L:14.6e}  {keff:14.6e}")
    print()


def demo_effective_stiffness():
    """2. Effective stiffness κ_eff = κ₀ + αg."""
    print("=" * 65)
    print("DEMO 2: Effective Stiffness κ_eff(x) = κ₀ + αg(x)")
    print("=" * 65)

    stiffness = EffectiveStiffness(kappa_0=1e-12, alpha=1.0)
    g_cross = stiffness.crossover_acceleration()
    print(f"  Crossover acceleration: g_cross = κ₀/α = {g_cross:.2e} m/s²")

    g_values = np.logspace(-13, -8, 6)
    print(f"\n  {'g [m/s²]':>12s}  {'κ_eff':>14s}  {'grav_frac':>10s}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*10}")
    for g in g_values:
        keff = stiffness.kappa_eff(g)
        frac = stiffness.gravitational_fraction(g)
        print(f"  {g:12.2e}  {keff:14.6e}  {frac:10.6f}")
    print()


def demo_dispersion():
    """3. Dispersion relation ω²(k,g)."""
    print("=" * 65)
    print("DEMO 3: Dispersion Relation ω²(k,g) = κ_eff/m_eff · k²")
    print("=" * 65)

    disp = DispersionRelation(m_eff=1.0, kappa_0=1e-12, alpha=1.0)

    k = 1.0
    g_values = np.logspace(-12, -8, 5)
    print(f"  Wavenumber k = {k}")
    print(f"\n  {'g [m/s²]':>12s}  {'ω²':>14s}  {'ω':>14s}  {'v_ph':>14s}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*14}  {'-'*14}")
    for g in g_values:
        w2 = disp.omega_squared(k, g)
        w = disp.omega(k, g)
        vph = disp.phase_velocity(g)
        print(f"  {g:12.2e}  {w2:14.6e}  {w:14.6e}  {vph:14.6e}")
    print()


def demo_theorem():
    """4. Theorem 1: E ∝ √g verification."""
    print("=" * 65)
    print("DEMO 4: Theorem 1 — E ∝ √g Verification")
    print("=" * 65)

    theorem = GradientCouplingTheorem(alpha=1.0, m_eff=1.0)
    print(f"  {theorem.info()}")

    g_test = np.logspace(-11, -9, 5)
    result = theorem.verify_scaling(g_test)

    print(f"\n  {'g [m/s²]':>12s}  {'E [J]':>14s}  {'E/√g':>14s}")
    print(f"  {'-'*12}  {'-'*14}  {'-'*14}")
    for g, E, r in zip(result["g_values"], result["E_values"], result["ratios"]):
        print(f"  {g:12.2e}  {E:14.6e}  {r:14.6e}")

    print(f"\n  Ratio mean:     {result['ratio_mean']:.6e}")
    print(f"  Ratio std:      {result['ratio_std']:.2e}")
    print(f"  Scaling verified: {result['scaling_verified']}")
    print()


def demo_operator_uniqueness():
    """5. Operator elimination table."""
    print("=" * 65)
    print("DEMO 5: Operator Uniqueness (Table 1)")
    print("=" * 65)

    elim = OperatorElimination()
    summary = elim.summary()
    print(f"  Total candidates: {summary['total_candidates']}")
    print(f"  Eliminated:       {summary['eliminated']}")
    print(f"  Survivors:        {summary['survivors']}")
    print(f"  Conclusion:       {summary['conclusion']}")

    print(f"\n  {'ID':>4s}  {'Operator':>10s}  {'Survives':>8s}  Reason")
    print(f"  {'-'*4}  {'-'*10}  {'-'*8}  {'-'*40}")
    for c in elim.evaluate_all():
        reason = c["failure_reason"] or "PASSES all constraints"
        surv = "YES" if c["survives"] else "no"
        print(f"  {c['id']:>4s}  {c['operator']:>10s}  {surv:>8s}  {reason}")
    print()


def demo_regimes():
    """6. Three physical regimes."""
    print("=" * 65)
    print("DEMO 6: Three Physical Regimes")
    print("=" * 65)

    regimes = RegimeAnalysis(kappa_0=1e-12, alpha=1.0, m_eff=1.0)
    info = regimes.info()
    print(f"  Crossover: g_cross = {info['g_cross']:.2e} m/s²")
    for name in info["regimes"]:
        print(f"  {name:15s}: {info[name]}")

    g_values = [1e-14, 1e-13, 5e-13, 1e-12, 5e-12, 1e-11, 1e-10, 1e-9]
    table = regimes.regime_table(g_values)
    print(f"\n  {'g [m/s²]':>12s}  {'αg/κ₀':>10s}  {'Regime':>15s}  {'ω/k':>14s}")
    print(f"  {'-'*12}  {'-'*10}  {'-'*15}  {'-'*14}")
    for row in table:
        print(f"  {row['g']:12.2e}  {row['alpha_g_over_kappa0']:10.2f}  "
              f"{row['regime']:>15s}  {row['omega_over_k']:14.6e}")
    print()


def demo_quantisation():
    """7. Bosonic quantisation and thermal occupation."""
    print("=" * 65)
    print("DEMO 7: Bosonic Quantisation & Bose-Einstein Statistics")
    print("=" * 65)

    quant = BosonicQuantisation(m_eff=1.0, kappa_0=1e-12, alpha=1.0)

    k = 1.0
    g = 1e-10
    T_values = [1e-5, 1e-3, 1e-1, 1.0, 10.0]

    print(f"  Mode: k={k}, g={g:.1e} m/s²")
    print(f"  Zero-point energy: E₀ = {quant.zero_point_energy(k, g):.6e} J")

    print(f"\n  {'T [K]':>10s}  {'⟨n_k⟩':>14s}  {'⟨E⟩ [J]':>14s}  {'Z_k':>14s}")
    print(f"  {'-'*10}  {'-'*14}  {'-'*14}  {'-'*14}")
    for T in T_values:
        n = quant.thermal_occupation(k, g, T)
        E = quant.mean_energy(k, g, T)
        Z = quant.partition_function_mode(k, g, T)
        print(f"  {T:10.1e}  {n:14.6e}  {E:14.6e}  {Z:14.6e}")
    print()


def demo_predictions():
    """8. Falsifiable predictions P1 and P2."""
    print("=" * 65)
    print("DEMO 8: Falsifiable Predictions")
    print("=" * 65)

    pred = FalsifiablePredictions(kappa_0=1e-12, alpha=1.0)
    summary = pred.summary()

    p1 = summary["P1"]
    print(f"\n  P1: {p1['description']}")
    print(f"      Condition: {p1['condition']}")
    print(f"      Ratio κ₀/(α·a₀) = {p1['ratio']:.6e}")
    print(f"      Satisfied: {p1['satisfied']}")

    p2 = summary["P2"]
    print(f"\n  P2: {p2['description']}")
    print(f"      g_cross = {p2['g_cross']:.2e} m/s²")
    print(f"      g_cross/a₀ = {p2['g_cross_over_a0']:.6e}")
    print(f"      Observable: {p2['observable']}")
    print(f"      Status: {p2['status']}")
    print()


if __name__ == "__main__":
    print()
    print("EFC Gradient-Coupled Grid Action — Full Demo")
    print("DOI: 10.6084/m9.figshare.31941465")
    print("Author: Morten Magnusson")
    print()

    demo_grid_action()
    demo_effective_stiffness()
    demo_dispersion()
    demo_theorem()
    demo_operator_uniqueness()
    demo_regimes()
    demo_quantisation()
    demo_predictions()

    print("=" * 65)
    print("All 8 demonstrations completed successfully.")
    print("Complete chain: S_grid → E-L → WKB → E∝√g → BE → μ(g)")
    print("=" * 65)
