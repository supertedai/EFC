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


def test_forelder_har_lavere_indeks():
    """Platå-retningen: forelderen er platået UNDER — dens indeks skal
    være lavere enn barnets (review-krav PR #449 r1)."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for n in atlas["nodes"]:
        far = n["nivaa"]["forelder"]
        if far is not None:
            assert noder[far]["nivaa"]["indeks"] < n["nivaa"]["indeks"], (
                f"{n['id']}: forelder {far} har indeks "
                f"{noder[far]['nivaa']['indeks']} >= {n['nivaa']['indeks']}")


def test_grafen_er_asyklisk():
    """DFS fra hver node — ingen sykler i forelder-grafen."""
    atlas = _atlas()
    noder = {n["id"]: n for n in atlas["nodes"]}
    for start in noder:
        sett = set()
        nid = start
        while nid is not None:
            if nid in sett:
                raise AssertionError(f"syklus fra {start}")
            sett.add(nid)
            nid = noder[nid]["nivaa"]["forelder"]


def test_atlas_og_motor_nivaa_stemmer():
    """Samfunns-motorenes nivaa i atlaset skal stemme med motorenes
    regime_node() (review-krav: de var uenige).

    Sammenligningen er HELE nivaa-blokken, ikke bare ``forelder``. Maalt
    2026-09-18 i t_dd5efeec: den gamle varianten sammenlignet bare
    ``forelder``, og en mutasjon av ``indeks`` (1 -> 2) paa en av de tre
    motorene lot testen staa GRØNN — mens ``forelder``-mutasjonen ble fanget.
    Hele klassen (alle 20 motorer, alle felt) eies av
    ``tests/test_bro_konvensjon.py``; denne testen dekker de tre
    samfunnsmotorene og er med vilje en DUBBELT kontroll, ikke den eneste.
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
