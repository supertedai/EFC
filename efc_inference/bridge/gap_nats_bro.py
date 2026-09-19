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

SUBJECT_VOLCANO = "kosmos.jord.tilstand.usgs-vulkan"
SUBJECT_OCEAN = "verden.klima.tilstand.noaa-tides"
SUBJECT_PLANTS = "verden.miljo.tilstand.gbif-planter"

LEGITIMASJON = os.environ.get("NATS_LEGITIMASJON",
                              "/etc/nats/legitimasjon.env")
TIMEOUT = 20


def _legit(role: str = "KONSUMENT"):
    try:
        for line in open(LEGITIMASJON, encoding="utf-8"):
            if line.startswith(f"NATS_{role}="):
                m = re.match(r"nats://([^:]+):([^@]+)@([^:]+):(\d+)",
                             line.split("=", 1)[1].strip())
                if m:
                    return (m.group(1), m.group(2), m.group(3),
                            int(m.group(4)), "")
    except OSError as e:
        return None, None, None, None, f"{LEGITIMASJON}: {type(e).__name__}"
    return None, None, None, None, f"the role {role} is missing"


def analyser_vulkan(message: dict) -> dict:
    """VHP state -> regime classification (the status list)."""
    state = message.get("tilstand", {})
    active_count = sum(1 for v in state.values()
                       if str(v.get("nivaa", "")).upper()
                       not in ("", "NORMAL", "GREEN"))
    return {"antall_spurte": message.get("antall_spurte", 0),
            "antall_aktive": active_count,
            "prosent_aktive": round(100 * active_count /
                                    max(1, message.get("antall_spurte", 1)),
                                    1)}


def analyser_hav(message: dict) -> dict:
    """NOAA temperatures -> proxy for ocean energy (the climate engine)."""
    temps = message.get("temperaturer_c", {})
    values = [v for v in temps.values()
              if isinstance(v, (int, float)) and v == v]
    if not values:
        return {"maalt": False, "antall_stasjoner":
                message.get("antall_stasjoner", 0)}
    return {"maalt": True, "middel_c": round(sum(values) /
                                             len(values), 2),
            "min_c": round(min(values), 2),
            "max_c": round(max(values), 2),
            "antall_maalte": len(values)}


def analyser_planter(message: dict) -> dict:
    """GBIF counts -> biosphere footprint (the energy-flow engine)."""
    counts = message.get("tellinger", {})
    return {"tellinger": counts,
            "sum": sum(counts.values()),
            "feil": len(message.get("feil", []))}


def bro_runde(subjects: dict) -> dict:
    """One round: read the states (via the reader interface that is fed
    in), analyse, return the engine input. The reading itself happens
    through the verden-MCP (the house STREAM.MSG.GET form)."""
    results = {}
    for name, (subject, analyse, message) in subjects.items():
        results[name] = analyse(message) if message else {
            "readable": False,
            "note": "no message — the bridge waits for connector deploy"}
    return results
