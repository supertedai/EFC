from __future__ import annotations

import numpy as np

from efc_inference.engine.aksjonspotensial import ActionPotentialEngine
from efc_inference.engine.hjerte_syklus import CardiacCycleEngine
from efc_inference.engine.cellesyklus import CellCycleEngine
from efc_inference.engine.metabolisme import MetabolismEngine


def test_action_potential_measured_anchors_and_nan_outside_regime():
    # Measured references: -70/-55/+30 mV (OpenStax A&P 2e, 12.5).
    p = {"resting_potential_mv": -70.0, "threshold_mv": -55.0,
         "peak_potential_mv": 30.0, "depolarization_ms": 1.0,
         "repolarization_ms": 2.0, "refractory_ms": 3.0}
    m = ActionPotentialEngine()
    y = m.compute(p, np.array([0.0, 1.0, 3.0, 6.1]))
    assert y[0] == -70.0
    assert y[1] == 30.0
    assert y[2] == -70.0
    assert np.isnan(y[3])
    assert m.regime_node(p)["regime"]["name"]


def test_cardiac_cycle_measured_references_and_nan_outside_cycle():
    # Measured references: SV 70 mL (NCBI StatPearls), EF 55-70%
    # (American Heart Association), resting HR 60-100 bpm (AHA).
    p = {"heart_rate_bpm": 75.0, "stroke_volume_ml": 70.0,
         "ejection_fraction": 0.60, "end_diastolic_volume_ml": 117.0,
         "end_systolic_volume_ml": 47.0, "systole_fraction": 0.40}
    m = CardiacCycleEngine()
    # t=0 and t=cycle are the end of filling (EDV); t=0.32 is end of
    # ejection. The measured invariant is EDV - ESV = SV = 70 mL.
    y = m.compute(p, np.array([0.0, 0.32, 0.80, 0.81]))
    assert p["end_diastolic_volume_ml"] - p["end_systolic_volume_ml"] == 70.0
    assert y[1] == 47.0
    assert y[2] == 117.0
    assert np.isnan(y[3])
    assert 55.0 <= 100.0 * p["ejection_fraction"] <= 70.0


def test_cell_cycle_checkpoints_can_stop_cycle_and_nan_outside():
    # Checkpoint/phase references: G1/S/G2/M and G0 (PMC4990352).
    p = {"g1_hours": 8.0, "s_hours": 7.0, "g2_hours": 4.0,
         "m_hours": 1.0, "g1_checkpoint_passed": True,
         "g2_checkpoint_passed": True, "spindle_checkpoint_passed": True}
    m = CellCycleEngine()
    assert np.array_equal(m.compute(p, np.array([1.0, 9.0, 16.0, 20.0])),
                           np.array([0.0, 1.0, 2.0, 3.0]))
    blocked = {**p, "g1_checkpoint_passed": False}
    assert np.all(m.compute(blocked, np.array([1.0, 9.0])) == 4.0)
    assert np.isnan(m.compute(p, np.array([21.0]))[0])


def test_metabolism_measured_references_and_regime_boundary():
    # Measured references: aerobic yield about 30-32 ATP/glucose and
    # carbohydrate RQ=1.0 (OpenStax Microbiology 8.3; NCBI RQ).
    p = {"aerobic_atp_per_glucose": 31.0, "anaerobic_atp_per_glucose": 2.0,
         "carbohydrate_rq": 1.0, "oxygen_fraction": 0.21,
         "anaerobic_intensity_threshold": 0.85}
    m = MetabolismEngine()
    y = m.compute(p, np.array([0.0, 0.5, 0.9, 1.1]))
    assert y[:2].tolist() == [31.0, 31.0]
    assert y[2] == 2.0
    assert np.isnan(y[3])
    assert m.classify(p, 0.5) == "active"
    assert m.classify(p, 0.9) == "anaerob"
    assert m.regime_node(p)["regime"]["validity"]
