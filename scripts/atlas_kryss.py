#!/usr/bin/env python3
"""Cross-rotation: two axes against each other, on top of the generic finder.

`atlas_lesing.akser()` already finds EVERY axis by itself (dotted paths, nested
fields) -- the generic rotation asked for on 2026-09-17: "make sure you can
rotate around all axes and the whole atlas". What it did not do, and what this
file adds, is hold two axes against each other. "Where do the falsifiable nodes
land, and on what evidence?" is not a lookup -- it is a cross.

So this file declares NO axis paths of its own. It asks `akser()` what exists,
and adds only the DERIVED coordinates, which are not fields in the bank but
arithmetic over several fields.

    python3 scripts/atlas_kryss.py                 # every axis, discovered
    python3 scripts/atlas_kryss.py --akse rcmp.overlap
    python3 scripts/atlas_kryss.py --roter can_be_felled,epistemikk.evidensstatus
    python3 scripts/atlas_kryss.py --roter nivaa.indeks,can_be_felled --bare-offentlige

A node where an axis does not resolve is a HOLE for that axis (printed as "—"),
never a zero and never a guess.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_lesing  # noqa: E402

#: Derived coordinates: not fields in the bank, but arithmetic over several
#: fields. Declared here so they can be rotated like any other axis.
DERIVED = ("can_be_felled", "falsifiability_stance", "uncertainty")


def _get(node: dict, path: str):
    v = node
    for bit in path.split("."):
        if not isinstance(v, dict) or bit not in v:
            return None
        v = v[bit]
    return v


def _scalar(v):
    """A coordinate is a SCALAR. An object cannot be rotated on.

    Measured 2026-09-19: an earlier version pointed straight at `nivaa` and
    `regime`, which are objects, and the rotation printed the whole object as
    the value of a cell. The rule lives here so that cannot happen silently.
    """
    if v is None or isinstance(v, (str, int, float, bool)):
        return v if v != "" else None
    raise SystemExit(
        f"the axis resolves to a {type(v).__name__}, not a scalar — declare the "
        f"coordinate (e.g. `nivaa.indeks`), not the object (`nivaa`)")


def uncertainty(node: dict):
    """A bound is a NUMBER. `feilgrense: null` is a NAMED hole, not a bound."""
    poster = _get(node, "usikkerhet.poster")
    if not isinstance(poster, (dict, list)):
        return None
    values = poster.values() if isinstance(poster, dict) else poster
    bounds = [p.get("feilgrense") for p in values
              if isinstance(p, dict) and p.get("feilgrense") is not None]
    return ";".join(str(b) for b in bounds) if bounds else None


def axis_value(node: dict, axis: str):
    """One axis for one node: declared, derived, or a named hole (None)."""
    if axis in DERIVED:
        if axis == "can_be_felled":
            if node.get("ville_falsifisere"):
                return "yes"
            if node.get("falsifiserbarhet") or \
                    (node.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn"):
                return "no"
            return None
        if axis == "falsifiability_stance":
            if node.get("ville_falsifisere"):
                return "falsifier"
            if node.get("falsifiserbarhet"):
                return "status"
            if (node.get("stipulasjoner") or {}).get("ikke_falsifiserbar_grunn"):
                return "class"
            return None
        return "with_bound" if uncertainty(node) else None
    return _scalar(_get(node, axis))


def rotate(nodes: list[dict], axes: list[str]) -> dict:
    """The cross. A rotation PARTITIONS the population: every node in one cell."""
    cross: dict[tuple, int] = {}
    for n in nodes:
        key = tuple(str(axis_value(n, a) or "—") for a in axes)
        cross[key] = cross.get(key, 0) + 1
    return {"axes": axes, "nodes": len(nodes),
            "cells": sorted(cross.items(), key=lambda x: -x[1])}


def main() -> None:
    p = argparse.ArgumentParser(description="Cross-rotation in the atlas")
    p.add_argument("--ref", default="HEAD")
    p.add_argument("--akse", help="show one axis for every node")
    p.add_argument("--roter", help="cross axes, e.g. nivaa.indeks,can_be_felled")
    p.add_argument("--bare-offentlige", action="store_true",
                   help="public nodes only")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    atlas = atlas_lesing.les_atlas(ROT, ref=a.ref)
    nodes = atlas.get("noder") or []
    if a.bare_offentlige:
        nodes = [n for n in nodes if n.get("synlighet") != "intern"]
    found = atlas_lesing.akser(atlas)

    if a.akse:
        values: dict[str, list[str]] = {}
        for n in nodes:
            values.setdefault(str(axis_value(n, a.akse) or "—"), []).append(n["id"])
        if a.json:
            print(json.dumps(values, ensure_ascii=False, indent=2))
            return
        print(f"{a.akse}: {len(values)} values over {len(nodes)} nodes")
        for v, ids in sorted(values.items(), key=lambda x: -len(x[1])):
            print(f"  {v[:48]:50} {len(ids):>3}  "
                  f"{' '.join(ids[:4])}{' …' if len(ids) > 4 else ''}")
        return

    if a.roter:
        axes = [x.strip() for x in a.roter.split(",") if x.strip()]
        unknown = [x for x in axes if x not in found and x not in DERIVED]
        if unknown:
            raise SystemExit(
                f"unknown axis: {', '.join(unknown)} — `--dekning` shows the "
                f"{len(found) + len(DERIVED)} that exist")
        r = rotate(nodes, axes)
        if a.json:
            print(json.dumps(r, ensure_ascii=False, indent=2))
            return
        print(f"ROTATION {' × '.join(axes)} — {len(nodes)} nodes, "
              f"{len(r['cells'])} cells\n")
        for key, c in r["cells"][:40]:
            print(f"  {' | '.join(v[:22] for v in key):70} {c:>4}")
        if len(r["cells"]) > 40:
            print(f"  … {len(r['cells']) - 40} more cells (--json for all)")
        return

    print(f"THE AXES — {len(found)} discovered in the data + {len(DERIVED)} derived "
          f"({len(nodes)} nodes)\n")
    print(f"{'axis':40} {'n':>4}  example")
    for path, (n, ex) in sorted(found.items(), key=lambda x: -x[1][0]):
        print(f"{path:40} {n:>4}  {', '.join(str(e)[:18] for e in ex[:3])}")
    for axis in DERIVED:
        filled = sum(1 for x in nodes if axis_value(x, axis) is not None)
        print(f"{axis + ' (derived)':40} {filled:>4}")
    print("\nA hole is not an error — it is an axis the node has not answered.")


if __name__ == "__main__":
    main()
