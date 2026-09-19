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
    # K6 (10087393): the engine is observed THROUGH, so this edge lives on the
    # observation (`obs.bao OBSERVED_THROUGH efc.hubble_engine`), not on the
    # engine. The inverted form was the defect, not an expectation.
    "efc.hubble_engine": [("COUPLED_TO", "efc.l1"),
                          ("COUPLED_TO", "efc.l2")],
    "efc.growth_engine": [("COUPLED_TO", "efc.l2"),],
    # K6: the edge now lives on the observation (see the test below).
    "efc.lensing_engine": [],
    "efc.cluster_engine": [],
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


def test_the_edge_to_the_engine_lives_on_the_observation() -> None:
    """K6 (10087393): `obs.X OBSERVED_THROUGH efc.Y`, not the other way round.

    The six inverted `OBSERVED_IN` edges (engine as subject) were renamed to
    `OBSERVED_THROUGH`, because the direction was the defect. This test holds
    the corrected pairs where they now live, so removing them from the engines'
    expectation lists above cannot silently drop the relation.
    """
    import json as _json
    from pathlib import Path as _Path

    atlas = _Path(__file__).resolve().parents[1] / "schema" / "regime_nodes.jsonld"
    kanter = {(r["subject"], r["predicate"], r["object"])
              for r in _json.loads(atlas.read_text(encoding="utf-8"))["relations"]}
    par = [("obs.bao", "efc.hubble_engine"),
           ("obs.fsigma8", "efc.growth_engine"),
           ("obs.s8", "efc.growth_engine"),
           ("obs.cmb_lensing", "efc.lensing_engine"),
           ("obs.cluster_hmf", "efc.cluster_engine"),
           ("obs.cluster_mass", "efc.cluster_engine")]
    mangler = [x for x in par if (x[0], "OBSERVED_THROUGH", x[1]) not in kanter]
    assert not mangler, (
        f"these observations do not carry the edge to their engine: {mangler}")
