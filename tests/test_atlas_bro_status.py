"""t_1610348d — the cosmos–cognition bridge is recorded as a PROPOSAL, not a result.

Pinned claim (card t_1610348d; ADR ``docs/adr/2026-11-10-cosmos-cognition-bridge-status/``):

    formal/model-based bridge proposals between EFC cosmology and cognition exist;
    empirical/causal cosmology-to-cognition validation is NOT established.

Why the pin is needed. The node already SAID "the bridge is the hypothesis, not the
result" and "the cosmology-to-cognition bridge is not established" — but it named no
proposal and carried no DOI for one, so a reader of the bank could not tell

    "nobody has proposed a bridge"      from      "a bridge has been proposed, and is
                                                    still unvalidated".

That difference IS the epistemic content, and it is what is now recorded. The test also
pins the *limits* from inside the two proposals (ansatz; unconstrained gamma;
equilibrium level; propofol material "does not yet constitute a direct test"), because a
proposal recorded without its limits becomes a result the next time someone quotes it.

Measured before the change: ``ontology.proveniens.kilder`` held three entries, none of
them a bridge DOI; ``revisjon`` held two entries, both dated 2026-09-19.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"

NODE_ID = "efc.lag_c0"

#: B1 cosmology -> neural entropy production; B2 neural entropy structure <->
#: RLHF reward curvature (DOI 10.6084/m9.figshare.31940547).
BRIDGE_DOI = "10.6084/m9.figshare.31940547"
#: Dimensionless S -> (Omega-hat, kappa-hat) mapping with candidate C
#: (DOI 10.6084/m9.figshare.31969983).
MAPPING_DOI = "10.6084/m9.figshare.31969983"

REVISION_DATE = "2026-11-10"

#: The bank totals at the change's baseline. Pinned because this change must add
#: NO node and NO relation — the card forbids inventing either.
NODES_BASELINE = 126
RELATIONS_BASELINE = 86


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(atlas: dict | None = None) -> dict:
    atlas = atlas or _atlas()
    matches = [n for n in atlas["nodes"] if n.get("id") == NODE_ID]
    assert len(matches) == 1, f"{NODE_ID}: expected exactly one node, got {len(matches)}"
    return matches[0]


def _node_text(node: dict) -> str:
    return json.dumps(node, ensure_ascii=False)


def _bridge_revision(node: dict) -> str:
    entries = [r for r in node.get("revisjon", [])
               if REVISION_DATE in r and "bridge" in r.lower()]
    assert len(entries) == 1, (
        f"{NODE_ID}: expected exactly one revision entry dated {REVISION_DATE} about the "
        f"bridge, found {len(entries)}")
    return entries[0]


def test_status_is_still_hypothesis_and_proxy():
    """The change records a proposal; it does not promote the node."""
    ep = _node()["epistemikk"]
    assert ep["sannhetsstatus"] == "hypotese", ep
    assert ep["evidensstatus"] == "proxy", ep
    assert "not established" in ep["sosial_mekanisme"]


def test_both_proposals_are_in_provenance_as_dois():
    """A proposal a later reader cannot find is not recorded."""
    kilder = _node()["ontology"]["proveniens"]["kilder"]
    dois = {k["ref"] for k in kilder if k.get("type") == "doi"}
    assert BRIDGE_DOI in dois, sorted(dois)
    assert MAPPING_DOI in dois, sorted(dois)
    for k in kilder:
        if k.get("type") == "doi" and k["ref"] in (BRIDGE_DOI, MAPPING_DOI):
            assert k.get("hentet"), k


def test_revision_records_the_conclusion_as_not_established():
    text = _bridge_revision(_node())
    assert "not established" in text.lower(), text
    # The conclusion must be about empirical/causal validation, not about the proposal.
    assert re.search(r"empirical|causal", text, re.I), text


def test_revision_records_the_limits_from_inside_the_proposals():
    """A proposal quoted without its limits becomes a result."""
    text = _bridge_revision(_node())
    lowered = text.lower()
    assert "ansatz" in lowered, "the transfer-entropy identification is an ansatz"
    assert re.search(r"gamma|γ", text, re.I) and re.search(
        r"unconstrained|undetermined|not determined|free parameter", lowered), (
        "gamma must be recorded as unconstrained")
    assert re.search(r"does not yet constitute a direct test|not a direct test", lowered), (
        "the propofol material is not a direct test of the full model")
    # Review finding 6 + 7 (gpt-5.6-luna, 2026-11-10): the two limits that keep a reader
    # from inferring a complete, closed bridge must be part of the record, not only the
    # proposal's own paper.
    assert re.search(r"does not close the cosmology[- ]rlhf loop", lowered), (
        "31940547 states the bridge does not close the cosmology-RLHF loop directly")
    assert re.search(r"not yet been fitted to a neural dataset|not yet fitted to a neural",
                     lowered), (
        "31940505 states EFC-C had not yet been fitted to a neural dataset")
    # Both proposal ids must be named in the entry itself, not only in provenance.
    assert "31940547" in text and "31969983" in text, text


def test_revision_preserves_the_v2_0_v2_1_discrepancy_as_a_discrepancy():
    """The EFC-C v2 note (32091700): DataCite titles it v2.0, the repo's index says v2.1."""
    text = _bridge_revision(_node())
    assert "32091700" in text, text
    assert "v2.0" in text and "v2.1" in text, text
    assert re.search(r"discrepan|unresolved|not resolved", text, re.I), text


def test_node_never_asserts_establishment():
    """Every claim of establishment in this node must be a NEGATION."""
    text = _node_text(_node())
    for m in re.finditer(r"established", text, re.I):
        window = text[max(0, m.start() - 48):m.start()].lower()
        assert "not " in window or "never " in window, (
            "affirmative establishment claim: "
            + text[max(0, m.start() - 90):m.end() + 30])
    for verb in (r"\bconfirms?\b", r"\bproves?\b", r"\bvalidates?\b",
                 r"\bconfirms EFC\b"):
        assert not re.search(verb, text, re.I), verb
    # A causal link, if ever claimed, is the one thing the sources explicitly disclaim.
    assert not re.search(
        r"causal(ly)?\s+(link|connection|relation)\s+(is|has been|was)\s+"
        r"(established|shown|demonstrated|confirmed)", text, re.I), text


def test_no_node_and_no_relation_were_invented():
    atlas = _atlas()
    assert len(atlas["nodes"]) == NODES_BASELINE, (
        f"nodes changed: {NODES_BASELINE} -> {len(atlas['nodes'])}; this change adds no node")
    assert len(atlas["relations"]) == RELATIONS_BASELINE, (
        f"relations changed: {RELATIONS_BASELINE} -> {len(atlas['relations'])}; "
        "this change adds no edge")
    touching = [r for r in atlas["relations"]
                if NODE_ID in (r.get("subject"), r.get("object"))]
    assert touching == [], touching
