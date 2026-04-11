#!/usr/bin/env python3
"""
efc_maintain.py — [PHASE2_STAGED] Phase 2 full maintenance orchestrator.

⚠️  STAGED. Chains four destructive/incompatible children. See
    scripts/maintenance/phase2/README.md.  ⚠️

Runs the complete Phase 2 pipeline in order:
  1. efc_gen_ai_friendly.py  — scan papers, extract DOIs/results
  2. efc_sync_dois.py --apply — update ledger.json, auto-tick checkboxes
  3. efc_render_ledger.py    — regenerate HTML from updated ledger.json
  4. efc_gen_ai_friendly.py  — convergence re-scan
  5. efc_verify.py           — Phase 2 C1–C8 invariants

Every child script has its own --i-know-this-is-staged guard; this
orchestrator forwards the flag. Refuses to run without it.
"""

from __future__ import annotations
import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS_DIR = Path(__file__).parent


def run_step(name: str, script: str, args: list) -> int:
    cmd = [sys.executable, str(SCRIPTS_DIR / script)] + args
    print(f"\n{'=' * 60}")
    print(f"  STEP: {name}")
    print(f"  CMD:  {' '.join(cmd)}")
    print(f"{'=' * 60}\n")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT))
    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="[PHASE2_STAGED] Full maintenance pass")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--i-know-this-is-staged", action="store_true")
    args = parser.parse_args()

    if not args.i_know_this_is_staged:
        print(
            "ERROR: This is a PHASE 2 STAGED orchestrator.",
            file=sys.stderr,
        )
        print(
            "       It chains four children that would overwrite paper "
            "metadata and the live HTML.",
            file=sys.stderr,
        )
        print(
            "       See scripts/maintenance/phase2/README.md.",
            file=sys.stderr,
        )
        print(
            "       Pass --i-know-this-is-staged to confirm you understand.",
            file=sys.stderr,
        )
        sys.exit(2)

    forward = ["--root", str(args.root), "--i-know-this-is-staged"]
    errors = []

    rc = run_step("Generate manifests + extract", "efc_gen_ai_friendly.py", forward)
    if rc != 0:
        errors.append(f"efc_gen_ai_friendly.py failed (rc={rc})")

    rc = run_step("Sync DOIs → update ledger", "efc_sync_dois.py", ["--apply"] + forward)
    if rc != 0:
        errors.append(f"efc_sync_dois.py failed (rc={rc})")

    rc = run_step("Render HTML", "efc_render_ledger.py", forward)
    if rc != 0:
        errors.append(f"efc_render_ledger.py failed (rc={rc})")

    run_step("Re-scan (convergence)", "efc_gen_ai_friendly.py", forward)

    rc = run_step("Verify C1–C8", "efc_verify.py", forward)
    if rc != 0:
        errors.append(f"efc_verify.py found issues (rc={rc})")

    print(f"\n{'=' * 60}")
    print("  PHASE 2 MAINTENANCE SUMMARY")
    print(f"{'=' * 60}")
    if errors:
        print(f"\n⚠️  {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    else:
        print("\n✅ All steps completed.")


if __name__ == "__main__":
    main()
