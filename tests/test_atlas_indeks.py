"""Tests that the generated index surface is complete and readable."""
from __future__ import annotations

import json
import pathlib
import re

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
    """The node ids, read from the bold head pair in each row.

    A row is TWO lines (a head plus named details) on purpose: the first
    version had nine unnamed columns, among them «1 · nei», and was
    unreadable. The test therefore reads the id where it stands — not a
    column index that would hide that the format has changed.
    """
    return [m.group(1) for line in _index_lines()
            if (m := re.match(r"^- \*\*[A-Za-z0-9]{1,2} · ([\w.]+)\*\*", line))]


def test_hver_publiserte_node_staar_noyaktig_en_gang():
    ids = _node_rows()
    expected = [node["id"] for node in _public_nodes()]
    assert len(ids) == len(expected)
    assert sorted(ids) == sorted(expected)
    assert len(ids) == len(set(ids))


def test_hver_node_har_navngitte_detaljer():
    """A number without a label is a riddle. The columns shall say what they are."""
    detaljer = [line for line in _index_lines() if line.startswith("  ")]
    assert detaljer, "ingen detaljlinjer"
    for linje in detaljer:
        assert "perspective=" in linje and "group=" in linje, linje
    # ingen bar «1 · nei»-kolonne igjen
    assert not any(re.search(r"·\s*\d+\s*·\s*(ja|nei)\s*$", l)
                   for l in _index_lines())


def test_overskriftens_tall_er_utledet_fra_banken():
    text = INDEKS.read_text(encoding="utf-8")
    public = _public_nodes()
    import sys
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    import efc_atlas_generator as generator
    ghost = sum(generator._gruppe(node["id"]) == "ghost" for node in public)
    grunn = generator.uten_gruppe_grunner(public)
    evidence = sum((node.get("epistemikk") or {}).get("evidensstatus") == "ingen" for node in public)
    questions = sum(len(node.get("open_questions") or []) for node in public)
    assert sum(grunn.values()) == ghost, (grunn, ghost)
    expected = (f"> {len(public)} published nodes · "
                f"{generator.uten_gruppe_frase(public, '')} · "
                f"{evidence} without evidence · {questions} open questions")
    assert expected in text


def test_hver_gruppelos_node_er_navngitt_med_grunn():
    text = INDEKS.read_text(encoding="utf-8")
    section = text.split("## With no group yet", 1)[1]
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


def test_spliten_summerer_og_flaten_pastaar_ingen_byggestatus():
    """K2: the group-less have no GROUP, not a build status.

    The split is read positionally from the generator's own accounting
    (observation, regime, engine, other — in that insertion order), so this
    test adds no Norwegian of its own. What it pins: the four reasons add up to
    the number of group-less nodes, and the surfaces never fall back to the
    English phrasing "designed and not built" that turned a placement fact into
    a build status.
    """
    text = INDEKS.read_text(encoding="utf-8")
    public = _public_nodes()
    import sys
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    import efc_atlas_generator as generator
    grunn = generator.uten_gruppe_grunner(public)
    gruppelose = sum(generator._gruppe(n["id"]) == "ghost" for n in public)
    assert sum(grunn.values()) == gruppelose, (grunn, gruppelose)
    assert gruppelose > 0, "ingen gruppelose noder — testen er blind"
    # why they are missing, not just that they are
    talla = [int(x) for x in __import__("re").findall(r"(\d+) [a-z]+", text.split("without a group yet", 1)[1].split(")")[0])]
    assert talla == list(grunn.values()), (talla, list(grunn.values()))
    for flate in ("docs/efc-atlas/SYSTEM.md", "docs/efc-atlas/atlas.html",
                  "docs/efc-atlas/atlas/data.mjs"):
        assert "designed and not built" not in (ROT / flate).read_text("utf-8"), flate
