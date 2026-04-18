#!/usr/bin/env python3
"""
EFC Ledger Autofill — closes the loop that keeps breaking CI.

Every time a new empirical / sealed paper lands in docs/papers/efc/,
its DOI must be registered in BOTH:

  - docs/public/EFC_Validation_Ledger.html   (blocking gate)
  - docs/public/EFC_Changelog.html           (non-blocking but expected)

Historically this was a manual step. Whenever it got forgotten,
scripts/maintenance/efc_precommit_gate.py rejected the commit and
a human had to hand-craft the HTML. This script does it automatically
from each paper's index.json metadata.

Behaviour
---------
For every paper_type in the MUST_BE_IN_LEDGER set whose DOI is
missing from the Ledger HTML, this script inserts an `<li>` block
right before the closing `</ul>` of the Empirical section
(detected as the `<ul>` that immediately precedes
`<h3>Methodological / Core Framework</h3>`).

For every paper whose DOI is missing from Changelog.html, a dated
`<li>` entry is inserted at the top of the current-year `<ul>`.

The rendering is fully deterministic — it uses title, description,
paper_type, tier, and (when available) key_results.main_finding from
index.json. No LLM required.

Idempotent: re-running after all DOIs are registered is a no-op.

Exit code: always 0 (purely additive; never blocks).
"""
from __future__ import annotations
import json
import os
import re
import sys
from datetime import date
from html import escape

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")
CHANGELOG = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")

# Keep this set in sync with efc_precommit_gate.MUST_BE_IN_LEDGER.
MUST_BE_IN_LEDGER = {
    "empirical_test",
    "empirical_analysis",
    "empirical_validation",
    "sealed_prediction",
    "observational_pipeline",
}

SKIP_DIRS = {"ai_friendly_index.json"}  # not a paper dir


def extract_bare_doi(doi_str):
    if not doi_str:
        return None
    m = re.search(r"(\d{7,9})", str(doi_str))
    return m.group(1) if m else None


def truncate_clause(text, limit=260):
    text = re.sub(r"\s+", " ", str(text)).strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut + "…"


def load_paper(paper_dir):
    idx_path = os.path.join(paper_dir, "index.json")
    if not os.path.isfile(idx_path):
        return None
    try:
        with open(idx_path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def render_ledger_item(idx):
    """Return the HTML `<li>` string for a paper's Ledger entry."""
    title = idx.get("title") or "Untitled"
    doi = extract_bare_doi(idx.get("doi", ""))
    paper_type = idx.get("paper_type", "").replace("_", " ")
    tier = idx.get("tier", "") or idx.get("status", "")
    tier_label = tier if tier.startswith("T") else (f"T{tier}" if tier else "")

    # Preferred summary source: key_results.main_finding, then description, then abstract.
    summary = ""
    kr = idx.get("key_results")
    if isinstance(kr, dict):
        summary = kr.get("main_finding") or ""
    if not summary:
        summary = idx.get("description") or idx.get("abstract") or ""
    summary = truncate_clause(summary)

    tag_bits = [t for t in (tier_label, paper_type) if t]
    tag = f" ({', '.join(tag_bits)})" if tag_bits else ""

    if summary:
        strong = f"{escape(title)}{tag}: {escape(summary)}:"
    else:
        strong = f"{escape(title)}{tag}:"

    return (
        f'  <li><strong>{strong}</strong>\n'
        f'    <a href="https://doi.org/10.6084/m9.figshare.{doi}">{doi}</a></li>'
    )


def render_changelog_item(idx, today):
    title = idx.get("title") or "Untitled"
    doi = extract_bare_doi(idx.get("doi", ""))
    paper_type = idx.get("paper_type", "").replace("_", " ")
    tier = idx.get("tier", "") or idx.get("status", "")
    tier_label = tier if tier.startswith("T") else (f"T{tier}" if tier else "")

    summary = ""
    kr = idx.get("key_results")
    if isinstance(kr, dict):
        summary = kr.get("main_finding") or ""
    if not summary:
        summary = idx.get("description") or idx.get("abstract") or ""
    summary = truncate_clause(summary, limit=320)

    tag_bits = [t for t in (tier_label, paper_type) if t]
    tag = f", {', '.join(tag_bits)}" if tag_bits else ""
    suffix = f" {escape(summary)}" if summary else ""
    return (
        f'  <li><strong>{today}</strong> &mdash; '
        f'<strong>{escape(title)}</strong> '
        f'(<a href="https://doi.org/10.6084/m9.figshare.{doi}">{doi}</a>{tag}).{suffix}</li>'
    )


def insert_into_ledger(ledger_text, items):
    """Insert items before the `</ul>` that closes the Empirical section.

    Anchor: the `</ul>` immediately preceding
    `<h3>Methodological / Core Framework</h3>`.
    Falls back to appending before the first `</ul>` if anchor missing.
    """
    if not items:
        return ledger_text
    block = "\n" + "\n".join(items) + "\n"
    anchor = "</ul>\n\n<h3>Methodological / Core Framework</h3>"
    if anchor in ledger_text:
        return ledger_text.replace(anchor, block + anchor, 1)
    # Conservative fallback: insert before first closing </ul>.
    idx = ledger_text.find("</ul>")
    if idx == -1:
        return ledger_text + block
    return ledger_text[:idx] + block + ledger_text[idx:]


def insert_into_changelog(changelog_text, items, year):
    """Insert items at the top of the current year's `<ul>`."""
    if not items:
        return changelog_text
    block = "\n" + "\n".join(items)
    anchor = f"<h2>{year}</h2>\n\n<ul>"
    if anchor in changelog_text:
        return changelog_text.replace(anchor, anchor + block, 1)
    # Fallback: insert at very top of first `<ul>` in the file.
    idx = changelog_text.find("<ul>")
    if idx == -1:
        return changelog_text
    head = changelog_text[: idx + len("<ul>")]
    tail = changelog_text[idx + len("<ul>"):]
    return head + block + tail


def main():
    with open(LEDGER, encoding="utf-8") as f:
        ledger_text = f.read()
    with open(CHANGELOG, encoding="utf-8") as f:
        changelog_text = f.read()

    today = date.today().isoformat()
    year = today[:4]

    missing_ledger_items = []
    missing_changelog_items = []
    touched_ledger_dois = []
    touched_changelog_dois = []

    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_DIRS:
            continue
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue
        idx = load_paper(paper_dir)
        if not idx:
            continue
        doi = extract_bare_doi(idx.get("doi", ""))
        if not doi:
            continue
        paper_type = idx.get("paper_type", "").lower()

        if paper_type in MUST_BE_IN_LEDGER and doi not in ledger_text:
            missing_ledger_items.append(render_ledger_item(idx))
            touched_ledger_dois.append(doi)

        if doi not in changelog_text:
            # Only auto-register empirical/sealed/observational in changelog;
            # pure theory / methodology papers get registered by efc_auto_changelog.py.
            if paper_type in MUST_BE_IN_LEDGER:
                missing_changelog_items.append(render_changelog_item(idx, today))
                touched_changelog_dois.append(doi)

    if not missing_ledger_items and not missing_changelog_items:
        print("[efc-ledger-autofill] nothing to add — Ledger + Changelog already cover every empirical/sealed DOI")
        return 0

    # Defensive nav sanitizer: guarantees short labels + External Research
    # link on every write. Idempotent; no-op if nav already canonical.
    try:
        import sys as _sys
        import os as _os
        _sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
        from _nav_helper import ensure_nav as _ensure_nav
    except Exception:
        _ensure_nav = lambda x: x  # noqa: E731 — fallback no-op

    if missing_ledger_items:
        new_ledger = insert_into_ledger(ledger_text, missing_ledger_items)
        new_ledger = _ensure_nav(new_ledger)
        with open(LEDGER, "w", encoding="utf-8") as f:
            f.write(new_ledger)
        print(f"[efc-ledger-autofill] Ledger: added {len(missing_ledger_items)} "
              f"entry/ies for DOI(s) {', '.join(touched_ledger_dois)}")

    if missing_changelog_items:
        new_changelog = insert_into_changelog(changelog_text, missing_changelog_items, year)
        new_changelog = _ensure_nav(new_changelog)
        with open(CHANGELOG, "w", encoding="utf-8") as f:
            f.write(new_changelog)
        print(f"[efc-ledger-autofill] Changelog: added {len(missing_changelog_items)} "
              f"entry/ies for DOI(s) {', '.join(touched_changelog_dois)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
