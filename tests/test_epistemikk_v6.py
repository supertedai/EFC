"""Tests for epistemology v6 — recursion as STRUCTURE (requirement b).

The three-liner review: "fractal is a claim about recursion in one string, not
a recursive structure. The schema is flat."

The nivaa field turns the plateaus into a graph:
- indeks: which plateau the node is on (0 = substrate, increasing = more
  emerged)
- forelder: the node id of the plateau below — or null for the root
- tidsskala / lengdeskala: the plateau's characteristic scale

The validator requirements:
- all nodes have nivaa
- forelder points at an existing node or is null
- no self-forelder (a cycle of one step)
- the h2o chain is connected (molecule -> droplet -> ocean -> climate)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def test_nivaa_feltet_finnes_og_er_required():
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    node = skjema["$defs"]["RegimeNode"]
    assert "nivaa" in node["properties"]
    assert "nivaa" in node.get("required", [])
    nv = node["properties"]["nivaa"]
    for felt in ("indeks", "forelder", "tidsskala", "lengdeskala"):
        assert felt in nv.get("required", []), felt


def test_alle_noder_har_nivaa():
    for n in _atlas()["nodes"]:
        assert "nivaa" in n, n["id"]
        assert isinstance(n["nivaa"]["indeks"], int), n["id"]


def test_foreldre_peker_paa_eksisterende_noder():
    """The graph must be closed — forelder is a real node or null."""
    atlas = _atlas()
    noder = {n["id"] for n in atlas["nodes"]}
    for n in atlas["nodes"]:
        forelder = n["nivaa"]["forelder"]
        assert forelder is None or forelder in noder, (
            f"{n['id']}: forelder {forelder!r} does not exist")


def test_ingen_selv_forelder():
    for n in _atlas()["nodes"]:
        assert n["nivaa"]["forelder"] != n["id"], n["id"]


def test_h2o_kjeden_er_sammenhengende():
    """Molecule -> droplet -> ocean -> climate must form a real
    parent-child chain in the graph — not just in the prose."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for barn, forelder in (
        ("h2o.droplet", "h2o.liquid"),
        ("efc.water_phase_engine", "h2o.liquid"),
    ):
        assert noder[barn]["nivaa"]["forelder"] == forelder, barn


def test_forelder_har_lavere_indeks():
    """The plateau direction: the parent is the plateau BELOW — its indeks must
    be lower than the child's (review requirement PR #449 r1)."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for n in atlas["nodes"]:
        far = n["nivaa"]["forelder"]
        if far is not None:
            assert noder[far]["nivaa"]["indeks"] < n["nivaa"]["indeks"], (
                f"{n['id']}: forelder {far} has indeks "
                f"{noder[far]['nivaa']['indeks']} >= {n['nivaa']['indeks']}")


def test_grafen_er_asyklisk():
    """DFS from every node — no cycles in the forelder graph."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for start in noder:
        sett = set()
        nid = start
        while nid is not None:
            if nid in sett:
                raise AssertionError(f"cycle from {start}")
            sett.add(nid)
            nid = noder[nid]["nivaa"]["forelder"]


def test_atlas_og_motor_nivaa_stemmer():
    """The society engines' nivaa in the atlas must agree with the engines'
    regime_node() (review requirement: they disagreed).

    The comparison is the WHOLE nivaa block, not just ``forelder``. Measured
    2026-09-18 in t_dd5efeec: the old variant compared only ``forelder``, and a
    mutation of ``indeks`` (1 -> 2) on one of the three engines left the test
    GREEN — while the ``forelder`` mutation was caught. The whole class (all 20
    engines, all fields) is owned by ``tests/test_bro_konvensjon.py``; this test
    covers the three society engines and is deliberately a DOUBLE check, not the
    only one.
    """
    import importlib
    for motor, nid in (("samfunn", "efc.samfunn_engine"),
                       ("oekonomi", "efc.oekonomi_engine"),
                       ("enerflyt", "efc.enerflyt_engine")):
        mod = importlib.import_module(f"efc_inference.engine.{motor}")
        klasser = [k for k in vars(mod).values()
                   if isinstance(k, type) and hasattr(k, "regime_node")
                   and k.__module__ == mod.__name__]
        motor_node = klasser[0]().regime_node({
            "produksjon": 1.0, "forbruk": 1.0, "buffer": 1.0} if motor ==
            "enerflyt" else {"beta": 0.3, "gamma": 0.1, "N": 100.0} if motor ==
            "samfunn" else {"gjeld": 1.0, "inntekt": 1.0, "rente": 0.05,
                            "tillit": 0.06})
        atlas_node = {n["id"]: n for n in _atlas()["nodes"]}[nid]
        assert atlas_node["nivaa"] == motor_node["nivaa"], motor
