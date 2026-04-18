#!/usr/bin/env python3
"""
EFC Auto-Changelog — detect changes and append to Changelog
============================================================

Runs after the AI Brain and compares the current state against
the previous snapshot. If anything changed (papers enriched,
public pages updated, inference modules modified), appends a
timestamped entry to both:
  - docs/public/EFC_Changelog.html
  - docs/validation-ledger/data/changelog.json

Usage:
  python3 scripts/maintenance/efc_auto_changelog.py

Meant to run as part of efc_maintain.py pipeline.
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from datetime import date

# Defensive nav sanitizer — ensures short labels + External Research link
# survive every HTML write. Idempotent; no-op if nav already canonical.
try:
    from _nav_helper import ensure_nav  # type: ignore
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _nav_helper import ensure_nav  # type: ignore

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PUBLIC = os.path.join(REPO, "docs", "public")
LEDGER_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")
CHANGELOG_HTML = os.path.join(PUBLIC, "EFC_Changelog.html")
CHANGELOG_JSON = os.path.join(LEDGER_DATA, "changelog.json")


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
    """Build an HTML changelog entry from categorized changes."""
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

    summary = "; ".join(parts) + "."
    html = f'<li><strong>{today}</strong> &mdash; {summary}</li>'
    return html, summary


def update_html_changelog(html_entry):
    """Insert entry into EFC_Changelog.html."""
    if not os.path.exists(CHANGELOG_HTML):
        return False
    with open(CHANGELOG_HTML, encoding="utf-8") as f:
        text = f.read()

    # Insert after <ul> tag
    marker = "<ul>"
    if marker in text:
        # Find the first <ul> after "2026"
        idx = text.find("2026")
        if idx > 0:
            ul_idx = text.find("<ul>", idx)
            if ul_idx > 0:
                insert_point = ul_idx + len("<ul>")
                text = text[:insert_point] + "\n  " + html_entry + text[insert_point:]
                text = ensure_nav(text)  # normalize nav block (idempotent)
                with open(CHANGELOG_HTML, "w", encoding="utf-8") as f:
                    f.write(text)
                return True
    return False


def update_json_changelog(summary):
    """Insert entry into changelog.json."""
    if not os.path.exists(CHANGELOG_JSON):
        return False
    with open(CHANGELOG_JSON) as f:
        cl = json.load(f)

    today = date.today().isoformat()
    # Don't add duplicate entry for same date
    if cl.get("changes") and cl["changes"][0].get("date") == today:
        # Append to existing entry
        existing = cl["changes"][0].get("summary", "")
        if summary not in existing:
            cl["changes"][0]["summary"] = existing + " " + summary
    else:
        cl["changes"].insert(0, {
            "date": today,
            "type": "auto_maintenance",
            "summary": summary,
        })

    with open(CHANGELOG_JSON, "w") as f:
        json.dump(cl, f, indent=2)
    return True


def main():
    print("[efc-auto-changelog] checking for changes...")
    files = get_git_changes()

    if not files:
        print("[efc-auto-changelog] no uncommitted changes — skipping")
        return 0

    cats = categorize_changes(files)

    # Only log if there are meaningful changes
    if cats["papers_enriched"] == 0 and not cats["public_pages"] and not cats["ledger_data"]:
        print("[efc-auto-changelog] only script/workflow changes — skipping changelog")
        return 0

    result = build_changelog_entry(cats)
    if not result:
        print("[efc-auto-changelog] nothing to log")
        return 0

    html_entry, summary = result
    print(f"[efc-auto-changelog] {summary}")

    html_ok = update_html_changelog(html_entry)
    json_ok = update_json_changelog(summary)

    if html_ok:
        print("[efc-auto-changelog] updated EFC_Changelog.html")
    if json_ok:
        print("[efc-auto-changelog] updated changelog.json")

    return 0


if __name__ == "__main__":
    sys.exit(main())
