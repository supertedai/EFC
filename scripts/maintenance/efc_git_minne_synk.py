#!/usr/bin/env python3
"""efc_git_minne_synk.py — git → Opus-minne synk (komponent 3, del 1: detektor).

Leser nye EFC-relevante git-commits siden siste synk (markør i
.claude/efc_git_minne_synk.json), trekker ut strukturerte oppsummeringer
(ny DOI-pakke: doi + tittel + paper_type; ellers endringskategori), og
skriver dem som append-only JSONL til data/inntak/git_minne_synk.jsonl +
avanserer markøren. Idempotent: re-kjøring gir ingen nye linjer.

Retain til hindsight-banken (mcp__hindsight_efc__retain) skjer i et SEPARAT
steg — en Opus-sesjon via cron — fordi MCP-en ikke er kallbar fra et
frittstående skript.

Bruk:
  efc_git_minne_synk.py --dry-run            # vis hva som ville synkes, skriv ingenting
  efc_git_minne_synk.py                      # skriv kø + avanser markør
  efc_git_minne_synk.py --since <sha>        # eksplisitt start (testing)
"""

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MARKER = REPO / ".claude" / "efc_git_minne_synk.json"
QUEUE = REPO / "data" / "inntak" / "git_minne_synk.jsonl"

# Stier som bærer EFC-innsikt verdt å speile til minnet
RELEVANT_PREFIXES = (
    "docs/papers/efc/",
    "docs/validation-ledger/",
    "figshare/",
    "docs/public/",
)


def _git(*args: str) -> str:
    r = subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=REPO, timeout=30
    )
    return r.stdout.strip() if r.returncode == 0 else ""


def _last_sha() -> str:
    if MARKER.exists():
        try:
            return json.loads(MARKER.read_text(encoding="utf-8")).get("last_sha", "")
        except Exception:
            return ""
    return ""


def _fetch_commits(since: str) -> list[dict]:
    out = _git(
        "log", "--no-merges", "--format=%H%x1f%aI%x1f%s",
        f"{since}..origin/main", "--", *RELEVANT_PREFIXES,
    )
    commits = []
    for line in out.split("\n"):
        if not line.strip():
            continue
        parts = line.split("\x1f")
        if len(parts) < 3:
            continue
        sha, date, subject = parts[0], parts[1], parts[2]
        files = _git("show", "--name-only", "--format=", sha).split()
        commits.append({"sha": sha, "date": date[:10], "subject": subject, "files": files})
    commits.reverse()  # eldste først
    return commits


def _classify(files: list[str]) -> tuple[list[str], list[str]]:
    categories = set()
    new_papers = set()
    for f in files:
        if f.startswith("docs/papers/efc/"):
            categories.add("papers")
            rel = f[len("docs/papers/efc/"):]
            if "/" in rel:
                new_papers.add(rel.split("/")[0])
        elif f.startswith("docs/validation-ledger/"):
            categories.add("ledger")
        elif f.startswith("figshare/"):
            categories.add("doi-registry")
        elif f.startswith("docs/public/"):
            categories.add("public-pages")
    return sorted(categories), sorted(new_papers)


def _paper_summary(slug: str) -> dict:
    idx = REPO / "docs" / "papers" / "efc" / slug / "index.json"
    if not idx.exists():
        return {}
    try:
        d = json.loads(idx.read_text(encoding="utf-8"))
        return {
            "doi": d.get("doi", ""),
            "title": d.get("title", ""),
            "paper_type": d.get("paper_type", ""),
        }
    except Exception:
        return {}


def _build_entries(commits: list[dict]) -> list[dict]:
    entries = []
    for c in commits:
        cats, new_papers = _classify(c["files"])
        e = {"sha": c["sha"][:12], "date": c["date"], "subject": c["subject"], "categories": cats}
        if new_papers:
            e["papers"] = [{"slug": s, **_paper_summary(s)} for s in new_papers]
        entries.append(e)
    return entries


def main() -> int:
    dry = "--dry-run" in sys.argv
    since = _last_sha()
    if "--since" in sys.argv:
        i = sys.argv.index("--since")
        if i + 1 < len(sys.argv):
            since = sys.argv[i + 1]
    if not since:
        since = _git("rev-parse", "origin/main~1")

    commits = _fetch_commits(since)
    if not commits:
        print(f"git-minne-synk: ingen nye EFC-relevante commits siden {since[:12]}")
        return 0

    entries = _build_entries(commits)
    if dry:
        print(f"[dry-run] {len(entries)} oppføring(er) siden {since[:12]}:")
        for e in entries:
            print(f"  - {e['sha']}  {e['subject'][:70]}  [{','.join(e['categories'])}]")
            for p in e.get("papers", []):
                print(f"      DOI: {p.get('doi') or '(ingen)'}  |  {(p.get('title') or '')[:60]}")
        return 0

    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE, "a", encoding="utf-8") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(json.dumps({"last_sha": commits[-1]["sha"]}, indent=2) + "\n")
    print(
        f"git-minne-synk: {len(entries)} oppføring(er) skrevet til "
        f"{QUEUE.relative_to(REPO)}; markør -> {commits[-1]['sha'][:12]}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
