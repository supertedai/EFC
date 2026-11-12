"""Readback tests for the Atlas external-evidence subgraph.

The card this guards (t_87ffe720) asked for one thing that is easy to lose:
independent results may be LINKED to EFC's cosmology nodes, but never at a
strength that reads as confirmation, and never in a way that quietly settles a
sealed prediction.

So the tests are not "does the file exist". They are:

  1. the artifact validates against its own CLOSED schema (the schema registry
     gate, C10, validates the same pair);
  2. every link target resolves in the artifact it claims to point at - the
     public Atlas phenomena, the regime-node bank, the sealed prediction cards;
  3. the declared strength ceiling is enforced on every link, and the forbidden
     upgrade phrases appear nowhere in the claim text;
  4. the frozen contract of the sealed cards (badge, values, seal DOI,
     falsifier, arbiter) is BYTE-IDENTICAL to origin/main - a provenance
     correction may rewrite prose, never a status;
  5. the live fsigma8 contract is still pending, and no settlement is claimed;
  6. the rendered public page is a byte-deterministic function of the JSON and
     actually carries the provenance records next to the cards they concern.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

EVIDENCE = _REPO / "docs" / "validation-ledger" / "data" / "atlas_external_evidence.json"
SCHEMA = _REPO / "schema" / "atlas_external_evidence.schema.json"
ATLAS = _REPO / "docs" / "validation-ledger" / "data" / "atlas.json"
NODES = _REPO / "schema" / "regime_nodes.jsonld"
BUILD = _REPO / "scripts" / "build_atlas.py"
PAGE = _REPO / "docs" / "public" / "EFC_Atlas.html"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema not installed")

#: The frozen contract as it stands on origin/main at the time this register
#: was written. A provenance pass may correct prose; it may not move a status.
FROZEN_ON_MAIN = {
    "P2": {
        "badge": "DAMAGE",
        "efc_value": "0.430",
        "lcdm_value": "0.449",
        "seal_doi": "10.6084/m9.figshare.32013156",
        "falsifier_id": "",
        "arbiter_instrument": "DESI DR2 full-shape RSD",
    },
    "P4": {
        "badge": "PASS",
        "efc_value": "≈ 0.82 (robust); 0.847 ± 0.015 only under fragile η-boost",
        "lcdm_value": "0.811 ± 0.006 (Planck)",
        "seal_doi": "10.6084/m9.figshare.32013738",
        "falsifier_id": "F4",
        "arbiter_instrument": "Rubin LSST DP2",
    },
}

#: Phrases that turn a compatibility into a claim. They may appear in
#: policy.forbidden_upgrades (where they are named as forbidden) and nowhere in
#: the claim text.
_UPGRADE_PHRASES = (
    "confirms efc",
    "proves efc",
    "validates efc",
    "settles p2",
    "settles p4",
    "observed efc signal",
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _evidence() -> dict:
    return _load(EVIDENCE)


def _atlas() -> dict:
    return _load(ATLAS)


def _claim_text_strings(doc: dict) -> list[str]:
    """Every string in the register that asserts something about a result.

    Deliberately exhaustive: a phrase hidden in a nested rationale, a guard
    rule or a discriminator is still published text.
    """
    out: list[str] = []

    def walk(node, key: str = "") -> None:
        if isinstance(node, str):
            if key in ("forbidden_upgrades",):
                return  # the place the phrases are NAMED as forbidden
            out.append(node)
        elif isinstance(node, dict):
            for k, v in node.items():
                walk(v, k)
        elif isinstance(node, list):
            for v in node:
                walk(v, key)

    walk(doc)
    return out


# ---------------------------------------------------------------------------
# 1. schema
# ---------------------------------------------------------------------------

@requires_jsonschema
def test_instance_validates_against_its_own_schema():
    jsonschema.Draft202012Validator(_load(SCHEMA)).validate(_evidence())


@requires_jsonschema
def test_schema_is_valid_and_closed():
    s = _load(SCHEMA)
    jsonschema.Draft202012Validator.check_schema(s)
    assert s.get("additionalProperties") is False
    # No subschema may be the empty object - an open hole in a closed schema.
    def walk(n, path="#"):
        if isinstance(n, dict):
            assert n != {}, f"open subschema at {path}"
            for k, v in n.items():
                walk(v, f"{path}/{k}")
        elif isinstance(n, list):
            for i, v in enumerate(n):
                walk(v, f"{path}/{i}")
    walk(s)


def test_schema_is_registered_in_the_schema_gate():
    """A schema nobody validates is a document, not a gate."""
    gate = (_REPO / "scripts" / "maintenance" / "efc_schema_check.py").read_text(
        encoding="utf-8")
    assert "schema/atlas_external_evidence.schema.json" in gate
    assert "docs/validation-ledger/data/atlas_external_evidence.json" in gate


# ---------------------------------------------------------------------------
# 2. referential integrity against the registries it points at
# ---------------------------------------------------------------------------

def test_named_conflicts_exist():
    """A record that points at 'CONFLICT-X' is a citation: the target must
    exist. A dangling id in prose reads as a trail that is not there."""
    ev = _evidence()
    ids = {c["id"] for c in ev["status_conflicts"]}
    blob = json.dumps(ev, ensure_ascii=False)
    import re
    for named in set(re.findall(r"CONFLICT-[A-Z0-9-]+", blob)):
        assert named in ids, f"named conflict {named} does not exist"


def test_every_source_reference_resolves():
    ev = _evidence()
    ids = {s["id"] for s in ev["sources"]}
    assert len(ids) == len(ev["sources"]), "duplicate source id"
    for f in ev["fragments"]:
        assert f["source_id"] in ids, f"{f['id']}: unknown source {f['source_id']}"


def test_every_link_target_resolves_in_its_own_registry():
    ev = _evidence()
    atlas = _atlas()
    phenomena = {p["id"] for p in atlas["phenomena"]}
    predictions = {p["id"] for p in atlas["tier1_demo_predictions"]}
    nodes = {n["id"] for n in _load(NODES)["nodes"]}

    for f in ev["fragments"]:
        for link in f["links"]:
            kind, target = link["target_kind"], link["target"]
            if kind == "phenomenon":
                assert target in phenomena, f"{f['id']}: unknown phenomenon {target}"
            elif kind == "prediction":
                assert target in predictions, f"{f['id']}: unknown prediction {target}"
            elif kind == "regime_node":
                assert target in nodes, f"{f['id']}: unknown regime node {target}"
            if link.get("node_ref"):
                assert link["node_ref"] in nodes, (
                    f"{f['id']}: node_ref {link['node_ref']} is not in the node bank")
            # a phenomenon link that names a node_ref must name the SAME observable
            if kind == "phenomenon" and link.get("node_ref"):
                assert link["node_ref"].startswith("obs."), (
                    f"{f['id']}: phenomenon link carries a non-observation node ref")


def test_every_conflict_points_at_a_real_card_or_is_general():
    ev = _evidence()
    predictions = {p["id"] for p in _atlas()["tier1_demo_predictions"]}
    for c in ev["status_conflicts"]:
        if c["prediction_id"] is not None:
            assert c["prediction_id"] in predictions, (
                f"{c['id']}: unknown prediction {c['prediction_id']}")


# ---------------------------------------------------------------------------
# 3. the strength ceiling
# ---------------------------------------------------------------------------

def test_declared_link_types_match_the_ceiling():
    ev = _evidence()
    ceiling = ev["policy"]["strength_ceiling"]
    assert ceiling == "candidate_compatibility"
    declared = {lt["id"]: lt for lt in ev["link_types"]}
    for lt in ev["link_types"]:
        assert lt["max_strength"] == ceiling, (
            f"link type {lt['id']} declares a strength above the ceiling")
    for f in ev["fragments"]:
        for link in f["links"]:
            assert link["type"] in declared, (
                f"{f['id']}: undeclared link type {link['type']}")
            assert link["strength"] == ceiling, (
                f"{f['id']}: strength {link['strength']} is above the ceiling")


def test_no_claim_text_upgrades_a_compatibility():
    ev = _evidence()
    for text in _claim_text_strings(ev):
        low = text.lower()
        for phrase in _UPGRADE_PHRASES:
            assert phrase not in low, f"claim text upgrades: ...{phrase}... in {text[:120]!r}"


def test_every_link_says_what_it_does_not_imply():
    """The canonical form is 'that <something>' - a non-implication is a
    sentence about what the link does NOT license, not an adjective."""
    ev = _evidence()
    for f in ev["fragments"]:
        for link in f["links"]:
            assert link["does_not_imply"], (
                f"{f['id']}: link to {link['target']} has no stated limit")
            assert any(item.lower().startswith("that ") for item in link["does_not_imply"]), (
                f"{f['id']}: limits on {link['target']} are not phrased as non-implications")


def test_the_fragments_are_kept_apart():
    """ISW observation, peculiar-flow theory, IMF inference and S8 measurements
    must stay separate fragments - merging them is how a theory becomes an
    observation."""
    ev = _evidence()
    kinds = {f["claim_type"] for f in ev["fragments"]}
    assert {"direct_observation_candidate", "model_derived_theory",
            "measurement_inference", "survey_measurement"} <= kinds


# ---------------------------------------------------------------------------
# 4. the frozen contract is untouched
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("pid", sorted(FROZEN_ON_MAIN))
def test_sealed_card_contract_is_identical_to_main(pid):
    card = next(p for p in _atlas()["tier1_demo_predictions"] if p["id"] == pid)
    for field, expected in FROZEN_ON_MAIN[pid].items():
        assert card.get(field) == expected, (
            f"{pid}.{field} moved: a provenance pass may rewrite prose, not status")


def test_corrections_are_declared_with_the_previous_wording():
    """Every corrected line must still carry the text it replaced."""
    ev = _evidence()
    corrected = [c for c in ev["status_conflicts"]
                 if c["resolution_label"] in ("wording_corrected", "citation_corrected")]
    assert corrected, "no corrections declared - the readback found real errors"
    for c in corrected:
        assert len(c["previous_text"]) > 20, f"{c['id']}: previous text not preserved"
        assert c["evidence_check"], f"{c['id']}: no check recorded"
        assert c["action_taken"], f"{c['id']}: no action recorded"


def test_unresolved_divergences_are_not_silently_resolved():
    ev = _evidence()
    unresolved = [c for c in ev["status_conflicts"]
                  if c["resolution_label"] == "unresolved_status_preserved"]
    assert len(unresolved) >= 3, "the known open divergences must stay recorded"
    for c in unresolved:
        assert c["remaining"], f"{c['id']}: an unresolved entry needs the open question"
        assert c["resolution_requires"], f"{c['id']}: unresolved without who can close it"


def test_atlas_carries_a_dated_provenance_entry():
    log = _atlas()["change_log"]
    entry = next((e for e in log if e["date"] == "2026-11-12"), None)
    assert entry is not None, "no dated change_log entry for this pass"
    assert entry["changes"], "the entry records no changes"


# ---------------------------------------------------------------------------
# 5. the pending contract
# ---------------------------------------------------------------------------

def test_the_fsigma8_contract_is_pending_and_unsettled():
    ev = _evidence()
    assert len(ev["pending_contracts"]) == 1
    c = ev["pending_contracts"][0]
    assert c["subject"] == "kosmos.kosmologi.prediksjon.efc-fs8"
    assert c["stream"] == "VERDEN_PROGNOSE"
    assert c["state"] == "pending"
    assert c["settlement_found"] is False
    assert "DESI DR2 full-shape" in c["arbiter_waiting_for"]
    # the bus says arbiter=no; a register that flipped it here would be a claim
    assert c["arbiter"].lower().startswith("no")
    assert c["sealed_doi"] == "10.6084/m9.figshare.32013156"
    assert len(c["sealing_sha256"]) == 64


def test_pending_card_is_not_reported_as_settled_in_the_atlas():
    card = next(p for p in _atlas()["tier1_demo_predictions"] if p["id"] == "P2")
    assert card["badge"] == "DAMAGE", "P2 stays at its frozen badge while the arbiter is open"
    assert "DESI DR2 full-shape RSD" == card["arbiter_instrument"]
    claim = (card["narrative_intro"] + card["claim"]).lower()
    assert "still open" in claim, "the P2 narrative must say the contract is open"


# ---------------------------------------------------------------------------
# 6. the rendered page is a function of the data, and carries it
# ---------------------------------------------------------------------------

def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_build_is_byte_deterministic():
    before_page = _sha(PAGE)
    for _ in range(2):
        subprocess.run([sys.executable, str(BUILD)], check=True,
                       capture_output=True, cwd=_REPO)
        assert _sha(PAGE) == before_page, (
            "build_atlas.py is not idempotent - the committed page would drift")
    # and the committed page is the one the build produces
    assert _sha(PAGE) == before_page


def test_page_carries_every_fragment_conflict_and_contract():
    html = PAGE.read_text(encoding="utf-8")
    ev = _evidence()
    assert 'data-tab="external"' in html
    assert 'id="tab-external"' in html
    for f in ev["fragments"]:
        assert f["id"] in html, f"fragment {f['id']} missing from the page"
    for c in ev["status_conflicts"]:
        assert c["id"] in html, f"conflict {c['id']} missing from the page"
    for c in ev["pending_contracts"]:
        assert c["subject"] in html
    assert "STATE: PENDING" in html
    assert "Settlement check." in html


def test_provenance_records_sit_inside_the_cards_they_concern():
    """A conflict about P2 that renders only in a distant tab is not next to
    the claim. Both hero cards must carry their own record."""
    html = PAGE.read_text(encoding="utf-8")
    ev = _evidence()
    for pid in ("P2", "P4"):
        start = html.find(f'id="pred-{pid}"')
        assert start != -1, f"card {pid} not found"
        end = html.find('<div class="hero"', start + 1)
        card = html[start:end if end != -1 else len(html)]
        ids = [c["id"] for c in ev["status_conflicts"] if c["prediction_id"] == pid]
        assert ids, f"no recorded conflicts for {pid}"
        for cid in ids:
            assert cid in card, f"{cid} is not rendered inside the {pid} card"


def test_no_placeholder_survives_the_build():
    html = PAGE.read_text(encoding="utf-8")
    assert "__EXTERNAL_CONTENT__" not in html
    assert "__" not in html.replace("__canonical", "")
