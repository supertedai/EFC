#!/usr/bin/env python3
"""Build a work queue directly from a git ref, not from the working disk."""
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


def _git_sha(ref: str) -> str:
    """Resolve the ref to one commit ONCE, and read everything from there.

    Without this the run reads the moving ref over and over: if `origin/main`
    moves in the meantime, two files in the same answer can come from
    different states, and the answer becomes impossible to reproduce.
    """
    try:
        ut = subprocess.run(["git", "rev-parse", ref], cwd=ROT, check=True,
                            capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"unknown ref {ref!r}: {exc}") from exc
    return ut.stdout.strip()


def _git_fil(ref: str, sti: str) -> str:
    """Read a file from ref so that uncommitted changes cannot change the answer."""
    try:
        ut = subprocess.run(
            ["git", "show", f"{ref}:{sti}"],
            cwd=ROT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"could not read {sti} from {ref}: {exc}") from exc
    return ut.stdout


def _bank(ref: str) -> dict[str, Any]:
    return json.loads(_git_fil(ref, "schema/regime_nodes.jsonld"))


def _plassering(ref: str) -> dict[str, tuple[str, int]]:
    """Fetch the generator's explicit group and chapter map from the same ref."""
    tre = ast.parse(_git_fil(ref, "scripts/maintenance/efc_atlas_generator.py"))
    for node in tre.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PLASSERING"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit(f"PLASSERING is missing in {ref}")


def _fylt(verdi: Any) -> bool:
    """Is the field DECLARED with content?

    `"   "` is not an answer. The first version treated a whitespace string as
    filled, so a node could look measured with an empty field — and the test
    computed the expected number with `bool()`, that is a DIFFERENT definition
    than the code it tested. `False` and `0` count as declared: they are
    answers, not the absence of an answer.
    """
    if isinstance(verdi, str):
        return bool(verdi.strip())
    return verdi is not None and verdi != [] and verdi != {}


def _status(objekt: dict[str, Any], felt: str) -> str | None:
    """Tell a missing key apart from an existing, empty value."""
    if felt not in objekt:
        return "finnes_ikke"
    if not _fylt(objekt[felt]):
        return "tomt"
    return None


def sakse_noder(noder: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build the S-queue and the measurement sums from public nodes."""
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
        if node["id"] not in plassering:
            # No default value here. The class of error was measured before:
            # in the atlas `PLASSERING.get(navn, ("ghost", 8))` made 68 of 73
            # nodes "not built", and the error looked like data. A node that
            # is missing a placement must be reported, not guessed at.
            raise SystemExit(
                f"[arbeidskoe] {node['id']} is not in the generator's "
                f"PLASSERING — cannot decide whether it is built or ghost")
        gruppe, kapittel = plassering[node["id"]]
        if gruppe != "ghost":
            continue
        # target is the bank's own declaration of what the node must measure.
        maal = (node.get("measure") or {}).get("target")
        rader.append({
            "id": node["id"],
            "intensjon": maal,
            "intensjon_status": "declared" if _fylt(maal) else "not declared",
            "gruppe": gruppe,
            "kapittel": kapittel,
        })
    rader.sort(key=lambda rad: rad["id"])
    return {"modus": "ghost", "noder": rader}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generated atlas work queue")
    modus = parser.add_mutually_exclusive_group(required=True)
    modus.add_argument("--sakse", action="store_true")
    modus.add_argument("--ghost", action="store_true")
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable output (default: readable list)")
    args = parser.parse_args()
    # Read everything from ONE resolved commit, not from the moving ref. If
    # `origin/main` moves mid-run, the header and the content could otherwise
    # answer from different states.
    sha = _git_sha(args.ref)
    data = _bank(sha)
    if args.sakse:
        svar = arbeidskoe_sakse(data)
    else:
        svar = arbeidskoe_ghost(data, _plassering(sha))
    if args.json:
        print(json.dumps(svar, ensure_ascii=False, indent=2, sort_keys=True))
        return
    # The default is READABLE output. The first version wrote only JSON:
    # correct, but a queue nobody can read without an extra tool is not a
    # queue for a human who must choose what gets filled next.
    if args.sakse:
        m = svar["maalte"]
        noder = svar["noder"]
        print(f"S-axis work queue · {len(noder)} nodes are missing at least one "
              f"field (nodes without gaps are not in the queue)")
        print("  measured in total: " + " · ".join(
            f"{k} {v}" for k, v in sorted(m.items())))
        print()
        for rad in noder[:40]:
            hull = ", ".join(f"{f['felt']}:{f['status']}" for f in rad["mangler"])
            print(f"  {rad['id']:<30} measured={rad['maalte']}  missing {hull}")
        if len(noder) > 40:
            print(f"  … {len(noder) - 40} more (use --json for the full list)")
    else:
        print(f"Ghost nodes · {len(svar['noder'])} designed, not built")
        print()
        for rad in svar["noder"]:
            intensjon = rad.get("intensjon") or "intensjon: not declared"
            print(f"  {rad['id']:<28} [{rad['gruppe']}] {intensjon}")


if __name__ == "__main__":
    main()
