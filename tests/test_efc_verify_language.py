"""Unit tests for the C9 language-discipline check in efc_verify.py.

C9 is the JSON sibling of C3: it enforces AGENTS.md's language discipline
("consistent with" / "overlaps with" / "within EFC prediction band", never
"confirms EFC") on the EFC-authored free-text fields of
docs/public/external_research_watch.json.

The tests drive check_c9_watch_language against temporary watchlist files by
patching the module-level WATCH_JSON path, so they never touch the real
watchlist and run offline. One test asserts the shipped watchlist is clean,
which is what would have caught the 2026-08-19 breach.
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "efc_verify.py"
WATCHLIST = REPO_ROOT / "docs" / "public" / "external_research_watch.json"


def _load_module():
    spec = importlib.util.spec_from_file_location("efc_verify", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["efc_verify"] = mod
    spec.loader.exec_module(mod)
    return mod


verify = _load_module()


def _run_c9(items):
    """Run C9 over a throwaway watchlist and return its issues."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "external_research_watch.json")
        with open(path, "w", encoding="utf-8") as fh:
            json.dump({"version": "test", "items": items}, fh, ensure_ascii=False)
        issues = []
        with mock.patch.object(verify, "WATCH_JSON", path):
            verify.check_c9_watch_language(issues)
        return issues


def _errors(issues):
    return [i for i in issues if i.severity == "error"]


def _warnings(issues):
    return [i for i in issues if i.severity == "warn"]


class ForbiddenPhraseTests(unittest.TestCase):
    def test_validates_efc_in_relevance_is_an_error(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00001",
            "efc_relevance": "2.6σ CMB tension validates EFC μ(a) < 1 prediction.",
        }])
        errs = _errors(issues)
        self.assertEqual(len(errs), 1)
        self.assertEqual(errs[0].code, "C9")
        self.assertIn("arXiv:0000.00001", errs[0].where)
        self.assertIn("validates EFC", errs[0].msg)

    def test_forbidden_phrase_in_ledger_action_is_an_error(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00002",
            "ledger_action": "Add row noting this confirms EFC.",
        }])
        self.assertEqual(len(_errors(issues)), 1)
        self.assertIn("ledger_action", _errors(issues)[0].where)

    def test_match_is_case_insensitive(self):
        issues = _run_c9([{
            "key": "k", "efc_relevance": "This PROVES EFC beyond doubt.",
        }])
        self.assertEqual(len(_errors(issues)), 1)

    def test_compliant_phrasing_passes(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00003",
            "efc_relevance": "S8 = 0.798 (NLA); overlaps with the logged DES Y6 "
                             "P3 PASS and is within the EFC μ(a) < 1 prediction band.",
            "ledger_action": "Replace preliminary DES Y6 row with published values.",
        }])
        self.assertEqual(issues, [])


class FieldCarveOutTests(unittest.TestCase):
    """The JSON carve-out is by field (who is speaking), not by section.

    Unlike the HTML ledger's positional §4b block, every watchlist item is
    external by construction, so only the EFC-authored fields are scanned.
    """

    def test_external_title_is_not_scanned(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00004",
            "title": "A Measurement That Confirms EFC, According To Its Authors",
            "efc_relevance": "Consistent with the L2→L3 transition.",
        }])
        self.assertEqual(issues, [])

    def test_url_and_source_type_are_not_scanned(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00005",
            "url": "https://example.org/proves-efc-paper",
            "source_type": "preprint that validates EFC",
        }])
        self.assertEqual(issues, [])


class SoftClaimTests(unittest.TestCase):
    """"supports EFC" and friends warn but do not fail — promotion to
    FORBIDDEN_PHRASES is a human judgement call (see the PR discussion)."""

    def test_supports_efc_warns_without_erroring(self):
        issues = _run_c9([{
            "key": "arXiv:0000.00006",
            "efc_relevance": "3.1σ preference for w0wa; supports EFC L2→L3 transition.",
        }])
        self.assertEqual(_errors(issues), [])
        warns = _warnings(issues)
        self.assertEqual(len(warns), 1)
        self.assertIn("supports EFC", warns[0].msg)
        self.assertIn("not enforced", warns[0].msg)

    def test_soft_list_is_disjoint_from_forbidden_list(self):
        hard = {p.lower() for p in verify.FORBIDDEN_PHRASES}
        soft = {p.lower() for p in verify.SOFT_CLAIM_PHRASES}
        self.assertEqual(hard & soft, set())


class MalformedInputTests(unittest.TestCase):
    def test_missing_file_reports_an_error(self):
        issues = []
        with mock.patch.object(verify, "WATCH_JSON", "/nonexistent/watch.json"):
            verify.check_c9_watch_language(issues)
        self.assertEqual(len(_errors(issues)), 1)

    def test_unparseable_file_reports_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "watch.json")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("{not json")
            issues = []
            with mock.patch.object(verify, "WATCH_JSON", path):
                verify.check_c9_watch_language(issues)
        self.assertEqual(len(_errors(issues)), 1)
        self.assertIn("unparseable", _errors(issues)[0].msg)

    def test_schema_change_warns_rather_than_crashing(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "watch.json")
            with open(path, "w", encoding="utf-8") as fh:
                json.dump({"version": "9.0", "entries": []}, fh)
            issues = []
            with mock.patch.object(verify, "WATCH_JSON", path):
                verify.check_c9_watch_language(issues)
        self.assertEqual(_errors(issues), [])
        self.assertEqual(len(_warnings(issues)), 1)

    def test_missing_and_non_dict_items_are_tolerated(self):
        issues = _run_c9([{"key": "no-free-text-fields"}, "junk", None])
        self.assertEqual(issues, [])


class ShippedWatchlistTests(unittest.TestCase):
    """Regression guard: the real watchlist must stay clean.

    Two items breached this on 2026-08-19 (v1.8, 106 items) — arXiv:2602.10065
    ("validates EFC") and arXiv:2503.14738 ("supports EFC") — undetected
    because C3 only ever scanned the HTML ledger.
    """

    def test_shipped_watchlist_has_no_forbidden_language(self):
        self.assertTrue(WATCHLIST.exists(), f"{WATCHLIST} not found")
        issues = []
        verify.check_c9_watch_language(issues)
        self.assertEqual(
            [str(i) for i in _errors(issues)], [],
            "docs/public/external_research_watch.json breaches AGENTS.md "
            "language discipline",
        )


if __name__ == "__main__":
    unittest.main()
