#!/usr/bin/env python3
"""validate_repo.py — directory and file structure, naming conventions,
forbidden files.

Builds on the invariants in AGENTS.md ("Repository invariants") and design §2.
Phase 1: known root directories must exist; machine-readable files in
public/graph, public/page-meta and public/candidates follow kebab-case;
forbidden files are rejected hard; large binaries are rejected; UTF-8 on all
text files.

Usage: python3 scripts/maintenance/validate_repo.py [--json]
Exit: 0 = OK, 1 = hard errors.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# The sibling module sits next to this file, and the tool is loaded both as a
# script and via importlib from the tests — then the directory is not on
# sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _repo_tre import filer as _tre_filer  # noqa: E402

ROT = Path(__file__).resolve().parents[2]

PAALAGTE_MAPPER = ["docs", "evidence", "efc_inference", "scripts", "tests",
                   "schemas", "public/graph", "public/page-meta", "public/candidates"]
FORBUDTE_NAVN = re.compile(r"(\.env$|token|secret|\.pem$|\.key$|\.DS_Store$|"
                           r"credentials)", re.IGNORECASE)
KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*\.(yaml|yml|json|jsonl|md)$")
INSID = re.compile(r"^INS-[0-9a-f]{8,}\.(yaml|yml)$")
MAKS_BINÆR = 5 * 1024 * 1024


def sjekk(root: Path = ROT) -> list[dict]:
    feil: list[dict] = []
    for m in PAALAGTE_MAPPER:
        if not (root / m).is_dir():
            feil.append({"type": "missing_dir", "msg": f"{m} is missing"})
    for rot, prefix in ((root / "public" / "graph", "public/graph/"),
                        (root / "public" / "page-meta", "public/page-meta/"),
                        (root / "public" / "candidates", "public/candidates/")):
        if not rot.is_dir():
            continue
        for p in rot.rglob("*"):
            if not p.is_file() or p.is_symlink():  # symlinks are not followed
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
    # forbidden files in the whole repo — read the GIT TREE, not the disk.
    #
    # Measured 2026-10-05 (vedlikeholdsrunde): a disk walk answered with
    # `.venv/lib/python3.12/site-packages/packaging/_tokenizer.py` — gitignored
    # local state, present on disk, flagged as if it were committed. The rule
    # is the one `_repo_tre.py` establishes (kanban t_12494ba1): in a git tree
    # the answer is `git ls-files`, i.e. what is actually published, and it is
    # the same in all clones. A NEW file must be `git add`-ed before the tool
    # sees it; an untracked forbidden file is caught by the pre-commit gate,
    # not by this checker.
    for p in _tre_filer(root):
        if FORBUDTE_NAVN.search(p.name):
            feil.append({"type": "forbidden_file",
                         "msg": p.relative_to(root).as_posix()})
    return feil


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    feil = sjekk()
    if a.json:
        print(json.dumps({"feil": feil}, ensure_ascii=False, indent=1))
    else:
        print(f"repo-contract: {len(feil)} errors")
        for f in feil[:20]:
            print("  ", f)
    return 1 if feil else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
