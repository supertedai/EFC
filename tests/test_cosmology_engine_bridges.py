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

ATLAS = Path("schema/regime_nodes.jsonld")

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


def test_hver_motor_har_regime_node_bro():
    for engine, params, node_id in KANONISKE:
        node = engine.regime_node(params)
        assert node["id"] == node_id
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_broer_matcher_atlas_maskinelt():
    """Motorenes selvbeskrivelse skal stemme med atlas-nodene — samme
    id, samme validity, samme law_form (med de kanoniske parametrene)."""
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    atlas_noder = {n["id"]: n for n in atlas["nodes"]}
    for engine, params, node_id in KANONISKE:
        node = engine.regime_node(params)
        assert node_id in atlas_noder, f"{node_id} mangler i atlaset"
        at = atlas_noder[node_id]
        assert at["regime"]["validity"] == node["regime"]["validity"]
        assert at["regime"]["law_form"] == node["regime"]["law_form"]


def test_stub_motorer_sier_stub():
    """Lensing og cluster er stubber — selvbeskrivelsen skal IKKE late
    som fysikken er der."""
    for engine, params, node_id in KANONISKE:
        if node_id in ("efc.lensing_engine", "efc.cluster_engine"):
            node = engine.regime_node(params)
            assert "stub" in node["regime"]["validity"].lower()


def test_relasjoner_til_observasjoner():
    """Koblingene fra atlas-relasjonene skal peke til kjente noder."""
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    id_map = {n["id"] for n in atlas["nodes"]}
    motorbroer = {nid for _, _, nid in KANONISKE}
    relasjoner = atlas.get("relations", [])
    for rel in relasjoner:
        if rel["subject"] in motorbroer:
            assert rel["object"] in id_map
            assert rel["predicate"] in ("COUPLED_TO", "OBSERVED_IN",
                                        "CARRIES", "EMERGES_FROM")
