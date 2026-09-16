"""Test av H2O fasemotoren (trinn 1, runde 2 etter uavhengig review).

TDD: nye tester for review-kravene skrives FOER motoren fikses.
Referansene er maalte fysiske verdier (IAPWS R6-95 / R14-08), ikke
modellens egne utregninger.

Review-krav som dekkes her:
  K1: dampkurvens gyldighetsomraade begrenses ærlig (kalibreringsvinduet),
      NaN utenfor — ikke extrapolering mot kritisk punkt.
  K2: smeltekurven begrenses til ice Ih (P <= 208.566 MPa), NaN utenfor.
  K3: compute() validerer parametre og returnerer NaN ved ugyldige.
  K4: ugyldige temperaturer/trykk/koordinatformer avvises deterministisk.
  K5: kritisk-punkt- og fasegrense-semantikk: superkritisk krever P > P_c;
      punkter paa grensen klassifiseres som «coexistence».
  K6: flerpunkt-IAPWS-referanser + kontraktstester.
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

# Referanseparametre (fysikk, ikke modelldata)
PARAMS = {
    "t_triple": 273.16,               # K
    "p_triple": 611.657,              # Pa
    "t_critical": 647.096,            # K
    "p_critical": 22.064e6,           # Pa (IAPWS kritisk trykk)
    "latent_vaporization_ref": 2.257e6,  # J/kg ved t_vap_ref
    "t_vap_ref": 373.15,              # K — ogsaa ovre kalibreringsgrense
    "p_vap_ref": 101325.0,            # Pa — kokepunkt per definisjon
    "latent_fusion": 333550.0,        # J/kg
    "latent_sublimation": 2.834e6,    # J/kg (ved ~0 C)
    "gas_constant": 461.5,            # J/(kg*K), R_v for H2O
    "density_ice": 916.7,             # kg/m3
    "density_water": 999.8,           # kg/m3
    "p_ice_ih_max": 208.566e6,        # Pa — ice Ih-grensen (IAPWS R14-08)
    "t_sublim_min": 50.0,             # K — nedre grense for sublimasjon
}


def _motor() -> WaterPhaseEngine:
    return WaterPhaseEngine()


# --------------------------------------------------------------------------
# Dampkurve (vaeske <-> gass)
# --------------------------------------------------------------------------

def test_saturation_pressure_anchors_at_triple_point():
    """Dampkurven er kalibrert mot trippelpunktet — eksakt ved konstruksjon."""
    m = _motor()
    p = m.saturation_pressure(PARAMS, np.array([PARAMS["t_triple"]]))[0]
    assert abs(p - PARAMS["p_triple"]) / PARAMS["p_triple"] < 1e-9


def test_saturation_pressure_at_boiling_point():
    """P_sat(373.15 K) skal lande naer 101325 Pa — innenfor 2 %."""
    m = _motor()
    p = m.saturation_pressure(PARAMS, np.array([373.15]))[0]
    assert abs(p - 101325.0) / 101325.0 < 0.02


def test_saturation_pressure_iapws_multipoint():
    """Flerpunkt mot IAPWS R6-95: 300 K -> 3.5369 kPa, 323.15 K -> 12.352 kPa."""
    m = _motor()
    for t_k, p_ref in ((300.0, 3536.9), (323.15, 12352.0)):
        p = m.saturation_pressure(PARAMS, np.array([t_k]))[0]
        assert abs(p - p_ref) / p_ref < 0.05, f"{t_k} K: {p} vs {p_ref}"


def test_saturation_pressure_rises_monotonically():
    """Dampkurven skal vaere strengt stigende i T."""
    m = _motor()
    t = np.linspace(273.16, 373.15, 20)
    p = m.saturation_pressure(PARAMS, t)
    assert np.all(np.diff(p) > 0)


def test_saturation_pressure_nan_below_triple():
    """Under trippelpunktet er dampkurven ikke definert — sublimasjon eier det."""
    m = _motor()
    assert np.isnan(m.saturation_pressure(PARAMS, np.array([250.0]))[0])


def test_saturation_pressure_nan_above_calibration():
    """Over kalibreringsvinduet (t_vap_ref) extrapoleres det ikke — NaN.

    Review-malt: n=0.33 er tilpasset 0-100 C; ved 450 K er avviket -9.7 %
    og ved 625 K -52.5 %. Motoren skal si «utenfor regime», ikke lyve.
    """
    m = _motor()
    for t_k in (450.0, 625.0, 647.096):
        assert np.isnan(m.saturation_pressure(PARAMS, np.array([t_k]))[0])


# --------------------------------------------------------------------------
# Smeltekurve (ice Ih <-> vaeske)
# --------------------------------------------------------------------------

def test_melting_temperature_at_one_atmosphere():
    """T_m(101325 Pa) skal lande naer 273.15 K — innenfor 0.1 K."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    assert abs(t - 273.15) < 0.1


def test_melting_temperature_iapws_100mpa():
    """Ice Ih ved 100 MPa: ~264.5 K (skoytefysikk). Innenfor 2 K."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([100.0e6]))[0]
    assert abs(t - 264.5) < 2.0


def test_ice_anomaly_melting_slope_is_negative():
    """Is flyter: smeltetemperaturen FALLER med trykket (dT_m/dP < 0)."""
    m = _motor()
    t_lo = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    t_hi = m.melting_temperature(PARAMS, np.array([10.0e6]))[0]
    assert t_hi < t_lo


def test_melting_temperature_nan_beyond_ice_ih():
    """Over 208.566 MPa finnes andre isfaser — motoren svarer NaN."""
    m = _motor()
    assert np.isnan(m.melting_temperature(PARAMS, np.array([300.0e6]))[0])


def test_melting_temperature_nan_negative_pressure():
    """Negativt trykk avvises deterministisk."""
    m = _motor()
    assert np.isnan(m.melting_temperature(PARAMS, np.array([-1.0e5]))[0])


# --------------------------------------------------------------------------
# Sublimasjonskurve (ice Ih <-> gass)
# --------------------------------------------------------------------------

def test_sublimation_pressure_at_minus_20c():
    """P_sub(253.15 K) skal lande naer 103 Pa — innenfor 10 % (var 20)."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([253.15]))[0]
    assert abs(p - 103.0) / 103.0 < 0.10


def test_sublimation_pressure_iapws_minus_40c():
    """Flerpunkt mot IAPWS R14-08: 233.15 K -> ~12.8 Pa. Innenfor 10 %."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([233.15]))[0]
    assert abs(p - 12.8) / 12.8 < 0.10


def test_sublimation_pressure_nan_below_50k():
    """Under 50 K er sublimasjonskurven ikke definert (IAPWS R14-08)."""
    m = _motor()
    for t_k in (40.0, -10.0):
        assert np.isnan(m.sublimation_pressure(PARAMS, np.array([t_k]))[0])


# --------------------------------------------------------------------------
# Trippelpunkt-konsistens
# --------------------------------------------------------------------------

def test_triple_point_consistency_melting():
    """Smeltekurven i p_triple skal gi t_triple tilbake."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([PARAMS["p_triple"]]))[0]
    assert abs(t - PARAMS["t_triple"]) < 1e-9


def test_triple_point_consistency_sublimation():
    """Sublimasjonskurven i t_triple skal gi p_triple tilbake."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([PARAMS["t_triple"]]))[0]
    assert abs(p - PARAMS["p_triple"]) / PARAMS["p_triple"] < 1e-9


# --------------------------------------------------------------------------
# Faseklassifisering
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
    """Over kalibreringsvinduet med P > P_sat(t_vap_ref) kan motoren ikke
    avgjoere ærlig (ekte P_sat(500 K) ~ 2.6 MPa er utenfor dens modell) —
    den svarer «unknown», ikke en gjettet fase."""
    assert _motor().classify(PARAMS, 500.0, 5.0e6) == "unknown"


def test_classify_supercritical_requires_pressure_above_critical():
    """K5: over T_c med P > P_c -> supercritical; med P <= P_c -> gas."""
    m = _motor()
    assert m.classify(PARAMS, 700.0, 30.0e6) == "supercritical"
    assert m.classify(PARAMS, 700.0, 101325.0) == "gas"


def test_classify_on_vapor_boundary_is_coexistence():
    """K5: et punkt paa fasegrensen er coexistence, ikke vilkaarlig side."""
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
    """Naer trippelpunktet skal klassifikasjonen ikke krasje og vaere entydig."""
    m = _motor()
    for t in (273.15, 273.16, 273.17):
        for p in (500.0, 611.657, 700.0):
            assert m.classify(PARAMS, t, p) in {
                "solid", "liquid", "gas", "supercritical", "coexistence"}


# --------------------------------------------------------------------------
# Kontrakten: compute() + validate_params + deterministisk avvisning
# --------------------------------------------------------------------------

def test_compute_returns_saturation_curve():
    m = _motor()
    p = m.compute(PARAMS, np.array([300.0, 373.15]))
    assert p.shape == (2,)
    assert abs(p[1] - 101325.0) / 101325.0 < 0.02


def test_compute_empty_params_returns_nan():
    """K3: manglende parametre skal gi NaN, ikke KeyError."""
    m = _motor()
    p = m.compute({}, np.array([300.0]))
    assert p.shape == (1,)
    assert np.all(np.isnan(p))


def test_compute_incomplete_params_returns_nan():
    m = _motor()
    mangler = {k: v for k, v in PARAMS.items() if k != "p_triple"}
    p = m.compute(mangler, np.array([300.0]))
    assert np.all(np.isnan(p))


def test_compute_2d_coordinates_returns_nan():
    """K4: 2D-koordinater avvises deterministisk med NaN."""
    m = _motor()
    p = m.compute(PARAMS, np.zeros((2, 2)))
    assert p.shape == (2, 2)
    assert np.all(np.isnan(p))


def test_curve_methods_accept_scalar_input():
    """K4: skalar-input skal fungere (atleast_1d), ikke krasje."""
    m = _motor()
    assert m.saturation_pressure(PARAMS, 300.0).shape == (1,)
    assert m.melting_temperature(PARAMS, 101325.0).shape == (1,)
    assert m.sublimation_pressure(PARAMS, 253.15).shape == (1,)


# --------------------------------------------------------------------------
# Empati-porten
# --------------------------------------------------------------------------

def test_manifest_declares_name_and_couplings():
    """Manifestet er motorens globale koblingsflate: navn, akser, referanser."""
    manifest = _motor().manifest(PARAMS)
    assert manifest["name"]
    assert len(manifest["couplings"]) > 0
    for c in manifest["couplings"]:
        assert c["axis"] and c["relation"]
    for v in manifest["calibration"].values():
        assert isinstance(v, float)


def test_manifest_links_to_efc_atlas_concepts():
    """Koblingene skal peke paa EFC-atlasbegreper, ikke loese ord."""
    manifest = _motor().manifest(PARAMS)
    akser = {c["axis"] for c in manifest["couplings"]}
    assert {"node", "regime", "fase", "emergens", "proxy"} <= akser
