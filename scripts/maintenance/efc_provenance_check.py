#!/usr/bin/env python3
"""
Package provenance gate (C13) — a registered deviation carries its evidence
==========================================================================

Why this exists (measured 2026-09-18, card t_20a3c257; first measured
2026-09-17 by EFC-H2, card t_d3c7fdf2): four packages under
``docs/papers/efc/`` carry a Figshare DOI whose *registered* record differs
from what the package says about itself — a subtitle dropped, a title
truncated, an uploaded filename left standing as the title, and in one case a
title that is not a variant of the package title at all.  The registry cannot
be edited from here and the package title must not be overwritten blindly, so
the deviation is registered *in the package* — and this gate is what keeps a
registration from being a decoration.

What this asserts, for every ``metadata.json`` under ``docs/papers/efc/``:

  1. if the package carries a ``provenance`` block, that block is complete:
     the archived title, the archived date, the archive DOI, the source, the
     measurement date and a note are all present and non-empty;
  2. ``title_matches_archive`` is not an opinion — it must equal
     ``title == archive_title``, and ``date_matches_repo`` must equal
     ``date == archive_date``.  A package cannot claim a match it does not
     have, and cannot deny one it has.  No normalisation is applied: the
     archived title is registered *verbatim* on purpose, so that the
     comparison is the same one a reader makes with their eyes;
  3. the block points at the package's own DOI (``archive_doi`` equals the
     DOI registered in the same file), so a copy-pasted block cannot claim
     another paper's archive;
  4. the DOIs in REGISTERED carry a provenance block at all — the four
     deviations measured 2026-09-18 must not be silently un-registered.

Deliberately NOT asserted: what the archived title *should* be.  Re-titling a
published record is a human decision (see the card's human gate), and the
archived title may legitimately change when it is made.  The gate therefore
requires the registration to exist and to be internally consistent — it does
not freeze the measured values.

meta/metadata.json is out of scope: this gate walks paper packages only.

Usage:  efc_provenance_check.py [--list]      exit 1 on any deviation
Needs:  Python standard library only (efc-verify.yml installs nothing)
"""
from __future__ import annotations

import json
import os
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf",
    "efc_graph_edges.json", "efc_graph_schema.json",
    "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
    "_archived",
}

# The four deviations measured 2026-09-18 (doi.org CSL-JSON, cross-checked
# against DataCite). Keyed by DOI, not by directory: a package rename must not
# drop the registration. A row without a reason is a hidden failure.
REGISTERED: dict[str, str] = {
    "10.6084/m9.figshare.28111925":
        "registered title carries the subtitle the package title omits",
    "10.6084/m9.figshare.28112036":
        "registered title is a different title from the package title",
    "10.6084/m9.figshare.28098314":
        "registered title carries the uploaded filename, '.pdf' included",
    "10.6084/m9.figshare.30402427":
        "registered title is truncated mid-phrase",
}

REQUIRED_STRINGS = (
    "archive_doi", "archive_title", "archive_date", "archive_type",
    "archive_date_type", "source", "measured_at", "note",
)
REQUIRED_BOOLS = ("title_matches_archive", "date_matches_repo")


def _package_doi(doc: dict) -> str | None:
    """The DOI the package registers about itself, in canonical form."""
    cand = doc.get("doi")
    if not isinstance(cand, str) or not cand.strip():
        paper = doc.get("paper")
        cand = paper.get("doi") if isinstance(paper, dict) else None
    if not isinstance(cand, str):
        return None
    return cand.strip() or None


def check_metadata(doc, rel: str) -> list[str]:
    """Structural and internal-consistency rule for one metadata.json."""
    problems: list[str] = []
    if not isinstance(doc, dict):
        return [f"{rel}: not a JSON object"]
    prov = doc.get("provenance")
    if prov is None:
        return problems
    if not isinstance(prov, dict):
        return [f"{rel}: provenance is {type(prov).__name__}, not an object"]

    for key in REQUIRED_STRINGS:
        v = prov.get(key)
        if not isinstance(v, str) or not v.strip():
            problems.append(f"{rel}: provenance.{key} is missing or empty — "
                            f"a registration without its evidence is not a registration")
    for key in REQUIRED_BOOLS:
        if not isinstance(prov.get(key), bool):
            problems.append(f"{rel}: provenance.{key} is not a boolean")

    if isinstance(prov.get("title_matches_archive"), bool):
        expected = doc.get("title") == prov.get("archive_title")
        if prov["title_matches_archive"] != expected:
            problems.append(
                f"{rel}: provenance.title_matches_archive is "
                f"{prov['title_matches_archive']} but title == archive_title is {expected}")
    if isinstance(prov.get("date_matches_repo"), bool):
        expected = doc.get("date") == prov.get("archive_date")
        if prov["date_matches_repo"] != expected:
            problems.append(
                f"{rel}: provenance.date_matches_repo is "
                f"{prov['date_matches_repo']} but date == archive_date is {expected}")

    own = _package_doi(doc)
    arch = prov.get("archive_doi")
    if own and arch and isinstance(arch, str) and own != arch.strip():
        problems.append(f"{rel}: provenance.archive_doi {arch!r} is not this "
                        f"package's DOI {own!r}")
    return problems


def scan(root: str = REPO) -> tuple[list[str], dict[str, str]]:
    """Return (problems, doi -> directory) for every paper package."""
    problems: list[str] = []
    papers = os.path.join(root, "docs", "papers", "efc")
    by_doi: dict[str, str] = {}
    if not os.path.isdir(papers):
        return [f"{papers}: no such directory"], by_doi
    for name in sorted(os.listdir(papers)):
        if name in SKIP_TOP:
            continue
        full = os.path.join(papers, name)
        if not os.path.isdir(full):
            continue
        meta_path = os.path.join(full, "metadata.json")
        rel = os.path.relpath(meta_path, root)
        if not os.path.isfile(meta_path):
            continue
        try:
            with open(meta_path, encoding="utf-8") as fh:
                doc = json.load(fh)
        except (OSError, ValueError) as e:
            problems.append(f"{rel}: unreadable — {e}")
            continue
        problems.extend(check_metadata(doc, rel))
        if isinstance(doc, dict) and isinstance(doc.get("provenance"), dict):
            doi = _package_doi(doc)
            if doi:
                by_doi[doi] = name
    return problems, by_doi


def check_registered(by_doi: dict[str, str]) -> list[str]:
    return [f"{doi}: no package carries a provenance block for it — "
            f"measured deviation unregistered ({why})"
            for doi, why in sorted(REGISTERED.items()) if doi not in by_doi]


def check(root: str = REPO) -> list[str]:
    problems, by_doi = scan(root)
    return problems + check_registered(by_doi)


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for doi, why in sorted(REGISTERED.items()):
            print(f"{doi}  — {why}")
        return 0
    problems = check()
    for p in problems:
        print(f"[efc-provenance] {p}")
    if problems:
        print(f"[efc-provenance] FAIL — {len(problems)} problem(s)")
        return 1
    _, by_doi = scan()
    print(f"[efc-provenance] OK — {len(by_doi)} registered provenance block(s), "
          f"{len(REGISTERED)} required DOI(s) present")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
