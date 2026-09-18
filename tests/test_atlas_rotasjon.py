"""Kan atlaset ROTERES — ikke bare slaaS opp?

Morten, 2026-09-17: «du skal umiddelbart se episenter, felt, domene,
paradigme, konsensus, akademia, vektor, maal, maaler, maaleinstrument,
emergence, proxy, osv i alle ledd for alt som ligger der saa du kan
navigere deg enkelt rundt».

Maalt: `atlas_lesing.py` hadde fire flagg — `--emne`, `--ref`, `--hent`,
`--alle`. Den kunne slaa opp et emne og liste alt. Den kunne ikke filtrere
paa `perspektiv`, ikke vise proxy-kjeder, ikke skille en maalt node fra en
avledet. Rotasjonen fantes ikke.

Denne filen laaser den.
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


class TestRotasjon:

    def test_filtrer_paa_perspektiv(self, atlas: dict) -> None:
        p = atlas_lesing.roter(atlas, perspektiv="paradigme")
        assert p, "ingen noder med perspektiv=paradigme"
        assert all(n.get("perspektiv") == "paradigme" for n in p)

    def test_filtrer_paa_fase(self, atlas: dict) -> None:
        f = atlas_lesing.roter(atlas, fase="instrument")
        assert f
        assert all(n.get("phase") == "instrument" for n in f)

    def test_filtrer_paa_domene(self, atlas: dict) -> None:
        d = atlas_lesing.roter(atlas, domene="kosmos.kosmologi")
        assert d
        assert all(n.get("buss_domene") == "kosmos.kosmologi" for n in d)

    def test_maaleform_skiller_maalt_fra_avledet(self, atlas: dict) -> None:
        """Det du spurte om: hvilke MAALER, og med hva."""
        former = atlas_lesing.maaleformer(atlas)
        assert set(former) >= {"instrument", "avledet", "ingen"}, set(former)
        assert former["instrument"], "ingen instrument-noder funnet"

    def test_proxy_kjeder_kan_listes(self, atlas: dict) -> None:
        """Hva gaar via hva — i alle ledd."""
        kjeder = atlas_lesing.proxy_kjeder(atlas)
        assert kjeder, "ingen proxy-kjeder funnet"
        navn, ledd = next(iter(kjeder.items()))
        assert isinstance(ledd, list) and len(ledd) > 0

    def test_roter_rundt_en_node_gir_alle_felt(self, atlas: dict) -> None:
        """Kjernen: én node, ALLE felt — ikke bare de tre jeg husker."""
        r = atlas_lesing.roter(atlas, node="efc.growth_engine")
        assert r, "fant ikke noden"
        n = r[0]
        for felt in ("episenter", "regime", "measure", "emergence", "coupling",
                     "observer", "buffer", "fractal", "ontology", "epistemikk",
                     "maale_paradigme", "stipulasjoner", "nivaa"):
            assert felt in n, f"roter() skjuler {felt}"

    def test_ukjent_node_feiler_hoeyt(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.roter(atlas, node="finnes.ikke")
