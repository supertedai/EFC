"""Tests for scripts/maintenance/efc_spraakvakt.py, the repo-wide language gate.

What must not rot, and why each test exists:

* The rule's SCOPE is a decision. The gate is green only while the committed
  baseline matches the tree, so a new Norwegian string in a guarded path fails
  the PR that adds it -- and a translation that removes debt shows up as slack
  instead of passing silently.
* The rule's FALSE POSITIVES are measured, not promised. The class token
  measured on 2026-09-17 was read as Norwegian by a word-boundary rule; the
  test pins the rule that removes it and pins the limit that comes with it.
* The rule's LIMITS are declared and locked: hyphen-adjacent prose reads as an
  identifier, and that is asserted here so nobody discovers it later.

The Norwegian SAMPLE TEXT is read from the vocabulary instead of being written
into this file: a test suite for a language gate would otherwise be the largest
single piece of debt in the gate's own baseline. It also makes the assertions
true statements about the vocabulary the gate actually uses.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
sys.path.insert(0, str(MAINT))

import efc_spraakvakt as gate  # noqa: E402

WORDS, LABELS = gate.read_vocabulary()
PATTERN = gate.build_pattern(WORDS)
WORD = WORDS[0]                       # sample prose, from the rule's own list
LABEL = sorted(LABELS)[0]             # sample label, from the rule's own list
WORD_BOUNDARY = re.compile(r"\b(" + "|".join(WORDS) + r")\b", re.IGNORECASE)
GAP_PAGE = ROOT / "docs" / "public" / "EFC_Gap_Analysis.html"
WORKFLOW = ROOT / ".github" / "workflows" / "efc-spraak.yml"


# --------------------------------------------------------------------------
# the detector rule
# --------------------------------------------------------------------------

def test_a_word_in_prose_is_a_hit():
    assert gate.hits(f"a line with {WORD} in it", PATTERN, LABELS) == [WORD]


def test_an_identifier_fragment_is_not_prose():
    """R1. Measured: the class token badge-med produced 10 hits in one page."""
    assert gate.hits(f'<span class="badge-{WORD}">', PATTERN, LABELS) == []
    assert gate.hits(f"badge_{WORD} = 1", PATTERN, LABELS) == []


def test_the_declared_labels_are_not_hits():
    """R2. Measured: the severity label MED produced 7 hits in the same page."""
    assert gate.hits(f"<td>{LABEL}</td>", PATTERN, LABELS) == []
    assert gate.hits(f"level {LABEL} here", PATTERN, LABELS) == []


def test_the_lower_case_word_the_labels_shadow_is_still_a_hit():
    """The exclusion is the declared uppercase label, not the word itself."""
    masked = [w for w in WORDS if w.lower() in {x.lower() for x in LABELS}]
    assert masked, "the vocabulary no longer shadows a label; re-measure R2"
    plain = masked[0].lower()
    assert gate.hits(f"a line with {plain} in it", PATTERN, LABELS) == [plain]


def test_hyphen_adjacent_prose_is_the_declared_limit():
    """R1's cost, locked: a hyphen-joined compound is read as an identifier.

    This asserts a LIMIT, not a virtue. If the rule is ever made sharper, this
    test is the one that has to be rewritten deliberately.
    """
    assert gate.hits(f"{WORD}-{WORD}", PATTERN, LABELS) == []


def test_the_measured_false_positive_class_of_one_real_page():
    """docs/public/EFC_Gap_Analysis.html: measured, re-runnable.

    2026-09-17: 17 hits under a word-boundary rule, of which 10 were the class
    token and 7 the visible label -- the page is English. 2026-09-18: 0 hits
    under the declared rule. The two numbers together are the point: the rule
    removes a real class, and it does not remove prose.
    """
    text = GAP_PAGE.read_text(encoding="utf-8")
    boundary = len(WORD_BOUNDARY.findall(text))
    declared = len(gate.hits(text, PATTERN, LABELS))
    assert declared == 0, (
        f"{GAP_PAGE.name} has {declared} hit(s) under the declared rule; the "
        f"page was measured clean (the class token and the label were the "
        f"whole measured class)")
    assert boundary - declared >= 10, (
        f"the measured false-positive class is no longer visible: {boundary} "
        f"hits under a word boundary, {declared} under the declared rule. If "
        f"the page was renamed or rewritten, re-measure and record the number.")


def test_the_exemption_is_exactly_the_rule_itself():
    assert set(gate.EXEMPT) == {"scripts/maintenance/spraak-ord.json"}


def test_the_prefix_exemption_is_exactly_frozen_reviews():
    assert set(gate.EXEMPT_PREFIXES) == {"docs/validation-ledger/reviews/deleg_7f3e9a1c/"}


# --------------------------------------------------------------------------
# a synthetic tree: the ratchet, and the mutation proof
# --------------------------------------------------------------------------

def _tree(tmp_path: Path, files: dict[str, str], baseline: dict | None = None,
          vocabulary: bool = True) -> Path:
    root = tmp_path / "tree"
    if vocabulary:
        target = root / "scripts" / "maintenance" / "spraak-ord.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((MAINT / "spraak-ord.json").read_text(encoding="utf-8"),
                          encoding="utf-8")
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    if baseline is not None:
        (root / "baseline.json").write_text(json.dumps(baseline), encoding="utf-8")
    return root


def _scan(root: Path, capsys) -> tuple[int, dict]:
    rc = gate.main(["--root", str(root), "--baseline",
                    str(root / "baseline.json"), "--json"])
    return rc, json.loads(capsys.readouterr().out)


CLEAN = "public/graph/page.yaml"
GUARDED = "scripts/maintenance/tool.py"


def test_a_clean_tree_passes(tmp_path, capsys):
    root = _tree(tmp_path, {CLEAN: "all English here\n"}, {"files": {}})
    rc, out = _scan(root, capsys)
    assert rc == 0, out
    assert out["debt"] == {"files": 0, "hits": 0}


@pytest.mark.parametrize("run", [1, 2, 3])
def test_mutated_tree_fails_and_restored_tree_passes(tmp_path, capsys, run):
    """mutated = FAIL naming the file, restored = PASS. Repeated on purpose:
    a verdict that flaps between two runs is not a verdict."""
    baseline = {"files": {GUARDED: {"count": 1}}}
    root = _tree(tmp_path, {CLEAN: "clean\n", GUARDED: f"one {WORD} line\n"},
                 baseline)
    rc, out = _scan(root, capsys)
    assert rc == 0, out

    path = root / GUARDED
    original = path.read_text(encoding="utf-8")
    path.write_text(original + f"and another {WORD} line\n", encoding="utf-8")
    rc, out = _scan(root, capsys)
    assert rc == 1, out
    assert [f["file"] for f in out["new"]] == [GUARDED]
    assert out["new"][0]["excess"] == 1

    path.write_text(original, encoding="utf-8")
    rc, out = _scan(root, capsys)
    assert rc == 0, out
    assert out["new"] == []


def test_a_guarded_file_the_baseline_never_saw_is_a_finding(tmp_path, capsys):
    root = _tree(tmp_path, {CLEAN: "clean\n", GUARDED: f"one {WORD} line\n"},
                 {"files": {}})
    rc, out = _scan(root, capsys)
    assert rc == 1, out
    assert out["new"][0]["expected"] is None
    assert out["new"][0]["file"] == GUARDED


def test_debt_below_the_baseline_is_slack_not_a_failure(tmp_path, capsys):
    """A translation that removes words must not fail the gate it feeds."""
    root = _tree(tmp_path, {GUARDED: "clean now\n"},
                 {"files": {GUARDED: {"count": 5}}})
    rc, out = _scan(root, capsys)
    assert rc == 0, out
    assert out["slack"] == [{"file": GUARDED, "count": 0, "expected": 5,
                             "freed": 5}]


def test_the_two_rules_are_clamped_from_both_sides(tmp_path, capsys):
    """The ratchet darf neither let growth through nor reject a reduction."""
    baseline = {"files": {GUARDED: {"count": 2}}}
    for text, expected in ((f"{WORD}\n{WORD}\n", 0),
                           (f"{WORD}\n{WORD}\n{WORD}\n", 1)):
        root = _tree(tmp_path / str(len(text)), {GUARDED: text}, baseline)
        rc, out = _scan(root, capsys)
        assert rc == expected, out


def test_an_area_outside_the_guard_is_counted_but_not_failed(tmp_path, capsys):
    """The scope is reported, not punished: an unlisted area is counted, never
    failed. The repository has one such area today, measured in --grenser."""
    root = _tree(tmp_path, {"internt/notat.md": f"one {WORD} line\n"},
                 {"files": {}})
    rc, out = _scan(root, capsys)
    assert rc == 0, out
    assert out["unlisted_areas"] == [{"area": "internt/", "count": 1}]


def test_an_unreadable_text_file_is_a_finding_and_a_binary_is_not(tmp_path, capsys):
    root = _tree(tmp_path, {CLEAN: "clean\n"}, {"files": {}})
    (root / "docs" / "public").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "public" / "page.html").write_bytes(b"\xff\xfe\x00bad")
    rc, out = _scan(root, capsys)
    assert rc == 1, out
    assert out["unreadable_text"] == ["docs/public/page.html"]

    (root / "docs" / "public" / "page.html").unlink()
    (root / "docs" / "public" / "figure.png").write_bytes(b"\x89PNG\x00")
    rc, out = _scan(root, capsys)
    assert rc == 0, out
    assert out["skipped_binary"] == ["docs/public/figure.png"]


# --------------------------------------------------------------------------
# commit subjects: no window, no baseline
# --------------------------------------------------------------------------

def _git_repo(tmp_path: Path, subjects: list[str]) -> Path:
    root = tmp_path / "repo"
    (root / "scripts" / "maintenance").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "maintenance" / "spraak-ord.json").write_text(
        (MAINT / "spraak-ord.json").read_text(encoding="utf-8"), encoding="utf-8")
    if not (root / ".git").exists():
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root,
                       check=True, stdout=subprocess.DEVNULL)
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(tmp_path)}
    for subject in subjects:
        subprocess.run(["git", "commit", "--allow-empty", "-q", "-m", subject],
                       cwd=root, env=env, check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.PIPE)
    return root


def test_english_subjects_pass_and_one_norwegian_subject_fails(tmp_path, capsys):
    root = _git_repo(tmp_path, ["feat(atlas): add a node",
                                "fix(gate): name the file"])
    rc = gate.main(["--root", str(root), "--commits", "HEAD~1..HEAD", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0, out

    _git_repo(tmp_path, [f"feat(atlas): legg inn {WORD} node"])
    rc = gate.main(["--root", str(root), "--commits", "HEAD~1..HEAD", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1, out
    assert len(out["hits"]) == 1
    assert WORD in out["hits"][0]["subject"]
    assert out["hits"][0]["matches"] == [WORD]


def test_the_commit_rule_has_no_lookback_window(tmp_path, capsys):
    """The repair for the 30-entry changelog window: the range is the window.

    The violating subject sits 39 commits back, far outside any bounded
    lookback, and is still reported. A 30-entry rule would have said nothing.
    """
    root = _git_repo(tmp_path, ["chore: init",
                                f"feat: second, with {WORD} in it"] +
                     [f"chore: filler {i}" for i in range(39)])
    rc = gate.main(["--root", str(root), "--commits", "HEAD~40..HEAD", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1, out
    assert out["commits_read"] == 40
    assert len(out["hits"]) == 1, out["hits"]
    assert out["hits"][0]["sha"] != ""


def test_an_unresolvable_range_is_a_finding_not_an_empty_answer(tmp_path, capsys):
    root = _git_repo(tmp_path, ["feat: one"])
    rc = gate.main(["--root", str(root), "--commits", "no-such-ref..HEAD", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 2, out
    assert "could not be resolved" in out["error"]


# --------------------------------------------------------------------------
# the changelog window, and the tree the gate actually guards
# --------------------------------------------------------------------------

def test_the_changelog_window_is_reported_not_implied(tmp_path, capsys):
    root = _tree(tmp_path, {CLEAN: "clean\n"}, {"files": {}})
    target = root / "docs" / "validation-ledger" / "data"
    target.mkdir(parents=True, exist_ok=True)
    entries = [{"summary": "feat: english entry"}] * 40
    entries[-1] = {"summary": f"feat: older {WORD} entry outside the window"}
    (target / "changelog.json").write_text(
        json.dumps({"changes": entries}), encoding="utf-8")
    rc = gate.main(["--root", str(root), "--changelog", "--vindu", "30", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0, out
    assert out["entries"] == 40
    assert out["entries_outside_window"] == 10
    assert out["hits"] == []
    assert "NOT" in " ".join(out["declared_limits"])

    rc = gate.main(["--root", str(root), "--changelog", "--vindu", "40", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1, out
    assert out["entries_outside_window"] == 0


def _git_tree(tmp_path: Path) -> tuple[Path, dict]:
    """A temp git repo with the vocabulary, ready for content commits."""
    root = tmp_path / "repo"
    (root / "scripts" / "maintenance").mkdir(parents=True, exist_ok=True)
    (root / "scripts" / "maintenance" / "spraak-ord.json").write_text(
        (MAINT / "spraak-ord.json").read_text(encoding="utf-8"), encoding="utf-8")
    env = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid",
           "PATH": "/usr/local/bin:/usr/bin:/bin", "HOME": str(tmp_path)}
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=root, check=True,
                   stdout=subprocess.DEVNULL)
    return root, env


def _commit(root: Path, env: dict, message: str, files: dict[str, str]) -> None:
    for rel, text in files.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
    subprocess.run(["git", "commit", "-q", "-m", message], cwd=root, check=True,
                   env=env, stdout=subprocess.DEVNULL)


def test_a_reference_puts_the_failure_on_the_change_not_on_the_base(tmp_path, capsys):
    """Measured, 2026-09-18, on this gate's own first CI run (PR #530).

    The PR was red for `scripts/atlas_lesing.py` +2 and
    `scripts/maintenance/efc_bro_konvensjon.py` +2 -- files it had never
    touched, because main had grown underneath it after the record was written.
    A gate that blames every PR for its base branch blocks every PR (the wedged
    condition this card was written about). With a reference the rule belongs to
    the change -- and the drift is still REPORTED, never silenced.
    """
    root, env = _git_tree(tmp_path)
    (root / "baseline.json").write_text(json.dumps({"files": {}}),
                                        encoding="utf-8")
    guarded = "public/graph/page.yaml"
    _commit(root, env, "feat: a page with one line",
            {guarded: f"title: a page\nnote: one {WORD} line\n"})

    # Absolute, against a record that never saw the file: a finding.
    rc = gate.main(["--root", str(root), "--baseline", str(root / "baseline.json"),
                    "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1, out
    assert out["new"][0]["file"] == guarded

    # Relative to the commit that carries it: green, and the debt is reported.
    rc = gate.main(["--root", str(root), "--baseline", str(root / "baseline.json"),
                    "--referanse", "HEAD", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0, out
    assert out["new"] == []
    assert out["undeclared_growth"] == [{"file": guarded, "count": 1,
                                         "recorded": None}]
    assert out["measured_against"] == "the reference HEAD"

    # A second commit that makes the file worse IS this change's finding.
    _commit(root, env, "feat: another line",
            {guarded: f"title: a page\nnote: one {WORD} line\nmore: {WORD}\n"})
    rc = gate.main(["--root", str(root), "--baseline", str(root / "baseline.json"),
                    "--referanse", "HEAD^", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 1, out
    assert out["new"] == [{"file": guarded, "count": 2, "expected": 1,
                           "excess": 1}]


def test_an_unreadable_reference_is_a_finding_not_a_false_blame(tmp_path, capsys):
    """Falling back to the record would blame this change for the base branch's
    debt -- the exact failure the reference exists to prevent. So a reference
    that cannot be read is exit 2: could not measure."""
    root, env = _git_tree(tmp_path)
    (root / "baseline.json").write_text(json.dumps({"files": {}}),
                                        encoding="utf-8")
    _commit(root, env, "feat: one", {"public/graph/page.yaml": "clean\n"})
    rc = gate.main(["--root", str(root), "--baseline", str(root / "baseline.json"),
                    "--referanse", "no-such-ref", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 2, out
    assert "could not be read" in out["error"]
    assert "new" not in out, "nothing may be blamed on the change"


def test_baseline_generator_records_what_the_scan_finds(tmp_path, capsys):
    """--oppdater-baseline is the generator side of the ratchet. If it writes
    anything other than what the scan found, the gate and the debt drift."""
    root = _tree(tmp_path, {GUARDED: f"{WORD}\n{WORD}\n"}, None)
    rc = gate.main(["--root", str(root), "--baseline",
                    str(root / "baseline.json"), "--oppdater-baseline"])
    capsys.readouterr()
    assert rc == 0
    written = json.loads((root / "baseline.json").read_text(encoding="utf-8"))
    assert written["files"] == {GUARDED: {"count": 2}}, written["files"]
    assert written["measured_scope"]["debt_recorded"] == 2
    rc = gate.main(["--root", str(root), "--baseline",
                    str(root / "baseline.json")])
    capsys.readouterr()
    assert rc == 0, "the freshly written baseline must be green on its own tree"


def test_the_declared_limits_cover_the_guard_and_name_the_rest(tmp_path, capsys):
    """--grenser is the measurement of what the gate does NOT see."""
    root = _tree(tmp_path, {GUARDED: f"one {WORD} line\n",
                            "internt/notat.md": f"one {WORD} line\n"},
                 {"files": {}})
    rc = gate.main(["--root", str(root), "--grenser", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0, out
    guarded = {a["area"] for a in out["areas"] if a["scope"] == "guarded"}
    assert guarded == set(gate.GUARDED)
    assert {u["area"] for u in out["unlisted_areas_with_hits"]} == {"internt/"}
    assert out["declared_limits"], "the limits must be stated, not implied"
    assert set(out["exception"]) == set(gate.EXEMPT)


def test_this_change_does_not_grow_the_guard_against_its_parent(capsys):
    """The acceptance criterion, run in CI: this change adds no Norwegian.

    The parent revision is the reference. In a PR checkout HEAD is the merge
    commit whose first parent is the base branch tip, so the check answers «did
    this change grow the guard» -- and never «is the base branch clean», which
    would wedge every PR the moment something landed there.
    """
    parent = subprocess.run(["git", "rev-parse", "--verify", "HEAD^"], cwd=ROOT,
                            capture_output=True, text=True)
    if parent.returncode != 0:
        pytest.skip("no parent revision in this checkout (shallow clone)")
    rc = gate.main(["--json", "--referanse", "HEAD^"])
    out = json.loads(capsys.readouterr().out)
    assert rc == 0, out["new"]
    assert out["new"] == []
    assert out["unreadable_text"] == []


def test_the_report_accounts_for_every_hit_against_the_record(capsys):
    """No hit may be invisible, and none may be invented.

    debt - record == the sum of the per-file deltas, exactly. That is the
    property that makes «recorded, never silenced» checkable when the tree is
    allowed to carry debt above the record (a base branch that grew after the
    record was written).
    """
    rc = gate.main(["--json"])
    out = json.loads(capsys.readouterr().out)
    assert rc in (0, 1), out
    delta = sum(d["count"] - (d["recorded"] or 0) for d in out["record_delta"])
    assert out["debt"]["hits"] - out["record"]["hits"] == delta, (
        f"the report does not explain itself: {out['debt']['hits']} debt minus "
        f"{out['record']['hits']} recorded is not {delta}")
    for d in out["undeclared_growth"]:
        assert d["recorded"] is None or d["recorded"] < d["count"]
    committed = json.loads((MAINT / "spraak-baseline.json").read_text(
        encoding="utf-8"))
    assert committed["files"], "the record must name the files it records"
    assert committed["measured_scope"]["debt_recorded"] == sum(
        v["count"] for v in committed["files"].values())


def test_the_workflow_runs_on_the_paths_the_gate_guards():
    """CI coverage is part of the rule, so it is asserted, not assumed."""
    yaml = pytest.importorskip("yaml")
    text = WORKFLOW.read_text(encoding="utf-8")
    doc = yaml.safe_load(text)
    triggers = doc[True] if True in doc else doc["on"]
    paths = triggers["pull_request"]["paths"]
    assert paths == triggers["push"]["paths"], (
        "push and pull_request must watch the same paths (the lesson from "
        "t_0d65ccdf)")
    for guarded in gate.GUARDED:
        assert f"{guarded}**" in paths, f"{guarded} is guarded but not watched"
    assert "efc_spraakvakt.py" in text
    assert "--commits" in text, "the source-level rule must run in CI"
    assert "--referanse" in text, (
        "the scan must be measured against the base revision of the change, or "
        "every PR is blamed for whatever landed on the base branch")
    assert "git push" not in text and "git commit" not in text


def test_the_changelog_step_and_this_gate_share_one_vocabulary():
    """The two language rules must not drift apart about what is Norwegian.

    Either the changelog step inlines the same alternation, or it has been
    replaced by a call to this gate. Anything else is a second vocabulary.
    """
    changelog_workflow = (ROOT / ".github" / "workflows" /
                          "efc-changelog-sync.yml")
    text = changelog_workflow.read_text(encoding="utf-8")
    if "efc_spraakvakt.py" in text:
        return
    first_word = re.escape(WORDS[0])
    match = re.search(r"\b(" + first_word + r"\|[^)\"]+)", text)
    assert match, ("the changelog language step has neither the shared "
                   "alternation nor a call to this gate")
    inline = match.group(1).split("|")
    assert inline == WORDS, (
        f"the changelog step and spraak-ord.json disagree: "
        f"{set(inline) ^ set(WORDS)}")
