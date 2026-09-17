"""Tester for RomvaerEngine — magnetosfærens Kp-buffer (L-038).

Kp-indeksen (0-9) er magnetosfærens utladningsnivå: bufferen lades
av solvinden (sørvendt Bz er ladestrømmen) og utløses i
geomagnetiske stormer. Motoren er en KORRELASJONSMODELL
(solvind -> Kp), ikke fysikk fra bunnen — formens kobling til
solens flares er EFC-bidraget, og det står i selvbeskrivelsen.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.romvaer import RomvaerEngine

PARAMS = {
    "lade_koeffisient": 0.7,       # Kp per (nT/10 * 100 km/s) — kalibrert
                                   # så Bz=-12/v=600 gir Kp≈5 (G1)
    "utladningsrate": 0.25,        # Kp per 3t-tikk — bufferens utladning
    "storm_terskel": 5.0,          # Kp — G1-stormgrensen
}


def test_forventet_kp_fra_solvind():
    """Sørvendt Bz lader: Kp stiger med |Bz| og hastighet."""
    e = RomvaerEngine()
    kp_rolig = e.forventet_kp(PARAMS, bz=2.0, hastighet=350.0)
    kp_storm = e.forventet_kp(PARAMS, bz=-12.0, hastighet=600.0)
    assert 0 <= kp_rolig < 5
    assert kp_storm > kp_rolig
    assert kp_storm >= PARAMS["storm_terskel"]


def test_nordvendt_bz_lader_ikke():
    """Nordvendt Bz er skjermende: bufferen lades ikke."""
    e = RomvaerEngine()
    kp_nord = e.forventet_kp(PARAMS, bz=12.0, hastighet=600.0)
    assert kp_nord < 3.0


def test_storm_niva_fra_kp():
    """G1-G5-stormnivåene: Kp 5->G1, 6->G2, 7->G3, 8->G4, 9->G5."""
    e = RomvaerEngine()
    assert e.storm_niva(PARAMS, 5.0) == "G1"
    assert e.storm_niva(PARAMS, 7.0) == "G3"
    assert e.storm_niva(PARAMS, 9.0) == "G5"
    assert e.storm_niva(PARAMS, 4.0) == "ingen"


def test_buffer_utlades_over_tid():
    """Utladningen: Kp faller med utladningsraten per 3t-tikk."""
    e = RomvaerEngine()
    kp0 = 7.0
    kp1 = e.utlad(kp0, PARAMS, tikk=1)
    kp2 = e.utlad(kp0, PARAMS, tikk=2)
    assert kp1 < kp0
    assert kp2 < kp1


def test_compute_rapporterer_kp_per_solvind():
    e = RomvaerEngine()
    koord = np.array([[-12.0, 600.0], [2.0, 350.0]])
    ut = e.compute(PARAMS, koord)
    assert ut.shape == (2,)
    assert ut[0] > ut[1]
    assert np.all(np.isfinite(ut))


def test_regime_node_selvbeskrivelse():
    e = RomvaerEngine()
    node = e.regime_node(PARAMS)
    assert node["id"] == "efc.romvaer_engine"
    tekst = json.dumps(node, ensure_ascii=False).lower()
    assert "korrelasjonsmodell" in tekst
    assert "ikke fysikk fra bunnen" in tekst or \
           "ikke fysikk fra bunn" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
