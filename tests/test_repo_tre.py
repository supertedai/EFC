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
# Den settes sammen av deler her, ikke skrevet rett ut: vernet skanner alle
# sporede filer, og denne fila er sporet — med adressen skrevet ut felt den
# seg selv (målt: 1 failed på `tests/test_repo_tre.py` før denne linja ble
# delt). Å bygge strengen av deler er det som gjør at ingen fil er unntatt.
PRIVAT = "Hassel" + "vegen 5, " + "4051 " + "Sola"


class Rigg(unittest.TestCase):
    """Et temp-tre med git, uten commit — `git add` er nok for indeksen."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def skriv(self, rel: str, tekst: str = "x\n", spor: bool = True) -> Path:
        """Skriv en fil. `spor=True` legger den i indeksen naar treet er git.

        Verktoeyet leser INDEKSEN, ikke disken. En rigg som bare skriver
        til disk bygger derfor et tomt tre — og det ble «loest» ved aa la
        `filer()` falle tilbake til diskvandring, som gjorde at USPOREDE
        filer ble lest i et ekte, tomt tre. Rettelsen hoerer her.

        `spor=False` for testene som bevisst vil ha en fil utenfor
        indeksen; ignorerte stier feiler stille paa `git add`, som er
        meningen (se `test_ignorert_katalog_er_ikke_med`).
        """
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(tekst, encoding="utf-8")
        if spor and (self.tmp / ".git").exists():
            subprocess.run(["git", "-C", str(self.tmp), "add", "--", rel],
                           capture_output=True)  # ignorert sti feiler — greit
        return p

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.tmp)] + list(args), check=True,
                       capture_output=True)

    def git_init(self) -> None:
        self.git("init", "-q")

    def rel(self, stier) -> list[str]:
        return sorted(p.relative_to(self.tmp).as_posix() for p in stier)


class GitTre(Rigg):
    def test_tomt_indeks_er_et_svar_ikke_en_fallback(self):
        """Et gyldig, TOMT git-tre skal gi null filer — ikke diskvandring.

        Maalt i uavhengig review 2026-09-17: `git_indeks` returnerte
        `stier or None`. Et tomt tre ble dermed behandlet som «ikke et
        git-tre», `filer()` falt tilbake til diskvandring, og USPOREDE
        filer ble lest — i strid med premisset om at git-treet er
        autoritativt. Reprodusert med `git init` + én usporet fil.

        De to tilstandene maa skilles: «git svarte, og svaret var tomt»
        mot «git svarte ikke». Bare den andre skal falle tilbake.
        """
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=rot, check=True)
            (rot / "usporet.jsonld").write_text("PRIVAT", encoding="utf-8")
            self.assertEqual(git_indeks(rot), [],
                             "tomt tre skal gi tom liste, ikke None")
            self.assertEqual(filer(rot), [],
                             "en usporet fil skal ikke leses fra et git-tre")

    def test_utenfor_git_faller_tilbake_til_disk(self):
        """Den andre halvdelen: utenfor et git-tre SKAL disken leses."""
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            (rot / "a.jsonld").write_text("{}", encoding="utf-8")
            self.assertIsNone(git_indeks(rot),
                              "utenfor git skal svaret vaere None")
            self.assertEqual(len(filer(rot)), 1,
                             "fallbacken skal fortsatt virke")

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
        self.skriv("docs/ulost.json", "{}\n", spor=False)
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/sporet.json"])

    def test_sporet_fil_leses_fra_indeksen(self):
        """Riggen legger filen i indeksen, og den leses derfra.

        Dette erstatter `test_tom_indeks_faller_tilbake_til_disken`, som
        laaste inne feilen: den bygget et tomt indeks og krevde at
        `filer()` leste DISKEN i stedet. Det er den atferden som lekker —
        se `test_tomt_indeks_er_et_svar_ikke_en_fallback`.
        """
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
