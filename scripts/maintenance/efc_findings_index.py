#!/usr/bin/env python3
"""efc_findings_index.py — aggregate findings across review runs (deterministic).

Authority (generator with --check, same discipline as changelog_projeksjon.py).

Scans docs/validation-ledger/reviews/deleg_*/verdict.json and aggregates their
findings into docs/validation-ledger/data/findings_index.json.

  --check   exit 1 if the committed index drifts from regeneration
  --apply   (re)write the index

Determinism is part of the contract: the output depends ONLY on the committed
review artifacts, ordered deterministically. No wall-clock in the payload, no
per-run identifier that can drift between two identical invocations.

Revision separation: every row carries method_revision (from its verdict) and
release_eligible (revision >= 2, numeric). A legacy verdict with no
method_revision field is reported as revision "" and is NEVER release-eligible.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MIN_RELEASE_REVISION = 2


def _reviews_dir() -> Path:
    """Read at call time so tests can point EFC_REVIEWS_DIR at a temp dir."""
    return Path(os.environ.get("EFC_REVIEWS_DIR", ROOT / "docs" / "validation-ledger" / "reviews"))


def _out_path() -> Path:
    return Path(os.environ.get("EFC_FINDINGS_INDEX_OUT", ROOT / "docs" / "validation-ledger" / "data" / "findings_index.json"))


def _rev_number(rev: object) -> int:
    m = re.match(r"^v(\d+)$", str(rev or ""))
    return int(m.group(1)) if m else -1


def _norm(s: object) -> str:
    return " ".join(str(s).split())


def _signature(f: dict) -> str:
    layer = _norm(f.get("evidence_layer", ""))
    typ = _norm(f.get("type", ""))
    role = _norm(f.get("reviewer_role", ""))
    text = _norm(f.get("finding", ""))
    blob = f"{layer}\x00{typ}\x00{role}\x00{text}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _collect() -> list[dict]:
    rows: list[dict] = []
    reviews = _reviews_dir()
    if not reviews.is_dir():
        return rows
    for vp in sorted(reviews.glob("deleg_*/verdict.json")):
        try:
            v = json.loads(vp.read_text(encoding="utf-8"))
        except Exception:
            continue
        run = vp.parent.name
        revision = str(v.get("method_revision", ""))
        release_eligible = _rev_number(revision) >= MIN_RELEASE_REVISION
        for f in v.get("findings", []):
            if not isinstance(f, dict):
                continue
            rows.append({
                "run": run,
                "method_revision": revision,
                "release_eligible": release_eligible,
                "finding_id": f.get("finding_id", ""),
                "claim_id": f.get("claim_id", ""),
                "reviewer_role": f.get("reviewer_role", ""),
                "evidence_layer": f.get("evidence_layer", ""),
                "type": f.get("type", ""),
                "severity": f.get("severity", ""),
                "disposition": f.get("disposition"),
                "supports_or_attacks": f.get("supports_or_attacks", ""),
                "atlas_field": f.get("atlas_field"),
                "signature": _signature(f),
                "finding": _norm(f.get("finding", "")),
            })

    rows.sort(key=lambda r: (r["signature"], r["run"], r["finding_id"]))
    return rows


def build() -> dict:
    rows = _collect()
    by_sig: dict[str, list[dict]] = {}
    for r in rows:
        by_sig.setdefault(r["signature"], []).append(r)

    recurring: list[dict] = []
    resolved: list[dict] = []
    chronic: list[dict] = []
    for sig in sorted(by_sig):
        group = by_sig[sig]
        runs = sorted({r["run"] for r in group})
        revisions = sorted({r["method_revision"] for r in group})
        dispositions = sorted({str(r["disposition"]) for r in group if r["disposition"]})
        entry = {
            "signature": sig,
            "evidence_layer": group[0]["evidence_layer"],
            "type": group[0]["type"],
            "atlas_field": group[0]["atlas_field"],
            "finding": group[0]["finding"],
            "runs": runs,
            "revisions": revisions,
            "count": len(runs),
            "dispositions": dispositions,
        }
        if len(runs) >= 2:
            recurring.append(entry)
        if "accepted" in dispositions or "already-covered" in dispositions:
            resolved.append(entry)
        if "author-gate" in dispositions and "accepted" not in dispositions:
            chronic.append(entry)

    rev_summary: dict[str, dict] = {}
    for r in rows:
        key = r["method_revision"] or "(pre-revision pilot)"
        s = rev_summary.setdefault(key, {"runs": set(), "findings": 0, "release_eligible": r["release_eligible"]})
        s["runs"].add(r["run"])
        s["findings"] += 1
    revisions = {
        k: {"runs": sorted(v["runs"]), "findings": v["findings"], "release_eligible": v["release_eligible"]}
        for k, v in sorted(rev_summary.items())
    }

    return {
        "generated_by": "scripts/maintenance/efc_findings_index.py",
        "source_runs": sorted({r["run"] for r in rows}),
        "total_findings": len(rows),
        "revisions": revisions,
        "recurring": recurring,
        "resolved": resolved,
        "chronic": chronic,
        "rows": rows,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--check", action="store_true", help="exit 1 on drift from committed index")
    g.add_argument("--apply", action="store_true", help="(re)write the index")
    args = ap.parse_args(argv)

    data = build()
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    out = _out_path()

    if args.apply:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        print(f"wrote {out} ({len(data['rows'])} findings)")
        return 0

    if not out.exists():
        print(f"REFUSED: {out} does not exist (run --apply)", file=sys.stderr)
        return 1
    committed = out.read_text(encoding="utf-8")
    if committed != text:
        print(f"REFUSED: {out} drifts from regeneration (run --apply)", file=sys.stderr)
        return 1
    print(f"ok: {out} matches regeneration ({len(data['rows'])} findings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
