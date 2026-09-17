#!/usr/bin/env python3
"""changelog_projeksjon — deterministic PUBLIC changelog from git history.

Principle (P0 t_26dd0ef5 + Morten 2026-09-17): the PUBLIC changelog is a
PROJECTION of one canonical source — the git history — but ONLY of changes
relevant to the public pages, written for HUMANS (English, readable
summaries). Two atlases exist by design: the internal atlas (everything:
house, world, ocean/biosphere/volcano) and the public EFC atlas (cosmos).
This changelog belongs to the PUBLIC pages only; internal-atlas work never
appears here — it has its own changelog.

Regeneration is deterministic: given last_processed_sha (stored in
changelog.json) and HEAD, this script always produces the same output.
The CI gate (efc-changelog-sync.yml) runs the script and FAILS if the
committed changelog diverges — so the changelog is de facto updated in the
same PR that changes public HTML, or CI goes red.

Language rule (Morten 2026-09-17): ALL EFC public content is English —
summaries are cleaned commit subjects; Norwegian stopwords fail the gate.

Usage:  python3 scripts/maintenance/changelog_projeksjon.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _nav_helper import ensure_nav  # type: ignore
except ImportError:
    ensure_nav = lambda t: t  # noqa: E731

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HTML = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")
JSON = os.path.join(REPO, "docs", "validation-ledger", "data", "changelog.json")

# The changelog files THEMSELVES are side-effects, not public content: a
# commit whose only public-path touch is the changelog is internal work
# (the old generator wrote the changelog on every commit — that loop must
# not make internal commits "public-relevant").
CHANGELOG_SELV = {
    "docs/public/EFC_Changelog.html",
    "docs/validation-ledger/data/changelog.json",
}

# High-precision Norwegian stopwords (avoids English false positives like
# "for", "den", "det"). One or more hits = Norwegian content.
NORSKE_ORD = re.compile(
    r"\b(skal|ikke|v[æe]re|v[æe]rt|ble|har|som|med|og|forutsier|konsistent|"
    r"prediksjonen|målt|stor|negativ|også|etter|men|mot|fra|til|endret|"
    r"oppdatert|påkrevd|rettet|æ|ø|å)\b",
    re.I)


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       cwd=REPO, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def _fil_kategori(f: str) -> str | None:
    """PUBLIC-relevant categories only — changelog side-effects excluded.

    Two atlases exist BY DESIGN (Morten 2026-09-17): the internal atlas
    (everything: house, world, ocean/biosphere/volcano nodes) and the public
    EFC atlas (cosmos). The PUBLIC changelog is a projection of changes
    relevant to the PUBLIC pages ONLY. Returns None for internal paths.
    """
    if f in CHANGELOG_SELV:
        return None  # side-effect, not content
    if f.startswith("docs/public/"):
        return "public_pages"
    if f.startswith("docs/papers/"):
        return "papers"
    if f.startswith("docs/validation-ledger/"):
        return "ledger_data"
    if f.startswith("public/"):
        return "statement_graph"
    return None


def _ren_tekst(melding: str) -> str:
    """Human-readable: strip backslash-escapes that raw commit subjects can
    carry (e.g. 'fix\\(x\\)'), collapse whitespace."""
    s = re.sub(r"\\([()\\])", r"\1", melding)
    return " ".join(s.split())[:140]


def _infra_bare(filer: list[str]) -> bool:
    """A change touching ONLY the changelog machinery needs no entry."""
    infra = {
        "scripts/maintenance/changelog_projeksjon.py",
        ".github/workflows/efc-changelog-sync.yml",
        "docs/public/EFC_Changelog.html",
        "docs/validation-ledger/data/changelog.json",
    }
    return bool(filer) and all(f in infra for f in filer)


def _hent_commits(siden: str) -> list[dict]:
    ut = _git("log", "--no-merges", "--format=%H%x1f%aI%x1f%s%x1e",
              f"{siden}..HEAD") if siden else ""
    if not ut:
        return []
    commits = []
    for blokk in ut.split("\x1e"):
        blokk = blokk.strip()
        if not blokk:
            continue
        sha, dato, melding = blokk.split("\x1f", 2)
        filer = _git("show", "--name-only", "--format=", sha).split()
        if _infra_bare(filer):
            continue
        kategorier = {}
        for f in filer:
            k = _fil_kategori(f)
            if k:
                kategorier[k] = kategorier.get(k, 0) + 1
        if not kategorier:
            # No public-relevant file touched — internal-only change,
            # invisible on the public pages, so no changelog entry here.
            continue
        commits.append({"sha": sha, "dato": dato[:10],
                        "melding": _ren_tekst(melding), "kategorier": kategorier})
    commits.reverse()  # oldest first
    return commits


def _hoved() -> int:
    if not os.path.exists(JSON):
        raise SystemExit("changelog.json missing")
    with open(JSON, encoding="utf-8") as f:
        cl = json.load(f)

    siste = (cl.get("metadata") or {}).get("last_processed_sha") or ""
    if siste:
        # The stored SHA must be reachable — squash merges discard the
        # pre-squash commits, leaving an invalid revision range. Fall back
        # to the tip's parent instead of crashing.
        r = subprocess.run(["git", "merge-base", "--is-ancestor", siste, "HEAD"],
                           capture_output=True, cwd=REPO, timeout=30)
        if r.returncode != 0:
            siste = ""
    if not siste:
        # Empty or unreachable seed (legacy or interrupted regeneration):
        # start from the tip's parent so the projection is forward-looking
        # and deterministic.
        siste = _git("rev-parse", "HEAD~1")
    commits = _hent_commits(siste)
    if not commits:
        print("changelog_projeksjon: no new commits since last projection")
        return 0

    nye = []
    for c in commits:
        nye.append({
            "date": c["dato"],
            "sha": c["sha"][:12],
            "summary": c["melding"],
            "categories": c["kategorier"],
            "id": c["sha"][:12],
        })
    eksisterende = cl.get("changes", [])
    kjente_ider = {e.get("id") or e.get("sha") for e in eksisterende}
    friske = [c for c in nye if c["id"] not in kjente_ider]
    cl["changes"] = friske + eksisterende
    cl.setdefault("metadata", {})["last_processed_sha"] = commits[-1]["sha"]
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(cl, f, ensure_ascii=False, indent=2)

    # HTML: new <li> at the top of the changelog list, deterministic.
    with open(HTML, encoding="utf-8") as f:
        tekst = f.read()
    for c in nye:
        li = (f'<li><strong>{c["date"]}</strong> &mdash; {c["summary"]} '
              f'<span style="color:#6b7f9e;">({c["id"]})</span></li>')
        if li in tekst:
            continue
        # The changelog list sits AFTER the year heading — never in the
        # navigation's <ul> (the first <ul> in the file is the nav).
        anker = tekst.find("<h2>202")
        ul = tekst.find("<ul>", anker) if anker > 0 else -1
        if ul < 0:
            raise SystemExit("EFC_Changelog.html missing changelog <ul>")
        tekst = tekst[:ul + 4] + "\n  " + li + tekst[ul + 4:]
    tekst = ensure_nav(tekst)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(tekst)

    print(f"changelog_projeksjon: {len(friske)} new changes projected "
          f"(last: {commits[-1]['sha'][:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_hoved())
