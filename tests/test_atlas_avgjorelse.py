"""THE DECISION: a node must have TAKEN A POSITION, not just omitted the field.

Measured 2026-09-18 (card t_fc25238b): `plasser()` was called from ONE
place — the CLI itself. No hook, no CI. The entry point existed and sat
unused, and each of the night's four closings ended in the same sentence:
"I still have to remember to do it".

The generator already has two guards that FAIL: codes (#476) and
PLACEMENT (#507). Both caught their own author tonight. That is the
pattern.

The third guard is different: it must not require a node to be DONE — it
must require that the CHOICE has been made. An instrument node needs no
engine. But it must say so, not stay silent.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def nodes() -> list[dict]:
    d = json.loads(ATLAS.read_text(encoding="utf-8"))
    return d["nodes"]


def test_hver_node_har_tatt_stilling_til_buss_domene(nodes: list[dict]) -> None:
    """Either a domain, or a written reason for not having one."""
    missing = []
    for n in nodes:
        if n.get("buss_domene"):
            continue
        s = n.get("stipulasjoner") or {}
        if not s.get("buss_status"):
            missing.append(n["id"])
    assert not missing, (
        f"{len(missing)} node(s) have neither buss_domene nor buss_status: {missing[:8]}")


def test_hver_node_har_tatt_stilling_til_motor(nodes: list[dict]) -> None:
    """Same for engine: a working engine, or a reason for not having one."""
    missing = []
    for n in nodes:
        s = n.get("stipulasjoner") or {}
        if s.get("motor"):
            continue
        if not s.get("motor_status"):
            missing.append(n["id"])
    assert not missing, (
        f"{len(missing)} node(s) have neither motor nor motor_status: {missing[:8]}")


def test_statusene_sier_noe_om_hvorfor(nodes: list[dict]) -> None:
    """"none" is an answer; an empty string is an omission."""
    for n in nodes:
        s = n.get("stipulasjoner") or {}
        for field in ("buss_status", "motor_status"):
            v = s.get(field)
            if v is not None:
                assert v.strip(), f"{n['id']}.{field} is empty — say why"


def test_de_interne_forklarer_seg_selv(nodes: list[dict]) -> None:
    """The internal nodes are not an error — they are a choice that must stand."""
    internal = [n for n in nodes if n.get("synlighet") == "intern"]
    assert internal, "precondition: internal nodes exist"
    for n in internal:
        s = n.get("stipulasjoner") or {}
        assert n.get("buss_domene") or s.get("buss_status"), (
            f"{n['id']} is internal without justification — it must have a "
            f"buss_domene or a written reason for not having one")
