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

    def test_main_sync_har_porten_etter_vedlikehold_og_dispatcher_verify_og_schema(self):
        wf = self._load("efc-main-sync.yml")
        self.assertEqual(wf["permissions"].get("actions"), "write")
        steps = wf["jobs"]["auto-sync"]["steps"]
        names = [s.get("name", "") for s in steps]
        by_id = {s.get("id"): s for s in steps if s.get("id")}
        self.assertIn("porten", by_id)
        for tool in ("efc_sync_dois.py --check", "efc_ontology.py", "efc_concepts.py", "efc_identity.py", "efc_verify.py", "efc_drift_detector.py"):
            self.assertIn(tool, by_id["porten"]["run"], tool)
        self.assertIn("exit 1", by_id["porten"]["run"], "a red gate must make the run red")
        i_maint = next(i for i, n in enumerate(names) if n.startswith("Run maintenance pipeline"))
        i_porten = names.index("Porten foer auto-commit (C8, C9, C11, C12, C1–C8, drift)")
        i_commit = names.index("Auto-commit fixes to main")
        self.assertLess(i_maint, i_porten, "the gate runs AFTER the maintenance pass (which may be the repair)")
        self.assertLess(i_porten, i_commit, "and BEFORE the commit")
        commit = steps[i_commit]
        self.assertIn("steps.porten.outputs.rc == '0'", commit["if"], "fail closed: an empty rc must not commit")
        self.assertIn("gh workflow run efc-verify.yml --ref main", commit["run"])
        self.assertIn("gh workflow run efc-schema.yml --ref main", commit["run"])
        self.assertLess(commit["run"].index("Push succeeded."), commit["run"].index("gh workflow run efc-verify.yml"), "dispatch right after the push, in the same step")
        self.assertIn("Push failed four times", commit["run"])
        self.assertFalse(any("pages.yml" in (s.get("run") or "") for s in steps), "no Pages dispatch: the legacy builder builds on every push")

    def test_ingen_pages_workflow(self):
        """t_0d65ccdf measured the legacy 'errored' builds as supersessions, not failures."""
        self.assertFalse((ROOT / ".github" / "workflows" / "pages.yml").exists())

if __name__ == "__main__":
    unittest.main()
