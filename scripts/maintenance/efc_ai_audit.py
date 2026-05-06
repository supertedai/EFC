#!/usr/bin/env python3
"""
EFC AI Consistency Auditor

Scans all public-facing pages and README, extracts key claims (numbers,
predictions, status badges, kill criteria, paper counts), and uses
OpenAI to cross-check consistency. Outputs a structured report.

Requires: OPENAI_API_KEY environment variable.
Usage: python3 scripts/maintenance/efc_ai_audit.py [--fix]
"""
from __future__ import annotations
import json
import os
import re
import sys
import datetime

# ── Config ──────────────────────────────────────────────
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PUBLIC = os.path.join(REPO, "docs", "public")
PAPERS = os.path.join(REPO, "docs", "papers", "efc")

AUDIT_FILES = {
    "README": os.path.join(REPO, "README.md"),
    "Elevator_Pitch": os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    "Validation_Ledger": os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    "Likelihood_Ledger": os.path.join(PUBLIC, "EFC_Likelihood_Ledger.html"),
    "Evaluation_Ledger": os.path.join(PUBLIC, "EFC_Evaluation_Ledger.html"),
    "Model_Comparison": os.path.join(PUBLIC, "EFC_Model_Comparison.html"),
    "Master_v1_1": os.path.join(PUBLIC, "EFC_Master_v1.1.html"),
    "White_Paper_Series": os.path.join(PUBLIC, "EFC_White_Paper_Series.html"),
    "Stage_IV_Roadmap": os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html"),
    "Gap_Analysis": os.path.join(PUBLIC, "EFC_Gap_Analysis.html"),
    "External_Research_Ledger": os.path.join(PUBLIC, "EFC_External_Research_Ledger.html"),
    "Predictions": os.path.join(PUBLIC, "EFC_Predictions.html"),
    "Atlas": os.path.join(PUBLIC, "EFC_Atlas.html"),
    "Changelog": os.path.join(PUBLIC, "EFC_Changelog.html"),
    "pipelines_README": os.path.join(REPO, "pipelines", "README.md"),
}

MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")  # Best available reasoning model
MAX_CHARS_PER_FILE = 12000  # Truncate large files for API context


def count_paper_dirs():
    """Count actual paper directories on disk."""
    skip = {"README.md", "cover_letter-2.pdf", "efc_graph_edges.json",
            "efc_graph_schema.json", "efc_index.json", "efc_index.jsonld",
            "ai_friendly_index.json"}
    count = 0
    for name in os.listdir(PAPERS):
        if name in skip:
            continue
        if os.path.isdir(os.path.join(PAPERS, name)):
            count += 1
    return count


def extract_numbers(text):
    """Extract key numerical claims from text."""
    findings = {}
    # Paper/package counts
    for m in re.finditer(r'(\d{2,3})\s*(?:papers?|packages?|paper dir)', text):
        findings.setdefault('paper_counts', []).append(int(m.group(1)))
    # Test counts
    for m in re.finditer(r'(\d{2,3})\s*(?:tests?|independent tests?)', text):
        findings.setdefault('test_counts', []).append(int(m.group(1)))
    # Kill criteria counts
    for m in re.finditer(r'(\d)\s*(?:kill criter|sealed.*predict)', text):
        findings.setdefault('kill_counts', []).append(int(m.group(1)))
    # Sigma values
    for m in re.finditer(r'(\d+\.?\d*)\s*[σ&]', text):
        findings.setdefault('sigma_values', []).append(m.group(1))
    # SHA-256 hashes
    for m in re.finditer(r'SHA-256[:\s]+([a-f0-9]{8,64})', text, re.IGNORECASE):
        findings.setdefault('sha256', []).append(m.group(1)[:16] + "...")
    # Pipeline status badges
    for m in re.finditer(r'(PREDICTION READY|IN PROGRESS|PIPELINE NEEDED|METHOD DEFINED|SEALED|PLANNED)', text):
        findings.setdefault('status_badges', []).append(m.group(1))
    return findings


def read_file_truncated(path, max_chars=MAX_CHARS_PER_FILE):
    """Read file, truncate if too large."""
    if not os.path.exists(path):
        return f"[FILE NOT FOUND: {path}]"
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    if len(content) > max_chars:
        # Keep start and end for context
        half = max_chars // 2
        content = content[:half] + f"\n\n[... TRUNCATED {len(content)-max_chars} chars ...]\n\n" + content[-half:]
    return content


def load_ledger_stats_for_audit():
    """Load ledger stats for ground truth."""
    stats_path = os.path.join(REPO, "docs", "validation-ledger", "data", "stats.json")
    if os.path.exists(stats_path):
        with open(stats_path, encoding="utf-8") as f:
            data = json.load(f)
            return data.get("stats", data)
    return {}


def find_sealed_prediction_papers():
    """Find all papers with paper_type: sealed_prediction and their DOIs."""
    sealed = []
    for name in os.listdir(PAPERS):
        d = os.path.join(PAPERS, name)
        idx_path = os.path.join(d, "index.json")
        if not os.path.isdir(d) or not os.path.exists(idx_path):
            continue
        try:
            with open(idx_path, encoding="utf-8") as f:
                idx = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        if idx.get("paper_type") in ("sealed_prediction", "observational_pipeline"):
            sealed.append({
                "doi": idx.get("doi", ""),
                "title": idx.get("title", name),
                "keywords": idx.get("keywords", []),
            })
    return sealed


def build_audit_prompt(file_contents, ground_truth):
    """Build the prompt for OpenAI."""
    stats = ground_truth.get("ledger_stats", {})
    sealed_papers = ground_truth.get("sealed_papers", [])

    stats_block = ""
    if stats:
        total = stats.get("total_public", "?")
        planned = stats.get("planned_pipeline", "?")
        falsified = stats.get("n_falsified", "?")
        active = total - planned if isinstance(total, int) and isinstance(planned, int) else "?"
        survived = active - falsified if isinstance(active, int) and isinstance(falsified, int) else "?"
        stats_block = f"""- Test counts from ledger.json: total={total}, active={active}, survived={survived}, falsified={falsified}, pipeline={planned}
"""

    sealed_block = ""
    if sealed_papers:
        lines = [f"  - {sp['doi']} — {sp['title'][:80]}" for sp in sealed_papers[:10]]
        sealed_block = f"- Sealed prediction DOIs ({len(sealed_papers)} total):\n" + "\n".join(lines) + "\n"

    prompt = f"""You are a scientific repository auditor. Your job is to verify
that all public-facing documents in the EFC (Energy-Flow Cosmology) repository
are internally consistent — that numbers, claims, status badges, predictions,
and kill criteria match across all pages.

## Ground Truth (from filesystem)
- Paper directories on disk: {ground_truth['paper_count']}
- Date: {ground_truth['date']}
{stats_block}{sealed_block}
## Documents to Audit

"""
    for name, content in file_contents.items():
        prompt += f"### {name}\n```\n{content}\n```\n\n"

    prompt += """## Your Task

Check the following and report PASS, WARN, or FAIL for each:

1. **PAPER COUNT**: Do all pages agree on the number of papers/packages?
   Check README badge, README text, pipelines README, Ledger mentions.

2. **TEST COUNT**: Do all pages agree on the number of tests (e.g. "103 tests")?

3. **KILL CRITERIA**: Are the same 5 kill criteria (KC1-KC5) listed consistently
   across Roadmap, White Paper, Ledger, and Elevator Pitch?

4. **SEALED PREDICTIONS**: Do all pages agree on how many sealed predictions
   exist? Are the SHA-256 hashes consistent where mentioned?

5. **PIPELINE STATUS**: Are the pipeline status badges in the Roadmap consistent
   with what the pipeline README and Ledger say?

6. **EUCLID PREDICTIONS**: Are the Euclid DR1 benchmark numbers (sigma8 +1.21%,
   P(k) +2.09%, lensing -6.01%, E_G -3.98%) consistent across all pages
   that mention them?

7. **PARAMETER CONSTRAINTS**: Are M0<0.1 (Planck ISW) and M0>=3*B0 (stability)
   consistently stated?

8. **CONFIRMATION LADDER**: Is the confirmation ladder (Hint->Suggestive->
   Evidence->Detection) consistent between Roadmap and White Paper?

9. **VERSION/DATE CONSISTENCY**: Are version numbers and dates consistent?

10. **LANGUAGE COMPLIANCE**: No page claims EFC is "proven" or "confirmed"
    (forbidden language per RCMP).

11. **TEST COUNT CROSS-PAGE CONSISTENCY**: Every public page that mentions
    test counts must show the SAME numbers as the ground truth from
    ledger.json. Check Elevator Pitch, White Paper Series, Stage-IV Roadmap,
    and Gap Analysis intro sections. Stale numbers (e.g. "106 tests" when
    ledger says 118) are a FAIL.

12. **KC STATUS vs SEALED DOIs**: For each Kill Criterion (KC1-KC5) that is
    marked "NOT STARTED" or "PIPELINE NEEDED" in any public page, check if a
    sealed prediction DOI exists (listed in ground truth above) that should
    have closed it. A KC marked stale when a sealed DOI covers it is a FAIL.

For each check, state:
- PASS / WARN / FAIL
- Brief explanation (1-2 sentences)
- If FAIL: what specifically is wrong and in which file

End with a SUMMARY line: X/12 PASS, Y WARN, Z FAIL.
"""
    return prompt


def call_openai(prompt):
    """Call OpenAI API."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[ERROR] OPENAI_API_KEY not set. Set it as environment variable.")
        sys.exit(1)

    try:
        import openai
    except ImportError:
        # Minimal HTTP fallback
        import urllib.request
        import urllib.error
        import ssl

        ctx = ssl.create_default_context()
        req = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps({
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_completion_tokens": 4000,
            }).encode(),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=180) as resp:
                body = resp.read()
                data = json.loads(body)
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="replace")
            print(f"[ERROR] OpenAI API HTTP {e.code}: {body[:500]}")
            sys.exit(1)
        except Exception as e:
            print(f"[ERROR] OpenAI API call failed: {e}")
            sys.exit(1)

    client = openai.OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=4000,
    )
    return resp.choices[0].message.content


def main():
    print("=" * 70)
    print("EFC AI CONSISTENCY AUDIT")
    print(f"Date: {datetime.date.today().isoformat()}")
    print(f"Model: {MODEL}")
    print("=" * 70)

    # Ground truth
    paper_count = count_paper_dirs()
    print(f"\nGround truth: {paper_count} paper directories on disk")

    # Read all files
    file_contents = {}
    for name, path in AUDIT_FILES.items():
        content = read_file_truncated(path)
        file_contents[name] = content
        nums = extract_numbers(content)
        print(f"  {name}: {len(content)} chars"
              + (f", papers mentioned: {nums.get('paper_counts', [])}" if nums.get('paper_counts') else "")
              + (f", tests: {nums.get('test_counts', [])}" if nums.get('test_counts') else ""))

    # Build prompt with extended ground truth
    ledger_stats = load_ledger_stats_for_audit()
    sealed_papers = find_sealed_prediction_papers()
    if ledger_stats:
        print(f"  Ledger: total_public={ledger_stats.get('total_public', '?')}, "
              f"n_falsified={ledger_stats.get('n_falsified', '?')}, "
              f"planned_pipeline={ledger_stats.get('planned_pipeline', '?')}")
    print(f"  Sealed prediction papers: {len(sealed_papers)}")

    ground_truth = {
        "paper_count": paper_count,
        "date": datetime.date.today().isoformat(),
        "ledger_stats": ledger_stats,
        "sealed_papers": sealed_papers,
    }
    prompt = build_audit_prompt(file_contents, ground_truth)
    print(f"\nPrompt size: {len(prompt)} chars")
    print("\nCalling OpenAI API...")

    # Call API
    result = call_openai(prompt)

    print("\n" + "=" * 70)
    print("AUDIT RESULT")
    print("=" * 70)
    print(result)

    # Save report
    report_path = os.path.join(REPO, "docs", "audit_report.md")
    with open(report_path, "w") as f:
        f.write(f"# EFC AI Consistency Audit Report\n\n")
        f.write(f"**Date:** {datetime.date.today().isoformat()}\n")
        f.write(f"**Model:** {MODEL}\n")
        f.write(f"**Paper directories:** {paper_count}\n\n")
        f.write("---\n\n")
        f.write(result)
    print(f"\nReport saved to {report_path}")

    # Exit code: parse the SUMMARY line for actual failures
    # Matches patterns like "0 FAIL", "2 FAIL", "Z FAIL"
    summary_match = re.search(r'(\d+)\s*FAIL', result)
    actual_fails = int(summary_match.group(1)) if summary_match else 0
    if actual_fails > 0:
        print(f"\n[AUDIT] {actual_fails} FAIL(s) detected")
        return 1
    print("\n[AUDIT] All checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
