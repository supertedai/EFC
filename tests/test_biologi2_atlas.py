"""Tests for the second biology atlas section (L-032).

Immunology, neurobiology, ecology and evolution — with the same discipline:
analogy labelling, physiological precision, hypotheses qualified.
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

BIO2_NODER = [
    "homo.immunologi",
    "homo.sovn_vaaken",
    "homo.okologi",
    "homo.evolusjon",
]


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(navn: str) -> dict:
    for n in _atlas()["nodes"]:
        if n["id"] == navn:
            return n
    raise AssertionError(f"{navn} is missing from the atlas")


def test_bio2_nodene_finnes_og_har_regime():
    for navn in BIO2_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_immunologi_har_aktiveringsterskel():
    """The immune response is threshold-driven — activation thresholds and
    memory shall stand in the node."""
    node = _node("homo.immunologi")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "terskel" in tekst.lower()
    assert "hukommelse" in tekst.lower() or "minne" in tekst.lower()


def test_sovn_vaaken_er_regimeskifte():
    """Sleep/wake is a genuine regime shift in the brain — the node shall
    name both regimes and the transition."""
    node = _node("homo.sovn_vaaken")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "søvn" in tekst.lower() or "sovn" in tekst.lower()
    assert "våken" in tekst.lower() or "vaaken" in tekst.lower()


def test_okologi_har_vippepunkt():
    """Ecosystems have alternative stable states and tipping points —
    the node shall say so with the honest uncertainty that belongs to it."""
    node = _node("homo.okologi")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "vippe" in tekst or "alternativ" in tekst


def test_evolusjon_er_punktuert_likevekt():
    """Punctuated equilibrium (stasis -> rapid change) is holding->
    release in evolutionary time — the node shall call that form by name."""
    node = _node("homo.evolusjon")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "stasis" in tekst or "punktuert" in tekst or \
           "holding" in tekst


def test_bio2_nodene_tilfredsstiller_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    for navn in BIO2_NODER:
        feil = sorted(validator.iter_errors(_node(navn)),
                      key=lambda e: list(e.path))
        assert not feil, f"{navn}: {[e.message for e in feil[:3]]}"


def test_bio2_koblet_til_homo_fluxus():
    relasjoner = _atlas().get("relations", [])
    funnet = [
        r for r in relasjoner
        if r["object"] == "homo.fluxus" and r["subject"] in BIO2_NODER
    ]
    assert funnet, "biology nodes are missing a relation to homo.fluxus"


def test_analogi_merking_i_bio2():
    """Every bio2 node shall explicitly label the analogies as ANALOGY —
    not identity."""
    for navn in BIO2_NODER:
        node = _node(navn)
        tekst = json.dumps(node, ensure_ascii=False).lower()
        assert "analogi" in tekst, f"{navn} is missing analogy labelling"
