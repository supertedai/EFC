#!/usr/bin/env python3
"""efc_review_gate.py — fail-closed release gate for EFC claim promotion.

Authority. Pure stdlib, no Hermes dependency: this script and the review
artifacts in git are what decide whether a manuscript may proceed to DOI
reservation or publication. Hermes skills and the Figshare MCP are THIN
CALLERS — they invoke this script and MUST treat a non-zero exit as a hard
refusal. A Hermes update that removes a skill cannot weaken this gate.

Usage:
    efc_review_gate.py release <slug> --confirmed-by morten

Exit code is the contract:
  0           the manuscript has a frozen v2 (or later) verdict that is
              structurally closed, snapshot-verified, human-gated (via a
              SEPARATE human_gate.json — the frozen verdict is never mutated),
              and every promoted claim is grounded in a non-opinion evidence
              layer -> release may proceed.
  non-zero    refused; a one-line reason is printed to stderr.

Fail-closed by construction: any missing or malformed condition is a refusal,
never a pass. The method_revision check is numeric (>= v2), NOT equality — a
future v3 protocol must not break the gate.

Why human_gate is a SEPARATE artifact: the verdict.json is the frozen
meta-reviewer output. A human disposing inside it would mutate frozen reviewer
words — the exact cascade this system exists to prevent. So the human's
binding disposition lives in human_gate.json beside the verdict, and this gate
reads both. The verdict stays immutable; the human gate is separately tracked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

MIN_REVISION = 2
REQUIRED_CONFIRMED_BY = "morten"

# Layers that can ground a promotion, split by the user's own decomposition:
# the measurer/instrument/proxy ARE paradigm-laden (borrowed from ΛCDM/GR), so
# INSTRUMENT and PROXY ground ONLY when the finding also carries an atlas_field
# — the bias-audit (gate 7) is shown by pointing at the measurement chain
# (measure.proxy_chain etc.), not left implicit. Raw signal, target, normative,
# derived and external evidence ground directly.
DIRECT_GROUNDING_LAYERS = {
    "RAW_SIGNAL", "TARGET", "NORMATIVE", "DERIVED", "EXTERNAL",
}
PARADIGM_LADEN_GROUNDING_LAYERS = {"INSTRUMENT", "PROXY"}

PROMOTED_STATUSES = {"declared_derived", "declared_companion_upgrade"}


def _reviews_dir() -> Path:
    """Read at call time so tests can point EFC_REVIEWS_DIR at a temp dir."""
    return Path(os.environ.get("EFC_REVIEWS_DIR", ROOT / "docs" / "validation-ledger" / "reviews"))


def _repo_root() -> Path:
    """Read at call time so tests can point EFC_REPO_ROOT at a temp tree."""
    return Path(os.environ.get("EFC_REPO_ROOT", ROOT))


def _rev_number(rev: object) -> int:
    m = re.match(r"^v(\d+)$", str(rev or ""))
    return int(m.group(1)) if m else -1


def _slug_matches(slug: str, manuscript: object) -> bool:
    """Directory-component match, not substring — a slug is a path component."""
    parts = str(manuscript or "").replace("\\", "/").split("/")
    return slug in parts


def _find_verdicts() -> list[Path]:
    d = _reviews_dir()
    if not d.is_dir():
        return []
    return sorted(d.glob("deleg_*/verdict.json"))


def _load(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


ROLES_PATH = ROOT / "docs" / "validation-ledger" / "review_roles.json"
GATES_PATH = ROOT / "docs" / "validation-ledger" / "gates.json"


def _required_roles() -> list[str]:
    """The nine reviewer roles, from review_roles.json (ONE source)."""
    data = _load(ROLES_PATH)
    roles = (data or {}).get("roles", {})
    return sorted(roles.keys())


def _required_gates() -> list[int]:
    """The ten gate identities, from gates.json (ONE source)."""
    data = _load(GATES_PATH)
    return [g["id"] for g in (data or {}).get("gates", [])
            if isinstance(g, dict) and isinstance(g.get("id"), int)]


def check_roles_and_gates(v: dict, vp: Path) -> tuple[bool, str]:
    """Refuse unless all nine reviewer roles delivered a finding AND a
    claim-gate matrix covers every claim with all ten gates, bound to the exact
    verdict. Shared by gate_manuscript (release) and the runner's check (run
    stage) — ONE authority, not two.

    Any open gate on ANY claim is a refusal: the ten gates must be closed for
    the WHOLE verdict before a manuscript reaches the DOI stage, not only for
    promoted claims.
    """
    findings = [f for f in v.get("findings", []) if isinstance(f, dict)]
    required_roles = _required_roles()
    if not required_roles:
        return False, "review_roles.json has no roles (cannot verify the nine reviewers)"
    roles_present = {f.get("reviewer_role") for f in findings}
    missing_roles = [r for r in required_roles if r not in roles_present]
    if missing_roles:
        return False, f"missing reviewer_role(s): {', '.join(missing_roles)}"
    unknown_roles = sorted(r for r in roles_present if r not in required_roles and r)
    if unknown_roles:
        return False, f"unknown reviewer_role(s): {', '.join(unknown_roles)}"

    matrix_path = vp.parent / "claim_gate_matrix.json"
    if not matrix_path.exists():
        return False, "claim_gate_matrix.json missing beside verdict.json (the ten gates are not proven per claim)"
    m = _load(matrix_path)
    if m is None:
        return False, "claim_gate_matrix.json is not readable JSON"
    if m.get("verdict_id") != v.get("verdict_id"):
        return False, "claim_gate_matrix.verdict_id does not match the verdict"
    if m.get("verdict_sha256") != _sha256(vp):
        return False, "claim_gate_matrix.verdict_sha256 does not match the verdict it binds to"

    gates_needed = _required_gates()
    if not gates_needed:
        return False, "gates.json has no gates (cannot verify the ten gates)"
    claim_ids = [cv.get("claim_id") for cv in v.get("claim_verdicts", []) if isinstance(cv, dict)]
    rows = {row.get("claim_id"): row for row in m.get("matrix", []) if isinstance(row, dict)}

    # exact claim coverage: no missing row, no row for an unknown claim
    for cid in claim_ids:
        if cid not in rows:
            return False, f"claim '{cid}' has no claim-gate matrix row"
    extra = [cid for cid in rows if cid not in claim_ids]
    if extra:
        return False, f"claim-gate matrix has row(s) for unknown claim(s): {', '.join(map(str, extra))}"

    for cid in claim_ids:
        row = rows[cid]
        gate_entries = [g for g in row.get("gates", []) if isinstance(g, dict)]
        gids = [g.get("gate_id") for g in gate_entries]
        if len(gids) != len({g for g in gids}):
            return False, f"claim '{cid}' has duplicate gate entries"
        entries = {g.get("gate_id"): g for g in gate_entries}
        for g in gates_needed:
            if g not in entries:
                return False, f"claim '{cid}' missing gate {g}"
        for gid, entry in entries.items():
            if gid not in gates_needed:
                return False, f"claim '{cid}' has unknown gate {gid}"
            status = entry.get("status")
            if status == "satisfied":
                if not entry.get("evidence"):
                    return False, f"claim '{cid}' gate {gid} is satisfied but has no evidence"
            elif status == "not_applicable":
                if not entry.get("reason"):
                    return False, f"claim '{cid}' gate {gid} is not_applicable but has no reason"
            elif status == "open":
                return False, f"claim '{cid}' has an open gate ({gid})"
            else:
                return False, f"claim '{cid}' gate {gid} has unknown status '{status}'"
            role = entry.get("reviewer_role")
            if role and role not in required_roles:
                return False, f"claim '{cid}' gate {gid} has unknown reviewer_role '{role}'"

    return True, "roles and gates closed"


def gate_manuscript(slug: str, confirmed_by: str, run_id: str | None = None) -> tuple[bool, str]:
    """Return (ok, reason) for releasing the manuscript whose slug is given.

    run_id (e.g. "deleg_7f3e9a1c") narrows candidates to one review directory
    when several v2 verdicts exist for the same slug.
    """

    if confirmed_by != REQUIRED_CONFIRMED_BY:
        return False, f"confirmed_by must be '{REQUIRED_CONFIRMED_BY}' (got '{confirmed_by}')"

    candidates = []
    for vp in _find_verdicts():
        v = _load(vp)
        if v and _slug_matches(slug, v.get("manuscript", "")):
            if run_id is not None and vp.parent.name != run_id:
                continue
            candidates.append((vp, v))

    if not candidates:
        return False, f"no verdict found for manuscript slug '{slug}'"

    best_rev = max(_rev_number(v.get("method_revision", "")) for _, v in candidates)
    at_best = [c for c in candidates if _rev_number(c[1].get("method_revision", "")) == best_rev]
    if len(at_best) > 1:
        names = ", ".join(c[0].parent.name for c in at_best)
        return False, (
            f"ambiguous: multiple v{best_rev} verdicts for slug '{slug}' "
            f"({names}); select a run-id explicitly"
        )
    vp, v = at_best[0]

    rev = _rev_number(v.get("method_revision", ""))
    if rev < MIN_REVISION:
        return False, (
            f"method_revision '{v.get('method_revision')}' < v{MIN_REVISION} "
            f"(frozen pilot history, not a release gate)"
        )

    findings = v.get("findings", [])
    if not findings:
        return False, "verdict has no findings"

    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            return False, f"finding {i} is not an object"
        if not f.get("disposition"):
            fid = f.get("finding_id", "?")
            return False, f"finding {i} ({fid}) has no closed disposition"

    snap = v.get("snapshot_sha256")
    if not snap:
        return False, "snapshot_sha256 missing (cannot verify what was reviewed)"
    snap_file = vp.parent / "snapshot.tex"
    if not snap_file.exists():
        return False, f"snapshot.tex missing in {vp.parent.name} (cannot verify the reviewed source)"
    if _sha256(snap_file) != snap:
        return False, "snapshot_sha256 does not match the review directory's snapshot.tex"

    # the LIVE manuscript must be byte-identical to the reviewed snapshot —
    # editing the source after review silently invalidates the verdict otherwise
    mpath = v.get("manuscript")
    if not mpath:
        return False, "verdict.manuscript path missing (cannot bind the review to the live source)"
    p = Path(str(mpath))
    if p.is_absolute() or ".." in p.parts:
        return False, f"verdict.manuscript '{mpath}' is not a repo-relative path (integrity boundary)"
    live = _repo_root() / p
    if not live.exists():
        return False, f"live manuscript '{mpath}' missing"
    if _sha256(live) != snap:
        return False, "live manuscript does not match the reviewed snapshot (source edited after review)"

    # human gate is a SEPARATE artifact — the frozen verdict is never mutated
    hg = _load(vp.parent / "human_gate.json")
    if not hg:
        return False, "human_gate.json missing (a human must dispose; agents cannot)"
    if not hg.get("status"):
        return False, "human_gate.status missing"
    if hg.get("status") != "approved":
        return False, "human_gate.status must be 'approved' (a human must dispose; 'rejected' cannot release)"
    if hg.get("confirmed_by") != REQUIRED_CONFIRMED_BY:
        return False, f"human_gate.confirmed_by must be '{REQUIRED_CONFIRMED_BY}'"
    if not hg.get("at"):
        return False, "human_gate.at missing"
    if hg.get("verdict_id") != v.get("verdict_id"):
        return False, "human_gate.verdict_id does not match the verdict it disposes"
    if hg.get("method_revision") != v.get("method_revision"):
        return False, "human_gate.method_revision does not match the verdict"
    if hg.get("verdict_sha256") != _sha256(vp):
        return False, "human_gate.verdict_sha256 does not match the verdict it binds to"

    approved = hg.get("approved_claims") or []

    # precedence: a promoted claim must be approved AND grounded in a non-opinion layer
    for cv in v.get("claim_verdicts", []):
        if not isinstance(cv, dict):
            continue
        status = cv.get("claim_status")
        if status not in PROMOTED_STATUSES:
            continue
        cid = cv.get("claim_id", "?")
        if cid not in approved:
            return False, f"promoted claim '{cid}' is not in human_gate.approved_claims"
        grounded = False
        for f in findings:
            if not (isinstance(f, dict) and f.get("claim_id") == cid):
                continue
            if f.get("supports_or_attacks") != "supports":
                continue
            if f.get("disposition") != "accepted":
                continue
            layer = f.get("evidence_layer")
            if layer in DIRECT_GROUNDING_LAYERS:
                grounded = True
                break
            if layer in PARADIGM_LADEN_GROUNDING_LAYERS and f.get("atlas_field"):
                grounded = True
                break
        if not grounded:
            return False, (
                f"claim '{cid}' is promoted ({status}) but has no grounding "
                f"support layer (consensus is not evidence; INSTRUMENT/PROXY "
                f"grounding requires an atlas_field bias-audit)"
            )

    # 9-role + 10-gate completeness — ONE authority (check_roles_and_gates),
    # shared with the runner's run-stage check. Any open gate on ANY claim is a
    # refusal here, not only on promoted claims.
    ok, reason = check_roles_and_gates(v, vp)
    if not ok:
        return False, reason

    return True, f"ok: {vp} rev={v.get('method_revision')}"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Fail-closed release gate for EFC claim promotion."
    )
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("release", help="gate a manuscript for DOI reservation/publication")
    r.add_argument("slug", help="manuscript slug (package directory name)")
    r.add_argument("--confirmed-by", required=True, help="authorizing identity")
    r.add_argument("--run-id", default=None, help="narrow to one review directory when several exist")
    args = ap.parse_args(argv)

    if args.cmd == "release":
        ok, reason = gate_manuscript(args.slug, args.confirmed_by, args.run_id)
        if ok:
            print(reason)
            return 0
        print(f"REFUSED: {reason}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
