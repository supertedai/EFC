"""Vern om repoets testkonfigurasjon.

Maalt 2026-09-17, to runder:

  1. `pytest` fra repo-roten samlet forskningskoden under `docs/papers/` og
     `pipelines/` — ekte tester for sine papirer, men med egne avhengigheter
     (emcee, efc.perturbation, run_pilot) som ikke er installert. 10
     collection-feil. Fem reviewere brukte tid paa aa gjette kommandoen.

  2. Foerste fiks brukte `testpaths = ["tests"]`. Review maalte at det
     fjernet 123 tester i `efc_inference/tests/` fra suiten — 704 samlet ble
     542. Det var ikke en fiks, det var aa fjerne en femtedel av kontrollen
     for aa faa tallet til aa se bra ut.

Disse testene fanger BEGGE feilene. Den andre er den viktigste: en losning
som ser ryddig ut og fjerner dekning i stillhet.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Pytests egne standarder for `norecursedirs`. Definerer man denne noekkelen,
# OVERSKRIVER man dem — derfor maa de liste seg opp igjen.
PYTEST_STANDARDER = ["*.egg", ".*", "_darcs", "build", "CVS", "dist",
                     "node_modules", "venv", "{arch}"]


@pytest.fixture(scope="module")
def ini_options() -> dict:
    with open(REPO / "pyproject.toml", "rb") as f:
        return tomllib.load(f).get("tool", {}).get("pytest", {}).get("ini_options", {})


class TestForskjellskillet:
    def test_forskningskoden_er_utelatt(self, ini_options: dict) -> None:
        utelatt = ini_options.get("norecursedirs", [])
        for katalog in ("docs", "pipelines"):
            assert katalog in utelatt, (
                f"`{katalog}` skal staa i norecursedirs — koden der har egne "
                f"avhengigheter og hoerer ikke i hovedsuiten")

    def test_pytest_standardene_er_beholdt(self, ini_options: dict) -> None:
        """`norecursedirs` OVERSKRIVER standardene — de maa liste seg opp.

        Maalt i review: uten `.*` ble en midlertidig `tests/.probe/` samlet.
        Det gjoer suiten avhengig av hva som tilfeldigvis ligger paa disken.
        """
        utelatt = ini_options.get("norecursedirs", [])
        mangler = [s for s in PYTEST_STANDARDER if s not in utelatt]
        assert not mangler, (
            f"norecursedirs mangler Pytests standarder: {mangler}. "
            f"Definerer man noekkelen, overskriver man dem.")


class TestIngenDekningForsvinner:
    def test_testpaths_avgrenser_ikke(self, ini_options: dict) -> None:
        """`testpaths = ["tests"]` fjernet 123 tester fra suiten.

        Maalt: 704 samlet foer, 542 etter. Det er den fella denne testen
        finnes for — en ryddig konfigurasjon som fjerner dekning i stillhet.
        Vil man avgrense, skal det gjoeres med `norecursedirs` og bare for
        kataloger som faktisk ikke hoerer i suiten.
        """
        testpaths = ini_options.get("testpaths")
        assert testpaths is None, (
            f"`testpaths = {testpaths}` utelater tester utenfor de katalogene. "
            f"`efc_inference/tests/` har 123 tester som hoerer i hovedsuiten. "
            f"Bruk `norecursedirs` for aa utelate forskningskoden i stedet.")

    def test_efc_inference_testene_er_med(self) -> None:
        """Den konkrete maalingen: testene i efc_inference/tests skal samles.

        Tallet er ikke pinnet — det vokser naar avhengigheter installeres
        (maalt: 123 uten `emcee`, 125 med). Det som pinnes er at samlingen
        LYKKES og at den er stor nok til aa romme dem.

        Merk: sjekken gaar paa «errors during collection», ikke paa ordet
        «error» — det finnes tester med `error` i navnet, og en sjekk som
        ikke skiller dem feller paa sitt eget innhold. Jeg gikk i den fellen
        to ganger; derfor står den her.
        """
        p = subprocess.run([sys.executable, "-m", "pytest", "--co", "-q",
                            "efc_inference/tests"],
                           cwd=REPO, capture_output=True, text=True, timeout=180)
        assert p.returncode == 0, (
            f"efc_inference/tests samles ikke:\n{p.stdout[-600:]}\n{p.stderr[-300:]}")
        assert "errors during collection" not in p.stdout.lower(), p.stdout[-600:]
        tall = 0
        for ord_ in p.stdout.split():
            if ord_.isdigit() and int(ord_) > tall:
                tall = int(ord_)
        assert tall >= 120, (
            f"bare {tall} tester samles i efc_inference/tests — suiten har "
            f"mistet dekning der")


class TestRotenVirker:
    def test_pytest_fra_roten_feiler_ikke(self) -> None:
        """Den faktiske maalingen: samlingen skal gaa gjennom fra roten."""
        p = subprocess.run([sys.executable, "-m", "pytest", "--co", "-q"],
                           cwd=REPO, capture_output=True, text=True, timeout=180)
        assert p.returncode == 0, (
            f"pytest fra repo-roten feiler i samlingen:\n"
            f"{p.stdout[-800:]}\n{p.stderr[-400:]}")
        # Sjekk den FAKTISKE feilmeldingen, ikke ordet «error» — det finnes
        # tester som heter `..._error`, og en sjekk som ikke skiller dem
        # feller paa navnet sitt eget innhold. Maalt: den felle skjedde.
        assert "errors during collection" not in p.stdout.lower(), (
            f"pytest samler noe det ikke skal:\n{p.stdout[-600:]}")

    def test_samlingen_er_stor_nok(self) -> None:
        """Et gulv. Faller tallet, er noe blitt usynlig for suiten."""
        p = subprocess.run([sys.executable, "-m", "pytest", "--co", "-q"],
                           cwd=REPO, capture_output=True, text=True, timeout=180)
        tall = 0
        for ord_ in p.stdout.split():
            if ord_.isdigit() and int(ord_) > tall:
                tall = int(ord_)
        assert tall >= 650, (
            f"bare {tall} tester samles fra roten — maalt 667 den 2026-09-17. "
            f"Er noe blitt utelatt?")


class TestAvhengighetslisteneErISynk:
    """`requirements.txt` og CI-installasjonen PASTAAR de er identiske.

    Maalt 2026-09-17: begge filene sier det i en kommentar —
    requirements.txt: «CI gate C10 + tests; .github/workflows/efc-schema.yml
    installs the same», og workflowen: «pinned ranges, same as
    requirements.txt». Ingen av dem holdt den paastanden oppdatert.

    Review runde 2 fant det: `emcee` ble lagt i `[project.optional-
    dependencies].verify`, men CI installerer pakkene EKSPLISITT — den leser
    ikke ekstraen. Uten denne testen ville de to listene glidd fra hverandre
    igjen, og kommentarene ville fortsatt paastatt at de var like.
    """

    def _req_pakker(self) -> list[str]:
        import re
        tekst = (REPO / "requirements.txt").read_text(encoding="utf-8")
        i = tekst.index("Verification (CI gate C10")
        return sorted(re.findall(r"^([A-Za-z][A-Za-z0-9_-]*)>=", tekst[i:], re.M))

    def _ci_pakker(self) -> list[str]:
        import re
        tekst = (REPO / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"pip install --quiet (.+)", tekst)
        assert m, "fant ikke pip-installasjonen i efc-schema.yml"
        return sorted(re.findall(r'"([A-Za-z][A-Za-z0-9_-]*)>=', m.group(1)))

    def test_listene_er_identiske(self) -> None:
        req, ci = self._req_pakker(), self._ci_pakker()
        assert req == ci, (
            f"requirements.txt og CI-installasjonen har glidd fra hverandre.\n"
            f"  requirements.txt: {req}\n"
            f"  efc-schema.yml  : {ci}\n"
            f"Begge filene paastaar i en kommentar at de er like. Oppdater begge.")

    def test_emcee_er_i_begge(self) -> None:
        """Det konkrete funnet fra review runde 2.

        `efc_inference/runs/research_mcmc.py` importerer `emcee` ved
        modulimport, saa samling av `efc_inference/tests/` feiler uten den.
        """
        for navn, pakker in (("requirements.txt", self._req_pakker()),
                             ("efc-schema.yml", self._ci_pakker())):
            assert "emcee" in pakker, (
                f"`emcee` mangler i {navn} — efc_inference/tests kan ikke "
                f"samles uten den")
