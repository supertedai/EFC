#!/usr/bin/env python3
"""Generate figshare/doi-map.json from ORCID cache + repo walk.

Replaces the legacy 19-byte PLACEHOLDER stub with a verifiable mapping that
records, per Figshare DOI, the local repo directory and packaging completeness.
Idempotent: re-running produces byte-identical output (modulo timestamp) when
no facts have changed.

Inputs read:
    .claude/orcid_sync_report.json  — ORCID source-of-truth cache
    docs/papers/efc/<paper>/index.json  — per-paper metadata

Outputs written:
    figshare/doi-map.json  — master mapping
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ORCID_CACHE = REPO_ROOT / ".claude" / "orcid_sync_report.json"
PAPERS_ROOT = REPO_ROOT / "docs" / "papers" / "efc"
OUTPUT = REPO_ROOT / "figshare" / "doi-map.json"

REQUIRED_FILES = {
    "index.json",
    "schema.json",
    "metadata.json",
    "README.md",
    "CITATION.cff",
    "citations.bib",
}
REQUIRED_DIRS = {"src", "data", "examples"}


def load_orcid_cache() -> dict:
    return json.loads(ORCID_CACHE.read_text())


def walk_paper_dirs() -> list[dict]:
    rows: list[dict] = []
    for index_path in sorted(PAPERS_ROOT.rglob("index.json")):
        if "_archived" in index_path.parts:
            continue
        # Skip nested same-name directories (e.g.
        # CMB-Thermodynamic-Interpretation/CMB-Thermodynamic-Interpretation/)
        # which exist as content containers for the parent's manifest, not as
        # separate papers.
        parent = index_path.parent
        if parent.parent.name == parent.name and parent.parent.parent.name == "efc":
            continue
        rel_dir = index_path.parent.relative_to(REPO_ROOT)
        try:
            data = json.loads(index_path.read_text())
        except json.JSONDecodeError:
            data = {}
        doi_full = data.get("doi", "")
        figshare_id = ""
        if "figshare." in doi_full:
            figshare_id = doi_full.split("figshare.")[-1].strip()
        files = {p.name for p in index_path.parent.iterdir() if p.is_file()}
        dirs = {p.name for p in index_path.parent.iterdir() if p.is_dir()}
        has_pdf = any(name.lower().endswith(".pdf") for name in files)
        has_jsonld = any(name.lower().endswith(".jsonld") for name in files)
        package_complete = (
            REQUIRED_FILES.issubset(files)
            and REQUIRED_DIRS.issubset(dirs)
            and has_pdf
            and has_jsonld
        )
        rows.append(
            {
                "doi": doi_full,
                "figshare_id": figshare_id,
                "title": data.get("title", ""),
                "date": data.get("date", ""),
                "version": data.get("version", ""),
                "repo_dir": str(rel_dir).replace("\\", "/"),
                "package_complete": package_complete,
                "has_pdf": has_pdf,
            }
        )
    return rows


def build_map() -> dict:
    cache = load_orcid_cache()
    papers = walk_paper_dirs()

    repo_dois = {p["figshare_id"] for p in papers if p["figshare_id"]}
    orcid_dois = {row["doi"] for row in cache.get("matched", []) if isinstance(row, dict)}
    if not orcid_dois:
        orcid_dois = set(cache.get("matched", []))

    duplicate_doi_dirs: dict[str, list[str]] = {}
    for paper in papers:
        fid = paper["figshare_id"]
        if not fid:
            continue
        duplicate_doi_dirs.setdefault(fid, []).append(paper["repo_dir"])
    duplicates = [
        {"doi": f"10.6084/m9.figshare.{fid}", "dirs": dirs, "action": "consolidate"}
        for fid, dirs in duplicate_doi_dirs.items()
        if len(dirs) > 1
    ]

    dirs_without_doi = [
        {"dir": p["repo_dir"], "action": "assign_doi_or_archive"}
        for p in papers
        if not p["figshare_id"]
    ]

    missing_repo_dirs = [
        {
            "figshare_id": row["doi"],
            "title": row["title"],
            "action": "create_paper_dir_or_decide_legacy",
        }
        for row in cache.get("on_orcid_not_in_repo", [])
        if isinstance(row, dict)
    ]

    return {
        "$schema": "https://supertedai.github.io/EFC/schema/doi-map.schema.json",
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "generator": "scripts/maintenance/generate_doi_map.py",
        "author": {
            "name": "Morten Magnusson",
            "orcid": cache.get("orcid_id", "0009-0002-4860-5095"),
            "figshare_authors_id": "20477774",
        },
        "totals": {
            "orcid_works": cache.get("orcid_works_count", 0),
            "orcid_dois": cache.get("orcid_dois_count", 0),
            "repo_paper_dirs": len(papers),
            "repo_unique_dois": len(repo_dois),
            "matched_count": cache.get("matched_count", 0),
            "missing_paper_dirs": cache.get("on_orcid_not_in_repo_count", 0),
            "duplicate_doi_dirs": len(duplicates),
            "dirs_without_doi": len(dirs_without_doi),
            "complete_packages": sum(1 for p in papers if p["package_complete"]),
        },
        "papers": papers,
        "missing_repo_dirs": missing_repo_dirs,
        "duplicate_doi_dirs": duplicates,
        "dirs_without_doi": dirs_without_doi,
    }


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    payload = build_map()
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    totals = payload["totals"]
    print(
        f"[doi-map] wrote {OUTPUT.relative_to(REPO_ROOT)} — "
        f"{totals['repo_paper_dirs']} dirs, "
        f"{totals['repo_unique_dois']} unique DOIs, "
        f"{totals['complete_packages']} complete packages, "
        f"{totals['missing_paper_dirs']} missing on ORCID, "
        f"{totals['duplicate_doi_dirs']} duplicate-DOI dirs, "
        f"{totals['dirs_without_doi']} dirs without DOI"
    )


if __name__ == "__main__":
    main()
