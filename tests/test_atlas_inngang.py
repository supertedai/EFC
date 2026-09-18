"""TO GAPER.

1. SOEKET normaliserer ikke bindestrek mot mellomrom. Maalt 2026-09-18:
   `--emne "energy-flow"` traff, `--emne "energy flow"` gav 0 treff.
   Ordene Morten bruker har begge former.

2. INNGANGEN. Vi kan rotere rundt alt som ALT ER i atlaset. Men naar vi
   gjoer en NY observasjon finnes det ingen vei fra den og inn i kartet.
   Koblingene er der; inngangen for nye fragmenter er det ikke.
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
        assert {x["id"] for x in a["treff"]}, "energy-flow traff ingenting"
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in b["treff"]}, \
            "bindestrek og mellomrom gir ulike treff"

    def test_understrek_er_ogsaa_samme(self, atlas: dict) -> None:
        a = atlas_lesing.finn(REPO, "energi-flyt", "HEAD")
        c = atlas_lesing.finn(REPO, "energi flyt", "HEAD")
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in c["treff"]}

    def test_store_og_smaa_bokstaver(self, atlas: dict) -> None:
        a = atlas_lesing.finn(REPO, "EFC-D", "HEAD")
        b = atlas_lesing.finn(REPO, "efc-d", "HEAD")
        assert {x["id"] for x in a["treff"]} == {x["id"] for x in b["treff"]}


class TestInngangen:
    """Plasser en NY observasjon i atlaset og rotér rundt den."""

    def test_plasser_foreslaar_hjem_for_et_fragment(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "PAH i interstellar støv")
        assert p["forslag"], "ingen forslag til hvor fragmentet horer"
        forslag = p["forslag"][0]
        assert "domene" in forslag and "noder" in forslag

    def test_plasser_sier_hva_som_MANGLER(self, atlas: dict) -> None:
        """Et fragment ingen node eier skal ikke skjules — det er et funn."""
        p = atlas_lesing.plasser(atlas, "xylofonstemning i mars")
        assert p["status"] in ("uten_hjem", "svakt")
        assert p.get("naere_noder") is not None

    def test_plasser_gir_aksene_fragmentet_maa_utfylle(self, atlas: dict) -> None:
        """Inngangen er ikke et hull — den er en liste over hva som maa fylles."""
        p = atlas_lesing.plasser(atlas, "PAH i interstellar støv")
        paakrevd = set((atlas.get("noder") or [{}])[0].keys())
        assert p["mangler"], "forslaget sier ikke hva som gjenstaar"
        assert set(p["mangler"]) <= paakrevd

    def test_ukjent_tekst_feiler_ikke(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "")
        assert p["status"] == "tomt"
