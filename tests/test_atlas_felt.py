"""Ontological field declaration and the C(S) positions for observers."""
from __future__ import annotations

import json
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
KILDE = ROT / "schema" / "regime_nodes.jsonld"
OBS_PREFIXER = ("obs.", "homo.", "efc.selv.")


def _noder() -> dict[str, dict]:
    return {node["id"]: node for node in json.loads(KILDE.read_text())["nodes"]}


def _observatoer_ids(noder: dict[str, dict]) -> list[str]:
    return ["opus.dommekraft"] + sorted(
        nid for nid in noder if nid.startswith(OBS_PREFIXER)
    )


def test_c0_deklarerer_bevissthetsfeltet_som_ontologi() -> None:
    gyldighet = _noder()["efc.lag_c0"]["regime"]["validity"].lower()
    assert "the field" in gyldighet
    assert "lets everything be" in gyldighet
    assert "c(s)" in gyldighet


def test_dommekraft_har_c_s_posisjon_fra_som_selvmodellerende_observatoer() -> None:
    posisjon = _noder()["opus.dommekraft"]["observer"]["c_s_posisjon"].lower()
    assert "s>0" in posisjon
    assert "differentiated" in posisjon
    assert "r_c" in posisjon


def test_alle_bevissthetssporets_observatoerer_har_c_s_posisjon() -> None:
    noder = _noder()
    ids = _observatoer_ids(noder)
    assert len(ids) >= 5
    assert all(noder[nid].get("observer", {}).get("c_s_posisjon") for nid in ids)
