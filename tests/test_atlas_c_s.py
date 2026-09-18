"""C(S)-deklarasjoner langs den roterbare S-aksen."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
NODER = {
    "efc.l0",
    "efc.l1",
    "efc.l2",
    "efc.l3",
    "efc.lag_s",
    "efc.lag_d",
    "efc.lag_c0",
}


def _atlas() -> dict:
    return json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text())


def _cs(node: dict) -> str:
    return node["maale_paradigme"]["klarhetsfunksjon"]


def test_s_aksen_viser_c_s_deklarasjoner_for_alle_s_baerende_noder() -> None:
    resultat = subprocess.run(
        [sys.executable, "scripts/atlas_lesing.py", "--akse", "S", "--ref", "HEAD", str(ROT)],
        cwd=ROT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert len(NODER) == 7
    assert all(nid in resultat.stdout for nid in NODER)
    assert resultat.stdout.count("C(S)") >= len(NODER)


def test_l2_c_s_deklarerer_r_c_terskelen() -> None:
    noder = {node["id"]: node for node in _atlas()["nodes"]}
    assert "R_c" in _cs(noder["efc.l2"])


def test_c_s_kobler_begge_doi_kildene() -> None:
    noder = {node["id"]: node for node in _atlas()["nodes"]}
    kilder = " ".join(node["ontology"]["source"] for node in noder.values())
    assert "10.6084/m9.figshare.28098386" in kilder
    assert "10.6084/m9.figshare.30275947" in kilder


def test_propofol_eeg_er_synlig_som_lokal_c_s_maaling() -> None:
    noder = {node["id"]: node for node in _atlas()["nodes"]}
    tekst = _cs(noder["efc.lag_c0"])
    assert "propofol-EEG" in tekst
    assert "locally" in tekst
