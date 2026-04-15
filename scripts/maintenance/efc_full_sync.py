#!/usr/bin/env python3
"""
EFC Full Sync — event-driven, fixpoint-converging repo synchroniser.

This is the new orchestrator that implements the general algorithm:

    1. Snapshot current `State`
    2. Classify diff vs HEAD~1 → list[Change]
    3. Topological sort → dispatch to typed handlers
    4. Regenerate derived files (ai_manifest, ai_friendly_index, HTML, …)
    5. Re-snapshot. If diff != ∅, loop (max 5 iterations).
    6. Verify §1–§31 invariants.
    7. If all ERROR-severity checks pass → exit 0; else exit 1.

It does NOT replace efc_maintain.py — it runs alongside it. Both are
idempotent so running both back-to-back is safe (but redundant).

Entry points:
    python3 scripts/maintenance/efc_full_sync.py            # normal
    python3 scripts/maintenance/efc_full_sync.py --dry-run  # snapshot+verify only
    python3 scripts/maintenance/efc_full_sync.py --verify   # invariants only
"""
from __future__ import annotations

import argparse
import sys

from sync_engine.classify import classify_git_diff, classify_state_diff, topological_sort
from sync_engine.derived import regenerate_all
from sync_engine.handlers import dispatch
from sync_engine.invariants import SEVERITY_ERROR, verify_all
from sync_engine.state import State

MAX_ITER = 5


def _print_changes(changes, prefix="[full-sync]") -> None:
    if not changes:
        print(f"{prefix} no changes detected")
        return
    print(f"{prefix} {len(changes)} change(s):")
    for ch in changes:
        print(f"  • {ch.type}  {ch.payload or ''}")


def _print_violations(violations) -> int:
    err = sum(1 for v in violations if v.severity == SEVERITY_ERROR)
    warn = len(violations) - err
    print(f"[full-sync] invariants: {err} error(s), {warn} warning(s)")
    for v in violations:
        print(f"  {v}")
    return err


def run_sync(dry_run: bool = False, verify_only: bool = False) -> int:
    if verify_only:
        state = State.snapshot()
        violations = verify_all(state)
        return 0 if _print_violations(violations) == 0 else 1

    pre = State.snapshot()
    git_changes = classify_git_diff()
    state_changes = classify_state_diff(None, pre)
    initial = topological_sort(git_changes + state_changes)
    _print_changes(initial, prefix="[full-sync] initial:")

    if dry_run:
        violations = verify_all(pre)
        return 0 if _print_violations(violations) == 0 else 1

    # Fixpoint loop
    prev_state = pre
    for it in range(1, MAX_ITER + 1):
        print(f"[full-sync] --- iteration {it} ---")
        if it == 1:
            changes = initial
        else:
            changes = topological_sort(classify_state_diff(prev_state, State.snapshot()))
        _print_changes(changes)

        if all(c.type == "T15_NOOP" for c in changes):
            print("[full-sync] converged (only NOOP changes)")
            break

        touched = dispatch(changes)
        if touched:
            print(f"[full-sync] handlers touched: {sum(len(v) for v in touched.values())} surface(s)")

        regenerate_all()

        curr_state = State.snapshot()
        if curr_state == prev_state:
            print("[full-sync] converged (state stable)")
            break
        prev_state = curr_state
    else:
        print(f"[full-sync] WARNING: no convergence after {MAX_ITER} iterations")

    final_state = State.snapshot()
    print(f"[full-sync] final state: {final_state.n_paper_dirs} papers · "
          f"{final_state.n_ai_friendly} ai-friendly · "
          f"{final_state.total_public_tests} tests")

    violations = verify_all(final_state)
    err_count = _print_violations(violations)
    return 0 if err_count == 0 else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="Classify + verify without running handlers")
    ap.add_argument("--verify", action="store_true",
                    help="Only run invariants on current state")
    args = ap.parse_args()
    return run_sync(dry_run=args.dry_run, verify_only=args.verify)


if __name__ == "__main__":
    sys.exit(main())
