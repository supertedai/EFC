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
        for name in ("efc-verify.yml", "efc-schema.yml", "atlas-verify.yml", "efc-page-consistency.yml", "efc-rootfile-consistency.yml", "efc-4b-register.yml", "efc-atlas-konsistens.yml"):
            text = (workflow_dir / name).read_text(encoding="utf-8")
            self.assertNotIn("git push", text, name)
            self.assertNotIn("git commit", text, name)
            self.assertNotIn("gh pr create", text, name)

    def test_ingen_pages_workflow(self):
        """t_0d65ccdf measured the legacy 'errored' builds as supersessions, not failures."""
        self.assertFalse((ROOT / ".github" / "workflows" / "pages.yml").exists())


class AtlasGaten(unittest.TestCase):
    """t_2102d90e: 50 tests were red in 18 files and NO workflow ran any of them.

    The atlas family is the family that can rot without going red: the atlas is
    generated, so a pruned node reaches the flat surfaces through
    `efc_atlas_generator.py` — and nothing in CI compared the surfaces to the
    bank. `efc-atlas-konsistens.yml` closes that hole. These assertions keep the
    gate from silently narrowing afterwards: every test_atlas_* file on disk
    must be matched by the pytest command, and push and pull_request must guard
    the same files.
    """

    WF = "efc-atlas-konsistens.yml"

    def setUp(self):
        try:
            import yaml  # noqa: F401
        except ImportError:
            self.skipTest("PyYAML not installed — workflow files cannot be parsed here (CI installs it)")

    def _kommando(self) -> str:
        text = (ROOT / ".github" / "workflows" / self.WF).read_text(encoding="utf-8")
        linjer = text.splitlines()
        start = [i for i, l in enumerate(linjer) if "python3 -m pytest" in l]
        self.assertEqual(len(start), 1, f"expected one pytest command in {self.WF}")
        blokk = [linjer[start[0]]]
        i = start[0]
        while blokk[-1].rstrip().endswith("\\"):
            i += 1
            blokk.append(linjer[i])
        return " ".join(x.strip().rstrip("\\").strip() for x in blokk)

    def test_hver_atlas_testfil_er_dekket_av_kommandoen(self):
        import fnmatch
        import re
        kommando = self._kommando()
        monstre = re.findall(r"tests/[\w.*-]+\.py", kommando)
        self.assertTrue(monstre, kommando)
        filer = sorted(p.name for p in (ROOT / "tests").glob("test_atlas_*.py"))
        self.assertGreater(len(filer), 0)
        udekket = [f for f in filer
                   if not any(fnmatch.fnmatch("tests/" + f, m) for m in monstre)]
        self.assertEqual(
            udekket, [],
            f"atlas test files that exist but no workflow runs: {udekket}\n"
            f"  the gate runs: {kommando}\n"
            "A test that is not run is documentation — the 50 reds of 56bbe317 "
            "were exactly this.")

    def test_push_og_pr_vokter_samme_filer(self):
        on = self._last_workflow()[True]
        self.assertEqual(on["push"]["paths"], on["pull_request"]["paths"],
                         "push and pull_request must guard the same files")
        for sti in ("schema/regime_nodes.jsonld", "docs/efc-atlas/**",
                    "scripts/maintenance/efc_atlas_generator.py",
                    "tests/test_atlas_*.py"):
            self.assertIn(sti, on["push"]["paths"])

    def _last_workflow(self) -> dict:
        import yaml
        return yaml.safe_load(
            (ROOT / ".github" / "workflows" / self.WF).read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
