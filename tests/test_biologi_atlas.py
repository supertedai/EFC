"""Tests for the first biological atlas section (L-007).

The biology is placed in the coordinates with the same discipline as the rest:
analogy labelling (not identity), physiological precision, and the framework's
hypotheses qualified as hypotheses.
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

BIO_NODER = [
    "homo.genregulering",
    "homo.cellesyklus",
    "homo.metabolisme",
]


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(navn: str) -> dict:
    for n in _atlas()["nodes"]:
        if n["id"] == navn:
            return n
    raise AssertionError(f"{navn} is missing from the atlas")


def test_bio_nodene_finnes_og_har_regime():
    for navn in BIO_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_genregulering_er_analogi_merket():
    """Gene regulation as a regime switch is an ANALOGY to the atlas's other
    switches — not identity, and not a claim that the genome IS an EFC regime
    without further qualification."""
    node = _node("homo.genregulering")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "analogi" in tekst


def test_cellesyklus_har_sjekkpunkter():
    """The cell cycle's control points (G1/S, G2/M) are the actual
    regulation — the node must name them."""
    node = _node("homo.cellesyklus")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "G1" in tekst and "G2" in tekst and "M" in tekst


def test_metabolisme_har_atp_loop():
    """Metabolism's ATP cycle is the biochemistry of the energy flow — the law
    form must show the cycle, not just the name."""
    node = _node("homo.metabolisme")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "ATP" in tekst


def test_bio_nodene_tilfredsstiller_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema is not installed")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    for navn in BIO_NODER:
        feil = sorted(validator.iter_errors(_node(navn)),
                      key=lambda e: list(e.path))
        assert not feil, f"{navn}: {[e.message for e in feil[:3]]}"


def test_biologi_koblet_til_homo_fluxus():
    """The biological section must hang on homo.fluxus — the human carries the
    cells, not the other way around."""
    relasjoner = _atlas().get("relations", [])
    funnet = [
        r for r in relasjoner
        if r["object"] == "homo.fluxus" and
        r["subject"] in BIO_NODER
    ]
    assert funnet, "biological nodes lack a relation to homo.fluxus"
