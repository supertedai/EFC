#!/usr/bin/env python3
"""
efc_render_ledger.py — [PHASE2_STAGED] Render HTML from ledger.json.

⚠️  STAGED. Would overwrite docs/public/EFC_Validation_Ledger.html
    (currently 2135 lines) with a ~200-line regeneration if run.
    See scripts/maintenance/phase2/README.md (Conflict 3).  ⚠️

Execution is blocked unless --i-know-this-is-staged is passed AND the
output path is explicitly redirected away from the live location.
"""

from __future__ import annotations
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ledger_schema import STATUS_EMOJI, SECTOR_MARK, Status, Tier  # noqa: E402


REPO_ROOT = Path(__file__).resolve().parents[3]


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def doi_link(doi_id: str) -> str:
    return f'<a href="https://doi.org/10.6084/m9.figshare.{doi_id}">{doi_id}</a>'


def tier_badge(tier: str) -> str:
    return f'<span class="tier-badge">{tier}</span>' if tier else ""


def status_cell(entry: dict) -> str:
    status = entry.get("status", "")
    emoji = STATUS_EMOJI.get(status, "")
    tier = entry.get("tier", "")
    text = entry.get("status_text", "")
    badge = tier_badge(tier)
    if not text:
        STATUS_LABELS = {
            Status.CONSISTENT_ROBUST: "Consistent (robust)",
            Status.CONSISTENT_PRELIMINARY: "Consistent (preliminary)",
            Status.COMPLETED_LIKELIHOOD: "Completed (Data Likelihood Test)",
            Status.COMPLETED_CONSISTENCY: "Completed (Consistency Check)",
            Status.COMPLETED_STRUCTURAL: "Completed (Structural Constraint)",
            Status.PHENOMENOLOGICAL: "Phenomenological",
            Status.FRAMEWORK_DIAGNOSTIC: "Framework-Level Diagnostic",
            Status.PLANNED_READY: "Planned (Pipeline Ready)",
            Status.CONCEPTUAL: "Conceptual / Method Defined",
            Status.DISCREPANT: "Discrepant",
            Status.INACTIVE: "Inactive / Not Dominant",
            Status.FALSIFIED: "Falsified",
        }
        text = STATUS_LABELS.get(status, status)
    return f"{emoji} {badge} <strong>{text}</strong>" if badge else f"{emoji} <strong>{text}</strong>"


def sector_cell(value: str) -> str:
    return SECTOR_MARK.get(value, value)


def evidence_cell(dois: list) -> str:
    if not dois:
        return "—"
    links = [doi_link(d) for d in dois[:5]]
    result = ", ".join(links)
    if len(dois) > 5:
        result += f" (+{len(dois) - 5} more)"
    return result


def render_executive_summary(ledger: dict) -> str:
    total = ledger.get("total_tests", 0)
    passed = ledger.get("passed", 0)
    partial = ledger.get("partial", 0)
    failed = ledger.get("failed", 0)
    planned = ledger.get("planned", 0)
    entries = ledger.get("entries", [])
    robust = [e for e in entries if e.get("status") == Status.CONSISTENT_ROBUST]
    preliminary = [e for e in entries if e.get("status") == Status.CONSISTENT_PRELIMINARY]
    discrepant = [e for e in entries if e.get("status") == Status.DISCREPANT]
    robust_summary = "; ".join(e.get("phenomenon", "") for e in robust[:4])
    preliminary_summary = "; ".join(e.get("phenomenon", "") for e in preliminary[:4])
    discrepant_summary = "none" if not discrepant else "; ".join(
        e.get("phenomenon", "") for e in discrepant
    )
    return f"""
<p><strong>🔵 Stage: Non-rejectable model.</strong> EFC cannot be rejected on current data
and shows consistent Δχ² ≤ 0 across independent probes.
<strong>Global verdict remains OPEN.</strong></p>

<p>✅ <strong>Consistent (robust):</strong> {robust_summary}.
🟡 <strong>Consistent (preliminary / limited sample):</strong> {preliminary_summary}.
⚪ <strong>Neutral by construction:</strong> CMB primary (αS → 0 at z &gt; 1100).
🔴 <strong>Discrepant:</strong> {discrepant_summary}.</p>

<p><em>Totals: {total} tests — ✅ {passed} passed, ⚠️ {partial} partial,
❌ {failed} failed, 📋 {planned} planned</em></p>
"""


def render_main_table(entries: list) -> str:
    main_entries = [e for e in entries if e.get("section", "main") == "main"]
    rows = []
    for e in main_entries:
        dois = e.get("evidence_dois", [])
        rows.append(
            f"""<tr>
  <td><strong>{e.get("phenomenon", "")}</strong></td>
  <td>{e.get("datasets", "")}</td>
  <td>{sector_cell(e.get("efc_s", "na"))}</td>
  <td>{sector_cell(e.get("efc_d", "na"))}</td>
  <td>{sector_cell(e.get("efc_c", "na"))}</td>
  <td>{sector_cell(e.get("lcdm", "na"))}</td>
  <td>{e.get("regime_interpretation", "")}</td>
  <td>{status_cell(e)}</td>
  <td>{evidence_cell(dois)}</td>
</tr>"""
        )
    return f"""
<h2>1. Validation Status Summary (Regime-Aware)</h2>
<table>
<thead>
<tr>
  <th>Phenomenon</th><th>Primary dataset(s)</th>
  <th>EFC-S</th><th>EFC-D</th><th>EFC-C</th><th>ΛCDM</th>
  <th>Regime interpretation</th><th>Status</th><th>Evidence</th>
</tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
"""


def render_falsification_conditions(ledger: dict) -> str:
    conditions = ledger.get("falsification_conditions", [])
    if not conditions:
        return ""
    rows = []
    for fc in conditions:
        rows.append(
            f"""<tr>
  <td><strong>{fc.get("id", "")}</strong></td>
  <td>{fc.get("condition", "")}</td>
  <td>{fc.get("sector", "")}</td>
  <td>{fc.get("consequence", "")}</td>
</tr>"""
        )
    return f"""
<h2>3.1 Explicit Falsification Conditions</h2>
<table>
<thead>
<tr><th>#</th><th>Condition</th><th>Sector</th><th>Consequence if observed</th></tr>
</thead>
<tbody>
{"".join(rows)}
</tbody>
</table>
"""


def render_evidence_register(ledger: dict) -> str:
    sections = []
    for category, title in (
        ("evidence_empirical", "Empirical & Phenomenological"),
        ("evidence_structural", "Structural / Theoretical Constraints"),
        ("evidence_methodological", "Methodological / Core Framework"),
    ):
        dois = ledger.get(category, [])
        if dois:
            items = "\n".join(f"  <li>{doi_link(d)}</li>" for d in dois)
            sections.append(f"<h3>{title}</h3>\n<ul>\n{items}\n</ul>")
    return f'<h2>4. Evidence Register (Citable Artifacts)</h2>\n{"".join(sections)}\n'


def render_full_html(ledger: dict) -> str:
    entries = ledger.get("entries", [])
    version = ledger.get("version", "")
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Energy-Flow Cosmology (EFC) – Complete Validation Ledger</title>
<style>
:root {{
  --bg: #0a0a0f; --fg: #e8e6e3; --accent: #4a9eff;
  --muted: #6b7280; --surface: #1a1a2e; --border: #2d2d44;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'IBM Plex Serif', 'Georgia', serif;
  background: var(--bg); color: var(--fg); line-height: 1.7;
  padding: 2rem; max-width: 1400px; margin: 0 auto;
}}
h1 {{ font-size: 1.8rem; margin: 2rem 0 1rem; color: var(--accent); }}
h2 {{ font-size: 1.4rem; margin: 2rem 0 0.8rem; border-bottom: 1px solid var(--border); padding-bottom: 0.3rem; }}
h3 {{ font-size: 1.1rem; margin: 1.5rem 0 0.5rem; color: var(--muted); }}
p {{ margin: 0.5rem 0; }}
a {{ color: var(--accent); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}
table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.85rem; }}
th, td {{ padding: 0.5rem 0.6rem; border: 1px solid var(--border); text-align: left; vertical-align: top; }}
th {{ background: var(--surface); font-weight: 600; }}
tr:hover {{ background: rgba(74, 158, 255, 0.05); }}
.tier-badge {{
  display: inline-block; background: var(--accent); color: var(--bg);
  font-size: 0.7rem; font-weight: 700; padding: 0.1rem 0.4rem;
  border-radius: 3px; margin-right: 0.3rem;
}}
.meta {{ color: var(--muted); font-size: 0.8rem; margin: 0.5rem 0; }}
ul {{ margin: 0.5rem 0 0.5rem 1.5rem; }}
hr {{ border: none; border-top: 1px solid var(--border); margin: 2rem 0; }}
</style>
</head>
<body>

<h1>Energy-Flow Cosmology (EFC) – Complete Validation Ledger</h1>

<p class="meta">Version {version} — Generated {generated} from
<code>docs/validation-ledger/ledger.json</code> by
<code>scripts/maintenance/phase2/efc_render_ledger.py</code> [STAGED]</p>

{render_executive_summary(ledger)}

<hr>

{render_main_table(entries)}

<hr>

{render_falsification_conditions(ledger)}

<hr>

{render_evidence_register(ledger)}

<hr>

<p class="meta">⚠️ This is a Phase 2 STAGED render — do not copy to the
live validation ledger path. The live HTML contains 2135 lines of
hand-curated content (stage banner, elevator pitch, §0.x architecture,
§4b externals, §6 recent updates) that this renderer does not yet
reproduce.</p>

</body>
</html>"""


def _phase2_safety_guard(args: argparse.Namespace) -> None:
    if not getattr(args, "i_know_this_is_staged", False):
        print(
            "ERROR: This is a PHASE 2 STAGED script that would replace the "
            "2135-line live Validation Ledger HTML with a ~200-line render.",
            file=sys.stderr,
        )
        print(
            "       See scripts/maintenance/phase2/README.md (Conflict 3).",
            file=sys.stderr,
        )
        print(
            "       Pass --i-know-this-is-staged AND --output <path> "
            "to test output to a staging path.",
            file=sys.stderr,
        )
        sys.exit(2)
    live = REPO_ROOT / "docs" / "public" / "EFC_Validation_Ledger.html"
    if args.output.resolve() == live.resolve():
        print(
            "ERROR: --output is pointing at the live HTML. Choose a different path.",
            file=sys.stderr,
        )
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="[PHASE2_STAGED] HTML renderer")
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/phase2_ledger_preview.html"),
        help="Output path for the rendered HTML (must NOT be the live path)",
    )
    parser.add_argument("--i-know-this-is-staged", action="store_true")
    args = parser.parse_args()

    _phase2_safety_guard(args)

    ledger_path = args.root / "docs" / "validation-ledger" / "ledger.json"
    if not ledger_path.exists():
        # Fall back to the bundled sample
        ledger_path = Path(__file__).parent / "ledger.json"
    if not ledger_path.exists():
        print(f"ERROR: ledger.json not found at {ledger_path}")
        sys.exit(1)

    ledger = load_json(ledger_path)
    print(f"Loaded ledger v{ledger.get('version', '?')} with {len(ledger.get('entries', []))} entries")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    html = render_full_html(ledger)
    args.output.write_text(html, encoding="utf-8")
    print(f"  Wrote preview HTML to {args.output}")
    print("  (Not touching the live EFC_Validation_Ledger.html)")


if __name__ == "__main__":
    main()
