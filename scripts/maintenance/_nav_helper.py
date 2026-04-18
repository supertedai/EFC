"""
Canonical navigation block for all EFC public HTML ledgers.

Any renderer that writes to docs/public/EFC_*.html SHOULD call
ensure_nav(content) before writing, so the nav block is normalized
to the current canonical form. Idempotent and safe to run every write.

This guarantees:
  - Short labels (Pitch, Ledger, White Paper, Roadmap, Gaps, ...)
  - External Research link present
  - Consistent ordering across all ledgers
"""
from __future__ import annotations
import re


CANONICAL_NAV_HTML = (
    '<div style="background:#f8f9fa; border:1px solid #d0d7e3; '
    'border-radius:6px; padding:12px 18px; margin-bottom:1.5rem; '
    'font-size:0.92rem;">\n'
    '  <a href="EFC_Elevator_Pitch.html" style="margin-right:1.5rem; font-weight:600;">Pitch</a>\n'
    '  <a href="EFC_Validation_Ledger.html" style="margin-right:1.5rem; font-weight:600;">Ledger</a>\n'
    '  <a href="EFC_White_Paper_Series.html" style="margin-right:1.5rem; font-weight:600;">White Paper</a>\n'
    '  <a href="EFC_Stage-IV_Data_Roadmap.html" style="margin-right:1.5rem; font-weight:600;">Roadmap</a>\n'
    '  <a href="EFC_Gap_Analysis.html" style="margin-right:1.5rem; font-weight:600;">Gaps</a>\n'
    '  <a href="EFC_External_Research_Ledger.html" style="margin-right:1.5rem; font-weight:600;">External Research</a>\n'
    '  <a href="EFC_Predictions.html" style="margin-right:1.5rem; font-weight:600;">Predictions</a>\n'
    '  <a href="EFC_Changelog.html" style="font-weight:600;">Changelog</a>\n'
    '</div>'
)

# Pattern that matches ANY existing nav block anchored on Elevator Pitch link.
# Handles both old long-label format and any other variant, as long as it
# contains the Elevator Pitch anchor and ends with a </div>.
_NAV_REGEX = re.compile(
    r'<div[^>]*>\s*'
    r'(?:<a[^>]*href="EFC_Elevator_Pitch\.html"[^>]*>[^<]*</a>\s*)'
    r'(?:<a[^>]*>[^<]*</a>\s*)+'
    r'</div>',
    re.DOTALL,
)


def ensure_nav(html: str) -> str:
    """
    Replace any existing EFC nav block with the canonical one. If no nav
    block is found, return the HTML unchanged (do NOT inject one — the
    original page author owns the decision about where the nav lives).

    Idempotent: running this multiple times yields the same result.
    """
    if not html:
        return html
    # Only replace if a nav block exists AND differs from canonical
    if _NAV_REGEX.search(html):
        new_html, _ = _NAV_REGEX.subn(CANONICAL_NAV_HTML, html, count=1)
        return new_html
    return html


def has_external_research_link(html: str) -> bool:
    """Quick sanity check used by CI/audit scripts."""
    return "EFC_External_Research_Ledger.html" in (html or "")
