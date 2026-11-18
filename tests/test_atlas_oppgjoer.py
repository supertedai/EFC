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
import os
import subprocess
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


def test_a_measurement_with_a_string_z_eff_is_refused(arb: dict) -> None:
    """A quoted redshift is not a number: the window guard must REFUSE it,
    not silently skip the whole window check (t_1e7895c2)."""
    fails = O.gate(_candidate(z_eff="0.7"), arb)
    assert any("z_eff must be a number" in f for f in fails), fails


def test_a_boolean_z_eff_is_refused_as_not_a_number(arb: dict) -> None:
    """bool is a subclass of int in Python; a boolean redshift must not pass
    as a number."""
    fails = O.gate(_candidate(z_eff=True), arb)
    assert any("z_eff must be a number" in f for f in fails), fails


def test_a_string_fsigma8_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(fsigma8="0.43"), arb)
    assert any("fsigma8 must be a number" in f for f in fails), fails


def test_a_non_string_reference_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(referanse=123), arb)
    assert any("referanse must be a string" in f for f in fails), fails


def test_a_dict_seq_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(seq={}), arb)
    assert any("seq must be an integer" in f for f in fails), fails


def test_a_non_string_msg_id_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(Nats_Msg_Id=123), arb)
    assert any("Nats_Msg_Id must be a string" in f for f in fails), fails


def test_a_valid_candidate_still_passes_the_gate(arb: dict) -> None:
    """The gate's own "empty = passed" contract, on a fully valid candidate."""
    assert O.gate(_candidate(), arb) == []


def test_a_string_seq_passes_the_gate(arb: dict) -> None:
    """`seq` is provenance carried verbatim — a string sequence is accepted,
    not rejected (t_1e7895c2)."""
    assert O.gate(_candidate(seq="999"), arb) == []


def test_a_nan_fsigma8_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(fsigma8=float("nan")), arb)
    assert any("finite" in f for f in fails), fails


def test_an_infinite_fsigma8_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(fsigma8=float("inf")), arb)
    assert any("finite" in f for f in fails), fails


def test_a_nan_sigma_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(fsigma8_sigma=float("nan")), arb)
    assert any("finite" in f for f in fails), fails


def test_an_infinite_sigma_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(fsigma8_sigma=float("inf")), arb)
    assert any("finite" in f for f in fails), fails


def test_a_nan_z_eff_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(z_eff=float("nan")), arb)
    assert any("finite" in f for f in fails), fails


def test_an_infinite_z_eff_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(z_eff=float("inf")), arb)
    assert any("finite" in f for f in fails), fails


def test_an_integer_too_large_for_a_float_is_refused(arb: dict) -> None:
    """math.isfinite overflows on ints beyond float range; _finite must catch
    that and refuse, not crash the gate (t_1e7895c2)."""
    fails = O.gate(_candidate(fsigma8=10 ** 400), arb)
    assert any("finite" in f for f in fails), fails


def test_dump_bank_refuses_a_non_finite_value() -> None:
    """The decisive layer: JSON has no NaN/Infinity token, so `allow_nan=False`
    makes the serialiser fail closed before write_text can touch the file."""
    with pytest.raises(ValueError):
        O.dump_bank({"gap_sigma": float("nan")})


def test_dump_bank_reproduces_the_landed_bank_byte_for_byte() -> None:
    """The writer's serialiser is the exact on-disk format: `--skriv` must not
    produce a spurious diff on the untouched parts of the bank."""
    raw = O.ATLAS.read_bytes()
    assert O.dump_bank(json.loads(raw)).encode("utf-8") == raw


def test_verdict_refuses_a_non_finite_gap(bro: dict, arb: dict) -> None:
    """Two finite inputs can still overflow the normalised gap (1e308 / 1e-300).
    The verdict must refuse — not emit `contradicted` with an infinite gap."""
    exp = O.expected(bro)
    with pytest.raises(ValueError):
        O.verdict(_candidate(fsigma8=1e308, fsigma8_sigma=1e-300), exp, arb)


def test_a_measurement_that_overflows_the_gap_is_refused(tmp_path) -> None:
    """The wiring maps the verdict's ValueError to a REFUSED exit code before
    any write. `--kandidat` without `--skriv` reads only bro/arb, never the bank."""
    cand = _candidate(fsigma8=1e308, fsigma8_sigma=1e-300)
    kfile = tmp_path / "candidate.json"
    kfile.write_text(json.dumps(cand), encoding="utf-8")
    env = {**os.environ}
    env.pop("PYTHONPATH", None)
    r = subprocess.run(
        [sys.executable, str(ROT / "scripts" / "atlas_oppgjoer.py"),
         "--kandidat", str(kfile)],
        capture_output=True, text=True,
        env=env)
    assert r.returncode == O.EXIT_REFUSED, r.stdout
    assert "REFUSED" in r.stdout, r.stdout


def test_main_writes_through_dump_bank(tmp_path, monkeypatch) -> None:
    """Nothing else pins that main() calls dump_bank: an inline
    json.dumps(allow_nan=True) in the write path would survive the whole
    suite. This fails loudly if the wiring is ever unpicked (t_1e7895c2)."""
    sentinel = RuntimeError("dump_bank must be the writer's serialiser")
    bank_copy = tmp_path / "regime_nodes.jsonld"
    bank_copy.write_bytes(O.ATLAS.read_bytes())
    monkeypatch.setattr(O, "ATLAS", bank_copy)

    def boom(_bank: dict) -> str:
        raise sentinel

    monkeypatch.setattr(O, "dump_bank", boom)
    flat = tmp_path / "candidate.json"
    flat.write_text(json.dumps(_candidate()), encoding="utf-8")
    monkeypatch.setattr(sys, "argv",
                        ["atlas_oppgjoer.py", "--kandidat", str(flat), "--skriv"])
    with pytest.raises(RuntimeError) as excinfo:
        O.main()
    assert excinfo.value is sentinel


def test_a_serialisation_failure_is_a_controlled_refusal(tmp_path, monkeypatch) -> None:
    """A ValueError from the serialiser is a controlled refusal (EXIT_REFUSED),
    not a traceback — and nothing is written (t_1e7895c2)."""
    bank_copy = tmp_path / "regime_nodes.jsonld"
    bank_copy.write_bytes(O.ATLAS.read_bytes())
    before = bank_copy.read_bytes()
    monkeypatch.setattr(O, "ATLAS", bank_copy)

    def boom(_bank: dict) -> str:
        raise ValueError("non-finite value")

    monkeypatch.setattr(O, "dump_bank", boom)
    flat = tmp_path / "candidate.json"
    flat.write_text(json.dumps(_candidate()), encoding="utf-8")
    monkeypatch.setattr(sys, "argv",
                        ["atlas_oppgjoer.py", "--kandidat", str(flat), "--skriv"])
    with pytest.raises(SystemExit) as excinfo:
        O.main()
    assert excinfo.value.code == O.EXIT_REFUSED
    assert bank_copy.read_bytes() == before


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


def test_verdict_rounds_gap_sigma_but_derives_outcome_from_raw_gap(bro: dict, arb: dict) -> None:
    """verdict() stores round(gap, 2) but derives outcome from the RAW gap.

    gap = 1.004 -> outcome "contradicted" (raw |gap| > 1.0), yet the stored
    gap_sigma is round(1.004, 2) == 1.0. This is why the reader must trust
    `outcome` and NOT re-derive the tolerance from the rounded gap_sigma —
    recomputing would flip this verdict to "confirmed".
    """
    exp = O.expected(bro)
    v = O.verdict(_candidate(fsigma8=0.4802, fsigma8_sigma=0.05), exp, arb)
    assert v["outcome"] == "contradicted"
    assert v["gap_sigma"] == 1.0


def test_the_landed_bank_has_no_settlement_yet(arb: dict) -> None:
    """If this fails, the loop was closed against something that is not the arbiter."""
    bank = O.read(O.ATLAS)
    node = next(n for n in bank["nodes"] if n["id"] == arb["claim_node"])
    assert "settlement_result" not in node, (
        f"{arb['claim_node']} already carries a settlement — measured against what?")
