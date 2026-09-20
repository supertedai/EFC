"""PLACEMENT: no fallback, and no dead keys.

Measured 2026-09-18 (card t_aadbf18d): PLASSERING was keyed on OLD names
(`efc.rotation` against `efc.rotation_engine`, `efc.water` against
`efc.water_phase_engine`). 17 of 28 keys pointed at nodes that never have
had that name, and the fallback `("ghost", 8)` answered instead of saying
so. 68 of 73 public nodes ended up as «Not yet built» — of which 10 with
`evidensstatus: replikert`.

The same class as #476 (the codes), in a different table.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

import efc_atlas_generator as g  # noqa: E402


@pytest.fixture(scope="module")
def noder() -> list[dict]:
    d = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
    return d["nodes"]


def test_ingen_nokkel_peker_paa_ingenting(noder: list[dict]) -> None:
    """A key that matches no node is a silent miss."""
    ider = {n["id"] for n in noder}
    dode = sorted(k for k in g.PLASSERING if k not in ider)
    assert not dode, f"PLASSERING keys without a node: {dode[:8]}"


def test_alle_offentlige_noder_har_plassering(noder: list[dict]) -> None:
    """Nobody must fall back: ghost is a CHOICE and stands explicitly."""
    off = [n["id"] for n in noder if n.get("synlighet") == "offentlig"]
    uten = [i for i in off if i not in g.PLASSERING]
    assert not uten, f"public nodes without placement: {uten[:8]}"


def test_fallbacken_er_borte() -> None:
    """The source must no longer have a `.get(navn, default)` for placement."""
    src = (ROT / "scripts" / "maintenance" / "efc_atlas_generator.py").read_text(
        encoding="utf-8")
    assert 'PLASSERING.get(navn, ("ghost", 8))' not in src, (
        "fallbacken svarer fortsatt i stedet for aa si fra")
    assert "is not in PLASSERING" in src, "vakten mangler"


def test_ghost_er_deklarert_som_valg() -> None:
    src = (ROT / "scripts" / "maintenance" / "efc_atlas_generator.py").read_text(
        encoding="utf-8")
    assert "Ghost is a CHOICE" in src, "ghost staar uten begrunnelse"
