"""Tests for epistemics v3 — orthogonality and analogy discipline.

The two remaining structural gaps from the three-lens review:

1. EPISTEMICS ORTHOGONALITY (Claude's sharpest criticism): the perspektiv
   field mixes "who we stand in" with "how true is the claim".
   Consensus is a SOCIAL phenomenon — truth status and consensus
   status shall be SEPARATE axes, and it shall stand explicitly that
   consensus is not truth.
2. ANALOGY DISCIPLINE: nodes that declare ANALOGOUS_TO relations
   shall carry the analogi field with an explicit mapping AND a disanalogy
   (where the analogy breaks) — otherwise the analogy hardens into ontology.

Both are required in RegimeNode — no node without epistemic
accounting.
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
        "const") is True, "konsensus_er_ikke_sannhet shall be const true"


def test_alle_noder_har_epistemikk():
    for n in _atlas()["nodes"]:
        assert "epistemikk" in n, n["id"]
        assert n["epistemikk"]["konsensus_er_ikke_sannhet"] is True, n["id"]


def test_konsensus_noder_har_sosial_mekanisme():
    """Nodes marked konsensus shall describe the social mechanism —
    not just stand with the label."""
    for n in _atlas()["nodes"]:
        if n["perspektiv"] == "konsensus":
            assert n["epistemikk"]["sosial_mekanisme"], (
                f"{n['id']}: konsensus node without a social mechanism")


def test_analogiske_noder_har_disanalogi():
    """The ANALOGOUS_TO relation requires the analogi field with BOTH a mapping
    and a disanalogy (review requirement: both are mandatory)."""
    atlas = _atlas()
    analogiske = {r["subject"] for r in atlas.get("relations", [])
                  if r.get("predicate") == "ANALOGOUS_TO"}
    for n in atlas["nodes"]:
        if n["id"] in analogiske:
            assert "analogi" in n, (
                f"{n['id']}: ANALOGOUS_TO without an analogi field")
            assert n["analogi"]["avbildning"], (
                f"{n['id']}: the mapping is missing")
            assert n["analogi"]["bryter_der"], (
                f"{n['id']}: the disanalogy is missing — the analogy is undisciplined")


def test_analogi_feltene_er_required_i_skjema():
    """analogi.required shall require both fields (review requirement PR #445 r1)."""
    analogi = _skjema()["$defs"]["RegimeNode"]["properties"]["analogi"]
    assert set(analogi.get("required", [])) == {"avbildning", "bryter_der"}


def test_konsensus_mekanismer_er_individualiserte():
    """No two konsensus nodes shall share sosial_mekanisme text —
    template-based filling is a false traceability (review requirement)."""
    tekster = [n["epistemikk"]["sosial_mekanisme"] for n in _atlas()["nodes"]
               if n["perspektiv"] == "konsensus"]
    assert len(tekster) == len(set(tekster)), (
        "duplicate sosial_mekanisme texts among the konsensus nodes")


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
