"""MOTSTRIDEN: en node skal ikke si to motsatte ting samtidig.

Maalt 2026-09-18, etter #514: alle 12 homo-noder hadde BEGGE —
`buss_domene: verden.helse` OG `buss_status: «ingen buss-vei — emnet
finnes ikke som domene i snapshotet»`. Feltet ble satt, den gamle
statusen sto igjen, og begge var lesbare.

Det er verre enn et tomt felt. Et tomt felt sier «ikke avgjort».
To motstridende svar sier at atlaset ikke vet hva det selv mener — og
en leser som bare ser det ene, faar svar uten aa vite at det finnes et
annet.

Regelen: naar feltet er satt, skal statusen bort. En avgjorelse staar
alene.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
NODER = ROT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def noder() -> list[dict]:
    return json.loads(NODER.read_text(encoding="utf-8"))["nodes"]


def test_buss_domene_og_buss_status_utelukker_hverandre(noder: list[dict]) -> None:
    """Har noden en buss, skal den ikke samtidig ha en «ingen buss»-status."""
    begge = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        if n.get("buss_domene") and s.get("buss_status"):
            begge.append(n["id"])
    assert not begge, (
        f"{len(begge)} node(r) har BEGGE: buss_domene og buss_status. "
        f"Naar feltet er satt, skal statusen bort: {begge[:6]}")


def test_motor_og_motor_status_utelukker_hverandre(noder: list[dict]) -> None:
    """Det samme for motoren."""
    begge = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        if s.get("motor") and s.get("motor_status"):
            begge.append(n["id"])
    assert not begge, (
        f"{len(begge)} node(r) har BEGGE: motor og motor_status: {begge[:6]}")


def test_ingen_status_sier_imot_sitt_eget_felt(noder: list[dict]) -> None:
    """Den direkte motsigelsen: feltet sier ja, statusen sier nei."""
    motsigelser = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        b = n.get("buss_domene")
        st = (s.get("buss_status") or "").lower()
        if b and ("ingen buss" in st or "ikke som domene" in st):
            motsigelser.append(n["id"])
    assert not motsigelser, (
        f"{len(motsigelser)} node(r) sier baade at de HAR en buss og at de "
        f"IKKE har det: {motsigelser[:6]}")
