#!/usr/bin/env python3
"""efc_doi_impact_manifest.py — Komponent 1: DOI-impact-manifest.

Bygger `data/doi_impact_manifest.json`: for hver kjent DOI (kanonisk kilde
`figshare/doi-map.json`), hvilke filer i repoet som refererer DOI-en.

Invarianten som gjør dekningen *av konstruksjon* i stedet for *av enumerering*:

  *no-orphan* — hver DOI i doi-map.json må forekomme i minst én fil utenom
  selve doi-map.json. En DOI som bare står i katalogen, men aldri er projisert
  til en pakke- eller side-fil, er en «orphan» og feiler.

Bruk:
    python3 scripts/maintenance/efc_doi_impact_manifest.py           # skriv manifest
    python3 scripts/maintenance/efc_doi_impact_manifest.py --check   # kun verifiser invariant

Returnerer 0 hvis invarianten holder, 1 ellers (for CI-gate).
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

# Filer som alltid hoppes over (binærfiler). rg hopper over .git, skjulte filer
# og binære filer som standard; disse er ekstra sikkerhet for kjente binærtyper.
SKIP_GLOBS = ["!*.pdf", "!*.png", "!*.jpg", "!*.jpeg", "!*.gif",
              "!*.bin", "!*.gz", "!*.zip", "!*.woff", "!*.woff2", "!*.ttf"]


def load_known_dois() -> dict[str, dict]:
    """Les kanoniske DOI-er fra doi-map.json. Returnerer {doi: {title, paper_type, repo_dir}}."""
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
    """Én rg-pass over repoet: DOI -> sett av filer (relative baner) som nevner den."""
    args = ["rg", "-H", "-o", "-N", r"10\.6084/m9\.figshare\.\d+"]
    for g in SKIP_GLOBS:
        args += ["-g", g]
    args += ["."]
    proc = subprocess.run(args, cwd=REPO, capture_output=True, text=True)
    if proc.returncode not in (0, 1):
        # rc=1 = ingen treff (rg); andre verdier = feil
        if proc.returncode != 1:
            raise RuntimeError(f"rg failed rc={proc.returncode}: {proc.stderr[:400]}")

    refs: dict[str, set[str]] = {}
    for line in proc.stdout.splitlines():
        # format: "sti:DOI" (med -H er filnavn alltid prefikset)
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
    """DOI-er som bare står i doi-map.json (aldri projisert til en annen fil)."""
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
            print(f"FAIL: {len(orphans)} orphan DOI-er (kun i doi-map, aldri projisert):")
            for d in orphans:
                print(f"  - {d}")
            return 1
        print(f"OK: ingen orphan DOI-er ({manifest['totals']['known_dois']} kjente).")
        return 0

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Manifest skrevet: {MANIFEST.relative_to(REPO)}")
    print(f"  kjente DOI-er: {manifest['totals']['known_dois']}")
    print(f"  orphan DOI-er: {manifest['totals']['orphan_dois']}")
    print(f"  filer med DOI-ref: {manifest['totals']['files_referencing_dois']}")
    if orphans:
        print("Orphan DOI-er:")
        for d in orphans:
            print(f"  - {d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
