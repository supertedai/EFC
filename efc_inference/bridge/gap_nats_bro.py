"""gap_nats_bro — three bridges from NATS into the EFC engines (ocean, plants, volcano).

    kosmos.jord.tilstand.usgs-vulkan        -> volcano state (regime status)
    verden.klima.tilstand.noaa-tides     -> ocean temperature proxy
    verden.miljo.tilstand.gbif-planter -> biosphere counts

The states are described in the cold-archive seed (Hetzner PR #1006). These
bridges READ the streams and feed the engines — the injectability design:
NATS is not an atlas node, NATS -> bridge -> engine -> atlas node.
"""
from __future__ import annotations

import json
import os
import re
import socket

EMNE_VULKAN = "kosmos.jord.tilstand.usgs-vulkan"
EMNE_HAV = "verden.klima.tilstand.noaa-tides"
EMNE_PLANTER = "verden.miljo.tilstand.gbif-planter"

LEGITIMASJON = os.environ.get("NATS_LEGITIMASJON",
                              "/etc/nats/legitimasjon.env")
TIDSAVBRUDD = 20


def _legit(rolle: str = "KONSUMENT"):
    try:
        for linje in open(LEGITIMASJON, encoding="utf-8"):
            if linje.startswith(f"NATS_{rolle}="):
                m = re.match(r"nats://([^:]+):([^@]+)@([^:]+):(\d+)",
                             linje.split("=", 1)[1].strip())
                if m:
                    return (m.group(1), m.group(2), m.group(3),
                            int(m.group(4)), "")
    except OSError as e:
        return None, None, None, None, f"{LEGITIMASJON}: {type(e).__name__}"
    return None, None, None, None, f"the role {rolle} is missing"


def analyser_vulkan(melding: dict) -> dict:
    """VHP state -> regime classification (the status list)."""
    tilstand = melding.get("tilstand", {})
    antall_aktive = sum(1 for v in tilstand.values()
                        if str(v.get("nivaa", "")).upper()
                        not in ("", "NORMAL", "GREEN"))
    return {"antall_spurte": melding.get("antall_spurte", 0),
            "antall_aktive": antall_aktive,
            "prosent_aktive": round(100 * antall_aktive /
                                    max(1, melding.get("antall_spurte", 1)),
                                    1)}


def analyser_hav(melding: dict) -> dict:
    """NOAA temperatures -> proxy for ocean energy (the climate engine)."""
    temp = melding.get("temperaturer_c", {})
    verdier = [v for v in temp.values()
               if isinstance(v, (int, float)) and v == v]
    if not verdier:
        return {"maalt": False, "antall_stasjoner":
                melding.get("antall_stasjoner", 0)}
    return {"maalt": True, "middel_c": round(sum(verdier) /
                                             len(verdier), 2),
            "min_c": round(min(verdier), 2),
            "max_c": round(max(verdier), 2),
            "antall_maalte": len(verdier)}


def analyser_planter(melding: dict) -> dict:
    """GBIF counts -> biosphere footprint (the energy-flow engine)."""
    tellinger = melding.get("tellinger", {})
    return {"tellinger": tellinger,
            "sum": sum(tellinger.values()),
            "feil": len(melding.get("feil", []))}


def bro_runde(emner: dict) -> dict:
    """One round: read the states (via the reader interface that is fed
    in), analyse, return the engine input. The reading itself happens
    through the verden-MCP (the house STREAM.MSG.GET form)."""
    resultat = {}
    for navn, (emne, analyser, melding) in emner.items():
        resultat[navn] = analyser(melding) if melding else {
            "lesbar": False,
            "note": "no message — the bridge waits for connector deploy"}
    return resultat
