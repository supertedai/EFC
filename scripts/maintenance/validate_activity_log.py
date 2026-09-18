#!/usr/bin/env python3
"""validate_activity_log.py — phase 1 check of logs/activity.jsonl.

Append-only is a git property, not a file property: CI runs with
--base origin/main and requires that the diff on logs/ is ONLY insertions
(checked in the CI step, not here — here the lines are validated). This script
checks per line: valid JSON, required fields, unique event_id, valid ISO-8601
time, known action, role within the enum.

The status words (t_882cfca): `statusord` is an OPTIONAL list with values from
{maskinelt kontrollert, eksternt verifisert, faglig godkjent}. The three words
are mutually independent — none of them implies the other two, and the guard
never adds or requires a word that is not in the post. The one rule enforced:
"faglig godkjent" can only stand on a post with role=menneske, because
professional approval cannot be delegated to a label (the decision 2026-09-17,
section "Three status words that must never be mixed"). Writing "maskinelt
kontrollert" is process control and can be done by a profile; writing
"faglig godkjent" is the human's.

Usage: python3 scripts/maintenance/validate_activity_log.py [--json]
Exit: 0 = OK, 1 = error.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
LOGG = ROT / "logs" / "activity.jsonl"

AKSJONER = {
    "card_created", "lease_acquired", "branch_created", "file_changed",
    "validation_finished", "commit_created", "pr_opened", "review_completed",
    "merge_completed", "remote_readback", "public_readback", "blocked",
    "unblocked", "card_closed", "rollback_completed",
}
ROLLER = {"researcher", "orchestrator", "faber", "opus-core", "verifier", "legacy", "menneske"}
STATUSORD = {"maskinelt kontrollert", "eksternt verifisert", "faglig godkjent"}
MENNESKELIGE_ORD = {"faglig godkjent"}
PLIKT = ["event_id", "occurred_at", "action", "role", "kanban_card",
         "files", "why", "result", "reversible"]


def sjekk_statusord(e: dict, nr: int) -> list[dict]:
    """The status words are mutually independent.

    This function NEVER adds a word and NEVER requires a word that is not in
    the post — it only rejects unknown values, duplicates, an empty list, and
    "faglig godkjent" on a post that is not the human's.
    """
    feil: list[dict] = []
    if "statusord" not in e:
        return feil
    v = e["statusord"]
    if not isinstance(v, list) or not v:
        return [{"type": "bad_statusord", "linje": nr,
                 "msg": "statusord must be a non-empty list"}]
    sett: set[str] = set()
    for ord_ in v:
        if ord_ not in STATUSORD:
            feil.append({"type": "unknown_statusord", "linje": nr, "statusord": ord_})
        if ord_ in sett:
            feil.append({"type": "duplicate_statusord", "linje": nr, "statusord": ord_})
        sett.add(ord_)
    if (sett & MENNESKELIGE_ORD) and e.get("role") != "menneske":
        feil.append({"type": "faglig_godkjent_uten_menneske", "linje": nr,
                     "role": e.get("role")})
    return feil


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    feil = []
    sett = set()
    if not LOGG.is_file():
        feil.append({"type": "missing_log", "msg": str(LOGG)})
    else:
        for nr, linje in enumerate(LOGG.read_text(encoding="utf-8").splitlines(), 1):
            if not linje.strip():
                continue
            try:
                e = json.loads(linje)
            except json.JSONDecodeError as ex:
                feil.append({"type": "invalid_json", "linje": nr, "msg": str(ex)[:100]})
                continue
            for felt in PLIKT:
                if felt not in e or e[felt] in (None, ""):
                    feil.append({"type": "missing_field", "linje": nr, "felt": felt})
            if e.get("event_id") in sett:
                feil.append({"type": "duplicate_event_id", "linje": nr, "id": e["event_id"]})
            sett.add(e.get("event_id"))
            if e.get("action") not in AKSJONER:
                feil.append({"type": "unknown_action", "linje": nr, "action": e.get("action")})
            if e.get("role") not in ROLLER:
                feil.append({"type": "unknown_role", "linje": nr, "role": e.get("role")})
            try:
                datetime.fromisoformat(str(e.get("occurred_at", "")).replace("Z", "+00:00"))
            except ValueError:
                feil.append({"type": "invalid_timestamp", "linje": nr})
            feil += sjekk_statusord(e, nr)
    if a.json:
        print(json.dumps({"feil": feil}, ensure_ascii=False, indent=1))
    else:
        print(f"activity-log: {len(feil)} errors")
        for f in feil[:20]:
            print("  ", f)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
