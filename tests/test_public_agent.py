"""Focused safety tests for the review-only public agent."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from unittest import mock
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "efc_public_agent.py"
spec = importlib.util.spec_from_file_location("efc_public_agent", SCRIPT)
agent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agent)


class PublicAgentTests(unittest.TestCase):
    def make_repo(self, records=None, **config_overrides):
        root = Path(tempfile.mkdtemp())
        (root / "config").mkdir()
        (root / "docs/public").mkdir(parents=True)
        records = records or [{"id": "a", "title": "A", "target": "docs/public/a.html"}]
        for record in records:
            target = record.get("target", "")
            if (isinstance(target, str) and target.startswith("docs/public/")
                    and target.endswith(".html") and target != "docs/public/link.html"):
                (root / target).write_text("<html></html>")
        (root / "config" / "input.json").write_text(json.dumps(records))
        config = {"version": "1.0", "review_only": True, "publish": False,
                  "permissions": {"contents": "read", "pull_requests": "none"},
                  "operations": ["review"], "source_files": ["config/input.json"],
                  "output_dir": "reports/efc-public-agent"}
        config.update(config_overrides)
        path = root / "config" / "agent.json"
        path.write_text(json.dumps(config))
        return root, path

    def test_dry_run_is_deterministic_and_writes_no_artifacts(self):
        root, config = self.make_repo()
        first = agent.run(root, config, "dry-run", False)
        second = agent.run(root, config, "dry-run", False)
        self.assertEqual(first, second)
        self.assertFalse((root / "reports").exists())
        self.assertFalse(first["public_html_mutation"])
        self.assertTrue(first["review_required"])

    def test_pr_mode_only_writes_review_artifacts_outside_public(self):
        root, config = self.make_repo()
        plan = agent.run(root, config, "pr", True)
        self.assertTrue((root / "reports/efc-public-agent/public-agent-plan.json").exists())
        self.assertTrue((root / "reports/efc-public-agent/public-agent-pr.md").exists())
        self.assertTrue((root / "docs/public").exists())
        self.assertEqual(plan["requested_mode"], "pr")

    def test_public_output_target_fails_closed(self):
        root, config = self.make_repo(output_dir="docs/public/reports")
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)

    def test_alternate_output_is_rejected_without_mutation(self):
        root, config = self.make_repo(output_dir="reports/other")
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)
        self.assertFalse((root / "reports").exists())

    def test_targets_must_be_existing_regular_public_files(self):
        root, config = self.make_repo(records=[{"id": "a", "title": "A", "target": "docs/public/missing.html"}])
        (root / "docs/public/missing.html").unlink()
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "dry-run", False)

    def test_hostile_targets_fail_before_output(self):
        for target in ("docs/publicX/a.html", "docs/public/../secret.html", "/docs/public/a.html",
                       "docs\\public\\a.html", "docs/public/link.html"):
            with self.subTest(target=target):
                root, config = self.make_repo(records=[{"id": "a", "title": "A", "target": target}])
                if target == "docs/public/link.html":
                    (root / "docs/public/link.html").symlink_to(root / "docs/public/a.html")
                with self.assertRaises(agent.AgentError):
                    agent.run(root, config, "pr", True)
                self.assertFalse((root / "reports").exists())

    def test_symlinked_source_and_output_fail_before_output(self):
        root, config = self.make_repo()
        source = root / "config/input.json"
        source.unlink()
        source.symlink_to(root / "docs/public/a.html")
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)
        self.assertFalse((root / "reports").exists())

        root, config = self.make_repo()
        (root / "reports").symlink_to(root / "docs")
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)
        self.assertFalse((root / "reports/efc-public-agent").exists())

    def test_malformed_config_and_unsupported_mode_fail_without_output(self):
        root, config = self.make_repo()
        config.write_text("not json")
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)
        self.assertFalse((root / "reports").exists())
        root, config = self.make_repo()
        config.unlink()
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "pr", True)
        self.assertFalse((root / "reports").exists())
        root, config = self.make_repo()
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "publish", True)
        self.assertFalse((root / "reports").exists())
        root, config = self.make_repo(operations=["review", "publish"])
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "dry-run", False)
        self.assertFalse((root / "reports").exists())

    def test_publish_and_duplicate_are_rejected(self):
        root, config = self.make_repo(
            records=[{"id": "a", "title": "A", "target": "docs/public/a.html"},
                     {"id": "a", "title": "B", "target": "docs/public/b.html"}])
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "dry-run", False)
        root, config = self.make_repo(publish=True)
        with self.assertRaises(agent.AgentError):
            agent.run(root, config, "dry-run", False)

    def test_plan_contains_source_citations_and_disabled_opus_adapter(self):
        root, config = self.make_repo()
        plan = agent.run(root, config, "dry-run", False)
        self.assertEqual(plan["opus"]["adapter"], "disabled")
        self.assertEqual(plan["records"][0]["citations"], ["config/input.json"])

    def test_configured_opus_adapter_is_rejected_without_explicit_adapter(self):
        root, config = self.make_repo()
        with mock.patch.dict(agent.os.environ, {"EFC_OPUS_ADAPTER": "http"}):
            with self.assertRaises(agent.AgentError):
                agent.run(root, config, "dry-run", False)


if __name__ == "__main__":
    unittest.main()
