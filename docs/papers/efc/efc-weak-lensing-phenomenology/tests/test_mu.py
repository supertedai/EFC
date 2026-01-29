"""
Unit tests for EFC weak lensing implementation.

Run with: pytest tests/test_mu.py -v
"""

import numpy as np
import pytest
import sys
sys.path.insert(0, '../src')

from efc_weak_lensing import EFCParams, mu_efc, sigma_lens_efc, eta_efc


class TestGRLimits:
    """Test that μ → 1 in appropriate limits (GR recovery)."""
    
    def test_zero_amplitude(self):
        """μ = 1 when A_μ = 0."""
        params = EFCParams(A_mu=0.0, z_t=2.0, k_star=0.1)
        
        k = np.logspace(-3, 1, 50)
        z = np.array([0.3, 0.5, 1.0, 2.5])
        
        for zi in z:
            mu = mu_efc(k, zi, params)
            np.testing.assert_allclose(mu, 1.0, rtol=1e-10)
    
    def test_high_redshift(self):
        """μ = 1 when z > z_t (regime gating)."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        k = np.logspace(-3, 1, 50)
        z_high = np.array([2.1, 3.0, 5.0, 10.0])
        
        for zi in z_high:
            mu = mu_efc(k, zi, params)
            np.testing.assert_allclose(mu, 1.0, rtol=1e-10)
    
    def test_high_k(self):
        """μ → 1 when k >> k_* (scale suppression)."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        k_high = np.array([1.0, 5.0, 10.0, 100.0])
        z = 0.5
        
        mu = mu_efc(k_high, z, params)
        
        # At k = 10, scale factor = 1/(1+100) ≈ 0.01
        # So μ ≈ 1 + (-0.2)(0.01) = 0.998
        assert np.all(np.abs(mu - 1.0) < 0.05)


class TestModificationBehavior:
    """Test expected modification behavior."""
    
    def test_negative_amplitude_reduces_mu(self):
        """A_μ < 0 should give μ < 1 at low z, low k."""
        params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
        
        k = 0.01  # k << k_*
        z = 0.5   # z < z_t
        
        mu = mu_efc(k, z, params)
        assert mu < 1.0
        assert mu > 0.5  # Sanity check
    
    def test_positive_amplitude_increases_mu(self):
        """A_μ > 0 should give μ > 1 at low z, low k."""
        params = EFCParams(A_mu=0.1, z_t=2.0, k_star=0.1)
        
        k = 0.01
        z = 0.5
        
        mu = mu_efc(k, z, params)
        assert mu > 1.0
    
    def test_k_dependence(self):
        """μ should decrease toward 1 as k increases."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        k = np.array([0.001, 0.01, 0.1, 1.0])
        z = 0.5
        
        mu = mu_efc(k, z, params)
        
        # Modification should decrease with k
        assert mu[0] < mu[1] < mu[2] < mu[3]
        
        # All should be less than 1 for A_μ < 0
        assert np.all(mu < 1.0)


class TestLensingParameter:
    """Test lensing parameter Σ_lens."""
    
    def test_minimal_model_sigma_equals_mu(self):
        """In minimal model (η=1), Σ_lens = μ."""
        params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
        
        k = np.logspace(-3, 1, 50)
        z = 0.5
        
        mu = mu_efc(k, z, params)
        sigma = sigma_lens_efc(k, z, params)
        
        np.testing.assert_allclose(sigma, mu, rtol=1e-10)
    
    def test_eta_is_unity(self):
        """Gravitational slip η = 1 in minimal model."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        k = np.logspace(-3, 1, 50)
        z = np.array([0.3, 0.5, 1.0])
        
        for zi in z:
            eta = eta_efc(k, zi, params)
            np.testing.assert_allclose(eta, 1.0, rtol=1e-10)


class TestNumericalStability:
    """Test numerical stability."""
    
    def test_extreme_k_values(self):
        """Should not produce NaN or Inf for extreme k."""
        params = EFCParams(A_mu=-0.1, z_t=2.0, k_star=0.1)
        
        k_extreme = np.array([1e-10, 1e-5, 1e5, 1e10])
        z = 0.5
        
        mu = mu_efc(k_extreme, z, params)
        
        assert np.all(np.isfinite(mu))
        assert np.all(mu > 0)
    
    def test_z_at_transition(self):
        """Should handle z exactly at z_t."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        k = 0.1
        z_at_transition = 2.0
        
        mu = mu_efc(k, z_at_transition, params)
        
        assert np.isfinite(mu)


class TestS8Scaling:
    """Test S8 scaling approximation."""
    
    def test_s8_ratio_approximate(self):
        """S8 ratio ≈ sqrt(μ) at effective scale."""
        params = EFCParams(A_mu=-0.2, z_t=2.0, k_star=0.1)
        
        # Effective k for S8 measurement
        k_eff = 0.1
        z = 0.5
        
        mu = mu_efc(k_eff, z, params)
        s8_ratio = np.sqrt(mu)
        
        # DES Y6 S8 / Planck S8 ≈ 0.789 / 0.83 ≈ 0.95
        # For A_μ = -0.2, we expect ratio ~ 0.95
        assert 0.9 < s8_ratio < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
