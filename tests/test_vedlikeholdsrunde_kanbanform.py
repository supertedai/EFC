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

#: The surface a card gets in these tests. The real one is the board's
#: canonical surface (`/opt/agent-work/EFC`); the tests never touch a disk.
SURFACE = "/opt/agent-work/EFC"


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
    monkeypatch.setattr(vr, "_kanonisk_flate", lambda rot=vr.ROT: SURFACE)
    monkeypatch.setattr(vr, "_lag_kort",
                        lambda title, body, dry, flate: made.append(title) or True)
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


# -- the surface: a card is created ON the board's canonical surface --------
#
# Measured 2026-10-05 (t_216d8d76): the round created a card with the DEFAULT
# `scratch` surface while the body named a code file. The preflight rejected it
# as a code card in a scratch workspace (scratch is always empty), so no worker
# could ever pick it up -- the dispatch loop for maintenance findings was
# broken. The repair: every card carries `--workspace worktree:<surface>`.


def test_card_is_created_with_the_surface(monkeypatch):
    kalt = []

    def fake_run(cmd, **kw):
        kalt.append(list(cmd))
        return _Answer(0, "")

    monkeypatch.setattr(vr.subprocess, "run", fake_run)
    assert vr._lag_kort("[vedlikehold] repo-contract-funn", "kropp", False, SURFACE)
    cmd = kalt[-1]
    assert "--workspace" in cmd, "the card got no work surface"
    assert cmd[cmd.index("--workspace") + 1] == f"worktree:{SURFACE}"


def test_card_without_a_surface_is_never_created(monkeypatch):
    kalt = []
    monkeypatch.setattr(vr.subprocess, "run",
                        lambda *a, **k: kalt.append(a) or _Answer(0, ""))
    assert not vr._lag_kort("[vedlikehold] lenker-funn", "kropp", False, "")
    assert kalt == [], "a card was created without a surface"


def test_a_surface_must_be_the_main_clone_carrying_the_round(tmp_path):
    (tmp_path / ".git").mkdir()
    assert not vr._er_kortflate(str(tmp_path)), "a surface without the round"
    (tmp_path / vr.EGEN_STI.parent).mkdir(parents=True)
    (tmp_path / vr.EGEN_STI).write_text("", encoding="utf-8")
    assert vr._er_kortflate(str(tmp_path))
    assert not vr._er_kortflate(str(tmp_path / "missing"))
    assert not vr._er_kortflate(None)


def test_a_linked_worktree_is_not_a_surface(tmp_path):
    # `.git` as a FILE is a linked worktree: it belongs to one card, never to
    # the round's own cards (the dispatcher anchors `<main clone>/.worktrees`).
    (tmp_path / ".git").write_text("gitdir: /elsewhere/.git\n", encoding="utf-8")
    (tmp_path / vr.EGEN_STI.parent).mkdir(parents=True)
    (tmp_path / vr.EGEN_STI).write_text("", encoding="utf-8")
    assert not vr._er_kortflate(str(tmp_path))


def _patch_round(monkeypatch, tmp_path, surface):
    """Everything around hoved() replaced, and every hermes call captured."""
    cmds = []

    def fake_run(cmd, **kw):
        cmds.append(list(cmd))
        return _Answer(0, "[]")

    monkeypatch.setattr(vr, "_kun_vert", lambda dry: True)
    monkeypatch.setattr(vr, "LAAS", tmp_path / "lock")
    monkeypatch.setattr(vr, "_kjor",
                        lambda navn, skript, ekstra: (0, {"feil": [{"x": 1}]}))
    monkeypatch.setattr(vr, "_kanonisk_flate", lambda rot=vr.ROT: surface)
    monkeypatch.setattr(vr.subprocess, "run", fake_run)
    monkeypatch.setattr(vr.sys, "argv", ["vedlikeholdsrunde.py"])
    return cmds


def test_round_creates_every_card_on_the_resolved_surface(monkeypatch, tmp_path):
    cmds = _patch_round(monkeypatch, tmp_path, SURFACE)
    assert vr.hoved() == 0
    created = [c for c in cmds if "create" in c]
    assert created, "the round created no cards"
    for c in created:
        assert c[c.index("--workspace") + 1] == f"worktree:{SURFACE}"


def test_round_without_a_surface_creates_no_card_and_exits_4(monkeypatch, tmp_path):
    cmds = _patch_round(monkeypatch, tmp_path, None)
    assert vr.hoved() == 4
    assert [c for c in cmds if "create" in c] == [], "a scratch card was created"
