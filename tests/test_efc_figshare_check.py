"""Unit tests for scripts/maintenance/efc_figshare_check.py.

The tests stub all network paths so they run offline. We exercise the
public surface — title-mismatch classifier, scaffold layout, primary-file
selection — plus a couple of end-to-end dry runs through `cmd_check` /
`cmd_scaffold` with a temporary doi-map.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "efc_figshare_check.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("efc_figshare_check", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_figshare_check"] = mod
    spec.loader.exec_module(mod)
    return mod


figshare = _load_module()


class TitleClassifierTests(unittest.TestCase):
    def test_exact_match_is_ok(self):
        self.assertEqual(
            figshare.classify_title_mismatch("Same Title", "Same Title"),
            "ok",
        )

    def test_efc_dash_prefix(self):
        self.assertEqual(
            figshare.classify_title_mismatch(
                "EFC — Hypothesis: Foo", "Hypothesis: Foo"
            ),
            "prefix_efc_dash",
        )

    def test_white_paper_prefix(self):
        self.assertEqual(
            figshare.classify_title_mismatch(
                "Field Equations and Observable Mapping",
                "White Paper - Part 2 of 4 - Field Equations and Observable Mapping",
            ),
            "prefix_white_paper",
        )

    def test_truncation_local(self):
        self.assertEqual(
            figshare.classify_title_mismatch("ABC", "ABC and the rest"),
            "truncation_local",
        )

    def test_truncation_remote(self):
        self.assertEqual(
            figshare.classify_title_mismatch("ABC and the rest", "ABC"),
            "truncation_remote",
        )

    def test_truncation_after_prefix_strip(self):
        self.assertEqual(
            figshare.classify_title_mismatch(
                "EFC — Foo Bar", "White Paper - Part 1 of 4 - Foo Bar"
            ),
            "truncation_after_prefix_strip",
        )

    def test_semantic_drift(self):
        self.assertEqual(
            figshare.classify_title_mismatch(
                "EFC Hypothesis: Energy Entropy",
                "The Grid Model as a Structural Framework",
            ),
            "semantic_drift",
        )

    def test_empty_remote_is_drift(self):
        self.assertEqual(
            figshare.classify_title_mismatch("Local", ""), "semantic_drift"
        )


class AuthorMatchTests(unittest.TestCase):
    def test_match_by_full_name(self):
        article = {"authors": [{"full_name": "Morten Magnusson"}]}
        self.assertTrue(figshare.author_matches(article))

    def test_match_by_id(self):
        article = {"authors": [{"id": 20477774}]}
        self.assertTrue(figshare.author_matches(article))

    def test_no_match(self):
        article = {"authors": [{"full_name": "Someone Else", "id": 999}]}
        self.assertFalse(figshare.author_matches(article))

    def test_empty(self):
        self.assertFalse(figshare.author_matches({}))


class WithdrawnDetectionTests(unittest.TestCase):
    def test_metadata_record_is_withdrawn(self):
        self.assertTrue(figshare.article_is_withdrawn({"is_metadata_record": True}))

    def test_status_withdrawn(self):
        self.assertTrue(figshare.article_is_withdrawn({"status": "withdrawn"}))

    def test_normal_article(self):
        self.assertFalse(figshare.article_is_withdrawn({"status": "public"}))


class PrimaryAttachmentTests(unittest.TestCase):
    def test_pdf_preferred(self):
        article = {
            "files": [
                {"name": "draft.docx", "download_url": "u1"},
                {"name": "paper.pdf", "download_url": "u2"},
            ]
        }
        self.assertEqual(figshare.primary_attachment(article), ("paper.pdf", "u2"))

    def test_docx_fallback_when_no_pdf(self):
        article = {"files": [{"name": "Hypothesis.docx", "download_url": "u-docx"}]}
        self.assertEqual(
            figshare.primary_attachment(article), ("Hypothesis.docx", "u-docx")
        )

    def test_other_fallback(self):
        article = {"files": [{"name": "data.zip", "download_url": "u-zip"}]}
        self.assertEqual(figshare.primary_attachment(article), ("data.zip", "u-zip"))

    def test_no_files_returns_none(self):
        self.assertIsNone(figshare.primary_attachment({"files": []}))


class CheckOneTests(unittest.TestCase):
    def _patch_fetch(self, payload, err=None):
        return mock.patch.object(
            figshare, "fetch_figshare", return_value=(payload, err)
        )

    def test_not_found(self):
        with self._patch_fetch(None, err="not_found"):
            r = figshare.check_one("10.6084/m9.figshare.123", "Local")
        self.assertEqual(r["status"], "not_found")

    def test_network_error(self):
        with self._patch_fetch(None, err="network_unreachable: x"):
            r = figshare.check_one("10.6084/m9.figshare.123", "Local")
        self.assertEqual(r["status"], "network_error")

    def test_wrong_author(self):
        article = {
            "title": "Local",
            "authors": [{"full_name": "Other"}],
            "status": "public",
        }
        with self._patch_fetch(article):
            r = figshare.check_one("10.6084/m9.figshare.123", "Local")
        self.assertEqual(r["status"], "wrong_author")

    def test_withdrawn(self):
        article = {
            "title": "Local",
            "authors": [{"full_name": "Morten Magnusson"}],
            "is_metadata_record": True,
        }
        with self._patch_fetch(article):
            r = figshare.check_one("10.6084/m9.figshare.123", "Local")
        self.assertEqual(r["status"], "withdrawn")

    def test_ok(self):
        article = {
            "title": "Local",
            "authors": [{"full_name": "Morten Magnusson"}],
            "status": "public",
        }
        with self._patch_fetch(article):
            r = figshare.check_one("10.6084/m9.figshare.123", "Local")
        self.assertEqual(r["status"], "ok")

    def test_title_mismatch_subclass(self):
        article = {
            "title": "Foo Bar",
            "authors": [{"full_name": "Morten Magnusson"}],
            "status": "public",
        }
        with self._patch_fetch(article):
            r = figshare.check_one("10.6084/m9.figshare.123", "EFC — Foo Bar")
        self.assertEqual(r["status"], "title_mismatch")
        self.assertEqual(r["subclass"], "prefix_efc_dash")


class ScaffoldTests(unittest.TestCase):
    def test_scaffold_creates_canonical_layout(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            target = Path(tmp)
            with mock.patch.object(figshare, "fetch_figshare", return_value=(None, None)):
                result = figshare.scaffold_one(
                    {"figshare_id": 12345, "title": "Test Paper"},
                    with_pdf=False,
                    out_root=target,
                )
            paper_dir = target / "test-paper"
            self.assertTrue(paper_dir.is_dir())
            for fname in (
                "index.json",
                "metadata.json",
                "schema.json",
                "README.md",
                "CITATION.cff",
                "citations.bib",
                "LICENSE",
                ".scaffolded",
                "test-paper.jsonld",
            ):
                self.assertTrue(
                    (paper_dir / fname).exists(),
                    f"missing {fname} in scaffold",
                )
            for d in ("src", "data", "examples"):
                self.assertTrue((paper_dir / d).is_dir())
            self.assertTrue(
                (paper_dir / "src" / "__init__.py").exists(),
                "missing src/__init__.py marker",
            )
            idx = json.loads((paper_dir / "index.json").read_text())
            self.assertEqual(idx["doi"], "10.6084/m9.figshare.12345")
            self.assertTrue(idx["scaffolded"])
            self.assertEqual(result["status"], "scaffolded")

    def test_scaffold_skips_existing(self):
        from tempfile import TemporaryDirectory

        with TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target / "test-paper").mkdir()
            with mock.patch.object(figshare, "fetch_figshare", return_value=(None, None)):
                result = figshare.scaffold_one(
                    {"figshare_id": 12345, "title": "Test Paper"},
                    with_pdf=False,
                    out_root=target,
                )
        self.assertEqual(result["status"], "exists")


class CmdCheckIntegrationTests(unittest.TestCase):
    def test_network_only_returns_zero(self):
        # Patch DOI_MAP to a tiny fake
        from tempfile import NamedTemporaryFile

        fake_map = {
            "papers": [
                {
                    "doi": "10.6084/m9.figshare.111",
                    "title": "Some Paper",
                }
            ],
            "missing_repo_dirs": [],
        }
        with NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            json.dump(fake_map, fh)
            tmp_path = Path(fh.name)
        try:
            with (
                mock.patch.object(figshare, "DOI_MAP", tmp_path),
                mock.patch.object(figshare, "REPORTS_DIR", tmp_path.parent),
                mock.patch.object(
                    figshare,
                    "fetch_figshare",
                    return_value=(None, "network_unreachable: sandbox"),
                ),
            ):
                rc = figshare.cmd_check(json_out=False)
            self.assertEqual(rc, 0)  # network-only does not gate
        finally:
            os.unlink(tmp_path)


if __name__ == "__main__":
    unittest.main()
