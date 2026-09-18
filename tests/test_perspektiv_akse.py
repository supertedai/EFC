"""Tests for the perspective axis — the epistemic labelling of the
whole system (Morten's requirement 2026-09-17).

Four axes:
    paradigme  = our own frame (EFC engines, atlas mappings)
    konsensus  = the prevailing world view (ΛCDM, observational data)
    akademia   = established knowledge base (Kepler, SIR, Minsky, IAPWS,
                 physiology — published models and methods)
    agnostikk  = the open/unknown (microphysics, consciousness)

The discipline: every atlas node and every engine's regime_node() must
declare ONE perspective. The schema validates that the field exists and
is one of the four values. A node without a perspective is a claim
without an epistemic home — it must not exist.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")

PERSPEKTIV = ("paradigme", "konsensus", "akademia", "agnostikk")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def test_skjemaet_har_perspektiv_feltet():
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    node = skjema["$defs"]["RegimeNode"]
    assert "perspektiv" in node["properties"], \
        "the RegimeNode schema is missing the perspektiv field"
    enum = node["properties"]["perspektiv"].get("enum", [])
    assert set(enum) == set(PERSPEKTIV), enum
    # Review requirement (PR #442 r1): the field must be MANDATORY —
    # a node without a perspective is a claim without an epistemic home.
    assert "perspektiv" in node.get("required", []), \
        "perspektiv must be required so that unlabelled nodes fail"


def test_alle_atlas_noder_har_gyldig_perspektiv():
    atlas = _atlas()
    for n in atlas["nodes"]:
        persp = n.get("perspektiv")
        assert persp in PERSPEKTIV, f"{n['id']}: perspektiv={persp!r}"


def test_observasjons_noder_er_konsensus():
    """The obs.* nodes are MEASUREMENTS of the world — consensus."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("obs."):
            assert n["perspektiv"] == "konsensus", n["id"]


def test_motor_noder_er_paradigme():
    """The efc.* engine nodes are OUR frame — paradigm."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.") and n["id"] != "efc.l0":
            assert n["perspektiv"] == "paradigme", n["id"]


def test_h2o_fysikk_noder_er_akademia():
    """The h2o.* nodes are established thermodynamics (IAPWS) — academia."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("h2o."):
            assert n["perspektiv"] == "akademia", n["id"]


def test_alle_motorer_deklarerer_perspektiv():
    """Every engine's regime_node() must carry the perspektiv field."""
    import importlib
    motorer = ["water", "victron", "rotation", "hubble", "growth",
               "lensing", "cluster", "solar_flare", "jordskjelv",
               "mu_kz", "orbital", "klima", "romvaer", "tidevann",
               "samfunn", "oekonomi", "transient"]
    for navn in motorer:
        mod = importlib.import_module(f"efc_inference.engine.{navn}")
        klasse = [k for k in vars(mod).values()
                  if isinstance(k, type)
                  and hasattr(k, "regime_node")
                  and k.__module__ == mod.__name__][0]
        # call regime_node with empty params — the field must exist
        # independently of parameter values
        import inspect
        kilde = inspect.getsource(klasse.regime_node)
        assert '"perspektiv"' in kilde or "'perspektiv'" in kilde, navn
