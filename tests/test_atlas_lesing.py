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
        self.assertEqual(
            [n["id"] for n in forsta["noder"]],
            [n["id"] for n in andre["noder"]],
            "lesningen endret seg da arbeidsstreet endret seg — den leser "
            "arbeidsstreet, ikke refen")
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
