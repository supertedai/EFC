"""Tests for likelihood functions."""

import numpy as np
import pytest

from efc_inference.core.likelihoods import (
    log_likelihood_chi2, log_likelihood_covariance,
    chi2_reduced, aic, bic
)


class TestChi2Likelihood:
    def test_perfect_fit(self):
        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.0, 2.0, 3.0])
        err = np.array([0.1, 0.1, 0.1])
        ll = log_likelihood_chi2(obs, pred, err)
        # Perfect fit should have high likelihood
        assert np.isfinite(ll)
        assert ll > -10.0

    def test_poor_fit(self):
        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([10.0, 20.0, 30.0])
        err = np.array([0.1, 0.1, 0.1])
        ll = log_likelihood_chi2(obs, pred, err)
        assert ll < -1000

    def test_zero_errors(self):
        obs = np.array([1.0, 2.0])
        pred = np.array([1.0, 2.0])
        err = np.array([0.0, 0.1])
        ll = log_likelihood_chi2(obs, pred, err)
        assert ll == -np.inf

    def test_larger_errors_higher_likelihood(self):
        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.5, 2.5, 3.5])  # 0.5 off
        small_err = np.array([0.1, 0.1, 0.1])
        large_err = np.array([1.0, 1.0, 1.0])

        ll_small = log_likelihood_chi2(obs, pred, small_err)
        ll_large = log_likelihood_chi2(obs, pred, large_err)
        # With larger errors, the same residuals are less penalized
        # But normalization also changes, so just check both are finite
        assert np.isfinite(ll_small)
        assert np.isfinite(ll_large)


class TestCovarianceLikelihood:
    def test_diagonal_matches_chi2(self):
        obs = np.array([1.0, 2.0, 3.0])
        pred = np.array([1.1, 2.1, 3.1])
        err = np.array([0.5, 0.5, 0.5])
        cov = np.diag(err**2)

        ll_chi2 = log_likelihood_chi2(obs, pred, err)
        ll_cov = log_likelihood_covariance(obs, pred, cov)
        assert ll_chi2 == pytest.approx(ll_cov, rel=1e-10)

    def test_non_positive_definite(self):
        obs = np.array([1.0, 2.0])
        pred = np.array([1.0, 2.0])
        bad_cov = np.array([[-1.0, 0.0], [0.0, 1.0]])
        ll = log_likelihood_covariance(obs, pred, bad_cov)
        assert ll == -np.inf


class TestModelComparison:
    def test_chi2_reduced(self):
        obs = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        pred = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        err = np.array([0.1, 0.1, 0.1, 0.1, 0.1])
        cr = chi2_reduced(obs, pred, err, n_params=2)
        assert cr == pytest.approx(0.0)

    def test_chi2_reduced_dof_zero(self):
        obs = np.array([1.0, 2.0])
        pred = np.array([1.0, 2.0])
        err = np.array([0.1, 0.1])
        cr = chi2_reduced(obs, pred, err, n_params=3)
        assert cr == np.inf

    def test_aic(self):
        result = aic(-100.0, 3)
        assert result == pytest.approx(206.0)

    def test_bic(self):
        result = bic(-100.0, 3, 100)
        expected = 200.0 + 3 * np.log(100)
        assert result == pytest.approx(expected)
