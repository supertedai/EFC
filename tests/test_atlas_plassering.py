"""PLASSERING: ingen fallback, og ingen doede noekler.

Maalt 2026-09-18 (kort t_aadbf18d): PLASSERING var noklet paa GAMLE navn
(`efc.rotation` mot `efc.rotation_engine`, `efc.water` mot
`efc.water_phase_engine`). 17 av 28 noekler pekte paa noder som aldri har
hatt det navnet, og fallbacken `("ghost", 8)` svarte i stedet for aa si
fra. 68 av 73 offentlige noder endte som «Not yet built» — hvorav 10 med
`evidensstatus: replikert`.

Samme klasse som #476 (kodene), i en annen tabell.
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
    """En noekkel som ikke matcher en node er en stille bom."""
    ider = {n["id"] for n in noder}
    dode = sorted(k for k in g.PLASSERING if k not in ider)
    assert not dode, f"PLASSERING-noekler uten node: {dode[:8]}"


def test_alle_offentlige_noder_har_plassering(noder: list[dict]) -> None:
    """Ingen skal falle tilbake: ghost er et VALG og staar eksplisitt."""
    off = [n["id"] for n in noder if n.get("synlighet") == "offentlig"]
    uten = [i for i in off if i not in g.PLASSERING]
    assert not uten, f"offentlige uten plassering: {uten[:8]}"


def test_fallbacken_er_borte() -> None:
    """Kilden skal ikke lenger ha en `.get(navn, default)` for plassering."""
    src = (ROT / "scripts" / "maintenance" / "efc_atlas_generator.py").read_text(
        encoding="utf-8")
    assert 'PLASSERING.get(navn, ("ghost", 8))' not in src, (
        "fallbacken svarer fortsatt i stedet for aa si fra")
    assert "is not in PLASSERING" in src, "vakten mangler"


def test_ghost_er_deklarert_som_valg() -> None:
    src = (ROT / "scripts" / "maintenance" / "efc_atlas_generator.py").read_text(
        encoding="utf-8")
    assert "Ghost is a CHOICE" in src, "ghost staar uten begrunnelse"
