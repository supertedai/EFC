"""Test of the H2O phase engine (step 1, round 2 after independent review).

TDD: the new tests for the review requirements are written BEFORE the engine is
fixed. The references are measured physical values (IAPWS R6-95 / R14-08), not
the model's own computations.

Review requirements covered here:
  K1: the vapour curve's validity range is bounded honestly (the calibration
      window), NaN outside — no extrapolation towards the critical point.
  K2: the melting curve is bounded to ice Ih (P <= 208.566 MPa), NaN outside.
  K3: compute() validates parameters and returns NaN for invalid ones.
  K4: invalid temperatures/pressures/coordinate shapes are rejected
      deterministically.
  K5: critical point and phase boundary semantics: supercritical needs P > P_c;
      points on the boundary are classified as "coexistence".
  K6: multi-point IAPWS references + contract tests.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from efc_inference.engine.water import WaterPhaseEngine  # noqa: E402

# Reference parameters (physics, not model data)
PARAMS = {
    "t_triple": 273.16,               # K
    "p_triple": 611.657,              # Pa
    "t_critical": 647.096,            # K
    "p_critical": 22.064e6,           # Pa (IAPWS critical pressure)
    "latent_vaporization_ref": 2.257e6,  # J/kg ved t_vap_ref
    "t_vap_ref": 373.15,              # K — also the upper calibration bound
    "p_vap_ref": 101325.0,            # Pa — boiling point by definition
    "latent_fusion": 333550.0,        # J/kg
    "latent_sublimation": 2.834e6,    # J/kg (at ~0 C)
    "gas_constant": 461.5,            # J/(kg*K), R_v for H2O
    "density_ice": 916.7,             # kg/m3
    "density_water": 999.8,           # kg/m3
    "p_ice_ih_max": 208.566e6,        # Pa — the ice Ih bound (IAPWS R14-08)
    "t_sublim_min": 50.0,             # K — lower bound for sublimation
}


def _motor() -> WaterPhaseEngine:
    return WaterPhaseEngine()


# --------------------------------------------------------------------------
# Vapour curve (liquid <-> gas)
# --------------------------------------------------------------------------

def test_saturation_pressure_anchors_at_triple_point():
    """The vapour curve is calibrated on the triple point — exact by
    construction."""
    m = _motor()
    p = m.saturation_pressure(PARAMS, np.array([PARAMS["t_triple"]]))[0]
    assert abs(p - PARAMS["p_triple"]) / PARAMS["p_triple"] < 1e-9


def test_saturation_pressure_at_boiling_point():
    """P_sat(373.15 K) must land near 101325 Pa — within 2 %."""
    m = _motor()
    p = m.saturation_pressure(PARAMS, np.array([373.15]))[0]
    assert abs(p - 101325.0) / 101325.0 < 0.02


def test_saturation_pressure_iapws_multipoint():
    """IAPWS R6-95 multi-point: 300 K -> 3.5369 kPa, 323.15 K -> 12.352 kPa."""
    m = _motor()
    for t_k, p_ref in ((300.0, 3536.9), (323.15, 12352.0)):
        p = m.saturation_pressure(PARAMS, np.array([t_k]))[0]
        assert abs(p - p_ref) / p_ref < 0.05, f"{t_k} K: {p} vs {p_ref}"


def test_saturation_pressure_rises_monotonically():
    """The vapour curve must be strictly increasing in T."""
    m = _motor()
    t = np.linspace(273.16, 373.15, 20)
    p = m.saturation_pressure(PARAMS, t)
    assert np.all(np.diff(p) > 0)


def test_saturation_pressure_nan_below_triple():
    """Below the triple point the curve is undefined — sublimation owns it."""
    m = _motor()
    assert np.isnan(m.saturation_pressure(PARAMS, np.array([250.0]))[0])


def test_saturation_pressure_nan_above_calibration():
    """Above the calibration window (t_vap_ref) nothing is extrapolated — NaN.

    Review measurement: n=0.33 is fitted to 0-100 C; at 450 K the deviation is
    -9.7 % and at 625 K -52.5 %. The engine must say "outside regime", not lie.
    """
    m = _motor()
    for t_k in (450.0, 625.0, 647.096):
        assert np.isnan(m.saturation_pressure(PARAMS, np.array([t_k]))[0])


# --------------------------------------------------------------------------
# Melting curve (ice Ih <-> liquid)
# --------------------------------------------------------------------------

def test_melting_temperature_at_one_atmosphere():
    """T_m(101325 Pa) must land near 273.15 K — within 0.1 K."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    assert abs(t - 273.15) < 0.1


def test_melting_temperature_iapws_100mpa():
    """Ice Ih at 100 MPa: ~264.5 K (skating physics). Within 2 K."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([100.0e6]))[0]
    assert abs(t - 264.5) < 2.0


def test_ice_anomaly_melting_slope_is_negative():
    """Ice floats: the melting point FALLS with pressure (dT_m/dP < 0)."""
    m = _motor()
    t_lo = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    t_hi = m.melting_temperature(PARAMS, np.array([10.0e6]))[0]
    assert t_hi < t_lo


def test_melting_temperature_nan_beyond_ice_ih():
    """Above 208.566 MPa other ice phases exist — the engine answers NaN."""
    m = _motor()
    assert np.isnan(m.melting_temperature(PARAMS, np.array([300.0e6]))[0])


def test_melting_temperature_nan_negative_pressure():
    """Negative pressure is rejected deterministically."""
    m = _motor()
    assert np.isnan(m.melting_temperature(PARAMS, np.array([-1.0e5]))[0])


# --------------------------------------------------------------------------
# Sublimation curve (ice Ih <-> gas)
# --------------------------------------------------------------------------

def test_sublimation_pressure_at_minus_20c():
    """P_sub(253.15 K) must land near 103 Pa — within 10 % (was 20)."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([253.15]))[0]
    assert abs(p - 103.0) / 103.0 < 0.10


def test_sublimation_pressure_iapws_minus_40c():
    """Multi-point vs IAPWS R14-08: 233.15 K -> ~12.8 Pa. Within 10 %."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([233.15]))[0]
    assert abs(p - 12.8) / 12.8 < 0.10


def test_sublimation_pressure_nan_below_50k():
    """Below 50 K the sublimation curve is not defined (IAPWS R14-08)."""
    m = _motor()
    for t_k in (40.0, -10.0):
        assert np.isnan(m.sublimation_pressure(PARAMS, np.array([t_k]))[0])


# --------------------------------------------------------------------------
# Triple point consistency
# --------------------------------------------------------------------------

def test_triple_point_consistency_melting():
    """The melting curve at p_triple must give t_triple back."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([PARAMS["p_triple"]]))[0]
    assert abs(t - PARAMS["t_triple"]) < 1e-9


def test_triple_point_consistency_sublimation():
    """The sublimation curve at t_triple must give p_triple back."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([PARAMS["t_triple"]]))[0]
    assert abs(p - PARAMS["p_triple"]) / PARAMS["p_triple"] < 1e-9


# --------------------------------------------------------------------------
# Phase classification
# --------------------------------------------------------------------------

def test_classify_room_temperature_pressure_is_liquid():
    assert _motor().classify(PARAMS, 300.0, 101325.0) == "liquid"


def test_classify_low_pressure_is_gas():
    assert _motor().classify(PARAMS, 300.0, 1000.0) == "gas"


def test_classify_cold_atmosphere_is_solid():
    assert _motor().classify(PARAMS, 250.0, 101325.0) == "solid"


def test_classify_hot_atmosphere_is_gas():
    assert _motor().classify(PARAMS, 500.0, 101325.0) == "gas"


def test_classify_above_calibration_high_pressure_is_unknown():
    """Above the calibration window with P > P_sat(t_vap_ref) the engine cannot
    decide honestly (the true P_sat(500 K) ~ 2.6 MPa is outside its model) —
    it answers "unknown", not a guessed phase."""
    assert _motor().classify(PARAMS, 500.0, 5.0e6) == "unknown"


def test_classify_supercritical_requires_pressure_above_critical():
    """K5: above T_c with P > P_c -> supercritical; with P <= P_c -> gas."""
    m = _motor()
    assert m.classify(PARAMS, 700.0, 30.0e6) == "supercritical"
    assert m.classify(PARAMS, 700.0, 101325.0) == "gas"


def test_classify_at_critical_temperature_is_not_supercritical():
    """K5 round 2: supercritical needs STRICTLY T > T_c. At T == T_c:
    P < P_c -> gas, P == P_c -> coexistence (critical point),
    P > P_c -> unknown (outside the engine's judgement)."""
    m = _motor()
    tc = PARAMS["t_critical"]
    pc = PARAMS["p_critical"]
    assert m.classify(PARAMS, tc, 2.0 * pc) != "supercritical"
    assert m.classify(PARAMS, tc, 2.0 * pc) == "unknown"
    assert m.classify(PARAMS, tc, pc) == "coexistence"
    assert m.classify(PARAMS, tc, 1.0e6) == "gas"


def test_classify_boiling_point_is_coexistence():
    """K5 round 2: (t_vap_ref, p_vap_ref) IS the boiling point — a phase
    boundary, not "gas". The reference point is used because the model's
    P_sat(373.15) sits 1.7 % below the physical definition."""
    assert _motor().classify(PARAMS, 373.15, 101325.0) == "coexistence"


def test_classify_boiling_point_tolerance_is_symmetric():
    """Round 3: the tolerance around t_vap_ref must be symmetric — both just
    below and just above the boiling temperature are the boundary."""
    m = _motor()
    for t_k in (373.15 - 0.5e-6, 373.15 + 0.5e-6):
        assert m.classify(PARAMS, t_k, 101325.0) == "coexistence", t_k


def test_classify_on_vapor_boundary_is_coexistence():
    """K5: a point on the boundary is coexistence, not an arbitrary side."""
    m = _motor()
    p_sat = float(m.saturation_pressure(PARAMS, np.array([300.0]))[0])
    assert m.classify(PARAMS, 300.0, p_sat) == "coexistence"


def test_classify_on_melting_boundary_is_coexistence():
    m = _motor()
    t_m = float(m.melting_temperature(PARAMS, np.array([101325.0]))[0])
    assert m.classify(PARAMS, t_m, 101325.0) == "coexistence"


def test_classify_triple_point_is_coexistence():
    assert _motor().classify(PARAMS, 273.16, 611.657) == "coexistence"


def test_classify_near_triple_point_reports_all_boundaries():
    """Near the triple point the classification must not crash and be clear."""
    m = _motor()
    for t in (273.15, 273.16, 273.17):
        for p in (500.0, 611.657, 700.0):
            assert m.classify(PARAMS, t, p) in {
                "solid", "liquid", "gas", "supercritical", "coexistence"}


# --------------------------------------------------------------------------
# The contract: compute() + validate_params + deterministic rejection
# --------------------------------------------------------------------------

def test_compute_returns_saturation_curve():
    m = _motor()
    p = m.compute(PARAMS, np.array([300.0, 373.15]))
    assert p.shape == (2,)
    assert abs(p[1] - 101325.0) / 101325.0 < 0.02


def test_compute_empty_params_returns_nan():
    """K3: missing parameters must give NaN, not KeyError."""
    m = _motor()
    p = m.compute({}, np.array([300.0]))
    assert p.shape == (1,)
    assert np.all(np.isnan(p))


def test_compute_incomplete_params_returns_nan():
    m = _motor()
    mangler = {k: v for k, v in PARAMS.items() if k != "p_triple"}
    p = m.compute(mangler, np.array([300.0]))
    assert np.all(np.isnan(p))


def test_compute_invalid_param_types_return_nan():
    """K3 round 2: invalid parameter types (None, string, array) must give
    NaN, not TypeError/ValueError."""
    m = _motor()
    for darlig in (None, "273.16", np.array([273.16, 273.17])):
        p = m.compute({**PARAMS, "t_triple": darlig}, np.array([300.0]))
        assert np.all(np.isnan(p)), f"t_triple={darlig!r} did not crash"


def test_compute_2d_coordinates_returns_nan():
    """K4: 2D coordinates are rejected deterministically with NaN."""
    m = _motor()
    p = m.compute(PARAMS, np.zeros((2, 2)))
    assert p.shape == (2, 2)
    assert np.all(np.isnan(p))


def test_curve_methods_accept_scalar_input():
    """K4: scalar input must work (atleast_1d), not crash."""
    m = _motor()
    assert m.saturation_pressure(PARAMS, 300.0).shape == (1,)
    assert m.melting_temperature(PARAMS, 101325.0).shape == (1,)
    assert m.sublimation_pressure(PARAMS, 253.15).shape == (1,)


# --------------------------------------------------------------------------
# The empathy gate
# --------------------------------------------------------------------------

def test_manifest_declares_name_and_couplings():
    """The manifest is the engine global coupling surface: name, axes, refs."""
    manifest = _motor().manifest(PARAMS)
    assert manifest["name"]
    assert len(manifest["couplings"]) > 0
    for c in manifest["couplings"]:
        assert c["axis"] and c["relation"]
    for v in manifest["calibration"].values():
        assert isinstance(v, float)


def test_manifest_links_to_efc_atlas_concepts():
    """The couplings must point at EFC atlas concepts, not loose words."""
    manifest = _motor().manifest(PARAMS)
    akser = {c["axis"] for c in manifest["couplings"]}
    assert {"node", "regime", "fase", "emergens", "proxy"} <= akser
