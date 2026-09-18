#!/usr/bin/env python3
"""Migrer bankens EGEN ventetilstand til `open_questions`.

Bakgrunn, maalt 2026-09-18: atlasets spoersmaalsfane var tom etter at den
genererte linja («no evidence yet — hypothesis marked honestly», identisk for
alle sju) ble fjernet — med rette, den var ikke et spoersmaal. Men 26 noder i
banken DEKLARERER allerede at noe staar aapent, i feltet `buss_status`:

    «stroemmen finnes ikke — venter paa konnektor»            (2 noder)
    «ingen buss-vei — emnet finnes ikke som domene i
     snapshotet (maalt 2026-09-18)»                           (24 noder)

De deklarasjonene var usynlige i atlaset. Denne migreringen flytter dem til
`open_questions`, ORDRETT — spoersmaalet er nodens egen tekst, ikke en
omskriving. Ingen `to` settes: hvem som skal loese det staar ikke i banken, og
et paafunnent ansvar er verre enn et tomt felt.

Migreringen er idempotent: en node som allerede har `open_questions` roeres
ikke. Skriving krever `--skriv`; standard er toerrkjoering.

    python3 scripts/maintenance/migrer_buss_status_til_open_questions.py --vis
    python3 scripts/maintenance/migrer_buss_status_til_open_questions.py --skriv
"""
from __future__ import annotations

import argparse
import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parents[2]
BANK = ROT / "schema" / "regime_nodes.jsonld"

#: Formuleringene som betyr «denne noden staar aapen». Bare de maalte.
AAPNE_FORMULERINGER = (
    "stroemmen finnes ikke — venter paa konnektor",
    "ingen buss-vei — emnet finnes ikke som domene i snapshotet",
)


def _buss_status(node: dict) -> str:
    """Deklarasjonen ligger under `stipulasjoner` (maalt: 25 av 126 noder).

    Foerste utgave leste `node["buss_status"]` og fant null: feltet finnes, men
    et annet sted. En migrering som leter paa feil sted og melder «ingenting aa
    gjoere» ser ut som en ferdig jobb.
    """
    stip = node.get("stipulasjoner") or {}
    return str(node.get("buss_status") or stip.get("buss_status") or "").strip()


def aapne_noder(noder: list[dict]) -> list[tuple[str, str]]:
    """[(node-id, deklarasjonen)] for noder som deklarerer en aapen tilstand."""
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
                   help="skriv til banken (standard: toerrkjoering)")
    p.add_argument("--vis", action="store_true", help="vis hver node")
    a = p.parse_args()

    data = json.loads(BANK.read_text(encoding="utf-8"))
    kandidater = aapne_noder(data["nodes"])
    print(f"{len(kandidater)} noder deklarerer en aapen tilstand "
          f"og mangler open_questions")
    if a.vis:
        for nid, bs in kandidater:
            print(f"  {nid}: {bs[:80]}")
    if not a.skriv:
        print("toerrkjoering — ingenting skrevet (bruk --skriv)")
        return 0
    if not kandidater:
        print("ingenting aa gjoere")
        return 0

    per_id = dict(kandidater)
    for n in data["nodes"]:
        if n["id"] in per_id:
            # Ordrett. Spoersmaalet ER nodens egen deklarasjon.
            n["open_questions"] = [f"{n['id']}: {per_id[n['id']]}"]
    BANK.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")

    etter = json.loads(BANK.read_text(encoding="utf-8"))
    med = [n["id"] for n in etter["nodes"] if n.get("open_questions")]
    print(f"skrevet: {len(med)} noder har open_questions")
    if len(med) != len(kandidater):
        print(f"AVVIK: ventet {len(kandidater)}, fant {len(med)}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
