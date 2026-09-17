"""Tester for OrbitalEngine — Kepler og baneregimer (L-037).

Banemekanikk er den mest testbare EFC-motoren: prediksjoner på kjente
objekter med kjente tall. Motoren koder baneregimene som EFC-former:
bundet bane = holding (negativ spesifikk energi), unbundet = release,
resonans = periodelåsing, og Hill-sfæren/Lagrange-punktene som
potensialbuffere. IDEALISERT tolegeme-mekanikk — den er IKKE en
N-kroppsimulator, og det skal stå i selvbeskrivelsen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.orbital import OrbitalEngine

# Jord-måne-systemet (SI): G, M_jord, a_måne, e_måne
PARAMS = {
    "G": 6.67430e-11,          # m^3/(kg s^2)
    "M_sentral": 5.9722e24,    # kg — jorden
    "a": 3.844e8,              # m — månens store halvakse
    "e": 0.0549,               # månens eksentrisitet
    "m_objekt": 7.342e22,      # kg — månen
}

# Forventede verdier (månen, kjente tall):
# T = 2π sqrt(a^3/(G M)) med M = M_sentral + m_objekt
M_TOT = PARAMS["M_sentral"] + PARAMS["m_objekt"]
T_FORVENTET = 2 * np.pi * np.sqrt(PARAMS["a"] ** 3 / (PARAMS["G"] * M_TOT))


def test_kepler_periode_maten():
    e = OrbitalEngine()
    t = e.periode(PARAMS)
    assert np.isclose(t, T_FORVENTET, rtol=1e-9)


def test_periode_maten_er_siderisk_riktig():
    """Månens sideriske omløpstid skal være ~27.3 døgn."""
    e = OrbitalEngine()
    t_dogn = e.periode(PARAMS) / 86400.0
    assert 27.0 < t_dogn < 28.0


def test_vis_viva_hastighet():
    """Vis-viva: v^2 = GM(2/r - 1/a) — ved r=a i sirkelbanen er
    v = sqrt(GM/a)."""
    e = OrbitalEngine()
    v_sirkel = e.hastighet(PARAMS, PARAMS["a"])
    forventet = np.sqrt(PARAMS["G"] * M_TOT / PARAMS["a"])
    assert np.isclose(v_sirkel, forventet, rtol=1e-9)


def test_spesifikk_energi_skiller_holding_og_release():
    """Negativ spesifikk energi = bundet (holding); positiv = ubundet
    (release). Unnslipningshastigheten gir nøyaktig null."""
    e = OrbitalEngine()
    eps_bundet = e.spesifikk_energi(PARAMS, PARAMS["a"])
    assert eps_bundet < 0  # månen er bundet — holding
    # Unnslipning: v = sqrt(2GM/r) -> eps = 0
    v_esc = np.sqrt(2 * PARAMS["G"] * M_TOT / PARAMS["a"])
    eps_esc = 0.5 * v_esc ** 2 - PARAMS["G"] * M_TOT / PARAMS["a"]
    assert abs(eps_esc) < 1e-6


def test_hill_sfaere_er_bufferen():
    """Hill-sfæren er månebanens buffer mot jorden: r_H = a (m/(3M))^(1/3).
    Innenfor holder den seg; utenfor bryter bindingen."""
    e = OrbitalEngine()
    r_h = e.hill_sfaere(PARAMS)
    forventet = PARAMS["a"] * (PARAMS["m_objekt"]
                               / (3 * PARAMS["M_sentral"])) ** (1 / 3)
    assert np.isclose(r_h, forventet, rtol=1e-9)


def test_compute_rapporterer_regime_per_bane():
    """compute() skal gi regime-status: bundet (holding, eps<0) for
    a>0, ubundet (release, eps>0) for hyperbolsk a<0."""
    e = OrbitalEngine()
    koord = np.array([[PARAMS["a"], PARAMS["e"]],
                      [-1.0e9, 0.9]])  # hyperbolsk — negativ a
    ut = e.compute(PARAMS, koord)
    assert ut.shape == (2,)
    assert ut[0] < 0  # bundet = negativ energi = holding
    assert ut[1] > 0  # ubundet = positiv energi = release


def test_compute_haandterer_ugyldige_parametre():
    """Ugyldige parametre skal gi NaN, ikke KeyError."""
    e = OrbitalEngine()
    ut = e.compute({"G": 6.67430e-11}, np.array([[3.844e8, 0.05]]))
    assert np.all(np.isnan(ut))


def test_regime_node_selvbeskrivelse():
    e = OrbitalEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.orbital_engine"
    assert "kepler" in json.dumps(node, ensure_ascii=False).lower()
    assert "idealis" in json.dumps(node, ensure_ascii=False).lower() or \
           "tolegeme" in json.dumps(node, ensure_ascii=False).lower()
    assert node["regime"]["law_form"].strip()


def test_resonans_forhold_oppdages():
    """3:2-resonans (f.eks. Neptun-Pluto) skal gjenkjennes som
    periodelåsing — holding i fase."""
    e = OrbitalEngine()
    forhold = e.resonans_forhold(3.0, 2.0)  # perioder i 3:2
    assert abs(forhold - 3.0 / 2.0) < 1e-9


import json  # noqa: E402
