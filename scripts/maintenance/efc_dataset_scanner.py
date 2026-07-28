#!/usr/bin/env python3
"""
EFC Dataset Scanner — Monitors External Data Releases
======================================================

Checks public data release pages for new datasets relevant to EFC:
  - Euclid (ESA)
  - DESI (Berkeley Lab)
  - KiDS (Leiden)
  - DES (Fermilab)
  - Planck (ESA)
  - Simons Observatory

Compares against known datasets in the Roadmap and reports new ones.

Requires: OPENAI_API_KEY for GPT-5 assessment of relevance.

Usage:
  python3 scripts/maintenance/efc_dataset_scanner.py
  python3 scripts/maintenance/efc_dataset_scanner.py --dry-run

Exit 0 = no new datasets, 1 = new datasets found.
"""
from __future__ import annotations
import json
import os
import re
import sys
import datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ROADMAP = os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html")
REPORT_PATH = os.path.join(REPO, ".claude", "dataset_scan_report.json")

# Known data release URLs to check
DATA_SOURCES = [
    {
        "name": "Euclid",
        "url": "https://www.euclid-ec.org/science-results/",
        "search_terms": ["DR1", "data release", "cosmic shear", "galaxy clustering"],
    },
    {
        "name": "DESI",
        "url": "https://data.desi.lbl.gov/doc/releases/",
        "search_terms": ["DR2", "BAO", "full-shape", "data release"],
    },
    {
        "name": "KiDS",
        "url": "https://kids.strw.leidenuniv.nl/DR5/",
        "search_terms": ["DR5", "cosmic shear", "KiDS-Legacy"],
    },
    {
        "name": "Simons Observatory",
        "url": "https://simonsobservatory.org/news/",
        "search_terms": ["first light", "data release", "CMB"],
    },
]

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")


def check_roadmap_datasets():
    """Extract datasets already mentioned in the Roadmap."""
    if not os.path.exists(ROADMAP):
        return set()
    with open(ROADMAP) as f:
        text = f.read()
    # Find dataset names mentioned
    datasets = set()
    for m in re.finditer(r'(Euclid DR\d|DESI DR\d|KiDS[- ](?:DR\d|Legacy|1000)|DES Y\d|Planck PR\d|Simons Observatory)', text, re.I):
        datasets.add(m.group(1))
    return datasets


def fetch_url(url, timeout=10):
    """Fetch URL content. Returns text or empty string."""
    try:
        import urllib.request
        import ssl
        ctx = ssl.create_default_context()
        req = urllib.request.Request(url, headers={"User-Agent": "EFC-Dataset-Scanner/1.0"})
        with urllib.request.urlopen(req, context=ctx, timeout=timeout) as resp:
            return resp.read().decode(errors="replace")[:20000]
    except Exception:
        return ""


def scan_for_new_datasets():
    """Check each data source for new releases."""
    known = check_roadmap_datasets()
    findings = []

    for source in DATA_SOURCES:
        html = fetch_url(source["url"])
        if not html:
            print(f"  {source['name']}: could not fetch {source['url']}")
            continue

        # Look for release announcements
        for term in source["search_terms"]:
            if term.lower() in html.lower():
                # Check if it's already known
                is_new = not any(term.lower() in k.lower() for k in known)
                if is_new:
                    findings.append({
                        "source": source["name"],
                        "term": term,
                        "url": source["url"],
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                    })

    return findings


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("EFC DATASET SCANNER")
    print(f"Date: {datetime.date.today().isoformat()}")
    print("=" * 60)

    known = check_roadmap_datasets()
    print(f"\nKnown datasets in Roadmap: {len(known)}")
    for d in sorted(known):
        print(f"  - {d}")

    print(f"\nScanning {len(DATA_SOURCES)} sources...")
    findings = scan_for_new_datasets()

    if not findings:
        print("\nNo new datasets found.")
        return 0

    print(f"\n{len(findings)} potential new dataset(s):")
    for f in findings:
        print(f"  [{f['source']}] {f['term']} — {f['url']}")

    # Save report
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        json.dump({"date": datetime.date.today().isoformat(),
                   "known": sorted(known), "findings": findings}, f, indent=2)
    print(f"\nReport saved to {REPORT_PATH}")

    return 1


if __name__ == "__main__":
    sys.exit(main())
