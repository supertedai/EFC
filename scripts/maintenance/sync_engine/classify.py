"""
Diff classification.

Compares two `State` snapshots (or working tree vs HEAD~1) and emits
a list of typed `Change` events that handlers can dispatch on.

Detection signals are intentionally simple — when uncertain, classify
as the more general type and let the handler decide what to do.
"""
from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from typing import Iterable

from .state import REPO, State


# Change-type identifiers (must stay in sync with handlers/__init__.py)
T1_NEW_PAPER         = "T1_NEW_PAPER"
T2_PAPER_METADATA    = "T2_PAPER_METADATA"
T3_FALSIFICATION     = "T3_FALSIFICATION"
T4_GAP_CLOSURE       = "T4_GAP_CLOSURE"
T5_NEW_HYPOTHESIS    = "T5_NEW_HYPOTHESIS"
T6_PARAMETER_UPDATE  = "T6_PARAMETER_UPDATE"
T7_DATASET_RELEASE   = "T7_DATASET_RELEASE"
T8_INFERENCE_REFRESH = "T8_INFERENCE_REFRESH"
T9_VERSION_BUMP      = "T9_VERSION_BUMP"
T10_SEALED_PRED      = "T10_SEALED_PRED"
T11_STRUCTURAL       = "T11_STRUCTURAL"
T12_PIPELINE_PLANNED = "T12_PIPELINE_PLANNED"
T13_DRIFT_FIX        = "T13_DRIFT_FIX"
T14_DATE_ROLLOVER    = "T14_DATE_ROLLOVER"
T15_NOOP             = "T15_NOOP"


@dataclass
class Change:
    type: str
    payload: dict
    source: str = "diff"

    def __repr__(self) -> str:
        return f"Change({self.type}, {list(self.payload.keys())})"


def _git_diff_files(rev_from: str, rev_to: str) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", REPO, "diff", "--name-only", rev_from, rev_to],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []
    return [ln for ln in out.splitlines() if ln.strip()]


def _git_status_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-C", REPO, "status", "--porcelain"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError:
        return []
    files = []
    for ln in out.splitlines():
        if len(ln) > 3:
            files.append(ln[3:].strip())
    return files


def classify_state_diff(prev: State, curr: State) -> list[Change]:
    """Type-classify based on snapshot deltas only."""
    changes: list[Change] = []
    diff = prev.diff(curr) if prev else {f: (None, getattr(curr, f)) for f in curr.__dataclass_fields__}

    # New papers — DOIs added to the working tree
    new_dois = curr.paper_dois - (prev.paper_dois if prev else frozenset())
    for doi in sorted(new_dois):
        changes.append(Change(T1_NEW_PAPER, {"doi": doi}))

    # Drift: derived counts disagree with canonical paper count
    if curr.n_ai_friendly is not None and curr.n_ai_friendly != curr.n_paper_dirs:
        changes.append(Change(T13_DRIFT_FIX, {
            "metric": "n_ai_friendly",
            "canonical": curr.n_paper_dirs,
            "observed": curr.n_ai_friendly,
        }))

    if curr.evidence_register_count and curr.doi_map_count and \
       abs(curr.evidence_register_count - len(curr.paper_dois)) > 5:
        changes.append(Change(T13_DRIFT_FIX, {
            "metric": "evidence_register_vs_paper_dois",
            "canonical": len(curr.paper_dois),
            "observed": curr.evidence_register_count,
        }))

    # Version bump
    if "public_version" in diff and diff["public_version"][0] is not None:
        changes.append(Change(T9_VERSION_BUMP, {
            "from": diff["public_version"][0],
            "to": diff["public_version"][1],
        }))

    # Internal version drift between ledger.json and index.md
    if curr.ledger_version and curr.index_md_version and \
       curr.ledger_version != curr.index_md_version:
        changes.append(Change(T13_DRIFT_FIX, {
            "metric": "internal_ledger_version",
            "canonical": curr.index_md_version,
            "observed": curr.ledger_version,
        }))

    if not changes:
        changes.append(Change(T15_NOOP, {}))

    return changes


def classify_git_diff(rev_from: str = "HEAD~1", rev_to: str = "HEAD") -> list[Change]:
    """Inspect git diff to add path-based change types snapshots can't see."""
    changes: list[Change] = []
    files = _git_diff_files(rev_from, rev_to) or _git_status_files()

    new_index_jsons = [
        f for f in files
        if f.startswith("docs/papers/efc/")
        and f.endswith("/index.json")
    ]
    for f in new_index_jsons:
        slug = f.split("/")[-2]
        changes.append(Change(T1_NEW_PAPER, {"slug": slug, "path": f}, source="git"))

    if any(f == "docs/validation-ledger/data/inference.json" for f in files):
        changes.append(Change(T8_INFERENCE_REFRESH, {}, source="git"))

    if any(f == "docs/validation-ledger/data/frontier-gaps.json" for f in files):
        changes.append(Change(T4_GAP_CLOSURE, {}, source="git"))

    if any(f == "codemeta.json" for f in files):
        changes.append(Change(T9_VERSION_BUMP, {}, source="git"))

    if any(f.startswith(".claude/dataset_scan_report") for f in files):
        changes.append(Change(T7_DATASET_RELEASE, {}, source="git"))

    return changes


def topological_sort(changes: Iterable[Change]) -> list[Change]:
    """Order: new_paper → metadata → version_bump → others → drift_fix last."""
    order = {
        T1_NEW_PAPER: 0,
        T2_PAPER_METADATA: 1,
        T9_VERSION_BUMP: 2,
        T10_SEALED_PRED: 3,
        T3_FALSIFICATION: 3,
        T4_GAP_CLOSURE: 3,
        T5_NEW_HYPOTHESIS: 3,
        T6_PARAMETER_UPDATE: 3,
        T8_INFERENCE_REFRESH: 3,
        T11_STRUCTURAL: 3,
        T12_PIPELINE_PLANNED: 3,
        T7_DATASET_RELEASE: 4,
        T14_DATE_ROLLOVER: 5,
        T13_DRIFT_FIX: 9,  # always last
        T15_NOOP: 10,
    }
    return sorted(changes, key=lambda c: order.get(c.type, 5))
