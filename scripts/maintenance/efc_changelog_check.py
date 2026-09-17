#!/usr/bin/env python3
"""efc_changelog_check.py — CI-vakten for changelog-projeksjonen.

Sjekker at registerpost → changelog.json → EFC_Changelog.html peker på SAMME
change_id, og at projeksjonen er den loggen faktisk gir. Alle harde feil
betyr at kjeden er brutt: en endring uten change_id på en flate, en manuelt
redigert generert region, en utdatert projeksjon, eller en logg som er
omskrevet istedenfor appendert.

Regenerering (den eneste lovlige fiksen):

  python3 scripts/maintenance/efc_auto_changelog.py

Bruk:
  python3 scripts/maintenance/efc_changelog_check.py [--json] [--base <ref>]

Exit: 0 = kjeden er intakt, 1 = harde feil.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from efc_change_id import (  # noqa: E402
    GENERATOR,
    GENERATORVERSJON,
    KILDELOGG,
    avvik,
)

ROT = Path(__file__).resolve().parents[2]
LOGG = ROT / KILDELOGG
CHANGELOG_JSON = ROT / "docs" / "validation-ledger" / "data" / "changelog.json"
CHANGELOG_HTML = ROT / "docs" / "public" / "EFC_Changelog.html"


def append_only_feil(base: str) -> list[dict]:
    """Append-only er en git-egenskap: diffen på loggen skal bare ha innsettinger.

    Dette steget er dokumentert i validate_activity_log.py som «sjekkes i
    CI-steget» — her er det steget. Uten det kan en linje omskrives i det
    stille, og da er ikke loggen lenger kanonisk.
    """
    try:
        res = subprocess.run(
            ["git", "diff", "--numstat", f"{base}..HEAD", "--", KILDELOGG],
            cwd=str(ROT), capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError) as ex:
        return [{"type": "append_only_ikke_kjort", "msg": str(ex)[:150]}]
    if res.returncode != 0:
        return [{"type": "append_only_ikke_kjort", "base": base,
                 "msg": res.stderr.strip()[:150]}]
    feil: list[dict] = []
    for linje in res.stdout.splitlines():
        deler = linje.split("\t")
        if len(deler) < 3:
            continue
        slettet = deler[1]
        if slettet.isdigit() and int(slettet) > 0:
            feil.append({"type": "aktivitetslogg_omskrevet", "base": base,
                         "slettede_linjer": int(slettet),
                         "melding": "loggen er append-only — linjer skal bare "
                                    "legges til, aldri endres eller fjernes"})
    return feil


def hoved(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", action="store_true")
    p.add_argument("--base", help="git-ref for append-only-sjekken "
                                 "(f.eks. origin/main)")
    a = p.parse_args(argv)

    resultat = avvik(LOGG, CHANGELOG_JSON, CHANGELOG_HTML)
    feil = resultat["feil"]
    info = dict(resultat.get("info") or {})
    if a.base:
        feil += append_only_feil(a.base)
    ellers = len(feil)

    rapport = {
        "sjekk": "changelog-projeksjon",
        "generator": GENERATOR,
        "generator_version": GENERATORVERSJON,
        "input_hash": info.get("input_hash"),
        "endringer": info.get("endringer"),
        "legacy_uten_change_id": info.get("legacy_uten_change_id"),
        "meta_hendelser": info.get("meta_hendelser"),
        "base": a.base,
        "feil": feil,
    }
    if a.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=1))
    else:
        print(f"changelog-projeksjon: {ellers} feil "
              f"({info.get('endringer')} endringer, "
              f"input_hash={info.get('input_hash')})")
        for f in feil[:25]:
            print("  ", f)
        if img := info.get("legacy_uten_change_id"):
            print(f"  INFO: {img} legacy-linje(r) uten lagret change_id — "
                  f"avledet, ikke en feil")
        if feil:
            print(f"  fiks: python3 scripts/maintenance/{GENERATOR}")
    return 1 if ellers else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
