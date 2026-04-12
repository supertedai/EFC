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
    "Validation_Ledger": os.path.join(PUBLIC, "EFC_Validation_Ledger.html"),
    "White_Paper_Series": os.path.join(PUBLIC, "EFC_White_Paper_Series.html"),
    "Elevator_Pitch": os.path.join(PUBLIC, "EFC_Elevator_Pitch.html"),
    "Stage_IV_Roadmap": os.path.join(PUBLIC, "EFC_Stage-IV_Data_Roadmap.html"),
    "Changelog": os.path.join(PUBLIC, "EFC_Changelog.html"),
    "pipelines_README": os.path.join(REPO, "pipelines", "README.md"),
}

MODEL = os.environ.get("OPENAI_MODEL", "o3")  # Best reasoning model available
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


def build_audit_prompt(file_contents, ground_truth):
    """Build the prompt for OpenAI."""
    prompt = f"""You are a scientific repository auditor. Your job is to verify
that all public-facing documents in the EFC (Energy-Flow Cosmology) repository
are internally consistent — that numbers, claims, status badges, predictions,
and kill criteria match across all pages.

## Ground Truth (from filesystem)
- Paper directories on disk: {ground_truth['paper_count']}
- Date: {ground_truth['date']}

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

For each check, state:
- PASS / WARN / FAIL
- Brief explanation (1-2 sentences)
- If FAIL: what specifically is wrong and in which file

End with a SUMMARY line: X/10 PASS, Y WARN, Z FAIL.
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
                "temperature": 0.1,
                "max_tokens": 4000,
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
        temperature=0.1,
        max_tokens=4000,
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

    # Build prompt
    ground_truth = {
        "paper_count": paper_count,
        "date": datetime.date.today().isoformat(),
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
