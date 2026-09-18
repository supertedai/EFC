"""Tests for EnerFlytEngine — society as energy flow (L-052).

Morten's principle (f): "the whole of society is one big energy-flow
diagram along all axes". The SIR engine models the fraction flux of
epidemiology; EnerFlytEngine models the ENERGY flux:

    dS/dt = P - C - L    (production - consumption - loss)

The buffer S is holding: abundance when P > C + L, scarcity when
consumption drains the buffer below the threshold. Release = the crisis
(rationing/redistribution).

Discipline from the engines' review rounds:
- fraction invariant: per-capita normalisation must not change the
  regime
- honesty: this is ONE axis of society — money, attention and trust are
  other currencies with explicitly NOT-conserving flows
- no crisis prediction: the model says when the buffer CROSSES the
  threshold, not when the crisis happens
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from efc_inference.engine.enerflyt import EnerFlytEngine

ATLAS = Path("schema/regime_nodes.jsonld")

BASE = {
    "produksjon": 100.0,     # P — energy units/time
    "forbruk": 90.0,         # C
    "tap": 5.0,              # L
    "buffer": 500.0,         # S0 — the initial stock
    "terskel": 50.0,         # the scarcity threshold
}


def test_overflod_regime():
    e = EnerFlytEngine()
    u = e.vurder(BASE)
    assert u["regime"] == "overflod", u
    assert u["dS_dt"] == pytest.approx(5.0)  # 100 - 90 - 5


def test_balanse_ved_null_drift():
    p = dict(BASE, produksjon=95.0)  # 95 - 90 - 5 = 0
    u = EnerFlytEngine().vurder(p)
    assert u["regime"] == "balanse", u


def test_knapphet_naar_forbruket_toemmer_bufferen():
    p = dict(BASE, forbruk=120.0, buffer=60.0)  # drift -25
    u = EnerFlytEngine().vurder(p)
    assert u["regime"] == "knapphet", u
    assert u["dS_dt"] == pytest.approx(-25.0)


def test_fraksjonsinvariant_per_kapita():
    """Same flow per capita = same regime — the normalisation is a
    scale, not a change of physics."""
    e = EnerFlytEngine()
    large = e.vurder(BASE)
    per_kapita = dict(BASE, produksjon=1.0, forbruk=0.9, tap=0.05,
                      buffer=5.0, terskel=0.5)
    small = e.vurder(per_kapita)
    assert large["regime"] == small["regime"] == "overflod"
    assert large["dS_dt"] / BASE["buffer"] == pytest.approx(
        small["dS_dt"] / per_kapita["buffer"])


def test_negativ_drift_med_tomt_lager_gir_nan():
    """The review pattern from the economy engine: negative drift with an
    empty store is not silent clipping — it is NaN."""
    p = dict(BASE, buffer=0.0, forbruk=120.0)
    u = EnerFlytEngine().vurder(p)
    assert math.isnan(u["buffer_etter"]), u


def test_ingen_krise_prediksjon_deklarert():
    e = EnerFlytEngine()
    n = e.regime_node(BASE)
    blob = json.dumps(n, ensure_ascii=False)
    assert "Predikerer IKKE" in blob


def test_er_merket_idealisert():
    n = EnerFlytEngine().regime_node(BASE)
    blob = json.dumps(n, ensure_ascii=False)
    assert "idealiser" in blob


def test_en_akse_av_mange_deklarert():
    """The engine must state that energy is ONE axis — other currencies
    are explicitly not conserving."""
    n = EnerFlytEngine().regime_node(BASE)
    text = json.dumps(n["ontology"], ensure_ascii=False)
    assert "penger" in text and "tillit" in text
