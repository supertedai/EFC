"""Tests for scripts/maintenance/changelog_projeksjon.py — the projection start must exist.

What must not rot: last_processed_sha is stamped from the commit the projection
ran on, so a squash-merge (or a deleted branch) can leave it on no branch at
all. Measured 2026-09-17: main's recorded 72d91914… was squashed to 1b51a04e;
every run — on main and on every PR — then died with «fatal: Invalid revision
range», so no change whatsoever could turn the gate green. The resolver must
repair such a start deterministically, and must NOT touch a start that already
resolves (a repaired-gate regression would silently re-project history).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
sys.path.insert(0, str(MAINT))

import changelog_projeksjon as cp  # noqa: E402

PHANTOM = "deadbeef" * 5  # 40 hex chars, resolves to nothing


def test_unknown_sha_does_not_resolve():
    assert cp._finnes(PHANTOM) is False
    assert cp._finnes("") is False


def test_head_resolves():
    assert cp._finnes("HEAD") is True


def test_unreachable_start_is_repaired_to_a_real_commit():
    repaired = cp._los_opp_startpunkt(PHANTOM)
    assert repaired != PHANTOM, "a phantom start must not be echoed back"
    assert cp._finnes(repaired), "the repaired start must resolve in this repo"
    # Deterministic: the main line is the documented first fallback.
    if cp._finnes("origin/main"):
        assert repaired == cp._git("rev-parse", "origin/main")


def test_resolvable_start_is_untouched():
    head = cp._git("rev-parse", "HEAD")
    assert cp._los_opp_startpunkt(head) == head


def test_repair_is_idempotent():
    once = cp._los_opp_startpunkt(PHANTOM)
    assert cp._los_opp_startpunkt(once) == once, (
        "the repaired start must itself be stable, or every run rewrites "
        "the projection start")


# --- the window the repair jumps over (t_f610686f, measured 2026-09-18) ------

def _dangling_commit() -> str:
    """A commit object that exists here but that HEAD does not descend from."""
    tree = cp._git("rev-parse", "HEAD^{tree}")
    env = dict(os.environ, GIT_AUTHOR_NAME="test", GIT_AUTHOR_EMAIL="t@local",
               GIT_COMMITTER_NAME="test", GIT_COMMITTER_EMAIL="t@local")
    r = subprocess.run(["git", "commit-tree", tree, "-m", "dangling test"],
                       capture_output=True, text=True, cwd=cp.REPO, env=env)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_object_existence_is_not_enough_for_a_start():
    """A side branch's commit resolves but yields the wrong range: measured
    2026-09-18, a clone that once fetched a deleted branch kept the object, so
    `git log <rev>..HEAD` silently dropped everything that branch carried."""
    dangling = _dangling_commit()
    assert cp._finnes(dangling) is True
    assert cp._i_historien(dangling) is False
    cl = {"metadata": {"last_processed_sha": dangling}, "changes": []}
    start = cp._velg_startpunkt(cl)
    assert start != dangling
    assert cp._i_historien(start)


def test_the_window_the_repair_would_skip_is_projected():
    """The documented fallback (origin/main) looks forward; on `main` its range
    is empty, so four public-relevant commits were never projected. The start
    must move back to the newest entry HEAD still descends from."""
    eldre = cp._git("rev-parse", "HEAD~3")
    cl = {"metadata": {"last_processed_sha": PHANTOM}, "changes": [{"id": eldre}]}
    assert cp._velg_startpunkt(cl) == eldre, (
        "an unusable start must not silently skip the window: project from the "
        "newest entry HEAD still descends from, not from origin/main")


# --- the language rule at the source (t_f610686f) ---------------------------

def test_declared_english_form_is_used_and_flagged():
    kort = "dddddddddddd"
    tekst, deklarert = cp._summary(
        {"sha": kort + "0" * 28, "melding": "feat(x): norsk emne"},
        {kort: "feat(x): an English subject"})
    assert tekst == "feat(x): an English subject"
    assert deklarert is True


def test_undeclared_norwegian_subject_is_refused():
    with pytest.raises(SystemExit):
        cp._summary({"sha": "a" * 40, "melding": "fix(x): noe som ble endret"}, {})


def test_english_subject_needs_no_declaration():
    melding = "fix(x): the projection start was repaired"
    tekst, deklarert = cp._summary({"sha": "b" * 40, "melding": melding}, {})
    assert (tekst, deklarert) == (melding, False)


def test_declared_forms_are_shaped_like_shas_and_are_english():
    deklarert = cp._deklarerte_summaries()
    assert deklarert, "the declared English forms moved — the gate covers them"
    for sha, tekst in deklarert.items():
        assert len(sha) == 12 and all(c in "0123456789abcdef" for c in sha)
        assert not cp.NORSKE_ORD.search(tekst), tekst


# --- the two artifacts must not drift apart ---------------------------------

def _lastet():
    with open(cp.JSON, encoding="utf-8") as f:
        cl = json.load(f)
    with open(cp.HTML, encoding="utf-8") as f:
        return cl, f.read()


def test_every_entry_with_an_id_is_on_the_page_verbatim():
    """The page is generated from the entry, so the row must match it exactly.
    Drift here is what left an unresolved merge conflict on the page."""
    cl, html = _lastet()
    for e in cl["changes"]:
        if not e.get("id"):
            continue
        li = (f'<li><strong>{e["date"]}</strong> &mdash; {e["summary"]} '
              f'<span style="color:#6b7f9e;">({e["id"]})</span></li>')
        assert html.count(li) == 1, f"{e['id']}: <li> found {html.count(li)} times"


def test_the_page_carries_no_orphan_row():
    """The forward check is not enough: the projection ADDS rows and never
    removes one, so a row whose sha is not an entry survives every
    regeneration. Two such rows (471e154f40e0, 72d919146b23) sat on the page
    inside a committed merge conflict while the forward direction passed."""
    cl, html = _lastet()
    ider = {e.get("id") or e.get("sha") for e in cl["changes"]
            if (e.get("id") or e.get("sha"))}
    funnet = set(re.findall(r"\(([0-9a-f]{12})\)</span></li>", html))
    assert funnet == ider, (
        f"rows with no entry: {sorted(funnet - ider)}; "
        f"entries with no row: {sorted(ider - funnet)}")


def test_no_entry_carries_a_sha_the_repo_does_not_descend_from():
    cl, _ = _lastet()
    dode = [e.get("id") or e.get("sha") for e in cl["changes"]
            if (e.get("id") or e.get("sha")) and not cp._i_historien(e["id"])]
    assert dode == [], f"entries whose sha resolves nowhere: {dode}"


def test_no_entry_trips_the_language_rule():
    """The workflow's own language step checks only the first 30 entries; the
    rule is about every entry."""
    cl, _ = _lastet()
    treff = [e.get("summary", "") for e in cl["changes"]
             if cp.NORSKE_ORD.search(e.get("summary", ""))]
    assert treff == [], treff


def test_the_page_carries_no_merge_conflict():
    _, html = _lastet()
    mark = [l for l in html.split("\n")
            if l.startswith("<<<<<<<") or l.startswith(">>>>>>>")
            or l == "======="]
    assert mark == [], mark
