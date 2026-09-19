"""The armed prediction must be readable, and its arithmetic must be recomputed.

Measured 2026-09-19. Two errors of my own were caught while building this, and
both are pinned here so they cannot come back silently:

1. The snapshot's first version carried HAND-WRITTEN derived numbers, and they
   were wrong: it said the nearest baseline was z=0.93 (0.23 away) and the gap
   -1.44 sigma. The arithmetic gives z=0.85 at 0.15 and -1.21 sigma.
   `scripts/atlas_prediksjon.py` found it by recomputing.
2. The bridge pointed at ONE node. A prediction lives on two: the measurement
   node records the observation (and correctly cannot be felled -- it IS the
   measurement), while the CLAIM node carries the falsifier and is where the
   settlement lands. The failing test is what surfaced it.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_prediksjon as P  # noqa: E402

BRO = ROT / "schema" / "efc_fs8.bro.json"
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def bro() -> dict:
    return P.les_bro()


@pytest.fixture(scope="module")
def bank() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def test_every_baseline_carries_its_own_provenance(bro: dict) -> None:
    """A value without a seq is a claim, not a measurement."""
    assert bro["baselines"], "precondition: the bridge carries baselines"
    for b in bro["baselines"]:
        assert b.get("seq"), f"{b.get('survey')} {b.get('tracer')} has no seq"
        assert b.get("Nats_Msg_Id"), f"{b.get('survey')} {b.get('tracer')} has no msg id"
        assert isinstance(b.get("sigma"), float) and b["sigma"] > 0


def test_the_nearest_baseline_is_the_measured_one(bro: dict) -> None:
    """Pinned: eBOSS DR16 ELG at z=0.85 is 0.15 from the z=0.7 window."""
    n = P.naermeste(bro)
    assert (n["survey"], n["tracer"]) == ("eBOSS DR16", "ELG")
    assert n["z_eff"] == 0.85
    t = P.tilstand(bro)
    assert t["distance_z"] == 0.15
    assert t["gap_sigma_efc"] == -1.21


def test_the_gap_is_recomputed_not_trusted(bro: dict) -> None:
    n, f = P.naermeste(bro), P.expected(bro)
    ventet = round(P.avvik_sigma(n, f), 2)
    assert ventet == P.tilstand(bro)["gap_sigma_efc"] == -1.21


def test_no_derived_numbers_are_written_into_the_file(bro: dict) -> None:
    """A number that can be computed must not be written."""
    derived = bro.get("derived", {})
    tall = {k: v for k, v in derived.items()
            if isinstance(v, (int, float)) or
            (isinstance(v, dict) and any(isinstance(x, (int, float)) for x in v.values()))}
    assert not tall, f"derived carries hand-written numbers: {tall}"


def test_an_open_settlement_needs_a_named_missing_arbiter(bro: dict) -> None:
    """0 settlements is only correct because the criterion names what is missing."""
    p, bus = bro["prediction"], P._bus(bro)
    assert bro["counts"]["oppgjoer"] == 0
    assert p[bus["arbiter"]] == "nei"
    assert p[bus["awaits"]], "an open settlement without a named arbiter is neglect"


def test_the_prediction_was_frozen_before_the_measurements(bro: dict) -> None:
    """Blind means frozen BEFORE the data it will be judged against."""
    p, bus = bro["prediction"], P._bus(bro)
    assert P.freeze(bro)["primary_freeze"]["timestamp_utc"].startswith("2026-02-18")
    assert p[bus["sealed_doi"]].startswith("10.6084/")
    assert len(p[bus["sealed_sha256"]]) == 64


def test_the_loop_has_both_ends_in_the_atlas(bro: dict, bank: dict) -> None:
    """The measurement records; the claim is felled. Both must exist."""
    for key in ("atlas_node_measurement", "atlas_node_claim"):
        nid = bro[key]
        assert any(n["id"] == nid for n in bank["nodes"]), f"{nid} is not in the bank"


def test_the_claim_node_carries_the_arbiter_criterion_as_its_falsifier(
        bro: dict, bank: dict) -> None:
    """The falsifier on the claim node must NAME what would settle the loop."""
    node = next(n for n in bank["nodes"] if n["id"] == bro["atlas_node_claim"])
    f = node.get("ville_falsifisere")
    assert f, f"{bro['atlas_node_claim']} carries a prediction but no falsifier"
    tekst = f if isinstance(f, str) else json.dumps(f, ensure_ascii=False)
    assert "DESI DR2 full-shape" in tekst
    assert "0.430" in tekst


def test_the_measurement_node_correctly_cannot_be_felled(bro: dict, bank: dict) -> None:
    """An instrument node is the measurement; its falsification belongs to the claim.

    This is not a defect: it is the distinction that makes the landing place the
    claim node. Recorded so nobody 'fixes' it the wrong way.
    """
    node = next(n for n in bank["nodes"] if n["id"] == bro["atlas_node_measurement"])
    assert not node.get("ville_falsifisere")
    grunn = (node.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn")
    assert grunn, "a node that cannot be felled must say why"
