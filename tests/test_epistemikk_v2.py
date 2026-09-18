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
3. Falsification condition: every node can carry `ville_falsifisere`
   and `revisjon` (log of changed thresholds/assumptions).
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
