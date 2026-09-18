"""Tester for epistemikk v5 — ramme-skillene (Mortens korreksjoner).

To presisjoner Morten ga 2026-09-17:

1. «Tid er funksjon av rom, masse og hastighet i LCDM?» — JA.
   Tiden er ikke ett valgt koordinat; det er TO valgte rammer:
   lokal egentid (SI, cesium) og kosmisk tidskoordinat vevd inn i
   romtid (Lorentz-blanding, gravitasjonell dilatasjon, a(t)).

2. «Masse er koblet til gravitasjon i LCDM mens i EFC er
   gravitasjon entropi» — to GRAVITASJONS-rammer:
   LCDM: masse -> krumning (konsensus-romtiden);
   EFC: gravitasjon = entropi (mu-kanalen er koblingen).

Disse skillene skal stå I nodene, ikke bare i hodet.
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
    raise AssertionError(f"mangler node {nid}")


def test_paradigme_tid_har_to_valgte_rammer():
    """Tiden er ikke ett koordinat — SI-egentiden og romtid-tiden er
    to ulike valgte rammer."""
    n = _node("efc.selv.paradigme_tid")
    alt = n["maale_paradigme"]["alternativer"]
    assert any("spacetime" in a for a in alt), \
        "romtid-rammen mangler i alternativene"


def test_paradigme_masse_skiller_gravitasjons_rammene():
    """EFC-rammen er den generelle; LCDM er SPESIALTILFELET (mu -> 1)."""
    n = _node("efc.selv.paradigme_masse")
    alt = n["maale_paradigme"]["alternativer"]
    assert any("entropi" in a for a in alt), "EFC-rammen mangler"
    assert any("SPECIAL CASE" in a for a in alt), \
        "LCDM er ikke deklarert som spesialtilfelle"


def test_kosmologi_motorene_deklarerer_romtid_veving():
    """LCDM-kjørende motorer skal si at tiden deres er romtid-vevd."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine",
                "efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        alt = n["maale_paradigme"]["alternativer"]
        assert any("spacetime" in a for a in alt), nid


def test_efc_motorene_deklarerer_entropi_rammen():
    """EFC-variantene (mu) skal si at deres gravitasjon er entropi —
    ikke krumning."""
    for nid in ("efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("entropy" in a for a in assumes), nid


def test_lcdm_motorene_deklarerer_spesialtilfelle():
    """LCDM-kjørende motorer skal deklarere HELE grensen — mu -> 1
    med alpha_cosmo = 0 og flat FLRW — ikke bare én parameter."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("alpha_cosmo" in a and "mu -> 1" in a
                   for a in assumes), nid


def test_mu_kz_koblingen_er_deklarert_som_plan():
    """Review-krav (PR #447 r1): mu_kz -> growth er IKKE implementert —
    noden skal si det eksplisitt, ikke late som koden kobler."""
    n = _node("efc.mu_kz_engine")
    assumes = n["ontology"]["assumes"]
    assert any("NOT implemented" in a for a in assumes), (
        "mu_kz-noden overpåstår koblingen til growth")


def test_egentid_er_metrikk_og_verdenslinje():
    """Review-krav: egentiden bestemmes av metrikken og verdenslinjen —
    masse er kilde til metrikken, ikke direkte kinematisk variabel."""
    n = _node("efc.selv.paradigme_tid")
    alt = n["maale_paradigme"]["alternativer"]
    assert any("METRIC" in a and "worldline" in a for a in alt), (
        "formuleringen av egentiden er upresis")
