"""Tests for scripts/maintenance/efc_schema_check.py — registered pairs valid and closed.

What must not rot: a violating instance is a problem (not a warning), an OPEN
object schema is a problem even when the instance validates (the whole point
of the gate is that an invented key fails), an invalid schema is named as
such, and the real tree is green.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_schema_check.py"


def _load():
    spec = importlib.util.spec_from_file_location("efc_schema_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_schema_check"] = mod
    spec.loader.exec_module(mod)
    return mod


def _write(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


CLOSED = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["version", "entries"],
    "properties": {
        "version": {"type": "string"},
        "entries": {"type": "array", "items": {"$ref": "#/definitions/entry"}},
    },
    "additionalProperties": False,
    "definitions": {
        "entry": {
            "type": "object",
            "properties": {"id": {"type": "string"}, "kind": {"enum": ["a", "b"]}},
            "required": ["id"],
            "additionalProperties": False,
        }
    },
}
GOOD = {"version": "1", "entries": [{"id": "x", "kind": "a"}]}


class Rigg(unittest.TestCase):
    def setUp(self):
        self.mod = _load()
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def _check(self, schema, inst, instanceless=()):
        _write(self.tmp / "s.json", schema)
        _write(self.tmp / "i.json", inst)
        for n, s in enumerate(instanceless):
            _write(self.tmp / f"x{n}.json", s)
        return self.mod.check(self.tmp, pairs=[("s.json", "i.json")], instanceless=[(f"x{n}.json", f"x{n}-data.json") for n in range(len(instanceless))])

    def test_groent_par_gir_ingen_problemer(self):
        self.assertEqual(self._check(CLOSED, GOOD), [])

    def test_oppfunnet_noekkel_feiler_fordi_skjemaet_er_lukket(self):
        bad = json.loads(json.dumps(GOOD))
        bad["entries"][0]["synonym"] = "invented"
        problems = self._check(CLOSED, bad)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("i.json: entries/0:", problems[0])
        self.assertIn("synonym", problems[0])

    def test_aapent_objektskjema_er_et_problem_selv_om_instansen_validerer(self):
        open_ = json.loads(json.dumps(CLOSED))
        del open_["definitions"]["entry"]["additionalProperties"]
        problems = self._check(open_, GOOD)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("/definitions/entry is open", problems[0])

    def test_ugyldig_skjema_navngis(self):
        broken = json.loads(json.dumps(CLOSED))
        broken["properties"]["version"] = {"type": "strnig"}
        problems = self._check(broken, GOOD)
        self.assertTrue(any("not a valid schema" in p for p in problems), problems)

    def test_instansloest_skjema_sjekkes_bare_mot_metaskjemaet(self):
        open_ = json.loads(json.dumps(CLOSED))
        del open_["additionalProperties"]
        broken = {"$schema": "http://json-schema.org/draft-07/schema#", "type": 7}
        problems = self._check(CLOSED, GOOD, instanceless=[open_, broken])
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("x1.json: not a valid schema", problems[0])

    def test_vandreren_ser_bar_type_object_tomt_skjema_og_typet_map_men_ikke_et_navn(self):
        """Reviewfunn runde 1: `{"type":"object"}`, `{}` og `additionalProperties: {schema}`
        slapp oppfunne noekler gjennom, mens et property som HETER `properties`
        ble flagget som skjema."""
        sch = json.loads(json.dumps(CLOSED))
        sch["properties"]["bare"] = {"type": "object"}
        sch["properties"]["anything"] = {}
        sch["properties"]["typed_map"] = {"type": "object", "additionalProperties": {"type": "integer"}}
        sch["properties"]["properties"] = {"type": "string"}
        found = self.mod.open_schemas(sch)
        self.assertTrue(any(p.startswith("/properties/bare is open") for p in found), found)
        self.assertTrue(any(p.startswith("/properties/anything accepts anything") for p in found), found)
        self.assertTrue(any(p.startswith("/properties/typed_map is open") for p in found), found)
        self.assertFalse(any("/properties/properties" in p for p in found), found)
        self.assertEqual(len(found), 3, found)

    def test_lovet_instans_som_dukker_opp_meldes(self):
        _write(self.tmp / "s.json", CLOSED)
        _write(self.tmp / "i.json", GOOD)
        _write(self.tmp / "x.json", CLOSED)
        _write(self.tmp / "x-data.json", GOOD)
        problems = self.mod.check(self.tmp, pairs=[("s.json", "i.json")], instanceless=[("x.json", "x-data.json")])
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("x-data.json exists now — register", problems[0])

    def test_format_date_time_haandheves(self):
        try:
            import rfc3339_validator  # noqa: F401
        except ImportError:
            self.skipTest("rfc3339-validator not installed — date-time cannot be checked here (CI installs it)")
        sch = json.loads(json.dumps(CLOSED))
        sch["properties"]["when"] = {"type": "string", "format": "date-time"}
        good = json.loads(json.dumps(GOOD)); good["when"] = "2026-09-06T07:03:00Z"
        bad = json.loads(json.dumps(GOOD)); bad["when"] = "nope"
        self.assertEqual(self._check(sch, good), [])
        problems = self._check(sch, bad)
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("'nope' is not a 'date-time'", problems[0])

    def test_uleselig_instans_er_et_problem_ikke_et_krasj(self):
        _write(self.tmp / "s.json", CLOSED)
        (self.tmp / "i.json").write_text("{not json", encoding="utf-8")
        problems = self.mod.check(self.tmp, pairs=[("s.json", "i.json")], instanceless=[])
        self.assertTrue(any("i.json: unreadable" in p for p in problems), problems)


class Generatoren(unittest.TestCase):
    """efc_atlas_export.py defined SCHEMA_PATH and never used it (card finding).
    Now it validates the snapshot before writing and refuses a rejected one."""

    def _mod(self):
        spec = importlib.util.spec_from_file_location("efc_atlas_export", ROOT / "scripts" / "maintenance" / "efc_atlas_export.py")
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_eksporten_validerer_mot_skjemaet_foer_skriving(self):
        m = self._mod()
        atlas = m.load_current_atlas()
        self.assertEqual(m.validate_against_schema(atlas), [])
        atlas["synonym_invented_here"] = 1
        problems = m.validate_against_schema(atlas)
        self.assertTrue(problems and "synonym_invented_here" in problems[0], problems)
        src = (ROOT / "scripts" / "maintenance" / "efc_atlas_export.py").read_text(encoding="utf-8")
        i_val, i_dry, i_dump = src.index("problems = validate_against_schema(atlas)"), src.index("if dry_run:"), src.index("json.dump(atlas")
        self.assertLess(i_val, i_dry, "a dry run must report validation")
        self.assertLess(i_dry, i_dump, "--apply --dry-run must never write (review finding)")


class Repoet(unittest.TestCase):
    def test_registrerte_par_er_gyldige_og_lukket(self):
        mod = _load()
        self.assertEqual(mod.check(), [])
        self.assertGreaterEqual(len(mod.PAIRS), 2)


if __name__ == "__main__":
    unittest.main()
