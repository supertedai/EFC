r"""Atlas-lesing: regelen er KJØRBAR, og referanser er HVITELISTET.

To ting denne filen verner, og begge kom av reviewfunn:

1. REGELEN. Den forrige utgaven leste dokumentet og krevde at ordene
   «origin/main» og «working copy» fantes. En mutant som SNUDDE regelen —
   «read from the working copy … Never from git:origin/main» — passerte
   3/3. Samme feilklasse som `startswith("git:")` i PR #1016: formen ble
   kontrollert, enhver verdi slapp gjennom.

     En test kan ikke lese mening ut av prosa. Regelen bor derfor i
     `scripts/atlas_lesing.py`, og testes ved å endre VERDEN — testen
     muterer arbeidsstreet og krever at lesningen er bit-for-bit identisk.

2. REFERANSER. Tre runder prøvde å verne det publiserte dokumentet med en
   SVARTELISTE over onde stiformer:

     runde 3: fast liste (/opt/agent-work, /home/morten)
     runde 4: revieweren brøt den med /Users/morten, C:\\..., /srv/...
     runde 5: revieweren brøt den med UNC, file:///, ett-ledds absolutte
     runde 6: revieweren brøt den med path=..., markdown-tabellceller,
              file://<vert>/..., windows extended-length (\\?\)

   Og ga svaret: «Dette bør ikke løses med enda en lengre svarteliste. En
   whitelist av tillatte publiserte referanser er bedre.»

   Det er rett. En svarteliste må gjette BÅDE stiformene OG hvilke tegn som
   kan stå foran dem, og begge kan alltid omgås. Spørsmålet er snudd: ikke
   «er dette en vond sti?» men «er dette en form vi TILLATER?».
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

from atlas_lesing import AtlasLesingFeil, les_atlas  # noqa: E402


def _git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(ROT), *a],
                          capture_output=True, text=True).stdout


class TestAtlasLesing(unittest.TestCase):
    def test_leser_fra_refen_og_navngir_kilden(self):
        d = les_atlas(ROT)
        self.assertEqual(d["kilde"], "git:origin/main")
        self.assertEqual(d["ref"], "origin/main")
        self.assertTrue(d["commit"], "commit mangler — kilden er ikke navngitt")
        self.assertGreater(len(d["noder"]), 0)

    def test_arbeidsstreet_paavirker_ikke_lesningen(self):
        """DEN AVGJØRENDE TESTEN — endrer verden, ikke teksten.

        Muterer arbeidsstreets fil og krever at resultatet er BIT-FOR-BIT
        identisk. Reviewfunn runde 2: den forrige utgaven sammenlignet bare
        node-ID-er, så en mutant som endret alle FELTER men beholdt id-ene
        passerte. Nå sammenlignes hele strukturen.
        """
        forsta = les_atlas(ROT)
        fil = ROT / "schema" / "regime_nodes.jsonld"
        opprinnelig = fil.read_bytes()
        try:
            fil.write_text(
                json.dumps({"nodes": [dict(n, tampered=True)
                                      for n in forsta["noder"]]}),
                encoding="utf-8")
            andre = les_atlas(ROT)
        finally:
            fil.write_bytes(opprinnelig)
        self.assertEqual(forsta["noder"], andre["noder"],
                         "lesningen endret seg da arbeidsstreet endret seg — "
                         "den leser arbeidsstreet, ikke refen")
        self.assertEqual(json.dumps(forsta, sort_keys=True),
                         json.dumps(andre, sort_keys=True),
                         "hele resultatet må være identisk")
        self.assertNotIn("tampered", json.dumps(andre))

    def test_ukjent_ref_feiler_og_faller_ikke_stille_tilbake(self):
        """En stille fallback til arbeidsstreet er nettopp feilmodusen."""
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(ROT, ref="finnes/ikke")

    def test_den_leste_commiten_er_den_refen_peker_paa(self):
        self.assertEqual(les_atlas(ROT)["commit"],
                         _git("rev-parse", "origin/main").strip())

    def test_foreldet_ref_er_synlig_i_resultatet(self):
        """`origin/main` kan være foreldet — den er en remote-tracking ref.
        Funksjonen henter ikke av seg selv, men den RAPPORTERER full commit,
        så en foreldet ref står i resultatet og ikke i leserens antakelse."""
        self.assertEqual(len(les_atlas(ROT, hent=False)["commit"]), 40)


class TestDokumentetPekerPaaKoden(unittest.TestCase):
    """Dokumentet skal ikke bære regelen selv — den kan ikke testes.

    En prosa-regel kan snus uten at noen test feller (bevist i runde 1).
    Derfor skal dokumentet PEKE PÅ funksjonen, og denne testen holder
    pekeren fast.
    """

    def test_dokumentet_navngir_den_kjorbare_regelen(self):
        t = (ROT / "docs" / "atlas-lesing.md").read_text(encoding="utf-8")
        self.assertIn("scripts/atlas_lesing.py", t,
                      "dokumentet peker ikke på den kjørbare regelen")

    def test_funksjonen_som_dokumentet_peker_paa_finnes(self):
        self.assertTrue((ROT / "scripts" / "atlas_lesing.py").exists())


class TestFunksjonensKanter(unittest.TestCase):
    """Ugyldig JSON og manglende 'nodes' skal gi AtlasLesingFeil, ikke rå
    JSONDecodeError/KeyError. Ingen stille eller feil-typet feil når en
    leser skal kunne stole på resultatet."""

    def _repo(self, innhold: str) -> Path:
        r = Path(tempfile.mkdtemp())
        (r / "schema").mkdir()
        (r / "schema" / "regime_nodes.jsonld").write_text(innhold,
                                                          encoding="utf-8")
        for cmd in (["init", "-q"], ["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "x"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        return r

    def test_ugyldig_json_gir_AtlasLesingFeil(self):
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(self._repo("{ikke json"), ref="HEAD")

    def test_manglende_nodes_gir_AtlasLesingFeil(self):
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(self._repo('{"noe": "annet"}'), ref="HEAD")

    def test_hent_oppdaterer_refen(self):
        """`hent=True` skal faktisk hente. Revieweren beviste det manuelt;
        det skal stå i testsettet, ikke bare i en rapport."""
        opp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "--bare", opp],
                       capture_output=True, text=True)
        r = Path(tempfile.mkdtemp())
        for cmd in (["init", "-q", "-b", "main"],
                    ["remote", "add", "origin", opp]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        (r / "schema").mkdir()
        f = r / "schema" / "regime_nodes.jsonld"
        f.write_text('{"nodes": [{"id": "a"}]}', encoding="utf-8")
        for cmd in (["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "1"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        forste = les_atlas(r, ref="origin/main", hent=True)["commit"]
        f.write_text('{"nodes": [{"id": "b"}]}', encoding="utf-8")
        for cmd in (["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "2"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        andre = les_atlas(r, ref="origin/main", hent=True)["commit"]
        self.assertNotEqual(forste, andre, "hent=True hentet ikke")


class TestIngenVertsspesifikkeReferanser(unittest.TestCase):
    r"""Regel 16: `docs/` er Pages-roten — det som står der PUBLISERES.

    HVITELISTE, ikke svarteliste. Se modulens docstring for historikken:
    tre runder med stramming ble brutt tre ganger, og reviewen ga svaret
    som står der. Her sjekkes det motsatte spørsmålet — er dette en form
    vi TILLATER?

    Tillatt: repo-relative stier (to eller flere ledd), http(s)-lenker, og
    git-ref:sti. Alt annet som bærer en sti-separator er et avvik.
    """

    # Tillatte former. `..` som HELT segment peker ut av repoet og avvises
    # — reviewfunn runde 7: ../../etc/passwd slapp gjennom fordi '..'
    # matchet [A-Za-z0-9_.-]+. Regex alene er feil verktøy for dette
    # (lookahead ble for svak), saa segmentene sjekkes direkte.
    FORME = [
        re.compile(r"^[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)+$"),
        re.compile(r"^https?://[^\s]+$"),
        # Git-ref kan ha flere segmenter (origin/feature/foo), store
        # bokstaver og bindestrek (Release-2026), og refs/-form
        # (refs/heads/main). Reviewfunn runde 8: den forrige formen
        # krevde [a-z]+/[a-z]+ og avviste alle disse.
        # Sti-delen etter kolon maa STARTE med et vanlig tegn, ikke "/".
        # Uten dette matchet `file:///Users/...` ref-formen med `file`
        # som ref og `///Users/...` som sti — og rullet tilbake til
        # noeyaktig det runde 5-6 hadde stengt.
        re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*:[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)*$"),
    ]

    @staticmethod
    def _traverserer(t: str) -> bool:
        """`..` som eget segment, i stien eller etter git-refens kolon."""
        sti = t.split(":", 1)[1] if re.match(r"^[a-z]+/[a-z]+:", t) else t
        return ".." in sti.split("/")

    def _tillatt(self, t: str) -> bool:
        return (not self._traverserer(t)
                and any(r.match(t) for r in self.FORME))

    DEL = re.compile(r"[\s`|<>()\[\]{}\"'*,;]+")

    def _referanser(self, tekst: str):
        ut = []
        for linje in tekst.splitlines():
            if linje.startswith("#!"):
                continue
            for t in self.DEL.split(linje):
                if t in ("/", "\\"):
                    continue
                if "/" in t or "\\" in t or re.match(r"^[A-Za-z]:[\\/]", t):
                    ut.append(t)
        return ut

    def _avvik(self, tekst: str):
        return [t for t in self._referanser(tekst)
                if not self._tillatt(t)]

    def _docstring(self, sti: Path) -> str:
        t = sti.read_text(encoding="utf-8")
        i = t.index('"""') + 3
        return t[i:t.index('"""', i)]

    def test_publisert_dokument_har_bare_tillatte_referanser(self):
        self.assertEqual(
            self._avvik((ROT / "docs" / "atlas-lesing.md")
                        .read_text(encoding="utf-8")), [])

    def test_modulens_docstring_har_bare_tillatte_referanser(self):
        """Kun DOCSTRINGEN — filen inneholder også kode, og
        `except ... as e:` er ikke en sti."""
        self.assertEqual(
            self._avvik(self._docstring(ROT / "scripts" / "atlas_lesing.py")),
            [])

    def test_hvitelisten_fanger_formene_seks_runder_fant(self):
        """Hver form svartelisten slapp gjennom skal hvitelisten felle.
        Testet eksplisitt så listen ikke driver tilbake til en oppramsing av
        onde former — den er en hviteliste over TILLATTE former, og alt
        utenfor den felles uansett hvilken form det har."""
        for form in (
                "/Users", "/Users/morten/EFC", "C:\\Users\\morten",
                "path=/Users/morten/EFC", "|/Users/morten/EFC|",
                "<file:///Users/morten/EFC>", "file:///Users/morten/EFC",
                "file://localhost/Users/morten/EFC",
                "file://server/share/EFC",
                "\\\\?\\C:\\Users\\morten", "\\\\?\\UNC\\server\\share",
                "//server/share", "~/EFC", "\\\\server\\share\\EFC",
                "/opt/agent-work/EFC"):
            self.assertTrue(self._avvik("se " + form),
                            f"hvitelisten slipper gjennom {form}")

    def test_hvitelisten_slipper_legitime_referanser_gjennom(self):
        for form in ("scripts/atlas_lesing.py", "docs/atlas-lesing.md",
                     "origin/main:schema/regime_nodes.jsonld",
                     "https://example.com/a", "10.5281/zenodo.123"):
            self.assertEqual(self._avvik("se " + form), [],
                             f"hvitelisten felte {form}")


if __name__ == "__main__":
    unittest.main()


class TestTraversering(unittest.TestCase):
    """Reviewfunn runde 7: hvitelisten tillot `..` som segment.

    `../../etc/passwd` og `foo/../../etc` slapp gjennom fordi `..` matchet
    `[A-Za-z0-9_.-]+`. En hviteliste som tillater traversering peker ut av
    repoet og er ikke en hviteliste. Segmentet `..` avvises naa eksplisitt.
    """

    T = TestIngenVertsspesifikkeReferanser()

    def test_traversering_avvises(self):
        for form in ("../../etc/passwd", "../outside/file", "foo/../../etc",
                     "origin/main:../../etc", "a/./../b"):
            self.assertTrue(self.T._avvik("se " + form),
                            f"traversering slipper gjennom: {form}")

    def test_vanlige_dotnavn_avvises_ikke(self):
        """`.github/workflows/x.yml` og `a.b/c.d` er legitime — prikker er
        bare farlige som HELT segment."""
        for form in (".github/workflows/x.yml", "a.b/c.d"):
            self.assertEqual(self.T._avvik("se " + form), [],
                             f"felte et legitimt navn: {form}")


class TestGitRefFormer(unittest.TestCase):
    """Reviewfunn runde 8: hvitelisten var for SNEVER, ikke for vid.

    Den avviste origin/feature/foo:..., upstream/release/v1:... og
    Release-2026:... — alle legitime git-refs. En hviteliste som avviser
    ekte referanser er ogsaa en feil; den tvinger fram omskrivinger av
    korrekt dokumentasjon.

    Samtidig skal utvidelsen IKKE aapne for traversering: `..` er forbudt
    som segment baade i refen og i stien.
    """

    T = TestIngenVertsspesifikkeReferanser()

    def test_fler_segmenter_store_bokstaver_og_refs_form(self):
        for f in ("origin/main:schema/regime_nodes.jsonld",
                  "origin/feature/foo:schema/x.jsonld",
                  "upstream/release/v1:schema/x.jsonld",
                  "origin/Release-2026:schema/x.jsonld",
                  "refs/heads/main:schema/x.jsonld"):
            self.assertEqual(self.T._avvik("se " + f), [],
                             f"felte en legitim git-ref: {f}")

    def test_utvidelsen_aapnet_ikke_for_traversering(self):
        for f in ("origin/main:../../etc", "../../etc/passwd", "../x",
                  "foo/../../etc", "origin/../..:x"):
            self.assertTrue(self.T._avvik("se " + f),
                            f"traversering slipper gjennom: {f}")
