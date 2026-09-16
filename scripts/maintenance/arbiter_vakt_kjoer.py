"""Kjør rapid-response-vakten på den siste buss-meldingen.

Vakten leser meldingen fra en fil (eksportert fra bussen), skriver
artefakten lokalt — og når en FAKTISK dom felles (PASS/FAIL),
publiseres utfallet på bussen som oppgjort prediksjon:
`kosmos.kosmologi.oppgjoer.efc-fs8-arbiter` (VERDEN_PROGNOSE-strømmen).
VENTER-diagnoser publiseres aldri — en ikke-dom er ikke et oppgjør.

Buss-henting og legitimasjon er kallens ansvar: publiseringen er
best-effort via NATS_PRODUSENT i miljøet. Repoet bærer aldri
legitimasjon.

Bruk:
    python scripts/maintenance/arbiter_vakt_kjoer.py \
        --melding siste-melding.json --artefakt utfall.json \
        [--publiser-emne kosmos.kosmologi.oppgjoer.efc-fs8-arbiter]
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
    """Publiserer via NATS_PRODUSENT i miljøet — best-effort, aldri
    krasj. Returnerer status («ok» eller hvorfor ikke)."""
    url = os.environ.get("NATS_PRODUSENT", "")
    if not url:
        return "ingen produsent-legitimasjon (NATS_PRODUSENT mangler)"
    try:
        bruker, rest = url.split("://", 1)[1].split(":", 1)
        passord, vertport = rest.rsplit("@", 1)
        vert, port = vertport.split(":", 1)
        port = int(port)
    except (ValueError, IndexError):
        return "ugyldig NATS_PRODUSENT-form"
    try:
        s = socket.create_connection((vert, port), timeout=TIDSAVBRUDD)
        s.settimeout(TIDSAVBRUDD)
        s.recv(4096)
        c = json.dumps({"verbose": False, "headers": True,
                        "name": "arbiter-vakt",
                        "user": bruker, "pass": passord})
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
          publiser_emne: str = OPPGJOER_EMNE,
          publiser: Optional[Callable[[str, str], str]] = None) -> dict:
    """Kjernelogikken — testbar, transport injiserbar."""
    publiser = publiser or publiser_best_effort
    vakt = RapidResponseVakt(artefakt_sti=artefakt_sti)
    payload = vakt.sjekk(melding, params=params)
    dom = payload["rapport"]["dom"]

    publiseringsstatus = "ikke aktuelt — ingen dom"
    if dom["status"] in ("PASS", "FAIL"):
        try:
            publiseringsstatus = publiser(
                publiser_emne, json.dumps(payload, ensure_ascii=False))
        except Exception as e:  # pragma: no cover
            publiseringsstatus = f"publiseringsfeil: {e}"

    return {"payload": payload, "dom": dom,
            "publiseringsstatus": publiseringsstatus}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--melding", required=True,
                        help="JSON-fil med siste buss-melding")
    parser.add_argument("--artefakt", default="arbiter-efc-fs8-dom.json",
                        help="hvor dommen skrives")
    parser.add_argument("--params", default=None,
                        help="valgfri JSON-fil med motorparametre "
                             "(f.eks. mu_0) for motorprediksjonen")
    args = parser.parse_args()

    melding = json.loads(Path(args.melding).read_text(encoding="utf-8"))
    params = None
    if args.params:
        params = json.loads(Path(args.params).read_text(encoding="utf-8"))

    resultat = kjoer(melding, artefakt_sti=args.artefakt, params=params)
    dom = resultat["dom"]
    print(f"dom: {dom['status']}")
    print(f"årsak: {dom['årsak']}")
    print(f"artefakt: {args.artefakt}")
    print(f"publisert: {resultat['publiseringsstatus']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
