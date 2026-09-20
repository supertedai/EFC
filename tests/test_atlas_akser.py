"""ALL axes — not the six I happened to build.

Morten, 2026-09-17: «Epicentre, vector, field, domain, cross-domain,
isomorphism, what is measured, who measures, where it is measured, which
measuring instrument, via proxies, fractals of the whole picture, emergence à la
the rainbow and BAO, loops, consciousness, paradigm, consensus, academia etc.
etc... search and find them all here and make sure you can rotate around all axes and
the whole atlas so that you can navigate around efficiently».

MEASURED: the atlas carried 21 top-level fields, ALL mandatory on all 86 nodes.
The rotation covered SIX. The other fifteen — emergence.loop, fractal.pattern,
coupling, observer, epistemikk, maale_paradigme, nivaa, stipulasjoner,
buffer, ontology, analogi (the isomorphism), falsifiserbarhet, prediction,
settlement, synlighet — were in the data and were invisible to the tool.

The solution is not twenty flags. It is one generic rotation that finds the
axes itself, so an axis added tomorrow also works tomorrow.
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


class TestAkselisten:

    def test_akser_finner_alle_toppnivaa_felt(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        for felt in ("regime", "phase", "measure", "episenter", "buffer",
                     "ontology", "observer", "emergence", "fractal",
                     "coupling", "perspektiv", "stipulasjoner", "epistemikk",
                     "maale_paradigme", "nivaa", "synlighet"):
            assert felt in a, f"the axis `{felt}` is invisible to the tool"

    def test_hver_akse_har_antall_og_eksempelverdier(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        n, verdier = a["perspektiv"]
        assert n == len(atlas["noder"])
        assert set(verdier) <= {"paradigme", "konsensus", "akademia", "agnostikk"}

    def test_nestede_akser_naas_med_dotted_sti(self, atlas: dict) -> None:
        """Emergence, epistemikk and nivaa are not top-level values."""
        a = atlas_lesing.akser(atlas)
        for sti in ("emergence.loop", "epistemikk.sannhetsstatus",
                    "maale_paradigme.koordinater", "nivaa.tidsskala",
                    "measure.placement", "observer.awareness"):
            assert sti in a, f"the nested axis `{sti}` is invisible"


class TestGeneriskRotasjon:

    def test_roter_paa_en_akse_med_verdi(self, atlas: dict) -> None:
        """The value comes from the data, not from my assumption about them."""
        verdier = atlas_lesing.akser(atlas)["perspektiv"][1]
        assert verdier, "the perspektiv axis has no values"
        t = atlas_lesing.roter_akse(atlas, "perspektiv", verdier[0])
        assert t, f"found no nodes with perspektiv={verdier[0]}"
        assert all(n["perspektiv"] == verdier[0] for n in t)

    def test_roter_paa_nested_sti(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "emergence.loop", None)
        assert len(t) == len(atlas["noder"]), "all nodes have a loop"

    def test_roter_paa_isomorfismen(self, atlas: dict) -> None:
        """«isomorphisme» — it is called `analogi` in the atlas. 14 nodes."""
        t = atlas_lesing.roter_akse(atlas, "analogi", None)
        assert len(t) == 14, f"analogi: {len(t)}"

    def test_roter_paa_epistemisk_status(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "epistemikk.sannhetsstatus", "hypotese")
        assert t
        assert all(n["epistemikk"]["sannhetsstatus"] == "hypotese" for n in t)

    def test_ukjent_akse_feiler_med_forslag(self, atlas: dict) -> None:
        with pytest.raises(KeyError) as e:
            atlas_lesing.roter_akse(atlas, "finnes.ikke", None)
        assert "Nearby" in str(e.value), "feilen skal foreslaa alternativer"

    def test_ukjent_verdi_paa_kjent_akse_gir_tomt_ikke_feil(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "perspektiv", "no-such-value")
        assert t == []


class TestNavnelaget:
    """MORTEN'S names against the ATLAS'S paths — three different classes.

    Measured 2026-09-17: `isomorphisme` is `analogi`, `loop` is
    `emergence.loop`, and `paradigme` is a VALUE of `perspektiv` — not an
    axis. Without this layer all three look alike: «does not exist».
    """

    def test_alias_isomorphisme_er_analogi(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "isomorphisme")
        assert len(t) == 14, f"isomorphisme: {len(t)}"

    def test_alias_loop_er_emergence_loop(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "loop")
        assert len(t) == len(atlas["noder"])

    def test_verdi_paradigme_loeses_som_perspektiv_verdi(self, atlas: dict) -> None:
        """THIRD CLASS: `paradigme` is not an axis. It is a value."""
        t = atlas_lesing.roter_akse(atlas, "paradigme")
        assert t
        assert all(n["perspektiv"] == "paradigme" for n in t)

    def test_menneskelige_maalefelt_naas(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        for navn, sti in (("hva_maales", "measure.target"),
                          ("hvem_maaler", "measure.measurer"),
                          ("hvor_maales", "measure.placement"),
                          ("maaleinstrument", "measure.instrument")):
            assert sti in a, f"{navn} -> {sti} is missing"

    def test_ukjent_navn_feiler_fortsatt(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.roter_akse(atlas, "no.such.axis.here")


class TestOversikten:
    """«ALL of this must be global in the atlas and you must immediately know
    what is what where etc.» — not a search. The state."""

    def test_oversikt_gir_aksene_som_skiller(self, atlas: dict) -> None:
        o = dict(atlas_lesing.oversikt(atlas))
        for sti in ("perspektiv", "synlighet", "epistemikk.sannhetsstatus",
                    "nivaa.indeks", "stipulasjoner.stipulert_av_oss"):
            assert sti in o, f"the overview hides `{sti}`"

    def test_oversikten_utelater_konstanter(self, atlas: dict) -> None:
        """An axis with one value separates nothing — it must go."""
        o = dict(atlas_lesing.oversikt(atlas))
        for sti, ford in o.items():
            assert len(ford) > 1, f"`{sti}` is a constant and must not be shown"

    def test_oversikten_utelater_fritekst(self, atlas: dict) -> None:
        """«Immediately» means it must be readable on one line."""
        o = dict(atlas_lesing.oversikt(atlas))
        for sti, ford in o.items():
            for v, _ in ford[:8]:
                assert len(v) <= 34, f"`{sti}` has the free-text value {v[:40]!r}"

    def test_tellingen_stemmer_med_nodene(self, atlas: dict) -> None:
        o = dict(atlas_lesing.oversikt(atlas))
        persp = dict(o["perspektiv"])
        fra_data = {}
        for n in atlas["noder"]:
            fra_data[n["perspektiv"]] = fra_data.get(n["perspektiv"], 0) + 1
        assert persp == fra_data, "the overview and the data disagree"
