"""Tester for SamfunnEngine — SIR-epidemiologi som flytmodell (L-042).

SIR er flytmodellen i ren form: mottagelige -> smittede -> friske,
med R0 = beta/gamma som terskelen: R0 > 1 = utbrudd (release),
R0 <= 1 = dempet (holding). Motoren er en IDEALISERT homogen SIR —
ingen aldersstruktur, ingen nettverk, ingen atferd — og den sier
det selv. Den er IKKE en epidemiologisk modell-konkurrent.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.samfunn import SamfunnEngine

PARAMS = {
    "beta": 0.3,       # 1/døgn — smitterate
    "gamma": 0.1,      # 1/døgn — tilfriskningsrate
    "N": 1.0e6,        # populasjon
}


def test_r0_er_terskelverdien():
    """R0 = beta/gamma — over 1 er utbrudd, under 1 dempet."""
    e = SamfunnEngine()
    assert np.isclose(e.r0(PARAMS), 3.0)
    assert e.utbrudds_status(PARAMS) == "utbrudd"  # R0 > 1
    dempet = {**PARAMS, "beta": 0.05}
    assert e.r0(dempet) == 0.5
    assert e.utbrudds_status(dempet) == "dempet"


def test_r0_eksakt_1_er_terskelen():
    """R0 = 1 er selve regimeskiftet — verken utbrudd eller dempet,
    og det skal rapporteres som terskelen."""
    e = SamfunnEngine()
    terskel = {**PARAMS, "beta": 0.1}
    assert np.isclose(e.r0(terskel), 1.0)
    assert e.utbrudds_status(terskel) == "terskel"


def test_sir_dynamikk_bevarer_populasjon():
    """S + I + R = N til enhver tid — flyten lekker ikke."""
    e = SamfunnEngine()
    t = np.linspace(0, 30, 100)
    s, i, r = e.sir_bane(PARAMS, t, s0=0.999, i0=0.001)
    assert np.allclose(s + i + r, 1.0, atol=1e-9)


def test_epidemikurven_stiger_og_faller():
    """Utbruddskurven: I stiger til et toppunkt og faller — formen
    på en flyt gjennom et begrenset mottagelig-reservoar."""
    e = SamfunnEngine()
    t = np.linspace(0, 100, 200)
    s, i, r = e.sir_bane(PARAMS, t, s0=0.999, i0=0.001)
    topp = np.argmax(i)
    assert 0 < topp < len(t) - 1  # toppunkt inne i vinduet
    assert i[topp] > i[0] and i[-1] < i[topp]


def test_compute_rapporterer_r0_per_parametre():
    e = SamfunnEngine()
    koord = np.array([[0.3, 0.1], [0.05, 0.1]])  # (beta, gamma)-par
    ut = e.compute(PARAMS, koord)
    assert ut.shape == (2,)
    assert np.isclose(ut[0], 3.0)
    assert np.isclose(ut[1], 0.5)


def test_regime_node_selvbeskrivelse():
    e = SamfunnEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.samfunn_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealis" in tekst
    assert "ikke en epidemiologisk" in tekst or \
           "ikke epidemiologisk" in tekst
    assert "sir" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
