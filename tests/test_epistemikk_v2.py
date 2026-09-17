"""Tests for epistemikk v2 — the structural closures.

Based on three independent lenses (Claude Opus 5 second opinion +
coverage audit + gap audit, 2026-09-17). Every gap is closed
as a VERIFIABLE INVARIANT, not as free text:

1. Self-application: the atlas and the schema must be nodes in the atlas —
   `efc.selv.atlas` and `efc.selv.skjema` exist, and
   `efc.selv.paradigme_tid` et al. turn (d) into nodes.
2. Stipulation explicitness: the engines' thresholds must be able to be
   declared in the node with `stipulert_av_oss: true` — and a node can
   refer to the engine that holds the threshold.
3. Falsification condition: every node MUST have taken a position — a
   falsifier (`ville_falsifisere`), a fixed
   `falsifiserbarhet` status, or a written reason
   (`stipulasjoner.ikke_falsifiserbar_grunn`). «Can carry» was the fault:
   the field was optional, and measured 2026-09-18, 82 of 113 nodes
   answered neither yes nor no. `revisjon` is the log of changed
   thresholds/assumptions.
4. The observer in the system: `observer.er_del_av_systemet` is
   MANDATORY and must be true for all nodes — we are
   the measuring instrument, not a god outside.
5. Analogy vs causality: `analogi` with `bryter_der` (disanalogy)
   is mandatory when the node declares an analogy.
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


def test_selvanvendelse_nodene_finnes():
    """The atlas, the schema and the base paradigms are nodes in the atlas."""
    atlas = _atlas()
    noder = {n["id"] for n in atlas["nodes"]}
    for krevd in ("efc.selv.atlas", "efc.selv.skjema",
                  "efc.selv.paradigme_tid", "efc.selv.paradigme_masse"):
        assert krevd in noder, krevd


def test_observer_er_del_av_systemet_obligatorisk():
    skjema = _skjema()
    obs = skjema["$defs"]["RegimeNode"]["properties"]["observer"]
    assert "er_del_av_systemet" in obs.get("required", []), \
        "observer.er_del_av_systemet must be required"
    assert obs["properties"]["er_del_av_systemet"].get("const") is True, \
        "er_del_av_systemet must be const true — we are the instrument"


def test_alle_noder_sier_observeren_er_i_systemet():
    for n in _atlas()["nodes"]:
        assert n["observer"]["er_del_av_systemet"] is True, n["id"]


def test_stipulasjonsfeltet_finnes():
    skjema = _skjema()
    node = skjema["$defs"]["RegimeNode"]
    assert "stipulasjoner" in node["properties"]
    sti = node["properties"]["stipulasjoner"]
    assert "stipulert_av_oss" in sti.get("required", [])


def test_selv_nodene_er_agnostiske_eller_paradigme():
    """The efc.selv.* nodes are our own framework's — paradigm; they are not
    consensus and not academia."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.selv."):
            assert n["perspektiv"] in ("paradigme", "agnostikk"), n["id"]


def test_ingen_node_uten_terskel_deklarasjon():
    """Review requirement (PR #444 r1): stipulasjoner.terskler must be
    filled with a value/source OR an explicit declaration — never an empty
    mask."""
    for n in _atlas()["nodes"]:
        terskler = n["stipulasjoner"]["terskler"]
        assert terskler, (
            f"{n['id']}: empty threshold list — populate it or declare "
            f"explicitly that the node has no thresholds")


def test_motor_nodene_har_motor_referanse():
    """The efc.* engine nodes must point at the engine that holds the threshold."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.") and "_engine" in n["id"]:
            assert n["stipulasjoner"].get("motor"), (
                f"{n['id']}: missing engine reference in stipulasjoner")


def test_skjemaet_kjenner_falsifiseringsavgjorelsen():
    """The field shall be DECLARED, and an empty string shall not count as an
    answer.

    The schema cannot REQUIRE the answer. The third answer lives inside
    `stipulasjoner`, and JSON Schema cannot require a named field in a
    sub-object from its parent without a subschema with `properties` — which
    the C10 gate (`efc_schema_check.py`) then reports as «open», because it
    does not distinguish «describes an object» from «imposes a requirement on
    one field». Measured 2026-09-18 (card t_c11ffa45), with the requirement
    attempted on both RegimeNode and a separate AtlasNode:

        schema at /$defs/AtlasNode/allOf[1]/oneOf[2] is open

    The requirement is therefore held as for
    `buss_status`/`motor_status`/`alene_status` (#511/#513/#515, the same
    pattern): `test_atlas_avgjorelse.py` measures that someone HAS answered,
    `test_atlas_motsigelse.py` that only ONE has answered. The schema says
    what CAN be written — with minLength 1, so an empty string is never an
    answer.
    """
    node = _skjema()["$defs"]["RegimeNode"]
    vf = node["properties"].get("ville_falsifisere")
    assert vf, "the schema does not know ville_falsifisere"
    assert vf.get("minLength") == 1, (
        "without minLength an empty string is a valid answer in the schema")
    st = node["properties"]["stipulasjoner"]["properties"]
    assert "ikke_falsifiserbar_grunn" in st, (
        "stipulasjoner does not know the reason — then there is nowhere to write it")
    assert st["ikke_falsifiserbar_grunn"].get("minLength") == 1, (
        "without minLength an empty reason is a valid answer in the schema")


def test_falsifiseringsbetingelsen_er_dekket_ikke_bare_mulig():
    """Counts nodes that CARRY a decision — not nodes that CAN carry one.

    127 of 127 (was 113 before the 13 new nodes came, and 126 on 2026-09-21
    before the quantum-info node). The field must be
    present, also when the answer is no: a node without an answer does not
    answer, and an answer that does not exist cannot be read.
    """
    noder = _atlas()["nodes"]
    uten = [n["id"] for n in noder
            if not (n.get("ville_falsifisere") or n.get("falsifiserbarhet")
                    or (n.get("stipulasjoner") or {})
                    .get("ikke_falsifiserbar_grunn"))]
    assert not uten, (
        f"{len(uten)} of {len(noder)} node(s) have not taken a position: {uten[:8]}")
    assert len(noder) - len(uten) == 127, (
        f"coverage must be 127 of 127 (the atlas grew from 113 on 2026-09-19 and 126 on 2026-09-21; every new node answered), is {len(noder) - len(uten)}")
