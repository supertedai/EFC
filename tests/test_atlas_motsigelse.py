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


# --- Falsifiserbarhet: en avgjoerelse staar alene (kort t_c11ffa45) ---------
#
# Samme regel som over, for det paret som ble maalt 2026-09-18: 82 av 113
# noder svarte ikke paa om de kunne felles. Naa svarer de — med en
# falsifikator eller med en skriftlig grunn. Den som har BEGGE sier to ting
# samtidig, og det er den samme feilen som #514: leseren faar ett svar uten
# aa vite at det finnes et annet.

def test_ville_falsifisere_og_ikke_falsifiserbar_grunn_utelukker_hverandre(
        noder: list[dict]) -> None:
    """Kan noden felles, skal den ikke samtidig si at den ikke kan det."""
    begge = [n["id"] for n in noder
             if n.get("ville_falsifisere") and n.get("ikke_falsifiserbar_grunn")]
    assert not begge, (
        f"{len(begge)} node(r) har BEGGE: en falsifikator og en grunn til aa "
        f"ikke ha en. En avgjoerelse staar alene: {begge[:6]}")


def test_en_tom_verdi_er_ikke_en_avgjoerelse(noder: list[dict]) -> None:
    """«Kan ikke felles» er et svar; en tom streng er en utelatelse.

    Samme regel som `test_statusene_sier_noe_om_hvorfor` over: feltet skal
    vaere FYLT eller FRAVAERENDE, aldri fylt med ingenting. En tom streng
    tilfredsstiller «feltet finnes» og svarer ikke paa spoersmaalet — det er
    noeyaktig feilklassen `test_falsifiserbarhet.py` har felt tre ganger.
    """
    tomme = [f"{n['id']}.{felt}"
             for n in noder
             for felt in ("ville_falsifisere", "ikke_falsifiserbar_grunn")
             if felt in n and not str(n[felt]).strip()]
    assert not tomme, f"tomme avgjoerelser: {tomme[:6]}"
