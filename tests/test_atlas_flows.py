"""FLOWS must be DRAWABLE — not merely defined.

Measured 2026-09-17 (card t_508e0c03): hopPath() in template.html looked up
`sceneNodes.find(n=>n.id===h.from)` while the FLOWS hops carry CODES
(«HA -> KL»). The result was that ALL endpoints were unresolved and the
flow lines were dead code.

The root is the namespace: the nodes have `id`, the hops have `code`, and the
lookup knew only one of them.
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
    """The lookup must span BOTH namespaces — otherwise half the atlas is invisible."""
    assert "NODES.flatMap(n=>[[n.id,n],[n.code,n]])" in template, (
        "byId is still built on id alone — the hops carry codes")


def test_hopPath_slaar_opp_i_begge_navnerom(template: str) -> None:
    m = re.search(r"function hopPath\(h\)\{(.*?)\n\}", template, re.S)
    assert m, "did not find hopPath"
    kropp = m.group(1)
    assert "n.code" in kropp, (
        "hopPath still looks up only in the id namespace")
    assert "return null" in kropp, "hopPath must still fail loudly"


def test_alle_hopp_loeser_seg_i_dataene() -> None:
    """The real proof: every endpoint in FLOWS must exist as a node."""
    if not DATA.exists():
        pytest.skip("data.mjs is missing")
    src = DATA.read_text(encoding="utf-8")
    noder = json.loads(re.search(r"export const NODES\s*=\s*(\[.*?\]);", src, re.S).group(1))
    flows = json.loads(re.search(r"export const FLOWS\s*=\s*(\[.*?\]);", src, re.S).group(1))
    nokler = {n["code"] for n in noder} | {n["id"] for n in noder}
    uopploest = [(h[0], h[1]) for f in flows for h in (f.get("hops") or [])
                 if h[0] not in nokler or h[1] not in nokler]
    assert not uopploest, f"unresolved hop endpoints: {uopploest[:6]}"
    assert sum(len(f.get("hops") or []) for f in flows) > 0, "no hops to test"
