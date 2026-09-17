#!/usr/bin/env python3
"""validate_repo.py — mappe- og filstruktur, navnekonvensjoner, forbudte filer.

Bygger på invariantene i AGENTS.md («Repository invariants») og designet §2.
Fase 1: kjente rot-mapper må finnes; maskinlesbare filer i public/graph,
public/page-meta og public/candidates følger kebab-case; forbudte filer
avvises hardt; store binærfiler avvises; UTF-8 på alle tekstfiler.

Bruk: python3 scripts/maintenance/validate_repo.py [--json]
Exit: 0 = OK, 1 = harde feil.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]

PAALAGTE_MAPPER = ["docs", "evidence", "efc_inference", "scripts", "tests",
                   "schemas", "public/graph", "public/page-meta", "public/candidates"]
FORBUDTE_NAVN = re.compile(r"(\.env$|token|secret|\.pem$|\.key$|\.DS_Store$|"
                           r"credentials)", re.IGNORECASE)
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.(yaml|yml|json|jsonl|md)$")
INSID = re.compile(r"^INS-[0-9a-f]{8,}\.(yaml|yml)$")
MAKS_BINÆR = 5 * 1024 * 1024


def sjekk() -> list[dict]:
    feil: list[dict] = []
    for m in PAALAGTE_MAPPER:
        if not (ROT / m).is_dir():
            feil.append({"type": "missing_dir", "msg": f"{m} mangler"})
    for rot, prefix in ((ROT / "public" / "graph", "public/graph/"),
                        (ROT / "public" / "page-meta", "public/page-meta/"),
                        (ROT / "public" / "candidates", "public/candidates/")):
        if not rot.is_dir():
            continue
        for p in rot.rglob("*"):
            if not p.is_file():
                continue
            rel = f"{prefix}{p.relative_to(rot)}"
            if FORBUDTE_NAVN.search(p.name):
                feil.append({"type": "forbidden_file", "msg": rel})
            if p.stat().st_size > MAKS_BINÆR:
                feil.append({"type": "oversized_file", "msg": rel})
            if p.suffix.lower() in (".yaml", ".yml", ".json", ".jsonl", ".md"):
                if prefix.startswith("public/candidates"):
                    if not INSID.match(p.name):
                        feil.append({"type": "non_insid_name", "msg": rel,
                                     "forventet": "INS-<hex>.yaml"})
                elif not KEBAB.match(p.name):
                    feil.append({"type": "non_kebab_name", "msg": rel})
                try:
                    p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    feil.append({"type": "non_utf8", "msg": rel})
    # forbudte filer i hele repoet (utenom .git/.worktrees)
    for p in ROT.rglob("*"):
        if not p.is_file() or ".git" in p.parts or ".worktrees" in p.parts:
            continue
        if FORBUDTE_NAVN.search(p.name):
            feil.append({"type": "forbidden_file", "msg": str(p.relative_to(ROT))})
    return feil


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    feil = sjekk()
    if a.json:
        print(json.dumps({"feil": feil}, ensure_ascii=False, indent=1))
    else:
        print(f"repo-contract: {len(feil)} feil")
        for f in feil[:20]:
            print("  ", f)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
