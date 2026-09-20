#!/usr/bin/env python3
"""efc_4b — §4b is generated from a data file instead of being edited as HTML.

Why, measured 2026-08-23: five workers were each given an external finding to
register. All five put their entry in the same `<ul>` in
`EFC_Validation_Ledger.html`. All five PRs became `CONFLICTING`, had to be pulled
and merged into one. The promotion had to be throttled to one card at a time.

It is not a concurrency problem you throttle your way out of — it is that **two
additions to the same HTML list always collide**. If the workers instead add a
*row* to a JSON file, they collide only if they touch the same row.

The register is `docs/validation-ledger/data/external-references.json`. It is
used by two:

* `efc_build_4b.py --skriv` writes the §4b block in the HTML from it.
* `efc_doi_coverage.py` reads `rolle` from it, so a registered external
  citation is no longer reported as an anomaly.

**Lossless on purpose.** Every entry stores the whole `<li>…</li>` verbatim in
`html`. The generator renders it unchanged; it does not rewrite prose. The
fields `tag`, `arxiv` and `rolle` are derived *next to* it for tools, not instead
of the text. A generator that rephrases a published claim is not a
generator — it is an author.

Usage:
    efc_4b.py hent      # read §4b from the HTML → write the register (one-time)
    efc_4b.py bygg      # the register → §4b in the HTML
    efc_4b.py sjekk     # build in memory, exit 1 if the HTML deviates
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
    """The bounds of the §4b lists. Uses the markers when they exist, otherwise
    from the first <ul> after the heading to the last </ul> before the next <h2>."""
    if START in t and SLUTT in t:
        return t.index(START), t.index(SLUTT) + len(SLUTT)
    i = t.find("4b. External Observations Under Confrontation")
    if i < 0:
        raise SystemExit("[4b] did not find the §4b heading")
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
        "_om": ("§4b in EFC_Validation_Ledger.html is generated from this file. "
                "Edit HERE, not in the HTML — two additions to the same HTML list "
                "always collide, two rows in this one do not."),
        "_roller": {
            "under_confrontation": "third-party finding EFC tests itself against",
            "input_data": "measurement EFC builds on",
            "context": "background, not confronted",
        },
        "_advarsel": ("`html` is stored verbatim and rendered unchanged. A generator "
                      "that rephrases a published claim is not a "
                      "generator, it is an author."),
        "grupper": grupper,
    }
    REG.parent.mkdir(parents=True, exist_ok=True)
    REG.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8")
    n = sum(len(g["oppforinger"]) for g in grupper)
    print(f"[4b] fetched {n} entries in {len(grupper)} group(s) → "
          f"{REG.relative_to(ROOT)}")
    return 0


def _render(d: dict) -> str:
    """Renders §4b with the SAME formatting as the original.

    The first draft wrote `<li>` flush left with no blank lines in between.
    The content was preserved verbatim, but the diff against the original was
    37 lines. A generator that changes layout on its first run cannot prove that it
    is lossless — and on a public page, needless layout churn is the same
    noise as the timestamp commits in §6 of ADR-024.

    The format mirrored: two spaces in front of `<li>`, a blank line between
    the entries, a blank line before `<h3>`, no blank line before `</ul>`.

    One place is NORMALISED: the original was missing a blank line between two of
    the entries — uneven formatting from earlier hand editing. It is evened
    out. Coding historical sloppiness into the register forever would be to choose
    fidelity to a coincidence over fidelity to the content. The content is verified
    byte-identical one by one; it is only whitespace that changes.
    """
    ut = [START]
    for i, g in enumerate(d["grupper"]):
        if g.get("overskrift"):
            if i:
                ut.append("")          # blank line before <h3>, as in the original
            ut.append(f'<h3 style="margin-bottom:4px;">{g["overskrift"]}</h3>')
        ut.append("<ul>")
        # The register has two kinds of rows. Those with `html` ARE §4b entries
        # and are rendered. Those without are REGISTERED citations — known
        # external works with DOI and role, which stand in running text
        # elsewhere. They are read by `efc_doi_coverage.py`, but do not belong
        # in the §4b list, and a generator that wrote them there would inflate
        # the confrontation section with references nobody confronts.
        rader = [o["html"] for o in g["oppforinger"] if o.get("html")]
        ut.append("\n\n".join("  " + r for r in rader))
        ut.append("</ul>")
    ut.append(SLUTT)
    return "\n".join(ut)


def bygg(bare_sjekk: bool) -> int:
    if not REG.exists():
        print(f"[4b] the register is missing: {REG}", file=sys.stderr)
        return 2
    d = json.loads(REG.read_text(encoding="utf-8"))
    t = HTML.read_text(encoding="utf-8")
    a, b = _blokk(t)
    ny = t[:a] + _render(d) + t[b:]
    if ny == t:
        print("[4b] unchanged")
        return 0
    if bare_sjekk:
        print("[4b] DEVIATION: the HTML does not match the register. "
              "Run `efc_4b.py bygg`.", file=sys.stderr)
        return 1
    HTML.write_text(ny, encoding="utf-8")
    n = sum(len(g["oppforinger"]) for g in d["grupper"])
    print(f"[4b] wrote {n} entries to {HTML.relative_to(ROOT)}")
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
