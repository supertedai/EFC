"""Tester for den andre biologiske atlas-seksjonen (L-032).

Immunologi, nevrobiologi, økologi og evolusjon — med samme disiplin:
analogi-merking, fysiologisk presisjon, hypoteser kvalifisert.
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
    raise AssertionError(f"{navn} mangler i atlaset")


def test_bio2_nodene_finnes_og_har_regime():
    for navn in BIO2_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_immunologi_har_aktiveringsterskel():
    """Immunresponsen er terskelstyrt — aktiveringsterskler og
    hukommelse skal sta i noden."""
    node = _node("homo.immunologi")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "threshold" in tekst.lower()
    assert "memory" in tekst.lower()


def test_sovn_vaaken_er_regimeskifte():
    """Søvn/våken er et ekte regimeskifte i hjernen — noden skal
    navngi begge regimene og overgangen."""
    node = _node("homo.sovn_vaaken")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "søvn" in tekst.lower() or "sovn" in tekst.lower()
    assert "våken" in tekst.lower() or "vaaken" in tekst.lower()


def test_okologi_har_vippepunkt():
    """Økosystemer har alternative stabile tilstander og vippepunkter —
    noden skal si det med den ærlige usikkerheten som hører til."""
    node = _node("homo.okologi")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "vippe" in tekst or "alternativ" in tekst


def test_evolusjon_er_punktuert_likevekt():
    """Punktuert likevekt (stasis -> raske endringer) er holding->
    release i evolusjonstid — noden skal kalle den formen ved navn."""
    node = _node("homo.evolusjon")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "stasis" in tekst or "punktuert" in tekst or \
           "holding" in tekst


def test_bio2_nodene_tilfredsstiller_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
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
    assert funnet, "biologiske noder mangler relasjon til homo.fluxus"


def test_analogi_merking_i_bio2():
    """Hver bio2-node skal eksplisitt merke analogiene som ANALOGI —
    ikke identitet."""
    for navn in BIO2_NODER:
        node = _node(navn)
        tekst = json.dumps(node, ensure_ascii=False).lower()
        assert "analogi" in tekst, f"{navn} mangler analogi-merking"
