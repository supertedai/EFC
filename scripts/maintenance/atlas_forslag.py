#!/usr/bin/env python3
"""Foreslaa plassering av nye innsikter uten aa opprette atlas-noder.

Lytteren er bevisst en terskel rundt atlaset: den leser koeen eller nye
innsikter, bruker den eksisterende ``plasser()``-leseren, og returnerer
forslag som mennesket/Opus kan godkjenne. Ingen skrivebane peker til
``schema/regime_nodes.jsonld``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from atlas_lesing import les_atlas, plasser  # noqa: E402

STANDARD_KOE = ROOT / "data" / "inntak" / "atlas_fragmenter.jsonl"
VURDERINGSORD = (
    "jeg tror", "jeg mener", "tror", "mener", "kanskje", "burde",
    "bør", "bor", "vurder", "mulig", "antar", "antak", "hypotese",
    "synes", "sannsynligvis", "muligens",
)


def les_koe(sti: str | Path) -> list[str]:
    """Les tekstfelt fra JSONL-koeen; manglende koe er en tom koe."""
    fil = Path(sti)
    if not fil.exists():
        return []
    innsikter: list[str] = []
    for nummer, linje in enumerate(fil.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            record = json.loads(linje)
        except json.JSONDecodeError as feil:
            raise ValueError(f"ugyldig JSONL paa linje {nummer} i {fil}: {feil}") from feil
        tekst = record.get("tekst") if isinstance(record, dict) else record
        if isinstance(tekst, str) and tekst.strip():
            innsikter.append(tekst)
    return innsikter


def _er_vurdering(tekst: str) -> bool:
    lav = " ".join(tekst.casefold().replace("-", " ").split())
    return any(ord_ in lav for ord_ in VURDERINGSORD)


def _domener(plassering: dict[str, Any], atlas: dict[str, Any]) -> list[str]:
    """Hent bare reelle domeneforslag, aldri plasser() sin visningsfallback."""
    resultat: list[str] = []
    for forslag in plassering.get("forslag", []):
        domene = forslag.get("domene")
        if domene and domene != "(avledet)" and domene not in resultat:
            if forslag.get("noder") or "alfabetisk" not in forslag.get("kobling", ""):
                resultat.append(domene)
    noder = {n.get("id"): n for n in atlas.get("noder", [])}
    for node_id in plassering.get("naere_noder", []):
        domene = (noder.get(node_id) or {}).get("buss_domene")
        if domene and domene not in resultat:
            resultat.append(domene)
    return resultat


def foreslaa(atlas: dict[str, Any], tekst: str) -> dict[str, Any]:
    """Lag ett forslag og marker eksplisitt at ingen node ble opprettet."""
    plassering = plasser(atlas, tekst)
    if _er_vurdering(tekst):
        kategori = "ikke-node-verdig"
        destinasjon = "Hindsight-retain"
    elif plassering.get("status") == "hjem_funnet" or plassering.get("naere_noder"):
        kategori = "node-verdig"
        destinasjon = "menneskelig/Opus-vurdering"
    else:
        kategori = "uten_hjem"
        destinasjon = "menneskelig/Opus-vurdering"

    return {
        "tekst": tekst,
        "kategori": kategori,
        "nodeverdig": kategori == "node-verdig",
        "domene_forslag": _domener(plassering, atlas) if kategori == "node-verdig" else [],
        "naere_noder": plassering.get("naere_noder", []),
        "plassering": plassering,
        "destinasjon": destinasjon,
        "opprettet_node": False,
    }


def foreslaa_alle(atlas: dict[str, Any], innsikter: Iterable[str]) -> dict[str, Any]:
    return {
        "kilde": atlas.get("kilde"),
        "commit": atlas.get("commit"),
        "forslag": [foreslaa(atlas, tekst) for tekst in innsikter if tekst.strip()],
        "noder_opprettet": 0,
    }


def _argumenter() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Foreslaa atlas-plassering uten aa opprette noder.")
    parser.add_argument("--tekst", action="append", help="ny innsikt; kan gjentas")
    parser.add_argument("--alle", action="store_true", help="les alle fragmenter fra koeen")
    parser.add_argument("--inntak-fil", default=str(STANDARD_KOE), help="JSONL-koe for --alle")
    parser.add_argument("--repo", default=str(ROOT), help="EFC-repositoriet")
    parser.add_argument("--ref", default="HEAD", help="git-ref atlaset skal leses fra")
    return parser.parse_args()


def main() -> int:
    args = _argumenter()
    innsikter = list(args.tekst or [])
    if args.alle:
        innsikter.extend(les_koe(args.inntak_fil))
    if not innsikter and not sys.stdin.isatty():
        stdin = sys.stdin.read().strip()
        if stdin:
            innsikter.append(stdin)
    if not innsikter:
        raise SystemExit("oppgi --tekst, --alle eller tekst paa stdin")
    atlas = les_atlas(args.repo, ref=args.ref)
    print(json.dumps(foreslaa_alle(atlas, innsikter), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
