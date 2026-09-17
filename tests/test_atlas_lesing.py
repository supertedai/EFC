"""Regelen for atlas-lesing er KJORBAR, ikke beskrevet.

Reviewfunn runde 1 (PR #471), blokkerende og rett: de forrige testene leste
dokumentet og krevde at ordene «origin/main» og «working copy» fantes. En
mutant som SNUDDE regelen — «read the atlas from the working copy ... Never
from git:origin/main» — passerte 3/3. Testen saa formen, ikke meningen.

Samme feilklasse som `startswith("git:")`-testen i PR #1016: den kontrollerte
formatet og slapp enhver verdi gjennom.

  En test kan ikke lese mening ut av prosa. Regelen maa derfor bo i en
  funksjon som kan kjores — og testes ved aa endre VERDEN, ikke teksten.

Den avgjorende testen under muterer arbeidsstreet og krever at lesningen er
UPAVIRKET. Det er den eneste testen som skiller «les fra refen» fra «les fra
arbeidsstreet», uansett hva dokumentet sier.
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

REPO = ROT


def _git(*a: str) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a],
                          capture_output=True, text=True).stdout


class TestAtlasLesing(unittest.TestCase):
    def test_leser_fra_refen_og_navngir_kilden(self):
        d = les_atlas(REPO)
        self.assertEqual(d["kilde"], "git:origin/main")
        self.assertEqual(d["ref"], "origin/main")
        self.assertTrue(d["commit"], "commit mangler — kilden er ikke navngitt")
        self.assertGreater(len(d["noder"]), 0)

    def test_arbeidsstreet_paavirker_ikke_lesningen(self):
        """DEN AVGJORENDE TESTEN.

        Endrer arbeidsstreet — den filen en naiv implementasjon ville lest —
        og krever at resultatet er bit for bit likt. En implementasjon som
        leste filen ville endret seg her. Uansett hva dokumentet sier.
        """
        forsta = les_atlas(REPO)
        fil = REPO / "schema" / "regime_nodes.jsonld"
        opprinnelig = fil.read_bytes()
        try:
            odelagt = {"nodes": [{"id": "SLEPTET"}]}
            fil.write_text(json.dumps(odelagt), encoding="utf-8")
            andre = les_atlas(REPO)
        finally:
            fil.write_bytes(opprinnelig)
        # BIT-FOR-BIT: hele strukturen, ikke bare id-ene. Reviewfunn
        # runde 2: en mutant som endret alle FELTER men beholdt id-ene
        # passerte en sammenligning paa id-nivaa.
        self.assertEqual(
            forsta["noder"], andre["noder"],
            "lesningen endret seg da arbeidsstreet endret seg — den leser "
            "arbeidsstreet, ikke refen")
        self.assertEqual(json.dumps(forsta, sort_keys=True),
                         json.dumps(andre, sort_keys=True),
                         "hele resultatet maa vaere identisk")
        self.assertNotIn("SLEPTET", [n["id"] for n in andre["noder"]])

    def test_ukjent_ref_feiler_og_faller_ikke_stille_tilbake(self):
        """En stille fallback til arbeidsstreet er nettopp feilmodusen."""
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(REPO, ref="finnes/ikke")

    def test_den_leste_commiten_er_den_refen_peker_paa(self):
        d = les_atlas(REPO)
        self.assertEqual(d["commit"], _git("rev-parse", "origin/main").strip())

    def test_foreldet_ref_er_synlig_i_resultatet(self):
        """`origin/main` kan vaere foreldet — den er en remote-tracking ref.
        Funksjonen henter ikke av seg selv, men den RAPPORTERER commiten,
        saa en foreldet ref staar i resultatet og ikke i leserens antakelse.
        """
        d = les_atlas(REPO, hent=False)
        self.assertEqual(len(d["commit"]), 40,
                         "commit maa vaere full SHA — ellers kan ferskhet "
                         "ikke sammenlignes med origin")


if __name__ == "__main__":
    unittest.main()


class TestDokumentetPekerPaaKoden(unittest.TestCase):
    """Dokumentet skal ikke baere regelen selv — den kan ikke testes.

    En prosa-regel kan snus uten at noen test feller (bevist i runde 1:
    mutanten «read from the working copy ... Never from git:origin/main»
    passerte 3/3). Derfor skal dokumentet PEKE PAA funksjonen, og denne
    testen holder pekeren fast.
    """

    def test_dokumentet_navngir_den_kjorbare_regelen(self):
        t = (ROT / "docs" / "atlas-lesing.md").read_text(encoding="utf-8")
        self.assertIn("scripts/atlas_lesing.py", t,
                      "dokumentet peker ikke paa den kjorbare regelen")

    def test_funksjonen_som_dokumentet_peker_paa_finnes(self):
        self.assertTrue((ROT / "scripts" / "atlas_lesing.py").exists())


class TestFunksjonensKanter(unittest.TestCase):
    """Reviewfunn runde 2: ugyldig JSON og manglende 'nodes' ga raa
    JSONDecodeError/KeyError. Samme prinsipp som resten — ingen stille
    eller feilaktig feiltype naar leseren skal kunne stole paa resultatet.
    """

    def _repo(self, innhold: str):
        t = tempfile.mkdtemp()
        r = Path(t)
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
        r = self._repo("{ikke json")
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(r, ref="HEAD")

    def test_manglende_nodes_gir_AtlasLesingFeil(self):
        r = self._repo('{"noe": "annet"}')
        with self.assertRaises(AtlasLesingFeil):
            les_atlas(r, ref="HEAD")

    def test_hent_oppdaterer_refen(self):
        """`hent=True` skal faktisk hente. Revieweren beviste det manuelt;
        det skal staa i testsettet, ikke bare i en rapport."""
        opp = tempfile.mkdtemp()
        subprocess.run(["git", "init", "-q", "--bare", opp],
                       capture_output=True, text=True)
        arb = tempfile.mkdtemp()
        r = Path(arb)
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
        forsta = les_atlas(r, ref="origin/main", hent=True)["commit"]
        f.write_text('{"nodes": [{"id": "b"}]}', encoding="utf-8")
        for cmd in (["add", "-A"],
                    ["-c", "user.name=t", "-c", "user.email=t@t",
                     "commit", "-qm", "2"], ["push", "-q", "origin", "main"]):
            subprocess.run(["git", "-C", str(r), *cmd],
                           capture_output=True, text=True)
        andre = les_atlas(r, ref="origin/main", hent=True)["commit"]
        self.assertNotEqual(forsta, andre, "hent=True hentet ikke")


class TestIngenAbsolutteStier(unittest.TestCase):
    """Regel 16: `docs/` er Pages-roten — det som staar der PUBLISERES.

    Reviewfunn runde 3: dokumentet navnga vertsspesifikke stier.
    Reviewfunn runde 4 (BLOKKERER): den foerste testen brukte en fast liste
    av stier jeg tilfeldigvis kom paa. Den slapp `/Users/morten/...`,
    `C:\\Users\\morten\\...` og `/srv/agent-work/...` gjennom.

      En liste over kjente tilfeller er ikke en invariant over klassen.
      Det er samme feil som resten av PR-en handler om.

    Invarianten er generisk: en ABSOLUTT filsystem-sti er vertsspesifikk
    uansett hvilken vert den peker paa. Repo-relative navn er dokumentasjon
    og skal gjennom.

    Reviewfunn runde 5: den forrige utgaven krevde to stiledd og manglet
    UNC og filsystem-URL-er. /Users, \\server\share\EFC,
    //server/share/EFC og file:///Users/morten/EFC slapp gjennom. Naa
    dekkes de.

    GRENSE, sagt hoeyt: dette er en SVARTELISTE over kjente stiformer, og
    en svarteliste kan i prinsippet alltid omgaas. Den er likevel et reelt
    vern her fordi den fanger formene som faktisk forekommer i praksis —
    og fordi testen under krever at hver form den paastaar aa fange FAKTISK
    fanges. Blir den omgaatt igjen, er spoersmaalet om tilnaermingen er
    feil, ikke om monsteret mangler et ledd.
    """

    ABSOLUTT = re.compile(r"""
    (?:^|[\s(\[`"'>])
    (?:
        /(?:[A-Za-z0-9._-]+)(?:/[A-Za-z0-9._-]*)*   # unix-absolutt, 1+ ledd
      | /{2,}[A-Za-z0-9._-]+                        # UNC med skraastrek
      | \\\\{1,2}[A-Za-z0-9._-]+                    # windows UNC
      | [A-Za-z][A-Za-z0-9+.-]*:///                 # filsystem-URL, tom vert
      | [A-Za-z]:[\\/]                              # windows-stasjon
      | ~/                                          # hjemmekatalog
    )
    """, re.VERBOSE)

    def _sjekk(self, sti: Path, hva: str):
        t = sti.read_text(encoding="utf-8")
        treff = [m.group(0).strip() for m in self.ABSOLUTT.finditer(t)]
        self.assertEqual(treff, [], f"absolutt sti i {hva}: {treff}")

    def test_publisert_dokument_har_ingen_absolutte_stier(self):
        self._sjekk(ROT / "docs" / "atlas-lesing.md", "publisert doc")

    def test_modulens_docstring_har_ingen_absolutte_stier(self):
        self._sjekk(ROT / "scripts" / "atlas_lesing.py", "docstring")

    def test_invarianten_fanger_vertsformer_den_forrige_misset(self):
        """Reviewerens fire eksempler, som alle slapp gjennom den forrige
        lista. Testes eksplisitt saa invarianten ikke driver tilbake til en
        oppramsing."""
        for form in ("/Users/morten/EFC-review", "C:\\Users\\morten\\EFC",
                     "/srv/agent-work/EFC", "/opt/agent_work/EFC",
                     "~/EFC",
                     # runde 5 — disse slapp gjennom den forrige invarianten
                     "/Users", "\\\\server\\share\\EFC",
                     "//server/share/EFC", "file:///Users/morten/EFC"):
            self.assertIsNotNone(
                self.ABSOLUTT.search("se " + form),
                f"invarianten fanger ikke vertsformen {form}")

    def test_invarianten_slipper_repo_relative_navn_gjennom(self):
        for form in ("scripts/atlas_lesing.py", "docs/atlas-lesing.md",
                     "origin/main:schema/regime_nodes.jsonld"):
            self.assertIsNone(
                self.ABSOLUTT.search("se " + form),
                f"invarianten felte et repo-relativt navn: {form}")


if __name__ == "__main__":
    unittest.main()
