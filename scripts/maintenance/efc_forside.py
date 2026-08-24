#!/usr/bin/env python3
"""efc_forside — genererer docs/index.html fra sidene som faktisk finnes.

## Hvorfor den finnes

`docs/index.html` var ni linjer: en `<meta refresh>` til Validation Ledger,
skrevet 2026-02-13 og urørt siden. Konsekvensene, målt 2026-08-24:

* **To av fjorten sider var unåbare** ved å navigere fra forsida —
  `EFC_Master_v1.1.html` (hovedspesifikasjonen) og `EFC_System_Health.html`.
  De var publisert bare i teknisk forstand.
* **Målet var hardkodet.** Døpes Validation Ledger om, blir hele nettstedet
  en 404.
* **Ingen eide den.**

## Hvorfor generert og ikke skrevet

En håndskrevet forside driver fra sidene den peker på. Denne leser
`docs/public/*.html`, henter `<title>` fra hver, og bygger lista. Legges en
side til, står den på forsida ved neste kjøring. Fjernes en, forsvinner
lenka — ingen 404.

Samme mønster som §4b-registeret: det som kan utledes, utledes, og CI
håndhever at fila stemmer med kilden.

## Hva den IKKE gjør

Den skriver ingen påstander om EFC. Titlene kommer fra sidene selv, og
rekkefølgen fra en fast liste her — ikke fra en vurdering av hva som er
viktigst. Å bestemme hva som skal møte en leser først er en redaksjonell
beslutning, og den er Mortens.

Bruk:
    efc_forside.py --bygg     # skriv docs/index.html
    efc_forside.py --sjekk    # exit 1 hvis fila ikke stemmer med sidene
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUB = ROOT / "docs/public"
UT = ROOT / "docs/index.html"

# Rekkefølge. Sider som ikke står her havner sist, alfabetisk — så en ny side
# ALLTID kommer med, også når ingen har oppdatert denne lista. En rekkefølge
# som taper sider er verre enn en rekkefølge som er litt feil.
ORDEN = [
    "EFC_Elevator_Pitch.html",
    "EFC_Master_v1.1.html",
    "EFC_Validation_Ledger.html",
    "EFC_Predictions.html",
    "EFC_Atlas.html",
    "EFC_Gap_Analysis.html",
    "EFC_Stage-IV_Data_Roadmap.html",
    "EFC_White_Paper_Series.html",
    "EFC_External_Research_Ledger.html",
    "EFC_Likelihood_Ledger.html",
    "EFC_Evaluation_Ledger.html",
    "EFC_Model_Comparison.html",
    "EFC_Changelog.html",
    "EFC_System_Health.html",
]


def _tittel(p: Path) -> str:
    t = p.read_text(encoding="utf-8", errors="replace")[:4000]
    m = re.search(r"<title>(.*?)</title>", t, re.S | re.I)
    if not m:
        return p.stem.replace("_", " ")
    s = html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip()
    # «Energy-Flow Cosmology (EFC) – Gap Analysis» → «Gap Analysis». Prefikset
    # er likt på alle fjorten og bærer null informasjon i en liste.
    return re.sub(r"^Energy-Flow Cosmology\s*(\(EFC\))?\s*[–—-]\s*", "", s) or s


def bygg_html() -> str:
    sider = sorted(p.name for p in PUB.glob("*.html"))
    rekke = [s for s in ORDEN if s in sider] + [s for s in sider if s not in ORDEN]
    rader = "\n".join(
        f'      <li><a href="public/{html.escape(s)}">'
        f'{html.escape(_tittel(PUB / s))}</a></li>'
        for s in rekke)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Energy-Flow Cosmology (EFC)</title>
<link rel="stylesheet" href="efc_master.css">
</head>
<body>
  <main>
    <h1>Energy-Flow Cosmology (EFC)</h1>
    <p>Morten Magnusson &middot;
      <a href="https://orcid.org/0009-0002-4860-5095">ORCID 0009-0002-4860-5095</a>
      &middot; Symbiose Research, Sandnes, Norway</p>
    <ul>
{rader}
    </ul>
    <p><small>Denne siden er generert av
      <code>scripts/maintenance/efc_forside.py</code> fra sidene i
      <code>docs/public/</code>. Rediger den ikke for hånd &mdash; en
      håndskrevet forside driver fra sidene den peker på.</small></p>
  </main>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bygg", action="store_true")
    ap.add_argument("--sjekk", action="store_true")
    a = ap.parse_args()
    if not PUB.is_dir():
        print(f"[forside] finner ikke {PUB}", file=sys.stderr)
        return 2
    ny = bygg_html()
    gml = UT.read_text(encoding="utf-8") if UT.exists() else ""
    if a.sjekk:
        if ny == gml:
            n = ny.count('<li><a href="public/')
            print(f"[forside] docs/index.html stemmer med de {n} sidene")
            return 0
        print("[forside] AVVIK: docs/index.html stemmer ikke med docs/public/. "
              "Kjør `efc_forside.py --bygg`.", file=sys.stderr)
        return 1
    if a.bygg:
        UT.write_text(ny, encoding="utf-8")
        print(f"[forside] skrev {UT.relative_to(ROOT)} — "
              f"{ny.count('<li><a href=')} sider")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
