#!/usr/bin/env python3
"""
EFC Cross-Validation Gate
==========================

Checks ALL public pages against repo data, ledger, and DOIs BEFORE
any auto-commit. Blocks publishing if critical discrepancies are found.

This is the "council" step — it reads the same data that Symbiose,
Claude Monitor, and GPT-5 Brain see, and flags any inconsistency.

Usage:
  python3 scripts/maintenance/efc_cross_validate.py
  python3 scripts/maintenance/efc_cross_validate.py --fix   # auto-fix numbers
  python3 scripts/maintenance/efc_cross_validate.py --strict # exit 1 on any warning

Exit codes:
  0 = all checks pass
  1 = critical discrepancies found (blocks publish)
  2 = warnings only (publish OK but review recommended)
"""
from __future__ import annotations
import html as _html
import json
import os
import re
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
PUBLIC = os.path.join(REPO, "docs", "public")
LEDGER_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")
SYMBIOSE_SNAPSHOT = os.path.join(REPO, ".claude", "symbiose_snapshot.json")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
    # container for superseded papers, not a paper itself — counting it
    # inflated the repo total to 170 vs the true 169 (README, drift-detector,
    # ai_friendly_index all agree on 169)
    "_archived",
}

PUBLIC_PAGES = {
    "elevator": os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    "ledger": os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    "whitepaper": os.path.join(PUBLIC, "EFC_White_Paper_Series.html"),
    "roadmap": os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html"),
    "gap": os.path.join(PUBLIC, "EFC_Gap_Analysis.html"),
    "changelog": os.path.join(PUBLIC, "EFC_Changelog.html"),
}


class ValidationResult:
    def __init__(self):
        self.errors = []    # Critical — blocks publish
        self.warnings = []  # Non-critical — review recommended

    def error(self, msg):
        self.errors.append(msg)
        print(f"  [CRITICAL] {msg}")

    def warn(self, msg):
        self.warnings.append(msg)
        print(f"  [WARNING]  {msg}")

    def ok(self, msg):
        print(f"  [OK]       {msg}")


def count_repo_papers():
    """Count actual paper directories and DOIs in repo."""
    total = 0
    with_doi = 0
    with_key_results = 0
    with_sealed = 0
    sealed_total = 0

    for name in os.listdir(PAPERS):
        if name in SKIP_TOP:
            continue
        d = os.path.join(PAPERS, name)
        if not os.path.isdir(d):
            continue
        total += 1
        idx_path = os.path.join(d, "index.json")
        if os.path.exists(idx_path):
            try:
                with open(idx_path, encoding="utf-8", errors="replace") as f:
                    idx = json.load(f)
                if idx.get("doi"):
                    with_doi += 1
                if idx.get("key_results") or idx.get("tests") or idx.get("numerical_table"):
                    with_key_results += 1
                sp = idx.get("sealed_predictions", [])
                if sp:
                    with_sealed += 1
                    sealed_total += len(sp)
            except (json.JSONDecodeError, OSError):
                pass

    return {
        "total": total,
        "with_doi": with_doi,
        "with_key_results": with_key_results,
        "with_sealed": with_sealed,
        "sealed_total": sealed_total,
    }


def load_ledger_stats():
    """Load stats from ledger data.

    Prefers ledger.json (authoritative) over stats.json (derived).
    Falls back to stats.json if ledger.json has no stats block.
    """
    # Primary: ledger.json stats block
    ledger_path = os.path.join(LEDGER_DATA, "ledger.json")
    if os.path.exists(ledger_path):
        with open(ledger_path, encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            s = data.get("stats", {})
            if s.get("total_public"):
                return s

    # Fallback: stats.json
    stats_path = os.path.join(LEDGER_DATA, "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, encoding="utf-8", errors="replace") as f:
            data = json.load(f)
            return data.get("stats", data)
    return {}


def load_symbiose_snapshot():
    """Load Symbiose ground truth snapshot if available."""
    if os.path.exists(SYMBIOSE_SNAPSHOT):
        with open(SYMBIOSE_SNAPSHOT) as f:
            return json.load(f)
    return None


def read_page(key):
    """Read a public HTML page."""
    path = PUBLIC_PAGES.get(key, "")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""


def find_numbers_in_html(html, pattern):
    """Find all numbers matching a regex pattern in HTML."""
    return [int(m) for m in re.findall(pattern, html)]


def validate_elevator_pitch(repo, stats, result):
    """Check Elevator Pitch numbers against repo and ledger."""
    print("\n--- Elevator Pitch ---")
    html = read_page("elevator")
    if not html:
        result.error("Elevator Pitch HTML missing")
        return

    # Check paper count claims
    paper_nums = re.findall(r'(\d+)\s*(?:paper|publication|AI-friendly)', html)
    for num_str in paper_nums:
        num = int(num_str)
        if abs(num - repo["total"]) > 5:
            result.error(
                f"Paper count '{num}' in Elevator Pitch != {repo['total']} in repo")
        else:
            result.ok(f"Paper count {num} close to repo {repo['total']}")

    # Check test count claims
    total_public = stats.get("total_public", 0)
    planned = stats.get("planned_pipeline", 0)
    active_tests = total_public - planned
    test_nums = re.findall(r'(\d+)\s*(?:test|probe|active)', html)
    for num_str in test_nums:
        num = int(num_str)
        # Accept either total_public or active_tests
        if num > 50 and abs(num - total_public) > 5 and abs(num - active_tests) > 5:
            result.warn(
                f"Test count '{num}' != total {total_public} or active {active_tests}")

    # Check survival claims
    n_falsified = stats.get("n_falsified", 0)
    if "survives every" in html.lower() and n_falsified > 0:
        result.error(
            f"Claims 'survives every test' but n_falsified={n_falsified}")

    survived_match = re.search(r'(\d+)/(\d+)\s*survived', html)
    if survived_match:
        survived = int(survived_match.group(1))
        tested = int(survived_match.group(2))
        planned = stats.get("planned_pipeline", 0)
        expected_active = total_public - planned
        expected_survived = expected_active - n_falsified
        if survived != expected_survived:
            result.warn(
                f"Survived {survived}/{tested} but expected "
                f"{expected_survived}/{expected_active} "
                f"(total={total_public}, falsified={n_falsified}, pipeline={planned})")
        else:
            result.ok(f"Survival count {survived}/{tested} matches ledger")


def validate_ledger_page(repo, stats, result):
    """Check Validation Ledger HTML against stats."""
    print("\n--- Validation Ledger ---")
    html = read_page("ledger")
    if not html:
        result.error("Validation Ledger HTML missing")
        return

    total_public = stats.get("total_public", 0)
    test_nums = re.findall(r'(\d+)-test', html)
    for num_str in test_nums:
        num = int(num_str)
        if abs(num - total_public) > 2:
            result.warn(f"'{num}-test' in Ledger HTML != {total_public} in stats")
        else:
            result.ok(f"Test count {num} matches ledger {total_public}")

    n_falsified = stats.get("n_falsified", 0)
    if "survives every" in html.lower() and n_falsified > 0:
        result.error(
            f"Ledger claims 'survives every test' but n_falsified={n_falsified}")


def validate_all_pages_numbers(stats, result):
    """Check public pages intro sections for stale numbers.

    Only checks the FIRST 5000 chars of each page (intro/header section).
    Historical changelog entries and ledger version history are excluded
    because they record what was true at the time of writing.
    """
    print("\n--- All Pages Number Check ---")
    total_public = stats.get("total_public", 0)
    n_falsified = stats.get("n_falsified", 0)

    # Only check intro sections (Elevator, White Paper, Roadmap, Gap)
    # Skip Changelog and Ledger body (they contain historical entries)
    for key in ["elevator", "whitepaper", "roadmap", "gap"]:
        html = read_page(key)
        if not html:
            continue

        # Only check first 5000 chars (intro section)
        intro = html[:5000]
        page_name = key.capitalize()

        if "survives every" in intro.lower() and n_falsified > 0:
            result.error(
                f"{page_name}: claims 'survives every test' but n_falsified={n_falsified}")

        if "204 publications" in intro or "204 papers" in intro:
            result.error(f"{page_name}: still says '204 publications'")

        # Check test count in intro (not in historical entries)
        if re.search(r'\b103\b.*test', intro) and total_public != 103:
            result.warn(
                f"{page_name}: intro says '103 tests' but total_public={total_public}")


def validate_inference_doi(result):
    """Check that inference modules are anchored to DOI data, not stubs."""
    print("\n--- Inference DOI Anchoring ---")
    inf_path = os.path.join(LEDGER_DATA, "inference.json")
    if not os.path.exists(inf_path):
        result.warn("inference.json missing")
        return
    with open(inf_path) as f:
        inf = json.load(f)

    stubs = 0
    anchored = 0
    for m in inf.get("modules", []):
        name = m.get("name", "?")
        engine = m.get("engine_status", "unknown")
        doi_sources = m.get("doi_sources", [])
        if engine == "lcdm_stub":
            stubs += 1
            result.error(f"{name}: still LCDM stub — no DOI data")
        elif engine == "doi_anchored" and doi_sources:
            anchored += 1
            dois = ", ".join(s.get("doi", "?").split("/")[-1] for s in doi_sources[:2])
            result.ok(f"{name}: DOI-anchored ({dois})")
        elif engine in ("active", "self_consistent"):
            chi2 = m.get("chi2_reduced")
            if chi2 is not None and chi2 > 5.0:
                result.warn(f"{name}: active but poor fit (chi2={chi2:.1f})")
            else:
                result.ok(f"{name}: {engine}")

    if stubs > 0:
        result.error(f"{stubs} inference modules still on LCDM stubs")
    else:
        result.ok(f"All {anchored} inference modules DOI-anchored")


def validate_consistency(repo, stats, result):
    """Cross-check repo paper count vs README vs stats."""
    print("\n--- Cross-consistency ---")

    # README paper count
    readme_path = os.path.join(REPO, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, encoding="utf-8", errors="replace") as f:
            readme = f.read()
        readme_nums = re.findall(r'(\d+)\s*paper', readme)
        for num_str in readme_nums:
            num = int(num_str)
            if num > 50 and abs(num - repo["total"]) > 3:
                result.warn(f"README says '{num} papers', repo has {repo['total']}")
            elif num > 50:
                result.ok(f"README paper count {num} matches repo {repo['total']}")

    # Stats internal consistency
    total = (stats.get("physics_test", 0) + stats.get("consistency_check", 0) +
             stats.get("phenomenological", 0) + stats.get("framework_constraint", 0) +
             stats.get("planned_pipeline", 0))
    if total != stats.get("total_public", 0):
        result.error(
            f"Stats category sum {total} != total_public {stats.get('total_public')}")
    else:
        result.ok(f"Stats categories sum to {total} = total_public")

    # DOI count
    doi_sync_path = os.path.join(REPO, "scripts", "maintenance", "efc_sync_dois.py")
    if os.path.exists(doi_sync_path):
        result.ok(f"DOI sync script present, {repo['with_doi']}/{repo['total']} papers have DOIs")

    # Sealed predictions
    if repo["sealed_total"] > 0:
        result.ok(f"{repo['with_sealed']} papers have sealed predictions ({repo['sealed_total']} total)")


def validate_test_counts_all_pages(stats, result):
    """Check that ALL public pages show the same test counts as ledger.json.

    This catches the specific failure where ledger.json gets updated (e.g. by
    efc_ledger_impact_sync) but the intro text in Roadmap, White Papers, or
    Gap Analysis still carries stale numbers like '106 tests'.
    """
    print("\n--- Test Count Cross-Page Consistency ---")
    total_public = stats.get("total_public", 0)
    planned = stats.get("planned_pipeline", 0)
    n_falsified = stats.get("n_falsified", 0)
    active = total_public - planned
    survived = active - n_falsified

    if total_public == 0:
        result.warn("Ledger total_public is 0 — skipping cross-page check")
        return

    # Patterns that capture test counts in natural-language contexts
    # e.g. "118 tests registered", "100 active", "91 survived", "18 in pipeline"
    PATTERNS = {
        "total": [
            r"(\d+)\s*(?:tests?\s*registered|registered\s*tests?|total\s*tests?)",
            r"(\d+)\s*(?:tests?\s*\()",  # "118 tests ("
        ],
        "active": [r"(\d+)\s*active"],
        "survived": [
            r"(\d+)/\d+\s*survived",  # "91/100 survived" → 91
            r"(?<!/)\b(\d+)\s*survived",  # "91 survived" but not "100 survived" after /
        ],
        "falsified": [r"(\d+)\s*falsified"],
        "pipeline": [r"(\d+)\s*(?:in\s*)?pipeline"],
    }

    expected = {
        "total": total_public,
        "active": active,
        "survived": survived,
        "falsified": n_falsified,
        "pipeline": planned,
    }

    # Only check pages with intro/summary text (skip changelog, skip ledger body)
    for key in ["elevator", "whitepaper", "roadmap", "gap"]:
        html = read_page(key)
        if not html:
            continue
        page_name = {
            "elevator": "Elevator Pitch",
            "whitepaper": "White Paper Series",
            "roadmap": "Stage-IV Roadmap",
            "gap": "Gap Analysis",
        }[key]

        # Only check intro sections — not historical changelog tables
        # For roadmap, also check §12 (embedded gap analysis)
        intro = html[:8000]

        for metric, patterns in PATTERNS.items():
            for pat in patterns:
                for m in re.finditer(pat, intro, re.IGNORECASE):
                    found = int(m.group(1))
                    exp = expected[metric]
                    if found != exp and found > 10:  # ignore small numbers
                        result.error(
                            f"{page_name}: says {found} {metric} but "
                            f"ledger has {exp}")


def _extract_stage4_kcs_from_paper(idx):
    """Extract Stage-IV KC references (KC1-KC5, FA1-FA6) from a paper's
    index.json by reading structured fields, not guessing from keywords.

    Priority order:
    1. ledger_impact.kill_criteria_addressed (explicit, highest trust)
    2. kill_criteria text array (parse "KC1", "KC4", "FA4" labels)
    3. sealed_predictions[].falsifiable_by (parse KC refs)

    Returns a set of normalized labels like {"KC4", "FA4"}.
    """
    kcs = set()

    # Source 1: ledger_impact.kill_criteria_addressed (most authoritative)
    li = idx.get("ledger_impact", {})
    if isinstance(li, dict):
        for kc in li.get("kill_criteria_addressed", []):
            kcs.add(kc.upper().strip())

    # Source 2: kill_criteria text array — parse KC/FA labels
    for text in idx.get("kill_criteria", []):
        for m in re.finditer(r"\b(KC\d|FA\d)\b", text, re.IGNORECASE):
            kcs.add(m.group(1).upper())

    # Source 3: sealed_predictions[].falsifiable_by
    for sp in idx.get("sealed_predictions", []):
        fb = sp.get("falsifiable_by", "")
        for m in re.finditer(r"\b(KC\d|FA\d)\b", fb, re.IGNORECASE):
            kcs.add(m.group(1).upper())

    return kcs


def validate_kc_status_vs_dois(result):
    """Check that KC rows marked 'NOT STARTED' or 'PIPELINE NEEDED' in
    public pages don't have a sealed prediction DOI that addresses them.

    Uses DOI-semantic parsing: reads kill_criteria fields from paper
    index.json and ledger_impact.kill_criteria_addressed to determine
    which KCs each sealed prediction covers. No keyword guessing.
    """
    print("\n--- KC Status vs Sealed DOIs (semantic) ---")

    # Build map: KC label -> list of covering DOIs
    kc_to_dois = {}  # e.g. {"KC4": [{"doi": "...", "title": "..."}]}
    for name in os.listdir(PAPERS):
        d = os.path.join(PAPERS, name)
        idx_path = os.path.join(d, "index.json")
        if not os.path.isdir(d) or not os.path.exists(idx_path):
            continue
        try:
            with open(idx_path, encoding="utf-8", errors="replace") as f:
                idx = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        ptype = idx.get("paper_type", "")
        if ptype not in ("sealed_prediction", "observational_pipeline",
                         "empirical_test", "empirical_analysis"):
            continue
        doi = idx.get("doi", "")
        if not doi:
            continue

        kcs = _extract_stage4_kcs_from_paper(idx)
        for kc in kcs:
            kc_to_dois.setdefault(kc, []).append({
                "doi": doi,
                "title": idx.get("title", name),
            })

    if not kc_to_dois:
        result.ok("No papers with KC/FA references found")
        return

    covered = sorted(kc_to_dois.keys())
    result.ok(f"Sealed/empirical DOIs cover: {', '.join(covered)}")

    # Check Gap Analysis and Roadmap for stale KC rows
    for page_key in ["gap", "roadmap"]:
        html = read_page(page_key)
        if not html:
            continue
        page_name = "Gap Analysis" if page_key == "gap" else "Stage-IV Roadmap"

        for row in re.findall(r"<tr>(.*?)</tr>", html, flags=re.DOTALL):
            if not re.search(r"NOT\s*STARTED|PIPELINE\s*NEEDED", row, re.IGNORECASE):
                continue

            # Which KC does this HTML row reference?
            row_kcs = set(m.group(1).upper()
                          for m in re.finditer(r"\b(KC\d|FA\d)\b", row, re.IGNORECASE))

            for kc in row_kcs:
                if kc in kc_to_dois:
                    dois = kc_to_dois[kc]
                    doi_list = ", ".join(d["doi"].split("/")[-1] for d in dois[:3])
                    result.warn(
                        f"{page_name}: {kc} marked NOT STARTED/PIPELINE NEEDED "
                        f"but {len(dois)} sealed DOI(s) address it: {doi_list}")


def validate_section12_sync(result):
    """Check that Roadmap §12 KC readiness matches Gap Analysis §2.

    Both pages have KC status tables. If one gets updated and the other
    doesn't, this catches the drift.
    """
    print("\n--- Roadmap §12 vs Gap Analysis Sync ---")
    gap_html = read_page("gap")
    road_html = read_page("roadmap")
    if not gap_html or not road_html:
        result.warn("Cannot compare — one or both pages missing")
        return

    # Extract KC badge statuses from each page
    def extract_kc_badges(html):
        badges = {}
        for m in re.finditer(
            r"(KC\d).*?(SEALED|DONE|PREDICTION READY|P3 PASS|"
            r"PIPELINE NEEDED|NOT STARTED|Monitoring|PLANNED|HIGH|ACTIVE)",
            html, re.DOTALL | re.IGNORECASE,
        ):
            kc = m.group(1).upper()
            status = m.group(2).upper()
            # Take the FIRST status found for each KC (most prominent)
            if kc not in badges:
                badges[kc] = status
        return badges

    gap_kc = extract_kc_badges(gap_html)
    road_kc = extract_kc_badges(road_html)

    mismatches = 0
    for kc in sorted(set(gap_kc) | set(road_kc)):
        g = gap_kc.get(kc, "MISSING")
        r = road_kc.get(kc, "MISSING")
        if g != r:
            result.warn(
                f"{kc}: Gap Analysis says '{g}' but Roadmap §12 says '{r}'")
            mismatches += 1

    if mismatches == 0:
        result.ok(f"Roadmap §12 and Gap Analysis KC statuses match ({len(gap_kc)} KCs)")


def validate_gap_bottom_line(result):
    """Check Gap Analysis 'Bottom Line' is coherent with Theory Gaps /
    Priority Actions tables above.

    Catches the specific failure mode where an individual gap row gets
    flipped to CLOSED/DONE but the hardcoded summary in 'Bottom Line'
    still cites that same gap as the biggest outstanding one.
    """
    print("\n--- Gap Analysis Coherence ---")
    html = read_page("gap")
    if not html:
        result.warn("Gap Analysis page not found")
        return

    bl_pos = html.find("Bottom Line")
    if bl_pos < 0:
        result.warn("Gap Analysis: no Bottom Line section")
        return

    body = html[:bl_pos]
    bottom = html[bl_pos:]

    # Gather topics that have been CLOSED/DONE/SEALED in the tables above.
    # Walk row-by-row: any <tr> whose status column carries a badge-done
    # with CLOSED/DONE/SEALED wording is considered closed.
    closed_topics = []
    for row in re.findall(r"<tr>(.*?)</tr>", body, flags=re.DOTALL):
        if not re.search(r"badge-done", row):
            continue
        if not re.search(r"\b(CLOSED|DONE|SEALED|PREDICTION READY|P3 PASS)\b",
                         row, flags=re.IGNORECASE):
            continue
        first_td = re.search(r"<td[^>]*>(.*?)</td>", row, flags=re.DOTALL)
        if not first_td:
            continue
        topic = _html.unescape(re.sub(r"<[^>]+>", " ", first_td.group(1)))
        topic = re.sub(r"\s+", " ", topic).strip()
        if 3 <= len(topic) <= 160:
            closed_topics.append(topic.lower())

    # Extract the "Biggest gap right now" cell content.
    m = re.search(
        r"Biggest gap right now</td>\s*<td>(.+?)</td>",
        bottom,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not m:
        result.warn("Gap Analysis: could not parse 'Biggest gap right now'")
        return

    biggest_raw = _html.unescape(re.sub(r"<[^>]+>", " ", m.group(1))).lower()

    def _normalize(s):
        # Collapse any non-alphanumeric (hyphens, Greek, HTML entities) to spaces.
        return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", s)).strip()

    biggest_norm = _normalize(biggest_raw)
    biggest_says_closed = any(
        tok in biggest_norm for tok in ("closed", "done", "sealed"))

    # Any CLOSED topic still cited as the biggest gap?  That's stale.
    for topic in closed_topics:
        tokens = _normalize(topic).split()
        tokens = [t for t in tokens if len(t) > 2 and t not in {
            "and", "the", "for", "with", "mapping", "function", "analysis"}]
        if len(tokens) < 2:
            continue
        key = " ".join(tokens[:2])
        if key in biggest_norm and not biggest_says_closed:
            result.error(
                f"Gap Analysis 'Biggest gap right now' still cites "
                f"'{key}' but that row is marked CLOSED/DONE in the tables above")
            return

    result.ok(f"Gap Analysis Bottom Line coherent ({len(closed_topics)} closed rows checked)")


def validate_symbiose(repo, stats, result):
    """Cross-check against Symbiose snapshot (graph + Qdrant + GNN)."""
    print("\n--- Symbiose Council ---")
    snap = load_symbiose_snapshot()
    if not snap:
        result.warn("No Symbiose snapshot — run efc_symbiose_snapshot.py first")
        return

    source = snap.get("source", "unknown")
    print(f"  Snapshot source: {source}")

    # Compare test counts
    sym_tests = snap.get("tests", {})
    sym_total = sym_tests.get("total", 0)
    ledger_total = stats.get("total_public", 0)
    if sym_total != ledger_total and sym_total > 0:
        result.warn(
            f"Symbiose tests={sym_total} vs ledger total_public={ledger_total}")
    elif sym_total > 0:
        result.ok(f"Symbiose test count {sym_total} matches ledger")

    # Compare falsified count
    sym_falsified = sym_tests.get("falsified", 0)
    ledger_falsified = stats.get("n_falsified", 0)
    if sym_falsified != ledger_falsified and sym_falsified > 0:
        result.warn(
            f"Symbiose falsified={sym_falsified} vs ledger n_falsified={ledger_falsified}")

    # Compare paper count
    sym_papers = snap.get("papers", {}).get("total", 0)
    if sym_papers > 0 and abs(sym_papers - repo["total"]) > 2:
        result.error(
            f"Symbiose papers={sym_papers} vs repo={repo['total']}")
    elif sym_papers > 0:
        result.ok(f"Symbiose paper count {sym_papers} matches repo")

    # Sealed prediction hashes
    sealed = snap.get("sealed_predictions", {})
    for key, pred in sealed.items():
        h = pred.get("hash_prefix", "")
        if h:
            result.ok(f"Sealed {key}: alpha={pred.get('alpha')}, hash={h}...")

    # α-signal: check that public pages show BOTH LOO and current MCMC
    alpha = snap.get("alpha_signal", {})
    if alpha.get("current_value") is not None:
        elevator_html = read_page("elevator")
        has_loo = "2.20" in elevator_html or "LOO" in elevator_html
        has_current = "0.68" in elevator_html or "0.141" in elevator_html or "degeneracy" in elevator_html.lower()
        if has_loo and has_current:
            result.ok("Elevator Pitch shows both LOO (2.2s) and current MCMC (0.7s)")
        elif has_loo and not has_current:
            result.error("Elevator Pitch shows LOO but NOT the weaker current MCMC result")
        elif not has_loo:
            result.warn("Elevator Pitch does not mention alpha-signal at all")

    if alpha.get("status") == "STOPPED_DEGENERACY_PERSISTS":
        result.warn(
            f"alpha-signal: {alpha.get('current_value')} +/- "
            f"{alpha.get('current_uncertainty')} "
            f"({alpha.get('current_sigma')}s) -- "
            f"LOO was {alpha.get('loo_sigma', '?')}s -- degeneracy unresolved")

    # GRAV pipeline
    grav = snap.get("grav", {})
    if grav.get("kt3") == "MARGINAL":
        result.warn("GRAV KT3 still MARGINAL — resolution path needed")

    # Health score
    health = snap.get("health_score")
    if health and health < 50:
        result.error(f"Symbiose health score {health}/100 — below threshold")
    elif health:
        result.ok(f"Symbiose health score {health}/100")


def main():
    do_fix = "--fix" in sys.argv
    strict = "--strict" in sys.argv

    print("=" * 60)
    print("EFC CROSS-VALIDATION GATE (with Symbiose Council)")
    print("=" * 60)

    repo = count_repo_papers()
    stats = load_ledger_stats()
    result = ValidationResult()

    print(f"\nRepo: {repo['total']} papers, {repo['with_doi']} DOIs")
    print(f"Ledger: {stats.get('total_public', '?')} tests, "
          f"{stats.get('n_falsified', '?')} falsified")

    validate_elevator_pitch(repo, stats, result)
    validate_ledger_page(repo, stats, result)
    validate_all_pages_numbers(stats, result)
    validate_test_counts_all_pages(stats, result)
    validate_kc_status_vs_dois(result)
    validate_section12_sync(result)
    validate_inference_doi(result)
    validate_consistency(repo, stats, result)
    validate_gap_bottom_line(result)
    validate_symbiose(repo, stats, result)

    print(f"\n{'=' * 60}")
    print(f"RESULT: {len(result.errors)} errors, {len(result.warnings)} warnings")

    if result.errors:
        print("VERDICT: BLOCK — critical discrepancies prevent publishing")
        print("Fix these before auto-commit:")
        for e in result.errors:
            print(f"  - {e}")
        return 1

    if result.warnings and strict:
        print("VERDICT: BLOCK (strict mode) — warnings found")
        for w in result.warnings:
            print(f"  - {w}")
        return 2

    if result.warnings:
        print("VERDICT: PASS with warnings")
        for w in result.warnings:
            print(f"  - {w}")
        return 0

    print("VERDICT: PASS — all checks clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
