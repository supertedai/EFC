"""Tests for epistemikk v4 — the coordinate paradigms (requirement d).

Morten's principle (d): time, space, mass and velocity are THEMSELVES
paradigms — chosen coordinates, not something given. The three independent
lenses found that the SI quantities are used raw in the engines without ontological
status.

The maale_paradigme field requires that every node declares:
- koordinater: which coordinate choices it stands on (time, space, mass,
  temperature, energy, electric potential, magnetic field, fraction)
- enheter: which units it measures in
- status: valgt_ramme / avledet / direkte_observerbar / proxy
- alternativer: which alternative descriptions are omitted
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


def test_maale_paradigme_feltet_finnes_og_er_required():
    skjema = _skjema()
    node = skjema["$defs"]["RegimeNode"]
    assert "maale_paradigme" in node["properties"]
    assert "maale_paradigme" in node.get("required", [])
    mp = node["properties"]["maale_paradigme"]
    for felt in ("koordinater", "enheter", "status"):
        assert felt in mp.get("required", []), felt


def test_alle_noder_deklarerer_maale_paradigme():
    for n in _atlas()["nodes"]:
        assert "maale_paradigme" in n, n["id"]
        assert n["maale_paradigme"]["status"] in (
            "valgt_ramme", "avledet", "direkte_observerbar", "proxy")


def test_paradigme_nodene_har_koordinatet_som_objekt():
    """efc.selv.paradigme_tid shall have tid as its COORDINATE — not
    use it as given."""
    for n in _atlas()["nodes"]:
        if n["id"] == "efc.selv.paradigme_tid":
            assert "tid" in n["maale_paradigme"]["koordinater"], n["id"]
        if n["id"] == "efc.selv.paradigme_masse":
            assert "masse" in n["maale_paradigme"]["koordinater"], n["id"]


def test_motor_noder_deklarerer_sine_koordinater():
    """Engine nodes shall declare the coordinates they assume — not stand
    without a declaration."""
    forventet = {
        "efc.orbital_engine": ("rom", "masse", "tid", "hastighet"),
        "efc.water_phase_engine": ("temperatur",),
        "efc.romvaer_engine": ("magnetfelt", "tid", "hastighet"),
    }
    for n in _atlas()["nodes"]:
        if n["id"] in forventet:
            for koord in forventet[n["id"]]:
                assert koord in n["maale_paradigme"]["koordinater"], (
                    f"{n['id']}: missing {koord}")


def test_hastighet_er_i_enumet():
    """Review requirement (PR #446 r1): the schema declares hastighet as a
    paradigm — the enum must be able to represent it."""
    mp = _skjema()["$defs"]["RegimeNode"]["properties"]["maale_paradigme"]
    enum = mp["properties"]["koordinater"]["items"]["enum"]
    assert "hastighet" in enum
