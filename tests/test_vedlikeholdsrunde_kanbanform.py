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


@pytest.fixture
def run_round(monkeypatch, tmp_path):
    """Run hoved() with everything around it replaced: no hermes, no writes."""
    made = []
    monkeypatch.setattr(vr, "_kun_vert", lambda dry: True)
    monkeypatch.setattr(vr, "LAAS", tmp_path / "lock")
    monkeypatch.setattr(vr, "_kjor", lambda name, script, extra: (0, {"feil": [{"x": 1}]}))
    monkeypatch.setattr(vr, "_lag_kort", lambda title, body, dry: made.append(title) or True)
    monkeypatch.setattr(vr.sys, "argv", ["vedlikeholdsrunde.py"])

    def run(kanban_answer):
        monkeypatch.setattr(vr.subprocess, "run", lambda *a, **k: kanban_answer)
        made.clear()
        return vr.hoved(), list(made)
    return run


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
