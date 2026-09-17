"""Tester for OekonomiEngine — Minskys finansregimer (L-041).

Minskys finansielle ustabilitetshypotese er holding→release i
finans: stabilitet avler tillit -> gjeld vokser -> hedge ->
spekulativ -> Ponzi -> krise. De stabile årene ER holdingen som
bygger bufferen til utløsningen. Motoren er en IDEALISERT
regime-klassifisering — IKKE en økonomisk modell-konkurrent, og
det står i selvbeskrivelsen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.oekonomi import OekonomiEngine

PARAMS = {
    "rente": 0.05,           # 1/år — lånerenten
    "inntektsavkastning": 0.08,  # 1/år — avkastningen på inntekten
    "gjeldsgrad_hedge": 2.0,  # terskel: gjeld/inntekt for hedge->spekulativ
    "gjeldsgrad_ponzi": 5.0,  # terskel: spekulativ->ponzi
}


def test_regime_klassifisering():
    """Hedge: inntektene dekker gjeld OG renter. Spekulativ: dekker
    rentene, må rulle gjelden. Ponzi: dekker ingen av delene."""
    e = OekonomiEngine()
    assert e.regime(PARAMS, gjeldsgrad=1.0) == "hedge"
    assert e.regime(PARAMS, gjeldsgrad=3.0) == "spekulativ"
    assert e.regime(PARAMS, gjeldsgrad=6.0) == "ponzi"


def test_gjeldsgraden_drifter_i_stabile_perioder():
    """Minsky-momentet: i stabile perioder vokser gjelden raskere enn
    inntekten — gjeldsgraden drifter oppover mot tersklene."""
    e = OekonomiEngine()
    g0 = 1.5
    g_etter = e.gjeldsgrad_drift(PARAMS, g0, stabile_aar=10)
    assert g_etter > g0  # stabilitet bygger bufferen til krisen


def test_minsky_momentet_er_maalet():
    """Momentet: desto lengre stabilitet, desto nærmere terskelen —
    «stabilitet er destabiliserende» som en målbar drift."""
    e = OekonomiEngine()
    kort = e.gjeldsgrad_drift(PARAMS, 1.5, stabile_aar=2)
    lang = e.gjeldsgrad_drift(PARAMS, 1.5, stabile_aar=20)
    assert lang > kort


def test_utlosning_ved_ponzi_terskel():
    """Krisen er utløsningen: når gjeldsgraden krysser ponzi-terskelen,
    rapporterer motoren regimeskiftet (holding -> release)."""
    e = OekonomiEngine()
    g = 1.0
    for _ in range(30):
        g = e.gjeldsgrad_drift(PARAMS, g, stabile_aar=1)
    assert e.regime(PARAMS, g) in ("spekulativ", "ponzi")


def test_compute_rapporterer_regime_per_gjeldsgrad():
    e = OekonomiEngine()
    ut = e.compute(PARAMS, np.array([1.0, 3.0, 6.0]))
    assert ut.shape == (3,)
    # koder: 0=hedge, 1=spekulativ, 2=ponzi
    assert ut[0] == 0 and ut[1] == 1 and ut[2] == 2


def test_regime_node_selvbeskrivelse():
    e = OekonomiEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.oekonomi_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealis" in tekst
    assert "ikke en økonomisk" in tekst or "ikke økonomisk" in tekst
    assert "minsky" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
