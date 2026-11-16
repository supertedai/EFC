#!/usr/bin/env python3
"""efc_doi_surface_audit.py — v2: uncovered-file inverse for the DOI surface.

The no-orphan invariant (component 1) ensures every DOI is referenced somewhere.
This is the inverse: for every statement mapped to a page (appears_on), the
statement's evidence DOIs (via supported_by -> evidence -> locator.doi) must
actually appear in that page's HTML. A page that is declared to carry a result
but does not reference its DOI is an "uncovered surface" — the drift the owner
worries about.

Usage:
    python3 scripts/maintenance/efc_doi_surface_audit.py            # report
    python3 scripts/maintenance/efc_doi_surface_audit.py --json     # machine (CI)

Exit 0 = no uncovered surface; 1 = uncovered surfaces found.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "public" / "graph"
PAGE_META = ROOT / "public" / "page-meta"
PUBLIC = ROOT / "docs" / "public"

DOI_RE = re.compile(r"10\.6084/m9\.figshare\.\d+")


def _yaml(path: Path) -> dict:
    import yaml
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d if isinstance(d, dict) else {}


def load_expected() -> dict[str, set[str]]:
    """page_id -> set of DOIs that should appear there (from statements' evidence)."""
    st = _yaml(GRAPH / "statements.yaml").get("statements", [])
    ev = _yaml(GRAPH / "evidence.yaml").get("evidence", [])
    ev_doi: dict[str, str] = {}
    for e in ev:
        loc = (e.get("locator") or {})
        doi = loc.get("doi", "")
        if doi:
            ev_doi[e.get("evidence_id", "")] = doi

    expected: dict[str, set[str]] = {}
    for s in st:
        appears = s.get("appears_on") or []
        refs = s.get("supported_by") or []
        for a in appears:
            pid = a.get("page_id", "")
            if not pid:
                continue
            for ref in refs:
                if ref in ev_doi:
                    expected.setdefault(pid, set()).add(ev_doi[ref])
    return expected


def page_path(page_id: str) -> str:
    meta = _yaml(PAGE_META / f"{page_id}.yaml")
    return (meta.get("path") or "").lstrip("/")


def scan_page_html(page_id: str) -> set[str]:
    path = page_path(page_id)
    if not path:
        return set()
    f = PUBLIC / path
    if not f.exists():
        return set()
    return set(DOI_RE.findall(f.read_text(encoding="utf-8", errors="replace")))


def audit() -> list[dict]:
    findings = []
    expected = load_expected()
    for pid, dois in sorted(expected.items()):
        present = scan_page_html(pid)
        for doi in sorted(dois):
            if doi not in present:
                findings.append({"page": pid, "doi": doi})
    return findings


def main() -> int:
    findings = audit()
    if "--json" in sys.argv:
        print(json.dumps(findings, ensure_ascii=False, indent=1))
    else:
        print(f"doi-surface-audit: {len(findings)} uncovered surface(s)")
        for f in findings[:30]:
            print(f"  {f['page']}: {f['doi']}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
