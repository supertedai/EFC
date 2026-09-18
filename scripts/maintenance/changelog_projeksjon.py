#!/usr/bin/env python3
"""changelog_projeksjon — deterministic PUBLIC changelog from git history.

Principle (P0 t_26dd0ef5 + Morten 2026-09-17): the PUBLIC changelog is a
PROJECTION of one canonical source — the git history — but ONLY of changes
relevant to the public pages, written for HUMANS (English, readable
summaries). Two atlases exist by design: the internal atlas (everything:
house, world, ocean/biosphere/volcano) and the public EFC atlas (cosmos).
This changelog belongs to the PUBLIC pages only; internal-atlas work never
appears here — it has its own changelog.

Regeneration is deterministic: given last_processed_sha (stored in
changelog.json) and HEAD, this script always produces the same output.
The CI gate (efc-changelog-sync.yml) runs the script and FAILS if the
committed changelog diverges — so the changelog is de facto updated in the
same PR that changes public HTML, or CI goes red.

Language rule (Morten 2026-09-17): ALL EFC public content is English —
summaries are cleaned commit subjects. A landed commit subject cannot be
amended, so the English form of a non-English subject is DECLARED, keyed by
sha, in changelog_summaries.json (an input, reviewed like any other; the sha
stays the provenance). A subject the stopword list can see, and that no
declared English form exists for, is refused rather than projected.

Usage:  python3 scripts/maintenance/changelog_projeksjon.py

OWNERSHIP: these two files have exactly ONE writer, this script. Step 8 of
``efc_maintain.py`` (``efc_auto_changelog.py``) reports the working-tree diff
and writes neither, so that a second input — the working tree, next to the git
history — can never make the gate unsatisfiable. Measured 2026-09-18
(t_9cdf466e).
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _nav_helper import ensure_nav  # type: ignore
except ImportError:  # pragma: no cover — a missing helper must not block a write
    def ensure_nav(html: str, page: str | None = None) -> str:  # type: ignore[misc]
        return html

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HTML = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")
JSON = os.path.join(REPO, "docs", "validation-ledger", "data", "changelog.json")
# Declared English forms for commit subjects that are not English: the sha
# (12 hex) maps to the summary the public page shows. Input to the projection,
# not an edit of its output.
SUMMARIES = os.path.join(REPO, "scripts", "maintenance",
                         "changelog_summaries.json")

# The changelog files THEMSELVES are side-effects, not public content: a
# commit whose only public-path touch is the changelog is internal work
# (the old generator wrote the changelog on every commit — that loop must
# not make internal commits "public-relevant").
CHANGELOG_SELV = {
    "docs/public/EFC_Changelog.html",
    "docs/validation-ledger/data/changelog.json",
}

# High-precision Norwegian stopwords (avoids English false positives like
# "for", "den", "det"). One or more hits = Norwegian content.
NORSKE_ORD = re.compile(
    r"\b(skal|ikke|v[æe]re|v[æe]rt|ble|har|som|med|og|forutsier|konsistent|"
    r"prediksjonen|målt|stor|negativ|også|etter|men|mot|fra|til|endret|"
    r"oppdatert|påkrevd|rettet|æ|ø|å)\b",
    re.I)


def _git(*args: str) -> str:
    r = subprocess.run(["git", *args], capture_output=True, text=True,
                       cwd=REPO, timeout=30)
    if r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def _finnes(rev: str) -> bool:
    """True when rev resolves to a commit in THIS repository."""
    if not rev:
        return False
    r = subprocess.run(["git", "rev-parse", "--verify", "--quiet",
                        f"{rev}^{{commit}}"],
                       capture_output=True, text=True, cwd=REPO, timeout=30)
    return r.returncode == 0


def _los_opp_startpunkt(siste: str) -> str:
    """Resolve a projection start that EXISTS here.

    A recorded start can be unreachable even though it was real when it was
    written: last_processed_sha is stamped from the commit the projection ran
    on, and a squash-merge (or a deleted branch) leaves that commit on no
    branch at all. Measured 2026-09-17: main's pristine sha 72d91914… was
    squashed to 1b51a04e, and EVERY run — main and every PR — died with
    «fatal: Invalid revision range», so the gate could not be satisfied by any
    change. Falling back deterministically (and saying so) is what keeps the
    gate usable; the alternative is a gate nobody can turn green.
    """
    if _finnes(siste):
        return siste
    for kandidat in ("origin/main", "HEAD~1"):
        if _finnes(kandidat):
            ny = _git("rev-parse", kandidat)
            print(f"changelog_projeksjon: recorded start "
                  f"{siste[:12] if siste else '<empty>'} does not exist in this "
                  f"repository (squash-merge or deleted branch) — projecting "
                  f"from {kandidat} ({ny[:12]}) instead")
            return ny
    raise SystemExit("changelog_projeksjon: no usable start point in this repo")


def _i_historien(rev: str) -> bool:
    """True when rev is an ANCESTOR OF HEAD — the only start that yields a
    valid revision range.

    Object existence is not enough, and the difference is measured: a clone
    that once fetched a branch keeps the object after the branch is deleted,
    so `rev-parse` resolves it while `git log <rev>..HEAD` silently drops
    everything the side branch already contains. The same repository state
    would then project two different windows depending on what happened to be
    fetched, and the CI gate compares its own regeneration against the
    committed file.
    """
    if not _finnes(rev):
        return False
    r = subprocess.run(["git", "merge-base", "--is-ancestor", rev, "HEAD"],
                       capture_output=True, cwd=REPO, timeout=30)
    return r.returncode == 0


def _alder(rev: str) -> int:
    """Commit timestamp — the only ordering used to choose between two starts."""
    return int(_git("log", "-1", "--format=%at", rev))


def _siste_kjente_endring(cl: dict) -> str:
    """Newest entry in changes[] that HEAD still descends from.

    Used ONLY when the recorded start is unusable. The documented fallback
    (origin/main) looks forward, so on `main` its range is empty and every
    commit between the dead start and the tip is skipped without a word —
    measured 2026-09-18: four public-relevant commits (#459's maintenance
    sequence, the Test_Paper_Y artefact, #497 and #460) were never projected
    that way. The newest entry HEAD still descends from is a lower bound for
    «what the projection has already seen», and it is derived from the
    committed artifact plus the history, so the repair stays deterministic.
    """
    beste = ""
    for e in cl.get("changes", []) or []:
        sid = e.get("id") or e.get("sha")
        if sid and _i_historien(sid) and (not beste or _alder(sid) > _alder(beste)):
            beste = sid
    return beste


def _velg_startpunkt(cl: dict) -> str:
    """The start the projection must use now.

    A recorded start HEAD descends from is used untouched. An unusable one is
    repaired (documented, printed); when a changelog entry HEAD still descends
    from is OLDER than that repair, the older start is used instead, so the
    window the repair jumps over is projected rather than dropped in silence.
    """
    oppgitt = (cl.get("metadata") or {}).get("last_processed_sha") or ""
    if _i_historien(oppgitt):
        return oppgitt

    # Two different defects hide behind «unusable»: the recorded commit is gone
    # (squash-merge or deleted branch), or it exists in this clone but on a line
    # HEAD does not descend from. Only the first is what _los_opp_startpunkt
    # documents, and neither may yield a start HEAD does not descend from — so
    # whatever it returns is verified here.
    if _finnes(oppgitt):
        print(f"changelog_projeksjon: recorded start {oppgitt[:12]} exists in "
              f"this clone but HEAD does not descend from it (side branch) — "
              f"the range would silently drop what the side branch carries")
    reparert = _los_opp_startpunkt(oppgitt)
    if not _i_historien(reparert):
        reparert = ""
        for kandidat in ("origin/main", "HEAD~1"):
            if _i_historien(kandidat):
                reparert = _git("rev-parse", kandidat)
                break
    if not reparert:
        raise SystemExit("changelog_projeksjon: no start point HEAD descends "
                         "from (tried the recorded sha, origin/main, HEAD~1)")

    kjent = _siste_kjente_endring(cl)
    if kjent and _alder(kjent) < _alder(reparert):
        print(f"changelog_projeksjon: closing the window the repair would "
              f"skip — projecting from the newest entry HEAD still descends "
              f"from ({kjent[:12]}) instead of {reparert[:12]}")
        return kjent
    return reparert


def _deklarerte_summaries() -> dict:
    """sha -> declared English summary (input file; absent means none)."""
    if not os.path.exists(SUMMARIES):
        return {}
    with open(SUMMARIES, encoding="utf-8") as f:
        d = json.load(f)
    return {k: v for k, v in d.items() if not k.startswith("_")}


def _fil_kategori(f: str) -> str | None:
    """PUBLIC-relevant categories only — changelog side-effects excluded.

    Two atlases exist BY DESIGN (Morten 2026-09-17): the internal atlas
    (everything: house, world, ocean/biosphere/volcano nodes) and the public
    EFC atlas (cosmos). The PUBLIC changelog is a projection of changes
    relevant to the PUBLIC pages ONLY. Returns None for internal paths.
    """
    if f in CHANGELOG_SELV:
        return None  # side-effect, not content
    if f.startswith("docs/public/"):
        return "public_pages"
    if f.startswith("docs/papers/"):
        return "papers"
    if f.startswith("docs/validation-ledger/"):
        return "ledger_data"
    if f.startswith("public/"):
        return "statement_graph"
    return None


def _ren_tekst(melding: str) -> str:
    """Human-readable: strip backslash-escapes that raw commit subjects can
    carry (e.g. 'fix\\(x\\)'), collapse whitespace."""
    s = re.sub(r"\\([()\\])", r"\1", melding)
    return " ".join(s.split())[:140]


def _infra_bare(filer: list[str]) -> bool:
    """A change touching ONLY the changelog machinery needs no entry."""
    infra = {
        "scripts/maintenance/changelog_projeksjon.py",
        ".github/workflows/efc-changelog-sync.yml",
        "docs/public/EFC_Changelog.html",
        "docs/validation-ledger/data/changelog.json",
    }
    return bool(filer) and all(f in infra for f in filer)


def _hent_commits(siden: str) -> list[dict]:
    ut = _git("log", "--no-merges", "--format=%H%x1f%aI%x1f%s%x1e",
              f"{siden}..HEAD") if siden else ""
    if not ut:
        return []
    commits = []
    for blokk in ut.split("\x1e"):
        blokk = blokk.strip()
        if not blokk:
            continue
        sha, dato, melding = blokk.split("\x1f", 2)
        filer = _git("show", "--name-only", "--format=", sha).split()
        if _infra_bare(filer):
            continue
        kategorier = {}
        for f in filer:
            k = _fil_kategori(f)
            if k:
                kategorier[k] = kategorier.get(k, 0) + 1
        if not kategorier:
            # No public-relevant file touched — internal-only change,
            # invisible on the public pages, so no changelog entry here.
            continue
        commits.append({"sha": sha, "dato": dato[:10],
                        "melding": _ren_tekst(melding), "kategorier": kategorier})
    commits.reverse()  # oldest first
    return commits


def _summary(commit: dict, deklarert: dict) -> tuple[str, bool]:
    """The entry's English summary — or a refusal.

    A landed subject cannot be amended, so a non-English subject is translated
    ONCE, declared by sha in changelog_summaries.json and reviewed there; the
    projection never rewrites an entry on its own. Subjects the stopword list
    cannot see exist (measured 2026-09-18: «EFC: registrer proveniensavviket
    for de fire lyshastighet-DOI-ene» scores 0), which is the second reason the
    English form is declared rather than derived.
    """
    kort = commit["sha"][:12]
    if kort in deklarert:
        return deklarert[kort], True
    if NORSKE_ORD.search(commit["melding"]):
        raise SystemExit(
            f"changelog_projeksjon: {kort} has a Norwegian-looking subject and "
            f"no declared English form:\n    {commit['melding']}\n"
            f"    add \"{kort}\": \"<english summary>\" to "
            f"scripts/maintenance/changelog_summaries.json "
            f"(the sha stays the provenance).")
    return commit["melding"], False


def _hoved() -> int:
    if not os.path.exists(JSON):
        raise SystemExit("changelog.json missing")
    with open(JSON, encoding="utf-8") as f:
        cl = json.load(f)

    siste = _velg_startpunkt(cl)
    commits = _hent_commits(siste)
    if not commits:
        print("changelog_projeksjon: no new commits since last projection")
        return 0

    deklarert = _deklarerte_summaries()
    nye = []
    for c in commits:
        tekst, fra_deklarert = _summary(c, deklarert)
        post = {
            "date": c["dato"],
            "sha": c["sha"][:12],
            "summary": tekst,
            "categories": c["kategorier"],
            "id": c["sha"][:12],
        }
        if fra_deklarert:
            post["summary_source"] = "declared"
        nye.append(post)
    eksisterende = cl.get("changes", [])
    kjente_ider = {e.get("id") or e.get("sha") for e in eksisterende}
    # Newest first, like the page: the HTML list is built by pushing each <li>
    # onto the top (oldest first), so the JSON block is reversed to read the
    # same way. Only the block's internal order is affected.
    friske = [c for c in reversed(nye) if c["id"] not in kjente_ider]
    cl["changes"] = friske + eksisterende
    cl.setdefault("metadata", {})["last_processed_sha"] = commits[-1]["sha"]
    with open(JSON, "w", encoding="utf-8") as f:
        json.dump(cl, f, ensure_ascii=False, indent=2)

    # HTML: new <li> at the top of the changelog list, deterministic.
    with open(HTML, encoding="utf-8") as f:
        tekst = f.read()
    for c in nye:
        li = (f'<li><strong>{c["date"]}</strong> &mdash; {c["summary"]} '
              f'<span style="color:#6b7f9e;">({c["id"]})</span></li>')
        if li in tekst:
            continue
        # The changelog list sits AFTER the year heading — never in the
        # navigation's <ul> (the first <ul> in the file is the nav).
        anker = tekst.find("<h2>202")
        ul = tekst.find("<ul>", anker) if anker > 0 else -1
        if ul < 0:
            raise SystemExit("EFC_Changelog.html missing changelog <ul>")
        tekst = tekst[:ul + 4] + "\n  " + li + tekst[ul + 4:]
    # ONE canonical navbar form, shared with efc_navbar_sync.py: the helper
    # asks that module's render_nav() for THIS page, so the red active-page
    # marker survives the write. Without the page name the helper is a no-op
    # (by contract) and a drifted navbar would stay drifted.
    tekst = ensure_nav(tekst, HTML)
    with open(HTML, "w", encoding="utf-8") as f:
        f.write(tekst)

    print(f"changelog_projeksjon: {len(friske)} new changes projected "
          f"(last: {commits[-1]['sha'][:12]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(_hoved())
