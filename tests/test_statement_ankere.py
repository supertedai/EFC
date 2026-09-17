"""Regression tests for the statement graph's anchor machinery (the stale_page class).

The contract: an appears_on coupling that declares an `anchor` MUST be visible in
the page text, a page must not carry an anchor the graph does not attribute to it,
and a primary page must not be unverifiable.

The tests cover BOTH directions:
  * the machinery catches breaches (mutated fixtures — a check that cannot fail
    is worthless);
  * the real graph and the real pages are consistent today.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


def _module():
    path = ROOT / "scripts" / "maintenance" / "statement_graph_check.py"
    spec = importlib.util.spec_from_file_location("statement_graph_check", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fixture(tmp_path: Path, statements: list[dict], pages: dict[str, str]):
    """A minimal tree: public/graph/statements.yaml + page-meta + docs/public/*.html."""
    (tmp_path / "public" / "graph").mkdir(parents=True)
    (tmp_path / "public" / "page-meta").mkdir(parents=True)
    (tmp_path / "docs" / "public").mkdir(parents=True)
    (tmp_path / "public" / "graph" / "statements.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "statements": statements},
                       sort_keys=False, allow_unicode=True), encoding="utf-8")
    (tmp_path / "public" / "graph" / "evidence.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "evidence": []}), encoding="utf-8")
    for pid, html in pages.items():
        (tmp_path / "public" / "page-meta" / f"{pid}.yaml").write_text(
            yaml.safe_dump({"page_id": pid, "path": f"/{pid}.html"}), encoding="utf-8")
        (tmp_path / "docs" / "public" / f"{pid}.html").write_text(html, encoding="utf-8")


def _st(**kw) -> dict:
    base = {
        "statement_id": "efc.x1.001", "text": "a statement", "kind": "derived_result",
        "epistemic_level": "partial_support", "owner_role": "researcher",
        "status": "active", "supported_by": ["ev.efc.x1.001"],
        "contradicts": [], "supersedes": None,
    }
    base.update(kw)
    return base


def test_an_anchor_that_holds_is_green(tmp_path):
    m = _module()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "page", "role": "primary",
                               "anchor": "efc.x1.001"}])],
             {"page": '<div data-statement-id="efc.x1.001">the statement</div>'})
    m.ROOT, m.GRAPH, m.PAGE_META = (tmp_path, tmp_path / "public" / "graph",
                                    tmp_path / "public" / "page-meta")
    f = m.scan()
    assert f["anchor_missing"] == [] and f["anchor_ghost"] == []


def test_a_declared_anchor_missing_on_the_page_is_caught(tmp_path):
    m = _module()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "page", "role": "primary",
                               "anchor": "efc.x1.001"}])],
             {"page": "<div>no anchor here</div>"})
    m.ROOT, m.GRAPH, m.PAGE_META = (tmp_path, tmp_path / "public" / "graph",
                                    tmp_path / "public" / "page-meta")
    f = m.scan()
    assert [x["anchor"] for x in f["anchor_missing"]] == ["efc.x1.001"]


def test_an_anchor_on_a_page_the_graph_does_not_attribute_is_caught(tmp_path):
    """The page carries the anchor, but appears_on does not name that page → contradiction."""
    m = _module()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "other", "role": "cited",
                               "anchor": "efc.x1.001"}])],
             {"other": '<div data-statement-id="efc.x1.001">x</div>',
              "page": '<div data-statement-id="efc.x1.001">x</div>'})
    m.ROOT, m.GRAPH, m.PAGE_META = (tmp_path, tmp_path / "public" / "graph",
                                    tmp_path / "public" / "page-meta")
    f = m.scan()
    assert [(x["page"], x["anchor"]) for x in f["anchor_ghost"]] == [("page", "efc.x1.001")]


def test_a_primary_page_without_an_anchor_is_hard(tmp_path):
    m = _module()
    _fixture(tmp_path, [_st(appears_on=[{"page_id": "page", "role": "primary"}])],
             {"page": "<div>no anchor</div>"})
    m.ROOT, m.GRAPH, m.PAGE_META = (tmp_path, tmp_path / "public" / "graph",
                                    tmp_path / "public" / "page-meta")
    f = m.scan()
    assert [x["type"] for x in f["harde"]] == ["primary_uten_anker"]
    assert f["anchor_queue"], "a primary page without an anchor must also land in the queue"


def test_the_real_graph_and_pages_are_consistent():
    """Locks the current state: remove an anchor from a page and CI fails here."""
    m = _module()
    f = m.scan()
    assert f["harde"] == [], f"hard errors in the statement graph: {f['harde']}"
    assert f["anchor_missing"] == [], f"declared anchors that do not exist: {f['anchor_missing']}"
    assert f["anchor_ghost"] == [], f"anchors without a graph coupling: {f['anchor_ghost']}"

    st = {s["statement_id"]: s for s in yaml.safe_load(
        (ROOT / "public" / "graph" / "statements.yaml").read_text(encoding="utf-8"))["statements"]}
    # The DESI DR2 collapse and the Variant H negative must be anchored, not just mapped.
    for sid in ("efc.h1.002", "efc.h1.003", "efc.h4.001", "efc.core.status.001"):
        anchors = [a for a in st[sid]["appears_on"] if a.get("anchor")]
        assert anchors, f"{sid} lacks an anchored coupling to a public page"
    assert st["efc.sparc.001"]["appears_on"] == [], (
        "sparc.001 was returned to page-less on 2026-09-17 — the value exists on "
        "neither atlas, likelihood-ledger nor validation-ledger")
