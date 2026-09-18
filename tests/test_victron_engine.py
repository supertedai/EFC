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


def bro_kanoniske() -> dict:
    """Kanoniske parametre for motorens ATLAS-NODE.

    Én kilde for testen og bro-synken (scripts/maintenance/efc_bro_synk.py):
    parametrene finnes ikke som et modulnivaa-dict her — de KONSTRUERES av
    den syntetiske CC/CV-kurven testene selv bruker, og en synk som gjettet
    ville maalt en annen node enn testen.
    """
    return params_for(*syntetisk_cccv())


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


def test_compute_none_params_lukket():
    """compute(None, ...) skal ikke kaste — lukket håndtering (zeros)."""
    engine = VictronChargeEngine()
    t = np.arange(20, dtype=float)
    labels = engine.compute(None, t)
    assert labels.shape == t.shape
    assert np.all(labels == 0)


def test_ugyldige_terskler_lukket():
    """Negative/ikke-endelige terskler => ingen overgang (zeros)."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0)
    for darlig_tol, darlig_di in [(-0.05, 0.1), (0.05, -0.1),
                                  (np.nan, 0.1), (np.inf, 0.1)]:
        p = params_for(t, v, i, v_knee_tol=darlig_tol, di_threshold=darlig_di)
        labels = engine.compute(p, t)
        assert np.all(labels == 0)


def test_ikke_monotone_tider_lukket():
    """Uordnede tidskoordinater => zeros, ingen krasj."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0)
    t_kaos = t.copy()
    t_kaos[10] = t_kaos[9] - 5.0  # bryter monotoni
    labels = engine.compute(params_for(t, v, i), t_kaos)
    assert np.all(labels == 0)


def test_dt_uavhengighet():
    """Samme fysiske kurve, ulik sampling => samme t_knee.

    Terskelen di_threshold er per TIDSENHET (dI/dt), ikke per sample —
    motoren skal dele på faktisk dt. Dekimering av en fin serie maa
    gi samme kne-tidspunkt."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv(t_k=60.0, dt=1.0, n=200)
    knee_fin = engine.find_knee(params_for(t, v, i), t)
    assert knee_fin["found"] is True
    assert abs(knee_fin["t_knee"] - 60.0) <= 4.0
    # Samme kurve, hvert 10. sample (dt=10).
    step = 10
    t10, v10, i10 = t[::step], v[::step], i[::step]
    knee_grov = engine.find_knee(params_for(t10, v10, i10), t10)
    assert knee_grov["found"] is True
    assert abs(knee_grov["t_knee"] - 60.0) <= 4.0 * step


def test_dt_skalering_mutersikker():
    """Dekay som er SUB-terskel per tidsenhet men SUPER-terskel per
    sample skal IKKE gi kne — motoren MA dele på faktisk dt.

    Mutasjonsfølsom: med /2.0 i stedet for /dt_mid blir |dI/dt| per
    sample 0.6/2 = 0.3 > terskelen, og koden ville finne et falskt kne."""
    step = 60.0  # sample hvert 60. sekund
    n = 120
    t = np.arange(n) * step
    v = np.full(n, 3.45)
    i = np.full(n, 10.0)
    # Svak dekay: -0.01 A/s => -0.6 A per sample (langt over 0.05).
    i[60:] = 10.0 - 0.01 * (t[60:] - t[60])
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i, di_threshold=0.05), t)
    assert knee["found"] is False


def test_enkeltstaaende_stroemspike_gir_ikke_kne():
    """Én negativ spike midt i flatt CC-plataa => ingen overgang.

    Krav: overgangen krever et bekreftelsesvindu — ett punkt er ikke
    nok til aa skru alle etterfoelgende samples til CV."""
    n = 200
    t = np.arange(n, dtype=float)
    i = np.full(n, 10.0)
    i[100] = 9.0  # enkeltstaaende spike ned
    v = np.full(n, 3.45)  # naer grensen: near_limit er oppfylt
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is False


def test_stroemrebound_etter_falskt_decay():
    """Kort decay + rebound (soltopp) foer det ekte kneet => det EKTE
    kneet finnes, ikke det falske."""
    n = 300
    t = np.arange(n, dtype=float)
    v = np.full(n, 3.45)  # flat, naer grensen
    i = np.full(n, 10.0)
    # Falsk decay + rebound ved k=80-85.
    i[80] = 9.9
    i[81] = 9.8
    i[82] = 10.0
    i[83] = 10.0
    # Ekte CV-start ved k=150: eksponentielt avtagende.
    i[150:] = 10.0 * np.exp(-(np.arange(150, n) - 150) / 30.0)
    engine = VictronChargeEngine()
    knee = engine.find_knee(params_for(t, v, i), t)
    assert knee["found"] is True
    assert abs(knee["t_knee"] - 150.0) <= 6.0


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


def test_regime_node_validity_reflekterer_parametre():
    """Validity-strengen skal baere de EFFEKTIVE parametrene — ikke
    hardkodede default-tall — saa broen er generisk."""
    engine = VictronChargeEngine()
    t, v, i = syntetisk_cccv()
    node = engine.regime_node(params_for(t, v, i, v_knee_tol=0.20,
                                         di_threshold=0.35))
    val = node["regime"]["validity"]
    assert "0.2" in val and "0.35" in val


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
