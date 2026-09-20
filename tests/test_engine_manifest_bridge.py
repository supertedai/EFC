"""Test of the engine↔schema bridge (step 4).

WaterPhaseEngine's new method regime_node() must return a VALID
RegimeNode according to regime_node.schema.json — so that any EFCEngine
with this method is machine-coupled to the atlas's structure. The bridge
is generic: future engines get atlas coupling for free.

The local-global coupling (the empathy gate) is a MACHINE consistency
check: the engine's declared validity-domain numbers must match the
instance's h2o node numbers — not just look alike in text.

TDD: written before regime_node() exists — fails with AttributeError.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pytest

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from efc_inference.engine.water import WaterPhaseEngine  # noqa: E402

SCHEMA_PATH = _REPO / "schema" / "regime_node.schema.json"
INSTANCE_PATH = _REPO / "schema" / "regime_nodes.jsonld"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema not installed")

PARAMS = {
    "t_triple": 273.16,
    "p_triple": 611.657,
    "t_critical": 647.096,
    "p_critical": 22.064e6,
    "latent_vaporization_ref": 2.257e6,
    "t_vap_ref": 373.15,
    "p_vap_ref": 101325.0,
    "latent_fusion": 333550.0,
    "latent_sublimation": 2.834e6,
    "gas_constant": 461.5,
    "density_ice": 916.7,
    "density_water": 999.8,
    "p_ice_ih_max": 208.566e6,
    "t_sublim_min": 50.0,
}


def _schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _instance() -> dict:
    return json.loads(INSTANCE_PATH.read_text(encoding="utf-8"))


def _regime_node_schema() -> dict:
    s = _schema()
    return {
        "$schema": s["$schema"],
        "$defs": s["$defs"],
        "$ref": "#/$defs/RegimeNode",
    }


# --------------------------------------------------------------------------
# The bridge: the engine's self-description IS a regime node
# --------------------------------------------------------------------------

@requires_jsonschema
def test_engine_regime_node_is_valid():
    """regime_node() must validate against the RegimeNode definition in the schema."""
    node = WaterPhaseEngine().regime_node(PARAMS)
    jsonschema.Draft202012Validator(_regime_node_schema()).validate(node)


def test_engine_regime_node_has_engine_id():
    node = WaterPhaseEngine().regime_node(PARAMS)
    assert node["id"] == "efc.water_phase_engine"


def test_engine_regime_node_declares_its_law_form():
    node = WaterPhaseEngine().regime_node(PARAMS)
    assert "Clausius-Clapeyron" in node["regime"]["law_form"]


def test_manifest_contract_unchanged():
    """manifest() from step 1 must be untouched — backward compatible."""
    m = WaterPhaseEngine()
    manifest = m.manifest(PARAMS)
    assert manifest["name"]
    akser = {c["axis"] for c in manifest["couplings"]}
    assert {"node", "regime", "fase", "emergens", "proxy"} <= akser


# --------------------------------------------------------------------------
# Local-global coupling: machine consistency engine <-> atlas
# --------------------------------------------------------------------------

def test_engine_is_a_node_in_the_atlas():
    """The engine must stand as a node in regime_nodes.jsonld — not just in the code."""
    ids = {n["id"] for n in _instance()["nodes"]}
    assert "efc.water_phase_engine" in ids


def test_engine_carries_the_phase_nodes():
    """The engine carries the phase-boundary computation for the three phases (CARRIES)."""
    rels = _instance()["relations"]
    preds = {(r["subject"], r["predicate"], r["object"]) for r in rels}
    assert ("efc.water_phase_engine", "CARRIES", "h2o.solid") in preds
    assert ("efc.water_phase_engine", "CARRIES", "h2o.liquid") in preds
    assert ("efc.water_phase_engine", "CARRIES", "h2o.gas") in preds


# --------------------------------------------------------------------------
# Machine number consistency engine <-> atlas (the empathy gate)
# --------------------------------------------------------------------------
#
# Review finding 2026-09-17 (step 4): the previous test was a
# substring test — it said the bridge was "machine-verified" while it
# only looked for text fragments. This block compares NUMBERS: the
# engine's declared limits against the h2o nodes' numbers, both ways,
# and the engine's own atlas node against regime_node(). "50 K" and
# "50.0" are the same limit; "50" as part of "IAPWS R14-08" is a
# reference and is skipped.

# Curve names in the engine's declaration -> the h2o nodes the limit applies to.
GRENSE_TIL_NODER = {
    "vapour": ("h2o.liquid", "h2o.gas"),
    "melt": ("h2o.solid",),
    "sublimation": ("h2o.solid",),
}

# Numbers with a unit ("50 K", "208.566 MPa", "101325 Pa") — not prose numbers.
_TALL_MED_ENHET = re.compile(r"(\d+(?:[.,]\d+)?)\s*(K|MPa|Pa)\b")
_GRENSE = re.compile(r"(vapour|melt|sublimation)\s*\[([^\]]+)\]")


def _numbers(text: str) -> list:
    return [float(t.replace(",", "."))
            for t in re.findall(r"\d+(?:[.,]\d+)?", text)]


def _has(numbers: float, kandidater: list) -> bool:
    """Numeric equality — the atlas's "50" and the engine's "50.0" are the same limit."""
    return any(abs(numbers - k) <= 1e-9 * max(1.0, abs(numbers)) for k in kandidater)


def _limits(validity: str) -> dict:
    """The engine's declared limits, per curve name, as numbers.

    The limit may be written with a symbol ("t_triple"); the symbol is
    the parameter's name and the value lives in PARAMS — here only the
    numbers are read.
    """
    return {name: _numbers(body) for name, body in _GRENSE.findall(validity)}


def test_engine_declaration_carries_the_three_machine_readable_limits():
    """The declaration must have all three limits as NUMBERS — otherwise
    the tests below would have been empty (and the bridge "verified"
    without content)."""
    limits = _limits(
        WaterPhaseEngine().regime_node(PARAMS)["regime"]["validity"])
    assert set(limits) == set(GRENSE_TIL_NODER)
    for name, numbers in limits.items():
        assert numbers, f"{name}: no numbers in the limit"


def test_engine_declared_limits_are_the_atlas_nodes_limits():
    """FORWARD: every limit the engine declares must exist as a NUMBER in
    the validity text of the h2o node it applies to.

    Exception: 0 MPa — the natural zero, which the atlas does not cite.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    limits = _limits(node["regime"]["validity"])
    h2o = {n["id"]: n for n in _instance()["nodes"]}
    for name, nodes in GRENSE_TIL_NODER.items():
        for numbers in limits[name]:
            if numbers == 0.0:
                continue
            for nid in nodes:
                assert _has(numbers, _numbers(h2o[nid]["regime"]["validity"])), (
                    f"the engine declares {numbers} in «{name}», but {nid} "
                    f"does not mention it: {h2o[nid]['regime']['validity']}")


def test_atlas_node_numbers_are_numbers_the_engine_holds():
    """BACKWARD: every number WITH A UNIT in the h2o nodes' validity must be
    reproducible by the engine — from a declared limit or from a parameter.
    A number the atlas cites and the engine does not hold is a loose claim.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    limits = _limits(node["regime"]["validity"])
    engine_numbers = [t for numbers in limits.values() for t in numbers] + [
        float(v) for v in PARAMS.values()]
    h2o = {n["id"]: n for n in _instance()["nodes"]}
    for name, nodes in GRENSE_TIL_NODER.items():
        for nid in nodes:
            for raw, unit in _TALL_MED_ENHET.findall(
                    h2o[nid]["regime"]["validity"]):
                value = float(raw.replace(",", "."))
                assert _has(value, engine_numbers), (
                    f"{nid} cites {value} {unit}, but the engine does not "
                    f"hold that number (limits: {limits})")


def test_engine_node_and_its_atlas_node_agree_on_derived_fields():
    """The engine's OWN atlas node must carry the same parameter-derived
    fields that regime_node() gives — the same requirement step 11 places
    on the five cosmological engines (test_broer_matcher_atlas_maskinelt).

    Measured 2026-09-17: the water node failed the requirement — the
    atlas's validity was an OLDER text than the engine's (the engine was
    tightened in review 2026-09-16 and the atlas was not regenerated).
    Regeneration: scripts/maintenance/efc_bro_synk.py.

    Water is one case. The class — all 20 engines and ALL fields, with
    ownership split between engine and atlas — is tested in
    tests/test_bro_konvensjon.py, and the convention stands in
    scripts/maintenance/efc_bro_konvensjon.py.
    """
    node = WaterPhaseEngine().regime_node(PARAMS)
    atlas = {n["id"]: n for n in _instance()["nodes"]}["efc.water_phase_engine"]
    assert atlas["regime"]["validity"] == node["regime"]["validity"]
    assert atlas["regime"]["law_form"] == node["regime"]["law_form"]


def test_engine_regime_node_reflects_effective_params():
    """Review round 1: the self-description must be DERIVED from the
    effective parameters — with alternative parameters the node must
    declare the alternative limits, not the canonical ones."""
    alt = {
        **PARAMS,
        "t_vap_ref": 370.0,
        "p_ice_ih_max": 123.0e6,
        "t_sublim_min": 60.0,
        "watson_exponent": 0.5,
    }
    node = WaterPhaseEngine().regime_node(alt)
    text = node["regime"]["validity"] + node["regime"]["law_form"]
    assert "370" in text          # t_vap_ref is included
    assert "123" in text          # p_ice_ih_max is included (in MPa)
    assert "60" in text           # t_sublim_min is included
    assert "0.5" in text          # the watson exponent is included
    # ...and the canonical numbers must NOT stand there.
    assert "373.15" not in text
    assert "208.566" not in text
    assert "0.33" not in text
