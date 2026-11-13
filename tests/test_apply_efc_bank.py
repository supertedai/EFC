"""Regression tests for safe Hindsight API compatibility and bank writes."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "integrations" / "hindsight" / "apply_efc_bank.py"
_spec = importlib.util.spec_from_file_location("apply_efc_bank", SCRIPT)
assert _spec and _spec.loader
apply_efc_bank = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = apply_efc_bank
_spec.loader.exec_module(apply_efc_bank)


class NewPagesClient:
    def get_page_tree(self, bank_id):
        return {"roots": [{"name": bank_id}]}

    def create_page_folder(self, bank_id, *, name):
        return {"id": f"{bank_id}:{name}"}

    def create_page(self, bank_id, *, name, source_query, parent_id=None, tags=None):
        return {"name": name, "parent_id": parent_id}


class LegacyPagesClient:
    def get_knowledge_base_tree(self, *, bank_id):
        return {"roots": [{"name": bank_id}]}

    def create_knowledge_folder(self, *, bank_id, name):
        return {"id": f"{bank_id}:{name}"}

    def create_knowledge_page(self, *, bank_id, name, source_query, parent_id=None, tags=None):
        return {"name": name, "parent_id": parent_id}


class PageCompatibilityTests(unittest.TestCase):
    def test_new_pages_methods_are_supported(self):
        api = apply_efc_bank.resolve_page_api(NewPagesClient())
        tree = apply_efc_bank.call_bank_method(api["tree"], "efc")
        folder = apply_efc_bank.call_bank_method(api["folder"], "efc", name="Validation")
        page = apply_efc_bank.call_bank_method(
            api["page"], "efc", name="Status", source_query="status?", parent_id=folder["id"], tags=["efc"]
        )
        self.assertEqual(tree["roots"][0]["name"], "efc")
        self.assertEqual(page["parent_id"], "efc:Validation")

    def test_legacy_knowledge_pages_methods_are_supported(self):
        api = apply_efc_bank.resolve_page_api(LegacyPagesClient())
        tree = apply_efc_bank.call_bank_method(api["tree"], "efc")
        folder = apply_efc_bank.call_bank_method(api["folder"], "efc", name="Validation")
        page = apply_efc_bank.call_bank_method(
            api["page"], "efc", name="Status", source_query="status?", parent_id=folder["id"], tags=["efc"]
        )
        self.assertEqual(tree["roots"][0]["name"], "efc")
        self.assertEqual(page["parent_id"], "efc:Validation")

    def test_unknown_client_fails_before_any_write(self):
        with self.assertRaisesRegex(RuntimeError, "page.*methods|methods.*page"):
            apply_efc_bank.resolve_page_api(object())

    def test_mission_extension_preserves_original_and_is_idempotent(self):
        original = "Bank-authored rules."
        addition = "Append this missing rule."
        once = apply_efc_bank.merge_mission_extension(original, addition)
        twice = apply_efc_bank.merge_mission_extension(once, addition)
        self.assertTrue(once.startswith(original))
        self.assertEqual(once, original + "\n\n" + addition)
        self.assertEqual(once, twice)

    def test_spec_loads_mission_additions_outside_config_fields(self):
        spec = apply_efc_bank.load_spec()
        self.assertIn("retain_mission", spec["_mission_additions"])
        self.assertIn("reflect_mission", spec["_mission_additions"])
        self.assertNotIn("_mission_additions", spec["config"])


class FakeConfigClient:
    def __init__(self, after):
        self.after = after
        self.get_calls = 0
        self.list_directives_called = False
        self.create_directive_called = False
        self.close_calls = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def close(self):
        self.close_calls += 1

    def get_bank_config(self, bank):
        self.get_calls += 1
        if self.get_calls == 1:
            return {"config": {}, "overrides": {}}
        return {"config": self.after, "overrides": self.after}

    def update_bank_config(self, bank_id, supported=None):
        raise AssertionError("unknown config key must use the REST fallback")

    def list_directives(self, *, bank_id):
        self.list_directives_called = True
        return {"items": []}

    def create_directive(self, **kwargs):
        self.create_directive_called = True


class ConfigWriteGateTests(unittest.TestCase):
    def _run_main(self, status, after, spec_config=None, skip_pages=True):
        client = FakeConfigClient(after)
        spec = {
            "config": spec_config or {"recall_prefer_observations": True},
            "directives": [{"name": "must-not-run-on-bad-readback", "content": "x"}],
            "pages": [],
        }
        fake_module = types.SimpleNamespace(Hindsight=lambda **kwargs: client)
        argv = [str(SCRIPT), "--apply"]
        if skip_pages:
            argv.append("--skip-pages")
        with tempfile.TemporaryDirectory() as tmp:
            out = io.StringIO()
            with (
                patch.dict(sys.modules, {"hindsight_client": fake_module}),
                patch.object(apply_efc_bank, "load_spec", return_value=spec),
                patch.object(apply_efc_bank, "BACKUP_DIR", Path(tmp)),
                patch.object(apply_efc_bank, "DEFAULT_URL", "http://example.invalid"),
                patch.object(apply_efc_bank, "hermes_env_token", return_value=None),
                patch.object(apply_efc_bank, "patch_config_rest", return_value=(status, "")),
                patch.object(sys, "argv", argv),
                contextlib.redirect_stdout(out),
            ):
                result = apply_efc_bank.main()
        return result, client, out.getvalue()

    def test_http_200_is_followed_by_readback(self):
        result, client, _ = self._run_main(200, {"recall_prefer_observations": True})
        self.assertEqual(result, 0)
        self.assertEqual(client.get_calls, 2)
        self.assertEqual(client.close_calls, 1)

    def test_http_204_is_followed_by_readback(self):
        result, client, _ = self._run_main(204, {"recall_prefer_observations": True})
        self.assertEqual(result, 0)
        self.assertEqual(client.get_calls, 2)

    def test_non_2xx_stops_before_readback_and_directives(self):
        result, client, _ = self._run_main(409, {"recall_prefer_observations": True})
        self.assertEqual(result, 1)
        self.assertEqual(client.get_calls, 1)
        self.assertEqual(client.close_calls, 1)
        self.assertFalse(client.list_directives_called)
        self.assertFalse(client.create_directive_called)

    def test_mismatched_readback_stops_before_directives(self):
        result, client, _ = self._run_main(204, {"recall_prefer_observations": False})
        self.assertEqual(result, 1)
        self.assertEqual(client.get_calls, 2)
        self.assertFalse(client.list_directives_called)
        self.assertFalse(client.create_directive_called)

    def test_missing_page_methods_fails_before_config_read(self):
        result, client, _ = self._run_main(
            200, {"recall_prefer_observations": True}, skip_pages=False
        )
        self.assertEqual(result, 2)
        self.assertEqual(client.get_calls, 0)
        self.assertEqual(client.close_calls, 1)
        self.assertFalse(client.list_directives_called)
        self.assertFalse(client.create_directive_called)


if __name__ == "__main__":
    unittest.main()
