"""Tester for holding->release-motorene: sol-flare, jordskjelv og transient (L-026/L-028/L-036).

Alle tre motorer koder den samme formen: energi/spenning/masse lades
langsomt i en buffer, og utloses plutselig naar en terskel krysses — det
samme monsteret som ble funnet i recon-en av kosmos.sol (GOES-flares),
kosmos.jord (USGS-skjelv) og kosmos.transienter (ALeRCE/ZTF-hendelser).
Motorene er REGIME-MOTORER: de beregner formens observabler
(oppladningstid, utlost energi/moment, klasse) fra fysikalske parametre
— de pastar ikke prediksjonskraft for enkelthendelser.

Disiplin: modellene er idealiserte (Avallon-stil magnetisk buffer;
elastic-rebound/Burridge-Knopoff-stil forkastningslading; kollaps-buffer
med G*M^2/R). Det skal sta i motorens egen beskrivelse, og utlosning skal
vaere TERSKELSTYRT — ikke tidsstyrt.

Transient-motoren (L-036) har UTSATT atlas-kobling: schema/regime_nodes.jsonld
roeres ikke for kollisjonsrekkefolgen i kortet er landet (t_bdf8e82f).
Testen nedenfor gjor utsettelsen maskinelt synlig og sier hva som skal
skje naar atlas-noden legges.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from efc_inference.engine.solar_flare import SolarFlareEngine
from efc_inference.engine.jordskjelv import JordskjelvEngine
from efc_inference.engine.transient import TransientEngine

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

_ATLAS = Path(__file__).resolve().parents[1] / "schema" / "regime_nodes.jsonld"
_SKJEMA = Path(__file__).resolve().parents[1] / "schema" / "regime_node.schema.json"


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


def test_solarflare_goes_anker_1e22_j_er_m():
    """Kalibreringsankeret: 1e22 J ~ M-klasse (typisk M-flare-energi).
    Proxeyens dokumentasjon og kode skal stemme."""
    e = SolarFlareEngine()
    assert e.goes_klasse(1e22) == "M"
    assert e.goes_klasse(1e23) == "X"
    assert e.goes_klasse(1e21) == "C"
    assert e.goes_klasse(1e20) == "B"


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
# Transient-motoren (stjernedod)
# ----------------------------------------------------------------------

TRANS_PARAMS = {
    "G": 6.67430e-11,           # m^3 kg^-1 s^-2 — gravitasjonskonstanten
    "terskelmasse": 2.785e30,   # kg — stabilitetsgrensen (Chandrasekhar-stil, MODELLPARAMETER)
    "radius": 1.0e4,            # m — kjerneradius ved kollaps
    "vekstrate": 6.3e19,        # kg/s — massetilvekst (oppladningen)
    "stigningstid_dager": 20.0,  # dager — rask stigning i lettkurven
    "haletid_dager": 40.0,      # dager — eksponensiell hale
    "stigningseksponent": 2.0,  # formparameter for stigningen
}


def test_transient_bindingsenergi_skalerer_med_masse_kvadrert():
    """E_bind = G*M^2/R — og den skalerer som M^2 (4x masse -> 4x energi)."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    forventet = (TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"])
    assert np.isclose(e.bindingsenergi(TRANS_PARAMS, np.array([m]))[0], forventet)
    dobbel = e.bindingsenergi(TRANS_PARAMS, np.array([2 * m]))[0]
    assert np.isclose(dobbel / forventet, 4.0)


def test_transient_utlost_energi_ved_terskelen():
    """Utlost energi VED terskelen = G*terskelmasse^2/R."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    forventet = TRANS_PARAMS["G"] * m ** 2 / TRANS_PARAMS["radius"]
    assert np.isclose(e.utlost_energi(TRANS_PARAMS), forventet)
    assert e.utlost_energi(TRANS_PARAMS) > 0


def test_transient_holdetid_fra_vekstrate():
    """Holdetiden = terskelmasse / vekstrate (sekunder), positiv og endelig."""
    e = TransientEngine()
    t = e.holdetid(TRANS_PARAMS)
    assert np.isclose(t, TRANS_PARAMS["terskelmasse"] / TRANS_PARAMS["vekstrate"])
    assert t > 0


def test_transient_holdingsfase_under_terskel():
    """Under stabilitetsgrensen holder kjernen: ingen utlosning (0)."""
    e = TransientEngine()
    out = e.compute(TRANS_PARAMS, np.array([0.5 * TRANS_PARAMS["terskelmasse"]]))
    assert out.shape == (1,)
    assert out[0] == 0.0


def test_transient_utlosning_bruker_den_lokale_massen():
    """Konvensjonen skal vaere eksplisitt og testet: compute() bruker den
    LOKALE massen (energien skalerer med M^2), mens utlost_energi(params)
    er energien VED terskelen — samme konvensjon som solar_flare.compute().
    En implementasjon som returnerer den deklarerte terskelenergien for en
    masse OVER terskelen skal falle her."""
    e = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    ved_terskel = e.compute(TRANS_PARAMS, np.array([m]))[0]
    assert np.isclose(ved_terskel, e.utlost_energi(TRANS_PARAMS))
    over = e.compute(TRANS_PARAMS, np.array([1.5 * m]))[0]
    assert np.isclose(over, e.bindingsenergi(TRANS_PARAMS, np.array([1.5 * m]))[0])
    assert over > ved_terskel
    assert not np.isclose(over, ved_terskel)


def test_transient_lettkurve_peak_ved_stigningstiden():
    """Formen: (t/t_stig)^alpha under stigningstiden, exp(-(t-t_stig)/t_hale)
    etter — kontinuerlig med maksimum 1.0 i t = stigningstid_dager."""
    e = TransientEngine()
    t_stig = TRANS_PARAMS["stigningstid_dager"]
    t_hale = TRANS_PARAMS["haletid_dager"]
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig]))[0], 1.0)
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([0.0]))[0], 0.0)
    # stigningen er rask og monoton: alpha = 2 -> (t/t_stig)^2
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig / 2]))[0], 0.25)
    # halen er eksponensiell med t_hale som tidsskala
    assert np.isclose(e.lettkurve(TRANS_PARAMS, np.array([t_stig + t_hale]))[0],
                      np.exp(-1.0))
    # monoton stigning foran kneet, monoton hale etter (to punkter hver vei)
    stig = e.lettkurve(TRANS_PARAMS, np.array([0.2, 0.5, 0.9]) * t_stig)
    hale = e.lettkurve(TRANS_PARAMS, np.array([1.0, 2.0, 5.0]) * t_stig)
    assert list(stig) == sorted(stig)
    assert list(hale) == sorted(hale, reverse=True)


def test_transient_lettkurve_enhet_er_dager_ikke_sekunder():
    """Enhetsfolsom logikk: formen tar DAGER (parameteren heter _dager).
    Fixturen er laget slik at en feil enhet gaar til MOTSATT konklusjon:
    100 dager = t_stig + 2*t_hale skal gi exp(-2) ~ 0.135, mens en
    implementasjon som leser parameteren som sekunder gir exp(-1.7e5) ~ 0.
    """
    e = TransientEngine()
    t_stig = TRANS_PARAMS["stigningstid_dager"]
    t_hale = TRANS_PARAMS["haletid_dager"]
    v = e.lettkurve(TRANS_PARAMS, np.array([t_stig + 2 * t_hale]))[0]
    assert v > 0.1
    assert np.isclose(v, np.exp(-2.0))
    # ...og langt ute paa halen skal den fortsatt vaere > 0, men < 1e-6
    langt = e.lettkurve(TRANS_PARAMS, np.array([t_stig + 20 * t_hale]))[0]
    assert 0.0 < langt < 1e-6


def test_transient_fail_closed_paa_ugyldig_inngang():
    """Ugyldig inngang gir NaN — aldri en gjetning og aldri en exception."""
    e = TransientEngine()
    ut = e.compute(TRANS_PARAMS, np.array([-1.0, np.nan, TRANS_PARAMS["terskelmasse"]]))
    assert np.isnan(ut[0]) and np.isnan(ut[1]) and ut[2] > 0
    lk = e.lettkurve(TRANS_PARAMS, np.array([-1.0, np.nan, np.inf]))
    assert np.all(np.isnan(lk))
    assert e.validate_params(TRANS_PARAMS) is True
    ufullstendig = dict(TRANS_PARAMS)
    del ufullstendig["radius"]
    assert e.validate_params(ufullstendig) is False


def test_transient_regime_node_selvbeskrivelse():
    e = TransientEngine()
    node = e.regime_node(TRANS_PARAMS)
    assert node["id"] == "efc.transient_engine"
    assert "holding" in node["regime"]["validity"].lower()
    assert "release" in node["regime"]["validity"].lower() or \
           "utlos" in node["regime"]["validity"].lower()
    assert node["regime"]["law_form"].strip()
    tekst = json.dumps(node, ensure_ascii=False)
    assert "IDEALISERT" in tekst
    # De tre andre holding->release-endepunktene skal vaere navngitt.
    for endepunkt in ("homo.aksjonspotensial", "efc.solar_flare_engine",
                      "efc.jordskjelv_engine"):
        assert endepunkt in tekst, endepunkt
    assert "ANALOGOUS_TO" in tekst
    # Scoping: motoren koder kollaps-grenen, ikke hendelsesstrommen.
    assert "kosmos.transienter" in tekst
    assert "hendelsesstr" in tekst.lower() or "ikke ett regime" in tekst.lower()


def test_transient_regime_node_er_gyldig_etter_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
    skjema = json.loads(_SKJEMA.read_text(encoding="utf-8"))
    node = TransientEngine().regime_node(TRANS_PARAMS)
    feil = sorted(jsonschema.Draft202012Validator(
        skjema["$defs"]["RegimeNode"]).iter_errors(node), key=lambda e: list(e.path))
    if feil:
        raise AssertionError("; ".join(f"{list(e.path)}: {e.message}" for e in feil[:3]))


def test_transient_validity_deriveres_fra_parametrene():
    """Selvbeskrivelsen skal baere de EFFEKTIVE parametrene — ikke
    hardkodede kanoniske tall (review-familien fra victron/vann)."""
    e = TransientEngine()
    node = e.regime_node(TRANS_PARAMS)
    tekst = node["regime"]["validity"] + " " + node["regime"]["law_form"]
    alt = {
        "G": TRANS_PARAMS["G"],
        "terskelmasse": 4.0e30,
        "radius": 3.0e4,
        "vekstrate": 1.0e20,
        "stigningstid_dager": 33.0,
        "haletid_dager": 77.0,
        "stigningseksponent": 2.5,
    }
    alt_tekst = e.regime_node(alt)["regime"]["validity"]
    assert str(alt["terskelmasse"]) in alt_tekst
    assert str(alt["radius"]) in alt_tekst
    assert str(alt["vekstrate"]) in alt_tekst or str(
        alt["terskelmasse"] / alt["vekstrate"]) in alt_tekst
    for kanonisk in ("2.785e+30", "10000.0", "6.3e+19", "20.0", "40.0"):
        assert kanonisk not in alt_tekst, kanonisk
    # ...og de kanoniske tallene SKAL staa i den kanoniske teksten.
    for kanonisk in ("2.785e+30", "10000.0", "20.0", "40.0"):
        assert kanonisk in tekst, kanonisk


def test_transient_atlas_node_venter_paa_kollisjonsrekkefolgen():
    """Atlas-noden er UTSATT med vilje (kollisjonsrekkefolgen i kortet:
    schema/regime_nodes.jsonld roeres ikke for t_bdf8e82f er landet).

    Denne testen er en VAKT, ikke en pastand om at noe mangler: den feiler
    den dagen noden legges — med instruksen om hva som da skal gjores.
    """
    atlas = json.loads(_ATLAS.read_text(encoding="utf-8"))
    ids = {n["id"] for n in atlas["nodes"]}
    if "efc.transient_engine" in ids:
        pytest.fail(
            "efc.transient_engine finnes naa i atlaset: bytt denne vakten mot "
            "bro-testen (regime_node() == atlas-noden, maskinelt) og legg inn "
            "ANALOGOUS_TO-relasjonene til homo.aksjonspotensial, "
            "efc.solar_flare_engine og efc.jordskjelv_engine.")
    assert TransientEngine().regime_node(TRANS_PARAMS)["id"] == "efc.transient_engine"


# ----------------------------------------------------------------------
# Felles disiplin
# ----------------------------------------------------------------------


def test_alle_tre_motorene_er_idealisert_merket():
    """Motorene skal SELV si at de er idealiserte regime-modeller —
    ikke prediksjonsverktoy for enkelthendelser."""
    for e, params in ((SolarFlareEngine(), SOLFLARE_PARAMS),
                      (JordskjelvEngine(), JORDSKJELV_PARAMS),
                      (TransientEngine(), TRANS_PARAMS)):
        node = e.regime_node(params)
        assert "idealis" in json.dumps(node).lower() or \
               "ideal" in json.dumps(node).lower()


def test_alle_tre_motorene_er_terskelstyrte_ikke_tidsstyrte():
    """Samme form i tre domener: under terskelen skjer INGENTING, over
    terskelen slippes bufferen. Tid alene utloser ingenting."""
    solar = SolarFlareEngine()
    assert solar.compute(SOLFLARE_PARAMS, np.array([0.29]))[0] == 0.0
    assert solar.compute(SOLFLARE_PARAMS, np.array([0.31]))[0] > 0.0

    jord = JordskjelvEngine()
    assert jord.compute(JORDSKJELV_PARAMS, np.array([2.9e6]))[0] == 0.0
    assert jord.compute(JORDSKJELV_PARAMS, np.array([3.1e6]))[0] > 0.0

    trans = TransientEngine()
    m = TRANS_PARAMS["terskelmasse"]
    assert trans.compute(TRANS_PARAMS, np.array([0.99 * m]))[0] == 0.0
    assert trans.compute(TRANS_PARAMS, np.array([1.01 * m]))[0] > 0.0
