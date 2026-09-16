"""Test av H2O fasemotoren (trinn 1): fase-grense-kurver og trippelpunkt.

TDD: denne fila skrives FOER motoren finnes, og skal feile med ImportError.
Referansene er maalte fysiske verdier, ikke modellens egne utregninger:
  - trippelpunkt: 273.16 K, 611.657 Pa (IAPWS-95-definisjon)
  - kokepunkt:    373.15 K, 101325 Pa (per definisjon)
  - smeltepunkt:  273.15 K ved 1 atm (is I)
  - sublimasjon:  ~103 Pa ved -20 C (is I)
  - is-anomali:   dT_m/dP < 0 (is flyter)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

# Repo-rota paa sys.path, saa `efc_inference.engine.water` kan importeres
# uansett hvor pytest startes fra.
_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from efc_inference.engine.water import WaterPhaseEngine  # noqa: E402

# Referanseparametre (fysikk, ikke modelldata)
PARAMS = {
    "t_triple": 273.16,               # K
    "p_triple": 611.657,              # Pa
    "t_critical": 647.096,            # K
    "latent_vaporization_ref": 2.257e6,  # J/kg ved t_vap_ref
    "t_vap_ref": 373.15,              # K
    "latent_fusion": 333550.0,        # J/kg
    "latent_sublimation": 2.834e6,    # J/kg (ved ~0 C)
    "gas_constant": 461.5,            # J/(kg*K), R_v for H2O
    "density_ice": 916.7,             # kg/m3
    "density_water": 999.8,           # kg/m3
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


def test_saturation_pressure_rises_monotonically():
    """Dampkurven skal vaere strengt stigende i T."""
    m = _motor()
    t = np.linspace(273.16, 400.0, 20)
    p = m.saturation_pressure(PARAMS, t)
    assert np.all(np.diff(p) > 0)


def test_saturation_pressure_is_nan_above_critical():
    """Over kritisk temperatur fins ingen vaeske-gass-grense."""
    m = _motor()
    p = m.saturation_pressure(PARAMS, np.array([700.0]))[0]
    assert np.isnan(p)


# --------------------------------------------------------------------------
# Smeltekurve (is I <-> vaeske)
# --------------------------------------------------------------------------

def test_melting_temperature_at_one_atmosphere():
    """T_m(101325 Pa) skal lande naer 273.15 K — innenfor 0.1 K."""
    m = _motor()
    t = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    assert abs(t - 273.15) < 0.1


def test_ice_anomaly_melting_slope_is_negative():
    """Is flyter: smeltetemperaturen FALLER med trykket (dT_m/dP < 0)."""
    m = _motor()
    t_lo = m.melting_temperature(PARAMS, np.array([101325.0]))[0]
    t_hi = m.melting_temperature(PARAMS, np.array([10.0e6]))[0]
    assert t_hi < t_lo


# --------------------------------------------------------------------------
# Sublimasjonskurve (is I <-> gass)
# --------------------------------------------------------------------------

def test_sublimation_pressure_at_minus_20c():
    """P_sub(253.15 K) skal lande naer 103 Pa — innenfor 20 %."""
    m = _motor()
    p = m.sublimation_pressure(PARAMS, np.array([253.15]))[0]
    assert abs(p - 103.0) / 103.0 < 0.20


# --------------------------------------------------------------------------
# Trippelpunkt-konsistens: de tre kurvene skal moetes i ETT punkt
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
# Faseklassifisering — «hvilken fase er H2O her?»
# --------------------------------------------------------------------------

def test_classify_room_temperature_pressure_is_liquid():
    assert _motor().classify(PARAMS, 300.0, 101325.0) == "liquid"


def test_classify_low_pressure_is_gas():
    assert _motor().classify(PARAMS, 300.0, 1000.0) == "gas"


def test_classify_cold_atmosphere_is_solid():
    assert _motor().classify(PARAMS, 250.0, 101325.0) == "solid"


def test_classify_hot_atmosphere_is_gas():
    assert _motor().classify(PARAMS, 500.0, 101325.0) == "gas"


def test_classify_above_critical_is_supercritical():
    assert _motor().classify(PARAMS, 700.0, 101325.0) == "supercritical"


def test_classify_near_triple_point_reports_all_boundaries():
    """Naer trippelpunktet skal klassifikasjonen ikke krasje og vaere entydig."""
    m = _motor()
    for t in (273.15, 273.16, 273.17):
        for p in (500.0, 611.657, 700.0):
            assert m.classify(PARAMS, t, p) in {
                "solid", "liquid", "gas", "supercritical"}


# --------------------------------------------------------------------------
# Empati-porten: motoren erklarer hva den betjener (lokalt-globalt kobling)
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
