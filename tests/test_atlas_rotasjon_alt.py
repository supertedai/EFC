"""KAN JEG ROTERE RUNDT ALT? — vakten som manglet da de tolv motorene kom inn.

Maalt 2026-09-18, etter #514: gjennomgangen av alle 39 domener ble kjoert
manuelt en gang, og ikke som test. Da de tolv biologimotorene ble lagt inn,
ble den ikke kjoert paa nytt.

Denne testen svarer paa to ting, og de er ikke de samme:

  1. HVER AKSE `akser()` finner skal kunne roteres, og svaret skal ha
     samme antall noder som aksen oppgir. Uenighet betyr at aksen tilbyr
     noe den ikke kan svare paa.

  2. HVERT DOMENE skal gi alle sine noder naar jeg roterer rundt det.
     Uenighet mot dekningsfilen betyr at et domene sier noe annet enn
     atlaset gjor.

Rotasjon er ikke dekning. Et atlas kan ha alle nodene sine og fortsatt
ikke kunne roteres rundt dem.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(ROT, ref="HEAD")


@pytest.fixture(scope="module")
def dekning() -> dict:
    return json.loads(
        (ROT / "schema" / "atlas_dekning.json").read_text(encoding="utf-8"))


def test_hver_akse_kan_roteres(atlas: dict) -> None:
    """En akse som tilbys skal svare — og svare like mange."""
    assert len(atlas["noder"]) == 126
    dode = []
    for sti, (antall, _) in sorted(atlas_lesing.akser(atlas).items()):
        try:
            treff = atlas_lesing.roter_akse(atlas, sti)
        except Exception as e:  # noqa: BLE001
            dode.append(f"{sti}: kastet {type(e).__name__}")
            continue
        if antall == 0:
            dode.append(f"{sti}: tilbys med 0 noder")
        elif len(treff) != antall:
            dode.append(f"{sti}: sier {antall}, svarer {len(treff)}")
    assert not dode, (
        f"{len(dode)} akse(r) kan ikke roteres: {dode[:6]}")


def test_ingen_akse_tilbyr_none_som_verdi(atlas: dict) -> None:
    """`None` er ikke en verdi — og «None» som tekst er verre."""
    tilbyr = []
    for sti, (_, verdier) in atlas_lesing.akser(atlas).items():
        if any(v == "None" for v in verdier):
            tilbyr.append(sti)
    assert not tilbyr, (
        f"{len(tilbyr)} akse(r) tilbyr bokstavelig talt «None» som verdi: "
        f"{tilbyr[:6]}")


def test_hvert_domene_kan_roteres(atlas: dict, dekning: dict) -> None:
    """Roterer jeg rundt et domene, skal jeg faa alle dets noder."""
    feil = []
    for dom, v in sorted(dekning["domener"].items()):
        forventet = v.get("noder") or []
        if not forventet:
            feil.append(f"{dom}: tomt domene")
            continue
        treff = atlas_lesing.roter_akse(atlas, "buss_domene", dom)
        if len(treff) != len(forventet):
            feil.append(
                f"{dom}: dekningen sier {len(forventet)}, "
                f"rotasjonen gir {len(treff)}")
    assert not feil, f"{len(feil)} domene(r) kan ikke roteres: {feil[:6]}"


def test_alle_domener_er_provd(atlas: dict, dekning: dict) -> None:
    """Forutsetningen: dekningsfilen skal dekke hvert domene atlaset kjenner."""
    dom = set(dekning["domener"])
    assert len(dom) == 39, f"forventet 39 domener, fant {len(dom)}"
    kjente = {n.get("buss_domene") for n in atlas["noder"]} - {None}
    udekket = kjente - dom
    assert not udekket, (
        f"{len(udekket)} buss-domene(r) finnes i atlaset men ikke i "
        f"dekningsfilen: {sorted(udekket)[:6]}")
