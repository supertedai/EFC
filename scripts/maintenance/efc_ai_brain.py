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
MAX_PDF_CHARS = 8000
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

def _find_pdftotext():
    """Find pdftotext binary, checking common paths."""
    import shutil
    path = shutil.which("pdftotext")
    if path:
        return path
    # Fallback: common install locations
    for p in ["/usr/bin/pdftotext", "/usr/local/bin/pdftotext"]:
        if os.path.isfile(p):
            return p
    return None


def extract_pdf_text(paper_dir, max_chars=MAX_PDF_CHARS):
    pdfs = [f for f in os.listdir(paper_dir) if f.lower().endswith(".pdf")]
    if not pdfs:
        return ""
    pdftotext_bin = _find_pdftotext()
    if not pdftotext_bin:
        print("    [FAIL] pdftotext not found (poppler-utils)")
        return ""
    for f in pdfs:
        pdf_path = os.path.join(paper_dir, f)
        try:
            result = subprocess.run(
                [pdftotext_bin, pdf_path, "-"],
                capture_output=True, text=True, timeout=15)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout[:max_chars]
            if result.returncode != 0:
                print(f"    [WARN] pdftotext rc={result.returncode} for {f}: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            print(f"    [WARN] pdftotext timeout for {f}")
        except Exception as e:
            print(f"    [WARN] pdftotext failed: {type(e).__name__}: {e}")
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

def call_gpt5(prompt, max_tokens=8000, retries=4):
    """Call GPT-5 API with retry logic for transient failures.

    Uses exponential backoff: 5s, 10s, 20s, 40s between retries.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("    [FAIL] OPENAI_API_KEY empty at call time")
        return None
    import urllib.request, urllib.error, ssl
    import time as _time
    ctx = ssl.create_default_context()

    for attempt in range(1, retries + 1):
        body = json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": max_tokens,
        })
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=body.encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=300) as resp:
                data = json.loads(resp.read())
                choice = data["choices"][0]
                content = choice.get("message", {}).get("content")
                finish = choice.get("finish_reason", "")
                if not content:
                    reason = f"finish_reason={finish}" if finish else "no content"
                    print(f"    [WARN] GPT-5 empty ({reason}) attempt {attempt}/{retries}")
                    if attempt < retries:
                        _time.sleep(5 * (2 ** (attempt - 1)))
                        continue
                    return None
                # Strip markdown fences
                content = re.sub(r'^```(?:json)?\s*', '', content.strip())
                content = re.sub(r'\s*```$', '', content.strip())
                return content
        except urllib.error.HTTPError as e:
            body_text = ""
            try:
                body_text = e.read().decode()[:300]
            except Exception:
                pass
            if e.code in (429, 500, 502, 503) and attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] HTTP {e.code} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] GPT-5 HTTP {e.code}: {e.reason} -- {body_text}")
            return None
        except Exception as e:
            if attempt < retries:
                wait = 5 * (2 ** (attempt - 1))
                print(f"    [RETRY] {type(e).__name__} — waiting {wait}s ({attempt}/{retries})")
                _time.sleep(wait)
                continue
            print(f"    [FAIL] GPT-5: {type(e).__name__}: {e}")
    return None


def _repair_json(text):
    """Try to fix truncated JSON from GPT-5 (missing closing braces)."""
    text = text.strip()
    # Count unmatched braces/brackets
    opens = text.count('{') + text.count('[')
    closes = text.count('}') + text.count(']')
    if opens > closes:
        # Try adding missing closers
        diff = opens - closes
        # Remove any trailing partial key/value
        last_comma = text.rfind(',')
        last_brace = max(text.rfind('}'), text.rfind(']'))
        if last_comma > last_brace:
            text = text[:last_comma]
        # Add closers in reverse order
        for ch in reversed(text):
            if diff <= 0:
                break
            if ch == '{':
                text += '}'
                diff -= 1
            elif ch == '[':
                text += ']'
                diff -= 1
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
    return None


# ═══════════════════════════════════════════════════════════
# Step 1: Enrich metadata to 10/10
# ═══════════════════════════════════════════════════════════

def enrich_metadata(dirname, dirpath, title, doi, missing_fields=None):
    """Send PDF to GPT-5, get back 10/10 index.json content.

    Merges GPT-5 output with existing index.json — never overwrites
    fields that are already populated and valid.
    Falls back to title+existing metadata if PDF text extraction fails.
    """
    text = extract_pdf_text(dirpath)
    if not text:
        print(f"    [INFO] No PDF text extracted — using title + existing metadata")

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

    # Build context from what we have
    source_text = text if text else ""
    existing_context = json.dumps(existing, indent=2)[:4000] if existing else "{}"

    prompt = f"""You are processing an EFC (Energy-Flow Cosmology) research paper for the AI-friendly archive.

PAPER TITLE: {title}
DOI: {doi}
DIRECTORY: {dirname}

FIELDS THAT NEED FILLING: {missing_str}

EXISTING index.json (preserve anything already good):
{existing_context}

{"PAPER TEXT (first " + str(MAX_PDF_CHARS) + " chars):" + chr(10) + source_text if source_text else "NOTE: No PDF text available. Generate metadata based on the title, directory name, and existing index.json above. For fields you cannot determine from the title alone, use reasonable defaults based on the EFC framework context."}

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
        print(f"    [FAIL] GPT-5 returned no response")
        return None
    try:
        enriched = json.loads(result)
    except json.JSONDecodeError:
        # Try to repair truncated JSON (GPT-5 sometimes cuts off)
        repaired = _repair_json(result)
        if repaired:
            enriched = repaired
        else:
            print(f"    [WARN] GPT-5 returned invalid JSON: {result[:200]}")
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
    """Update each public page separately with targeted GPT-5 calls.

    Instead of one massive prompt for all 6 pages, makes separate focused
    calls: Changelog, Ledger, Elevator, Roadmap, Whitepaper, Gap.
    """
    if not paper_list:
        return

    import time as _time

    # Build paper descriptions (shared context)
    paper_descs = []
    for p in paper_list[:20]:
        dirpath = os.path.join(PAPERS, p["directory"])
        idx_path = os.path.join(dirpath, "index.json")
        if os.path.exists(idx_path):
            with open(idx_path) as f:
                idx = json.load(f)
            paper_descs.append({
                "directory": p["directory"],
                "title": idx.get("title", ""),
                "doi": idx.get("doi", ""),
                "description": idx.get("description", "")[:200],
                "paper_type": idx.get("paper_type", idx.get("type", "unknown")),
                "tier": idx.get("tier", idx.get("status", "N/A")),
            })

    papers_json = json.dumps(paper_descs, indent=2)[:6000]
    today = date.today().isoformat()

    # --- 1. CHANGELOG ---
    changelog_text = read_page("changelog")
    if changelog_text:
        prompt = f"""Add a changelog entry for {len(paper_descs)} new EFC papers registered on {today}.

PAPERS:
{papers_json}

Respond with ONLY the HTML <li> element to insert. Example format:
<li><strong>{today}</strong> &mdash; Registered {len(paper_descs)} papers: [list titles with DOI links].</li>

Use &mdash; not —. DOI links: <a href="https://doi.org/DOI">short-id</a>"""

        result = call_gpt5(prompt, max_tokens=2000)
        if result:
            result = result.strip()
            if result.startswith("<li"):
                if "<ol reversed>" in changelog_text:
                    changelog_text = changelog_text.replace(
                        "<ol reversed>", "<ol reversed>\n  " + result)
                    write_page("changelog", changelog_text)
                    print("    Updated Changelog")

    _time.sleep(3)

    # --- 2. LEDGER (only empirical tests) ---
    empirical = [p for p in paper_descs if p.get("paper_type") in
                 ("empirical_test", "sealed_prediction")]
    if empirical:
        ledger_text = read_page("ledger")
        if ledger_text:
            # Find existing table format
            last_tr = ledger_text.rfind("<tr>")
            sample_row = ledger_text[last_tr:last_tr + 500] if last_tr > 0 else ""

            prompt = f"""Add rows to the EFC Validation Ledger HTML table for these empirical test papers.

PAPERS TO ADD:
{json.dumps(empirical, indent=2)}

EXISTING TABLE ROW FORMAT (match this exactly):
{sample_row[:300]}

Respond with ONLY the <tr>...</tr> elements, one per paper. Use &Delta; not Δ, &mdash; not —."""

            result = call_gpt5(prompt, max_tokens=3000)
            if result and "<tr>" in result:
                idx_pos = ledger_text.rfind("</tbody>")
                if idx_pos >= 0:
                    ledger_text = ledger_text[:idx_pos] + result + "\n" + ledger_text[idx_pos:]
                    write_page("ledger", ledger_text)
                    print(f"    Updated Ledger ({len(empirical)} papers)")

    _time.sleep(3)

    # --- 3. ELEVATOR PITCH (update stats) ---
    elevator_text = read_page("elevator")
    if elevator_text:
        # Count current papers and tests
        import re as _re
        paper_count = len([d for d in os.listdir(PAPERS)
                          if os.path.isdir(os.path.join(PAPERS, d))
                          and d not in SKIP_TOP])

        prompt = f"""Update the paper count and test count in this EFC Elevator Pitch HTML.

Current paper count in archive: {paper_count}
New papers just registered: {len(paper_descs)}

Current Elevator Pitch HTML (first 3000 chars):
{elevator_text[:3000]}

Find any number that represents the paper count or test count and update it.
Respond with JSON: {{"old_text": "text to find", "new_text": "replacement text"}}
If no update needed, respond with {{"old_text": null, "new_text": null}}"""

        result = call_gpt5(prompt, max_tokens=500)
        if result:
            try:
                upd = json.loads(result)
                if upd.get("old_text") and upd["old_text"] in elevator_text:
                    elevator_text = elevator_text.replace(upd["old_text"], upd["new_text"])
                    write_page("elevator", elevator_text)
                    print("    Updated Elevator Pitch")
            except (json.JSONDecodeError, KeyError):
                pass

    _time.sleep(3)

    # --- 4. ROADMAP (if pipeline/prediction papers) ---
    pipeline_papers = [p for p in paper_descs if p.get("paper_type") in
                       ("observational_pipeline", "sealed_prediction")]
    if pipeline_papers:
        roadmap_text = read_page("roadmap")
        if roadmap_text:
            prompt = f"""These new EFC papers may need Roadmap updates:
{json.dumps(pipeline_papers, indent=2)}

Current Roadmap HTML (first 3000 chars):
{roadmap_text[:3000]}

If any paper adds a new dataset, pipeline, or prediction to track, respond with:
{{"html": "<tr>new row HTML</tr>", "insert_before": "exact text to find in page"}}

If no update needed: {{"html": null}}"""

            result = call_gpt5(prompt, max_tokens=1000)
            if result:
                try:
                    r = json.loads(result)
                    if r.get("html") and r.get("insert_before"):
                        if r["insert_before"] in roadmap_text:
                            roadmap_text = roadmap_text.replace(
                                r["insert_before"], r["html"] + "\n" + r["insert_before"])
                            write_page("roadmap", roadmap_text)
                            print("    Updated Roadmap")
                except (json.JSONDecodeError, KeyError):
                    pass

    _time.sleep(3)

    # --- 5. WHITE PAPER SERIES (sealed predictions) ---
    sealed_papers = [p for p in paper_descs if p.get("paper_type") == "sealed_prediction"]
    if sealed_papers:
        wp_text = read_page("whitepaper")
        if wp_text:
            prompt = f"""These EFC papers contain sealed predictions for the White Paper Series:
{json.dumps(sealed_papers, indent=2)}

Current White Paper Series HTML (first 3000 chars):
{wp_text[:3000]}

If any paper should be added, respond with:
{{"html": "<li>new entry HTML</li>", "insert_before": "exact text to find"}}

If no update: {{"html": null}}"""

            result = call_gpt5(prompt, max_tokens=1000)
            if result:
                try:
                    r = json.loads(result)
                    if r.get("html") and r.get("insert_before"):
                        if r["insert_before"] in wp_text:
                            wp_text = wp_text.replace(
                                r["insert_before"], r["html"] + "\n" + r["insert_before"])
                            write_page("whitepaper", wp_text)
                            print("    Updated White Paper Series")
                except (json.JSONDecodeError, KeyError):
                    pass

    _time.sleep(3)

    # --- 6. GAP ANALYSIS + ROADMAP GAP CLOSURE ---
    # This is the CONTEXTUAL step — checks if any new paper closes a known gap.
    # Needs full description (not truncated) and the actual gap table.
    gap_text = read_page("gap")
    roadmap_text = read_page("roadmap")

    if gap_text and paper_descs:
        # Build richer paper context for gap matching
        rich_descs = []
        for p in paper_list[:20]:
            dirpath = os.path.join(PAPERS, p["directory"])
            idx_path = os.path.join(dirpath, "index.json")
            if os.path.exists(idx_path):
                with open(idx_path) as f:
                    idx = json.load(f)
                rich_descs.append({
                    "directory": p["directory"],
                    "title": idx.get("title", ""),
                    "doi": idx.get("doi", ""),
                    "description": idx.get("description", "")[:500],
                    "paper_type": idx.get("paper_type", idx.get("type", "")),
                    "key_results": {
                        "main_finding": idx.get("key_results", {}).get("main_finding", "") if isinstance(idx.get("key_results"), dict) else "",
                    },
                    "kill_criteria": idx.get("kill_criteria", [])[:3],
                    "keywords": idx.get("keywords", [])[:8],
                })

        # Extract gap table section specifically
        gap_table = ""
        for marker in ["<thead><tr><th>Gap</th>", "Theory Gaps", "Gap Analysis"]:
            pos = gap_text.find(marker)
            if pos > 0:
                gap_table = gap_text[pos:pos + 3000]
                break
        if not gap_table:
            gap_table = gap_text[3000:6000]  # fallback to middle section

        # Also extract roadmap gap table
        roadmap_gaps = ""
        if roadmap_text:
            for marker in ["<thead><tr><th>Gap</th>", "Theory Gaps"]:
                pos = roadmap_text.find(marker)
                if pos > 0:
                    roadmap_gaps = roadmap_text[pos:pos + 2000]
                    break

        prompt = f"""You are checking if any new EFC paper CLOSES a known gap in the Gap Analysis or Roadmap.

NEW PAPERS (with full descriptions and keywords):
{json.dumps(rich_descs, indent=2)[:6000]}

CURRENT GAP TABLE (from Gap Analysis):
{gap_table[:3000]}

CURRENT ROADMAP GAPS:
{roadmap_gaps[:2000]}

IMPORTANT: A paper closes a gap if its description, keywords, or key_results directly address the gap's topic.
For example: a paper about "Bellini-Sawicki alpha functions" closes the gap "Bellini-Sawicki α-function mapping: Not started".

For EACH gap that is closed by a new paper, respond with a JSON array of updates:
[
  {{
    "page": "gap" or "roadmap",
    "old_text": "exact text to find in the HTML (the gap row or cell text)",
    "new_text": "replacement with CLOSED status and DOI link",
    "reason": "why this paper closes this gap"
  }}
]

If no gaps are closed: respond with []
Be precise with old_text — it must match exactly."""

        result = call_gpt5(prompt, max_tokens=2000)
        if result:
            try:
                updates = json.loads(result)
                if isinstance(updates, list):
                    for upd in updates:
                        page = upd.get("page", "gap")
                        old = upd.get("old_text", "")
                        new = upd.get("new_text", "")
                        reason = upd.get("reason", "")
                        if old and new:
                            text = gap_text if page == "gap" else (roadmap_text or "")
                            if old in text:
                                text = text.replace(old, new)
                                if page == "gap":
                                    gap_text = text
                                    write_page("gap", gap_text)
                                else:
                                    roadmap_text = text
                                    write_page("roadmap", roadmap_text)
                                print(f"    Closed gap ({page}): {reason[:60]}")
            except (json.JSONDecodeError, KeyError):
                pass


# ═══════════════════════════════════════════════════════════
# Auto-register DOIs in evidence register
# ═══════════════════════════════════════════════════════════

def update_evidence_register(paper_list):
    """Add new DOIs to the evidence register if not already present."""
    er_path = os.path.join(REPO, "docs", "validation-ledger", "data", "evidence-register.json")
    if not os.path.exists(er_path):
        return

    with open(er_path) as f:
        er = json.load(f)

    empirical = er.get("categories", {}).get("empirical", [])
    existing_dois = {e.get("doi") for e in empirical}

    added = 0
    for p in paper_list:
        dirpath = os.path.join(PAPERS, p["directory"])
        idx_path = os.path.join(dirpath, "index.json")
        if not os.path.exists(idx_path):
            continue
        with open(idx_path) as f:
            idx = json.load(f)
        doi = idx.get("doi", "")
        if not doi:
            continue
        # Extract just the figshare ID
        doi_id = doi.split("/")[-1] if "/" in doi else doi
        if doi_id not in existing_dois:
            paper_type = idx.get("paper_type", idx.get("type", "unknown"))
            cat = "empirical" if paper_type in ("empirical_test", "sealed_prediction") else "structural"
            empirical.append({
                "doi": doi_id,
                "name": idx.get("title", p["directory"])[:80],
                "category": cat,
            })
            existing_dois.add(doi_id)
            added += 1

    if added > 0:
        er["categories"]["empirical"] = empirical
        with open(er_path, "w") as f:
            json.dump(er, f, indent=2)
        print(f"    Added {added} DOI(s) to evidence register")


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

    pdftotext_bin = _find_pdftotext()

    print("=" * 60)
    print("EFC AI BRAIN — Full Autonomous Processing")
    print(f"Model: {MODEL}")
    print(f"Mode: {'DRY-RUN' if dry_run else 'LIVE'}")
    print(f"API key: {'SET' if api_key else 'NOT SET'}")
    print(f"pdftotext: {pdftotext_bin or 'NOT FOUND'}")
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
        import time as _time
        print(f"\n>>> Step 1: Enriching {len(needs_enrichment)} paper(s) to 10/10 <<<\n")
        enriched_count = 0
        for idx_num, p in enumerate(needs_enrichment):
            # Rate limit: 3s pause between API calls to avoid empty responses
            if idx_num > 0 and not dry_run:
                _time.sleep(3)
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
            update_evidence_register(page_papers)
        else:
            for p in page_papers:
                print(f"  [DRY-RUN] Would register: {p['directory']}")
    else:
        print("\n>>> Step 2: All papers registered in public pages <<<")

    # Step 3: Register DOIs from enriched papers (even if already in public pages)
    all_papers = load_unprocessed_for_pages() or []
    if not dry_run and needs_enrichment:
        update_evidence_register(needs_enrichment)

    print(f"\n{'=' * 60}")
    print("EFC AI BRAIN — done")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
