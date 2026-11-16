#!/usr/bin/env python3
"""efc_escalation_digest.py — report escalated claims for the owner.

Scans data/triangulation/*.json for claims whose action is 'escalate' or
'owner-gate', and prints a compact digest. Exit 0 and 'no escalated claims'
when the queue is empty. Read-only: never mutates a record.

A claim record is the output of efc_triangulate.classify() plus its statement,
written by the triangulation wiring. A resolved claim drops out of the digest
once its action is no longer 'escalate'/'owner-gate'.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DIR = REPO / "data" / "triangulation"


def load_claims() -> list[dict]:
    if not DIR.exists():
        return []
    claims: list[dict] = []
    for p in sorted(DIR.glob("*.json")):
        try:
            claims.append(json.loads(p.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return claims


def escalated(claims: list[dict]) -> list[dict]:
    return [c for c in claims if c.get("action") in ("escalate", "owner-gate")]


def main() -> int:
    claims = escalated(load_claims())
    if not claims:
        # stdout stays empty so a no_agent cron stays silent; stderr is for manual runs.
        print("no escalated claims", file=sys.stderr)
        return 0
    print(f"{len(claims)} escalated claim(s):")
    for c in claims:
        why = c.get("support_status") or c.get("independence_status") or c.get("kind", "?")
        n = c.get("n_sources", 0)
        print(f"  - {c.get('claim_id', '?')} [{c.get('kind', '?')}] "
              f"{c.get('statement', '')[:80]} — {why} — {n} source(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
