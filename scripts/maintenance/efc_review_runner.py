#!/usr/bin/env python3
"""efc_review_runner.py — review-flow orchestrator (VALIDATOR-ONLY).

Authority boundary. This runner plans a review run and REFUSES on
incompleteness. It never authors a finding, a disposition, a claim_status, or
a verdict — those are reviewer output (roles 1-9) and the human gate. The
binding refusal remains `efc_review_gate.py release`; this runner is the
RUN-STAGE companion that lets a review be planned and checked for the nine
roles and the ten gates before the release gate is ever consulted.

Usage:
    efc_review_runner.py plan <slug>            emit a deterministic run plan
    efc_review_runner.py snapshot <run_id>      freeze snapshot.tex from the live manuscript
    efc_review_runner.py check <run_id>         refuse unless all nine roles delivered
                                                and the claim-gate matrix is complete

Exit 0 = the check passes; non-zero = a one-line refusal on stderr.
Pure stdlib, no Hermes dependency, English-only output (the language gate).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ROLES_PATH = ROOT / "docs" / "validation-ledger" / "review_roles.json"
GATES_PATH = ROOT / "docs" / "validation-ledger" / "gates.json"


def _reviews_dir() -> Path:
    """Read at call time so tests can point EFC_REVIEWS_DIR at a temp dir —
    the same discipline as efc_review_gate.py and efc_findings_index.py."""
    return Path(os.environ.get("EFC_REVIEWS_DIR",
                               ROOT / "docs" / "validation-ledger" / "reviews"))

ROUNDS = [
    ("blind", "round 1, roles 1-8, run in parallel without each other's findings"),
    ("adversarial", "round 2, one fresh Advocate and one Attacker rebuttal each"),
    ("synthesis", "round 3, meta-reviewer (role 9) synthesises, never writes status"),
]


def _roles() -> list[str]:
    """The nine reviewer roles, read from review_roles.json (ONE source)."""
    data = json.loads(ROLES_PATH.read_text(encoding="utf-8"))
    roles = data.get("roles", {})
    if not roles:
        raise SystemExit("review_roles.json has no roles")
    return sorted(roles.keys())


def _gates() -> list[int]:
    """The ten gate identities, read from gates.json (ONE source)."""
    data = json.loads(GATES_PATH.read_text(encoding="utf-8"))
    return [g["id"] for g in data.get("gates", [])]


def _run_dir(run_id: str) -> Path:
    d = _reviews_dir() / run_id
    if not d.is_dir():
        raise SystemExit(f"no review directory '{run_id}' under {_reviews_dir()}")
    return d


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _slug_dir(slug: str) -> Path:
    d = ROOT / "docs" / "papers" / "efc" / slug
    if not d.is_dir():
        raise SystemExit(f"no manuscript package for slug '{slug}'")
    return d


def plan(slug: str) -> int:
    """Emit a deterministic run plan; print the run id. Mutates nothing but the
    plan file. The run id is a hash of the manuscript bytes so re-planning the
    same snapshot is idempotent."""
    roles = _roles()
    gates = _gates()
    pkg = _slug_dir(slug)
    tex = pkg / f"{slug}.tex"
    if not tex.exists():
        raise SystemExit(f"no manuscript at {tex}")
    run_id = "deleg_" + _sha(tex)[:8]

    plan_doc = {
        "run_id": run_id,
        "slug": slug,
        "manuscript": f"docs/papers/efc/{slug}/{slug}.tex",
        "method_revision": "v2",
        "rounds": [{"name": n, "description": d} for n, d in ROUNDS],
        "roles": roles,
        "gates": gates,
        "note": (
            "This runner plans and checks structure only. Reviewer findings, "
            "dispositions and claim_status are written by the nine roles and "
            "the human gate — never by this tool."
        ),
    }
    d = _reviews_dir() / run_id
    d.mkdir(parents=True, exist_ok=True)
    (d / "plan.json").write_text(json.dumps(plan_doc, indent=2) + "\n", encoding="utf-8")
    print(f"run planned: {run_id} (roles={len(roles)}, gates={gates})")
    return 0


def snapshot(run_id: str) -> int:
    """Freeze the live manuscript into snapshot.tex and record its hash in plan.json."""
    d = _run_dir(run_id)
    plan_path = d / "plan.json"
    if not plan_path.exists():
        raise SystemExit(f"{d.name} has no plan.json (run 'plan' first)")
    pdoc = json.loads(plan_path.read_text(encoding="utf-8"))
    live = ROOT / pdoc["manuscript"]
    if not live.exists():
        raise SystemExit(f"live manuscript missing: {live}")
    snap = _sha(live)
    (d / "snapshot.tex").write_bytes(live.read_bytes())
    pdoc["snapshot_sha256"] = snap
    plan_path.write_text(json.dumps(pdoc, indent=2) + "\n", encoding="utf-8")
    print(f"snapshot frozen: {snap}")
    return 0


def check(run_id: str) -> int:
    """Refuse unless the run directory carries all nine roles and a complete
    claim-gate matrix. Validator-only, fail-closed: a missing verdict is a
    refusal, never an 'expected' pass. Delegates to efc_review_gate's
    check_roles_and_gates so the run stage and the release stage are the SAME
    authority — no second, weaker copy that can drift."""
    d = _run_dir(run_id)
    vp = d / "verdict.json"
    if not vp.exists():
        print("REFUSED: verdict.json missing — review run not complete", file=sys.stderr)
        return 1
    try:
        v = json.loads(vp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print("REFUSED: verdict.json is not valid JSON", file=sys.stderr)
        return 1

    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    import efc_review_gate as gate_mod

    ok, reason = gate_mod.check_roles_and_gates(v, vp)
    if not ok:
        print(f"REFUSED: {reason}", file=sys.stderr)
        return 1
    print(f"ok: {run_id} structurally complete (9 roles, 10 gates closed)")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="EFC review-flow orchestrator (validator-only)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("plan", help="emit a deterministic run plan")
    sp.add_argument("slug")
    ss = sub.add_parser("snapshot", help="freeze snapshot.tex from the live manuscript")
    ss.add_argument("run_id")
    sc = sub.add_parser("check", help="refuse unless all nine roles delivered")
    sc.add_argument("run_id")
    args = ap.parse_args(argv)

    if args.cmd == "plan":
        return plan(args.slug)
    if args.cmd == "snapshot":
        return snapshot(args.run_id)
    if args.cmd == "check":
        return check(args.run_id)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
