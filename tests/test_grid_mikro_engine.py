"""Tests for GridMikroEngine — the formulas AGAINST the papers' published
results (the DOIs are the source)."""
from __future__ import annotations

import math

import pytest

from efc_inference.engine.grid_mikro import GridMikroEngine

P = {"rho": 1.0, "rho_crit": 1.0, "Gamma0": 2.0}


def test_scenario_a_er_papirets_form():
    """Γ = Γ0·ρ/(ρ+ρcrit) (DOI 31942821)."""
    e = GridMikroEngine()
    assert e.gamma(P, scenario="A") == pytest.approx(2.0 * 1.0 / 2.0)  # 1.0


def test_scenario_b_plus_er_papirets_form():
    """Γ = Γ0·y/(1+y), y = √(ρ/ρcrit) (DOI 31942800)."""
    e = GridMikroEngine()
    y = math.sqrt(1.0 / 1.0)  # 1
    assert e.gamma(P, scenario="B_plus") == pytest.approx(2.0 * 1 / 2)  # 1.0


def test_metning_ved_hoey_tetthet():
    e = GridMikroEngine()
    hoy = {**P, "rho": 100.0}
    assert e.gamma(hoy, scenario="A") == pytest.approx(
        2.0 * 100 / 101)  # → Γ0
    assert e.gamma(hoy, scenario="B_plus") == pytest.approx(
        2.0 * 10 / 11)  # → Γ0


def test_linearitet_ved_lav_tetthet():
    e = GridMikroEngine()
    lav = {**P, "rho": 0.01}
    assert e.gamma(lav, scenario="A") == pytest.approx(
        2.0 * 0.01 / 1.01, rel=1e-6)


def test_deff_er_sqrt_formen():
    e = GridMikroEngine()
    assert e.deff(P) == pytest.approx(1.0)
    assert e.deff({**P, "rho": 4.0}) == pytest.approx(2.0)


def test_regime_skifte_ved_rho_crit():
    e = GridMikroEngine()
    assert e.regime({**P, "rho": 0.5}) == "low_density"
    assert e.regime({**P, "rho": 1.0}) == "saturated"


def test_regime_ugyldige_innganger_gir_ugyldig():
    """Review requirement PR #458 r1: NaN/negative inputs shall give
    'invalid', not fall through to 'saturated'."""
    e = GridMikroEngine()
    assert e.regime({**P, "rho": float("nan")}) == "invalid"
    assert e.regime({**P, "rho_crit": float("nan")}) == "invalid"
    assert e.regime({**P, "rho_crit": -1.0}) == "invalid"
    assert e.regime({**P, "rho": -0.5}) == "invalid"
    assert e.regime({**P, "rho": float("inf")}) == "invalid"


def test_negativ_tetthet_gir_nan():
    e = GridMikroEngine()
    assert math.isnan(e.gamma({**P, "rho": -1.0}, scenario="A"))
    assert math.isnan(e.deff({**P, "rho": -1.0}))


def test_noden_deklarerer_doi_kildene():
    n = GridMikroEngine().regime_node(P)
    assert "31942821" in n["ontology"]["source"]
    assert "31942800" in n["ontology"]["source"]


def test_noden_deklarerer_hypotese_ikke_konsensus():
    n = GridMikroEngine().regime_node(P)
    assert n["epistemikk"]["sannhetsstatus"] == "hypotese"
    assert "HYPOTHESIS" in n["ontology"]["assumes"][2]


def test_compute_returnerer_gamma_per_punkt():
    import numpy as np
    e = GridMikroEngine()
    ut = e.compute(P, np.array([1.0, 4.0]))
    assert ut[0] == pytest.approx(1.0)
    assert ut[1] == pytest.approx(2.0 * 2 / 3)
