"""Test of the Victron charge engine (step 8): the CC->CV knee in time series.

The engine classifies the charge regime (0=CC, 1=CV) along time — the same
pattern as WaterPhaseEngine classifying phases in P-T space. The knee is the
transition in the label series.

TDD: written before the engine exists — must fail at import.
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
    """Pure CC/CV charge curve: constant current + rising voltage (CC),
    then constant voltage + exponentially falling current (CV)."""
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


def bro_kanoniske() -> dict:
    """Canonical parameters for the engine's ATLAS NODE.

    One source for the test and the bridge sync (scripts/maintenance/
    efc_bro_synk.py): the parameters do not exist as a module-level dict here —
    they are CONSTRUCTED by the synthetic CC/CV curve the tests use, and a sync
    that guessed would measure a different node than the test.
    """
    return params_for(*syntetisk_cccv())


# ---------------------------------------------------------------------------
# Classification along time
# ---------------------------------------------------------------------------

def test_ren_cccv_klassifiserer_regimer():
    t, v, i = syntetisk_cccv(t_k=60.0)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    # Before the knee: CC (0); after: CV (1). The knee sits at t=60 (index 60).
    assert np.all(labels[:55] == 0)
    assert np.all(labels[65:] == 1)


def test_find_knee_treffer_kjent_kne():
    t, v, i = syntetisk_cccv(t_k=60.0)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 60.0) <= 2.0  # within 2*dt
    assert abs(knee["v_knee"] - 3.45) < 0.1
    assert knee["i_knee"] > 5.0  # the current is still near the CC level


def test_ingen_kne_uten_lading():
    """Flat series (battery at rest): no transition — found=False, labels 0."""
    t = np.arange(100, dtype=float)
    v = np.full(100, 3.3)
    i = np.zeros(100)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    assert np.all(labels == 0)
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_stoy_robust():
    """The knee must be found also with measurement noise on V and I."""
    t, v, i = syntetisk_cccv(t_k=60.0, stoy=0.02, seed=7)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i, v_knee_tol=0.10,
                                       di_threshold=0.05), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 60.0) <= 5.0  # noise => looser tolerance


def test_solstyrt_lading_finner_ikke_falskt_kne():
    """The source contract (measured against live VRM data): solar-driven
    charging has VARIABLE power — the current follows the solar curve, not a
    CC plateau. The engine must say found=False instead of calling the solar
    peak a CV start."""
    t = np.arange(400, dtype=float) * 60.0  # minute resolution
    # Soft solar curve: rises, peaks at t ~ 3.3 hours, falls.
    i = 10.0 * np.sin(np.pi * np.arange(400) / 400.0) + 0.5
    v = np.minimum(3.2 + 0.25 * (np.arange(400) / 400.0), 3.45)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_klassifiserer_fortsatt_ladefase_paa_grove_data():
    """On coarse data the engine still classifies charging vs non-charging —
    the CC/CV knee is not visible, but the charge phase is."""
    t, v, i = syntetisk_cccv(t_k=7200.0, dt=60.0, n=400, tau=3600.0)
    def midle(s):
        return np.array([s[k:k + 15].mean() for k in range(0, 400, 15)])
    t15 = midle(t)
    v15 = midle(v)
    i15 = midle(i)
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t15, v15, i15), t15)
    # The whole series is a charge phase with falling current over time; the
    # engine must not crash and returns as many labels as points.
    assert len(labels) == len(t15)
    assert set(np.unique(labels)) <= {0, 1}


def test_labels_same_length_as_coordinates():
    """compute() must return as many labels as coordinates (the engine
    contract)."""
    t, v, i = syntetisk_cccv()
    engine = VictronChargeEngine()
    labels = engine.compute(params_for(t, v, i), t)
    assert len(labels) == len(t)


# ---------------------------------------------------------------------------
# Invalid input — the NaN contract
# ---------------------------------------------------------------------------

def test_ugyldig_input_gir_ikke_krasj():
    engine = VictronChargeEngine()
    t = np.arange(10, dtype=float)
    # Different lengths for V/I
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


def test_compute_none_params_lukket():
    """compute(None, ...) must not raise — closed handling (zeros)."""
    engine = VictronChargeEngine()
    t = np.arange(20, dtype=float)
    labels = engine.compute(None, t)
    assert labels.shape == t.shape
    assert np.all(labels == 0)


def test_ugyldige_terskler_lukket():
    """Negative/non-finite thresholds => no transition (zeros)."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0)
    for darlig_tol, darlig_di in [(-0.05, 0.1), (0.05, -0.1),
                                  (np.nan, 0.1), (np.inf, 0.1)]:
        p = params_for(t, v, i, v_knee_tol=darlig_tol, di_threshold=darlig_di)
        labels = engine.compute(p, t)
        assert np.all(labels == 0)


def test_ikke_monotone_tider_lukket():
    """Unordered time coordinates => zeros, no crash."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0)
    t_kaos = t.copy()
    t_kaos[10] = t_kaos[9] - 5.0  # breaks monotonicity
    labels = engine.compute(params_for(t, v, i), t_kaos)
    assert np.all(labels == 0)


def test_dt_uavhengighet():
    """Same physical curve, different sampling => same t_knee.

    The di_threshold threshold is per TIME UNIT (dI/dt), not per sample — the
    engine must divide by the actual dt. Decimating a fine series must give the
    same knee time."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0, dt=1.0, n=200)
    knee_fin = engine.find_knee(params_for(t, v, i), t)
    assert knee_fin["found"] is True
    assert abs(knee_fin["t_knee"] - 60.0) <= 4.0
    # Same curve, every 10th sample (dt=10).
    step = 10
    t10, v10, i10 = t[::step], v[::step], i[::step]
    knee_grov = engine.find_knee(params_for(t10, v10, i10), t10)
    assert knee_grov["found"] is True
    assert abs(knee_grov["t_knee"] - 60.0) <= 4.0 * step


def test_dt_skalering_mutersikker():
    """A decay that is SUB-threshold per time unit but SUPER-threshold per
    sample must NOT give a knee — the engine MUST divide by the actual dt.

    Mutation-sensitive: with /2.0 instead of /dt_mid, |dI/dt| per sample
    becomes 0.6/2 = 0.3 > the threshold, and the code finds a false knee."""
    step = 60.0  # sample every 60 seconds
    n = 120
    t = np.arange(n) * step
    v = np.full(n, 3.45)
    i = np.full(n, 10.0)
    # Weak decay: -0.01 A/s => -0.6 A per sample (far above 0.05).
    i[60:] = 10.0 - 0.01 * (t[60:] - t[60])
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i, di_threshold=0.05), t)
    assert knee["found"] is False


def test_enkeltstaaende_stroemspike_gir_ikke_kne():
    """One negative spike in the middle of a flat CC plateau => no transition.

    Requirement: the transition needs a confirmation window — one point is not
    enough to switch every subsequent sample to CV."""
    n = 200
    t = np.arange(n, dtype=float)
    i = np.full(n, 10.0)
    i[100] = 9.0  # single isolated spike down
    v = np.full(n, 3.45)  # near the limit: near_limit is satisfied
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_stroemrebound_etter_falskt_decay():
    """Short decay + rebound (solar peak) before the real knee => the REAL
    knee is found, not the false one."""
    n = 300
    t = np.arange(n, dtype=float)
    v = np.full(n, 3.45)  # flat, near the limit
    i = np.full(n, 10.0)
    # False decay + rebound at k=80-85.
    i[80] = 9.9
    i[81] = 9.8
    i[82] = 10.0
    i[83] = 10.0
    # Real CV start at k=150: exponentially decaying.
    i[150:] = 10.0 * np.exp(-(np.arange(150, n) - 150) / 30.0)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 150.0) <= 6.0


# ---------------------------------------------------------------------------
# the regime_node() bridge (the step 4 pattern)
# ---------------------------------------------------------------------------

def test_regime_node_bro():
    """The engine describes itself as a regime node — the atlas bridge."""
    t, v, i = syntetisk_cccv()
    engine = VictronChargeEngine()
    node = engine.regime_node(params_for(t, v, i))
    assert node["id"] == "efc.victron_cccv_engine"
    # The node must declare its coupling to batteri.lading (the CC/CV knee).
    koblinger = [r for r in node.get("couplings", [])]
    if koblinger:
        assert any("batteri.lading" in str(k) for k in koblinger)
    # And the validity range must mention CC and CV.
    assert "CC" in node["regime"]["validity"] and "CV" in node["regime"]["validity"]


def test_regime_node_validity_reflekterer_parametre():
    """The validity string must carry the EFFECTIVE parameters — not hardcoded
    default numbers — so the bridge is generic."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv()
    node = engine.regime_node(params_for(t, v, i, v_knee_tol=0.20,
                                         di_threshold=0.35))
    val = node["regime"]["validity"]
    assert "0.2" in val and "0.35" in val


def test_engine_node_matches_atlas():
    """Mechanical consistency: the engine's regime_node() must agree with the
    atlas node in regime_nodes.jsonld — same id, same validity numbers, and a
    CARRIES relation to batteri.lading."""
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
