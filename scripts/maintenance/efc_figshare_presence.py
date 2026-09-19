#!/usr/bin/env python3
"""efc_figshare_presence — are the DOIs in the repo actually on Figshare?

A DOI written into the repo is a **claim**. This checks the claim against the
canon. It reads against the public Figshare API: no token, no writes, no
account access.

## Why it exists

The chain was "known as a description, but not live-verified". First run,
2026-08-24, against 176 unique Figshare DOIs in the repo:

    present on Figshare   168
    404 (does not exist)    8

And worse than a 404: `10.6084/m9.figshare.999999` — an obvious placeholder —
**resolves**. To a PLOS ONE figure from 2014 about hydrosalpinx in mice. A
fabricated Figshare ID is not a dead link; it is a live link to someone else's
work. That is why the check cannot be a regex pattern on the shape.

## What a 404 means — and does not mean

The public API sees only published articles. A draft that is not yet published
answers 404 here even though it exists on the account. The tool therefore says
"not public", not "does not exist". The distinction is settled with account
access (`figshare-hent <id>` through the queue guard on `.12`), and it is a
step of its own.

Absence of data is not a positive finding — not here either.

Usage:
    python3 scripts/maintenance/efc_figshare_presence.py            # report
    python3 scripts/maintenance/efc_figshare_presence.py --sjekk    # exit 1 on 404
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
# git grep uses POSIX ERE, which does not know \d. Same pattern, two
# dialects — and it must stay this way, or git grep finds nothing and the
# tool reports "no DOIs" as if that were a finding.
DOI_ERE = r"10\.6084/m9\.figshare\.[0-9]+"
FILTYPER = ("*.html", "*.json", "*.md", "*.tex", "*.cff", "*.bib", "*.jsonld")
AVVIK = Path(__file__).resolve().parent / "figshare-avvik.json"


def _kjente() -> dict[str, str]:
    """Known deviations that must not fail --sjekk. Every row REQUIRES a reason:
    an exception list without justifications becomes a place where errors hide."""
    if not AVVIK.exists():
        return {}
    d = json.loads(AVVIK.read_text(encoding="utf-8"))
    ut = {}
    for rad in d.get("avvik", []):
        if not rad.get("grunn"):
            raise SystemExit(f"[presence] {AVVIK.name}: «{rad.get('doi')}» "
                             f"has no reason. An exception without a reason "
                             f"is a hidden error.")
        ut[rad["doi"]] = rad["grunn"]
    return ut


def _rentekst(s: str | None) -> str:
    """DataCite delivers titles HTML-escaped, some with <i> tags."""
    if not s:
        return ""
    return re.sub(r"<[^>]+>", "", html.unescape(s)).strip()


def _doier() -> dict[str, list[str]]:
    """DOI -> the files it appears in. git grep, so .gitignore is respected."""
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


# Fixed pace between calls, shared by all threads.
#
# The first version REACTED to throttling with backoff. It worked, but very
# badly: 176 lookups took over 25 minutes without finishing, because every
# throttled request cost 15-45 s and then provoked the next one. Waiting
# after you have been throttled is more expensive than not being throttled.
#
# Now: a fixed minimum spacing between calls. 176 x 0.4 s = ~70 s, and
# Figshare does not throttle. The backoff remains as a safety net, not as a
# strategy.
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


# Circuit breaker: if Figshare gives us 403 time after time, that is not an
# answer about the DOIs — and to keep going for hours to collect more
# non-answers is wasted. Then we stop, and say that we stopped.
STRUPEGRENSE = int(os.environ.get("EFC_PRESENCE_STRUPEGRENSE", "12"))
_strupet = [0]


class Strupet(Exception):
    """Enough. The result is incomplete, and that must not be dressed up."""


# DataCite, not Figshare. Three reasons, all measured 2026-08-24:
#
# 1. Hermes is IP-BLOCKED by api.figshare.com — nginx answers 403 to
#    EVERYTHING, including the public endpoint without a token. The circuit
#    breaker here read that as throttling and aborted after 2 of 176 DOIs.
#    The check could never work from the host, and said "2 DOIs checked" as
#    if that were a result. DataCite answers 200 from the same machine.
#
# 2. DataCite looks up the DOI STRING. Figshare looks up the ARTICLE ID.
#    They are not the same: 10.6084/m9.figshare.31224739 does not exist as a
#    DOI, but article 31224739 does — it belongs to University of Wollongong.
#    Figshare thus gave me a foreign article and let me believe the ID was
#    valid. DataCite answers correctly "does not exist".
#
# 3. The answer carries AUTHORS. It is the author name that decides whether a
#    DOI is Morten's — the strongest of the three checks, and Figshare's
#    public endpoint does not give it.
#
# Lost: "published without files", which DataCite does not report. It found
# 0 either way, and file checking belongs where the account access is.
FORFATTER = os.environ.get("EFC_FORFATTER", "Magnusson")


def _hent(doi: str) -> tuple[str, dict]:
    req = urllib.request.Request(
        "https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""),
        headers={"Accept": "application/json",
                 "User-Agent": "efc-presence/2.0 (+https://github.com/supertedai/EFC)"})
    for forsok in range(4):
        if _strupet[0] >= STRUPEGRENSE:
            raise Strupet(f"{_strupet[0]} throttled responses")
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
                    # The strongest check: is the DOI his at all?
                    "fremmed_forfatter": bool(forf) and not any(
                        FORFATTER.lower() in f.lower() for f in forf),
                    "filer": None}
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return doi, {"status": "404", "tittel": "", "doi_hos_figshare": "",
                             "publisert": "", "filer": 0}
            # 403 is also rate limiting here, not just 429 — measured
            # 2026-08-24 by running the check several times in a row.
            # Without this, a throttled run reads as "the DOI does not exist".
            if e.code in (403, 429):
                _strupet[0] += 1
            if e.code in (403, 429, 500, 502, 503) and forsok < 3:
                time.sleep(5 * (forsok + 1))      # safety net, not the plan
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
                    help="exit 1 if a DOI is not public, or points somewhere else")
    ap.add_argument("--json", metavar="FIL")
    a = ap.parse_args()

    kilder = _doier()
    if not kilder:
        print("[presence] found no Figshare DOIs — check you are in the repo",
              file=sys.stderr)
        return 2

    res: dict[str, dict] = {}
    # 2 concurrent, with long backoff. Used to be 5, and then Figshare
    # answered 403 after a few runs in a row — 403 is throttling here, not an
    # answer about the DOI. A tool that reads its own throttling as "does not
    # exist" produces false findings about published research, so slow over
    # wrong.
    #
    # Consequence: the run takes minutes, not seconds. It therefore belongs
    # as a NIGHTLY job, not as a gate on every PR — a gate that fails from
    # throttling teaches people to re-run it until it goes through, and then
    # it is no longer a gate.
    avbrutt = False
    with cf.ThreadPoolExecutor(max_workers=2) as ex:
        try:
            for doi, r in ex.map(_hent, sorted(kilder)):
                r["filer_i_repoet"] = kilder[doi]
                res[doi] = r
        except Strupet as e:
            avbrutt = True
            print(f"\n[presence] ABORTED: {e}. Figshare is throttling. The "
                  f"{len(kilder) - len(res)} remaining DOIs are NOT "
                  f"checked, and the result below covers only the "
                  f"{len(res)} first.", file=sys.stderr)

    # Second round for the stragglers. A couple of throttled lookups must not
    # fail an otherwise complete run — but they must not be dressed up either,
    # so the round is ONE, it is sequential, and what still fails remains
    # standing as failed.
    henge = [d for d, r in res.items() if r["status"] not in ("OK", "404")]
    if henge and not avbrutt:
        print(f"[presence] {len(henge)} lookups failed — waiting 60 s and "
              f"retrying them once, sequentially.", file=sys.stderr)
        time.sleep(60)
        _strupet[0] = 0                      # new round, new budget
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
    # Does the DOI point SOMEWHERE ELSE than it claims? That is worse than a
    # 404. DataCite looks up the DOI string, so "doi_hos_figshare" always
    # agrees with what we asked for. What CAN be wrong is that the DOI belongs
    # to someone else — and we see that from the author.
    feilpekende = sorted(d for d, r in res.items()
                         if r["status"] == "OK" and r.get("fremmed_forfatter"))
    tomme: list[str] = []   # DataCite does not report files; see the comment above

    print(f"DOIs in the repo:         {len(res)}")
    print(f"  public on Figshare:     {len(res) - len(ikke_offentlig) - len(feil):>5}")
    print(f"  not public (404):       {len(ikke_offentlig):>5}")
    print(f"  points elsewhere:       {len(feilpekende):>5}")
    print(f"  lookup failed:          {len(feil):>5}")
    print(f"  published w/o files:    {len(tomme):>5}")

    if feilpekende:
        print("\n── FOREIGN AUTHOR (the DOI exists, but is not Morten's) ──")
        for d in feilpekende:
            r = res[d]
            print(f"   {d}\n      → {', '.join(r.get('forfattere') or ['?'])}"
                  f"  «{r['tittel'][:56]}»")
            for f in r["filer_i_repoet"][:3]:
                print(f"        {f}")
    if ikke_offentlig:
        print("\n── NOT PUBLIC (may be an unpublished draft — settled with account access) ──")
        for d in ikke_offentlig:
            for f in res[d]["filer_i_repoet"][:3]:
                print(f"   {d}  {f}")
    if feil:
        print("\n── LOOKUP FAILED (not a finding about the DOI, but about the network) ──")
        for d, s in sorted(feil.items()):
            print(f"   {d}  {s}")

    if a.json:
        Path(a.json).write_text(json.dumps(res, ensure_ascii=False, indent=1) + "\n",
                                encoding="utf-8")
        print(f"\nwrote {a.json}")

    kjente = _kjente()
    nye = [d for d in ikke_offentlig + feilpekende if d not in kjente]
    if kjente:
        print(f"\n({len(kjente)} known deviations in {AVVIK.name} — "
              f"reported above, they do not fail the check)")
    if a.sjekk and nye:
        print("\n── NEW deviations, not in the deviation list ──", file=sys.stderr)
        for d in nye:
            print(f"   {d}", file=sys.stderr)
        print("[presence] A DOI in the repo is a claim — these do not hold. "
              "Fix them, or enter them in the deviation list WITH a reason.",
              file=sys.stderr)
        return 1
    if a.sjekk and avbrutt:
        print("\n[presence] Incomplete run. Not interpreted as PASS.",
              file=sys.stderr)
        return 2
    if a.sjekk and feil:
        print("\n[presence] lookup failed; says NOTHING about the DOIs. "
              "Not interpreted as PASS.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
