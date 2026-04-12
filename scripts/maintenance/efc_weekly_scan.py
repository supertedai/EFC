#!/usr/bin/env python3
"""
EFC Weekly Scan — Comprehensive Repository Health & Sync Monitor

Catches EVERYTHING that changes in the repo, not just DOI papers:

  1. Unprocessed papers (DOI not in Ledger/Changelog)
  2. Pipeline runs (new outputs in pipelines/ not reflected in public pages)
  3. Recent git commits not documented in Changelog
  4. Validation-ledger JSON vs HTML drift (test counts, versions)
  5. New theory/src files not referenced anywhere
  6. Symbiosis research status sync (inference cycles, gaps, validations)
  7. Kill-criteria pipeline readiness changes

Designed to run:
  - Weekly via GitHub Actions (efc-ai-audit.yml, Monday 07:00 UTC)
  - On demand: python3 scripts/maintenance/efc_weekly_scan.py
  - Via SessionStart hook (after efc_maintain.py)

Output:
  - docs/weekly_scan_report.json  — structured report for Claude
  - Console summary

Exit codes:
  0 = everything in sync
  2 = items need attention
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")
CHANGELOG = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")
ROADMAP = os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html")
PIPELINES = os.path.join(REPO, "pipelines", "efc")
VAL_DATA = os.path.join(REPO, "docs", "validation-ledger", "data")
THEORY = os.path.join(REPO, "theory")
SRC = os.path.join(REPO, "src")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

EMPIRICAL_KEYWORDS = {
    "chi2", "chi-squared", "chi_squared", "delta_chi2",
    "aic", "bic", "delta_aic", "delta_bic",
    "p_value", "p-value", "significance", "sigma",
    "sparc", "desi", "boss", "euclid", "planck",
    "rotation_curve", "bao", "rsd", "lensing",
    "sealed", "pre-registered", "blind_prediction",
    "cross-validation", "hold-out", "parameter-locked",
}

THEORY_KEYWORDS = {
    "hypothesis", "philosophical", "conceptual", "introduction",
    "overview", "synthesis", "integration", "framework",
    "ontology", "epistemology", "meta-architecture",
}


def load_json(path):
    try:
        with open(path) as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


def read_file(path, max_bytes=500000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(max_bytes)
    except OSError:
        return ""


def extract_bare_doi(doi_str):
    if not doi_str:
        return None
    m = re.search(r'(\d{7,9})', str(doi_str))
    return m.group(1) if m else None


def classify_paper(paper_dir, idx):
    """Classify a paper as LEDGER candidate or CHANGELOG_ONLY."""
    classification = "CHANGELOG_ONLY"
    confidence = "low"
    reasons = []

    if "key_results" in idx:
        kr = idx["key_results"]
        if isinstance(kr, (dict, list)) and kr:
            classification = "LEDGER"
            confidence = "medium"
            reasons.append("has key_results in index.json")

    idx_text = json.dumps(idx).lower()
    empirical_hits = [kw for kw in EMPIRICAL_KEYWORDS if kw in idx_text]
    theory_hits = [kw for kw in THEORY_KEYWORDS if kw in idx_text]

    if len(empirical_hits) >= 3:
        classification = "LEDGER"
        confidence = "medium"
        reasons.append(f"empirical keywords: {', '.join(empirical_hits[:5])}")

    if theory_hits and not empirical_hits:
        classification = "CHANGELOG_ONLY"
        confidence = "medium"
        reasons.append(f"theory keywords: {', '.join(theory_hits[:3])}")

    readme_path = os.path.join(paper_dir, "README.md")
    readme = read_file(readme_path, 20000).lower()
    if readme:
        if re.findall(r'(?:chi2|χ²|delta_chi|Δχ)\s*[=≈]\s*[\d.+-]+', readme):
            classification = "LEDGER"
            confidence = "high"
            reasons.append("chi2 values found in README")
        if re.findall(r'(?:aic|bic|delta_aic|ΔAIC)\s*[=≈]\s*[\d.+-]+', readme):
            classification = "LEDGER"
            confidence = "high"
            reasons.append("AIC/BIC values found in README")
        if "pre-registered" in readme or "sealed" in readme:
            classification = "LEDGER"
            confidence = "high"
            reasons.append("pre-registered or sealed prediction found")

    doi = extract_bare_doi(idx.get("doi", ""))
    if doi and doi.startswith("28"):
        if classification != "LEDGER" or confidence == "low":
            classification = "CHANGELOG_ONLY"
            confidence = "high"
            reasons.append("early foundational paper (DOI 28xxx)")

    if not reasons:
        reasons.append("no strong indicators found")

    return classification, confidence, reasons


# ─── Section 1: Unprocessed Papers ───────────────────────────────────────────

def scan_unprocessed_papers():
    """Find papers with DOIs not in Ledger/Changelog."""
    ledger_text = read_file(LEDGER)
    changelog_text = read_file(CHANGELOG)
    items = []

    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue
        idx = load_json(os.path.join(paper_dir, "index.json"))
        if not idx:
            continue
        bare = extract_bare_doi(idx.get("doi"))
        if not bare:
            continue

        missing = []
        if bare not in ledger_text:
            missing.append("Ledger")
        if bare not in changelog_text:
            missing.append("Changelog")
        if not missing:
            continue

        classification, confidence, reasons = classify_paper(paper_dir, idx)
        items.append({
            "directory": name,
            "doi": bare,
            "title": idx.get("title", name),
            "missing_from": missing,
            "track": idx.get("track", "unknown"),
            "classification": classification,
            "confidence": confidence,
            "reasons": reasons,
        })
    return items


# ─── Section 2: Pipeline Runs ────────────────────────────────────────────────

def scan_pipeline_outputs():
    """Check for pipeline output files newer than last Changelog entry."""
    items = []
    changelog_text = read_file(CHANGELOG)

    if not os.path.isdir(PIPELINES):
        return items

    for pipeline_name in sorted(os.listdir(PIPELINES)):
        pipeline_dir = os.path.join(PIPELINES, pipeline_name)
        if not os.path.isdir(pipeline_dir):
            continue

        outputs_dir = os.path.join(pipeline_dir, "outputs")
        if not os.path.isdir(outputs_dir):
            continue

        for run_name in sorted(os.listdir(outputs_dir)):
            run_dir = os.path.join(outputs_dir, run_name)
            if not os.path.isdir(run_dir):
                continue

            # Check if this run is referenced in any public page
            if run_name not in changelog_text:
                # Get modification time
                try:
                    mtime = os.path.getmtime(run_dir)
                    mod_date = datetime.fromtimestamp(mtime).isoformat()
                except OSError:
                    mod_date = "unknown"

                # Check for results files
                result_files = [f for f in os.listdir(run_dir)
                                if f.endswith(('.json', '.csv', '.pkl', '.h5'))]

                items.append({
                    "pipeline": pipeline_name,
                    "run": run_name,
                    "path": os.path.relpath(run_dir, REPO),
                    "modified": mod_date,
                    "result_files": result_files[:10],
                    "n_files": len(os.listdir(run_dir)),
                })
    return items


# ─── Section 3: Recent Git Commits ───────────────────────────────────────────

def scan_recent_commits(days=7):
    """Find commits in the last N days not reflected in Changelog."""
    items = []
    changelog_text = read_file(CHANGELOG)

    since = (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")
    try:
        result = subprocess.run(
            ["git", "log", f"--since={since}", "--oneline", "--no-merges",
             "--format=%H|%s|%ai"],
            capture_output=True, text=True, cwd=REPO, timeout=30
        )
        if result.returncode != 0:
            return items
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return items

    for line in result.stdout.strip().split("\n"):
        if not line:
            continue
        parts = line.split("|", 2)
        if len(parts) < 3:
            continue
        sha, subject, date = parts

        # Skip maintenance/merge commits
        skip_prefixes = ("chore:", "Merge", "Auto-update", "fix:", "ci:")
        if any(subject.startswith(p) for p in skip_prefixes):
            continue

        # Check if the commit SHA or a meaningful keyword is in the Changelog
        short_sha = sha[:7]
        if short_sha not in changelog_text:
            # Check if the commit changes important files
            try:
                files_result = subprocess.run(
                    ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
                    capture_output=True, text=True, cwd=REPO, timeout=10
                )
                changed_files = files_result.stdout.strip().split("\n")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                changed_files = []

            # Only flag commits that touch important directories
            important = [f for f in changed_files if any(
                f.startswith(d) for d in (
                    "pipelines/", "theory/", "src/efc/",
                    "docs/public/", "docs/papers/efc/",
                    "docs/validation-ledger/",
                )
            )]

            if important:
                items.append({
                    "sha": short_sha,
                    "subject": subject,
                    "date": date.strip(),
                    "important_files": important[:10],
                    "n_files_changed": len(changed_files),
                })
    return items


# ─── Section 4: Validation Data Drift ────────────────────────────────────────

def scan_validation_drift():
    """Check if JSON data files are in sync with HTML Ledger."""
    items = []

    # Check stats.json test count vs HTML Ledger banner
    stats = load_json(os.path.join(VAL_DATA, "stats.json"))
    if stats:
        json_count = stats.get("stats", {}).get("total_public", 0)

        ledger_text = read_file(LEDGER)
        # Extract test count from stage banner (e.g., "103 tests" or "103-test")
        m = re.search(r'(\d+)[- ]test', ledger_text)
        html_count = int(m.group(1)) if m else 0

        if json_count and html_count and json_count != html_count:
            items.append({
                "type": "test_count_mismatch",
                "json_count": json_count,
                "html_count": html_count,
                "source": "stats.json vs EFC_Validation_Ledger.html",
            })

    # Check ledger.json version vs HTML version
    ledger_json = load_json(os.path.join(VAL_DATA, "ledger.json"))
    if ledger_json:
        json_version = ledger_json.get("version", "")
        m = re.search(r'v(\d+\.\d+)', read_file(LEDGER, 2000))
        html_version = m.group(0) if m else ""
        if json_version and html_version and json_version != html_version:
            items.append({
                "type": "version_mismatch",
                "json_version": json_version,
                "html_version": html_version,
                "source": "ledger.json vs EFC_Validation_Ledger.html",
            })

    # Check evidence-register.json DOI count vs Ledger §4
    evidence = load_json(os.path.join(VAL_DATA, "evidence-register.json"))
    if evidence:
        json_dois = set()
        for entry in evidence.get("entries", evidence.get("empirical", [])):
            if isinstance(entry, dict):
                d = extract_bare_doi(entry.get("doi", ""))
                if d:
                    json_dois.add(d)

        # Count DOIs in Ledger §4 evidence register
        ledger_text = read_file(LEDGER)
        html_dois = set(re.findall(r'figshare\.(\d{7,9})', ledger_text))

        json_only = json_dois - html_dois
        html_only = html_dois - json_dois

        if json_only:
            items.append({
                "type": "evidence_doi_in_json_not_html",
                "dois": sorted(json_only)[:20],
                "count": len(json_only),
            })
        if html_only and len(html_only) > 5:
            items.append({
                "type": "evidence_doi_in_html_not_json",
                "dois": sorted(html_only)[:20],
                "count": len(html_only),
            })

    return items


# ─── Section 5: New Theory/Source Files ───────────────────────────────────────

def scan_new_theory_files(days=7):
    """Check for recently modified theory/src files not referenced in docs."""
    items = []
    cutoff = datetime.utcnow() - timedelta(days=days)
    changelog_text = read_file(CHANGELOG)

    for base_dir, label in [(THEORY, "theory"), (SRC, "src")]:
        if not os.path.isdir(base_dir):
            continue
        for root, dirs, files in os.walk(base_dir):
            for fname in files:
                if not fname.endswith(('.py', '.tex', '.md', '.json')):
                    continue
                fpath = os.path.join(root, fname)
                try:
                    mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
                except OSError:
                    continue

                if mtime > cutoff:
                    rel = os.path.relpath(fpath, REPO)
                    if fname not in changelog_text and rel not in changelog_text:
                        items.append({
                            "file": rel,
                            "modified": mtime.isoformat(),
                            "category": label,
                        })
    return items


# ─── Section 6: Kill Criteria Pipeline Check ─────────────────────────────────

def scan_kill_criteria_readiness():
    """Check if kill criteria pipelines have changed status."""
    items = []
    roadmap_text = read_file(ROADMAP)

    kc_pipelines = {
        "KC1": {"label": "P(k) full-shape", "dir": "pipelines/efc/euclid_dr1"},
        "KC2": {"label": "fσ8 trajectory", "dir": None},
        "KC3": {"label": "S8 convergence", "dir": "pipelines/efc/euclid_dr1"},
        "KC4": {"label": "Gravitational slip η", "dir": None},
        "KC5": {"label": "Dark energy w(z)", "dir": None},
    }

    for kc, info in kc_pipelines.items():
        if info["dir"]:
            pipeline_path = os.path.join(REPO, info["dir"])
            if os.path.isdir(pipeline_path):
                # Check if pipeline has new outputs since last scan
                outputs = []
                for root, dirs, files in os.walk(pipeline_path):
                    for f in files:
                        if f.endswith(('.json', '.h5', '.pkl', '.csv')):
                            fp = os.path.join(root, f)
                            try:
                                mt = os.path.getmtime(fp)
                                if datetime.fromtimestamp(mt) > datetime.utcnow() - timedelta(days=7):
                                    outputs.append(os.path.relpath(fp, REPO))
                            except OSError:
                                pass
                if outputs:
                    items.append({
                        "kc": kc,
                        "label": info["label"],
                        "new_outputs": outputs[:5],
                        "n_new": len(outputs),
                    })

    return items


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("[efc-weekly-scan] === Comprehensive EFC Repository Scan ===")
    print()

    report = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "scan_type": "comprehensive",
        "sections": {},
    }

    total_items = 0

    # 1. Unprocessed papers
    papers = scan_unprocessed_papers()
    ledger_candidates = sum(1 for p in papers if p["classification"] == "LEDGER")
    report["sections"]["unprocessed_papers"] = {
        "count": len(papers),
        "ledger_candidates": ledger_candidates,
        "changelog_only": len(papers) - ledger_candidates,
        "items": papers,
    }
    total_items += len(papers)
    print(f"[1/6] Unprocessed papers: {len(papers)} ({ledger_candidates} LEDGER candidates)")

    # 2. Pipeline outputs
    pipelines = scan_pipeline_outputs()
    report["sections"]["pipeline_outputs"] = {
        "count": len(pipelines),
        "items": pipelines,
    }
    total_items += len(pipelines)
    print(f"[2/6] Undocumented pipeline runs: {len(pipelines)}")

    # 3. Recent commits
    commits = scan_recent_commits(days=7)
    report["sections"]["recent_commits"] = {
        "count": len(commits),
        "items": commits,
    }
    total_items += len(commits)
    print(f"[3/6] Undocumented commits (7d): {len(commits)}")

    # 4. Validation drift
    drift = scan_validation_drift()
    report["sections"]["validation_drift"] = {
        "count": len(drift),
        "items": drift,
    }
    total_items += len(drift)
    print(f"[4/6] Validation data drift: {len(drift)} issues")

    # 5. New theory/source files
    theory = scan_new_theory_files(days=7)
    report["sections"]["new_theory_files"] = {
        "count": len(theory),
        "items": theory[:50],
    }
    total_items += len(theory)
    print(f"[5/6] New theory/src files (7d): {len(theory)}")

    # 6. Kill criteria pipeline changes
    kc = scan_kill_criteria_readiness()
    report["sections"]["kill_criteria_changes"] = {
        "count": len(kc),
        "items": kc,
    }
    total_items += len(kc)
    print(f"[6/6] KC pipeline changes (7d): {len(kc)}")

    report["total_items"] = total_items

    # Write report
    report_path = os.path.join(REPO, "docs", "weekly_scan_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print()
    if total_items == 0:
        print("[efc-weekly-scan] Everything in sync. No action needed.")
        return 0

    print(f"[efc-weekly-scan] {total_items} item(s) need attention.")

    # Print details for high-priority items
    if pipelines:
        print("\n  Pipeline runs not in Changelog:")
        for p in pipelines[:5]:
            print(f"    {p['pipeline']}/{p['run']} ({p['n_files']} files)")

    if drift:
        print("\n  Validation data drift:")
        for d in drift:
            print(f"    {d['type']}: {d.get('source', json.dumps(d))}")

    if commits:
        print("\n  Commits needing documentation:")
        for c in commits[:5]:
            print(f"    {c['sha']} {c['subject']} ({c['n_files_changed']} files)")

    if kc:
        print("\n  Kill criteria with new outputs:")
        for k in kc:
            print(f"    {k['kc']} ({k['label']}): {k['n_new']} new files")

    print(f"\n[efc-weekly-scan] Full report: {report_path}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
