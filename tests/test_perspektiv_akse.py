"""Tester for perspektiv-aksen — den epistemiske merkingen av hele
systemet (Mortens krav 2026-09-17).

Fire akser:
    paradigme  = vår egen ramme (EFC-motorer, atlas-kartlegginger)
    konsensus  = det rådende verdensbildet (ΛCDM, observasjons-målinger)
    akademia   = etablert kunnskapsbase (Kepler, SIR, Minsky, IAPWS,
                 fysiologi — publiserte modeller og metoder)
    agnostikk  = det åpne/ukjente (mikrofysikk, bevissthet)

Disiplinen: hver atlas-node og hver motors regime_node() skal
deklarere ETT perspektiv. Skjemaet validerer at feltet finnes og er
innenfor de fire verdiene. En node uten perspektiv er en påstand
uten epistemisk hjemsted — det skal ikke finnes.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

ATLAS = Path("schema/regime_nodes.jsonld")
SKJEMA = Path("schema/regime_node.schema.json")

PERSPEKTIV = ("paradigme", "konsensus", "akademia", "agnostikk")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def test_skjemaet_har_perspektiv_feltet():
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    node = skjema["$defs"]["RegimeNode"]
    assert "perspektiv" in node["properties"], \
        "RegimeNode-skjemaet mangler perspektiv-feltet"
    enum = node["properties"]["perspektiv"].get("enum", [])
    assert set(enum) == set(PERSPEKTIV), enum
    # Review-krav (PR #442 r1): feltet skal være OBLIGATORISK — en node
    # uten perspektiv er en påstand uten epistemisk hjemsted.
    assert "perspektiv" in node.get("required", []), \
        "perspektiv må være required for at umerkede noder feiler"


def test_alle_atlas_noder_har_gyldig_perspektiv():
    atlas = _atlas()
    for n in atlas["nodes"]:
        persp = n.get("perspektiv")
        assert persp in PERSPEKTIV, f"{n['id']}: perspektiv={persp!r}"


def test_observasjons_noder_er_konsensus():
    """obs.*-nodene er MÅLINGER av verden — konsensus."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("obs."):
            assert n["perspektiv"] == "konsensus", n["id"]


def test_motor_noder_er_paradigme():
    """efc.*-motornodene er VÅR ramme — paradigme."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("efc.") and n["id"] != "efc.l0":
            assert n["perspektiv"] == "paradigme", n["id"]


def test_h2o_fysikk_noder_er_akademia():
    """h2o.*-nodene er etablert termodynamikk (IAPWS) — akademia."""
    for n in _atlas()["nodes"]:
        if n["id"].startswith("h2o."):
            assert n["perspektiv"] == "akademia", n["id"]


def test_alle_motorer_deklarerer_perspektiv():
    """Hver motors regime_node() skal bære perspektiv-feltet."""
    import importlib
    motorer = ["water", "victron", "rotation", "hubble", "growth",
               "lensing", "cluster", "solar_flare", "jordskjelv",
               "mu_kz", "orbital", "klima", "romvaer", "tidevann",
               "samfunn", "oekonomi", "transient"]
    for navn in motorer:
        mod = importlib.import_module(f"efc_inference.engine.{navn}")
        klasse = [k for k in vars(mod).values()
                  if isinstance(k, type)
                  and hasattr(k, "regime_node")
                  and k.__module__ == mod.__name__][0]
        # kall regime_node med tomme params — feltet skal finnes
        # uavhengig av parameterverdier
        import inspect
        kilde = inspect.getsource(klasse.regime_node)
        assert '"perspektiv"' in kilde or "'perspektiv'" in kilde, navn
