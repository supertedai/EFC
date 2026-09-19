#!/usr/bin/env python3
"""gate_log.py — external audit log for security-critical events.

The repo log is a readable projection; THIS log lives OUTSIDE the repo
(/opt/opus-ledger/efc-gate-hendelser.jsonl) and is what a repo admin
cannot rewrite unseen. Writes append-only, atomically, with a monotonic
sequence.

Usage: python3 scripts/maintenance/gate_log.py <gate_type> <kort> <utfall> [beskrivelse]
Exit: 0 = written and read back, 1 = error.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path(os.environ.get("EFC_GATE_LOGG", "/opt/opus-ledger/efc-gate-hendelser.jsonl"))


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: gate_log.py <gate_type> <kort> <utfall> [beskrivelse]", file=sys.stderr)
        return 2
    gate_type, card, outcome = sys.argv[1], sys.argv[2], sys.argv[3]
    description = sys.argv[4] if len(sys.argv) > 4 else ""
    event = {
        "sekvens": None, "ts": datetime.now(timezone.utc).isoformat(),
        "gate": gate_type, "kort": card, "utfall": outcome,
        "beskrivelse": description, "skrevet_av": os.environ.get("USER", "unknown"),
    }
    try:
        if LOG_PATH.is_file():
            lines = [l for l in LOG_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
            last = json.loads(lines[-1]) if lines else {"sekvens": 0}
            event["sekvens"] = int(last.get("sekvens") or 0) + 1
        else:
            LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
            event["sekvens"] = 1
        # atomic: temp file in the same directory, then rename
        fd, tmp = tempfile.mkstemp(dir=str(LOG_PATH.parent), prefix=".gate-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
        os.unlink(tmp)
        # readback
        read = [l for l in LOG_PATH.read_text(encoding="utf-8").splitlines() if l.strip()]
        ok = json.loads(read[-1]).get("sekvens") == event["sekvens"]
        if not ok:
            print("readback failed — the line was not on disk", file=sys.stderr)
            return 1
        print(f"gate-event {event['sekvens']}: {gate_type} {card} {outcome}")
        return 0
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
