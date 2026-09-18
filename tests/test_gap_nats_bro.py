"""Tests for gap_nats_bro — the analyses against fixed message shapes.

The shapes are the ones the connectors publish (Hetzner PR #1006),
which in turn are measured against real source responses (NOAA 200,
GBIF 108 042, VHP 400/403).
"""
from __future__ import annotations

import pathlib

import pytest

from efc_inference.bridge.gap_nats_bro import (
    analyser_hav, analyser_planter, analyser_vulkan)


def test_analyser_vulkan_teller_aktive():
    m = {"antall_spurte": 3,
         "tilstand": {"Kilauea": {"nivaa": "WATCH", "status": "erupting"},
                      "Etna": {"nivaa": "NORMAL", "status": "green"},
                      "Eyjafjallajokull": {"nivaa": "NORMAL",
                                           "status": "green"}}}
    r = analyser_vulkan(m)
    assert r["antall_aktive"] == 1
    assert r["prosent_aktive"] == 33.3


def test_analyser_hav_middel_og_spredning():
    m = {"antall_stasjoner": 3,
         "temperaturer_c": {"9414290": 12.5, "8518750": 14.0}}
    r = analyser_hav(m)
    assert r["maalt"] is True
    assert r["middel_c"] == 13.25
    assert r["min_c"] == 12.5
    assert r["max_c"] == 14.0
    assert r["antall_maalte"] == 2


def test_analyser_hav_ingen_data_er_ikke_feil():
    r = analyser_hav({"antall_stasjoner": 2, "temperaturer_c": {}})
    assert r["maalt"] is False


def test_analyser_planter_summerer_tellinger():
    m = {"tellinger": {"plant": 108042, "Vascular plant": 90000},
         "feil": []}
    r = analyser_planter(m)
    assert r["sum"] == 198042
    assert r["feil"] == 0


def test_analyser_hav_skjermer_nan():
    m = {"antall_stasjoner": 2,
         "temperaturer_c": {"a": float("nan"), "b": 12.0}}
    r = analyser_hav(m)
    assert r["middel_c"] == 12.0


def test_bro_runde_uten_melding_er_aarlig():
    from efc_inference.bridge.gap_nats_bro import bro_runde
    r = bro_runde({})
    assert r == {}


def test_legit_parser_gyldig_nats_url():
    """Regression test: nats://user:pass@host:4222 must parse
    (over-escaped \\d was a review finding in both Hetzner and EFC)."""
    from efc_inference.bridge import gap_nats_bro
    import tempfile, os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".env",
                                     delete=False) as f:
        f.write("NATS_KONSUMENT=nats://bruker:pass@10.0.0.1:4222\n")
        navn = f.name
    gammel = gap_nats_bro.LEGITIMASJON
    gap_nats_bro.LEGITIMASJON = navn
    try:
        b, pw, host, port, feil = gap_nats_bro._legit()
        assert feil == ""
        assert (b, host, port) == ("bruker", "10.0.0.1", 4222)
    finally:
        os.unlink(navn)
        gap_nats_bro.LEGITIMASJON = gammel
