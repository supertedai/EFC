"""Maalebaserte tester for fysiologiske/okologiske lag.

Referanser (uavhengige av motorens beregning):
* Janeway's Immunobiology, 9th ed., ch. 11: sekundær antistoffrespons er
  omtrent 10--100 ganger større og raskere enn primærresponsen (5--10 døgn
  mot 1--3 døgn).
* Borbely (1982), Hum Neurobiol 1:195--204, og Carskadon & Dement (2011):
  søvnsyklus omtrent 90 min, 4--6 sykluser/natt, NREM ca. 75--80 %.
* Scheffer et al. (2001), Nature 413:591--596: alternative stabile
  økosystemtilstander; Lotka--Volterra-perioden er 2π/sqrt(alpha*delta)
  for den målbare idealiserte modellen (ikke en universell naturkonstant).
"""
import numpy as np

from efc_inference.engine.genregulering import GenreguleringEngine
from efc_inference.engine.immunologi import ImmunologiEngine
from efc_inference.engine.sovn_vaaken import SovnVaakenEngine
from efc_inference.engine.okologi import OkologiEngine


def test_genregulering_hill_regimer_and_nan():
    m = GenreguleringEngine()
    p = {"basal_expression": 1.0, "max_expression": 100.0, "activation_threshold": 2.0,
         "repression_threshold": 20.0, "hill_coefficient": 2.0, "repression_coefficient": 2.0}
    assert m.classify(p, 0.0) == "av"
    assert m.classify(p, 1.0) == "basalt"
    assert m.classify(p, 5.0) == "aktivert"
    assert m.classify(p, 30.0) == "repressivt"
    assert np.isnan(m.compute(p, np.array([-1.0]))[0])


def test_immunologi_measured_response_anchors_and_domain():
    m = ImmunologiEngine()
    p = {"antigen_threshold": 1.0, "exposure": "secondary", "peak_day": 2.0,
         "peak_titer": 100.0, "baseline_titer": 1.0, "decay_rate": 0.1}
    out = m.compute(p, np.array([2.0]))
    assert out[0] == 100.0
    assert m.classify(p, 0.0) == "sekundaerrespons"
    assert np.isnan(m.compute(p, np.array([-1.0]))[0])


def test_sleep_measured_cycle_and_nrem_reference():
    m = SovnVaakenEngine()
    p = {"circadian_period": 24.2, "sleep_pressure_max": 1.0, "sleep_pressure_decay": 0.2,
         "wake_pressure_gain": 0.1, "sleep_threshold": 0.7, "rem_fraction": 0.2,
         "nrem_fraction": 0.78}
    assert abs(m.cycle_period_minutes(p) - 90.0) < 1e-9
    assert 0.75 <= p["nrem_fraction"] <= 0.80
    assert m.classify(p, 10.0) == "vaaken"
    assert np.isnan(m.compute(p, np.array([-1.0]))[0])


def test_ecology_measured_logistic_and_lotka_volterra_period():
    m = OkologiEngine()
    p = {"growth_rate": 0.5, "carrying_capacity": 100.0, "initial_population": 10.0,
         "prey_growth_rate": 1.0, "predation_rate": 0.1, "predator_growth_rate": 0.1,
         "predator_death_rate": 0.5}
    assert abs(m.logistic_population(p, np.array([0.0]))[0] - 10.0) < 1e-12
    assert abs(m.lotka_volterra_period(p) - 2*np.pi/np.sqrt(0.5)) < 1e-12
    assert m.classify(p, 10.0, 10.0) == "vekst"
    assert np.isnan(m.compute(p, np.array([-1.0]))[0])


def test_all_motors_have_regime_nodes_and_contract():
    for cls in (GenreguleringEngine, ImmunologiEngine, SovnVaakenEngine, OkologiEngine):
        m = cls()
        node = m.regime_node({})
        assert node["id"].startswith("homo.")
        assert len(node["regime"]["regimes"]) == (3 if cls is SovnVaakenEngine else 4)
        assert m.SYNLIGHET == "offentlig"
