"""Tests for EFCSampler and MetaController."""

import numpy as np
import pytest

from efc_inference.core.parameters import EFCParameterVector
from efc_inference.core.priors import UniformPrior, GaussianPrior
from efc_inference.core.sampler import EFCSampler, MetaController


def _has_emcee():
    try:
        import emcee
        return True
    except ImportError:
        return False


class MockModule:
    """Simple module for testing: likelihood = -0.5 * sum((x - target)^2)."""

    def __init__(self, target: np.ndarray):
        self.target = target
        self.name = "mock"

    def log_likelihood(self, params_dict: dict) -> float:
        values = np.array([params_dict.get(f"p{i}", 0.0)
                           for i in range(len(self.target))])
        return -0.5 * np.sum((values - self.target) ** 2)


class TestMetaController:
    def test_empty_controller(self):
        mc = MetaController()
        assert mc.log_penalty({"x": 1.0}) == 0.0
        assert mc.layer_names == []

    def test_add_layer(self):
        mc = MetaController()
        mc.add_layer("test", lambda d: -1.0)
        assert mc.log_penalty({"x": 1.0}) == -1.0
        assert mc.layer_names == ["test"]

    def test_multiple_layers(self):
        mc = MetaController()
        mc.add_layer("a", lambda d: -1.0)
        mc.add_layer("b", lambda d: -2.0)
        assert mc.log_penalty({"x": 1.0}) == -3.0

    def test_inf_penalty(self):
        mc = MetaController()
        mc.add_layer("block", lambda d: -np.inf)
        mc.add_layer("normal", lambda d: -1.0)
        assert mc.log_penalty({"x": 1.0}) == -np.inf


class TestEFCSampler:
    def test_log_probability_basic(self):
        pv = EFCParameterVector()
        pv.add("p0", 5.0, bounds=(0.0, 10.0), prior=UniformPrior(0.0, 10.0))

        module = MockModule(target=np.array([5.0]))
        sampler = EFCSampler(pv, modules=[module])

        # At the target
        lp = sampler.log_probability(np.array([5.0]))
        assert np.isfinite(lp)

        # Out of bounds
        lp_oob = sampler.log_probability(np.array([-1.0]))
        assert lp_oob == -np.inf

    def test_log_probability_with_meta(self):
        pv = EFCParameterVector()
        pv.add("p0", 5.0, bounds=(0.0, 10.0))

        module = MockModule(target=np.array([5.0]))
        meta = MetaController()
        meta.add_layer("penalty", lambda d: -0.5)

        sampler = EFCSampler(pv, modules=[module], meta=meta)

        lp_no_meta = EFCSampler(pv, modules=[module]).log_probability(np.array([5.0]))
        lp_with_meta = sampler.log_probability(np.array([5.0]))

        assert lp_with_meta == pytest.approx(lp_no_meta - 0.5)

    @pytest.mark.skipif(
        not _has_emcee(),
        reason="emcee not installed"
    )
    def test_run_short(self):
        pv = EFCParameterVector()
        pv.add("p0", 5.0, bounds=(0.0, 10.0),
               prior=GaussianPrior(5.0, 1.0))

        module = MockModule(target=np.array([5.0]))
        sampler = EFCSampler(pv, modules=[module], n_walkers=8)
        sampler.run(n_steps=50, burn_in=10, progress=False)

        results = sampler.results()
        assert "best_fit" in results
        assert "posterior_summary" in results
        assert "convergence" in results

        # Best fit should be near 5.0
        assert abs(results["best_fit"]["p0"] - 5.0) < 3.0

    def test_no_free_params_raises(self):
        pv = EFCParameterVector()
        pv.add("p0", 5.0, bounds=(0.0, 10.0), fixed=True)

        module = MockModule(target=np.array([5.0]))
        sampler = EFCSampler(pv, modules=[module])

        with pytest.raises(ValueError, match="No free parameters"):
            sampler.run(n_steps=10, burn_in=5, progress=False)
