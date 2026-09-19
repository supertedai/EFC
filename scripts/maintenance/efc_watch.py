#!/usr/bin/env python3
"""efc_watch — one file per watched source, instead of one long list.

Same recipe as `efc_4b.py`, and for the same reason — but one notch further.

Measured 2026-08-23: three workers ran in parallel for the first time after
§4b became data-driven. §4b held. But **all three** touched
`external_research_watch.json` and collided there instead. Making §4b data
moved the boundary one notch; it did not remove it.

For §4b it was enough to gather the rows in one JSON file, because the workers
there added text blocks that would otherwise land in the same `<ul>`. Here the
source is already JSON — and it still collides, because two additions to **the
same array** hit the same lines. A shared file does not help when the conflict
is textual.

Therefore: **one file per source** under
`docs/public/external_research_watch/`.
Two workers that each add their own source never touch the same file, and git
has nothing to merge. `external_research_watch.json` becomes generated, and is
kept because the monitor's prompt reads it.

    efc_watch.py hent    one-off: split the long list into one file per source
    efc_watch.py bygg    the parts → external_research_watch.json
    efc_watch.py sjekk   exit 1 if the generated file drifted from the parts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMLET = ROOT / "docs/public/external_research_watch.json"
DELER = ROOT / "docs/public/external_research_watch"


def _navn(post: dict, i: int) -> str:
    """File name from the key. `arXiv:2607.18234` → `2607.18234.json`.

    The key is the identity: two workers that find the same source write to the
    same file and collide — as they should. Only *different* sources must be
    able to run in parallel.
    """
    k = str(post.get("key") or "").strip()
    s = re.sub(r"^arxiv:", "", k, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")
    return f"{s or f'post-{i:03d}'}.json"


def hent(rydd: bool) -> int:
    d = json.loads(SAMLET.read_text(encoding="utf-8"))
    poster = d.get("items") or []
    DELER.mkdir(parents=True, exist_ok=True)
    (DELER / "_hode.json").write_text(
        json.dumps({k: v for k, v in d.items() if k != "items"},
                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    sett: set[str] = set()
    for i, p in enumerate(poster):
        n = _navn(p, i)
        if n in sett:                        # the same key twice
            n = f"{n[:-5]}-{i:03d}.json"
        sett.add(n)
        (DELER / n).write_text(
            json.dumps(p, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8")
    print(f"[watch] split {len(poster)} sources → {DELER.relative_to(ROOT)}/")

    # Parts that are NOT in the combined file. Two completely different things
    # look alike here, which is why it does not clean up by itself:
    #
    #   a) leftovers — the post was removed from the combined file, and without
    #      cleanup it sneaks back in at the next `bygg`
    #   b) FRESH WORK — a worker just added a source that has not been folded
    #      in yet. One file per source exists precisely so that this can
    #      happen.
    #
    # Deleting blindly would take (b) with (a). Leaving it alone would let (a)
    # live. Therefore: name them and fail closed. `bygg` folds (b) into the
    # combined file; after that what remains is by definition (a), and `--rydd`
    # removes it.
    ukjent = sorted(f.name for f in DELER.glob("*.json")
                    if f.name != "_hode.json" and f.name not in sett)
    if ukjent:
        if rydd:
            for n in ukjent:
                (DELER / n).unlink()
            print(f"[watch] cleaned {len(ukjent)} part(s) without a post in "
                  f"the combined file: {', '.join(ukjent)}")
            return 0
        print(f"[watch] {len(ukjent)} part(s) are not in the combined file:",
              file=sys.stderr)
        for n in ukjent:
            print(f"          {n}", file=sys.stderr)
        print("[watch] either they are fresh work — run `bygg` first — "
              "or leftovers: `hent --rydd`.", file=sys.stderr)
        return 1
    return 0


def _samle() -> dict:
    hode = json.loads((DELER / "_hode.json").read_text(encoding="utf-8"))
    par = []
    for f in sorted(DELER.glob("*.json")):
        if f.name == "_hode.json":
            continue
        par.append((f.name, json.loads(f.read_text(encoding="utf-8"))))
    # Stable order: most recently seen first, then `key` — and the file name
    # when `key` is missing. All 109 posts have a unique `key` today, so the
    # fallback changes no order now; it exists so that a future post without
    # `key` does not let the filesystem's answer decide the order. That would
    # make the generator produce a new diff without anything having changed —
    # the same noise as the timestamp commits in ADR-024 §6.
    #
    # Sorting by file name instead would be equally stable, but would reshuffle
    # all 109 rows now (the file name strips the "arXiv:" prefix that `key`
    # keeps). This PR promises that the parts rebuild the combined file BYTE
    # FOR BYTE; a reshuffle would break exactly that promise to gain robustness
    # no post needs yet.
    par.sort(key=lambda fp: (str(fp[1].get("date_seen") or ""),
                             str(fp[1].get("key") or "") or fp[0]),
             reverse=True)
    return {**hode, "items": [p for _, p in par]}


def bygg(bare_sjekk: bool) -> int:
    if not (DELER / "_hode.json").exists():
        print(f"[watch] the parts are missing: {DELER}", file=sys.stderr)
        return 2
    samlet = _samle()                       # once: it reads every part
    ny = json.dumps(samlet, ensure_ascii=False, indent=2) + "\n"
    gml = SAMLET.read_text(encoding="utf-8") if SAMLET.exists() else ""
    # `status` is in the schema, but two posts on main are missing it. That is
    # inherited data, not something this generator introduced — hence WARNING
    # and not an error. A generator that starts rejecting data it was handed
    # itself stops the maintenance instead of carrying it.
    mangler = [str(x.get("key") or "?") for x in samlet["items"]
               if "status" not in x]
    if mangler:
        print(f"[watch] WARNING: {len(mangler)} post(s) without 'status': "
              f"{', '.join(mangler)}", file=sys.stderr)
    if ny == gml:
        print("[watch] unchanged")
        return 0
    if bare_sjekk:
        print("[watch] DEVIATION: the combined file does not match the parts. "
              "Run `efc_watch.py bygg`.", file=sys.stderr)
        return 1
    SAMLET.write_text(ny, encoding="utf-8")
    print(f"[watch] wrote {len(samlet['items'])} sources to "
          f"{SAMLET.relative_to(ROOT)}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("handling", choices=("hent", "bygg", "sjekk"))
    ap.add_argument("--rydd", action="store_true",
                    help="delete parts that are not in the combined file "
                         "(run `bygg` first, otherwise fresh work is lost)")
    a = ap.parse_args()
    if a.handling == "hent":
        return hent(a.rydd)
    return bygg(a.handling == "sjekk")


if __name__ == "__main__":
    raise SystemExit(main())
