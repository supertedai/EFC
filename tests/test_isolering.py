"""The tests shall not depend on which other tests ran before them.

Two measured ways a test in this suite could change the outcome of state
outside itself (t_122b4022, 2026-09-18):

  1. ORDER. `tests/test_growth_friction.py` imports `efc`, which lives under
     `src/`. It was only importable because a file collected before it
     (`tests/test_cosmology_engine_bridges.py`, "c" < "g") imports
     `efc_inference.engine.rotation`, and that module puts `src/` into
     sys.path as a side effect of the import. Reverse the order, and
     collection stops with a collection error. `pythonpath = ["src"]` in
     pyproject.toml makes the import independent of the order.

  2. ENVIRONMENT. The git calls in `test_risiko_register.py` and
     `test_blast_radius.py` ran with the inherited environment: a GIT_DIR
     felled 9 tests, a local gitconfig with `commit.gpgsign` felled both
     append_only tests, and `diff.external` made the register's append-only
     gate blind. Both files scrub the environment through `tests/_gitmiljo.py`.

The guards below re-run the affected files and require them to be green in an
environment built to topple them. The canaries go first, so a guard that has
lost its teeth reports it instead of being green out of nothing.
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
    """A file that imports `efc` must be runnable without another file's help.

    Before the fix: `pytest tests/test_growth_friction.py` gave
    `ModuleNotFoundError: No module named 'efc'` — it was green only because
    another test file was collected first. Exit 4 from pytest IS the collection
    error, so the requirement is both exit 0 and at least one test run.
    """
    r = _pytest("tests/test_growth_friction.py")
    assert r.returncode == 0, (
        f"the file cannot be collected alone (exit {r.returncode}):\n{r.stdout[-3000:]}")
    siste = [ln for ln in r.stdout.splitlines() if ln.strip()][-1]
    assert " passed" in siste and not siste.startswith("0 passed"), \
        f"no test ran — so this proves nothing: {siste!r}"


def _fiendtlig_miljo(tmp_path: Path) -> dict[str, str]:
    """The environment the two git files must tolerate: another repo that
    GIT_DIR points at, plus a local gitconfig that makes a commit unsigned and
    a raw diff empty."""
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

    # --- canary: is the poisoning in force? --------------------------------
    # Without a canary this guard could go green because a channel stopped
    # working — and then it measures nothing.
    a, b = tmp_path / "a.txt", tmp_path / "b.txt"
    a.write_text("én\n", encoding="utf-8")
    b.write_text("to\n", encoding="utf-8")

    def _diff(m: dict[str, str]) -> subprocess.CompletedProcess:
        return subprocess.run(["git", "diff", "--no-index", str(a), str(b)],
                              env=m, capture_output=True, text=True)

    ren = {k: v for k, v in miljo.items() if k != "GIT_CONFIG_GLOBAL"}
    assert "-én" in _diff(ren).stdout, \
        "the canary is blind without the poisoning too — then it measures the wrong thing"
    assert _diff(miljo).stdout.strip() == "", \
        "diff.external does not empty the diff — then the environment is not hostile"
    assert subprocess.run(["git", "config", "--get", "commit.gpgsign"],
                          env=miljo, capture_output=True, text=True
                          ).stdout.strip() == "true", \
        "the local gitconfig is not being read — then the environment is not hostile"

    kanar = tmp_path / "kanar"
    kanar.mkdir()
    subprocess.run(GIT + ["init", "-q"], cwd=kanar, check=True,
                   env={**os.environ, "HOME": str(tmp_path)})
    gitdir = subprocess.run(GIT + ["rev-parse", "--git-dir"], cwd=kanar,
                            env=miljo, capture_output=True, text=True).stdout.strip()
    assert gitdir == str(tmp_path / "annet-repo" / ".git"), \
        f"GIT_DIR is not being listened to ({gitdir!r}) — then the environment is not hostile"

    # --- the requirement: the files are green here too ---------------------
    r = _pytest(*GIT_FILER, env=miljo)
    assert r.returncode == 0, (
        "a test in the git-based files changed the outcome of the git state "
        f"outside itself (exit {r.returncode}):\n{r.stdout[-4000:]}\n{r.stderr[-2000:]}")
