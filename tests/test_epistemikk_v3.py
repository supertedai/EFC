"""Tester for epistemikk v3 — ortogonaliteten og analogi-disiplinen.

De to gjenværende strukturelle hullene fra tre-linsers-granskingen:

1. EPISTEMIKK-ORTOGONALITET (Claudes skarpeste kritikk): perspektiv-
   feltet blander «hvem står vi i» med «hvor sann er påstanden».
   Konsensus er et SOSIALT fenomen — sannhetsstatus og konsensus-
   status skal være ADSKILTE akser, og det skal stå eksplisitt at
   konsensus ikke er sannhet.
2. ANALOGI-DISIPLIN: noder som erklærer ANALOGOUS_TO-relasjoner
   skal bære analogi-feltet med eksplisitt avbildning OG disanalogi
   (hvor brekker analogien) — ellers herdes analogi til ontologi.

Begge er required i RegimeNode — ingen node uten epistemisk
regnskap.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _skjema() -> dict:
    return json.loads(SKJEMA.read_text(encoding="utf-8"))


def test_epistemikk_feltet_finnes_og_er_required():
    skjema = _skjema()
    node = skjema["$defs"]["RegimeNode"]
    assert "epistemikk" in node["properties"]
    assert "epistemikk" in node.get("required", [])
    epi = node["properties"]["epistemikk"]
    for felt in ("sannhetsstatus", "evidensstatus", "konsensusstatus",
                 "sosial_mekanisme"):
        assert felt in epi.get("required", []), felt


def test_konsensus_er_ikke_sannhet_er_konst():
    epi = _skjema()["$defs"]["RegimeNode"]["properties"]["epistemikk"]
    assert epi["properties"]["konsensus_er_ikke_sannhet"].get(
        "const") is True, "konsensus_er_ikke_sannhet skal være konst sann"


def test_alle_noder_har_epistemikk():
    for n in _atlas()["nodes"]:
        assert "epistemikk" in n, n["id"]
        assert n["epistemikk"]["konsensus_er_ikke_sannhet"] is True, n["id"]


def test_konsensus_noder_har_sosial_mekanisme():
    """Noder merket konsensus skal beskrive den sosiale mekanismen —
    ikke bare stå med etiketten."""
    for n in _atlas()["nodes"]:
        if n["perspektiv"] == "konsensus":
            assert n["epistemikk"]["sosial_mekanisme"], (
                f"{n['id']}: konsensus-node uten sosial mekanisme")


def test_analogiske_noder_har_disanalogi():
    """ANALOGOUS_TO-relasjonen krever analogi-feltet med BÅDE avbildning
    og disanalogi (review-krav: begge er obligatoriske)."""
    atlas = _atlas()
    analogiske = {r["subject"] for r in atlas.get("relations", [])
                  if r.get("predicate") == "ANALOGOUS_TO"}
    for n in atlas["nodes"]:
        if n["id"] in analogiske:
            assert "analogi" in n, (
                f"{n['id']}: ANALOGOUS_TO uten analogi-felt")
            assert n["analogi"]["avbildning"], (
                f"{n['id']}: avbildningen mangler")
            assert n["analogi"]["bryter_der"], (
                f"{n['id']}: disanalogi mangler — analogien er udisiplinert")


def test_analogi_feltene_er_required_i_skjema():
    """analogi.required skal kreve begge feltene (review-krav PR #445 r1)."""
    analogi = _skjema()["$defs"]["RegimeNode"]["properties"]["analogi"]
    assert set(analogi.get("required", [])) == {"avbildning", "bryter_der"}


def test_konsensus_mekanismer_er_individualiserte():
    """Ingen to konsensus-noder skal dele sosial_mekanisme-tekst —
    malbasert fylling er en falsk sporbarhet (review-krav)."""
    tekster = [n["epistemikk"]["sosial_mekanisme"] for n in _atlas()["nodes"]
               if n["perspektiv"] == "konsensus"]
    assert len(tekster) == len(set(tekster)), (
        "dupliserte sosial_mekanisme-tekster blant konsensus-nodene")


def test_epistemikk_statusene_er_gyldige_enum():
    epi = _skjema()["$defs"]["RegimeNode"]["properties"]["epistemikk"]
    for felt, forventet in (
        ("sannhetsstatus", {"uavklart", "hypotese", "modellrelativ",
                            "stottet", "motbevist"}),
        ("evidensstatus", {"ingen", "proxy", "direkte", "uavhengig",
                           "replikert"}),
        ("konsensusstatus", {"ingen", "minoritet", "omstridt",
                             "institusjonell", "bred"}),
    ):
        assert set(epi["properties"][felt]["enum"]) == forventet, felt
