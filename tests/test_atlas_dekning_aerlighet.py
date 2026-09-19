"""Guard for coverage that does not contradict its own justification."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(encoding="utf-8"))
NODER = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))["nodes"]
SNAPSHOT = json.loads((ROT / "schema" / "nats_domener.snapshot.json").read_text(encoding="utf-8"))["domener"]


def test_dekket_begrunnelse_kan_ikke_innromme_et_gap():
    """A covered status cannot at the same time say that the domain lacks something."""
    funnet = []
    for domene, rad in DEKNING["domener"].items():
        if rad["status"] != "dekket":
            continue
        if re.search(r"mangler|ikke[_ ]dekket", rad.get("begrunnelse", ""), re.IGNORECASE):
            funnet.append(domene)
    assert not funnet, f"covered status with its own admitted gap: {funnet}"


def test_dekket_stromdomene_eies_av_instrument_eller_observasjon():
    """A measured domain cannot be called covered by engine nodes alone."""
    per_domene = {}
    for node in NODER:
        domene = node.get("buss_domene")
        if domene and node.get("phase") in {"instrument", "observation"}:
            per_domene.setdefault(domene, []).append(node["id"])
    uten_maling = []
    for domene, rad in DEKNING["domener"].items():
        har_stroem = bool(SNAPSHOT.get(domene, {}).get("emner"))
        if rad["status"] == "dekket" and har_stroem and not per_domene.get(domene):
            uten_maling.append(domene)
    assert not uten_maling, (
        "covered domains with measured flows but no instrument/observation: "
        f"{uten_maling}"
    )
