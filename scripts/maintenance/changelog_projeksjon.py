#!/usr/bin/env python3
"""changelog_projeksjon — deterministic changelog projection from git history.

Principle (P0 t_26dd0ef5): the changelog is a PROJECTION of one canonical
source, never an alternative truth. The canonical source is the git history —
it is unlosable, append-only, and contains everything that actually changed —
while logs/activity.jsonl annotates it (change_id/kanban_card) where present.

Regeneration is deterministic: given last_processed_sha (stored in
changelog.json) and HEAD, this script always produces the same output.
The CI gate (efc-changelog-sync.yml) runs the script and FAILS if the
committed changelog diverges — so the changelog is de facto updated in the
same PR that changes public HTML, or CI goes red.

Language rule (Morten 2026-09-17): ALL EFC repo content is English.
Summaries are projected verbatim from commit messages, so commit messages
must be English too — the CI gate enforces this on new entries.

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

# High-precision Norwegian stopwords (avoids English false positives like
# "for", "den", "det"). Two or more hits = Norwegian content.
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


def _fil_kategori(f: str) -> str:
    """Covers the WHOLE tree — the changelog must reflect every area."""
    if f.startswith("docs/public/"):
        return "public_pages"
    if f.startswith("docs/papers/"):
        return "papers"
    if f.startswith("docs/validation-ledger/"):
        return "ledger_data"
    if f.startswith("public/graph/"):
        return "statement_graph"
    if f.startswith("public/page-meta/"):
        return "page_meta"
    if f.startswith("schemas/"):
        return "schemas"
    if f.startswith("scripts/"):
        return "scripts"
    if f.startswith(".github/workflows/"):
        return "workflows"
    if f.startswith("config/"):
        return "config"
    if f.startswith("governance/"):
        return "governance"
    if f.startswith("evidence/"):
        return "evidence"
    if f.startswith("tests/"):
        return "tests"
    if f.startswith("efc_inference/") or f.startswith("src/"):
        return "code"
    if f.startswith("logs/activity.jsonl"):
        return "activity_log"
    return "other"


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
            kategorier[k] = kategorier.get(k, 0) + 1
        commits.append({"sha": sha, "dato": dato[:10], "melding": melding,
                        "kategorier": kategorier})
    commits.reverse()  # eldste først
    return commits


def _hoved() -> int:
    if not os.path.exists(JSON):
        raise SystemExit("changelog.json mangler")
    with open(JSON, encoding="utf-8") as f:
        cl = json.load(f)

    siste = (cl.get("metadata") or {}).get("last_processed_sha") or ""
    commits = _hent_commits(siste)
    if not commits:
        print("changelog_projeksjon: ingen nye commits siden siste projeksjon")
        return 0

    nye = []
    for c in commits:
        kat = ", ".join(f"{k}:{v}" for k, v in sorted(c["kategorier"].items()))
        nye.append({
            "date": c["dato"],
            "sha": c["sha"][:12],
            "summary": c["melding"][:140],
            "categories": c["kategorier"],
            "id": c["sha"][:12],
        })
    eksisterende = cl.get("changes", [])
    kjente_ider = {e.get("id") or e.get("sha") for e in eksisterende}
    friske = [c for c in nye if c["id"] not in kjente_ider]
    cl["changes"] = friske + eksisterende
    cl.setdefault("metadata", {})["last_processed_sha"] = commits[-1]["sha"]
    cl.setdefault("metadata", {})["generated_at"] = datetime.now(timezone.utc).isoformat()
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(cl, f, ensure_ascii=False, indent=2)

    # HTML: nye <li> øverst i lista, deterministisk
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

    print(f"changelog_projeksjon: {len(nye)} nye endringer projisert "
          f"(siste: {commits[-1]['sha'][:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_hoved())
