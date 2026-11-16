#!/usr/bin/env python3
"""efc_doi_impact_manifest.py — Component 1: DOI impact manifest.

Builds `data/doi_impact_manifest.json`: for every known DOI (canonical source
`figshare/doi-map.json`), the set of repo files that reference that DOI.

The invariant that makes coverage *by construction* instead of *by enumeration*:

  *no-orphan* — every DOI in doi-map.json must occur in at least one file other
  than doi-map.json itself. A DOI that only appears in the catalog, but is never
  projected into a package or page file, is an "orphan" and fails.

Usage:
    python3 scripts/maintenance/efc_doi_impact_manifest.py           # write manifest
    python3 scripts/maintenance/efc_doi_impact_manifest.py --check   # verify invariant only

Returns 0 if the invariant holds, 1 otherwise (for CI gating).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOI_MAP = REPO / "figshare" / "doi-map.json"
MANIFEST = REPO / "data" / "doi_impact_manifest.json"

DOI_RE = re.compile(r"10\.6084/m9\.figshare\.\d+")

# Files always skipped (binaries). rg skips .git, hidden files and binary files
# by default; these are extra safety for known binary types.
SKIP_GLOBS = ["!*.pdf", "!*.png", "!*.jpg", "!*.jpeg", "!*.gif",
              "!*.bin", "!*.gz", "!*.zip", "!*.woff", "!*.woff2", "!*.ttf"]


def load_known_dois() -> dict[str, dict]:
    """Read canonical DOIs from doi-map.json. Returns {doi: {title, paper_type, repo_dir}}."""
    data = json.loads(DOI_MAP.read_text())
    out: dict[str, dict] = {}
    for p in data.get("papers", []):
        doi = p.get("doi", "")
        if not doi.startswith("10.6084/m9.figshare."):
            continue
        out[doi] = {
            "title": p.get("title", ""),
            "paper_type": p.get("paper_type", ""),
            "repo_dir": p.get("repo_dir", ""),
        }
    return out


def scan_references() -> dict[str, set[str]]:
    """Single rg pass over the repo: DOI -> set of files (relative paths) that mention it."""
    args = ["rg", "-H", "-o", "-N", r"10\.6084/m9\.figshare\.\d+"]
    for g in SKIP_GLOBS:
        args += ["-g", g]
    args += ["."]
    proc = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        # rc=1 = no matches (rg); other values = error
        if proc.returncode != 1:
            raise RuntimeError(f"rg failed rc={proc.returncode}: {proc.stderr[:400]}")

    refs: dict[str, set[str]] = {}
    for line in proc.stdout.splitlines():
        # format: "path:DOI" (with -H the filename is always prefixed)
        if ":" not in line:
            continue
        path, doi = line.rsplit(":", 1)
        if not DOI_RE.fullmatch(doi):
            continue
        rel = Path(path).as_posix()
        if rel.startswith("./"):
            rel = rel[2:]
        refs.setdefault(doi, set()).add(rel)
    return refs


def _detect_orphans(known: dict[str, dict], refs: dict[str, set[str]]) -> list[str]:
    """DOIs that only appear in doi-map.json (never projected into another file)."""
    orphans: list[str] = []
    for doi in sorted(known):
        beyond_catalog = [f for f in refs.get(doi, set()) if f != "figshare/doi-map.json"]
        if not beyond_catalog:
            orphans.append(doi)
    return orphans


def build_manifest(known: dict[str, dict] | None = None,
                   refs: dict[str, set[str]] | None = None) -> tuple[dict, list[str]]:
    known = known if known is not None else load_known_dois()
    refs = refs if refs is not None else scan_references()
    orphans = _detect_orphans(known, refs)

    manifest_dois: dict[str, dict] = {}
    for doi in sorted(known):
        files = sorted(refs.get(doi, set()))
        manifest_dois[doi] = {
            "title": known[doi]["title"],
            "paper_type": known[doi]["paper_type"],
            "repo_dir": known[doi]["repo_dir"],
            "files": files,
            "referenced_beyond_catalog": sum(1 for f in files if f != "figshare/doi-map.json"),
        }

    manifest = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generator": "scripts/maintenance/efc_doi_impact_manifest.py",
        "totals": {
            "known_dois": len(known),
            "orphan_dois": len(orphans),
            "files_referencing_dois": len({f for s in refs.values() for f in s}),
        },
        "dois": manifest_dois,
    }
    return manifest, orphans


def main() -> int:
    check_only = "--check" in sys.argv
    manifest, orphans = build_manifest()

    if check_only:
        if orphans:
            print(f"FAIL: {len(orphans)} orphan DOIs (only in doi-map, never projected):")
            for d in orphans:
                print(f"  - {d}")
            return 1
        print(f"OK: no orphan DOIs ({manifest['totals']['known_dois']} known).")
        return 0

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Manifest written: {MANIFEST.relative_to(REPO)}")
    print(f"  known DOIs: {manifest['totals']['known_dois']}")
    print(f"  orphan DOIs: {manifest['totals']['orphan_dois']}")
    print(f"  files with DOI refs: {manifest['totals']['files_referencing_dois']}")
    if orphans:
        print("Orphan DOIs:")
        for d in orphans:
            print(f"  - {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
