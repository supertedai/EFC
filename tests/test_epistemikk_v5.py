"""Tests for epistemology v5 — the framing skills (Morten's corrections).

Two precisions Morten gave 2026-09-17:

1. "Is time a function of space, mass and velocity in LCDM?" — YES.
   Time is not one chosen coordinate; it is TWO chosen frames:
   local proper time (SI, caesium) and the cosmic time coordinate
   woven into spacetime (Lorentz mixing, gravitational dilation, a(t)).

2. "Mass is coupled to gravity in LCDM while in EFC gravity is
   entropy" — two GRAVITY frames:
   LCDM: mass -> curvature (the consensus spacetime);
   EFC: gravity = entropy (the mu channel is the coupling).

These distinctions must stand IN the nodes, not just in the head.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ATLAS = Path("schema/regime_nodes.jsonld")


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(nid: str) -> dict:
    for n in _atlas()["nodes"]:
        if n["id"] == nid:
            return n
    raise AssertionError(f"missing node {nid}")


def test_paradigme_tid_har_to_valgte_rammer():
    """Time is not one coordinate — SI proper time and spacetime time
    are two different chosen frames."""
    n = _node("efc.selv.paradigme_tid")
    options = n["maale_paradigme"]["alternativer"]
    assert any("romtid" in a for a in options), \
        "the romtid frame is missing from the alternatives"


def test_paradigme_masse_skiller_gravitasjons_rammene():
    """The EFC frame is the general one; LCDM is the SPECIAL CASE (mu -> 1)."""
    n = _node("efc.selv.paradigme_masse")
    options = n["maale_paradigme"]["alternativer"]
    assert any("entropi" in a for a in options), "the EFC frame is missing"
    assert any("SPESIALTILFELLE" in a for a in options), \
        "LCDM is not declared as a special case"


def test_kosmologi_motorene_deklarerer_romtid_veving():
    """LCDM-running engines must state that their time is spacetime-woven."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine",
                "efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        options = n["maale_paradigme"]["alternativer"]
        assert any("romtid" in a for a in options), nid


def test_efc_motorene_deklarerer_entropi_rammen():
    """The EFC variants (mu) must state that their gravity is entropy —
    not curvature."""
    for nid in ("efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("entropi" in a for a in assumes), nid


def test_lcdm_motorene_deklarerer_spesialtilfelle():
    """LCDM-running engines must declare the WHOLE limit — mu -> 1
    with alpha_cosmo = 0 and flat FLRW — not just one parameter."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("alpha_cosmo" in a and "mu -> 1" in a
                   for a in assumes), nid


def test_mu_kz_koblingen_er_deklarert_som_plan():
    """Review requirement (PR #447 r1): mu_kz -> growth is NOT implemented —
    the node must say so explicitly, not pretend the code couples them."""
    n = _node("efc.mu_kz_engine")
    assumes = n["ontology"]["assumes"]
    assert any("IKKE implementert" in a for a in assumes), (
        "the mu_kz node overclaims the coupling to growth")


def test_egentid_er_metrikk_og_verdenslinje():
    """Review requirement: proper time is determined by the metric and the
    world line — mass is a source of the metric, not a direct kinematic
    variable."""
    n = _node("efc.selv.paradigme_tid")
    options = n["maale_paradigme"]["alternativer"]
    assert any("METRIKKEN" in a and "verdenslinjen" in a for a in options), (
        "the formulation of proper time is imprecise")
