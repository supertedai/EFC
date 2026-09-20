"""Test of the generic regime-node schema and the H2O instance (step 2).

TDD: written BEFORE the schema exists — must fail on reading.

Anchoring (the schema's canonical source):
  regime/proxy/placement/episenter/compression are defined in
  "Regime-Bound Measurement in Complex Systems: Proxy, Placement, and
  Validity" (DOI 10.6084/m9.figshare.31564123, 2026-03-07) and in the
  meta reference docs/papers/meta/Proxy/. Morten's extensions (target,
  measurer, instrument, proxy chain, buffer/holding, phase, ontology,
  observer bandwidth, emergence loop, fractal, local-global coupling)
  are structural containers — the schema claims no physics.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

# Shared reader of the git tree — see scripts/maintenance/_repo_tre.py.
_MAINT = _REPO / "scripts" / "maintenance"
if str(_MAINT) not in sys.path:
    sys.path.insert(0, str(_MAINT))
from _repo_tre import filer as _tre_filer  # noqa: E402

SCHEMA_PATH = _REPO / "schema" / "regime_node.schema.json"
INSTANCE_PATH = _REPO / "schema" / "regime_nodes.jsonld"

# The private home address is never written out verbatim in this file. The
# file is itself tracked, and the regression guard below scans every tracked
# file — written out, the guard would have caught itself and would have
# needed an exception. Built from parts, no file is exempt, not even the
# guard itself.
HJEM = "Hassel" + "vegen"
POSTSTED = "4051 " + "Sola"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema not installed")


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _instance() -> dict:
    return json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------
# The schema
# --------------------------------------------------------------------------

@requires_jsonschema
def test_schema_is_valid_and_closed():
    s = _schema()
    jsonschema.Draft202012Validator.check_schema(s)
    assert s.get("additionalProperties") is False


def test_schema_requires_mortens_node_fields():
    s = _schema()
    node_req = set(s["$defs"]["RegimeNode"]["required"])
    assert {"id", "regime", "phase", "measure", "episenter", "buffer",
            "ontology", "observer", "emergence", "fractal",
            "coupling"} <= node_req


def test_schema_uses_canonical_episenter_spelling():
    """Review round 1: the canonical term in the source README and the PR is
    "episenter" — the English "epicenter" must not be a field name."""
    s = _schema()
    props = s["$defs"]["RegimeNode"]["properties"]
    assert "episenter" in props
    assert "epicenter" not in props


def test_context_maps_ids_and_relation_targets_to_iris():
    """Review round 1: the instance must be a linked JSON-LD graph —
    node ids and relation endpoints are IRI references, not loose text."""
    inst = _instance()
    ctx = inst["@context"]
    assert ctx.get("id") == "@id"
    assert ctx.get("subject") == {"@type": "@id"}
    assert ctx.get("object") == {"@type": "@id"}


def test_schema_requires_measurement_chain():
    s = _schema()
    measure = s["$defs"]["RegimeNode"]["properties"]["measure"]
    req = set(measure["required"])
    assert {"target", "measurer", "instrument", "proxy_chain",
            "placement", "compression"} <= req
    pc = measure["properties"]["proxy_chain"]
    assert pc["type"] == "array"


def test_schema_observer_bandwidth_is_explicit():
    """The observer sees a window of the spectrum — bandwidth is a required
    field, and the awareness status is a declared class, not a claim."""
    s = _schema()
    obs = s["$defs"]["RegimeNode"]["properties"]["observer"]
    assert {"bandwidth", "awareness"} <= set(obs["required"])
    awareness_enum = obs["properties"]["awareness"]["enum"]
    assert "instrument_window" in awareness_enum
    assert "hypothesis_open" in awareness_enum
    assert "not_claimed" in awareness_enum


def test_schema_relation_predicates_include_transition_and_emergence():
    s = _schema()
    preds = s["$defs"]["RegimeRelation"]["properties"]["predicate"]["enum"]
    assert "TRANSITIONS_TO" in preds
    assert "EMERGES_FROM" in preds
    assert "COUPLED_TO" in preds


# --------------------------------------------------------------------------
# The H2O instance
# --------------------------------------------------------------------------

@requires_jsonschema
def test_h2o_instance_validates_against_schema():
    jsonschema.Draft202012Validator(_schema()).validate(_instance())


def test_h2o_instance_has_four_phase_nodes():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical"} <= ids


def test_h2o_instance_has_triple_point_node():
    ids = {n["id"] for n in _instance()["nodes"]}
    assert "h2o.triple_point" in ids


def test_h2o_transitions_meet_at_triple_point():
    """All three phase transitions must be represented — that is what the
    triple point MEANS in this structure."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.liquid") in preds
    assert ("h2o.liquid", "TRANSITIONS_TO", "h2o.gas") in preds
    assert ("h2o.solid", "TRANSITIONS_TO", "h2o.gas") in preds


def test_every_node_declares_empathy_coupling():
    """Systemic empathy: every node must declare its local role AND its
    global reach — no node is only local."""
    inst = _instance()
    for n in inst["nodes"]:
        c = n["coupling"]
        assert c["local"], n["id"]
        assert c["global"], n["id"]


def test_every_node_has_ontology_source():
    """Ontological assumptions must have a source — not float loose."""
    inst = _instance()
    for n in inst["nodes"]:
        assert n["ontology"]["source"], n["id"]


def test_phase_nodes_declare_regime_validity():
    """Every phase node must say WHERE it applies (validity domain)."""
    inst = _instance()
    for n in inst["nodes"]:
        if n["id"].startswith("h2o.") and n["id"] != "h2o.triple_point":
            assert n["regime"]["validity"], n["id"]


# --------------------------------------------------------------------------
# Step 3: the rainbow — the genericity test (an emergence, not a phase)
# --------------------------------------------------------------------------

def test_rainbow_nodes_exist():
    """The rainbow as a second instance: light, droplet, dispersion, observer."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"lys.sol", "h2o.droplet", "optikk.dispersjon",
            "regnbue", "regnbue.observator"} <= ids


def test_rainbow_emerges_from_droplets_and_light():
    """The rainbow is an EMERGENCE of droplets + light — not a node beside them."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "EMERGES_FROM", "h2o.droplet") in preds
    assert ("regnbue", "EMERGES_FROM", "lys.sol") in preds


def test_rainbow_is_observed_through_observer():
    """Without an observer in anti-solar geometry it is just scattered light
    — the rainbow is OBSERVED_THROUGH the observer."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("regnbue", "OBSERVED_THROUGH", "regnbue.observator") in preds


def test_observer_bandwidth_states_visible_window():
    """"Everything is on an electromagnetic spectrum in total, the observer
    sees only a few nm" — the eye's window (400-700 nm) must stand in the
    observer's bandwidth."""
    inst = _instance()
    obs = next(n for n in inst["nodes"] if n["id"] == "regnbue.observator")
    bw = obs["observer"]["bandwidth"]
    assert "400" in bw and "700" in bw


def test_rainbow_is_emergent_pattern_not_phase():
    """The rainbow is not a thermodynamic phase — it is an emerged pattern.
    The schema must be able to carry emergences beyond phases."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert rb["phase"] == "emergent_pattern"


def test_rainbow_requires_liquid_droplets():
    """The rainbow requires FLUID (spherical) droplets — ice crystals give
    halos, not rainbows. The validity domain must say so."""
    inst = _instance()
    rb = next(n for n in inst["nodes"] if n["id"] == "regnbue")
    assert "requires liquid (spherical) droplets" in rb["regime"]["validity"].lower()


def test_existing_h2o_nodes_untouched():
    """The H2O nodes from step 2 must be untouched in the same atlas."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"h2o.solid", "h2o.liquid", "h2o.gas",
            "h2o.supercritical", "h2o.triple_point"} <= ids


# --------------------------------------------------------------------------
# Step 5: the L0–L3 cosmology — EFC's core into the same structure
# --------------------------------------------------------------------------

def test_l0_l3_nodes_exist():
    """EFC's four regimes must stand as nodes in the atlas."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"efc.l0", "efc.l1", "efc.l2", "efc.l3"} <= ids


def test_l0_l3_transition_chain():
    """The regimes form the chain L0→L1→L2→L3 via TRANSITIONS_TO."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("efc.l0", "TRANSITIONS_TO", "efc.l1") in preds
    assert ("efc.l1", "TRANSITIONS_TO", "efc.l2") in preds
    assert ("efc.l2", "TRANSITIONS_TO", "efc.l3") in preds


def test_l1_l2_is_declared_regime_transition():
    """L1→L2 is EFC's regime transition — the triple-point analogy. It must
    be declared in the transition relation's note (not just an edge)."""
    rels = _instance()["relations"]
    transition = next(
        (r for r in rels
         if (r["subject"], r["predicate"]) == ("efc.l1", "TRANSITIONS_TO")
         and r["object"] == "efc.l2"),
        None)
    assert transition is not None
    assert "regime transition" in transition["note"].lower()


def test_regimes_declare_s_values():
    """Every regime must declare its S value in validity (S→0, S≈0,
    S>0, S→1) — S is the regime coordinate, not decoration."""
    inst = _instance()
    nodes = {n["id"]: n for n in inst["nodes"]}
    assert "S" in nodes["efc.l0"]["regime"]["validity"]
    assert "S" in nodes["efc.l1"]["regime"]["validity"]
    assert "S" in nodes["efc.l2"]["regime"]["validity"]
    assert "S" in nodes["efc.l3"]["regime"]["validity"]


def test_observer_is_inside_l2():
    """The observer is INSIDE the system: we observe FROM L2 and look back
    in time to L1 (CMB) — the observer's placement is part of the structure,
    not a neutral vantage point."""
    inst = _instance()
    obs = next(n for n in inst["nodes"] if n["id"] == "efc.l2")
    # L2-noden skal selv deklarere observatorens posisjon.
    assert "observer" in obs["observer"]["bandwidth"].lower() or \
        "observer" in obs["episenter"].lower()


# --------------------------------------------------------------------------
# Step 6: Victron/battery — the buffer's electrical form
# --------------------------------------------------------------------------

def test_battery_nodes_exist():
    """The battery domain must stand as nodes: cell, charging, buffer,
    inverter — chemical regime, transition, storage, conversion."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert {"batteri.celle", "batteri.lading",
            "batteri.buffer", "batteri.inverter"} <= ids


def test_cc_cv_transition_declared():
    """The CC -> CV knee is the charging regime's phase transition — the
    triple-point analogy in electrical form. The transition must be declared
    in the relation between cell and charging."""
    rels = _instance()["relations"]
    transition = next(
        (r for r in rels
         if (r["subject"], r["predicate"], r["object"])
         == ("batteri.celle", "TRANSITIONS_TO", "batteri.lading")),
        None)
    assert transition is not None
    note = transition["note"].upper()
    assert "CC" in note and "CV" in note


def test_soc_is_regime_coordinate():
    """SOC is the battery's regime coordinate — flat in the middle, steep at
    the ends. The cell node must declare this in validity."""
    inst = _instance()
    cell = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    assert "SOC" in cell["regime"]["validity"]


def test_buffer_is_broad_electric():
    """The buffer is Morten's broad buffer in electrical form: homeostasis,
    storage, damping — not just a storage box."""
    inst = _instance()
    buffer_node = next(n for n in inst["nodes"] if n["id"] == "batteri.buffer")
    role = buffer_node["buffer"]["role"].lower()
    assert "homeost" in role or "lagr" in role or "energi" in role


def test_inverter_is_regime_converter():
    """The inverter is the regime converter: DC <-> AC — the transformation
    node where two regimes meet."""
    inst = _instance()
    inv = next(n for n in inst["nodes"] if n["id"] == "batteri.inverter")
    assert ("DC" in inv["emergence"]["loop"].upper()
            or "DC" in inv["regime"]["validity"].upper())


def test_proxy_chain_v_a_w_to_soc():
    """The Victron instruments measure V/A/W and derive SOC/SOH — the proxy
    chain must be declared in the cell node's measurement."""
    inst = _instance()
    cell = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    chain = " ".join(cell["measure"]["proxy_chain"]).upper()
    assert "V" in chain and "SOC" in chain


def test_soc_proxy_is_qualified():
    """SOC is an ESTIMATE, not a direct measurement: the proxy chain must
    separate coulomb counting (estimated) from OCV (only after rest) —
    otherwise we confuse charging voltage with rest voltage."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    kjede = " ".join(celle["measure"]["proxy_chain"]).upper()
    assert "COULOMB" in kjede and "AFTER REST" in kjede
    assert "ESTIMAT" in kjede or "ESTIMATOR" in kjede


def test_pack_vs_cell_declared():
    """The measurements are PACK voltage; the cell level is a BMS-internal
    proxy. The distinction must be declared in the cell node's validity."""
    inst = _instance()
    celle = next(n for n in inst["nodes"] if n["id"] == "batteri.celle")
    validity = celle["regime"]["validity"].upper()
    assert "PACK" in validity and "BMS" in validity


def test_inverter_is_bidirectional():
    """The inverter is a TWO-WAY converter: DC->AC (inverter mode) and
    AC->DC (charging mode) — not just the one direction."""
    inst = _instance()
    inv = next(n for n in inst["nodes"] if n["id"] == "batteri.inverter")
    tekst = (inv["regime"]["law_form"] + " " + inv["emergence"]["loop"]).upper()
    assert "DC -> AC" in tekst.replace("DC->AC", "DC -> AC").replace(
        "AC->DC", "AC -> DC") or ("DC->AC" in tekst and "AC->DC" in tekst)
    assert ("CHARGE MODE" in tekst or "CHARGING" in tekst)


def test_no_private_site_info_in_public_instance():
    """The public instance must NOT carry private site info: address, site
    ID or internal file path. Full provenance lives in a private artifact —
    a regression guard against reintroducing it here."""
    raw = INSTANCE_PATH.read_text(encoding="utf-8")
    for forbidden in [HJEM, "380961", "/opt/hermes-opus", "idSite",
                      "maalt 2026-09-16T13:41:57Z", "intern MCP-bro",
                      "feltkoder"]:
        assert forbidden not in raw, f"private info leaks: {forbidden}"


# --------------------------------------------------------------------------
# Step 7: BAO + coupling of cosmological observations to the regime nodes
# --------------------------------------------------------------------------

# The cosmological OBSERVATIONS in docs/validation-ledger/data/atlas.json
# (instrument-borne measurements, not model parameterisations). The value is
# the LIST of regime nodes the observation is coupled to — bridge
# observations (bao, isw, h0_tension) carry two regimes. The atlas's L labels
# are a DIFFERENT axis (layer axis) than the phase chain efc.l0-l3; every
# node declares both.
KOSMOLOGISKE_OBSERVASJONER = {
    "obs.bao": ["efc.l1", "efc.l2"],   # r_d frozen in L1, measured in L2
    "obs.cmb_tt": ["efc.l1"],
    "obs.cmb_lensing": ["efc.l2"],     # lenses L2 structure
    "obs.bbn": ["efc.l1"],             # the phase chain's earliest reading
    "obs.fsigma8": ["efc.l2"],
    "obs.s8": ["efc.l2"],
    "obs.eg": ["efc.l2"],
    "obs.isw": ["efc.l1", "efc.l2"],   # cross-regime
    "obs.ksz": ["efc.l2"],
    "obs.cluster_mass": ["efc.l2"],
    "obs.cluster_hmf": ["efc.l2"],
    "obs.rar": ["efc.l2"],
    "obs.bullet": ["efc.l2"],
    "obs.satellites": ["efc.l2"],
    "obs.jwst_ems": ["efc.l2"],
    "obs.gw_ct": ["efc.l2"],
    "obs.pta_gwb": ["efc.l2"],
    "obs.h0_tension": ["efc.l1", "efc.l2"],  # the tension BETWEEN the regimes
    "obs.w0wa": ["efc.l3"],
    "obs.cc": ["efc.l3"],
}


def test_cosmological_observation_nodes_exist():
    """Every cosmological observation in the atlas must stand as a node."""
    ids = {n["id"] for n in _instance()["nodes"]}
    for obs_id in KOSMOLOGISKE_OBSERVASJONER:
        assert obs_id in ids, f"missing node: {obs_id}"


def test_observations_are_coupled_to_regimes():
    """Every observation must be coupled to its regime(s) with OBSERVED_IN —
    not just lie loose in the atlas."""
    rels = _instance()["relations"]
    coupled = {(r["subject"], r["object"])
               for r in rels if r["predicate"] == "OBSERVED_IN"}
    for obs_id, regimes in KOSMOLOGISKE_OBSERVASJONER.items():
        for regime in regimes:
            assert (obs_id, regime) in coupled, \
                f"missing OBSERVED_IN coupling: {obs_id} -> {regime}"


def test_bao_is_standard_ruler():
    """The BAO node must declare the sound horizon r_d as the standard ruler
    — the only known physical length in cosmology."""
    inst = _instance()
    bao = next(n for n in inst["nodes"] if n["id"] == "obs.bao")
    text = (bao["regime"]["validity"] + " " + bao["episenter"]).upper()
    assert "R_D" in text or "STANDARDLINJAL" in text or \
        "STANDARD RULER" in text or "LYDHORISONT" in text


def test_bao_declares_lag_axis_vs_phase_chain():
    """The BAO node must declare that the atlas's L axis is a DIFFERENT
    division than the regime nodes' phase chain — the axes are not mixed."""
    inst = _instance()
    bao = next(n for n in inst["nodes"] if n["id"] == "obs.bao")
    kilde = bao["ontology"]["source"].lower()
    assert "different axis" in kilde and "phase chain" in kilde


def test_observation_nodes_sourced_from_atlas():
    """Every observation node must point to atlas.json as its source — the
    coupling is machine-anchored, not ad hoc."""
    inst = _instance()
    nodes = {n["id"]: n for n in inst["nodes"]}
    for obs_id in KOSMOLOGISKE_OBSERVASJONER:
        source = nodes[obs_id]["ontology"]["source"].lower()
        assert "atlas.json" in source or "validation-ledger" in source, \
            f"{obs_id}: source does not point to the atlas"


# Forbidden strings for the guard below, built from the same parts as above.
FORBUDTE_ADRESSER = (HJEM, POSTSTED, HJEM + " 5")


def test_ingen_privat_info_i_hele_repoet():
    """Regression guard (extended 2026-09-17): the home address must not exist
    in ANY tracked file — the guard covered only the schema folder, and
    efc-toolkit leaked address + phone in 13 files.

    Reads the git tree, not the disk (`_repo_tre`). An `rglob` over the work
    tree found `.worktrees/` in the main clone — gitignored, but on disk — and
    failed the test on files that are not in the repo.
    """
    for path in _tre_filer(_REPO):
        if path.suffix.lower() in (".csv", ".png", ".pdf", ".jpg", ".pyc"):
            continue  # scientific data / compiled cache
        try:
            raw = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for forbidden in FORBUDTE_ADRESSER:
            if forbidden in raw:
                raise AssertionError(
                    f"private address leaks: {path.relative_to(_REPO).as_posix()}")


def test_ingen_tomme_redaksjons_felt_i_toolkit():
    """Review requirement PR #455 r2: the edit must not leave
    "field": , behind — the field must be removed, not emptied."""
    for path in Path("docs/papers/efc").rglob("*"):
        if not path.is_file() or path.suffix not in (".json", ".jsonld"):
            continue
        raw = path.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'"[^"]+"\s*:\s*,', raw):
            raise AssertionError(f"empty field after edit: {path}")
