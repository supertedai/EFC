#!/usr/bin/env python3
"""
EFC Unprocessed Paper Detector

Scans all paper directories for DOIs that are NOT yet registered in
the Validation Ledger HTML. These papers need Claude's attention:
read the content, classify relevance, and update public pages.

Output: list of paper directories with DOIs missing from the Ledger.
Exit 0 = all processed, exit 2 = unprocessed papers found.
"""
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")
ROADMAP = os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html")
CHANGELOG = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def extract_bare_doi(doi_str):
    """Extract '31990053' from any DOI form."""
    if not doi_str:
        return None
    m = re.search(r'(\d{7,9})', str(doi_str))
    return m.group(1) if m else None


def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def main():
    # Read all public pages
    ledger_text = read_file(LEDGER)
    roadmap_text = read_file(ROADMAP)
    changelog_text = read_file(CHANGELOG)

    unprocessed = []

    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue

        # Get DOI from index.json
        idx = load_json(os.path.join(paper_dir, "index.json"))
        if not idx:
            continue
        doi = idx.get("doi")
        bare = extract_bare_doi(doi)
        if not bare:
            continue

        # Check if DOI is in Ledger
        in_ledger = bare in ledger_text
        in_changelog = bare in changelog_text

        missing = []
        if not in_ledger:
            missing.append("Ledger")
        if not in_changelog:
            missing.append("Changelog")

        if missing:
            title = idx.get("title", name)
            unprocessed.append({
                "directory": name,
                "doi": bare,
                "title": title,
                "missing_from": missing,
                "has_key_results": "key_results" in idx,
                "track": idx.get("track", "unknown"),
            })

    if not unprocessed:
        print("[efc-unprocessed] All papers with DOIs are registered in public pages")
        return 0

    print(f"[efc-unprocessed] {len(unprocessed)} paper(s) need processing:")
    for p in unprocessed:
        print(f"  {p['directory']} (DOI {p['doi']})")
        print(f"    Title: {p['title']}")
        print(f"    Missing from: {', '.join(p['missing_from'])}")
        print(f"    Has key_results: {p['has_key_results']}")
        print(f"    Track: {p['track']}")

    # Write report for Claude
    report_path = os.path.join(REPO, ".claude", "unprocessed_papers.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(unprocessed, f, indent=2)

    return 2


if __name__ == "__main__":
    sys.exit(main())
