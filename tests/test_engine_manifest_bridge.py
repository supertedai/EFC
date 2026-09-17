"""Test av motor↔skjema-broen (trinn 4).

WaterPhaseEngine sin nye metode regime_node() skal returnere en GYLDIG
RegimeNode etter regime_node.schema.json — slik at enhver EFCEngine med
denne metoden er maskinelt koblet til atlasets struktur. Broen er
generisk: fremtidige motorer faar atlas-kobling gratis.

Den lokalt-globale koblingen (empati-porten) er en MASKINELL
konsistenssjekk: motorens deklarerte gyldighetsomraade-tall skal stemme
med instansens h2o-node-tall — ikke bare se like ut i tekst.

TDD: skrives foer regime_node() finnes — feiler med AttributeError.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from efc_inference.engine.water import WaterPhaseEngine  # noqa: E402

SCHEMA_PATH = _REPO / "schema" / "regime_node.schema.json"
INSTANCE_PATH = _REPO / "schema" / "regime_nodes.jsonld"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema ikke installert")

PARAMS = {
    "t_triple": 273.16,
    "p_triple": 611.657,
    "t_critical": 647.096,
    "p_critical": 22.064e6,
    "latent_vaporization_ref": 2.257e6,
    "t_vap_ref": 373.15,
    "p_vap_ref": 101325.0,
    "latent_fusion": 333550.0,
    "latent_sublimation": 2.834e6,
    "gas_constant": 461.5,
    "density_ice": 916.7,
    "density_water": 999.8,
    "p_ice_ih_max": 208.566e6,
    "t_sublim_min": 50.0,
}


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _instance() -> dict:
    return json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))


def _regime_node_schema() -> dict:
    s = _schema()
    return {
        "$schema": s["$schema"],
        "$defs": s["$defs"],
        "$ref": "#/$defs/RegimeNode",
    }


# --------------------------------------------------------------------------
# Broen: motorens selvbeskrivelse ER en regime-node
# --------------------------------------------------------------------------

@requires_jsonschema
def test_engine_regime_node_is_valid():
    """regime_node() skal validere mot RegimeNode-definisjonen i skjemaet."""
    node = WaterPhaseEngine().regime_node(PARAMS)
    jsonschema.Draft202012Validator(_regime_node_schema()).validate(node)


def test_engine_regime_node_has_engine_id():
    node = WaterPhaseEngine().regime_node(PARAMS)
    assert node["id"] == "efc.water_phase_engine"


def test_engine_regime_node_declares_its_law_form():
    node = WaterPhaseEngine().regime_node(PARAMS)
    assert "Clausius-Clapeyron" in node["regime"]["law_form"]


def test_manifest_contract_unchanged():
    """manifest() fra trinn 1 skal vaere urort — bakoverkompatibelt."""
    m = WaterPhaseEngine()
    manifest = m.manifest(PARAMS)
    assert manifest["name"]
    akser = {c["axis"] for c in manifest["couplings"]}
    assert {"node", "regime", "fase", "emergens", "proxy"} <= akser


# --------------------------------------------------------------------------
# Lokalt-globalt kobling: maskinell konsistens motor <-> atlas
# --------------------------------------------------------------------------

def test_engine_is_a_node_in_the_atlas():
    """Motoren skal staa som node i regime_nodes.jsonld — ikke bare i koden."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert "efc.water_phase_engine" in ids


def test_engine_carries_the_phase_nodes():
    """Motoren baerer fasegrense-beregningen for de tre fasene (CARRIES)."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("efc.water_phase_engine", "CARRIES", "h2o.solid") in preds
    assert ("efc.water_phase_engine", "CARRIES", "h2o.liquid") in preds
    assert ("efc.water_phase_engine", "CARRIES", "h2o.gas") in preds


# --------------------------------------------------------------------------
# Maskinell tallkonsistens motor <-> atlas (empati-porten)
# --------------------------------------------------------------------------
#
# Reviewfunn 2026-09-17 (trinn 4): den forrige testen var en
# substring-test — den sa at broen var «maskinelt verifisert» mens den
# bare lette etter tekstbiter. Denne bolken sammenligner TALL: motorens
# deklarerte grenser mot h2o-nodenes tall, begge veier, og motorens
# eget atlas-node mot regime_node(). «50 K» og «50.0» er samme grense;
# «50» som en del av «IAPWS R14-08» er en referanse og hoppes over.

# Kurvenavn i motorens deklarasjon -> h2o-nodene grensen gjelder for.
GRENSE_TIL_NODER = {
    "damp": ("h2o.liquid", "h2o.gas"),
    "smelte": ("h2o.solid",),
    "sublimasjon": ("h2o.solid",),
}

# Tall med enhet («50 K», «208.566 MPa», «101325 Pa») — ikke prosa-tall.
_TALL_MED_ENHET = re.compile(r"(\d+(?:[.,]\d+)?)\s*(K|MPa|Pa)\b")
_GRENSE = re.compile(r"(damp|smelte|sublimasjon)\s*\[([^\]]+)\]")


def _tall(tekst: str) -> list:
    return [float(t.replace(",", "."))
            for t in re.findall(r"\d+(?:[.,]\d+)?", tekst)]


def _har(tall: float, kandidater: list) -> bool:
    """Numerisk likhet — atlasets «50» og motorens «50.0» er samme grense."""
    return any(abs(tall - k) <= 1e-9 * max(1.0, abs(tall)) for k in kandidater)


def _grenser(validity: str) -> dict:
    """Motorens deklarerte grenser, per kurvenavn, som tall.

    Grensen kan vaere skrevet med et symbol («t_triple»); symbolet er
    parameterens navn og verdien ligger i PARAMS — her leses bare tallene.
    """
    return {navn: _tall(kropp) for navn, kropp in _GRENSE.findall(validity)}


def test_engine_declaration_carries_the_three_machine_readable_limits():
    """Deklarasjonen maa ha alle tre grensene som TALL — ellers ville
    testene under vaert tomme (og broen «verifisert» uten innhold)."""
    grenser = _grenser(
        WaterPhaseEngine().regime_node(PARAMS)["regime"]["validity"])
    assert set(grenser) == set(GRENSE_TIL_NODER)
    for navn, tall in grenser.items():
        assert tall, f"{navn}: ingen tall i grensen"


def test_engine_declared_limits_are_the_atlas_nodes_limits():
    """FOROVER: hver grense motoren deklarerer skal finnes som TALL i
    validity-teksten til h2o-noden den gjelder for.

    Unntak: 0 MPa — den naturlige nullen, som atlaset ikke siterer.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    grenser = _grenser(node["regime"]["validity"])
    h2o = {n["id"]: n for n in _instance()["nodes"]}
    for navn, noder in GRENSE_TIL_NODER.items():
        for tall in grenser[navn]:
            if tall == 0.0:
                continue
            for nid in noder:
                assert _har(tall, _tall(h2o[nid]["regime"]["validity"])), (
                    f"motoren deklarerer {tall} i «{navn}», men {nid} "
                    f"nevner den ikke: {h2o[nid]['regime']['validity']}")


def test_atlas_node_numbers_are_numbers_the_engine_holds():
    """BAKOVER: hvert tall MED ENHET i h2o-nodenes validity skal motoren
    kunne gjenskape — fra en deklarert grense eller fra en parameter.
    Et tall atlaset siterer og motoren ikke holder, er en loes påstand.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    grenser = _grenser(node["regime"]["validity"])
    motorens = [t for tall in grenser.values() for t in tall] + [
        float(v) for v in PARAMS.values()]
    h2o = {n["id"]: n for n in _instance()["nodes"]}
    for navn, noder in GRENSE_TIL_NODER.items():
        for nid in noder:
            for raa, enhet in _TALL_MED_ENHET.findall(
                    h2o[nid]["regime"]["validity"]):
                verdi = float(raa.replace(",", "."))
                assert _har(verdi, motorens), (
                    f"{nid} siterer {verdi} {enhet}, men motoren holder "
                    f"ikke det tallet (grenser: {grenser})")


def test_engine_node_and_its_atlas_node_agree_on_derived_fields():
    """Motorens EGET atlas-node skal baere de samme parameteravledede
    feltene som regime_node() gir — samme krav som trinn 11 stiller til
    de fem kosmologiske motorene (test_broer_matcher_atlas_maskinelt).

    Maalt 2026-09-17: vann-noden feilet kravet — atlasets validity var en
    ELDRE tekst enn motorens (motoren ble skjerpet i review 2026-09-16 og
    atlaset ble ikke regenerert). Regenerering:
    scripts/maintenance/efc_bro_synk.py.

    Bare de avledede tekstfeltene sjekkes her. Resten av noden — nivaa,
    epistemikk/sosial_mekanisme, maale_paradigme/koordinater,
    stipulasjoner, buss_domene — har avvik i BEGGE retninger mellom motor
    og atlas (maalt i samme audit), og konvensjonen maa vedtas én gang for
    alle noder; det ligger i eget kort, ikke her.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    atlas = {n["id"]: n for n in _instance()["nodes"]}["efc.water_phase_engine"]
    assert atlas["regime"]["validity"] == node["regime"]["validity"]
    assert atlas["regime"]["law_form"] == node["regime"]["law_form"]


def test_engine_regime_node_reflects_effective_params():
    """Review runde 1: selvbeskrivelsen skal DERIVERES fra de effektive
    parametrene — med alternative parametre skal noden deklarere de
    alternative grensene, ikke de kanoniske."""
    alt = {
        **PARAMS,
        "t_vap_ref": 370.0,
        "p_ice_ih_max": 123.0e6,
        "t_sublim_min": 60.0,
        "watson_exponent": 0.5,
    }
    node = WaterPhaseEngine().regime_node(alt)
    tekst = node["regime"]["validity"] + node["regime"]["law_form"]
    assert "370" in tekst          # t_vap_ref er med
    assert "123" in tekst          # p_ice_ih_max er med (i MPa)
    assert "60" in tekst           # t_sublim_min er med
    assert "0.5" in tekst          # watson-eksponenten er med
    # ...og de kanoniske tallene skal IKKE staa der.
    assert "373.15" not in tekst
    assert "208.566" not in tekst
    assert "0.33" not in tekst
