"""Test av det generiske regime-node-skjemaet og H2O-instansen (trinn 2).

TDD: skrives FOER skjemaet finnes — skal feile ved innlesing.

Forankring (skjemaets kanoniske kilde):
  regime/proxy/placement/episenter/compression er definert i
  «Regime-Bound Measurement in Complex Systems: Proxy, Placement, and
  Validity» (DOI 10.6084/m9.figshare.31564123, 2026-03-07) og i
  meta-referansen docs/papers/meta/Proxy/. Mortens utvidelser (maal,
  maaler, maaleinstrument, proxychain, buffer/holding, fase, ontologi,
  observator-baandbredde, emergence-loop, fraktal, lokal-global
  kobling) er strukturelle beholdere — skjemaet hevder ingen fysikk.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

SCHEMA_PATH = _REPO / "schema" / "regime_node.schema.json"
INSTANCE_PATH = _REPO / "schema" / "regime_nodes.jsonld"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema ikke installert")


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _instance() -> dict:
    return json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# Skjemaet
# --------------------------------------------------------------------------

@requires_jsonschema
def test_schema_is_valid_and_closed():
    s = _schema()
    jsonschema.Draft202012Validator.check_schema(s)
    assert s.get("additionalProperties") is False


def test_schema_requires_mortens_node_fields():
    s = _schema()
    node_req = set(s["$defs"]["RegimeNode"]["required"])
    assert {"id", "regime", "phase", "measure", "episenter", "buffer",
            "ontology", "observer", "emergence", "fractal",
            "coupling"} <= node_req


def test_schema_uses_canonical_episenter_spelling():
    """Review runde 1: kanonisk term i kilde-README-en og PR-en er
    «episenter» — det engelske «epicenter» skal ikke vaere feltnavn."""
    s = _schema()
    props = s["$defs"]["RegimeNode"]["properties"]
    assert "episenter" in props
    assert "epicenter" not in props


def test_context_maps_ids_and_relation_targets_to_iris():
    """Review runde 1: instansen skal vaere en lenket JSON-LD-graf —
    node-id-er og relasjonsendepunkter er IRI-referanser, ikke loes tekst."""
    inst = _instance()
    ctx = inst["@context"]
    assert ctx.get("id") == "@id"
    assert ctx.get("subject") == {"@type": "@id"}
    assert ctx.get("object") == {"@type": "@id"}


def test_schema_requires_measurement_chain():
    s = _schema()
    measure = s["$defs"]["RegimeNode"]["properties"]["measure"]
    req = set(measure["required"])
    assert {"target", "measurer", "instrument", "proxy_chain",
            "placement", "compression"} <= req
    pc = measure["properties"]["proxy_chain"]
    assert pc["type"] == "array"


def test_schema_observer_bandwidth_is_explicit():
    """Observatoren ser et vindu av spekteret — baandbredde er et paakrevd
    felt, og bevissthetsstatusen er en deklarert klasse, ikke en pastand."""
    s = _schema()
    obs = s["$defs"]["RegimeNode"]["properties"]["observer"]
    assert {"bandwidth", "awareness"} <= set(obs["required"])
    awareness_enum = obs["properties"]["awareness"]["enum"]
    assert "instrument_window" in awareness_enum
    assert "hypothesis_open" in awareness_enum
    assert "not_claimed" in awareness_enum


def test_schema_relation_predicates_include_transition_and_emergence():
    s = _schema()
    preds = s["$defs"]["RegimeRelation"]["properties"]["predicate"]["enum"]
    assert "TRANSITIONS_TO" in preds
    assert "EMERGES_FROM" in preds
    assert "COUPLED_TO" in preds


# --------------------------------------------------------------------------
# H2O-instansen
# --------------------------------------------------------------------------

@requires_jsonschema
def test_h2o_instance_validates_against_schema():
    jsonschema.Draft202012Validator(_schema()).validate(_instance())


def test_h2o_instance_has_four_phase_nodes():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical"} <= ids


def test_h2o_instance_has_triple_point_node():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert "h2o.triple_point" in ids


def test_h2o_transitions_meet_at_triple_point():
    """De tre faseovergangene skal alle vaere representert — det er det
    trippelpunktet BETYR i denne strukturen."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.liquid") in preds
    assert ("h2o.liquid", "TRANSITIONS_TO", "h2o.gas") in preds
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.gas") in preds


def test_every_node_declares_empathy_coupling():
    """Systemisk empati: hver node maa deklarere sin lokale rolle OG sin
    globale rekkevidde — ingen node er bare lokal."""
    inst = _instance()
    for n in inst["nodes"]:
        c = n["coupling"]
        assert c["local"], n["id"]
        assert c["global"], n["id"]


def test_every_node_has_ontology_source():
    """Ontologiske antakelser skal ha kilde — ikke sveve loest."""
    inst = _instance()
    for n in inst["nodes"]:
        assert n["ontology"]["source"], n["id"]


def test_phase_nodes_declare_regime_validity():
    """Hver fasenode maa si HVOR den gjelder (gyldighetsomraade)."""
    inst = _instance()
    for n in inst["nodes"]:
        if n["id"].startswith("h2o.") and n["id"] != "h2o.triple_point":
            assert n["regime"]["validity"], n["id"]


# --------------------------------------------------------------------------
# Trinn 3: regnbuen — generisitetstesten (en emergence, ikke en fase)
# --------------------------------------------------------------------------

def test_rainbow_nodes_exist():
    """Regnbuen som andre instans: lys, draape, dispersjon, observator."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"lys.sol", "h2o.droplet", "optikk.dispersjon",
            "regnbue", "regnbue.observator"} <= ids


def test_rainbow_emerges_from_droplets_and_light():
    """Regnbuen er en EMERGENCE av draaper + lys — ikke en node ved siden av."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "EMERGES_FROM", "h2o.droplet") in preds
    assert ("regnbue", "EMERGES_FROM", "lys.sol") in preds


def test_rainbow_is_observed_through_observer():
    """Uten observator i anti-solar geometri er det bare spredt lys —
    regnbuen OBSERVED_THROUGH observatoren."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "OBSERVED_THROUGH", "regnbue.observator") in preds


def test_observer_bandwidth_states_visible_window():
    """«Alt er paa et elektrospektrum totalt, observatoeren ser noen faa nm»
    — oeyets vindu (400-700 nm) skal staa i observatorens baandbredde."""
    inst = _instance()
    obs = next(n for n in inst["nodes"] if n["id"] == "regnbue.observator")
    bw = obs["observer"]["bandwidth"]
    assert "400" in bw and "700" in bw


def test_rainbow_is_emergent_pattern_not_phase():
    """Regnbuen er ingen termodynamisk fase — den er et emergert monster.
    Skjemaet maa kunne baere emergences utover faser."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert rb["phase"] == "emergent_pattern"


def test_rainbow_requires_liquid_droplets():
    """Regnbuen krever FLYTENDE (sfaeriske) draaper — iskrystaller gir
    haloer, ikke regnbue. Gyldighetsomraadet maa si det."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert "flytende" in rb["regime"]["validity"].lower()


def test_existing_h2o_nodes_untouched():
    """H2O-nodene fra trinn 2 skal vaere urorte i samme atlas."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical", "h2o.triple_point"} <= ids
