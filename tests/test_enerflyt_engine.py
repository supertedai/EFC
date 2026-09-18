"""Tester for EnerFlytEngine — samfunnet som energiflyt (L-052).

Mortens prinsipp (f): «hele samfunnet er en stor energyflyt diagram i
alle akser». SIR-motoren modellerer epidemiologiens fraksjonsfluks;
EnerFlytEngine modellerer ENERGI-fluksen:

    dS/dt = P - C - L    (produksjon - forbruk - tap)

Bufferen S er holding: overflod når P > C + L, knapphet når
forbruket tømmer bufferen under terskelen. Release = krisen
(rasjonering/omfordeling).

Disiplin fra motorenes review-runder:
- fraksjonsinvariant: per-kapita-normalisering skal ikke endre
  regimet
- ærlighet: dette er ÉN akse av samfunnet — penger, oppmerksomhet
  og tillit er andre valutaer med eksplisitt IKKE-konservering
- ingen krise-prediksjon: modellen sier når bufferen KRYSSER
  terskelen, ikke når krisen inntreffer
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from efc_inference.engine.enerflyt import EnerFlytEngine

ATLAS = Path("schema/regime_nodes.jsonld")

BASE = {
    "produksjon": 100.0,     # P — enheter energi/tid
    "forbruk": 90.0,         # C
    "tap": 5.0,              # L
    "buffer": 500.0,         # S0 — startbeholdningen
    "terskel": 50.0,         # knapphetsgrensen
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
    """Samme flyt per kapita = samme regime — normaliseringen er en
    skala, ikke en fysikk-endring."""
    e = EnerFlytEngine()
    stor = e.vurder(BASE)
    per_kapita = dict(BASE, produksjon=1.0, forbruk=0.9, tap=0.05,
                      buffer=5.0, terskel=0.5)
    liten = e.vurder(per_kapita)
    assert stor["regime"] == liten["regime"] == "overflod"
    assert stor["dS_dt"] / BASE["buffer"] == pytest.approx(
        liten["dS_dt"] / per_kapita["buffer"])


def test_negativ_drift_med_tomt_lager_gir_nan():
    """Review-mønsteret fra økonomi-motoren: negativ drift med tomt
    lager er ikke stille klipping — det er NaN."""
    p = dict(BASE, buffer=0.0, forbruk=120.0)
    u = EnerFlytEngine().vurder(p)
    assert math.isnan(u["buffer_etter"]), u


def test_ingen_krise_prediksjon_deklarert():
    e = EnerFlytEngine()
    n = e.regime_node(BASE)
    hel = json.dumps(n, ensure_ascii=False)
    assert "Does NOT predict" in hel


def test_er_merket_idealisert():
    n = EnerFlytEngine().regime_node(BASE)
    hel = json.dumps(n, ensure_ascii=False)
    assert "idealized" in hel or "idealised" in hel


def test_en_akse_av_mange_deklarert():
    """Motoren skal si at energi er ÉN akse — andre valutaer er
    eksplisitt ikke-konserverte."""
    n = EnerFlytEngine().regime_node(BASE)
    tekst = json.dumps(n["ontology"], ensure_ascii=False)
    assert "money" in tekst and "trust" in tekst
