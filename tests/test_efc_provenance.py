"""Tests for scripts/maintenance/efc_provenance_check.py — C13.

Card t_20a3c257: four DOIs have a measured discrepancy between doi.org's
archive and the repo package. The discrepancy is registered in the package
(metadata.json -> provenance), and this test is what keeps the registration
from becoming decoration.

What must not rot:

  - a provenance field WITHOUT an archived title or date is a problem
    (the card's acceptance criterion 3);
  - `title_matches_archive` and `date_matches_repo` are not opinions — they
    must match `title`/`date` in the SAME file. A package cannot claim a
    match it does not have, nor deny one it does have;
  - `archive_doi` must be the package's own DOI, so a copied block cannot
    claim another article's archive;
  - the four registered DOIs must STILL have a provenance block.

What the test does NOT measure, and that is deliberate: whether the archive
title should have been a different one. Retitling a published record is a
human decision (the card's human gate), so the archive title may legally
change. The gate requires that the registration EXISTS and is internally
consistent — it does not freeze the measured values.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_provenance_check.py"
VERIFY_WORKFLOW = ROOT / ".github" / "workflows" / "efc-verify.yml"

BUNDLE = {
    "title": "EFC — A Title The Package Claims",
    "date": "2025-01-01",
    "doi": "10.6084/m9.figshare.28111925",
    "provenance": {
        "archive_doi": "10.6084/m9.figshare.28111925",
        "archive_title": "A Registered Title That Differs",
        "archive_date": "2024-12-30",
        "archive_date_type": "issued",
        "archive_type": "thesis",
        "source": "doi.org CSL-JSON",
        "measured_at": "2026-09-18",
        "title_matches_archive": False,
        "date_matches_repo": False,
        "note": "measured, not corrected",
    },
}


def _load():
    spec = importlib.util.spec_from_file_location("efc_provenance_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_provenance_check"] = mod
    spec.loader.exec_module(mod)
    return mod


class Rigg(unittest.TestCase):
    """Synthetic packages: the gate must FAIL, not just say OK on the real tree."""

    def setUp(self):
        self.mod = _load()
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def _write(self, name: str, doc) -> None:
        d = self.tmp / "docs" / "papers" / "efc" / name
        d.mkdir(parents=True, exist_ok=True)
        (d / "metadata.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                                         encoding="utf-8")

    def _problem(self, mutations=()) -> list[str]:
        """The structure rule alone — `scan`, not `check`.

        `check` adds the register rule (the four measured DOIs), and a
        synthetic tree with ONE package would fail on the three other DOIs
        every time. That rule is exercised in
        `test_registeret_krever_blokk_for_hver_doi`.
        """
        doc = json.loads(json.dumps(BUNDLE))
        for key, value in mutations:
            tgt = doc["provenance"]
            if value is None:
                tgt.pop(key, None)
            else:
                tgt[key] = value
        self._write("A_Package", doc)
        return self.mod.scan(str(self.tmp))[0]

    def test_komplett_blokk_er_groenn_naar_booleans_stemmer(self):
        self.assertEqual(self._problem(), [])

    def test_uten_arkivtittel_er_et_problem(self):
        problems = self._problem([("archive_title", None)])
        self.assertTrue(any("archive_title" in p for p in problems), problems)

    def test_uten_arkividato_er_et_problem(self):
        problems = self._problem([("archive_date", None)])
        self.assertTrue(any("archive_date" in p for p in problems), problems)

    def test_tom_arkivtittel_er_et_problem(self):
        """An empty string is not a registration — it only looks like one."""
        for empty in ("", "   "):
            problems = self._problem([("archive_title", empty)])
            self.assertTrue(any("archive_title" in p for p in problems), (empty, problems))

    def test_arkivtittel_og_dato_uten_kilde_er_et_problem(self):
        for key in ("source", "measured_at", "archive_doi", "note"):
            problems = self._problem([(key, None)])
            self.assertTrue(any(key in p for p in problems), (key, problems))

    def test_paastatt_samsvar_som_ikke_finnes_felles(self):
        """`title_matches_archive: true` against a title that is not equal."""
        problems = self._problem([("title_matches_archive", True)])
        self.assertTrue(any("title_matches_archive" in p for p in problems), problems)

    def test_benektet_samsvar_som_faktisk_finnes_felles(self):
        """...and the opposite: an equal title with `false` is also wrong."""
        doc = json.loads(json.dumps(BUNDLE))
        doc["provenance"]["archive_title"] = doc["title"]
        self._write("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("title_matches_archive" in p for p in problems), problems)

    def test_datofeltet_maa_stemme_paa_samme_maate(self):
        problems = self._problem([("date_matches_repo", True)])
        self.assertTrue(any("date_matches_repo" in p for p in problems), problems)

    def test_boolean_maa_vaere_boolean(self):
        for key in ("title_matches_archive", "date_matches_repo"):
            problems = self._problem([(key, "false")])
            self.assertTrue(any(key in p and "boolean" in p for p in problems), (key, problems))

    def test_kopiert_blokk_fra_en_annen_pakke_felles(self):
        problems = self._problem([("archive_doi", "10.6084/m9.figshare.99999999")])
        self.assertTrue(any("is not this package's DOI" in p for p in problems), problems)

    def test_blokk_som_ikke_er_et_objekt_felles(self):
        doc = json.loads(json.dumps(BUNDLE))
        doc["provenance"] = "2024-12-30"
        self._write("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("not an object" in p for p in problems), problems)

    def test_pakke_uten_provenance_er_ikke_i_seg_selv_et_problem(self):
        """Absence is not a violation — only the REGISTERED DOIs require a block.

        Otherwise the gate would fail ~160 packages it has not measured.
        """
        doc = json.loads(json.dumps(BUNDLE))
        doc.pop("provenance")
        self._write("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertEqual([p for p in problems if "A_Package" in p], [], problems)

    def test_registeret_krever_blokk_for_hver_doi(self):
        """The register rule: the four DOIs must have a block — and only the four."""
        for doi in self.mod.REGISTERED:
            doc = json.loads(json.dumps(BUNDLE))
            doc["doi"] = doi
            doc["provenance"]["archive_doi"] = doi
            self._write("pkg_" + doi.rsplit(".", 1)[1], doc)
        self.assertEqual(self.mod.check(str(self.tmp)), [])

    def test_en_registrert_doi_uten_blokk_navngis(self):
        for doi in self.mod.REGISTERED:
            doc = json.loads(json.dumps(BUNDLE))
            doc["doi"] = doi
            doc["provenance"]["archive_doi"] = doi
            if doi == "10.6084/m9.figshare.28098314":
                doc.pop("provenance")
            self._write("pkg_" + doi.rsplit(".", 1)[1], doc)
        problems = self.mod.check(str(self.tmp))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("10.6084/m9.figshare.28098314", problems[0])
        self.assertEqual(len(self.mod.REGISTERED), 4, "the four measured discrepancies must stand in the register")

    def test_uleselig_metadata_er_et_problem_ikke_et_krasj(self):
        d = self.tmp / "docs" / "papers" / "efc" / "A_Package"
        d.mkdir(parents=True)
        (d / "metadata.json").write_text("{not json", encoding="utf-8")
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("unreadable" in p for p in problems), problems)


class Registeret(unittest.TestCase):
    """Every registered row must carry a reason — a row without a reason is a hidden error."""

    def test_hver_rad_har_en_grunn(self):
        for doi, why in _load().REGISTERED.items():
            self.assertTrue(why and why.strip(), doi)
            self.assertTrue(doi.startswith("10.6084/m9.figshare."), doi)


class Repoet(unittest.TestCase):
    def test_ekte_tre_er_groent(self):
        self.assertEqual(_load().check(), [])

    def test_de_fire_registrerte_doi_ene_har_blokk_med_tittel_og_dato(self):
        _, by_doi = _load().scan()
        for doi in _load().REGISTERED:
            self.assertIn(doi, by_doi, f"{doi} is missing a provenance block")
        for doi, name in by_doi.items():
            meta = json.loads((ROOT / "docs" / "papers" / "efc" / name / "metadata.json")
                              .read_text(encoding="utf-8"))
            prov = meta["provenance"]
            self.assertTrue(prov["archive_title"].strip(), doi)
            self.assertTrue(prov["archive_date"].strip(), doi)
            self.assertEqual(prov["archive_doi"], doi)


class GatenKjoererISelv(unittest.TestCase):
    """A test that is not run is documentation. efc-verify.yml touches
    docs/papers/efc/** — that is where the packages change, so that is where
    the gate belongs. efc-schema.yml runs the pytest files; this one must
    stand there."""

    def test_verify_workflowen_kjoerer_skriptet(self):
        tekst = VERIFY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/maintenance/efc_provenance_check.py", tekst,
                      "the gate is not run in efc-verify.yml — then it is not a gate")

    def test_denne_filen_staar_i_ci_pytest_kommandoen(self):
        import re
        schema = (ROOT / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"python3 -m pytest ([^\n]+)", schema)
        self.assertIsNotNone(m, "found no pytest command in efc-schema.yml")
        self.assertIn("test_efc_provenance.py", m.group(1),
                      f"this test file is not run in CI: {m.group(1)}")


if __name__ == "__main__":
    unittest.main()
