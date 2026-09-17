"""Regresjonstester for statement-grafens anker-mekanikk (stale_page-klassen).

Kontrakten: en appears_on-kobling som erklærer et `anchor` MÅ kunne vises i
sideteksten, en side må ikke bære et anker grafen ikke tilskriver den, og en
primærside må ikke være uverifiserbar.

Testene dekker BEGGE retninger:
  * mekanismen fanger brudd (muterte fixturer — en sjekk som ikke kan feile
    er verdiløs);
  * den virkelige grafen og de virkelige sidene er i dag konsistente.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest
import yaml

ROT = Path(__file__).resolve().parents[1]


def _modul():
    sti = ROT / "scripts" / "maintenance" / "statement_graph_check.py"
    spec = importlib.util.spec_from_file_location("statement_graph_check", sti)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _fixture(tmp_path: Path, statements: list[dict], sider: dict[str, str]):
    """Minimal tre: public/graph/statements.yaml + page-meta + docs/public/*.html."""
    (tmp_path / "public" / "graph").mkdir(parents=True)
    (tmp_path / "public" / "page-meta").mkdir(parents=True)
    (tmp_path / "docs" / "public").mkdir(parents=True)
    (tmp_path / "public" / "graph" / "statements.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "statements": statements},
                       sort_keys=False, allow_unicode=True), encoding="utf-8")
    (tmp_path / "public" / "graph" / "evidence.yaml").write_text(
        yaml.safe_dump({"schema_version": "1.0", "evidence": []}), encoding="utf-8")
    for pid, html in sider.items():
        (tmp_path / "public" / "page-meta" / f"{pid}.yaml").write_text(
            yaml.safe_dump({"page_id": pid, "path": f"/{pid}.html"}), encoding="utf-8")
        (tmp_path / "docs" / "public" / f"{pid}.html").write_text(html, encoding="utf-8")


def _st(**kw) -> dict:
    grunn = {
        "statement_id": "efc.x1.001", "text": "en påstand", "kind": "derived_result",
        "epistemic_level": "partial_support", "owner_role": "researcher",
        "status": "active", "supported_by": ["ev.efc.x1.001"],
        "contradicts": [], "supersedes": None,
    }
    grunn.update(kw)
    return grunn


def test_anker_som_holder_er_groent(tmp_path):
    m = _modul()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "side", "role": "primary",
                               "anchor": "efc.x1.001"}])],
             {"side": '<div data-statement-id="efc.x1.001">påstanden</div>'})
    m.ROT, m.GRAF, m.META = tmp_path, tmp_path / "public" / "graph", tmp_path / "public" / "page-meta"
    f = m.sjekk()
    assert f["anchor_missing"] == [] and f["anchor_ghost"] == []


def test_erklaert_anker_som_mangler_paa_siden_fanges(tmp_path):
    m = _modul()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "side", "role": "primary",
                               "anchor": "efc.x1.001"}])],
             {"side": "<div>ingen anker her</div>"})
    m.ROT, m.GRAF, m.META = tmp_path, tmp_path / "public" / "graph", tmp_path / "public" / "page-meta"
    f = m.sjekk()
    assert [x["anchor"] for x in f["anchor_missing"]] == ["efc.x1.001"]


def test_anker_paa_side_grafen_ikke_tilskriver_fanges(tmp_path):
    """Siden bærer et anker, men appears_on nevner ikke den siden → selvmotsigelse."""
    m = _modul()
    _fixture(tmp_path,
             [_st(appears_on=[{"page_id": "annen", "role": "cited",
                               "anchor": "efc.x1.001"}])],
             {"annen": '<div data-statement-id="efc.x1.001">x</div>',
              "side": '<div data-statement-id="efc.x1.001">x</div>'})
    m.ROT, m.GRAF, m.META = tmp_path, tmp_path / "public" / "graph", tmp_path / "public" / "page-meta"
    f = m.sjekk()
    assert [(x["page"], x["anchor"]) for x in f["anchor_ghost"]] == [("side", "efc.x1.001")]


def test_primærside_uten_anker_er_hardt(tmp_path):
    m = _modul()
    _fixture(tmp_path, [_st(appears_on=[{"page_id": "side", "role": "primary"}])],
             {"side": "<div>uten anker</div>"})
    m.ROT, m.GRAF, m.META = tmp_path, tmp_path / "public" / "graph", tmp_path / "public" / "page-meta"
    f = m.sjekk()
    assert [x["type"] for x in f["harde"]] == ["primary_uten_anker"]
    assert f["anchor_queue"], "primærside uten anker skal også havne i køen"


def test_virkelig_graf_og_sider_er_konsistente():
    """Låser dagens tilstand: fjernes et anker fra en side, feiler CI her."""
    m = _modul()
    f = m.sjekk()
    assert f["harde"] == [], f"harde feil i statement-grafen: {f['harde']}"
    assert f["anchor_missing"] == [], f"erkærte ankere som ikke finnes: {f['anchor_missing']}"
    assert f["anchor_ghost"] == [], f"ankere uten graf-kobling: {f['anchor_ghost']}"

    st = {s["statement_id"]: s for s in yaml.safe_load(
        (ROT / "public" / "graph" / "statements.yaml").read_text(encoding="utf-8"))["statements"]}
    # DESI DR2-kollapsen og Variant H-negativen skal være ankret, ikke bare kartlagt.
    for sid in ("efc.h1.002", "efc.h1.003", "efc.h4.001", "efc.core.status.001"):
        ankere = [a for a in st[sid]["appears_on"] if a.get("anchor")]
        assert ankere, f"{sid} mangler ankret kobling til en offentlig side"
    assert st["efc.sparc.001"]["appears_on"] == [], (
        "sparc.001 ble tilbakeført til side-løs 2026-09-17 — verdien finnes ikke på "
        "atlas/likelihood-ledger/validation-ledger")
