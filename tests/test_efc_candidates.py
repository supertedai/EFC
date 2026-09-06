"""Tests for scripts/maintenance/efc_candidates.py — it reads, it never chooses.

What must not rot: a form list that a null can be trusted against, whole-word
matching, a source that NAMES the term rather than sitting near one, ranking
that prefers a defining sentence, and a draft that leaves every judgement
open. And the tool must never write the registry.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_candidates.py"


def _load():
    spec = importlib.util.spec_from_file_location("efc_candidates", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_candidates"] = mod
    spec.loader.exec_module(mod)
    return mod


class Rigg(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)
        subprocess.run(["git", "init", "-q"], cwd=self.tmp, check=True)

    def w(self, rel, text):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        subprocess.run(["git", "add", "-f", rel], cwd=self.tmp, check=True)

    def _tre(self):
        self.w("docs/papers/efc/Alfa/README.md",
               "Introduces the Alpha Lock, a constraint that binds the grid.\nCLASS v3 is unrelated.\n")
        self.w("docs/papers/efc/Alfa/index.json", json.dumps({"doi": "10.6084/m9.figshare.1", "title": "Alpha Lock"}))
        self.w("docs/papers/efc/Beta/README.md", "This paper is about halos and says nothing else.\n")
        # Only a heading and a table row: no definition candidate, but the
        # paper still CARRIES the term (review finding, 82 lost sources).
        self.w("docs/papers/efc/Gamma/README.md", "# Alpha Lock\n| Alpha Lock | 3 |\n")
        self.w("docs/papers/efc/Gamma/index.json", json.dumps({"doi": "10.6084/m9.figshare.3"}))
        # A container directory that is a strict prefix of a child paper.
        self.w("docs/papers/efc/Delta/README.md", "Nothing here.\n")
        self.w("docs/papers/efc/Delta/index.json", json.dumps({"doi": "10.6084/m9.figshare.4"}))
        self.w("docs/papers/efc/Delta_part_1/README.md", "The Alpha Lock is used here.\n")
        self.w("docs/papers/efc/Delta_part_1/index.json", json.dumps({"doi": "10.6084/m9.figshare.5"}))
        self.w("docs/papers/efc/Beta/index.json", json.dumps({"doi": "10.6084/m9.figshare.2", "title": "Beta"}))
        self.w("notes/bruk.md", "We used the Alpha Lock in the run.\n")
        self.w("figshare/doi-map.json", json.dumps({"papers": [
            {"doi": "10.6084/m9.figshare.1", "repo_dir": "docs/papers/efc/Alfa"},
            {"doi": "10.6084/m9.figshare.2", "repo_dir": "docs/papers/efc/Beta"},
            {"doi": "10.6084/m9.figshare.3", "repo_dir": "docs/papers/efc/Gamma"},
            {"doi": "10.6084/m9.figshare.4", "repo_dir": "docs/papers/efc/Delta"},
            {"doi": "10.6084/m9.figshare.5", "repo_dir": "docs/papers/efc/Delta_part_1"}]}))
        self.w("docs/ontology.jsonld", json.dumps({"@graph": [{"@id": "efc:AlphaLock"}]}))
        self.w("docs/concepts.jsonld", json.dumps({"@graph": [{"@id": "efc:EFC", "@type": "skos:Concept"}]}))

    def test_former_daekker_engelsk_typografi_og_akronym(self):
        f = self.mod.forms("Grid–Higgs Framework")
        for venter in ("Grid–Higgs Framework", "Grid-Higgs Framework", "GHF", "Grid–Higgs_Framework"):
            self.assertIn(venter, f, venter)
        self.assertNotIn("CL", self.mod.forms("Core Lock"), "a two-letter acronym matched CLASS (measured)")
        self.assertIn("proxies", self.mod.forms("proxy"))

    def test_helord_ikke_delstreng(self):
        self.assertTrue(self.mod.whole_word("CL", "the CL value"))
        self.assertFalse(self.mod.whole_word("CL", "CLASS v3.2.0"))
        self.assertFalse(self.mod.whole_word("S0", "S01 is different"))
        self.assertTrue(self.mod.whole_word("Alpha Lock", "the Alpha Lock, a constraint"))
        self.assertFalse(self.mod.whole_word("lock", "blålock er ikke en lås"),
                         "the boundary is \\w, so a Norwegian note does not produce a hit")
        self.assertFalse(self.mod.whole_word("sol", "solår"))

    def test_en_feilet_git_er_en_feil_ikke_en_dom(self):
        """Review: a failing `git ls-files` produced an empty file list, and
        every term came back NOT IN TREE — a search reported as an absence,
        over the whole tree at once."""
        tom = Path(tempfile.mkdtemp())
        self.addCleanup(lambda: __import__("shutil").rmtree(tom, ignore_errors=True))
        with self.assertRaises(self.mod.NotAGitTree):
            self.mod.draft(tom, "Alpha Lock")
        subprocess.run(["git", "init", "-q"], cwd=tom, check=True)
        with self.assertRaises(self.mod.NotAGitTree):
            self.mod.draft(tom, "Alpha Lock")   # a git tree with no text files

    def test_totaler_og_grenser_vises(self):
        self._tre()
        d = self.mod.draft(self.tmp, "Alpha Lock", limit=1)
        self.assertEqual(len(d["definition_candidates"]), 1)
        self.assertGreater(d["definition_candidates_total"], 1)
        self.assertIn("of %d shown" % d["definition_candidates_total"], self.mod.render(d))
        alle = self.mod.draft(self.tmp, "Alpha Lock", limit=0)
        self.assertEqual(len(alle["definition_candidates"]), alle["definition_candidates_total"])

    def test_limit_naar_ogsaa_menneskemodus(self):
        """Review runde 2: --all og --limit naadde bare --json, mens
        utskriften skrev «--all for the rest» paa hver kjoering."""
        self._tre()
        d = self.mod.draft(self.tmp, "Alpha Lock", limit=0)
        smal = self.mod.render(d, limit=1)
        bred = self.mod.render(d, limit=0)
        self.assertNotEqual(smal, bred, "--all must change what a person sees, not only the JSON")
        self.assertIn("shown; --all for the rest", smal)
        self.assertNotIn("shown; --all for the rest", bred, "no dead pointer when everything is shown")
        self.assertEqual(bred.count("candidate "), d["definition_candidates_total"])

    def test_verktoeyets_egen_dokumentasjon_er_ikke_en_kilde(self):
        self.w("scripts/maintenance/README.md", "The Alpha Lock is a worked example in this tool's own docs.\n")
        self._tre()
        d = self.mod.draft(self.tmp, "Alpha Lock")
        self.assertFalse(any("scripts/maintenance/README.md" in c["anchor"] for c in d["definition_candidates"]),
                         "a tool must not cite itself as a source about the thing it reports on")

    def test_tie_break_er_kasus_ufoelsom_paa_stien(self):
        """Review runde 3: en sti er ikke prosa. Kasus-sensitiv matching ga
        bonusen til RCMP og L0 men ikke til `regime` i
        EFC-Regime-Transition-Framework, som da tapte definisjonen sin til et
        retorisk spørsmål."""
        self.assertGreater(self.mod.score("The alpha lock is a constraint on the grid layer.", "alpha lock",
                                          "docs/papers/efc/Alpha-Lock/README.md", "alpha lock"),
                           self.mod.score("The alpha lock is a constraint on the grid layer.", "alpha lock",
                                          "docs/papers/efc/Other-Paper/README.md", "alpha lock"))

    def test_cli_koder(self):
        self.assertEqual(self.mod.main(["--help"]), 0)
        self.assertEqual(self.mod.main(["--tullball"]), 2)
        self.assertEqual(self.mod.main(["--limit", "x"]), 2)

    def test_utkastet_navngir_kilder_som_baerer_termen_ikke_naboer(self):
        self._tre()
        d = self.mod.draft(self.tmp, "Alpha Lock")
        self.assertTrue(d["in_tree"])
        papers = [s["paper"] for s in d["sources_naming_the_term"]]
        self.assertNotIn("docs/papers/efc/Beta", papers,
                         "Beta is about halos and never says the term — proximity is not a source (the efc:HME lesson)")
        self.assertIn("docs/papers/efc/Alfa", papers)
        self.assertIn("docs/papers/efc/Gamma", papers,
                      "a term that appears only in a heading or a table still means the paper carries it")
        self.assertIn("docs/papers/efc/Delta_part_1", papers)
        self.assertNotIn("docs/papers/efc/Delta", papers,
                         "a container directory must not be credited with its child paper's term")
        self.assertEqual(d["sources_total"], len(d["sources_naming_the_term"]))
        self.assertTrue(d["already_declared_in_vocabulary"], "efc:AlphaLock is in the vocabulary")
        self.assertFalse(d["already_registered"])

    def test_rangeringen_foretrekker_en_definerende_setning(self):
        self._tre()
        d = self.mod.draft(self.tmp, "Alpha Lock")
        toppen = d["definition_candidates"][0]
        self.assertIn("Introduces the Alpha Lock", toppen["sentence"])
        self.assertRegex(toppen["anchor"], r"#L\d+$")
        self.assertGreater(toppen["score"], d["definition_candidates"][-1]["score"])

    def test_ikke_i_treet_baerer_formene_som_ble_proevd(self):
        self._tre()
        d = self.mod.draft(self.tmp, "metaspeil")
        self.assertFalse(d["in_tree"])
        self.assertEqual(d["forms_found"], {})
        self.assertIn("metaspeil", d["forms_searched"])
        self.assertIn("NOT IN TREE", self.mod.render(d))
        self.assertIn("inventing EFC vocabulary", self.mod.render(d))

    def test_doemmekraften_staar_aapen_og_registeret_roeres_ikke(self):
        self._tre()
        foer = (self.tmp / "docs/concepts.jsonld").read_bytes()
        d = self.mod.draft(self.tmp, "Alpha Lock")
        self.assertEqual((self.tmp / "docs/concepts.jsonld").read_bytes(), foer, "the tool never writes the registry")
        self.assertEqual(len(d["open_decisions"]), 4)
        for felt in ("skos:definition", "efc:entityType", "efc:registryStatus", "skos:broader"):
            self.assertTrue(any(x.startswith(felt) for x in d["open_decisions"]), felt)
        self.assertNotIn("skos:definition", {k: v for k, v in d.items() if k != "open_decisions"})
        self.assertIn("suggested_id_not_a_decision", d, "the IRI is a suggestion, not a decision")
        src = SCRIPT.read_text(encoding="utf-8")
        self.assertNotIn("REGISTRY).write_text", src)
        self.assertNotIn('open(root / REGISTRY, "w"', src)

    def test_deterministisk(self):
        self._tre()
        self.assertEqual(self.mod.draft(self.tmp, "Alpha Lock"), self.mod.draft(self.tmp, "Alpha Lock"))


class Repoet(unittest.TestCase):
    def test_verktoeyet_kjoerer_paa_det_ekte_treet(self):
        mod = _load()
        try:
            d = mod.draft(ROOT, "RCMP")
        except mod.NotAGitTree:
            # The tool reads `git ls-files`, so this test needs git metadata.
            # A `git archive` export has none, and that is the export used to
            # verify a commit — skipping here is honest, and the rig above
            # covers the behaviour without git.
            self.skipTest("not a git checkout — the tool refuses to report an absence it cannot measure")
        self.assertTrue(d["in_tree"])
        self.assertTrue(d["already_declared_in_vocabulary"], "efc:RCMP is a declared term")
        self.assertFalse(d["already_registered"], "and it is not registered — that is the point of the card")
        self.assertTrue(d["sources_naming_the_term"])


if __name__ == "__main__":
    unittest.main()
