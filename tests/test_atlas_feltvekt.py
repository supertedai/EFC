"""Field weight: which fields are actually referenced — measured, not assumed.

Closes K1 in the closure list (`t_7feb0525`). The premise was that several of
the 19 fields are read by nobody, so a new node is forced to fill dead weight.

**The premise did not survive a broad measurement.** The first count looked
only at the five atlas readers and `tests/test_atlas*.py`, giving
`fractal` = 1 reader / 2 tests. Against all of `scripts/` and all of `tests/`,
`fractal` sits in 3 scripts and 4 tests, and `lagdeling` in 4 and 2. That was a
**scope error**, not a finding — the same class as "86 relations" against
"79 published" in ADR-086.

The tests below do three things:
1. Re-measure the references with grep and name every field that falls below
   the limit TODAY.
2. Require that the table covers every requirement, so a new field cannot slip
   in without being weighed.
3. Fail if the table CLAIMS a reference that the measurement says is not there.
   Growth is allowed; a false claim is not.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402

FELT = sorted(atlas_lesing.FELT_REFERANSER)


def _count(field: str, directory: str) -> int:
    """How many .py files under `directory` mention the field."""
    r = subprocess.run(
        ["grep", "-rl", field, f"{directory}/", "--include=*.py"],
        capture_output=True, text=True, cwd=ROT)
    return len([x for x in r.stdout.splitlines() if x.strip()])


def test_the_table_covers_every_requirement():
    """A field demanded of a new node must have been weighed."""
    atlas = atlas_lesing.les_atlas(ROT, ref="HEAD")
    krav = set(atlas_lesing.skjema_krav(atlas)) | set(atlas_lesing.HUSETS_KRAV)
    uncovered = sorted(krav - set(FELT))
    assert not uncovered, (
        f"these requirements are not weighed in FELT_REFERANSER: {uncovered} — "
        f"add them with measured numbers")


def test_the_table_never_claims_a_reference_that_is_not_there():
    """A false claim about usage is worse than an old number."""
    wrong = []
    for field in FELT:
        scripts, tests = atlas_lesing.FELT_REFERANSER[field]
        measured_scripts, measured_tests = (_count(field, "scripts"),
                                            _count(field, "tests"))
        if scripts > measured_scripts or tests > measured_tests:
            wrong.append((field, (scripts, tests),
                          (measured_scripts, measured_tests)))
    assert not wrong, (
        "the table claims more references than exist "
        f"(field, table, measured): {wrong}")


def test_no_requirement_falls_below_the_limit_today():
    """The premise of K1, re-measured. Fails if it becomes true again."""
    below = []
    for field in FELT:
        if field in atlas_lesing.HUSETS_KRAV:
            continue
        if not atlas_lesing.baerer_feltet_noe(field):
            scripts, tests = atlas_lesing.FELT_REFERANSER[field]
            below.append((field, scripts, tests))
    assert not below, (
        "these requirements are barely referenced any more — the premise of K1 "
        f"has become true, and plasser must name them: {below}")


def test_plasser_reports_the_weight_of_every_requirement():
    """The answer must carry the measurement, not just the list."""
    atlas = atlas_lesing.les_atlas(ROT, ref="HEAD")
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    for k in p["krav"]:
        assert "referert_i_skript" in k and "referert_i_tester" in k, k
        assert k["baerer"] is atlas_lesing.baerer_feltet_noe(k["felt"]), k


def test_the_summary_separates_the_two():
    atlas = atlas_lesing.les_atlas(ROT, ref="HEAD")
    p = atlas_lesing.plasser(atlas, "BAO maaling i galakser")
    o = p["oppsummering"]
    assert o["baerer"] + o["uten_leser"] == len(p["krav"]), o
    assert set(o["uten_leser_felt"]) == {
        k["felt"] for k in p["krav"] if not k["baerer"]}, o


def test_the_limit_is_low_on_purpose():
    """The limit is chosen, not measured — it must sit where it can be retested."""
    assert atlas_lesing.GRENSE_SKRIPT == 2
    assert atlas_lesing.GRENSE_TESTER == 2
