"""
Canonical navigation block for all EFC public HTML ledgers.

The navbar has exactly ONE owner: ``efc_navbar_sync.py`` — run as step 5b in
``efc_maintain.py`` and enforced by ``.github/workflows/efc-page-consistency.yml``
(``efc_navbar_sync.py --check``). It renders the block with
``render_nav(active_href=page)``, including the red «du er her» marker
(``color:#c22;``) on the page being rendered.

A renderer that owns part of a public page calls::

    from _nav_helper import ensure_nav
    text = ensure_nav(text, "EFC_Changelog.html")   # or a full path

before writing. It normalizes the existing navbar to exactly the canonical
block *for that page* — marker included — so a writer can never leave a page
drifted. Idempotent and safe to run on every write.

Why the page name is required
-----------------------------
This module used to carry its own copy of the navbar, without the active-page
marker, and ``ensure_nav(html)`` rewrote any page to that copy. Every such
write turned a canonical page into ``navbar_drift``: measured 2026-09-17 on
``docs/public/EFC_Changelog.html``, the canonical block came out without
``color:#c22;`` and ``efc_navbar_sync.py --check`` answered rc=2. The copy is
gone; there is one renderer, and it is asked for the right page.

Contract
--------
- ``ensure_nav(html, page)`` replaces the existing navbar block with
  ``efc_navbar_sync.render_nav(page)``. ``page`` is the page's file name
  (``EFC_Changelog.html``); a full path is reduced to its file name.
- Without a ``page`` the navbar is left COMPLETELY untouched: a renderer that
  does not know which page it is writing must not strip the marker of the page
  that does. Legacy call sites therefore become harmless instead of destructive.
- A page with no navbar block at all is returned unchanged. Inserting a navbar
  is ``efc_navbar_sync.py``'s job, not a writer's.
- If the canonical renderer cannot be imported, the html is returned unchanged
  — never a home-made navbar.
"""
from __future__ import annotations

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

try:  # the one renderer
    from efc_navbar_sync import find_existing_nav, render_nav
except Exception:  # pragma: no cover — never let a nav import block a write
    find_existing_nav = None  # type: ignore[assignment]
    render_nav = None  # type: ignore[assignment]


def page_name(path_or_name: str) -> str:
    """Normalize a page reference to its file name (``EFC_Changelog.html``)."""
    return os.path.basename(str(path_or_name or "").strip())


def ensure_nav(html: str, page: str | None = None) -> str:
    """
    Return ``html`` with its navbar block normalized to the canonical block for
    ``page`` (red «du er her» marker on that page).

    Does nothing when ``page`` is missing/empty, when no navbar block is found,
    or when the canonical renderer is unavailable — in every one of those cases
    the html is returned exactly as it came in.
    """
    if not html:
        return html
    name = page_name(page) if page else ""
    if not name or find_existing_nav is None or render_nav is None:
        return html
    bounds = find_existing_nav(html)
    if bounds is None:
        return html
    start, end = bounds
    canonical = render_nav(active_href=name)
    if html[start:end] == canonical:
        return html
    return html[:start] + canonical + html[end:]


def has_external_research_link(html: str) -> bool:
    """Quick sanity check used by CI/audit scripts."""
    return "EFC_External_Research_Ledger.html" in (html or "")
