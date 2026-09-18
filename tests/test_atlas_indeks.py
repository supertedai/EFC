"""Tester at den genererte indeksflaten er komplett og lesbar."""
from __future__ import annotations

import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parents[1]
BANK = ROT / "schema" / "regime_nodes.jsonld"
INDEKS = ROT / "docs" / "efc-atlas" / "INDEKS.md"


def _bank():
    return json.loads(BANK.read_text(encoding="utf-8"))


def _public_nodes():
    return [n for n in _bank()["nodes"] if n.get("synlighet") == "offentlig"]


def _index_lines():
    return INDEKS.read_text(encoding="utf-8").splitlines()


def _node_rows():
    return [line for line in _index_lines() if line.startswith("- ") and " · " in line]


def test_hver_publiserte_node_staar_noyaktig_en_gang():
    rows = _node_rows()
    ids = [row.split(" · ", 2)[1] for row in rows]
    expected = [node["id"] for node in _public_nodes()]
    assert len(rows) == len(expected)
    assert sorted(ids) == sorted(expected)
    assert len(ids) == len(set(ids))


def test_overskriftens_tall_er_utledet_fra_banken():
    text = INDEKS.read_text(encoding="utf-8")
    public = _public_nodes()
    import sys
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    import efc_atlas_generator as generator
    ghost = sum(generator._gruppe(node["id"]) == "ghost" for node in public)
    evidence = sum((node.get("epistemikk") or {}).get("evidensstatus") == "ingen" for node in public)
    questions = sum(len(node.get("open_questions") or []) for node in public)
    expected = f"> {len(public)} publiserte noder · {ghost} designet og ikke bygget · {evidence} mangler evidens · {questions} aapne spoersmaal"
    assert expected in text


def test_hver_ghost_node_er_navngitt_i_ikke_bygget():
    text = INDEKS.read_text(encoding="utf-8")
    section = text.split("## Hva som ikke er bygget", 1)[1]
    import sys
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    import efc_atlas_generator as generator
    for node in _public_nodes():
        if generator._gruppe(node["id"]) == "ghost":
            assert node["id"] in section


def test_indeksens_linjelaengde_er_lesbar():
    assert max(map(len, _index_lines()), default=0) <= 200


def test_indeks_uten_trailing_whitespace():
    assert all(line.rstrip() == line for line in _index_lines())
