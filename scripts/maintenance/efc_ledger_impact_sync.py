#!/usr/bin/env python3
"""
EFC Ledger Impact Sync — DOI-gated deterministic mutation of the
Validation Ledger, stats counters, and Gap Analysis HTML.

For every paper under docs/papers/efc/<name>/index.json that has:

  - A registered DOI (`index.json["doi"]` populated), AND
  - A `ledger_impact` block with `status == "ready"`, AND
  - Not yet been applied (`applied_by_doi` != current DOI),

this script applies the declared impact exactly once:

  - `tests_added`    → appended to docs/validation-ledger/data/tests.json
  - `tests_updated`  → patches result/status fields of existing tests
  - `gaps_closed`    → flips <tr data-gap-id="..."> rows in
                        docs/public/EFC_Gap_Analysis.html to CLOSED
                        with a DOI link

After successful apply:
  - `applied_at`, `applied_by_doi` are written back to the paper's
    `index.json` (guarantees idempotence)
  - `stats.json["n_falsified"]`, `total_public`, and per-category counts
    are recomputed from tests.json

If a paper has no DOI → skipped, reported as "awaiting_doi" (this is
the "maintainer mode" the architecture demands — no DOI = no ledger
mutation, ever).

If a paper has DOI but `ledger_impact.status == "draft"` → skipped with
warning.

If `ledger_impact` references a test_id or gap_id that doesn't exist →
hard fail (exit 2), to prevent silent drift.

Modes:
  (default)     dry-run — prints plan, no file writes
  --apply       live mode — writes files + stamps applied_by_doi

Exit codes:
  0  no changes to apply (or dry-run completed successfully)
  1  changes applied (live mode) OR would be applied (dry-run)
  2  validation error — unknown test_id / gap_id / category / vocabulary
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PAPERS = os.path.join(REPO, "docs", "papers", "efc")
TESTS = os.path.join(REPO, "docs", "validation-ledger", "data", "tests.json")
STATS = os.path.join(REPO, "docs", "validation-ledger", "data", "stats.json")
GAP_HTML = os.path.join(REPO, "docs", "public", "EFC_Gap_Analysis.html")

EMPIRICAL_TYPES = {
    "empirical_test",
    "empirical_analysis",
    "empirical_validation",
    "sealed_prediction",
    "observational_pipeline",
}

KNOWN_RESULT_VOCAB = {
    "PASS",
    "MARGINAL",
    "COLLAPSED",
    "Planned",
    "REQUIRES_EXTERNAL_TOOL",
    "PIPELINE_NOT_READY",
    "DEGENERACY_LIMITED",
}

KNOWN_STATUS_VOCAB = {"success", "partial", "failed", "pending", "unknown"}


def extract_bare_doi(doi_str):
    if not doi_str:
        return None
    m = re.search(r"(\d{7,9})", str(doi_str))
    return m.group(1) if m else None


def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.write("\n")


def read_text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write_text(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def iter_papers():
    """Yield (paper_dir_name, index_path, index_data) for every paper."""
    if not os.path.isdir(PAPERS):
        return
    for name in sorted(os.listdir(PAPERS)):
        paper_dir = os.path.join(PAPERS, name)
        if not os.path.isdir(paper_dir):
            continue
        idx_path = os.path.join(paper_dir, "index.json")
        if not os.path.isfile(idx_path):
            continue
        try:
            yield name, idx_path, load_json(idx_path)
        except (OSError, json.JSONDecodeError):
            continue


def collect_gap_ids(html_text):
    """Return the set of data-gap-id values present in Gap_Analysis.html."""
    return set(re.findall(r'data-gap-id="([^"]+)"', html_text))


def collect_test_ids(tests_data):
    """Return {test_id: (category, row_dict)} across all categories."""
    out = {}
    for cat, rows in tests_data.get("categories", {}).items():
        for row in rows:
            tid = row.get("test_id")
            if tid:
                out[tid] = (cat, row)
    return out


def validate_impact(paper_name, impact, tests_by_id, gap_ids):
    """Return list of error strings (empty = valid)."""
    errors = []
    categories = {"physics_test", "consistency_check", "phenomenological",
                  "framework_constraint", "planned_pipeline"}

    for i, t in enumerate(impact.get("tests_added", [])):
        if t.get("category") not in categories:
            errors.append(
                f"{paper_name}: tests_added[{i}].category="
                f"{t.get('category')!r} unknown (must be one of {categories})"
            )
        if t.get("test_id") in tests_by_id:
            errors.append(
                f"{paper_name}: tests_added[{i}].test_id={t.get('test_id')!r} "
                f"already exists — use tests_updated instead"
            )
        if t.get("result") and t["result"] not in KNOWN_RESULT_VOCAB:
            errors.append(
                f"{paper_name}: tests_added[{i}].result={t.get('result')!r} "
                f"outside known vocabulary {sorted(KNOWN_RESULT_VOCAB)}"
            )
        if t.get("status") and t["status"] not in KNOWN_STATUS_VOCAB:
            errors.append(
                f"{paper_name}: tests_added[{i}].status={t.get('status')!r} "
                f"outside known vocabulary {sorted(KNOWN_STATUS_VOCAB)}"
            )

    for i, t in enumerate(impact.get("tests_updated", [])):
        tid = t.get("test_id")
        if tid not in tests_by_id:
            errors.append(
                f"{paper_name}: tests_updated[{i}].test_id={tid!r} "
                f"not found in tests.json"
            )

    for i, gid in enumerate(impact.get("gaps_closed", [])):
        if gid not in gap_ids:
            errors.append(
                f"{paper_name}: gaps_closed[{i}]={gid!r} — no matching "
                f"data-gap-id in EFC_Gap_Analysis.html"
            )
    return errors


def apply_tests_added(tests_data, additions, source_paper):
    """Append new test rows into tests.json categories."""
    for t in additions:
        cat = t["category"]
        row = {
            "test_id": t["test_id"],
            "name": t.get("name", ""),
            "description": t.get("description", ""),
            "result": t.get("result", ""),
            "status": t.get("status", "unknown"),
            "vl_category": cat,
            "also_phenomenological": None,
            "data_source": t.get("data_source", ""),
            "prediction": t.get("prediction", ""),
            "notes": f"Added by ledger_impact_sync from paper {source_paper}",
            "quantitative_result": t.get("quantitative_result"),
            "last_synced": now_iso(),
            "status_detail": t.get("status", "unknown"),
            "source_paper": source_paper,
        }
        tests_data["categories"].setdefault(cat, []).append(row)


def apply_tests_updated(tests_by_id, updates, source_paper):
    """Mutate existing test rows in place."""
    for u in updates:
        cat, row = tests_by_id[u["test_id"]]
        if "new_result" in u:
            row["result"] = u["new_result"]
        if "new_status" in u:
            row["status"] = u["new_status"]
            row["status_detail"] = u["new_status"]
        if u.get("evidence_summary"):
            prior = row.get("notes") or ""
            row["notes"] = (
                f"{prior}\n[ledger_impact {source_paper}]: "
                f"{u['evidence_summary']}"
            ).strip()
        row["last_synced"] = now_iso()


def recount_stats(tests_data, stats_data):
    """Recompute derived counters in stats.json from tests.json.

    n_falsified semantics: a test row counts as falsified if
    result == "COLLAPSED" OR status == "failed". The union is used
    because historically some rows carry the verdict in `result`
    (new entries) and others in `status` (legacy entries). The
    deterministic sync normalises on this union until a manual
    re-baselining pass reconciles the two fields.
    """
    per_cat = {}
    n_falsified = 0
    total = 0
    for cat, rows in tests_data.get("categories", {}).items():
        per_cat[cat] = len(rows)
        total += len(rows)
        for r in rows:
            result = str(r.get("result") or "").strip()
            status = str(r.get("status") or "").strip()
            if result == "COLLAPSED" or status == "failed":
                n_falsified += 1
    changes = []
    for k in ("physics_test", "consistency_check", "phenomenological",
             "framework_constraint", "planned_pipeline"):
        new = per_cat.get(k, 0)
        old = stats_data["stats"].get(k)
        if new != old:
            changes.append(f"{k}: {old} → {new}")
            stats_data["stats"][k] = new
    if stats_data["stats"].get("total_public") != total:
        changes.append(
            f"total_public: {stats_data['stats'].get('total_public')} → {total}"
        )
        stats_data["stats"]["total_public"] = total
    if stats_data["stats"].get("n_falsified") != n_falsified:
        changes.append(
            f"n_falsified: {stats_data['stats'].get('n_falsified')} → "
            f"{n_falsified}"
        )
        stats_data["stats"]["n_falsified"] = n_falsified
    stats_data["generated_at"] = now_iso()
    return changes


GAP_CLOSED_ROW_RE = re.compile(
    r'(<tr\s+data-gap-id="(?P<id>[^"]+)"[^>]*>)(?P<body>.*?)(</tr>)',
    re.DOTALL,
)


def apply_gaps_closed(html_text, gaps, bare_doi):
    """Return (new_html, list of actually-changed gap_ids).

    A row is 'closed' by:
      - inserting a `<span class="badge-done">CLOSED</span>` (with DOI
        anchor) into the <td> that currently carries a priority badge
      - leaving the rest of the row untouched so human formatting stays
    """
    changed = []
    doi_url = f"https://doi.org/10.6084/m9.figshare.{bare_doi}"
    closed_span = (
        f'<span class="badge-done">CLOSED</span> '
        f'(<a href="{doi_url}">{bare_doi}</a>)'
    )

    def _repl(match):
        gid = match.group("id")
        if gid not in gaps:
            return match.group(0)
        body = match.group("body")
        # If already marked CLOSED with this DOI, leave untouched
        if f"{bare_doi}</a>)" in body and "badge-done" in body and "CLOSED" in body:
            return match.group(0)
        # Replace the first priority badge we see, or inject into last <td>
        new_body, n = re.subn(
            r'<span\s+class="badge-(?:high|med|low)">[^<]*</span>',
            closed_span,
            body,
            count=1,
        )
        if n == 0:
            # No priority badge — inject at end of last <td>
            tds = list(re.finditer(r'<td[^>]*>(.*?)</td>', body, re.DOTALL))
            if tds:
                last = tds[-1]
                new_body = (
                    body[:last.start(1)]
                    + f"{closed_span} {last.group(1)}"
                    + body[last.end(1):]
                )
            else:
                new_body = body  # can't inject
        changed.append(gid)
        return match.group(1) + new_body + "</tr>"

    new_html = GAP_CLOSED_ROW_RE.sub(_repl, html_text)
    return new_html, changed


# ── Page update support (council-gated) ──────────────────────────────

PAGE_UPDATE_ROW_RE = re.compile(
    r'(<(?:tr|td|table|div|strong)\s+[^>]*data-(?:kc-id|action-id|section|landscape-id)='
    r'"(?P<id>[^"]+)"[^>]*>)(?P<body>.*?)(</(?:tr|td|table|div|strong)>)',
    re.DOTALL,
)

BADGE_RE = re.compile(
    r'<span\s+class="(?:badge-done|badge-high|badge-med|badge-low|'
    r'seal-badge|pipeline-badge|pass-badge|kill-badge)">'
    r'[^<]*</span>',
)

PAGE_FILE_MAP = {
    "gap": os.path.join(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")),
        "docs", "public", "EFC_Gap_Analysis.html"),
    "roadmap": os.path.join(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")),
        "docs", "public", "EFC_Stage-IV_Data_Roadmap.html"),
    "elevator": os.path.join(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")),
        "docs", "public", "EFC_Elevator_Pitch.html"),
    "whitepaper": os.path.join(os.path.abspath(os.path.join(
        os.path.dirname(__file__), "..", "..")),
        "docs", "public", "EFC_White_Paper_Series.html"),
}


def _load_council():
    """Import council gate, return validate function or None."""
    try:
        here = os.path.dirname(__file__)
        sys.path.insert(0, here)
        from efc_council_gate import council_validate_page_update
        return council_validate_page_update
    except ImportError:
        return None


def apply_page_updates(updates, bare_doi, idx, apply_mode):
    """Apply page_updates from ledger_impact, gated by GPT-5 council.

    Returns (list of planned actions, list of errors, dict of changed pages).
    """
    planned = []
    errors = []
    changed_pages = {}  # page_key -> new_html

    council_fn = _load_council()
    paper_doi = idx.get("doi", "")
    paper_title = idx.get("title", "?")
    paper_kc = idx.get("kill_criteria", [])
    paper_sp = idx.get("sealed_predictions", [])
    paper_desc = idx.get("description", "")

    for upd in updates:
        page_key = upd.get("page", "")
        target = upd.get("target", "")
        action = upd.get("action", "")
        new_badge = upd.get("new_badge", "")
        new_text = upd.get("new_text", "")
        doi_refs = upd.get("doi_refs", [])

        page_path = PAGE_FILE_MAP.get(page_key)
        if not page_path or not os.path.exists(page_path):
            errors.append(f"page_updates: unknown page '{page_key}'")
            continue

        # Load page HTML (use cached if already modified)
        if page_key in changed_pages:
            html = changed_pages[page_key]
        else:
            with open(page_path, encoding="utf-8", errors="replace") as f:
                html = f.read()

        # Find target element
        target_attr = target.replace('"', '"')
        target_re = re.compile(
            r'(<[^>]+' + re.escape(target_attr) + r'[^>]*>)(.*?)(</[^>]+>)',
            re.DOTALL,
        )
        match = target_re.search(html)
        if not match:
            errors.append(
                f"page_updates: target {target} not found in {page_key}")
            continue

        old_element = match.group(0)

        # Generate proposed new HTML based on action type
        if action == "update_badge":
            badge_class = {
                "SEALED": "seal-badge", "DONE": "badge-done",
                "PREDICTION READY": "pass-badge", "P3 PASS": "pass-badge",
                "PIPELINE NEEDED": "pipeline-badge", "HIGH": "badge-high",
                "PLANNED": "badge-med", "ACTIVE": "badge-high",
            }.get(new_badge, "badge-done")
            new_badge_html = f'<span class="{badge_class}">{new_badge}</span>'
            new_body = match.group(2)
            # Replace existing badge
            if BADGE_RE.search(new_body):
                new_body = BADGE_RE.sub(new_badge_html, new_body, count=1)
            else:
                new_body = new_badge_html + " " + new_body
            if new_text:
                # Replace text after badge in the same <td>
                # Find the <td> containing the badge and replace its content
                td_re = re.compile(r'(<td[^>]*>)(.*?)(</td>)', re.DOTALL)
                tds = list(td_re.finditer(new_body))
                if len(tds) >= 2:
                    # Replace second <td> content (status column)
                    td = tds[1]
                    doi_links = " ".join(
                        f'(<a href="https://doi.org/10.6084/m9.figshare.{d}">'
                        f'{d}</a>)' for d in doi_refs
                    )
                    new_body = (
                        new_body[:td.start(2)]
                        + f'{new_badge_html} {new_text} {doi_links}'
                        + new_body[td.end(2):]
                    )
            new_element = match.group(1) + new_body + match.group(3)

        elif action == "mark_done":
            done_text = upd.get("done_text", "DONE")
            doi_links = " ".join(
                f'(<a href="https://doi.org/10.6084/m9.figshare.{d}">{d}</a>)'
                for d in doi_refs
            )
            new_body = match.group(2)
            # Wrap existing text in <s> and append DONE
            new_body = re.sub(
                r'(<td[^>]*>)(.*?)(</td>)',
                lambda m: (
                    f'{m.group(1)}<s>{m.group(2)}</s> '
                    f'<strong>DONE</strong> {doi_links} {done_text}'
                    f'{m.group(3)}'
                ),
                new_body,
                count=1,
            )
            new_element = match.group(1) + new_body + match.group(3)

        elif action == "update_text":
            new_element = match.group(1) + new_text + match.group(3)

        else:
            errors.append(f"page_updates: unknown action '{action}'")
            continue

        desc = f"{action} {target} on {page_key}"
        planned.append(desc)

        if not apply_mode:
            continue

        # Council gate
        if council_fn:
            approved, reason = council_fn(
                page_name=page_key,
                action=action,
                target_id=target,
                old_html=old_element[:1500],
                new_html=new_element[:1500],
                paper_doi=paper_doi,
                paper_title=paper_title,
                paper_kill_criteria=paper_kc,
                paper_sealed_predictions=paper_sp,
                paper_description=paper_desc,
            )
            if not approved:
                errors.append(
                    f"page_updates: council REJECTED {desc}: {reason[:200]}")
                continue
        else:
            # No council available — reject (safe default)
            errors.append(
                f"page_updates: council module not available — "
                f"REJECTED {desc} (safe default)")
            continue

        # Apply the change
        html = html[:match.start()] + new_element + html[match.end():]
        changed_pages[page_key] = html

    # Write changed pages to disk
    if apply_mode:
        for page_key, new_html in changed_pages.items():
            page_path = PAGE_FILE_MAP[page_key]
            with open(page_path, "w", encoding="utf-8") as f:
                f.write(new_html)

    return planned, errors, changed_pages


def process_paper(paper_name, idx_path, idx, tests_data, stats_data,
                  gap_html, gap_ids, apply_mode):
    """Process one paper. Returns dict with actions + updated artifacts."""
    report = {
        "paper": paper_name,
        "status": "skip",
        "reason": "",
        "planned": [],
        "errors": [],
    }

    doi = idx.get("doi", "")
    bare = extract_bare_doi(doi)
    paper_type = idx.get("paper_type", "").lower()
    impact = idx.get("ledger_impact")

    if not bare:
        report["reason"] = "awaiting_doi (no DOI registered)"
        if paper_type in EMPIRICAL_TYPES:
            report["reason"] += " — empirical paper in maintainer mode"
        return report, tests_data, stats_data, gap_html

    if not impact:
        if paper_type in EMPIRICAL_TYPES:
            report["reason"] = "DOI registered but no ledger_impact block"
            report["status"] = "warn"
        else:
            report["reason"] = "no ledger_impact (non-empirical — optional)"
        return report, tests_data, stats_data, gap_html

    status = impact.get("status", "draft")
    if status == "draft":
        report["reason"] = "ledger_impact.status=draft (finalize before sync)"
        report["status"] = "warn"
        return report, tests_data, stats_data, gap_html

    if impact.get("applied_by_doi") == bare:
        report["reason"] = f"already applied (applied_at={impact.get('applied_at')})"
        return report, tests_data, stats_data, gap_html

    if impact.get("applied_by_doi") and impact.get("applied_by_doi") != bare:
        report["reason"] = (
            f"applied_by_doi={impact.get('applied_by_doi')!r} "
            f"!= current doi={bare!r} — manual reconciliation required"
        )
        report["status"] = "error"
        report["errors"].append(report["reason"])
        return report, tests_data, stats_data, gap_html

    if status != "ready":
        report["reason"] = f"ledger_impact.status={status!r} (expected 'ready')"
        report["status"] = "warn"
        return report, tests_data, stats_data, gap_html

    # Validate
    tests_by_id = collect_test_ids(tests_data)
    errs = validate_impact(paper_name, impact, tests_by_id, gap_ids)
    if errs:
        report["status"] = "error"
        report["errors"] = errs
        return report, tests_data, stats_data, gap_html

    # Plan
    for t in impact.get("tests_added", []):
        report["planned"].append(
            f"ADD test [{t.get('category')}] {t.get('test_id')} "
            f"result={t.get('result')}"
        )
    for t in impact.get("tests_updated", []):
        report["planned"].append(
            f"UPDATE test {t.get('test_id')} → result={t.get('new_result')} "
            f"status={t.get('new_status')}"
        )
    for gid in impact.get("gaps_closed", []):
        report["planned"].append(f"CLOSE gap {gid}")

    # page_updates (council-gated)
    page_updates = impact.get("page_updates", [])
    if page_updates:
        pu_planned, _, _ = apply_page_updates(page_updates, bare, idx, False)
        report["planned"].extend(pu_planned)

    if not report["planned"]:
        report["reason"] = "ledger_impact block is empty — nothing to do"
        return report, tests_data, stats_data, gap_html

    if not apply_mode:
        report["status"] = "would_apply"
        return report, tests_data, stats_data, gap_html

    # LIVE APPLY
    apply_tests_added(tests_data, impact.get("tests_added", []), paper_name)
    # Re-collect after additions so tests_updated sees them too
    tests_by_id = collect_test_ids(tests_data)
    apply_tests_updated(tests_by_id, impact.get("tests_updated", []),
                        paper_name)
    gap_html, gaps_actually_changed = apply_gaps_closed(
        gap_html, set(impact.get("gaps_closed", [])), bare
    )
    if set(gaps_actually_changed) != set(impact.get("gaps_closed", [])):
        missed = set(impact.get("gaps_closed", [])) - set(gaps_actually_changed)
        if missed:
            report["errors"].append(
                f"gaps_closed: could not mark {sorted(missed)} (already closed?)"
            )

    # page_updates (council-gated)
    page_updates = impact.get("page_updates", [])
    if page_updates:
        pu_planned, pu_errors, pu_changed = apply_page_updates(
            page_updates, bare, idx, True
        )
        report["errors"].extend(pu_errors)
        if pu_changed:
            report["planned"].extend(
                [f"COUNCIL APPROVED: {p}" for p in pu_changed.keys()])

    # Stamp idempotence markers in the paper's index.json
    impact["applied_at"] = now_iso()
    impact["applied_by_doi"] = bare
    impact["status"] = "applied"
    write_json(idx_path, idx)

    report["status"] = "applied"
    return report, tests_data, stats_data, gap_html


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Actually write files (default: dry-run)")
    parser.add_argument("--paper",
                        help="Limit processing to one paper directory name")
    args = parser.parse_args()

    mode = "LIVE" if args.apply else "DRY-RUN"
    print("=" * 70)
    print(f"EFC LEDGER IMPACT SYNC — {mode}")
    print("=" * 70)

    if not os.path.isfile(TESTS):
        print(f"[error] tests.json not found at {TESTS}")
        return 2
    if not os.path.isfile(STATS):
        print(f"[error] stats.json not found at {STATS}")
        return 2
    if not os.path.isfile(GAP_HTML):
        print(f"[error] Gap_Analysis.html not found at {GAP_HTML}")
        return 2

    tests_data = load_json(TESTS)
    stats_data = load_json(STATS)
    gap_html = read_text(GAP_HTML)
    gap_ids = collect_gap_ids(gap_html)
    print(f"Known gap IDs in HTML: {len(gap_ids)}")

    reports = []
    any_error = False
    any_change = False

    for name, idx_path, idx in iter_papers():
        if args.paper and name != args.paper:
            continue
        rep, tests_data, stats_data, gap_html = process_paper(
            name, idx_path, idx, tests_data, stats_data,
            gap_html, gap_ids, apply_mode=args.apply,
        )
        reports.append(rep)
        if rep["status"] == "error":
            any_error = True
        if rep["status"] in ("applied", "would_apply"):
            any_change = True

    # Summarise
    buckets = {}
    for r in reports:
        buckets.setdefault(r["status"], []).append(r)
    print(f"\nProcessed {len(reports)} paper(s)")
    for status, items in sorted(buckets.items()):
        print(f"  {status}: {len(items)}")
        if status in ("applied", "would_apply", "warn", "error"):
            for r in items:
                print(f"    - {r['paper']}: {r['reason'] or ''}")
                for line in r.get("planned", []):
                    print(f"        · {line}")
                for e in r.get("errors", []):
                    print(f"        ! {e}")

    if any_error:
        print("\n[ledger-impact-sync] ERRORS — no writes performed")
        return 2

    if any_change and args.apply:
        # Recount stats, persist
        stat_changes = recount_stats(tests_data, stats_data)
        write_json(TESTS, tests_data)
        write_json(STATS, stats_data)
        write_text(GAP_HTML, gap_html)
        print("\n[ledger-impact-sync] wrote:")
        print(f"  - {os.path.relpath(TESTS, REPO)}")
        print(f"  - {os.path.relpath(STATS, REPO)}")
        print(f"  - {os.path.relpath(GAP_HTML, REPO)}")
        if stat_changes:
            print("  stats.json recount:")
            for c in stat_changes:
                print(f"    {c}")
        return 1

    if any_change and not args.apply:
        print("\n[ledger-impact-sync] DRY-RUN — re-run with --apply to write")
        return 1

    print("\n[ledger-impact-sync] nothing to do — all papers in steady state")
    return 0


if __name__ == "__main__":
    sys.exit(main())
