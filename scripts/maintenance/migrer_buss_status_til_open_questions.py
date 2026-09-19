#!/usr/bin/env python3
"""Migrate the bank's OWN waiting state into `open_questions`.

Background, measured 2026-09-18: the atlas question tab was empty after the
generated line («no evidence yet — hypothesis marked honestly», identical for
all seven) was removed — rightly so, it was not a question. But 26 nodes in
the bank ALREADY declare that something stands open, in the field
`buss_status`, in the two formulations held verbatim in
`AAPNE_FORMULERINGER` below (2 nodes and 24 nodes, measured 2026-09-18).

Those declarations were invisible in the atlas. This migration moves them into
`open_questions`, VERBATIM — the question is the node's own text, not a
rewrite. No `to` is set: who is to solve it is not in the bank, and an
invented owner is worse than an empty field.

The migration is idempotent: a node that already has `open_questions` is left
alone. Writing requires `--skriv`; the default is a dry run.

    python3 scripts/maintenance/migrer_buss_status_til_open_questions.py --vis
    python3 scripts/maintenance/migrer_buss_status_til_open_questions.py --skriv
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROT / "schema" / "regime_nodes.jsonld"

#: The formulations that mean «this node stands open». Only the measured ones.
AAPNE_FORMULERINGER = (
    "stroemmen finnes ikke — venter paa konnektor",
    "ingen buss-vei — emnet finnes ikke som domene i snapshotet",
)


def _buss_status(node: dict) -> str:
    """The declaration sits under `stipulasjoner` (measured: 25 of 126 nodes).

    The first version read `node["buss_status"]` and found nothing: the field
    exists, but somewhere else. A migration that searches in the wrong place
    and reports «nothing to do» looks like a finished job.
    """
    stip = node.get("stipulasjoner") or {}
    return str(node.get("buss_status") or stip.get("buss_status") or "").strip()


def aapne_noder(noder: list[dict]) -> list[tuple[str, str]]:
    """[(node-id, the declaration)] for nodes that declare an open state."""
    ut = []
    for n in noder:
        bs = _buss_status(n)
        if not bs or n.get("open_questions"):
            continue
        if any(f in bs for f in AAPNE_FORMULERINGER):
            ut.append((n["id"], bs))
    return ut


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--skriv", action="store_true",
                   help="write to the bank (default: dry run)")
    p.add_argument("--vis", action="store_true", help="show each node")
    a = p.parse_args()

    data = json.loads(BANK.read_text(encoding="utf-8"))
    kandidater = aapne_noder(data["nodes"])
    print(f"{len(kandidater)} nodes declare an open state "
          f"and lack open_questions")
    if a.vis:
        for nid, bs in kandidater:
            print(f"  {nid}: {bs[:80]}")
    if not a.skriv:
        print("dry run — nothing written (use --skriv)")
        return 0
    if not kandidater:
        print("nothing to do")
        return 0

    per_id = dict(kandidater)
    for n in data["nodes"]:
        if n["id"] in per_id:
            # Verbatim. The question IS the node's own declaration.
            n["open_questions"] = [f"{n['id']}: {per_id[n['id']]}"]
    BANK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

    bank = json.loads(BANK.read_text(encoding="utf-8"))
    carried = [n["id"] for n in bank["nodes"] if n.get("open_questions")]
    print(f"written: {len(carried)} nodes have open_questions")
    if len(carried) != len(kandidater):
        print(f"MISMATCH: expected {len(kandidater)}, found {len(carried)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
