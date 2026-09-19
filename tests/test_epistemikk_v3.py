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


def test_alle_noder_har_sosial_mekanisme():
    """The field is required in the schema, and it is the precondition for
    the test below: a node without it is invisible to the duplicate check
    (rule 73 — an absent field is not an answer)."""
    mangler = [n["id"] for n in _atlas()["nodes"]
               if not (n["epistemikk"].get("sosial_mekanisme") or "").strip()]
    assert not mangler, f"nodes without sosial_mekanisme: {mangler}"


def test_sosial_mekanisme_er_individualisert():
    """No two nodes may share a sosial_mekanisme text — template filling is
    false traceability, however many nodes share the template (rule 46).

    The guard used to cover ONLY nodes with ``perspektiv == "konsensus"``.
    The engine nodes are ``konsensusstatus: minoritet`` (perspektiv:
    paradigme), so they were outside the guard — and one and the same
    template could stand in 30 nodes (measured 2026-09-18: 20 engine nodes,
    17 with the long template + 3 with the short, plus 27 non-engine nodes in
    those same two templates and 10 h2o/optics nodes in a third). The class
    is the WHOLE population where the field is set: it is the text that is
    false traceability, not the consensus status.
    """
    grupper: dict = {}
    for n in _atlas()["nodes"]:
        tekst = n["epistemikk"]["sosial_mekanisme"]
        grupper.setdefault(tekst, []).append(n["id"])
    delt = {t: ids for t, ids in grupper.items() if len(ids) > 1}
    linjer = "\n".join(f"  {len(ids)}x {t[:80]!r} -> {ids}"
                       for t, ids in delt.items())
    assert not delt, (
        f"{len(delt)} sosial_mekanisme text(s) shared by several nodes "
        f"(template, not individualized):\n{linjer}")


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
