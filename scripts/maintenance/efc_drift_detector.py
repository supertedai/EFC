#!/usr/bin/env python3
"""
EFC Drift Detector

Scans the repo for hard facts (paper count, test count, version numbers,
pipeline status) and compares them against what the public-facing documents
claim. Outputs a structured drift report that Claude Code acts on.

Run by the SessionStart hook after efc_maintain.py.
Exit 0 = clean, exit 2 = drift detected (not an error, just work to do).
"""
from __future__ import annotations
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
SYMBIOSE_SNAPSHOT = os.path.join(REPO, ".claude", "symbiose_snapshot.json")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
    "_archived",
}

# Files to check for consistency
CHECK_FILES = {
    "README.md": os.path.join(REPO, "README.md"),
    "AGENTS.md": os.path.join(REPO, "AGENTS.md"),
    "Validation_Ledger": os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html"),
    "White_Paper_Series": os.path.join(REPO, "docs", "public", "EFC_White_Paper_Series.html"),
    "Elevator_Pitch": os.path.join(REPO, "docs", "public", "EFC_Elevator_Pitch.html"),
    "Stage_IV_Roadmap": os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html"),
    "Changelog": os.path.join(REPO, "docs", "public", "EFC_Changelog.html"),
    "Atlas": os.path.join(REPO, "docs", "public", "EFC_Atlas.html"),
    "pipelines_README": os.path.join(REPO, "pipelines", "README.md"),
}


def _load_symbiose_truth():
    """Return ground-truth counts dict, or empty if snapshot is unavailable."""
    try:
        with open(SYMBIOSE_SNAPSHOT, encoding="utf-8") as f:
            snap = json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}
    tests = snap.get("tests") or {}
    return {
        "tests_total": tests.get("total"),
        "tests_active": tests.get("active"),
        "tests_survived": tests.get("survived"),
        "tests_falsified": tests.get("falsified"),
        "tests_pipeline": tests.get("planned_pipeline"),
    }


def count_paper_dirs():
    count = 0
    for name in os.listdir(PAPERS):
        if name in SKIP_TOP:
            continue
        if os.path.isdir(os.path.join(PAPERS, name)):
            count += 1
    return count


def read_file(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def find_all_counts(text, pattern):
    """Find all integer matches for a pattern like r'(\d+)\s*papers'."""
    return [int(m.group(1)) for m in re.finditer(pattern, text)]


_HIST_DATE_RE = re.compile(r'(?:20\d\d-\d\d|at time of publication|as of\s+\w+|204\s*(?:pubs|publications))', re.IGNORECASE)
_DOI_NEAR_RE = re.compile(r'(?:doi\.org/|figshare\.|10\.6084/m9\.figshare)', re.IGNORECASE)

# Files that the drift fixer must NEVER rewrite. The Changelog by
# definition is an append-only log of history; existing entries are
# historical statements that rotate stale numbers as the repo evolves.
# Auto-rewriting them changes the historical record. New Changelog
# entries are added by efc_ledger_autofill.py / efc_auto_changelog.py.
_FIX_FORBIDDEN = {"Changelog"}


def _is_historical_match(text, start, end):
    """Heuristic: True if this match looks like a quoted/historical claim
    rather than a statement of current repo state.

    Triggers (any one):
      - the surrounding ~1000-char window contains a Figshare DOI link,
        a v3.x/v4.x update tag, or a YYYY-MM-DD timestamp, AND the
        match itself isn't in the very-first paragraph of the page
      - a "204 publications" snapshot marker is anywhere within ~800 chars
      - a Figshare DOI URL within 100 chars before the match (paper card)
      - the match is inside an `<li>...</li>` whose enclosing block
        starts with a date stamp or "(v3.NN" / "(v4.NN" version tag
    """
    para_start = max(0, start - 800)
    para_end = min(len(text), end + 400)
    paragraph = text[para_start:para_end]

    if re.search(r'204\s*(?:pubs|publications)', paragraph, re.IGNORECASE):
        return True
    if _DOI_NEAR_RE.search(text[max(0, start - 100):start]):
        return True

    # Locate the nearest preceding <li> open-tag and check its first
    # 200 chars for a historical-style date or version stamp. If there
    # isn't a <li> open within 4000 chars, consider the match to be in
    # body prose (assume current).
    li_open = text.rfind('<li>', max(0, start - 4000), start)
    if li_open != -1:
        # Make sure no </li> closed it before our match
        li_close = text.rfind('</li>', li_open, start)
        if li_close == -1:
            li_head = text[li_open:li_open + 250]
            if re.search(r'\b20\d\d-\d\d-\d\d\b', li_head):
                return True
            if re.search(r'\(v[34]\.\d+', li_head):
                return True

    # Inside a long Executive Summary paragraph that mixes version-tagged
    # historical updates? Detect by `<strong>v3.x update:</strong>` or
    # `<strong>v4.x update` markers within the same paragraph window.
    if re.search(r'<strong>v[34]\.\d+\s*update', paragraph, re.IGNORECASE):
        return True

    # "Test counts updated from X to Y" is by construction a historical
    # statement — never auto-rewrite this phrase.
    if re.search(r'test counts? updated from', paragraph, re.IGNORECASE):
        return True

    return False


def detect_drift():
    drift = []
    actual_papers = count_paper_dirs()
    truth = _load_symbiose_truth()

    # Patterns that match "<int> <prefix-words?> (papers|packages|tests|...)"
    # where <prefix-words?> can be 0-3 hyphenated/lower-case ASCII words
    # (e.g. "AI-friendly", "validation"). We deliberately scope to a small
    # vocabulary to avoid matching arbitrary phrases.
    PAPER_PATTERN = re.compile(
        r'(\d{2,3})\s+(?:[A-Za-z][\w-]{0,20}\s+){0,2}'
        r'(?:papers?|packages?|paper dir(?:ectorie)?s?)',
        re.IGNORECASE,
    )

    # Test count patterns. Anchor on tests= keyword to avoid arbitrary
    # numbers. Allow at most one adjective (registered/active/total/etc.)
    # between the number and the keyword.
    TESTS_TOTAL_PATTERN = re.compile(
        r'(\d{2,3})\s+(?:[a-z][a-z-]{0,15}\s+)?tests?\b(?!\.[a-z])',
        re.IGNORECASE,
    )
    # Hyphenated form: "118-test status"
    TESTS_HYPHEN_PATTERN = re.compile(
        r'(\d{2,3})-tests?\b',
        re.IGNORECASE,
    )
    # "X total" inside test-context paragraphs (loose total count)
    TESTS_TOTAL_BARE_PATTERN = re.compile(
        r'(\d{2,3})\s+total\b',
        re.IGNORECASE,
    )
    # "112 active probes" or "112 active tests"
    TESTS_ACTIVE_PROSE_PATTERN = re.compile(
        r'(\d{2,3})\s+active\s+(?:probes?|tests?)\b',
        re.IGNORECASE,
    )
    # "survived 93" / "survives 93"
    TESTS_SURVIVED_VERB_PATTERN = re.compile(
        r'survive[ds]?\s+(\d{2,3})\b',
        re.IGNORECASE,
    )
    # "93/103 survived"  → group 1=survived, group 2=active
    TESTS_SURVIVED_RATIO_PATTERN = re.compile(
        r'(\d{2,3})\s*/\s*(\d{2,3})\s+survived',
        re.IGNORECASE,
    )
    # "18 in pipeline"
    TESTS_PIPELINE_PROSE_PATTERN = re.compile(
        r'(\d{2,3})\s+in\s+pipeline',
        re.IGNORECASE,
    )
    # "10 falsified", "Ten probes have been falsified"
    TESTS_FALSIFIED_PROSE_PATTERN = re.compile(
        r'(\d{2,3})\s+(?:probes?\s+)?(?:have\s+been\s+)?falsified',
        re.IGNORECASE,
    )
    TESTS_BREAKDOWN_PATTERN = re.compile(
        r'(\d+)\s+active[^\)]*?(\d+)\s+survived[^\)]*?'
        r'(\d+)\s+falsified[^\)]*?(\d+)\s+(?:in\s+)?(?:pipeline|planned)',
        re.IGNORECASE,
    )

    def _is_test_context(start, end):
        """Loose proximity check — only fire bare patterns when there's
        a probe/test/active keyword within ~250 chars."""
        window = text[max(0, start - 250):min(len(text), end + 250)]
        return bool(re.search(
            r'\b(?:probes?|tests?|active|survived|falsified|pipeline)\b',
            window, re.IGNORECASE,
        ))

    for name, path in CHECK_FILES.items():
        text = read_file(path)
        if not text:
            continue

        # Paper/package counts — skip historical Changelog rows.
        for m in PAPER_PATTERN.finditer(text):
            claimed = int(m.group(1))
            if claimed != actual_papers and abs(claimed - actual_papers) < 30:
                context_before = text[max(0, m.start()-80):m.start()]
                if name == "Changelog" and re.search(r'20\d\d-\d\d', context_before):
                    continue
                drift.append({
                    "file": name,
                    "type": "paper_count",
                    "claimed": claimed,
                    "actual": actual_papers,
                    "context": text[max(0, m.start()-30):m.end()+30].strip(),
                })

        # Test totals — only flag if symbiose truth is available.
        if truth.get("tests_total") is not None:
            for m in TESTS_TOTAL_PATTERN.finditer(text):
                claimed = int(m.group(1))
                if _is_historical_match(text, m.start(), m.end()):
                    continue
                if claimed != truth["tests_total"] and abs(claimed - truth["tests_total"]) < 50:
                    drift.append({
                        "file": name,
                        "type": "tests_total",
                        "claimed": claimed,
                        "actual": truth["tests_total"],
                        "context": text[max(0, m.start()-30):m.end()+30].strip(),
                    })

        # Test breakdown — match the parenthesised quartet and verify each.
        if all(truth.get(k) is not None for k in
               ("tests_active", "tests_survived", "tests_falsified", "tests_pipeline")):
            for m in TESTS_BREAKDOWN_PATTERN.finditer(text):
                if _is_historical_match(text, m.start(), m.end()):
                    continue
                pairs = (
                    ("tests_active", int(m.group(1))),
                    ("tests_survived", int(m.group(2))),
                    ("tests_falsified", int(m.group(3))),
                    ("tests_pipeline", int(m.group(4))),
                )
                for key, claimed in pairs:
                    expected = truth[key]
                    if claimed != expected and abs(claimed - expected) < 50:
                        drift.append({
                            "file": name,
                            "type": key,
                            "claimed": claimed,
                            "actual": expected,
                            "context": text[max(0, m.start()-15):m.end()+15].strip(),
                        })

        # Prose-form test counts — fire only inside test-context windows.
        prose_checks = [
            (TESTS_HYPHEN_PATTERN, "tests_total"),
            (TESTS_TOTAL_BARE_PATTERN, "tests_total"),
            (TESTS_ACTIVE_PROSE_PATTERN, "tests_active"),
            (TESTS_SURVIVED_VERB_PATTERN, "tests_survived"),
            (TESTS_PIPELINE_PROSE_PATTERN, "tests_pipeline"),
            (TESTS_FALSIFIED_PROSE_PATTERN, "tests_falsified"),
        ]
        for pat, key in prose_checks:
            if truth.get(key) is None:
                continue
            for m in pat.finditer(text):
                if _is_historical_match(text, m.start(), m.end()):
                    continue
                if not _is_test_context(m.start(), m.end()):
                    continue
                claimed = int(m.group(1))
                expected = truth[key]
                if claimed != expected and abs(claimed - expected) < 50:
                    drift.append({
                        "file": name,
                        "type": key,
                        "claimed": claimed,
                        "actual": expected,
                        "context": text[max(0, m.start()-15):m.end()+15].strip(),
                        "match_form": pat.pattern[:30],
                    })

        # Ratio form: "93/103 survived" — survived first, then active.
        if truth.get("tests_survived") is not None and truth.get("tests_active") is not None:
            for m in TESTS_SURVIVED_RATIO_PATTERN.finditer(text):
                if _is_historical_match(text, m.start(), m.end()):
                    continue
                surv_claimed = int(m.group(1))
                act_claimed = int(m.group(2))
                if surv_claimed != truth["tests_survived"]:
                    drift.append({
                        "file": name,
                        "type": "tests_survived",
                        "claimed": surv_claimed,
                        "actual": truth["tests_survived"],
                        "context": text[max(0, m.start()-15):m.end()+15].strip(),
                        "match_form": "ratio",
                    })
                if act_claimed != truth["tests_active"]:
                    drift.append({
                        "file": name,
                        "type": "tests_active",
                        "claimed": act_claimed,
                        "actual": truth["tests_active"],
                        "context": text[max(0, m.start()-15):m.end()+15].strip(),
                        "match_form": "ratio",
                    })

        # Check badge counts (e.g. AI_Packages-138)
        for m in re.finditer(r'AI_Packages-(\d+)', text):
            claimed = int(m.group(1))
            if claimed != actual_papers:
                drift.append({
                    "file": name,
                    "type": "badge_count",
                    "claimed": claimed,
                    "actual": actual_papers,
                })

    # Check AGENTS.md version strings
    agents = read_file(CHECK_FILES.get("AGENTS.md", ""))
    if agents:
        # ai_packages count
        m = re.search(r'ai_packages:\s*(\d+)', agents)
        if m and int(m.group(1)) != actual_papers:
            drift.append({
                "file": "AGENTS.md",
                "type": "agents_package_count",
                "claimed": int(m.group(1)),
                "actual": actual_papers,
            })
        # Stale version in AGENTS.md
        m = re.search(r'validation_ledger:\s*v([\d.]+)\s*\(', agents)
        if m:
            agents_version = m.group(1)
            # Check against Changelog for latest version
            changelog = read_file(CHECK_FILES.get("Changelog", ""))
            cm = re.search(r'\(v(3\.\d+)\)', changelog)
            if cm and cm.group(1) != agents_version:
                drift.append({
                    "file": "AGENTS.md",
                    "type": "version_drift",
                    "claimed": agents_version,
                    "actual": cm.group(1),
                })

    return drift, actual_papers


def fix_drift(drift, actual_papers):
    """Auto-fix paper/package/test count drift in public-facing files."""
    fixed_files = set()

    # Group by file path to apply all fixes once per file in memory.
    # Refuse to write append-only Changelog files — those are historical
    # by construction.
    by_file = {}
    for d in drift:
        if d["file"] in _FIX_FORBIDDEN:
            continue
        path = CHECK_FILES.get(d["file"])
        if not path or not os.path.isfile(path):
            continue
        by_file.setdefault(path, []).append(d)

    truth = _load_symbiose_truth()

    test_keyword = {
        "tests_total": r"(?:[a-z][a-z-]{0,15}\s+)?tests?",
        "tests_active": r"active(?:\s+(?:probes?|tests?))?",
        "tests_survived": r"survived",
        "tests_falsified": r"(?:probes?\s+)?(?:have\s+been\s+)?falsified",
        "tests_pipeline": r"(?:in\s+)?(?:pipeline|planned)",
    }

    for path, ds in by_file.items():
        text = read_file(path)
        original = text

        for d in ds:
            old = str(d["claimed"])
            new = str(d["actual"])
            t = d["type"]
            form = d.get("match_form", "")

            if t == "paper_count":
                text = re.sub(
                    rf'(?<!\d){re.escape(old)}(\s+(?:[A-Za-z][\w-]{{0,20}}\s+){{0,2}}'
                    rf'(?:papers?|packages?|paper dir(?:ectorie)?s?))',
                    rf'{new}\g<1>', text, flags=re.IGNORECASE,
                )
            elif t == "badge_count":
                text = re.sub(
                    rf'AI_Packages-{re.escape(old)}',
                    f'AI_Packages-{new}', text,
                )
            elif t == "agents_package_count":
                text = re.sub(
                    rf'(ai_packages:\s*){re.escape(old)}',
                    rf'\g<1>{new}', text,
                )
            elif t == "tests_survived" and form == "ratio":
                # "93/103 survived" — replace only the survived (first) number
                text = re.sub(
                    rf'(?<!\d){re.escape(old)}(\s*/\s*\d{{2,3}}\s+survived)',
                    rf'{new}\g<1>', text, flags=re.IGNORECASE,
                )
            elif t == "tests_active" and form == "ratio":
                # "X/103 survived" — replace the denominator only
                text = re.sub(
                    rf'(\d{{2,3}}\s*/\s*){re.escape(old)}(\s+survived)',
                    rf'\g<1>{new}\g<2>', text, flags=re.IGNORECASE,
                )
            elif t == "tests_survived" and form.startswith("survive"):
                # verb-first: "survives 93", "survived 93"
                text = re.sub(
                    rf'(survive[ds]?\s+){re.escape(old)}(?!\d)',
                    rf'\g<1>{new}', text, flags=re.IGNORECASE,
                )
            elif t == "tests_total" and form.startswith(r"(\d{2,3})-"):
                # hyphenated: "118-test"
                text = re.sub(
                    rf'(?<!\d){re.escape(old)}(-tests?)',
                    rf'{new}\g<1>', text, flags=re.IGNORECASE,
                )
            elif t == "tests_total" and form.startswith(r"(\d{2,3})\s+total"):
                # bare total: "121 total"
                text = re.sub(
                    rf'(?<!\d){re.escape(old)}(\s+total\b)',
                    rf'{new}\g<1>', text, flags=re.IGNORECASE,
                )
            elif t in test_keyword:
                kw = test_keyword[t]
                # Default: number followed by keyword
                text = re.sub(
                    rf'(?<!\d){re.escape(old)}(\s+{kw})',
                    rf'{new}\g<1>', text, flags=re.IGNORECASE,
                )

        if text != original:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            fixed_files.add(path)
            for d in ds:
                print(f"  [fixed] {d['file']}: {d['claimed']} → {d['actual']} ({d['type']})")

    return len(fixed_files)


def main():
    fix_mode = "--fix" in sys.argv
    drift, actual_papers = detect_drift()

    if not drift:
        print(f"[efc-drift] {actual_papers} papers · no drift detected")
        return 0

    print(f"[efc-drift] {actual_papers} papers · {len(drift)} drift(s) detected:")
    for d in drift:
        if d["type"] in ("paper_count", "badge_count", "agents_package_count"):
            print(f"  {d['file']}: claims {d['claimed']} but actual is {d['actual']}")
        elif d["type"] == "version_drift":
            print(f"  {d['file']}: version {d['claimed']} but latest is {d['actual']}")
        else:
            print(f"  {d['file']}: {d['type']} — {d.get('claimed')} vs {d.get('actual')}")

    if fix_mode:
        n = fix_drift(drift, actual_papers)
        print(f"[efc-drift] auto-fixed {n} file(s)")
        # Re-check after fix
        drift2, _ = detect_drift()
        remaining = len(drift2)
        if remaining > 0:
            print(f"[efc-drift] {remaining} drift(s) remain (need manual fix)")
        else:
            print(f"[efc-drift] all drift resolved")
            return 0

    # Write machine-readable drift report
    report_path = os.path.join(REPO, ".claude", "drift_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w") as f:
        json.dump({"paper_count": actual_papers, "drift": drift}, f, indent=2)

    return 2  # drift detected, not an error


if __name__ == "__main__":
    sys.exit(main())
