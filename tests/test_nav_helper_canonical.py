"""Locks the navbar contract on the write paths of the public pages (t_41d80135).

The navbar has one owner: ``efc_navbar_sync.py``. It renders the canonical
block for the CURRENT page — with the red "you are here" marker
(``color:#c22``). ``_nav_helper.ensure_nav()`` previously carried its own copy of
the navbar WITHOUT the marker, so any writer that called it turned a canonical
page into ``navbar_drift``: measured 2026-09-17, ``EFC_Changelog.html`` came out of the
write path without ``color:#c22;`` and ``efc_navbar_sync.py --check`` answered rc=2.
The drift was invisible to the page-content checks because they do not see the navbar.

What is locked here:
  1. ``ensure_nav`` without the page's name does not touch the navbar at all.
  2. ``ensure_nav`` with the page's name restores exactly the canonical
     block for that page, and is idempotent.
  3. A write from each of the two writers (``efc_ai_brain.write_page`` and
     ``efc_ledger_autofill.skriv_side``) to a drifted page leaves the
     REAL gate green: ``efc_navbar_sync.main(["--check"]) == 0``.
  4. ``efc_ledger_autofill.main`` writes both pages through ``skriv_side``,
     so the path via the canonical name cannot be bypassed.

The writes go to a sandbox copy of ``docs/public``; neither the repo nor
the real pages are touched.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAINT = ROOT / "scripts" / "maintenance"
PUBLIC = ROOT / "docs" / "public"
sys.path.insert(0, str(MAINT))

import _nav_helper  # noqa: E402
import efc_ai_brain as brain  # noqa: E402
import efc_ledger_autofill as autofill  # noqa: E402
import efc_navbar_sync as sync  # noqa: E402

SIDEN = "EFC_Changelog.html"


def _legacy_nav() -> str:
    """The navbar as the old `_nav_helper` copy wrote it (without the marker)."""
    linjer = [sync.NAV_OPEN]
    for i, (href, label) in enumerate(sync.NAV_ENTRIES):
        style = ("font-weight:600;" if i == len(sync.NAV_ENTRIES) - 1
                 else "margin-right:1.5rem; font-weight:600;")
        linjer.append(f'  <a href="{href}" style="{style}">{label}</a>')
    linjer.append("</div>")
    return "\n".join(linjer)


def _driftet(tekst: str, side: str) -> str:
    """Replace the canonical navbar with the old, marker-less variant."""
    kanonisk = sync.render_nav(side)
    assert kanonisk in tekst, f"{side}: found no canonical navbar to drift from"
    return tekst.replace(kanonisk, _legacy_nav(), 1)


def _sandkasse(tmp_path: Path) -> Path:
    """Copy of docs/public with all the pages the gate checks."""
    pub = tmp_path / "docs" / "public"
    pub.mkdir(parents=True, exist_ok=True)
    for side in sync.ALL_PAGES:
        (pub / side).write_text((PUBLIC / side).read_text(encoding="utf-8"),
                                encoding="utf-8")
    return pub


def test_ensure_nav_uten_side_rorer_ikke_navbaren():
    """Without the page's name a writer cannot know which marker applies."""
    tekst = (PUBLIC / SIDEN).read_text(encoding="utf-8")
    rendered = _nav_helper.ensure_nav(tekst)
    assert rendered == tekst
    assert sync.render_nav(SIDEN) in rendered


def test_ensure_nav_med_side_reparerer_drift_og_er_idempotent():
    tekst = (PUBLIC / SIDEN).read_text(encoding="utf-8")
    driftet = _driftet(tekst, SIDEN)
    assert sync.render_nav(SIDEN) not in driftet, "the fixture is not real drift"

    reparert = _nav_helper.ensure_nav(driftet, SIDEN)
    assert sync.render_nav(SIDEN) in reparert
    assert "color:#c22;" in reparert, "the marker for the current page is missing"
    assert reparert == tekst, "the repair did not give the canonical page back"
    assert _nav_helper.ensure_nav(reparert, SIDEN) == reparert

    # A full path is also a valid page reference.
    assert _nav_helper.ensure_nav(driftet, str(PUBLIC / SIDEN)) == tekst


def test_nav_helper_har_ingen_egen_navbar():
    """The root cause: the module shall no longer carry its own navbar copy."""
    kilde = (MAINT / "_nav_helper.py").read_text(encoding="utf-8")
    assert "CANONICAL_NAV_HTML" not in kilde
    assert 'href="EFC_Elevator_Pitch.html"' not in kilde


def test_ai_brain_skriving_holder_navbaren_kanonisk(tmp_path, monkeypatch):
    pub = _sandkasse(tmp_path)
    sti = pub / SIDEN
    sti.write_text(_driftet(sti.read_text(encoding="utf-8"), SIDEN), encoding="utf-8")

    monkeypatch.setattr(sync, "PUBLIC_ROOT", pub)
    monkeypatch.setattr(brain, "PUBLIC_PAGES", {"changelog": str(sti)})

    assert sync.main(["--check"]) == 2, "the gate shall stand red on the fixture before writing"

    brain.write_page("changelog", brain.read_page("changelog") + "\n<li>nytt</li>\n")

    assert "<li>nytt</li>" in sti.read_text(encoding="utf-8")
    assert sync.main(["--check"]) == 0
    assert "color:#c22;" in sti.read_text(encoding="utf-8")


def test_ledger_autofill_skriving_holder_navbaren_kanonisk(tmp_path, monkeypatch):
    pub = _sandkasse(tmp_path)
    sider = ("EFC_Validation_Ledger.html", "EFC_Changelog.html")
    for side in sider:
        sti = pub / side
        sti.write_text(_driftet(sti.read_text(encoding="utf-8"), side), encoding="utf-8")

    monkeypatch.setattr(sync, "PUBLIC_ROOT", pub)
    monkeypatch.setattr(autofill, "LEDGER", str(pub / sider[0]))
    monkeypatch.setattr(autofill, "CHANGELOG", str(pub / sider[1]))

    assert sync.main(["--check"]) == 2, "the gate shall stand red on the fixture before writing"

    for sti in (autofill.LEDGER, autofill.CHANGELOG):
        tekst = Path(sti).read_text(encoding="utf-8")
        autofill.skriv_side(sti, tekst + "\n<li>autofyll</li>\n")
        assert "<li>autofyll</li>" in Path(sti).read_text(encoding="utf-8")

    assert sync.main(["--check"]) == 0
    for side in sider:
        assert "color:#c22;" in (pub / side).read_text(encoding="utf-8")


def test_autofill_main_skriver_begge_sidene_gjennom_skriv_side():
    """main() shall not have its own write path past the canonical name."""
    tre = ast.parse((MAINT / "efc_ledger_autofill.py").read_text(encoding="utf-8"))
    main = next(n for n in ast.walk(tre)
                if isinstance(n, ast.FunctionDef) and n.name == "main")
    kall = [n for n in ast.walk(main) if isinstance(n, ast.Call)]

    skrevne = {k.args[0].id for k in kall
               if isinstance(k.func, ast.Name) and k.func.id == "skriv_side"
               and k.args and isinstance(k.args[0], ast.Name)}
    assert skrevne == {"LEDGER", "CHANGELOG"}

    egne_skrivinger = [
        k for k in kall
        if isinstance(k.func, ast.Name) and k.func.id == "open"
        and len(k.args) > 1
        and isinstance(k.args[1], ast.Constant) and k.args[1].value == "w"
    ]
    assert egne_skrivinger == [], "main() writes a public page outside skriv_side()"
