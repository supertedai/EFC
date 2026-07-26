"""Tests for EFCParameterVector and priors."""

import numpy as np
import pytest

from efc_inference.core.parameters import EFCParameterVector
from efc_inference.core.priors import (
    UniformPrior, GaussianPrior, LogUniformPrior, TruncatedGaussianPrior
)


class TestPriors:
    def test_uniform_in_bounds(self):
        p = UniformPrior(0.0, 10.0)
        assert np.isfinite(p.log_prob(5.0))
        assert p.log_prob(5.0) == pytest.approx(-np.log(10.0))

    def test_uniform_out_of_bounds(self):
        p = UniformPrior(0.0, 10.0)
        assert p.log_prob(-1.0) == -np.inf
        assert p.log_prob(11.0) == -np.inf

    def test_gaussian(self):
        p = GaussianPrior(0.0, 1.0)
        # Max at mean
        assert p.log_prob(0.0) > p.log_prob(1.0)
        assert p.log_prob(0.0) > p.log_prob(-1.0)

    def test_log_uniform(self):
        p = LogUniformPrior(1e-5, 1e-1)
        # In bounds
        assert np.isfinite(p.log_prob(1e-3))
        # Out of bounds
        assert p.log_prob(1e-6) == -np.inf

    def test_truncated_gaussian(self):
        p = TruncatedGaussianPrior(5.0, 2.0, 0.0, 10.0)
        assert np.isfinite(p.log_prob(5.0))
        assert p.log_prob(-1.0) == -np.inf
        assert p.log_prob(11.0) == -np.inf

    def test_prior_sampling(self):
        rng = np.random.default_rng(42)
        p = UniformPrior(0.0, 1.0)
        samples = [p.sample(rng) for _ in range(1000)]
        assert all(0.0 <= s <= 1.0 for s in samples)


class TestParameterVector:
    def test_add_and_access(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0))
        pv.add("y", 2.0, bounds=(0.0, 10.0))
        assert pv["x"] == 1.0
        assert pv["y"] == 2.0
        assert pv.ndim == 2

    def test_to_from_array(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0))
        pv.add("y", 2.0, bounds=(0.0, 10.0))

        arr = pv.to_array()
        assert np.allclose(arr, [1.0, 2.0])

        pv2 = pv.from_array(np.array([3.0, 4.0]))
        assert pv2["x"] == 3.0
        assert pv2["y"] == 4.0

    def test_fixed_params(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0), fixed=True)
        pv.add("y", 2.0, bounds=(0.0, 10.0))
        assert pv.ndim == 1  # Only y is free
        assert pv.free_names == ["y"]

        arr = pv.to_array()
        assert len(arr) == 1
        assert arr[0] == 2.0

        pv2 = pv.from_array(np.array([5.0]))
        assert pv2["x"] == 1.0  # Fixed, unchanged
        assert pv2["y"] == 5.0

    def test_log_prior(self):
        pv = EFCParameterVector()
        pv.add("x", 5.0, bounds=(0.0, 10.0), prior=UniformPrior(0.0, 10.0))
        lp = pv.log_prior()
        assert np.isfinite(lp)

        # Out of bounds
        pv["x"] = -1.0
        assert pv.log_prior() == -np.inf

    def test_in_bounds(self):
        pv = EFCParameterVector()
        pv.add("x", 5.0, bounds=(0.0, 10.0))
        assert pv.in_bounds()

        pv["x"] = 11.0
        assert not pv.in_bounds()

    def test_sample_prior(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0))
        pv.add("y", 1.0, bounds=(0.0, 10.0))

        rng = np.random.default_rng(42)
        sample = pv.sample_prior(rng)
        assert len(sample) == 2
        assert 0.0 <= sample[0] <= 10.0
        assert 0.0 <= sample[1] <= 10.0

    def test_duplicate_name_raises(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0))
        with pytest.raises(ValueError, match="already exists"):
            pv.add("x", 2.0, bounds=(0.0, 10.0))

    def test_to_dict(self):
        pv = EFCParameterVector()
        pv.add("x", 1.0, bounds=(0.0, 10.0))
        pv.add("y", 2.0, bounds=(0.0, 10.0), fixed=True)
        d = pv.to_dict()
        assert d == {"x": 1.0, "y": 2.0}
