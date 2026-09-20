"""Sealing test for the L-043/L-044 pre-registration.

The pattern from sealed_fs8_repro: the seal is a HASH that is tested —
changes to the pre-reg document after sealing fail the test, and
require a new document (not editing).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

DOK = Path("docs/papers/efc/EFC_L043_L044_PreRegistration/README.md")
REGISTER = Path("docs/validation-ledger/data/evidence-register.json")

# Sealed 2026-09-17 — INDEPENDENT expected digest, hardcoded here
# (review requirement PR #452 r1: the digest must not be computed
# dynamically from the file, else document AND register change together).
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
    assert DOK.exists(), "the pre-reg document is missing"


def test_forseglingen_er_registrert():
    reg = _register()
    poster = reg.get("forseglinger", [])
    assert any(p.get("dok") == str(DOK) for p in poster), \
        "the seal is missing from the evidence register"


def test_forseglingen_matcher_registeret():
    reg = _register()
    for p in reg.get("forseglinger", []):
        if p.get("dok") == str(DOK):
            assert p.get("sha256") == FORSEGLET, (
                "the register differs from the hardcoded digest — "
                "changes to register AND document cannot both pass")
            return
    pytest.fail("the seal was not found")


def test_filen_matcher_den_hardkodede_digesten():
    """Independent digest check: the file itself must match the constant —
    editing after sealing requires a new document."""
    assert _fil_sha() == FORSEGLET, (
        "the document was changed after sealing — a new document "
        "is required, not editing")


TESTPLAN = Path("docs/papers/efc/EFC_L043_L044_PreRegistration/testplan.md")


def test_lag_b_finnes_og_er_registrert():
    """The two-layer design is enforceable: the test plan (Lag B) must exist
    and be registered in the evidence register (review requirement r3)."""
    assert TESTPLAN.exists(), "the test plan (Lag B) is missing"
    reg = _register()
    assert any(p.get("dok") == str(TESTPLAN)
               for p in reg.get("forseglinger", [])), \
        "Lag B is not registered in the evidence register"


def test_lag_b_maaler_ingen_trengsel():
    """No measurement may happen before Lag B is SEALED — the test fails
    if someone removes the placeholder status without sealing, and never
    fails for a correctly sealed or correctly open plan."""
    tekst = TESTPLAN.read_text(encoding="utf-8")
    reg = _register()
    post = next((p for p in reg.get("forseglinger", [])
                 if p.get("dok") == str(TESTPLAN)), None)
    forseglet = bool(post and post.get("sha256"))
    if "Status: FORSEGLET" in tekst:
        assert forseglet, ("the test plan declares FORSEGLET without "
                           "SHA registration — the seal is invalid")
    else:
        assert "IKKE LÅST" in tekst, (
            "the test plan has neither a FORSEGLET status nor an honest "
            "IKKE-LÅST status")


def test_prediksjonene_har_falsifikatorer():
    """Every prediction must have an explicit falsifier —
    the KILL matrix discipline."""
    tekst = DOK.read_text(encoding="utf-8")
    assert tekst.count("**Falsifikator:**") == 3, \
        "all three predictions must have falsifiers"


def test_avhengigheten_er_deklarert():
    """P2's missing data source must be declared, not hidden."""
    tekst = DOK.read_text(encoding="utf-8")
    assert "ingen kilde på bussen ennå" in tekst
