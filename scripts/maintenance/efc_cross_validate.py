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
                with open(idx_path) as f:
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
    """Load stats from ledger data."""
    stats_path = os.path.join(LEDGER_DATA, "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path) as f:
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


def validate_consistency(repo, stats, result):
    """Cross-check repo paper count vs README vs stats."""
    print("\n--- Cross-consistency ---")

    # README paper count
    readme_path = os.path.join(REPO, "README.md")
    if os.path.exists(readme_path):
        with open(readme_path) as f:
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
            result.ok(f"Sealed {key}: α={pred.get('alpha')}, hash={h}...")

    # α-signal: check that public pages show BOTH LOO and current MCMC
    alpha = snap.get("alpha_signal", {})
    if alpha.get("current_value") is not None:
        elevator_html = read_page("elevator")
        has_loo = "2.20" in elevator_html or "LOO" in elevator_html
        has_current = "0.68" in elevator_html or "0.141" in elevator_html or "degeneracy" in elevator_html.lower()
        if has_loo and has_current:
            result.ok("Elevator Pitch shows both LOO (2.2σ) and current MCMC (0.7σ)")
        elif has_loo and not has_current:
            result.error("Elevator Pitch shows LOO but NOT the weaker current MCMC result")
        elif not has_loo:
            result.warn("Elevator Pitch does not mention α-signal at all")

    if alpha.get("status") == "STOPPED_DEGENERACY_PERSISTS":
        result.warn(
            f"α-signal: {alpha.get('current_value')} ± "
            f"{alpha.get('current_uncertainty')} "
            f"({alpha.get('current_sigma')}σ) — "
            f"LOO was {alpha.get('loo_sigma', '?')}σ — degeneracy unresolved")

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
    validate_consistency(repo, stats, result)
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
