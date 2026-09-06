"""Tests for scripts/maintenance/efc_identity.py — one $id authority (served form), one dialect, @id on top.

What must not rot: the check names every class of deviation; the rewrite fixes
them textually without disturbing formatting (CRLF, indentation, comma
placement when the anchor is the last member); a paper's index.json with a
`definitions` LIST is not a schema; @graph documents are exempt; pointers must
reach a schema; identifiers are percent-encoded and use the served path; the
rewrite is idempotent; the robots write identity themselves; the real tree is
green.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
AUTH = "https://supertedai.github.io/EFC/"


def _load(name="efc_identity"):
    spec = importlib.util.spec_from_file_location(name, MAINT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


class Rigg(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def w(self, rel, text, nl="\n"):
        p = self.tmp / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(text.replace("\n", nl).encode("utf-8"))

    def _tre(self):
        self.w("docs/s.json", '{\n  "$schema": "http://json-schema.org/draft-07/schema#",\n  "id": "old-id",\n  "type": "object",\n  "properties": {\n    "id": {"type": "string"},\n    "x": {"$ref": "#/definitions/x"}\n  },\n  "definitions": {\n    "x": {"type": "integer"}\n  }\n}\n')
        self.w("schema/last.json", '{\n  "type": "object",\n  "properties": {},\n  "$schema": "https://json-schema.org/draft-07/schema#"\n}\n')
        self.w("docs/req_schema.json", '{\n  "required": ["a"]\n}\n')
        self.w("docs/paper/schema.json", '{\n  "properties": {"title": {"type": "string"}},\n  "required": ["title"]\n}\n')
        self.w("docs/paper/index.json", '{\n  "$schema": "./schema.json",\n  "id": "paper-1",\n  "title": "T",\n  "definitions": [\n    {"id": "D1", "text": "Geometry as boundary condition"}\n  ]\n}\n')
        self.w("docs/notschema/schema.json", '{\n  "name": "x",\n  "slug": "x"\n}\n')
        self.w("docs/notschema/index.json", '{\n  "$schema": "./schema.json",\n  "id": "n"\n}\n')
        self.w("docs/d.jsonld", '{\n  "@context": "https://schema.org",\n  "@type": "ScholarlyArticle",\n  "identifier": "https://doi.org/10.6084/m9.figshare.123"\n}\n', nl="\r\n")
        self.w("meta/e.jsonld", '{\n  "@context": "https://schema.org",\n  "@type": "CreativeWork",\n  "name": "e"\n}\n')
        self.w("docs/g.jsonld", '{\n  "@context": {"efc": "%s"},\n  "@graph": [{"@id": "efc:A"}]\n}\n' % "https://supertedai.github.io/EFC/ontology#")
        self.w("docs/A B/Λ.jsonld", '{\n  "@context": "https://schema.org",\n  "@type": "CreativeWork"\n}\n')
        self.w("docs/drift.jsonld", '{\n  "@context": "https://schema.org",\n  "@id": "%sdocs/drift.jsonld",\n  "@type": "CreativeWork"\n}\n' % AUTH)
        self.w("docs/foreign.jsonld", '{\n  "@context": "https://schema.org",\n  "@id": "https://energyflow-cosmology.com/",\n  "@type": "WebSite"\n}\n')
        self.w("docs/inst.json", '{\n  "$schema": "kill_test_v6_universality",\n  "metadata": {}\n}\n')
        self.w("docs/only.json", '{\n  "metadata": {},\n  "$schema": "kill_test_v6_universality_curves"\n}\n')
        self.w("docs/ok.json", '{\n  "$schema": "./s.json",\n  "id": "z",\n  "x": 1\n}\n')
        self.w("codemeta.json", '{\n  "@context": "https://doi.org/10.5063/schema/codemeta-2.0",\n  "@type": "SoftwareSourceCode",\n  "contIntegration": false\n}\n')
        self.w("CITATION.cff", "cff-version: 1.2.0\ntype: dataset\ntitle: x\n")

    def test_check_navngir_hver_klasse_av_avvik_og_ikke_de_andre(self):
        self._tre()
        problems = self.mod.check(self.tmp)
        for needle in ("docs/s.json: $schema is", "docs/s.json: $id is None, expected " + AUTH + "s.json", "docs/s.json: draft-07 `definitions`", "docs/s.json: draft-04 top-level `id`",
                       "schema/last.json: $id is None, expected " + AUTH + "schema/last.json", "docs/req_schema.json: $schema is", "docs/paper/schema.json: $id is None",
                       "docs/d.jsonld: no top-level @id", "meta/e.jsonld: no top-level @id", "docs/A B/Λ.jsonld: no top-level @id",
                       "docs/drift.jsonld: @id " + AUTH + "docs/drift.jsonld is under the authority but is not the served identifier " + AUTH + "drift.jsonld",
                       "docs/inst.json: \"$schema\": 'kill_test_v6_universality' does not resolve to a schema", "docs/only.json:", "docs/notschema/index.json: \"$schema\": './schema.json' does not resolve to a schema",
                       "codemeta.json: @context is", "codemeta.json: 2.0 property `contIntegration`"):
            self.assertTrue(any(needle in p for p in problems), (needle, problems))
        for absent in ("docs/paper/index.json", "docs/ok.json", "docs/g.jsonld", "docs/foreign.jsonld", "CITATION.cff", "docs/notschema/schema.json"):
            self.assertFalse(any(absent in p for p in problems), (absent, problems))

    def test_rewrite_retter_alt_bevarer_form_og_er_idempotent(self):
        self._tre()
        changed = self.mod.rewrite(self.tmp)
        self.assertEqual(sorted(changed), sorted(["codemeta.json", "docs/d.jsonld", "docs/inst.json", "docs/only.json", "docs/s.json", "meta/e.jsonld", "schema/last.json",
                                                  "docs/req_schema.json", "docs/paper/schema.json", "docs/notschema/index.json", "docs/A B/Λ.jsonld", "docs/drift.jsonld"]))
        notes = []
        self.assertEqual(self.mod.check(self.tmp, notes=notes), [])
        self.assertTrue(notes[0].startswith("2 identifier(s) under"), notes)      # schema/last.json + meta/e.jsonld
        self.assertTrue(notes[1].startswith("1 @graph document(s)"), notes)
        self.assertIn("docs/notschema/schema.json", notes[2])
        self.assertIn("DISAGREE", notes[4])
        s = json.loads((self.tmp / "docs/s.json").read_text(encoding="utf-8"))
        self.assertEqual((s["$schema"], s["$id"]), (self.mod.DIALECT, AUTH + "s.json"))
        self.assertNotIn("id", s)
        self.assertIn("id", s["properties"], "a property NAMED id is a name, not the draft-04 keyword")
        self.assertEqual(s["properties"]["x"]["$ref"], "#/$defs/x")
        last = (self.tmp / "schema/last.json").read_text(encoding="utf-8")
        self.assertIn('"$schema": "https://json-schema.org/draft/2020-12/schema",\n  "$id": "https://supertedai.github.io/EFC/schema/last.json"\n}', last)
        paper = json.loads((self.tmp / "docs/paper/index.json").read_text(encoding="utf-8"))
        self.assertEqual(paper["id"], "paper-1", "a paper's index.json is not a schema: its id and definitions survive")
        self.assertEqual(paper["$schema"], "./schema.json")
        self.assertEqual(json.loads((self.tmp / "docs/paper/schema.json").read_text(encoding="utf-8"))["$id"], AUTH + "paper/schema.json")
        self.assertNotIn("$schema", json.loads((self.tmp / "docs/notschema/index.json").read_text(encoding="utf-8")), "a pointer to a non-schema binds nothing")
        raw = (self.tmp / "docs/d.jsonld").read_bytes()
        self.assertIn(b"\r\n", raw)
        self.assertNotIn(b"\n  \"@type\"", raw.replace(b"\r\n", b"\x00"), "no bare LF introduced")
        self.assertEqual(json.loads(raw.decode("utf-8"))["@id"], "https://doi.org/10.6084/m9.figshare.123")
        self.assertEqual(json.loads((self.tmp / "meta/e.jsonld").read_text(encoding="utf-8"))["@id"], AUTH + "meta/e.jsonld")
        self.assertEqual(json.loads((self.tmp / "docs/A B/Λ.jsonld").read_text(encoding="utf-8"))["@id"], AUTH + "A%20B/%CE%9B.jsonld")
        self.assertEqual(json.loads((self.tmp / "docs/drift.jsonld").read_text(encoding="utf-8"))["@id"], AUTH + "drift.jsonld")
        self.assertNotIn("@id", json.loads((self.tmp / "docs/g.jsonld").read_text(encoding="utf-8")), "@graph documents are left alone")
        self.assertEqual(json.loads((self.tmp / "docs/foreign.jsonld").read_text(encoding="utf-8"))["@id"], "https://energyflow-cosmology.com/")
        self.assertEqual(json.loads((self.tmp / "docs/only.json").read_text(encoding="utf-8")), {"metadata": {}})
        cm = json.loads((self.tmp / "codemeta.json").read_text(encoding="utf-8"))
        self.assertEqual(cm["@context"], "https://w3id.org/codemeta/3.0")
        self.assertIn("continuousIntegration", cm)
        self.assertIn("type: dataset", (self.tmp / "CITATION.cff").read_text(encoding="utf-8"), "CITATION.cff is a human word, not rewritten")
        self.assertEqual(self.mod.rewrite(self.tmp), [], "second rewrite changes nothing")

    def test_docs_x_som_skygger_x_er_en_kollisjon(self):
        self.w("docs/meta/c.jsonld", '{\n  "@context": "https://schema.org",\n  "@type": "CreativeWork"\n}\n')
        self.w("meta/c.jsonld", '{\n  "@context": "https://schema.org",\n  "@type": "CreativeWork"\n}\n')
        self.mod.rewrite(self.tmp)
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("collides with" in p and "meta/c.jsonld" in p for p in problems), problems)


class Robotene(unittest.TestCase):
    def test_skjemamalen_beskriver_begge_robotenes_index_json_og_er_lukket(self):
        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed (CI gate C10 installs it)")
        gen = _load("efc_gen_ai_friendly")
        schema = gen.index_schema("T", "docs/papers/efc/A B/schema.json")
        self.assertEqual(schema["$id"], AUTH + "papers/efc/A%20B/schema.json")
        V = jsonschema.Draft202012Validator(schema)
        gen_shape = {"id": "x", "title": "T", "author": "Morten Magnusson", "orcid": "0", "affiliation": "S", "license": "CC-BY-4.0",
                     "track": "Spor 1", "regimes": [], "primary_pdf": None, "files": ["a.pdf"], "see_also": "ai_manifest.json"}
        auto_shape = {"$schema": "./schema.json", "id": "x", "title": "T", "description": "d", "version": "1.0", "date": "2026-01-01",
                      "keywords": ["k"], "author": {"name": "M", "orcid": "0", "affiliation": "S"}, "files": {"pdf": "a.pdf", "readme": "README.md"},
                      "doi": "10.6084/m9.figshare.1", "figshare_url": "https://doi.org/10.6084/m9.figshare.1"}
        self.assertEqual(list(V.iter_errors(gen_shape)), [])
        self.assertEqual(list(V.iter_errors(auto_shape)), [])
        self.assertTrue(list(V.iter_errors({**gen_shape, "synonym": 1})), "closed")

    def test_alle_tre_jsonld_skriverne_setter_id(self):
        auto = (MAINT / "efc_auto_metadata.py").read_text(encoding="utf-8")
        self.assertNotIn('f"doi:{doi}"', auto)
        self.assertIn('jsonld["@id"] = f"https://doi.org/{doi}"', auto)
        self.assertIn('jsonld["@id"] = served_id(', auto)
        gen = (MAINT / "efc_gen_ai_friendly.py").read_text(encoding="utf-8")
        self.assertIn('"@id": served_id(os.path.relpath(os.path.join(d, slug + ".jsonld")', gen)
        brain = (MAINT / "efc_ai_brain.py").read_text(encoding="utf-8")
        self.assertNotIn('f"doi:{doi}"', brain)
        self.assertIn('jsonld["@id"] = f"https://doi.org/{doi}"', brain)
        self.assertIn('jsonld["@id"] = _served_id(', brain)


class Repoet(unittest.TestCase):
    def test_treet_er_groent(self):
        mod = _load()
        notes = []
        self.assertEqual(mod.check(notes=notes), [])
        self.assertEqual(len(notes), 5)
        self.assertIn("CITATION.cff type", notes[4], "the CFF/codemeta state is reported on every check")


if __name__ == "__main__":
    unittest.main()
