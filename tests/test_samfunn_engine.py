"""Tests for SamfunnEngine — SIR epidemiology as a flow model (L-042).

SIR is the flow model in pure form: susceptible -> infected -> recovered,
with R0 = beta/gamma as the threshold: R0 > 1 = outbreak (release),
R0 < 1 = damped (holding), R0 = 1 = the threshold itself. The engine is an
IDEALIZED homogeneous SIR — no age structure, no network,
no behaviour — and it says so itself. It is NOT an epidemiological
model competitor.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.samfunn import SamfunnEngine

PARAMS = {
    "beta": 0.3,       # 1/day — infection rate
    "gamma": 0.1,      # 1/day — recovery rate
    "N": 1.0e6,        # population
}


def test_r0_er_terskelverdien():
    """R0 = beta/gamma — above 1 is outbreak, below 1 damped."""
    e = SamfunnEngine()
    assert np.isclose(e.r0(PARAMS), 3.0)
    assert e.utbrudds_status(PARAMS) == "utbrudd"  # R0 > 1
    dempet = {**PARAMS, "beta": 0.05}
    assert e.r0(dempet) == 0.5
    assert e.utbrudds_status(dempet) == "dempet"


def test_r0_eksakt_1_er_terskelen():
    """R0 = 1 is the regime shift itself — neither outbreak nor damped,
    and it shall be reported as the threshold."""
    e = SamfunnEngine()
    terskel = {**PARAMS, "beta": 0.1}
    assert np.isclose(e.r0(terskel), 1.0)
    assert e.utbrudds_status(terskel) == "terskel"


def test_sir_dynamikk_bevarer_fraksjonssummen():
    """s + i + r = 1 at all times (fractions; the population numbers
    are S = N*s, I = N*i, R = N*r) — the flow does not leak."""
    e = SamfunnEngine()
    t = np.linspace(0, 30, 100)
    s, i, r = e.sir_bane(PARAMS, t, s0=0.999, i0=0.001)
    assert np.allclose(s + i + r, 1.0, atol=1e-9)


def test_epidemikurven_stiger_og_faller():
    """The outbreak curve: I rises to a peak and falls — the shape
    of a flow through a limited susceptible reservoir."""
    e = SamfunnEngine()
    t = np.linspace(0, 100, 200)
    s, i, r = e.sir_bane(PARAMS, t, s0=0.999, i0=0.001)
    topp = np.argmax(i)
    assert 0 < topp < len(t) - 1  # the peak inside the window
    assert i[topp] > i[0] and i[-1] < i[topp]


def test_compute_rapporterer_r0_per_parametre():
    e = SamfunnEngine()
    koord = np.array([[0.3, 0.1], [0.05, 0.1]])  # (beta, gamma) pair
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
