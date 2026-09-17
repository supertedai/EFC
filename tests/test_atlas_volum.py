"""atlas_volum — volumet leses fra maalingen, og hullet sorteres etter det.

Kortet som gjorde denne testen nødvendig (t_29a426ac) ble funnet ved aa
BRUKE atlasoppslaget, ikke ved aa teste det: `verden.vaer` (190 229
meldinger) og `verden.utdanning` (2 598) svarte likt, fordi svaret ikke
hadde stoerrelse.

To ting maa derfor pinnes, og de er ulike:

1. **Tallet er maalt.** Testene under mater syntetiske maalinger der
   deklarasjonen LYVER om volumet, og krever at leseren svarer med
   maalingen. Uten dem ville «sortér etter betydning» kunne innfris av et
   felt noen skrev for haand.
2. **Sorteringen er en sortering.** Et hull paa to og et paa 190 000 skal
   komme i den rekkefølgen, ogsaa naar navnene sier det motsatte.
   Separerende tilfelle: `aaa.lite` mot `zzz.stort` — alfabetisk og
   volummessig orden er motsatt.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
MODUL = ROT / "scripts" / "atlas_volum.py"

_spec = importlib.util.spec_from_file_location("atlas_volum", MODUL)
assert _spec and _spec.loader
av = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(av)

DEKNING = json.loads((ROT / "schema" / "atlas_dekning.json").read_text(
    encoding="utf-8"))
SNAPSHOT = json.loads(
    (ROT / "schema" / "nats_domener.snapshot.json").read_text(encoding="utf-8"))


def _dekl(rader: dict) -> dict:
    return {"domener": {navn: {"status": s, "meldinger": m,
                               "noder": [], "begrunnelse": "test",
                               "emner": list(e)}
                        for navn, (s, m, e) in rader.items()}}


def _snap(rader: dict) -> dict:
    return {"domener": {navn: {"emner": dict(e)}
                        for navn, e in rader.items()}}


class TestSorteringEtterBetydning(unittest.TestCase):
    def test_storrelse_gaar_foran_alfabet(self):
        """Det separerende tilfellet. Alfabetisk ville sagt `aaa.lite`
        foerst; det er nettopp lesningen kortet fant."""
        dekl = _dekl({"aaa.lite": ("ikke_dekket", 2, ["a"]),
                      "zzz.stort": ("ikke_dekket", 190000, ["b"])})
        ut = av.hull(dekl)
        self.assertEqual([r["domene"] for r in ut], ["zzz.stort", "aaa.lite"],
                         "hullene kom i alfabetisk rekkefølge — da kan et "
                         "hull på 190 000 ikke skilles fra ett på 2")

    def test_rekkefoelgen_henger_ikke_paa_innsettingsrekkefoelgen(self):
        fram = _dekl({"a": ("ikke_dekket", 5, []), "b": ("ikke_dekket", 500, []),
                      "c": ("ikke_dekket", 50, [])})
        bak = _dekl({"c": ("ikke_dekket", 50, []), "b": ("ikke_dekket", 500, []),
                     "a": ("ikke_dekket", 5, [])})
        self.assertEqual([r["domene"] for r in av.hull(fram)],
                         [r["domene"] for r in av.hull(bak)])

    def test_like_store_hull_sorteres_paa_navn(self):
        """Uten dette ville rekkefølgen mellom like store hull vaert
        tilfeldig, og en diff ville sett ut som en endring."""
        dekl = _dekl({"b": ("ikke_dekket", 10, []), "a": ("ikke_dekket", 10, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl)], ["a", "b"])

    def test_volumet_leses_fra_maalingen_naar_den_finnes(self):
        """Deklarasjonen sier 3, maalingen sier 3000. Leseren skal svare
        maalingen — ellers kan «sortert etter betydning» innfris av et tall
        noen skrev for haand, som er nøyaktig feilmodusen kortet navngir."""
        dekl = _dekl({"x": ("ikke_dekket", 3, ["e1"])})
        snap = _snap({"x": {"e1": 3000}})
        ut = av.hull(dekl, snap)
        self.assertEqual(ut[0]["meldinger"], 3000)

    def test_emnefordelingen_foelger_domenet(self):
        snap = _snap({"x": {"liten": 2, "stor": 90}})
        dekl = _dekl({"x": ("ikke_dekket", 92, ["liten", "stor"])})
        self.assertEqual(av.hull(dekl, snap)[0]["emner"],
                         [("stor", 90), ("liten", 2)])

    def test_standarden_er_bare_ikke_dekket(self):
        dekl = _dekl({"hull": ("ikke_dekket", 10, []),
                      "nesten": ("delvis", 5000, []),
                      "dekket": ("dekket", 9000, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl)], ["hull"])

    def test_alle_statuser_kan_vis_se_naar_statuser_er_none(self):
        """`--alle` finnes fordi motsatt feil ogsaa er usynlig: en `dekket`
        kanal med mye trafikk bak én node ser ferdig ut."""
        dekl = _dekl({"hull": ("ikke_dekket", 10, []),
                      "dekket": ("dekket", 9000, [])})
        self.assertEqual([r["domene"] for r in av.hull(dekl, statuser=None)],
                         ["dekket", "hull"])

    def test_den_ekte_filen_gir_hull_sortert_etter_volum(self):
        rader = av.hull(DEKNING, SNAPSHOT)
        self.assertTrue(rader, "ingen ikke_dekket-domener — da maa testen "
                               "skrives om, ikke bare passere")
        self.assertTrue(all(r["status"] == "ikke_dekket" for r in rader))
        nokler = [(-r["meldinger"], r["domene"]) for r in rader]
        self.assertEqual(nokler, sorted(nokler))
        self.assertTrue(all(r["meldinger"] > 0 for r in rader),
                        "et deklarert hull uten maalte meldinger er ikke "
                        "maalt — det er et tall noen har skrevet")


class TestMaalingen(unittest.TestCase):
    def _stub(self, katalog: Path, kropp: str) -> Path:
        fil = katalog / "stub-verden-mcp.py"
        fil.write_text(kropp, encoding="utf-8")
        return fil

    def test_maal_bussen_normaliserer_emnet_til_domenets_form(self):
        """Bussen navngir emnet fullt ut (`verden.vaer.prediksjon.metno`);
        snapshottet bærer den korte formen. En maaling som skrev den fulle
        formen ville dobbeltfoert domenet i hver rad — og falt testen i
        test_atlas_dekning, som sammenligner emnelistene."""
        kropp = (
            "def verden_domener(_args):\n"
            "    return {'domener': {'verden.vaer': [\n"
            "        {'emne': 'verden.vaer.prediksjon.metno', 'meldinger': 7},\n"
            "        {'emne': 'verden.vaer.tilstand.metar', 'meldinger': 3},\n"
            "    ]}, 'tomme_stroemmer': []}\n")
        with tempfile.TemporaryDirectory() as d:
            fil = self._stub(Path(d), kropp)
            gammel = os.environ.get("NATS_VERDEN")
            os.environ["NATS_VERDEN"] = "nats://bruker:hemmelig@eksempel:4222"
            try:
                ut = av.maal_bussen(fil)
            finally:
                if gammel is None:
                    os.environ.pop("NATS_VERDEN", None)
                else:
                    os.environ["NATS_VERDEN"] = gammel
        self.assertEqual(ut["domener"],
                         {"verden.vaer": {"prediksjon.metno": 7,
                                          "tilstand.metar": 3}})

    def test_maal_bussen_nektar_aa_gjette_naar_verktoeyet_mangler(self):
        with self.assertRaises(av.VolumFeil) as ctx:
            av.maal_bussen(Path("/finnes/ikke/verden-mcp.py"))
        self.assertIn("verden-mcp.py", str(ctx.exception))

    def test_modulen_har_ingen_volumtabell(self):
        """Den mekaniske gaten mot feilmodusen kortet navngir: «ikke løs det
        ved aa gjette». Et tall i koden er en paastand om bussen som ingen
        maaling holder oppdatert — den råtner ved foerste endring i
        trafikken. Kommentarer og docstrings bærer maalte tall; KODEN skal
        ikke bære ett eneste et."""
        tre = ast.parse(MODUL.read_text(encoding="utf-8"))
        tall = [n.value for n in ast.walk(tre)
                if isinstance(n, ast.Constant) and isinstance(n.value, int)
                and not isinstance(n.value, bool) and abs(n.value) >= 1000]
        self.assertEqual(
            tall, [],
            f"et tall større enn 999 staar i koden ({tall}) — volumet skal "
            f"komme fra maalingen, ikke fra en tabell")


class TestSkrivingen(unittest.TestCase):
    def test_oppdater_dekning_roerer_ikke_stillingtagen(self):
        dekl = {"_form": "x", "domener": {
            "a.b": {"status": "delvis", "noder": ["n1"],
                    "begrunnelse": "fordi noen har vurdert det",
                    "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(dekl, {"a.b": {"tilstand.k": 41}})
        rad = ny["domener"]["a.b"]
        self.assertEqual(rad["meldinger"], 41)
        self.assertEqual(rad["status"], "delvis")
        self.assertEqual(rad["noder"], ["n1"])
        self.assertEqual(rad["begrunnelse"], "fordi noen har vurdert det")
        self.assertEqual(ny["_form"], "x")
        self.assertEqual(rapport["nye_domener"], [])
        self.assertEqual(rapport["nye_emner"], {})

    def test_nye_domener_og_emner_rapporteres_og_deklareres_ikke(self):
        """Maalingen faar ikke lov aa deklarere et domene: status og
        begrunnelse er en stillingtagen. Den skal NAVNGI det som mangler,
        slik at invarianten feller — ikke gjøre testen groenn."""
        dekl = {"domener": {"a.b": {"status": "ikke_dekket", "noder": [],
                                    "begrunnelse": "ingen node",
                                    "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(
            dekl, {"a.b": {"tilstand.k": 1, "diskusion.ny": 9},
                   "c.d": {"tilstand.m": 5}})
        self.assertEqual(rapport["nye_domener"], ["c.d"])
        self.assertEqual(rapport["nye_emner"], {"a.b": ["diskusion.ny"]})
        self.assertNotIn("c.d", ny["domener"])
        self.assertNotIn("diskusion.ny", ny["domener"]["a.b"]["emner"])

    def test_et_domene_ute_av_maalingen_faar_null_ikke_gammelt_tall(self):
        """Retensjonen kan tømme et domene. Da er det gamle tallet en
        loegn om naa; null er en maaling av at det ikke lenger bærer noe."""
        dekl = {"domener": {"borte.nå": {"status": "ikke_dekket", "noder": [],
                                         "begrunnelse": "x",
                                         "emner": ["tilstand.k"]}}}
        ny, rapport = av.oppdater_dekning(dekl, {})
        self.assertEqual(ny["domener"]["borte.nå"]["meldinger"], 0)
        self.assertEqual(rapport["borte"], ["borte.nå"])

    def test_snapshottet_baerer_proveniens_og_maalt_antall(self):
        with tempfile.TemporaryDirectory() as d:
            sti = Path(d) / "snap.json"
            av.skriv_snapshot(sti, {"b.d": {"tilstand.k": 4},
                                    "a.c": {"tilstand.m": 1}},
                              lest_av="test", maalt="2026-09-17T00:00:00Z")
            data = json.loads(sti.read_text(encoding="utf-8"))
        prov = data["_proveniens"]
        self.assertEqual(prov["maalt"], "2026-09-17T00:00:00Z")
        self.assertEqual(prov["lest_av"], "test")
        self.assertTrue(prov["kilde"].strip())
        self.assertEqual(data["domener"]["a.c"]["emner"], {"tilstand.m": 1})
        self.assertEqual(list(data["domener"]), ["a.c", "b.d"],
                         "domenene skal staa sortert — en usortert fil gir "
                         "diff-støy uten informasjon")

    def test_maal_skriver_begge_filene_og_leser_arbeidsstreet(self):
        """Maalingen SKRIVER til arbeidsstreet, og maa derfor lese det
        samme street. Foerste utgave leste deklarasjonen fra refen — en
        ukommitert stillingtagen ville da blitt kastet stille av en
        vedlikeholds-kjoering."""
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            (rot / "schema").mkdir()
            (rot / "schema" / "atlas_dekning.json").write_text(
                json.dumps({"_form": "x", "domener": {
                    "a.b": {"status": "delvis", "noder": ["n1"],
                            "begrunnelse": "ukommitert vurdering",
                            "emner": ["tilstand.k"]}}},
                    indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            opprinnelig = av.maal_bussen
            setattr(av, "maal_bussen",
                    lambda *a, **k: {"domener": {"a.b": {"tilstand.k": 77}},
                                     "tomme_stroemmer": []})
            try:
                self.assertEqual(av.hoved(["--maal", "--repo", str(rot)]), 0)
            finally:
                setattr(av, "maal_bussen", opprinnelig)
            dekl = json.loads((rot / "schema" / "atlas_dekning.json")
                              .read_text(encoding="utf-8"))
            snap = json.loads((rot / "schema" / "nats_domener.snapshot.json")
                              .read_text(encoding="utf-8"))
        self.assertEqual(dekl["domener"]["a.b"]["begrunnelse"],
                         "ukommitert vurdering")
        self.assertEqual(dekl["domener"]["a.b"]["status"], "delvis")
        self.assertEqual(dekl["domener"]["a.b"]["meldinger"], 77)
        self.assertEqual(snap["domener"]["a.b"]["emner"], {"tilstand.k": 77})
        self.assertTrue(snap["_proveniens"]["lest_av"].strip())

    def test_leseren_feiler_forstaaelig_paa_en_maaling_uten_antall(self):
        """Refs eldre enn denne modulen bærer emnene som en navneliste.
        Foerste utgave krasjet med `AttributeError: 'list' object has no
        attribute 'values'` — en stakksporing som sier at noe er i stykker,
        ikke hva som mangler. Volumet finnes ikke i den formen, og leseren
        skal SI det."""
        with self.assertRaises(av.VolumFeil) as ctx:
            av.meldinger_per_domene({"domener": {"x": {"emner": ["tilstand.k"]}}})
        self.assertIn("--maal", str(ctx.exception))

    def test_les_fra_ref_feiler_hoeyt_paa_ukjent_ref(self):
        """Samme regel som atlas_lesing: en ugyldig ref skal reise, ikke
        stille falle tilbake til arbeidsstreet."""
        with self.assertRaises(av.VolumFeil):
            av.les_fra_ref(ROT, "finnes-ikke-ref")

    def test_les_fra_ref_leser_begge_filene(self):
        lest = av.les_fra_ref(ROT, "HEAD")
        self.assertIn("snapshot", lest)
        self.assertIn("dekning", lest)
        self.assertEqual(len(lest["commit"]), 40)


if __name__ == "__main__":
    unittest.main()
