#!/usr/bin/env python3
"""
EFC Pre-Commit Gate — HARD BLOCKER

Blocks commits when empirical/sealed papers are missing from the Ledger.
Theory/methodology papers are allowed (Changelog-only is fine for them).

This is the enforcement layer that makes the classification protocol
actually work: if paper_type is in the empirical set and the DOI is
NOT in the HTML Ledger, the commit is REJECTED.

Exit codes:
  0 = no blocking issues
  1 = missing empirical papers found — commit BLOCKED

Install as .git/hooks/pre-commit or run manually before committing.
"""
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")
CHANGELOG = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")

# Paper types that MUST be in the Ledger
MUST_BE_IN_LEDGER = {
    "empirical_test",
    "empirical_analysis",
    "empirical_validation",
    "sealed_prediction",
    "observational_pipeline",
}


def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def extract_bare_doi(doi_str):
    if not doi_str:
        return None
    m = re.search(r'(\d{7,9})', str(doi_str))
    return m.group(1) if m else None


def main():
    ledger_text = read_file(LEDGER)
    changelog_text = read_file(CHANGELOG)

    missing_ledger = []
    missing_changelog = []

    for name in sorted(os.listdir(PAPERS)):
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue

        idx_path = os.path.join(paper_dir, "index.json")
        if not os.path.isfile(idx_path):
            continue

        try:
            with open(idx_path) as f:
                idx = json.load(f)
        except (OSError, json.JSONDecodeError):
            continue

        paper_type = idx.get("paper_type", "").lower()
        doi = idx.get("doi", "")
        bare = extract_bare_doi(doi)
        if not bare:
            continue

        title = idx.get("title", name)[:70]
        tier = idx.get("tier", "")

        in_ledger = bare in ledger_text
        in_changelog = bare in changelog_text

        if paper_type in MUST_BE_IN_LEDGER and not in_ledger:
            missing_ledger.append({
                "doi": bare,
                "paper_type": paper_type,
                "tier": tier,
                "title": title,
                "directory": name,
            })

        if not in_changelog:
            missing_changelog.append({
                "doi": bare,
                "paper_type": paper_type,
                "title": title,
                "directory": name,
            })

    if not missing_ledger:
        print(f"[efc-precommit] OK — no empirical papers missing from Ledger")
        if missing_changelog:
            print(f"[efc-precommit] NOTE: {len(missing_changelog)} paper(s) "
                  f"missing from Changelog (non-blocking)")
        return 0

    # HARD BLOCK
    print("=" * 70)
    print("[efc-precommit] COMMIT BLOCKED")
    print("=" * 70)
    print(f"\n{len(missing_ledger)} empirical/sealed paper(s) missing from Ledger:\n")
    for p in missing_ledger:
        print(f"  DOI {p['doi']}  [{p['paper_type']}, {p['tier']}]")
        print(f"    {p['title']}")
        print(f"    Directory: {p['directory']}")
        print()

    print("=" * 70)
    print("ACTION REQUIRED:")
    print("  1. Add each DOI to docs/public/EFC_Validation_Ledger.html")
    print("     (evidence register section §4, or new test row in §1)")
    print("  2. Add each DOI to docs/public/EFC_Changelog.html")
    print("  3. Re-run: python3 scripts/maintenance/efc_precommit_gate.py")
    print("  4. Commit again once this script returns exit 0")
    print("=" * 70)
    return 1


if __name__ == "__main__":
    sys.exit(main())
