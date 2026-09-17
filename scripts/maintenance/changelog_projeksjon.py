#!/usr/bin/env python3
"""changelog_projeksjon — deterministisk changelog fra git-historikken.

Prinsippet (P0 t_26dd0ef5): changelogen er en PROJEKSJON av én kanonisk
kilde, aldri en alternativ sannhet. Kanonisk kilde er git-historikken —
den er utappelig, append-only og inneholder ALT som faktisk endret seg —
mens logs/activity.jsonl annoterer (change_id/kanban_card) der den finnes.

Regenerering er deterministisk: gitt last_processed_sha (lagret i
changelog.json) og HEAD, produserer dette skriptet alltid samme output.
CI-gaten (efc-changelog-sync.yml) kjører skriptet og FEILER hvis den
committede changelogen avviker — dermed blir changelogen de facto
oppdatert i samme PR som endrer public HTML, ellers rød CI.

Bruk:  python3 scripts/maintenance/changelog_projeksjon.py
"""
from __future__ import annotations

import json
import os
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


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       cwd=REPO, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} feilet: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def _fil_kategori(f: str) -> str:
    """Alle repo-områder — changelogen skal dekke HELE treet."""
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
    return "annet"


def _infra_bare(filer: list[str]) -> bool:
    """Endring som kun rører selve changelog-maskineriet trenger ingen oppføring."""
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
        # Changelog-lista ligger ETTER siste årstallsoverskrift — aldri
        # navigasjonens <ul> (første <ul> i fila er nav).
        anker = tekst.rfind("2026")
        ul = tekst.find("<ul>", anker) if anker > 0 else -1
        if ul < 0:
            raise SystemExit("EFC_Changelog.html mangler changelog-<ul>")
        tekst = tekst[:ul + 4] + "\n  " + li + tekst[ul + 4:]
    tekst = ensure_nav(tekst)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(tekst)

    print(f"changelog_projeksjon: {len(nye)} nye endringer projisert "
          f"(siste: {commits[-1]['sha'][:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_hoved())
