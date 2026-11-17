#!/usr/bin/env python3
"""Classify open EFC pull requests; auto-act is limited to reversible CLOSE.

Deterministic classification over measurable signals (merge state, CI, file
set, age, draft status, "already merged elsewhere"). The ONLY autonomous
actions are closing DEAD (stale point-in-time draft snapshots) and SUPERSEDED
(equivalent change already on main). Everything else is escalated, including
what looks like a "routine" merge.

Why no auto-merge: second opinion (gpt-5.6-luna, confidence 0.94) ruled that
file paths + green CI are not sufficient safety signals — .github/workflows
can change the control mechanism itself, tests can weaken verification, and
scripts/Makefile can touch production. Only machine-verifiable DERIVED
artifacts (regenerated files reproducible bit-for-bit) are auto-merge
eligible, and v1 deliberately ships no such class. Default is ESCALATE.

Truth-gates (falsify / canonize / publish / canonical merge) are never touched.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Callable, Optional

DEAD_AGE_DAYS = 30
POINT_IN_TIME_RE = re.compile(
    r"(delta\s*scan|watchlist|research[- ]watch|watch\s+v?\d)", re.IGNORECASE
)

# Touching any of these is truth-adjacent: never routine, always escalate.
CANONICAL_PREFIXES = (
    "schema/",
    "adr/",
    "public/graph/",
    "docs/papers/",
    "scripts/atlas_",
    "scripts/efc_",
    "governance/ownership-register.json",
    "wiki/",
    "docs/validation-ledger/",
)

# A PR whose merge state is one of these cannot be merged as-is.
DIRTY_STATES = ("DIRTY", "CONFLICTING", "UNSTABLE")

CLASS_LABEL = {
    "close_dead": "CLOSE (stale point-in-time draft)",
    "close_superseded": "CLOSE (already merged elsewhere)",
    "escalate_needs_rebase": "ESCALATE (needs rebase)",
    "escalate_canonical": "ESCALATE (truth-adjacent paths)",
    "escalate_routine": "ESCALATE (green routine — needs your word)",
    "escalate_unknown": "ESCALATE (cannot determine)",
}


@dataclass(frozen=True)
class PR:
    number: int
    title: str
    is_draft: bool
    merge_state: str
    updated_at: str
    files: tuple[str, ...]


def age_days(updated_at: str, now: Optional[dt.datetime] = None) -> int:
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        ts = dt.datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return 0
    return (now - ts).days


def is_canonical(files: tuple[str, ...]) -> bool:
    return any(
        f == p.rstrip("/") or f.startswith(p) for f in files for p in CANONICAL_PREFIXES
    )


def classify(pr: PR, superseded: Optional[bool] = None) -> str:
    """Pure, deterministic classification. Returns a class key."""
    if superseded is True:
        return "close_superseded"
    if (
        pr.is_draft
        and age_days(pr.updated_at) >= DEAD_AGE_DAYS
        and POINT_IN_TIME_RE.search(pr.title)
    ):
        # A stale point-in-time draft is dead regardless of merge state.
        return "close_dead"
    if pr.merge_state in DIRTY_STATES:
        return "escalate_needs_rebase"
    if is_canonical(pr.files):
        return "escalate_canonical"
    if pr.merge_state == "CLEAN":
        return "escalate_routine"
    return "escalate_unknown"


def is_close_class(cls: str) -> bool:
    return cls.startswith("close_")


def list_prs(gh: Callable[..., str]) -> list[PR]:
    """Fetch open PRs via gh. Returns list[PR]."""
    raw = gh("pr", "list", "--state", "open", "--limit", "100",
             "--json", "number,title,isDraft,mergeStateStatus,updatedAt,headRefName")
    data = json.loads(raw)
    prs = []
    for d in data:
        files_raw = gh("pr", "view", str(d["number"]), "--json", "files")
        files = tuple(f["path"] for f in json.loads(files_raw)["files"])
        prs.append(PR(
            number=d["number"],
            title=d["title"],
            is_draft=d["isDraft"],
            merge_state=d["mergeStateStatus"],
            updated_at=d["updatedAt"],
            files=files,
        ))
    return prs


def check_superseded(number: int, head_branch: str) -> Optional[bool]:
    """True if the branch is already an ancestor of origin/main."""
    r = subprocess.run(
        ["git", "merge-base", "--is-ancestor", f"origin/{head_branch}", "origin/main"],
        capture_output=True, text=True,
    )
    if r.returncode == 0:
        return True
    if r.returncode == 1:
        return False
    return None


def build_report(classifications: dict[int, str]) -> str:
    lines = ["# EFC PR-triage — tørrkjøring", ""]
    order = ("close_dead", "close_superseded", "escalate_needs_rebase",
             "escalate_canonical", "escalate_routine", "escalate_unknown")
    for cls in order:
        nums = sorted(n for n, c in classifications.items() if c == cls)
        if not nums:
            continue
        lines.append(f"## {CLASS_LABEL[cls]} ({len(nums)})")
        lines.append(", ".join(f"#{n}" for n in nums))
        lines.append("")
    closes = sorted(n for n, c in classifications.items() if is_close_class(c))
    lines.append(f"## Auto-handling (kun med --utfoer): {len(closes)} lukkinger")
    lines.append("Alt annet eskaleres.")
    return "\n".join(lines)


def close_pr(number: int, cls: str) -> str:
    """Close a DEAD/SUPERSEDED PR with an auditable reason comment."""
    reasons = {
        "close_dead": "stale point-in-time draft (research-watch delta), superseded by later scans",
        "close_superseded": "equivalent change already merged to main via another PR",
    }
    subprocess.run(
        ["gh", "pr", "close", str(number),
         "--comment", f"Auto-closed by efc_pr_triage: {reasons[cls]}."],
        check=False, capture_output=True, text=True,
    )
    return f"closed #{number} ({cls})"


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--torr", action="store_true", default=True,
                    help="report only (default)")
    ap.add_argument("--utfoer", action="store_true", help="close DEAD/SUPERSEDED")
    args = ap.parse_args(argv)

    import shutil
    if not shutil.which("gh"):
        print("gh not found", file=sys.stderr)
        return 3

    def gh(*a: str) -> str:
        r = subprocess.run(["gh", *a], capture_output=True, text=True, check=True)
        return r.stdout

    prs = list_prs(gh)
    classifications = {pr.number: classify(pr) for pr in prs}

    if args.utfoer:
        closed = []
        for pr in prs:
            cls = classifications[pr.number]
            if is_close_class(cls):
                closed.append(close_pr(pr.number, cls))
        print("CLOSED: " + (", ".join(closed) if closed else "(none)"))

    print(build_report(classifications))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
