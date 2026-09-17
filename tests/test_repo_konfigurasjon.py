"""Vern om repoets testkonfigurasjon.

Maalt 2026-09-17: `pytest` fra repo-roten samlet ogsaa forskningskoden under
`docs/papers/` og `pipelines/`, som har egne avhengigheter (emcee,
efc.perturbation, run_pilot) og ga 10 collection-feil. Skillet mellom
hovedsuiten og forskningskoden fantes ikke skrevet ned noe sted, saa fire
reviewere brukte tid paa aa gjette riktig kommando.

Disse testene fanger at skillet forsvinner igjen — ikke fordi konfigurasjon
er viktig i seg selv, men fordi et manglende skille ser ut som en ødelagt
repo for den som ikke kjenner historien.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def pyproject() -> dict:
    with open(REPO / "pyproject.toml", "rb") as f:
        return tomllib.load(f)


class TestTestkonfigurasjonen:
    def test_testpaths_er_satt(self, pyproject: dict) -> None:
        opts = pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {})
        assert "testpaths" in opts, (
            "uten `testpaths` samler pytest forskningskoden under docs/papers/ "
            "og gir collection-feil fra repo-roten. Se pyproject.toml.")
        assert "tests" in opts["testpaths"], (
            f"testpaths skal peke paa tests/, ikke {opts['testpaths']}")

    def test_forskningskoden_er_utelatt(self, pyproject: dict) -> None:
        opts = pyproject.get("tool", {}).get("pytest", {}).get("ini_options", {})
        utelatt = opts.get("norecursedirs", [])
        for katalog in ("docs", "pipelines"):
            assert katalog in utelatt, (
                f"`{katalog}` skal staa i norecursedirs — koden der har egne "
                f"avhengigheter og hoerer ikke i hovedsuiten")

    def test_pytest_fra_roten_feiler_ikke(self) -> None:
        """Den faktiske maalingen: samlingen skal gaa gjennom fra roten."""
        p = subprocess.run(
            [sys.executable, "-m", "pytest", "--co", "-q"],
            cwd=REPO, capture_output=True, text=True, timeout=180)
        assert p.returncode == 0, (
            f"pytest fra repo-roten feiler i samlingen:\n"
            f"{p.stdout[-800:]}\n{p.stderr[-400:]}")
        # Sjekk den FAKTISKE feilmeldingen, ikke ordet «error» — det finnes
        # tester som heter `..._error`, og en sjekk som ikke skiller dem
        # feller paa navnet sitt eget innhold. Maalt: den felle skjedde.
        assert "errors during collection" not in p.stdout.lower(), (
            f"pytest samler noe det ikke skal:\n{p.stdout[-600:]}")
