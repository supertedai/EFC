"""Tests for scripts/maintenance/efc_concepts.py — one SKOS source, generated views, nothing authored.

What must not rot: a concept without a doi.org source, a definition without a
source, a stale view, a dead copy that comes back, a concept the vocabulary
does not declare — each is a problem. And in the real tree every
skos:definition is a VERBATIM sentence from the file efc:definitionQuotedFrom
names (ADR-024: the registry copies, it does not write).
"""
from __future__ import annotations

import importlib.util
import hashlib
import json
import re
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
                 "skos:notation": "A", "efc:entityType": "concept", "skos:inScheme": {"@id": S}, "skos:topConceptOf": {"@id": S}, "skos:definition": {"@value": "Alpha is the first.", "@language": "en"},
                 "efc:definitionQuotedFrom": {"@id": GH + "README.md#L1"}, "dcterms:source": [{"@id": "https://doi.org/10.6084/m9.figshare.1"}, {"@id": GH + "README.md#L1"}]},
                {"@id": "efc:B", "@type": "skos:Concept", "skos:prefLabel": {"@value": "Beta", "@language": "en"}, "skos:altLabel": [],
                 "skos:notation": "B", "efc:entityType": "concept", "skos:inScheme": {"@id": S}, "skos:topConceptOf": {"@id": S},
                 "skos:scopeNote": {"@value": "no defining sentence in the tree (measured)", "@language": "en"}, "dcterms:source": [{"@id": "https://doi.org/10.6084/m9.figshare.2"}]},
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
        self.reg["@graph"][2]["dcterms:source"] = [{"@id": GH + "README.md#L1"}]
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

    def test_fragmentanker_kreves_og_maa_peke_paa_riktige_linjer(self):
        """t_91579b0e: «delstreng hvor som helst i fila» er ikke evidens i en
        fil paa tusenvis av linjer. Ankeret er en GitHub-lenke, saa
        identifikatoren er den klikkbare evidensen."""
        (self.tmp / "README.md").write_text("intro\nAlpha is the first.\ntail\n", encoding="utf-8")
        q = self.reg["@graph"][1]["skos:definition"]["@value"]
        for anker, ventet in ((GH + "README.md", "needs a line fragment"), (GH + "README.md#L1", "lines 1-1"), (GH + "README.md#L99", "but README.md has")):
            self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": anker}
            self._save(); self.mod.apply(self.tmp)
            problems = self.mod.check(self.tmp)
            self.assertTrue(any(ventet in p for p in problems), (anker, problems))
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "README.md#L2", "efc:quoteSha256": "0" * 64}
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("efc:quoteSha256 does not match" in p for p in self.mod.check(self.tmp)))
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "README.md#L1-L3", "efc:quoteSha256": hashlib.sha256(q.encode("utf-8")).hexdigest()}
        self._save(); self.mod.apply(self.tmp)
        self.assertEqual(self.mod.check(self.tmp), [], "a wider span that still contains the quote is legitimate")
        for anker, ventet in ((GH + "README.md#L0", "lines are numbered from 1"),
                              (GH + "README.md#L3-L2", "runs backwards"),
                              (GH + "README.md#L99", "but README.md has 3"),
                              (GH + "README.md#Loverview", "needs a line fragment"),
                              (GH + "README.md", "needs a line fragment"),
                              (GH + "READ%00ME.md#L1", "is not a readable file in the tree")):
            self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": anker}
            self._save(); self.mod.apply(self.tmp)
            self.assertTrue(any(ventet in p for p in self.mod.check(self.tmp)), (anker, self.mod.check(self.tmp)))
        # A one-element LIST is the same statement as a bare node: a JSON-LD
        # expand/compact round makes every value a list, and the hash check
        # must not fall off that edge (review finding).
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = [{"@id": GH + "README.md#L2", "efc:quoteSha256": "0" * 64}]
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("efc:quoteSha256 does not match" in p for p in self.mod.check(self.tmp)), self.mod.check(self.tmp))
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = [{"@id": GH + "README.md#L2", "efc:quoteSha256": hashlib.sha256(q.encode("utf-8")).hexdigest()}]
        self._save(); self.mod.apply(self.tmp)
        self.assertEqual(self.mod.check(self.tmp), [], "a one-element list is the same statement")

    def test_manglende_definisjon_krever_scopenote(self):
        c = self.reg["@graph"][2]
        self.assertNotIn("skos:definition", c)
        for tom in (None, "", "   "):
            if tom is None:
                c.pop("skos:scopeNote", None)
            else:
                c["skos:scopeNote"] = {"@value": tom, "@language": "en"}
            self._save(); self.mod.apply(self.tmp)
            self.assertTrue(any("no skos:definition and no skos:scopeNote" in p for p in self.mod.check(self.tmp)), repr(tom))
        c.pop("skos:scopeNote", None)
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("no skos:definition and no skos:scopeNote" in p for p in self.mod.check(self.tmp)))
        c["skos:scopeNote"] = {"@value": "no defining sentence in the tree (measured)", "@language": "en"}
        self._save(); self.mod.apply(self.tmp)
        self.assertEqual(self.mod.check(self.tmp), [])

    def test_definisjon_som_ikke_er_ordrett_eller_mangler_quotedFrom_er_et_problem(self):
        """ADR-024-vernet i PORTEN: en parafrasert eller forfattet definisjon feller."""
        (self.tmp / "README.md").write_text("Alpha is the first.\n", encoding="utf-8")
        _write(self.tmp / "figshare" / "doi-map.json", {"papers": [{"doi": "10.6084/m9.figshare.1"}, {"doi": "10.6084/m9.figshare.2"}]})
        self.mod.apply(self.tmp)
        self.assertEqual(self.mod.check(self.tmp), [])
        self.reg["@graph"][1]["skos:definition"] = {"@value": "Alpha is the very first.", "@language": "en"}
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("not a verbatim substring of README.md lines 1-1" in p for p in self.mod.check(self.tmp)))
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
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "../utenfor-treet.md#L1"}
        self.reg["@graph"][0]["skos:topConceptOf"] = {"@id": self.mod.SCHEME_IRI}
        self._save(); self.mod.apply(self.tmp)
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("resolves outside the tree" in p for p in problems), problems)
        self.assertTrue(any("skos:topConceptOf on a node that is not a skos:Concept" in p for p in problems), problems)
        self.reg["@graph"][1]["efc:definitionQuotedFrom"] = {"@id": GH + "README.md#L1"}
        self.reg["@graph"][1]["skos:definition"] = {"@value": "", "@language": "en"}
        del self.reg["@graph"][0]["skos:topConceptOf"]
        self._save(); self.mod.apply(self.tmp)
        self.assertTrue(any("skos:definition is empty" in p for p in self.mod.check(self.tmp)))

    def test_sitert_doi_er_ikke_publisert(self):
        _write(self.tmp / "docs" / "papers" / "efc" / "p" / "index.json", {"doi": "10.6084/m9.figshare.1", "references": ["10.1007/978-3-662-05328-7"]})
        self.assertEqual(self.mod.known_dois(self.tmp), {"10.6084/m9.figshare.1", "10.6084/m9.figshare.2"})

    def test_entitytype_er_paakrevd_lukket_og_ikke_begreper_faar_egen_melding(self):
        for verdi, ventet, alene in ((None, "no efc:entityType", False), ("publication", "is not a concept and cannot be registered here", True),
                                     ("dataset", "cannot be registered here", True), ("person", "cannot be registered here", True),
                                     ("artifact", "cannot be registered here", True), ("organization", "cannot be registered here", True),
                                     ("tullball", "is not in the closed list", False)):
            if verdi is None:
                self.reg["@graph"][1].pop("efc:entityType", None)
            else:
                self.reg["@graph"][1]["efc:entityType"] = verdi
            self._save(); self.mod.apply(self.tmp)
            problems = [p for p in self.mod.check(self.tmp) if "efc:A" in p]
            self.assertTrue(any(ventet in p for p in problems), (verdi, problems))
            if alene:
                self.assertEqual(len(problems), 1, f"a non-concept gets its own message and nothing else: {problems}")
        for verdi in ("concept", "method", "measurement_principle", "regime"):
            self.reg["@graph"][1]["efc:entityType"] = verdi
            self._save(); self.mod.apply(self.tmp)
            self.assertEqual(self.mod.check(self.tmp), [], verdi)
        self.reg["@graph"][1]["efc:entityType"] = "concept"

    def test_visningen_baerer_type_og_definisjonsstatus(self):
        self.mod.apply(self.tmp)
        view = json.loads((self.tmp / self.mod.VIEW_TERMSET).read_text(encoding="utf-8"))
        prop = {p["name"]: p["value"] for p in view["hasDefinedTerm"][0]["additionalProperty"]}
        self.assertEqual(prop, {"entityType": "concept", "definition_status": "explicit"})
        self.assertNotIn("definition_status", json.dumps(self.reg), "a computable fact is not stored")
        b = {p["name"]: p["value"] for p in view["hasDefinedTerm"][1]["additionalProperty"]}
        self.assertEqual(b["definition_status"], "gap")

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
                m = re.match(r"^([^#]+)#L(\d+)(?:-L(\d+))?$", src[len(GH):])
                self.assertIsNotNone(m, f"{c['@id']}: efc:definitionQuotedFrom needs a #L line fragment: {src}")
                lines = (ROOT / m.group(1)).read_text(encoding="utf-8").split("\n")
                start, end = int(m.group(2)), int(m.group(3) or m.group(2))
                self.assertIn(c["skos:definition"]["@value"], "\n".join(lines[start - 1:end]),
                              f"{c['@id']}: definition is not verbatim from {m.group(1)} lines {start}-{end}")
                digest = c["efc:definitionQuotedFrom"].get("efc:quoteSha256")
                if digest:
                    self.assertEqual(digest, hashlib.sha256(c["skos:definition"]["@value"].encode("utf-8")).hexdigest(), c["@id"])
            else:
                self.assertIn("skos:scopeNote", c, f"{c['@id']}: neither a sourced definition nor a scopeNote saying why")


if __name__ == "__main__":
    unittest.main()
