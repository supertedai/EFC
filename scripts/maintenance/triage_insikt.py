#!/usr/bin/env python3
"""triage_insikt.py — phase 1 triage for insight candidates.

Validates against schemas/insight-candidate.schema.json and classifies
lav / middels / høy with a MANDATORY justification from the fields (can be
overridden by the verifier). No numeric score in phase 1 — the score is
calibrated against actual decisions once 20+ candidates exist.

Usage: python3 scripts/maintenance/triage_insikt.py <candidate.yaml>
Exit: 0 = valid candidate (triage written), 1 = invalid (needs-rework).
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
SKJEMA = ROT / "schemas" / "insight-candidate.schema.json"

TRIGGERE = {
    "hoy": [
        ("claim_type", "prediction"),
        ("claim_type", "correction"),
        ("falsification_test", None),  # testable -> a serious candidate
        ("counterevidence", None),     # counterevidence -> mature candidate
    ],
    "middels": [
        ("claim_type", "observation"),
        ("source_refs", 2),                    # ≥2 independent sources
    ],
}


def triage(k: dict) -> tuple[str, list[str]]:
    grunner: list[str] = []
    hoy = 0
    for felt, verdi in TRIGGERE["hoy"]:
        if verdi is None:
            if k.get(felt):
                hoy += 1
                grunner.append(f"{felt} is set")
        elif k.get(felt) == verdi:
            hoy += 1
            grunner.append(f"claim_type={verdi}")
    if hoy >= 2:
        return "høy", grunner
    middels = 0
    for felt, verdi in TRIGGERE["middels"]:
        if verdi is None:
            if k.get(felt):
                middels += 1
                grunner.append(f"{felt} is set")
        elif isinstance(verdi, int):
            if len(k.get(felt) or []) >= verdi:
                middels += 1
                grunner.append(f"≥{verdi} {felt}")
        elif k.get(felt) == verdi:
            middels += 1
            grunner.append(f"{felt}={verdi}")
    if middels >= 1 or hoy >= 1:
        return "middels", grunner
    grunner.append("no høy/middels triggers hit")
    return "lav", grunner


def hoved() -> int:
    if len(sys.argv) != 2:
        print("usage: triage_insikt.py <kandidate.yaml>", file=sys.stderr)
        return 2
    sti = Path(sys.argv[1])
    import yaml
    k = yaml.safe_load(sti.read_text(encoding="utf-8")) or {}
    if not isinstance(k, dict):
        print(json.dumps({"status": "needs-rework", "grunn": "the candidate is not a YAML object"},
                         ensure_ascii=False, indent=1))
        return 1
    # content_hash check: ALWAYS — a missing hash is needs-rework, not an
    # optional addition. Canonical form: scripts/maintenance/kanon_hash.py (v1),
    # the one shared specification for generator and verifier.
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    from kanon_hash import kanon_hash
    lagret = k.get("content_hash")
    if not isinstance(lagret, str):
        print(json.dumps({"status": "needs-rework",
                          "grunn": "content_hash is missing or invalid"},
                         ensure_ascii=False, indent=1))
        return 1
    kopi = dict(k)
    kopi.pop("content_hash", None)
    beregnet = kanon_hash(kopi)
    if beregnet != lagret:
        print(json.dumps({"status": "needs-rework",
                          "grunn": "content_hash does not match the content"},
                         ensure_ascii=False, indent=1))
        return 1
    try:
        import jsonschema
    except ImportError:
        print("jsonschema is missing — run `uv sync`", file=sys.stderr)
        return 2
    try:
        jsonschema.validate(k, json.loads(SKJEMA.read_text(encoding="utf-8")))
    except jsonschema.ValidationError as e:
        print(json.dumps({"status": "needs-rework", "grunn": e.message[:300]},
                         ensure_ascii=False, indent=1))
        return 1
    klasse, grunner = triage(k)
    print(json.dumps({"status": "gyldig", "triage": klasse,
                      "begrunnelse": grunner,
                      "vurdert_av": "triage_insikt.py",
                      "vurdert_naa": datetime.now(timezone.utc).isoformat()},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
