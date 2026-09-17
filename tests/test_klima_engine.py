"""Tester for KlimaEngine — strålingsbalanse som energiflyt (L-040).

Klimaets energibalansemodell er EFC i ren form på jorden: energi inn
(sol), buffer (havets varmekapasitet, is-albedo), terskeloverganger
(iskollaps). Motoren er en IDEALISERT 0D-energibalansemodell — IKKE en
klimamodell-konkurrent, og det står i selvbeskrivelsen.

Kortet navnga TO regimebrytere: is-albedo og AMOC. Bare is-albedo er
kodet. AMOC-bryteren er VURDERT og BEVISST UTELATT (t_9978fc90) — den
avgrensningen testes eksplisitt nedenfor, så fraværet ikke kan bli
taushet igjen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.klima import KlimaEngine

PARAMS = {
    "solarkonstant": 1361.0,       # W/m^2
    "albedo": 0.30,                # jordas gjennomsnitt
    "emissivitet": 0.61,           # effektiv (drivhuseffekt inkludert)
    "stefan_boltzmann": 5.670374419e-8,  # W/(m^2 K^4)
    "hav_varmekapasitet": 1.0e8,   # J/(m^2 K) — blandingslaget
}


def test_likevektstemperatur_maten():
    """Jordas effektive likevektstemperatur: ~288 K med drivhus."""
    e = KlimaEngine()
    t = e.likevektstemperatur(PARAMS)
    assert 280.0 < t < 295.0  # jorda ligger her med drivhus


def test_likevektstemperatur_uten_drivhus_kaldere():
    """Med emissivitet 1 (svart legeme) og albedo 0.3: ~255 K."""
    params_uten = {**PARAMS, "emissivitet": 1.0}
    e = KlimaEngine()
    t = e.likevektstemperatur(params_uten)
    forventet = (PARAMS["solarkonstant"] * (1 - PARAMS["albedo"])
                 / (4 * PARAMS["stefan_boltzmann"])) ** 0.25
    assert np.isclose(t, forventet, rtol=1e-9)


def test_is_albedo_tilbakekobling_er_positiv():
    """Is-albedo: kaldere -> mer is -> høyere albedo -> enda kaldere.
    Positiv tilbakekobling (forsterkning)."""
    e = KlimaEngine()
    forsterkning = e.albedo_tilbakekobling(PARAMS, delta_t=-1.0)
    assert forsterkning > 1.0  # forsterker, demper ikke


def test_bufferen_demper_forstyrrelser():
    """Havets varmekapasitet er bufferen: responsen på en
    strålingsforstyrrelse er treg — dempet og forsinket."""
    e = KlimaEngine()
    respons = e.tidskonstant(PARAMS)
    # tidskonstant = C / (4 eps sigma T^3) — år i praksis
    assert respons > 0
    assert respons / (365.25 * 86400) < 100  # under 100 år


def test_regimeskifte_ved_albedo_terskel():
    """Is-albedo-bryteren: over en terskel-albedo finnes ingen varm
    likevekt — systemet faller til snøballjord."""
    e = KlimaEngine()
    albedoer = np.linspace(0.3, 0.9, 7)
    stabile = [e.har_varm_likevekt({**PARAMS, "albedo": a})
               for a in albedoer]
    # ved høy albedo forsvinner den varme likevekten
    assert stabile[-1] is False
    assert stabile[0] is True


def test_hysterese_to_tilstandsavhengige_terskler():
    """Ekte hysterese: systemet faller fra «varm» ved alpha_fall,
    men returnerer fra «snøball» først ved alpha_retur (< alpha_fall).
    I vinduet mellom dem avhenger svaret av TILSTANDEN."""
    e = KlimaEngine()
    alpha_fall = e._alpha_ved_frysepunkt(PARAMS)
    alpha_retur = PARAMS.get("alpha_retur", 0.35)
    assert alpha_retur < alpha_fall
    # I hysteresebåndet: varm-tilstand sier «varm», snøball-tilstand
    # sier «ingen varm likevekt»
    midt = (alpha_fall + alpha_retur) / 2
    p = {**PARAMS, "albedo": midt}
    assert e.har_varm_likevekt(p, tilstand="varm") is True
    assert e.har_varm_likevekt(p, tilstand="snøball") is False


def test_regime_node_selvbeskrivelse():
    e = KlimaEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.klima_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealiser" in tekst or "0d" in tekst
    assert "ikke en klimamodell" in tekst or \
           "ikke klimamodell" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402


# ----------------------------------------------------------------------
# AMOC-avgrensningen (t_9978fc90)
#
# Kortet for klima-motoren navngir to regimebrytere: is-albedo og AMOC.
# Bare is-albedo er kodet. Disse testene holder avgrensningen synlig:
# fraværet skal stå i selvbeskrivelsen, med grunn og med en henvisning
# til hvor bryteren hører hjemme — og det skal fortsatt være SANT at
# koden ikke har den.
# ----------------------------------------------------------------------


def test_amoc_bryteren_er_bevisst_utelatt_ikke_glemt():
    """AMOC er VURDERT og BEVISST UTELATT. Avgrensningen skal stå i
    moduldocstringen, i node.ontology.assumes og i node.regime.validity
    — ikke bare i hodet på den som vurderte den."""
    import efc_inference.engine.klima as modul

    doc = (modul.__doc__ or "").lower()
    assert "amoc" in doc, "moduldocstringen nevner ikke AMOC"
    assert "utelatt" in doc, "moduldocstringen sier ikke at AMOC er utelatt"

    node = KlimaEngine().regime_node(PARAMS)

    assumes = " ".join(node["ontology"]["assumes"]).lower()
    assert "amoc" in assumes, "ontology.assumes nevner ikke AMOC"
    assert "utelatt" in assumes, "ontology.assumes sier ikke UTELATT"

    validity = node["regime"]["validity"].lower()
    assert "amoc" in validity, "regime.validity nevner ikke AMOC"
    assert "utelatt" in validity, "regime.validity sier ikke UTELATT"


def test_amoc_avgrensningen_oppgir_grunn_og_tilhørighet():
    """En avgrensning uten grunn er en forglemmelse med finere ord.
    Grunnen her: 0D-energibalansen har ingen sirkulasjonsvariabel.
    Og den skal si hvor bryteren HØRER hjemme — egen motor, eget fag."""
    node = KlimaEngine().regime_node(PARAMS)
    tekst = (node["regime"]["validity"] + " "
             + " ".join(node["ontology"]["assumes"])).lower()
    assert "sirkulasjon" in tekst, "grunnen (ingen sirkulasjon) mangler"
    assert "ferskvann" in tekst, "driveren (ferskvannspåslag) mangler"
    assert "egen motor" in tekst or "eget fag" in tekst, (
        "avgrensningen sier ikke hvor AMOC-bryteren hører hjemme")


def test_amoc_er_faktisk_ikke_kodet():
    """Avgrensningen skal være SANN: det finnes ingen AMOC-bryter i
    koden, og parameterrommet er fortsatt strålingsboksens. Koder noen
    bryteren senere, må de røre deklarasjonen — testen gjør det
    maskinelt synlig i stedet for stille."""
    e = KlimaEngine()
    assert [m for m in dir(e) if "amoc" in m.lower()] == [], \
        "AMOC er kodet — da holder ikke avgrensningen lenger"
    for navn in ("ferskvann", "salinitet", "omvelting"):
        treff = [p for p in KlimaEngine.REQUIRED_PARAMS if navn in p.lower()]
        assert treff == [], f"AMOC-parameter i REQUIRED_PARAMS: {treff}"
    assert len(KlimaEngine.REQUIRED_PARAMS) == 5, \
        "REQUIRED_PARAMS er utvidet — oppdater AMOC-avgrensningen"
