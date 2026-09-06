"""Tests for scripts/maintenance/efc_concepts.py — one SKOS source, generated views, nothing authored.

What must not rot: a concept without a doi.org source, a definition without a
source, a stale view, a dead copy that comes back, a concept the vocabulary
does not declare — each is a problem. And in the real tree every
skos:definition is a VERBATIM sentence from the file efc:definitionQuotedFrom
names (ADR-024: the registry copies, it does not write).
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_concepts.py"
GH = "https://github.com/supertedai/EFC/blob/main/"


def _load():
    spec = importlib.util.spec_from_file_location("efc_concepts", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_concepts"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


class Rigg(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self.tmp = Path(tempfile.mkdtemp())
        S = self.mod.SCHEME_IRI
        self.reg = {
            "@context": {"efc": self.mod.NS, "skos": "http://www.w3.org/2004/02/skos/core#", "dcterms": "http://purl.org/dc/terms/"},
            "@graph": [
                {"@id": S, "@type": "skos:ConceptScheme", "skos:hasTopConcept": [{"@id": "efc:A"}, {"@id": "efc:B"}]},
                {"@id": "efc:A", "@type": "skos:Concept", "skos:prefLabel": {"@value": "Alpha", "@language": "en"}, "skos:altLabel": [{"@value": "A", "@language": "en"}],
                 "skos:notation": "A", "skos:inScheme": {"@id": S}, "skos:topConceptOf": {"@id": S}, "skos:definition": {"@value": "Alpha is the first.", "@language": "en"},
                 "efc:definitionQuotedFrom": {"@id": GH + "README.md"}, "dcterms:source": [{"@id": "https://doi.org/10.6084/m9.figshare.1"}, {"@id": GH + "README.md"}]},
                {"@id": "efc:B", "@type": "skos:Concept", "skos:prefLabel": {"@value": "Beta", "@language": "en"}, "skos:altLabel": [],
                 "skos:notation": "B", "skos:inScheme": {"@id": S}, "skos:topConceptOf": {"@id": S}, "dcterms:source": [{"@id": "https://doi.org/10.6084/m9.figshare.2"}]},
            ],
        }
        _write(self.tmp / self.mod.REGISTRY, self.reg)
        _write(self.tmp / self.mod.ONTOLOGY, {"@graph": [{"@id": "efc:A"}, {"@id": "efc:B"}]})
        _write(self.tmp / "figshare" / "doi-map.json", {"papers": [{"doi": "10.6084/m9.figshare.1"}, {"doi": "10.6084/m9.figshare.2"}]})
        (self.tmp / "README.md").write_text("Alpha is the first.\n", encoding="utf-8")
        self.mod.apply(self.tmp)

    def _save(self):
        _write(self.tmp / self.mod.REGISTRY, self.reg)

    def test_groent_etter_apply(self):
        self.assertEqual(self.mod.check(self.tmp), [])
        view = json.loads((self.tmp / self.mod.VIEW_TERMSET).read_text(encoding="utf-8"))
        a = view["hasDefinedTerm"][0]
        self.assertEqual(a["termCode"], "A")
        self.assertEqual(a["inDefinedTermSet"], self.mod.SCHEME_IRI)
        self.assertEqual(a["citation"], ["https://doi.org/10.6084/m9.figshare.1"])
        self.assertEqual(a["url"], self.mod.NS + "A")
        idx = json.loads((self.tmp / self.mod.VIEW_INDEX).read_text(encoding="utf-8"))
        self.assertEqual([i["item"]["url"] for i in idx["itemListElement"]], [self.mod.NS + "A", self.mod.NS + "B"])

    def test_begrep_uten_doi_kilde_er_et_problem(self):
        self.reg["@graph"][2]["dcterms:source"] = [{"@id": GH + "README.md"}]
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("efc:B: no dcterms:source that is a doi.org URL" in p for p in self.mod.check(self.tmp)))

    def test_definisjon_uten_kilde_er_et_problem(self):
        self.reg["@graph"][2]["skos:definition"] = {"@value": "Beta is second.", "@language": "en"}
        self.reg["@graph"][2]["dcterms:source"] = []
        self._save(); self.mod.apply(self.tmp)
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("efc:B: no dcterms:source that is a doi.org URL" in p for p in problems), problems)
        self.assertTrue(any("efc:B: a skos:definition must name exactly one efc:definitionQuotedFrom" in p for p in problems), problems)

    def test_foreldet_visning_og_doed_kopi_og_udeklarert_begrep(self):
        (self.tmp / self.mod.VIEW_TERMSET).write_text("{}\n", encoding="utf-8")
        _write(self.tmp / self.mod.DEAD[0], {"old": True})
        _write(self.tmp / self.mod.ONTOLOGY, {"@graph": [{"@id": "efc:A"}]})
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("schema/concepts.json is stale" in p for p in problems), problems)
        self.assertTrue(any("dead copy still present" in p for p in problems), problems)
        self.assertTrue(any("efc:B is not declared" in p for p in problems), problems)

    def test_definisjon_som_ikke_er_ordrett_eller_mangler_quotedFrom_er_et_problem(self):
        """ADR-024-vernet i PORTEN: en parafrasert eller forfattet definisjon feller."""
        (self.tmp / "README.md").write_text("Alpha is the first.\n", encoding="utf-8")
        _write(self.tmp / "figshare" / "doi-map.json", {"papers": [{"doi": "10.6084/m9.figshare.1"}, {"doi": "10.6084/m9.figshare.2"}]})
        self.mod.apply(self.tmp)
        self.assertEqual(self.mod.check(self.tmp), [])
        self.reg["@graph"][1]["skos:definition"] = {"@value": "Alpha is the very first.", "@language": "en"}
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("not a verbatim substring of README.md (ADR-024)" in p for p in self.mod.check(self.tmp)))
        self.reg["@graph"][1]["skos:definition"] = {"@value": "Alpha is the first.", "@language": "en"}
        del self.reg["@graph"][1]["efc:definitionQuotedFrom"]
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("must name exactly one efc:definitionQuotedFrom" in p for p in self.mod.check(self.tmp)))

    def test_oppdiktet_doi_og_toppbegrep_med_broader_og_duplikat_er_problemer(self):
        _write(self.tmp / "figshare" / "doi-map.json", {"papers": [{"doi": "10.6084/m9.figshare.1"}]})
        (self.tmp / "README.md").write_text("Alpha is the first.\n", encoding="utf-8")
        self.reg["@graph"][2]["skos:broader"] = {"@id": "efc:A"}
        self.reg["@graph"][2]["skos:topConceptOf"] = {"@id": self.mod.SCHEME_IRI}
        self.reg["@graph"].append(dict(self.reg["@graph"][2]))
        self._save(); self.mod.apply(self.tmp)
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("efc:B: dcterms:source https://doi.org/10.6084/m9.figshare.2 is not a DOI the tree records" in p for p in problems), problems)
        self.assertTrue(any("efc:B: has skos:broader and is skos:topConceptOf" in p for p in problems), problems)
        self.assertTrue(any("duplicate @id 'efc:B'" in p for p in problems), problems)
        self.assertTrue(any("skos:hasTopConcept must list exactly" in p for p in problems), problems)

    def test_traversering_tom_definisjon_og_skjemanode_med_concept_egenskaper(self):
        (self.tmp.parent / "utenfor-treet.md").write_text("Alpha is the first.\n", encoding="utf-8")
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "../utenfor-treet.md"}
        self.reg["@graph"][0]["skos:topConceptOf"] = {"@id": self.mod.SCHEME_IRI}
        self._save(); self.mod.apply(self.tmp)
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("resolves outside the tree" in p for p in problems), problems)
        self.assertTrue(any("skos:topConceptOf on a node that is not a skos:Concept" in p for p in problems), problems)
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "README.md"}
        self.reg["@graph"][1]["skos:definition"] = {"@value": "", "@language": "en"}
        del self.reg["@graph"][0]["skos:topConceptOf"]
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("skos:definition is empty" in p for p in self.mod.check(self.tmp)))

    def test_sitert_doi_er_ikke_publisert(self):
        _write(self.tmp / "docs" / "papers" / "efc" / "p" / "index.json", {"doi": "10.6084/m9.figshare.1", "references": ["10.1007/978-3-662-05328-7"]})
        self.assertEqual(self.mod.known_dois(self.tmp), {"10.6084/m9.figshare.1", "10.6084/m9.figshare.2"})

    def test_begrep_utenfor_namespacet_er_et_problem(self):
        self.reg["@graph"][2]["@id"] = "https://example.org/B"
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("is not in the efc: namespace" in p for p in self.mod.check(self.tmp)))


class Repoet(unittest.TestCase):
    def test_registeret_er_groent_og_sitatene_er_ordrette(self):
        mod = _load()
        self.assertEqual(mod.check(), [])
        reg = json.loads((ROOT / mod.REGISTRY).read_text(encoding="utf-8"))
        cs = mod.concepts(reg)
        self.assertEqual(sorted(c["@id"] for c in cs), ["efc:EFC", "efc:EntropyGradient", "efc:GHF", "efc:HME", "efc:IMX"])
        for c in cs:
            if "skos:definition" in c:
                src = c["efc:definitionQuotedFrom"]["@id"]
                self.assertTrue(src.startswith(GH), src)
                text = (ROOT / src[len(GH):]).read_text(encoding="utf-8")
                self.assertIn(c["skos:definition"]["@value"], text, f"{c['@id']}: definition is not verbatim from {src}")
            else:
                self.assertIn("skos:scopeNote", c, f"{c['@id']}: neither a sourced definition nor a scopeNote saying why")


if __name__ == "__main__":
    unittest.main()
