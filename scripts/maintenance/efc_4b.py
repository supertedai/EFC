#!/usr/bin/env python3
"""efc_4b — §4b genereres fra en datafil i stedet for å redigeres som HTML.

Hvorfor, målt 2026-08-23: fem arbeidere fikk hvert sitt eksterne funn å
registrere. Alle fem la sin oppføring i samme `<ul>` i
`EFC_Validation_Ledger.html`. Alle fem PR-er ble `CONFLICTING`, måtte trekkes
og samles i én. Fremmingen måtte struped til ett kort om gangen.

Det er ikke et samtidighetsproblem å strupe seg ut av — det er at **to
tillegg i samme HTML-liste alltid kolliderer**. Legger arbeiderne i stedet til
en *rad* i en JSON-fil, kolliderer de bare hvis de rører samme rad.

Registeret er `docs/validation-ledger/data/external-references.json`. Det
brukes av to:

* `efc_build_4b.py --skriv` skriver §4b-blokken i HTML-en fra det.
* `efc_doi_coverage.py` leser `rolle` derfra, så en registrert ekstern
  sitering ikke lenger rapporteres som anomali.

**Tapsfritt med vilje.** Hver oppføring lagrer hele `<li>…</li>` ordrett i
`html`. Generatoren gjengir den uendret; den skriver ikke om prosa. Feltene
`tag`, `arxiv` og `rolle` er utledet *ved siden av* for verktøy, ikke i stedet
for teksten. En generator som formulerer om en publisert påstand er ikke en
generator — den er en forfatter.

Bruk:
    efc_4b.py hent      # les §4b fra HTML → skriv registeret (engangs)
    efc_4b.py bygg      # registeret → §4b i HTML
    efc_4b.py sjekk     # bygg i minnet, exit 1 hvis HTML-en avviker
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = ROOT / "docs/public/EFC_Validation_Ledger.html"
REG = ROOT / "docs/validation-ledger/data/external-references.json"

START = "<!-- 4b:generert:start -->"
SLUTT = "<!-- 4b:generert:slutt -->"

ROLLER = ("under_confrontation", "input_data", "context")


def _blokk(t: str) -> tuple[int, int]:
    """Grensene for §4b-listene. Bruker markørene når de finnes, ellers
    fra første <ul> etter overskriften til siste </ul> før neste <h2>."""
    if START in t and SLUTT in t:
        return t.index(START), t.index(SLUTT) + len(SLUTT)
    i = t.find("4b. External Observations Under Confrontation")
    if i < 0:
        raise SystemExit("[4b] fant ikke §4b-overskriften")
    ul = t.find("<ul>", i)
    j = t.find("<h2>5.", i)
    slutt = t.rfind("</ul>", ul, j if j > 0 else len(t)) + len("</ul>")
    return ul, slutt


def hent() -> int:
    t = HTML.read_text(encoding="utf-8")
    a, b = _blokk(t)
    blokk = t[a:b]
    grupper: list[dict] = []
    naa: dict | None = None
    for m in re.finditer(r"<h3[^>]*>(.*?)</h3>|<li>.*?</li>", blokk, re.S):
        s = m.group(0)
        if s.startswith("<h3"):
            naa = {"overskrift": m.group(1).strip(), "oppforinger": []}
            grupper.append(naa)
            continue
        if naa is None:
            naa = {"overskrift": None, "oppforinger": []}
            grupper.append(naa)
        tag = re.search(r"\[external\s*(?:&mdash;|—)\s*([^\]]{0,60})", s)
        arx = re.search(r"arXiv:([0-9.]+)", s)
        naa["oppforinger"].append({
            "tag": (tag.group(1).strip() if tag else ""),
            "arxiv": (arx.group(1) if arx else None),
            "rolle": "under_confrontation",
            "html": s,
        })
    d = {
        "_om": ("§4b i EFC_Validation_Ledger.html genereres fra denne fila. "
                "Rediger HER, ikke i HTML-en — to tillegg i samme HTML-liste "
                "kolliderer alltid, to rader i denne gjør det ikke."),
        "_roller": {
            "under_confrontation": "tredjepartsfunn EFC prøver seg mot",
            "input_data": "måling EFC bygger på",
            "context": "bakgrunn, ikke konfrontert",
        },
        "_advarsel": ("`html` lagres ordrett og gjengis uendret. En generator "
                      "som formulerer om en publisert påstand er ikke en "
                      "generator, den er en forfatter."),
        "grupper": grupper,
    }
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    n = sum(len(g["oppforinger"]) for g in grupper)
    print(f"[4b] hentet {n} oppføringer i {len(grupper)} gruppe(r) → "
          f"{REG.relative_to(ROOT)}")
    return 0


def _render(d: dict) -> str:
    """Gjengir §4b med SAMME formatering som originalen.

    Første utkast skrev `<li>` flushet til venstre uten blanke linjer mellom.
    Innholdet var ordrett bevart, men diffen mot originalen ble 37 linjer.
    En generator som endrer layout ved første kjøring kan ikke bevise at den
    er tapsfri — og på en offentlig side er unødig layout-churn den samme
    støyen som tidsstempel-commitene i §6 av ADR-024.

    Formatet som speiles: to mellomrom foran `<li>`, blank linje mellom
    oppføringene, blank linje foran `<h3>`, ingen blank linje før `</ul>`.

    Ett sted NORMALISERES det: originalen manglet blank linje mellom to av
    oppføringene — ujevn formatering fra tidligere håndredigering. Den jevnes
    ut. Å kode historisk slurv inn i registeret for alltid ville vært å velge
    troskap mot en tilfeldighet framfor mot innholdet. Innholdet er verifisert
    byte-identisk hver for seg; det er bare mellomrom som endres.
    """
    ut = [START]
    for i, g in enumerate(d["grupper"]):
        if g.get("overskrift"):
            if i:
                ut.append("")          # blank linje foran <h3>, som originalen
            ut.append(f'<h3 style="margin-bottom:4px;">{g["overskrift"]}</h3>')
        ut.append("<ul>")
        # Registeret har to slags rader. De med `html` ER §4b-oppfoeringer og
        # gjengis. De uten er REGISTRERTE siteringer — kjente eksterne verk med
        # DOI og rolle, som staar i loepende tekst andre steder. De leses av
        # `efc_doi_coverage.py`, men hoerer ikke i §4b-lista, og en generator
        # som skrev dem dit ville blaast opp konfrontasjonsseksjonen med
        # referanser ingen konfronterer.
        rader = [o["html"] for o in g["oppforinger"] if o.get("html")]
        ut.append("\n\n".join("  " + r for r in rader))
        ut.append("</ul>")
    ut.append(SLUTT)
    return "\n".join(ut)


def bygg(bare_sjekk: bool) -> int:
    if not REG.exists():
        print(f"[4b] registeret mangler: {REG}", file=sys.stderr)
        return 2
    d = json.loads(REG.read_text(encoding="utf-8"))
    t = HTML.read_text(encoding="utf-8")
    a, b = _blokk(t)
    ny = t[:a] + _render(d) + t[b:]
    if ny == t:
        print("[4b] uendret")
        return 0
    if bare_sjekk:
        print("[4b] AVVIK: HTML-en stemmer ikke med registeret. "
              "Kjør `efc_4b.py bygg`.", file=sys.stderr)
        return 1
    HTML.write_text(ny, encoding="utf-8")
    n = sum(len(g["oppforinger"]) for g in d["grupper"])
    print(f"[4b] skrev {n} oppføringer til {HTML.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("handling", choices=("hent", "bygg", "sjekk"))
    a = ap.parse_args()
    if a.handling == "hent":
        return hent()
    return bygg(a.handling == "sjekk")


if __name__ == "__main__":
    raise SystemExit(main())
