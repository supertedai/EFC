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

# The measured read/import closure of the atlas reader and connector tests
# that efc-schema.yml now runs (t_995a7134). The workflow must both RUN these
# tests and WATCH these sources; otherwise a change to a watched file skips the
# gate and "green CI" becomes "absence of check" again.
REQUIRED_TESTS = ("tests/test_atlas_arbiter_konnektor.py",
                  "tests/test_atlas_oppslag.py")
REQUIRED_SOURCES = (
    "scripts/atlas_lesing.py",
    "scripts/atlas_oppgjoer.py",
    "scripts/atlas_arbiter_konnektor.py",
    "scripts/maintenance/arbiter_vakt_kjoer.py",
    "scripts/maintenance/_repo_tre.py",
    "efc_inference/arbiter/**",
    "efc_inference/engine/**",
    "efc_inference/core/cosmology_model.py",
    "efc_inference/core/__init__.py",
    "efc_inference/__init__.py",
    "schema/efc_fs8.*",
    "schema/regime_node.schema.json",
    "schema/regime_nodes.jsonld",
    "schema/nats_domener.snapshot.json",
    "docs/concepts.jsonld",
    "docs/ontology.jsonld",
    "docs/nats-koblingskart.md",
)


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

    def test_efc_schema_watches_sources_and_runs_atlas_tests(self):
        """t_995a7134: the atlas reader and connector tests ran in no CI workflow
        for five weeks, so green CI was absence of check, not validation. The
        efc-schema workflow must both run them and watch their sources; a change
        that breaks either must fail this test."""
        doc = self._load("efc-schema.yml")
        on = doc[True]
        self.assertIn("workflow_dispatch", on)
        push = on["push"]["paths"]
        pr = on["pull_request"]["paths"]
        self.assertEqual(set(push), set(pr),
                         "push.paths and pull_request.paths must watch the same files")

        # The pytest step is the one with `-m pytest`; `pip install` also
        # contains the word "pytest" (the pinned range), so that substring is
        # not enough.
        runs = [s["run"] for s in doc["jobs"]["schema"]["steps"] if "run" in s]
        pytest_runs = [r for r in runs if "-m pytest" in r]
        self.assertEqual(len(pytest_runs), 1, "exactly one pytest step expected")
        pytest_line = pytest_runs[0]

        for t in REQUIRED_TESTS:
            self.assertIn(t, pytest_line, f"{t} not in the pytest step")
            self.assertIn(t, push, f"{t} missing from push.paths")
            self.assertIn(t, pr, f"{t} missing from pull_request.paths")

        for s in REQUIRED_SOURCES:
            self.assertIn(s, push, f"{s} missing from push.paths")
            self.assertIn(s, pr, f"{s} missing from pull_request.paths")

        # Structural invariant (t_995a7134): no test may ever run unwatched.
        # Every tests/test_*.py token in the pytest step must also be watched by
        # both path blocks — the exact hole this card closes. This is a
        # self-discovering rule, not a remembered list: a test added to the
        # pytest step without a matching path fails here.
        pytest_test_tokens = set(t for t in pytest_line.split()
                                 if t.startswith("tests/test_"))
        self.assertGreater(len(pytest_test_tokens), 0,
                           "the pytest step names no tests")
        for t in sorted(pytest_test_tokens):
            self.assertIn(t, push,
                          f"{t} in the pytest step but missing from push.paths")
            self.assertIn(t, pr,
                          f"{t} in the pytest step but missing from pull_request.paths")

        # The schema gate and the bro-sync step are the point of this workflow;
        # a rewrite must not swap them out for the reader tests.
        self.assertTrue(any("efc_schema_check.py" in r for r in runs),
                        "C10 step lost")
        self.assertTrue(any("efc_bro_synk.py" in r for r in runs),
                        "bro-sync step lost")

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
        for name in ("efc-verify.yml", "efc-schema.yml", "atlas-verify.yml", "efc-page-consistency.yml", "efc-rootfile-consistency.yml", "efc-4b-register.yml", "efc-testsuite.yml"):
            text = (workflow_dir / name).read_text(encoding="utf-8")
            self.assertNotIn("git push", text, name)
            self.assertNotIn("git commit", text, name)
            self.assertNotIn("gh pr create", text, name)

    def test_ingen_pages_workflow(self):
        """t_0d65ccdf measured the legacy 'errored' builds as supersessions, not failures."""
        self.assertFalse((ROOT / ".github" / "workflows" / "pages.yml").exists())


class TheWholeSuiteRuns(unittest.TestCase):
    """t_89eea983: the job that runs the WHOLE suite must not be narrowed in silence.

    Measured 2026-09-18: four workflows ran pytest and named twelve test files
    between them, against a suite of 1123 tests. The consequence was measured,
    not assumed: tests/test_bro_konvensjon.py::test_hvert_skjema_felt_har_en_eier
    was RED on main (PR #555 added `open_questions` to the schema without
    updating the bridge convention) and no gate said so.

    This class is the OPPOSITE guard of the one that already existed. From
    before we know that "a test file that is not run is documentation": that
    guard catches a file falling out of a named command. It does NOT catch the
    command itself shrinking back to a handful of files, and that silence is
    what made the damage possible. So the shape of the command is locked here.
    """

    FIL = ROOT / ".github" / "workflows" / "efc-testsuite.yml"

    def _text(self) -> str:
        self.assertTrue(self.FIL.exists(),
                        "efc-testsuite.yml is missing — the whole suite has no CI gate")
        return self.FIL.read_text(encoding="utf-8")

    def _command(self) -> str:
        import re
        m = re.search(r"^\s*run: (python3 -m pytest .+)$", self._text(), re.M)
        self.assertIsNotNone(m, "no `python3 -m pytest` command in efc-testsuite.yml")
        assert m is not None
        return m.group(1).strip()

    def test_runs_from_the_root_without_exclusions(self):
        """Root collection, not `tests/`: `tests/` drops efc_inference/tests/ (123 tests)."""
        command = self._command()
        self.assertTrue(command.startswith("python3 -m pytest"),
                        f"the command must use the `-m` form, so CWD is on sys.path: {command}")
        for exclusion in ("tests/", "efc_inference/", "--ignore", "--deselect", "-k ", "--co"):
            self.assertNotIn(exclusion, command,
                             f"`{exclusion}` narrows the suite in silence: {command}")
        self.assertIn("-q", command, f"the suite must RUN, not merely be collected: {command}")

    def test_installs_from_requirements(self):
        """The dependencies have one source: requirements.txt, not a list of the job's own.

        The project itself is deliberately NOT installed: `pythonpath = ["src"]`
        in pyproject.toml already puts src on the path, so
        tests/test_growth_friction.py is collected without it (measured: 3
        passed with no package installed).
        """
        text = self._text()
        self.assertIn("requirements.txt", text,
                      "the job must install from requirements.txt, not from its own list")
        self.assertIn("pip install", text, "the job installs nothing")

    def test_no_paths_filter_and_it_runs_on_main(self):
        """A whole-suite gate must see every change — including on main."""
        try:
            import yaml
        except ImportError:
            self.skipTest("PyYAML not installed")
        on = yaml.safe_load(self._text())[True]
        self.assertIn("workflow_dispatch", on)
        self.assertEqual(on["push"]["branches"], ["main"])
        # `on: pull_request:` with no value parses as None, not as {}.
        pull = on.get("pull_request") or {}
        self.assertNotIn("paths", pull,
                         "a paths filter would make this something other than a whole-suite gate")
        self.assertNotIn("paths", on["push"],
                         "a paths filter would make this something other than a whole-suite gate")


if __name__ == "__main__":
    unittest.main()
