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
        assert node["stipulasjoner"]["motor_status"] == "instrument — needs no engine"


def test_every_waiting_node_states_its_state_truthfully():
    """A waiting node may GAIN a bus domain -- then it must say what is still missing.

    Measured 2026-09-19 (commit 53721bad wired DESI DR2 BAO in): the DESI-BAO node
    now carries `buss_domene: kosmos.kosmologi` because the BAO part of DR2 is
    published and carried by obs.bao, while its open question still names the
    missing LIVE stream. The earlier version of this test demanded that a waiting
    node have NO bus domain -- true while the connector did not exist, and wrong
    the day one landed. The rule that survives is: no node may wait in silence.
    """
    noder = {node["id"]: node for node in NODER}
    for node_id in ("kosmos.kosmologi_desi_bao", "verden.klima_isbre"):
        node = noder[node_id]
        stip = node.get("stipulasjoner") or {}
        if node.get("buss_domene"):
            aapne = node.get("open_questions") or []
            assert aapne, (
                f"{node_id} has a bus domain but names nothing it still waits for")
        else:
            assert stip.get("buss_status"), (
                f"{node_id} has no bus domain and no written reason")
            s = stip["buss_status"]
            assert ("does not exist" in s or "no stream" in s.lower() or
                    "absent" in s.lower()), (
                f"{node_id} must say WHY it has no domain: {stip.get('buss_status')!r}")


def test_homo_nodene_ligger_i_s_regime():
    assert all(node["maale_paradigme"]["s_regime"] == "S~0.5"
               for node in NODER if node["id"].startswith("homo."))
    assert all("C(S) at S~0.5" in node["maale_paradigme"]["klarhetsfunksjon"]
               for node in NODER if node["id"].startswith("homo."))


def test_restlistedomenene_er_dekket():
    for domene in ("kosmos.romvaer", "kosmos.sol", "kosmos.transienter",
                   "kosmos.kosmologi", "verden.klima"):
        assert DEKNING[domene]["status"] == "dekket"
