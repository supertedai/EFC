"""Regresjonstester for den mekaniske restlisten i atlaset."""
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
NODER = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))["nodes"]
DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(encoding="utf-8"))["domener"]


def test_motor_only_domenene_har_instrumentnoder():
    noder = {node["id"]: node for node in NODER}
    forventet = {
        "kosmos.romvaer_swpc": ("kosmos.romvaer", "tilstand.swpc-kp"),
        "kosmos.sol_goes": ("kosmos.sol", "tilstand.swpc-goes-xray"),
        "kosmos.transienter_alerce": ("kosmos.transienter", "hendelse.alerce"),
    }
    for node_id, (domene, stroem) in forventet.items():
        node = noder[node_id]
        assert node["phase"] == "instrument"
        assert node["buss_domene"] == domene
        assert node["ontology"]["source"] == stroem
        assert node["ontology"]["proveniens"]["kilder"][0]["type"] == "stroem"
        assert node["stipulasjoner"]["motor_status"] == "instrument — trenger ingen motor"


def test_ventenodene_er_aerlige_og_uten_bussdomene():
    noder = {node["id"]: node for node in NODER}
    for node_id in ("kosmos.kosmologi_desi_bao", "verden.klima_isbre"):
        node = noder[node_id]
        assert "buss_domene" not in node
        assert "the stream does not exist" in node["stipulasjoner"]["buss_status"]
        assert node["ontology"]["proveniens"]["kilder"][0]["type"] == "intern"


def test_homo_nodene_ligger_i_s_regime():
    assert all(node["maale_paradigme"]["s_regime"] == "S~0.5"
               for node in NODER if node["id"].startswith("homo."))
    assert all("C(S) ved S~0.5" in node["maale_paradigme"]["klarhetsfunksjon"]
               for node in NODER if node["id"].startswith("homo."))


def test_restlistedomenene_er_dekket():
    for domene in ("kosmos.romvaer", "kosmos.sol", "kosmos.transienter",
                   "kosmos.kosmologi", "verden.klima"):
        assert DEKNING[domene]["status"] == "dekket"
