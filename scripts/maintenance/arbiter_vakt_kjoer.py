"""Kjør rapid-response-vakten på den siste buss-meldingen.

Read-only: vakten leser meldingen fra en fil (eksportert fra bussen)
og skriver artefakten lokalt. Buss-hentingen gjøres av kalleren —
f.eks. verden-MCP (read-only konsument) — slik at repoet aldri
avhenger av buss-legitimasjon.

Bruk:
    python scripts/maintenance/arbiter_vakt_kjoer.py \
        --melding siste-melding.json --artefakt utfall.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from efc_inference.arbiter.rapid_response import RapidResponseVakt  # noqa: E402


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

    vakt = RapidResponseVakt(artefakt_sti=args.artefakt)
    payload = vakt.sjekk(melding, params=params)

    dom = payload["rapport"]["dom"]
    print(f"dom: {dom['status']}")
    print(f"årsak: {dom['årsak']}")
    print(f"artefakt: {args.artefakt}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
