#!/usr/bin/env python3
"""
EFC Drift Detector

Scans the repo for hard facts (paper count, test count, version numbers,
pipeline status) and compares them against what the public-facing documents
claim. Outputs a structured drift report that Claude Code acts on.

Run by the SessionStart hook after efc_maintain.py.
Exit 0 = clean, exit 2 = drift detected (not an error, just work to do).
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

# Files to check for consistency
CHECK_FILES = {
    "README.md": os.path.join(REPO, "README.md"),
    "AGENTS.md": os.path.join(REPO, "AGENTS.md"),
    "Validation_Ledger": os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html"),
    "White_Paper_Series": os.path.join(REPO, "docs", "public", "EFC_White_Paper_Series.html"),
    "Elevator_Pitch": os.path.join(REPO, "docs", "public", "EFC_Elevator_Pitch.html"),
    "Stage_IV_Roadmap": os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html"),
    "Changelog": os.path.join(REPO, "docs", "public", "EFC_Changelog.html"),
    "pipelines_README": os.path.join(REPO, "pipelines", "README.md"),
}


def count_paper_dirs():
    count = 0
    for name in os.listdir(PAPERS):
        if name in SKIP_TOP:
            continue
        if os.path.isdir(os.path.join(PAPERS, name)):
            count += 1
    return count


def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def find_all_counts(text, pattern):
    """Find all integer matches for a pattern like r'(\d+)\s*papers'."""
    return [int(m.group(1)) for m in re.finditer(pattern, text)]


def detect_drift():
    drift = []
    actual_papers = count_paper_dirs()

    for name, path in CHECK_FILES.items():
        text = read_file(path)
        if not text:
            continue

        # Check paper/package counts (skip historical entries in Changelog)
        for m in re.finditer(r'(\d{2,3})\s*(?:papers?|packages?|paper dir)', text):
            claimed = int(m.group(1))
            if claimed != actual_papers and abs(claimed - actual_papers) < 20:
                # Skip if this looks like a historical Changelog entry (has a date before it)
                context_before = text[max(0, m.start()-80):m.start()]
                if name == "Changelog" and re.search(r'20\d\d-\d\d', context_before):
                    continue
                drift.append({
                    "file": name,
                    "type": "paper_count",
                    "claimed": claimed,
                    "actual": actual_papers,
                    "context": text[max(0, m.start()-30):m.end()+30].strip(),
                })

        # Check badge counts (e.g. AI_Packages-138)
        for m in re.finditer(r'AI_Packages-(\d+)', text):
            claimed = int(m.group(1))
            if claimed != actual_papers:
                drift.append({
                    "file": name,
                    "type": "badge_count",
                    "claimed": claimed,
                    "actual": actual_papers,
                })

    # Check AGENTS.md version strings
    agents = read_file(CHECK_FILES.get("AGENTS.md", ""))
    if agents:
        # ai_packages count
        m = re.search(r'ai_packages:\s*(\d+)', agents)
        if m and int(m.group(1)) != actual_papers:
            drift.append({
                "file": "AGENTS.md",
                "type": "agents_package_count",
                "claimed": int(m.group(1)),
                "actual": actual_papers,
            })
        # Stale version in AGENTS.md
        m = re.search(r'validation_ledger:\s*v([\d.]+)\s*\(', agents)
        if m:
            agents_version = m.group(1)
            # Check against Changelog for latest version
            changelog = read_file(CHECK_FILES.get("Changelog", ""))
            cm = re.search(r'\(v(3\.\d+)\)', changelog)
            if cm and cm.group(1) != agents_version:
                drift.append({
                    "file": "AGENTS.md",
                    "type": "version_drift",
                    "claimed": agents_version,
                    "actual": cm.group(1),
                })

    return drift, actual_papers


def main():
    drift, actual_papers = detect_drift()

    if not drift:
        print(f"[efc-drift] {actual_papers} papers · no drift detected")
        return 0

    print(f"[efc-drift] {actual_papers} papers · {len(drift)} drift(s) detected:")
    for d in drift:
        if d["type"] in ("paper_count", "badge_count", "agents_package_count"):
            print(f"  {d['file']}: claims {d['claimed']} but actual is {d['actual']}")
        elif d["type"] == "version_drift":
            print(f"  {d['file']}: version {d['claimed']} but latest is {d['actual']}")
        else:
            print(f"  {d['file']}: {d['type']} — {d.get('claimed')} vs {d.get('actual')}")

    # Write machine-readable drift report
    report_path = os.path.join(REPO, ".claude", "drift_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"paper_count": actual_papers, "drift": drift}, f, indent=2)

    return 2  # drift detected, not an error


if __name__ == "__main__":
    sys.exit(main())
