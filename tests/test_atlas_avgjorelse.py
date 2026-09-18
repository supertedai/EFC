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
        assert n.get("buss_domene") or s.get("buss_status"), (
            f"{n['id']} er intern uten begrunnelse — den maa ha et "
            f"buss_domene eller en skriftlig grunn til aa ikke ha det")


# --- Falsifiserbarhet: samme regel som buss og motor (kort t_c11ffa45) ------
#
# Maalt 2026-09-18 fra landet main: `ville_falsifisere` manglet paa 82 av 113
# noder, og skjemaet gjorde feltet VALGFRITT. Atlaset testet at hver node KAN
# baere feltet — aldri at den HAR tatt stilling. Suiten var groenn likevel,
# ogsaa for `obs.bao` — noden som baerer motbeviset mot vaart eget regime.
#
# Regelen er den samme som for buss og motor: valget skal vaere TATT. En
# instrument-node kan ikke felles av en observasjon — det er et gyldig svar.
# Et tomt felt er ikke et svar.

GRUNN = "ikke_falsifiserbar_grunn"

#: Tekster som ser ut som et svar uten aa vaere det.
PLASSHOLDERE = ("vet ikke", "ukjent", "ikke relevant", "n/a", "todo",
                "fylles ut", "kommer", "tbd", "-")


def test_hver_node_har_tatt_stilling_til_falsifiserbarhet(noder: list[dict]) -> None:
    """Enten en falsifikator, ELLER en skriftlig grunn til at den ikke har.

    Populasjonen er ALLE 113 noder, ikke bare de offentlige: skillet i
    `test_falsifiserbarhet.py` sier hva som er VAARE paastander, mens denne
    sier at ingen node faar staa uten avgjoerelse. Tallene er pinnet fordi
    begge utfall er ekte — en node som mister falsifikatoren sin, og en node
    som blir omklassifisert, skal vaere et valg noen har tatt.
    """
    uten = [n["id"] for n in noder
            if not n.get("ville_falsifisere") and not n.get(GRUNN)]
    assert not uten, (
        f"{len(uten)} av {len(noder)} node(r) har verken falsifikator eller "
        f"grunn til aa ikke ha en: {uten[:8]}")
    kan = [n["id"] for n in noder if n.get("ville_falsifisere")]
    maa = [n["id"] for n in noder if n.get(GRUNN)]
    assert len(noder) == 113, f"atlaset endret storrelse: {len(noder)}"
    assert len(kan) == 31, (
        f"falsifiserbare: {len(kan)} — forventet 31 (27 offentlige + 4 "
        f"interne). Gikk tallet ned, mistet en node sin falsifikator")
    assert len(maa) == 82, (
        f"med skriftlig grunn: {len(maa)} — forventet 82. Gikk tallet ned, "
        f"har en node faatt en falsifikator; det skal noen ha bestemt")
    assert len(kan) + len(maa) == len(noder), (
        "en node har BEGGE — da sier atlaset to ting om samme spoersmaal")


def test_grunnen_er_skrevet_for_denne_noden(noder: list[dict]) -> None:
    """En plassholder er en utelatelse med tekst paa.

    Samme to krav som falsifikatoren har hatt siden 2026-09-17: lang nok til
    aa bety noe (40 tegn), og ikke en tekst som gaar igjen paa flere noder.
    Et svar som kan kopieres til tjue noder svarer ikke for noen av dem.
    """
    tekster: dict[str, list[str]] = {}
    for n in noder:
        t = n.get(GRUNN)
        if t is None:
            continue
        assert t.strip(), f"{n['id']}.{GRUNN} er tom — si hvorfor"
        assert len(t) >= 40, (
            f"{n['id']}.{GRUNN} er {len(t)} tegn — for kort til aa bety noe")
        assert t.strip().lower() not in PLASSHOLDERE, (
            f"{n['id']}.{GRUNN} er en plassholder: {t!r}")
        tekster.setdefault(t, []).append(n["id"])
    delt = {t: ids for t, ids in tekster.items() if len(ids) > 1}
    assert not delt, (
        f"identisk grunn paa flere noder: {list(delt.values())}")


def test_grunnen_navngir_ikke_feltet_den_erstatter(noder: list[dict]) -> None:
    """`atlas_lesing._har_falsifikator` leser noden som TEKST.

    Den spoer om strengen `ville_falsifisere` finnes i `json.dumps(node)` —
    saa en grunn som skriver feltnavnet sitt ville telt som en falsifikator
    baade i oppslaget og i navigasjonens `kan_felles`. Vakten staar her fordi
    den er usynlig i dataene: den fyrer foerst naar noen omformulerer seg.
    """
    lekkasje = [n["id"] for n in noder
                if "ville_falsifisere" in (n.get(GRUNN) or "")]
    assert not lekkasje, (
        f"{len(lekkasje)} node(r) skriver feltnavnet i grunnen sin og ville "
        f"blitt talt som falsifiserbare: {lekkasje[:6]}")


def test_en_node_som_skylder_en_terskel_sier_det_i_grunnen(noder: list[dict]) -> None:
    """`falsifiserbarhet` er pinnet til fire noder. Grunnen skal navngi dem.

    De fire har en kriterietekst som venter paa en fastsatt terskel eller paa
    at stubben blir fysikk. Sier grunnen noe annet, er det to svar paa samme
    spoersmaal — og da vet ikke leseren hvilket av dem som gjelder.
    """
    skylder = [n for n in noder if n.get("falsifiserbarhet")]
    assert len(skylder) == 4, f"forventet 4, fikk {len(skylder)}"
    for n in skylder:
        status = n["falsifiserbarhet"]["status"]
        assert status in n.get(GRUNN, ""), (
            f"{n['id']} skylder en terskel (status {status!r}) men grunnen "
            f"navngir den ikke — da staar to svar side om side")
