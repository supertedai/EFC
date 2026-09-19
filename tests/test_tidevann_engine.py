"""Tests for TidevannEngine — periodic gravitational coupling (L-039).

The tide is a periodic energy-flow coupling: the Moon lifts and lowers
the Earth's oceans in an endless charge/discharge cycle. Phase locking
(the Moon always shows the same face) is the holding of tidal braking.
The engine is an IDEALISED equilibrium model (no ocean-basin dynamics,
no resonance amplification) — it says so in its self-description.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.tidevann import TidevannEngine

# The Earth-Moon system
PARAMS = {
    "G": 6.67430e-11,          # m^3/(kg s^2)
    "M_sentral": 5.9722e24,    # kg — the Earth
    "m_objekt": 7.342e22,      # kg — the Moon
    "avstand": 3.844e8,        # m — Earth-Moon distance
    "radius_sentral": 6.371e6,  # m — the Earth's radius
    "rho_sentral": 5514.0,      # kg/m^3 — Earth density
    "rho_objekt": 3344.0,       # kg/m^3 — Moon density
}


def test_tidevannskraft_maten():
    """The tidal acceleration ~ 2GMm/(r^3) * R."""
    e = TidevannEngine()
    a = e.tidevannsakselerasjon(PARAMS)
    forventet = (2 * PARAMS["G"] * PARAMS["m_objekt"]
                 / PARAMS["avstand"] ** 3 * PARAMS["radius_sentral"])
    assert np.isclose(a, forventet, rtol=1e-9)


def test_tidevannshoyde_fysikalsk_skala():
    """The tidal height in open ocean is ~0.5 m for the Earth-Moon —
    order of magnitude, not exact (basin resonance omitted)."""
    e = TidevannEngine()
    h = e.tidevannshoyde(PARAMS)
    assert 0.2 < h < 2.0  # the open-ocean scale is ~0.5 m


def test_roche_grense_er_terskelen():
    """The Roche limit: below it the cohesion breaks apart — the engine
    computes it from the densities (idealised fluid body)."""
    e = TidevannEngine()
    r_roche = e.roche_grense(PARAMS)
    # For the Earth-Moon: ~2.4 Earth radii (fluid)
    assert 2.0 * PARAMS["radius_sentral"] < r_roche < 3.5 * PARAMS["radius_sentral"]


def test_faselaasing_er_holding():
    """Phase locking: when the rotation is tidally braked to synchronous,
    the system is held in resonance — holding."""
    e = TidevannEngine()
    assert e.er_faselaast(PARAMS, rotasjonsperiode=27.32 * 86400.0,
                          omlopsperiode=27.32 * 86400.0) is True
    assert e.er_faselaast(PARAMS, rotasjonsperiode=1.0 * 86400.0,
                          omlopsperiode=27.32 * 86400.0) is False


def test_compute_rapporterer_tidevannskraft_per_avstand():
    e = TidevannEngine()
    avstander = np.array([3.844e8, 3.0e8])
    ut = e.compute(PARAMS, avstander)
    assert ut.shape == (2,)
    assert ut[1] > ut[0]  # closer = stronger tide
    assert np.all(np.isfinite(ut))


def test_regime_node_selvbeskrivelse():
    e = TidevannEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.tidevann_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealis" in tekst
    assert "resonans" in tekst or "basseng" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
