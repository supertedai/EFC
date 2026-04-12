#!/usr/bin/env python3
"""
efc_ai_monitor.py — Read-only AI observer of the EFC maintenance stack.

Runs a single Claude API call per invocation. Reads the current state
of the ledger, paper archive, and recent git commits, sends a
structured snapshot to Claude, and receives back a review with:

  - overall_health     : "green" | "yellow" | "red"
  - anomalies          : list of things that look wrong or stale
  - stale_entries      : ledger entries that haven't been touched in a long
                         time and might need revisiting
  - suggested_updates  : concrete changes the maintainer should consider
  - commentary         : one-paragraph plain-English summary

Writes two outputs:
  - docs/validation-ledger/ai_review.json  (machine-readable, structured)
  - docs/validation-ledger/ai_review.md    (human-readable, committed)

Design constraints
------------------
1. **Read-only.** Never writes to ledger.json, paper dirs, HTML, or
   workflows. Only its own two output files.
2. **Fail-safe.** If ``ANTHROPIC_API_KEY`` is not set, prints a
   message and exits 0. The workflow that wraps this script treats
   that as "secret not configured, skip gracefully" — it does not
   fail CI.
3. **Single API call.** Uses prompt caching (ephemeral) so repeated
   invocations are cheap.
4. **Cost-conscious.** Capped at ~8k input tokens and 2k output
   tokens. Truncates long lists before sending.
5. **No network beyond Anthropic.** No Figshare, no GitHub API, no
   arXiv — those are jobs for other scripts.
6. **Model choice.** Uses ``claude-sonnet-4-6`` — a good balance of
   reasoning and cost for this observe-and-summarise workload.

Usage
-----
    # Local dry-run (requires ANTHROPIC_API_KEY in env):
    python3 scripts/maintenance/efc_ai_monitor.py

    # Force summary even if API key missing (writes a stub review):
    python3 scripts/maintenance/efc_ai_monitor.py --dry-run

    # Custom output directory:
    python3 scripts/maintenance/efc_ai_monitor.py --out /tmp/review

Install ``anthropic`` SDK:
    pip install anthropic
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
LEDGER_DIR = REPO_ROOT / "docs" / "validation-ledger"
PAPERS_DIR = REPO_ROOT / "docs" / "papers" / "efc"

DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_GIT_COMMITS = 40
MAX_ANOMALY_LINES = 50
MAX_OUTPUT_TOKENS = 2048


def load_json(path: Path) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {}


def recent_commits(limit: int = MAX_GIT_COMMITS) -> list[str]:
    try:
        out = subprocess.check_output(
            ["git", "log", f"-{limit}", "--oneline", "--no-color"],
            cwd=str(REPO_ROOT),
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return [line.strip() for line in out.splitlines() if line.strip()]
    except (OSError, subprocess.CalledProcessError):
        return []


def collect_state() -> dict:
    """Gather a compact snapshot of the EFC maintenance state."""
    state: dict[str, Any] = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "repo": "supertedai/efc",
    }

    # Phase 1 ledger.json (canonical)
    phase1_ledger = load_json(LEDGER_DIR / "data" / "ledger.json")
    if phase1_ledger:
        stats = phase1_ledger.get("stats", {})
        state["phase1_ledger"] = {
            "version": phase1_ledger.get("version"),
            "generated_at": phase1_ledger.get("generated_at"),
            "stats": stats,
            "n_empirical": len(
                phase1_ledger.get("evidence_register", {}).get("empirical", [])
            ),
            "n_physics_test": len(phase1_ledger.get("tests", {}).get("physics_test", [])),
            "n_consistency_check": len(
                phase1_ledger.get("tests", {}).get("consistency_check", [])
            ),
            "n_planned_pipeline": len(
                phase1_ledger.get("tests", {}).get("planned_pipeline", [])
            ),
            "n_frontier_gaps": len(phase1_ledger.get("frontier_gaps", [])),
            "n_hypotheses": len(phase1_ledger.get("hypotheses", [])),
        }

    # Phase 2 sample (if present)
    phase2_ledger_path = LEDGER_DIR / "ledger.json"
    if phase2_ledger_path.exists():
        phase2 = load_json(phase2_ledger_path)
        state["phase2_ledger_sample"] = {
            "version": phase2.get("version"),
            "total_tests": phase2.get("total_tests"),
            "passed": phase2.get("passed"),
            "entries_sample": [
                {"id": e.get("id"), "status": e.get("status"), "phenomenon": e.get("phenomenon")}
                for e in phase2.get("entries", [])[:5]
            ],
        }

    # Paper archive summary
    ai_friendly = load_json(PAPERS_DIR / "ai_friendly_index.json")
    if ai_friendly:
        state["paper_archive"] = {
            "n_packages": ai_friendly.get("n_packages"),
            "last_generated": ai_friendly.get("generated"),
        }

    # Recent git activity
    commits = recent_commits()
    state["recent_commits"] = commits[:MAX_GIT_COMMITS]

    # Phase 2 staging presence
    state["phase2_staging_present"] = (REPO_ROOT / "scripts" / "maintenance" / "phase2").exists()

    return state


SYSTEM_PROMPT = """You are the EFC Maintenance Observer — a read-only
reviewer for the Energy-Flow Cosmology repository. Your job is to look
at the current state of the validation ledger, paper archive, and
recent commit history, and produce a structured review.

You MUST respond with a single JSON object matching this schema:

{
  "overall_health": "green" | "yellow" | "red",
  "anomalies": [
    {"severity": "low|medium|high", "area": "...", "description": "..."}
  ],
  "stale_entries": [
    {"id": "...", "reason": "...", "suggested_action": "..."}
  ],
  "suggested_updates": [
    {"priority": "low|medium|high", "target": "...", "action": "..."}
  ],
  "commentary": "One plain-English paragraph summarising the state."
}

Scoring rules:
- green  = pipeline is healthy, no action needed
- yellow = something is drifting, stale, or inconsistent
- red    = a critical invariant is broken (missing ledger, zero tests,
            hook failure, etc.)

Be conservative: suggest only concrete, small changes. Do NOT propose
architectural rewrites or new features unless explicitly asked. Do not
invent DOIs, test IDs, or dates. If a field is missing from the input
snapshot, say so instead of guessing.

Respond with ONLY the JSON object — no prose around it, no markdown
fences."""


def build_user_message(state: dict) -> list[dict]:
    """Build the user message with prompt caching on the state snapshot."""
    snapshot_text = json.dumps(state, indent=2, ensure_ascii=False)
    if len(snapshot_text) > 30000:
        snapshot_text = snapshot_text[:30000] + "\n... [truncated]"
    return [
        {
            "type": "text",
            "text": "EFC maintenance state snapshot:\n\n```json\n"
            + snapshot_text
            + "\n```",
            "cache_control": {"type": "ephemeral"},
        },
        {
            "type": "text",
            "text": (
                "Review the snapshot above and respond with the JSON object "
                "described in the system prompt. Focus on: (1) stale or "
                "missing ledger entries, (2) recent commits that look "
                "suspicious or incomplete, (3) mismatches between the "
                "Phase 1 and Phase 2 ledger state, (4) any anomaly that a "
                "maintainer should see this week."
            ),
        },
    ]


def call_claude(state: dict, model: str) -> dict:
    """Call Claude once, return the parsed review JSON."""
    try:
        import anthropic  # type: ignore
    except ImportError:
        return {
            "overall_health": "yellow",
            "anomalies": [
                {
                    "severity": "low",
                    "area": "monitor",
                    "description": "anthropic SDK not installed — run `pip install anthropic`",
                }
            ],
            "stale_entries": [],
            "suggested_updates": [],
            "commentary": (
                "The AI monitor cannot produce a review because the anthropic "
                "SDK is not available in this environment. The snapshot was "
                "collected successfully; only the API call failed."
            ),
        }

    client = anthropic.Anthropic()
    messages = [{"role": "user", "content": build_user_message(state)}]

    response = client.messages.create(
        model=model,
        max_tokens=MAX_OUTPUT_TOKENS,
        system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
        messages=messages,
    )

    text_parts = [block.text for block in response.content if block.type == "text"]
    body = "".join(text_parts).strip()

    # Strip accidental markdown fences
    if body.startswith("```"):
        body = body.split("```", 2)[1]
        if body.startswith("json"):
            body = body[4:]
        body = body.strip()

    try:
        review = json.loads(body)
    except json.JSONDecodeError:
        review = {
            "overall_health": "yellow",
            "anomalies": [
                {
                    "severity": "medium",
                    "area": "monitor",
                    "description": "Claude response was not valid JSON; kept as raw text in commentary.",
                }
            ],
            "stale_entries": [],
            "suggested_updates": [],
            "commentary": body,
        }
    return review


def dry_run_stub(state: dict) -> dict:
    """Produce a deterministic stub review without calling the API."""
    n_packages = state.get("paper_archive", {}).get("n_packages", "?")
    n_tests = state.get("phase1_ledger", {}).get("stats", {}).get("total_public", "?")
    return {
        "overall_health": "green",
        "anomalies": [],
        "stale_entries": [],
        "suggested_updates": [],
        "commentary": (
            f"[DRY RUN] The EFC maintenance stack is running with {n_packages} "
            f"paper packages and {n_tests} public ledger tests. No API call was "
            f"made — this is a stub produced by --dry-run or because "
            f"ANTHROPIC_API_KEY was not set. Configure the secret to receive "
            f"actual Claude-powered reviews."
        ),
    }


def render_markdown(state: dict, review: dict) -> str:
    """Render the review as a committable Markdown document."""
    lines: list[str] = []
    lines.append("# EFC AI Monitor — Weekly Review")
    lines.append("")
    lines.append(f"_Generated {state.get('generated', '?')} by `scripts/maintenance/efc_ai_monitor.py`_")
    lines.append("")
    health = review.get("overall_health", "?")
    emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(health, "⚪")
    lines.append(f"## Overall health: {emoji} `{health}`")
    lines.append("")
    lines.append(review.get("commentary", ""))
    lines.append("")

    anomalies = review.get("anomalies", []) or []
    if anomalies:
        lines.append("## Anomalies")
        lines.append("")
        lines.append("| Severity | Area | Description |")
        lines.append("|---|---|---|")
        for a in anomalies[:MAX_ANOMALY_LINES]:
            sev = a.get("severity", "")
            area = a.get("area", "")
            desc = str(a.get("description", "")).replace("|", "\\|")
            lines.append(f"| {sev} | {area} | {desc} |")
        lines.append("")
    else:
        lines.append("## Anomalies")
        lines.append("")
        lines.append("_None reported._")
        lines.append("")

    stale = review.get("stale_entries", []) or []
    if stale:
        lines.append("## Stale entries")
        lines.append("")
        for s in stale[:MAX_ANOMALY_LINES]:
            lines.append(
                f"- **{s.get('id', '?')}** — {s.get('reason', '')}"
                f" → _{s.get('suggested_action', '')}_"
            )
        lines.append("")

    suggestions = review.get("suggested_updates", []) or []
    if suggestions:
        lines.append("## Suggested updates")
        lines.append("")
        for s in suggestions[:MAX_ANOMALY_LINES]:
            pri = s.get("priority", "")
            tgt = s.get("target", "")
            act = s.get("action", "")
            lines.append(f"- **[{pri}]** `{tgt}` — {act}")
        lines.append("")

    lines.append("## Snapshot metadata")
    lines.append("")
    p1 = state.get("phase1_ledger", {})
    if p1:
        lines.append(f"- Phase 1 ledger version: `{p1.get('version', '?')}`")
        lines.append(f"- Phase 1 tests (physics): {p1.get('n_physics_test', '?')}")
        lines.append(f"- Phase 1 consistency checks: {p1.get('n_consistency_check', '?')}")
        lines.append(f"- Phase 1 planned pipeline: {p1.get('n_planned_pipeline', '?')}")
        lines.append(f"- Phase 1 empirical DOIs: {p1.get('n_empirical', '?')}")
    pa = state.get("paper_archive", {})
    if pa:
        lines.append(f"- Paper packages: {pa.get('n_packages', '?')}")
    if state.get("phase2_staging_present"):
        lines.append("- Phase 2 staging directory: present (not active)")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "_This review is produced by a Claude API call to "
        "`claude-sonnet-4-6`. The monitor is read-only: it never modifies "
        "the ledger, paper archive, or public HTML. Its only outputs are "
        "`docs/validation-ledger/ai_review.json` and "
        "`docs/validation-ledger/ai_review.md`._"
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="EFC AI monitor — read-only observer")
    parser.add_argument("--model", default=DEFAULT_MODEL, help="Claude model to use")
    parser.add_argument(
        "--out",
        type=Path,
        default=LEDGER_DIR,
        help="Directory to write ai_review.json / ai_review.md (default: docs/validation-ledger/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Skip the API call and write a stub review (useful for CI without a secret)",
    )
    args = parser.parse_args()

    print("[efc-ai-monitor] collecting state snapshot…")
    state = collect_state()

    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    if args.dry_run or not has_key:
        if not has_key and not args.dry_run:
            print(
                "[efc-ai-monitor] ANTHROPIC_API_KEY not set — producing dry-run stub",
                file=sys.stderr,
            )
        review = dry_run_stub(state)
        mode = "dry-run"
    else:
        print(f"[efc-ai-monitor] calling Claude ({args.model})…")
        try:
            review = call_claude(state, args.model)
            mode = "live"
        except Exception as exc:
            print(f"[efc-ai-monitor] API call failed: {exc}", file=sys.stderr)
            review = {
                "overall_health": "yellow",
                "anomalies": [
                    {
                        "severity": "medium",
                        "area": "monitor",
                        "description": f"API call failed: {exc}",
                    }
                ],
                "stale_entries": [],
                "suggested_updates": [],
                "commentary": "The AI monitor could not reach Claude this run; snapshot was collected but not reviewed.",
            }
            mode = "error"

    args.out.mkdir(parents=True, exist_ok=True)
    json_path = args.out / "ai_review.json"
    md_path = args.out / "ai_review.md"

    output = {
        "generated": state["generated"],
        "mode": mode,
        "model": args.model if mode == "live" else None,
        "state_snapshot_summary": {
            "phase1_ledger_version": state.get("phase1_ledger", {}).get("version"),
            "n_paper_packages": state.get("paper_archive", {}).get("n_packages"),
            "n_recent_commits": len(state.get("recent_commits", [])),
            "phase2_staging_present": state.get("phase2_staging_present"),
        },
        "review": review,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(render_markdown(state, review))

    print(f"[efc-ai-monitor] wrote {json_path}")
    print(f"[efc-ai-monitor] wrote {md_path}")
    print(f"[efc-ai-monitor] mode={mode} overall_health={review.get('overall_health', '?')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
