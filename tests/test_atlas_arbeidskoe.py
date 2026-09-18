"""Tester arbeidskoeen mot den versjonerte atlasbanken."""
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

#: `sys.executable`, ikke en hardkodet sti: en test som bare virker
#: med prosjektets venv feiler i en kopi uten den — og da maaler den
#: miljoeet, ikke koden.
PYTHON = sys.executable
CLI = ROT / "scripts" / "atlas_arbeidskoe.py"
REF = "HEAD"


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
    # SAMME definisjon av «fylt» som koden. Foerste utgave regnet ventetallet
    # med `bool()`, mens koden brukte sin egen `_fylt()` — to definisjoner av
    # samme ord, og en test som ville passert selv om de gled fra hverandre.
    ventet = {
        felt: sum(_fylt((n.get("maale_paradigme") or {}).get(felt))
                  for n in noder)
        for felt in felter
    }
    ventet["rcmp"] = sum(_fylt(n.get("rcmp")) for n in noder)
    assert kjoer("--sakse")["maalte"] == ventet


def test_manglende_plassering_feiler_istedenfor_aa_gjette():
    """En node uten plassering skal meldes, ikke bli «ghost» av en standardverdi.

    Klasseslekten er maalt: `PLASSERING.get(navn, ("ghost", 8))` gjorde 68 av
    73 noder til «ikke bygget» i atlaset, og feilen saa ut som data.
    """
    import atlas_arbeidskoe

    node = {"id": "finnes.ikke", "synlighet": "offentlig"}
    with pytest.raises(SystemExit, match="PLASSERING"):
        atlas_arbeidskoe.arbeidskoe_ghost({"nodes": [node]}, {})


def test_hvitrom_er_ikke_et_svar():
    """`"   "` er ikke en maaling, selv om strengen er sann."""
    import atlas_arbeidskoe

    assert atlas_arbeidskoe._fylt("   ") is False
    assert atlas_arbeidskoe._fylt(None) is False
    assert atlas_arbeidskoe._fylt(False) is True       # deklarert svar
    assert atlas_arbeidskoe._fylt(0) is True           # deklarert svar


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
