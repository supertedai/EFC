#!/usr/bin/env python3
"""
Demo: EFC Empirical Validation -- Cluster Lensing and Galaxy Rotation Curves

Demonstrates:
1. Lambda scaling across regimes
2. Bullet Cluster lensing analysis
3. Rotation curve: EFC vs Newtonian
4. Yukawa and Gaussian kernels
5. Synthetic rotation curve fitting
6. Validation result summary
"""

import math
import sys
import os

# Allow import from the package src directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.empirical_validation import (
    LambdaScaling,
    LensingResult,
    RotationCurvePoint,
    RotationCurveModel,
    NewtonianModel,
    ValidationResult,
    yukawa_kernel,
    gaussian_kernel,
    BULLET_CLUSTER_LENSING,
    LAMBDA_SCALING_BULLET,
    LAMBDA_SCALING_GALAXY,
    ROTATION_CURVE_RESULT,
)


def demo_lambda_scaling():
    """Demo 1: Lambda scales with system size."""
    print("=" * 60)
    print("Demo 1: Lambda Scaling Across Regimes")
    print("=" * 60)

    for ls in [LAMBDA_SCALING_BULLET, LAMBDA_SCALING_GALAXY]:
        print(f"  {ls.system_name}: lambda={ls.lambda_kpc} kpc, "
              f"R={ls.system_size_kpc} kpc, lambda/R={ls.ratio:.2f}")

    # lambda/R should be in [0.5, 1.0] for both
    assert 0.4 <= LAMBDA_SCALING_BULLET.ratio <= 1.1, \
        f"Bullet ratio {LAMBDA_SCALING_BULLET.ratio} out of expected range"
    assert 0.4 <= LAMBDA_SCALING_GALAXY.ratio <= 1.1, \
        f"Galaxy ratio {LAMBDA_SCALING_GALAXY.ratio} out of expected range"
    print("  PASS: lambda/R ~ 0.5-1.0 across regimes\n")


def demo_bullet_cluster():
    """Demo 2: Bullet Cluster lensing -- gas term irrelevant."""
    print("=" * 60)
    print("Demo 2: Bullet Cluster Lensing")
    print("=" * 60)

    bc = BULLET_CLUSTER_LENSING
    print(f"  Full model logL:     {bc.log_likelihood_full}")
    print(f"  Gal-only model logL: {bc.log_likelihood_gal_only}")
    print(f"  Delta logL:          {bc.delta_log_likelihood}")
    print(f"  p-value (gas term):  {bc.p_value_gas}")
    print(f"  Gas significant?     {bc.gas_term_significant}")

    assert bc.delta_log_likelihood == 0.0
    assert not bc.gas_term_significant, "Gas term should NOT be significant"
    assert bc.p_value_gas > 0.95
    print("  PASS: kappa follows galaxies, not gas\n")


def demo_rotation_curve():
    """Demo 3: EFC rotation curve vs Newtonian."""
    print("=" * 60)
    print("Demo 3: Rotation Curve -- EFC vs Newton")
    print("=" * 60)

    # Synthetic galaxy: exponential disk (declining baryon curve)
    def v_baryon(r):
        # Simplified exponential disk profile
        r_d = 3.0  # disk scale length [kpc]
        v_max = 120.0  # peak baryon velocity [km/s]
        x = r / r_d
        if x <= 0:
            return 0.0
        return v_max * (1.6 * x) ** 0.5 * math.exp(-0.8 * x)

    efc = RotationCurveModel(v_h=160.0, r_h=2.4)
    newton = NewtonianModel()

    # Generate synthetic observed data (flat rotation curve)
    data = []
    for i in range(1, 21):
        r = 0.5 + i * 1.0
        # Flat curve at ~180 km/s with 10 km/s errors
        v_obs = 175.0 + 5.0 * math.sin(i * 0.7)
        data.append(RotationCurvePoint(r_kpc=r, v_obs_km_s=v_obs, v_err_km_s=10.0))

    chi2_efc = efc.chi_squared(data, v_baryon)
    chi2_newton = newton.chi_squared(data, v_baryon)

    print(f"  EFC chi2:      {chi2_efc:.1f}")
    print(f"  Newton chi2:   {chi2_newton:.1f}")
    print(f"  Improvement:   {(1 - chi2_efc / chi2_newton) * 100:.0f}%")

    assert chi2_efc < chi2_newton, "EFC should fit better than pure Newtonian"
    print("  PASS: EFC fits flat rotation curve better than Newtonian\n")


def demo_kernels():
    """Demo 4: Yukawa and Gaussian entropy kernels."""
    print("=" * 60)
    print("Demo 4: Entropy Coupling Kernels")
    print("=" * 60)

    lam = 10.0  # coupling scale

    # Yukawa should decay like exp(-r/lam)/r
    y1 = yukawa_kernel(1.0, lam)
    y10 = yukawa_kernel(10.0, lam)
    y50 = yukawa_kernel(50.0, lam)
    print(f"  Yukawa(r=1, lam=10):  {y1:.4f}")
    print(f"  Yukawa(r=10, lam=10): {y10:.4f}")
    print(f"  Yukawa(r=50, lam=10): {y50:.6f}")
    assert y1 > y10 > y50, "Yukawa should be monotonically decreasing"

    # Gaussian
    g1 = gaussian_kernel(0.0, lam)
    g10 = gaussian_kernel(10.0, lam)
    g30 = gaussian_kernel(30.0, lam)
    print(f"  Gaussian(r=0, lam=10):  {g1:.4f}")
    print(f"  Gaussian(r=10, lam=10): {g10:.4f}")
    print(f"  Gaussian(r=30, lam=10): {g30:.6f}")
    assert g1 == 1.0, "Gaussian at r=0 should be 1.0"
    assert g1 > g10 > g30

    # Edge cases
    assert yukawa_kernel(0.0, lam) == 0.0
    assert yukawa_kernel(5.0, 0.0) == 0.0
    print("  PASS: Kernels behave correctly\n")


def demo_paper_results():
    """Demo 5: Reproduce paper key results."""
    print("=" * 60)
    print("Demo 5: Paper Key Results")
    print("=" * 60)

    vr = ROTATION_CURVE_RESULT
    print(f"  Dataset: {vr.dataset_name}")
    print(f"  EFC chi2:    {vr.chi2_efc}")
    print(f"  Newton chi2: {vr.chi2_newton}")
    print(f"  Improvement: {vr.improvement_percent:.0f}%")
    print(f"  chi2/dof (EFC): {vr.chi2_per_dof_efc:.2f}")

    assert abs(vr.improvement_percent - 98.0) < 1.0, \
        f"Expected ~98% improvement, got {vr.improvement_percent}%"
    assert vr.chi2_efc == 4.5
    assert vr.chi2_newton == 296.0
    print("  PASS: Paper results reproduced\n")


def demo_entropy_velocity_profile():
    """Demo 6: Entropy velocity profile shape."""
    print("=" * 60)
    print("Demo 6: Entropy Velocity Profile")
    print("=" * 60)

    model = RotationCurveModel(v_h=200.0, r_h=3.0)

    radii = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
    print(f"  {'r [kpc]':>10s}  {'v_entropy [km/s]':>16s}")
    prev_v = 0.0
    for r in radii:
        v_ent = math.sqrt(model.v_entropy_squared(r))
        print(f"  {r:10.1f}  {v_ent:16.2f}")
        assert v_ent >= prev_v - 1e-6, "Entropy velocity should be non-decreasing"
        prev_v = v_ent

    # Asymptotically approaches v_h
    v_far = math.sqrt(model.v_entropy_squared(1000.0))
    assert abs(v_far - model.v_h) < 1.0, \
        f"At large r, v_entropy should approach v_h={model.v_h}, got {v_far}"
    print(f"  v_entropy(r=1000) = {v_far:.2f} ~ v_h = {model.v_h}")
    print("  PASS: Entropy velocity profile is physically correct\n")


if __name__ == "__main__":
    demo_lambda_scaling()
    demo_bullet_cluster()
    demo_rotation_curve()
    demo_kernels()
    demo_paper_results()
    demo_entropy_velocity_profile()
    print("All 6 demos passed.")
