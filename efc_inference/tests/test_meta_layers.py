"""Tests for meta-control layers (L0-L3, EBE, RBC)."""

import numpy as np
import pytest

from efc_inference.meta.epistemic_levels import (
    EpistemicWeighting, EpistemicLevel, LEVEL_MULTIPLIERS, LEVEL_PENALTIES
)
from efc_inference.meta.ebe_boundary import EBEBoundary
from efc_inference.meta.rbc_regime import RBCRegime


class TestEpistemicLevels:
    def test_default_level(self):
        ew = EpistemicWeighting(default_level=EpistemicLevel.L1)
        assert ew.get_level("unknown_param") == EpistemicLevel.L1

    def test_set_and_get(self):
        ew = EpistemicWeighting()
        ew.set_level("entropy_scale", EpistemicLevel.L0)
        ew.set_level("length_scale", EpistemicLevel.L3)

        assert ew.get_level("entropy_scale") == EpistemicLevel.L0
        assert ew.get_level("length_scale") == EpistemicLevel.L3

    def test_multipliers(self):
        assert LEVEL_MULTIPLIERS[EpistemicLevel.L0] == 10.0
        assert LEVEL_MULTIPLIERS[EpistemicLevel.L3] == 1.0
        # L0 should have widest priors
        assert LEVEL_MULTIPLIERS[EpistemicLevel.L0] > LEVEL_MULTIPLIERS[EpistemicLevel.L3]

    def test_log_penalty(self):
        ew = EpistemicWeighting()
        ew.set_level("x", EpistemicLevel.L0)
        ew.set_level("y", EpistemicLevel.L3)

        penalty = ew.log_penalty({"x": 1.0, "y": 2.0})
        # L0 has penalty -2.0, L3 has 0.0
        expected = LEVEL_PENALTIES[EpistemicLevel.L0] + LEVEL_PENALTIES[EpistemicLevel.L3]
        assert penalty == pytest.approx(expected)

    def test_scale_prior_bounds(self):
        ew = EpistemicWeighting()
        ew.set_level("x", EpistemicLevel.L0)  # 10x

        original = (0.0, 10.0)
        scaled = ew.scale_prior_bounds("x", original)
        # Center = 5.0, half_width = 5.0, scaled = 50.0
        assert scaled[0] == pytest.approx(-45.0)
        assert scaled[1] == pytest.approx(55.0)

    def test_l3_no_scaling(self):
        ew = EpistemicWeighting()
        ew.set_level("x", EpistemicLevel.L3)  # 1x

        original = (0.0, 10.0)
        scaled = ew.scale_prior_bounds("x", original)
        assert scaled[0] == pytest.approx(original[0])
        assert scaled[1] == pytest.approx(original[1])

    def test_summary(self):
        ew = EpistemicWeighting()
        ew.set_level("x", EpistemicLevel.L2)
        s = ew.summary()
        assert "x" in s
        assert s["x"]["level"] == "L2"
        assert s["x"]["multiplier"] == 1.5


class TestEBEBoundary:
    def test_stub_returns_zero(self):
        ebe = EBEBoundary()
        assert ebe.log_penalty({"x": 1.0}) == 0.0

    def test_disabled(self):
        ebe = EBEBoundary()
        ebe.enabled = False
        assert ebe.log_penalty({"x": 1.0}) == 0.0

    def test_check_constraints_stub(self):
        ebe = EBEBoundary()
        report = ebe.check_constraints({"x": 1.0})
        assert report["all_satisfied"] is True


class TestRBCRegime:
    def test_known_scales(self):
        for scale in ["planetary", "stellar", "galactic", "cluster", "cosmological"]:
            rbc = RBCRegime(scale=scale)
            assert rbc.scale == scale

    def test_unknown_scale_raises(self):
        with pytest.raises(ValueError, match="Unknown scale"):
            RBCRegime(scale="quantum")

    def test_stub_returns_zero(self):
        rbc = RBCRegime(scale="galactic")
        assert rbc.log_penalty({"x": 1.0}) == 0.0

    def test_disabled(self):
        rbc = RBCRegime(scale="galactic")
        rbc.enabled = False
        assert rbc.log_penalty({"x": 1.0}) == 0.0

    def test_compute_alpha_raises(self):
        rbc = RBCRegime(scale="galactic")
        with pytest.raises(NotImplementedError):
            rbc.compute_alpha({"x": 1.0})

    def test_alpha_ranges(self):
        """Galactic alpha range should be wider than planetary."""
        rbc_gal = RBCRegime(scale="galactic")
        rbc_plan = RBCRegime(scale="planetary")

        gal_width = rbc_gal.alpha_range[1] - rbc_gal.alpha_range[0]
        plan_width = rbc_plan.alpha_range[1] - rbc_plan.alpha_range[0]
        assert gal_width > plan_width
