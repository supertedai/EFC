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


def hent(rydd: bool) -> int:
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

    # Deler som IKKE står i den samlede fila. To helt ulike ting ser like ut
    # her, og det er derfor den ikke sletter av seg selv:
    #
    #   a) etterlatenskaper — posten er fjernet fra den samlede fila, og
    #      uten opprydding smetter den inn igjen ved neste `bygg`
    #   b) FERSK ARBEID — en arbeider la nettopp til en kilde som ennå ikke
    #      er bygget inn. Hele poenget med én fil per kilde er at det skal
    #      gå an.
    #
    # Å slette blindt ville tatt (b) med (a). Å la være ville latt (a) leve.
    # Derfor: navngi dem og feil lukket. `bygg` folder (b) inn i den samlede
    # fila; deretter er det som står igjen per definisjon (a), og `--rydd`
    # fjerner det.
    ukjent = sorted(f.name for f in DELER.glob("*.json")
                    if f.name != "_hode.json" and f.name not in sett)
    if ukjent:
        if rydd:
            for n in ukjent:
                (DELER / n).unlink()
            print(f"[watch] ryddet {len(ukjent)} del(er) uten post i den "
                  f"samlede fila: {', '.join(ukjent)}")
            return 0
        print(f"[watch] {len(ukjent)} del(er) staar ikke i den samlede fila:",
              file=sys.stderr)
        for n in ukjent:
            print(f"          {n}", file=sys.stderr)
        print("[watch] enten er de fersk arbeid — kjoer `bygg` foerst — "
              "eller etterlatenskaper: `hent --rydd`.", file=sys.stderr)
        return 1
    return 0


def _samle() -> dict:
    hode = json.loads((DELER / "_hode.json").read_text(encoding="utf-8"))
    par = []
    for f in sorted(DELER.glob("*.json")):
        if f.name == "_hode.json":
            continue
        par.append((f.name, json.loads(f.read_text(encoding="utf-8"))))
    # Stabil rekkefølge: nyest sett først, så `key` — og filnavnet når `key`
    # mangler. Alle 109 postene har unik `key` i dag, så fallbacken endrer
    # ingen rekkefølge nå; den finnes for at en framtidig post uten `key`
    # ikke skal la filsystemets svar avgjøre ordenen. Da ville generatoren
    # laget en ny diff uten at noe var endret — samme støy som
    # tidsstempel-commitene i ADR-024 §6.
    #
    # Å sortere på filnavn i stedet ville vært like stabilt, men ville
    # stokket om alle 109 radene nå (filnavnet stripper «arXiv:»-prefikset
    # som `key` beholder). Denne PR-en lover at delene bygger den samlede
    # fila BYTE FOR BYTE tilbake; en omstokking ville brutt nettopp det
    # løftet for å vinne robusthet ingen post trenger ennå.
    par.sort(key=lambda fp: (str(fp[1].get("date_seen") or ""),
                             str(fp[1].get("key") or "") or fp[0]),
             reverse=True)
    return {**hode, "items": [p for _, p in par]}


def bygg(bare_sjekk: bool) -> int:
    if not (DELER / "_hode.json").exists():
        print(f"[watch] delene mangler: {DELER}", file=sys.stderr)
        return 2
    samlet = _samle()                       # én gang: den leser hver del
    ny = json.dumps(samlet, ensure_ascii=False, indent=2) + "\n"
    gml = SAMLET.read_text(encoding="utf-8") if SAMLET.exists() else ""
    # `status` staar i skjemaet, men to poster paa main mangler det. Det er
    # arvet data, ikke noe denne generatoren innfoerte — derfor VARSEL og
    # ikke feil. En generator som begynner aa avvise data den selv fikk
    # utlevert, stopper vedlikeholdet i stedet for aa baere det.
    mangler = [str(x.get("key") or "?") for x in samlet["items"]
               if "status" not in x]
    if mangler:
        print(f"[watch] VARSEL: {len(mangler)} post(er) uten 'status': "
              f"{', '.join(mangler)}", file=sys.stderr)
    if ny == gml:
        print("[watch] uendret")
        return 0
    if bare_sjekk:
        print("[watch] AVVIK: den samlede fila stemmer ikke med delene. "
              "Kjør `efc_watch.py bygg`.", file=sys.stderr)
        return 1
    SAMLET.write_text(ny, encoding="utf-8")
    print(f"[watch] skrev {len(samlet['items'])} kilder til "
          f"{SAMLET.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("handling", choices=("hent", "bygg", "sjekk"))
    ap.add_argument("--rydd", action="store_true",
                    help="slett deler som ikke staar i den samlede fila "
                         "(kjoer `bygg` foerst, ellers ryker fersk arbeid)")
    a = ap.parse_args()
    if a.handling == "hent":
        return hent(a.rydd)
    return bygg(a.handling == "sjekk")


if __name__ == "__main__":
    raise SystemExit(main())
