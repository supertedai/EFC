"""Locks the fixpoint of the maintenance writers that own the changelog files.

Measured 2026-09-18 (t_9cdf466e) on ``origin/main``: the two generated files
``docs/validation-ledger/data/changelog.json`` and
``docs/public/EFC_Changelog.html`` had TWO writers, fed by two different
inputs. ``changelog_projeksjon.py`` derives them from the git history;
``efc_auto_changelog.py`` (step 8 of ``efc_maintain.py``) derived them from the
WORKING TREE. Two measured consequences:

1. Step 8 wrote the JSON with ``json.dump(..., indent=2)`` — the default
   ``ensure_ascii=True`` — so one maintenance run turned every em dash into
   ``\\u2014`` and merged its own summary into the projection's newest entry.
   Committing the tree exactly as ``efc_maintain.py`` left it made the
   projection rewrite the escapes back to literal dashes, so
   ``efc-changelog-sync`` was red on a tree that was in fixpoint. No commit
   could turn it green.
2. Both writers prepended ``<li>`` rows to the same list. Merging two such
   commits conflicted by construction, and the union was committed with the
   conflict markers still in the file (``docs/public/EFC_Changelog.html``,
   introduced by 207274ad).

These tests change the world rather than read prose. Each builds a throwaway
git repo that carries real copies of the two generated files, runs the writers
that own them — in the documented canonical order, step 8 before the
projection, navbar last — and requires the second pass to leave the tree
byte-identical to the first.

Mutants that must go red:
  * a writer that touches a projection-owned file on a dirty tree
    (``test_step_8_writes_nothing``),
  * a chain whose second pass is not a no-op
    (``test_chain_reaches_a_fixpoint``),
  * an ``ensure_nav`` call site that omits the page name, which silently
    leaves a drifted navbar drifted
    (``test_every_ensure_nav_call_names_its_page``).
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
sys.path.insert(0, str(MAINT))

import changelog_projeksjon as projeksjon  # noqa: E402
import efc_auto_changelog as step_8  # noqa: E402
import efc_navbar_sync as navbar  # noqa: E402

CHANGELOG_HTML = "docs/public/EFC_Changelog.html"
CHANGELOG_JSON = "docs/validation-ledger/data/changelog.json"
PROJECTION_OWNED = (CHANGELOG_HTML, CHANGELOG_JSON)

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "efc-fixture",
    "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
    "GIT_COMMITTER_NAME": "efc-fixture",
    "GIT_COMMITTER_EMAIL": "fixture@example.invalid",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree(repo: Path) -> dict[str, str]:
    """Every file in the fixture repo, so ANY write shows up as a change."""
    out: dict[str, str] = {}
    for path in repo.rglob("*"):
        if path.is_file() and ".git" not in path.parts:
            out[str(path.relative_to(repo))] = _sha256(path)
    return out


@pytest.fixture(autouse=True)
def _repo_untouched():
    """These tests must never write into the checkout they run in."""
    before = {rel: _sha256(ROOT / rel) for rel in PROJECTION_OWNED}
    yield
    after = {rel: _sha256(ROOT / rel) for rel in PROJECTION_OWNED}
    assert after == before, (
        "a writer escaped the fixture and wrote into the real repository — "
        "the fixture is missing a rebinding")


def _git(repo: Path, *args: str) -> str:
    res = subprocess.run(
        ["git", "-c", "init.defaultBranch=main", *args],
        cwd=str(repo), capture_output=True, text=True,
        env={**os.environ, **_GIT_ENV}, timeout=60)
    assert res.returncode == 0, f"git {' '.join(args)}: {res.stderr.strip()}"
    return res.stdout.strip()


def _bind(repo: Path, monkeypatch) -> None:
    """Point the writers at the fixture instead of the real repository.

    Every path a writer might reach for is rebound. Rebinding only ``REPO``
    would leave a writer that uses a module-level path constant — which is
    exactly what the removed second writer did — writing into the real
    checkout, and the guard would pass vacuously.
    """
    monkeypatch.setattr(projeksjon, "REPO", str(repo))
    monkeypatch.setattr(projeksjon, "HTML", str(repo / CHANGELOG_HTML))
    monkeypatch.setattr(projeksjon, "JSON", str(repo / CHANGELOG_JSON))

    for name, value in (
        ("REPO", str(repo)),
        ("PUBLIC", str(repo / "docs" / "public")),
        ("LEDGER_DATA", str(repo / "docs" / "validation-ledger" / "data")),
        ("CHANGELOG_HTML", str(repo / CHANGELOG_HTML)),
        ("CHANGELOG_JSON", str(repo / CHANGELOG_JSON)),
        ("PROJECTION_OWNED", (str(repo / CHANGELOG_HTML),
                              str(repo / CHANGELOG_JSON))),
        ("PROJEKSJON", str(MAINT / "changelog_projeksjon.py")),
    ):
        monkeypatch.setattr(step_8, name, value, raising=False)

    monkeypatch.setattr(navbar, "REPO_ROOT", repo)
    monkeypatch.setattr(navbar, "PUBLIC_ROOT", repo / "docs" / "public")


def _fixture(tmp_path: Path, monkeypatch) -> Path:
    """A throwaway git repo whose history the projection has not seen yet.

    The two generated files are the REAL ones, so the fixture reproduces the
    measured failure (a literal em dash in the JSON) rather than a caricature
    of it. ``last_processed_sha`` points at the seed commit and two later
    commits touch a public-relevant path, so the projection really writes.
    """
    repo = tmp_path / "repo"
    (repo / "docs" / "public").mkdir(parents=True)
    (repo / "docs" / "validation-ledger" / "data").mkdir(parents=True)
    for rel in PROJECTION_OWNED:
        shutil.copy(ROOT / rel, repo / rel)
    (repo / "docs" / "public" / "EFC_Atlas.html").write_text(
        "<html><body><h1>Atlas</h1><p>fixture</p></body></html>\n",
        encoding="utf-8")

    _git(repo, "init", "-q")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "chore: seed the fixture repository")

    start = _git(repo, "rev-parse", "HEAD")
    ledger_json = repo / "docs" / "validation-ledger" / "data" / "ledger.json"
    ledger_json.write_text("{}\n", encoding="utf-8")
    cl = json.loads((repo / CHANGELOG_JSON).read_text(encoding="utf-8"))
    cl.setdefault("metadata", {})["last_processed_sha"] = start
    (repo / CHANGELOG_JSON).write_text(
        json.dumps(cl, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "chore(ledger): record the fixture start point")

    ledger_json.write_text('{"papers": 1}\n', encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-qm", "feat(ledger): fixture change to project")

    _bind(repo, monkeypatch)
    return repo


def _run_chain(repo: Path) -> None:
    """Step 8, then the projection, then the navbar — the canonical tail."""
    assert step_8.main() == 0
    assert projeksjon._hoved() == 0
    assert navbar.main([]) == 0


def test_fixture_makes_the_projection_actually_write(tmp_path, monkeypatch):
    """A fixture where the first pass changes nothing would prove nothing."""
    repo = _fixture(tmp_path, monkeypatch)
    before = _tree(repo)
    _run_chain(repo)
    assert _tree(repo) != before
    added = json.loads((repo / CHANGELOG_JSON).read_text(encoding="utf-8"))
    summaries = {e.get("summary") for e in added["changes"]}
    assert "feat(ledger): fixture change to project" in summaries
    assert len(added["changes"]) > 1


def test_chain_reaches_a_fixpoint(tmp_path, monkeypatch):
    """Two consecutive passes over the whole chain must leave no diff."""
    repo = _fixture(tmp_path, monkeypatch)
    _run_chain(repo)
    after_first = _tree(repo)
    _run_chain(repo)
    assert _tree(repo) == after_first, (
        "the second pass rewrote a generated file — the chain is not in "
        "fixpoint, so the changelog-sync gate cannot stay green")


def test_json_is_written_without_ascii_escapes(tmp_path, monkeypatch):
    """The measured signature: ensure_ascii=True turns every dash into \\u2014."""
    repo = _fixture(tmp_path, monkeypatch)
    _run_chain(repo)
    raw = (repo / CHANGELOG_JSON).read_bytes()
    assert b"\\u2014" not in raw
    assert "\u2014".encode() in raw, "the fixture's em dash disappeared"
    # And the projection's bytes survive the next pass unchanged.
    _run_chain(repo)
    assert (repo / CHANGELOG_JSON).read_bytes() == raw


def test_step_8_writes_nothing(tmp_path, monkeypatch):
    """Step 8 detects; it writes no file at all, least of all a projected one."""
    repo = _fixture(tmp_path, monkeypatch)
    # A dirty, changelog-relevant tree — exactly the state step 8 used to
    # write from, and the state efc_maintain.py always leaves behind.
    (repo / "docs" / "public" / "EFC_Atlas.html").write_text(
        "<html><body><h1>Atlas</h1><p>fixture changed</p></body></html>\n",
        encoding="utf-8")
    before = _tree(repo)
    assert step_8.main() == 0
    assert _tree(repo) == before, (
        "step 8 wrote a file the projection owns — the gate can then be red "
        "on a tree that is in fixpoint")


def test_projection_keeps_the_active_page_marker(tmp_path, monkeypatch):
    """One canonical navbar form: the red marker survives the projection."""
    repo = _fixture(tmp_path, monkeypatch)
    _run_chain(repo)
    html = (repo / CHANGELOG_HTML).read_text(encoding="utf-8")
    assert "color:#c22;" in html
    assert navbar.render_nav("EFC_Changelog.html") in html


def test_every_ensure_nav_call_names_its_page():
    """Without the page name ensure_nav is a no-op — a silent drift hole."""
    offenders = []
    for path in sorted(MAINT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            called = getattr(node.func, "id", None) or getattr(node.func, "attr", "")
            if called.endswith("ensure_nav") and len(node.args) < 2:
                offenders.append(f"{path.name}:{node.lineno}")
    assert offenders == [], (
        "these ensure_nav call sites omit the page name, so they leave a "
        f"drifted navbar drifted: {offenders}")


def test_no_committed_conflict_markers():
    """The union of two writers into one region was committed unresolved."""
    res = subprocess.run(
        ["git", "grep", "-n", "-E", r"^(<{7}|>{7})( |$)", "--", "."],
        cwd=str(ROOT), capture_output=True, text=True, timeout=120)
    assert res.returncode in (0, 1), res.stderr.strip()
    assert res.stdout.strip() == "", f"conflict markers committed:\n{res.stdout}"

    for rel in PROJECTION_OWNED:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert "\n=======\n" not in text, f"{rel}: conflict separator committed"


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-q"]))
