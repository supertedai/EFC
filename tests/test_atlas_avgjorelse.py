"""AVGJOERELSEN: en node skal ha TATT STILLING, ikke bare utelatt feltet.

Maalt 2026-09-18 (kort t_fc25238b): `plasser()` ble kalt fra ETT sted —
CLI-en selv. Ingen hook, ingen CI. Inngangen fantes og sto ubrukt, og
hver av nattens fire lukkinger endte i samme setning: «jeg maa fortsatt
huske aa gjoere det».

Generatoren har alt to vakter som FELLER: koder (#476) og PLASSERING
(#507). Begge felte sin egen forfatter i natt. Det er malen.

Den tredje vakten er annerledes: den skal ikke kreve at en node er
FERDIG — den skal kreve at VALGET er tatt. En instrument-node trenger
ingen motor. Men den skal si det, ikke tie.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def noder() -> list[dict]:
    d = json.loads(ATLAS.read_text(encoding="utf-8"))
    return d["nodes"]


def test_hver_node_har_tatt_stilling_til_buss_domene(noder: list[dict]) -> None:
    """Enten et domene, eller en skriftlig grunn til aa ikke ha et."""
    uten = []
    for n in noder:
        if n.get("buss_domene"):
            continue
        s = n.get("stipulasjoner") or {}
        if not s.get("buss_status"):
            uten.append(n["id"])
    assert not uten, (
        f"{len(uten)} node(r) har verken buss_domene eller buss_status: {uten[:8]}")


def test_hver_node_har_tatt_stilling_til_motor(noder: list[dict]) -> None:
    """Samme for motor: en fungerende motor, eller en grunn til aa ikke ha en."""
    uten = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        if s.get("motor"):
            continue
        if not s.get("motor_status"):
            uten.append(n["id"])
    assert not uten, (
        f"{len(uten)} node(r) har verken motor eller motor_status: {uten[:8]}")


def test_statusene_sier_noe_om_hvorfor(noder: list[dict]) -> None:
    """«ingen» er et svar; en tom streng er en utelatelse."""
    for n in noder:
        s = n.get("stipulasjoner") or {}
        for felt in ("buss_status", "motor_status"):
            v = s.get(felt)
            if v is not None:
                assert v.strip(), f"{n['id']}.{felt} er tom — si hvorfor"


def test_de_interne_forklarer_seg_selv(noder: list[dict]) -> None:
    """De interne nodene er ikke en feil — de er et valg som skal staa."""
    interne = [n for n in noder if n.get("synlighet") == "intern"]
    assert interne, "forutsetning: det finnes interne noder"
    for n in interne:
        s = n.get("stipulasjoner") or {}
        assert s.get("buss_status"), f"{n['id']} er intern uten begrunnelse"
