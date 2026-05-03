#!/usr/bin/env python3
"""
EFC Evidence Mirror
====================

Two ledger files MUST agree on the empirical/methodological/structural
DOI registers but historically drift apart:

  - docs/validation-ledger/data/evidence-register.json  (80 empirical)
  - docs/validation-ledger/data/ledger.json             (22 empirical)

This script enforces the invariant that ``ledger.json["evidence_register"]``
is a *superset* of the corresponding categories in ``evidence-register.json``.

Behaviour
---------
* For each category (empirical / methodological / structural) we union
  the two lists keyed by ``doi``. Whichever side has the entry wins;
  duplicates are deduplicated by DOI; ledger.json is overwritten with
  the merged result.
* evidence-register.json is also enriched with anything ledger.json
  knows about that the register doesn't — symmetric mirror.
* Additionally cross-references against repo paper directories: any
  paper whose ``paper_type`` ∈ {empirical_test, empirical_analysis,
  empirical_validation, sealed_prediction, observational_pipeline}
  but whose DOI is missing from BOTH registers gets added to the
  ``empirical`` list with the title from ``index.json``.

Idempotent. Safe to run as part of efc_maintain.

Exit codes
----------
  0  — clean (no changes or merged successfully)
  1  — fatal error (file missing / unreadable)
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")
EV_PATH = os.path.join(LEDGER_DATA, "evidence-register.json")
LEDGER_PATH = os.path.join(LEDGER_DATA, "ledger.json")

CATEGORIES = ("empirical", "methodological", "structural")
EMPIRICAL_TYPES = {
    "empirical_test", "empirical_analysis", "empirical_validation",
    "sealed_prediction", "observational_pipeline",
}
METHODOLOGY_TYPES = {"methodology"}
STRUCTURAL_TYPES = {"theory", "infrastructure"}

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

FIGSHARE_DOI_RE = re.compile(r"(\d{7,9})")


def _bare(doi):
    if not doi:
        return None
    m = FIGSHARE_DOI_RE.search(str(doi))
    return m.group(1) if m else None


def _load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def _save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def _dedup_by_doi(entries):
    seen = {}
    for e in entries:
        if not isinstance(e, dict):
            continue
        b = _bare(e.get("doi"))
        if not b:
            continue
        # Prefer the entry that has a non-empty "name"
        existing = seen.get(b)
        if existing is None:
            seen[b] = {**e, "doi": b}
        elif not (existing.get("name") or "").strip() and (e.get("name") or "").strip():
            seen[b] = {**e, "doi": b}
    return [seen[k] for k in sorted(seen)]


def _category_for_paper_type(paper_type):
    pt = (paper_type or "").lower()
    if pt in EMPIRICAL_TYPES:
        return "empirical"
    if pt in METHODOLOGY_TYPES:
        return "methodological"
    if pt in STRUCTURAL_TYPES:
        return "structural"
    return None


def _gather_repo_evidence():
    """Walk paper dirs and produce {category: [{doi, name, category}]}."""
    out = {c: [] for c in CATEGORIES}
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(PAPERS, name)
        if not os.path.isdir(full):
            continue
        idx = _load(os.path.join(full, "index.json")) or {}
        bare = _bare(idx.get("doi"))
        if not bare:
            continue
        cat = _category_for_paper_type(idx.get("paper_type"))
        if not cat:
            continue
        title = idx.get("title") or name
        out[cat].append({"doi": bare, "name": title, "category": cat})
    return out


def main():
    ev = _load(EV_PATH)
    ld = _load(LEDGER_PATH)
    if not isinstance(ev, dict) or not isinstance(ld, dict):
        print("[efc-evidence-mirror] cannot load registers", file=sys.stderr)
        return 1

    repo_evidence = _gather_repo_evidence()

    ev.setdefault("categories", {})
    ld.setdefault("evidence_register", {})

    summary = {}
    for cat in CATEGORIES:
        ev_list = ev["categories"].get(cat) or []
        ld_list = ld["evidence_register"].get(cat) or []
        if not isinstance(ev_list, list):
            ev_list = []
        if not isinstance(ld_list, list):
            ld_list = []
        repo_list = repo_evidence.get(cat, [])

        merged = _dedup_by_doi(list(ev_list) + list(ld_list) + list(repo_list))

        ev_count_before = len(_dedup_by_doi(ev_list))
        ld_count_before = len(_dedup_by_doi(ld_list))
        merged_count = len(merged)

        ev["categories"][cat] = merged
        ld["evidence_register"][cat] = merged

        summary[cat] = {
            "ev_before": ev_count_before,
            "ld_before": ld_count_before,
            "after": merged_count,
            "added_to_ev": merged_count - ev_count_before,
            "added_to_ld": merged_count - ld_count_before,
        }

    _save(EV_PATH, ev)
    _save(LEDGER_PATH, ld)

    print("=" * 72)
    print("EFC Evidence Mirror — registers reconciled")
    print("=" * 72)
    for cat, s in summary.items():
        print(
            f"  {cat:<14}  ev:{s['ev_before']:>3} → {s['after']:>3}  "
            f"(+{s['added_to_ev']})    ledger:{s['ld_before']:>3} → "
            f"{s['after']:>3} (+{s['added_to_ld']})"
        )
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
