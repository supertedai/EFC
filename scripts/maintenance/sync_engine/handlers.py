"""
Change handlers — one function per change type.

Each handler takes a `Change` and returns the list of file paths it
touched (used for commit-message composition + audit trail).

Handlers are deliberately additive + idempotent: running twice on the
same input yields the same output, and they never delete data without
an explicit instruction.

Most handlers delegate to existing scripts/maintenance/efc_*.py tools
because those already implement the bulk of the logic. The handler
layer adds typed dispatch + provenance tracking.
"""
from __future__ import annotations

import os
import subprocess
import sys
from datetime import date

from .classify import (
    Change,
    T1_NEW_PAPER, T2_PAPER_METADATA, T3_FALSIFICATION, T4_GAP_CLOSURE,
    T5_NEW_HYPOTHESIS, T6_PARAMETER_UPDATE, T7_DATASET_RELEASE,
    T8_INFERENCE_REFRESH, T9_VERSION_BUMP, T10_SEALED_PRED,
    T11_STRUCTURAL, T12_PIPELINE_PLANNED, T13_DRIFT_FIX,
    T14_DATE_ROLLOVER, T15_NOOP,
)
from .state import REPO

SCRIPTS = os.path.join(REPO, "scripts", "maintenance")


def _run(script: str, *args: str) -> int:
    path = os.path.join(SCRIPTS, script)
    if not os.path.exists(path):
        return 0
    res = subprocess.run([sys.executable, path, *args], cwd=REPO)
    return res.returncode


# ---------------------------------------------------------------------------
# Handler implementations
# ---------------------------------------------------------------------------

def handle_new_paper(change: Change) -> list[str]:
    """T1 — A new paper directory has appeared. Run the full enrichment chain."""
    touched: list[str] = []
    # Step A: skeleton + 10/10 enrichment
    _run("efc_auto_metadata.py")
    _run("efc_ai_brain.py")
    _run("efc_gen_ai_friendly.py")
    # Step B: DOI propagation across in-package files + registers
    _run("efc_sync_dois.py", "--apply")
    # Step C: Re-run generator so ai_manifest bytes match disk
    _run("efc_gen_ai_friendly.py")
    # Step D: HTML registration (Ledger + Changelog) for empirical/sealed types
    _run("efc_ledger_autofill.py")
    touched.extend([
        "docs/papers/efc/",
        "figshare/doi-map.json",
        "docs/validation-ledger/data/evidence-register.json",
        "docs/validation-ledger/data/ledger.json",
        "docs/public/EFC_Validation_Ledger.html",
        "docs/public/EFC_Changelog.html",
    ])
    return touched


def handle_metadata_change(change: Change) -> list[str]:
    """T2 — index.json edited. Re-derive ai_manifest + DOI mirror files."""
    _run("efc_gen_ai_friendly.py")
    _run("efc_sync_dois.py", "--apply")
    return ["docs/papers/efc/"]


def handle_falsification(change: Change) -> list[str]:
    """T3 — A test flipped to falsified. Refresh stats + Ledger HTML."""
    _run("efc_gen_ai_friendly.py")
    _run("efc_ledger_autofill.py")
    return [
        "docs/validation-ledger/data/ledger.json",
        "docs/public/EFC_Validation_Ledger.html",
    ]


def handle_gap_closure(change: Change) -> list[str]:
    """T4 — frontier-gaps.json modified. Cross-validate Gap Analysis page."""
    _run("efc_cross_validate.py")
    return ["docs/public/EFC_Gap_Analysis.html"]


def handle_new_hypothesis(change: Change) -> list[str]:
    return ["docs/validation-ledger/data/hypotheses.json"]


def handle_parameter_update(change: Change) -> list[str]:
    return ["docs/validation-ledger/data/parameters.json"]


def handle_dataset_release(change: Change) -> list[str]:
    """T7 — External dataset released. Refresh roadmap + scan report."""
    _run("efc_dataset_scanner.py")
    return [
        ".claude/dataset_scan_report.json",
        "docs/public/EFC_Stage-IV_Data_Roadmap.html",
    ]


def handle_inference_refresh(change: Change) -> list[str]:
    """T8 — inference.json modified. Cross-validate Gap Analysis §7."""
    _run("efc_cross_validate.py")
    return ["docs/public/EFC_Gap_Analysis.html"]


def handle_version_bump(change: Change) -> list[str]:
    """T9 — codemeta.json version changed. Propagate to all version surfaces."""
    # Existing scripts handle version mirroring via efc_drift_detector --fix
    _run("efc_drift_detector.py", "--fix")
    return ["README.md", "AGENTS.md", "llms.txt", "ecosystem.jsonld"]


def handle_sealed_prediction(change: Change) -> list[str]:
    """T10 — New sealed prediction. Snapshot regenerate + Ledger autofill +
    cross-validate to catch stale KC badges in Gap Analysis / Roadmap."""
    _run("efc_ledger_autofill.py")
    _run("efc_symbiose_snapshot.py", "--from-ledger")
    _run("efc_cross_validate.py")
    return [
        "docs/public/EFC_Validation_Ledger.html",
        "docs/public/EFC_Gap_Analysis.html",
        "docs/public/EFC_Stage-IV_Data_Roadmap.html",
        ".claude/symbiose_snapshot.json",
    ]


def handle_structural_result(change: Change) -> list[str]:
    return ["docs/validation-ledger/data/structural-constraints.json"]


def handle_pipeline_planned(change: Change) -> list[str]:
    return ["docs/validation-ledger/data/pipeline.json"]


def handle_drift_fix(change: Change) -> list[str]:
    """T13 — Counts drifted between source and consumer. Auto-fix."""
    _run("efc_drift_detector.py", "--fix")
    return ["README.md", "AGENTS.md", "llms.txt"]


def handle_date_rollover(change: Change) -> list[str]:
    """T14 — Day changed. Refresh date stamps + snapshot."""
    _run("efc_symbiose_snapshot.py", "--from-ledger")
    _run("efc_auto_changelog.py")
    return [".claude/symbiose_snapshot.json"]


def handle_noop(change: Change) -> list[str]:
    """T15 — Nothing to propagate. Still safe to run snapshot."""
    return []


HANDLERS = {
    T1_NEW_PAPER:         handle_new_paper,
    T2_PAPER_METADATA:    handle_metadata_change,
    T3_FALSIFICATION:     handle_falsification,
    T4_GAP_CLOSURE:       handle_gap_closure,
    T5_NEW_HYPOTHESIS:    handle_new_hypothesis,
    T6_PARAMETER_UPDATE:  handle_parameter_update,
    T7_DATASET_RELEASE:   handle_dataset_release,
    T8_INFERENCE_REFRESH: handle_inference_refresh,
    T9_VERSION_BUMP:      handle_version_bump,
    T10_SEALED_PRED:      handle_sealed_prediction,
    T11_STRUCTURAL:       handle_structural_result,
    T12_PIPELINE_PLANNED: handle_pipeline_planned,
    T13_DRIFT_FIX:        handle_drift_fix,
    T14_DATE_ROLLOVER:    handle_date_rollover,
    T15_NOOP:             handle_noop,
}


def dispatch(changes: list[Change]) -> dict[str, list[str]]:
    """Run handlers in given order and return {change_type: touched_files}."""
    result: dict[str, list[str]] = {}
    for ch in changes:
        h = HANDLERS.get(ch.type, handle_noop)
        try:
            touched = h(ch)
        except Exception as e:
            print(f"[sync-engine] handler {h.__name__} failed: {e}", file=sys.stderr)
            touched = []
        result.setdefault(ch.type, []).extend(touched)
    return result
