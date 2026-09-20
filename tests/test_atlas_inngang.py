"""TWO GAPS.

1. THE SEARCH does not normalize hyphen against space. Measured 2026-09-18:
   `--emne "energy-flow"` hit, `--emne "energy flow"` gave 0 hits.
   The words Morten uses have both forms.

2. THE ENTRY POINT. We can rotate around everything that IS ALREADY in the atlas. But when we
   make a NEW observation there is no path from it and into the map.
   The couplings are there; the entry point for new fragments is not.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import atlas_lesing  # noqa: E402


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(REPO, ref="HEAD")


class TestSoeketNormaliserer:

    def test_bindestrek_og_mellomrom_er_samme_ord(self, atlas: dict) -> None:
        a = atlas_lesing.finn(REPO, "energy-flow", "HEAD")
        b = atlas_lesing.finn(REPO, "energy flow", "HEAD")
        assert {x["id"] for x in a["treff"]}, "energy-flow hit nothing"
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in b["treff"]}, \
            "hyphen and space give different hits"

    def test_understrek_er_ogsaa_samme(self, atlas: dict) -> None:
        a = atlas_lesing.finn(REPO, "energi-flyt", "HEAD")
        c = atlas_lesing.finn(REPO, "energi flyt", "HEAD")
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in c["treff"]}

    def test_store_og_smaa_bokstaver(self, atlas: dict) -> None:
        a = atlas_lesing.finn(REPO, "EFC-D", "HEAD")
        b = atlas_lesing.finn(REPO, "efc-d", "HEAD")
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in b["treff"]}


class TestInngangen:
    """Place a NEW observation in the atlas and rotate around it."""

    def test_plasser_foreslaar_hjem_for_et_fragment(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "PAH i interstellar støv")
        assert p["forslag"], "no suggestion for where the fragment belongs"
        forslag = p["forslag"][0]
        assert "domene" in forslag and "noder" in forslag

    def test_plasser_sier_hva_som_MANGLER(self, atlas: dict) -> None:
        """A fragment no node owns shall not be hidden — it is a finding."""
        p = atlas_lesing.plasser(atlas, "xylofonstemning i mars")
        assert p["status"] in ("uten_hjem", "svakt")
        assert p.get("naere_noder") is not None

    def test_plasser_gir_aksene_fragmentet_maa_utfylle(self, atlas: dict) -> None:
        """The entry point is not a hole — it is a list of what must be filled in."""
        p = atlas_lesing.plasser(atlas, "PAH i interstellar støv")
        # the union of all nodes' fields — not the first node's, which can
        # lack a field the others have (layering arrived 2026-09-18).
        paakrevd = set()
        for n in atlas.get("noder") or []:
            paakrevd |= set(n.keys())
        assert p["mangler"], "the suggestion does not say what remains"
        assert set(p["mangler"]) <= paakrevd

    def test_ukjent_tekst_feiler_ikke(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "")
        assert p["status"] == "tomt"


def kjoer(*args: str) -> str:
    import subprocess
    return subprocess.check_output(
        [sys.executable, str(REPO / "scripts" / "atlas_inngang.py"),
         *args], text=True, cwd=REPO)


def test_node_svarer_for_node_motor_og_buss() -> None:
    svar = kjoer("efc.rotation_engine", "--ref", "HEAD")
    assert "NODE: efc.rotation_engine" in svar
    assert "ENGINE: rotation.py" in svar
    assert "BUS: kosmos.galakser" in svar
    assert "OUT OF REACH: the Hindsight bank efc" in svar


def test_kjent_hull_skilles_fra_ekte_hull() -> None:
    svar = kjoer("verden.energi", "--ref", "HEAD")
    assert "KNOWN GAP" in svar
    assert "no node" in svar


def test_ekte_hull_sier_at_atlaset_ikke_vet() -> None:
    svar = kjoer("ord_som_ingen_har_maalt", "--ref", "HEAD")
    assert "THE ATLAS DOES NOT KNOW" in svar


def test_utdata_er_deterministisk() -> None:
    assert kjoer("efc.rotation_engine", "--ref", "HEAD") == kjoer(
        "efc.rotation_engine", "--ref", "HEAD")


def test_ukjent_ref_feiler_hoyt() -> None:
    import subprocess
    p = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "atlas_inngang.py"),
         "efc.rotation_engine", "--ref", "ref-som-ikke-finnes"],
        text=True, capture_output=True, cwd=REPO)
    assert p.returncode != 0
    assert "failed" in p.stderr
