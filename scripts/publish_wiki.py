#!/usr/bin/env python3
"""
Publish docs/wiki/ to the GitHub Wiki (supertedai/EFC.wiki.git).

GitHub Wikis are a *separate* git repo. This script:

  1. Clones supertedai/EFC.wiki.git into a temp dir.
  2. Copies every docs/wiki/*.md there.
  3. Rewrites relative links (../public/..., ../../AGENTS.md, etc.)
     into absolute GitHub URLs so they resolve from the wiki context.
  4. Commits and pushes.

Run from repo root:

    python3 scripts/publish_wiki.py

Auth: uses whatever creds your local `git` is configured with. The wiki repo
must already exist — visit https://github.com/supertedai/EFC/wiki and create
the first page once, then this script takes over.

Env overrides:
    EFC_WIKI_URL   override the clone URL
    EFC_BLOB_BASE  override the GitHub blob base for link rewriting
                   (default: https://github.com/supertedai/EFC/blob/main)
    EFC_TREE_BASE  override the GitHub tree base
                   (default: https://github.com/supertedai/EFC/tree/main)
    EFC_DRY_RUN=1  do everything but `git push`
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
WIKI_SRC = REPO_ROOT / "docs" / "wiki"

WIKI_URL = os.environ.get(
    "EFC_WIKI_URL", "https://github.com/supertedai/EFC.wiki.git"
)
BLOB_BASE = os.environ.get(
    "EFC_BLOB_BASE", "https://github.com/supertedai/EFC/blob/main"
)
TREE_BASE = os.environ.get(
    "EFC_TREE_BASE", "https://github.com/supertedai/EFC/tree/main"
)
DRY_RUN = os.environ.get("EFC_DRY_RUN") == "1"

# Known wiki page stems (linked as ./<stem>.md); kept untouched so GitHub
# Wiki resolves them to sibling pages.
WIKI_PAGES = {
    "Home",
    "_Sidebar",
    "01-Theory",
    "02-Evidence",
    "03-Papers-by-Topic",
    "04-Reproduce",
    "05-For-AI-Agents",
    "06-Glossary",
}


def sh(*args: str, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print(f"  $ {' '.join(args)}  (cwd={cwd or '.'})")
    return subprocess.run(args, cwd=cwd, check=check)


def is_dir_link(target: str) -> bool:
    """Heuristic: treat trailing-slash or extensionless paths as directories."""
    if target.endswith("/"):
        return True
    tail = target.rsplit("/", 1)[-1]
    return "." not in tail


def rewrite_link(page_stem: str, link: str) -> str:
    """Rewrite one relative link so it resolves inside the wiki context."""
    # Leave external / anchor links alone.
    if link.startswith(("http://", "https://", "mailto:", "#")):
        return link
    # Split off an anchor.
    frag = ""
    if "#" in link:
        link, frag = link.split("#", 1)
        frag = "#" + frag
    # Sibling wiki page reference: ./Name.md or Name.md
    m = re.fullmatch(r"\./?([A-Za-z0-9_\-]+)\.md", link)
    if m and m.group(1) in WIKI_PAGES:
        return f"./{m.group(1)}.md{frag}"
    # Resolve anything else against the source file's location in the main repo.
    page_dir = WIKI_SRC  # all source pages live in docs/wiki/
    try:
        abs_target = (page_dir / link).resolve()
    except OSError:
        return link + frag
    try:
        rel = abs_target.relative_to(REPO_ROOT)
    except ValueError:
        return link + frag
    base = TREE_BASE if is_dir_link(link) or abs_target.is_dir() else BLOB_BASE
    return f"{base}/{rel.as_posix()}{frag}"


LINK_RE = re.compile(r"(\[[^\]]*\])\(([^)\s]+)\)")


def rewrite_text(page_stem: str, text: str) -> str:
    def repl(m: re.Match) -> str:
        label, link = m.group(1), m.group(2)
        return f"{label}({rewrite_link(page_stem, link)})"
    return LINK_RE.sub(repl, text)


def main() -> int:
    if not WIKI_SRC.exists():
        print(f"ERROR: {WIKI_SRC} does not exist.")
        return 1

    with tempfile.TemporaryDirectory(prefix="efc-wiki-") as tmp:
        tmp_path = Path(tmp)
        clone_dir = tmp_path / "wiki"
        print(f"[publish-wiki] cloning {WIKI_URL}")
        sh("git", "clone", "--depth", "1", WIKI_URL, str(clone_dir))

        print("[publish-wiki] rewriting + copying pages")
        written = []
        for src in sorted(WIKI_SRC.glob("*.md")):
            stem = src.stem
            new_text = rewrite_text(stem, src.read_text(encoding="utf-8"))
            dst = clone_dir / src.name
            dst.write_text(new_text, encoding="utf-8")
            written.append(src.name)
            print(f"  · {src.name}")

        sh("git", "add", *written, cwd=clone_dir)
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=clone_dir, capture_output=True, text=True, check=True,
        ).stdout.strip()
        if not status:
            print("[publish-wiki] wiki already up to date — nothing to commit.")
            return 0

        if DRY_RUN:
            print("[publish-wiki] EFC_DRY_RUN=1 — skipping commit + push.")
            sh("git", "diff", "--cached", "--stat", cwd=clone_dir)
            return 0

        # Uses the user's local git identity (user.name / user.email / signing).
        sh(
            "git", "commit",
            "-m", "docs(wiki): sync from docs/wiki/ in main repo",
            cwd=clone_dir,
        )
        print("[publish-wiki] pushing")
        sh("git", "push", "origin", "HEAD:master", cwd=clone_dir)

    print("[publish-wiki] done. Visit https://github.com/supertedai/EFC/wiki")
    print("[publish-wiki] NB: if a placeholder page exists, delete it from the UI.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
