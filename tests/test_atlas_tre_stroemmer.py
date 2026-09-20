"""Regresjonstest for de åtte målte NATS-strømmene."""
from __future__ import annotations

import json
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
NODER = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))["nodes"]
DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(encoding="utf-8"))["domener"]


FORVENTET = {
    "kosmos.galakser_mast": ("kosmos.galakser", "observasjon.mast-caom"),
    "verden.klima_gdelt": ("verden.klima", "observasjon.gdelt-gkg"),
    "verden.klima_worldbank": ("verden.klima", "tilstand.world-bank"),
    "verden.miljo_mikrobiom": ("verden.miljo", "tilstand.mgnify-mikrobiom"),
    "verden.miljo_gdelt": ("verden.miljo", "observasjon.gdelt-gkg"),
    "verden.oekonomi_worldbank": ("verden.oekonomi", "tilstand.world-bank"),
    "verden.oekonomi_imf": ("verden.oekonomi", "prediksjon.imf-datamapper"),
    "verden.oekonomi_gdelt": ("verden.oekonomi", "observasjon.gdelt-gkg"),
}


def test_de_tre_stroemnodene_eier_riktig_bussdomene():
    """Hver levende strøm skal ha en egen instrument-node."""
    noder = {node["id"]: node for node in NODER}
    for node_id, (domene, _) in FORVENTET.items():
        assert node_id in noder
        assert noder[node_id]["phase"] == "instrument"
        assert noder[node_id]["buss_domene"] == domene


def test_de_tre_stroemnodene_baerer_maalingskontrakten():
    """Each node must declare its measurement, its engine status, its
    falsifiability and its source. The rationale is the SHARED instrument
    class (a declared class, not a per-node sentence): measured 2026-09-19,
    63 of 126 nodes carry it, and this file previously pinned the same text
    in a second spelling without diacritics."""
    noder = {node["id"]: node for node in NODER}
    for node_id, (domene, stroem) in FORVENTET.items():
        node = noder[node_id]
        assert node["measure"]["placement"] == "observation"
        assert node["measure"]["target"]
        assert node["measure"]["measurer"]
        assert node["measure"]["instrument"]
        assert node["measure"]["proxy_chain"]
        assert node["ontology"]["source"] == stroem
        prov = node["ontology"]["proveniens"]
        assert {k["type"] for k in prov["kilder"]} == {"stroem"}
        assert prov["kilder"][0]["ref"] == stroem
        assert prov["begrensning"]
        assert prov["fullstendig"] is False
        assert node["stipulasjoner"]["motor_status"] == "instrument — needs no engine"
        assert node["stipulasjoner"]["ikke_falsifiserbar_grunn"] == (
            "The instrument node cannot be felled by an observation — it IS the "
            "measurement; any falsification belongs to the claim that uses the "
            "measurement."
        )
        assert node["epistemikk"]["konsensus_er_ikke_sannhet"] is True
        assert node["perspektiv"] == "konsensus"
        assert node["synlighet"] == "offentlig"


def test_de_to_domenene_er_dekket_med_stroemmene():
    """Dekningsfilen skal vise de målte domenene som dekket."""
    assert DEKNING["kosmos.galakser"]["status"] == "dekket"
    assert DEKNING["verden.klima"]["status"] == "dekket"
    assert "mast-caom" in DEKNING["kosmos.galakser"]["begrunnelse"]
    assert "gdelt-gkg" in DEKNING["verden.klima"]["begrunnelse"]
    assert "world-bank" in DEKNING["verden.klima"]["begrunnelse"]
