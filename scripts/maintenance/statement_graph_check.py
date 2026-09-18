#!/usr/bin/env python3
"""statement_graph_check.py — phase 1 checks for the EFC statement graph.

Checks that public/graph/statements.yaml + evidence.yaml hang together:
unique IDs, referential integrity, owner and status on everything, no
superseded marked active, evidence pointers that exist, and that appears_on
pages exist in page-meta. Orphan statements (empty appears_on) are INFO
findings in phase 1 — the page mapping is a separate work queue, not an
error.

Usage:
    python3 scripts/maintenance/statement_graph_check.py          # human report
    python3 scripts/maintenance/statement_graph_check.py --json   # machine-readable (CI)

Exit: 0 = no hard errors; 1 = hard errors; 2 = usage error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GRAPH = ROOT / "public" / "graph"
PAGE_META = ROOT / "public" / "page-meta"

ID_FORMAT = re.compile(r"^(efc|ev)\.[a-z0-9]+\.[a-z0-9]+(\.[a-z0-9]+)?$")
STATUS_VALID = {"active", "superseded", "withdrawn", "candidate", "falsified"}
LEVEL_VALID = {"documented", "reconstruction", "partial_support",
                "pending_external_validation", "independent_support",
                "falsified", "superseded"}


def _last_yaml(path: Path) -> dict:
    import yaml  # ships with the repo's dependencies
    with open(path, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d if isinstance(d, dict) else {}


def scan() -> dict:
    findings: dict[str, list[dict]] = {
        "harde": [], "info": [],
        "orphan": [], "dangling_reference": [], "missing_owner": [],
        "unsupported_claim": [], "hidden_contradiction": [],
    }
    if not GRAPH.is_dir() or not PAGE_META.is_dir():
        findings["harde"].append({"type": "missing_structure",
                              "msg": "public/graph/ or public/page-meta/ is missing"})
        return findings
    st = _last_yaml(GRAPH / "statements.yaml").get("statements", [])
    ev = _last_yaml(GRAPH / "evidence.yaml").get("evidence", [])
    meta_pages = {p.stem for p in PAGE_META.glob("*.yaml")}
    st_ids: dict[str, dict] = {}
    ev_ids: dict[str, dict] = {}

    for s in st:
        sid = s.get("statement_id")
        if not isinstance(sid, str) or not ID_FORMAT.match(sid):
            findings["harde"].append({"type": "invalid_statement_id", "msg": f"invalid ID: {sid!r}"})
            continue
        if sid in st_ids:
            findings["harde"].append({"type": "duplicate_statement_id", "msg": f"duplicate: {sid}"})
        st_ids[sid] = s
        if not s.get("owner_role"):
            findings["missing_owner"].append({"id": sid})
        if s.get("status") not in STATUS_VALID:
            findings["harde"].append({"type": "invalid_status", "id": sid, "status": s.get("status")})
        if s.get("epistemic_level") not in LEVEL_VALID:
            findings["harde"].append({"type": "invalid_epistemic_level",
                                  "id": sid, "level": s.get("epistemic_level")})
        if s.get("status") == "superseded" and not s.get("supersedes"):
            pass  # superseded stands on its own; nothing to require
        if not s.get("appears_on"):
            findings["orphan"].append({"id": sid, "text": (s.get("text") or "")[:60]})
        else:
            for a in s["appears_on"]:
                pid = a.get("page_id")
                if pid not in meta_pages:
                    findings["dangling_reference"].append(
                        {"id": sid, "page": pid, "msg": "the page does not exist in page-meta"})
        if s.get("status") == "active" and s.get("supersedes"):
            superseded_by = s["supersedes"]
            if isinstance(superseded_by, list):
                for g in superseded_by:
                    old = st_ids.get(g)
                    if old and old.get("status") == "active":
                        findings["hidden_contradiction"].append(
                            {"id": sid, "msg": f"{g} is superseded but still active"})
        ev_refs = s.get("supported_by") or []
        if not ev_refs and s.get("kind") not in ("model_definition", "hypothesis"):
            findings["unsupported_claim"].append(
                {"id": sid, "kind": s.get("kind"),
                 "msg": "empirical/similar claim without evidence or hypothesis status"})

    for e in ev:
        eid = e.get("evidence_id")
        if not isinstance(eid, str) or not ID_FORMAT.match(eid):
            findings["harde"].append({"type": "invalid_evidence_id", "msg": f"invalid: {eid!r}"})
            continue
        if eid in ev_ids:
            findings["harde"].append({"type": "duplicate_evidence_id", "msg": f"duplicate: {eid}"})
        ev_ids[eid] = e
        if e.get("type") == "external_source":
            loc = e.get("locator") or {}
            if not (loc.get("doi") or loc.get("url")):
                findings["harde"].append(
                    {"type": "external_source_uten_lenke", "id": eid,
                     "msg": "an external source must have a doi or url in locator"})
        for ref in e.get("supports_scope", []):
            if ref not in st_ids:
                findings["dangling_reference"].append(
                    {"id": eid, "msg": f"the evidence supports an unknown statement {ref}"})

    for s in st:
        for ref in (s.get("supported_by") or []):
            if ref not in ev_ids:
                findings["dangling_reference"].append(
                    {"id": s.get("statement_id"), "msg": f"unknown evidence {ref}"})
        for ref in (s.get("contradicts") or []) + (s.get("supersedes") or []):
            if ref not in st_ids:
                findings["dangling_reference"].append(
                    {"id": s.get("statement_id"), "msg": f"unknown statement {ref}"})

    return findings


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    findings = scan()
    if a.json:
        print(json.dumps(findings, ensure_ascii=False, indent=1))
    else:
        print(f"statement-graf: {len(findings['harde'])} hard errors, "
              f"{len(findings['orphan'])} orphan (info), "
              f"{len(findings['dangling_reference'])} dangling, "
              f"{len(findings['missing_owner'])} without an owner, "
              f"{len(findings['unsupported_claim'])} without support")
        for f in findings["harde"][:20]:
            print("  HARD:", f)
        for f in (findings["dangling_reference"] + findings["missing_owner"]
                  + findings["unsupported_claim"])[:20]:
            print("  FINDING:", f)
        for f in findings["orphan"][:20]:
            print("  INFO (not yet mapped to a page):", f["id"], "-", f["text"])
    return 1 if findings["harde"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
