"""Tester for scripts/maintenance/efc_provenance_check.py — C13.

Kortet t_20a3c257: fire DOI-er har et maalt avvik mellom doi.org sitt arkiv og
repo-pakken. Avviket registreres i pakken (metadata.json -> provenance), og
denne testen er det som hindrer at registreringen blir dekorasjon.

Det som ikke faar raatne:

  - et provenance-felt UTEN arkivert tittel eller dato er et problem
    (kortets akseptansekriterium 3);
  - `title_matches_archive` og `date_matches_repo` er ikke meninger — de maa
    stemme med `title`/`date` i SAMME fil. En pakke kan ikke paastaa et
    samsvar den ikke har, og ikke benekte et den har;
  - `archive_doi` maa vaere pakkens egen DOI, saa en kopiert blokk ikke kan
    paastaa en annen artikkels arkiv;
  - de fire registrerte DOI-ene maa FORTSATT ha en provenance-blokk.

Hva testen IKKE maaler, og det er med vilje: om arkivtittelen burde vaert en
annen. Omtitulering av en publisert post er et menneskeord (kortets human
gate), og arkivtittelen kan derfor endre seg lovlig. Gaten krever at
registreringen FINNES og er internt konsistent — den fryser ikke de maalte
verdiene.
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
    """Syntetiske pakker: gaten maa FELLE, ikke bare si OK paa ekte tre."""

    def setUp(self):
        self.mod = _load()
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.tmp = Path(self._td.name)

    def _skriv(self, navn: str, doc) -> None:
        d = self.tmp / "docs" / "papers" / "efc" / navn
        d.mkdir(parents=True, exist_ok=True)
        (d / "metadata.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False),
                                         encoding="utf-8")

    def _problem(self, mutations=()) -> list[str]:
        """Strukturregelen alene — `scan`, ikke `check`.

        `check` legger til registerregelen (de fire maalte DOI-ene), og en
        syntetisk tre med EEN pakke ville felt de tre andre DOI-ene hver gang.
        Den regelen proeves i `test_registeret_krever_blokk_for_hver_doi`.
        """
        doc = json.loads(json.dumps(BUNDLE))
        for key, value in mutations:
            tgt = doc["provenance"]
            if value is None:
                tgt.pop(key, None)
            else:
                tgt[key] = value
        self._skriv("A_Package", doc)
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
        """En tom streng er ikke en registrering — den ser bare ut som en."""
        for tom in ("", "   "):
            problems = self._problem([("archive_title", tom)])
            self.assertTrue(any("archive_title" in p for p in problems), (tom, problems))

    def test_arkivtittel_og_dato_uten_kilde_er_et_problem(self):
        for nokkel in ("source", "measured_at", "archive_doi", "note"):
            problems = self._problem([(nokkel, None)])
            self.assertTrue(any(nokkel in p for p in problems), (nokkel, problems))

    def test_paastatt_samsvar_som_ikke_finnes_felles(self):
        """`title_matches_archive: true` mot en tittel som ikke er lik."""
        problems = self._problem([("title_matches_archive", True)])
        self.assertTrue(any("title_matches_archive" in p for p in problems), problems)

    def test_benektet_samsvar_som_faktisk_finnes_felles(self):
        """...og motsatt: lik tittel med `false` er ogsaa feil."""
        doc = json.loads(json.dumps(BUNDLE))
        doc["provenance"]["archive_title"] = doc["title"]
        self._skriv("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("title_matches_archive" in p for p in problems), problems)

    def test_datofeltet_maa_stemme_paa_samme_maate(self):
        problems = self._problem([("date_matches_repo", True)])
        self.assertTrue(any("date_matches_repo" in p for p in problems), problems)

    def test_boolean_maa_vaere_boolean(self):
        for nokkel in ("title_matches_archive", "date_matches_repo"):
            problems = self._problem([(nokkel, "false")])
            self.assertTrue(any(nokkel in p and "boolean" in p for p in problems), (nokkel, problems))

    def test_kopiert_blokk_fra_en_annen_pakke_felles(self):
        problems = self._problem([("archive_doi", "10.6084/m9.figshare.99999999")])
        self.assertTrue(any("is not this package's DOI" in p for p in problems), problems)

    def test_blokk_som_ikke_er_et_objekt_felles(self):
        doc = json.loads(json.dumps(BUNDLE))
        doc["provenance"] = "2024-12-30"
        self._skriv("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("not an object" in p for p in problems), problems)

    def test_pakke_uten_provenance_er_ikke_i_seg_selv_et_problem(self):
        """Fravær er ikke lovbrudd — bare de REGISTRERTE DOI-ene krever en blokk.

        Ellers ville gaten felt ~160 pakker den ikke har maalt.
        """
        doc = json.loads(json.dumps(BUNDLE))
        doc.pop("provenance")
        self._skriv("A_Package", doc)
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertEqual([p for p in problems if "A_Package" in p], [], problems)

    def test_registeret_krever_blokk_for_hver_doi(self):
        """Registerregelen: de fire DOI-ene maa ha blokk — og bare de fire."""
        for doi in self.mod.REGISTERED:
            doc = json.loads(json.dumps(BUNDLE))
            doc["doi"] = doi
            doc["provenance"]["archive_doi"] = doi
            self._skriv("pkg_" + doi.rsplit(".", 1)[1], doc)
        self.assertEqual(self.mod.check(str(self.tmp)), [])

    def test_en_registrert_doi_uten_blokk_navngis(self):
        for doi in self.mod.REGISTERED:
            doc = json.loads(json.dumps(BUNDLE))
            doc["doi"] = doi
            doc["provenance"]["archive_doi"] = doi
            if doi == "10.6084/m9.figshare.28098314":
                doc.pop("provenance")
            self._skriv("pkg_" + doi.rsplit(".", 1)[1], doc)
        problems = self.mod.check(str(self.tmp))
        self.assertEqual(len(problems), 1, problems)
        self.assertIn("10.6084/m9.figshare.28098314", problems[0])
        self.assertEqual(len(self.mod.REGISTERED), 4, "de fire maalte avvikene skal staa i registeret")

    def test_uleselig_metadata_er_et_problem_ikke_et_krasj(self):
        d = self.tmp / "docs" / "papers" / "efc" / "A_Package"
        d.mkdir(parents=True)
        (d / "metadata.json").write_text("{not json", encoding="utf-8")
        problems = self.mod.scan(str(self.tmp))[0]
        self.assertTrue(any("unreadable" in p for p in problems), problems)


class Registeret(unittest.TestCase):
    """Hver registrert rad skal baere en grunn — en rad uten grunn er en skjult feil."""

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
            self.assertIn(doi, by_doi, f"{doi} mangler provenance-blokk")
        for doi, navn in by_doi.items():
            meta = json.loads((ROOT / "docs" / "papers" / "efc" / navn / "metadata.json")
                              .read_text(encoding="utf-8"))
            prov = meta["provenance"]
            self.assertTrue(prov["archive_title"].strip(), doi)
            self.assertTrue(prov["archive_date"].strip(), doi)
            self.assertEqual(prov["archive_doi"], doi)


class GatenKjoererISelv(unittest.TestCase):
    """En test som ikke kjoeres er dokumentasjon. efc-verify.yml rører
    docs/papers/efc/** — det er der pakkene endres, saa det er der gaten
    hoerer. efc-schema.yml kjoerer pytest-filene, denne maa staa der."""

    def test_verify_workflowen_kjoerer_skriptet(self):
        tekst = VERIFY_WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("scripts/maintenance/efc_provenance_check.py", tekst,
                      "gaten kjoeres ikke i efc-verify.yml — da er den ikke en gate")

    def test_denne_filen_staar_i_ci_pytest_kommandoen(self):
        import re
        skjema = (ROOT / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"python3 -m pytest ([^\n]+)", skjema)
        self.assertIsNotNone(m, "fant ingen pytest-kommando i efc-schema.yml")
        self.assertIn("test_efc_provenance.py", m.group(1),
                      f"denne testfilen kjoeres ikke i CI: {m.group(1)}")


if __name__ == "__main__":
    unittest.main()
