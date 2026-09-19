"""THE WHOLE — everything about one node, in one reading.

Morten, 2026-09-18 (translated from Norwegian): «if we speak of h2o, BAO, the
rainbow or victron, you shall immediately, via the atlas, get a local-global
interconnection, see emergence, see epicentre, the vectors, the fields, domain,
cross-domain, several hops in all directions, see paradigm, see consensus, see
academia, see emergence, see all the fractals the measured emergence has, be
able to rotate around what we measure, know what we measure, whether it is via
proxy, with which measurement methods, and the instrument».

THE TEST is the four he names: h2o, BAO, the rainbow, victron.
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


#: The four Morten names — the test is that ALL of them answer fully.
PROVER = ["h2o.liquid", "obs.bao", "regnbue", "batteri.lading"]


class TestHelheten:

    @pytest.mark.parametrize("nid", PROVER)
    def test_alle_fire_gir_en_helhet(self, atlas: dict, nid: str) -> None:
        h = atlas_lesing.helhet(atlas, nid)
        assert h.get("finnes"), f"{nid} does not exist: {h.get('naere')}"

    @pytest.mark.parametrize("nid", PROVER)
    def test_helheten_bar_de_seks_delene(self, atlas: dict, nid: str) -> None:
        """Measured: each of the four shall answer ALL six."""
        h = atlas_lesing.helhet(atlas, nid)
        for del_ in ("episenter", "felt", "maal", "perspektiv",
                     "emergence", "koblinger", "kryssdomene"):
            assert del_ in h, f"{nid} is missing `{del_}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_maalet_sier_hva_hvem_hvor_og_proxy(self, atlas: dict, nid: str) -> None:
        m = atlas_lesing.helhet(atlas, nid)["maal"]
        for felt in ("hva", "hvem", "hvor", "instrument", "proxy", "kompresjon"):
            assert felt in m, f"{nid}: the measurement is missing `{felt}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_perspektivet_skiller_de_tre(self, atlas: dict, nid: str) -> None:
        """paradigm / consensus / academia — who thinks what."""
        p = atlas_lesing.helhet(atlas, nid)["perspektiv"]
        for felt in ("perspektiv", "sannhetsstatus", "konsensusstatus",
                     "evidensstatus", "sosial_mekanisme"):
            assert felt in p, f"{nid}: the perspective is missing `{felt}`"

    @pytest.mark.parametrize("nid", PROVER)
    def test_hoppene_gaar_begge_veier(self, atlas: dict, nid: str) -> None:
        """«more hops in every direction» — OUT AND in."""
        h = atlas_lesing.helhet(atlas, nid)["koblinger"]
        assert "ut" in h and "inn" in h, h.keys()

    def test_kryssdomene_finner_det_node_ikke_er(self, atlas: dict) -> None:
        """Cross-domain = which OTHER domains the node reaches via hops."""
        k = atlas_lesing.helhet(atlas, "regnbue")["kryssdomene"]
        assert isinstance(k, list)
        for d in k:
            assert d != "optikk", "its own domain shall not count as cross"

    def test_fraktalene_hentes_fra_emergencen(self, atlas: dict) -> None:
        """«all the fractals the measured emergence has»."""
        f = atlas_lesing.helhet(atlas, "regnbue")["fraktaler"]
        assert isinstance(f, list) and f

    def test_ukjent_node_gir_naere_ikke_feil(self, atlas: dict) -> None:
        h = atlas_lesing.helhet(atlas, "no.such.axis.here")
        assert h["finnes"] is False
        assert "naere" in h


class TestPlassererBedre:
    """The fix Morten asked for: the fallback shall search in `maal` and
    regime, not only in the domain name."""

    def test_vulkansk_aske_finner_klima_eller_vulkan(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "vulkansk aske i stratosfaeren")
        navn = [f["domene"] for f in p["forslag"]] + p.get("naere_noder", [])
        assert any("vulkan" in n or "klima" in n or "jord" in n for n in navn), \
            f"the ash still points only at the alphabet: {navn[:4]}"

    def test_forslaget_nevner_hvorfor(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "vulkansk aske i stratosfaeren")
        for f in p["forslag"]:
            assert f.get("kobling"), "the proposal does not say why"

    def test_ordlikhet_kalles_ikke_viten(self, atlas: dict) -> None:
        p = atlas_lesing.plasser(atlas, "kvantedatamaskin")
        assert p["domene_visshet"] == "ingen_anelse"
        assert "ordlikhet" in p["domene_grunnlag"] or "ingen" in p["domene_grunnlag"]
