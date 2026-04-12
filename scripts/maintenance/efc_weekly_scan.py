#!/usr/bin/env python3
"""
EFC Weekly Scan — Automated Paper Classification and Report Generation

Extends efc_unprocessed.py by reading each unprocessed paper's content
and generating a structured classification report. Designed to run:
  - Weekly via GitHub Actions (efc-ai-audit.yml, Monday 07:00 UTC)
  - On demand: python3 scripts/maintenance/efc_weekly_scan.py
  - Via SessionStart hook (after efc_maintain.py)

Output:
  - docs/weekly_scan_report.json  — structured report for Claude
  - Console summary for CI job summaries

Classification logic:
  Papers with quantitative empirical tests, sealed predictions,
  pipeline results, or cross-validations → LEDGER candidate
  All others → CHANGELOG_ONLY

Exit codes:
  0 = no unprocessed papers
  2 = report generated (papers need processing)
"""
import json
import os
import re
import sys
from datetime import datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
LEDGER = os.path.join(REPO, "docs", "public", "EFC_Validation_Ledger.html")
CHANGELOG = os.path.join(REPO, "docs", "public", "EFC_Changelog.html")
ROADMAP = os.path.join(REPO, "docs", "public", "EFC_Stage-IV_Data_Roadmap.html")

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}

# Keywords that suggest empirical content
EMPIRICAL_KEYWORDS = {
    "chi2", "chi-squared", "chi_squared", "delta_chi2",
    "aic", "bic", "delta_aic", "delta_bic",
    "p_value", "p-value", "significance", "sigma",
    "sparc", "desi", "boss", "euclid", "planck",
    "rotation_curve", "bao", "rsd", "lensing",
    "sealed", "pre-registered", "blind_prediction",
    "cross-validation", "hold-out", "parameter-locked",
}

# Keywords that suggest theory/methodology only
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


def read_file(path, max_bytes=50000):
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

    # Check for key_results in index.json
    if "key_results" in idx:
        kr = idx["key_results"]
        if isinstance(kr, dict) and kr:
            classification = "LEDGER"
            confidence = "medium"
            reasons.append("has key_results in index.json")
        elif isinstance(kr, list) and kr:
            classification = "LEDGER"
            confidence = "medium"
            reasons.append("has key_results list in index.json")

    # Check keywords in index.json
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

    # Check README for quantitative content
    readme_path = os.path.join(paper_dir, "README.md")
    readme = read_file(readme_path, 20000).lower()
    if readme:
        chi2_pattern = re.findall(r'(?:chi2|χ²|delta_chi|Δχ)\s*[=≈]\s*[\d.+-]+', readme)
        if chi2_pattern:
            classification = "LEDGER"
            confidence = "high"
            reasons.append(f"chi2 values found in README ({len(chi2_pattern)})")

        aic_pattern = re.findall(r'(?:aic|bic|delta_aic|ΔAIC)\s*[=≈]\s*[\d.+-]+', readme)
        if aic_pattern:
            classification = "LEDGER"
            confidence = "high"
            reasons.append("AIC/BIC values found in README")

        if "pre-registered" in readme or "sealed" in readme:
            classification = "LEDGER"
            confidence = "high"
            reasons.append("pre-registered or sealed prediction found")

    # Check track
    track = idx.get("track", "").lower()
    if "galactic" in track or "cosmological" in track:
        if classification == "LEDGER":
            confidence = "high"
            reasons.append(f"track: {idx.get('track', 'unknown')}")

    # DOI-based heuristic: early papers (28xxx) are almost always theory
    doi = extract_bare_doi(idx.get("doi", ""))
    if doi and doi.startswith("28"):
        if classification != "LEDGER" or confidence == "low":
            classification = "CHANGELOG_ONLY"
            confidence = "high"
            reasons.append("early foundational paper (DOI 28xxx)")

    if not reasons:
        reasons.append("no strong indicators found")

    return classification, confidence, reasons


def main():
    ledger_text = read_file(LEDGER, 500000)
    changelog_text = read_file(CHANGELOG, 500000)

    unprocessed = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue

        idx = load_json(os.path.join(paper_dir, "index.json"))
        if not idx:
            continue
        doi = idx.get("doi")
        bare = extract_bare_doi(doi)
        if not bare:
            continue

        in_ledger = bare in ledger_text
        in_changelog = bare in changelog_text

        if in_ledger and in_changelog:
            continue

        missing = []
        if not in_ledger:
            missing.append("Ledger")
        if not in_changelog:
            missing.append("Changelog")

        classification, confidence, reasons = classify_paper(paper_dir, idx)

        title = idx.get("title", name)
        track = idx.get("track", "unknown")

        unprocessed.append({
            "directory": name,
            "doi": bare,
            "title": title,
            "missing_from": missing,
            "track": track,
            "classification": classification,
            "confidence": confidence,
            "reasons": reasons,
            "has_key_results": "key_results" in idx,
        })

    if not unprocessed:
        print("[efc-weekly-scan] All papers are registered. No action needed.")
        return 0

    # Generate report
    report = {
        "generated": datetime.utcnow().isoformat() + "Z",
        "total_unprocessed": len(unprocessed),
        "ledger_candidates": sum(1 for p in unprocessed if p["classification"] == "LEDGER"),
        "changelog_only": sum(1 for p in unprocessed if p["classification"] == "CHANGELOG_ONLY"),
        "papers": unprocessed,
    }

    report_path = os.path.join(REPO, "docs", "weekly_scan_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    # Console output
    print(f"[efc-weekly-scan] {len(unprocessed)} paper(s) need processing:")
    print(f"  LEDGER candidates: {report['ledger_candidates']}")
    print(f"  CHANGELOG_ONLY:    {report['changelog_only']}")
    print()

    for p in sorted(unprocessed, key=lambda x: (x["classification"] != "LEDGER", x["doi"])):
        tag = "LEDGER" if p["classification"] == "LEDGER" else "LOG"
        print(f"  [{tag}] {p['directory']} (DOI {p['doi']})")
        print(f"         Title: {p['title']}")
        print(f"         Missing: {', '.join(p['missing_from'])}")
        print(f"         Confidence: {p['confidence']}")
        print(f"         Reasons: {'; '.join(p['reasons'])}")

    print(f"\n[efc-weekly-scan] Report saved to {report_path}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
