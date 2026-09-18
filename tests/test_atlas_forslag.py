"""Tester innmatings-lytteren uten aa endre atlas-nodene."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CLI = ROT / "scripts" / "maintenance" / "atlas_forslag.py"
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


def kjør(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [PYTHON, str(CLI), *args], cwd=ROT, capture_output=True,
        text=True, check=False,
    )


def les_svar(prosess: subprocess.CompletedProcess[str]) -> dict:
    assert prosess.returncode == 0, prosess.stderr
    return json.loads(prosess.stdout)


def test_kjent_fragment_foreslaas_som_nodeverdig_med_domene() -> None:
    svar = les_svar(kjør("--tekst", "vulkansk aske i stratosfaeren"))

    assert svar["forslag"][0]["kategori"] == "node-verdig"
    assert svar["forslag"][0]["domene_forslag"]
    assert "kosmos.jord" in svar["forslag"][0]["domene_forslag"]
    assert svar["forslag"][0]["opprettet_node"] is False


def test_uforstaalig_fragment_foreslaas_som_uten_hjem() -> None:
    svar = les_svar(kjør("--tekst", "kwisatz haderach"))

    assert svar["forslag"][0]["kategori"] == "uten_hjem"
    assert svar["forslag"][0]["nodeverdig"] is False


def test_vurdering_foreslaas_til_hindsight() -> None:
    svar = les_svar(kjør("--tekst", "jeg tror kanskje dette burde vaere sant"))

    assert svar["forslag"][0]["kategori"] == "ikke-node-verdig"
    assert svar["forslag"][0]["destinasjon"] == "Hindsight-retain"
    assert svar["forslag"][0]["nodeverdig"] is False


def test_listeneren_mutere_ikke_regime_nodes() -> None:
    før = ATLAS.read_bytes()
    svar = les_svar(kjør("--tekst", "vulkansk aske i stratosfaeren"))
    etter = ATLAS.read_bytes()

    assert svar["forslag"]
    assert etter == før


def test_alle_leser_koe_og_returnerer_liste(tmp_path: Path) -> None:
    kø = tmp_path / "atlas_fragmenter.jsonl"
    kø.write_text(
        json.dumps({"tekst": "vulkansk aske i stratosfaeren"}) + "\n"
        + json.dumps({"tekst": "kwisatz haderach"}) + "\n",
        encoding="utf-8",
    )

    svar = les_svar(kjør("--alle", "--inntak-fil", str(kø)))

    assert [x["kategori"] for x in svar["forslag"]] == [
        "node-verdig", "uten_hjem"
    ]
    assert kø.read_text(encoding="utf-8").count("\n") == 2
