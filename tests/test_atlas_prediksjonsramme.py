"""Vakt for forseglede fs8/DH_over_rd-rammer i atlaset."""
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
ATLAS = ROT / "schema" / "regime_nodes.jsonld"
DOI = "10.6084/m9.figshare.32013156"
VENTER = "waiting for arbiter: DESI DR2 full-shape"


def _noder():
    return {n["id"]: n for n in json.loads(ATLAS.read_text())["nodes"]}


def test_atlaset_baerer_seglede_fs8_og_dh_rammesider():
    noder = _noder()
    assert len([n for n in noder.values() if "prediction" in n]) > 4

    fs8 = noder["obs.fsigma8"]["prediction"]
    assert fs8["sealed_doi"] == DOI
    assert json.loads(fs8["expected"]) == {
        "fsigma8_efc": 0.43,
        "fsigma8_lcdm": 0.449,
        "separasjon_sigma": 2.0,
        "z_eff": 0.7,
    }

    dh = noder["obs.bao"]["prediction"]
    assert dh["sealed_doi"] == DOI
    assert json.loads(dh["expected"]) == [
        {"DH_over_rd_efc": 19.797, "DH_over_rd_lcdm": 20.719, "separasjon_sigma": 2.3, "z_eff": 0.7},
        {"DH_over_rd_efc": 16.527, "DH_over_rd_lcdm": 17.466, "separasjon_sigma": 3.1, "z_eff": 1.0},
    ]


def test_seglede_prediksjoner_har_frys_og_venter_uten_oppgjoer():
    for node in _noder().values():
        prediction = node.get("prediction", {})
        if prediction.get("sealed_doi") != DOI:
            continue
        assert prediction.get("freeze"), node["id"]
        assert prediction.get("criterion"), node["id"]
        settlement = node.get("settlement")
        assert settlement["outcome"] == VENTER, node["id"]
        assert prediction["criterion"] in settlement["expected"], node["id"]
        assert settlement["outcome_source"] == "arbiter", node["id"]
