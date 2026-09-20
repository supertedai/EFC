"""Tests for KlimaEngine — radiative balance as energy flow (L-040).

The climate's energy-balance model is EFC in pure form on Earth: energy in
(sun), buffer (the ocean's heat capacity, ice albedo), threshold transitions
(ice collapse). The engine is an IDEALISED 0D energy-balance model — NOT a
climate-model competitor, and that is stated in the self-description.

The card named TWO regime switches: ice albedo and AMOC. Only ice albedo is
coded. The AMOC switch is CONSIDERED and DELIBERATELY OMITTED (t_9978fc90) — that
boundary is tested explicitly below, so the absence cannot become
silence again.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.klima import KlimaEngine

PARAMS = {
    "solarkonstant": 1361.0,       # W/m^2
    "albedo": 0.30,                # the Earth's average
    "emissivitet": 0.61,           # effective (greenhouse effect included)
    "stefan_boltzmann": 5.670374419e-8,  # W/(m^2 K^4)
    "hav_varmekapasitet": 1.0e8,   # J/(m^2 K) — the mixed layer
}


def test_likevektstemperatur_maten():
    """The Earth's effective equilibrium temperature: ~288 K with a greenhouse."""
    e = KlimaEngine()
    t = e.likevektstemperatur(PARAMS)
    assert 280.0 < t < 295.0  # the Earth sits here with a greenhouse


def test_likevektstemperatur_uten_drivhus_kaldere():
    """With emissivity 1 (black body) and albedo 0.3: ~255 K."""
    params_uten = {**PARAMS, "emissivitet": 1.0}
    e = KlimaEngine()
    t = e.likevektstemperatur(params_uten)
    forventet = (PARAMS["solarkonstant"] * (1 - PARAMS["albedo"])
                 / (4 * PARAMS["stefan_boltzmann"])) ** 0.25
    assert np.isclose(t, forventet, rtol=1e-9)


def test_is_albedo_tilbakekobling_er_positiv():
    """Ice albedo: colder -> more ice -> higher albedo -> even colder.
    Positive feedback (amplification)."""
    e = KlimaEngine()
    forsterkning = e.albedo_tilbakekobling(PARAMS, delta_t=-1.0)
    assert forsterkning > 1.0  # amplifies, does not damp


def test_bufferen_demper_forstyrrelser():
    """The ocean's heat capacity is the buffer: the response to a
    radiative perturbation is slow — damped and delayed."""
    e = KlimaEngine()
    respons = e.tidskonstant(PARAMS)
    # time constant = C / (4 eps sigma T^3) — years in practice
    assert respons > 0
    assert respons / (365.25 * 86400) < 100  # under 100 years


def test_regimeskifte_ved_albedo_terskel():
    """The ice-albedo switch: above a threshold albedo there is no warm
    equilibrium — the system falls to snowball Earth."""
    e = KlimaEngine()
    albedoer = np.linspace(0.3, 0.9, 7)
    stabile = [e.har_varm_likevekt({**PARAMS, "albedo": a})
               for a in albedoer]
    # at high albedo the warm equilibrium disappears
    assert stabile[-1] is False
    assert stabile[0] is True


def test_hysterese_to_tilstandsavhengige_terskler():
    """Real hysteresis: the system falls from «varm» at alpha_fall,
    but returns from «snøball» only at alpha_retur (< alpha_fall).
    In the window between them the answer depends on the STATE."""
    e = KlimaEngine()
    alpha_fall = e._alpha_ved_frysepunkt(PARAMS)
    alpha_retur = PARAMS.get("alpha_retur", 0.35)
    assert alpha_retur < alpha_fall
    # In the hysteresis band: the warm state says «varm», the snowball state
    # says «no warm equilibrium»
    midt = (alpha_fall + alpha_retur) / 2
    p = {**PARAMS, "albedo": midt}
    assert e.har_varm_likevekt(p, tilstand="varm") is True
    assert e.har_varm_likevekt(p, tilstand="snøball") is False


def test_regime_node_selvbeskrivelse():
    e = KlimaEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.klima_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealized" in tekst or "0d" in tekst
    assert "not a climate-model competitor" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402


# ----------------------------------------------------------------------
# The AMOC boundary (t_9978fc90)
#
# The card for the climate engine names two regime switches: ice albedo and AMOC.
# Only ice albedo is coded. These tests keep the boundary visible:
# the absence must stand in the self-description, with a reason and a reference
# to where the switch belongs — and it must still be TRUE that
# the code does not have it.
# ----------------------------------------------------------------------


def test_amoc_bryteren_er_bevisst_utelatt_ikke_glemt():
    """AMOC is CONSIDERED and DELIBERATELY OMITTED. The boundary must stand in
    the module docstring, in node.ontology.assumes and in node.regime.validity
    — not only in the head of the one who assessed it."""
    import efc_inference.engine.klima as modul

    doc = (modul.__doc__ or "").lower()
    assert "amoc" in doc, "moduldocstringen nevner ikke AMOC"
    assert "deliberately omitted" in doc, "moduldocstringen sier ikke at AMOC er utelatt"

    node = KlimaEngine().regime_node(PARAMS)

    assumes = " ".join(node["ontology"]["assumes"]).lower()
    assert "amoc" in assumes, "ontology.assumes nevner ikke AMOC"
    assert "deliberately omitted" in assumes, "ontology.assumes sier ikke UTELATT"

    validity = node["regime"]["validity"].lower()
    assert "amoc" in validity, "regime.validity nevner ikke AMOC"
    assert "deliberately omitted" in validity, "regime.validity sier ikke UTELATT"


def test_amoc_avgrensningen_oppgir_grunn_og_tilhørighet():
    """A boundary without a reason is an oversight in finer words.
    The reason here: the 0D energy balance has no circulation variable.
    And it must say where the switch BELONGS — its own engine, its own discipline."""
    node = KlimaEngine().regime_node(PARAMS)
    tekst = (node["regime"]["validity"] + " "
             + " ".join(node["ontology"]["assumes"])).lower()
    assert "overturning cell" in tekst, "grunnen (ingen sirkulasjon) mangler"
    assert "freshwater" in tekst, "driveren (ferskvannspåslag) mangler"
    assert "separate engine" in tekst or "own discipline" in tekst, (
        "avgrensningen sier ikke hvor AMOC-bryteren hører hjemme")


def test_amoc_er_faktisk_ikke_kodet():
    """The boundary must be TRUE: there is no AMOC switch in
    the code, and the parameter space is still the radiation box's. If anyone
    codes the switch later, they must touch the declaration — the test makes that
    machine-visible instead of silent."""
    e = KlimaEngine()
    assert [m for m in dir(e) if "amoc" in m.lower()] == [], \
        "AMOC is coded — then the boundary no longer holds"
    for navn in ("ferskvann", "salinitet", "omvelting"):
        treff = [p for p in KlimaEngine.REQUIRED_PARAMS if navn in p.lower()]
        assert treff == [], f"AMOC parameter in REQUIRED_PARAMS: {treff}"
    assert len(KlimaEngine.REQUIRED_PARAMS) == 5, \
        "REQUIRED_PARAMS has been extended — update the AMOC boundary"
