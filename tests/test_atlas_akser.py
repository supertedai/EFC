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
        assert n == 86
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
        assert len(t) == 86, "alle noder har en loekke"

    def test_roter_paa_isomorfismen(self, atlas: dict) -> None:
        """«isomorphisme» — det heter `analogi` i atlaset. 13 noder."""
        t = atlas_lesing.roter_akse(atlas, "analogi", None)
        assert len(t) == 13, f"analogi: {len(t)}"

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
