"""Tester arbeidskoeen mot den versjonerte atlasbanken."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
PYTHON = Path("/opt/venvs/t_123ed6d9/bin/python")
CLI = ROT / "scripts" / "atlas_arbeidskoe.py"
REF = "origin/main"


def kjoer(mode: str) -> dict:
    """Maskinlesbar modus. Standardutskriften er LESBAR (se testen under)."""
    ut = subprocess.run(
        [str(PYTHON), str(CLI), mode, "--json", "--ref", REF],
        cwd=ROT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(ut.stdout)


def kjoer_raa(mode: str) -> str:
    return subprocess.run(
        [str(PYTHON), str(CLI), mode, "--ref", REF],
        cwd=ROT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout


def test_standardutskriften_er_lesbar_ikke_json():
    """En koe som bare finnes som JSON er ikke en koe for et menneske.

    Maalt 2026-09-18: foerste utgave skrev JSON i alle modi. Riktig, men den
    som skal velge hva som fylles neste gang maatte hente et ekstra verktoy.
    """
    for mode in ("--sakse", "--ghost"):
        ut = kjoer_raa(mode)
        assert not ut.lstrip().startswith("{"), f"{mode} skriver JSON som standard"
        assert "mangler" in ut or "bygget" in ut, ut[:200]


def bank() -> dict:
    raw = subprocess.check_output(
        ["git", "show", f"{REF}:schema/regime_nodes.jsonld"],
        cwd=ROT,
    )
    return json.loads(raw)


def plassering() -> dict[str, tuple[str, int]]:
    raw = subprocess.check_output(
        ["git", "show", f"{REF}:scripts/maintenance/efc_atlas_generator.py"],
        cwd=ROT,
        text=True,
    )
    tree = ast.parse(raw)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "PLASSERING" for t in node.targets
        ):
            return ast.literal_eval(node.value)
    raise AssertionError("PLASSERING mangler")


def test_tellingene_er_utledet_fra_offentlig_bank():
    noder = [n for n in bank()["nodes"] if n.get("synlighet") == "offentlig"]
    felter = ["s_regime", "klarhetsfunksjon", "ebe_function", "sektor"]
    ventet = {
        felt: sum(bool((n.get("maale_paradigme") or {}).get(felt)) for n in noder)
        for felt in felter
    }
    ventet["rcmp"] = sum(bool(n.get("rcmp")) for n in noder)
    assert kjoer("--sakse")["maalte"] == ventet


def test_node_med_alle_feltene_er_ikke_i_saksekoeen():
    sys.path.insert(0, str(ROT / "scripts"))
    from atlas_arbeidskoe import sakse_noder

    node = {
        "id": "syntetisk.ferdig",
        "synlighet": "offentlig",
        "maale_paradigme": {felt: "maalt" for felt in
                            ("s_regime", "klarhetsfunksjon", "ebe_function", "sektor")},
        "rcmp": {"deklarasjon": "maalt"},
    }
    koe, maalte = sakse_noder([node])
    assert maalte == {
        "s_regime": 1,
        "klarhetsfunksjon": 1,
        "ebe_function": 1,
        "sektor": 1,
        "rcmp": 1,
    }
    assert koe == []


def test_sakse_skil_manglende_felt_fra_tomt_felt():
    sys.path.insert(0, str(ROT / "scripts"))
    from atlas_arbeidskoe import sakse_noder

    node = {"id": "syntetisk.delvis", "maale_paradigme": {"s_regime": ""}}
    koe, _ = sakse_noder([node])
    statuser = {rad["felt"]: rad["status"] for rad in koe[0]["mangler"]}
    assert statuser["s_regime"] == "tomt"
    assert statuser["klarhetsfunksjon"] == "finnes_ikke"
    assert statuser["rcmp"] == "finnes_ikke"


def test_hver_ghost_i_banken_staar_en_gang():
    ghost = {
        n["id"] for n in bank()["nodes"]
        if n.get("synlighet") == "offentlig"
        and plassering().get(n["id"], ("ghost", 8))[0] == "ghost"
    }
    faktisk = [n["id"] for n in kjoer("--ghost")["noder"]]
    assert len(faktisk) == len(set(faktisk))
    assert set(faktisk) == ghost


def test_json_er_deterministisk():
    assert kjoer("--sakse") == kjoer("--sakse")
    assert kjoer("--ghost") == kjoer("--ghost")
