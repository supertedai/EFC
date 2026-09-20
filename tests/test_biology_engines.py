"""Tests for the four biological regime engines."""
import numpy as np

from efc_inference.engine.fluxus import FluxusEngine
from efc_inference.engine.homeostase_buffer import HomeostaseBufferEngine
from efc_inference.engine.feber_regime import FeberRegimeEngine
from efc_inference.engine.evolusjon import EvolusjonEngine


def test_fluxus_uses_efc_flow_law_and_nan_outside_domain():
    m = FluxusEngine(); p = {"energy_density": 2.0, "entropy_production": 1.0, "tau_leak": 10.0, "kappa": 1.0}
    assert np.isclose(m.compute(p, np.array([2.0]))[0], 0.2)
    assert np.isnan(m.compute(p, np.array([-1.0]))[0])
    assert m.regime(p, 2.0) == "flytobjekt"
    assert m.regime({**p, "kappa": 3.0}, 2.0) == "flytsubjekt"
    assert "hypotese" in m.regime_node(p)["epistemikk"]["sannhetsstatus"]


def test_homeostasis_measured_reference_bands_and_regimes():
    m = HomeostaseBufferEngine(); p = {}
    assert m.classify_state(37.0, 5.0, 7.40) == "normalt"
    assert m.classify_state(37.8, 5.0, 7.40) == "kompensert"
    assert m.classify_state(39.0, 10.0, 7.10) == "dekompensert"
    assert np.isfinite(m.compute(p, np.array([[37.0, 5.0, 7.40]]))[0])
    assert np.isnan(m.compute(p, np.array([[20.0, 5.0, 7.40]]))[0])


def test_fever_separates_pyrogenic_fever_from_hyperthermia():
    m = FeberRegimeEngine(); p = {"setpoint_c": 37.0}
    assert m.classify(37.5, pyrogenic=False) == "normoterm"
    assert m.classify(39.0, pyrogenic=True) == "febril"
    assert m.classify(39.0, pyrogenic=False) == "hyperterm"
    assert m.classify(42.0, pyrogenic=True) == "hyperterm"
    assert np.isnan(m.compute(p, np.array([20.0]))[0])


def test_evolution_calculates_hardy_weinberg_selection_and_fixation():
    m = EvolusjonEngine()
    hw = m.hardy_weinberg(0.7)
    assert np.allclose(hw, [0.49, 0.42, 0.09])
    assert np.isclose(m.selection_coefficient(1.0, 1.1), 0.1)
    p = {"selection_coefficient": 0.1, "population_size": 1000.0}
    assert 0.5 < m.compute(p, np.array([0.5]))[0] < 0.56
    assert np.isfinite(m.fixation_time(0.1, 1000.0, 0.1))
    assert np.isnan(m.compute(p, np.array([1.2]))[0])
    assert "speciation" in EvolusjonEngine.__doc__
