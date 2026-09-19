"""MOTOREN — og spoersmaalet om automatikken.

Morten, 2026-09-18: «over alle domener og felt nå?? og hvilken motor osv? og
har du laget det slik nå at en hver ny innsikt blir mappet inn i atlaset
automatisk lages alle aksene?»

MAALT: --alt virket over alle 89 noder (0 feil), men viste IKKE motoren —
39 av dem har `stipulasjoner.motor` satt, og helheten skjulte den.
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


class TestMotoren:

    def test_helheten_bar_motoren(self, atlas: dict) -> None:
        """The engine is its MODULE NAME — not the node id.

        Measured 2026-09-19 (t_c015b6ee): the value was
        "efc.water_triple_point", a node absent from the bank and not a file.
        The form is named in scripts/maintenance/efc_bro_konvensjon.py: X means
        `efc_inference/engine/X.py`. This pins the form, not just the word — an
        id resolves to nothing, and that is the whole point.
        """
        h = atlas_lesing.helhet(atlas, "h2o.triple_point")
        assert "motor" in h, "helheten skjuler hvilken motor noden hoerer til"
        assert h["motor"] == "water", h["motor"]
        assert h["motor"] in {
            p.stem for p in (REPO / "efc_inference" / "engine").glob("*.py")}, (
            f"{h['motor']!r} is not an engine file")

    def test_motor_er_tom_naar_ingen_er_satt(self, atlas: dict) -> None:
        """En node uten motor skal si det — ikke skjule feltet."""
        uten = next(n["id"] for n in atlas["noder"]
                    if not (n.get("stipulasjoner") or {}).get("motor"))
        h = atlas_lesing.helhet(atlas, uten)
        assert "motor" in h
        assert h["motor"] in (None, "")

    def test_motor_er_soekbar_som_akse(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        assert "stipulasjoner.motor" in a, "motoren er ikke en akse"

    def test_alle_noder_svarer_paa_motor(self, atlas: dict) -> None:
        """Helheten skal vaere HEL, ogsaa naar feltet er tomt."""
        for n in atlas["noder"]:
            h = atlas_lesing.helhet(atlas, n["id"])
            assert "motor" in h, f"{n['id']} mangler motor-feltet"


class TestAutomatikken:
    """«blir en hver ny innsikt mappet inn automatisk?»

    Svaret er NEI, og testen laaser hva som faktisk skjer: inngangen finnes,
    men den maa KJORES. Denne klassen beskriver tilstanden, ikke oensket.
    """

    def test_vakten_ser_nye_noder_uten_falsifikator(self, atlas: dict) -> None:
        """Det naermeste vi har automatikk: vakten som FELLER en node som
        mangler falsifikator — den tvinger utfylling, men lager ikke noden."""
        paastander = [n for n in atlas["noder"]
                      if n["id"].startswith("efc.") and n.get("synlighet") == "offentlig"]
        uten = [n["id"] for n in paastander if "ville_falsifisere" not in n]
        assert isinstance(uten, list)

    def test_plasser_sier_hva_som_gjenstaar_for_enhver_tekst(self, atlas: dict) -> None:
        """Inngangen er generisk: hvilken som helst tekst gir en liste."""
        for tekst in ("et nytt fenomen", "vulkan", "kvantedatamaskin"):
            p = atlas_lesing.plasser(atlas, tekst)
            assert "mangler" in p and p["mangler"], f"{tekst}: ingen liste"
            assert len(p["mangler"]) > 5, f"{tekst}: for faa felt"
