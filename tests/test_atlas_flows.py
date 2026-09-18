"""FLOWS maa kunne TEGNES — ikke bare defineres.

Maalt 2026-09-17 (kort t_508e0c03): hopPath() i template.html slo opp
`sceneNodes.find(n=>n.id===h.from)` mens FLOWS-hoppene baerer KODER
(«HA -> KL»). Resultatet var at ALLE endepunkter var uopploeste og
flytenes linjer var dod kode.

Roten er navnerommet: nodene har `id`, hoppene har `code`, og oppslaget
kjente bare ett av dem.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
TEMPLATE = ROT / "docs" / "efc-atlas" / "atlas" / "template.html"
DATA = ROT / "docs" / "efc-atlas" / "atlas" / "data.mjs"


@pytest.fixture(scope="module")
def template() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def test_byId_kjenner_baade_id_og_kode(template: str) -> None:
    """Oppslaget maa romme BEGGE navnerom — ellers er halve atlaset usynlig."""
    assert "NODES.flatMap(n=>[[n.id,n],[n.code,n]])" in template, (
        "byId bygges fortsatt bare paa id — hoppene baerer koder")


def test_hopPath_slaar_opp_i_begge_navnerom(template: str) -> None:
    m = re.search(r"function hopPath\(h\)\{(.*?)\n\}", template, re.S)
    assert m, "fant ikke hopPath"
    kropp = m.group(1)
    assert "n.code" in kropp, (
        "hopPath slår fortsatt bare opp i id-navnerommet")
    assert "return null" in kropp, "hopPath skal fortsatt feile hoeyt"


def test_alle_hopp_loeser_seg_i_dataene() -> None:
    """Den ekte proven: hvert endepunkt i FLOWS maa finnes som node."""
    if not DATA.exists():
        pytest.skip("data.mjs mangler")
    src = DATA.read_text(encoding="utf-8")
    noder = json.loads(re.search(r"export const NODES\s*=\s*(\[.*?\]);", src, re.S).group(1))
    flows = json.loads(re.search(r"export const FLOWS\s*=\s*(\[.*?\]);", src, re.S).group(1))
    nokler = {n["code"] for n in noder} | {n["id"] for n in noder}
    uopploest = [(h[0], h[1]) for f in flows for h in (f.get("hops") or [])
                 if h[0] not in nokler or h[1] not in nokler]
    assert not uopploest, f"uopploeste hopp-endepunkter: {uopploest[:6]}"
    assert sum(len(f.get("hops") or []) for f in flows) > 0, "ingen hopp aa teste"
