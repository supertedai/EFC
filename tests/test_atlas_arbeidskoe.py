"""Tests the work queue against the versioned atlas bank."""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))
from atlas_arbeidskoe import _fylt  # noqa: E402

#: `sys.executable`, not a hard-coded path: a test that only works
#: with the project's venv fails in a copy without it — and then it measures
#: the environment, not the code.
PYTHON = sys.executable
CLI = ROT / "scripts" / "atlas_arbeidskoe.py"
REF = "HEAD"


def kjoer(mode: str) -> dict:
    """Machine-readable mode. The default output is READABLE (see the test below)."""
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
    """A queue that exists only as JSON is not a queue for a human.

    Measured 2026-09-18: the first version wrote JSON in every mode. Correct,
    but whoever had to choose what gets filled next had to fetch an extra tool.
    """
    for mode in ("--sakse", "--ghost"):
        ut = kjoer_raa(mode)
        assert not ut.lstrip().startswith("{"), f"{mode} writes JSON by default"
        assert "missing" in ut or "built" in ut, ut[:200]


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
    raise AssertionError("PLASSERING is missing")


def test_tellingene_er_utledet_fra_offentlig_bank():
    noder = [n for n in bank()["nodes"] if n.get("synlighet") == "offentlig"]
    felter = ["s_regime", "klarhetsfunksjon", "ebe_function", "sektor"]
    # The SAME definition of filled as the code. The first version computed the
    # expected count with `bool()`, while the code used its own `_fylt()` — two
    # definitions of the same word, and a test that would pass even if they
    # drifted apart.
    ventet = {
        felt: sum(_fylt((n.get("maale_paradigme") or {}).get(felt))
                  for n in noder)
        for felt in felter
    }
    ventet["rcmp"] = sum(_fylt(n.get("rcmp")) for n in noder)
    assert kjoer("--sakse")["maalte"] == ventet


def test_manglende_plassering_feiler_istedenfor_aa_gjette():
    """A node without a placement must be reported, not become «ghost» from a default.

    The class of defect is measured: `PLASSERING.get(navn, ("ghost", 8))` turned
    68 of 73 nodes into not-yet-built rows in the atlas, and the error looked
    like data.
    """
    import atlas_arbeidskoe

    node = {"id": "does.not-exist", "synlighet": "offentlig"}
    with pytest.raises(SystemExit, match="PLASSERING"):
        atlas_arbeidskoe.arbeidskoe_ghost({"nodes": [node]}, {})


def test_hvitrom_er_ikke_et_svar():
    """`"   "` is not a measurement, even if the string is true."""
    import atlas_arbeidskoe

    assert atlas_arbeidskoe._fylt("   ") is False
    assert atlas_arbeidskoe._fylt(None) is False
    assert atlas_arbeidskoe._fylt(False) is True       # declared answer
    assert atlas_arbeidskoe._fylt(0) is True           # declared answer


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
