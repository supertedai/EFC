"""A git environment that is not inherited from the run around the test.

The tests that build their own little git repo in `tmp_path` are not isolated
just because their repo is. `git` also reads the environment around it:

  * GIT_DIR / GIT_WORK_TREE / GIT_INDEX_FILE / GIT_COMMON_DIR point git at a
    DIFFERENT repo than the directory the call runs in. A test (or a wrapper)
    that sets one of them then changes what every later git call does.
  * ~/.gitconfig can carry `commit.gpgsign`, `init.defaultBranch` and
    `diff.external` — the last one makes a diff empty, i.e. invisible.

Measured 2026-09-18: with an inherited GIT_DIR, 9 tests in
test_risiko_register.py and test_blast_radius.py failed; with
`commit.gpgsign = true` in a local gitconfig both append_only tests fell. The
outcome shall come from the fixture, not from the machine.

Use: `env=RENT_GIT` or `env=rent_gitmiljo(tmp_path / "hjem")` on EVERY git
call in the test.
"""
from __future__ import annotations

import os
from pathlib import Path

# Variables that move which repo git talks to.
AMBARTE_REPO_VARS = (
    "GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
)

# Variables that can swap out or override the configuration.
AMBARTE_CONFIG_VARS = ("GIT_CONFIG", "GIT_CONFIG_GLOBAL", "GIT_CONFIG_SYSTEM")


def rent_gitmiljo(hjem: Path) -> dict[str, str]:
    """The environment a git call in a test shall use.

    The home directory is a fresh directory under `tmp_path`, so ~/.gitconfig
    and the XDG configuration of whoever runs the suite are out of reach.
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
