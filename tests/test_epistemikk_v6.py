"""Tester for epistemikk v6 — rekursjonen som STRUKTUR (krav b).

Tre-linsers-granskingen: «fractal er en påstand om rekursjon i én
streng, ikke en rekursiv struktur. Skjemaet er flatt.»

nivaa-feltet gjør platåene til en graf:
- indeks: hvilket platå noden er på (0 = substrat, økende = mer
  emergert)
- forelder: node-id-en til platået under — eller null for roten
- tidsskala / lengdeskala: platåets karakteristiske mål

Validator-kravene:
- alle noder har nivaa
- forelder peker på en eksisterende node eller er null
- ingen selv-forelder (syklus på ett trinn)
- h2o-kjeden er sammenhengende (molekyl -> dråpe -> hav -> klima)
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
    """Grafen skal være lukket — forelder er en ekte node eller null."""
    atlas = _atlas()
    noder = {n["id"] for n in atlas["nodes"]}
    for n in atlas["nodes"]:
        forelder = n["nivaa"]["forelder"]
        assert forelder is None or forelder in noder, (
            f"{n['id']}: forelder {forelder!r} finnes ikke")


def test_ingen_selv_forelder():
    for n in _atlas()["nodes"]:
        assert n["nivaa"]["forelder"] != n["id"], n["id"]


def test_h2o_kjeden_er_sammenhengende():
    """Molekyl -> dråpe -> hav -> klima skal danne en faktisk
    forelder-barn-kjede i grafen — ikke bare i prosaen."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for barn, forelder in (
        ("h2o.droplet", "h2o.liquid"),
        ("efc.water_phase_engine", "h2o.liquid"),
    ):
        assert noder[barn]["nivaa"]["forelder"] == forelder, barn
