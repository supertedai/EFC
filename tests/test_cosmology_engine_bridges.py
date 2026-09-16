"""Broer til de fem kosmologiske motorene (trinn 11).

Samme moenster som water (trinn 4) og victron (trinn 8): hver motor
beskriver seg selv som regime-node, og beskrivelsen skal stemme
MASKINELT med atlas-noden i schema/regime_nodes.jsonld.

Kanoniske parametre brukes i testene (og i atlaset):
Omega_m=0.3, H0=70, sigma8=0.8, alpha_cosmo=0.0, og rotation/lensing/
cluster sine egne kanoniske.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from efc_inference.engine.rotation import EFCRotation
from efc_inference.engine.hubble import EFCHubble
from efc_inference.engine.growth import EFCGrowth
from efc_inference.engine.lensing import EFCLensing
from efc_inference.engine.cluster import EFCCluster

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")

KANONISKE = [
    (EFCRotation(),
     {"entropy_scale": 1.0, "length_scale": 1.0,
      "flow_constant": 1.0, "velocity_scale": 200.0},
     "efc.rotation_engine"),
    (EFCHubble(),
     {"H0": 70.0, "Omega_m": 0.3, "alpha_cosmo": 0.0},
     "efc.hubble_engine"),
    (EFCGrowth(),
     {"Omega_m": 0.3, "H0": 70.0, "sigma8": 0.8, "alpha_cosmo": 0.0},
     "efc.growth_engine"),
    (EFCLensing(),
     {"alpha_lens": 0.0, "kappa_EFC": 0.0},
     "efc.lensing_engine"),
    (EFCCluster(),
     {"Omega_m": 0.3, "sigma8": 0.8, "alpha_cluster": 0.0},
     "efc.cluster_engine"),
]

# Eksakte koblinger som kreves av relasjonene i atlaset.
FORVENTEDE_RELASJONER = {
    "efc.rotation_engine": [("COUPLED_TO", "efc.l2")],
    "efc.hubble_engine": [("COUPLED_TO", "efc.l1"),
                          ("COUPLED_TO", "efc.l2"),
                          ("OBSERVED_IN", "obs.bao")],
    "efc.growth_engine": [("COUPLED_TO", "efc.l2"),
                          ("OBSERVED_IN", "obs.fsigma8"),
                          ("OBSERVED_IN", "obs.s8")],
    "efc.lensing_engine": [("OBSERVED_IN", "obs.cmb_lensing")],
    "efc.cluster_engine": [("OBSERVED_IN", "obs.cluster_hmf"),
                           ("OBSERVED_IN", "obs.cluster_mass")],
}


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def test_hver_motor_har_regime_node_bro():
    for engine, params, node_id in KANONISKE:
        node = engine.regime_node(params)
        assert node["id"] == node_id
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_broer_matcher_atlas_maskinelt():
    """Motorenes selvbeskrivelse skal stemme med atlas-nodene — samme
    id, samme validity, samme law_form (med de kanoniske parametrene)."""
    atlas = _atlas()
    atlas_noder = {n["id"]: n for n in atlas["nodes"]}
    for engine, params, node_id in KANONISKE:
        node = engine.regime_node(params)
        assert node_id in atlas_noder, f"{node_id} mangler i atlaset"
        at = atlas_noder[node_id]
        assert at["regime"]["validity"] == node["regime"]["validity"]
        assert at["regime"]["law_form"] == node["regime"]["law_form"]


def test_broer_tilfredsstiller_regime_node_skjemaet():
    """Hver bro skal vaere en gyldig RegimeNode etter skjemaet."""
    if jsonschema is None:
        pytest.skip("jsonschema ikke installert")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    definisjon = skjema["$defs"]["RegimeNode"]
    validator = jsonschema.Draft202012Validator(definisjon)
    for engine, params, node_id in KANONISKE:
        node = engine.regime_node(params)
        feil = sorted(validator.iter_errors(node), key=lambda e: list(e.path))
        if feil:
            meldinger = "; ".join(
                f"{list(e.path)}: {e.message}" for e in feil[:3])
            raise AssertionError(f"{node_id} feiler skjemaet: {meldinger}")


def test_validitet_endres_med_parametre():
    """Validity-strengen skal baere de EFFEKTIVE parametrene — ikke
    hardkodede tall (review-disiplin fra victron)."""
    for engine, params, _ in KANONISKE:
        node_a = engine.regime_node(params)
        endret = {k: (v + 1.0 if isinstance(v, float) else v)
                  for k, v in params.items()}
        node_b = engine.regime_node(endret)
        assert node_b["regime"]["validity"] != node_a["regime"]["validity"]


def test_stub_motorer_sier_stub_og_kaster():
    """Lensing og cluster er stubber: selvbeskrivelsen sier det, OG
    compute() hever NotImplementedError — ingen numerisk output."""
    import numpy as np
    for engine, params, node_id in KANONISKE:
        if node_id not in ("efc.lensing_engine", "efc.cluster_engine"):
            continue
        node = engine.regime_node(params)
        assert "stub" in node["regime"]["validity"].lower()
        with pytest.raises(NotImplementedError):
            engine.compute(params, np.array([1.0, 2.0]))


def test_relasjoner_eksakte():
    """Koblingene skal vaere NOEYAKTIG de forventede — ikke bare
    peke til kjente noder."""
    atlas = _atlas()
    funnet = {}
    for rel in atlas.get("relations", []):
        s = rel["subject"]
        if s in FORVENTEDE_RELASJONER:
            funnet.setdefault(s, []).append(
                (rel["predicate"], rel["object"]))
    for node_id, forventet in FORVENTEDE_RELASJONER.items():
        assert sorted(funnet.get(node_id, [])) == sorted(forventet), (
            f"{node_id}: fant {sorted(funnet.get(node_id, []))}, "
            f"forventet {sorted(forventet)}")
