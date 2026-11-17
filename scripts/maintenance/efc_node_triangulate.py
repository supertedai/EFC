#!/usr/bin/env python3
"""efc_node_triangulate.py — cross-node change-reconciliation picture.

Reads several stores ("source families") and emits one report on what changed,
what drifts, what is open, and what must be fixed. Read-only: it reports,
never auto-accepts, escalates, or writes.

Design: .hermes/plans/efc_node_triangulering.md (v2, after second opinion).

Two distinct concepts, kept separate on purpose:

1. INVARIANT check (v1, wired) — "does the healthy state hold?" Three states:
   ok (holds) / drift (violated) / unknown (telemetry unavailable). These are
   consistency and threshold checks, NOT independent confirmation.

2. CONFIRMATION (classify, tested, not yet wired) — "is a change real across
   independent sources?" Four states: confirmed (>=2 independent families
   attest the same exact value) / pending (single-family, in-flight) /
   drift (two families disagree) / unknown (unmeasured). This layers over the
   multihop change records that land in a later iteration.

classify() and the invariant checks are pure/hermetic; the probes do the I/O.
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, FrozenSet, Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parents[2]


# --- confirmation (4-state) — for the future multihop change layer ---

class Verdict(str, Enum):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    DRIFT = "drift"
    UNKNOWN = "unknown"


# --- invariant (3-state) — what v1 actually reports ---

class InvariantVerdict(str, Enum):
    OK = "ok"
    DRIFT = "drift"
    UNKNOWN = "unknown"


# Source families -> lineage id. Two families are INDEPENDENT only when their
# lineage ids differ. Same lineage = same underlying source replicated
# (e.g. two git clones of one repo), which confirms nothing on its own.
LINIAGE: Dict[str, str] = {
    "git-clone": "git",
    "forge": "git-forge",
    "kanban": "kanban",
    "working-memory": "working-memory",
    "publication": "publication",
    "public-surface": "public-surface",
}


@dataclass(frozen=True)
class Observation:
    """One store's attestation about one fact (key)."""
    family: str          # must be a key in LINIAGE
    key: str             # the fact identifier, e.g. "efc-clone-head"
    value: str           # the exact value asserted (SHA, normalized set hash, status)
    exact: bool = True   # False = inferred/candidate match, never a confirmed value
    ts: str = ""


def _exact_values(obs: Iterable[Observation]) -> List[str]:
    return sorted({o.value for o in obs if o.exact})


def check_consistency(obs: Iterable[Observation]) -> InvariantVerdict:
    """All observations must attest the SAME exact value (set-identity)."""
    vals = _exact_values(obs)
    if not vals:
        return InvariantVerdict.UNKNOWN
    if len(vals) >= 2:
        return InvariantVerdict.DRIFT
    return InvariantVerdict.OK


def check_threshold(obs: Iterable[Observation], expected: str) -> InvariantVerdict:
    """The healthy value must equal `expected`."""
    vals = _exact_values(obs)
    if not vals:
        return InvariantVerdict.UNKNOWN
    if len(vals) != 1 or vals[0] != expected:
        return InvariantVerdict.DRIFT
    return InvariantVerdict.OK


def classify(observations: Iterable[Observation],
             lineage: Dict[str, str] = LINIAGE) -> Verdict:
    """4-state confirmation. Rules (order matters):
    - no exact observations                    -> UNKNOWN
    - >=2 distinct exact values                -> DRIFT (disagreement)
    - one value, >=2 independent lineages      -> CONFIRMED
    - one value, <2 independent lineages       -> PENDING (in-flight / single-source)
    """
    obs = [o for o in observations if o.family in lineage and o.exact]
    if not obs:
        return Verdict.UNKNOWN
    values: Dict[str, List[Observation]] = {}
    for o in obs:
        values.setdefault(o.value, []).append(o)
    if len(values) >= 2:
        return Verdict.DRIFT
    the_value = next(iter(values))
    lineages = {lineage[o.family] for o in values[the_value]}
    return Verdict.CONFIRMED if len(lineages) >= 2 else Verdict.PENDING


# --------------------------------------------------------------------------
# Probes (I/O). Each returns Observations; empty = unmeasured (unknown).
# --------------------------------------------------------------------------

EFC_CLONES: List[Path] = [
    Path("/home/morten/EFC"),
    Path("/opt/agent-work/EFC"),
]


def _git_head(repo: Path) -> Optional[str]:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=repo,
            capture_output=True, text=True, timeout=10,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def probe_git_clones() -> List[Observation]:
    """Each clone's HEAD. Disagreement across clones = replication lag (drift)."""
    obs: List[Observation] = []
    for repo in EFC_CLONES:
        head = _git_head(repo)
        if head:
            obs.append(Observation(
                family="git-clone", key="efc-clone-head",
                value=head, exact=True, ts=str(repo),
            ))
    return obs


def probe_working_memory() -> List[Observation]:
    """Working-memory noise count. Healthy value = 0."""
    try:
        sys.path.insert(0, "/opt/hermes-opus")
        import arbeidsminne
        stoy = arbeidsminne.stoy()
        doors = sorted({s.get("kode", "?") for s in stoy})
        return [Observation(
            family="working-memory", key="working-memory-noise",
            value=str(len(stoy)), exact=True, ts=",".join(doors) if doors else "",
        )]
    except Exception:
        return []  # unmeasured -> UNKNOWN


def probe_kanban() -> List[Observation]:
    """Active cards (ready/blocked/review/running) with no owner. Healthy = 0.

    Uses the root kanban.db (single authoritative index). Triage cards are
    deliberately excluded: a triage card legitimately has no owner yet (it is
    waiting to be claimed), so it is not drift.
    """
    db = "/opt/hermes-tavle/kanban.db"
    try:
        c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        n = c.execute(
            "SELECT COUNT(*) FROM tasks WHERE status IN ('ready','blocked','review','running','in_progress') "
            "AND (assignee IS NULL OR assignee='')"
        ).fetchone()[0]
        c.close()
    except Exception:
        return []
    return [Observation(
        family="kanban", key="kanban-unowned",
        value=str(n), exact=True,
    )]


def _doi_set_fingerprint(dois: Iterable[str]) -> str:
    import hashlib
    norm = sorted({i.strip().lower().rstrip("/") for i in dois if i})
    return hashlib.sha256("\x00".join(norm).encode()).hexdigest()


def _repo_doi_fingerprint() -> Optional[str]:
    """DOI set from figshare/doi-map.json -> papers[].doi."""
    p = REPO_ROOT / "figshare" / "doi-map.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        dois = {r["doi"] for r in d.get("papers", []) if r.get("doi")}
        return _doi_set_fingerprint(dois) if dois else None
    except (OSError, json.JSONDecodeError):
        return None


def _orcid_doi_fingerprint() -> Optional[str]:
    """DOI set from .claude/orcid_cache.json -> works[].dois (list)."""
    p = REPO_ROOT / ".claude" / "orcid_cache.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        dois = set()
        for w in d.get("works", []):
            if isinstance(w, dict):
                for x in w.get("dois", []) or []:
                    dois.add(x)
        return _doi_set_fingerprint(dois) if dois else None
    except (OSError, json.JSONDecodeError):
        return None


def probe_doi() -> List[Observation]:
    """Published DOI set identity: repo catalog vs ORCID cache."""
    obs: List[Observation] = []
    fp = _repo_doi_fingerprint()
    if fp:
        obs.append(Observation(
            family="publication", key="doi-set", value=fp, exact=True, ts="doi-map",
        ))
    fp2 = _orcid_doi_fingerprint()
    if fp2:
        obs.append(Observation(
            family="publication", key="doi-set", value=fp2, exact=True, ts="orcid-cache",
        ))
    return obs


# --------------------------------------------------------------------------
# Picture assembly
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Fact:
    key: str
    description: str
    verdict: str
    detail: str = ""


def build_picture() -> Dict:
    facts: List[Fact] = []

    def add_consistency(key, desc, obs):
        v = check_consistency(obs)
        detail = ""
        if v == InvariantVerdict.DRIFT:
            detail = f"disagree: {len(_exact_values(obs))} distinct values"
        elif v == InvariantVerdict.UNKNOWN:
            detail = "telemetry unavailable"
        facts.append(Fact(key, desc, v.value, detail))

    def add_threshold(key, desc, obs, expected):
        v = check_threshold(obs, expected)
        detail = ""
        if v == InvariantVerdict.DRIFT:
            vals = _exact_values(obs)
            detail = f"expected {expected}, observed {vals[0] if vals else '?'}"
        elif v == InvariantVerdict.UNKNOWN:
            detail = "telemetry unavailable"
        facts.append(Fact(key, desc, v.value, detail))

    add_consistency("efc-clone-head", "all EFC clones agree on HEAD", probe_git_clones())
    add_threshold("working-memory-noise", "working-memory noise == 0 per door", probe_working_memory(), "0")
    add_threshold("kanban-unowned", "every active card has an owner", probe_kanban(), "0")
    add_consistency("doi-set", "repo DOI set == ORCID DOI set", probe_doi())

    buckets = {"ok": [], "drift": [], "unknown": []}
    for f in facts:
        buckets[f.verdict].append({"key": f.key, "description": f.description, "detail": f.detail})
    return {
        "schema_version": "node-triangulate/1",
        "families": LINIAGE,
        "buckets": buckets,
        "facts": [
            {"key": f.key, "description": f.description, "verdict": f.verdict, "detail": f.detail}
            for f in facts
        ],
    }


def main(argv: List[str]) -> int:
    picture = build_picture()
    if "--json" in argv:
        print(json.dumps(picture, ensure_ascii=False, indent=2))
    else:
        print("EFC node-triangulation picture:")
        for f in picture["facts"]:
            print(f"  [{f['verdict']:>7}] {f['key']}: {f['description']}"
                  + (f" ({f['detail']})" if f["detail"] else ""))
    verdicts = {f["verdict"] for f in picture["facts"]}
    if "drift" in verdicts:
        return 2
    if "unknown" in verdicts:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
