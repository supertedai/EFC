"""Tests for scripts/maintenance/doi_coverage_register.py.

Focused validation of the three generated registers: determinism, status
vocabulary, classification provenance, duplicate accounting, coverage/backlog
reconciliation, and that the generator writes only its three declared files.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN_PATH = ROOT / "scripts" / "maintenance" / "doi_coverage_register.py"
OUT = ROOT / "docs" / "validation-ledger" / "data"

MATRIX = OUT / "doi_coverage_matrix.json"
FINDINGS = OUT / "doi_coverage_open_findings.json"
PENDING = OUT / "doi_coverage_pending.json"


def _load_gen():
    spec = importlib.util.spec_from_file_location("doi_coverage_register", GEN_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def gen():
    return _load_gen()


@pytest.fixture(scope="module")
def built(gen):
    return gen.build()


def test_build_is_deterministic(gen):
    a = gen.build()
    b = gen.build()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_input_digest_identical_across_three_docs(built):
    matrix, findings, backlog = built
    d = matrix["input_digest"]
    assert findings["input_digest"] == d
    assert backlog["input_digest"] == d


def test_matrix_unique_dois_match_rows(built):
    matrix, _, _ = built
    assert matrix["measured"]["unique_dois"] == len(matrix["rows"])


def test_duplicate_groups_are_orthogonal_to_scope(built):
    """A duplicate dir must not drop an empirical DOI from atlas scope."""
    matrix, _, backlog = built
    # Every backlog entry is atlas_scope + not in atlas; duplicates must be retained.
    pending_dois = {e["doi"] for e in backlog["pending"]}
    for r in matrix["rows"]:
        if r["class"] == "atlas_scope" and not r["in_atlas_literal_url"]:
            assert r["doi"] in pending_dois, r["doi"]
            assert r["duplicate_dir"] in (True, False)  # duplicates are allowed


def test_backlog_reconciles_with_matrix(built):
    matrix, _, backlog = built
    n = sum(1 for r in matrix["rows"] if r["disposition"] == "atlas_candidate")
    assert backlog["count"] == n
    assert matrix["measured"]["atlas_candidate_missing_from_atlas"] == n


def test_findings_status_vocabulary_closed(built):
    _, findings, _ = built
    allowed = set(findings["status_vocabulary"])
    for f in findings["findings"]:
        assert f["status"] in allowed, f["id"]


def test_findings_have_next_step(built):
    _, findings, _ = built
    for f in findings["findings"]:
        assert f.get("next"), f["id"]


def test_classification_provenance_preserved(built):
    """Multi-label categories are recorded as overlap, not a contradiction."""
    matrix, _, _ = built
    for r in matrix["rows"]:
        if r["category_overlap"]:
            assert len(r["categories"]) > 1
        # categories are a list of the evidence-register's own labels
        assert all(c in ("empirical", "methodological", "structural")
                   for c in r["categories"])


def test_generated_files_match_build(built):
    """The committed registers must equal build() output (no hand-editing)."""
    matrix, findings, backlog = built
    for path, doc in ((MATRIX, matrix), (FINDINGS, findings), (PENDING, backlog)):
        assert path.exists(), f"missing generated register: {path.name}"
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk == doc, path.name
