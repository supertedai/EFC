"""THE CONTRADICTION: a node shall not say two opposite things at the same time.

Measured 2026-09-18, after #514: all 12 homo nodes had BOTH —
`buss_domene: verden.helse` AND `buss_status: «ingen buss — emnet
finnes ikke som domene i snapshotet»`. The field was set, the old
status remained, and both were readable.

That is worse than an empty field. An empty field says «not decided».
Two contradictory answers say that the atlas does not know what it itself
means — and a reader who only sees the one gets an answer without knowing
that there is another.

The rule: when the field is set, the status shall go. A decision stands
alone.
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
    """If the node has a bus, it shall not also carry an «ingen buss» status."""
    begge = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        if n.get("buss_domene") and s.get("buss_status"):
            begge.append(n["id"])
    assert not begge, (
        f"{len(begge)} node(s) have BOTH: buss_domene and buss_status. "
        f"When the field is set, the status shall go: {begge[:6]}")


def test_motor_og_motor_status_utelukker_hverandre(noder: list[dict]) -> None:
    """The same for the engine."""
    begge = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        if s.get("motor") and s.get("motor_status"):
            begge.append(n["id"])
    assert not begge, (
        f"{len(begge)} node(s) have BOTH: motor and motor_status: {begge[:6]}")


def test_ingen_status_sier_imot_sitt_eget_felt(noder: list[dict]) -> None:
    """The direct contradiction: the field says yes, the status says no."""
    motsigelser = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        b = n.get("buss_domene")
        st = (s.get("buss_status") or "").lower()
        if b and ("ingen buss" in st or "ikke som domene" in st):
            motsigelser.append(n["id"])
    assert not motsigelser, (
        f"{len(motsigelser)} node(s) say both that they HAVE a bus and that they "
        f"do NOT: {motsigelser[:6]}")
