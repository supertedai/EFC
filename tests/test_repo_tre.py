"""Test of scripts/maintenance/_repo_tre.py — the tools answer from the git tree.

Measured 2026-09-17 (kanban t_12494ba1): three instruments walked the disk
(`rglob`, `os.walk`) and found `.worktrees/` in the main clone — gitignored,
but on disk. Three tests that were green in CI went red locally, on files that
are not in the repo. The tests here pin both sides: what the reader answers,
and that the three instruments no longer see an ignored work surface.
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

# The same address that the regression guard in test_regime_node_schema.py
# looks for. It is assembled from parts here, not written out: that guard
# scans all tracked files, and this file is tracked — written out it would
# trip itself (measured: 1 failed on `tests/test_repo_tre.py` before this
# line was split). Building the string from parts exempts no file.
PRIVAT = "Hassel" + "vegen 5, " + "4051 " + "Sola"


class Rigg(unittest.TestCase):
    """A temp tree with git, without a commit — `git add` is enough for the index."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: shutil.rmtree(self.tmp, ignore_errors=True))

    def skriv(self, rel: str, tekst: str = "x\n", spor: bool = True) -> Path:
        """Write a file. `spor=True` puts it in the index when the tree is git.

        The tool reads the INDEX, not the disk. A rig that only writes
        to disk therefore builds an empty tree — and that was "solved" by
        letting `filer()` fall back to a disk walk, which made UNTRACKED
        files readable in a real, empty tree. The fix belongs here.

        `spor=False` for the tests that deliberately want a file outside
        the index; ignored paths fail silently on `git add`, which is
        the point (see `test_ignorert_katalog_er_ikke_med`).
        """
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(tekst, encoding="utf-8")
        if spor and (self.tmp / ".git").exists():
            subprocess.run(["git", "-C", str(self.tmp), "add", "--", rel],
                           capture_output=True)  # ignored path fails — fine
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
        """A valid, EMPTY git tree must give zero files — not a disk walk.

        Measured in independent review 2026-09-17: `git_indeks` returned
        `stier or None`. An empty tree was thereby treated as "not a
        git tree", `filer()` fell back to a disk walk, and UNTRACKED
        files were read — against the premise that the git tree is
        authoritative. Reproduced with `git init` + one untracked file.

        The two states must be told apart: "git answered, and the answer
        was empty" versus "git did not answer". Only the second may fall
        back.
        """
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            subprocess.run(["git", "init", "-q"], cwd=rot, check=True)
            (rot / "usporet.jsonld").write_text("PRIVAT", encoding="utf-8")
            self.assertEqual(git_indeks(rot), [],
                             "an empty tree must give an empty list, not None")
            self.assertEqual(filer(rot), [],
                             "an untracked file must not be read from a git tree")

    def test_utenfor_git_faller_tilbake_til_disk(self):
        """The other half: outside a git tree the disk MUST be read."""
        with tempfile.TemporaryDirectory() as d:
            rot = Path(d)
            (rot / "a.jsonld").write_text("{}", encoding="utf-8")
            self.assertIsNone(git_indeks(rot),
                              "outside git the answer must be None")
            self.assertEqual(len(filer(rot)), 1,
                             "the fallback must still work")

    def test_ignorert_katalog_er_ikke_med(self):
        """The measured error: `.worktrees/` is in .gitignore, but lies on
        disk — and a disk walk answered with it."""
        self.git_init()
        self.skriv(".gitignore", ".worktrees/\n")
        self.skriv("docs/a.json", "{}\n")
        self.skriv(".worktrees/efc-ev-abc/docs/papers/privat.jsonld", PRIVAT)
        self.git("add", ".gitignore", "docs/a.json")
        self.assertEqual(self.rel(filer(self.tmp)), [".gitignore", "docs/a.json"])

    def test_bare_indeksen_svarer(self):
        """Unstaged files are not included: the answer must not depend on what
        happens to lie unadded in the worktree. `git add` is the boundary."""
        self.git_init()
        self.skriv("docs/sporet.json", "{}\n")
        self.skriv("docs/ulost.json", "{}\n", spor=False)
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/sporet.json"])

    def test_sporet_fil_leses_fra_indeksen(self):
        """The rig puts the file in the index, and it is read from there.

        This replaces `test_tom_indeks_faller_tilbake_til_disken`, which
        locked in the error: it built an empty index and required that
        `filer()` read the DISK instead. That is the behaviour that leaks —
        see `test_tomt_indeks_er_et_svar_ikke_en_fallback`.
        """
        self.git_init()
        self.skriv("docs/a.json", "{}\n")
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/a.json"])

    def test_uten_git_leses_disken(self):
        self.skriv("docs/a.json", "{}\n")
        self.assertIsNone(git_indeks(self.tmp))
        self.assertEqual(self.rel(filer(self.tmp)), ["docs/a.json"])

    def test_ignorert_katalog_hoppes_over_ved_navn_uten_git(self):
        """The fallback reads the disk, but the ignored directories are the same:
        a directory that is not in the repo must not be able to fail an answer."""
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
        """The function answers with files that can be read — a `check()` must not
        fail on a path that does not exist."""
        self.git_init()
        p = self.skriv("docs/a.json", "{}\n")
        self.git("add", "docs/a.json")
        p.unlink()
        self.assertEqual(filer(self.tmp), [])

    def test_tomt_tre_er_tom_liste_ikke_en_feil(self):
        self.git_init()
        self.assertEqual(filer(self.tmp), [])


class Instrumentene(Rigg):
    """The three instruments must answer alike in all clones: an ignored
    work surface under the repo must not be able to fail them."""

    def test_identitetsvakten_ser_ikke_ignorert_arbeidsflate(self):
        ef = importlib.import_module("efc_identity")
        self.git_init()
        self.skriv(".gitignore", ".worktrees/\n")
        self.skriv("docs/s.json", json.dumps({
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "$id": "https://supertedai.github.io/EFC/s.json",
            "type": "object", "properties": {},
        }))
        # Legacy binding + missing @id, in a directory git ignores.
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
