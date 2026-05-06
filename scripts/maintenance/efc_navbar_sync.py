#!/usr/bin/env python3
"""Apply canonical 12-entry navbar to every public EFC page.

Single source of truth for the cross-page navigation. All 13 pages
under ``docs/public/EFC_*.html`` get the same navbar in the same order.
The link to the *current* page is rendered in red (``color:#c22;``) so
readers always know where they are.

Idempotent: re-running with the same canonical NAV produces no diff.

Usage
-----
    python3 scripts/maintenance/efc_navbar_sync.py            # apply
    python3 scripts/maintenance/efc_navbar_sync.py --check    # verify only
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROOT = REPO_ROOT / "docs" / "public"

# Canonical 12-entry navbar — order and labels as Morten specified.
# Master v1.1 is *not* in the navbar (it is the standalone master spec
# snapshot), but it still receives the navbar so a reader can navigate
# from it back to the rest.
NAV_ENTRIES = (
    ("EFC_Elevator_Pitch.html", "Pitch"),
    ("EFC_Validation_Ledger.html", "Validation"),
    ("EFC_Likelihood_Ledger.html", "Likelihood"),
    ("EFC_Evaluation_Ledger.html", "Evaluation"),
    ("EFC_Model_Comparison.html", "Models"),
    ("EFC_White_Paper_Series.html", "White Paper"),
    ("EFC_Stage-IV_Data_Roadmap.html", "Roadmap"),
    ("EFC_Gap_Analysis.html", "Gaps"),
    ("EFC_External_Research_Ledger.html", "External"),
    ("EFC_Predictions.html", "Predictions"),
    ("EFC_Atlas.html", "Atlas"),
    ("EFC_Changelog.html", "Changelog"),
)

# Pages that should get the navbar (all 13 — including Master v1.1).
ALL_PAGES = list(href for href, _ in NAV_ENTRIES) + ["EFC_Master_v1.1.html"]

NAV_OPEN = (
    '<div style="background:#f8f9fa; border:1px solid #d0d7e3; '
    'border-radius:6px; padding:12px 18px; margin-bottom:1.5rem; '
    'font-size:0.92rem;">'
)
NAV_CLOSE = "</div>"

# Marker comments delimit the canonical block; lets the regex be tight
# and lets future renderers find the navbar unambiguously.
NAV_MARK_BEGIN = "<!-- efc-navbar:begin -->"
NAV_MARK_END = "<!-- efc-navbar:end -->"


def render_nav(active_href: str) -> str:
    """Return the canonical navbar HTML, with the active page in red."""
    lines = [NAV_MARK_BEGIN, NAV_OPEN]
    for i, (href, label) in enumerate(NAV_ENTRIES):
        is_last = i == len(NAV_ENTRIES) - 1
        is_active = href == active_href
        style_parts = ["font-weight:600;"]
        if not is_last:
            style_parts.insert(0, "margin-right:1.5rem;")
        if is_active:
            style_parts.append("color:#c22;")
        style = " ".join(style_parts)
        lines.append(f'  <a href="{href}" style="{style}">{label}</a>')
    lines.append(NAV_CLOSE)
    lines.append(NAV_MARK_END)
    return "\n".join(lines)


# Match an existing navbar block. Two cases:
#   1. Wrapped in efc-navbar markers (idempotent path)
#   2. The legacy <div ...> ... <a href="EFC_Elevator_Pitch.html">...</a>
#      ... </div> block (first migration)
_MARKER_RE = re.compile(
    re.escape(NAV_MARK_BEGIN) + r".*?" + re.escape(NAV_MARK_END),
    re.DOTALL,
)
_LEGACY_RE = re.compile(
    r'<div[^>]*?background:#f8f9fa[^>]*?>\s*'
    r'(?:<a\s+href="EFC_[^"]+\.html"[^>]*?>[^<]+</a>\s*)+\s*</div>',
    re.DOTALL,
)


def find_existing_nav(text: str) -> tuple[int, int] | None:
    """Return (start, end) of an existing navbar block, or None."""
    m = _MARKER_RE.search(text)
    if m:
        return m.start(), m.end()
    m = _LEGACY_RE.search(text)
    if m:
        return m.start(), m.end()
    return None


def insert_after_h1(text: str, replacement: str) -> str:
    """Master v1.1 has no existing navbar — insert one after the first <h1>."""
    h1_match = re.search(r"</h1>", text)
    if not h1_match:
        # Fallback: insert after <body>.
        body_match = re.search(r"<body[^>]*>", text)
        if not body_match:
            return text
        i = body_match.end()
        return text[:i] + "\n\n" + replacement + "\n" + text[i:]
    i = h1_match.end()
    return text[:i] + "\n\n" + replacement + "\n" + text[i:]


def apply_to_page(page: str, write: bool) -> dict:
    path = PUBLIC_ROOT / page
    if not path.exists():
        return {"page": page, "status": "missing"}
    text = path.read_text(encoding="utf-8")
    canonical = render_nav(active_href=page)
    bounds = find_existing_nav(text)
    if bounds is None:
        # Fresh insert (Master v1.1 case).
        new_text = insert_after_h1(text, canonical)
        action = "inserted"
    else:
        start, end = bounds
        new_text = text[:start] + canonical + text[end:]
        action = "replaced"
    if new_text == text:
        return {"page": page, "status": "unchanged"}
    if write:
        path.write_text(new_text, encoding="utf-8")
    return {"page": page, "status": action}


def cmd_check() -> int:
    """Verify every page has the canonical nav. Exit 2 if drift detected."""
    drifts: list[dict] = []
    for page in ALL_PAGES:
        path = PUBLIC_ROOT / page
        if not path.exists():
            drifts.append({"page": page, "issue": "missing"})
            continue
        text = path.read_text(encoding="utf-8")
        expected = render_nav(active_href=page)
        if expected not in text:
            drifts.append({"page": page, "issue": "navbar_drift"})
    if drifts:
        print(f"[navbar-sync] {len(drifts)} page(s) drifted:")
        for d in drifts:
            print(f"  {d['page']}: {d['issue']}")
        print(
            "\nFix: python3 scripts/maintenance/efc_navbar_sync.py"
        )
        return 2
    print(f"[navbar-sync] all {len(ALL_PAGES)} pages have canonical navbar ✓")
    return 0


def cmd_apply() -> int:
    results = [apply_to_page(p, write=True) for p in ALL_PAGES]
    counts: dict[str, int] = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    print(f"[navbar-sync] processed {len(results)} page(s):")
    for k in sorted(counts):
        print(f"  {k}: {counts[k]}")
    for r in results:
        if r["status"] not in {"unchanged"}:
            print(f"  · {r['page']}: {r['status']}")
    return 0


def main(argv: Iterable[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EFC public-page navbar sync")
    p.add_argument(
        "--check", action="store_true", help="verify only; exit 2 on drift"
    )
    args = p.parse_args(list(argv) if argv is not None else None)
    if args.check:
        return cmd_check()
    return cmd_apply()


if __name__ == "__main__":
    sys.exit(main())
