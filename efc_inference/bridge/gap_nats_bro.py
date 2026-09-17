"""gap_nats_bro — tre broer fra NATS inn i EFC-motorene (hav, planter, vulkan).

    kosmos.jord.vulkan.usgs-vhp        -> vulkan-tilstand (regime-status)
    verden.hav.tilstand.noaa-tides     -> hav-temperatur-proxy
    verden.biosfaere.tilstand.gbif-planter -> biosfaere-tellinger

Tilstandene er beskrevet i kaldarkiv-seed (Hetzner PR #1006). Disse
broene LESER stroemmene og mater motorene — injiserbarhetsdesignet:
NATS er ikke en atlas-node, NATS -> bro -> motor -> atlas-node.
"""
from __future__ import annotations

import json
import os
import re
import socket

EMNE_VULKAN = "kosmos.jord.vulkan.usgs-vhp"
EMNE_HAV = "verden.hav.tilstand.noaa-tides"
EMNE_PLANTER = "verden.biosfaere.tilstand.gbif-planter"

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
    return None, None, None, None, f"rollen {rolle} mangler"


def analyser_vulkan(melding: dict) -> dict:
    """VHP-tilstand -> regime-klassifisering (statuslisten)."""
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
    """NOAA-temperaturer -> proxy for hav-energi (klima-motoren)."""
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
    """GBIF-tellinger -> biosfaere-fotavtrykk (enerflyt-motoren)."""
    tellinger = melding.get("tellinger", {})
    return {"tellinger": tellinger,
            "sum": sum(tellinger.values()),
            "feil": len(melding.get("feil", []))}


def bro_runde(emner: dict) -> dict:
    """Én runde: les tilstandene (via lesergrensesnittet som mates
    inn), analyser, returner motoren-input. Lesingen selv skjer
    gjennom verden-mcp (husets STREAM.MSG.GET-form)."""
    resultat = {}
    for navn, (emne, analyser, melding) in emner.items():
        resultat[navn] = analyser(melding) if melding else {
            "lesbar": False,
            "note": "ingen melding — broen venter paa konnektor-deploy"}
    return resultat
