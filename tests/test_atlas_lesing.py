"""Konvensjonen skal staa skriftlig, og den skal navngi refen.

Et notat ingen kan feile mot er et notat som forsvinner. Denne testen
holder dokumentet fast til det det paastaar: at `git:origin/main` er
navngitt som autoritativ, og at arbeidsstreet er navngitt som ikke-det.
"""
import unittest
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
DOK = ROT / "docs" / "atlas-lesing.md"


class TestAtlasLesing(unittest.TestCase):
    def test_konvensjonen_finnes(self):
        self.assertTrue(DOK.exists(), "docs/atlas-lesing.md mangler")

    def test_den_navngir_den_autoritative_refen(self):
        t = DOK.read_text(encoding="utf-8")
        self.assertIn("origin/main", t,
                      "dokumentet navngir ikke den autoritative refen")

    def test_den_navngir_arbeidsstreet_som_ikke_autoritativt(self):
        t = DOK.read_text(encoding="utf-8")
        self.assertIn("working copy", t.lower())


if __name__ == "__main__":
    unittest.main()
