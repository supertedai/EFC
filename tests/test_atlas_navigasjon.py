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
BASELINE_MOTORER_TOTALT = 20
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


class TestMotorKoblesTilRiktigNode:
    """Hver motor skal kobles til den noden som BAERER navnet dens.

    Review runde 6: mutanten `if nid and m in nid` -> `if nid` koblet ALLE
    motorer til den foerste noden, og alle 9 tester passerte. Koblingen er
    ikke pynt: den mater `motorer_uten_buss`, saa en feil kobling gir en feil
    hull-liste — i stillhet, og rapporten ville sett like overbevisende ut.
    """

    def test_hver_motor_peker_paa_en_node_som_inneholder_navnet(self, nav: dict) -> None:
        kobling = nav["kobling"]["motor_til_node"]
        assert kobling, "forutsetning: minst én motor er koblet"
        feil = {m: n for m, n in kobling.items() if m not in str(n)}
        assert not feil, (
            f"motorer koblet til en node som ikke inneholder motornavnet: "
            f"{feil} — koblingen har falt til «foerste node»")

    def test_koblingene_er_unike(self, nav: dict) -> None:
        """To motorer skal ikke dele node med mindre navnet faktisk deles."""
        noder = list(nav["kobling"]["motor_til_node"].values())
        if len(noder) != len(set(noder)):
            from collections import Counter
            delte = [n for n, c in Counter(noder).items() if c > 1]
            for n in delte:
                motorer = [m for m, x in nav["kobling"]["motor_til_node"].items() if x == n]
                assert all(m in str(n) for m in motorer), (
                    f"flere motorer peker paa {n} uten at navnene deles: {motorer}")

    def test_en_kjent_motor_peker_paa_riktig_node(self, nav: dict) -> None:
        """Konkret anker: `water` skal peke paa `efc.water_phase_engine`."""
        kobling = nav["kobling"]["motor_til_node"]
        if "water" in kobling:
            assert "water" in str(kobling["water"]), (
                f"`water` peker paa {kobling['water']} — skal peke paa noden "
                f"som baerer navnet")


class TestUdekkedeGrener:
    """Grener review runde 7 navnga som utestet.

    Disse er ikke stramming — de er grener som aldri har vaert kjort. En
    gren som aldri er kjort, er en gren ingen vet om virker.
    """

    def test_ugyldig_ref_reiser(self, tmp_path: Path) -> None:
        """`_git` feiler -> NavigasjonFeil. Aldri stille tomt svar."""
        repo = tmp_path / "r"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True,
                       capture_output=True)
        with pytest.raises(atlas_navigasjon.NavigasjonFeil):
            atlas_navigasjon.les_noder(repo, "finnes/ikke")

    def test_malformed_json_reiser(self, tmp_path: Path) -> None:
        """Ugyldig JSON i nodene skal REISE, ikke gi tom liste."""
        repo = tmp_path / "r"
        repo.mkdir()
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text("{ikke gyldig", encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        with pytest.raises(Exception):
            atlas_navigasjon.les_noder(repo, "HEAD")

    def test_tomt_snapshot_gir_null_emner(self, tmp_path: Path) -> None:
        """Snapshot uten domener skal gi 0 emner, ikke krasje."""
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text('{"nodes": []}', encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text('{"domener": {}}', encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        d = atlas_navigasjon.naviger(repo, ref="HEAD")
        assert d["lag"]["emner"] == 0
        assert d["dekning"]["emner"] == (0, 0)

    def test_node_uten_id_ignoreres(self, tmp_path: Path) -> None:
        """En node uten `id` skal ikke kunne bli en noekkel i koblingen."""
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": [{"buss_domene": "verden.energi"}, {"id": "ekte.node"}]}',
            encoding="utf-8")
        (repo / "schema" / "nats_domener.snapshot.json").write_text(
            '{"domener": {"verden.energi": {"emner": ["tilstand.x"]}}}', encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        d = atlas_navigasjon.naviger(repo, ref="HEAD")
        assert None not in d["kobling"]["domene_til_noder"].get("verden.energi", []), (
            "en node uten id havnet i koblingen — den kan ikke navngis")


class TestEpistemiskTilstand:
    """Hva sloeyfa INNEHOLDER — ikke bare hva den er koblet til.

    Maalt 2026-09-17 ved aa BRUKE oppslaget: 0 av 73 offentlige noder kunne
    felles av en observasjon, og 0 av 82 bar et utfall. Begge var
    engangsobservasjoner fra en samtale. Uten en maaling forsvinner de naar
    noen spoer igjen — og et atlas som ikke kan si hvor tynt det er, sier
    implisitt at det er tykt.

    Navigatoren maaler naa ogsaa dette, slik at tallene er reproduserbare og
    et fall fanges.
    """

    def test_falsifikatorer_er_talt(self, nav: dict) -> None:
        e = nav["epistemisk"]
        kf, kt = e["kan_felles"]
        mo, mt = e["maaler_eller_observert"]
        assert 0 <= kf <= kt and 0 <= mo <= mt
        # Til sammen skal de dekke HELE det offentlige atlaset — ellers
        # finnes det noder ingen av kategoriene eier, og de forsvinner
        # fra alle tall uten at noen ser det.
        assert kt + mt == e["offentlige"], (
            f"kategoriene dekker ikke alle offentlige: {kt} + {mt} "
            f"mot {e['offentlige']}")

    def test_prediksjoner_og_oppgjoer_er_talt(self, nav: dict) -> None:
        e = nav["epistemisk"]
        for nokkel in ("prediksjon", "oppgjoer"):
            assert nokkel in e, f"mangler {nokkel}-telling: {e}"
            naadd, totalt = e[nokkel]
            assert 0 <= naadd <= totalt

    def test_offentlige_og_interne_er_skilt(self, nav: dict) -> None:
        """Et hull blant de OFFENTLIGE er alvorligere enn blant de interne.

        De offentlige er det publiserte atlaset; de interne er vaare egne.
        """
        e = nav["epistemisk"]
        assert "kan_felles" in e and "maaler_eller_observert" in e, (
            f"skillet mellom vaare paastander og resten mangler: {e}")
        off, tot = e["kan_felles"]
        assert tot > 0, "forutsetning: det finnes EFC-paastander"
        assert off <= tot

    def test_tallet_er_ikke_skjult(self, nav: dict) -> None:
        """Naar null offentlige noder kan felles, skal det STAA — ikke skjules.

        Et atlas der dette tallet er 0 og ikke nevnes, ser fyldigere ut enn
        det er. Det var hele funnet.
        """
        e = nav["epistemisk"]
        off, tot = e["kan_felles"]
        assert isinstance(off, int) and isinstance(tot, int), (
            "tallet skal kunne leses, ogsaa naar det er 0")
        # og den andre halvdelen skal staa like tydelig
        mo, mt = e["maaler_eller_observert"]
        assert mo == mt, (
            f"{mt - mo} ikke-EFC-noder mangler begrunnelse for aa maale")


class TestRefErFaktiskValgt:
    """`--ref` ble stille ignorert i foerste utgave.

    CLI-en leste bare `sys.argv[1]` og brukte standardrefen ellers. Da
    maalte `--ref origin/wt/vaer-node` i virkeligheten `origin/main` — og
    svarte med de gamle tallene uten aa si fra. Instrumentet svarte paa et
    nabospoersmaal, som er feilklassen resten av huset verner mot.
    """

    def test_ref_maa_kunne_velges(self):
        import subprocess
        r = subprocess.run(
            ["/opt/venvs/t_123ed6d9/bin/python",
             str(REPO / "scripts" / "atlas_navigasjon.py"), str(REPO),
             "--help"], capture_output=True, text=True)
        assert "--ref" in r.stdout, "CLI-en tilbyr ikke --ref"

    def test_ugyldig_ref_feiler_hoeyt(self):
        """En ref som ikke finnes skal si det — ikke falle tilbake."""
        import subprocess
        r = subprocess.run(
            ["/opt/venvs/t_123ed6d9/bin/python",
             str(REPO / "scripts" / "atlas_navigasjon.py"), str(REPO),
             "--ref", "finnes/ikke"], capture_output=True, text=True)
        assert r.returncode != 0, "ukjent ref gav exit 0"


class TestFalsifiserbarhetsSkillet:
    """«Kan felles» maa ikke telle instrumenter som mangler.

    `_epistemisk` talte ALT likt: 0 av 74. Men 47 av de 74 er ikke
    EFC-paastander — de er etablert fysikk, observasjoner og instrumenter.
    Et instrument kan ikke felles av en observasjon; det ER observasjonen.
    Aa telle det som et hull gjor tallet verre enn virkeligheten, og et
    tall som lyver nedover er like ubrukelig som ett som lyver oppover.
    """

    def test_kan_felles_teller_bare_efc_paastander(self):
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        e = d["epistemisk"]
        assert "kan_felles" in e, "mangler skillet"
        n, t_ = e["kan_felles"]
        assert t_ == 27, f"nevneren skal vaere de 27 EFC-nodene, fikk {t_}"
        assert n == 19, f"kan felles: {n} av {t_} — forventet 19 (8 avventer, 47 maaler)"

    def test_instrumentene_telles_for_seg(self):
        d = atlas_navigasjon.naviger(REPO, "HEAD")
        e = d["epistemisk"]
        assert "maaler_eller_observert" in e, "de 47 er ikke navngitt"
        n, t_ = e["maaler_eller_observert"]
        assert n == t_ == 47, f"forventet 47/47, fikk {n}/{t_}"
