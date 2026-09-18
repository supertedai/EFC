"""Which files are the repo? One answer, not three.

Measured 2026-09-17 (kanban t_12494ba1): three instruments answered each for
itself by walking the disk — `Path(".").rglob("*")`, `root.rglob("*")`,
`os.walk(root)`. In the main clone they hit `.worktrees/`: gitignored
(.gitignore), but present on disk. Three tests that were green in CI went red
locally because of it — "private address leaks", "legacy binding", "$id is not
the served identifier" — because the instrument read the worktree and not the
source.

The rule here: in a git tree the answer is `git ls-files -z`, i.e. what is
actually published, and it is the same in all clones. If the tree is not a
git tree (a rig in a temp directory, a `git archive` export), the disk is
read, and the ignored directories are skipped by name.

Only the index is read, not `--others`: an answer such as "no private address
in the tree" or "one binding" must hold for what has been added to git,
otherwise the answer depends on what happens to lie unadded in the worktree.
The consequence is that a NEW file must be `git add`-ed before the tool sees
it.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path, PurePosixPath

# Directories that are never part of the repo, however the tree is read.
# `.worktrees/` is the measured one: work surfaces under the repo, ignored
# by git, but fully visible to a disk walk.
IGNORERTE_KATALOGER = frozenset({
    ".git", ".worktrees", "node_modules", "__pycache__", ".venv", "venv",
})


def git_indeks(root: Path) -> list[str] | None:
    """Tracked paths, relative to `root`, or None.

    None means "this is not a git tree I can read" — not "empty tree" — and
    that is what separates the two sources of an answer. `-z` because a path
    with a space or a non-ASCII letter is a path, and text mode quotes both.
    """
    try:
        ut = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                            capture_output=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    if ut.returncode != 0:
        return None
    stier = [p for p in ut.stdout.decode("utf-8", "surrogateescape").split("\0") if p]
    # AN EMPTY LIST IS AN ANSWER — not "no index".
    #
    # The first edition returned `stier or None`. A valid, empty git tree
    # was then treated as "not a git tree", `filer()` fell back to a disk
    # walk, and UNTRACKED files were read — against the premise that the
    # git tree is authoritative. Reproduced in review 2026-09-17:
    # `git init` + one untracked file with private content was returned.
    #
    # The docstring above already said that None means "not a git tree I can
    # read" and not "empty tree". The code did the opposite of what it said.
    return stier


def _fra_disk(root: Path, ignorerte: frozenset) -> list[str]:
    ut: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in ignorerte)
        for fn in filenames:
            ut.append((Path(dirpath) / fn).relative_to(root).as_posix())
    return ut


def filer(root: Path, suffixes=None, skip_dirs=(), skip_files=()) -> list[Path]:
    """The files in the tree, sorted by relative path.

    `suffixes` is a set of endings (None = all), `skip_dirs` and
    `skip_files` are the tool's own exceptions — the ignored directories
    above always apply in addition. Files that are in the index but deleted
    from the disk are skipped: this function answers with files that can be
    read.
    """
    root = Path(root)
    ignorerte = IGNORERTE_KATALOGER | set(skip_dirs)
    utelatte = set(skip_files)
    indeks = git_indeks(root)
    if indeks is None:
        relative = _fra_disk(root, ignorerte)
    else:
        relative = [p for p in indeks
                    if not any(del_ in ignorerte for del_ in PurePosixPath(p).parts)]
    ut = []
    for rel in relative:
        if rel in utelatte:
            continue
        if suffixes is not None and PurePosixPath(rel).suffix not in suffixes:
            continue
        p = root / rel
        if p.is_file():
            ut.append(p)
    return sorted(ut, key=lambda q: q.relative_to(root).as_posix())
