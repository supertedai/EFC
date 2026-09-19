"""The settlement path must be fail-closed: it may NOT close against a non-arbiter.

Measured 2026-09-19. The sealed fsigma8 prediction is armed on the bus with a
named arbiter and 0 settlements. The failure guarded against here is the one the
apparatus exists to prevent: computing a settlement against the wrong
measurement -- taking a non-arbiter as evidence.

Every test but the last is about REFUSAL. The last proves the loop is still
open, i.e. that nothing has settled it yet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_oppgjoer as O  # noqa: E402

ARB = ROT / "schema" / "efc_fs8.arbiter.json"
BRO = ROT / "schema" / "efc_fs8.bro.json"


@pytest.fixture(scope="module")
def arb() -> dict:
    return O.read(ARB)


@pytest.fixture(scope="module")
def bro() -> dict:
    return O.read(BRO)


def _candidate(**kw) -> dict:
    k = {"observable": "fsigma8", "survey": "DESI", "release": "DR2",
         "analysis": "full-shape", "fsigma8": 0.43, "fsigma8_sigma": 0.05,
         "z_eff": 0.7, "tracer": "LRG+ELG", "referanse": "DESI 2025 VI",
         "seq": 999, "Nats_Msg_Id": "efc-fs8.v1.DESI_DR2.LRG+ELG.0.7000.test"}
    k.update(kw)
    return k


def test_the_loop_is_armed_and_that_is_recorded(arb: dict) -> None:
    assert arb["state_now"]["arbiter_present"] is False
    assert arb["state_now"]["settlements"] == 0
    assert arb["state_now"]["armed_since"].startswith("2026-02-18")
    assert arb["state_now"]["why_open_is_correct"]


def test_a_measurement_outside_the_window_is_refused(arb: dict) -> None:
    """DESI DR1 at z=0.93 is a real measurement and NOT the arbiter."""
    fails = O.gate(_candidate(z_eff=0.93), arb)
    assert any("outside the window" in f for f in fails), fails


def test_a_measurement_without_provenance_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(seq=None, Nats_Msg_Id=None), arb)
    assert any("provenance" in f for f in fails), fails


def test_a_measurement_without_its_own_sigma_is_refused(arb: dict) -> None:
    """The tolerance is the measurement's OWN sigma. No sigma, no settlement."""
    fails = O.gate(_candidate(fsigma8_sigma=None), arb)
    assert any("OWN sigma" in f for f in fails), fails
    fails = O.gate(_candidate(fsigma8_sigma=0), arb)
    assert any("positive number" in f for f in fails), fails


def test_a_missing_required_field_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(referanse=None), arb)
    assert any("referanse" in f for f in fails), fails


def test_a_wrong_observable_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(observable="sigma8"), arb)
    assert any("observable is" in f for f in fails), fails


def test_the_verdict_uses_the_measurements_own_sigma(bro: dict, arb: dict) -> None:
    """A value ON the prediction is confirmed; a distant one is contradicted."""
    exp = O.expected(bro)
    assert O.verdict(_candidate(fsigma8=0.43, fsigma8_sigma=0.05), exp, arb) == {
        "gap_sigma": 0.0, "formula": "(fsigma8 - fsigma8_efc) / fsigma8_sigma",
        "tolerance_rule": arb["tolerance_rule"], "outcome": "confirmed",
        "compared_with": "DESI LRG+ELG"}
    assert O.verdict(_candidate(fsigma8=0.55, fsigma8_sigma=0.05),
                     exp, arb)["outcome"] == "contradicted"
    # the SAME 0.06 gap passes or fails depending on the measurement's own sigma
    assert O.verdict(_candidate(fsigma8=0.49, fsigma8_sigma=0.05),
                     exp, arb)["outcome"] == "contradicted"
    assert O.verdict(_candidate(fsigma8=0.49, fsigma8_sigma=0.10),
                     exp, arb)["outcome"] == "confirmed"


def test_the_landed_bank_has_no_settlement_yet(arb: dict) -> None:
    """If this fails, the loop was closed against something that is not the arbiter."""
    bank = O.read(O.ATLAS)
    node = next(n for n in bank["nodes"] if n["id"] == arb["claim_node"])
    assert "settlement_result" not in node, (
        f"{arb['claim_node']} already carries a settlement — measured against what?")
