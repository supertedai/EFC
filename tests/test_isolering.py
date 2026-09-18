"""Testene skal ikke avhenge av hvilke andre tester som kjørte før dem.

To målte måter en test i denne suiten kunne endre utfall av tilstand utenfor
seg selv (t_122b4022, 2026-09-18):

  1. REKKEFØLGE. `tests/test_growth_friction.py` importerer `efc`, som ligger
     under `src/`. Den ble bare importerbar fordi en fil som samles før den
     (`tests/test_cosmology_engine_bridges.py`, «c» < «g») importerer
     `efc_inference.engine.rotation`, og den modulen setter `src/` inn i
     sys.path som bivirkning av importen. Snu rekkefølgen, og samlingen
     stopper med en collection-feil. `pythonpath = ["src"]` i pyproject.toml
     gjør importen uavhengig av rekkefølgen.

  2. MILJØ. Git-kallene i `test_risiko_register.py` og `test_blast_radius.py`
     kjørte med det arvede miljøet: en GIT_DIR felte 9 tester, en lokal
     gitconfig med `commit.gpgsign` felte begge append_only-testene, og
     `diff.external` gjorde registerets append-only-gate blind. Begge filene
     skrubbet miljøet via `tests/_gitmiljo.py`.

Vaktene under kjører de berørte filene på nytt og krever at de er grønne i et
miljø som er laget for å velte dem. Kanarifuglene går først, slik at en vakt
som har mistet tennene melder det i stedet for å være grønn av ingenting.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
GIT_FILER = [
    "tests/test_risiko_register.py",
    "tests/test_blast_radius.py",
]

GIT = ["git", "-c", "user.name=t", "-c", "user.email=t@e.org"]


def _pytest(*args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "pytest", "-q",
                           "-p", "no:cacheprovider", *args],
                          cwd=ROT, env=env, capture_output=True, text=True, timeout=600)


def test_en_testfil_kan_samles_alene(tmp_path):
    """En fil som importerer `efc` må kunne kjøres uten hjelp av en annen fil.

    Før fiksen: `pytest tests/test_growth_friction.py` ga
    `ModuleNotFoundError: No module named 'efc'` — den var bare grønn fordi en
    annen testfil ble samlet først. Exit 4 fra pytest ER collection-feilen, så
    kravet er både exit 0 og minst én kjørt test.
    """
    r = _pytest("tests/test_growth_friction.py")
    assert r.returncode == 0, (
        f"filen kan ikke samles alene (exit {r.returncode}):\n{r.stdout[-3000:]}")
    siste = [ln for ln in r.stdout.splitlines() if ln.strip()][-1]
    assert " passed" in siste and not siste.startswith("0 passed"), \
        f"ingen test ble kjørt — da beviser dette ingenting: {siste!r}"


def _fiendtlig_miljo(tmp_path: Path) -> dict[str, str]:
    """Miljøet de to git-filene må tåle: et annet repo GIT_DIR peker på, og en
    lokal gitconfig som gjør en commit usignert og en rå diff tom."""
    annet = tmp_path / "annet-repo"
    annet.mkdir()
    subprocess.run(GIT + ["init", "-q"], cwd=annet, check=True,
                   env={**os.environ, "HOME": str(tmp_path)})
    gitconfig = tmp_path / "gitconfig"
    gitconfig.write_text("[commit]\n\tgpgsign = true\n"
                         "[diff]\n\texternal = /bin/true\n", encoding="utf-8")
    miljo = {k: v for k, v in os.environ.items()
             if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_CONFIG_GLOBAL",
                          "GIT_CONFIG", "GIT_CONFIG_SYSTEM")}
    miljo["GIT_DIR"] = str(annet / ".git")
    miljo["GIT_CONFIG_GLOBAL"] = str(gitconfig)
    return miljo


def test_de_git_baserte_filene_taaler_git_tilstand_utenfor_seg(tmp_path):
    miljo = _fiendtlig_miljo(tmp_path)

    # --- kanarifugl: er forgiftningen virksom? -----------------------------
    # Uten kanarifugl kunne denne vakten blitt grønn av at en kanal sluttet å
    # virke — og da måler den ingenting.
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("én\n", encoding="utf-8")
    b.write_text("to\n", encoding="utf-8")

    def _diff(m: dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "diff", "--no-index", str(a), str(b)],
                              env=m, capture_output=True, text=True)

    ren = {k: v for k, v in miljo.items() if k != "GIT_CONFIG_GLOBAL"}
    assert "-én" in _diff(ren).stdout, \
        "kanarifuglen er blind også uten forgiftning — da måler den feil ting"
    assert _diff(miljo).stdout.strip() == "", \
        "diff.external gjør ikke diffen tom — da er ikke miljøet fiendtlig"
    assert subprocess.run(["git", "config", "--get", "commit.gpgsign"],
                          env=miljo, capture_output=True, text=True
                          ).stdout.strip() == "true", \
        "den lokale gitconfig-en blir ikke lest — da er ikke miljøet fiendtlig"

    kanar = tmp_path / "kanar"
    kanar.mkdir()
    subprocess.run(GIT + ["init", "-q"], cwd=kanar, check=True,
                   env={**os.environ, "HOME": str(tmp_path)})
    gitdir = subprocess.run(GIT + ["rev-parse", "--git-dir"], cwd=kanar,
                            env=miljo, capture_output=True, text=True).stdout.strip()
    assert gitdir == str(tmp_path / "annet-repo" / ".git"), \
        f"GIT_DIR blir ikke lyttet til ({gitdir!r}) — da er ikke miljøet fiendtlig"

    # --- kravet: filene er grønne også her --------------------------------
    r = _pytest(*GIT_FILER, env=miljo)
    assert r.returncode == 0, (
        "en test i de git-baserte filene endret utfall av git-tilstanden "
        f"utenfor seg (exit {r.returncode}):\n{r.stdout[-4000:]}\n{r.stderr[-2000:]}")
