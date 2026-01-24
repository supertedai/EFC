"""
Tests for EFC Toolkit
=====================

Author: Morten Magnusson
ORCID: 0009-0002-4860-5095
"""

import pytest
import numpy as np

from efc import (
    L0, L1, L2, L3, 
    get_regime,
    TransitionFunction,
    TransitionEstimator,
    ValidityChecker,
    EFC_CONSTANTS,
    DOIS,
)
from efc.regimes import get_entropy_regime, LOW_S, MID_S, HIGH_S
from efc.transition import check_cmb_consistency, mu_at_redshift


class TestRegimes:
    """Tests for regime architecture."""
    
    def test_regime_hierarchy(self):
        """Test that regimes have correct hierarchy."""
        assert L0.scale_min_mpc > L1.scale_max_mpc or L0.scale_min_mpc == L1.scale_max_mpc
        assert L1.scale_min_mpc > L2.scale_max_mpc or L1.scale_min_mpc == L2.scale_max_mpc
        assert L2.scale_min_mpc > L3.scale_max_mpc or L2.scale_min_mpc == L3.scale_max_mpc
    
    def test_get_regime_cosmological(self):
        """Test regime detection at cosmological scales."""
        regime = get_regime(500.0)  # 500 Mpc
        assert regime.level.name == "L0"
        assert regime.name == "Cosmological"
    
    def test_get_regime_lss(self):
        """Test regime detection at large-scale structure."""
        regime = get_regime(15.0)  # 15 Mpc
        assert regime.level.name == "L1"
        assert regime.name == "Large-Scale Structure"
    
    def test_get_regime_galaxy(self):
        """Test regime detection at galaxy scale."""
        regime = get_regime(0.015)  # 15 kpc
        assert regime.level.name == "L2"
        assert regime.name == "Galaxy"
    
    def test_get_regime_subgalactic(self):
        """Test regime detection at sub-galactic scale."""
        regime = get_regime(0.0001)  # 100 pc
        assert regime.level.name == "L3"
        assert regime.name == "Sub-galactic"
    
    def test_mu_values(self):
        """Test that μ values are physically sensible."""
        assert L0.mu_typical == 1.0  # CMB consistent
        assert L1.mu_typical > 1.0   # Transition
        assert L2.mu_typical > L1.mu_typical  # Enhancement
        assert L3.mu_typical == 1.0  # Newtonian limit
    
    def test_gr_consistency(self):
        """Test GR consistency check."""
        assert L0.is_gr_consistent()
        assert L3.is_gr_consistent()
        assert not L2.is_gr_consistent()


class TestEntropyRegimes:
    """Tests for entropy sub-regimes."""
    
    def test_low_s(self):
        """Test low-S regime."""
        regime = get_entropy_regime(0.05)
        assert regime.name == "Low-S"
        assert regime.model_status == "GR_LIMIT"
    
    def test_mid_s(self):
        """Test mid-S regime (EFC core domain)."""
        regime = get_entropy_regime(0.5)
        assert regime.name == "Mid-S"
        assert regime.model_status == "CORE_DOMAIN"
    
    def test_high_s(self):
        """Test high-S regime."""
        regime = get_entropy_regime(0.95)
        assert regime.name == "High-S"
        assert regime.model_status == "BOUNDARY"
    
    def test_boundary_values(self):
        """Test entropy at boundaries."""
        assert get_entropy_regime(0.1).name == "Mid-S"  # Just above low
        assert get_entropy_regime(0.9).name == "High-S"  # Just at high


class TestTransitionFunction:
    """Tests for μ(a) transition function."""
    
    def test_early_time_limit(self):
        """Test μ → 1 at early times (CMB consistency)."""
        mu = TransitionFunction(delta_mu=0.1)
        assert abs(mu(0.001) - 1.0) < 0.001
    
    def test_late_time_value(self):
        """Test μ → 1 + Δμ at late times."""
        mu = TransitionFunction(delta_mu=0.1)
        assert abs(mu(1.0) - 1.1) < 0.01
    
    def test_monotonic(self):
        """Test that μ(a) is monotonically increasing."""
        mu = TransitionFunction(delta_mu=0.1)
        a_values = np.logspace(-3, 0, 100)
        mu_values = mu(a_values)
        assert np.all(np.diff(mu_values) >= 0)
    
    def test_cmb_consistency(self):
        """Test CMB consistency check."""
        mu = TransitionFunction(delta_mu=0.1)
        is_consistent, mu_cmb = check_cmb_consistency(mu)
        assert is_consistent
        assert abs(mu_cmb - 1.0) < 0.001
    
    def test_custom_parameters(self):
        """Test with custom transition parameters."""
        mu = TransitionFunction(
            delta_mu=0.2,
            a_transition=0.05,
            sigma=0.3
        )
        assert mu(1.0) > 1.15


class TestTransitionEstimator:
    """Tests for Δ_F estimator."""
    
    def test_fugaku_consistency(self):
        """Test that default parameters give Δ_F ≈ 0.1."""
        mu = TransitionFunction(delta_mu=0.1)
        estimator = TransitionEstimator(mu)
        delta_F = estimator.compute()
        # Should be close to 0.1 (within some tolerance)
        assert 0.05 < delta_F < 0.2
    
    def test_zero_transition(self):
        """Test Δ_F = 0 when μ = 1 everywhere."""
        mu = TransitionFunction(delta_mu=0.0)
        estimator = TransitionEstimator(mu)
        delta_F = estimator.compute()
        assert abs(delta_F) < 0.001
    
    def test_fugaku_check(self):
        """Test Fugaku consistency check method."""
        mu = TransitionFunction(delta_mu=0.1)
        estimator = TransitionEstimator(mu)
        is_consistent, value = estimator.fugaku_consistency(tolerance=0.05)
        assert isinstance(is_consistent, bool)
        assert isinstance(value, float)


class TestValidityChecker:
    """Tests for validity checking."""
    
    def test_cosmological_scale(self):
        """Test validity at cosmological scale."""
        checker = ValidityChecker()
        result = checker.check_scale(500.0)
        assert result.status.value == "gr_limit"
        assert result.is_valid()
    
    def test_galaxy_scale(self):
        """Test validity at galaxy scale."""
        checker = ValidityChecker()
        result = checker.check_scale(0.015)
        assert result.status.value == "valid"
        assert result.is_valid()
    
    def test_mid_entropy(self):
        """Test validity at mid-S entropy."""
        checker = ValidityChecker()
        result = checker.check_entropy(0.5)
        assert result.status.value == "valid"
        assert result.is_valid()
    
    def test_high_entropy_boundary(self):
        """Test that high-S is flagged as boundary."""
        checker = ValidityChecker()
        result = checker.check_entropy(0.95)
        assert result.status.value == "boundary"
        assert result.requires_caution()
    
    def test_check_claim(self):
        """Test simple claim checking."""
        checker = ValidityChecker()
        is_valid, reason = checker.check_claim(L2, "rotation_curve", entropy_normalized=0.5)
        assert is_valid
        
        is_valid, reason = checker.check_claim(L2, "rotation_curve", entropy_normalized=0.95)
        assert not is_valid


class TestConstants:
    """Tests for constants and DOIs."""
    
    def test_author_info(self):
        """Test author information is correct."""
        from efc.constants import AUTHOR
        assert AUTHOR.name == "Morten Magnusson"
        assert AUTHOR.address == "Hasselvegen 5, 4051 Sola, Norway"
        assert AUTHOR.orcid == "0009-0002-4860-5095"
    
    def test_dois_exist(self):
        """Test that DOIs are defined."""
        assert DOIS.foundations is not None
        assert DOIS.sparc_175 is not None
        assert len(DOIS.all()) > 10
    
    def test_physical_constants(self):
        """Test physical constants are reasonable."""
        assert EFC_CONSTANTS.G_N > 0
        assert EFC_CONSTANTS.c > 0
        assert 60 < EFC_CONSTANTS.H0_planck < 80
        assert 0.2 < EFC_CONSTANTS.omega_m_planck < 0.4


class TestIntegration:
    """Integration tests combining multiple components."""
    
    def test_full_workflow(self):
        """Test complete workflow: check validity → compute μ → estimate Δ_F."""
        # 1. Check validity at galaxy scale
        checker = ValidityChecker()
        result = checker.check_scale(0.015)
        assert result.is_valid()
        
        # 2. Create transition function
        mu = TransitionFunction(delta_mu=0.1)
        
        # 3. Check CMB consistency
        is_cmb_ok, _ = check_cmb_consistency(mu)
        assert is_cmb_ok
        
        # 4. Compute estimator
        estimator = TransitionEstimator(mu)
        delta_F = estimator.compute()
        
        # 5. Should be in reasonable range
        assert 0.05 < delta_F < 0.2
    
    def test_regime_transition(self):
        """Test that μ values match regime expectations."""
        mu = TransitionFunction(delta_mu=0.1)
        
        # Early universe (L0 scale factor)
        assert abs(mu(0.001) - L0.mu_typical) < 0.01
        
        # Late universe (should be enhanced)
        assert mu(1.0) > 1.05


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
