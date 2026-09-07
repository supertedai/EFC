"""Every GitHub workflow file parses and has jobs with runnable steps.

Measured 2026-09-06 on PR #376: four local gates and a line-by-line audit were
green while `.github/workflows/efc-verify.yml` was not valid YAML — a step
named `Check the efc: namespace (...)` puts `efc:` followed by a space in a
plain scalar, which YAML reads as a nested mapping. GitHub reported the run as
failed with no log. Nothing in the tree parsed the workflow files before this.
"""
from __future__ import annotations

import glob
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Workflows(unittest.TestCase):
    def test_alle_workflow_filer_parser_og_har_kjoerbare_steg(self):
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed — workflow files cannot be parsed here (CI installs it)")
        files = sorted(glob.glob(str(ROOT / ".github" / "workflows" / "*.yml")))
        self.assertGreater(len(files), 0)
        for f in files:
            with open(f, encoding="utf-8") as fh:
                doc = yaml.safe_load(fh)
            self.assertIsInstance(doc, dict, f)
            self.assertIn("jobs", doc, f)
            for job_name, job in doc["jobs"].items():
                for step in job.get("steps", []):
                    self.assertTrue("run" in step or "uses" in step, f"{f}: job {job_name}: step without run/uses: {step}")


class Triggere(unittest.TestCase):
    """t_0d65ccdf: verification must reach main, not only the PR window."""

    def _load(self, name):
        import yaml
        with open(ROOT / ".github" / "workflows" / name, encoding="utf-8") as fh:
            return yaml.safe_load(fh)

    def setUp(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed")

    def test_efc_verify_kjoerer_paa_push_plan_og_dispatch_med_samme_paths(self):
        on = self._load("efc-verify.yml")[True]
        self.assertIn("workflow_dispatch", on)
        self.assertIn("schedule", on)
        self.assertEqual(on["push"]["branches"], ["main"])
        self.assertEqual(on["push"]["paths"], on["pull_request"]["paths"], "push and pull_request must watch the same files")
        self.assertIn("**/*.jsonld", on["push"]["paths"])

    def test_cron_owns_writes_and_maintenance_actions_are_absent(self):
        """The cron maintenance chain is the sole EFC writer.

        GitHub Actions validate PR/main state; they must not race cron by
        auto-committing or auto-pushing the same public/ledger surfaces.
        """
        workflows = {p.name for p in (ROOT / ".github" / "workflows").glob("*.yml")}
        for removed in ("efc-main-sync.yml", "efc-sync.yml", "atlas-sync.yml", "efc-doi-coverage.yml", "efc-system-health.yml"):
            self.assertNotIn(removed, workflows, removed)

    def test_validation_workflows_are_read_only(self):
        """Required PR gates must not contain repository write commands."""
        workflow_dir = ROOT / ".github" / "workflows"
        for name in ("efc-verify.yml", "efc-schema.yml", "atlas-verify.yml", "efc-page-consistency.yml", "efc-rootfile-consistency.yml", "efc-4b-register.yml"):
            text = (workflow_dir / name).read_text(encoding="utf-8")
            self.assertNotIn("git push", text, name)
            self.assertNotIn("git commit", text, name)
            self.assertNotIn("gh pr create", text, name)

    def test_ingen_pages_workflow(self):
        """t_0d65ccdf measured the legacy 'errored' builds as supersessions, not failures."""
        self.assertFalse((ROOT / ".github" / "workflows" / "pages.yml").exists())

if __name__ == "__main__":
    unittest.main()
