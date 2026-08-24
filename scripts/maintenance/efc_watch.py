#!/usr/bin/env python3
"""efc_watch — én fil per overvåket kilde, i stedet for én lang liste.

Samme oppskrift som `efc_4b.py`, og av samme grunn — men ett hakk lenger.

Målt 2026-08-23: tre arbeidere kjørte parallelt for første gang etter at §4b
ble datadrevet. §4b holdt. Men **alle tre** rørte `external_research_watch.json`
og kolliderte der i stedet. Å gjøre §4b til data flyttet grensen ett hakk; den
forsvant ikke.

For §4b holdt det å samle radene i én JSON-fil, fordi arbeiderne der la til
tekstblokker som ellers havnet i samme `<ul>`. Her er kilden allerede JSON —
og den kolliderer likevel, fordi to tillegg i **samme array** treffer samme
linjer. En felles fil hjelper ikke når konflikten er tekstlig.

Derfor: **én fil per kilde** under `docs/public/external_research_watch/`.
To arbeidere som legger til hver sin kilde rører aldri samme fil, og git har
ingenting å slå sammen. `external_research_watch.json` blir generert, og
beholdes fordi monitorens prompt leser den.

    efc_watch.py hent    engangs: split den lange lista i én fil per kilde
    efc_watch.py bygg    delene → external_research_watch.json
    efc_watch.py sjekk   exit 1 hvis den genererte fila har drevet fra delene
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMLET = ROOT / "docs/public/external_research_watch.json"
DELER = ROOT / "docs/public/external_research_watch"


def _navn(post: dict, i: int) -> str:
    """Filnavn fra nøkkelen. `arXiv:2607.18234` → `2607.18234.json`.

    Nøkkelen er identiteten: to arbeidere som finner samme kilde skriver til
    samme fil og kolliderer — som de skal. Det er bare *ulike* kilder som skal
    kunne gå parallelt.
    """
    k = str(post.get("key") or "").strip()
    s = re.sub(r"^arxiv:", "", k, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")
    return f"{s or f'post-{i:03d}'}.json"


def hent() -> int:
    d = json.loads(SAMLET.read_text(encoding="utf-8"))
    poster = d.get("items") or []
    DELER.mkdir(parents=True, exist_ok=True)
    (DELER / "_hode.json").write_text(
        json.dumps({k: v for k, v in d.items() if k != "items"},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sett: set[str] = set()
    for i, p in enumerate(poster):
        n = _navn(p, i)
        if n in sett:                        # samme nøkkel to ganger
            n = f"{n[:-5]}-{i:03d}.json"
        sett.add(n)
        (DELER / n).write_text(
            json.dumps(p, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    print(f"[watch] delte {len(poster)} kilder → {DELER.relative_to(ROOT)}/")
    return 0


def _samle() -> dict:
    hode = json.loads((DELER / "_hode.json").read_text(encoding="utf-8"))
    poster = []
    for f in sorted(DELER.glob("*.json")):
        if f.name == "_hode.json":
            continue
        poster.append(json.loads(f.read_text(encoding="utf-8")))
    # Stabil rekkefølge: nyest sett først, så filnavn. Uten en fast orden
    # ville generatoren laget en ny diff hver gang filsystemet svarte i en
    # annen rekkefølge — samme støy som tidsstempel-commitene i ADR-024 §6.
    poster.sort(key=lambda p: (str(p.get("date_seen") or ""),
                               str(p.get("key") or "")), reverse=True)
    return {**hode, "items": poster}


def bygg(bare_sjekk: bool) -> int:
    if not (DELER / "_hode.json").exists():
        print(f"[watch] delene mangler: {DELER}", file=sys.stderr)
        return 2
    ny = json.dumps(_samle(), ensure_ascii=False, indent=2) + "\n"
    gml = SAMLET.read_text(encoding="utf-8") if SAMLET.exists() else ""
    if ny == gml:
        print("[watch] uendret")
        return 0
    if bare_sjekk:
        print("[watch] AVVIK: den samlede fila stemmer ikke med delene. "
              "Kjør `efc_watch.py bygg`.", file=sys.stderr)
        return 1
    SAMLET.write_text(ny, encoding="utf-8")
    print(f"[watch] skrev {len(_samle()['items'])} kilder til "
          f"{SAMLET.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("handling", choices=("hent", "bygg", "sjekk"))
    a = ap.parse_args()
    return hent() if a.handling == "hent" else bygg(a.handling == "sjekk")


if __name__ == "__main__":
    raise SystemExit(main())
