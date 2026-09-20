"""Does the closed experiment still reproduce — and is its drift named?

`RESULTAT.md` is a DATED measurement, not a description of today's atlas. It was
measured against the bank as it stood when `key.json` was sealed
(`bank.SEAL_COMMIT`). Reading `origin/main` at run time made every sealed answer
depend on a bank that is still being edited; measured 2026-09-19 on
`origin/main` (`bbc2c3b1`), 4 of 12 tests failed because the bank had moved
under them.

This file separates the two claims that were tangled together:

1. **The measurement reproduces** — on the bank it was measured against, the
   sealed table in `RESULTAT.md` must come out exactly. Deterministic forever.
2. **The bank still moves, and the movement is NAMED** — the living atlas is
   allowed to leave the sealed premise, but not silently. The two commits that
   did it are named with their measured effect, and this file fails if the
   documented drift is undone, so the note in `RESULTAT.md` cannot quietly stop
   being true.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import bank  # noqa: E402
import leser_a  # noqa: E402
import leser_b  # noqa: E402
import scorer  # noqa: E402

#: The table in `RESULTAT.md`, reproduced mechanically.
SEALED = {
    "A": {"korrekt": 5, "feil": 1, "avstaaelse": 2,
          "falske_stoettepastander": 0, "proveniens": 6},
    "B": {"korrekt": 7, "feil": 1, "avstaaelse": 0,
          "falske_stoettepastander": 0, "proveniens": 8},
}

#: The three `OBSERVED_IN` edges with an engine as subject that Q4 measured, and
#: the way they read on the living atlas after `10087393`.
INVERTED = [
    ("efc.hubble_engine", "obs.bao"),
    ("efc.growth_engine", "obs.fsigma8"),
    ("efc.growth_engine", "obs.s8"),
]

#: The two commits that moved the bank after the seal, with what they did. See
#: the note appended to `RESULTAT.md`.
DRIFT_COMMITS = {
    "10087393": "2026-09-18 22:34 — the six engine-subject OBSERVED_IN rows "
                "became obs.X --OBSERVED_THROUGH--> efc.motor, and the "
                "duplicated ANALOGOUS_TO row was removed with the symmetry "
                "declared in the predicate (#567, closing K6)",
    "fe865b95": "2026-09-18 22:41 — ADR-086 §3.1, adopted 2026-09-18: the "
                "optional usikkerhet field came in; obs.bao carries beta as a "
                "HOLE (#568)",
}


def _fixture():
    key = json.loads((HERE / "key.json").read_text(encoding="utf-8"))
    evidence = json.loads((HERE / "evidenslag.json").read_text(encoding="utf-8"))
    return key, evidence


def _relations(bank_data: dict) -> list[dict]:
    return [r for r in bank_data.get("relations", [])
            if all(k in r for k in ("subject", "predicate", "object"))]


# --------------------------------------------------------------------------
# 1. the measurement reproduces on its own bank
# --------------------------------------------------------------------------

def test_the_sealed_bank_is_present_and_pinned():
    """A missing snapshot is a loud failure, never a fallback to another ref."""
    sealed = bank.load_sealed()
    assert sealed["relations"], "the sealed bank has no relations — wrong ref?"
    assert bank.read_bytes()[:1] == b"{"


def test_the_sealed_table_in_resultat_md_reproduces_exactly():
    """RESULTAT.md's table, re-derived from the sealed bank and the key."""
    key, evidence = _fixture()
    sealed = bank.load_sealed()
    measured = {
        "A": scorer.score(leser_a.svar(sealed, key), key),
        "B": scorer.score(leser_b.svar(sealed, key, evidence), key),
    }
    assert measured == SEALED, (
        "the closed experiment no longer reproduces on the bank it was sealed "
        f"against ({bank.SEAL_COMMIT}): measured {measured}, RESULTAT.md says "
        f"{SEALED}")


def test_the_readers_agree_with_the_key_on_the_sealed_bank():
    """The invariant that was broken: the bank answers Q1 as the key says.

    Scoped to the snapshot on purpose. On the living atlas this invariant is
    FALSE by design — the bank was repaired and then extended — and pretending
    otherwise is what made the tests red on `main`.
    """
    key, _ = _fixture()
    sealed = bank.load_sealed()
    assert leser_a.svar(sealed, key)[0]["svar"] == {
        "observasjon": ["obs.fsigma8", "obs.s8"], "regime": ["efc.l2"]}


# --------------------------------------------------------------------------
# 2. the living atlas moved — and the movement is the documented one
# --------------------------------------------------------------------------

def test_the_living_atlas_is_not_the_sealed_bank():
    """If this fails, the drift note in RESULTAT.md describes nothing."""
    assert bank.read_bytes(bank.LIVE_REF) != bank.read_bytes(bank.SEAL_COMMIT)


def test_the_documented_drift_is_still_the_drift():
    """The named commits, re-measured on the living atlas.

    Fails if the documented drift is undone (a reverted OBSERVED_IN fix, a
    removed uncertainty field), because then `RESULTAT.md`'s note would be
    stale — and a stale reproducibility note is the failure this guards.
    """
    live = bank.load_live()
    relations = _relations(live)
    nodes = {n["id"]: n for n in live.get("nodes", [])}

    # 10087393: the inverted edges are gone, and read the other way round.
    for subject, obj in INVERTED:
        assert not [r for r in relations
                    if r["predicate"] == "OBSERVED_IN"
                    and r["subject"] == subject and r["object"] == obj], (
            f"the inverted edge {subject} --OBSERVED_IN--> {obj} is back on the "
            f"living atlas; re-measure and update RESULTAT.md "
            f"({DRIFT_COMMITS['10087393']})")
        assert [r for r in relations
                if r["predicate"] == "OBSERVED_THROUGH"
                and r["subject"] == obj and r["object"] == subject], (
            f"the replacement {obj} --OBSERVED_THROUGH--> {subject} is missing "
            f"on the living atlas ({DRIFT_COMMITS['10087393']})")

    # fe865b95: Q7's premise («no node carries an uncertainty field») is gone.
    assert any("usikkerhet" in node for node in nodes.values()), (
        "no node carries usikkerhet on the living atlas; Q7's key "
        f"({DRIFT_COMMITS['fe865b95']}) may be true again — re-measure")


def test_the_sealed_answer_to_q1_is_no_longer_what_the_living_atlas_says():
    """The drift is not cosmetic: it changes the answers the key recorded."""
    key, evidence = _fixture()
    live = leser_b.svar(bank.load_live(), key, evidence)
    q1 = next(row for row in live if row["id"] == "Q1")
    assert q1["svar"]["observasjon"] == [], (
        "the living atlas answers Q1 the way the sealed key does; the drift "
        "note in RESULTAT.md no longer describes the living atlas")
