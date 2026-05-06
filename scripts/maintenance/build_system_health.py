#!/usr/bin/env python3
"""Build docs/public/EFC_System_Health.html — single-page status dashboard.

Auto-generated from the in-repo state: counts, drift, sealed predictions,
guard summaries. The page is intended to give Morten a 30-second overview
without having to consult 13 separate public pages, the Symbiose
research_status briefing, GitHub Actions, and Mattermost.

Pulls from:
  .claude/orcid_sync_report.json     — ORCID truth (S1)
  figshare/doi-map.json              — DOI/repo mapping
  docs/validation-ledger/data/ledger.json  — Symbiose pipeline truth
  .seal-manifest.json                — sealed predictions

Output:
  docs/public/EFC_System_Health.html

Re-runs are byte-idempotent (modulo the generated_at timestamp), so the
hourly workflow that owns this file produces a stable git diff signal.
"""
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ORCID_CACHE = REPO_ROOT / ".claude" / "orcid_sync_report.json"
DOI_MAP = REPO_ROOT / "figshare" / "doi-map.json"
LEDGER_DATA = REPO_ROOT / "docs" / "validation-ledger" / "data" / "ledger.json"
SEAL_MANIFEST = REPO_ROOT / ".seal-manifest.json"
PUBLIC_DIR = REPO_ROOT / "docs" / "public"
OUTPUT = PUBLIC_DIR / "EFC_System_Health.html"

_NAV_SCRIPT = REPO_ROOT / "scripts" / "maintenance" / "efc_navbar_sync.py"
_nav_spec = importlib.util.spec_from_file_location("efc_navbar_sync", _NAV_SCRIPT)
_nav_module = importlib.util.module_from_spec(_nav_spec)
_nav_spec.loader.exec_module(_nav_module)
render_canonical_navbar = _nav_module.render_nav


def safe_read(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def truth() -> dict:
    orcid = safe_read(ORCID_CACHE)
    doi_map = safe_read(DOI_MAP)
    ledger = safe_read(LEDGER_DATA)
    seal = safe_read(SEAL_MANIFEST)
    stats = ledger.get("stats", {})
    totals = doi_map.get("totals", {})
    return {
        "orcid_works": orcid.get("orcid_works_count", "?"),
        "matched_count": orcid.get("matched_count", "?"),
        "missing_count": orcid.get("on_orcid_not_in_repo_count", "?"),
        "repo_paper_dirs": totals.get("repo_paper_dirs", "?"),
        "complete_packages": totals.get("complete_packages", "?"),
        "duplicate_doi_dirs": totals.get("duplicate_doi_dirs", "?"),
        "tests_total": stats.get("total_public", "?"),
        "n_falsified": stats.get("n_falsified", "?"),
        "planned_pipeline": stats.get("planned_pipeline", "?"),
        "physics_test": stats.get("physics_test", "?"),
        "sealed_count": len(seal.get("entries", [])),
        "sealed_files": [e.get("path", "") for e in seal.get("entries", [])],
        "checked_at": orcid.get("checked_at", ""),
    }


def status_pill(label: str, ok: bool) -> str:
    color = "#1a7a1a" if ok else "#c22"
    bg = "#e6f4e6" if ok else "#f9e3df"
    icon = "✓" if ok else "✗"
    return (
        f'<span style="display:inline-block;background:{bg};color:{color};'
        f'border:1px solid {color}33;border-radius:4px;padding:2px 8px;'
        f'font-size:0.78rem;font-weight:600;margin-right:6px;">'
        f"{icon} {label}</span>"
    )


def render_page() -> str:
    t = truth()
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    active = (
        t["tests_total"] - t["planned_pipeline"]
        if isinstance(t["tests_total"], int) and isinstance(t["planned_pipeline"], int)
        else "?"
    )
    survived = (
        active - t["n_falsified"]
        if isinstance(active, int) and isinstance(t["n_falsified"], int)
        else "?"
    )

    nav = render_canonical_navbar(active_href="EFC_System_Health.html")

    pills = [
        status_pill("ORCID synced", t["orcid_works"] != "?"),
        status_pill(
            f"DOI-map {t['repo_paper_dirs']} dirs",
            isinstance(t["repo_paper_dirs"], int) and t["repo_paper_dirs"] > 0,
        ),
        status_pill(
            f"{t['n_falsified']} falsified / {t['tests_total']} tests",
            isinstance(t["n_falsified"], int),
        ),
        status_pill(
            f"{t['sealed_count']} sealed predictions",
            t["sealed_count"] >= 3,
        ),
        status_pill(
            f"{t['missing_count']} missing on ORCID",
            t["missing_count"] in (0, "?"),
        ),
    ]

    sealed_rows = (
        "\n".join(
            f"<li><code>{path}</code></li>"
            for path in t["sealed_files"]
        )
        or "<li><em>No sealed manifest.</em></li>"
    )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Energy-Flow Cosmology (EFC) — System Health</title>
  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Roboto, Arial, sans-serif; line-height: 1.7;
            color: #1a1a2e; background: #ffffff; max-width: 1200px;
            margin: 0 auto; padding: 2rem 2.5rem 3rem; }}
    h1 {{ font-size: 1.8rem; color: #0d1b3e; border-bottom: 3px solid #007bff;
          padding-bottom: 0.6rem; margin-bottom: 1.2rem; }}
    h2 {{ font-size: 1.25rem; color: #1a3a6b; margin-top: 1.8rem; margin-bottom: 0.6rem;
          border-left: 4px solid #007bff; padding-left: 0.7rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
             gap: 0.75rem; margin: 1rem 0 1.5rem; }}
    .card {{ background: #fafbfd; border: 1px solid #d0d7e3; border-left: 4px solid #007bff;
             border-radius: 6px; padding: 12px 16px; }}
    .card .label {{ font-size: 0.75rem; text-transform: uppercase; color: #5b6a7a;
                    font-weight: 600; letter-spacing: 0.5px; }}
    .card .value {{ font-size: 1.6rem; color: #0d1b3e; font-weight: 700;
                    font-family: 'Courier New', monospace; }}
    code {{ font-family: 'Courier New', monospace; background: #f0f2f5;
            padding: 1px 5px; border-radius: 3px; font-size: 0.9em; }}
    .pills {{ margin: 1rem 0; }}
    .meta {{ font-size: 0.85rem; color: #5b6a7a; }}
    a {{ color: #0056b3; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>

<h1>Energy-Flow Cosmology (EFC) — System Health</h1>

{nav}

<p class="meta">Auto-generated by <code>scripts/maintenance/build_system_health.py</code>
  · Last refresh: {now}
  · ORCID cache: {t['checked_at']}</p>

<div class="pills">{''.join(pills)}</div>

<h2>Truth source counts</h2>
<div class="grid">
  <div class="card"><div class="label">ORCID works</div><div class="value">{t['orcid_works']}</div></div>
  <div class="card"><div class="label">Matched in repo</div><div class="value">{t['matched_count']}</div></div>
  <div class="card"><div class="label">Missing on ORCID</div><div class="value">{t['missing_count']}</div></div>
  <div class="card"><div class="label">Repo paper dirs</div><div class="value">{t['repo_paper_dirs']}</div></div>
  <div class="card"><div class="label">Complete packages</div><div class="value">{t['complete_packages']}</div></div>
  <div class="card"><div class="label">Duplicate-DOI dirs</div><div class="value">{t['duplicate_doi_dirs']}</div></div>
</div>

<h2>Validation ledger (Symbiose pipeline truth)</h2>
<div class="grid">
  <div class="card"><div class="label">Total tests</div><div class="value">{t['tests_total']}</div></div>
  <div class="card"><div class="label">Active probes</div><div class="value">{active}</div></div>
  <div class="card"><div class="label">Survived</div><div class="value">{survived}</div></div>
  <div class="card"><div class="label">Falsified</div><div class="value">{t['n_falsified']}</div></div>
  <div class="card"><div class="label">In pipeline</div><div class="value">{t['planned_pipeline']}</div></div>
  <div class="card"><div class="label">Physics tests</div><div class="value">{t['physics_test']}</div></div>
</div>

<h2>Sealed predictions ({t['sealed_count']})</h2>
<ul>{sealed_rows}</ul>

<h2>Cross-validation guards</h2>
<ul>
  <li><strong>navbar-sync</strong> — canonical 12-entry navbar on all 13 pages</li>
  <li><strong>page-consistency (P1–P4 + P8)</strong> — header banners, word/numeric falsified, ledger arithmetic, propagation notes, DOI cross-page anchoring</li>
  <li><strong>rootfile-consistency</strong> — Ledger version dual-track sync (public HTML + internal data)</li>
  <li><strong>sealed-prediction-guard</strong> — SHA-256 immutability for Euclid DR1 benchmark</li>
  <li><strong>figshare-presence</strong> — weekly per-DOI verification + auto-scaffold of missing entries</li>
  <li><strong>AI audit</strong> — GPT council reviews all 13 public pages weekly</li>
</ul>

<h2>References</h2>
<ul>
  <li><a href="EFC_Validation_Ledger.html">Validation Ledger</a> — sealed test ledger</li>
  <li><a href="EFC_Atlas.html">Framework Atlas</a> — cross-framework comparison</li>
  <li><a href="EFC_Predictions.html">Sealed Predictions</a> — frozen pre-registrations</li>
  <li><a href="../validation-ledger/data/ledger.json">ledger.json</a> — Symbiose pipeline raw data</li>
  <li><a href="../../figshare/doi-map.json">figshare/doi-map.json</a> — DOI ↔ repo dir mapping</li>
</ul>

</body>
</html>
"""


def main() -> None:
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(render_page(), encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
