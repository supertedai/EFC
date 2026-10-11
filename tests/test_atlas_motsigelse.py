"""THE CONTRADICTION: a node shall not say two opposite things at the same time.

Measured 2026-09-18, after #514: all 12 homo nodes had BOTH —
`buss_domene: verden.helse` AND `buss_status: "no bus — the subject
does not exist as a domain in the snapshot"`. The field was set, the old
status remained, and both were readable.

That is worse than an empty field. An empty field says "not decided".
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
    """If the node has a bus, it shall not also carry a "no bus" status."""
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
        if b and ("no bus" in st or "does not exist as a domain" in st):
            motsigelser.append(n["id"])
    assert not motsigelser, (
        f"{len(motsigelser)} node(s) say both that they HAVE a bus and that they "
        f"do NOT: {motsigelser[:6]}")


# --- Falsifiability: a decision stands alone (card t_c11ffa45) --------------
#
# The same rule as above, for the three answers measured 2026-09-18:
# `ville_falsifisere`, `falsifiserbarhet` and `stipulasjoner.
# ikke_falsifiserbar_grunn`. A node with TWO of them says two things at once
# — the same fault as #514: the reader gets one answer without knowing there is
# another. `test_atlas_avgjorelse.py` measures that no node is SILENT (>= 1
# answer); here it is measured that nobody answers twice (<= 1).

def _antall_svar(n: dict) -> int:
    return (bool(n.get("ville_falsifisere"))
            + bool(n.get("falsifiserbarhet"))
            + bool((n.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn")))


def test_ingen_node_har_to_falsifiseringssvar(noder: list[dict]) -> None:
    begge = [n["id"] for n in noder if _antall_svar(n) > 1]
    assert not begge, (
        f"{len(begge)} node(s) have more than one answer on whether they can "
        f"be felled. A decision stands alone: {begge[:6]}")


def test_falsifikator_og_ikke_falsifiserbar_grunn_utelukker_hverandre(
        noder: list[dict]) -> None:
    """The direct contradiction: «here is what would fell me» AND «I cannot
    be felled» in the same node."""
    begge = [n["id"] for n in noder
             if n.get("ville_falsifisere")
             and (n.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn")]
    assert not begge, (
        f"{len(begge)} node(s) have BOTH: a falsifier and a reason not to "
        f"have one: {begge[:6]}")


def test_en_tom_verdi_er_ikke_en_avgjoerelse(noder: list[dict]) -> None:
    """«Cannot be felled» is an answer; an empty string is an omission.

    The same rule as `test_statusene_sier_noe_om_hvorfor` above: the field must
    be FILLED or ABSENT, never filled with nothing. An empty string satisfies
    «the field exists» and does not answer the question — exactly the fault
    class `test_falsifiserbarhet.py` has felled three times.
    """
    tomme = []
    for n in noder:
        s = n.get("stipulasjoner") or {}
        for felt in ("ville_falsifisere", "ikke_falsifiserbar_grunn"):
            verdi = n.get(felt) if felt == "ville_falsifisere" else s.get(felt)
            if verdi is not None and not str(verdi).strip():
                tomme.append(f"{n['id']}.{felt}")
    assert not tomme, f"empty decisions: {tomme[:6]}"
