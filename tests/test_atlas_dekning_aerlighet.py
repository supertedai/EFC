"""Vakt for dekning som ikke motsier sin egen begrunnelse."""
from __future__ import annotations

import json
import re
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(encoding="utf-8"))
NODER = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))["nodes"]
SNAPSHOT = json.loads((ROT / "schema" / "nats_domener.snapshot.json").read_text(encoding="utf-8"))["domener"]


def test_dekket_begrunnelse_kan_ikke_innromme_et_gap():
    """En dekket-status kan ikke samtidig si at domenet mangler noe."""
    funnet = []
    for domene, rad in DEKNING["domener"].items():
        if rad["status"] != "dekket":
            continue
        if re.search(r"mangler|ikke[_ ]dekket", rad.get("begrunnelse", ""), re.IGNORECASE):
            funnet.append(domene)
    assert not funnet, f"dekket-status med egen gap-innrømmelse: {funnet}"


def test_dekket_stromdomene_eies_av_instrument_eller_observasjon():
    """Et målt domene kan ikke kalles dekket av bare motor-noder."""
    per_domene = {}
    for node in NODER:
        domene = node.get("buss_domene")
        if domene and node.get("phase") in {"instrument", "observasjon"}:
            per_domene.setdefault(domene, []).append(node["id"])
    uten_maling = []
    for domene, rad in DEKNING["domener"].items():
        har_stroem = bool(SNAPSHOT.get(domene, {}).get("emner"))
        if rad["status"] == "dekket" and har_stroem and not per_domene.get(domene):
            uten_maling.append(domene)
    assert not uten_maling, (
        "dekket-domener med målte strømmer uten instrument/observasjon: "
        f"{uten_maling}"
    )
