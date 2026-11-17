#!/usr/bin/env python3
"""efc_selfheal.py — the autonomous self-validating loop.

Observe -> decide -> act, kept separate. Runs the node-triangulation picture,
auto-fixes ONLY the narrow safe case (own clone lag, ff-only, verified), and
escalates everything else. Never touches another door, never forces, never
auto-fixes publishing/DOI/merge/physics (human gate).

Design: .hermes/plans/efc_node_triangulering.md §12 (v3), after a second
opinion (gpt-5.6-luna, confidence 0.93). The panel's core correction:
"reversible" is NOT the gate — the gate is "bounded, authorized, independently
verifiable change to a known derived state, idempotent, recoverable". So the
auto-fix whitelist holds exactly ONE entry (own clone lag); the rest escalates.

Exit codes: 0 = no drift / all fixed, 2 = drift escalated (work for a human),
3 = unknown (telemetry unavailable). stdout is silent on clean (watchdog
pattern); non-empty only when something was fixed or escalated.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))  # so `scripts.maintenance` imports resolve standalone

from scripts.maintenance.efc_node_triangulate import build_picture, EFC_CLONES

# The ONLY auto-fix allowed: my own clone, fast-forward only, verified.
OWN_CLONE = Path("/home/morten/EFC")
TRUSTED_ORIGIN = "supertedai/EFC"


def _git(rev: str, cwd: Path) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "rev-parse", rev], cwd=cwd,
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _origin_url(cwd: Path) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "remote", "get-url", "origin"], cwd=cwd,
            capture_output=True, text=True, timeout=15,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def _fix_own_clone_lag() -> Dict:
    """Fast-forward my own clone to origin/main, verified. Fail-closed.

    Preconditions (all must hold, else fail-closed -> escalate):
    - clone is OWN_CLONE (owned by this agent)
    - origin is TRUSTED_ORIGIN (supertedai/EFC)
    - ff-only (never rewrites local history)
    Postcondition verified by read-back of HEAD against origin/main.
    """
    if not OWN_CLONE.exists():
        return {"ok": False, "reason": "own clone missing"}
    origin = _origin_url(OWN_CLONE)
    if not origin or TRUSTED_ORIGIN not in origin:
        return {"ok": False, "reason": f"untrusted origin: {origin}"}

    before = _git("HEAD", OWN_CLONE)
    remote = _git("refs/remotes/origin/main", OWN_CLONE)
    if before == remote:
        return {"ok": True, "action": "already-current", "before": before}

    # Save the prior HEAD for rollback before moving.
    try:
        r = subprocess.run(
            ["git", "pull", "--ff-only", "origin", "main"], cwd=OWN_CLONE,
            capture_output=True, text=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError) as e:
        return {"ok": False, "reason": f"pull failed: {e}"}
    if r.returncode != 0:
        return {"ok": False, "reason": f"pull non-ff/refused: {r.stderr.strip()[:120]}"}

    # Independent read-back: HEAD must now equal origin/main.
    after = _git("HEAD", OWN_CLONE)
    if after != remote:
        return {"ok": False, "reason": f"post-verify failed: HEAD={after} != origin/main={remote}"}

    return {"ok": True, "action": "fast-forwarded", "before": before, "after": after}


# The whitelist: fact key -> fix function. One entry, by design.
AUTO_FIX = {
    "efc-clone-head": _fix_own_clone_lag,
}


def selfheal() -> Dict:
    picture = build_picture()
    fixed: List[Dict] = []
    escalated: List[Dict] = []

    for fact in picture["facts"]:
        if fact["verdict"] != "drift":
            continue
        if fact["key"] in AUTO_FIX:
            result = AUTO_FIX[fact["key"]]()
            if result.get("ok"):
                fixed.append({"key": fact["key"], "detail": fact["detail"], **result})
            else:
                escalated.append({
                    "key": fact["key"], "detail": fact["detail"],
                    "reason": result.get("reason", "auto-fix failed"),
                })
        else:
            escalated.append({"key": fact["key"], "detail": fact["detail"]})

    return {"fixed": fixed, "escalated": escalated, "picture": picture}


def main(argv: List[str]) -> int:
    result = selfheal()
    fixed = result["fixed"]
    escalated = result["escalated"]

    # stdout: silent on clean (watchdog); non-empty only when there is work.
    lines: List[str] = []
    for f in fixed:
        lines.append(f"FIXED {f['key']}: {f.get('action', '')} ({f.get('before', '?')[:8]} -> {f.get('after', '?')[:8]})")
    for e in escalated:
        lines.append(f"ESCALATED {e['key']}: {e['detail']}"
                     + (f" ({e.get('reason', '')})" if e.get("reason") else ""))

    if "--json" in argv:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif lines:
        print("\n".join(lines))

    if escalated:
        return 2
    # unknown facts are not drift; report them only if asked
    unknowns = [f for f in result["picture"]["facts"] if f["verdict"] == "unknown"]
    if unknowns and "--json" not in argv and lines:
        print(f"UNKNOWN: {len(unknowns)} fact(s) unmeasured")
    if unknowns and not fixed and not escalated:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
