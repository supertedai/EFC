"""Regression tests for the link rule on the Markdown surface (wiki/**).

WHY THIS EXISTS
---------------
Measured 2026-11-12 (card t_56beaebd): ``validate_links.py`` scanned
``docs/public/*.html`` and ``docs/index.html`` only, so the wiki — 21 relative
links, 12 of them dead — was measured by nothing. The fix extends the scanner
to ``wiki/**/*.md`` and makes an internal dead link a HARD error there too.

The contract these tests pin, one rule per test:
  * a relative link that resolves to a file exists;
  * a relative link that resolves to a DIRECTORY exists (wiki pages link to
    directories on purpose — ``../theory/formal/``);
  * a relative link to nothing is hard, on both surfaces;
  * fragment-only, ``mailto:``, ``tel:`` and absolute URLs are not path links;
  * a query string or fragment does not break an otherwise good link;
  * reference-style definitions are read, not silently skipped;
  * HTML keeps the stricter rule: a directory is NOT a target for a page.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))


def _tre(tmp_path: Path) -> Path:
    """A small tree where one target exists as a file and one as a directory."""
    (tmp_path / "wiki").mkdir()
    (tmp_path / "wiki" / "Existing.md").write_text("# exists\n", encoding="utf-8")
    (tmp_path / "theory" / "formal").mkdir(parents=True)
    return tmp_path


def test_relative_links_to_file_and_directory_are_not_hard(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = ("- [page](Existing.md)\n"
             "- [dir](../theory/formal/)\n"
             "- [dir without slash](../theory/formal)\n")
    harde, eksterne = sjekk_side(side, tekst, markdown=True)
    assert harde == [], f"live targets must not be hard: {harde}"
    assert eksterne == []


def test_dead_relative_link_is_hard(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = "- [missing](Not-Written-Yet.md)\n"
    harde, _ = sjekk_side(side, tekst, markdown=True)
    assert len(harde) == 1
    assert harde[0]["type"] == "broken_internal"
    assert harde[0]["href"] == "Not-Written-Yet.md"
    assert harde[0]["side"].endswith("wiki/Home.md")


def test_non_path_links_are_skipped_and_external_is_a_finding(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = ("- [section](#start-here)\n"
             "- [mail](mailto:someone@example.org)\n"
             "- [phone](tel:+4700000000)\n"
             "- [external](https://example.org/nope)\n")
    harde, eksterne = sjekk_side(side, tekst, markdown=True)
    assert harde == [], f"non-path links must not be hard: {harde}"
    assert eksterne == ["https://example.org/nope"]


def test_query_string_and_fragment_do_not_break_a_good_link(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = "- [page](Existing.md#a-heading)\n- [page again](Existing.md?plain=1)\n"
    harde, _ = sjekk_side(side, tekst, markdown=True)
    assert harde == [], f"fragment/query must be stripped before the check: {harde}"


def test_reference_style_definition_is_measured(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = ("Read the [glossary][gl].\n\n"
             "[gl]: Glossary.md\n")
    harde, _ = sjekk_side(side, tekst, markdown=True)
    assert [h["href"] for h in harde] == ["Glossary.md"]


def test_links_shown_as_code_are_not_links(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    side = rot / "wiki" / "Home.md"
    tekst = ("Document the syntax like this:\n\n"
             "```markdown\n"
             "- [a page](Not-Written-Yet.md)\n"
             "```\n\n"
             "and inline as `[x](Also-Missing.md)` — neither is a link.\n")
    harde, _ = sjekk_side(side, tekst, markdown=True)
    assert harde == [], f"code is not a link: {harde}"


def test_html_keeps_the_stricter_rule_for_directories(tmp_path):
    from validate_links import sjekk_side
    rot = _tre(tmp_path)
    (rot / "theory" / "formal" / "index.html").write_text("<p>ok</p>", encoding="utf-8")
    side = rot / "docs" / "public" / "Page.html"
    side.parent.mkdir(parents=True)
    tekst = ('<a href="../../theory/formal/">dir</a>'
             '<a href="../../theory/formal/index.html">page</a>')
    harde, _ = sjekk_side(side, tekst, markdown=False)
    assert [h["href"] for h in harde] == ["../../theory/formal/"]
