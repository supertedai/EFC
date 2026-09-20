"""Run the rapid-response guard on the latest bus message.

The guard reads the message from a file (exported from the bus), writes
the artifact locally — and when an ACTUAL verdict is reached (PASS/FAIL),
the outcome is published on the bus as a settled prediction:
`kosmos.kosmologi.oppgjoer.efc-fs8-arbiter` (the VERDEN_PROGNOSE stream).
VENTER diagnoses are never published — a non-verdict is not a settlement.

Bus fetching and credentials are the caller's responsibility: the publication is
best-effort via NATS_PRODUSENT in the environment. The repo never carries
credentials.

Usage:
    python scripts/maintenance/arbiter_vakt_kjoer.py \
        --melding siste-melding.json --artefakt utfall.json
"""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from efc_inference.arbiter.rapid_response import RapidResponseVakt  # noqa: E402

OPPGJOER_EMNE = "kosmos.kosmologi.oppgjoer.efc-fs8-arbiter"
TIDSAVBRUDD = 8


def publiser_best_effort(emne: str, payload: str) -> str:
    """Publishes via NATS_PRODUSENT in the environment — best-effort, never
    a crash. Returns a status ("ok" or why not)."""
    url = os.environ.get("NATS_PRODUSENT", "")
    if not url:
        return "no producer credentials (NATS_PRODUSENT is missing)"
    try:
        user, rest = url.split("://", 1)[1].split(":", 1)
        password, hostport = rest.rsplit("@", 1)
        host, port = hostport.split(":", 1)
        port = int(port)
    except (ValueError, IndexError):
        return "malformed NATS_PRODUSENT"
    try:
        s = socket.create_connection((host, port), timeout=TIDSAVBRUDD)
        s.settimeout(TIDSAVBRUDD)
        s.recv(4096)
        c = json.dumps({"verbose": False, "headers": True,
                        "name": "arbiter-vakt",
                        "user": user, "pass": password})
        s.sendall(f"CONNECT {c}\r\nPING\r\n".encode())
        svar = s.recv(4096).decode(errors="replace")
        if "-ERR" in svar:
            return f"paalogging avvist: {svar.strip()[:80]}"
        data = payload.encode()
        s.sendall(f"PUB {emne} {len(data)}\r\n".encode() + data + b"\r\n")
        svar = s.recv(4096).decode(errors="replace")
        s.close()
        if "-ERR" in svar:
            return f"publikasjon avvist: {svar.strip()[:80]}"
        return "ok"
    except OSError as e:
        return f"nettverksfeil: {e}"


def kjoer(melding: dict,
          artefakt_sti: str,
          params: Optional[dict] = None,
          publiser: Optional[Callable[[str, str], str]] = None) -> dict:
    """The core logic — testable, transport injectable. The subject is ALWAYS
    OPPGJOER_EMNE — no override exists."""
    publiser = publiser or publiser_best_effort
    vakt = RapidResponseVakt(artefakt_sti=artefakt_sti)
    payload = vakt.sjekk(melding, params=params)
    dom = payload["rapport"]["dom"]

    publish_status = "not applicable — no verdict"
    if dom["status"] in ("PASS", "FAIL"):
        try:
            publish_status = publiser(
                OPPGJOER_EMNE, json.dumps(payload, ensure_ascii=False))
        except Exception as e:  # pragma: no cover
            publish_status = f"publish error: {e}"

    return {"payload": payload, "dom": dom,
            "publiseringsstatus": publish_status}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--melding", required=True,
                        help="JSON file with the latest bus message")
    parser.add_argument("--artefakt", default="arbiter-efc-fs8-dom.json",
                        help="where the verdict is written")
    parser.add_argument("--params", default=None,
                        help="optional JSON file with engine parameters "
                             "(e.g. mu_0) for the engine prediction")
    args = parser.parse_args()

    melding = json.loads(Path(args.melding).read_text(encoding="utf-8"))
    params = None
    if args.params:
        params = json.loads(Path(args.params).read_text(encoding="utf-8"))

    resultat = kjoer(melding, artefakt_sti=args.artefakt, params=params)
    dom = resultat["dom"]
    print(f"verdict: {dom['status']}")
    print(f"reason: {dom['årsak']}")
    print(f"artifact: {args.artefakt}")
    print(f"published: {resultat['publiseringsstatus']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
