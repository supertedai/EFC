"""THE ORPHANS: a node must not stand alone unless that is a CHOICE.

Measured 2026-09-18 (card t_7dd41524): 13 of 113 nodes had NULL links.
`_koblinger()` finds seven kinds — forelder, barn, samme_domene,
deler_analogi, samme_motor, samme_kilde, deler_proxy_ledd — and these
thirteen matched none of them.

They are not random nodes. They are the h2o phases, lys.sol,
kjemi.periodesystemet, efc.l0/l2/l3, and four instrument nodes that are
alone in their own bus domain.

Two outcomes are valid:
  KOBLET     — the node has the link it actually belongs to
  BEGRUNNET  — the node is honestly alone, and says why in `stipulasjoner`

What is not valid is standing empty.
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
    """The core: every node must either have a neighbour or say why it has none."""
    uten = []
    for n in atlas["noder"]:
        if _ett_hopp(atlas, n["id"]) > 0:
            continue
        s = n.get("stipulasjoner") or {}
        if not s.get("alene_status"):
            uten.append(n["id"])
    assert not uten, (
        f"{len(uten)} node(s) stand alone WITHOUT a reason: {uten[:8]}")


def test_h2o_fasene_henger_sammen(atlas: dict) -> None:
    """The phase map is ONE map — not five loose nodes."""
    for nid in ("h2o.solid", "h2o.gas", "h2o.supercritical", "h2o.liquid"):
        n = next(x for x in atlas["noder"] if x["id"] == nid)
        f = (n.get("nivaa") or {}).get("forelder")
        assert f, f"{nid} has no parent in the phase map"


def test_lys_er_forutsetningen_for_dispersjon(atlas: dict) -> None:
    """The direction must be physical: dispersion PRESUPPOSES light, not the other way."""
    d = next(x for x in atlas["noder"] if x["id"] == "optikk.dispersjon")
    assert (d.get("nivaa") or {}).get("forelder") == "lys.sol", (
        "optikk.dispersjon must have lys.sol as parent — the light is the presupposition")


def test_efc_lagene_henger_i_en_kjede(atlas: dict) -> None:
    """L0 -> L1 -> L2 -> L3 is a sequence, not four loose regimes."""
    for nid, forventet in (("efc.l2", "efc.l1"), ("efc.l3", "efc.l2"),
                           ("efc.l1", "efc.l0")):
        n = next(x for x in atlas["noder"] if x["id"] == nid)
        assert (n.get("nivaa") or {}).get("forelder") == forventet, (
            f"{nid} must have {forventet} as parent")


def test_alene_status_sier_noe(atlas: dict) -> None:
    """'alene' is an answer; an empty string is an omission."""
    for n in atlas["noder"]:
        v = (n.get("stipulasjoner") or {}).get("alene_status")
        if v is not None:
            assert v.strip(), f"{n['id']}.alene_status is empty"
