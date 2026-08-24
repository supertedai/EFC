#!/usr/bin/env python3
"""efc_doi_coverage — DOI-dekning for docs/public, målt i repoet selv.

Erstatter `public_pages_doi_drift.py`, som kjørte utenfor repoet (Symbiose,
`.12`) og committet til `main` hver sjette time. Målt 2026-08-23: 64 av de
siste 80 commitene på `main` var den jobben, og hver endret **kun
tidsstempelet** — tallene sto stille. Se ADR-024 §6 og §8.3 punkt 3.

Tre krav fra den gjennomgangen, alle innfridd her:

1. **Ingen tid i utdataene.** Rapporten inneholder ingen `generated_at`.
   Identisk innhold gir identisk fil gir ingen commit. Tidspunktet bærer git.
2. **En sitering er ikke et tall i en setning.** DOI-er inne i rader merket
   som planlagt arbeid (`data-result="Planned"`) telles ikke. Målt: dette
   gjelder 5 DOI-er, alle på Atlas — bl.a. `…figshare.31140000`, som stod
   oppført som anomali i sju uker fordi den nevnes i en *oppgave* om å
   re-ingeste ufullstendige DOI-er.
3. **Ingen plassering uten treff.** Hver side som føres opp for en DOI er
   funnet i den fila. Den gamle rapporten førte `10.17863/cam.690` som
   forekommende på Atlas; `git grep` fant den kun i rapporten selv.

Kanon hentes **direkte fra ORCID**, ikke fra en mellomliggende fil.

Bruk:
    python3 scripts/maintenance/efc_doi_coverage.py            # skriv rapport
    python3 scripts/maintenance/efc_doi_coverage.py --sjekk    # kun exit-kode
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "docs" / "public"
RAPPORT = PUBLIC / "DOI_Coverage_Report.md"
REGISTER = ROOT / "docs" / "validation-ledger" / "data" / "external-references.json"
ORCID = "0009-0002-4860-5095"

DOI_RE = re.compile(r"10\.\d{4,9}/[^\s\"<>&),;]+")
PLANNED_RE = re.compile(r'<tr[^>]*data-result="Planned"[^>]*>.*?</tr>', re.S)


def orcid_kanon() -> set[str]:
    req = urllib.request.Request(
        f"https://pub.orcid.org/v3.0/{ORCID}/works",
        headers={"Accept": "application/json", "User-Agent": "efc-doi-coverage"})
    with urllib.request.urlopen(req, timeout=60) as r:
        d = json.loads(r.read().decode())
    ut = set()
    for g in d.get("group", []):
        for eid in (g.get("external-ids") or {}).get("external-id", []):
            if (eid.get("external-id-type") or "").lower() == "doi":
                v = (eid.get("external-id-value") or "").strip().lower()
                if v.startswith("10.") and "/" in v:
                    ut.add(v)
    return ut


def registrerte() -> dict[str, str]:
    """Verifiserte eksterne siteringer, med rolle. Fila kan mangle — da er
    den tom, og det er et ærlig svar, ikke en feil."""
    if not REGISTER.exists():
        return {}
    d = json.loads(REGISTER.read_text(encoding="utf-8"))
    # Samme register som §4b genereres fra (efc_4b.py). Én sannhet for
    # eksterne referanser, ikke to: §4b-generatoren bruker `html`, denne
    # bruker `doi` og `rolle`. En oppforing uten `doi` er et arXiv-funn som
    # ikke har en DOI aa avstemme — den hoerer i §4b, ikke her.
    if isinstance(d, dict) and "grupper" in d:
        poster = [o for g in d["grupper"] for o in g.get("oppforinger", [])]
    else:
        poster = d.get("references", d) if isinstance(d, dict) else d
    ut = {}
    for p in poster:
        if not isinstance(p, dict):
            continue
        doi = str(p.get("doi") or "").strip().lower()
        if doi.startswith("10.") and "/" in doi:
            ut[doi] = p.get("rolle") or p.get("role") or "uklassifisert"
    return ut


def skann() -> dict[str, set[str]]:
    """DOI → sider den faktisk står på. Planlagt-rader hoppes over."""
    funn: dict[str, set[str]] = {}
    for sti in sorted(PUBLIC.glob("*.html")):
        h = sti.read_text(encoding="utf-8", errors="replace")
        utelatt = set()
        for rad in PLANNED_RE.findall(h):
            utelatt.update(m.lower() for m in DOI_RE.findall(rad))
        for m in DOI_RE.finditer(h):
            d = m.group(0).rstrip(".").lower()
            if d in utelatt:
                continue
            funn.setdefault(d, set()).add(sti.name)
    return funn


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sjekk", action="store_true",
                    help="ikke skriv fil; exit 1 hvis anomalier finnes")
    a = ap.parse_args()

    kanon = orcid_kanon()
    reg = registrerte()
    funn = skann()

    dekket = sorted(d for d in funn if d in kanon)
    mangler = sorted(kanon - set(funn))
    registrert = sorted(d for d in funn if d not in kanon and d in reg)
    ukjente = sorted(d for d in funn if d not in kanon and d not in reg)

    linjer = [
        "# DOI Coverage Report — docs/public × ORCID canon",
        "",
        "_Generated deterministically by `scripts/maintenance/efc_doi_coverage.py` "
        "in this repository's own CI. Canon is read directly from ORCID. "
        "No timestamp in this file — identical content produces no commit._",
        "",
        f"**Canon:** {len(kanon)} works · **Covered:** {len(dekket)} · "
        f"**Missing from all pages:** {len(mangler)} · "
        f"**Registered external:** {len(registrert)} · "
        f"**Unrecognized:** {len(ukjente)} · **Pages scanned:** "
        f"{len(list(PUBLIC.glob('*.html')))}",
        "",
        "## Canonical works not referenced on any public page",
        "",
    ]
    linjer += ([f"- `{d}`" for d in mangler] or ["_None — full coverage._"])
    linjer += ["", "## Registered external citations (verified intentional)", ""]
    if registrert:
        linjer += ["| DOI | role | pages |", "|---|---|---|"]
        linjer += [f"| `{d}` | {reg[d]} | {', '.join(sorted(funn[d]))} |"
                   for d in registrert]
    else:
        linjer += [f"_None registered. The register is `{REGISTER.relative_to(ROOT)}`"
                   + ("" if REGISTER.exists() else " — file does not exist yet") + "._"]
    linjer += ["", "## Unrecognized DOIs — neither in canon nor registered", ""]
    if ukjente:
        linjer += ["| DOI | pages |", "|---|---|"]
        linjer += [f"| `{d}` | {', '.join(sorted(funn[d]))} |" for d in ukjente]
    else:
        linjer += ["_None._"]
    linjer += ["", "## DOI counts per page", "", "| Page | DOIs |", "|---|---|"]
    per: dict[str, int] = {}
    for d, sider in funn.items():
        for s in sider:
            per[s] = per.get(s, 0) + 1
    linjer += [f"| {s} | {n} |" for s, n in sorted(per.items())]
    tekst = "\n".join(linjer) + "\n"

    if a.sjekk:
        print(f"[doi-coverage] kanon={len(kanon)} dekket={len(dekket)} "
              f"mangler={len(mangler)} registrert={len(registrert)} "
              f"ukjente={len(ukjente)}")
        for d in ukjente:
            print(f"  ukjent: {d}  ({', '.join(sorted(funn[d]))})")
        return 1 if (ukjente or mangler) else 0

    endret = (not RAPPORT.exists()) or RAPPORT.read_text(encoding="utf-8") != tekst
    RAPPORT.write_text(tekst, encoding="utf-8")
    print(f"[doi-coverage] {'oppdatert' if endret else 'uendret'} — "
          f"kanon={len(kanon)} ukjente={len(ukjente)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
