"""Tests for scripts/maintenance/doi_provenance_register.py.

Focused validation of the provenance chain and metadata-correction registers:
determinism, closed vocabularies, machine-verified citation edges, live-read
correction values, and that committed output equals build() (no hand-editing).
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
GEN_PATH = ROOT / "scripts" / "maintenance" / "doi_provenance_register.py"
OUT = ROOT / "docs" / "validation-ledger" / "data"

CHAIN = OUT / "doi_provenance_chain.json"
CORRECTIONS = OUT / "doi_metadata_correction_proposals.json"


def _load_gen():
    spec = importlib.util.spec_from_file_location("doi_provenance_register", GEN_PATH)
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


def test_input_digest_identical_across_docs(built):
    chain, corrections = built
    assert chain["input_digest"] == corrections["input_digest"]


def test_relation_vocabulary_closed(built):
    chain, _ = built
    allowed = set(chain["relation_vocabulary"])
    for r in chain["relations"]:
        assert r["relation"] in allowed, r["id"]


def test_reserved_relations_disjoint_from_vocabulary(built):
    chain, _ = built
    vocab = set(chain["relation_vocabulary"])
    reserved = set(chain["reserved_relations"])
    assert not (vocab & reserved), "reserved relations must not be emitted"


def test_status_vocabulary_closed(built):
    chain, _ = built
    allowed = set(chain["status_vocabulary"])
    for r in chain["relations"]:
        assert r["status"] in allowed, r["id"]


def test_source_verified_edges_have_evidence(built):
    chain, _ = built
    for r in chain["relations"]:
        if r["status"] == "source_verified":
            assert r["evidence_text"], f"{r['id']} missing evidence_text"
            assert r["source_file"], f"{r['id']} missing source_file"
            assert r["to_doi"], f"{r['id']} missing to_doi"


def test_open_mapping_edges_have_no_evidence(built):
    chain, _ = built
    for r in chain["relations"]:
        if r["status"] == "open_mapping":
            assert r["evidence_text"] is None, r["id"]
            assert r["evidence_kind"] is None, r["id"]
            assert r["source_file"] is None, r["id"]


def test_counts_reconcile_with_relations(built):
    chain, _ = built
    assert chain["counts"]["total"] == len(chain["relations"])
    assert chain["counts"]["source_verified"] == sum(
        1 for r in chain["relations"] if r["status"] == "source_verified")
    assert chain["counts"]["open_mapping"] == sum(
        1 for r in chain["relations"] if r["status"] == "open_mapping")


def test_corrections_have_live_current_values(built):
    _, corrections = built
    for c in corrections["corrections"]:
        assert c.get("current"), c["id"]
        assert c.get("verified_against_file") is True, c["id"]
        assert c.get("requires_author_word") is True, c["id"]
        assert c.get("json_pointer"), c["id"]


def test_corrections_all_point_at_31942821(built):
    _, corrections = built
    for c in corrections["corrections"]:
        assert c["doi"] == "10.6084/m9.figshare.31942821", c["id"]


def test_corrections_carry_finding_id(built):
    _, corrections = built
    for c in corrections["corrections"]:
        assert c.get("finding_id") == "F1", c["id"]


def test_companion_edge_has_semantic_marker(built):
    chain, _ = built
    companion = [r for r in chain["relations"] if r["relation"] == "COMPANION_TO"]
    assert len(companion) == 1
    edge = companion[0]
    assert edge["evidence_kind"] == "code_header"
    assert edge["evidence_text"], "companion edge missing evidence_text"
    assert "Companion" in edge["evidence_text"]
    assert "31942800" in edge["evidence_text"]


def test_cross_register_f1_linked(built):
    """The coverage register's F1 must name the corrections register as its
    expansion, so the two authorities cannot drift apart silently."""
    chain, corrections = built
    # coverage register is committed; read it directly
    coverage = json.loads(
        (OUT / "doi_coverage_open_findings.json").read_text(encoding="utf-8"))
    f1 = next(f for f in coverage["findings"] if f["id"] == "F1")
    assert "doi_metadata_correction_proposals.json" in f1["claim"], \
        "F1 must name the corrections register"
    # and every correction proposal points back at F1
    assert all(c.get("finding_id") == "F1" for c in corrections["corrections"])


def test_relation_ids_are_unique(built):
    chain, _ = built
    ids = [r["id"] for r in chain["relations"]]
    assert len(ids) == len(set(ids)), "relation ids must be unique"


def test_source_verified_relation_semantics(built):
    chain, _ = built
    for r in chain["relations"]:
        if r["status"] == "source_verified":
            assert r["relation"] in {"CITES", "COMPANION_TO"}, r["id"]
            assert r["source_file"], r["id"]
            assert r["evidence_text"], r["id"]


def test_unverifiable_edge_aborts(gen):
    """A fabricated citation edge that cannot be confirmed must raise, so the
    fail-closed promise cannot silently degrade."""
    dmap = gen._doi_map()
    fake = {
        "id": "rel-fake",
        "from_doi": "10.6084/m9.figshare.31942800",
        "to_doi": "10.6084/m9.figshare.99999999",
        "to_label": None,
        "relation": "CITES",
        "claim": "fabricated",
        "status": "source_verified",
        "evidence_kind": "citation",
        "source_file": "citations.bib",
        "evidence_text": None,
    }
    with pytest.raises(SystemExit):
        gen._verify_relation(fake, dmap, {})


def test_generated_files_match_build(built):
    """The committed registers must equal build() output (no hand-editing)."""
    chain, corrections = built
    for path, doc in ((CHAIN, chain), (CORRECTIONS, corrections)):
        assert path.exists(), f"missing generated register: {path.name}"
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        assert on_disk == doc, path.name


# ---------------------------------------------------------------------------
# The correction lifecycle gate (F1 / card t_3a2d983f). The status is computed
# from the value read live out of index.json, so these tests fail the moment the
# published package drifts back to the old forms — or the moment someone edits
# it without author word.
# ---------------------------------------------------------------------------
def test_correction_status_vocabulary_closed(built):
    _, corrections = built
    allowed = set(corrections["status_vocabulary"])
    for c in corrections["corrections"]:
        assert c["status"] in allowed, c["id"]


def test_licensed_corrections_are_applied(built):
    """Every correction licensed by an author instruction MUST be applied.

    A failure here is not a test bug: index.json no longer carries the value the
    author word licensed. Either the file drifted (restore it) or the edit was
    intentional (then update the entry's expected_value and its author_word_ref
    deliberately, in the same change).
    """
    _, corrections = built
    not_applied = [c["id"] for c in corrections["corrections"]
                   if c.get("author_word_ref") and c["status"] != "applied"]
    assert not not_applied, (
        "licensed metadata corrections are not applied in 31942821/index.json: "
        f"{not_applied}"
    )


def test_unlicensed_corrections_are_not_applied(built):
    """An entry without author word must NOT already be present in the package."""
    _, corrections = built
    applied = [c["id"] for c in corrections["corrections"]
               if not c.get("author_word_ref") and c["status"] == "applied"]
    assert not applied, (
        "published package carries corrections that no author instruction "
        f"licensed: {applied}"
    )


def test_correction_counts_reconcile(built):
    _, corrections = built
    counts = corrections["counts"]
    entries = corrections["corrections"]
    assert counts["total"] == len(entries)
    assert counts["applied"] == sum(1 for c in entries if c["status"] == "applied")
    assert counts["proposed"] == sum(1 for c in entries if c["status"] == "proposed")
    assert counts["applied"] + counts["proposed"] == counts["total"]


def test_corrections_carry_expected_values(built):
    _, corrections = built
    for c in corrections["corrections"]:
        assert c.get("expected_value"), c["id"]
        assert c["current"] == c["expected_value"] or c["status"] == "proposed", c["id"]


def test_pointer_into_a_list_is_resolved(gen):
    """/kill_criteria/4 addresses an array element; the resolver must handle it."""
    doc = {"kill_criteria": ["a", "b", "c", "d", "KC5: target"]}
    assert gen._resolve_pointer(doc, "/kill_criteria/4") == "KC5: target"
    with pytest.raises(SystemExit):
        gen._resolve_pointer(doc, "/kill_criteria/9")


def test_prose_no_longer_presents_the_ansatz_as_derived(built):
    """Negative guard, independent of expected_value: the drifted sentences.

    The description and main_finding must not read the saturating ansatz as the
    derivation's outcome.
    """
    idx = json.loads(
        (ROOT / "docs" / "papers" / "efc" / "Derivation_of_the_Entropy_Production"
         / "index.json").read_text(encoding="utf-8"))
    prose = idx["description"] + " " + idx["key_results"]["main_finding"]
    assert "phenomenological approximation" in prose
    for drifted in ("The work yields a saturating form",
                    "takes the saturating form",
                    "satisfying low-density linearity and high-density saturation"):
        assert drifted not in prose, drifted


def test_be_exponent_is_the_sqrt_form_in_every_metadata_field(built):
    """Widened guard: g/a0 appears nowhere as the BE exponent or as x."""
    idx = json.loads(
        (ROOT / "docs" / "papers" / "efc" / "Derivation_of_the_Entropy_Production"
         / "index.json").read_text(encoding="utf-8"))
    assert "exp(g/a0)" not in idx["description"]
    for name, eq in idx["core_equations"].items():
        latex = eq.get("latex", "")
        if name in ("be_occupation", "x_of_rho", "entropy_marginal"):
            assert "sqrt" in latex, f"{name} lost its sqrt: {latex}"
    assert "e^{g/a0}" not in idx["kill_criteria"][4]
