"""Tester for atlasoppslaget — inngangen til atlaset.

Maalt behov 2026-09-17: atlaset hadde en leser (`les_atlas`) men ingen
inngang. Prisen for aa konsultere det var aa laste alle 82 noder og lete
selv, saa det skjedde ikke spontant i samtale. Atlaset var en katalog man
kan lese, ikke et oppslagsverk man kan spoerre.

Disse testene vernet om TRE ting, og de er ikke de samme:

  1. Oppslaget leser fra GIT-REFEN, ikke fra arbeidsstreet. Samme feilmodus
     som `les_atlas` finnes for aa hindre — en kopi som svarer, leser som
     et levende atlas. En mutant som bytter til arbeidsstreet skal felles.

  2. Et tomt svar er et SVAR. «Atlaset vet ikke» maa kunne skilles fra
     «oppslaget feilet». En test som bare teller treff, kan ikke se det.

  3. Hvert treff navngir sin epistemiske status. Et oppslagsverk som lister
     navn uten aa si hva som er kjent og hva som er stipulert, flytter
     arbeidet tilbake til leseren.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import atlas_lesing  # noqa: E402


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return p.stdout


@pytest.fixture
def ekte_repo() -> Path:
    """Repoen testene kjoerer i — atlaset finnes paa origin/main eller HEAD."""
    return REPO


class TestOppslagetSvarer:
    def test_kjent_emne_gir_treff(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["antall"] > 0, "h2o skal finnes i atlaset"
        assert svar["hull"] is False

    def test_ukjent_emne_er_et_hull_ikke_en_feil(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "kvantegravitasjon_xyzzy", ref="HEAD")
        assert svar["antall"] == 0
        assert svar["hull"] is True, (
            "et tomt svar maa NAVNGIS som hull — 'atlaset vet ikke' er et "
            "svar, og maa kunne skilles fra 'oppslaget feilet'")

    def test_soket_er_case_insensitivt(self, ekte_repo: Path) -> None:
        a = atlas_lesing.finn(ekte_repo, "H2O", ref="HEAD")
        b = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert a["antall"] == b["antall"] > 0


class TestKildenErNavngitt:
    def test_svaret_navngir_commit(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["commit"] == _git(ekte_repo, "rev-parse", "HEAD").strip()
        assert svar["kilde"].startswith("git:")

    def test_oppslaget_leser_ikke_arbeidsstreet(self, tmp_path: Path) -> None:
        """MUTANT-FELLE: en arbeidskopi som avviker skal ikke kunne svare.

        Dette er hele grunnen til at modulen finnes. Lager en arbeidskopi med
        en node som IKKE finnes i git-treet, og krever at oppslaget ikke ser
        den naar det leser fra refen.
        """
        repo = tmp_path / "repo"
        repo.mkdir()
        _git(repo, "init", "-q")
        _git(repo, "config", "user.email", "t@t")
        _git(repo, "config", "user.name", "t")
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            json.dumps({"nodes": [{"id": "ekte.node", "synlighet": "offentlig"}]}),
            encoding="utf-8")
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", "x")

        # Arbeidsstreet faar en node som IKKE er i git-treet.
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            json.dumps({"nodes": [{"id": "ekte.node"}, {"id": "spokelse.node"}]}),
            encoding="utf-8")

        svar = atlas_lesing.finn(repo, "spokelse", ref="HEAD")
        assert svar["antall"] == 0, (
            "oppslaget leste arbeidsstreet — det er feilmodusen modulen finnes "
            "for aa hindre. En ucommittet node skal ikke kunne svare.")
        assert svar["hull"] is True

        # ...og den ekte noden skal finnes, fra git-treet.
        assert atlas_lesing.finn(repo, "ekte", ref="HEAD")["antall"] == 1


class TestEpistemiskStatus:
    def test_hvert_treff_navngir_status(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        for t in svar["treff"]:
            assert "synlighet" in t, "et treff maa si om noden publiseres"
            assert "har_falsifikator" in t, (
                "et treff maa si om noden kan felles av en observasjon — "
                "ellers kan leseren ikke skille en test fra en pastand")
            assert "har_prediksjon" in t
            assert "har_oppgjoer" in t

    def test_falsifikator_telles_riktig(self, ekte_repo: Path) -> None:
        """Nodene med `ville_falsifisere` skal merkes — de andre ikke."""
        atlas = atlas_lesing.les_atlas(ekte_repo, ref="HEAD")
        med = [n["id"] for n in atlas["noder"]
               if "ville_falsifisere" in json.dumps(n, ensure_ascii=False)]
        assert med, "forutsetning: noen noder har ville_falsifisere"
        svar = atlas_lesing.finn(ekte_repo, med[0].split(".")[0], ref="HEAD")
        merket = [t for t in svar["treff"] if t["id"] == med[0]]
        assert merket and merket[0]["har_falsifikator"] is True

    def test_hull_sier_hva_som_ble_sokt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "finnesikke", ref="HEAD")
        assert svar["emne"] == "finnesikke", (
            "et hull maa navngi hva som ble søkt etter — ellers kan ikke "
            "leseren se om hullet skyldes soket eller atlaset")


class TestFeilErIkkeStille:
    def test_ukjent_ref_reiser(self, ekte_repo: Path) -> None:
        with pytest.raises(atlas_lesing.AtlasLesingFeil):
            atlas_lesing.finn(ekte_repo, "h2o", ref="finnes/ikke")

    def test_refen_er_parameter_ikke_hardkodet(self, ekte_repo: Path) -> None:
        """Standardrefen skal vaere navngitt, ikke skjult i kallet."""
        assert atlas_lesing.STANDARD_REF == "origin/main"
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert svar["ref"] == "HEAD"


class TestTrefftypenErSynlig:
    """Et delstreng-treff er ikke det samme som et ord-treff.

    Maalt 2026-09-17: `--emne sol` ga 20 treff, hvorav `h2o.solid` kom med
    fordi «sol» er en delstreng av «solid». Et oppslagsverk som ikke skiller
    disse, tvinger leseren til aa gjette hvilke treff som er ekte — og da
    flyttet vi bare arbeidet tilbake til leseren.
    """

    def test_fire_nivaaer_og_rekkefolgen(self, ekte_repo: Path) -> None:
        """`id` > `domene` > `ord` > `delstreng`.

        «sol» traff `batteri.lading` som ORD — fordi ordet finnes i en tekst
        inne i noden. Det er ikke det samme som at noden handler om sol.
        Nivaaene maa derfor skilles: i id-en, som eget ord, som delstreng.
        """
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        assert svar["antall"] > 0
        typer = [t["trefftype"] for t in svar["treff"]]
        assert "id" in typer, "lys.sol har sol i id-en"
        for svakere, sterkere in (("domene", "id"), ("ord", "domene"),
                                  ("delstreng", "ord")):
            if svakere in typer and sterkere in typer:
                assert typer.index(sterkere) < typer.index(svakere), (
                    f"{sterkere} skal komme foran {svakere}")
        rekkefolge = {"id": 0, "domene": 1, "ord": 2, "delstreng": 3}
        assert typer == sorted(typer, key=lambda x: rekkefolge[x]), (
            f"feil rekkefolge: {typer}")

    def test_delstreng_treffet_navngir_seg_selv(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        solid = [t for t in svar["treff"] if t["id"] == "h2o.solid"]
        assert solid, "forutsetning: h2o.solid finnes"
        assert solid[0]["trefftype"] == "delstreng"

    def test_id_treffet_er_id_treff(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "regnbue", ref="HEAD")
        assert svar["treff"], "forutsetning: regnbue finnes"
        egne = [t for t in svar["treff"] if t["id"].startswith("regnbue")]
        assert egne, "forutsetning: noden regnbue finnes"
        assert all(t["trefftype"] == "id" for t in egne), (
            "naar emnet staar i node-id-en, er det et id-treff — det sterkeste")
        # ...og de skal ligge foran alt som bare nevner ordet i teksten.
        typer = [t["trefftype"] for t in svar["treff"]]
        if "ord" in typer:
            assert typer.index("id") < typer.index("ord"), (
                f"id-treff skal ligge foran ord-treff: {typer}")


class TestSeparatorer:
    """Underscore er en separator i id-er, ikke et ordtegn.

    Maalt i review 2026-09-17: `sovn` i `homo.sovn_vaaken` ble klassifisert
    som `delstreng`, fordi `\\b` regner `_` som ordtegn. Men i node-id-er
    skiller `_` ledd — `homo.sovn_vaaken`, `efc.solar_flare_engine`. Saa
    `sovn` ER et eget ledd i id-en, og skal merkes som `id`, ikke svekkes
    til en delstreng.
    """

    def test_underscore_skiller_ledd_i_id(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sovn", ref="HEAD")
        treff = [t for t in svar["treff"] if t["id"] == "homo.sovn_vaaken"]
        assert treff, "forutsetning: homo.sovn_vaaken finnes"
        assert treff[0]["trefftype"] == "id", (
            f"`sovn` er et eget ledd i `homo.sovn_vaaken` — underscore "
            f"skiller ledd, den limer dem ikke sammen. Fikk: {treff[0]['trefftype']}")

    def test_bindestrek_skiller_ledd_i_id(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "dayahead", ref="HEAD")
        for t in svar["treff"]:
            if "-" in str(t["id"]):
                assert t["trefftype"] == "id", (
                    "ogsaa bindestrek skiller ledd i en id")

    def test_delstreng_i_midten_av_et_ledd_er_fortsatt_delstreng(self, ekte_repo: Path) -> None:
        """`sol` i `solid` skal FORTSATT vaere delstreng — skillet skal ikke slakkes."""
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        solid = [t for t in svar["treff"] if t["id"] == "h2o.solid"]
        assert solid and solid[0]["trefftype"] == "delstreng", (
            "`sol` er midt inne i leddet `solid` — det er en delstreng, "
            "og skal ikke bli id-treff naar vi utvider separator-settet")


class TestKommandolinjen:
    """CLI-en er en PASTAND i PR-beskrivelsen — og den skal kunne kjores.

    Review 2026-09-17: `finn()` var dekket, men ikke subprocess-kjoringen.
    En CLI som ikke testes, er en pastand om at den virker.
    """

    def _kjoer(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(REPO / "scripts" / "atlas_lesing.py"), str(REPO), *args],
            capture_output=True, text=True, timeout=120)

    def test_oppslag_paa_kommandolinjen(self) -> None:
        p = self._kjoer("--emne", "sovn", "--ref", "HEAD")
        assert p.returncode == 0, p.stderr
        assert "homo.sovn_vaaken" in p.stdout
        assert "1 treff" in p.stdout

    def test_hull_paa_kommandolinjen_er_tydelig(self) -> None:
        p = self._kjoer("--emne", "kvantegravitasjon_xyzzy", "--ref", "HEAD")
        assert p.returncode == 0, (
            "et hull er et gyldig svar — kommandolinjen skal ikke feile paa det")
        assert "ATLASET VET IKKE" in p.stdout

    def test_uten_emne_listes_hele_atlaset(self) -> None:
        """Antallet leses fra kilden — ikke skrevet inn.

        Foerste utgave hadde `assert "82 noder" in p.stdout`. Det var sant
        da det ble skrevet, og usant samme kveld: atlaset gikk til 83 og
        deretter 84, og testen feilet paa TALLET mens den trodde den
        maalte at CLI-en lister hele atlaset. Et hardkodet tall blir
        staaende lenger enn kilden sin og lyver til slutt — det er samme
        klasse som resten av huset verner mot.

        Det som faktisk skal maales er at CLI-en og filen er ENIGE — og
        filen maa leses fra SAMME sted som CLI-en. Foerste rettelse leste
        arbeidsstreet mens CLI-en leste `--ref HEAD`; de gikk fra
        hverandre i det oyeblikket en node var lagt til men ikke
        committet. Arbeidsstreet og git-treet svarer ikke paa samme
        spoersmaal — samme klasse en gang til.
        """
        import json as _json
        import subprocess as _sp
        raa = _sp.run(["git", "show", "HEAD:schema/regime_nodes.jsonld"],
                      cwd=REPO, capture_output=True, text=True, check=True)
        noder = _json.loads(raa.stdout)["nodes"]
        p = self._kjoer("--ref", "HEAD")
        assert p.returncode == 0, p.stderr
        assert f"{len(noder)} noder" in p.stdout, (
            f"CLI-en og filen er uenige om antallet: {p.stdout[:200]}")


class TestKjenteHull:
    """«Atlaset vet ikke» og «dette er et KJENT hull» er ikke samme svar.

    Maalt 2026-09-17: `finn()` leste bare `regime_nodes.jsonld`, mens
    dekningsstatusen ligger i `schema/atlas_dekning.json` (27 ikke_dekket,
    6 delvis, 6 dekket). Et oppslagsverk som svarer «vet ikke» om noe noen
    faktisk har maalt og funnet manglende, kaster bort det dyreste det vet.
    """

    def test_kjent_hull_navngis_som_kjent(self, ekte_repo: Path) -> None:
        """Dekningsfilens form er maalt, ikke antatt: `domener` er en DICT
        fra domenenavn til {status, noder, begrunnelse, emner}."""
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        domener = dek["domener"]
        assert isinstance(domener, dict), "forutsetning: domener er en dict"
        ikke_dekket = [k for k, v in domener.items()
                       if isinstance(v, dict) and v.get("status") == "ikke_dekket"]
        assert ikke_dekket, "forutsetning: dekningsfilen har kjente hull"
        svar = atlas_lesing.finn(ekte_repo, ikke_dekket[0], ref="HEAD")
        assert svar["kjent_hull"] is not None, (
            f"`{ikke_dekket[0]}` er maalt som ikke_dekket — oppslaget skal "
            f"si det, ikke bare «vet ikke»")
        assert svar["kjent_hull"]["status"] == "ikke_dekket"

    def test_ukjent_emne_uten_dekning_er_fortsatt_bare_ukjent(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "kvantegravitasjon_xyzzy", ref="HEAD")
        assert svar["hull"] is True
        assert svar["kjent_hull"] is None, (
            "noe ingen har maalt skal ikke meldes som et kjent hull — "
            "det ville gjort «kjent» meningsloest")

    def test_svaret_sier_hvor_dekningen_kom_fra(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        assert "dekning_fil" in svar, (
            "leseren maa kunne se hvilken fil dekningsstatusen kom fra")


class TestRelevans:
    """Et oppslagsverk som svarer med alt, svarer ikke.

    Maalt 2026-09-17 ved aa BRUKE oppslaget paa ekte spoersmaal:
      «EF»         → 80 treff, ALLE delstreng av «efc»/«buffer»/«celle»
      «instrument» → 82 treff — alle 82 noder, fordi ordet finnes i alle
      «atlas»      → 46 treff, ETT er relevant (efc.selv.atlas)

    Svakeste trefftype maa derfor ikke dominere svaret. `buss_domene` er
    ogsaa et signal: en node som dekker domenet `verden.energi` ER relevant
    for «energi», selv om ordet bare staar i prosaen.
    """

    def test_buss_domene_treff_rangeres_over_prosa(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "energi", ref="HEAD")
        domene = [t for t in svar["treff"] if t.get("buss_domene") == "verden.energi"]
        assert domene, "forutsetning: verden.energi finnes"
        assert domene[0]["trefftype"] in ("id", "domene"), (
            f"en node som DEKKER domenet skal ikke rangeres som loes prosa: "
            f"{domene[0]}")

    def test_for_bredt_sok_navngis(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "instrument", ref="HEAD")
        assert svar["antall"] > 50, "forutsetning: instrument treffer bredt"
        assert svar["for_bredt"] is True, (
            "et sok som treffer nesten hele atlaset skal SI det, ikke late "
            "som det er et presist svar")
        assert svar["raad"] is not None, "naar soket er for bredt, si hva man kan gjore"

    def test_presist_sok_er_ikke_for_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "regnbue", ref="HEAD")
        assert svar["for_bredt"] is False, (
            "et presist sok skal ikke merkes som bredt — da blir varselet "
            "stoy og ignoreres")

    def test_cli_viser_relevante_forst(self, ekte_repo: Path) -> None:
        import subprocess as _sp
        p = _sp.run([sys.executable, str(REPO / "scripts" / "atlas_lesing.py"),
                     str(REPO), "--ref", "HEAD", "--emne", "energi"],
                    capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr
        linjer = [l for l in p.stdout.splitlines() if "efc." in l or "batteri" in l]
        assert linjer, p.stdout[:300]
        assert "efc." in linjer[0], (
            f"offentlige motor-noder skal ikke ligge under interne batteri-"
            f"noder naar begge er ord-treff: {linjer[:3]}")


class TestBareNavnetTeller:
    """Matching skjer paa domeneNAVN — aldri paa begrunnelsesteksten.

    Pastanden stod i commit-meldingen for 0a41054b, men var IKKE dekket av
    en test. Review runde 3 viste det: mutanten som ogsaa matcher begrunnelsen
    passerte hele suiten (40/40). En pastand om vernet som vernet ikke kan
    felle, er den samme feilen som resten av denne perioden.

    Proben er reviewens egen: `mast-caom-observasjonen` staar i
    `kosmos.galakser`s BEGRUNNELSE, men er ikke et domenenavn. Hadde
    matchingen lest prosa, ville den sluppet gjennom som «kjent hull».
    """

    def test_begrunnelsestekst_er_ikke_et_treff(self, ekte_repo: Path) -> None:
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        domener = dek["domener"]
        # Finn et ord som staar i en begrunnelse men ikke er et domenenavn.
        kandidat = None
        for dom, v in domener.items():
            tekst = (v or {}).get("begrunnelse") or ""
            for ord_ in tekst.replace(",", " ").replace(".", " ").split():
                if len(ord_) > 8 and ord_ not in domener and not any(
                        ord_ in d for d in domener):
                    kandidat = ord_
                    break
            if kandidat:
                break
        assert kandidat, "forutsetning: en begrunnelse inneholder et ord som ikke er et domenenavn"

        svar = atlas_lesing.finn(ekte_repo, kandidat, ref="HEAD")
        assert svar["kjent_hull"] is None, (
            f"`{kandidat}` staar i en BEGRUNNELSE, ikke i et domenenavn — "
            f"oppslaget leste prosa og meldte «kjent hull». Matching skal "
            f"bare skje paa navnet: {svar['kjent_hull']}")

    def test_ordet_finnes_faktisk_i_en_begrunnelse(self, ekte_repo: Path) -> None:
        """Negativ kontroll: uten denne kunne testen over passere fordi
        ordet ikke fantes noe sted — og da testet den ingenting."""
        import json as _json
        dek = _json.loads(_git(ekte_repo, "show", "HEAD:schema/atlas_dekning.json"))
        all_tekst = " ".join((v or {}).get("begrunnelse", "")
                             for v in dek["domener"].values())
        assert "mast-caom" in all_tekst, (
            "reviewens probe skal finnes i en begrunnelse — ellers er "
            "testen over tom")
        svar = atlas_lesing.finn(ekte_repo, "mast-caom", ref="HEAD")
        assert svar["kjent_hull"] is None, (
            "`mast-caom` er ikke et domenenavn. At det staar i en begrunnelse "
            "skal ikke gjore det til et kjent hull.")


class TestBreddeKriteriet:
    """«For bredt» skal hvile paa et PRESIST treff, ikke paa et tall.

    Review runde 4 maalte terskelen jeg hadde valgt (50 treff eller 60 %):
    sol=20, energi=25, kosmos=32, h2o=36 — alle langt under. instrument=82,
    over. Ingen ekte spoersmaal laa i naarheten. Tallet var gjettet.

    Det meningsfulle kriteriet er om soket har NOE presist: et `id`-treff
    eller et `domene`-treff. `sol` har `lys.sol` — det er ikke bredt, uansett
    hvor mange som ellers nevner ordet i prosa. `instrument` har null presise
    treff; alt er loes prosa.
    """

    def test_sok_uten_presist_treff_er_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "instrument", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert not presise, "forutsetning: instrument har ingen presise treff"
        assert svar["for_bredt"] is True, (
            "et sok med NULL presise treff er bredt — uansett antall")

    def test_sok_med_presist_treff_er_ikke_bredt(self, ekte_repo: Path) -> None:
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert presise, "forutsetning: sol har id-treffet lys.sol"
        assert svar["for_bredt"] is False, (
            f"et sok med et presist treff er ikke bredt, selv om "
            f"{svar['antall']} noder nevner ordet i prosa")

    def test_de_maalte_spoersmaalene_fra_reviewen(self, ekte_repo: Path) -> None:
        """Reviewens egne maalinger — de skal holde som grenseverdier."""
        forventet = {"sol": False, "energi": False, "kosmos": False,
                     "h2o": False, "instrument": True}
        for emne, skal_vaere_bredt in forventet.items():
            s = atlas_lesing.finn(ekte_repo, emne, ref="HEAD")
            assert s["for_bredt"] is skal_vaere_bredt, (
                f"«{emne}»: forventet for_bredt={skal_vaere_bredt}, "
                f"fikk {s['for_bredt']} ({s['antall']} treff)")

    def test_mange_treff_med_presist_er_ikke_bredt(self, ekte_repo: Path) -> None:
        """DET AVGJOERENDE TILFELLET — der de to kriteriene er uenige.

        `efc` gir 68 treff, hvorav 32 presise (`efc.*`-nodene). En
        ANTALLS-terskel sier «bredt» fordi 68 > 50. Det er feil: 32 presise
        treff er det stikk motsatte av bredt.

        Uten denne testen passerer begge kriteriene paa de samme dataene —
        og da maaler testene ikke skillet de paastaar aa verne.
        """
        svar = atlas_lesing.finn(ekte_repo, "efc", ref="HEAD")
        presise = [t for t in svar["treff"] if t["trefftype"] in ("id", "domene")]
        assert len(presise) > 10, f"forutsetning: efc har mange presise ({len(presise)})"
        assert svar["antall"] > 50, f"forutsetning: efc har mange treff ({svar['antall']})"
        assert svar["for_bredt"] is False, (
            f"«efc» har {len(presise)} PRESISE treff av {svar['antall']} — "
            f"det er ikke et bredt sok. En antalls-terskel ville sagt bredt.")

    def test_kriteriet_skalerer_med_atlaset(self, ekte_repo: Path) -> None:
        """Kriteriet skal ikke avhenge av hvor STORT atlaset er.

        En prosent-terskel ville flyttet seg naar atlaset vokste; «finnes
        det et presist treff» gjoer det ikke.
        """
        s = atlas_lesing.finn(ekte_repo, "h2o", ref="HEAD")
        presise = [t for t in s["treff"] if t["trefftype"] in ("id", "domene")]
        assert presise, "h2o har id-treff"
        assert s["for_bredt"] is False


class TestVisningsgrensen:
    """`_VIS_MAKS` skal faktisk begrense — mutanten 999 ble ikke felt."""

    def test_grensen_er_satt_og_lav_nok(self) -> None:
        assert 0 < atlas_lesing._VIS_MAKS <= 30, (
            f"_VIS_MAKS={atlas_lesing._VIS_MAKS} — en grense som ikke "
            f"begrenser noe er ikke en grense")

    def test_cli_kutter_og_sier_hvor_mange_som_ligger_under(self, ekte_repo: Path) -> None:
        import subprocess as _sp
        p = _sp.run([sys.executable, str(REPO / "scripts" / "atlas_lesing.py"),
                     str(REPO), "--ref", "HEAD", "--emne", "instrument"],
                    capture_output=True, text=True, timeout=120)
        assert p.returncode == 0, p.stderr
        linjer = [l for l in p.stdout.splitlines() if "(ord)" in l or "(delstreng)" in l]
        assert len(linjer) <= atlas_lesing._VIS_MAKS, (
            f"CLI viste {len(linjer)} treff, grensen er {atlas_lesing._VIS_MAKS}")
        assert "flere" in p.stdout, (
            "naar treffene kuttes, skal CLI si hvor mange som ligger under")


class TestStorrelsenPaaHullet:
    """«Kjent hull» uten størrelse kan ikke prioriteres.

    Maalt 2026-09-17: `verden.vaer` (190 770 meldinger) og
    `kosmos.asteroider` (228) ga IDENTISK svar. PR #475 gjør at
    dekningsfilen bærer `meldinger` per domene — men den er ikke merget, så
    lesingen må være VALGFRI: finnes feltet, vises det; finnes det ikke,
    virker oppslaget som før.

    Alternativet — å kreve feltet — ville låst denne PR-en til #475, og et
    oppslagsverk som ikke virker før en annen PR lander, er et oppslagsverk
    som ikke virker.
    """

    def _repo_med(self, tmp_path: Path, ekstra: dict) -> Path:
        repo = tmp_path / "r"
        (repo / "efc_inference" / "engine").mkdir(parents=True)
        (repo / "schema").mkdir()
        (repo / "schema" / "regime_nodes.jsonld").write_text(
            '{"nodes": []}', encoding="utf-8")
        dekning = {"domener": {"kosmos.asteroider": dict(
            {"status": "ikke_dekket", "noder": [], "begrunnelse": "ingen node"}.items(),
            **ekstra)}}
        (repo / "schema" / "atlas_dekning.json").write_text(
            json.dumps(dekning), encoding="utf-8")
        for a in (("init", "-q"), ("config", "user.email", "t@t"),
                  ("config", "user.name", "t"), ("add", "-A"),
                  ("commit", "-q", "-m", "x")):
            subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True)
        return repo

    def test_meldinger_er_med_nar_feltet_finnes(self, tmp_path: Path) -> None:
        repo = self._repo_med(tmp_path, {"meldinger": 228})
        svar = atlas_lesing.finn(repo, "kosmos.asteroider", ref="HEAD")
        assert svar["kjent_hull"] is not None
        assert svar["kjent_hull"]["meldinger"] == 228, (
            f"stoerrelsen mangler: {svar['kjent_hull']}")

    def test_uten_feltet_virker_oppslaget_som_foer(self, tmp_path: Path) -> None:
        repo = self._repo_med(tmp_path, {})
        svar = atlas_lesing.finn(repo, "kosmos.asteroider", ref="HEAD")
        assert svar["kjent_hull"] is not None, (
            "oppslaget skal virke ogsaa uten `meldinger` — feltet er valgfritt")
        assert svar["kjent_hull"]["meldinger"] is None

    def test_navnet_matches_fortsatt_bare_paa_domenenavn(self, tmp_path: Path) -> None:
        """Stoerrelsen skal ikke gjore at flere ting matcher."""
        repo = self._repo_med(tmp_path, {"meldinger": 228})
        svar = atlas_lesing.finn(repo, "228", ref="HEAD")
        assert svar["kjent_hull"] is None, (
            "tallet 228 er ikke et domenenavn")
