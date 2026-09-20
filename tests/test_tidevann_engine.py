"""Tester for TidevannEngine — periodisk gravitasjonskopling (L-039).

Tidevann er periodisk energiflyt-kopling: månen løfter og senker
jordas hav i en uendelig lade/tøm-syklus. Fase-låsing (månen viser
alltid samme side) er tidevannsbremsingens holding. Motoren er en
IDEALISERT likevektsmodell (ingen hav-basseng-dynamikk, ingen
resonansforsterkning) — det står i selvbeskrivelsen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.tidevann import TidevannEngine

# Jord-måne-systemet
PARAMS = {
    "G": 6.67430e-11,          # m^3/(kg s^2)
    "M_sentral": 5.9722e24,    # kg — jorden
    "m_objekt": 7.342e22,      # kg — månen
    "avstand": 3.844e8,        # m — jord-måne-avstand
    "radius_sentral": 6.371e6,  # m — jordas radius
    "rho_sentral": 5514.0,      # kg/m^3 — jordas tetthet
    "rho_objekt": 3344.0,       # kg/m^3 — månens tetthet
}


def test_tidevannskraft_maten():
    """Tidevannsakselerasjonen ~ 2GMm/(r^3) * R."""
    e = TidevannEngine()
    a = e.tidevannsakselerasjon(PARAMS)
    forventet = (2 * PARAMS["G"] * PARAMS["m_objekt"]
                 / PARAMS["avstand"] ** 3 * PARAMS["radius_sentral"])
    assert np.isclose(a, forventet, rtol=1e-9)


def test_tidevannshoyde_fysikalsk_skala():
    """Tidevannshøyden i åpent hav er ~0.5 m for jord-måne —
    størrelsesorden, ikke eksakt (basseng-resonans utelatt)."""
    e = TidevannEngine()
    h = e.tidevannshoyde(PARAMS)
    assert 0.2 < h < 2.0  # åpen-hav-skalaen er ~0.5 m


def test_roche_grense_er_terskelen():
    """Roche-grensen: under den brytes sammenhengen — motoren skal
    beregne den fra tetthetene (idealisert flytende legeme)."""
    e = TidevannEngine()
    r_roche = e.roche_grense(PARAMS)
    # For jord-måne: ~2.4 jordradier (flytende)
    assert 2.0 * PARAMS["radius_sentral"] < r_roche < 3.5 * PARAMS["radius_sentral"]


def test_faselaasing_er_holding():
    """Fase-låsing: når rotasjonen er tidevannsbremset til synkron,
    er systemet holdt i resonans — holding."""
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
    assert ut[1] > ut[0]  # nærmere = sterkere tidevann
    assert np.all(np.isfinite(ut))


def test_regime_node_selvbeskrivelse():
    e = TidevannEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.tidevann_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealized equilibrium model" in tekst
    assert "resonance" in tekst or "basin" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
