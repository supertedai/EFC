"""Negative test suite for the fail-closed EFC review gate.

Proves the gate refuses every malformed condition and passes exactly one
synthetic, fully-conformant v2 verdict. These tests are the load-bearing proof
that a Hermes update (which cannot touch this file or the scripts in git)
cannot silently weaken the release gate.

The gate and the aggregator are loaded by file path (importlib), and pointed at
temp review dirs via EFC_REVIEWS_DIR, so no test touches the real
docs/validation-ledger/reviews/ tree.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts" / "maintenance"

SLUG = "EFC_Model_Family_Reconciliation"
MANUSCRIPT = f"docs/papers/efc/{SLUG}/EFC_Model_Family_Reconciliation.tex"

# The nine reviewer roles, from review_roles.json — a conformant verdict must
# carry at least one finding from each, or the release gate refuses.
ALL_ROLES = [
    "cartographer", "provenance", "formalist", "paradigm_critic",
    "falsifier", "alternative_paradigm", "measurement_proxy", "reproducer",
    "meta_reviewer",
]

# The ten gate identities, from gates.json — a conformant claim-gate matrix
# must cover every gate for every claim.
ALL_GATES = list(range(1, 11))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


gate = _load("efc_review_gate", SCRIPTS / "efc_review_gate.py")
index_mod = _load("efc_findings_index", SCRIPTS / "efc_findings_index.py")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _verdict(**over) -> dict:
    """A fully-conformant v2 verdict: all nine roles deliver a finding, and the
    reproducer finding grounds the promoted claim on a direct evidence layer."""
    findings = []
    for i, role in enumerate(ALL_ROLES):
        findings.append({
            "finding_id": f"F-test-{i}",
            "claim_id": "C1",
            "reviewer_role": role,
            "evidence_layer": "TARGET" if role == "reproducer" else "RAW_SIGNAL",
            "finding": f"{role} finding",
            "severity": "medium",
            "type": "empirical",
            "supports_or_attacks": "supports" if role == "reproducer" else "neutral",
            "source": "src/example.py",
            "confidence": 0.9,
            "method_revision": "v2",
            "disposition": "accepted",
        })
    base = {
        "verdict_id": "test-verdict",
        "manuscript": MANUSCRIPT,
        "method_revision": "v2",
        "snapshot_sha256": "",
        "claim_verdicts": [
            {"claim_id": "C1", "claim_status": "declared_derived"}
        ],
        "findings": findings,
    }
    base.update(over)
    return base


def _matrix(**over) -> dict:
    """A fully-conformant claim-gate matrix: all ten gates satisfied for C1.
    verdict_sha256 is bound by _write_review after the verdict is written."""
    gates = [
        {"gate_id": g, "status": "satisfied", "evidence": f"gate {g} evidence",
         "reviewer_role": "reproducer", "source_ref": "src/example.py"}
        for g in ALL_GATES
    ]
    base = {
        "verdict_id": "test-verdict",
        "matrix": [{"claim_id": "C1", "gates": gates}],
    }
    base.update(over)
    return base


def _human_gate(**over) -> dict:
    """Build a human-gate dict WITHOUT reading any verdict file.

    The verdict_sha256 binding is done by _write_review (via setdefault) after
    the verdict is written. Callers that need an explicit (wrong or real) hash
    pass it in `over`; setdefault then respects it.
    """
    base = {
        "verdict_id": "test-verdict",
        "method_revision": "v2",
        "status": "approved",
        "confirmed_by": "morten",
        "at": "2026-09-21T12:00:00Z",
        "approved_claims": ["C1"],
    }
    base.update(over)
    return base


def _finding_by_role(v: dict, role: str) -> dict:
    """The single finding authored by `role`. Grounding tests must mutate the
    reproducer finding — not findings[0], which is now the cartographer."""
    for f in v["findings"]:
        if f.get("reviewer_role") == role:
            return f
    raise AssertionError(f"no finding with reviewer_role={role!r}")


def _write_review(tmp_path: Path, verdict: dict, *, human_gate: dict | None,
                  snapshot: str | None = None, verdict_name: str = "deleg_t1",
                  matrix: dict | None = None, omit_matrix: bool = False) -> Path:
    d = tmp_path / verdict_name
    d.mkdir(parents=True, exist_ok=True)
    vp = d / "verdict.json"

    if snapshot is None:
        snapshot = "frozen source snapshot\n"
    (d / "snapshot.tex").write_text(snapshot, encoding="utf-8")
    v = dict(verdict)
    v["snapshot_sha256"] = hashlib.sha256(snapshot.encode("utf-8")).hexdigest()
    # the live manuscript (at EFC_REPO_ROOT / verdict.manuscript) must match
    vp.write_text(json.dumps(v), encoding="utf-8")
    mp = v.get("manuscript")
    if mp is not None:
        mp = Path(str(mp))
        if not mp.is_absolute() and ".." not in mp.parts:
            live = tmp_path / mp
            live.parent.mkdir(parents=True, exist_ok=True)
            live.write_text(snapshot, encoding="utf-8")

    # claim-gate matrix: conformant by default, override with an explicit dict
    # (negative tests), suppress entirely with omit_matrix=True.
    if not omit_matrix:
        m = _matrix() if matrix is None else matrix
        m.setdefault("verdict_id", v.get("verdict_id", "test-verdict"))
        m.setdefault("verdict_sha256", _sha(vp))
        (d / "claim_gate_matrix.json").write_text(json.dumps(m), encoding="utf-8")

    if human_gate is not None:
        hg = dict(human_gate)
        # bind to the verdict as actually written (unless the caller overrode)
        hg.setdefault("verdict_sha256", _sha(vp))
        (d / "human_gate.json").write_text(json.dumps(hg), encoding="utf-8")
    return d


@pytest.fixture
def reviews_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("EFC_REVIEWS_DIR", str(tmp_path))
    monkeypatch.setenv("EFC_REPO_ROOT", str(tmp_path))
    return tmp_path


# ── fail-closed matrix ────────────────────────────────────────────────────────

def test_no_verdict_refused(reviews_dir):
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "no verdict" in reason


def test_wrong_confirmed_by_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "someone-else")
    assert not ok and "confirmed_by" in reason


def test_v1_revision_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(method_revision="v1"), human_gate=None)
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "method_revision" in reason


def test_legacy_no_revision_refused(reviews_dir):
    v = _verdict()
    v.pop("method_revision")
    _write_review(reviews_dir, v, human_gate=None)
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "method_revision" in reason


def test_open_disposition_refused(reviews_dir):
    v = _verdict()
    v["findings"][0]["disposition"] = None
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "disposition" in reason


def test_missing_human_gate_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(), human_gate=None)
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "human_gate" in reason


def test_wrong_human_gate_confirmed_by_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(),
                  human_gate=_human_gate(confirmed_by="bob"))
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "confirmed_by" in reason


def test_rejected_status_refused(reviews_dir):
    """human_gate.status='rejected' is truthy but must NOT release."""
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate(status="rejected"))
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "approved" in reason


def test_rejected_supports_finding_does_not_ground(reviews_dir):
    """A rejected finding cannot ground a promotion, even on a grounding layer."""
    v = _verdict()
    _finding_by_role(v, "reproducer")["disposition"] = "rejected"
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "grounding" in reason


def test_ambiguous_multiple_verdicts_refused(reviews_dir):
    """Two v2 verdicts for the same slug must refuse, not pick arbitrarily."""
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate(), verdict_name="deleg_a")
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate(), verdict_name="deleg_b")
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "ambiguous" in reason


def test_snapshot_mismatch_refused(reviews_dir):
    d = _write_review(reviews_dir, _verdict(), human_gate=None)
    vp = d / "verdict.json"
    (d / "human_gate.json").write_text(
        json.dumps(_human_gate(verdict_sha256=_sha(vp))), encoding="utf-8")
    (d / "snapshot.tex").write_text("TAMPERED", encoding="utf-8")
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "snapshot" in reason


def test_live_manuscript_mutation_refused(reviews_dir):
    """The exact 59c8cbed failure mode: source edited after review."""
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate())
    (reviews_dir / MANUSCRIPT).write_text("EDITED AFTER REVIEW\n", encoding="utf-8")
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "does not match" in reason


def test_live_manuscript_absent_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate())
    (reviews_dir / MANUSCRIPT).unlink()
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "missing" in reason


def test_verdict_manuscript_path_missing_refused(reviews_dir):
    v = _verdict()
    v.pop("manuscript")
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "manuscript" in reason


def test_absolute_manuscript_path_refused(reviews_dir):
    v = _verdict(
        manuscript="/repo/docs/papers/efc/EFC_Model_Family_Reconciliation/EFC_Model_Family_Reconciliation.tex"
    )
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "repo-relative" in reason


def test_opinion_only_grounding_refused(reviews_dir):
    v = _verdict()
    _finding_by_role(v, "reproducer")["evidence_layer"] = "PARADIGM"
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "grounding" in reason


def test_instrument_without_bias_audit_refused(reviews_dir):
    """INSTRUMENT/PROXY are paradigm-laden — they ground only with atlas_field."""
    v = _verdict()
    f = _finding_by_role(v, "reproducer")
    f["evidence_layer"] = "PROXY"
    f["atlas_field"] = None
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "grounding" in reason


def test_instrument_with_bias_audit_grounds(reviews_dir):
    v = _verdict()
    f = _finding_by_role(v, "reproducer")
    f["evidence_layer"] = "PROXY"
    f["atlas_field"] = "measure.proxy_chain"
    _write_review(reviews_dir, v, human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert ok, reason


def test_promoted_claim_not_approved_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(),
                  human_gate=_human_gate(approved_claims=[]))
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "approved_claims" in reason


def test_human_gate_wrong_verdict_binding_refused(reviews_dir):
    _write_review(reviews_dir, _verdict(),
                  human_gate=_human_gate(verdict_sha256="0" * 64))
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert not ok and "verdict_sha256" in reason


def test_valid_v2_passes(reviews_dir):
    _write_review(reviews_dir, _verdict(), human_gate=_human_gate())
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert ok, reason


def test_v3_future_revision_passes(reviews_dir):
    _write_review(reviews_dir, _verdict(method_revision="v3"),
                  human_gate=_human_gate(method_revision="v3"))
    ok, reason = gate.gate_manuscript(SLUG, "morten")
    assert ok, reason


# ── finding-shape sync: the inline verdict schema must not drift ──────────────

def test_finding_shape_in_sync():
    finding = json.loads((ROOT / "docs/validation-ledger/finding.schema.json").read_text())
    verdict = json.loads((ROOT / "docs/validation-ledger/verdict.schema.json").read_text())
    inline = verdict["$defs"]["finding"]

    fp = set(finding["properties"].keys())
    ip = set(inline["properties"].keys())
    assert fp == ip, f"finding properties drifted: {fp ^ ip}"

    fr = set(finding.get("required", []))
    ir = set(inline.get("required", []))
    # the inline (final verdict) shape additionally requires disposition
    assert (fr | {"disposition"}) == ir, f"finding required drifted: {fr} vs {ir}"


# ── findings index: determinism + revision separation ────────────────────────

def test_index_deterministic_and_revision_separated(tmp_path, monkeypatch):
    reviews = tmp_path / "reviews"
    monkeypatch.setenv("EFC_REVIEWS_DIR", str(reviews))

    v2 = _verdict()
    _write_review(reviews, v2, human_gate=None, verdict_name="deleg_v2")
    v1 = _verdict(method_revision="v1")
    v1["findings"][0]["finding"] = "a different v1 finding text"
    v1["findings"][0]["finding_id"] = "F-v1-1"
    _write_review(reviews, v1, human_gate=None, verdict_name="deleg_v1")

    out = tmp_path / "index.json"
    monkeypatch.setenv("EFC_FINDINGS_INDEX_OUT", str(out))

    assert index_mod.main(["--apply"]) == 0
    first = out.read_text()
    assert index_mod.main(["--check"]) == 0
    assert out.read_text() == first, "index is not byte-deterministic"

    data = json.loads(first)
    revs = data["revisions"]
    assert "v1" in revs and "v2" in revs
    assert revs["v2"]["release_eligible"] is True
    assert revs["v1"]["release_eligible"] is False
