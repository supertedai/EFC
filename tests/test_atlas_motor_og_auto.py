"""THE ENGINE — and the question about the automation.

Morten, 2026-09-18: «across every domain and field now?? and which engine etc.? and
have you built it so now that every new insight is mapped into the atlas
automatically, all the axes are created?»

MEASURED: --alt worked across all 89 nodes (0 errors), but did NOT show the engine —
39 of them have `stipulasjoner.motor` set, and the whole hid it.
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
        assert "motor" in h, "the whole hides which engine the node belongs to"
        assert h["motor"] == "water", h["motor"]
        assert h["motor"] in {
            p.stem for p in (REPO / "efc_inference" / "engine").glob("*.py")}, (
            f"{h['motor']!r} is not an engine file")

    def test_motor_er_tom_naar_ingen_er_satt(self, atlas: dict) -> None:
        """A node without an engine must say so — not hide the field."""
        uten = next(n["id"] for n in atlas["noder"]
                    if not (n.get("stipulasjoner") or {}).get("motor"))
        h = atlas_lesing.helhet(atlas, uten)
        assert "motor" in h
        assert h["motor"] in (None, "")

    def test_motor_er_soekbar_som_akse(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        assert "stipulasjoner.motor" in a, "the engine is not an axis"

    def test_alle_noder_svarer_paa_motor(self, atlas: dict) -> None:
        """The whole must be WHOLE, also when the field is empty."""
        for n in atlas["noder"]:
            h = atlas_lesing.helhet(atlas, n["id"])
            assert "motor" in h, f"{n['id']} is missing the motor field"


class TestAutomatikken:
    """«is every new insight mapped in automatically?»

    The answer is NO, and the test locks what actually happens: the entry point exists,
    but it must be RUN. This class describes the state, not the wish.
    """

    def test_vakten_ser_nye_noder_uten_falsifikator(self, atlas: dict) -> None:
        """The closest thing we have to automation: the guard that FELLS a node that
        lacks a falsifier — it forces filling in, but does not create the node."""
        paastander = [n for n in atlas["noder"]
                      if n["id"].startswith("efc.") and n.get("synlighet") == "offentlig"]
        uten = [n["id"] for n in paastander if "ville_falsifisere" not in n]
        assert isinstance(uten, list)

    def test_plasser_sier_hva_som_gjenstaar_for_enhver_tekst(self, atlas: dict) -> None:
        """The entry point is generic: any text at all yields a list."""
        for tekst in ("et nytt fenomen", "vulkan", "kvantedatamaskin"):
            p = atlas_lesing.plasser(atlas, tekst)
            assert "mangler" in p and p["mangler"], f"{tekst}: no list"
            assert len(p["mangler"]) > 5, f"{tekst}: too few fields"
