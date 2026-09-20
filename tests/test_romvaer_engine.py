"""Tests for RomvaerEngine — the magnetosphere's Kp buffer (L-038).

The Kp index (0-9) is the magnetosphere's discharge level: the buffer is charged
by the solar wind (southward Bz is the charging current) and released in
geomagnetic storms. The engine is a CORRELATION MODEL
(solar wind -> Kp), not physics from the ground up — the shape's coupling to
the Sun's flares is the EFC contribution, and that is stated in the self-description.
"""
from __future__ import annotations

import numpy as np
import pytest

from efc_inference.engine.romvaer import RomvaerEngine

PARAMS = {
    "lade_koeffisient": 0.7,       # Kp per (nT/10 * 100 km/s) — calibrated
                                   # so that Bz=-12/v=600 gives Kp≈5 (G1)
    "utladningsrate": 0.25,        # Kp per 3h tick — the buffer's discharge
    "storm_terskel": 5.0,          # Kp — the G1 storm threshold
}


def test_forventet_kp_fra_solvind():
    """Southward Bz charges: Kp rises with |Bz| and speed."""
    e = RomvaerEngine()
    kp_rolig = e.forventet_kp(PARAMS, bz=2.0, hastighet=350.0)
    kp_storm = e.forventet_kp(PARAMS, bz=-12.0, hastighet=600.0)
    assert 0 <= kp_rolig < 5
    assert kp_storm > kp_rolig
    assert kp_storm >= PARAMS["storm_terskel"]


def test_nordvendt_bz_lader_ikke():
    """Northward Bz is shielding: the buffer is not charged."""
    e = RomvaerEngine()
    kp_nord = e.forventet_kp(PARAMS, bz=12.0, hastighet=600.0)
    assert kp_nord < 3.0


def test_storm_niva_fra_kp():
    """The G1-G5 storm levels: Kp 5->G1, 6->G2, 7->G3, 8->G4, 9->G5."""
    e = RomvaerEngine()
    assert e.storm_niva(PARAMS, 5.0) == "G1"
    assert e.storm_niva(PARAMS, 7.0) == "G3"
    assert e.storm_niva(PARAMS, 9.0) == "G5"
    assert e.storm_niva(PARAMS, 4.0) == "ingen"


def test_buffer_utlades_over_tid():
    """The discharge: Kp falls by the discharge rate per 3h tick."""
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
    assert "correlation model" in tekst
    assert "not physics from the ground up" in tekst
    assert node["regime"]["law_form"].strip()


import json  # noqa: E402
