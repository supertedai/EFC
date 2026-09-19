#!/usr/bin/env python3
"""Build a work queue straight from a git ref, not from the working disk."""
from __future__ import annotations

import argparse
import ast
import json
import subprocess
from pathlib import Path
from typing import Any

# ROT keeps its name: atlas_volum.py, atlas_navigasjon.py and the tests define
# the same module root under the same name. Reported, not hidden.
ROT = Path(__file__).resolve().parents[1]
# The four names are the bank's own fields (maale_paradigme and rcmp), not
# prose — they are read out of schema/regime_nodes.jsonld verbatim.
MEASURED_FIELDS = ("s_regime", "klarhetsfunksjon", "ebe_function", "sektor")
ALL_FIELDS = MEASURED_FIELDS + ("rcmp",)


def _git_sha(ref: str) -> str:
    """Resolve the ref to a commit ONCE, and read everything from there.

    Without this the run reads the moving ref over and over: if `origin/main`
    moves along the way, two files in the same answer can come from different
    states, and the answer becomes impossible to reproduce.
    """
    try:
        out = subprocess.run(["git", "rev-parse", ref], cwd=ROT, check=True,
                             capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"unknown ref {ref!r}: {exc}") from exc
    return out.stdout.strip()


def _git_file(ref: str, path: str) -> str:
    """Read a file from ref, so that uncommitted changes cannot change the answer."""
    try:
        out = subprocess.run(
            ["git", "show", f"{ref}:{path}"],
            cwd=ROT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"could not read {path} from {ref}: {exc}") from exc
    return out.stdout


def _bank(ref: str) -> dict[str, Any]:
    return json.loads(_git_file(ref, "schema/regime_nodes.jsonld"))


def _placement(ref: str) -> dict[str, tuple[str, int]]:
    """Fetch the generator's explicit group and chapter map from the same ref."""
    tree = ast.parse(_git_file(ref, "scripts/maintenance/efc_atlas_generator.py"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PLASSERING"
            for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise SystemExit(f"PLASSERING is missing in {ref}")


# `_fylt` keeps its name: tests/test_atlas_arbeidskoe.py imports it and calls
# it as the one definition of "filled" — the test and the code must agree on
# the definition, so they must agree on the name. Reported, not hidden.
def _fylt(value: Any) -> bool:
    """Is the field DECLARED with content?

    `"   "` is not an answer. The first version treated a whitespace string as
    filled, so a node could look measured with an empty field — and the test
    computed the expected number with `bool()`, that is, a DIFFERENT definition
    than the code it tested. `False` and `0` count as declared: they are
    answers, not the absence of an answer.
    """
    if isinstance(value, str):
        return bool(value.strip())
    return value is not None and value != [] and value != {}


def _status(object: dict[str, Any], field: str) -> str | None:
    """Distinguish a missing key from an existing, empty value.

    The two words it answers are the tool's own wire values, pinned by
    tests/test_atlas_arbeidskoe.py:149-150.
    """
    if field not in object:
        return "finnes_ikke"
    if not _fylt(object[field]):
        return "tomt"
    return None


# `sakse_noder` keeps its name: tests/test_atlas_arbeidskoe.py:121,143 imports
# it. Reported, not hidden.
def sakse_noder(nodes: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Build the S queue and the measurement sums from public nodes."""
    measured = {field: 0 for field in ALL_FIELDS}
    queue: list[dict[str, Any]] = []
    for node in nodes:
        measurement = node.get("maale_paradigme") or {}
        payload = dict(measurement)
        if "rcmp" in node:
            payload["rcmp"] = node["rcmp"]
        missing = []
        for field in ALL_FIELDS:
            status = _status(payload, field)
            if status is None:
                measured[field] += 1
            else:
                missing.append({"felt": field, "status": status})
        if missing:
            queue.append({
                "id": node["id"],
                "maalte": len(ALL_FIELDS) - len(missing),
                "mangler": missing,
            })
    queue.sort(key=lambda row: (-row["maalte"], row["id"]))
    return queue, measured


# `arbeidskoe_sakse` and `arbeidskoe_ghost` keep their names: the ghost mode is
# called by tests/test_atlas_arbeidskoe.py:106, and the two are one pair (the
# same `--sakse` / `--ghost` the CLI and the JSON `modus` carry).
def arbeidskoe_sakse(data: dict[str, Any]) -> dict[str, Any]:
    public = [n for n in data.get("nodes", []) if n.get("synlighet") == "offentlig"]
    nodes, measured = sakse_noder(public)
    return {"modus": "sakse", "maalte": measured, "noder": nodes}


def arbeidskoe_ghost(data: dict[str, Any], placement: dict[str, tuple[str, int]]) -> dict[str, Any]:
    rows = []
    for node in data.get("nodes", []):
        if node.get("synlighet") != "offentlig":
            continue
        if node["id"] not in placement:
            # No default value here. The class of bug is measured: in the atlas,
            # `PLASSERING.get(name, ("ghost", 8))` turned 68 of 73 nodes into
            # "not built", and the error looked like data. A node with no
            # placement must be reported, not guessed.
            raise SystemExit(
                f"[arbeidskoe] {node['id']} is not in the generator's "
                f"PLASSERING — cannot decide whether it is built or a ghost")
        group, chapter = placement[node["id"]]
        if group != "ghost":
            continue
        # target is the bank's own declaration of what the node shall measure.
        target = (node.get("measure") or {}).get("target")
        rows.append({
            "id": node["id"],
            "intensjon": target,
            "intensjon_status": "declared" if _fylt(target) else "not declared",
            "gruppe": group,
            "kapittel": chapter,
        })
    rows.sort(key=lambda row: row["id"])
    return {"modus": "ghost", "noder": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generated atlas work queue")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--sakse", action="store_true")
    mode.add_argument("--ghost", action="store_true")
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--json", action="store_true",
                        help="machine-readable output (default: readable list)")
    args = parser.parse_args()
    # Read everything from ONE resolved commit, not from the moving ref. If
    # `origin/main` moved mid-run, the header and the contents could otherwise
    # answer for two different states.
    sha = _git_sha(args.ref)
    data = _bank(sha)
    if args.sakse:
        answer = arbeidskoe_sakse(data)
    else:
        answer = arbeidskoe_ghost(data, _placement(sha))
    if args.json:
        print(json.dumps(answer, ensure_ascii=False, indent=2, sort_keys=True))
        return
    # The default is READABLE output. The first version wrote only JSON:
    # correct, but a queue nobody can read without an extra tool is not a queue
    # for a human who is to choose what gets filled next.
    if args.sakse:
        m = answer["maalte"]
        nodes = answer["noder"]
        print(f"S-axis work queue · {len(nodes)} nodes are missing at least one "
              f"field (nodes with no gap are not in the queue)")
        print("  measured in total: " + " · ".join(
            f"{k} {v}" for k, v in sorted(m.items())))
        print()
        for row in nodes[:40]:
            gaps = ", ".join(f"{f['felt']}:{f['status']}" for f in row["mangler"])
            print(f"  {row['id']:<30} measured={row['maalte']}  missing {gaps}")
        if len(nodes) > 40:
            print(f"  … {len(nodes) - 40} more (use --json for the full list)")
    else:
        print(f"Ghost nodes · {len(answer['noder'])} designed, not built")
        print()
        for row in answer["noder"]:
            intent = row.get("intensjon") or "intent: not declared"
            print(f"  {row['id']:<28} [{row['gruppe']}] {intent}")


if __name__ == "__main__":
    main()
