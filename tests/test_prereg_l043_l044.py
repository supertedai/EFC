"""Forseglings-test for L-043/L-044-pre-registreringen.

Mønsteret fra sealed_fs8_repro: forseglingen er en HASH som testes —
endringer i pre-reg-dokumentet etter forsegling feiler testen, og
krever et nytt dokument (ikke redigering).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

DOK = Path("docs/papers/efc/EFC_L043_L044_PreRegistration/README.md")
REGISTER = Path("docs/validation-ledger/data/evidence-register.json")

# Forseglet 2026-09-17 — UAVHENGIG forventet digest, hardkodet her
# (review-krav PR #452 r1: digesten må ikke beregnes dynamisk fra
# fila, ellers kan dokument OG register endres sammen og passere).
FORSEGLET = ("6dc7f912341529412e3f4e5c37d241e9"
             "28f683d35ce7aa50f5ee46ef820080a7")


def _fil_sha() -> str:
    return hashlib.sha256(
        DOK.read_text(encoding="utf-8").encode()).hexdigest()


def _register() -> dict:
    if not REGISTER.exists():
        return {}
    return json.loads(REGISTER.read_text(encoding="utf-8"))


def test_pre_reg_dokumentet_finnes():
    assert DOK.exists(), "pre-reg-dokumentet mangler"


def test_forseglingen_er_registrert():
    reg = _register()
    poster = reg.get("forseglinger", [])
    assert any(p.get("dok") == str(DOK) for p in poster), \
        "forseglingen mangler i evidence-registeret"


def test_forseglingen_matcher_registeret():
    reg = _register()
    for p in reg.get("forseglinger", []):
        if p.get("dok") == str(DOK):
            assert p.get("sha256") == FORSEGLET, (
                "registeret avviker fra den hardkodede digesten — "
                "endringer i register OG dokument kan ikke begge passere")
            return
    pytest.fail("forseglingen ikke funnet")


def test_filen_matcher_den_hardkodede_digesten():
    """Uavhengig digest-kontroll: filen selv må matche konstanten —
    redigering etter forsegling krever nytt dokument."""
    assert _fil_sha() == FORSEGLET, (
        "dokumentet er endret etter forsegling — et nytt dokument "
        "kreves, ikke redigering")


TESTPLAN = Path("docs/papers/efc/EFC_L043_L044_PreRegistration/testplan.md")


def test_lag_b_finnes_og_er_registrert():
    """To-lagsdesignet er håndhevbart: testplanen (Lag B) må finnes
    og være registrert i evidence-registeret (review-krav r3)."""
    assert TESTPLAN.exists(), "testplanen (Lag B) mangler"
    reg = _register()
    assert any(p.get("dok") == str(TESTPLAN)
               for p in reg.get("forseglinger", [])), \
        "Lag B er ikke registrert i evidence-registeret"


def test_lag_b_maaler_ingen_trengsel():
    """Ingen måling kan skje før Lag B er FORSEGLET — testen feiler
    hvis noen fjerner placeholder-statusen uten å forsegle, og feiler
    aldri for en korrekt forseglet eller korrekt åpen plan."""
    tekst = TESTPLAN.read_text(encoding="utf-8")
    reg = _register()
    post = next((p for p in reg.get("forseglinger", [])
                 if p.get("dok") == str(TESTPLAN)), None)
    forseglet = bool(post and post.get("sha256"))
    if "Status: FORSEGLET" in tekst:
        assert forseglet, ("testplanen erklærer FORSEGLET uten "
                           "SHA-registrering — forseglingen er ugyldig")
    else:
        assert "IKKE LÅST" in tekst, (
            "testplanen har verken FORSEGLET-status eller ærlig "
            "IKKE-LÅST-status")


def test_prediksjonene_har_falsifikatorer():
    """Hver prediksjon skal ha en eksplisitt falsifikator —
    KILL-matrise-disippelen."""
    tekst = DOK.read_text(encoding="utf-8")
    assert tekst.count("**Falsifikator:**") == 3, \
        "alle tre prediksjonene skal ha falsifikatorer"


def test_avhengigheten_er_deklarert():
    """P2s manglende datakilde skal være deklarert, ikke skjult."""
    tekst = DOK.read_text(encoding="utf-8")
    assert "ingen kilde på bussen ennå" in tekst
