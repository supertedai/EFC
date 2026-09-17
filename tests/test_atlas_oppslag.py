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

    def test_tre_nivaaer_og_rekkefolgen(self, ekte_repo: Path) -> None:
        """`id` er sterkest, saa `ord`, saa `delstreng`.

        «sol» traff `batteri.lading` som ORD — fordi ordet finnes i en tekst
        inne i noden. Det er ikke det samme som at noden handler om sol.
        Nivaaene maa derfor skilles: i id-en, som eget ord, som delstreng.
        """
        svar = atlas_lesing.finn(ekte_repo, "sol", ref="HEAD")
        assert svar["antall"] > 0
        typer = [t["trefftype"] for t in svar["treff"]]
        assert "id" in typer, "lys.sol har sol i id-en"
        for svakere, sterkere in (("ord", "id"), ("delstreng", "ord")):
            if svakere in typer and sterkere in typer:
                assert typer.index(sterkere) < typer.index(svakere), (
                    f"{sterkere} skal komme foran {svakere}")
        rekkefolge = {"id": 0, "ord": 1, "delstreng": 2}
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
        p = self._kjoer("--ref", "HEAD")
        assert p.returncode == 0, p.stderr
        assert "82 noder" in p.stdout, p.stdout[:200]
