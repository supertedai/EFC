"""Tests for the Homo Fluxus nodes in the atlas (L-006).

Homo Fluxus (the repo's own framework, DOI 32099389/31940604) shall
be placed in the atlas as nodes — the human's regimes in the EFC coordinates,
with the broad buffer logic explicitly marked as an ANALOGY (not
identity) to battery and water, in line with the rest of the atlas.
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

HOMO_NODER = [
    "homo.fluxus",
    "homo.homeostase_buffer",
    "homo.feber_regime",
    "homo.aksjonspotensial",
    "homo.hjerte_syklus",
]


def _atlas() -> dict:
    return json.loads(ATLAS.read_text(encoding="utf-8"))


def _node(navn: str) -> dict:
    for n in _atlas()["nodes"]:
        if n["id"] == navn:
            return n
    raise AssertionError(f"{navn} is missing from the atlas")


def test_homo_nodene_finnes():
    for navn in HOMO_NODER:
        node = _node(navn)
        assert node["regime"]["validity"].strip()
        assert node["regime"]["law_form"].strip()


def test_rc_terskelen_staar_med_verdi():
    """R_c ≈ 1/e ≈ 0.37 — the threshold between flow object and flow subject —
    shall stand with its value in the atlas."""
    node = _node("homo.fluxus")
    assert "0.37" in node["regime"]["validity"] or \
           "1/e" in node["regime"]["validity"]


def test_analogi_merking_til_batteri():
    """The homeostasis buffer is the broad buffer logic in the body —
    AN ANALOGY to the battery, not identity. It shall stand explicitly."""
    node = _node("homo.homeostase_buffer")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "batteri" in tekst
    assert "analogi" in tekst


def test_aksjonspotensialet_er_holding_release():
    """The neuron's membrane potential charges and releases — holding→release,
    the same shape as flares and earthquakes (analogy-marked)."""
    node = _node("homo.aksjonspotensial")
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert ("holding" in tekst and "release" in tekst) or \
           ("lad" in tekst and "utløs" in tekst)


def test_nodene_tilfredsstiller_skjemaet():
    """All the homo nodes shall be valid RegimeNodes."""
    if jsonschema is None:
        pytest.skip("jsonschema not installed")
    skjema = json.loads(SKJEMA.read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(skjema["$defs"]["RegimeNode"])
    for navn in HOMO_NODER:
        feil = sorted(validator.iter_errors(_node(navn)),
                      key=lambda e: list(e.path))
        assert not feil, f"{navn}: {[e.message for e in feil[:3]]}"


def test_relasjon_analogi_til_batteri_buffer():
    """The relation homo.homeostase_buffer ↔ batteri.buffer shall exist
    with an analogy predicate (not COUPLED_TO — that would be too
    strong)."""
    relasjoner = _atlas().get("relations", [])
    funnet = [
        r for r in relasjoner
        if (r["subject"] == "homo.homeostase_buffer" and
            r["object"] == "batteri.buffer")
        or (r["subject"] == "batteri.buffer" and
            r["object"] == "homo.homeostase_buffer")
    ]
    assert funnet, "the analogy relation to batteri.buffer is missing"
    for r in funnet:
        assert r["predicate"] in ("ANALOGOUS_TO", "ANALOGI_TIL")
