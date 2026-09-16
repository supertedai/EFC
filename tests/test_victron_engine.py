"""Test av Victron-lademotoren (trinn 8): CC->CV-kneet i tidsserier.

Motoren klassifiserer lade-regimet (0=CC, 1=CV) langs tiden — samme
mønster som WaterPhaseEngine klassifiserer faser i P-T-rommet. Kneet er
overgangen i label-serien.

TDD: skrives foer motoren finnes — skal feile ved import.
"""
from __future__ import annotations

import math

import numpy as np
import pytest

from efc_inference.engine.victron import VictronChargeEngine


def syntetisk_cccv(t_k: float = 60.0, dt: float = 1.0, n: int = 200,
                   v_start: float = 3.2, v_k: float = 3.45,
                   i_cc: float = 10.0, tau: float = 30.0,
                   stoy: float = 0.0, seed: int = 42) -> tuple:
    """Ren CC/CV-ladekurve: konstant strøm + stigende spenning (CC),
    deretter konstant spenning + eksponentielt avtagende strøm (CV)."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) * dt
    v = np.empty(n)
    i = np.empty(n)
    for k, tk in enumerate(t):
        if tk < t_k:
            v[k] = v_start + (v_k - v_start) * (tk / t_k)
            i[k] = i_cc
        else:
            v[k] = v_k
            i[k] = i_cc * math.exp(-(tk - t_k) / tau)
    if stoy > 0:
        v = v + rng.normal(0, stoy, n)
        i = i + rng.normal(0, stoy * i_cc / 10.0, n)
    return t, v, i


def params_for(t, v, i, v_knee_tol=0.05, di_threshold=0.1,
               cc_flat_threshold=0.05):
    return {
        "v_series": v,
        "i_series": i,
        "v_knee_tol": v_knee_tol,
        "di_threshold": di_threshold,
        "cc_flat_threshold": cc_flat_threshold,
    }


# ---------------------------------------------------------------------------
# Klassifisering langs tiden
# ---------------------------------------------------------------------------

def test_ren_cccv_klassifiserer_regimer():
    t, v, i = syntetisk_cccv(t_k=60.0)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    # Foer kneet: CC (0); etter: CV (1). Kneet ligger ved t=60 (indeks 60).
    assert np.all(labels[:55] == 0)
    assert np.all(labels[65:] == 1)


def test_find_knee_treffer_kjent_kne():
    t, v, i = syntetisk_cccv(t_k=60.0)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 60.0) <= 2.0  # innenfor 2*dt
    assert abs(knee["v_knee"] - 3.45) < 0.1
    assert knee["i_knee"] > 5.0  # strømmen er fortsatt nær CC-nivå ved kneet


def test_ingen_kne_uten_lading():
    """Flat serie (batteri i ro): ingen overgang — found=False, labels 0."""
    t = np.arange(100, dtype=float)
    v = np.full(100, 3.3)
    i = np.zeros(100)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    assert np.all(labels == 0)
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_stoy_robust():
    """Kneet skal finnes ogsa med maalestoey paa V og I."""
    t, v, i = syntetisk_cccv(t_k=60.0, stoy=0.02, seed=7)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i, v_knee_tol=0.10,
                                       di_threshold=0.05), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 60.0) <= 5.0  # stoey => loosere toleranse


def test_solstyrt_lading_finner_ikke_falskt_kne():
    """Kilde-kontrakten (maalt mot levende VRM-data): solstyrt lading
    har VARIABEL effekt — strømmen foelger solkurven, ikke et CC-plataa.
    Motoren skal si found=False i stedet for aa kalle soltoppen for
    CV-start."""
    t = np.arange(400, dtype=float) * 60.0  # minutt-opploesning
    # Myk solkurve: stiger, topper ved t ~ 3.3 timer, synker.
    i = 10.0 * np.sin(np.pi * np.arange(400) / 400.0) + 0.5
    v = np.minimum(3.2 + 0.25 * (np.arange(400) / 400.0), 3.45)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_klassifiserer_fortsatt_ladefase_paa_grove_data():
    """Paa grove data klassifiserer motoren fortsatt lading vs ikke-
    lading — CC/CV-kneet er ikke synlig, men ladefasen er det."""
    t, v, i = syntetisk_cccv(t_k=7200.0, dt=60.0, n=400, tau=3600.0)
    def midle(s):
        return np.array([s[k:k + 15].mean() for k in range(0, 400, 15)])
    t15 = midle(t)
    v15 = midle(v)
    i15 = midle(i)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t15, v15, i15), t15)
    # Hele serien er en ladefase med synkende stroem over tid; motoren
    # skal ikke krasje og returnere like mange labels som punkter.
    assert len(labels) == len(t15)
    assert set(np.unique(labels)) <= {0, 1}


def test_labels_same_length_as_coordinates():
    """compute() skal returnere like mange labels som koordinater
    (engine-kontrakten)."""
    t, v, i = syntetisk_cccv()
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    assert len(labels) == len(t)


# ---------------------------------------------------------------------------
# Ugyldig input — NaN-kontrakt
# ---------------------------------------------------------------------------

def test_ugyldig_input_gir_ikke_krasj():
    engine = VictronChargeEngine()
    t = np.arange(10, dtype=float)
    # Ulik lengde V/I
    darlig = {
        "v_series": np.ones(10),
        "i_series": np.ones(5),
        "v_knee_tol": 0.05,
        "di_threshold": 0.1,
    }
    knee = engine.find_knee(darlig, t)
    assert knee["found"] is False


def test_nan_input_gir_ikke_krasj():
    engine = VictronChargeEngine()
    t = np.arange(10, dtype=float)
    nan_serie = np.full(10, np.nan)
    knee = engine.find_knee(params_for(t, nan_serie, nan_serie), t)
    assert knee["found"] is False


def test_validate_params_krever_serier():
    engine = VictronChargeEngine()
    assert engine.validate_params({"v_knee_tol": 0.05,
                                   "di_threshold": 0.1}) is False
    assert engine.validate_params(params_for(np.arange(3.0),
                                             np.ones(3), np.ones(3))) is True


# ---------------------------------------------------------------------------
# regime_node()-broen (trinn 4-mønsteret)
# ---------------------------------------------------------------------------

def test_regime_node_bro():
    """Motoren beskriver seg selv som regime-node — broen til atlaset."""
    t, v, i = syntetisk_cccv()
    engine = VictronChargeEngine()
    node = engine.regime_node(params_for(t, v, i))
    assert node["id"] == "efc.victron_cccv_engine"
    # Noden skal deklarere koblingen til batteri.lading (CC/CV-overgangen).
    koblinger = [r for r in node.get("couplings", [])]
    if koblinger:
        assert any("batteri.lading" in str(k) for k in koblinger)
    # Og gyldighetsomraadet skal nevne CC og CV.
    assert "CC" in node["regime"]["validity"] and "CV" in node["regime"]["validity"]


def test_engine_node_matches_atlas():
    """Maskinell konsistens: motorens regime_node() skal stemme med
    atlas-noden i regime_nodes.jsonld — samme id, samme validity-tall,
    og CARRIES-kobling til batteri.lading."""
    import json
    from pathlib import Path
    t, v, i = syntetisk_cccv()
    engine = VictronChargeEngine()
    node = engine.regime_node(params_for(t, v, i))

    atlas = json.loads(Path("schema/regime_nodes.jsonld").read_text())
    atlas_node = next(n for n in atlas["nodes"] if n["id"] == node["id"])
    assert atlas_node["regime"]["validity"] == node["regime"]["validity"]
    assert atlas_node["regime"]["law_form"] == node["regime"]["law_form"]
    rel = next(r for r in atlas["relations"]
               if r["subject"] == node["id"] and r["predicate"] == "CARRIES")
    assert rel["object"] == "batteri.lading"
