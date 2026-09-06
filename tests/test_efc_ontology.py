"""Tests for scripts/maintenance/efc_ontology.py — one namespace, generated from use.

The three things that must not rot silently: the rewrite is TARGETED (a URL
elsewhere in a file, or prose like "EFC: a framework", survives), the check
FAILS on a legacy binding and on an undeclared term, and --apply is a
deterministic function of the tree so CI can diff the generated documents.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_ontology.py"


def _load():
    spec = importlib.util.spec_from_file_location("efc_ontology", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_ontology"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Rigg(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self.tmp = Path(tempfile.mkdtemp())
        self.mod.ROOT = self.tmp
        self.mod.OUT_JSONLD = self.tmp / "docs" / "ontology.jsonld"
        self.mod.OUT_HTML = self.tmp / "docs" / "ontology.html"
        self.NS = self.mod.NS

    def _tre(self):
        """Three documents: a legacy binding with a term, an EFC: prefixed one,
        and a plain schema.org document that must be left alone."""
        _write(self.tmp / "a" / "x.jsonld", {
            "@context": {"@vocab": "https://schema.org/", "efc": "https://energyflow-cosmology.com/ontology#"},
            "@type": "efc:EmpiricalResult",
            "efc:track": "efc:BetaConstraint",
            "url": "https://github.com/supertedai/EFC/tree/main/docs/papers/efc/x",
            "description": "EFC: a framework in which energy flows.",
        })
        _write(self.tmp / "b" / "y.jsonld", {
            "@context": ["https://schema.org", {"EFC": "https://energyflow-cosmology.com/schema#"}],
            "@type": "EFC:Node", "EFC:layer": "L1",
        })
        _write(self.tmp / "c" / "plain.jsonld", {"@context": "https://schema.org", "@type": "CreativeWork", "name": "z"})

    # ── inventar ──────────────────────────────────────────────────────
    def test_inventar_finner_bindinger_og_termer_etter_bruk(self):
        self._tre()
        per_file, agg, n, _ = self.mod.inventory(self.tmp)
        self.assertEqual(n, 3)
        self.assertEqual({p.name for p in per_file}, {"x.jsonld", "y.jsonld"})
        self.assertEqual(self.mod.classify(agg["EmpiricalResult"]), "rdfs:Class")
        self.assertEqual(self.mod.classify(agg["track"]), "rdf:Property")
        self.assertEqual(self.mod.classify(agg["BetaConstraint"]), "skos:Concept")
        self.assertEqual(self.mod.classify(agg["Node"]), "rdfs:Class")
        self.assertEqual(self.mod.classify(agg["layer"]), "rdf:Property")

    # ── rewrite ───────────────────────────────────────────────────────
    def test_rewrite_er_maalrettet_og_idempotent(self):
        self._tre()
        changed = self.mod.rewrite(self.tmp)
        self.assertEqual(sorted(changed), ["a/x.jsonld", "b/y.jsonld"])
        x = json.loads((self.tmp / "a" / "x.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(x["@context"]["efc"], self.NS)
        self.assertEqual(x["url"], "https://github.com/supertedai/EFC/tree/main/docs/papers/efc/x", "en URL utenfor @context skal ikke roeres")
        self.assertEqual(x["description"], "EFC: a framework in which energy flows.", "prosa med mellomrom etter kolon skal ikke roeres")
        y = json.loads((self.tmp / "b" / "y.jsonld").read_text(encoding="utf-8"))
        self.assertEqual(y["@context"][1], {"efc": self.NS})
        self.assertEqual(y["@type"], "efc:Node")
        self.assertIn("efc:layer", y)
        self.assertEqual(self.mod.rewrite(self.tmp), [], "andre kjoering skal ikke endre noe")

    # ── check ─────────────────────────────────────────────────────────
    def test_check_feiler_paa_legacy_binding_og_udeklarert_term(self):
        self._tre()
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("legacy binding" in p for p in problems), problems)
        self.assertTrue(any("missing or unreadable" in p for p in problems), problems)

    def test_apply_saa_check_er_groenn_og_deterministisk(self):
        self._tre()
        self.mod.rewrite(self.tmp)
        jl1, h1 = self.mod.generate(self.tmp)
        self.mod.OUT_JSONLD.parent.mkdir(parents=True)
        self.mod.OUT_JSONLD.write_text(jl1, encoding="utf-8")
        self.mod.OUT_HTML.write_text(h1, encoding="utf-8")
        self.assertEqual(self.mod.check(self.tmp), [])
        jl2, h2 = self.mod.generate(self.tmp)
        self.assertEqual((jl1, h1), (jl2, h2), "samme tre skal gi samme bytes")
        graph = json.loads(jl1)
        ids = {n["@id"] for n in graph["@graph"]}
        self.assertIn("efc:EmpiricalResult", ids)
        self.assertIn("efc:Node", ids)
        self.assertEqual(graph["@context"]["efc"], self.NS)
        self.assertIn('<script type="application/ld+json">', h1)

    def test_vocab_og_alias_bindes_som_termer_og_irregulaere_listes(self):
        """Reviewfunn: atlaset binder 47 noekler via @vocab og meta_universe fem
        via alias — ingen av dem har `efc:` i teksten. Og `efc:term/x` er en
        referanse, ikke et term: listes, deklareres ikke, feller ikke."""
        _write(self.tmp / "a" / "atlas.jsonld", {"@context": {"@vocab": self.NS}, "@type": "FrameworkAtlas",
                                                 "frameworks": [{"id": "x", "category": "baseline"}]})
        _write(self.tmp / "b" / "mu.jsonld", {"@context": {"efc": self.NS, "influences": "efc:influences",
                                                           "shapes": {"@id": "efc:shapes"}},
                                              "influences": "y", "shapes": "z", "identifier": "efc:term/co-field",
                                              "@id": "efc:Natural Entropy"})
        _, agg, _, irregular = self.mod.inventory(self.tmp)
        for name in ("FrameworkAtlas", "frameworks", "id", "category", "influences", "shapes"):
            self.assertIn(name, agg, name)
        self.assertEqual(self.mod.classify(agg["FrameworkAtlas"]), "rdfs:Class")
        self.assertEqual(sorted(x for _, x in irregular), ["efc:Natural Entropy", "efc:term/co-field"])
        jl, h = self.mod.generate(self.tmp)
        self.mod.OUT_JSONLD.parent.mkdir(parents=True, exist_ok=True)
        self.mod.OUT_JSONLD.write_text(jl, encoding="utf-8"); self.mod.OUT_HTML.write_text(h, encoding="utf-8")
        notes = []
        self.assertEqual(self.mod.check(self.tmp, notes=notes), [], "irregulaere skal ikke felle")
        self.assertEqual(len(notes), 2)

    def test_prefiks_uten_binding_er_et_problem(self):
        """`efc:Phantom` i et dokument som ikke binder `efc` er i JSON-LD en IRI
        med scheme efc — ikke et term i namespacet. Foerste runde absorberte
        det stille (reviewfunn)."""
        _write(self.tmp / "a" / "loose.jsonld", {"@context": "https://schema.org", "@type": "efc:Phantom", "efc:orphan": "efc:Ghost"})
        _write(self.tmp / "b" / "ok.jsonld", {"@context": {"efc": self.NS}, "@type": "efc:Real"})
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("loose.jsonld" in p and "without binding" in p for p in problems), problems)
        self.assertFalse(any("ok.jsonld" in p and "without binding" in p for p in problems), problems)

    def test_ugyldige_vocab_noekler_og_aliaser_listes(self):
        _write(self.tmp / "a" / "atlas.jsonld", {"@context": {"@vocab": self.NS, "sl": "efc:term/x"}, "ver.sion": 1, "9lead": 2, "fin": 3})
        _, agg, _, irregular = self.mod.inventory(self.tmp)
        self.assertIn("fin", agg)
        self.assertNotIn("ver.sion", agg)
        self.assertEqual(sorted(x for _, x in irregular), ["@context alias 'sl' -> efc:term/x", "@vocab key '9lead'", "@vocab key 'ver.sion'"])

    def test_rewrite_bevarer_crlf(self):
        """methodology/core/index.jsonld og open-process hadde CRLF paa main;
        foerste utgave normaliserte dem til LF (reviewfunn)."""
        p = self.tmp / "c" / "crlf.jsonld"
        p.parent.mkdir(parents=True)
        p.write_bytes(('{\r\n  "@context": {"efc": "https://energyflow-cosmology.com/ontology#"},\r\n'
                       '  "@type": "efc:Node"\r\n}\r\n').encode("utf-8"))
        self.assertEqual(self.mod.rewrite(self.tmp), ["c/crlf.jsonld"])
        raw = p.read_bytes()
        self.assertIn(b"\r\n", raw, "CRLF skal overleve")
        self.assertNotIn(b"\n  \"@type\"", raw.replace(b"\r\n", b"\x00"), "ingen naken LF er innfoert")
        self.assertIn(self.NS.encode(), raw)

    def test_check_feiler_naar_et_nytt_term_tas_i_bruk_uten_apply(self):
        self._tre()
        self.mod.rewrite(self.tmp)
        jl, h = self.mod.generate(self.tmp)
        self.mod.OUT_JSONLD.parent.mkdir(parents=True)
        self.mod.OUT_JSONLD.write_text(jl, encoding="utf-8")
        self.mod.OUT_HTML.write_text(h, encoding="utf-8")
        _write(self.tmp / "d" / "new.jsonld", {"@context": {"efc": self.NS}, "efc:brandNew": 1})
        problems = self.mod.check(self.tmp)
        self.assertTrue(any("efc:brandNew is used in the tree but not declared" in p for p in problems), problems)
        self.assertTrue(any("is stale" in p for p in problems), problems)


class Generatoren(unittest.TestCase):
    """efc_auto_metadata.py skrev `https://github.com/supertedai/EFC/ontology#`
    — en av de ni — og kjoeres av efc-main-sync med auto-commit (reviewfunn).
    Den importerer naa NS; her laases det at ingen legacy-URI finnes i kilden
    og at modulen faktisk baerer samme NS som efc_ontology."""

    def test_auto_metadata_baerer_ns_og_ingen_legacy_uri(self):
        mod = _load()
        src = (ROOT / "scripts" / "maintenance" / "efc_auto_metadata.py").read_text(encoding="utf-8")
        for legacy in mod.LEGACY:
            self.assertNotIn(legacy, src, legacy)
        spec = importlib.util.spec_from_file_location("efc_auto_metadata", ROOT / "scripts" / "maintenance" / "efc_auto_metadata.py")
        am = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(am)
        self.assertEqual(am.EFC_NS, mod.NS)

    def test_maintain_holder_vokabularet_ferskt(self):
        src = (ROOT / "scripts" / "maintenance" / "efc_maintain.py").read_text(encoding="utf-8")
        self.assertIn('run(ONTOLOGY, "--apply")', src)
        self.assertLess(src.index('run(ONTOLOGY, "--apply")'), src.index("rc_verify = run(VERIFY)"))


class Repoet(unittest.TestCase):
    """Mot det ekte treet: én binding, alt deklarert, dokumentene ferske."""

    def test_repoet_har_ett_namespace_og_ferske_dokumenter(self):
        mod = _load()
        self.assertEqual(mod.check(), [])


if __name__ == "__main__":
    unittest.main()
