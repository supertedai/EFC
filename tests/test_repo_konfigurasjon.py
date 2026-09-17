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

import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]

# Pytests egne standarder for `norecursedirs`. Definerer man denne noekkelen,
# OVERSKRIVER man dem — derfor maa de liste seg opp igjen.
PYTEST_STANDARDER = ["*.egg", ".*", "_darcs", "build", "CVS", "dist",
                     "node_modules", "venv", "{arch}"]


def _les_ini_options(tekst: str | None = None) -> dict:
    """Les `norecursedirs` og `testpaths` fra pyproject.toml.

    Bruker `tomllib` der den finnes (Python 3.11+), som er det CI kjoerer og
    det utvikleren her kjoerer. Paa 3.9/3.10 — som `requires-python` tillater
    — finnes den ikke, og vi faller tilbake til aa lese de to noeklene
    direkte. Den veien er en FORENKLING med kjente grenser (se
    `TestParserensGrenser`), ikke en full TOML-parser.

    Foerste utgave haandskrev parsing ubetinget. Review runde 5 maalte at den
    ga feil svar paa `]` inne i en streng og paa escaped quotes — og at
    vernet ikke felt en gjeninnsetting av den, fordi `pyproject.toml` har
    doble fnutter. Begge er rettet: `tomllib` der den finnes, og en
    enhetstest som proever BEGGE fnutt-stiler direkte mot parseren.
    """
    if tekst is None:
        tekst = (REPO / "pyproject.toml").read_text(encoding="utf-8")
    try:
        import tomllib
        return (tomllib.loads(tekst).get("tool", {}).get("pytest", {})
                .get("ini_options", {}))
    except ModuleNotFoundError:
        pass
    if "[tool.pytest.ini_options]" not in tekst:
        return {}
    seksjon = tekst.split("[tool.pytest.ini_options]", 1)[1]
    stopp = re.search(r"^\[", seksjon, re.M)
    if stopp:
        seksjon = seksjon[:stopp.start()]
    ut: dict = {}
    for noekkel in ("testpaths", "norecursedirs"):
        m = re.search(rf"^{noekkel}\s*=\s*\[(.*?)\]", seksjon, re.M | re.S)
        if m:
            ut[noekkel] = [a or b for a, b in
                           re.findall(r'"([^"]*)"|\'([^\']*)\'', m.group(1))]
    return ut


@pytest.fixture(scope="module")
def ini_options() -> dict:
    return _les_ini_options()


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

class TestRotenVirker:
    """`pytest` fra roten skal ikke samle forskningskoden.

    MERK hva som maales her, og hva som IKKE maales. CI installerer bare
    `verify`-settet, ikke prosjektets egne kjerneavhengigheter (numpy,
    scipy, matplotlib, pandas). `efc_inference/tests` importerer scipy, saa
    «hele suiten kan samles» er et MILJOE-spoersmaal — ikke et
    konfigurasjonsspoersmaal.

    Foerste utgave av denne testen krevde at HELE samlingen lyktes. Den
    passerte lokalt (der alt er installert) og feilet i CI med ni
    collection-feil. Den maalte altsaa miljoeet sitt og kalte det
    konfigurasjon. Det som faktisk skal vernes her er at `norecursedirs`
    holder forskningskoden ute — det er en egenskap ved konfigurasjonen og
    er lik i alle miljoeer.
    """

    def _samling(self) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-m", "pytest", "--co", "-q"],
                              cwd=REPO, capture_output=True, text=True, timeout=180)

    def test_forskningskoden_samles_ikke(self) -> None:
        """Den presise maalingen: docs/ og pipelines/ skal ikke med."""
        p = self._samling()
        funnet = [linje for linje in p.stdout.splitlines()
                  if linje.startswith("docs/") or linje.startswith("pipelines/")]
        assert not funnet, (
            f"forskningskoden samles fra roten — `norecursedirs` virker ikke:\n"
            f"  {funnet[:5]}")

    def test_hovedsuiten_er_med(self) -> None:
        """...og `tests/` skal VAERE med. Utelatelse skal vaere valgt, ikke tilfeldig."""
        p = self._samling()
        assert any(linje.startswith("tests/") for linje in p.stdout.splitlines()), (
            f"ingen tester under tests/ ble samlet fra roten:\n{p.stdout[-400:]}")

    def test_efc_inference_testene_er_med(self) -> None:
        """De 123 som `testpaths` fjernet skal fortsatt samles.

        Kan feile paa manglende avhengigheter i miljoeet — men da sier vi
        DET, i stedet for aa late som konfigurasjonen er feil.
        """
        p = self._samling()
        linjer = p.stdout.splitlines()
        if "errors during collection" in p.stdout:
            mangler = [l for l in linjer if l.startswith("ERROR")]
            pytest.skip(
                f"miljoeet mangler avhengigheter, saa samlingen er ufullstendig "
                f"({len(mangler)} moduler). Det er ikke en konfigurasjonsfeil: "
                f"{mangler[:3]}")
        assert any(linje.startswith("efc_inference/tests/") for linje in linjer), (
            "efc_inference/tests samles ikke — de 123 testene er borte igjen")


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
        # `\s*` foran `>=` er ikke pynt: uten den faller `jsonschema >=4.18`
        # ut av BEGGE listene, og testen passerer fordi de er «like».
        # Maalt i review runde 3.
        return sorted(re.findall(r"^([A-Za-z][A-Za-z0-9_-]*)\s*>=", tekst[i:], re.M))

    def _ci_pakker(self) -> list[str]:
        import re
        tekst = (REPO / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"pip install --quiet (.+)", tekst)
        assert m, "fant ikke pip-installasjonen i efc-schema.yml"
        return sorted(re.findall(r'"([A-Za-z][A-Za-z0-9_-]*)\s*>=', m.group(1)))

    def test_listene_er_identiske(self) -> None:
        req, ci = self._req_pakker(), self._ci_pakker()
        # To tomme lister er ogsa «identiske». Uten denne kunne en
        # omformatering som skjulte alle pakker passere som samsvar.
        assert len(req) >= 4, (
            f"fant bare {len(req)} pakker i requirements.txt — leser "
            f"parseren feil formatering? {req}")
        assert len(ci) >= 4, f"fant bare {len(ci)} pakker i CI-listen: {ci}"
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


class TestVernetKjoererISelv:
    """Testen maa selv staa i CI-kommandoen — ellers er den ikke en gate.

    Review runde 3, BLOKKERER: `efc-schema.yml` kjorer tre navngitte
    testfiler, og `tests/test_repo_konfigurasjon.py` var ikke blant dem.
    Vernet mot at avhengighetslistene glir fra hverandre fantes altsaa, men
    kjorte ikke i den eneste kjøringen som betyr noe.

    Det er samme form som resten av denne PR-en: et vern som ser riktig ut
    og ikke maaler. En testfil som ikke kjoeres, er dokumentasjon.
    """

    def _ci_pytest_kommando(self) -> str:
        tekst = (REPO / ".github" / "workflows" / "efc-schema.yml").read_text(encoding="utf-8")
        m = re.search(r"python3 -m pytest ([^\n]+)", tekst)
        assert m, "fant ingen pytest-kommando i efc-schema.yml"
        return m.group(1)

    def test_denne_filen_staar_i_ci_kommandoen(self) -> None:
        kommand = self._ci_pytest_kommando()
        assert "test_repo_konfigurasjon.py" in kommand, (
            f"tests/test_repo_konfigurasjon.py kjoeres ikke i CI:\n"
            f"  CI kjorer: {kommand}\n"
            f"Da er ikke avhengighetsbindingen en gate — bare en lokal test.")

    def test_alle_navngitte_testfiler_finnes(self) -> None:
        """CI navngir filer eksplisitt. Forsvinner en, feiler CI stille."""
        for navn in self._ci_pytest_kommando().split():
            if navn.endswith(".py"):
                assert (REPO / navn).exists(), (
                    f"CI kjorer `{navn}`, men filen finnes ikke — "
                    f"pytest vil feile med «file or directory not found»")


class TestParserensGrenser:
    """Parseren skal proves DIREKTE, ikke gjennom filens tilfeldige format.

    Review runde 5: den gamle parseren ble gjeninnsatt og suiten passerte
    fortsatt — fordi `pyproject.toml` har doble fnutter, og den gamle
    parseren haandterer nettopp dem. Vernet felt altsaa bare kombinasjonen
    «skjor parser OG omformatert fil». Gjeninnfoerer noen den skjore
    parseren alene, sier testene ingenting.

    Denne testen gir parseren BEGGE formatene som tekst, uavhengig av hva
    filen inneholder.
    """

    TO_DOBLE = '[tool.pytest.ini_options]\ntestpaths = ["tests"]\nnorecursedirs = ["docs", "pipelines"]\n'
    TO_ENKLE = "[tool.pytest.ini_options]\ntestpaths = ['tests']\nnorecursedirs = ['docs', 'pipelines']\n"

    def test_doble_fnutter(self) -> None:
        d = _les_ini_options(self.TO_DOBLE)
        assert d.get("testpaths") == ["tests"], d
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_enkle_fnutter(self) -> None:
        """Den varianten som felte den gamle parseren."""
        d = _les_ini_options(self.TO_ENKLE)
        assert d.get("testpaths") == ["tests"], (
            f"enkeltfnutter ble ikke lest: {d}")
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
            '    "docs",  # forskningskoden\n'
            '    "pipelines",\n'
            ']\n')
        assert d.get("norecursedirs") == ["docs", "pipelines"], d

    def test_kant_i_streng(self) -> None:
        """`]` inne i en streng skal ikke avslutte listen.

        Review runde 5 maalte at den haandskrevne parseren feilet her.
        Med `tomllib` er dette riktig — og testen laaser det.
        """
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'norecursedirs = ["a]b", "tests"]\n')
        assert d.get("norecursedirs") == ["a]b", "tests"], (
            f"`]` inne i en streng ble feillest: {d}")

    def test_mange_elementer_paa_linja(self) -> None:
        d = _les_ini_options(
            '[tool.pytest.ini_options]\n'
            'norecursedirs = ["a", "b", "c", "d", "e"]\n')
        assert d.get("norecursedirs") == ["a", "b", "c", "d", "e"], d
