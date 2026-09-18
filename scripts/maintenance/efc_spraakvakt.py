#!/usr/bin/env python3
"""efc_spraakvakt.py — the repo-wide language gate (English only in EFC content).

WHY THIS EXISTS
---------------
Measured 2026-09-17 (card t_537ab101): the only language check in CI was one
inline step inside .github/workflows/efc-changelog-sync.yml, and it read the
newest 30 entries of docs/validation-ledger/data/changelog.json. Nothing read
docs/validation-ledger/**, docs/public/**, public/**, scripts/** or tests/**:
6312 stopword hits lived in 131 of those files with no gate looking at them.
A Norwegian commit SUBJECT was only caught indirectly, by landing in the
changelog, and only while it sat inside the projection window -- a violation
ages out of that window silently (measured on 7c7e30b7, which meanwhile made
changelog-sync unsatisfiable; see card t_f610686f).

WHAT IT DOES
------------
1. ``--skann`` (default)  File content over the declared guarded paths,
   compared with the declared baseline. A file above its recorded count, or a
   guarded file with hits that the baseline does not know, is a finding. Debt
   below the baseline is reported as slack so the baseline can be tightened,
   never as a failure.

   ``--referanse REV`` measures the scan against that revision instead of the
   record. The failure rule then belongs to the change under test -- a PR is not
   responsible for Norwegian that landed on its base branch before it, which is
   the wedged-gate failure this card was written about -- and debt above the
   record is reported on every run, never failed. The reference tree is read
   through ``git archive`` and scanned with the same scanner, so there is no
   second rule about the same words. A reference that cannot be read is exit 2
   (could not measure): falling back to the record would blame this change for
   the base branch's debt, which is the failure this mode exists to prevent.
2. ``--commits RANGE``    The commit SUBJECTS in the range. No baseline and no
   window: this is the source-level rule, and it is where a violation is
   cheapest to fix (in the commit that creates it). It is the repair for the
   aging-out window, not a second opinion about it.
3. ``--changelog``        The check the CI step performs, with the window
   DECLARED (default 30, ``--vindu N``) and the number of entries outside it
   printed: the cap is a window, not a rule, and the report says so instead of
   leaving it implicit.

DETECTOR RULE (declared, so its false positives are not a surprise)
-------------------------------------------------------------------
The vocabulary is ``scripts/maintenance/spraak-ord.json`` -- the same list the
changelog step inlines; ``tests/test_spraakvakt.py`` fails when the two drift
apart. Two exclusions apply, both measured on this tree:

  R1 boundaries. A match counts only when neither neighbour is [A-Za-z0-9_-],
     so CSS classes, element ids and kebab/snake identifiers are not read as
     prose. Measured: the class token ``badge-med`` alone produced 10 hits in
     docs/public/EFC_Gap_Analysis.html under a word-boundary rule, because a
     hyphen is a word boundary.
  R2 labels. Exact matches of the declared uppercase labels MED and MEDIUM are
     English severity labels, not prose. Measured: 7 hits in the same file.

R1+R2 take that file from 17 hits to 0 and leave every lowercase prose hit in
place. The number is re-runnable: it is asserted in the test suite.

DECLARED LIMITS (what this gate does NOT see)
---------------------------------------------
* Hyphen-adjacent prose is read as an identifier, so a hyphen-joined Norwegian
  compound is invisible. That is the price of R1; it is declared, and locked by
  a test, rather than discovered later.
* The vocabulary is narrow on purpose (see ``kjente_hull`` in spraak-ord.json):
  function words that collide with English or with identifiers are absent, and
  prose built only from those is invisible.
* Only the guarded paths are scanned. Every area outside them is printed with
  its measured count under ``--grenser``, with a reason when the scope table
  names it and with the counted ``UG`` note when it does not. An area outside
  the guard is a scope question, so it is reported, not failed -- but it is
  never silent.
* Files that do not decode as UTF-8 are skipped and counted. A skipped file
  whose extension is a text format is a finding instead, because a text
  artefact the gate could not read is a hole and a PNG is not.
* The commit mode sees only the commits in the range it is handed. A violation
  merged before this gate existed is not caught retroactively.
* The residual is ratcheted, not zero. The baseline is the record of what is
  left, per file; ``filer`` in it is the work queue, not a permission.

JSON keys are English: this gate is new, nothing consumes its --json yet, and
the language rule is newer than the sibling checkers' Norwegian keys.

USAGE
-----
    python3 scripts/maintenance/efc_spraakvakt.py                  # report
    python3 scripts/maintenance/efc_spraakvakt.py --json           # machine
    python3 scripts/maintenance/efc_spraakvakt.py --grenser        # the limits
    python3 scripts/maintenance/efc_spraakvakt.py --commits origin/main..HEAD
    python3 scripts/maintenance/efc_spraakvakt.py --changelog --vindu 30
    python3 scripts/maintenance/efc_spraakvakt.py --oppdater-baseline

Exit: 0 = no findings; 1 = findings; 2 = could not measure (a measurement that
could not be made is a finding, not an empty answer).
"""
from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VOCAB = ROOT / "scripts" / "maintenance" / "spraak-ord.json"
BASELINE = ROOT / "scripts" / "maintenance" / "spraak-baseline.json"
CHANGELOG = ROOT / "docs" / "validation-ledger" / "data" / "changelog.json"

# The guarded paths. Every other area of the tree is declared below, with the
# reason it is out of scope, and its measured count is printed by --grenser.
GUARDED = (
    "docs/validation-ledger/",
    "docs/public/",
    "public/",
    "scripts/",
    "tests/",
)

# area -> class, and class -> reason. Longest prefix wins. An area that is not
# declared here and has hits is reported as an undeclared scope, which fails.
OUT_OF_SCOPE = (
    ("docs/papers/", "U1"),
    ("docs/efc-atlas/", "U2"),
    ("schema/", "U2"),
    ("jsonld/", "U2"),
    ("meta/", "U2"),
    ("meta-graph/", "U2"),
    ("efc_inference/", "U3"),
    ("pipelines/", "U3"),
    ("src/", "U3"),
    ("tools/", "U3"),
    ("integrations/", "U3"),
    ("simple/", "U3"),
    ("shared/", "U3"),
    ("api/", "U3"),
    ("config/", "U3"),
    ("data/", "U3"),
    ("evidence/", "U3"),
    ("reports/", "U3"),
    ("logs/", "U3"),
    ("figshare/", "U3"),
    ("schemas/", "U3"),
    ("auth/", "U3"),
    ("theory/", "U3"),
    ("methodology/", "U3"),
    ("governance/", "U3"),
    (".github/", "U4"),
    (".claude/", "U4"),
    ("docs/", "U5"),
    ("<root>", "U6"),
)

REASONS = {
    "U1": ("published paper packages, each carrying its own DOI: a language "
           "change there rewrites a published artefact, which is a release "
           "decision and not a gate"),
    "U2": ("the node bank and its generated mirrors (regime_nodes.jsonld writes "
           "the internal atlas -- its own header says the bank is the truth and "
           "the atlas is its mirror); the bank's own cards own its text, and "
           "gating the mirror would put the rule in two places"),
    "U3": ("the engine library, research code and governance: separate suites, "
           "separate cards, no part of the public ledger surface this gate "
           "guards"),
    "U4": ("CI and editor configuration plus root files; .github/ is where this "
           "rule's vocabulary is inlined, so scanning it would scan the rule"),
    "U5": ("the rest of the served docs/ surface (bridge conventions, the NATS "
           "map, internal notes, the notebook, the weekly scan report): "
           "internal working documents whose own owner decides their language, "
           "outside the ledger and public-page surfaces this gate guards"),
    "U6": ("repository root files -- the contracts and build configuration "
           "(AGENTS.md, README.md, OPERATING_MODEL.md, Makefile, "
           "pyproject.toml, layer.yaml, .gitignore). Their language is a "
           "governance decision on the repository's front door, not a "
           "checker's"),
    "UG": ("top-level areas outside the guard that the table above does not "
           "name. They are printed with their measured count on every run, "
           "and are not a failure: an area outside the guard is a scope "
           "question, not a language violation in the guard. Guard it or name "
           "it here if it should be"),
}

# The rule's own vocabulary is the one declared exemption: every entry in it is
# a stopword by construction. The count is printed on every run, so the
# exemption can never be silent, and the test suite locks the set to this path.
EXEMPT = {
    "scripts/maintenance/spraak-ord.json":
        "the rule's own vocabulary; every entry is a stopword by construction",
}

SKIP_DIRS = {".git", ".worktrees", "__pycache__", "node_modules", ".venv",
             ".mypy_cache", ".pytest_cache", ".ruff_cache"}

# A file that does not decode as UTF-8 is skipped and COUNTED. A skipped file
# with one of these extensions is a finding instead: a text artefact the gate
# could not read is a hole, a PNG is not.
TEXT_EXT = {".json", ".jsonld", ".md", ".html", ".htm", ".py", ".yaml", ".yml",
            ".sh", ".css", ".js", ".mjs", ".txt", ".csv", ".bib", ".cff",
            ".toml", ".ini", ".cfg", ".sql", ".tex", ".xml", ".ipynb", ".log",
            ".tsv", ".dockerfile"}


# --------------------------------------------------------------------------
# the detector
# --------------------------------------------------------------------------

def vocabulary_path(root: Path) -> Path:
    """The vocabulary lives with the rule, so a scanned tree carries its own."""
    return VOCAB if root == ROOT else root / "scripts" / "maintenance" / "spraak-ord.json"


def read_vocabulary(path: Path | None = None) -> tuple[list[str], set[str]]:
    path = path or VOCAB
    data = json.loads(path.read_text(encoding="utf-8"))
    words = [w for w in (data.get("ord") or []) if isinstance(w, str) and w]
    if not words:
        raise ValueError(f"empty vocabulary in {path}")
    labels = {w for w in (data.get("etiketter") or []) if isinstance(w, str)}
    return words, labels


def build_pattern(words: list[str]) -> re.Pattern:
    """R1: identifier-safe boundaries instead of a word boundary.

    A hyphen is a word boundary, which is exactly why the class token
    ``badge-med`` read as Norwegian. Excluding [A-Za-z0-9_-] on both sides is
    the rule; its cost is declared in the module docstring.
    """
    return re.compile(r"(?<![A-Za-z0-9_\-])(" + "|".join(words) +
                      r")(?![A-Za-z0-9_\-])", re.IGNORECASE)


def hits(text: str, pattern: re.Pattern, labels: set[str]) -> list[str]:
    """Every stopword match that survives R1 and R2, in order."""
    return [m.group(0) for m in pattern.finditer(text)
            if m.group(0) not in labels]


# --------------------------------------------------------------------------
# the tree
# --------------------------------------------------------------------------

def tree_files(root: Path) -> list[str]:
    """Relative posix paths to read.

    Tracked files come from ``git ls-files -z`` and untracked-but-not-ignored
    files are added, so a file being written right now is seen too. A directory
    that is not a git repo (the tests use a synthetic tree) is walked.
    """
    def _git(*args: str) -> list[str] | None:
        try:
            r = subprocess.run(["git", *args], cwd=root, capture_output=True,
                               text=True, timeout=120)
        except (OSError, subprocess.SubprocessError):
            return None
        if r.returncode != 0:
            return None
        return [f for f in r.stdout.split("\0") if f]

    listed = _git("ls-files", "-z")
    if listed is None:
        return sorted(p.relative_to(root).as_posix()
                      for p in root.rglob("*")
                      if p.is_file() and not any(d in p.parts for d in SKIP_DIRS))
    others = _git("ls-files", "--others", "--exclude-standard", "-z") or []
    return sorted({f for f in listed + others if f})


def area_of(rel: str) -> str:
    declared = [p for p, _ in OUT_OF_SCOPE] + list(GUARDED)
    best = ""
    for prefix in declared:
        if rel.startswith(prefix) and len(prefix) > len(best):
            best = prefix
    if best:
        return best
    return "<root>" if "/" not in rel else rel.split("/", 1)[0] + "/"


def is_guarded(rel: str) -> bool:
    return any(rel.startswith(p) for p in GUARDED)


def scan_tree(root: Path, words: list[str], labels: set[str],
              files: list[str] | None = None) -> dict:
    pattern = build_pattern(words)
    counts: dict[str, int] = {}
    unreadable_text: list[str] = []
    skipped_binary: list[str] = []
    exempt: list[dict] = []
    areas: dict[str, int] = {}
    for rel in (tree_files(root) if files is None else files):
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            if is_guarded(rel):
                if Path(rel).suffix.lower() in TEXT_EXT:
                    unreadable_text.append(rel)
                else:
                    skipped_binary.append(rel)
            continue
        found = len(hits(text, pattern, labels))
        area = area_of(rel)
        areas[area] = areas.get(area, 0) + found
        if not found:
            continue
        if rel in EXEMPT:
            exempt.append({"file": rel, "count": found, "reason": EXEMPT[rel]})
            continue
        if is_guarded(rel):
            counts[rel] = found
    return {"counts": counts, "unreadable_text": unreadable_text,
            "skipped_binary": skipped_binary, "exempt": exempt, "areas": areas}


def reference_counts(root: Path, rev: str, words: list[str],
                     labels: set[str]) -> tuple[dict[str, int] | None, str]:
    """Per-file counts in a reference revision, read through ``git archive``.

    The failure rule has to belong to the change under test. A PR is not
    responsible for Norwegian that landed on its base branch before it, and a
    gate that blames every PR for the base branch is the wedged-gate failure
    this card was written about (measured 2026-09-17 on 7c7e30b7, which made
    changelog-sync unsatisfiable for everyone).

    So the reference answers "did THIS change grow the guard", while the record
    (the committed baseline) answers "how much debt is there" and is reported on
    every run. The reference is read from a git archive, so the same scanner
    reads it and there is no second rule.
    """
    try:
        ls = subprocess.run(["git", "ls-tree", "--name-only", rev], cwd=root,
                            capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"the reference could not be read: {exc}"
    if ls.returncode != 0:
        return None, ("the reference could not be read: "
                      + ls.stderr.strip()[:200])
    tops = set(ls.stdout.split())
    prefixes = [p for p in GUARDED if p.split("/", 1)[0] in tops]
    if not prefixes:
        return {}, ""
    try:
        r = subprocess.run(["git", "archive", "--format=tar", rev, "--", *prefixes],
                           cwd=root, capture_output=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        return None, f"the reference could not be read: {exc}"
    if r.returncode != 0:
        return None, ("the reference could not be read: "
                      + r.stderr.decode("utf-8", "replace").strip()[:200])
    tmp = tempfile.mkdtemp(prefix="spraak-referanse-")
    try:
        with tarfile.open(fileobj=io.BytesIO(r.stdout)) as tar:
            try:
                tar.extractall(path=tmp, filter="data")
            except TypeError:            # Python before 3.12
                tar.extractall(path=tmp)
        return scan_tree(Path(tmp), words, labels)["counts"], ""
    except (tarfile.TarError, OSError) as exc:
        return None, f"the reference could not be read: {exc}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def compare(counts: dict[str, int], expected: dict[str, int],
            present: set[str] | None = None) -> dict:
    """The ratchet: growth is a finding, a reduction is slack, a deleted file
    is an expectation to drop.

    ``expected`` is either the reference revision (what the change is measured
    against) or the committed record (what the tree is measured against).
    ``present`` is the set of paths still in the tree, so a file whose hits went
    to zero can be told apart from a file that was removed.
    """
    new, slack, gone = [], [], []
    for rel in sorted(set(counts) | set(expected)):
        found = counts.get(rel, 0)
        if rel not in expected:
            if found:
                new.append({"file": rel, "count": found, "expected": None,
                            "excess": found})
            continue
        want = expected[rel]
        if found > want:
            new.append({"file": rel, "count": found, "expected": want,
                        "excess": found - want})
        elif found < want:
            if present is not None and rel not in present:
                gone.append(rel)
            else:
                slack.append({"file": rel, "count": found, "expected": want,
                              "freed": want - found})
    return {"new": new, "slack": slack, "gone": gone}


def unlisted_areas(areas: dict[str, int]) -> list[dict]:
    """Areas outside the guard and outside the declared table, with hits.

    INFO, not a finding: it is a scope question, printed with its measured
    count so the scope can be decided instead of assumed.
    """
    declared = {p for p, _ in OUT_OF_SCOPE} | set(GUARDED) | {"<root>"}
    return [{"area": a, "count": n} for a, n in sorted(areas.items())
            if a not in declared and n]


# --------------------------------------------------------------------------
# the three modes
# --------------------------------------------------------------------------

def read_record(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return {f: int(v.get("count") or 0)
            for f, v in (data.get("files") or {}).items()
            if isinstance(v, dict)}


def run_scan(root: Path, baseline_path: Path,
             reference: str | None = None) -> tuple[int, dict]:
    words, labels = read_vocabulary(vocabulary_path(root))
    files = tree_files(root)
    scanned = scan_tree(root, words, labels, files)
    record = read_record(baseline_path)

    ref_counts, ref_error = (None, "")
    if reference:
        ref_counts, ref_error = reference_counts(root, reference, words, labels)
        if ref_counts is None:
            # Measuring against the record here would blame this change for
            # whatever the base branch did -- the failure this mode exists to
            # prevent. So it is reported as a measurement that could not be
            # made, exactly like any other failed measurement in this house.
            return 2, {"mode": "scan", "root": str(root),
                       "reference": reference, "reference_error": ref_error,
                       "error": ref_error}
    expected = ref_counts if ref_counts is not None else record
    measured_against = ("the reference " + str(reference)
                        if ref_counts is not None else "the committed record")

    verdict = compare(scanned["counts"], expected, set(files))
    unlisted = unlisted_areas(scanned["areas"])
    delta = [{"file": f,
              "count": scanned["counts"].get(f, 0),
              "recorded": record.get(f)}
             for f in sorted(set(scanned["counts"]) | set(record))
             if scanned["counts"].get(f, 0) != record.get(f, 0)]
    limits = []
    if reference and ref_counts is not None:
        limits.append("the failure rule is relative to the reference: debt "
                      "above the record is reported, not failed, because it "
                      "belongs to the base revision and not to this change")
    return 1 if (verdict["new"] or scanned["unreadable_text"]) else 0, {
        "mode": "scan",
        "root": str(root),
        "guard": list(GUARDED),
        "files_in_guard": sum(1 for f in files if is_guarded(f)),
        "reference": reference,
        "reference_error": ref_error or None,
        "measured_against": measured_against,
        "hits_per_area": {a: n for a, n in sorted(scanned["areas"].items()) if n},
        "new": verdict["new"],
        "slack": verdict["slack"],
        "gone_from_expectation": verdict["gone"],
        "record_delta": delta,
        "undeclared_growth": [d for d in delta if (d["recorded"] or 0) < d["count"]],
        "unlisted_areas": unlisted,
        "unreadable_text": scanned["unreadable_text"],
        "skipped_binary": scanned["skipped_binary"],
        "exempt": scanned["exempt"],
        "debt": {"files": len(scanned["counts"]),
                 "hits": sum(scanned["counts"].values())},
        "record": {"files": len(record), "hits": sum(record.values())},
        "declared_limits": limits,
    }


def _git(root: Path, *args: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["git", *args], cwd=root, capture_output=True,
                           text=True, timeout=300)
    except (OSError, subprocess.SubprocessError) as exc:
        return 2, f"git could not be run: {exc}"
    return r.returncode, (r.stdout if r.returncode == 0 else r.stderr)


def run_commits(root: Path, commit_range: str) -> tuple[int, dict]:
    words, labels = read_vocabulary(vocabulary_path(root))
    pattern = build_pattern(words)
    rc, out = _git(root, "log", "--no-merges", "--format=%H%x1f%s",
                   commit_range)
    if rc != 0:
        return 2, {"mode": "commits", "range": commit_range,
                   "error": f"range could not be resolved: {out.strip()[:200]}"}
    found, total = [], 0
    for line in out.splitlines():
        if not line.strip():
            continue
        total += 1
        sha, _, subject = line.partition("\x1f")
        words_found = hits(subject, pattern, labels)
        if words_found:
            found.append({"sha": sha[:12], "subject": subject,
                          "matches": words_found})
    return (1 if found else 0), {
        "mode": "commits",
        "range": commit_range,
        "commits_read": total,
        "hits": found,
        "declared_limits": [
            "Merge commits carry no authored subject and are skipped (--no-merges).",
            "Only the commits inside the range are read: a violation merged "
            "before this gate existed is not caught retroactively.",
            "This mode has no lookback window -- the range IS the window, which "
            "is the repair for the 30-entry cap in the changelog step.",
        ],
    }


def run_changelog(root: Path, window: int) -> tuple[int, dict]:
    words, labels = read_vocabulary(vocabulary_path(root))
    pattern = build_pattern(words)
    path = CHANGELOG if root == ROOT else root / "docs" / "validation-ledger" / "data" / "changelog.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return 2, {"mode": "changelog", "error": f"could not read {path}: {exc}"}
    entries = data.get("changes") or []
    found = [{"index": i, "summary": e.get("summary", ""),
              "matches": hits(e.get("summary", ""), pattern, labels)}
             for i, e in enumerate(entries[:window])
             if hits(e.get("summary", ""), pattern, labels)]
    return (1 if found else 0), {
        "mode": "changelog",
        "window": window,
        "entries": len(entries),
        "entries_outside_window": max(0, len(entries) - window),
        "hits": found,
        "declared_limits": [
            f"The newest {window} entries are checked; the other "
            f"{max(0, len(entries) - window)} are NOT, which is the "
            f"silent-aging-out this gate's --commits mode repairs.",
            "An entry is verbatim commit text; the repair is an English SOURCE, "
            "never an edited or translated entry (the changelog is a projection).",
        ],
    }


def run_limits(root: Path) -> dict:
    words, labels = read_vocabulary(vocabulary_path(root))
    scanned = scan_tree(root, words, labels)
    areas = []
    for prefix in GUARDED:
        areas.append({"area": prefix, "scope": "guarded",
                      "hits": scanned["areas"].get(prefix, 0), "reason": None})
    for prefix, cls in OUT_OF_SCOPE:
        areas.append({"area": prefix, "scope": "out_of_scope",
                      "hits": scanned["areas"].get(prefix, 0),
                      "reason": REASONS[cls]})
    for extra in unlisted_areas(scanned["areas"]):
        areas.append({"area": extra["area"], "scope": "out_of_scope",
                      "hits": extra["count"], "reason": REASONS["UG"]})
    return {
        "mode": "limits",
        "vocabulary": ["ord", "etiketter", "kjente_hull"],
        "exception": EXEMPT,
        "areas": areas,
        "unlisted_areas_with_hits": unlisted_areas(scanned["areas"]),
        "unreadable_text": scanned["unreadable_text"],
        "skipped_binary": scanned["skipped_binary"],
        "declared_limits": [
            "Hyphen-adjacent prose reads as an identifier and is invisible (R1).",
            "The vocabulary is a stopword list, not a language detector; prose "
            "built only from absent function words is invisible.",
            "Only the guarded paths are scanned; the areas above carry the "
            "measured count of what is left outside.",
            "The commit mode sees only the range it is handed.",
            "The residual is ratcheted, not zero: the baseline is the record.",
        ],
    }


def write_baseline(root: Path, baseline_path: Path) -> dict:
    words, labels = read_vocabulary(vocabulary_path(root))
    scanned = scan_tree(root, words, labels)
    try:
        previous = json.loads(baseline_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        previous = {}
    keep = {f: v for f, v in (previous.get("files") or {}).items()}
    rc, sha = _git(root, "rev-parse", "--short", "HEAD")
    files = {}
    for rel in sorted(scanned["counts"]):
        entry = {"count": scanned["counts"][rel]}
        if isinstance(keep.get(rel), dict) and keep[rel].get("owner"):
            entry["owner"] = keep[rel]["owner"]
        files[rel] = entry
    payload = {
        "schema": "efc-spraak-baseline/1",
        "measured_on": sha.strip() if rc == 0 else "unknown",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "rule": ("scripts/maintenance/efc_spraakvakt.py over the vocabulary in "
                 "scripts/maintenance/spraak-ord.json; the residual is "
                 "recorded, never silenced"),
        "areas": {a: n for a, n in sorted(scanned["areas"].items())
                  if is_guarded(a) or a in GUARDED},
        "measured_scope": {
            "guarded_paths": sum(scanned["areas"].get(a, 0) for a in GUARDED),
            "debt_recorded": sum(scanned["counts"].values()),
            "exempt": sum(e["count"] for e in scanned["exempt"]),
            "outside_guard": sum(n for a, n in scanned["areas"].items()
                                 if not (is_guarded(a) or a in GUARDED)),
        },
        "files": files,
        "exempt": {k: {"count": next((e["count"] for e in scanned["exempt"]
                                      if e["file"] == k), 0), "reason": v}
                   for k, v in EXEMPT.items()},
    }
    baseline_path.write_text(json.dumps(payload, ensure_ascii=False, indent=1)
                             + "\n", encoding="utf-8")
    readback = json.loads(baseline_path.read_text(encoding="utf-8"))
    if readback.get("files") != files:
        raise SystemExit("baseline write did not read back; nothing to trust")
    return {"mode": "update-baseline", "path": str(baseline_path),
            "files": len(files), "hits": sum(scanned["counts"].values()),
            "exempt": payload["exempt"]}


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def print_scan(result: dict) -> None:
    print(f"language scan (spraakvakt): {len(result['new'])} new finding(s) "
          f"against {result['measured_against']}; {result['debt']['files']} "
          f"file(s) / {result['debt']['hits']} hit(s) of debt, record "
          f"{result['record']['files']} / {result['record']['hits']}")
    for f in result["new"]:
        print(f"  NEW: {f['file']}  {f['count']} hit(s), "
              f"expected {f['expected']}, excess {f['excess']}")
    for d in result["undeclared_growth"][:10]:
        print(f"  INFO growth above the record (belongs to the base revision, "
              f"not to this change): {d['file']} {d['count']} > "
              f"recorded {d['recorded']}")
    for u in result["unlisted_areas"]:
        print(f"  INFO outside the guard, not named in the scope table: "
              f"{u['area']} has {u['count']} hit(s)")
    for u in result["unreadable_text"]:
        print(f"  UNREADABLE TEXT: {u}")
    if result["skipped_binary"]:
        print(f"  skipped (not UTF-8, counted): {len(result['skipped_binary'])} "
              f"file(s), e.g. {result['skipped_binary'][0]}")
    for e in result["exempt"]:
        print(f"  exempt (declared): {e['file']} — {e['count']} hit(s): "
              f"{e['reason']}")
    if result["slack"]:
        print(f"  slack (below what is expected, so the record can shrink): "
              f"{len(result['slack'])} file(s)")
        for s in result["slack"][:5]:
            print(f"    {s['file']}: {s['count']} < {s['expected']}")
    if result["gone_from_expectation"]:
        print(f"  expectations for files that are gone or carry no hits: "
              f"{len(result['gone_from_expectation'])} (run --oppdater-baseline)")
    for line in result["declared_limits"]:
        print(f"  limit: {line}")
    if not result["new"]:
        print("  OK: no new Norwegian in the guarded paths")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    p.add_argument("--json", action="store_true")
    p.add_argument("--root", default=str(ROOT),
                   help="tree to read (default: this repository)")
    p.add_argument("--baseline", default=str(BASELINE))
    p.add_argument("--commits", metavar="RANGE",
                   help="check commit subjects in the range, e.g. origin/main..HEAD")
    p.add_argument("--referanse", metavar="REV",
                   help="measure the scan against this revision (the base of a "
                        "change) instead of the committed record; debt above "
                        "the record is then reported, never failed")
    p.add_argument("--changelog", action="store_true")
    p.add_argument("--vindu", type=int, default=30,
                   help="changelog entries read from the newest end (default 30)")
    p.add_argument("--grenser", action="store_true",
                   help="print the declared limits with measured counts")
    p.add_argument("--oppdater-baseline", action="store_true")
    a = p.parse_args(argv)
    root = Path(a.root).resolve()

    if a.oppdater_baseline:
        try:
            result = write_baseline(root, Path(a.baseline))
        except (OSError, ValueError) as exc:
            print(f"could not write the baseline: {exc}", file=sys.stderr)
            return 2
        print(f"baseline written: {result['files']} file(s), "
              f"{result['hits']} hit(s), read back and verified")
        if a.json:
            print(json.dumps(result, ensure_ascii=False, indent=1))
        return 0

    try:
        if a.commits:
            rc, result = run_commits(root, a.commits)
        elif a.changelog:
            rc, result = run_changelog(root, a.vindu)
        elif a.grenser:
            result = run_limits(root)
            rc = 0
        else:
            rc, result = run_scan(root, Path(a.baseline), a.referanse)
    except (OSError, ValueError) as exc:
        print(f"could not measure: {exc}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(result, ensure_ascii=False, indent=1))
    elif a.commits:
        print(f"commit subjects in {result['range']}: "
              f"{len(result['hits'])} finding(s) of {result['commits_read']} "
              f"commit(s)")
        for h in result["hits"]:
            print(f"  {h['sha']}  {h['matches']}  {h['subject']}")
        for line in result["declared_limits"]:
            print(f"  limit: {line}")
    elif a.changelog:
        print(f"changelog entries: {result['entries']} total, window "
              f"{result['window']}, {len(result['hits'])} finding(s)")
        for h in result["hits"]:
            print(f"  #{h['index']}  {h['matches']}  {h['summary']}")
        for line in result["declared_limits"]:
            print(f"  limit: {line}")
    elif a.grenser:
        print("declared scope (measured hits on this tree):")
        for area in result["areas"]:
            reason = f" — {area['reason']}" if area["reason"] else ""
            print(f"  {area['area']:22s} {area['scope']:12s} "
                  f"{area['hits']:6d}{reason}")
        print(f"  outside the guard and not named in the table: "
              f"{len(result['unlisted_areas_with_hits'])}")
        for u in result["unlisted_areas_with_hits"]:
            print(f"    {u['area']}: {u['count']}")
        for line in result["declared_limits"]:
            print(f"  limit: {line}")
    else:
        print_scan(result)
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
