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
  python3 scripts/maintenance/efc_dataset_scanner.py              # scan, write report
  python3 scripts/maintenance/efc_dataset_scanner.py --dry-run    # scan, write nothing
  python3 scripts/maintenance/efc_dataset_scanner.py --check-stale [--json]

Exit 0 = no new datasets, 1 = new datasets found.
`--check-stale` reads the report only (no network) and exits 1 when a finding
has passed the expiry the report declares for itself.

The report is a function of CONTENT, not of the clock
-----------------------------------------------------
Measured 2026-09-18 (card t_782249e4): the idempotence guard added in f99aeb71
compared the report's `date` field as well as the findings, so the first run on
a new calendar day rewrote `.claude/dataset_scan_report.json` with identical
findings and two fresh finding timestamps. Every PR that ran the canonical
maintenance sequence therefore carried a diff with no content behind it — the
class rule 51 in the EFC build discipline names.

The report now holds only content: the roadmap's known set, the findings the
pages yield, and each finding's FIRST observation date. Nothing in it is read
from the clock at write time, so two runs with identical findings render
identical bytes and the file is left alone.

A date that is kept would have to be either rewritten every day (the defect) or
frozen (a field claiming to be the last scan while it is really the last
change), so the top-level `date` is gone: the provenance lives on each finding,
which carries its own `source`, `url` and `first_seen`. `first_seen` is carried
forward, never re-stamped — a write must not date an observation nobody
re-observed.

A finding is a potential dataset nobody has taken a position on yet: it is
expected to be handled (taken into the roadmap, or dismissed by sharpening the
search terms), not to sit in the report forever. The report therefore declares
its own expiry (`stale_after_days`), the scanner READS it on every run, and
`--check-stale` answers it for a consumer that wants to gate on it — an expiry
nothing reads is a date without a consequence.
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

# The program that read the pages, recorded IN the artifact: a reader of the
# report must be able to see who made the observation.
READER = "scripts/maintenance/efc_dataset_scanner.py"

# How long an unhandled finding may stand before the scanner reports it as
# expired. Declared in the artifact, read back by the scanner.
STALE_AFTER_DAYS = 90

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
    """Check each data source for new releases.

    A finding carries no clock stamp: WHEN an observation was first made is a
    property of the report, not of the fetch (the pages are re-read on every
    run, and a re-read is not a new observation).
    """
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
                    })

    return findings


def read_report(path: str = REPORT_PATH):
    """(report, problem): the report on disk, and what is wrong with it.

    A MISSING report is (None, "") — there is nothing to carry forward, which is
    a legitimate state for a first run. A file that cannot be read, or is not a
    report, is (None, <why>): the two must not collapse into one value, because
    the write path would otherwise overwrite observations it could not read and
    re-date them as new.
    """
    if not os.path.exists(path):
        return None, ""
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError) as e:
        return None, f"{path} cannot be read ({e.__class__.__name__}: {e})"
    if not isinstance(data, dict):
        return None, f"{path} is not a report object ({type(data).__name__})"
    return data, ""


def _iso_date(value) -> str:
    """The value if it is a real calendar date (YYYY-MM-DD), else ""."""
    if not isinstance(value, str):
        return ""
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError:
        return ""


def first_seen(finding: dict, today: str) -> str:
    """When this finding was FIRST observed — carried forward, never re-stamped.

    A report that refreshes its timestamps on every write dates every
    observation today; a finding's age is the one thing the artifact is for.
    Reports written before 2026-09-18 carried a full `timestamp`; its date part
    is the same fact, so it is read rather than discarded.
    """
    return (_iso_date(finding.get("first_seen"))
            or _iso_date(str(finding.get("timestamp") or "")[:10])
            or today)


def build_report(known, findings: list, previous, today: str) -> dict:
    """The report as content: a pure function of known, findings, first_seen."""
    seen = {(f.get("source"), f.get("term")): first_seen(f, today)
            for f in (previous or {}).get("findings") or []}
    return {
        "reader": READER,
        "stale_after_days": STALE_AFTER_DAYS,
        "known": sorted(known),
        "findings": [{"source": f["source"], "term": f["term"], "url": f["url"],
                      "first_seen": seen.get((f["source"], f["term"])) or today}
                     for f in findings],
    }


def expired_findings(report: dict, today: datetime.date) -> list:
    """Findings past the expiry the report declares for itself."""
    max_age = report.get("stale_after_days")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age <= 0:
        return []
    expired = []
    for f in report.get("findings") or []:
        seen = _iso_date(f.get("first_seen"))
        if not seen:
            continue
        age = (today - datetime.date.fromisoformat(seen)).days
        if age > max_age:
            expired.append({**f, "age_days": age, "stale_after_days": max_age})
    return expired


def report_problems(report: dict) -> list:
    """Everything the report does not say, said out loud.

    An absent expiry is not «this artifact needs no expiry» — it is an artifact
    that answers forever, indistinguishable from nobody having looked.
    """
    problems = []
    max_age = report.get("stale_after_days")
    if not isinstance(max_age, int) or isinstance(max_age, bool) or max_age <= 0:
        problems.append("the report declares no usable stale_after_days — an "
                        "artifact with no expiry answers forever")
    if not report.get("reader"):
        problems.append("the report names no reader — an observation with no "
                        "observer cannot be traced")
    for f in report.get("findings") or []:
        where = f"{f.get('source')}/{f.get('term')}"
        if not _iso_date(f.get("first_seen")):
            problems.append(f"{where}: first_seen is not a calendar date "
                            f"({f.get('first_seen')!r})")
        if not f.get("url"):
            problems.append(f"{where}: no url — the source of the finding is gone")
    return problems


def stale_answer(path: str = REPORT_PATH, today: datetime.date | None = None) -> dict:
    """The machine-readable answer about the report's own expiry."""
    report, problem = read_report(path)
    if report is None:
        # An absent artifact is an answer too: it is not «nothing to report».
        return {"report": path, "expired": [],
                "problems": [problem or f"no report at {path}"]}
    return {"report": path,
            "reader": report.get("reader"),
            "stale_after_days": report.get("stale_after_days"),
            "problems": report_problems(report),
            "expired": expired_findings(report, today)}


def check_stale(path: str = REPORT_PATH, today: datetime.date | None = None,
                as_json: bool = False) -> int:
    """Read-only: has anything in the report passed the report's own expiry?

    No network, no write — the answer is a property of the artifact on disk.
    """
    today = today or datetime.date.today()
    answer = stale_answer(path, today)
    if as_json:
        print(json.dumps(answer, indent=2))
    else:
        for problem in answer["problems"]:
            print(f"  report problem: {problem}")
        for f in answer["expired"]:
            print(f"  expired: [{f['source']}] {f['term']} — first seen "
                  f"{f['first_seen']}, {f['age_days']} days (expiry "
                  f"{f['stale_after_days']}): take the dataset into the roadmap "
                  f"or sharpen the scanner's search terms, then re-run")
    return 1 if (answer["problems"] or answer["expired"]) else 0


def main():
    dry_run = "--dry-run" in sys.argv
    if "--check-stale" in sys.argv:
        return check_stale(as_json="--json" in sys.argv)

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

    # The report is COMPARED as text, not field by field: the file is either
    # exactly what this run renders, or it is not touched at all. A day boundary
    # alone therefore changes nothing. The exit code above (findings exist) is
    # independent of whether the file needed writing.
    today = datetime.date.today().isoformat()
    previous, problem = read_report(REPORT_PATH)
    if problem:
        # A report we cannot read is not «no report»: its observations exist and
        # we cannot see them, so overwriting it would re-date them as new. The
        # state is named and the file is left alone — a human fixes or removes it.
        print(f"\n  report problem: {problem}")
        print("  refusing to rewrite it: the observations it carries would be "
              "re-dated as new. Fix or remove the file, then re-run.")
        return 1
    new_report = build_report(known, findings, previous, today)
    new_text = json.dumps(new_report, indent=2)
    old_text = None
    if os.path.exists(REPORT_PATH):
        with open(REPORT_PATH, encoding="utf-8") as f:
            old_text = f.read()

    if old_text == new_text:
        print("\nReport unchanged — skipping write (idempotent).")
    elif dry_run:
        print("\n--dry-run: report NOT written. It would have been:")
        print(new_text)
    else:
        os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write(new_text)
        print(f"\nReport saved to {REPORT_PATH}")

    # The expiry the report declares is read here, on the path that produces it,
    # so a finding nobody has handled cannot age in silence.
    for f in expired_findings(new_report, datetime.date.today()):
        print(f"  EXPIRED: [{f['source']}] {f['term']} — first seen "
              f"{f['first_seen']}, {f['age_days']} days (expiry "
              f"{f['stale_after_days']}): handle it and re-run")

    return 1


if __name__ == "__main__":
    sys.exit(main())
