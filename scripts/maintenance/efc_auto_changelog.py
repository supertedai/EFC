#!/usr/bin/env python3
"""
EFC changelog step 8 — detect the changes that still have to be committed,
and report them.

Runs after the AI Brain, as step 8 of ``efc_maintain.py``, and compares the
working tree against HEAD. Anything that changed (papers enriched, public
pages updated, ledger data touched) is printed as the entry the changelog
projection will carry once the change is committed.

ONE WRITER PER GENERATED FILE (measured 2026-09-18, t_9cdf466e)
---------------------------------------------------------------
``docs/validation-ledger/data/changelog.json`` and
``docs/public/EFC_Changelog.html`` have exactly ONE writer:
``changelog_projeksjon.py``. The gate ``.github/workflows/efc-changelog-sync.yml``
re-runs that projection in CI and goes red unless the committed files are
byte-identical to its output.

This script used to be a second writer of both, driven by the WORKING TREE
rather than by the git history — two writers into the same region, from two
different inputs. Measured consequences, both on ``main``:

- ``json.dump(cl, f, indent=2)`` used the default ``ensure_ascii=True``, so one
  maintenance run rewrote every em dash in the file as its ``\\u2014`` escape
  and merged its own summary into the projection's newest entry. Committing the
  tree exactly as ``efc_maintain.py`` left it made the projection rewrite the
  escapes back to literal dashes — the gate was red on a tree that was in
  fixpoint.
- Both writers prepended ``<li>`` rows to the same list, so merging two such
  commits conflicted by construction; the union was committed with its conflict
  markers still in the file (``docs/public/EFC_Changelog.html``, introduced by
  207274ad).

This step therefore DETECTS and REPORTS only. It writes neither file; the
projection owns them and derives them from the history that lands.

Usage:
  python3 scripts/maintenance/efc_auto_changelog.py

Meant to run as part of efc_maintain.py pipeline.
"""
from __future__ import annotations
import os
import subprocess
import sys
from datetime import date

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# The files this step must never write — they belong to the projection.
PROJECTION_OWNED = (
    os.path.join(REPO, "docs", "public", "EFC_Changelog.html"),
    os.path.join(REPO, "docs", "validation-ledger", "data", "changelog.json"),
)
PROJEKSJON = os.path.join(REPO, "scripts", "maintenance",
                          "changelog_projeksjon.py")


def get_git_changes():
    """Get list of changed files since last commit."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only"],
            capture_output=True, text=True, cwd=REPO, timeout=10)
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split("\n") if f]
    except Exception:
        pass
    return []


def categorize_changes(files):
    """Categorize changed files into meaningful groups."""
    cats = {
        "papers_enriched": 0,
        "public_pages": [],
        "ledger_data": [],
        "scripts": [],
        "workflows": [],
    }
    for f in files:
        if f.startswith("docs/papers/efc/") and "index.json" in f:
            cats["papers_enriched"] += 1
        elif f.startswith("docs/public/"):
            name = os.path.basename(f).replace(".html", "").replace("EFC_", "")
            cats["public_pages"].append(name)
        elif f.startswith("docs/validation-ledger/data/"):
            cats["ledger_data"].append(os.path.basename(f))
        elif f.startswith("scripts/maintenance/"):
            cats["scripts"].append(os.path.basename(f))
        elif f.startswith(".github/workflows/"):
            cats["workflows"].append(os.path.basename(f))
    return cats


def build_changelog_entry(cats):
    """Build a human-readable summary of the detected changes."""
    today = date.today().isoformat()
    parts = []

    if cats["papers_enriched"] > 0:
        parts.append(f"{cats['papers_enriched']} paper package{'s' if cats['papers_enriched'] != 1 else ''} enriched")

    if cats["public_pages"]:
        pages = ", ".join(cats["public_pages"])
        parts.append(f"Public pages updated: {pages}")

    if cats["ledger_data"]:
        data = ", ".join(cats["ledger_data"])
        parts.append(f"Ledger data: {data}")

    if cats["scripts"]:
        scripts = ", ".join(cats["scripts"])
        parts.append(f"Maintenance scripts: {scripts}")

    if not parts:
        return None

    return today, "; ".join(parts) + "."


def main():
    print("[efc-auto-changelog] checking for changes...")
    files = get_git_changes()

    if not files:
        print("[efc-auto-changelog] no uncommitted changes — skipping")
        return 0

    cats = categorize_changes(files)

    # Only report if there are changelog-relevant changes.
    if cats["papers_enriched"] == 0 and not cats["public_pages"] and not cats["ledger_data"]:
        print("[efc-auto-changelog] only script/workflow changes — nothing to log")
        return 0

    result = build_changelog_entry(cats)
    if not result:
        print("[efc-auto-changelog] nothing to log")
        return 0

    today, summary = result
    print(f"[efc-auto-changelog] {today} — {summary}")
    print("[efc-auto-changelog] detected only — the changelog is a projection of "
          "git history and belongs to changelog_projeksjon.py. Commit the change, "
          "then run:")
    print(f"  python3 {os.path.relpath(PROJEKSJON, REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
