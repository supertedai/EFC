"""ØYENE: en node skal ikke stå alene uten at det er et VALG.

Maalt 2026-09-18 (kort t_7dd41524): 13 av 113 noder hadde NULL koblinger.
`_koblinger()` finner sju slag — forelder, barn, samme_domene, deler_analogi,
samme_motor, samme_kilde, deler_proxy_ledd — og disse tretten matchet ingen.

Det er ikke tilfeldige noder. Det er h2o-fasene, lys.sol,
kjemi.periodesystemet, efc.l0/l2/l3, og fire instrument-noder som er alene
i sitt eget buss-domene.

To utfall er gyldige:
  KOBLET     — noden har faatt den koblingen den faktisk horer til
  BEGRUNNET  — noden er aerlig alene, og sier hvorfor i `stipulasjoner`

Det som ikke er gyldig er aa staa tom.
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


def _ett_hopp(atlas: dict, nid: str) -> int:
    return atlas_lesing.helhet(atlas, nid).get("ett_hopp", 0)


def test_ingen_node_staar_uten_kobling_eller_grunn(atlas: dict) -> None:
    """Kjernen: hver node skal enten ha en nabo eller si hvorfor den ikke har det."""
    uten = []
    for n in atlas["noder"]:
        if _ett_hopp(atlas, n["id"]) > 0:
            continue
        s = n.get("stipulasjoner") or {}
        if not s.get("alene_status"):
            uten.append(n["id"])
    assert not uten, (
        f"{len(uten)} node(r) staar alene UTEN grunn: {uten[:8]}")


def test_h2o_fasene_henger_sammen(atlas: dict) -> None:
    """Fasekartet er ETT kart — ikke fem lause noder."""
    for nid in ("h2o.solid", "h2o.gas", "h2o.supercritical", "h2o.liquid"):
        n = next(x for x in atlas["noder"] if x["id"] == nid)
        f = (n.get("nivaa") or {}).get("forelder")
        assert f, f"{nid} har ingen forelder i fasekartet"


def test_lys_er_forutsetningen_for_dispersjon(atlas: dict) -> None:
    """Rettningen skal vaere fysisk: dispersjon FORUTSETTER lys, ikke omvendt."""
    d = next(x for x in atlas["noder"] if x["id"] == "optikk.dispersjon")
    assert (d.get("nivaa") or {}).get("forelder") == "lys.sol", (
        "optikk.dispersjon skal ha lys.sol som forelder — lyset er forutsetningen")


def test_efc_lagene_henger_i_en_kjede(atlas: dict) -> None:
    """L0 -> L1 -> L2 -> L3 er en sekvens, ikke fire lause regimer."""
    for nid, forventet in (("efc.l2", "efc.l1"), ("efc.l3", "efc.l2"),
                           ("efc.l1", "efc.l0")):
        n = next(x for x in atlas["noder"] if x["id"] == nid)
        assert (n.get("nivaa") or {}).get("forelder") == forventet, (
            f"{nid} skal ha {forventet} som forelder")


def test_alene_status_sier_noe(atlas: dict) -> None:
    """«alene» er et svar; en tom streng er en utelatelse."""
    for n in atlas["noder"]:
        v = (n.get("stipulasjoner") or {}).get("alene_status")
        if v is not None:
            assert v.strip(), f"{n['id']}.alene_status er tom"
