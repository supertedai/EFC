#!/usr/bin/env python3
"""
EFC Repository Maintenance Orchestrator

Runs the full keep-it-fresh sequence:

  1. efc_gen_ai_friendly.py   — regenerate ai_manifest.json + catalogue
  2. efc_sync_dois.py --apply — propagate DOIs through every paper's
                                 in-package files (index.json,
                                 metadata.json, CITATION.cff,
                                 citations.bib, *.jsonld) and sync
                                 efc_index.json + evidence-register.json
                                 + ledger.json empirical lists.
  3. efc_gen_ai_friendly.py   — re-run so ai_manifest reflects any
                                 byte-size changes from step 2.
  4. efc_verify.py            — consistency + language + evidence + DOI
                                 invariant checks (C1–C8).

Exit code:
  0  — clean (or only warnings)
  1  — errors found

Meant to be invoked by:
  - The .claude/settings.json SessionStart hook
  - CI (.github/workflows/efc-verify.yml + .github/workflows/efc-sync.yml)
  - Manually: `python3 scripts/maintenance/efc_maintain.py`
"""
from __future__ import annotations
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AUTO_META = os.path.join(HERE, "efc_auto_metadata.py")
GEN = os.path.join(HERE, "efc_gen_ai_friendly.py")
SYNC = os.path.join(HERE, "efc_sync_dois.py")
VERIFY = os.path.join(HERE, "efc_verify.py")
DRIFT = os.path.join(HERE, "efc_drift_detector.py")


def run(script: str, *args: str) -> int:
    print(f"[efc-maintain] running {os.path.basename(script)} {' '.join(args)}…")
    res = subprocess.run([sys.executable, script, *args])
    return res.returncode


def main() -> int:
    print("[efc-maintain] --- EFC maintenance pass ---")
    # Step 0: auto-generate metadata for bare PDFs (uploaded without index.json)
    run(AUTO_META)
    rc_gen = run(GEN)
    if rc_gen != 0:
        print(f"[efc-maintain] generator failed (rc={rc_gen})")
        return rc_gen
    rc_sync = run(SYNC, "--apply")
    if rc_sync not in (0, 1):  # 1 = conflicts; still continue to verify
        print(f"[efc-maintain] sync errored (rc={rc_sync})")
    # Re-run generator so ai_manifest picks up any byte-size diffs
    rc_gen2 = run(GEN)
    if rc_gen2 != 0:
        print(f"[efc-maintain] generator (post-sync) failed (rc={rc_gen2})")
        return rc_gen2
    rc_verify = run(VERIFY)
    # Step 5: auto-fix drift (paper counts in README/AGENTS/Changelog)
    rc_drift = run(DRIFT, "--fix")
    status = "clean" if rc_verify == 0 and rc_sync == 0 else "issues"
    print(f"[efc-maintain] --- done ({status}) ---")
    # Return the worst of the three, capped at 1
    return 1 if (rc_verify != 0 or rc_sync != 0) else 0


if __name__ == "__main__":
    sys.exit(main())
