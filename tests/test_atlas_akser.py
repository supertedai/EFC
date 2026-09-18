"""ALLE akser — ikke de seks jeg tilfeldigvis bygde.

Morten, 2026-09-17: «Episenter, vektor, felt, domene, kryssdomene,
isomorphisme, hva som maales, hvem maaler, hvor maales, hvilke
maaleinstrument, via proxyer, fraktaler av totalbildet, emergence ala
regnbuen og BAO, loops, bevisstheten, paradigme, konsensus, akademia osv
osv... let og finn alle her og paase at du kan rotere rundt alle akser og
hele atlaset saa du kan navigere deg rundt effektivt».

MAALT: atlaset bar 21 toppnivaa-felt, ALLE obligatoriske paa alle 86 noder.
Rotasjonen dekket SEKS. De femten andre — emergence.loop, fractal.pattern,
coupling, observer, epistemikk, maale_paradigme, nivaa, stipulasjoner,
buffer, ontology, analogi (isomorfismen), falsifiserbarhet, prediction,
settlement, synlighet — fantes i dataene og var usynlige for verktoeyet.

Loesningen er ikke tjue flagg. Det er én generisk rotasjon som finner
aksene selv, saa en akse som legges til i morgen ogsaa virker i morgen.
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
            assert felt in a, f"aksen `{felt}` er usynlig for verktoeyet"

    def test_hver_akse_har_antall_og_eksempelverdier(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        n, verdier = a["perspektiv"]
        assert n == len(atlas["noder"])
        assert set(verdier) <= {"paradigme", "konsensus", "akademia", "agnostikk"}

    def test_nestede_akser_naas_med_dotted_sti(self, atlas: dict) -> None:
        """Emergence, epistemikk og nivaa er ikke toppnivaa-verdier."""
        a = atlas_lesing.akser(atlas)
        for sti in ("emergence.loop", "epistemikk.sannhetsstatus",
                    "maale_paradigme.koordinater", "nivaa.tidsskala",
                    "measure.placement", "observer.awareness"):
            assert sti in a, f"den nestede aksen `{sti}` er usynlig"


class TestGeneriskRotasjon:

    def test_roter_paa_en_akse_med_verdi(self, atlas: dict) -> None:
        """Verdien kommer fra dataene, ikke fra min antakelse om dem."""
        verdier = atlas_lesing.akser(atlas)["perspektiv"][1]
        assert verdier, "perspektiv-aksen har ingen verdier"
        t = atlas_lesing.roter_akse(atlas, "perspektiv", verdier[0])
        assert t, f"fant ingen noder med perspektiv={verdier[0]}"
        assert all(n["perspektiv"] == verdier[0] for n in t)

    def test_roter_paa_nested_sti(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "emergence.loop", None)
        assert len(t) == len(atlas["noder"]), "alle noder har en loekke"

    def test_roter_paa_isomorfismen(self, atlas: dict) -> None:
        """«isomorphisme» — det heter `analogi` i atlaset. 14 noder."""
        t = atlas_lesing.roter_akse(atlas, "analogi", None)
        assert len(t) == 14, f"analogi: {len(t)}"

    def test_roter_paa_epistemisk_status(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "epistemikk.sannhetsstatus", "hypotese")
        assert t
        assert all(n["epistemikk"]["sannhetsstatus"] == "hypotese" for n in t)

    def test_ukjent_akse_feiler_med_forslag(self, atlas: dict) -> None:
        with pytest.raises(KeyError) as e:
            atlas_lesing.roter_akse(atlas, "finnes.ikke", None)
        assert "Nærliggende" in str(e.value), "feilen skal foreslaa alternativer"

    def test_ukjent_verdi_paa_kjent_akse_gir_tomt_ikke_feil(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "perspektiv", "finnes-ikke")
        assert t == []


class TestNavnelaget:
    """MORTENS navn mot ATLASETS stier — tre ulike klasser.

    Maalt 2026-09-17: `isomorphisme` er `analogi`, `loop` er
    `emergence.loop`, og `paradigme` er en VERDI av `perspektiv` — ikke en
    akse. Uten dette laget ser alle tre like ut: «finnes ikke».
    """

    def test_alias_isomorphisme_er_analogi(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "isomorphisme")
        assert len(t) == 14, f"isomorphisme: {len(t)}"

    def test_alias_loop_er_emergence_loop(self, atlas: dict) -> None:
        t = atlas_lesing.roter_akse(atlas, "loop")
        assert len(t) == len(atlas["noder"])

    def test_verdi_paradigme_loeses_som_perspektiv_verdi(self, atlas: dict) -> None:
        """TREDJE KLASSE: `paradigme` er ikke en akse. Det er en verdi."""
        t = atlas_lesing.roter_akse(atlas, "paradigme")
        assert t
        assert all(n["perspektiv"] == "paradigme" for n in t)

    def test_menneskelige_maalefelt_naas(self, atlas: dict) -> None:
        a = atlas_lesing.akser(atlas)
        for navn, sti in (("hva_maales", "measure.target"),
                          ("hvem_maaler", "measure.measurer"),
                          ("hvor_maales", "measure.placement"),
                          ("maaleinstrument", "measure.instrument")):
            assert sti in a, f"{navn} -> {sti} mangler"

    def test_ukjent_navn_feiler_fortsatt(self, atlas: dict) -> None:
        with pytest.raises(KeyError):
            atlas_lesing.roter_akse(atlas, "finnes.ikke.her")


class TestOversikten:
    """«ALT dette skal vaere globalt i atlaset og du skal umiddelbart vite
    hva som er hva hvor osv.» — ikke et soek. Tilstanden."""

    def test_oversikt_gir_aksene_som_skiller(self, atlas: dict) -> None:
        o = dict(atlas_lesing.oversikt(atlas))
        for sti in ("perspektiv", "synlighet", "epistemikk.sannhetsstatus",
                    "nivaa.indeks", "stipulasjoner.stipulert_av_oss"):
            assert sti in o, f"oversikten skjuler `{sti}`"

    def test_oversikten_utelater_konstanter(self, atlas: dict) -> None:
        """En akse med én verdi skiller ingenting — den skal bort."""
        o = dict(atlas_lesing.oversikt(atlas))
        for sti, ford in o.items():
            assert len(ford) > 1, f"`{sti}` er en konstant og skal ikke vises"

    def test_oversikten_utelater_fritekst(self, atlas: dict) -> None:
        """«Umiddelbart» betyr at det maa kunne leses paa én linje."""
        o = dict(atlas_lesing.oversikt(atlas))
        for sti, ford in o.items():
            for v, _ in ford[:8]:
                assert len(v) <= 34, f"`{sti}` har fritekstverdien {v[:40]!r}"

    def test_tellingen_stemmer_med_nodene(self, atlas: dict) -> None:
        o = dict(atlas_lesing.oversikt(atlas))
        persp = dict(o["perspektiv"])
        fra_data = {}
        for n in atlas["noder"]:
            fra_data[n["perspektiv"]] = fra_data.get(n["perspektiv"], 0) + 1
        assert persp == fra_data, "oversikten og dataene er uenige"
