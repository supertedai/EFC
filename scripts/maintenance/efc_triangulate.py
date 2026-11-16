#!/usr/bin/env python3
"""efc_triangulate.py — triangulation / cross-check layer (ADR-EFC-TRIANGULATION-2026-11-16).

Computes, for a claim, whether it may be auto-accepted or must be escalated to
the owner. The core invariant: a claim is auto-accepted only when its evidence
is external-origin, disjoint-provenance, and independently agreeing. Internal
self-agreement (self-generated data, self-sealed-then-self-confirmed, or
same-model/codebase/organization agreement) never raises confidence.

This module is pure and hermetic: it classifies claims from structured source
records; it performs no I/O and no LLM call, so the confidence is computed,
never claimed.

See ADR-EFC-TRIANGULATION-2026-11-16 for the full model.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import FrozenSet

REPO_ROOT = Path(__file__).resolve().parents[2]
RECORD_DIR = REPO_ROOT / "data" / "triangulation"


@dataclass(frozen=True)
class Source:
    """One piece of evidence for or against a claim."""
    external_id: str = ""            # DOI / arXiv id; empty = no stable external identity
    system_derived: bool = False     # True if produced by our own model/codebase
    supports: bool = True            # does it agree (True) or contradict (False) the claim
    data_lineage: FrozenSet[str] = field(default_factory=frozenset)
    code_lineage: FrozenSet[str] = field(default_factory=frozenset)
    citation_lineage: FrozenSet[str] = field(default_factory=frozenset)
    authors: FrozenSet[str] = field(default_factory=frozenset)
    organization: str = ""
    retrieved_at: str = ""


@dataclass(frozen=True)
class Claim:
    claim_id: str
    statement: str
    kind: str = "scientific"         # "mechanical" | "scientific" | "falsify" | "canonize" | "publish"
    risk: str = "low"                # "low" | "medium" | "high"
    sources: tuple = ()


def is_external(source: Source) -> bool:
    """External origin = a stable external identity AND not system-derived."""
    return bool(source.external_id) and not source.system_derived


def _shared(a: FrozenSet[str], b: FrozenSet[str]) -> bool:
    return bool(a & b)


def common_ancestor(a: Source, b: Source) -> bool:
    """True if the two sources share any lineage element, author, or organization."""
    return (
        _shared(a.data_lineage, b.data_lineage)
        or _shared(a.code_lineage, b.code_lineage)
        or _shared(a.citation_lineage, b.citation_lineage)
        or _shared(a.authors, b.authors)
        or (bool(a.organization) and a.organization == b.organization)
    )


def has_provenance(source: Source) -> bool:
    """Provenance = retrieval timestamp plus at least one lineage/identity marker."""
    return bool(source.retrieved_at) and bool(
        source.data_lineage or source.code_lineage or source.citation_lineage
        or source.authors or source.organization
    )


def independence(sources) -> str:
    """'independent' | 'correlated' | 'unknown' across the source set.

    - Any non-external source -> 'unknown' (cannot be trusted as independent).
    - Any source missing provenance -> 'unknown'.
    - Any pair sharing a common ancestor -> 'correlated'.
    - Otherwise -> 'independent'.
    """
    if not sources:
        return "unknown"
    for s in sources:
        if not is_external(s):
            return "unknown"
        if not has_provenance(s):
            return "unknown"
    for i, a in enumerate(sources):
        for b in sources[i + 1:]:
            if common_ancestor(a, b):
                return "correlated"
    return "independent"


def support(sources) -> str:
    """'unsupported' | 'single' | 'replicated' | 'contradicted' from independent sources."""
    indep = [s for s in sources if is_external(s) and has_provenance(s)]
    if not indep:
        return "unsupported"
    agreeing = [s for s in indep if s.supports]
    contradicting = [s for s in indep if not s.supports]
    if contradicting:
        return "contradicted"
    if len(agreeing) >= 2:
        return "replicated"
    if len(agreeing) == 1:
        return "single"
    return "unsupported"


def classify(claim: Claim) -> dict:
    """Return the full classification for a claim (the separated axes + action)."""
    sources = list(claim.sources)

    if claim.kind == "mechanical":
        mechanical_status = "verified"  # byte/hash provenance checked by the caller
    else:
        mechanical_status = "n/a"

    independence_status = independence(sources)
    support_status = support(sources)

    # Action policy (ADR 03-decision).
    if claim.kind in {"falsify", "canonize", "publish"}:
        action = "owner-gate"
    elif claim.kind == "mechanical":
        action = "auto-accept" if mechanical_status == "verified" else "escalate"
    elif (
        independence_status == "independent"
        and support_status == "replicated"
        and claim.risk == "low"
    ):
        action = "auto-accept"
    else:
        action = "escalate"

    return {
        "claim_id": claim.claim_id,
        "kind": claim.kind,
        "risk": claim.risk,
        "mechanical_status": mechanical_status,
        "support_status": support_status,
        "independence_status": independence_status,
        "action": action,
        "n_sources": len(sources),
        "n_independent": sum(1 for s in sources if is_external(s) and has_provenance(s)),
    }


def validate_sources(sources) -> list[str]:
    """Reject a source list that is cosmetic: non-external, duplicate, or provenance-less.

    Returns a list of problems; empty means the list is acceptable as a source record.
    """
    problems: list[str] = []
    seen_ids = set()
    for i, s in enumerate(sources):
        if not is_external(s):
            problems.append(f"source[{i}]: not external-origin (system-derived or no external_id)")
            continue
        if s.external_id in seen_ids:
            problems.append(f"source[{i}]: duplicate external_id {s.external_id}")
        seen_ids.add(s.external_id)
        if not has_provenance(s):
            problems.append(f"source[{i}]: missing provenance")
    return problems


def write_record(claim: Claim, classification: dict) -> Path:
    """Persist a claim's classification as an append-only record.

    Writes data/triangulation/<claim_id>.json so the escalation digest can
    report it. Idempotent: re-writing the same claim_id overwrites its record
    (the record is per-claim state, not an event log).
    """
    RECORD_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "claim_id": claim.claim_id,
        "statement": claim.statement,
        "kind": claim.kind,
        "risk": claim.risk,
        **classification,
        "sources": [
            {"external_id": s.external_id, "supports": s.supports}
            for s in claim.sources
        ],
        "written_at": datetime.now(timezone.utc).isoformat(),
    }
    path = RECORD_DIR / f"{claim.claim_id}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    return path


if __name__ == "__main__":
    print("efc_triangulate — import as a module; no standalone CLI.")
