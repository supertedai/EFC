"""Tester for holding->release-motorene: sol-flare og jordskjelv (L-026/L-028).

Begge motorer koder den samme formen: energi/spenning lades langsomt i
en buffer, og utloses plutselig naar en terskel krysses — det samme
monsteret som ble funnet i recon-en av kosmos.sol (GOES-flares) og
kosmos.jord (USGS-skjelv). Motorene er REGIME-MOTORER: de beregner
formens observabler (oppladningstid, utlost energi/moment, klasse) fra
fysikalske parametre — de pastar ikke prediksjonskraft for enkelthendelser.

Disiplin: modellene er idealiserte (Avallon-stil magnetisk buffer;
elastic-rebound/Burridge-Knopoff-stil forkastningslading). Det skal sta
i motorens egen beskrivelse, og utlosning skal vaere TERSKELSTYRT —
ikke tidsstyrt.
"""
from __future__ import annotations

import json

import numpy as np
import pytest

from efc_inference.engine.solar_flare import SolarFlareEngine
from efc_inference.engine.jordskjelv import JordskjelvEngine


# ----------------------------------------------------------------------
# Sol-flare-motoren
# ----------------------------------------------------------------------

SOLFLARE_PARAMS = {
    "mu_0": 1.25663706212e-6,   # N/A^2 — vakumpermeabilitet
    "b_crit": 0.3,              # T — kritisk feltstyrke for utlosning
    "oppladningsrate": 1.0e-6,  # T/s — dB/dt i aktivt omraade
    "volum": 1.0e21,            # m^3 — aktivt omraade-volum
}


def test_solarflare_beregner_oppladningstid():
    e = SolarFlareEngine()
    t = e.oppladningstid(SOLFLARE_PARAMS)
    assert np.isclose(t, SOLFLARE_PARAMS["b_crit"] / SOLFLARE_PARAMS["oppladningsrate"])
    assert t > 0


def test_solarflare_utlost_energi_fra_magnetisk_buffer():
    e = SolarFlareEngine()
    energi = e.utlost_energi(SOLFLARE_PARAMS)
    # E = B^2 / (2 mu_0) * volum
    forventet = (SOLFLARE_PARAMS["b_crit"] ** 2
                 / (2 * SOLFLARE_PARAMS["mu_0"])) * SOLFLARE_PARAMS["volum"]
    assert np.isclose(energi, forventet)


def test_solarflare_goes_klasse_monoton():
    """Hoyere utlost energi -> minst like hoy GOES-klasse (A<B<C<M<X)."""
    e = SolarFlareEngine()
    klasser = [e.goes_klasse(e.utlost_energi(
        {**SOLFLARE_PARAMS, "b_crit": b})) for b in (0.1, 0.2, 0.3, 0.5)]
    assert klasser == sorted(klasser, key="ABCMX".index)
    assert all(k in "ABCMX" for k in klasser)


def test_solarflare_holdingsfase_for_terskel():
    """For B < b_crit er bufferen i holding: ingen utlosning, energien
    bygges. compute() skal rapportere holding, ikke utlosning."""
    e = SolarFlareEngine()
    params = dict(SOLFLARE_PARAMS)
    out = e.compute(params, np.array([0.1]))  # B = 0.1 T < 0.3 T
    assert out.shape == (1,)
    # Ingen utlosning: utlost energi = 0
    assert out[0] == 0.0


def test_solarflare_regime_node_selvbeskrivelse():
    e = SolarFlareEngine()
    node = e.regime_node(SOLFLARE_PARAMS)
    assert node["id"] == "efc.solar_flare_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "utlos" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()


# ----------------------------------------------------------------------
# Jordskjelv-motoren
# ----------------------------------------------------------------------

JORDSKJELV_PARAMS = {
    "skjaermodul": 3.0e10,       # Pa — skjaermodul (jordskorpen)
    "lade_rate": 1.0e4,          # Pa/aar — spenningsakkumulering
    "terskel": 3.0e6,            # Pa — spenningsfall ved utlosning
    "areal": 1.0e8,              # m^2 — bruddflate
}


def test_jordskjelv_gjentakelsestid():
    e = JordskjelvEngine()
    t = e.gjentakelsestid(JORDSKJELV_PARAMS)
    assert np.isclose(t, JORDSKJELV_PARAMS["terskel"] / JORDSKJELV_PARAMS["lade_rate"])
    assert t > 0


def test_jordskjelv_moment_og_magnitude():
    e = JordskjelvEngine()
    m0 = e.seismisk_moment(JORDSKJELV_PARAMS)
    # M0 = mu * A * D med D = terskel / mu
    forventet = (JORDSKJELV_PARAMS["skjaermodul"] * JORDSKJELV_PARAMS["areal"]
                 * (JORDSKJELV_PARAMS["terskel"] / JORDSKJELV_PARAMS["skjaermodul"]))
    assert np.isclose(m0, forventet)
    # Mw = (2/3)(log10 M0 - 9.1)
    mw = e.magnitude(JORDSKJELV_PARAMS)
    assert np.isclose(mw, (2 / 3) * (np.log10(m0) - 9.1))


def test_jordskjelv_holdingsfase_for_akkumulering():
    e = JordskjelvEngine()
    # Spenning under terskel: holding — momentet bygges, utlosning er 0
    out = e.compute(JORDSKJELV_PARAMS, np.array([1.0e6]))  # 1 MPa < 3 MPa
    assert out.shape == (1,)
    assert out[0] == 0.0


def test_jordskjelv_utlosning_over_terskel():
    e = JordskjelvEngine()
    out = e.compute(JORDSKJELV_PARAMS, np.array([3.2e6]))  # over terskel
    assert out.shape == (1,)
    assert out[0] > 0.0  # momentet slippes


def test_jordskjelv_regime_node_selvbeskrivelse():
    e = JordskjelvEngine()
    node = e.regime_node(JORDSKJELV_PARAMS)
    assert node["id"] == "efc.jordskjelv_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "utlos" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()


# ----------------------------------------------------------------------
# Felles disiplin
# ----------------------------------------------------------------------

def test_begge_motorene_er_idealisert_merket():
    """Motorene skal SELV si at de er idealiserte regime-modeller —
    ikke prediksjonsverktoy for enkelthendelser."""
    for e, params in ((SolarFlareEngine(), SOLFLARE_PARAMS),
                      (JordskjelvEngine(), JORDSKJELV_PARAMS)):
        node = e.regime_node(params)
        assert "idealis" in json.dumps(node).lower() or \
               "ideal" in json.dumps(node).lower()
