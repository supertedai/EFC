#!/usr/bin/env python3
"""Demonstration: EFC v2.1 Complete Edition.

Tests the consolidated EFC specification: field equations, entropy sigmoid,
gravitational coupling, and modified Friedmann dynamics.
"""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_complete import (
    EntropyField, GravitationalCoupling, ModifiedFriedmann,
    EFCFieldEquation, EFCCompleteEdition,
)


def demo_entropy_field():
    """Demo 1: Entropy field sigmoid."""
    print("=" * 70)
    print("DEMO 1: Entropy Field S(a)")
    print("=" * 70)
    S = EntropyField()
    print(f"  Parameters: S_inf={S.S_inf}, a_t={S.a_t}, sigma={S.sigma}")
    print(f"  S(a=0.01) = {S.S(0.01):.6f}")
    print(f"  S(a=0.55) = {S.S(0.55):.4f}")
    print(f"  S(a=1.0)  = {S.S(1.0):.4f}")
    print(f"  z_t = {S.transition_redshift():.2f}")

    assert abs(S.S(0.55) - 0.5) < 0.01, "S at transition should be ~0.5"
    assert S.S(1.0) > 0.99, "S today should be near 1"
    assert S.S(0.01) < 0.01, "S at early times should be near 0"
    assert abs(S.transition_redshift() - 0.82) < 0.02
    # Check derivative peaks at transition
    dS_at_t = S.dS_dlna(0.55)
    dS_away = S.dS_dlna(0.01)
    assert dS_at_t > dS_away, "dS/dlna should peak near transition"
    print("  [PASSED]\n")


def demo_gravitational_coupling():
    """Demo 2: Effective gravitational coupling mu(a)."""
    print("=" * 70)
    print("DEMO 2: Gravitational Coupling mu(a) = 1 + beta*S(a)")
    print("=" * 70)
    gc = GravitationalCoupling()
    print(f"  beta = {gc.beta}")
    print(f"  mu(a=0.01) = {gc.mu(0.01):.6f}  (early universe, ~1.0)")
    print(f"  mu(a=0.55) = {gc.mu(0.55):.4f}  (transition)")
    print(f"  mu(a=1.0)  = {gc.mu(1.0):.4f}  (today)")

    assert abs(gc.mu_early() - 1.0) < 0.01, "mu early should be ~1"
    assert abs(gc.mu_today() - 1.16) < 0.01, "mu today should be ~1.16"
    assert gc.G_eff(1.0) > gc.G_eff(0.01), "G_eff should increase over time"
    print("  [PASSED]\n")


def demo_modified_friedmann():
    """Demo 3: Modified Friedmann dynamics."""
    print("=" * 70)
    print("DEMO 3: Modified Friedmann Dynamics")
    print("=" * 70)
    mf = ModifiedFriedmann()
    H_efc = mf.H(1.0)
    H_lcdm = mf.H_LCDM(1.0)
    print(f"  H0 (input) = {mf.H0} km/s/Mpc")
    print(f"  H(a=1) EFC  = {H_efc:.2f} km/s/Mpc")
    print(f"  H(a=1) LCDM = {H_lcdm:.2f} km/s/Mpc")

    # EFC should give slightly higher H today due to mu > 1
    assert H_efc > H_lcdm, "EFC H should exceed LCDM H at a=1"
    # At very early times, they should agree
    ratio_early = mf.H(0.001) / mf.H_LCDM(0.001)
    print(f"  H_EFC/H_LCDM at a=0.001: {ratio_early:.6f}")
    assert abs(ratio_early - 1.0) < 0.01, "At early times EFC ~ LCDM"
    print("  [PASSED]\n")


def demo_field_equation():
    """Demo 4: EFC field equation structure."""
    print("=" * 70)
    print("DEMO 4: EFC Field Equation")
    print("=" * 70)
    fe = EFCFieldEquation()
    print(f"  {fe.full_equation()}")
    components = fe.components()
    for name, expr in components.items():
        print(f"  {name}: {expr}")
    assert "G_{mu nu}" in fe.full_equation()
    assert len(components) == 4
    print("  [PASSED]\n")


def demo_complete_edition():
    """Demo 5: Complete edition container and summary."""
    print("=" * 70)
    print("DEMO 5: EFC v2.1 Complete Edition Summary")
    print("=" * 70)
    efc = EFCCompleteEdition()
    print(efc.summary())
    params = efc.parameters()
    assert params["beta"] == 0.16
    assert params["a_t"] == 0.55
    assert params["sigma"] == 0.10
    assert params["H0"] == 67.4
    assert efc.version == "2.1"
    print("\n  [PASSED]\n")


def demo_parameter_sensitivity():
    """Demo 6: Sensitivity to beta parameter."""
    print("=" * 70)
    print("DEMO 6: Parameter Sensitivity (beta)")
    print("=" * 70)
    betas = [0.0, 0.08, 0.16, 0.24, 0.32]
    print(f"  {'beta':>6s}  {'mu(a=1)':>8s}  {'H(a=1)':>10s}")
    print("  " + "-" * 30)
    mu_values = []
    for b in betas:
        gc = GravitationalCoupling(beta=b)
        mf = ModifiedFriedmann(coupling=gc)
        mu_val = gc.mu_today()
        H_val = mf.H(1.0)
        mu_values.append(mu_val)
        print(f"  {b:6.2f}  {mu_val:8.4f}  {H_val:10.2f}")
    # mu should increase with beta
    for i in range(1, len(mu_values)):
        assert mu_values[i] > mu_values[i - 1], "mu should increase with beta"
    # At beta=0, mu=1 (LCDM recovery)
    assert abs(mu_values[0] - 1.0) < 1e-10, "beta=0 should give mu=1"
    print("  [PASSED]\n")


if __name__ == "__main__":
    demo_entropy_field()
    demo_gravitational_coupling()
    demo_modified_friedmann()
    demo_field_equation()
    demo_complete_edition()
    demo_parameter_sensitivity()
    print("All demos passed!")
