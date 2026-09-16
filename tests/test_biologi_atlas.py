"""Tester for den første biologiske atlas-seksjonen (L-007).

Biologien plasseres i koordinatene med samme disiplin som resten:
analogi-merking (ikke identitet), fysiologisk presisjon, og
rammeverkets hypoteser kvalifisert som hypoteser.
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
    raise AssertionError(f"{navn} mangler i atlaset")


def test_bio_nodene_finnes_og_har_regime():
    for navn in BIO_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_genregulering_er_analogi_merket():
    """Genregulering som regime-bryter er ANALOGI til atlasets andre
    brytere — ikke identitet, og ikke en påstand om at genomet ER et
    EFC-regime uten videre."""
    node = _node("homo.genregulering")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "analogi" in tekst


def test_cellesyklus_har_sjekkpunkter():
    """Cellesyklusens kontrollpunkter (G1/S, G2/M) er den faktiske
    reguleringen — noden skal navngi dem."""
    node = _node("homo.cellesyklus")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "G1" in tekst and "G2" in tekst and "M" in tekst


def test_metabolisme_har_atp_loop():
    """Metabolismens ATP-syklus er energiflytens biokjemi — lovformen
    skal vise sykelen, ikke bare navnet."""
    node = _node("homo.metabolisme")
    tekst = json.dumps(node, ensure_ascii=False)
    assert "ATP" in tekst


def test_bio_nodene_tilfredsstiller_skjemaet():
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    for navn in BIO_NODER:
        feil = sorted(validator.iter_errors(_node(navn)),
                      key=lambda e: list(e.path))
        assert not feil, f"{navn}: {[e.message for e in feil[:3]]}"


def test_biologi_koblet_til_homo_fluxus():
    """Den biologiske seksjonen skal henge på homo.fluxus — mennesket
    er bæreren av cellene, ikke omvendt."""
    relasjoner = _atlas().get("relations", [])
    funnet = [
        r for r in relasjoner
        if r["object"] == "homo.fluxus" and
        r["subject"] in BIO_NODER
    ]
    assert funnet, "biologiske noder mangler relasjon til homo.fluxus"
