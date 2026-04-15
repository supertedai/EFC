"""
Derived-file regenerators.

After handlers touch canonical sources, this module rebuilds every
consumer file in topological order. All work is delegated to existing
scripts/maintenance/efc_*.py tools — this layer is just the wiring +
ordering contract.

Order matters: ai_friendly_index → stats → ecosystem → HTML pages →
README/AGENTS/llms.txt aggregation.
"""
from __future__ import annotations

import os
import subprocess
import sys

from .state import REPO

SCRIPTS = os.path.join(REPO, "scripts", "maintenance")


def _run(script: str, *args: str) -> int:
    path = os.path.join(SCRIPTS, script)
    if not os.path.exists(path):
        return 0
    res = subprocess.run([sys.executable, path, *args], cwd=REPO)
    return res.returncode


def regenerate_all() -> None:
    """Run the regeneration chain in topological order."""
    # Level 1 — per-paper bytes + catalogue
    _run("efc_gen_ai_friendly.py")
    # Level 1 — per-paper DOI propagation (idempotent)
    _run("efc_sync_dois.py", "--apply")
    # Level 2 — autofill missing Ledger + Changelog rows
    _run("efc_ledger_autofill.py")
    # Level 2 — drift fix (paper counts in README/AGENTS/llms.txt)
    _run("efc_drift_detector.py", "--fix")
    # Level 3 — Symbiose snapshot from ledger
    _run("efc_symbiose_snapshot.py", "--from-ledger")
    # Level 3 — auto-changelog stamp
    _run("efc_auto_changelog.py")
