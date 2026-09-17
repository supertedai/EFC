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
    assert any("romtid" in a for a in alt), \
        "romtid-rammen mangler i alternativene"


def test_paradigme_masse_skiller_gravitasjons_rammene():
    """EFC-rammen er den generelle; LCDM er SPESIALTILFELET (mu -> 1)."""
    n = _node("efc.selv.paradigme_masse")
    alt = n["maale_paradigme"]["alternativer"]
    assert any("entropi" in a for a in alt), "EFC-rammen mangler"
    assert any("SPESIALTILFELLE" in a for a in alt), \
        "LCDM er ikke deklarert som spesialtilfelle"


def test_kosmologi_motorene_deklarerer_romtid_veving():
    """LCDM-kjørende motorer skal si at tiden deres er romtid-vevd."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine",
                "efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        alt = n["maale_paradigme"]["alternativer"]
        assert any("romtid" in a for a in alt), nid


def test_efc_motorene_deklarerer_entropi_rammen():
    """EFC-variantene (mu) skal si at deres gravitasjon er entropi —
    ikke krumning."""
    for nid in ("efc.growth_engine", "efc.mu_kz_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("entropi" in a for a in assumes), nid


def test_lcdm_motorene_deklarerer_spesialtilfelle():
    """LCDM-kjørende motorer skal si at de kjører mu -> 1-grensen —
    ikke en konkurrerende ramme."""
    for nid in ("efc.rotation_engine", "efc.hubble_engine",
                "efc.lensing_engine", "efc.cluster_engine"):
        n = _node(nid)
        assumes = n["ontology"]["assumes"]
        assert any("SPESIALTILFELET" in a for a in assumes), nid
