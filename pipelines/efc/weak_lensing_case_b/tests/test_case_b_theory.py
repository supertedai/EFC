#!/usr/bin/env python3
"""
Sanity checks for Case B lensing theory.

Verifies:
1. Bridge reproduces reference (μ, Σ) at calibration point
2. GR limit (K0→0) gives μ=Σ=1 everywhere
3. Growth ratio is ~1 for small K0 (perturbative)
4. Σ(k,z) has correct scale dependence (large k → GR)
5. Config consistency between EFC and ΛCDM YAMLs
"""

import sys
import os
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from efc_lensing_theory import (
    mu_kz, sigma_kz, eta_kz, stiffness_response, compute_growth_ratio,
    verify_bridge, K0_REF, MSQ_REF, K_LENS_REF, GAMMA_PHI_SQ
)


def test_bridge_reference():
    """At (K0=1.66, m²=0.0035, k=0.05, z=0): μ≈0.94, Σ≈1.05."""
    assert verify_bridge()


def test_gr_limit():
    """K0→0 must give ��=Σ≈1 everywhere."""
    k = np.logspace(-3, 0, 20)
    z = np.array([0.0, 0.5, 1.0, 2.0])
    mu = mu_kz(1e-10, k, z)
    sig = sigma_kz(1e-10, MSQ_REF, k, z)
    assert np.allclose(mu, 1.0, atol=1e-4), f"μ not ~1 in GR limit"
    assert np.allclose(sig, 1.0, atol=1e-3), f"Σ not ~1 in GR limit"


def test_high_k_gr_recovery():
    """At k >> k_lens, R(k)→0, so μ→1 (GR on small scales)."""
    k_high = np.array([1.0, 5.0, 10.0])
    z = np.array([0.0])
    mu = mu_kz(K0_REF, k_high, z)
    # R ∝ k⁻⁴, so at k=1 vs k=0.05: R drops by (0.05/1)⁴ = 6.25e-6
    assert np.all(np.abs(mu - 1.0) < 0.01), f"μ not ~1 at high k: {mu}"


def test_growth_ratio_small_K0():
    """For tiny K0, growth ratio should be ~1.

    Note: This test solves the growth ODE and may be slow in
    sandbox environments. Skip with --fast if needed.
    """
    k = np.array([0.05])
    z = np.array([0.0])
    g2 = compute_growth_ratio(k, z, K0=0.01)
    assert np.allclose(g2, 1.0, atol=0.02), \
        f"Growth ratio not ~1 for small K0: {g2}"


def test_growth_ratio_reference():
    """At reference K0=1.66, growth should deviate from GR.

    Note: This test solves the growth ODE. Slow in sandbox.
    """
    k = np.array([0.05])
    z = np.array([0.0])
    g2 = compute_growth_ratio(k, z, K0=K0_REF)
    # μ < 1 at this scale → growth suppressed → ratio < 1
    assert g2[0, 0] < 1.0, f"Growth not suppressed at K0=1.66: {g2[0, 0]}"
    assert g2[0, 0] > 0.9, f"Growth too suppressed: {g2[0, 0]}"


def test_sigma_scale_dependence():
    """Σ must vary with k (not just a constant Alens)."""
    k = np.array([0.01, 0.05, 0.5])
    z = np.array([0.0])
    sig = sigma_kz(K0_REF, MSQ_REF, k, z)
    # At k=0.01 (low k, large R): Σ deviates more from 1
    # At k=0.5 (high k, small R): Σ closer to 1
    assert sig.flatten()[0] != sig.flatten()[-1], \
        "Σ has no scale dependence — this is Case A, not Case B"


def test_config_consistency():
    """EFC and ΛCDM configs share likelihoods and ΛCDM priors."""
    import yaml
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')

    with open(os.path.join(config_dir, 'efc_wl_polychord.yaml')) as f:
        efc = yaml.safe_load(f)
    with open(os.path.join(config_dir, 'lcdm_wl_polychord.yaml')) as f:
        lcdm = yaml.safe_load(f)

    # Likelihoods must match
    assert set(efc['likelihood'].keys()) == set(lcdm['likelihood'].keys())

    # Shared parameter priors must match
    for p in ['logA', 'ns', 'theta_MC_100', 'ombh2', 'omch2', 'tau']:
        efc_prior = efc['params'][p].get('prior')
        lcdm_prior = lcdm['params'][p].get('prior')
        assert efc_prior == lcdm_prior, f"Prior mismatch for {p}"

    # EFC must have K0/m_sq, ΛCDM must not
    assert 'K0' in efc['params']
    assert 'm_sq' in efc['params']
    assert 'K0' not in lcdm['params']
    assert 'm_sq' not in lcdm['params']


if __name__ == "__main__":
    tests = [
        test_bridge_reference,
        test_gr_limit,
        test_high_k_gr_recovery,
        test_growth_ratio_small_K0,
        test_growth_ratio_reference,
        test_sigma_scale_dependence,
        test_config_consistency,
    ]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
            failed += 1
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    sys.exit(failed)
