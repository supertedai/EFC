#!/usr/bin/env python3
"""
EFC Paper Processor — AI-Powered Auto-Registration

Reads unprocessed papers (PDFs with DOIs not in Ledger/Changelog),
sends content to GPT-5 for classification, and updates all public
pages automatically.

Pipeline:
  1. Detect unprocessed papers (efc_unprocessed.py output)
  2. Extract text from each PDF
  3. Send to GPT-5 for classification:
     - Is it empirical test, sealed prediction, methodology, theory?
     - Which kill criteria does it relate to?
     - What Ledger tier (T1/T2/T3)?
     - Key results summary
  4. Update public pages:
     - EFC_Validation_Ledger.html (new row if empirical)
     - EFC_Changelog.html (new entry always)
     - EFC_Stage-IV_Data_Roadmap.html (if pipeline/prediction)
     - EFC_White_Paper_Series.html (if sealed prediction)
  5. Update index.json with key_results from AI

Requires: OPENAI_API_KEY environment variable.
Usage:
  python3 scripts/maintenance/efc_process_paper.py
  python3 scripts/maintenance/efc_process_paper.py --dry-run
  python3 scripts/maintenance/efc_process_paper.py --max 5
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
import datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
PUBLIC = os.path.join(REPO, "docs", "public")
LEDGER = os.path.join(PUBLIC, "EFC_Validation_Ledger.html")
CHANGELOG = os.path.join(PUBLIC, "EFC_Changelog.html")
ROADMAP = os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html")
WHITEPAPER = os.path.join(PUBLIC, "EFC_White_Paper_Series.html")

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")
MAX_PDF_CHARS = 8000


def load_unprocessed():
    """Load list of unprocessed papers from the detector output."""
    path = os.path.join(REPO, ".claude", "unprocessed_papers.json")
    if not os.path.exists(path):
        # Run detector first
        subprocess.run([sys.executable,
                        os.path.join(os.path.dirname(__file__), "efc_unprocessed.py")],
                       capture_output=True)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def extract_pdf_text(paper_dir, max_chars=MAX_PDF_CHARS):
    """Extract text from the first PDF in a paper directory."""
    for f in os.listdir(paper_dir):
        if f.lower().endswith(".pdf"):
            pdf_path = os.path.join(paper_dir, f)
            try:
                result = subprocess.run(
                    ["pdftotext", pdf_path, "-"],
                    capture_output=True, text=True, timeout=15
                )
                if result.returncode == 0:
                    return result.stdout[:max_chars]
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
    return ""


def load_index(paper_dir):
    """Load index.json for a paper."""
    path = os.path.join(paper_dir, "index.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {}


def classify_paper(title, doi, text):
    """Ask GPT-5 to classify this paper and extract key information."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    prompt = f"""You are classifying an EFC (Energy-Flow Cosmology) research paper for the validation ledger.

PAPER TITLE: {title}
DOI: 10.6084/m9.figshare.{doi}

PAPER TEXT (first {MAX_PDF_CHARS} chars):
{text}

Classify this paper and respond with ONLY valid JSON (no markdown, no explanation):

{{
  "paper_type": "empirical_test | sealed_prediction | methodology | theory | infrastructure | consciousness",
  "ledger_entry": true or false (true if it contains a new empirical test or sealed prediction),
  "changelog_summary": "One sentence summary for the changelog entry",
  "key_results": {{
    "main_finding": "One sentence key finding",
    "delta_chi2": null or number,
    "significance_sigma": null or number,
    "parameters_tested": ["list of EFC parameters tested"],
    "datasets_used": ["list of datasets"],
    "verdict": "PASS | MARGINAL | FAIL | SEALED | PLANNED | N/A"
  }},
  "kill_criteria": ["KC1" and/or "KC2" etc., or empty list],
  "tier": "T1 | T2 | T3 | N/A",
  "regime": "L0 | L1 | L2 | L3 | N/A",
  "status": "PASS | MARGINAL | FAIL | SEALED | PLANNED | Completed",
  "related_dois": ["list of related figshare DOI numbers"],
  "ledger_row_html": "If ledger_entry is true, generate a single <tr>...</tr> HTML row matching the existing ledger table format. Otherwise null.",
  "changelog_entry_html": "A single <li><strong>date</strong> — summary with DOI link</li> for the changelog."
}}
"""

    try:
        import urllib.request
        import ssl

        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2000,
            }).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            # Strip markdown code fences if present
            content = re.sub(r'^```(?:json)?\s*', '', content.strip())
            content = re.sub(r'\s*```$', '', content.strip())
            return json.loads(content)
    except Exception as e:
        print(f"    [ERROR] GPT-5 API call failed: {e}")
        return None


def insert_changelog_entry(entry_html):
    """Insert a new changelog entry after the latest entry."""
    text = _read(CHANGELOG)
    # Find the first <li> after the ordered list starts
    # Insert before the first existing entry
    marker = "<!-- v3.20 entry"
    if marker in text:
        text = text.replace(marker, f"{entry_html}\n\n  {marker}")
    else:
        # Fallback: insert after <ol reversed>
        text = text.replace("<ol reversed>", f"<ol reversed>\n  {entry_html}")
    _write(CHANGELOG, text)


def insert_ledger_row(row_html):
    """Insert a new row into the Ledger table."""
    text = _read(LEDGER)
    # Find the end of the empirical test table body
    # Insert before the last </tbody>
    idx = text.rfind("</tbody>")
    if idx >= 0:
        text = text[:idx] + f"    {row_html}\n    " + text[idx:]
        _write(LEDGER, text)


def update_index_with_results(paper_dir, classification):
    """Update index.json with key_results from AI classification."""
    idx_path = os.path.join(paper_dir, "index.json")
    if not os.path.exists(idx_path):
        return
    with open(idx_path) as f:
        idx = json.load(f)

    if classification.get("key_results"):
        idx["key_results"] = classification["key_results"]
    if classification.get("paper_type"):
        idx["paper_type"] = classification["paper_type"]
    if classification.get("kill_criteria"):
        idx["kill_criteria"] = classification["kill_criteria"]
    if classification.get("tier"):
        idx["tier"] = classification["tier"]

    with open(idx_path, "w") as f:
        json.dump(idx, f, indent=2)


def _read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def _write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    dry_run = "--dry-run" in sys.argv
    max_papers = 100
    for arg in sys.argv:
        if arg.startswith("--max"):
            try:
                max_papers = int(sys.argv[sys.argv.index(arg) + 1])
            except (ValueError, IndexError):
                pass

    api_key = os.environ.get("OPENAI_API_KEY", "")

    print("=" * 60)
    print("EFC PAPER PROCESSOR — AI-Powered Auto-Registration")
    print(f"Model: {MODEL}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"API key: {'SET' if api_key else 'NOT SET'}")
    print("=" * 60)

    if not api_key:
        print("[SKIP] OPENAI_API_KEY not set. Cannot classify papers.")
        return 0

    unprocessed = load_unprocessed()
    # Only process papers missing from Ledger (not just Changelog)
    to_process = [p for p in unprocessed if "Ledger" in p.get("missing_from", [])]
    to_process = to_process[:max_papers]

    if not to_process:
        print("[OK] No papers need Ledger registration.")
        return 0

    print(f"\n{len(to_process)} paper(s) to process:\n")
    processed = 0

    for paper in to_process:
        dirname = paper["directory"]
        doi = paper["doi"]
        title = paper["title"]
        paper_dir = os.path.join(PAPERS, dirname)

        print(f"  [{processed+1}/{len(to_process)}] {dirname}")
        print(f"    Title: {title}")
        print(f"    DOI: {doi}")

        # Extract PDF text
        text = extract_pdf_text(paper_dir)
        if not text:
            print("    [SKIP] No PDF text extracted")
            continue

        # Classify with GPT-5
        print("    Classifying with GPT-5...")
        classification = classify_paper(title, doi, text)
        if not classification:
            print("    [SKIP] Classification failed")
            continue

        paper_type = classification.get("paper_type", "unknown")
        verdict = classification.get("key_results", {}).get("verdict", "N/A")
        print(f"    Type: {paper_type}")
        print(f"    Verdict: {verdict}")
        print(f"    Summary: {classification.get('changelog_summary', 'N/A')}")

        if dry_run:
            print("    [DRY-RUN] Would update Ledger + Changelog")
            print(f"    Classification: {json.dumps(classification, indent=2)[:500]}")
            processed += 1
            continue

        # Update index.json
        update_index_with_results(paper_dir, classification)
        print("    Updated index.json")

        # Update Changelog
        changelog_html = classification.get("changelog_entry_html")
        if changelog_html:
            insert_changelog_entry(changelog_html)
            print("    Updated Changelog")

        # Update Ledger (if empirical test or sealed prediction)
        if classification.get("ledger_entry"):
            ledger_html = classification.get("ledger_row_html")
            if ledger_html:
                insert_ledger_row(ledger_html)
                print("    Updated Ledger")

        processed += 1

    print(f"\n{'=' * 60}")
    print(f"Processed: {processed}/{len(to_process)}")
    print(f"{'=' * 60}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
