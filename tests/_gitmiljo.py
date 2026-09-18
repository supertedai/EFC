"""Et git-miljø som ikke arves fra kjøringen rundt testen.

Testene som lager sitt eget lille git-repo i `tmp_path` er ikke isolert bare
fordi repoet deres er det. `git` leser også omgivelsen:

  * GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE / GIT_COMMON_DIR peker git på et
    ANNET repo enn katalogen kallet kjører i. En test (eller en wrapper) som
    setter én av dem, endrer da hva alle senere git-kall gjør.
  * ~/.gitconfig kan inneholde `commit.gpgsign`, `init.defaultBranch` og
    `diff.external` — den siste gjør en diff tom, altså usynlig.

Målt 2026-09-18: med en arvet GIT_DIR feilet 9 tester i test_risiko_register.py
og test_blast_radius.py; med `commit.gpgsign = true` i en lokal gitconfig falt
begge append_only-testene. Utfallet skal komme fra fixturen, ikke fra maskinen.

Bruk: `env=RENT_GIT` eller `env=rent_gitmiljo(tmp_path / "hjem")` på HVERT
git-kall i testen.
"""
from __future__ import annotations

import os
from pathlib import Path

# Variabler som flytter hvilket repo git snakker med.
AMBARTE_REPO_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
)

# Variabler som kan bytte ut eller overstyre konfigurasjonen.
AMBARTE_CONFIG_VARS = ("GIT_CONFIG", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")


def rent_gitmiljo(hjem: Path) -> dict[str, str]:
    """Miljøet et git-kall i en test skal bruke.

    Hjemmemappa er en fersk katalog under `tmp_path`, så ~/.gitconfig og
    XDG-konfigurasjonen til den som kjører suiten er utenfor rekkevidde.
    """
    hjem = Path(hjem)
    (hjem / ".config").mkdir(parents=True, exist_ok=True)
    miljo = {k: v for k, v in os.environ.items()
             if k not in AMBARTE_REPO_VARS + AMBARTE_CONFIG_VARS}
    miljo["HOME"] = str(hjem)
    miljo["XDG_CONFIG_HOME"] = str(hjem / ".config")
    miljo["GIT_CONFIG_NOSYSTEM"] = "1"
    miljo["GIT_TERMINAL_PROMPT"] = "0"
    return miljo
