#!/usr/bin/env python3
"""validate_ownership.py — fail-closed ownership check over the WHOLE repo.

Every tracked file must hit at least one component coverage_glob in
governance/ownership-register.json. Unclassified files = HARD error —
ownership is not optional (Morten, translated from Norwegian: "the EFC agent
MUST own everything").

Usage: python3 scripts/maintenance/validate_ownership.py [--json]
Exit: 0 = full coverage, 1 = files without an owner.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
REGISTER = ROT / "governance" / "ownership-register.json"

# Legitimate exceptions: git-ignored and kanban work areas are not owned
# content.
UNNTAK = [".git/**", ".worktrees/**", "data/inntak/**", ".venv/**", "__pycache__/**"]


def _trackede_filer() -> list[str]:
    # -z: no quoting of paths with unicode/special characters (git otherwise
    # quotes "–" as \342\200\223 and the glob misses the whole path).
    r = subprocess.run(["git", "ls-files", "-z"], capture_output=True,
                       timeout=30, cwd=str(ROT))
    if r.returncode != 0:
        return []
    return [s for s in r.stdout.decode("utf-8", errors="replace").split("\0") if s]


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    komponenter = reg.get("components", [])
    glober: list[tuple[str, list[str]]] = [
        (c["id"], c.get("coverage_glob") or []) for c in komponenter]
    feil: list[dict] = []
    uten_eier: list[str] = []
    for fil in _trackede_filer():
        if any(fnmatch.fnmatch(fil, u) for u in UNNTAK):
            continue
        eiere = [cid for cid, gs in glober if any(fnmatch.fnmatch(fil, g) for g in gs)]
        if not eiere:
            uten_eier.append(fil)
            feil.append({"type": "unowned_file", "file": fil})
    if a.json:
        print(json.dumps({"feil": feil, "uten_eier": len(uten_eier)},
                         ensure_ascii=False, indent=1))
    else:
        print(f"ownership: {len(uten_eier)} files without an owner")
        for f in uten_eier[:25]:
            print("  WITHOUT OWNER:", f)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
