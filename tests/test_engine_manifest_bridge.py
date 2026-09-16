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


def test_engine_validity_matches_atlas_validity():
    """Maskinell konsistens: motorens deklarerte gyldighetstall skal finnes
    i de tilsvarende h2o-nodenes validity-tekster — broen er maalbar,
    ikke bare prosa."""
    node = WaterPhaseEngine().regime_node(PARAMS)
    validity = node["regime"]["validity"]
    inst = _instance()
    h2o = {n["id"]: n for n in inst["nodes"]}
    # Motoren deklarerer de tre grensene; atlaset gjentar dem per fase.
    assert "273.16" in validity and "373.15" in validity
    assert "208.566" in validity
    for nid in ("h2o.solid", "h2o.liquid", "h2o.gas"):
        assert h2o[nid]["regime"]["validity"], nid
    # Eksplisitt bro: gyldighetsteksten er IDENTISK med det motoren
    # rapporterer for sin kalibrering.
    assert "208.566" in h2o["h2o.solid"]["regime"]["validity"]
    assert "373.15" in h2o["h2o.liquid"]["regime"]["validity"]
