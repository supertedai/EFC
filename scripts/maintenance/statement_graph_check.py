#!/usr/bin/env python3
"""statement_graph_check.py — phase 1 checks for the EFC statement graph.

Checks that public/graph/statements.yaml + evidence.yaml hang together:
unique IDs, referential integrity, owner and status on everything, no
superseded marked active, evidence pointers that exist, and that appears_on
pages exist in page-meta. Orphan statements (empty appears_on) are INFO
findings in phase 1 — the page mapping is a separate work queue, not an
error.

The anchor checks (the stale_page class) are HARD:
  * an appears_on entry with an `anchor` MUST exist as
    data-statement-id="<anchor>" in the page it points at (anchor_missing);
  * a page carrying a data-statement-id the graph does not attribute to it is
    a self-contradiction (anchor_ghost);
  * a primary page without an anchor is an unverifiable main coupling
    (primary_uten_anker).
A coupling WITHOUT an anchor is not verified; it is listed in anchor_queue
(INFO) as a work queue, and made hard by setting `anchor` once it has been
checked against the page.

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


# ---------------------------------------------------------------------------
# The anchor machinery (the stale_page class)
# ---------------------------------------------------------------------------
# A statement the graph says stands on a public page must be VISIBLE on that
# page. The anchor is an HTML attribute — data-statement-id="<id>" — on the
# element carrying the statement. Without it, appears_on is a claim about a page
# nobody can check: the phase-1 mapping (2026-09-17) concluded with four orphan
# statements that all existed on the pages, and with three couplings
# (efc.sparc.001) to pages that do not carry them. Both error directions are
# caught here.
ANCHOR_ATTR = re.compile(r'data-statement-id\s*=\s*"([^"]+)"')


def _page_path(page_id: str, meta: dict) -> Path | None:
    """The path to the page behind page_id, or None if it does not exist."""
    m = meta.get(page_id) or {}
    raw = str(m.get("path") or "").strip()
    if not raw:
        return None
    candidate = raw.split(" ")[0].lstrip("/")   # "/docs/index.html — the entry page"
    for path in (ROOT / "docs" / "public" / candidate, ROOT / candidate,
                 ROOT / "docs" / candidate):
        if path.is_file():
            return path
    return None


def _anchors(path: Path) -> set[str]:
    return set(ANCHOR_ATTR.findall(path.read_text(encoding="utf-8", errors="replace")))


def scan() -> dict:
    findings: dict[str, list[dict]] = {
        "harde": [], "info": [],
        "orphan": [], "dangling_reference": [], "missing_owner": [],
        "unsupported_claim": [], "hidden_contradiction": [],
        "anchor_missing": [], "anchor_ghost": [], "anchor_queue": [],
    }
    if not GRAPH.is_dir() or not PAGE_META.is_dir():
        findings["harde"].append({"type": "missing_structure",
                              "msg": "public/graph/ or public/page-meta/ is missing"})
        return findings
    st = _last_yaml(GRAPH / "statements.yaml").get("statements", [])
    ev = _last_yaml(GRAPH / "evidence.yaml").get("evidence", [])
    meta_pages = {p.stem for p in PAGE_META.glob("*.yaml")}
    page_meta = {p.stem: (_last_yaml(p)) for p in PAGE_META.glob("*.yaml")}
    page_anchors: dict[str, set[str]] = {}
    for pid in meta_pages:
        path = _page_path(pid, page_meta)
        page_anchors[pid] = _anchors(path) if path else set()
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
                    continue
                anchor = a.get("anchor")
                if not anchor:
                    findings["anchor_queue"].append(
                        {"id": sid, "page": pid, "role": a.get("role") or "cited",
                         "msg": "appears_on without anchor — not verified against the page text"})
                    if (a.get("role") or "") == "primary":
                        findings["harde"].append(
                            {"type": "primary_uten_anker", "id": sid, "page": pid,
                             "msg": "a primary page must carry a checkable anchor"})
                    continue
                if anchor not in page_anchors.get(pid, set()):
                    findings["anchor_missing"].append(
                        {"id": sid, "page": pid, "anchor": anchor,
                         "msg": 'the page does not contain data-statement-id="%s"' % anchor})
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

    # --- anchor ghost: a page carries an anchor the graph does not attribute to it ---
    required: set[tuple[str, str]] = set()
    for s in st:
        for a in (s.get("appears_on") or []):
            if a.get("page_id") and a.get("anchor"):
                required.add((a["page_id"], a["anchor"]))
    for pid, anchors in page_anchors.items():
        for anchor in sorted(anchors):
            if (pid, anchor) not in required:
                findings["anchor_ghost"].append(
                    {"page": pid, "anchor": anchor,
                     "msg": "the page carries an anchor the graph does not attribute to it"})

    return findings


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    findings = scan()
    # Anchor breaches are hard: a verified coupling that does not hold, or an
    # anchor the page carries without the graph attributing that statement to it.
    hard = (list(findings["harde"]) + list(findings["anchor_missing"])
            + list(findings["anchor_ghost"]))
    if a.json:
        findings["harde"] = hard
        print(json.dumps(findings, ensure_ascii=False, indent=1))
    else:
        print(f"statement-graf: {len(hard)} hard errors, "
              f"{len(findings['orphan'])} orphan (info), "
              f"{len(findings['dangling_reference'])} dangling, "
              f"{len(findings['missing_owner'])} without an owner, "
              f"{len(findings['unsupported_claim'])} without support, "
              f"{len(findings['anchor_queue'])} in the anchor queue (info)")
        for f in hard[:20]:
            print("  HARD:", f)
        for f in (findings["dangling_reference"] + findings["missing_owner"]
                  + findings["unsupported_claim"])[:20]:
            print("  FINDING:", f)
        for f in findings["orphan"][:20]:
            print("  INFO (not yet mapped to a page):", f["id"], "-", f["text"])
        for f in findings["anchor_queue"][:20]:
            print("  INFO (coupling without an anchor):", f["id"], "->", f["page"])
    return 1 if hard else 0


if __name__ == "__main__":
    raise SystemExit(main())
