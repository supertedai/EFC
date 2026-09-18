"""HELHETEN — alt om en node, i én lesning.

Morten, 2026-09-18: «om vi snakker om h2o, BAO, regnbuen eller victron nå
skal du umiddelbart via atlaset få en lokalglobal sammenkobling, se
emergence, se episenter, vektorene, feltene, domene, kryssdomene, flere
hops i alle retninger, se paradigme, se konsensus, se akademia, se
emergence, se alle fraktalene den målte emergencen har, kunne rotere rundt
det vi måler, vite hva vi måler, om det er via proxy, med hvilke
målemetoder, og instrumentet».

TESTEN er de fire han navngir: h2o, BAO, regnbuen, victron.
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


#: De fire Morten navngir — testen er at ALLE svarer fullt.
PROVER = ["h2o.liquid", "obs.bao", "regnbue", "batteri.lading"]


class TestHelheten:

    @pytest.mark.parametrize("nid", PROVER)
    def test_alle_fire_gir_en_helhet(self, atlas: dict, nid: str) -> None:
        h = atlas_lesing.helhet(atlas, nid)
        assert h.get("finnes"), f"{nid} finnes ikke: {h.get('naere')}"

    @pytest.mark.parametrize("nid", PROVER)
    def test_helheten_bar_de_seks_delene(self, atlas: dict, nid: str) -> None:
        """Maalt: hver av de fire skal svare paa ALLE seks."""
        h = atlas_lesing.helhet(atlas, nid)
        for del_ in ("episenter", "felt", "maal", "perspektiv",
                     "emergence", "koblinger", "kryssdomene"):
            assert del_ in h, f"{nid} mangler `{del_}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_maalet_sier_hva_hvem_hvor_og_proxy(self, atlas: dict, nid: str) -> None:
        m = atlas_lesing.helhet(atlas, nid)["maal"]
        for felt in ("hva", "hvem", "hvor", "instrument", "proxy", "kompresjon"):
            assert felt in m, f"{nid}: maalet mangler `{felt}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_perspektivet_skiller_de_tre(self, atlas: dict, nid: str) -> None:
        """paradigme / konsensus / akademia — hva mener hvem."""
        p = atlas_lesing.helhet(atlas, nid)["perspektiv"]
        for felt in ("perspektiv", "sannhetsstatus", "konsensusstatus",
                     "evidensstatus", "sosial_mekanisme"):
            assert felt in p, f"{nid}: perspektivet mangler `{felt}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_hoppene_gaar_begge_veier(self, atlas: dict, nid: str) -> None:
        """«flere hops i alle retninger» — ut OG inn."""
        h = atlas_lesing.helhet(atlas, nid)["koblinger"]
        assert "ut" in h and "inn" in h, h.keys()

    def test_kryssdomene_finner_det_node_ikke_er(self, atlas: dict) -> None:
        """Kryssdomene = hvilke ANDRE domener noden naar via hopp."""
        k = atlas_lesing.helhet(atlas, "regnbue")["kryssdomene"]
        assert isinstance(k, list)
        for d in k:
            assert d != "optikk", "eget domene skal ikke telles som kryss"

    def test_fraktalene_hentes_fra_emergencen(self, atlas: dict) -> None:
        """«alle fraktalene den maalte emergencen har»."""
        f = atlas_lesing.helhet(atlas, "regnbue")["fraktaler"]
        assert isinstance(f, list) and f

    def test_ukjent_node_gir_naere_ikke_feil(self, atlas: dict) -> None:
        h = atlas_lesing.helhet(atlas, "finnes.ikke.her")
        assert h["finnes"] is False
        assert "naere" in h


class TestPlassererBedre:
    """Fiksen Morten ba om: fallback-en skal lete i maal og regime, ikke
    bare i domenenavn."""

    def test_vulkansk_aske_finner_klima_eller_vulkan(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "vulkansk aske i stratosfaeren")
        navn = [f["domene"] for f in p["forslag"]] + p.get("naere_noder", [])
        assert any("vulkan" in n or "klima" in n or "jord" in n for n in navn), \
            f"aske peker fortsatt bare paa alfabetet: {navn[:4]}"

    def test_forslaget_nevner_hvorfor(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "vulkansk aske i stratosfaeren")
        for f in p["forslag"]:
            assert f.get("kobling"), "forslaget sier ikke hvorfor"

    def test_ordlikhet_kalles_ikke_viten(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "kvantedatamaskin")
        assert p["domene_visshet"] == "ingen_anelse"
        assert "ordlikhet" in p["domene_grunnlag"] or "ingen" in p["domene_grunnlag"]
