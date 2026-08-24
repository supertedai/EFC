#!/usr/bin/env python3
"""efc_figshare_presence — er DOI-ene i repoet faktisk publisert på Figshare?

En DOI skrevet i repoet er en **påstand**. Denne sjekker påstanden mot kanon.
Leser mot det offentlige Figshare-API-et: ingen token, ingen skriving, ingen
konto-tilgang.

## Hvorfor den finnes

Kjeden var «kjent som beskrivelse, men ikke live-verifisert». Første kjøring,
2026-08-24, mot 176 unike Figshare-DOI-er i repoet:

    finnes på Figshare   168
    404 (finnes ikke)      8

Og verre enn en 404: `10.6084/m9.figshare.999999` — en åpenbar plassholder —
**resolverer**. Til en PLOS ONE-figur fra 2014 om hydrosalpinx hos mus. En
oppdiktet Figshare-ID er ikke en død lenke; den er en levende lenke til noen
andres arbeid. Det er derfor sjekken ikke kan være et regex-mønster på formen.

## Hva et 404 betyr — og ikke betyr

Det offentlige API-et ser bare publiserte artikler. En draft som ennå ikke er
publisert svarer 404 her selv om den finnes på kontoen. Verktøyet sier derfor
«ikke offentlig», ikke «finnes ikke». Skillet avgjøres med kontotilgang
(`figshare-hent <id>` gjennom køvakten på `.12`), og det er et eget steg.

Fravær av data er ikke et positivt funn — heller ikke her.

Bruk:
    python3 scripts/maintenance/efc_figshare_presence.py            # rapport
    python3 scripts/maintenance/efc_figshare_presence.py --sjekk    # exit 1 ved 404
    python3 scripts/maintenance/efc_figshare_presence.py --json ut.json
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOI_RE = re.compile(r"10\.6084/m9\.figshare\.(\d+)")
# git grep bruker POSIX ERE, som ikke kjenner \d. Samme moenster, to dialekter
# — og det maa staa slik, ellers finner git grep ingenting og verktoeyet
# rapporterer «ingen DOI-er» som om det var et funn.
DOI_ERE = r"10\.6084/m9\.figshare\.[0-9]+"
FILTYPER = ("*.html", "*.json", "*.md", "*.tex", "*.cff", "*.bib", "*.jsonld")
AVVIK = Path(__file__).resolve().parent / "figshare-avvik.json"


def _kjente() -> dict[str, str]:
    """Kjente avvik som ikke skal felle --sjekk. Hver rad KREVER en grunn:
    en unntaksliste uten begrunnelser blir et sted feil gjemmer seg."""
    if not AVVIK.exists():
        return {}
    d = json.loads(AVVIK.read_text(encoding="utf-8"))
    ut = {}
    for rad in d.get("avvik", []):
        if not rad.get("grunn"):
            raise SystemExit(f"[presence] {AVVIK.name}: «{rad.get('doi')}» "
                             f"mangler grunn. Et unntak uten begrunnelse er "
                             f"en skjult feil.")
        ut[rad["doi"]] = rad["grunn"]
    return ut


def _doier() -> dict[str, list[str]]:
    """DOI → filene den står i. git grep, så .gitignore respekteres."""
    r = subprocess.run(["git", "grep", "-InoE", DOI_ERE, "--", *FILTYPER],
                       cwd=ROOT, capture_output=True, text=True)
    ut: dict[str, list[str]] = {}
    for linje in r.stdout.splitlines():
        m = DOI_RE.search(linje)
        if not m:
            continue
        fil = linje.split(":", 1)[0]
        ut.setdefault(m.group(0), [])
        if fil not in ut[m.group(0)]:
            ut[m.group(0)].append(fil)
    return ut


def _hent(doi: str) -> tuple[str, dict]:
    aid = doi.rsplit(".", 1)[-1]
    req = urllib.request.Request(
        f"https://api.figshare.com/v2/articles/{aid}",
        headers={"Accept": "application/json",
                 "User-Agent": "efc-presence/1.0 (+https://github.com/supertedai/EFC)"})
    for forsok in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.loads(r.read().decode())
                return doi, {"status": "OK",
                             "tittel": (d.get("title") or "")[:90],
                             "doi_hos_figshare": d.get("doi") or "",
                             "publisert": (d.get("published_date") or "")[:10],
                             "filer": len(d.get("files") or [])}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return doi, {"status": "404", "tittel": "", "doi_hos_figshare": "",
                             "publisert": "", "filer": 0}
            # 403 er ogsaa rate-limiting her, ikke bare 429 — maalt
            # 2026-08-24 ved aa kjoere sjekken flere ganger paa rad. Uten
            # dette leses en strupet kjoering som «DOI-en finnes ikke».
            if e.code in (403, 429, 500, 502, 503) and forsok < 3:
                time.sleep(15 * (forsok + 1))     # 15 s, 30 s, 45 s
                continue
            return doi, {"status": f"HTTP {e.code}", "tittel": "",
                         "doi_hos_figshare": "", "publisert": "", "filer": 0}
        except Exception as e:                                    # noqa: BLE001
            if forsok < 2:
                time.sleep(2)
                continue
            return doi, {"status": type(e).__name__, "tittel": "",
                         "doi_hos_figshare": "", "publisert": "", "filer": 0}
    return doi, {"status": "ukjent", "tittel": "", "doi_hos_figshare": "",
                 "publisert": "", "filer": 0}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sjekk", action="store_true",
                    help="exit 1 hvis en DOI ikke er offentlig, eller peker et annet sted")
    ap.add_argument("--json", metavar="FIL")
    a = ap.parse_args()

    kilder = _doier()
    if not kilder:
        print("[presence] fant ingen Figshare-DOI-er — sjekk at du star i repoet",
              file=sys.stderr)
        return 2

    res: dict[str, dict] = {}
    # 2 samtidige, med lang backoff. Var 5, og da svarte Figshare 403 etter
    # noen kjoeringer paa rad — 403 er struping her, ikke et svar om DOI-en.
    # Et verktoey som tolker sin egen strupning som «finnes ikke» produserer
    # falske funn om publisert forskning, saa heller tregt enn galt.
    #
    # Konsekvens: kjoeringen tar minutter, ikke sekunder. Den hoerer derfor
    # hjemme som NATTLIG jobb, ikke som port paa hver PR — en port som
    # feiler av struping laerer folk aa kjoere den paa nytt til den gaar
    # gjennom, og da er den ikke lenger en port.
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        for doi, r in ex.map(_hent, sorted(kilder)):
            r["filer_i_repoet"] = kilder[doi]
            res[doi] = r

    ikke_offentlig = sorted(d for d, r in res.items() if r["status"] == "404")
    feil = {d: r["status"] for d, r in res.items() if r["status"] not in ("OK", "404")}
    # Peker DOI-en et ANNET sted enn den utgir seg for? Det er verre enn 404.
    feilpekende = sorted(
        d for d, r in res.items()
        if r["status"] == "OK" and r["doi_hos_figshare"]
        and not r["doi_hos_figshare"].startswith(d))
    tomme = sorted(d for d, r in res.items() if r["status"] == "OK" and not r["filer"])

    print(f"DOI-er i repoet:          {len(res)}")
    print(f"  offentlige paa Figshare:{len(res) - len(ikke_offentlig) - len(feil):>5}")
    print(f"  ikke offentlige (404):  {len(ikke_offentlig):>5}")
    print(f"  peker et annet sted:    {len(feilpekende):>5}")
    print(f"  oppslag feilet:         {len(feil):>5}")
    print(f"  publisert uten filer:   {len(tomme):>5}")

    if feilpekende:
        print("\n── PEKER ET ANNET STED (verre enn 404: levende lenke, feil verk) ──")
        for d in feilpekende:
            r = res[d]
            print(f"   {d}\n      → {r['doi_hos_figshare']}  «{r['tittel'][:60]}»")
            for f in r["filer_i_repoet"][:3]:
                print(f"        {f}")
    if ikke_offentlig:
        print("\n── IKKE OFFENTLIG (kan vaere upublisert draft — avgjoeres med kontotilgang) ──")
        for d in ikke_offentlig:
            for f in res[d]["filer_i_repoet"][:3]:
                print(f"   {d}  {f}")
    if feil:
        print("\n── OPPSLAG FEILET (ikke et funn om DOI-en, men om nettet) ──")
        for d, s in sorted(feil.items()):
            print(f"   {d}  {s}")

    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
        print(f"\nskrev {a.json}")

    kjente = _kjente()
    nye = [d for d in ikke_offentlig + feilpekende if d not in kjente]
    if kjente:
        print(f"\n({len(kjente)} kjente avvik i {AVVIK.name} — rapportert over, "
              f"feller ikke sjekken)")
    if a.sjekk and nye:
        print("\n── NYE avvik, ikke i avvikslista ──", file=sys.stderr)
        for d in nye:
            print(f"   {d}", file=sys.stderr)
        print("[presence] En DOI i repoet er en paastand — disse holder ikke. "
              "Rett dem, eller foer dem inn i avvikslista MED grunn.",
              file=sys.stderr)
        return 1
    if a.sjekk and feil:
        print("\n[presence] oppslag feilet; sier INGENTING om DOI-ene. "
              "Ikke tolket som PASS.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
