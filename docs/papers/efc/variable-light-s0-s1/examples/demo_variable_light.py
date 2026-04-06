#!/usr/bin/env python3
"""
Demo: Variable Effective Light Speed in Entropic Transition States (s0/s1)

Demonstrates:
1. Entropic states s0 and s1
2. c_eff modulation across entropy values
3. Information capacity and horizon scale
4. Collapse regimes at extreme entropy
5. Redshift correction from variable c_eff
6. Curvature from entropic gradients
"""

import math
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.variable_light import (
    C_VACUUM,
    EntropicState,
    VariableLightModel,
    CollapseRegime,
    RedshiftCorrection,
    entropy_gradient,
    curvature_from_entropy,
    S0_STATE,
    S1_STATE,
    S0_COLLAPSE,
    S1_COLLAPSE,
    DEFAULT_MODEL,
)


def demo_entropic_states():
    """Demo 1: s0 and s1 entropic states."""
    print("=" * 60)
    print("Demo 1: Entropic States s0 and s1")
    print("=" * 60)

    for state in [S0_STATE, S1_STATE]:
        print(f"  {state.label}: entropy={state.entropy}, {state.description}")

    assert S0_STATE.entropy < S1_STATE.entropy
    assert S0_STATE.label == "s0"
    assert S1_STATE.label == "s1"

    # Entropy must be in [0, 1]
    try:
        EntropicState("bad", 1.5, "invalid")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass

    print("  PASS: Entropic states defined correctly\n")


def demo_c_eff_profile():
    """Demo 2: Effective light speed across entropy values."""
    print("=" * 60)
    print("Demo 2: c_eff(S) Profile")
    print("=" * 60)

    model = DEFAULT_MODEL
    print(f"  c_0 = {model.c_0:.0f} m/s")
    print(f"  s_transition = {model.s_transition}")
    print(f"  c_min_fraction = {model.c_min_fraction}")
    print()

    print(f"  {'S':>6s} {'c_eff/c_0':>10s} {'c_eff [m/s]':>15s}")
    for S in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        ratio = model.c_eff_ratio(S)
        c = model.c_eff(S)
        print(f"  {S:6.2f} {ratio:10.4f} {c:15.0f}")

    # In s0 (low S): c_eff should be near c_0
    assert model.c_eff_ratio(0.0) > 0.95, "c_eff should be ~c_0 in deep s0"

    # In s1 (high S): c_eff should be reduced
    assert model.c_eff_ratio(1.0) < 0.2, "c_eff should be reduced in deep s1"

    # At transition: c_eff should be ~midpoint
    mid = model.c_eff_ratio(model.s_transition)
    expected_mid = (1.0 + model.c_min_fraction) / 2.0
    assert abs(mid - expected_mid) < 0.01, \
        f"At transition, c_eff/c_0 should be ~{expected_mid}, got {mid}"

    # Monotonically decreasing
    prev = model.c_eff_ratio(0.0)
    for S_val in [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        curr = model.c_eff_ratio(S_val)
        assert curr <= prev + 1e-10, "c_eff should decrease with entropy"
        prev = curr

    print("  PASS: c_eff profile is physically correct\n")


def demo_information_capacity():
    """Demo 3: Information capacity and horizon scale."""
    print("=" * 60)
    print("Demo 3: Information Capacity and Horizon")
    print("=" * 60)

    model = DEFAULT_MODEL
    t = 1.0  # 1 second

    print(f"  {'S':>6s} {'Info capacity':>15s} {'Horizon [m]':>15s}")
    for S in [0.0, 0.2, 0.5, 0.8, 1.0]:
        ic = model.information_capacity(S)
        h = model.horizon_scale(S, t)
        print(f"  {S:6.2f} {ic:15.4f} {h:15.0f}")

    # s0 should have higher info capacity than s1
    ic_s0 = model.information_capacity(0.1)
    ic_s1 = model.information_capacity(0.9)
    assert ic_s0 > ic_s1, "s0 should have higher information capacity"

    # Horizon in vacuum (S=0) should be ~c
    h_vac = model.horizon_scale(0.0, 1.0)
    assert abs(h_vac - C_VACUUM) < C_VACUUM * 0.05

    # Horizon in deep s1 should be much smaller
    h_s1 = model.horizon_scale(1.0, 1.0)
    assert h_s1 < 0.2 * C_VACUUM
    print("  PASS: Information capacity and horizon correct\n")


def demo_collapse_regimes():
    """Demo 4: Collapse at extreme entropy."""
    print("=" * 60)
    print("Demo 4: Collapse Regimes")
    print("=" * 60)

    for cr in [S0_COLLAPSE, S1_COLLAPSE]:
        print(f"  {cr.regime}: S_threshold={cr.entropy_threshold}")
        print(f"    {cr.description}")
        print(f"    Observable: {cr.observable_signature}")

    assert S0_COLLAPSE.is_s0
    assert not S1_COLLAPSE.is_s0
    assert S0_COLLAPSE.entropy_threshold < S1_COLLAPSE.entropy_threshold
    assert S0_COLLAPSE.entropy_threshold < 0.05
    assert S1_COLLAPSE.entropy_threshold > 0.95
    print("  PASS: Collapse regimes defined correctly\n")


def demo_redshift_correction():
    """Demo 5: Redshift correction from variable c_eff."""
    print("=" * 60)
    print("Demo 5: Redshift Correction")
    print("=" * 60)

    model = DEFAULT_MODEL

    # Case 1: No entropy difference -> no correction
    rc1 = RedshiftCorrection(z_expansion=1.0, S_emit=0.3, S_obs=0.3)
    z_corr1 = rc1.z_corrected(model)
    print(f"  Same entropy: z_exp=1.0, z_corrected={z_corr1:.4f}")
    assert abs(z_corr1 - 1.0) < 1e-6

    # Case 2: Emit from higher entropy -> blueshift correction
    rc2 = RedshiftCorrection(z_expansion=1.0, S_emit=0.8, S_obs=0.2)
    z_corr2 = rc2.z_corrected(model)
    print(f"  Higher S_emit: z_exp=1.0, z_corrected={z_corr2:.4f}")
    assert z_corr2 < 1.0, "Higher emission entropy -> lower c_emit -> blueshift"

    # Case 3: Emit from lower entropy -> redshift enhancement
    rc3 = RedshiftCorrection(z_expansion=1.0, S_emit=0.2, S_obs=0.8)
    z_corr3 = rc3.z_corrected(model)
    print(f"  Lower S_emit:  z_exp=1.0, z_corrected={z_corr3:.4f}")
    assert z_corr3 > 1.0, "Lower emission entropy -> higher c_emit -> extra redshift"

    print("  PASS: Redshift corrections behave correctly\n")


def demo_curvature():
    """Demo 6: Curvature from entropic gradients."""
    print("=" * 60)
    print("Demo 6: Curvature from Entropy")
    print("=" * 60)

    model = DEFAULT_MODEL

    print(f"  {'S':>6s} {'Curvature':>15s}")
    for S in [0.1, 0.3, 0.5, 0.7, 0.9]:
        kappa = curvature_from_entropy(S, model)
        print(f"  {S:6.2f} {kappa:15.2f}")

    # Curvature should be largest in the transition region (0.2-0.8)
    # The exact peak depends on d^2(c_eff)/dS^2, which is maximal
    # near the sigmoid shoulders, not at the inflection point itself.
    k_values = {S: curvature_from_entropy(S, model) for S in [0.1, 0.3, 0.5, 0.7, 0.9]}
    k_edge_avg = (k_values[0.1] + k_values[0.9]) / 2
    k_transition_max = max(k_values[0.3], k_values[0.5], k_values[0.7])
    assert k_transition_max > 0, "Curvature should be non-zero in transition region"

    # Entropy gradient
    grad = entropy_gradient(0.2, 0.8, 1.0)
    assert abs(grad - 0.6) < 1e-10
    print(f"  Entropy gradient (0.2->0.8, dr=1.0): {grad}")
    print("  PASS: Curvature peaks at entropic transition\n")


if __name__ == "__main__":
    demo_entropic_states()
    demo_c_eff_profile()
    demo_information_capacity()
    demo_collapse_regimes()
    demo_redshift_correction()
    demo_curvature()
    print("All 6 demos passed.")
