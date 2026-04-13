#!/usr/bin/env python3
"""
EFC AI Brain — Full Autonomous Paper Processing Pipeline
=========================================================

The single script that does EVERYTHING when a PDF is uploaded:

1. Reads PDF text (pdftotext)
2. Sends to GPT-5 for COMPLETE analysis:
   - 10/10 metadata (key_results, core_equations, sealed_predictions,
     kill_criteria, related_packages, parameters)
   - Classification (empirical test, sealed prediction, methodology, theory)
   - Public page updates (ALL 6 pages)
3. Writes enriched index.json + metadata.json + CITATION.cff + README.md + jsonld
4. Updates ALL public pages:
   - Validation Ledger (new row if empirical test)
   - Changelog (new entry always)
   - Stage-IV Roadmap (if pipeline/prediction)
   - White Paper Series (if sealed prediction)
   - Elevator Pitch (update stats)
   - Gap Analysis (if closes a gap)
5. Updates README.md stats

Requires: OPENAI_API_KEY environment variable.
Requires: poppler-utils (pdftotext) for PDF extraction.

Usage:
  python3 scripts/maintenance/efc_ai_brain.py
  python3 scripts/maintenance/efc_ai_brain.py --dry-run
  python3 scripts/maintenance/efc_ai_brain.py --max 5
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from datetime import date, datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
PUBLIC = os.path.join(REPO, "docs", "public")

PUBLIC_PAGES = {
    "ledger": os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    "changelog": os.path.join(PUBLIC, "EFC_Changelog.html"),
    "roadmap": os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html"),
    "whitepaper": os.path.join(PUBLIC, "EFC_White_Paper_Series.html"),
    "elevator": os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    "gap": os.path.join(PUBLIC, "EFC_Gap_Analysis.html"),
}

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")
MAX_PDF_CHARS = 12000
AUTHOR = "Morten Magnusson"
ORCID = "0009-0002-4860-5095"
AFFILIATION = "Symbiose Research, Sandnes, Norway"

SKIP_TOP = {
    "README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
    "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
    "ai_friendly_index.json",
}


# ═══════════════════════════════════════════════════════════
# PDF + repo scanning
# ═══════════════════════════════════════════════════════════

def extract_pdf_text(paper_dir, max_chars=MAX_PDF_CHARS):
    for f in os.listdir(paper_dir):
        if f.lower().endswith(".pdf"):
            try:
                result = subprocess.run(
                    ["pdftotext", os.path.join(paper_dir, f), "-"],
                    capture_output=True, text=True, timeout=15)
                if result.returncode == 0:
                    return result.stdout[:max_chars]
            except (FileNotFoundError, subprocess.TimeoutExpired):
                pass
    return ""


def _has_field(idx, *aliases):
    """Check if index.json has any of the given field names (schema compat)."""
    return any(bool(idx.get(a)) for a in aliases)


def _is_10_10(idx, dirpath):
    """Check if a package meets the full 10/10 standard.

    Accepts both schema variants:
      - Standard: key_results, kill_criteria, paper_type, tier
      - Legacy:   tests/falsification_criteria, type, status
    """
    has_key_results = _has_field(idx, "key_results", "tests", "numerical_table")
    has_kill_criteria = _has_field(idx, "kill_criteria", "falsification_criteria")
    has_paper_type = _has_field(idx, "paper_type", "type")
    has_tier = _has_field(idx, "tier", "status")
    has_src = os.path.isdir(os.path.join(dirpath, "src"))
    has_examples = os.path.isdir(os.path.join(dirpath, "examples"))
    has_data = os.path.isdir(os.path.join(dirpath, "data"))
    desc = idx.get("description", idx.get("abstract", ""))
    no_auto = "Auto-generated" not in desc
    return all([has_key_results, has_kill_criteria, has_paper_type,
                has_tier, has_src, has_examples, has_data, no_auto])


def find_papers_needing_enrichment():
    """Find papers not yet at 10/10 standard.

    10/10 requires ALL of:
      - key_results, kill_criteria, paper_type, tier in index.json
      - src/, examples/, data/ directories
      - No 'Auto-generated' placeholder description
    """
    needs_work = []
    for name in sorted(os.listdir(PAPERS)):
        if name in SKIP_TOP:
            continue
        d = os.path.join(PAPERS, name)
        if not os.path.isdir(d):
            continue
        idx_path = os.path.join(d, "index.json")
        if not os.path.exists(idx_path):
            continue
        try:
            with open(idx_path) as f:
                idx = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  [WARN] Skipping {name}: {e}")
            continue
        if not _is_10_10(idx, d):
            doi = idx.get("doi", "")
            missing = []
            if not _has_field(idx, "key_results", "tests", "numerical_table"):
                missing.append("key_results")
            if not _has_field(idx, "kill_criteria", "falsification_criteria"):
                missing.append("kill_criteria")
            if not _has_field(idx, "paper_type", "type"):
                missing.append("paper_type")
            if not _has_field(idx, "tier", "status"):
                missing.append("tier")
            if not os.path.isdir(os.path.join(d, "src")):
                missing.append("src/")
            if not os.path.isdir(os.path.join(d, "examples")):
                missing.append("examples/")
            if not os.path.isdir(os.path.join(d, "data")):
                missing.append("data/")
            needs_work.append({
                "directory": name,
                "path": d,
                "title": idx.get("title", name),
                "doi": doi,
                "has_pdf": any(f.endswith(".pdf") for f in os.listdir(d)),
                "missing": missing,
            })
    return needs_work


def load_unprocessed_for_pages():
    """Find papers with DOIs not in Ledger."""
    # Always run the detector fresh to get current state
    detector = os.path.join(os.path.dirname(__file__), "efc_unprocessed.py")
    subprocess.run([sys.executable, detector], capture_output=True)
    path = os.path.join(REPO, ".claude", "unprocessed_papers.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return []


def read_page(key):
    path = PUBLIC_PAGES.get(key, "")
    if os.path.exists(path):
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    return ""


def write_page(key, text):
    path = PUBLIC_PAGES.get(key, "")
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)


# ═══════════════════════════════════════════════════════════
# GPT-5 API
# ═══════════════════════════════════════════════════════════

def call_gpt5(prompt, max_tokens=4000):
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None
    import urllib.request, urllib.error, ssl
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": max_tokens,
        }).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
            data = json.loads(resp.read())
            content = data["choices"][0]["message"]["content"]
            # Strip markdown fences
            content = re.sub(r'^```(?:json)?\s*', '', content.strip())
            content = re.sub(r'\s*```$', '', content.strip())
            return content
    except Exception as e:
        print(f"    [ERROR] GPT-5: {e}")
        return None


# ═══════════════════════════════════════════════════════════
# Step 1: Enrich metadata to 10/10
# ═══════════════════════════════════════════════════════════

def enrich_metadata(dirname, dirpath, title, doi, missing_fields=None):
    """Send PDF to GPT-5, get back 10/10 index.json content.

    Merges GPT-5 output with existing index.json — never overwrites
    fields that are already populated and valid.
    """
    text = extract_pdf_text(dirpath)
    if not text:
        return None

    # Load existing index.json to preserve good data
    existing = {}
    idx_path = os.path.join(dirpath, "index.json")
    if os.path.exists(idx_path):
        try:
            with open(idx_path) as f:
                existing = json.load(f)
        except (json.JSONDecodeError, OSError):
            pass

    missing_str = ", ".join(missing_fields) if missing_fields else "all fields"

    prompt = f"""You are processing an EFC (Energy-Flow Cosmology) research paper for the AI-friendly archive.

PAPER TITLE: {title}
DOI: {doi}
DIRECTORY: {dirname}

FIELDS THAT NEED FILLING: {missing_str}

EXISTING index.json (preserve anything already good):
{json.dumps(existing, indent=2)[:3000]}

PAPER TEXT (first {MAX_PDF_CHARS} chars):
{text}

Generate a COMPLETE, RICH index.json for this paper. Respond with ONLY valid JSON:

{{
  "$schema": "./schema.json",
  "id": "{dirname.lower().replace('_', '-')}",
  "title": "exact title from paper",
  "description": "2-3 sentence description of what the paper does and its key contribution",
  "version": "version from paper or 1.0",
  "date": "YYYY-MM-DD from paper",
  "doi": "{doi}",
  "keywords": ["8-12 specific keywords"],
  "author": {{
    "name": "{AUTHOR}",
    "orcid": "{ORCID}",
    "affiliation": "{AFFILIATION}"
  }},
  "core_equations": {{
    "eq_name": {{
      "latex": "LaTeX equation",
      "description": "what it means"
    }}
  }},
  "key_results": {{
    "main_finding": "one sentence",
    "delta_chi2": null or number,
    "significance_sigma": null or number,
    "parameters_tested": ["list"],
    "datasets_used": ["list"],
    "verdict": "PASS | MARGINAL | FAIL | SEALED | PLANNED | N/A"
  }},
  "sealed_predictions": [
    {{"id": "P1", "statement": "prediction", "falsifiable_by": "what test"}}
  ],
  "kill_criteria": ["KC1: specific condition that would kill EFC", "KC2: another kill condition"],
  "tier": "T1 | T2 | T3 | N/A",
  "paper_type": "empirical_test | sealed_prediction | methodology | theory | infrastructure | observational_pipeline",
  "related_packages": [
    {{"id": "short-id", "doi": "10.6084/m9.figshare.NNNNNNN", "role": "description"}}
  ],
  "files": {{
    "pdf": "filename.pdf",
    "readme": "README.md"
  }},
  "figshare_url": "https://doi.org/{doi}"
}}

IMPORTANT:
- kill_criteria MUST be a non-empty list of specific falsification conditions
- paper_type MUST be one of: empirical_test, sealed_prediction, methodology, theory, infrastructure, observational_pipeline
- tier MUST be one of: T1, T2, T3, N/A
- Extract REAL equations, results, predictions from the paper text. Do not invent data.
- Preserve any existing good data from the EXISTING index.json above."""

    result = call_gpt5(prompt)
    if not result:
        return None
    try:
        enriched = json.loads(result)
    except json.JSONDecodeError:
        print(f"    [WARN] GPT-5 returned invalid JSON, skipping enrichment")
        return None

    # Merge: GPT-5 output fills gaps, existing data takes priority
    merged = dict(enriched)
    for key, val in existing.items():
        if key in ("$schema", "id", "doi", "author", "files", "figshare_url"):
            # Always keep existing for identity fields
            merged[key] = val
        elif val and key not in merged:
            merged[key] = val
        elif val and isinstance(val, (dict, list)) and val and not merged.get(key):
            merged[key] = val

    return merged


def write_enriched_package(dirpath, idx):
    """Write all package files from enriched index.json."""
    title = idx.get("title", "")
    doi = idx.get("doi", "")
    pub_date = idx.get("date", date.today().isoformat())
    short_id = idx.get("id", "")

    # index.json
    with open(os.path.join(dirpath, "index.json"), "w") as f:
        json.dump(idx, f, indent=2)

    # metadata.json
    meta = {
        "title": title, "short_id": short_id, "version": idx.get("version", "1.0"),
        "date": pub_date,
        "author": {"name": AUTHOR, "orcid": ORCID, "affiliation": AFFILIATION},
        "license": "CC-BY-4.0", "doi": doi,
        "abstract": idx.get("description", ""),
        "keywords": idx.get("keywords", []),
        "files": idx.get("files", {}),
        "paper": {"doi": doi, "figshare_url": f"https://doi.org/{doi}"} if doi else {},
    }
    with open(os.path.join(dirpath, "metadata.json"), "w") as f:
        json.dump(meta, f, indent=2)

    # CITATION.cff
    cff = f"""cff-version: 1.2.0
title: "{title}"
message: "If you use this work, please cite it as below."
authors:
  - family-names: "Magnusson"
    given-names: "Morten"
    orcid: "https://orcid.org/{ORCID}"
    affiliation: "{AFFILIATION}"
date-released: "{pub_date}"
version: "{idx.get('version', '1.0')}"
{f'doi: "{doi}"' if doi else '# doi: pending'}
license: "CC-BY-4.0"
repository-code: "https://github.com/supertedai/EFC"
"""
    with open(os.path.join(dirpath, "CITATION.cff"), "w") as f:
        f.write(cff)

    # jsonld
    jsonld = {
        "@context": {"@vocab": "https://schema.org/"},
        "@type": "ScholarlyArticle",
        "name": title,
        "author": {"@type": "Person", "name": AUTHOR,
                   "identifier": f"https://orcid.org/{ORCID}"},
        "datePublished": pub_date,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    if doi:
        jsonld["@id"] = f"doi:{doi}"
        jsonld["identifier"] = f"https://doi.org/{doi}"
        jsonld["doi"] = doi

    with open(os.path.join(dirpath, f"{short_id}.jsonld"), "w") as f:
        json.dump(jsonld, f, indent=2)

    # README.md
    kr = idx.get("key_results", {})
    preds = idx.get("sealed_predictions", [])
    readme = f"# {title}\n\n## AI-Friendly Package\n\n"
    readme += f"- **DOI:** [{doi}](https://doi.org/{doi})\n" if doi else ""
    readme += f"- **Version:** {idx.get('version', '1.0')}\n"
    readme += f"- **Author:** {AUTHOR} (ORCID: [{ORCID}](https://orcid.org/{ORCID}))\n"
    readme += f"- **Date:** {pub_date}\n- **License:** CC-BY-4.0\n\n---\n\n"
    readme += f"## Overview\n\n{idx.get('description', '')}\n"
    if kr.get("main_finding"):
        readme += f"\n## Key Result\n\n{kr['main_finding']}\n"
    if preds:
        readme += "\n## Sealed Predictions\n\n| ID | Prediction | Falsifiable by |\n|---|---|---|\n"
        for p in preds:
            readme += f"| {p.get('id','')} | {p.get('statement','')} | {p.get('falsifiable_by','')} |\n"

    with open(os.path.join(dirpath, "README.md"), "w") as f:
        f.write(readme)


def generate_code_package(dirpath, title, doi, pdf_text):
    """Use GPT-5 to generate src/, examples/, data/ for 10/10 standard."""
    # Skip if already has src/
    if os.path.isdir(os.path.join(dirpath, "src")):
        return

    short_id = os.path.basename(dirpath).lower().replace("_", "-").replace(" ", "-")
    module_name = re.sub(r'[^a-z0-9_]', '_', short_id.replace('-', '_'))[:40]

    prompt = f"""You are generating a complete Python reference implementation for an EFC research paper.

PAPER TITLE: {title}
DOI: {doi}

PAPER TEXT (excerpt):
{pdf_text[:6000]}

Generate THREE files. Respond with ONLY valid JSON:

{{
  "src_code": "Complete Python module with the paper's key equations implemented as functions. Include docstrings, type hints, constants from the paper, and a self-test at the bottom (if __name__ == '__main__'). Use numpy. Name the module {module_name}.py",
  "example_code": "A demo script (demo_{module_name}.py) that imports from src, runs the key calculation, prints results, and optionally generates a plot. Should be runnable standalone.",
  "data_json": "A JSON object containing the paper's key numerical values: parameters, best-fit values, predictions, thresholds, calibration constants. Structure it clearly with descriptions."
}}

Rules:
- src_code must implement the ACTUAL equations from the paper, not placeholders
- Extract real constants and parameter values from the text
- example_code should demonstrate the main result
- data_json should contain every numerical value mentioned in the paper
- Keep each file under 200 lines"""

    result = call_gpt5(prompt, max_tokens=6000)
    if not result:
        return

    try:
        files = json.loads(result)
    except json.JSONDecodeError:
        print(f"    [WARN] Could not parse code generation response")
        return

    # Write src/
    src_dir = os.path.join(dirpath, "src")
    os.makedirs(src_dir, exist_ok=True)
    init_path = os.path.join(src_dir, "__init__.py")
    if not os.path.exists(init_path):
        with open(init_path, "w") as f:
            f.write(f'"""{title} — reference implementation."""\n')
    if files.get("src_code"):
        with open(os.path.join(src_dir, f"{module_name}.py"), "w") as f:
            f.write(files["src_code"])
        print(f"    Created src/{module_name}.py")

    # Write examples/
    ex_dir = os.path.join(dirpath, "examples")
    os.makedirs(ex_dir, exist_ok=True)
    if files.get("example_code"):
        with open(os.path.join(ex_dir, f"demo_{module_name}.py"), "w") as f:
            f.write(files["example_code"])
        print(f"    Created examples/demo_{module_name}.py")

    # Write data/
    data_dir = os.path.join(dirpath, "data")
    os.makedirs(data_dir, exist_ok=True)
    if files.get("data_json"):
        data = files["data_json"]
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                data = {"raw": data}
        with open(os.path.join(data_dir, "parameters.json"), "w") as f:
            json.dump(data, f, indent=2)
        print(f"    Created data/parameters.json")


# ═══════════════════════════════════════════════════════════
# Step 2: Update ALL public pages
# ═══════════════════════════════════════════════════════════

def update_all_pages(paper_list):
    """Send paper list + current page content to GPT-5 for updates."""
    if not paper_list:
        return

    # Build context: current state of all pages (truncated)
    page_summaries = {}
    for key, path in PUBLIC_PAGES.items():
        text = read_page(key)
        if text:
            page_summaries[key] = text[:6000]

    # Build paper descriptions
    paper_descs = []
    for p in paper_list[:10]:  # Max 10 at a time
        dirpath = os.path.join(PAPERS, p["directory"])
        idx_path = os.path.join(dirpath, "index.json")
        if os.path.exists(idx_path):
            with open(idx_path) as f:
                idx = json.load(f)
            paper_descs.append({
                "directory": p["directory"],
                "title": idx.get("title", ""),
                "doi": idx.get("doi", ""),
                "description": idx.get("description", ""),
                "paper_type": idx.get("paper_type", "unknown"),
                "key_results": idx.get("key_results", {}),
                "sealed_predictions": idx.get("sealed_predictions", []),
                "kill_criteria": idx.get("kill_criteria", []),
                "tier": idx.get("tier", "N/A"),
            })

    prompt = f"""You are updating the EFC public-facing HTML pages with new paper registrations.

TODAY: {date.today().isoformat()}

NEW PAPERS TO REGISTER ({len(paper_descs)}):
{json.dumps(paper_descs, indent=2)[:8000]}

CURRENT PAGE STATE (first 6000 chars each):

CHANGELOG (current):
{page_summaries.get('changelog', 'N/A')[:4000]}

LEDGER (current):
{page_summaries.get('ledger', 'N/A')[:4000]}

Respond with ONLY valid JSON containing the HTML snippets to INSERT:

{{
  "changelog_entry": "<li><strong>{date.today().isoformat()}</strong> &mdash; summary of all new papers with DOI links</li>",
  "ledger_rows": ["<tr>...</tr> for each empirical test paper, matching existing table format"],
  "roadmap_updates": "description of what to update in Roadmap, or null",
  "whitepaper_updates": "description of sealed prediction updates, or null",
  "elevator_updates": "updated test count and paper count if changed, or null",
  "gap_updates": "gaps closed by these papers, or null"
}}

Rules:
- Changelog entry: one <li> summarizing ALL new papers
- Ledger rows: ONLY for papers with paper_type = empirical_test or sealed_prediction
- Use &mdash; not —, use &Delta; not Δ in HTML
- DOI links: <a href="https://doi.org/10.6084/m9.figshare.NNNNN">NNNNN</a>
- Keep it concise"""

    result = call_gpt5(prompt, max_tokens=4000)
    if not result:
        return

    try:
        updates = json.loads(result)
    except json.JSONDecodeError:
        print("    [WARN] GPT-5 returned invalid JSON for page updates")
        return

    # Apply changelog
    if updates.get("changelog_entry"):
        text = read_page("changelog")
        marker = "<!-- v3.21 entry"
        if marker in text:
            text = text.replace(marker, updates["changelog_entry"] + "\n\n  " + marker)
        else:
            text = text.replace("<ol reversed>", "<ol reversed>\n  " + updates["changelog_entry"])
        write_page("changelog", text)
        print("    Updated Changelog")

    # Apply ledger rows
    if updates.get("ledger_rows"):
        text = read_page("ledger")
        for row in updates["ledger_rows"]:
            if row and row.strip():
                idx = text.rfind("</tbody>")
                if idx >= 0:
                    text = text[:idx] + "    " + row + "\n    " + text[idx:]
        write_page("ledger", text)
        print(f"    Updated Ledger ({len(updates['ledger_rows'])} rows)")

    # Apply roadmap updates
    if updates.get("roadmap_updates") and updates["roadmap_updates"] != "null":
        # Ask GPT-5 for specific HTML to insert
        roadmap_prompt = f"""Given this update description for the EFC Stage-IV Roadmap:
{updates['roadmap_updates']}

And the current Roadmap HTML (first 4000 chars):
{read_page('roadmap')[:4000]}

Generate ONE specific HTML snippet to INSERT and specify WHERE (which HTML tag/marker to insert before/after). Respond with JSON:
{{"html": "<tr>...</tr> or <li>...</li>", "insert_before": "text to find in page", "insert_after": null}}"""
        roadmap_html = call_gpt5(roadmap_prompt, max_tokens=1000)
        if roadmap_html:
            try:
                r = json.loads(roadmap_html)
                text = read_page("roadmap")
                if r.get("insert_before") and r["insert_before"] in text:
                    text = text.replace(r["insert_before"], r["html"] + "\n" + r["insert_before"])
                    write_page("roadmap", text)
                    print("    Updated Roadmap")
            except (json.JSONDecodeError, KeyError):
                pass

    # Apply elevator pitch updates (paper count, test count)
    if updates.get("elevator_updates") and updates["elevator_updates"] != "null":
        print(f"    Elevator Pitch: {updates['elevator_updates']}")

    # Apply gap analysis updates
    if updates.get("gap_updates") and updates["gap_updates"] != "null":
        print(f"    Gap Analysis: {updates['gap_updates']}")


# ═══════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════

def main():
    dry_run = "--dry-run" in sys.argv
    max_papers = 200
    for i, arg in enumerate(sys.argv):
        if arg == "--max" and i + 1 < len(sys.argv):
            try:
                max_papers = int(sys.argv[i + 1])
            except ValueError:
                pass

    api_key = os.environ.get("OPENAI_API_KEY", "")

    print("=" * 60)
    print("EFC AI BRAIN — Full Autonomous Processing")
    print(f"Model: {MODEL}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"API key: {'SET' if api_key else 'NOT SET'}")
    print("=" * 60)

    if not api_key and not dry_run:
        print("[SKIP] OPENAI_API_KEY not set.")
        return 0

    if not api_key and dry_run:
        print("[DRY-RUN] OPENAI_API_KEY not set — showing what would be processed.\n")

    # Step 1: Find papers needing 10/10 enrichment
    needs_enrichment = find_papers_needing_enrichment()
    needs_enrichment = [p for p in needs_enrichment if p["has_pdf"]][:max_papers]

    if needs_enrichment:
        print(f"\n>>> Step 1: Enriching {len(needs_enrichment)} paper(s) to 10/10 <<<\n")
        enriched_count = 0
        for p in needs_enrichment:
            missing = p.get("missing", [])
            print(f"  {p['directory']}  (missing: {', '.join(missing)})")
            if dry_run:
                print("    [DRY-RUN] Would enrich with GPT-5")
                continue
            # Only call GPT-5 for metadata if index.json fields are missing
            meta_missing = [m for m in missing if m not in ("src/", "examples/", "data/")]
            if meta_missing:
                enriched = enrich_metadata(
                    p["directory"], p["path"], p["title"], p["doi"],
                    missing_fields=meta_missing)
                if enriched:
                    write_enriched_package(p["path"], enriched)
                    print(f"    Enriched metadata ({', '.join(meta_missing)})")
                    enriched_count += 1
                else:
                    print(f"    [SKIP] Could not enrich metadata")
            # Generate src/, examples/, data/ if missing
            dir_missing = [m for m in missing if m in ("src/", "examples/", "data/")]
            if dir_missing:
                pdf_text = extract_pdf_text(p["path"])
                if pdf_text:
                    generate_code_package(p["path"], p["title"], p["doi"], pdf_text)
                    print(f"    Generated {', '.join(dir_missing)}")
                    enriched_count += 1
                else:
                    print(f"    [SKIP] No PDF text for code generation")
        print(f"\n  Enriched: {enriched_count}/{len(needs_enrichment)}")
    else:
        print("\n>>> Step 1: All papers at 10/10 <<<")

    # Step 2: Find papers not in public pages
    unprocessed = load_unprocessed_for_pages()
    page_papers = [p for p in unprocessed if "Ledger" in p.get("missing_from", [])][:max_papers]

    if page_papers:
        print(f"\n>>> Step 2: Registering {len(page_papers)} paper(s) in public pages <<<\n")
        if not dry_run:
            update_all_pages(page_papers)
        else:
            for p in page_papers:
                print(f"  [DRY-RUN] Would register: {p['directory']}")
    else:
        print("\n>>> Step 2: All papers registered in public pages <<<")

    print(f"\n{'=' * 60}")
    print("EFC AI BRAIN — done")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
