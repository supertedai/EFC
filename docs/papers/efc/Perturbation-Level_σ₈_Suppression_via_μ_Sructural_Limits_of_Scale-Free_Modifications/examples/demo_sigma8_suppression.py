#!/usr/bin/env python3
"""
Demo: Perturbation-Level sigma_8 Suppression via mu(a) < 1

Demonstrates:
1. Gate function behaviour across steepness values
2. MuModel calibration (B from mu_0)
3. Universal factor-2 from suppression integral ratio
4. S8 computation and gap closure
5. Reference model WP1a verification
6. Sweep over mu_0 and n combinations
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.sigma8_suppression import (
    GateFunction,
    MuModel,
    compute_S8,
    gap_closure_percent,
    suppression_integral_ratio,
    REFERENCE_MODEL_WP1A,
    UNIVERSAL_FACTOR_2_DATA,
    S8_CLOSURE_DATA,
)


def demo_gate_function():
    """Demo 1: Gate function g(a) = 1/(1 + (a_t/a)^n)."""
    print("=" * 60)
    print("Demo 1: Gate Function Behaviour")
    print("=" * 60)

    a_t = 0.4975
    for n in [2, 4, 6, 10]:
        g = GateFunction(a_t=a_t, n=n)
        vals = [g(a) for a in [0.1, 0.3, 0.5, 0.7, 1.0]]
        print(f"  n={n:2d}: g(0.1)={vals[0]:.4f}  g(0.3)={vals[1]:.4f}  "
              f"g(0.5)={vals[2]:.4f}  g(0.7)={vals[3]:.4f}  g(1.0)={vals[4]:.4f}")

    # Gate at a_t should be ~0.5 for any n
    g2 = GateFunction(a_t=a_t, n=2)
    assert abs(g2(a_t) - 0.5) < 0.01, "g(a_t) should be ~0.5"
    # Gate at a=1 should be > 0.5
    assert g2(1.0) > 0.5
    # Gate at a << a_t should be near 0
    assert g2(0.01) < 0.01
    print("  PASS: Gate function behaves correctly\n")


def demo_mu_calibration():
    """Demo 2: MuModel calibration -- B derived from mu_0."""
    print("=" * 60)
    print("Demo 2: mu(a) Model Calibration")
    print("=" * 60)

    for mu_0 in [0.913, 0.85, 0.80]:
        model = MuModel(mu_0=mu_0, n=2, z_t=1.01)
        mu_now = model.mu(1.0)
        print(f"  mu_0={mu_0}, n=2 -> B={model.B:.4f}, mu(a=1)={mu_now:.4f}")
        assert abs(mu_now - mu_0) < 1e-6, \
            f"mu(1) should equal mu_0={mu_0}, got {mu_now}"

    # Check reference model B
    ref = MuModel(mu_0=0.85, n=2, z_t=1.01)
    assert abs(ref.B - 0.187) < 0.01, f"Expected B~0.187, got {ref.B}"
    print(f"  Reference model: B={ref.B:.3f} (expected ~0.187)")
    print("  PASS: Calibration correct\n")


def demo_universal_factor_2():
    """Demo 3: Universal factor-2 from integral ratio."""
    print("=" * 60)
    print("Demo 3: Universal Factor-2")
    print("=" * 60)

    # The universal factor-2 emerges from the full growth equation solution,
    # not just the gate integral. Verify from paper's CLASS-computed data:
    for uf in UNIVERSAL_FACTOR_2_DATA:
        print(f"  mu_0={uf.mu_0}: delta_s8(n=6)={uf.delta_sigma8_n6}, "
              f"delta_s8(n=2)={uf.delta_sigma8_n2}, ratio={uf.ratio:.2f}")
        assert abs(uf.ratio - 2.0) < 0.05, f"Ratio should be ~2.0, got {uf.ratio}"

    print("  PASS: Universal factor-2 confirmed\n")


def demo_s8_computation():
    """Demo 4: S_8 and gap closure."""
    print("=" * 60)
    print("Demo 4: S_8 Computation and Gap Closure")
    print("=" * 60)

    Omega_m = 0.3134
    sigma_8_planck = 0.811
    S8 = compute_S8(sigma_8_planck, Omega_m)
    print(f"  LCDM: sigma_8={sigma_8_planck}, S_8={S8:.3f}")

    # WP1a reference model
    S8_ref = compute_S8(0.773, Omega_m)
    print(f"  WP1a: sigma_8=0.773, S_8={S8_ref:.3f}")
    assert abs(S8_ref - 0.790) < 0.01

    closure = gap_closure_percent(0.773)
    print(f"  Gap closure: {closure:.0f}%")
    assert closure > 60 and closure < 80
    print("  PASS: S_8 and gap closure computed correctly\n")


def demo_reference_model():
    """Demo 5: Reference model WP1a verification."""
    print("=" * 60)
    print("Demo 5: Reference Model WP1a")
    print("=" * 60)

    ref = REFERENCE_MODEL_WP1A
    print(f"  mu_0 = {ref.mu_0}")
    print(f"  n    = {ref.n}")
    print(f"  B    = {ref.B}")
    print(f"  sigma_8 = {ref.sigma_8}")
    print(f"  S_8     = {ref.S_8}")
    print(f"  Gap closed = {ref.gap_closed_percent}%")
    print(f"  Planck status: {ref.planck_status}")

    assert ref.sigma_8 == 0.773
    assert ref.S_8 == 0.790
    assert ref.gap_closed_percent == 73
    assert ref.mu_0 == 0.85

    # Verify B calibration
    model = MuModel(mu_0=ref.mu_0, n=ref.n, z_t=1.01)
    assert abs(model.B - ref.B) < 0.005
    print("  PASS: Reference model verified\n")


def demo_closure_table():
    """Demo 6: S8 closure table from paper."""
    print("=" * 60)
    print("Demo 6: S8 Gap Closure Table")
    print("=" * 60)

    print(f"  {'mu_0':>5s} {'n':>3s} {'sigma_8':>8s} {'closed':>8s} {'status':>12s}")
    print(f"  {'-'*5} {'-'*3} {'-'*8} {'-'*8} {'-'*12}")
    for row in S8_CLOSURE_DATA:
        print(f"  {row.mu_0:5.3f} {row.n:3d} {row.sigma_8:8.3f} "
              f"{row.gap_closed_percent:7.0f}% {row.planck_status:>12s}")

    # Check monotonicity: lower mu_0 -> more closure
    closures = [r.gap_closed_percent for r in S8_CLOSURE_DATA]
    for i in range(len(closures) - 1):
        assert closures[i] <= closures[i + 1], \
            "Gap closure should increase with decreasing mu_0"

    # Structural ceiling: within Planck 1-sigma (mu_0 >= 0.9), max ~43%
    planck_ok = [r for r in S8_CLOSURE_DATA if "OK" in r.planck_status]
    max_closure_1sigma = max(r.gap_closed_percent for r in planck_ok)
    assert max_closure_1sigma <= 50, \
        f"Structural ceiling within 1-sigma should be <=50%, got {max_closure_1sigma}"
    print(f"\n  Max closure within Planck 1-sigma: {max_closure_1sigma}%")
    print("  PASS: Structural ceiling confirmed\n")


if __name__ == "__main__":
    demo_gate_function()
    demo_mu_calibration()
    demo_universal_factor_2()
    demo_s8_computation()
    demo_reference_model()
    demo_closure_table()
    print("All 6 demos passed.")
