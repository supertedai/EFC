#!/usr/bin/env python3
"""
EFC Paper Index Regenerator
============================

Rebuilds ``docs/papers/efc/efc_index.json`` deterministically from the
contents of every paper directory. The file is the canonical
"manifest of papers" the rest of the toolchain refers to via
``sync_efc_index()`` in efc_sync_dois.py.

When this file is missing (or a placeholder), every downstream sync
step fails silently. This script restores it.

Schema
------
{
  "version":     "1.<minor>",
  "generated":   "<ISO-8601 timestamp>",
  "root":        "docs/papers/efc",
  "paper_count": <int>,
  "papers": [
    {
      "id":      "<slug>",
      "path":    "<directory_name>",
      "type":    "<paper_type | 'paper'>",
      "doi":     "10.6084/m9.figshare.NNNNNNNN" | null,
      "title":   "<title>",
      "tier":    "T1|T2|T3|null"
    },
    …
  ]
}

Behaviour
---------
* Idempotent — reads the existing file (if non-placeholder) and
  reuses its ``id`` field per paper to avoid breaking external
  references that pin to ``id``. New papers get an ``id`` derived
  from the directory slug.
* Additive — never deletes a paper from the manifest unless its
  directory is gone from disk.
* Bumps minor version on every successful write that produces a diff.

Exit codes
----------
  0  — clean (no diff or successful write)
  1  — could not read paper directories (fatal)
"""
from __future__ import annotations
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
INDEX_PATH = os.path.join(PAPERS, "efc_index.json")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
    "_archived",
}

FIGSHARE_DOI_RE = re.compile(r"10\.6084/m9\.figshare\.(\d{7,9})")


def _load_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _normalise_doi(doi):
    if not doi:
        return None
    s = str(doi).strip()
    for pfx in ("https://doi.org/", "http://doi.org/", "doi:"):
        if s.lower().startswith(pfx):
            s = s[len(pfx):]
            break
    m = FIGSHARE_DOI_RE.search(s)
    if m:
        return f"10.6084/m9.figshare.{m.group(1)}"
    bare = re.match(r"^(\d{7,9})$", s)
    if bare:
        return f"10.6084/m9.figshare.{bare.group(1)}"
    return None


def _slugify_id(directory):
    """Default id derivation when no previous id is known."""
    return directory.lower().replace(" ", "-").replace("_", "-")


def _bump_minor(version):
    try:
        major, minor = str(version).split(".")
        return f"{major}.{int(minor) + 1}"
    except (ValueError, AttributeError):
        return "1.0"


def main():
    if not os.path.isdir(PAPERS):
        print(f"[efc-regen-index] {PAPERS} not found", file=sys.stderr)
        return 1

    existing = _load_json(INDEX_PATH)
    is_real_existing = isinstance(existing, dict) and "papers" in existing

    prev_by_path = {}
    if is_real_existing:
        for p in existing.get("papers", []):
            if isinstance(p, dict) and p.get("path"):
                prev_by_path[p["path"]] = p

    papers = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(PAPERS, name)
        if not os.path.isdir(full):
            continue

        idx = _load_json(os.path.join(full, "index.json")) or {}
        prev = prev_by_path.get(name, {})

        title = idx.get("title") or prev.get("title") or name
        doi = _normalise_doi(idx.get("doi")) or prev.get("doi")
        paper_type = idx.get("paper_type") or prev.get("type") or "paper"
        tier = idx.get("tier") or prev.get("tier")
        prev_id = prev.get("id")
        entry_id = prev_id or _slugify_id(name)

        entry = {
            "id": entry_id,
            "path": name,
            "type": paper_type,
            "doi": doi,
            "title": title,
        }
        if tier:
            entry["tier"] = tier
        papers.append(entry)

    new_doc = {
        "version": _bump_minor(existing.get("version", "1.0")) if is_real_existing else "2.0",
        "generated": datetime.now(timezone.utc).isoformat(),
        "root": "docs/papers/efc",
        "paper_count": len(papers),
        "papers": papers,
    }

    if is_real_existing:
        prev_papers_signature = json.dumps(
            sorted(
                ((p.get("path"), p.get("doi"), p.get("type"), p.get("title"))
                 for p in existing.get("papers", []) if isinstance(p, dict)),
                key=lambda x: x[0] or "",
            ),
            sort_keys=True,
        )
        new_papers_signature = json.dumps(
            sorted(
                ((p["path"], p.get("doi"), p["type"], p.get("title"))
                 for p in papers),
                key=lambda x: x[0] or "",
            ),
            sort_keys=True,
        )
        if prev_papers_signature == new_papers_signature:
            print(f"[efc-regen-index] no diff — {len(papers)} papers, version {existing.get('version')}")
            return 0

    _save_json(INDEX_PATH, new_doc)
    print(f"[efc-regen-index] wrote efc_index.json — {len(papers)} papers, version {new_doc['version']}")
    if not is_real_existing:
        print("[efc-regen-index] previous file was placeholder/missing — full rebuild")
    return 0


if __name__ == "__main__":
    sys.exit(main())
