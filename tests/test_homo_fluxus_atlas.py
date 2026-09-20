"""Tester for Homo Fluxus-nodene i atlaset (L-006).

Homo Fluxus (repoets eget rammeverk, DOI 32099389/31940604) skal
plasseres i atlaset som noder — menneskets regimer i EFC-koordinatene,
med den brede bufferlogikken eksplisitt merket som ANALOGI (ikke
identitet) til batteri og vann, i tråd med resten av atlaset.
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

HOMO_NODER = [
    "homo.fluxus",
    "homo.homeostase_buffer",
    "homo.feber_regime",
    "homo.aksjonspotensial",
    "homo.hjerte_syklus",
]


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(navn: str) -> dict:
    for n in _atlas()["nodes"]:
        if n["id"] == navn:
            return n
    raise AssertionError(f"{navn} mangler i atlaset")


def test_homo_nodene_finnes():
    for navn in HOMO_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_rc_terskelen_staar_med_verdi():
    """R_c ≈ 1/e ≈ 0.37 — terskelen mellom flytobjekt og flytsubjekt —
    skal stå med sin verdi i atlaset."""
    node = _node("homo.fluxus")
    assert "0.37" in node["regime"]["validity"] or \
           "1/e" in node["regime"]["validity"]


def test_analogi_merking_til_batteri():
    """Homeostase-bufferen er den brede bufferlogikken i kroppen —
    ANALOGI til batteriet, ikke identitet. Det skal stå eksplisitt."""
    node = _node("homo.homeostase_buffer")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "battery" in tekst
    assert "analogi" in tekst


def test_aksjonspotensialet_er_holding_release():
    """Nevronets membranpotensial lades og utløses — holding→release,
    samme form som flares og jordskjelv (analogi-merket)."""
    node = _node("homo.aksjonspotensial")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert ("holding" in tekst and "release" in tekst) or \
           ("lad" in tekst and "utløs" in tekst)


def test_nodene_tilfredsstiller_skjemaet():
    """Alle homo-nodene skal være gyldige RegimeNodes."""
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    for navn in HOMO_NODER:
        feil = sorted(validator.iter_errors(_node(navn)),
                      key=lambda e: list(e.path))
        assert not feil, f"{navn}: {[e.message for e in feil[:3]]}"


def test_relasjon_analogi_til_batteri_buffer():
    """Relasjonen homo.homeostase_buffer ↔ batteri.buffer skal finnes
    med et analogi-predikat (ikke COUPLED_TO — det ville vært for
    sterkt)."""
    relasjoner = _atlas().get("relations", [])
    funnet = [
        r for r in relasjoner
        if (r["subject"] == "homo.homeostase_buffer" and
            r["object"] == "batteri.buffer")
        or (r["subject"] == "batteri.buffer" and
            r["object"] == "homo.homeostase_buffer")
    ]
    assert funnet, "analogi-relasjonen til batteri.buffer mangler"
    for r in funnet:
        assert r["predicate"] in ("ANALOGOUS_TO", "ANALOGI_TIL")
