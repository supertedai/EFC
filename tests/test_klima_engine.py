"""Tester for KlimaEngine — strålingsbalanse som energiflyt (L-040).

Klimaets energibalansemodell er EFC i ren form på jorden: energi inn
(sol), buffer (havets varmekapasitet, is-albedo), terskeloverganger
(iskollaps, AMOC-stil brytere). Motoren er en IDEALISERT 0D-
energibalansemodell — IKKE en klimamodell-konkurrent, og det står i
selvbeskrivelsen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.klima import KlimaEngine

PARAMS = {
    "solarkonstant": 1361.0,       # W/m^2
    "albedo": 0.30,                # jordas gjennomsnitt
    "emissivitet": 0.61,           # effektiv (drivhuseffekt inkludert)
    "stefan_boltzmann": 5.670374419e-8,  # W/(m^2 K^4)
    "hav_varmekapasitet": 1.0e8,   # J/(m^2 K) — blandingslaget
}


def test_likevektstemperatur_maten():
    """Jordas effektive likevektstemperatur: ~288 K med drivhus."""
    e = KlimaEngine()
    t = e.likevektstemperatur(PARAMS)
    assert 280.0 < t < 295.0  # jorda ligger her med drivhus


def test_likevektstemperatur_uten_drivhus_kaldere():
    """Med emissivitet 1 (svart legeme) og albedo 0.3: ~255 K."""
    params_uten = {**PARAMS, "emissivitet": 1.0}
    e = KlimaEngine()
    t = e.likevektstemperatur(params_uten)
    forventet = (PARAMS["solarkonstant"] * (1 - PARAMS["albedo"])
                 / (4 * PARAMS["stefan_boltzmann"])) ** 0.25
    assert np.isclose(t, forventet, rtol=1e-9)


def test_is_albedo_tilbakekobling_er_positiv():
    """Is-albedo: kaldere -> mer is -> høyere albedo -> enda kaldere.
    Positiv tilbakekobling (forsterkning)."""
    e = KlimaEngine()
    forsterkning = e.albedo_tilbakekobling(PARAMS, delta_t=-1.0)
    assert forsterkning > 1.0  # forsterker, demper ikke


def test_bufferen_demper_forstyrrelser():
    """Havets varmekapasitet er bufferen: responsen på en
    strålingsforstyrrelse er treg — dempet og forsinket."""
    e = KlimaEngine()
    respons = e.tidskonstant(PARAMS)
    # tidskonstant = C / (4 eps sigma T^3) — år i praksis
    assert respons > 0
    assert respons / (365.25 * 86400) < 100  # under 100 år


def test_regimeskifte_ved_albedo_terskel():
    """Is-albedo-bryteren: over en terskel-albedo finnes ingen varm
    likevekt — systemet faller til snøballjord (hysterese)."""
    e = KlimaEngine()
    albedoer = np.linspace(0.3, 0.9, 7)
    stabile = [e.har_varm_likevekt({**PARAMS, "albedo": a})
               for a in albedoer]
    # ved høy albedo forsvinner den varme likevekten
    assert stabile[-1] is False
    assert stabile[0] is True


def test_regime_node_selvbeskrivelse():
    e = KlimaEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.klima_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "idealiser" in tekst or "0d" in tekst
    assert "ikke en klimamodell" in tekst or \
           "ikke klimamodell" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
