#!/usr/bin/env python3
"""Bygg ein arbeidskoe direkte fra ein git-ref, ikkje fra arbeidsdisken."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any

ROT = Path(__file__).resolve().parents[1]
MAALEFELT = ("s_regime", "klarhetsfunksjon", "ebe_function", "sektor")
ALLE_FELT = MAALEFELT + ("rcmp",)


def _git_fil(ref: str, sti: str) -> str:
    """Les ei fil fra ref slik at ulagte endringar ikkje kan endre svaret."""
    try:
        ut = subprocess.run(
            ["git", "show", f"{ref}:{sti}"],
            cwd=ROT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"kunne ikke lese {sti} fra {ref}: {exc}") from exc
    return ut.stdout


def _bank(ref: str) -> dict[str, Any]:
    return json.loads(_git_fil(ref, "schema/regime_nodes.jsonld"))


def _plassering(ref: str) -> dict[str, tuple[str, int]]:
    """Hent generatorens eksplisitte gruppe- og kapittelkart fra samme ref."""
    tre = ast.parse(_git_fil(ref, "scripts/maintenance/efc_atlas_generator.py"))
    for node in tre.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PLASSERING"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit(f"PLASSERING mangler i {ref}")


def _fylt(verdi: Any) -> bool:
    return verdi is not None and verdi != "" and verdi != [] and verdi != {}


def _status(objekt: dict[str, Any], felt: str) -> str | None:
    """Skill mellom manglende noekkel og eksisterende, tom verdi."""
    if felt not in objekt:
        return "finnes_ikke"
    if not _fylt(objekt[felt]):
        return "tomt"
    return None


def sakse_noder(noder: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Lag S-koeen og maalingssummer fra offentlige noder."""
    maalte = {felt: 0 for felt in ALLE_FELT}
    koe: list[dict[str, Any]] = []
    for node in noder:
        maale = node.get("maale_paradigme") or {}
        objekt = dict(maale)
        if "rcmp" in node:
            objekt["rcmp"] = node["rcmp"]
        mangler = []
        for felt in ALLE_FELT:
            status = _status(objekt, felt)
            if status is None:
                maalte[felt] += 1
            else:
                mangler.append({"felt": felt, "status": status})
        if mangler:
            koe.append({
                "id": node["id"],
                "maalte": len(ALLE_FELT) - len(mangler),
                "mangler": mangler,
            })
    koe.sort(key=lambda rad: (-rad["maalte"], rad["id"]))
    return koe, maalte


def arbeidskoe_sakse(data: dict[str, Any]) -> dict[str, Any]:
    offentlige = [n for n in data.get("nodes", []) if n.get("synlighet") == "offentlig"]
    noder, maalte = sakse_noder(offentlige)
    return {"modus": "sakse", "maalte": maalte, "noder": noder}


def arbeidskoe_ghost(data: dict[str, Any], plassering: dict[str, tuple[str, int]]) -> dict[str, Any]:
    rader = []
    for node in data.get("nodes", []):
        if node.get("synlighet") != "offentlig":
            continue
        gruppe, kapittel = plassering.get(node["id"], ("ghost", 8))
        if gruppe != "ghost":
            continue
        # target er bankens egen deklarasjon av hva noden skal maale.
        rader.append({
            "id": node["id"],
            "intensjon": (node.get("measure") or {}).get("target"),
            "gruppe": gruppe,
            "kapittel": kapittel,
        })
    rader.sort(key=lambda rad: rad["id"])
    return {"modus": "ghost", "noder": rader}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generert atlas-arbeidskoe")
    modus = parser.add_mutually_exclusive_group(required=True)
    modus.add_argument("--sakse", action="store_true")
    modus.add_argument("--ghost", action="store_true")
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--json", action="store_true",
                        help="maskinlesbar utdata (standard: lesbar liste)")
    args = parser.parse_args()
    data = _bank(args.ref)
    if args.sakse:
        svar = arbeidskoe_sakse(data)
    else:
        svar = arbeidskoe_ghost(data, _plassering(args.ref))
    if args.json:
        print(json.dumps(svar, ensure_ascii=False, indent=2, sort_keys=True))
        return
    # Standard er LESBAR utdata. Foerste utgave skrev bare JSON: riktig, men
    # en koe ingen kan lese uten et ekstra verktoy er ikke en koe for et
    # menneske som skal velge hva som fylles neste gang.
    if args.sakse:
        m = svar["maalte"]
        noder = svar["noder"]
        print(f"S-akse-arbeidskoe · {len(noder)} noder mangler minst ett felt "
              f"(noder uten hull staar ikke i koeen)")
        print("  maalt i alt: " + " · ".join(
            f"{k} {v}" for k, v in sorted(m.items())))
        print()
        for rad in noder[:40]:
            hull = ", ".join(f"{f['felt']}:{f['status']}" for f in rad["mangler"])
            print(f"  {rad['id']:<30} maalt={rad['maalte']}  mangler {hull}")
        if len(noder) > 40:
            print(f"  … {len(noder) - 40} flere (bruk --json for hele lista)")
    else:
        print(f"Ghost-noder · {len(svar['noder'])} designet, ikke bygget")
        print()
        for rad in svar["noder"]:
            print(f"  {rad['id']:<28} [{rad['gruppe']}] {rad.get('intensjon', '')}")


if __name__ == "__main__":
    main()
