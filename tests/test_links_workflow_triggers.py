"""Trigger tests for the link gate (`.github/workflows/efc-links.yml`).

WHY THIS EXISTS
---------------
Measured 2026-11-12 (card t_c2bb8c06): `scripts/maintenance/validate_links.py`
reads `docs/public/*.html` and `docs/index.html` (15 pages), but no workflow
ran it when one of those pages changed. The only runner was
`efc-statement-graph.yml`, and its trigger list does not include them, so a page
could land on main with a dead internal link and nothing would have measured it.
The same class of hole is created by ADDING A STEP without adding its input —
`wiki/Home.md` landed on main (`2690d749`) with `validate_ownership.py` red and
no run measured it.

The rule is therefore stated twice: once as the workflow's trigger list and
once here as the assertion that the list still covers what the rule reads. Every
assertion is derived from the files themselves — the pages that exist on disk,
the paths the script's own source names, and the workflows that invoke it — so
the guard follows a growing rule instead of a memory of one, and does not have
to be edited when the rule is extended.

Each failure names the file or path that is missing, because a gate that says
only "wrong" sends the next reader back to the card.
"""
from __future__ import annotations

import ast
import re
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIR = ROOT / ".github" / "workflows"
LINKS_WORKFLOW = WORKFLOW_DIR / "efc-links.yml"
LINK_RULE = ROOT / "scripts" / "maintenance" / "validate_links.py"
THIS_TEST = Path(__file__).resolve().relative_to(ROOT).as_posix()
HTML_SURFACE = "docs/public/*.html"
INDEX_PAGE = "docs/index.html"


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _on(doc: dict) -> dict:
    """The trigger block. YAML 1.1 reads a bare `on` key as boolean True.

    The document is still the contract; only the key's spelling is a parser
    accident, so both spellings are accepted rather than one being re-authored.
    """
    return doc.get(True) or doc.get("on") or {}


def _paths(doc: dict, event: str) -> list[str]:
    return list((_on(doc).get(event) or {}).get("paths") or [])


@lru_cache(maxsize=None)
def _regex(pattern: str) -> re.Pattern[str]:
    """GitHub's path-filter glob as a regex.

    `fnmatch` is wrong here: Python's `*` crosses `/`, GitHub's does not. A
    matcher that is too generous makes every check below pass on a nested page
    the gate would never start on.
    """
    out: list[str] = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("^" + "".join(out) + "$")


def _matches(pattern: str, path: str) -> bool:
    return _regex(pattern).match(path) is not None


def _covers_dir(pattern: str, directory: str) -> bool:
    """Would a change anywhere inside `directory` match `pattern`?"""
    return (pattern in ("**", "**/*")
            or pattern == directory
            or pattern.startswith(directory + "/"))


def _chain(node: ast.AST) -> list[str] | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left, right = _chain(node.left), _chain(node.right)
        if left is None or right is None:
            return None
        return left + right
    return []


def _named_paths(source: str) -> set[str]:
    """Relative paths the rule's source names as a `ROOT / "a" / "b"` chain.

    Read from the source rather than hard-coded, so a surface the rule gains
    later (the Markdown wiki, for instance) enters this guard by existing. A
    chain whose literal parts are empty — `page.parent / something_computed` —
    names no fixed path and is skipped.
    """
    found: set[str] = set()
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            parts = _chain(node)
            if parts:
                found.add("/".join(parts))
    return found


def _files_the_rule_reads() -> list[str]:
    """The files the rule enumerates, read by executing its module body.

    `exec` rather than `import`: an import writes `__pycache__` into the tree
    under test, and this test must leave the tree it measures unchanged. The
    module body only builds path lists and regexes — nothing is fetched here.
    """
    namespace: dict = {"__file__": str(LINK_RULE), "__name__": "validate_links_under_test"}
    exec(compile(LINK_RULE.read_text(encoding="utf-8"), str(LINK_RULE), "exec"), namespace)
    found: list[Path] = []
    for name, value in namespace.items():
        if (name.isupper() and isinstance(value, list) and value
                and all(isinstance(v, Path) for v in value)):
            found += value
    return sorted({p.relative_to(ROOT).as_posix() for p in found})


def _run_steps(doc: dict) -> list[str]:
    steps: list[dict] = []
    for job in (doc.get("jobs") or {}).values():
        if isinstance(job, dict):
            steps += [s for s in (job.get("steps") or []) if isinstance(s, dict)]
    return [s["run"] for s in steps if "run" in s]


def _workflows_running_the_rule() -> list[dict]:
    found: list[dict] = []
    for path in sorted(list(WORKFLOW_DIR.glob("*.yml")) + list(WORKFLOW_DIR.glob("*.yaml"))):
        doc = _load(path)
        if not isinstance(doc, dict):
            continue
        if any("validate_links.py" in run for run in _run_steps(doc)):
            found.append(doc)
    return found


def _union_paths(workflows: list[dict]) -> list[str]:
    """The union of the trigger lists, so the guard does not name a workflow.

    A surface is measured if SOME workflow that runs the rule also starts on a
    change to it. Which one is a routing decision (the link step may move out of
    `efc-statement-graph.yml` once the wiki surface is merged); the requirement
    is that nothing the rule reads is triggered by nothing.
    """
    out: list[str] = []
    for doc in workflows:
        on = _on(doc)
        for event in ("pull_request", "push"):
            if event not in on:
                continue
            # An event without a `paths` key starts on every change and
            # therefore covers every surface.
            out += _paths(doc, event) or ["**"]
    return out


# 1
def test_the_public_pages_are_trigger_paths_on_both_events():
    doc = _load(LINKS_WORKFLOW)
    on = _on(doc)
    for event in ("pull_request", "push"):
        assert event in on, (
            f"efc-links.yml has no `{event}` trigger. A link verdict read on "
            "only one side leaves the other side unmeasured")
        paths = _paths(doc, event)
        for path in (HTML_SURFACE, INDEX_PAGE):
            assert path in paths, (
                f"`{path}` is read by validate_links.py but is not a `paths` "
                f"entry of `{event}` in efc-links.yml — a change to it would "
                "not start the gate")


# 2
def test_the_two_trigger_lists_are_identical_and_push_watches_main():
    doc = _load(LINKS_WORKFLOW)
    on = _on(doc)
    assert _paths(doc, "pull_request") == _paths(doc, "push"), (
        "the PR list and the main list answer the same question and must not "
        "drift apart; edit both")
    assert (on.get("push") or {}).get("branches") == ["main"], (
        "push must watch `main`: a fail-closed gate whose verdict is never read "
        "on main cannot catch a direct commit or a merge that bypassed the PR")


# 3
def test_the_rule_the_workflow_and_this_test_are_trigger_paths():
    paths = _paths(_load(LINKS_WORKFLOW), "pull_request")
    for path in (LINK_RULE.relative_to(ROOT).as_posix(),
                 LINKS_WORKFLOW.relative_to(ROOT).as_posix(),
                 THIS_TEST):
        assert path in paths, (
            f"`{path}` is not in the trigger paths of efc-links.yml. A change to "
            "what the gate runs, or to the gate itself, must start the gate — "
            "otherwise the gate's own edit lands unmeasured")


# 4
def test_every_public_page_matches_a_trigger_pattern():
    """Nested pages: the rule's glob is non-recursive, so a page in a
    subdirectory is read by neither the rule nor the trigger. This assertion
    makes that visible instead of silent."""
    paths = _paths(_load(LINKS_WORKFLOW), "pull_request")
    pages = sorted((ROOT / "docs" / "public").rglob("*.html"))
    assert pages, "no pages found under docs/public — the measurement itself is broken"
    unmeasured = [p.relative_to(ROOT).as_posix() for p in pages
                  if not any(_matches(pattern, p.relative_to(ROOT).as_posix())
                             for pattern in paths)]
    assert unmeasured == [], (
        "these public pages match no trigger pattern, so an edit to them starts "
        f"no run: {unmeasured}. If they are nested, the rule's own glob must "
        "become recursive as well — a wider trigger alone would promise a "
        "measurement the rule does not make")


# 5
def test_scope_drift_in_the_rule_is_covered_by_a_workflow_that_runs_it():
    """If the rule starts reading more surfaces, that surface must be triggered.

    Derived, not remembered: the surfaces come from the rule's source, and the
    coverage from every workflow whose `run:` lines invoke the rule. So when the
    Markdown wiki is added to `validate_links.py`, this test starts requiring
    `wiki/**` in a trigger list without being edited — a wiki page that goes
    stale must be measured by the run it causes, not discovered by an unrelated
    HTML PR going red.
    """
    workflows = _workflows_running_the_rule()
    assert workflows, (
        "no workflow in .github/workflows runs validate_links.py: the link rule "
        "is then measured by nothing, and every surface it reads is unguarded")
    patterns = _union_paths(workflows)
    uncovered: list[str] = []

    for path in _files_the_rule_reads():
        if not any(_matches(pattern, path) for pattern in patterns):
            uncovered.append(path)

    for directory in sorted(_named_paths(LINK_RULE.read_text(encoding="utf-8"))):
        if (ROOT / directory).is_dir() and not any(
                _covers_dir(pattern, directory) for pattern in patterns):
            uncovered.append(directory + "/**")

    assert uncovered == [], (
        "validate_links.py reads these surfaces, but no workflow that runs it "
        f"starts on a change inside them: {uncovered}. Add the surface to the "
        "`paths` of a workflow that runs the rule, so the change is measured by "
        "the run it causes")
