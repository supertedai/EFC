"""Guarding the repo's test configuration.

Measured 2026-09-17, two rounds:

  1. `pytest` from the repo root collected the research code under
     `docs/papers/` and `pipelines/` — real tests for their papers, but with
     their own dependencies (emcee, efc.perturbation, run_pilot) that are not
     installed. 10 collection errors. Five reviewers spent time guessing the
     command.

  2. The first fix used `testpaths = ["tests"]`. Review measured that it
     removed 123 tests in `efc_inference/tests/` from the suite — 704
     collected became 542. That was not a fix, it was removing a fifth of
     the control to make the number look good.

These tests catch BOTH mistakes. The second is the most important one: a
solution that looks tidy and removes coverage in silence.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Pytest's own defaults for `norecursedirs`. Defining this key OVERRIDES
# them — which is why they must list themselves again.
PYTEST_STANDARDER = ["*.egg", ".*", "_darcs", "build", "CVS", "dist",
                     "node_modules", "venv", "{arch}"]


def _les_ini_options(text: str | None = None) -> dict:
    """Read `norecursedirs` and `testpaths` from pyproject.toml.

    Uses `tomllib` where it exists (Python 3.11+), which is what CI runs and
    what the developer here runs. On 3.9/3.10 — which `requires-python`
    allows — it does not exist, and we fall back to reading the two keys
    directly. That path is a SIMPLIFICATION with known limits (see
    `TestParserensGrenser`), not a full TOML parser.

    The first edition hand-wrote parsing unconditionally. Review round 5
    measured that it gave the wrong answer on `]` inside a string and on
    escaped quotes — and that the guard did not catch a reinstatement of it,
    because `pyproject.toml` uses double quotes. Both are fixed: `tomllib`
    where it exists, and a unit test that tries BOTH quote styles directly
    against the parser.
    """
    if text is None:
        text = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib
        return (tomllib.loads(text).get("tool", {}).get("pytest", {})
                .get("ini_options", {}))
    except ModuleNotFoundError:
        pass
    if "[tool.pytest.ini_options]" not in text:
        return {}
    section = text.split("[tool.pytest.ini_options]", 1)[1]
    stop = re.search(r"^\[", section, re.M)
    if stop:
        section = section[:stop.start()]
    out: dict = {}
    for key in ("testpaths", "norecursedirs"):
        m = re.search(rf"^{key}\s*=\s*\[(.*?)\]", section, re.M | re.S)
        if m:
            out[key] = [a or b for a, b in
                        re.findall(r'"([^"]*)"|\'([^\']*)\'', m.group(1))]
    return out


@pytest.fixture(scope="module")
def ini_options() -> dict:
    return _les_ini_options()


class TestForskjellskillet:
    def test_forskningskoden_er_utelatt(self, ini_options: dict) -> None:
        excluded = ini_options.get("norecursedirs", [])
        for directory in ("docs", "pipelines"):
            assert directory in excluded, (
                f"`{directory}` must stand in norecursedirs — the code there "
                f"has its own dependencies and does not belong in the main suite")

    def test_pytest_standardene_er_beholdt(self, ini_options: dict) -> None:
        """`norecursedirs` OVERRIDES the defaults — they must list themselves.

        Measured in review: without `.*` a temporary `tests/.probe/` was
        collected. That makes the suite depend on whatever happens to be on
        disk.
        """
        excluded = ini_options.get("norecursedirs", [])
        missing = [s for s in PYTEST_STANDARDER if s not in excluded]
        assert not missing, (
            f"norecursedirs is missing Pytest's defaults: {missing}. "
            f"Defining the key overrides them.")


class TestIngenDekningForsvinner:
    def test_testpaths_avgrenser_ikke(self, ini_options: dict) -> None:
        """`testpaths = ["tests"]` removed 123 tests from the suite.

        Measured: 704 collected before, 542 after. That is the trap this test
        exists for — a tidy configuration that removes coverage in silence.
        If you want to narrow the scope, do it with `norecursedirs` and only
        for directories that genuinely do not belong in the suite.
        """
        testpaths = ini_options.get("testpaths")
        assert testpaths is None, (
            f"`testpaths = {testpaths}` leaves out tests outside those "
            f"directories. `efc_inference/tests/` has 123 tests that belong in "
            f"the main suite. Use `norecursedirs` to exclude the research code "
            f"instead.")

class TestRotenVirker:
    """`pytest` from the root must not collect the research code.

    NOTE what is measured here, and what is NOT measured. CI installs only
    the `verify` set, not the project's own core dependencies (numpy, scipy,
    matplotlib, pandas). `efc_inference/tests` imports scipy, so "the whole
    suite can be collected" is an ENVIRONMENT question — not a configuration
    question.

    The first edition of this test required that the WHOLE collection
    succeeded. It passed locally (where everything is installed) and failed
    in CI with nine collection errors. It was therefore measuring its own
    environment and calling it configuration. What must actually be guarded
    here is that `norecursedirs` keeps the research code out — that is a
    property of the configuration and is the same in all environments.
    """

    def _collection(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-m", "pytest", "--co", "-q"],
                              cwd=REPO, capture_output=True, text=True, timeout=180)

    def test_forskningskoden_samles_ikke(self) -> None:
        """The precise measurement: docs/ and pipelines/ must not be in."""
        p = self._collection()
        found = [line for line in p.stdout.splitlines()
                 if line.startswith("docs/") or line.startswith("pipelines/")]
        assert not found, (
            f"the research code is collected from the root — `norecursedirs` "
            f"is not working:\n  {found[:5]}")

    def test_hovedsuiten_er_med(self) -> None:
        """...and `tests/` must BE in. Exclusion must be chosen, not accidental."""
        p = self._collection()
        assert any(line.startswith("tests/") for line in p.stdout.splitlines()), (
            f"no tests under tests/ were collected from the root:\n{p.stdout[-400:]}")

    def test_efc_inference_testene_er_med(self) -> None:
        """The 123 that `testpaths` removed must still be collected.

        May fail on missing dependencies in the environment — but then we say
        THAT, instead of pretending the configuration is wrong.
        """
        p = self._collection()
        lines = p.stdout.splitlines()
        if "errors during collection" in p.stdout:
            missing = [l for l in lines if l.startswith("ERROR")]
            pytest.skip(
                f"the environment is missing dependencies, so the collection is "
                f"incomplete ({len(missing)} modules). That is not a "
                f"configuration error: {missing[:3]}")
        assert any(line.startswith("efc_inference/tests/") for line in lines), (
            "efc_inference/tests is not collected — the 123 tests are gone again")


class TestAvhengighetslisteneErISynk:
    """`requirements.txt` and the CI install CLAIM they are identical.

    Measured 2026-09-17: both files say so in a comment — requirements.txt:
    "CI gate C10 + tests; .github/workflows/efc-schema.yml installs the
    same", and the workflow: "pinned ranges, same as requirements.txt".
    Neither of them kept that claim updated.

    Review round 2 found it: `emcee` was put in `[project.optional-
    dependencies].verify`, but CI installs the packages EXPLICITLY — it does
    not read the extra. Without this test the two lists would have drifted
    apart again, and the comments would still have claimed they were equal.
    """

    def _req_packages(self) -> list[str]:
        import re
        text = (REPO / "requirements.txt").read_text(encoding="utf-8")
        i = text.index("Verification (CI gate C10")
        # The `\s*` before `>=` is not decoration: without it `jsonschema >=4.18`
        # falls out of BOTH lists, and the test passes because they are "equal".
        # Measured in review round 3.
        return sorted(re.findall(r"^([A-Za-z][A-Za-z0-9_-]*)\s*>=", text[i:], re.M))

    def _ci_packages(self) -> list[str]:
        import re
        text = (REPO / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"pip install --quiet (.+)", text)
        assert m, "found no pip install in efc-schema.yml"
        return sorted(re.findall(r'"([A-Za-z][A-Za-z0-9_-]*)\s*>=', m.group(1)))

    def test_listene_er_identiske(self) -> None:
        req, ci = self._req_packages(), self._ci_packages()
        # Two empty lists are also "identical". Without this, a reformatting
        # that hid every package could pass as agreement.
        assert len(req) >= 4, (
            f"found only {len(req)} packages in requirements.txt — is the "
            f"parser reading the wrong formatting? {req}")
        assert len(ci) >= 4, f"found only {len(ci)} packages in the CI list: {ci}"
        assert req == ci, (
            f"requirements.txt and the CI install have drifted apart.\n"
            f"  requirements.txt: {req}\n"
            f"  efc-schema.yml  : {ci}\n"
            f"Both files claim in a comment that they are equal. Update both.")

    def test_emcee_er_i_begge(self) -> None:
        """The concrete finding from review round 2.

        `efc_inference/runs/research_mcmc.py` imports `emcee` at module
        import, so collection of `efc_inference/tests/` fails without it.
        """
        for name, packages in (("requirements.txt", self._req_packages()),
                               ("efc-schema.yml", self._ci_packages())):
            assert "emcee" in packages, (
                f"`emcee` is missing from {name} — efc_inference/tests cannot "
                f"be collected without it")


class TestVernetKjoererISelv:
    """The test must itself stand in the CI command — otherwise it is not a gate.

    Review round 3, BLOCKING: `efc-schema.yml` runs three named test files,
    and `tests/test_repo_konfigurasjon.py` was not among them. The guard
    against the dependency lists drifting apart therefore existed, but did
    not run in the one run that matters.

    That is the same shape as the rest of this PR: a guard that looks right
    and does not measure. A test file that is not run is documentation.
    """

    def _ci_pytest_command(self) -> str:
        text = (REPO / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"python3 -m pytest ([^\n]+)", text)
        assert m, "found no pytest command in efc-schema.yml"
        return m.group(1)

    def test_denne_filen_staar_i_ci_kommandoen(self) -> None:
        command = self._ci_pytest_command()
        assert "test_repo_konfigurasjon.py" in command, (
            f"tests/test_repo_konfigurasjon.py is not run in CI:\n"
            f"  CI runs: {command}\n"
            f"Then the dependency binding is not a gate — only a local test.")

    def test_alle_navngitte_testfiler_finnes(self) -> None:
        """CI names files explicitly. If one disappears, CI fails silently."""
        for name in self._ci_pytest_command().split():
            if name.endswith(".py"):
                assert (REPO / name).exists(), (
                    f"CI runs `{name}`, but the file does not exist — "
                    f"pytest will fail with «file or directory not found»")


class TestParserensGrenser:
    """The parser must be tried DIRECTLY, not through the file's accidental format.

    Review round 5: the old parser was reinstated and the suite still passed
    — because `pyproject.toml` uses double quotes, and the old parser handles
    exactly those. The guard therefore only caught the combination "fragile
    parser AND reformatted file". If someone reinstates the fragile parser
    alone, the tests say nothing.

    This test gives the parser BOTH formats as text, regardless of what the
    file contains.
    """

    TO_DOBLE = '[tool.pytest.ini_options]\ntestpaths = ["tests"]\nnorecursedirs = ["docs", "pipelines"]\n'
    TO_ENKLE = "[tool.pytest.ini_options]\ntestpaths = ['tests']\nnorecursedirs = ['docs', 'pipelines']\n"

    def test_doble_fnutter(self) -> None:
        d = _les_ini_options(self.TO_DOBLE)
        assert d.get("testpaths") == ["tests"], d
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_enkle_fnutter(self) -> None:
        """The variant that caught the old parser."""
        d = _les_ini_options(self.TO_ENKLE)
        assert d.get("testpaths") == ["tests"], (
            f"single quotes were not read: {d}")
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_blandede_fnutter(self) -> None:
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'testpaths = ["tests"]\n'
            "norecursedirs = ['docs', 'pipelines']\n")
        assert d.get("testpaths") == ["tests"], d
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_kommentar_inni_listen(self) -> None:
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'norecursedirs = [\n'
            '    "docs",  # the research code\n'
            '    "pipelines",\n'
            ']\n')
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_kant_i_streng(self) -> None:
        """`]` inside a string must not terminate the list.

        Review round 5 measured that the hand-written parser failed here.
        With `tomllib` this is correct — and the test locks it in.
        """
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'norecursedirs = ["a]b", "tests"]\n')
        assert d.get("norecursedirs") == ["a]b", "tests"], (
            f"`]` inside a string was misread: {d}")

    def test_mange_elementer_paa_linja(self) -> None:
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'norecursedirs = ["a", "b", "c", "d", "e"]\n')
        assert d.get("norecursedirs") == ["a", "b", "c", "d", "e"], d
