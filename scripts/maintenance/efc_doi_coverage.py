#!/usr/bin/env python3
"""efc_doi_coverage — DOI coverage for docs/public, measured in the repo itself.

Replaces `public_pages_doi_drift.py`, which ran outside the repo (Symbiose,
`.12`) and committed to `main` every six hours. Measured 2026-08-23: 64 of
the last 80 commits on `main` were that job, and each changed **only the
timestamp** — the numbers stood still. See ADR-024 §6 and §8.3 item 3.

Three requirements from that review, all met here:

1. **No time in the output.** The report contains no `generated_at`.
   Identical content gives an identical file gives no commit. Git carries the
   timestamp.
2. **A citation is not a number in a sentence.** DOIs inside rows marked as
   planned work (`data-result="Planned"`) are not counted. Measured: this
   applies to 5 DOIs, all on the Atlas — including `…figshare.31140000`,
   which stood listed as an anomaly for seven weeks because it is mentioned
   in a *task* about re-ingesting incomplete DOIs.
3. **No placement without a hit.** Every page listed for a DOI is found in
   that file. The old report listed `10.17863/cam.690` as occurring on the
   Atlas; `git grep` found it only in the report itself. (That DOI now
   legitimately appears in a `Planned` row and is excluded by requirement 2.)

The canon is fetched **directly from ORCID**, not from an intermediate file.

Usage:
    python3 scripts/maintenance/efc_doi_coverage.py            # write report
    python3 scripts/maintenance/efc_doi_coverage.py --sjekk    # exit code only
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "docs" / "public"
REPORT = PUBLIC / "DOI_Coverage_Report.md"
REGISTER = ROOT / "docs" / "validation-ledger" / "data" / "external-references.json"
ORCID = "0009-0002-4860-5095"

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>&),;]+")
PLANNED_RE = re.compile(r'<tr[^>]*data-result="Planned"[^>]*>.*?</tr>', re.S)


def _norm(doi: str) -> str:
    """Normalize a DOI for comparison: strip trailing punctuation, lowercase.

    One function used everywhere a DOI is compared, so the exclusion set and
    the scan loop cannot drift apart again. The old code built ``excluded``
    with ``.lower()`` but checked membership with ``.rstrip(".").lower()``,
    which let a Planned-row DOI ending in punctuation (e.g. ``CAM.690.``)
    slip through as a false positive.
    """
    return doi.rstrip(".,;:)]}").lower()


def orcid_canon() -> set[str]:
    req = urllib.request.Request(
        f"https://pub.orcid.org/v3.0/{ORCID}/works",
        headers={"Accept": "application/json", "User-Agent": "efc-doi-coverage"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    ut = set()
    for g in d.get("group", []):
        for eid in (g.get("external-ids") or {}).get("external-id", []):
            if (eid.get("external-id-type") or "").lower() == "doi":
                v = (eid.get("external-id-value") or "").strip().lower()
                if v.startswith("10.") and "/" in v:
                    ut.add(v)
    return ut


def registered_entries() -> dict[str, str]:
    """Verified external citations, with role. The file may be missing — then
    it is empty, and that is an honest answer, not an error."""
    if not REGISTER.exists():
        return {}
    d = json.loads(REGISTER.read_text(encoding="utf-8"))
    # The same register that §4b is generated from (efc_4b.py). One truth for
    # external references, not two: the §4b generator uses `html`, this one
    # uses `doi` and `rolle`. An entry without a `doi` is an arXiv finding
    # that has no DOI to reconcile — it belongs in §4b, not here.
    if isinstance(d, dict) and "grupper" in d:
        records = [o for g in d["grupper"] for o in g.get("oppforinger", [])]
    else:
        records = d.get("references", d) if isinstance(d, dict) else d
    ut = {}
    for p in records:
        if not isinstance(p, dict):
            continue
        doi = str(p.get("doi") or "").strip().lower()
        if doi.startswith("10.") and "/" in doi:
            ut[doi] = p.get("rolle") or p.get("role") or "unclassified"
    return ut


def scan(directory: Path = PUBLIC) -> dict[str, set[str]]:
    """DOI → pages it actually occurs on. Planned rows are skipped.

    ``directory`` is a test seam: it defaults to ``docs/public/``, but tests
    pass a temp dir so they do not depend on the live public surface.
    """
    found: dict[str, set[str]] = {}
    for path in sorted(directory.glob("*.html")):
        h = path.read_text(encoding="utf-8", errors="replace")
        excluded = set()
        for row in PLANNED_RE.findall(h):
            excluded.update(_norm(m) for m in DOI_RE.findall(row))
        for m in DOI_RE.finditer(h):
            d = _norm(m.group(0))
            if d in excluded:
                continue
            found.setdefault(d, set()).add(path.name)
    return found


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sjekk", action="store_true",
                    help="do not write the file; exit 1 if anomalies exist")
    a = ap.parse_args()

    canon = orcid_canon()
    reg = registered_entries()
    found = scan()

    covered = sorted(d for d in found if d in canon)
    missing = sorted(canon - set(found))
    registered = sorted(d for d in found if d not in canon and d in reg)
    unrecognized = sorted(d for d in found if d not in canon and d not in reg)

    lines = [
        "# DOI Coverage Report — docs/public × ORCID canon",
        "",
        "_Generated deterministically by `scripts/maintenance/efc_doi_coverage.py` "
        "in this repository's own CI. Canon is read directly from ORCID. "
        "No timestamp in this file — identical content produces no commit._",
        "",
        f"**Canon:** {len(canon)} works · **Covered:** {len(covered)} · "
        f"**Missing from all pages:** {len(missing)} · "
        f"**Registered external:** {len(registered)} · "
        f"**Unrecognized:** {len(unrecognized)} · **Pages scanned:** "
        f"{len(list(PUBLIC.glob('*.html')))}",
        "",
        "## Canonical works not referenced on any public page",
        "",
    ]
    lines += ([f"- `{d}`" for d in missing] or ["_None — full coverage._"])
    lines += ["", "## Registered external citations (verified intentional)", ""]
    if registered:
        lines += ["| DOI | role | pages |", "|---|---|---|"]
        lines += [f"| `{d}` | {reg[d]} | {', '.join(sorted(found[d]))} |"
                   for d in registered]
    else:
        lines += [f"_None registered. The register is `{REGISTER.relative_to(ROOT)}`"
                   + ("" if REGISTER.exists() else " — file does not exist yet") + "._"]
    lines += ["", "## Unrecognized DOIs — neither in canon nor registered", ""]
    if unrecognized:
        lines += ["| DOI | pages |", "|---|---|"]
        lines += [f"| `{d}` | {', '.join(sorted(found[d]))} |" for d in unrecognized]
    else:
        lines += ["_None._"]
    lines += ["", "## DOI counts per page", "", "| Page | DOIs |", "|---|---|"]
    per: dict[str, int] = {}
    for d, pages in found.items():
        for s in pages:
            per[s] = per.get(s, 0) + 1
    lines += [f"| {s} | {n} |" for s, n in sorted(per.items())]
    text = "\n".join(lines) + "\n"

    if a.sjekk:
        print(f"[doi-coverage] canon={len(canon)} covered={len(covered)} "
              f"missing={len(missing)} registered={len(registered)} "
              f"unrecognized={len(unrecognized)}")
        for d in unrecognized:
            print(f"  unrecognized: {d}  ({', '.join(sorted(found[d]))})")
        return 1 if (unrecognized or missing) else 0

    changed = (not REPORT.exists()) or REPORT.read_text(encoding="utf-8") != text
    REPORT.write_text(text, encoding="utf-8")
    print(f"[doi-coverage] {'updated' if changed else 'unchanged'} — "
          f"canon={len(canon)} unrecognized={len(unrecognized)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
