"""Tests for scripts/maintenance/efc_doi_impact_manifest.py — the no-orphan invariant.

Hermetic: exercises only the pure functions (`_detect_orphans`, `build_manifest`)
with injected dicts, never a live repo scan.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "maintenance" / "efc_doi_impact_manifest.py"


def _load():
    spec = importlib.util.spec_from_file_location("efc_doi_impact_manifest", SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _known(*dois: str) -> dict:
    return {d: {"title": f"t-{d}", "paper_type": "theory", "repo_dir": f"docs/papers/efc/{d}"}
            for d in dois}


def test_orphan_when_only_in_catalog():
    mod = _load()
    known = _known("10.6084/m9.figshare.111")
    refs = {"10.6084/m9.figshare.111": {"figshare/doi-map.json"}}
    assert mod._detect_orphans(known, refs) == ["10.6084/m9.figshare.111"]


def test_orphan_when_no_reference_at_all():
    mod = _load()
    known = _known("10.6084/m9.figshare.111")
    refs = {}
    assert mod._detect_orphans(known, refs) == ["10.6084/m9.figshare.111"]


def test_not_orphan_when_propagated():
    mod = _load()
    known = _known("10.6084/m9.figshare.111")
    refs = {"10.6084/m9.figshare.111": {
        "figshare/doi-map.json", "docs/papers/efc/111/index.json"}}
    assert mod._detect_orphans(known, refs) == []


def test_build_manifest_counts_beyond_catalog():
    mod = _load()
    known = _known("10.6084/m9.figshare.111", "10.6084/m9.figshare.222")
    refs = {
        "10.6084/m9.figshare.111": {"figshare/doi-map.json", "docs/papers/efc/111/index.json"},
        "10.6084/m9.figshare.222": {"figshare/doi-map.json"},  # orphan
    }
    manifest, orphans = mod.build_manifest(known=known, refs=refs)
    assert orphans == ["10.6084/m9.figshare.222"]
    assert manifest["totals"]["known_dois"] == 2
    assert manifest["totals"]["orphan_dois"] == 1
    assert manifest["dois"]["10.6084/m9.figshare.111"]["referenced_beyond_catalog"] == 1
    assert manifest["dois"]["10.6084/m9.figshare.222"]["referenced_beyond_catalog"] == 0
