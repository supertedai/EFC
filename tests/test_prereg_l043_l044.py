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
FORSEGLET = ("09f660b66bcf68f484e5a62e4056d734"
             "a2c0780c6a3d0b6b3e5a688dfcfef33e")


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
