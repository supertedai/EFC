"""Regression tests for the statement-graph trigger surface.

WHY THIS EXISTS
---------------
Measured 2026-11-12 (card t_56beaebd): `.github/workflows/efc-statement-graph.yml`
listed `public/graph/**` and `public/page-meta/**` but not
`governance/ownership-register.json` (the file the ownership step reads) and not
`wiki/**` (content the register covers). Commit 2690d749 landed on main with
`validate_ownership.py` exiting 1 and no run measured it; the red state only
surfaced on a later PR that happened to touch `public/graph/**`.

A gate that does not run on its inputs is not a gate, and this class of hole is
created by ADDING A STEP without adding its input — so the rule is derived from
the job itself: every `scripts/...` or `tests/...` path a `run:` line names must
be covered by the trigger list. The trigger lists for `pull_request` and `push`
must also be identical: a gate whose verdict is read only on the PR side leaves
main unmeasured, and the two lists drift the moment one is edited alone.
"""
from __future__ import annotations

import fnmatch
import re
from pathlib import Path

import yaml

ROT = Path(__file__).resolve().parents[1]
WORKFLOW = ROT / ".github" / "workflows" / "efc-statement-graph.yml"
STI = re.compile(r"(?:scripts|tests)/[A-Za-z0-9_./-]+\.(?:py|json)")


def _dok() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _wf() -> dict:
    d = _dok()
    # YAML 1.1 reads a bare `on` key as boolean True. The document is still the
    # contract; only the key's spelling is a parser accident.
    return d.get(True) or d.get("on") or {}


def _paths(hendelse: str) -> list[str]:
    return list(_wf()[hendelse]["paths"])


def _run_lines() -> list[str]:
    return [s["run"] for s in _dok()["jobs"]["statement-graph"]["steps"] if "run" in s]


def test_pull_request_and_push_paths_are_identical():
    on = _wf()
    assert _paths("pull_request") == _paths("push"), (
        "the PR list and the main list answer the same question and must not "
        "drift apart; edit both")
    assert on["push"]["branches"] == ["main"]


def test_the_measured_inputs_are_trigger_paths():
    """The two files whose absence produced the measured red-on-main."""
    paths = _paths("pull_request")
    assert "governance/ownership-register.json" in paths
    assert "wiki/**" in paths


def test_every_path_the_job_runs_is_covered_by_a_trigger():
    paths = _paths("pull_request")
    ubeskyttet = sorted(
        sti for run in _run_lines() for sti in STI.findall(run)
        if not any(fnmatch.fnmatch(sti, g) for g in paths))
    assert ubeskyttet == [], (
        "the job runs these files but a change to them would not start the "
        f"job: {ubeskyttet}")


def test_the_link_rule_test_is_both_triggered_and_run():
    """A test that CI never runs, or never starts on a change to itself, is
    documentation — not a gate."""
    paths = _paths("pull_request")
    assert "tests/test_validate_links_wiki.py" in paths
    assert any("tests/test_validate_links_wiki.py" in run for run in _run_lines()), (
        "the link-rule test must be invoked by a step, not only declared")
