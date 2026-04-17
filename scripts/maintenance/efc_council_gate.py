#!/usr/bin/env python3
"""
EFC Council Gate -- GPT-5 validation for proposed page updates.

Before any automated change is written to a public HTML page, this
module asks GPT-5 to verify the change is semantically correct.

The council checks:
  1. The DOI content actually supports the claimed update
  2. The action type is appropriate (sealed prediction -> SEALED, not DONE)
  3. No factual information is lost from the old element
  4. DOI references in new text are valid
  5. Numbers and values match the paper's actual content
  6. Language complies with RCMP (no "proves", "confirms")

Decision logic:
  - GPT-5 must explicitly say "APPROVED" with reasoning -> apply
  - Any other response -> reject (conservative, safe default)
  - No API key -> reject all, log warning
  - Network/timeout error -> reject

All decisions are logged to docs/council_log.json for audit trail.

Usage:
  from efc_council_gate import council_validate_page_update
  approved, reason = council_validate_page_update(...)
"""
from __future__ import annotations

import json
import os
import re
import sys
import datetime

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
COUNCIL_LOG = os.path.join(REPO, "docs", "council_log.json")
MODEL = os.environ.get("OPENAI_MODEL", "gpt-5")


def _call_openai(prompt: str) -> str | None:
    """Call OpenAI API. Returns response text or None on failure."""
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=2000,
        )
        return resp.choices[0].message.content
    except ImportError:
        pass

    # urllib fallback
    import urllib.request
    import urllib.error
    import ssl
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps({
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_completion_tokens": 2000,
        }).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=120) as resp:
            body = resp.read()
            data = json.loads(body)
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[COUNCIL] API error: {e}", file=sys.stderr)
        return None


def _log_decision(entry: dict) -> None:
    """Append a decision to the council log."""
    log = []
    if os.path.exists(COUNCIL_LOG):
        try:
            with open(COUNCIL_LOG, encoding="utf-8") as f:
                log = json.load(f)
        except (json.JSONDecodeError, OSError):
            log = []
    log.append(entry)
    # Keep last 200 entries
    if len(log) > 200:
        log = log[-200:]
    with open(COUNCIL_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)


def council_validate_page_update(
    page_name: str,
    action: str,
    target_id: str,
    old_html: str,
    new_html: str,
    paper_doi: str,
    paper_title: str,
    paper_kill_criteria: list | None = None,
    paper_sealed_predictions: list | None = None,
    paper_description: str = "",
) -> tuple[bool, str]:
    """Ask GPT-5 to validate a proposed page update.

    Returns (approved: bool, reason: str).
    """
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"

    # No API key = reject all (safe default)
    if not os.environ.get("OPENAI_API_KEY"):
        reason = "No OPENAI_API_KEY set -- all updates blocked (safe default)"
        print(f"[COUNCIL] REJECTED: {reason}")
        _log_decision({
            "timestamp": timestamp,
            "page": page_name,
            "target": target_id,
            "action": action,
            "doi": paper_doi,
            "verdict": "REJECTED",
            "reason": reason,
        })
        return False, reason

    # Build council prompt
    kc_text = ""
    if paper_kill_criteria:
        kc_text = "\n".join(f"  - {kc}" for kc in paper_kill_criteria[:5])

    sp_text = ""
    if paper_sealed_predictions:
        sp_lines = []
        for sp in paper_sealed_predictions[:5]:
            if isinstance(sp, dict):
                sp_lines.append(
                    f"  - {sp.get('id', '?')}: {sp.get('statement', '')[:200]}")
            else:
                sp_lines.append(f"  - {str(sp)[:200]}")
        sp_text = "\n".join(sp_lines)

    prompt = f"""You are a scientific integrity validator for the EFC (Energy-Flow Cosmology) repository.

A paper with DOI {paper_doi} is requesting an automated update to a public HTML page.
Your job is to decide whether this update is semantically correct and should be applied.

## Paper Information (from DOI content)
- **Title:** {paper_title}
- **Description:** {paper_description[:500]}
- **Kill Criteria declared in paper:**
{kc_text or '  (none)'}
- **Sealed Predictions:**
{sp_text or '  (none)'}

## Proposed Update
- **Page:** {page_name}
- **Target element:** {target_id}
- **Action:** {action}

### Current HTML (before):
```html
{old_html[:1500]}
```

### Proposed HTML (after):
```html
{new_html[:1500]}
```

## Your Task

Verify ALL of the following:
1. Does the DOI content (title, description, kill_criteria, sealed_predictions) actually support this update?
2. Is the action type appropriate for its kind?
   - update_badge: changes a status badge (SEALED, DONE, P3 PASS, PIPELINE NEEDED, etc.)
   - mark_done: strikes through the action and marks it DONE with DOI link
   - update_text: replaces text content inside the target element
   - add_row: inserts a new <tr> into a table (content in new_text must be complete valid HTML)
   - restructure_section: wholesale replacement of section body (use sparingly)
   A sealed prediction should typically become SEALED (not DONE). New distinctive predictions use add_row, not update_badge.
3. Is any factual information being lost from the old element? (add_row adds without removing; update_badge changes status only; update_text replaces text with equivalent content.)
4. Are DOI references in the new text valid and traceable to this paper?
5. Do numbers and values in the new text match the paper's actual content?
6. Does the language comply with RCMP? (no "proves EFC", "confirms EFC")

## Hedging is ALLOWED and ENCOURAGED

If the new text REPLACES strong claims with weaker, more accurate ones, this is GOOD not bad. Do NOT reject for hedging that makes claims more scientifically accurate:
- "proves" / "cannot" → "strongly disfavored" / "strongly disfavored within class" (when based on numerical scan, not proof)
- "no other model" → "distinctive within current model class" (when uniqueness is not universally established)
- Point prediction (η = 1.10) demoted to structural signature (μ < 1 ∧ Σ ≥ 1) when Monte Carlo robustness is low

These hedges REDUCE overclaiming. Approve them if the weaker claim is supported by the paper's evidence type (scan, MC robustness analysis, within-class analysis).

## Reinterpretation of prior DOIs

If the proposed text reattributes a signal from one channel to another (e.g., fσ₈ suppression from background α to perturbation μ<1 channel), this is allowed IF:
- The current paper contains explicit text supporting the reattribution
- The old DOI's observable claim (e.g., "fσ₈ lower than ΛCDM") is preserved
- Only the MECHANISM is reassigned, not the empirical finding

## Decision

If ALL 6 checks pass, respond with exactly:
VERDICT: APPROVED
REASONING: [your explanation of why each check passes, noting any hedging that was correctly applied]

If ANY check fails, respond with exactly:
VERDICT: REJECTED
REASONING: [which check(s) failed and why]

Be conservative about factual claims. Be permissive about hedging that reduces overclaiming. When in doubt about claims, REJECT; when in doubt about hedging, APPROVE.
"""

    response = _call_openai(prompt)

    if response is None:
        reason = "API call failed or timed out -- rejecting (conservative)"
        print(f"[COUNCIL] REJECTED: {reason}")
        _log_decision({
            "timestamp": timestamp,
            "page": page_name,
            "target": target_id,
            "action": action,
            "doi": paper_doi,
            "verdict": "REJECTED",
            "reason": reason,
        })
        return False, reason

    # Parse verdict -- only explicit APPROVED counts
    approved = bool(re.search(r"VERDICT:\s*APPROVED", response, re.IGNORECASE))
    reasoning_match = re.search(
        r"REASONING:\s*(.+)", response, re.DOTALL | re.IGNORECASE)
    reasoning = reasoning_match.group(1).strip()[:500] if reasoning_match else response[:500]

    verdict = "APPROVED" if approved else "REJECTED"
    print(f"[COUNCIL] {verdict}: {target_id} on {page_name} "
          f"(DOI {paper_doi.split('/')[-1] if '/' in paper_doi else paper_doi})")
    if not approved:
        print(f"[COUNCIL] Reason: {reasoning[:200]}")

    _log_decision({
        "timestamp": timestamp,
        "page": page_name,
        "target": target_id,
        "action": action,
        "doi": paper_doi,
        "verdict": verdict,
        "reason": reasoning,
        "model": MODEL,
        "full_response_length": len(response),
    })

    return approved, reasoning
