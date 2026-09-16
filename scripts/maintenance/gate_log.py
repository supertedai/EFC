#!/usr/bin/env python3
"""gate_log.py — ekstern audit-logg for sikkerhetskritiske hendelser.

Repo-loggen er en lesbar projeksjon; DENNE loggen ligger UTENFOR repoet
(/opt/opus-ledger/efc-gate-hendelser.jsonl) og er det en repo-admin
ikke kan omskrive usett. Skriver append-only, atomisk, med monoton
sekvens.

Bruk: python3 scripts/maintenance/gate_log.py <gate_type> <kort> <utfall> [beskrivelse]
Exit: 0 = skrevet og lest tilbake, 1 = feil.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

STI = Path(os.environ.get("EFC_GATE_LOGG", "/opt/opus-ledger/efc-gate-hendelser.jsonl"))


def hoved() -> int:
    if len(sys.argv) < 4:
        print("bruk: gate_log.py <gate_type> <kort> <utfall> [beskrivelse]", file=sys.stderr)
        return 2
    gate_type, kort, utfall = sys.argv[1], sys.argv[2], sys.argv[3]
    beskrivelse = sys.argv[4] if len(sys.argv) > 4 else ""
    hendelse = {
        "sekvens": None, "ts": datetime.now(timezone.utc).isoformat(),
        "gate": gate_type, "kort": kort, "utfall": utfall,
        "beskrivelse": beskrivelse, "skrevet_av": os.environ.get("USER", "ukjent"),
    }
    try:
        if STI.is_file():
            linjer = [l for l in STI.read_text(encoding="utf-8").splitlines() if l.strip()]
            siste = json.loads(linjer[-1]) if linjer else {"sekvens": 0}
            hendelse["sekvens"] = int(siste.get("sekvens") or 0) + 1
        else:
            STI.parent.mkdir(parents=True, exist_ok=True)
            hendelse["sekvens"] = 1
        # atomisk: temp-fil i samme katalog, så rename
        fd, tmp = tempfile.mkstemp(dir=str(STI.parent), prefix=".gate-", suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(hendelse, ensure_ascii=False) + "\n")
        with open(STI, "a", encoding="utf-8") as f:
            f.write(json.dumps(hendelse, ensure_ascii=False) + "\n")
        os.unlink(tmp)
        # readback
        lest = [l for l in STI.read_text(encoding="utf-8").splitlines() if l.strip()]
        ok = json.loads(lest[-1]).get("sekvens") == hendelse["sekvens"]
        if not ok:
            print("readback feilet — linja sto ikke på disk", file=sys.stderr)
            return 1
        print(f"gate-hendelse {hendelse['sekvens']}: {gate_type} {kort} {utfall}")
        return 0
    except OSError as e:
        print(f"feil: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(hoved())
