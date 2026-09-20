"""Tests for OekonomiEngine — Minsky's finance regimes (L-041).

Minsky's financial instability hypothesis is holding to release in
finance: stability breeds confidence -> debt grows -> hedge ->
speculative -> Ponzi -> crisis. The stable years ARE the holding that
builds the buffer for the release. The engine is an IDEALISED regime
classification — NOT an economic model competitor, and it says so in
its self-description.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.oekonomi import OekonomiEngine

PARAMS = {
    "rente": 0.05,           # 1/year — the lending rate
    "inntektsavkastning": 0.08,  # 1/year — the return on income
    "gjeldsgrad_hedge": 2.0,  # threshold: debt/income for hedge->speculative
    "gjeldsgrad_ponzi": 5.0,  # threshold: speculative->ponzi
}


def test_regime_klassifisering():
    """Hedge: income covers debt AND interest. Speculative: covers the
    interest, must roll over the debt. Ponzi: covers neither."""
    e = OekonomiEngine()
    assert e.regime(PARAMS, gjeldsgrad=1.0) == "hedge"
    assert e.regime(PARAMS, gjeldsgrad=3.0) == "spekulativ"
    assert e.regime(PARAMS, gjeldsgrad=6.0) == "ponzi"


def test_gjeldsgraden_drifter_i_stabile_perioder():
    """The Minsky moment: in stable periods the debt grows faster than
    the income — the leverage drifts upward towards the thresholds."""
    e = OekonomiEngine()
    g0 = 1.5
    g_etter = e.gjeldsgrad_drift(PARAMS, g0, stabile_aar=10)
    assert g_etter > g0  # stability builds the buffer for the crisis


def test_minsky_momentet_er_maalet():
    """The moment: the longer the stability, the closer the threshold —
    "stability is destabilising" as a measurable drift."""
    e = OekonomiEngine()
    kort = e.gjeldsgrad_drift(PARAMS, 1.5, stabile_aar=2)
    lang = e.gjeldsgrad_drift(PARAMS, 1.5, stabile_aar=20)
    assert lang > kort


def test_utlosning_ved_ponzi_terskel():
    """The crisis is the release: when the leverage crosses the ponzi
    threshold, the engine reports the regime shift (holding -> release)."""
    e = OekonomiEngine()
    g = 1.0
    for _ in range(30):
        g = e.gjeldsgrad_drift(PARAMS, g, stabile_aar=1)
    assert e.regime(PARAMS, g) in ("spekulativ", "ponzi")


def test_compute_rapporterer_regime_per_gjeldsgrad():
    e = OekonomiEngine()
    ut = e.compute(PARAMS, np.array([1.0, 3.0, 6.0]))
    assert ut.shape == (3,)
    # codes: 0=hedge, 1=speculative, 2=ponzi
    assert ut[0] == 0 and ut[1] == 1 and ut[2] == 2


def test_regime_node_selvbeskrivelse():
    e = OekonomiEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.oekonomi_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealis" in tekst
    assert "not an economic model competitor" in tekst
    assert "minsky" in tekst
    assert node["regime"]["law_form"].strip()


def test_avgresning_minsky_og_ikke_prediksjon():
    """Blocking requirement from review: Minsky is ONE tradition among
    several, and the model does NOT predict the timing of crises — both
    parts must appear in the self-description and ontology.source."""
    e = OekonomiEngine()
    node = e.regime_node(PARAMS)
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "one tradition among several" in tekst
    assert "does not predict the timing or occurrence of crises" in tekst


def test_negativ_drift_er_aerlig_nan():
    """Without positive drift the Minsky moment is undefined — NaN, not
    a silent clipping to a standstill."""
    e = OekonomiEngine()
    umulig = {**PARAMS, "inntektsavkastning": 0.20}  # the gap > the confidence term
    ut = e.gjeldsgrad_drift(umulig, 1.5, stabile_aar=10)
    assert np.isnan(ut)


import json  # noqa: E402
