"""Test av scripts/maintenance/_repo_tre.py — verktøyene svarer på git-treet.

Målt 2026-09-17 (kanban t_12494ba1): tre instrumenter vandret over disken
(`rglob`, `os.walk`) og fant `.worktrees/` i hovedklonen — gitignorert, men på
disk. Tre tester som var grønne i CI ble røde lokalt, på filer som ikke er i
repoet. Testene her pinner begge sider: hva leseren svarer, og at de tre
instrumentene ikke lenger ser en ignorert arbeidsflate.
"""
from __future__ import annotations

import importlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
_MAINT = _REPO / "scripts" / "maintenance"
if str(_MAINT) not in sys.path:
    sys.path.insert(0, str(_MAINT))

from _repo_tre import filer, git_indeks  # noqa: E402

# Samme adresse som regresjonsvernet i test_regime_node_schema.py leter etter.
PRIVAT = "Hasselvegen 5, 4051 Sola"


class Rigg(unittest.TestCase):
    """Et temp-tre med git, uten commit — `git add` er nok for indeksen."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def skriv(self, rel: str, tekst: str = "x\n") -> Path:
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(tekst, encoding="utf-8")
        return p

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.tmp)] + list(args), check=True,
                       capture_output=True)

    def git_init(self) -> None:
        self.git("init", "-q")

    def rel(self, stier) -> list[str]:
        return sorted(p.relative_to(self.tmp).as_posix() for p in stier)


class GitTre(Rigg):
    def test_ignorert_katalog_er_ikke_med(self):
        """Den målte feilen: `.worktrees/` står i .gitignore, men ligger på
        disk — og en diskvandring svarte med den."""
        self.git_init()
        self.skriv(".gitignore", ".worktrees/\n")
        self.skriv("docs/a.json", "{}\n")
        self.skriv(".worktrees/efc-ev-abc/docs/papers/privat.jsonld", PRIVAT)
        self.git("add", ".gitignore", "docs/a.json")
        self.assertEqual(self.rel(filer(self.tmp)), [".gitignore", "docs/a.json"])

    def test_bare_indeksen_svarer(self):
        """Uløste filer er ikke med: svaret skal ikke avhenge av hva som
        tilfeldigvis ligger ulagt i arbeidsstreet. `git add` er grensen."""
        self.git_init()
        self.skriv("docs/sporet.json", "{}\n")
        self.skriv("docs/ulost.json", "{}\n")
        self.git("add", "docs/sporet.json")
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/sporet.json"])

    def test_tom_indeks_faller_tilbake_til_disken(self):
        """Riggene bygger trær som ikke er lagt inn i git — de må fortsatt
        kunne leses, ellers måler ikke enhetstestene noe."""
        self.git_init()
        self.skriv("docs/a.json", "{}\n")
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/a.json"])

    def test_uten_git_leses_disken(self):
        self.skriv("docs/a.json", "{}\n")
        self.assertIsNone(git_indeks(self.tmp))
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/a.json"])

    def test_ignorert_katalog_hoppes_over_ved_navn_uten_git(self):
        """Fallbacken leser disken, men de ignorerte katalogene er de samme:
        en katalog som ikke er i repoet skal ikke kunne felle et svar."""
        self.skriv("docs/a.json", "{}\n")
        self.skriv(".worktrees/x/docs/b.json", "{}\n")
        self.skriv("__pycache__/c.pyc", "x\n")
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/a.json"])

    def test_suffix_og_unntak(self):
        self.git_init()
        self.skriv("docs/a.json", "{}\n")
        self.skriv("docs/b.jsonld", "{}\n")
        self.skriv("docs/c.md", "x\n")
        self.git("add", "-A")
        self.assertEqual(self.rel(filer(self.tmp, suffixes={".jsonld"})), ["docs/b.jsonld"])
        self.assertEqual(self.rel(filer(self.tmp, skip_files={"docs/a.json"})),
                         ["docs/b.jsonld", "docs/c.md"])

    def test_sporet_men_slettet_fra_disken_er_ikke_med(self):
        """Funksjonen svarer med filer som kan leses — en `check()` skal ikke
        felle på en sti som ikke finnes."""
        self.git_init()
        p = self.skriv("docs/a.json", "{}\n")
        self.git("add", "docs/a.json")
        p.unlink()
        self.assertEqual(filer(self.tmp), [])

    def test_tomt_tre_er_tom_liste_ikke_en_feil(self):
        self.git_init()
        self.assertEqual(filer(self.tmp), [])


class Instrumentene(Rigg):
    """De tre instrumentene skal svare likt i alle kloner: en ignorert
    arbeidsflate under repoet skal ikke kunne felle dem."""

    def test_identitetsvakten_ser_ikke_ignorert_arbeidsflate(self):
        ef = importlib.import_module("efc_identity")
        self.git_init()
        self.skriv(".gitignore", ".worktrees/\n")
        self.skriv("docs/s.json", json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://supertedai.github.io/EFC/s.json",
            "type": "object", "properties": {},
        }))
        # Legacy binding + manglende @id, i en katalog git ignorerer.
        self.skriv(".worktrees/efc-ev-abc/docs/legacy.jsonld",
                   json.dumps({"@context": {"efc": "https://github.com/supertedai/EFC/ontology#"}}))
        self.git("add", ".gitignore", "docs/s.json")
        problemer = ef.check(self.tmp)
        self.assertEqual([p for p in problemer if ".worktrees" in p], [], problemer)

    def test_ontologivakten_ser_ikke_ignorert_arbeidsflate(self):
        ont = importlib.import_module("efc_ontology")
        self.git_init()
        self.skriv(".gitignore", ".worktrees/\n")
        self.skriv("docs/a.jsonld", json.dumps({"@context": {"efc": ont.NS}}))
        self.skriv(".worktrees/efc-ev-abc/docs/legacy.jsonld",
                   json.dumps({"@context": {"efc": "https://github.com/supertedai/EFC/ontology#"}}))
        self.git("add", ".gitignore", "docs/a.jsonld")
        per_fil, _, antall, _ = ont.inventory(self.tmp)
        self.assertEqual(antall, 1, [str(p) for p in per_fil])
        self.assertEqual([p for p in per_fil if ".worktrees" in str(p)], [])


if __name__ == "__main__":
    unittest.main()
