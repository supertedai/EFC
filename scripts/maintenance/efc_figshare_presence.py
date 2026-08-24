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
import html
import threading
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
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


def _rentekst(s: str | None) -> str:
    """DataCite leverer titler HTML-escaped, noen med <i>-tagger."""
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", html.unescape(s)).strip()


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


# Fast takt mellom kall, delt av alle traadene.
#
# Foerste versjon REAGERTE paa struping med backoff. Det virket, men saerdeles
# daarlig: 176 oppslag brukte over 25 minutter uten aa bli ferdig, fordi hver
# strupte forespoersel kostet 15-45 s og saa provoserte den neste. Aa vente
# etter at man er strupet er dyrere enn aa ikke bli strupet.
#
# Naa: en fast minsteavstand mellom kall. 176 x 0,4 s = ~70 s, og Figshare
# struper ikke. Backoffen staar igjen som sikkerhetsnett, ikke som strategi.
TAKT_S = float(os.environ.get("EFC_PRESENCE_TAKT", "0.4"))
_takt_laas = threading.Lock()
_neste_lov = [0.0]


def _vent_paa_tur() -> None:
    with _takt_laas:
        naa = time.monotonic()
        vent = _neste_lov[0] - naa
        if vent > 0:
            time.sleep(vent)
            naa = time.monotonic()
        _neste_lov[0] = naa + TAKT_S


# Stroembryter: gir Figshare oss 403 gang paa gang, er det ikke et svar om
# DOI-ene — og aa fortsette i timevis for aa samle flere ikke-svar er
# bortkastet. Da stopper vi, og sier at vi stoppet.
STRUPEGRENSE = int(os.environ.get("EFC_PRESENCE_STRUPEGRENSE", "12"))
_strupet = [0]


class Strupet(Exception):
    """Nok. Resultatet er ufullstendig, og det skal ikke pyntes paa."""


# DataCite, ikke Figshare. Tre grunner, alle maalt 2026-08-24:
#
# 1. Hermes er IP-BLOKKERT av api.figshare.com — nginx svarer 403 paa ALT,
#    ogsaa det offentlige endepunktet uten token. Stroembryteren her tolket
#    det som struping og avbroet etter 2 av 176 DOI-er. Sjekken kunne aldri
#    virke fra verten, og sa «2 DOI-er sjekket» som om det var et resultat.
#    DataCite svarer 200 fra samme maskin.
#
# 2. DataCite slaar opp DOI-STRENGEN. Figshare slaar opp ARTIKKEL-ID-en. Det
#    er ikke det samme: 10.6084/m9.figshare.31224739 finnes ikke som DOI, men
#    artikkel 31224739 finnes — den tilhoerer University of Wollongong. Figshare
#    ga meg altsaa en fremmed artikkel og lot meg tro ID-en var gyldig.
#    DataCite svarer korrekt «finnes ikke».
#
# 3. Svaret baerer FORFATTERE. Det er forfatternavnet som avgjoer om en DOI er
#    Mortens — den sterkeste kontrollen av de tre, og Figshares offentlige
#    endepunkt gir den ikke.
#
# Tapt: «publisert uten filer», som DataCite ikke oppgir. Den fant 0 uansett,
# og filkontroll hoerer hjemme der kontotilgangen er.
FORFATTER = os.environ.get("EFC_FORFATTER", "Magnusson")


def _hent(doi: str) -> tuple[str, dict]:
    req = urllib.request.Request(
        "https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""),
        headers={"Accept": "application/json",
                 "User-Agent": "efc-presence/2.0 (+https://github.com/supertedai/EFC)"})
    for forsok in range(4):
        if _strupet[0] >= STRUPEGRENSE:
            raise Strupet(f"{_strupet[0]} strupte svar")
        try:
            _vent_paa_tur()
            with urllib.request.urlopen(req, timeout=30) as r:
                at = json.loads(r.read().decode())["data"]["attributes"]
                forf = [c.get("name") or "" for c in (at.get("creators") or [])]
                return doi, {
                    "status": "OK",
                    "tittel": _rentekst((at.get("titles") or [{}])[0].get("title"))[:90],
                    "doi_hos_figshare": at.get("doi") or "",
                    "publisert": str(at.get("registered") or "")[:10],
                    "tilstand": at.get("state") or "",
                    "forfattere": forf,
                    # Den sterkeste kontrollen: er DOI-en i det hele tatt hans?
                    "fremmed_forfatter": bool(forf) and not any(
                        FORFATTER.lower() in f.lower() for f in forf),
                    "filer": None}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return doi, {"status": "404", "tittel": "", "doi_hos_figshare": "",
                             "publisert": "", "filer": 0}
            # 403 er ogsaa rate-limiting her, ikke bare 429 — maalt
            # 2026-08-24 ved aa kjoere sjekken flere ganger paa rad. Uten
            # dette leses en strupet kjoering som «DOI-en finnes ikke».
            if e.code in (403, 429):
                _strupet[0] += 1
            if e.code in (403, 429, 500, 502, 503) and forsok < 3:
                time.sleep(5 * (forsok + 1))      # sikkerhetsnett, ikke plan
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
    avbrutt = False
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        try:
            for doi, r in ex.map(_hent, sorted(kilder)):
                r["filer_i_repoet"] = kilder[doi]
                res[doi] = r
        except Strupet as e:
            avbrutt = True
            print(f"\n[presence] AVBRUTT: {e}. Figshare struper. De "
                  f"{len(kilder) - len(res)} gjenstaaende DOI-ene er IKKE "
                  f"sjekket, og resultatet under gjelder bare de "
                  f"{len(res)} foerste.", file=sys.stderr)

    # Andre runde for etternoelerne. Et par strupte oppslag skal ikke felle en
    # ellers fullstendig kjoering — men de skal heller ikke pyntes bort, saa
    # runden er EN, den er sekvensiell, og det som fortsatt feiler blir
    # staaende som feilet.
    henge = [d for d, r in res.items() if r["status"] not in ("OK", "404")]
    if henge and not avbrutt:
        print(f"[presence] {len(henge)} oppslag feilet — venter 60 s og "
              f"proever dem en gang til, sekvensielt.", file=sys.stderr)
        time.sleep(60)
        _strupet[0] = 0                      # ny runde, nytt budsjett
        for d in henge:
            try:
                _, r = _hent(d)
            except Strupet:
                break
            if r["status"] == "OK" or r["status"] == "404":
                r["filer_i_repoet"] = res[d]["filer_i_repoet"]
                res[d] = r

    ikke_offentlig = sorted(d for d, r in res.items() if r["status"] == "404")
    feil = {d: r["status"] for d, r in res.items() if r["status"] not in ("OK", "404")}
    # Peker DOI-en et ANNET sted enn den utgir seg for? Det er verre enn 404.
    # DataCite slaar opp DOI-strengen, saa «doi_hos_figshare» stemmer alltid
    # med det vi spurte om. Det som KAN vaere galt, er at DOI-en tilhoerer noen
    # andre — og det ser vi paa forfatteren.
    feilpekende = sorted(d for d, r in res.items()
                         if r["status"] == "OK" and r.get("fremmed_forfatter"))
    tomme: list[str] = []   # DataCite oppgir ikke filer; se kommentaren over

    print(f"DOI-er i repoet:          {len(res)}")
    print(f"  offentlige paa Figshare:{len(res) - len(ikke_offentlig) - len(feil):>5}")
    print(f"  ikke offentlige (404):  {len(ikke_offentlig):>5}")
    print(f"  peker et annet sted:    {len(feilpekende):>5}")
    print(f"  oppslag feilet:         {len(feil):>5}")
    print(f"  publisert uten filer:   {len(tomme):>5}")

    if feilpekende:
        print("\n── FREMMED FORFATTER (DOI-en finnes, men er ikke Mortens) ──")
        for d in feilpekende:
            r = res[d]
            print(f"   {d}\n      → {', '.join(r.get('forfattere') or ['?'])}"
                  f"  «{r['tittel'][:56]}»")
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
    if a.sjekk and avbrutt:
        print("\n[presence] Ufullstendig kjoering. Ikke tolket som PASS.",
              file=sys.stderr)
        return 2
    if a.sjekk and feil:
        print("\n[presence] oppslag feilet; sier INGENTING om DOI-ene. "
              "Ikke tolket som PASS.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
