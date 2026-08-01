"""
Invariant verifier — runs the §1–§31 cross-checks from the audit spec.

Each invariant is a pure function: given the current `State`, return a
list of `Violation` objects. An empty list means PASS.

Violations are tagged by severity (ERROR vs WARN) so the orchestrator
can decide whether to rollback or just log.
"""
from __future__ import annotations

import glob
import json
import os
import re
from dataclasses import dataclass

from .state import LEDGER_DATA, PAPERS, PUBLIC, REPO, State, _bare_doi, _safe_json


SEVERITY_ERROR = "ERROR"
SEVERITY_WARN = "WARN"


@dataclass
class Violation:
    section: str
    metric: str
    expected: object
    observed: object
    severity: str = SEVERITY_ERROR

    def __str__(self) -> str:
        return (
            f"[{self.severity}] §{self.section} {self.metric}: "
            f"expected={self.expected!r} observed={self.observed!r}"
        )


# ---------------------------------------------------------------------------
# §1 Version consistency (reduced — single internal track)
# ---------------------------------------------------------------------------

def check_version_consistency(state: State) -> list[Violation]:
    out: list[Violation] = []
    if state.ledger_version and state.index_md_version and \
       state.ledger_version != state.index_md_version:
        out.append(Violation(
            "1", "internal_ledger_version",
            expected=state.index_md_version,
            observed=state.ledger_version,
            severity=SEVERITY_WARN,
        ))
    return out


# ---------------------------------------------------------------------------
# §2 DOI integrity — every paper DOI must be in doi-map.json
# ---------------------------------------------------------------------------

def check_doi_integrity(state: State) -> list[Violation]:
    out: list[Violation] = []
    doi_map = _safe_json(os.path.join(REPO, "figshare", "doi-map.json")) or {}
    if not isinstance(doi_map, dict):
        return out
    # doi-map.json is a wrapper: the entries live in the "papers" list, while the
    # top level holds metadata ($schema/version/generated_at/author/totals/…).
    # Reading only the top level yields no DOIs at all, which reported every paper
    # as missing. Keep the legacy flat-dict shape working too.
    entries = doi_map.get("papers")
    if isinstance(entries, list):
        records = [e for e in entries if isinstance(e, dict)]
    else:
        records = [v for v in doi_map.values() if isinstance(v, dict)]

    map_dois = {_bare_doi(e.get("doi")) for e in records}
    if not isinstance(entries, list):
        map_dois |= {_bare_doi(k) for k in doi_map.keys()}
    map_dois.discard(None)

    missing = state.paper_dois - map_dois
    for doi in sorted(missing):
        out.append(Violation(
            "2", f"doi_in_index_but_not_in_doi_map:{doi}",
            expected="present", observed="absent",
            severity=SEVERITY_WARN,
        ))

    # Orphan paths in doi-map
    for e in records:
        path = e.get("repo_dir") or e.get("path") or ""
        if path and not os.path.exists(os.path.join(REPO, path)):
            out.append(Violation(
                "2", f"doi_map_path_missing:{e.get('doi') or path}",
                expected="exists", observed=path,
                severity=SEVERITY_WARN,
            ))
    return out


# ---------------------------------------------------------------------------
# §3 Package 10/10 completeness (lightweight — only count low-scoring dirs)
# ---------------------------------------------------------------------------

PACKAGE_REQUIRED = [
    "README.md", "index.json", "metadata.json", "schema.json",
    "ai_manifest.json", "citations.bib",
]
PACKAGE_REQUIRED_DIRS = ["data", "src", "examples"]


def check_package_completeness(state: State) -> list[Violation]:
    out: list[Violation] = []
    paper_dirs = sorted(
        d for d in glob.glob(os.path.join(PAPERS, "*"))
        if os.path.isdir(d) and os.path.exists(os.path.join(d, "index.json"))
    )
    below = 0
    for d in paper_dirs:
        score = sum(os.path.exists(os.path.join(d, f)) for f in PACKAGE_REQUIRED)
        score += sum(
            os.path.isdir(os.path.join(d, sub)) and bool(os.listdir(os.path.join(d, sub)))
            for sub in PACKAGE_REQUIRED_DIRS
        )
        score += int(bool(glob.glob(os.path.join(d, "*.jsonld"))))
        if score < 10:
            below += 1
    if below > 0:
        out.append(Violation(
            "3", "packages_below_10_10",
            expected=0, observed=below,
            severity=SEVERITY_WARN,
        ))
    return out


# ---------------------------------------------------------------------------
# §5 Language discipline — forbidden absolutist phrases
# ---------------------------------------------------------------------------

FORBIDDEN_PHRASES = [
    "confirms efc",
    "proves efc",
    "demonstrates that efc is correct",
    "validates the theory",
    "definitive evidence",
]
LANGUAGE_SCAN_GLOBS = [
    os.path.join(PAPERS, "*", "README.md"),
    os.path.join(PAPERS, "*", "index.json"),
    os.path.join(PAPERS, "*", "metadata.json"),
    os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    os.path.join(PUBLIC, "EFC_Gap_Analysis.html"),
    os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    os.path.join(REPO, "docs", "validation-ledger", "index.md"),
]


def check_language_discipline(state: State) -> list[Violation]:
    out: list[Violation] = []
    for pattern in LANGUAGE_SCAN_GLOBS:
        for path in glob.glob(pattern):
            try:
                with open(path, encoding="utf-8") as fh:
                    content = fh.read().lower()
            except OSError:
                continue
            # Skip §4b external block in HTML ledger (third-party excerpts allowed)
            if path.endswith("EFC_Validation_Ledger.html"):
                start = content.find("4b. external observations")
                end = content.find("5. planned validation pipeline")
                if start != -1 and end != -1:
                    content = content[:start] + content[end:]
            for phrase in FORBIDDEN_PHRASES:
                if phrase in content:
                    out.append(Violation(
                        "5", f"forbidden_phrase:{phrase}",
                        expected="absent",
                        observed=os.path.relpath(path, REPO),
                        severity=SEVERITY_ERROR,
                    ))
    return out


# ---------------------------------------------------------------------------
# §7 Cross-reference: paper count must match across canonical consumers
# ---------------------------------------------------------------------------

def check_paper_count_consistency(state: State) -> list[Violation]:
    out: list[Violation] = []
    if state.n_ai_friendly is not None and state.n_ai_friendly != state.n_paper_dirs:
        out.append(Violation(
            "7", "n_ai_friendly_vs_paper_dirs",
            expected=state.n_paper_dirs,
            observed=state.n_ai_friendly,
            severity=SEVERITY_ERROR,
        ))
    return out


# ---------------------------------------------------------------------------
# §4 Ledger consistency — total_public sanity
# ---------------------------------------------------------------------------

def check_ledger_total_public(state: State) -> list[Violation]:
    out: list[Violation] = []
    if state.total_public_tests is None:
        return out
    ledger = _safe_json(os.path.join(LEDGER_DATA, "ledger.json")) or {}
    stats = ledger.get("stats") or {}
    parts = (
        (stats.get("physics_test") or 0)
        + (stats.get("consistency_check") or 0)
        + (stats.get("phenomenological") or 0)
        + (stats.get("framework_constraint") or 0)
        + (stats.get("planned_pipeline") or 0)
    )
    if parts and abs(parts - state.total_public_tests) > 0:
        out.append(Violation(
            "4", "total_public_vs_category_sum",
            expected=parts,
            observed=state.total_public_tests,
            severity=SEVERITY_WARN,
        ))
    return out


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

INVARIANTS = [
    check_version_consistency,
    check_doi_integrity,
    check_package_completeness,
    check_language_discipline,
    check_paper_count_consistency,
    check_ledger_total_public,
]


def verify_all(state: State) -> list[Violation]:
    """Run every invariant and return the flat list of violations."""
    violations: list[Violation] = []
    for check in INVARIANTS:
        try:
            violations.extend(check(state))
        except Exception as e:
            violations.append(Violation(
                "0", f"invariant_crashed:{check.__name__}",
                expected="ok", observed=str(e),
                severity=SEVERITY_ERROR,
            ))
    return violations
