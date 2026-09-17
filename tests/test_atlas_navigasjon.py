"""Validator for atlasnavigasjon — kan atlaset brukes i ALLE tre lag?

Maalt 2026-09-17, foerste gang noen maalte det:

    noder   : 82
    motorer : 19   — 19/19 naar fram fra en node
    NATS    : 118 emner i 39 domener — 34/118 naar fram

Atlaset kunne navigeres i ett lag og lest i to. Det er ikke det samme som
at det kan BRUKES: «hvor kommer dette tallet fra?» krever at man kan gaa
fra et emne paa bussen til noden og motoren som lager det.

Disse testene gjor tre ting, og den tredje er den viktigste:

  1. Binder navigasjonen til git-refen — en ucommittet motorfil skal ikke
     kunne svare, samme regel som `atlas_lesing` finnes for.
  2. Krever at alle 19 motorer har en node. Det er 100 % i dag, og det
     skal ikke falle.
  3. LAAASER dekningen som en BASELINE. Et hull som vokser er en
     regresjon; et hull som krymper skal oppdatere tallet MED VILJE, ikke
     ved at testen slutter aa se det.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import atlas_navigasjon  # noqa: E402

# Maalt mot origin/main 606b3127, 2026-09-17. Disse er ikke maal — de er
# et GULV. Synker de, er noe blitt usynlig for navigasjonen.
BASELINE_MOTORER_TOTALT = 19
BASELINE_MOTORER_NAADD = 17
BASELINE_EMNER_NAADD = 34
BASELINE_DOMENER_NAADD = 12
BASELINE_EMNER_TOTALT = 118


@pytest.fixture(scope="module")
def nav() -> dict:
    return atlas_navigasjon.naviger(REPO, ref="HEAD")


class TestAlleLagErSynlige:
    def test_tre_lag_er_talt(self, nav: dict) -> None:
        assert nav["lag"]["noder"] > 0, "atlaset skal ha noder"
        assert nav["lag"]["motorer"] > 0, "motorene skal vaere synlige"
        assert nav["lag"]["emner"] > 0, "bussen skal ha emner"
        assert nav["lag"]["buss_domener"] > 0

    def test_hver_motor_har_en_node(self, nav: dict) -> None:
        """En motor uten node er en maskin uten plass i kartet.

        Det er feilmodusen `verden.vaer` viser fra den andre siden: en
        stroem uten node. Maalt 2026-09-17: alle 19 har en.
        """
        mangler = [m for m in nav["kobling"]["motor_til_node"]
                   if not nav["kobling"]["motor_til_node"][m]]
        assert not mangler, f"motorer uten node: {mangler}"
        assert len(nav["kobling"]["motor_til_node"]) == nav["lag"]["motorer"], (
            "hver motor skal ha en oppfoering i motor_til_node")

    def test_motordekningen_er_minst_maalet(self, nav: dict) -> None:
        """17 av 19 motorer naar bussen — maalt, ikke antatt.

        Da jeg foerste gang skrev denne testen, antok jeg 19/19 og den
        passerte. Den var feil: `grid_mikro` og `samfunn` har en node uten
        `buss_domene`, og dermed ingen vei fra stroemmen tilbake til koden
        som regnet den. En test som passerer paa et ANTATT tall, maaler
        antakelsen sin — ikke virkeligheten.
        """
        assert nav["dekning"]["motorer"][1] == BASELINE_MOTORER_TOTALT, (
            f"motortallet endret: {nav['dekning']['motorer']}")
        assert nav["dekning"]["motorer"][0] >= BASELINE_MOTORER_NAADD, (
            f"motordekningen falt fra {BASELINE_MOTORER_NAADD} til "
            f"{nav['dekning']['motorer'][0]}")


class TestHulleneErNavngitt:
    def test_hull_er_lister_ikke_tall(self, nav: dict) -> None:
        """Et hull skal kunne NAVNGIS. «27 domener mangler» er ikke
        handlingsrettet; «kosmos.asteroider mangler» er."""
        for navn, hull in nav["hull"].items():
            assert isinstance(hull, list), f"{navn} skal vaere en liste"
            if hull:
                assert all(isinstance(h, str) and h for h in hull), (
                    f"{navn} skal navngi hvert hull")

    def test_dekningen_og_hullene_stemmer(self, nav: dict) -> None:
        """Dekning og hull maa telle samme virkelighet.

        Uten denne kunne de to tallene gli fra hverandre — og da ville
        testen over BASELINE passa paa et tall som ikke lenger betyr noe.
        """
        for navn, nokkel in (("emner", "emner_uten_node"),
                             ("domener", "domener_uten_node"),
                             ("motorer", "motorer_uten_buss")):
            naadd, totalt = nav["dekning"][navn]
            assert naadd + len(nav["hull"][nokkel]) == totalt, (
                f"{navn}: {naadd} naadd + {len(nav['hull'][nokkel])} hull "
                f"!= {totalt} totalt")

    def test_emner_uten_node_er_avledet_av_domener_uten_node(self, nav: dict) -> None:
        """Sanity: et emne kan ikke mangle node hvis domenet har en."""
        domener_hull = set(nav["hull"]["domener_uten_node"])
        for e in nav["hull"]["emner_uten_node"]:
            domene = ".".join(e.split(".")[:2])
            assert domene in domener_hull, (
                f"{e} meldes som hull, men domenet {domene} har en node — "
                f"da er de to maalingene uenige")


class TestBaseline:
    def test_antallet_emner_er_uendret(self, nav: dict) -> None:
        assert nav["dekning"]["emner"][1] == BASELINE_EMNER_TOTALT, (
            f"bussen hadde {BASELINE_EMNER_TOTALT} emner; naa "
            f"{nav['dekning']['emner'][1]}. Endret bussen seg, skal "
            f"baselinen oppdateres MED VILJE — ikke ved at testen slutter "
            f"aa se.")

    def test_dekningen_synker_ikke(self, nav: dict) -> None:
        """Den viktigste testen: et hull som VOKSER er en regresjon.

        Et hull som krymper er en forbedring og skal oppdatere tallet — men
        bare ved en bevisst endring, slik at ingen node kan forsvinne fra
        navigasjonen uten at noen ser det.
        """
        naadd_emner = nav["dekning"]["emner"][0]
        naadd_domener = nav["dekning"]["domener"][0]
        assert naadd_emner >= BASELINE_EMNER_NAADD, (
            f"emnedekningen falt fra {BASELINE_EMNER_NAADD} til {naadd_emner} — "
            f"noe er blitt usynlig for navigasjonen")
        assert naadd_domener >= BASELINE_DOMENER_NAADD, (
            f"domenedekningen falt fra {BASELINE_DOMENER_NAADD} til {naadd_domener}")


class TestKildenErGitRefen:
    def test_ucommittert_motorfil_kan_ikke_svare(self, tmp_path: Path) -> None:
        """Samme mutant-felle som `atlas_lesing` — i motorlaget.

        En motorfil som ligger ucommittet paa disken finnes ikke for den som
        leser fra refen, og skal ikke kunne dukke opp i navigasjonen.
        """
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": []}', encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text(
            '{"domener": {}}', encoding="utf-8")
        (repo / "efc_inference" / "engine" / "ekte.py").write_text(
            "x = 1\n", encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True,
                           capture_output=True)
        # ...og en SPOekELSE som bare finnes paa disken
        (repo / "efc_inference" / "engine" / "spokelse.py").write_text(
            "y = 2\n", encoding="utf-8")

        motorer = atlas_navigasjon.les_motorer(repo, "HEAD")
        assert "ekte" in motorer
        assert "spokelse" not in motorer, (
            "navigasjonen leste arbeidsstreet — en ucommittet motorfil "
            "skal ikke kunne svare")
