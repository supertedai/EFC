"""Tester for epistemikk v4 — koordinat-paradigmene (krav d).

Mortens prinsipp (d): tid, rom, masse og hastighet er SELV
paradigmer — valgte koordinater, ikke noe gitt. De tre uavhengige
linsene fant at SI-størrelsene brukes rå i motorene uten ontologisk
status.

maale_paradigme-feltet krever at hver node deklarerer:
- koordinater: hvilke koordinat-valg den står på (tid, rom, masse,
  temperatur, energi, elektrisk potensial, magnetfelt, fraksjon)
- enheter: hvilke enheter den måler i
- status: valgt_ramme / avledet / direkte_observerbar / proxy
- alternativer: hvilke alternative beskrivelser som er utelatt
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
    """efc.selv.paradigme_tid skal ha tid som sitt KOORDINAT — ikke
    bruke det som gitt."""
    for n in _atlas()["nodes"]:
        if n["id"] == "efc.selv.paradigme_tid":
            assert "tid" in n["maale_paradigme"]["koordinater"], n["id"]
        if n["id"] == "efc.selv.paradigme_masse":
            assert "masse" in n["maale_paradigme"]["koordinater"], n["id"]


def test_motor_noder_deklarerer_sine_koordinater():
    """Motornoder skal deklarere koordinatene de antar — ikke stå
    uten deklarasjon."""
    forventet = {
        "efc.orbital_engine": ("rom", "masse", "tid"),
        "efc.water_phase_engine": ("temperatur",),
        "efc.romvaer_engine": ("magnetfelt", "tid"),
    }
    for n in _atlas()["nodes"]:
        if n["id"] in forventet:
            for koord in forventet[n["id"]]:
                assert koord in n["maale_paradigme"]["koordinater"], (
                    f"{n['id']}: mangler {koord}")
