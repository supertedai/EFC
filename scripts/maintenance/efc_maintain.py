#!/usr/bin/env python3
"""
EFC Repository Maintenance Orchestrator

Runs the full keep-it-fresh sequence:

  1. efc_gen_ai_friendly.py   — regenerate ai_manifest.json + catalogue
  2. efc_verify.py            — consistency + language + evidence checks

Exit code:
  0  — clean (or only warnings)
  1  — errors found

Meant to be invoked by:
  - The .claude/settings.json SessionStart hook
  - CI (.github/workflows/efc-verify.yml)
  - Manually: `python3 scripts/maintenance/efc_maintain.py`
"""
from __future__ import annotations
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
GEN = os.path.join(HERE, "efc_gen_ai_friendly.py")
VERIFY = os.path.join(HERE, "efc_verify.py")


def run(script: str, *args: str) -> int:
    print(f"[efc-maintain] running {os.path.basename(script)} …")
    res = subprocess.run([sys.executable, script, *args])
    return res.returncode


def main() -> int:
    print("[efc-maintain] --- EFC maintenance pass ---")
    rc_gen = run(GEN)
    if rc_gen != 0:
        print(f"[efc-maintain] generator failed (rc={rc_gen})")
        return rc_gen
    rc_verify = run(VERIFY)
    status = "clean" if rc_verify == 0 else "issues"
    print(f"[efc-maintain] --- done ({status}) ---")
    return rc_verify


if __name__ == "__main__":
    sys.exit(main())
