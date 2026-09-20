"""Regression tests for epistemic scope and engine identifiers."""
from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]
NODER = json.loads((ROOT / "schema" / "regime_nodes.jsonld").read_text())[
    "nodes"
]
NODE_BY_ID = {node["id"]: node for node in NODER}
ENGINE_STEMS = {
    path.stem
    for path in (ROOT / "efc_inference" / "engine").glob("*.py")
    if path.name not in {"__init__.py", "base_engine.py"}
}


def test_dommekraft_skiller_lokal_stottet_fra_global_hypotese() -> None:
    """A local measurement can be supported without making the whole ledger supported."""
    epistemikk = NODE_BY_ID["opus.dommekraft"]["epistemikk"]
    kobling = NODE_BY_ID["opus.dommekraft"]["coupling"]

    assert epistemikk["sannhetsstatus"] == "hypotese"
    assert "every action is judged on its own" in kobling["local"]
    assert "NOT measured" in kobling["global"]
    assert "hypothesis" in kobling["global"]
    assert epistemikk["evidensstatus"] == "proxy"


def test_motoridentifikatorer_er_filer_eller_eksplisitt_virtuelle() -> None:
    """The five known deviations shall not pretend to be engine files."""
    berorte = {"efc.l0", "efc.l1", "efc.l2", "efc.l3", "efc.victron_cccv_engine"}
    for node_id in berorte:
        stipulasjoner = NODE_BY_ID[node_id]["stipulasjoner"]
        motor = stipulasjoner.get("motor")
        if motor:
            assert motor in ENGINE_STEMS, (node_id, motor)
        else:
            assert "abstract layer" in stipulasjoner.get("motor_status", ""), node_id


def test_virtuelle_lag_er_merket_uten_motorfelt() -> None:
    """L0–L3 are abstract phase layers, not engine files."""
    for node_id in ("efc.l0", "efc.l1", "efc.l2", "efc.l3"):
        stipulasjoner = NODE_BY_ID[node_id]["stipulasjoner"]
        assert "motor" not in stipulasjoner
        assert "abstract layer" in stipulasjoner["motor_status"]


def test_victron_peker_paa_victron_motorfil() -> None:
    """The Victron node shall follow the file stem victron.py."""
    stipulasjoner = NODE_BY_ID["efc.victron_cccv_engine"]["stipulasjoner"]
    assert stipulasjoner["motor"] == "victron"
    assert stipulasjoner["motor"] in ENGINE_STEMS
