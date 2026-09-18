"""Ekte CLI-tester for atlasets retain-inngang."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
CLI = REPO / "scripts" / "atlas_lesing.py"


def kjør_inntak(tmp_path: Path, tekst: str, kilde: str) -> subprocess.CompletedProcess[str]:
    """Run the real CLI against an isolated intake area."""
    data = tmp_path / "data"
    data.mkdir(exist_ok=True)
    # CLI-en bruker repoets data/inntak; testens repo er derfor en kopi av
    # bare inntaksomraadet via miljøvariabelen i den offentlige funksjonen.
    return subprocess.run(
        [PYTHON, str(CLI), str(REPO), "--ref", "HEAD", "--innta", tekst,
         "--kilde", kilde, "--inntak-fil", str(data / "atlas_fragmenter.jsonl")],
        cwd=REPO, capture_output=True, text=True, check=False,
    )


def les_linjene(sti: Path) -> list[dict]:
    return [json.loads(linje) for linje in sti.read_text(encoding="utf-8").splitlines()]


def test_innta_skriver_ekte_plassering_med_kilde_og_tidspunkt(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    resultat = kjør_inntak(tmp_path, "vulkansk aske i stratosfaeren", "samtale")

    assert resultat.returncode == 0, resultat.stderr
    assert "written to" in resultat.stdout
    record = les_linjene(fil)[0]
    assert record["tekst"] == "vulkansk aske i stratosfaeren"
    assert record["kilde"] == "samtale"
    assert record["tidspunkt"]
    assert record["plasseringsstatus"] == "uten_hjem"
    assert record["forslag"][0]["noder"] == ["kosmos.jord.vulkan"]


def test_innta_ukjent_fragment_blir_arlig_uten_hjem(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    resultat = kjør_inntak(tmp_path, "kwisatz haderach", "test")

    assert resultat.returncode == 0, resultat.stderr
    record = les_linjene(fil)[0]
    assert record["plasseringsstatus"] == "uten_hjem"
    assert record["domene_visshet"] == "ingen_anelse"
    assert record["kilde"] == "test"


def test_innta_er_append_only_for_to_fragmenter(tmp_path: Path) -> None:
    fil = tmp_path / "data" / "atlas_fragmenter.jsonl"
    første = kjør_inntak(tmp_path, "vulkansk aske i stratosfaeren", "samtale")
    andre = kjør_inntak(tmp_path, "kwisatz haderach", "samtale")

    assert første.returncode == andre.returncode == 0
    linjer = les_linjene(fil)
    assert len(linjer) == 2
    assert [x["tekst"] for x in linjer] == [
        "vulkansk aske i stratosfaeren", "kwisatz haderach"
    ]
