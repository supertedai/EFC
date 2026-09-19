#!/usr/bin/env python3
"""efc_ledger_speil — keep the ledger TWINS identical to their canonical source.

``docs/validation-ledger/data/ledger.json`` is CANONICAL for the GRAV claim
texts: it is the file the language rule is applied to (Morten 2026-09-17, all
repo content English), and the file the public pages are built from. Two
artifacts PROJECT it and must never be edited on their own:

  data/grav.json
      ``$.claims[i].text`` == ``ledger.json $.grav_pipeline.claims[i].text``.
      The two arrays are measured identical in length, order and every field
      other than ``text`` — asserted here, not assumed.

  index.md, section 3 ("EFC-GRAV Discrete Gravity Pipeline")
      the "Physics Claim" column of a claim row == ``text[:97] + "..."``
      (measured: every non-empty claim cell is exactly 100 characters).

Measuring these identities rather than trusting prose is the point: the drift
this repairs was created by translating ONE twin (PR #460) and leaving the
other, and nothing in the tree could see it. ``tests/test_ledger_speil.py``
locks both identities so the class cannot reopen silently.

Usage:
  python3 scripts/maintenance/efc_ledger_speil.py            # check (exit 1 on drift)
  python3 scripts/maintenance/efc_ledger_speil.py --skriv    # write the projections
  python3 scripts/maintenance/efc_ledger_speil.py --json     # machine-readable
"""
from __future__ import annotations

import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
LEDGER = os.path.join(REPO, "docs", "validation-ledger", "data", "ledger.json")
GRAV = os.path.join(REPO, "docs", "validation-ledger", "data", "grav.json")
INDEX = os.path.join(REPO, "docs", "validation-ledger", "index.md")

# Measured truncation of the claim text in index.md's claim table: the cell is
# always exactly 100 characters, i.e. 97 characters plus an ellipsis.
TRUNC = 97
EMPTY_CELL = "—"

# | # | Physics Claim | Status | Evidence |
CLAIM_ROW = re.compile(r"^\| (\d+) \| (.*) \| ([^|]*) \| ([^|]*) \|\s*$")


def _load():
    with open(LEDGER, encoding="utf-8") as fh:
        ledger = json.load(fh)
    with open(GRAV, encoding="utf-8") as fh:
        grav = json.load(fh)
    with open(INDEX, encoding="utf-8") as fh:
        index = fh.read()
    return ledger, grav, index


def kanoniske_tekster(ledger: dict) -> list[str]:
    return [c.get("text") or "" for c in ledger["grav_pipeline"]["claims"]]


def projeksjon(tekst: str) -> str:
    """index.md's rendering of one claim text."""
    if not tekst:
        return EMPTY_CELL
    return tekst[:TRUNC] + "..." if len(tekst) > TRUNC else tekst


def sjekk() -> dict:
    """Return the measured drift report. No writes."""
    ledger, grav, index = _load()
    kanon = kanoniske_tekster(ledger)
    grav_claims = grav["claims"]
    feil = []

    if len(grav_claims) != len(kanon):
        feil.append(f"claims length differs: grav.json={len(grav_claims)} "
                    f"ledger.json={len(kanon)}")
    ellers_lik = 0
    avvik_felt = {}
    tekst_avvik = []
    for i, (a, b) in enumerate(zip(grav_claims, kanon)):
        for k in set(a) | {"text"}:
            if k == "text":
                continue
            if a.get(k) != ledger["grav_pipeline"]["claims"][i].get(k):
                avvik_felt[k] = avvik_felt.get(k, 0) + 1
        if (a.get("text") or "") == b:
            ellers_lik += 1
        else:
            tekst_avvik.append(i)
    if avvik_felt:
        feil.append(f"grav.json differs from ledger.json in fields other than "
                    f"text: {avvik_felt}")
    if tekst_avvik:
        feil.append(f"grav.json.claims[].text differs from the canonical "
                    f"ledger.json text in {len(tekst_avvik)} place(s), "
                    f"e.g. index {tekst_avvik[:5]} — run --skriv")

    # index.md claim rows
    rader = 0
    rader_avvik = []
    for ln in index.split("\n"):
        m = CLAIM_ROW.match(ln)
        if not m:
            continue
        if not m.group(3).strip().startswith("❓") or m.group(4).strip() != "None":
            continue
        i = int(m.group(1)) - 1
        if i >= len(kanon):
            continue
        rader += 1
        gammel = grav_claims[i].get("text") or "" if i < len(grav_claims) else ""
        if m.group(2) not in (projeksjon(gammel), projeksjon(kanon[i])):
            rader_avvik.append((i + 1, m.group(2)[:60]))
    if rader_avvik:
        feil.append(f"index.md claim rows are neither the old nor the new "
                    f"projection: {rader_avvik[:5]}")

    return {
        "grav_text_avvik": len(tekst_avvik),
        "grav_text_like": ellers_lik,
        "index_rader": rader,
        "index_rader_avvik": len(rader_avvik),
        "feil": feil,
    }


def skriv() -> dict:
    """Rewrite both projections from the canonical source. Idempotent."""
    ledger, grav, index = _load()
    kanon = kanoniske_tekster(ledger)
    grav_claims = grav["claims"]
    if len(grav_claims) != len(kanon):
        raise SystemExit("REFUSE: claims length differs — not a twin pair")

    # 1. grav.json — only the text fields move. grav.json encodes "no text"
    #    as null where ledger.json uses "", so an empty canonical text leaves
    #    the existing representation alone (a null/"" flip for 28 096 claims
    #    would bury the real change in noise).
    for c, t in zip(grav_claims, kanon):
        if t:
            c["text"] = t
        elif c.get("text"):
            c["text"] = None
    with open(GRAV, "w", encoding="utf-8") as fh:
        json.dump(grav, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # 2. index.md — only the "Physics Claim" cell moves.
    ut, antall = [], 0
    for ln in index.split("\n"):
        m = CLAIM_ROW.match(ln)
        if m and m.group(3).strip().startswith("❓") and m.group(4).strip() == "None":
            i = int(m.group(1)) - 1
            if i < len(kanon):
                ny = projeksjon(kanon[i])
                if m.group(2) != ny:
                    antall += 1
                    ln = f"| {m.group(1)} | {ny} | {m.group(3)} | {m.group(4)} |"
        ut.append(ln)
    tekst = "\n".join(ut)
    if not tekst.endswith("\n"):
        tekst += "\n"
    with open(INDEX, "w", encoding="utf-8") as fh:
        fh.write(tekst)
    return {"grav_skrevet": len(kanon), "index_rader_endret": antall}


def main() -> int:
    skriv_modus = "--skriv" in sys.argv
    if skriv_modus:
        res = skriv()
        print(f"[ledger-speil] wrote {res['grav_skrevet']} grav.json texts, "
              f"{res['index_rader_endret']} index.md rows")
    rap = sjekk()
    if "--json" in sys.argv:
        print(json.dumps(rap, ensure_ascii=False, indent=2))
    else:
        print("[ledger-speil] grav.json texts differing from ledger.json: "
              f"{rap['grav_text_avvik']} (identical: {rap['grav_text_like']})")
        print(f"[ledger-speil] index.md claim rows checked: {rap['index_rader']}, "
              f"deviating: {rap['index_rader_avvik']}")
        for f in rap["feil"]:
            print(f"[ledger-speil] ERROR: {f}")
    return 1 if rap["feil"] else 0


if __name__ == "__main__":
    sys.exit(main())
