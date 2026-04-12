#!/usr/bin/env python3
"""
ledger_schema.py — Canonical schema and helpers for the future
docs/validation-ledger/ledger.json single-source-of-truth model.

STATUS: Phase 2 scaffold. This module is installed in the main
maintenance directory because it is a pure data model with no side
effects — importing it cannot break anything. It is consumed by the
Phase 2 rewritten scripts that currently live under
``scripts/maintenance/phase2/`` and are not yet active.

When ledger.json becomes the canonical authority (future migration),
this module will power:

  - All validation entries (tests, constraints, diagnostics)
  - Their status (planned, completed, passed, failed, etc.)
  - Checkbox ticks (✅🟡🔴⚪🔵) per sector (EFC-S, EFC-D, EFC-C, ΛCDM)
  - DOI references (Figshare, arXiv)
  - Tier classification (T1–T4)
  - Regime tags (L0–L3, ξ/η)

Until then it is imported only by the Phase 2 staging scripts and by
efc_ai_monitor.py, both of which handle its absence gracefully.

Pure stdlib — no external dependencies.
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class Status(str, Enum):
    """Validation maturity levels — must match Section 0.1 of the ledger."""

    STAGE_NONREJECTABLE = "stage_nonrejectable"
    CONSISTENT_ROBUST = "consistent_robust"
    CONSISTENT_PRELIMINARY = "consistent_preliminary"
    COMPLETED_LIKELIHOOD = "completed_likelihood"
    COMPLETED_CONSISTENCY = "completed_consistency"
    COMPLETED_STRUCTURAL = "completed_structural"
    PHENOMENOLOGICAL = "phenomenological"
    FRAMEWORK_DIAGNOSTIC = "framework_diagnostic"
    PLANNED_READY = "planned_ready"
    CONCEPTUAL = "conceptual"
    DISCREPANT = "discrepant"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    FALSIFIED = "falsified"


class Tier(str, Enum):
    """Validation tier — T1 strongest, T4 diagnostic-only."""

    T1 = "T1"  # Joint-likelihood
    T2 = "T2"  # Single-probe likelihood
    T3 = "T3"  # Structural / analytical
    T4 = "T4"  # Framework diagnostic
    NONE = ""   # Not yet assigned (planned tests)


STATUS_EMOJI = {
    Status.STAGE_NONREJECTABLE: "🔵",
    Status.CONSISTENT_ROBUST: "✅",
    Status.CONSISTENT_PRELIMINARY: "🟡",
    Status.COMPLETED_LIKELIHOOD: "🟢",
    Status.COMPLETED_CONSISTENCY: "🟢",
    Status.COMPLETED_STRUCTURAL: "🟢",
    Status.PHENOMENOLOGICAL: "🟡",
    Status.FRAMEWORK_DIAGNOSTIC: "🟡",
    Status.PLANNED_READY: "🔵",
    Status.CONCEPTUAL: "🔵",
    Status.DISCREPANT: "🔴",
    Status.INACTIVE: "⚪",
    Status.DEPRECATED: "⚪",
    Status.FALSIFIED: "🔴",
}

SECTOR_MARK = {
    "supported": "✅",
    "inactive": "⚪",
    "discrepant": "❌",
    "tension": "⚠️",
    "na": "—",
}


@dataclass
class ValidationEntry:
    """One row in the validation ledger."""

    # Identity
    id: str
    phenomenon: str
    section: str = "main"

    # Classification
    status: str = Status.PLANNED_READY
    tier: str = Tier.NONE
    category: str = ""

    # Regime
    regime_L0: str = "na"
    regime_L1: str = "na"
    regime_L2: str = "na"
    regime_L3: str = "na"
    xi_eta: str = ""
    active_sectors: str = ""

    # Sector support (for Section 1 table)
    efc_s: str = "na"
    efc_d: str = "na"
    efc_c: str = "na"
    lcdm: str = "na"

    # Content
    datasets: str = ""
    regime_interpretation: str = ""
    status_text: str = ""
    evidence_dois: list = field(default_factory=list)

    # Quantitative results (for auto-checkbox logic)
    delta_chi2: Optional[float] = None
    delta_aic: Optional[float] = None
    sigma_level: Optional[float] = None
    p_value: Optional[float] = None
    pass_fail: Optional[str] = None

    # Metadata
    version_added: str = ""
    last_updated: str = ""
    notes: str = ""
    pre_registered: bool = False
    frozen_params: bool = False


@dataclass
class LedgerData:
    """Complete ledger state."""

    version: str = "3.11"
    last_generated: str = ""
    global_verdict: str = "OPEN"
    stage: str = "Non-rejectable model"
    total_tests: int = 0
    passed: int = 0
    partial: int = 0
    failed: int = 0
    planned: int = 0
    entries: list = field(default_factory=list)

    evidence_empirical: list = field(default_factory=list)
    evidence_structural: list = field(default_factory=list)
    evidence_methodological: list = field(default_factory=list)
    evidence_external: list = field(default_factory=list)

    falsification_conditions: list = field(default_factory=list)
    historical_falsifications: list = field(default_factory=list)


def load_ledger(path: Path) -> LedgerData:
    """Load ledger.json into structured data."""
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return LedgerData(**raw)


def save_ledger(data: LedgerData, path: Path) -> None:
    """Write ledger.json from structured data."""
    out = asdict(data)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    _recount(data)


def _recount(data: LedgerData) -> None:
    """Recompute summary counts from entries."""
    entries = data.entries
    data.total_tests = len(entries)
    data.passed = sum(
        1
        for e in entries
        if e.get("status")
        in (
            Status.CONSISTENT_ROBUST,
            Status.COMPLETED_LIKELIHOOD,
            Status.COMPLETED_CONSISTENCY,
            Status.COMPLETED_STRUCTURAL,
        )
    )
    data.partial = sum(
        1
        for e in entries
        if e.get("status")
        in (
            Status.CONSISTENT_PRELIMINARY,
            Status.PHENOMENOLOGICAL,
            Status.FRAMEWORK_DIAGNOSTIC,
        )
    )
    data.failed = sum(
        1 for e in entries if e.get("status") in (Status.DISCREPANT, Status.FALSIFIED)
    )
    data.planned = sum(
        1 for e in entries if e.get("status") in (Status.PLANNED_READY, Status.CONCEPTUAL)
    )


def determine_status_from_results(entry: dict) -> Optional[str]:
    """Auto-determine status based on quantitative results.

    This is the CHECKBOX LOGIC — it decides what gets ticked when
    Phase 2 sync runs. Rules follow Section 0.1 of the ledger.
    """
    dchi2 = entry.get("delta_chi2")
    daic = entry.get("delta_aic")
    pf = entry.get("pass_fail")
    sigma = entry.get("sigma_level")

    # Explicit pass/fail from pre-registered test
    if pf == "PASS":
        if dchi2 is not None and dchi2 <= 0:
            if daic is not None and abs(daic) > 10:
                return Status.CONSISTENT_ROBUST
            return Status.CONSISTENT_PRELIMINARY
        return Status.COMPLETED_LIKELIHOOD

    if pf == "FAIL":
        return Status.DISCREPANT

    if pf == "PARTIAL":
        return Status.CONSISTENT_PRELIMINARY

    # Quantitative result without explicit pass/fail
    if dchi2 is not None:
        if dchi2 <= 0:
            if daic is not None and daic < -10:
                return Status.CONSISTENT_ROBUST
            if sigma is not None and sigma > 2.0:
                return Status.CONSISTENT_PRELIMINARY
            return Status.COMPLETED_LIKELIHOOD
        if dchi2 > 0 and sigma is not None and sigma > 3.0:
            return Status.DISCREPANT

    return None  # Cannot auto-determine; keep existing status


def extract_dois_from_text(text: str) -> list[str]:
    """Extract Figshare DOI IDs (e.g., 31304980) from arbitrary text.

    Matches:
      - 10.6084/m9.figshare.NNNNNNNN canonical form
      - figshare.com/articles/.../NNNNNNNN URL form
      - [NNNNNNNN] / (NNNNNNNN) inline form
      - Standalone 8-digit numbers starting with 3
    """
    pattern = (
        r"(?:10\.6084/m9\.figshare\.|figshare\.com/articles/\w+/|[\[\(])"
        r"(\d{8})(?:[\]\)])?"
    )
    found = re.findall(pattern, text)
    standalone = re.findall(r"\b(3[0-9]{7})\b", text)
    return sorted(set(found + standalone))
