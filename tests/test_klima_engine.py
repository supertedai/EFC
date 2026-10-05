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
import re  # noqa: E402
from pathlib import Path  # noqa: E402

from efc_inference.engine.klima import TILSTANDER  # noqa: E402

try:  # pragma: no cover
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

_SKJEMA = (Path(__file__).resolve().parents[1]
           / "schema" / "regime_node.schema.json")


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


# ----------------------------------------------------------------------
# The switch's state contract (t_l040-klima-kontrakt)
#
# The switch is the part of the engine an outside call hits. Before this
# guard, an unknown member — a transliteration («snoball»), a trailing
# space, uppercase, or a type outside the contract — gave the «varm»
# answer inside the hysteresis band, where the canonical «snøball» state
# says False: the opposite regime, without a word.
# ----------------------------------------------------------------------


@pytest.mark.parametrize("ugyldig", [
    "snoball",     # ASCII transliteration of «snøball»
    "snowball",
    "kald",
    "varm ",       # trailing space
    "SNØBALL",     # uppercase
    "",
    None,          # a type outside the contract
    1,
])
def test_ukjent_tilstand_feiler_lukket(ugyldig):
    """A state outside the canonical two must FAIL — not be read as «varm».

    Measured before the fix: every one of these gave the «varm» answer (True)
    in the middle of the hysteresis band, where the canonical «snøball»
    state says False — the opposite regime, without a word. The error is not
    academic: the house's own rule about canonical spelling exists precisely
    because transliterations occur in practice, and the switch is the part
    of the engine an outside call hits.
    """
    e = KlimaEngine()
    p = {**PARAMS, "albedo": 0.392}   # in the middle of the hysteresis band
    with pytest.raises(ValueError):
        e.har_varm_likevekt(p, tilstand=ugyldig)


def test_tersklene_har_kjent_side():
    """The boundaries must have a KNOWN side: «varm» falls at alpha_fall
    (<=), «snøball» returns only BELOW alpha_retur (<). The values are set
    exactly from the computed thresholds — not as alpha +/- a rounding (the
    house's own experience: «exactly 2 sigma» lands on 1.999999999).
    """
    e = KlimaEngine()
    alpha_fall = e._alpha_ved_frysepunkt(PARAMS)
    alpha_retur = PARAMS.get("alpha_retur", 0.35)
    assert alpha_retur < alpha_fall, "the hysteresis band must have width"

    # at alpha_fall: a warm equilibrium exists (<=), the snowball state says no
    p_fall = {**PARAMS, "albedo": alpha_fall}
    assert e.har_varm_likevekt(p_fall, "varm") is True
    assert e.har_varm_likevekt(p_fall, "snøball") is False

    # at alpha_retur: the snowball state still says no (strict <)
    assert e.har_varm_likevekt({**PARAMS, "albedo": alpha_retur},
                               "snøball") is False
    # just below: the snowball melts back
    assert e.har_varm_likevekt({**PARAMS, "albedo": alpha_retur - 1e-9},
                               "snøball") is True


def test_kanoniske_tilstander_er_de_eneste_godtatte():
    """The contract must be explicitly named in the code, not only in prose."""
    assert set(TILSTANDER) == {"varm", "snøball"}
    e = KlimaEngine()
    p = {**PARAMS, "albedo": 0.392}
    for tilstand in TILSTANDER:
        assert isinstance(e.har_varm_likevekt(p, tilstand=tilstand), bool)


@pytest.mark.parametrize("varmekapasitet", [1.0e8, 4.0e8, 6.3e9])
def test_selvbeskrivelsen_baerer_effektive_parametre(varmekapasitet):
    """The number in the self-description must be EXPRESSED from the
    parameters, not written in. The test reads the number out of the text and
    compares it with the hand-computed time constant for three different heat
    capacities — a hardcoded «tau ~ 1 year» falls on the other two.
    """
    e = KlimaEngine()
    p = {**PARAMS, "hav_varmekapasitet": varmekapasitet}
    tau_aar = e.tidskonstant(p) / (365.25 * 86400)
    tekst = e.regime_node(p)["regime"]["validity"]
    treff = re.search(r"tau ~ (\d+) year", tekst)
    assert treff, f"the self-description lacks the time constant: {tekst}"
    assert int(treff.group(1)) == round(tau_aar)


def test_regime_node_er_skjemavalid():
    """The self-description must be a valid RegimeNode after the schema —
    the same machine check as the bridge tests for the cosmological engines.
    """
    if jsonschema is None:
        pytest.skip("jsonschema is not installed")
    skjema = json.loads(_SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    node = KlimaEngine().regime_node(PARAMS)
    feil = sorted(validator.iter_errors(node), key=lambda e: list(e.path))
    meldinger = "; ".join(f"{list(e.path)}: {e.message}" for e in feil[:3])
    assert not feil, f"efc.klima_engine fails the schema: {meldinger}"
