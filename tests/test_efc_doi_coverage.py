"""Tests for scripts/maintenance/efc_doi_coverage.py — the planned-row exclusion.

Regression test for the normalization drift: the exclusion set and the scan
loop must use the SAME DOI normalization, otherwise a Planned-row DOI ending
in punctuation (e.g. ``10.17863/CAM.690.``) slips through as a false
"unrecognized" positive.

The test is hermetic: it exercises ``scan(directory=...)`` and ``_norm`` on a
temp directory, never the live ``docs/public/`` surface and never ORCID.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_doi_coverage.py"


def _load():
    spec = importlib.util.spec_from_file_location("efc_doi_coverage", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# The DOI in a planned row, followed by punctuation then prose — the exact
# shape that used to escape the exclusion set.
PLANNED_ROW_TEMPLATE = (
    '<tr data-category="physics_test" data-result="Planned">'
    "<td>{doi}{punct} N=20 subjects, 91-channel EEG</td></tr>"
)


def _build_html(planned_rows: list[str], extra_doi: str | None = None) -> str:
    """A minimal page: one or more planned rows, optionally one free DOI."""
    parts = ["<html><body><table>"]
    parts.extend(planned_rows)
    if extra_doi:
        parts.append(f"<p>freestanding citation {extra_doi}</p>")
    parts.append("</table></body></html>")
    return "\n".join(parts)


def test_norm_strips_punctuation():
    mod = _load()
    assert mod._norm("10.17863/CAM.690.") == "10.17863/cam.690"
    assert mod._norm("10.6084/m9.figshare.31876324,") == "10.6084/m9.figshare.31876324"
    assert mod._norm("10.6084/m9.figshare.31876324;") == "10.6084/m9.figshare.31876324"
    assert mod._norm("10.6084/m9.figshare.31876324)") == "10.6084/m9.figshare.31876324"


def test_planned_row_doi_never_flagged(tmp_path: Path):
    """A Planned-row DOI ending in any punctuation is excluded, not flagged."""
    mod = _load()
    doi = "10.17863/CAM.690"
    rows = [PLANNED_ROW_TEMPLATE.format(doi=doi, punct=p)
            for p in (".", ",", ";", ")", "]")]
    html = _build_html(rows)
    page = tmp_path / "page.html"
    page.write_text(html, encoding="utf-8")

    found = mod.scan(directory=tmp_path)
    assert doi.lower() not in found, f"planned-row DOI leaked into scan: {found}"
    assert found == {}, f"expected no freestanding DOIs, got {found}"


def test_freestanding_doi_still_flagged(tmp_path: Path):
    """The exclusion must NOT swallow a DOI outside a Planned row."""
    mod = _load()
    planned = PLANNED_ROW_TEMPLATE.format(doi="10.17863/CAM.690", punct=".")
    free = "10.6084/m9.figshare.31876324"
    html = _build_html([planned], extra_doi=free)
    page = tmp_path / "page.html"
    page.write_text(html, encoding="utf-8")

    found = mod.scan(directory=tmp_path)
    assert free in found, f"freestanding DOI not flagged: {found}"
    assert "10.17863/cam.690" not in found
