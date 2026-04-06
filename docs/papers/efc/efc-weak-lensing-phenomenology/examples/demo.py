"""
EFC Weak Lensing Phenomenology -- Demonstration Script
======================================================

Demonstrates the key functionality of the mu(k,z) framework:
1. GR recovery limits (A_mu=0, high-z, high-k)
2. Scale-dependent modification behaviour
3. Lensing parameter Sigma_lens in the minimal model
4. S8 tension scaling estimate
5. Smooth vs sharp redshift transition
6. Grid evaluation matching reference values

Run:
    python examples/demo.py
"""

import sys
import os
import numpy as np

# Add the src/ directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from efc_weak_lensing import EFCParams, mu_efc, sigma_lens_efc, eta_efc


def demo_gr_recovery():
    """Demo 1: GR recovery in three limits."""
    print("Demo 1: GR recovery limits")
    print("-" * 40)

    k = np.logspace(-3, 1, 50)
    z_low = np.array([0.5])
    z_high = np.array([3.0])

    # Limit A: A_mu = 0 gives mu = 1 everywhere
    params_gr = EFCParams(A_mu=0.0)
    mu_gr = mu_efc(k, z_low, params_gr)
    assert np.allclose(mu_gr, 1.0, atol=1e-12), "GR limit (A_mu=0) failed"
    print(f"  A_mu=0    -> mu = {mu_gr.ravel()[0]:.6f}  (expect 1.0)")

    # Limit B: z > z_t gives mu = 1 regardless of A_mu
    params = EFCParams(A_mu=-0.2)
    mu_high = mu_efc(k, z_high, params)
    assert np.allclose(mu_high, 1.0, atol=1e-12), "High-z limit failed"
    print(f"  z=3 > z_t -> mu = {mu_high.ravel()[0]:.6f}  (expect 1.0)")

    # Limit C: k >> k_* gives mu -> 1
    k_large = np.array([10.0])
    mu_hk = mu_efc(k_large, z_low, params)
    assert abs(float(mu_hk) - 1.0) < 0.01, "High-k limit failed"
    print(f"  k=10>>k_* -> mu = {float(mu_hk):.6f}  (expect ~1.0)")

    print("  PASSED\n")


def demo_scale_dependence():
    """Demo 2: Scale-dependent modification at fixed redshift."""
    print("Demo 2: Scale-dependent mu(k) at z=0.5, A_mu=-0.1")
    print("-" * 40)

    params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
    k_values = np.array([0.001, 0.01, 0.1, 1.0])
    z = np.array([0.5])

    mu = mu_efc(k_values, z, params)
    mu = mu.ravel()

    print(f"  k=0.001 : mu = {mu[0]:.4f}  (expect ~0.900)")
    print(f"  k=0.01  : mu = {mu[1]:.4f}  (expect ~0.900)")
    print(f"  k=0.1   : mu = {mu[2]:.4f}  (expect ~0.950)")
    print(f"  k=1.0   : mu = {mu[3]:.4f}  (expect ~0.999)")

    # Modification should weaken as k increases (mu increases toward 1)
    assert mu[0] < mu[1] <= mu[2] < mu[3], "Scale ordering violated"
    # All below 1 for negative A_mu
    assert np.all(mu < 1.0), "mu should be < 1 for A_mu < 0"
    # Check specific value at k=k_*: h(k_*)=0.5 so mu=1+(-0.1)(0.5)=0.95
    assert abs(mu[2] - 0.95) < 0.01, f"mu at k=k_* should be ~0.95, got {mu[2]}"

    print("  PASSED\n")


def demo_sigma_lens():
    """Demo 3: Lensing parameter Sigma_lens = mu when eta=1."""
    print("Demo 3: Sigma_lens in minimal model (eta=1)")
    print("-" * 40)

    params = EFCParams(A_mu=-0.15, z_t=2.0, k_star=0.1, eta=1.0)
    k = np.logspace(-3, 1, 30)
    z = np.array([0.3, 0.7, 1.5])

    mu = mu_efc(k, z, params)
    sigma = sigma_lens_efc(k, z, params)
    eta = eta_efc(k, z, params)

    # In minimal model: Sigma_lens = (mu/2)(1+eta) = mu when eta=1
    assert np.allclose(sigma, mu, rtol=1e-10), "Sigma_lens != mu for eta=1"
    assert np.allclose(eta, 1.0, rtol=1e-10), "eta != 1 in minimal model"

    print(f"  Sigma_lens == mu for all (k,z): True")
    print(f"  eta == 1.0 everywhere:          True")
    print(f"  Sample: mu(k=0.01, z=0.3) = {mu_efc(np.array([0.01]), np.array([0.3]), params).item():.4f}")
    print("  PASSED\n")


def demo_s8_scaling():
    """Demo 4: S8 tension scaling estimate."""
    print("Demo 4: S8 tension scaling")
    print("-" * 40)

    s8_des = 0.789
    s8_planck = 0.83
    target_ratio = s8_des / s8_planck  # ~0.95

    # At DES effective scale k_eff ~ k_* = 0.1 h/Mpc, z_eff ~ 0.5
    # mu = 1 + A_mu * 0.5  (since h(k_*) = 0.5)
    # S8 ratio ~ sqrt(mu)
    params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
    k_eff = np.array([0.1])
    z_eff = np.array([0.5])

    mu = float(mu_efc(k_eff, z_eff, params))
    s8_ratio = np.sqrt(mu)

    print(f"  DES Y6 S8 = {s8_des}, Planck S8 = {s8_planck}")
    print(f"  Target ratio = {target_ratio:.4f}")
    print(f"  A_mu = -0.2 -> mu(0.1, 0.5) = {mu:.4f}")
    print(f"  S8 ratio ~ sqrt(mu) = {s8_ratio:.4f}")

    assert 0.90 < s8_ratio < 1.0, f"S8 ratio out of range: {s8_ratio}"
    assert abs(s8_ratio - target_ratio) < 0.03, f"S8 ratio too far from target"

    print("  PASSED\n")


def demo_smooth_transition():
    """Demo 5: Smooth vs sharp redshift transition."""
    print("Demo 5: Smooth (tanh) vs sharp (Heaviside) transition")
    print("-" * 40)

    k = np.array([0.01])
    z_near_zt = np.array([1.8, 1.9, 2.0, 2.1, 2.2])

    params_sharp = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1, delta_z=0.0)
    params_smooth = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1, delta_z=0.2)

    mu_sharp = mu_efc(k, z_near_zt, params_sharp).ravel()
    mu_smooth = mu_efc(k, z_near_zt, params_smooth).ravel()

    for i, zi in enumerate(z_near_zt):
        print(f"  z={zi:.1f}  sharp={mu_sharp[i]:.4f}  smooth={mu_smooth[i]:.4f}")

    # Sharp transition: discontinuous jump at z_t
    assert mu_sharp[0] < 1.0, "Should be modified below z_t"
    assert mu_sharp[3] == 1.0, "Should be GR above z_t (sharp)"

    # Smooth transition: gradual change around z_t
    assert mu_smooth[2] < 1.0, "Smooth should still be modified at z=z_t"
    assert mu_smooth[4] > mu_smooth[0], "Smooth should approach GR above z_t"

    print("  PASSED\n")


def demo_grid_validation():
    """Demo 6: Validate against expected reference values."""
    print("Demo 6: Grid validation against reference values")
    print("-" * 40)

    params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)

    # Reference values from data/expected_outputs.json at z=0.5
    reference = {
        0.001: 0.900,
        0.01:  0.900,
        0.1:   0.950,
        1.0:   0.999,
    }

    z = np.array([0.5])
    all_ok = True
    for k_val, expected_mu in reference.items():
        mu = float(mu_efc(np.array([k_val]), z, params))
        match = abs(mu - expected_mu) < 0.002
        status = "ok" if match else "MISMATCH"
        print(f"  mu(k={k_val}, z=0.5) = {mu:.4f}  ref={expected_mu:.3f}  [{status}]")
        if not match:
            all_ok = False

    assert all_ok, "Grid validation failed for one or more reference values"

    # Also verify z > z_t gives mu=1
    k_grid = np.array([0.001, 0.01, 0.1, 1.0])
    z_above = np.array([2.5])
    mu_above = mu_efc(k_grid, z_above, params)
    assert np.allclose(mu_above, 1.0, atol=1e-12), "z>z_t should give mu=1"
    print(f"  z=2.5 (above z_t): all mu = 1.0  [ok]")

    print("  PASSED\n")


if __name__ == "__main__":
    print("=" * 50)
    print("EFC Weak Lensing Phenomenology -- Demo")
    print("=" * 50)
    print()

    demo_gr_recovery()
    demo_scale_dependence()
    demo_sigma_lens()
    demo_s8_scaling()
    demo_smooth_transition()
    demo_grid_validation()

    print("=" * 50)
    print("All demos passed.")
    print("=" * 50)
