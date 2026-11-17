"""vedlikeholdsrunde: the kanban list may arrive as a list OR an object.

Measured 2026-09-25: `hermes kanban list --json` answers with a list, and the
old code crashed on `.get` -- the unit was failed from 2026-09-21.
"""
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "maintenance" / "vedlikeholdsrunde.py"
spec = importlib.util.spec_from_file_location("vedlikeholdsrunde", SCRIPT)
vr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vr)

CARDS = [
    {"title": "[vedlikehold] lenker-funn", "status": "ready"},
    {"title": "[vedlikehold] eierskap-funn", "status": "done"},
    {"title": "[vedlikehold] blast-radius-funn", "status": "archived"},
]
OPEN = {"[vedlikehold] lenker-funn"}


def test_list_gives_open_titles():
    assert vr._open_titles_from_list(json.dumps(CARDS)) == OPEN


def test_object_with_tasks_still_works():
    assert vr._open_titles_from_list(json.dumps({"tasks": CARDS})) == OPEN


def test_object_with_rows_still_works():
    assert vr._open_titles_from_list(json.dumps({"rows": CARDS})) == OPEN


def test_unreadable_answer_is_none_not_empty_set():
    # An empty set would mean "no open cards" and create duplicate cards.
    assert vr._open_titles_from_list("not json") is None
    assert vr._open_titles_from_list("") is None
    assert vr._open_titles_from_list("42") is None


def test_empty_list_is_empty_set():
    assert vr._open_titles_from_list("[]") == set()


def test_object_without_list_is_none():
    assert vr._open_titles_from_list(json.dumps({"error": "something failed"})) is None
    assert vr._open_titles_from_list(json.dumps({"tasks": None})) is None


def test_list_of_non_objects_is_none():
    assert vr._open_titles_from_list(json.dumps(["a", "b"])) is None


# -- hoved(): what actually prevents duplicate cards ------------------------

class _Answer:
    def __init__(self, rc, out):
        self.returncode, self.stdout, self.stderr = rc, out, ""


class _Run:
    """One round's outcome: unpacks as (rc, created titles), keeps the bodies."""

    def __init__(self, rc: int, made: list[str], kropper: dict[str, str]):
        self.rc, self.made, self.kropper = rc, made, kropper

    def __iter__(self):
        return iter((self.rc, self.made))


@pytest.fixture
def run_round(monkeypatch, tmp_path):
    """Run hoved() with everything around it replaced: no hermes, no writes.

    ``_kjor`` answers a triple (rc, the answer, readable). A test that wants
    one class to fail passes its own triple for that class through ``sjekker``;
    every other class answers the default.
    """
    made: list[str] = []
    kropper: dict[str, str] = {}
    svar: dict[str, tuple] = {}
    monkeypatch.setattr(vr, "_kun_vert", lambda dry: True)
    monkeypatch.setattr(vr, "LAAS", tmp_path / "lock")
    monkeypatch.setattr(vr, "_kjor",
                        lambda name, script, extra: svar.get(
                            name, (0, {"feil": [{"x": 1}]}, True)))

    def lag_kort(title, body, dry):
        made.append(title)
        kropper[title] = body
        return True

    monkeypatch.setattr(vr, "_lag_kort", lag_kort)
    monkeypatch.setattr(vr.sys, "argv", ["vedlikeholdsrunde.py"])

    def run(kanban_answer, sjekker=None):
        svar.clear()
        svar.update(sjekker or {})
        monkeypatch.setattr(vr.subprocess, "run", lambda *a, **k: kanban_answer)
        made.clear()
        kropper.clear()
        return _Run(vr.hoved(), list(made), dict(kropper))

    return run


def _clean_answers() -> dict:
    return {navn: (0, {}, True) for navn, _, _ in vr.SJEKKER}


def test_round_kanban_rc_failure_creates_no_cards_and_exits_3(run_round):
    rc, made = run_round(_Answer(1, ""))
    assert made == [] and rc == 3


def test_round_rc_failure_counts_even_with_valid_json(run_round):
    # A CLI that exits non-zero after printing an empty list has NOT said
    # "no open cards" -- rc decides, not how tidy stdout looks.
    rc, made = run_round(_Answer(1, "[]"))
    assert made == [] and rc == 3


def test_round_unreadable_kanban_creates_no_cards_and_exits_3(run_round):
    rc, made = run_round(_Answer(0, "not json"))
    assert made == [] and rc == 3


def test_round_list_without_open_cards_creates_cards(run_round):
    rc, made = run_round(_Answer(0, json.dumps([{"title": "old", "status": "done"}])))
    assert rc == 0 and made  # findings exist and no open cards => cards created


def test_round_open_card_with_same_title_is_skipped(run_round):
    open_card = [{"title": "[vedlikehold] eierskap-funn", "status": "ready"}]
    rc, made = run_round(_Answer(0, json.dumps(open_card)))
    assert rc == 0
    assert "[vedlikehold] eierskap-funn" not in made


# -- a check that could not measure is a finding, never "0 findings" --------

# The measured failure (2026-10-05, t_c2c0ded1): statement_graph_check.py died
# with ModuleNotFoundError, and the round printed "statement-graf: rc=1,
# 0 funn", created no card and exited 0. The card's body carries the raw answer.
KRASJ = {"raa": "Traceback (most recent call last):\n"
                "ModuleNotFoundError: No module named 'yaml'"}


def test_round_crashed_check_creates_a_card_not_zero_findings(run_round):
    svar = _clean_answers()
    svar["statement-graf"] = (1, KRASJ, False)
    rc, made = run_round(_Answer(0, "[]"), svar)
    assert made == ["[vedlikehold] statement-graf-funn"]
    assert rc == 1  # a measurement that failed must fail the weekly unit too


def test_round_card_body_names_the_failed_measurement(run_round):
    svar = _clean_answers()
    svar["eierskap"] = (1, KRASJ, False)
    utfall = run_round(_Answer(0, "[]"), svar)
    kropp = utfall.kropper["[vedlikehold] eierskap-funn"]
    feil = json.loads(kropp.split("```json\n")[1].split("\n```")[0])[0]
    assert feil["type"] == vr.MANGLENDE_MALING
    assert feil["check"] == "eierskap"
    assert feil["raa"] == KRASJ["raa"]
    assert "MEASURED" in kropp


def test_round_clean_run_creates_no_cards_and_exits_zero(run_round):
    rc, made = run_round(_Answer(0, "[]"), _clean_answers())
    assert rc == 0 and made == []


def test_unreadable_answer_is_a_finding_not_an_empty_list():
    funn, maalt = vr._funn_fra("statement-graf", 1, KRASJ, False)
    assert maalt is False
    assert [f["type"] for f in funn] == [vr.MANGLENDE_MALING]


def test_nonzero_exit_without_a_recognised_finding_is_a_finding():
    funn, maalt = vr._funn_fra("eierskap", 1, {}, True)
    assert maalt is False and funn[0]["type"] == vr.MANGLENDE_MALING


def test_zero_exit_without_findings_is_clean():
    funn, maalt = vr._funn_fra("eierskap", 0, {"feil": []}, True)
    assert maalt is True and funn == []


def test_recognised_findings_are_still_read_from_their_keys():
    ut = {"harde": [{"a": 1}], "dangling_reference": [{"b": 2}]}
    funn, maalt = vr._funn_fra("statement-graf", 1, ut, True)
    assert maalt is True and len(funn) == 2


def test_bench_gap_is_a_measurement_but_a_crash_is_not():
    # A readable exit 1 from the bench IS its finding channel (a gap); a crash
    # arrives unreadable and must not be filed as a gap.
    funn, maalt = vr._funn_fra("verifier-bench", 1, {}, True)
    assert maalt is True and funn == [{"type": "bench_gap"}]
    funn, maalt = vr._funn_fra("verifier-bench", 1, KRASJ, False)
    assert maalt is False and funn[0]["type"] == vr.MANGLENDE_MALING


def test_kjor_reads_a_crashing_check_as_unreadable(tmp_path, monkeypatch):
    """A real subprocess that dies with a traceback on stderr and exit 1."""
    (tmp_path / "krasj.py").write_text(
        "import sys\n"
        "sys.stderr.write(\"Traceback (most recent call last):\\nboom\\n\")\n"
        "raise SystemExit(1)\n", encoding="utf-8")
    monkeypatch.setattr(vr, "MAINT", tmp_path)
    rc, ut, leste = vr._kjor("x", "krasj.py", [])
    assert rc == 1 and leste is False
    assert "boom" in ut["stderr"]


def test_kjor_reads_a_timeout_as_unreadable(monkeypatch):
    """Measured 2026-09-21 (t_470cf3c0): one hanging check killed the round."""
    def henger(*a, **k):
        raise vr.subprocess.TimeoutExpired(cmd="x", timeout=300)

    monkeypatch.setattr(vr.subprocess, "run", henger)
    rc, ut, leste = vr._kjor("x", "sjekk.py", [])
    assert leste is False and rc == 124


def test_round_with_a_really_crashing_check_creates_one_card(tmp_path, monkeypatch):
    """End to end: no double for _kjor, a check that crashes on stdout.

    This is the exact measurement from the card: a check answers rc != 0 with a
    traceback on stdout, and the round must open ONE card, not zero.
    """
    (tmp_path / "krasj.py").write_text(
        "import sys\n"
        "sys.stdout.write(\"Traceback (most recent call last):\\n\"\n"
        "                 \"ModuleNotFoundError: No module named 'yaml'\\n\")\n"
        "raise SystemExit(1)\n", encoding="utf-8")
    laget: list[str] = []
    kropper: dict[str, str] = {}

    def lag_kort(title, body, dry):
        laget.append(title)
        kropper[title] = body
        return True

    monkeypatch.setattr(vr, "MAINT", tmp_path)
    monkeypatch.setattr(vr, "SJEKKER", [("statement-graf", "krasj.py", [])])
    monkeypatch.setattr(vr, "_lag_kort", lag_kort)
    monkeypatch.setattr(vr.sys, "argv", ["vedlikeholdsrunde.py", "--dry-run"])
    assert vr.hoved() == 1
    assert laget == ["[vedlikehold] statement-graf-funn"]
    assert "No module named 'yaml'" in kropper["[vedlikehold] statement-graf-funn"]

