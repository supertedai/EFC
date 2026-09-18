"""The ledger twins must stay twins — measured, not assumed.

`docs/validation-ledger/data/ledger.json` is the canonical source for the GRAV
claim texts. Two artifacts PROJECT it:

  data/grav.json           $.claims[i].text
  index.md §3              the "Physics Claim" cell = text[:97] + "..."

PR #460 translated the source and left both projections carrying the OLD
Norwegian, and nothing in the tree could see it: every other field was still
identical, and the stopword count of each file was "0" *of its own* content.
`scripts/maintenance/efc_ledger_speil.py` repairs and checks the pair; these
tests lock the two identities so the drift class cannot reopen silently.

The tests read the WORKING TREE, which is where the mirror script reads and
writes — a test that measured a git ref instead would report a clean tree while
an uncommitted edit was drifting (rule: read the count from the same place the
code reads it).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

_MAINT = _REPO / "scripts" / "maintenance"
if str(_MAINT) not in sys.path:
    sys.path.insert(0, str(_MAINT))

import efc_ledger_speil as speil  # noqa: E402

LEDGER = _REPO / "docs" / "validation-ledger" / "data" / "ledger.json"
GRAV = _REPO / "docs" / "validation-ledger" / "data" / "grav.json"
INDEX = _REPO / "docs" / "validation-ledger" / "index.md"


def kanoniske(ledger: dict) -> list[str]:
    return speil.kanoniske_tekster(ledger)


def _load():
    return (json.loads(LEDGER.read_text(encoding="utf-8")),
            json.loads(GRAV.read_text(encoding="utf-8")),
            INDEX.read_text(encoding="utf-8"))


def test_the_measured_truncation_holds_for_every_claim_cell():
    """Every claim cell in index.md is exactly 100 characters, i.e. the source
    text cut at 97 plus an ellipsis — the rule the projection uses."""
    _, _, index = _load()
    cells = 0
    for ln in index.split("\n"):
        m = speil.CLAIM_ROW.match(ln)
        if not m or not m.group(3).strip().startswith("❓") or m.group(4).strip() != "None":
            continue
        if m.group(2) == speil.EMPTY_CELL:
            continue
        assert len(m.group(2)) == speil.TRUNC + 3, (
            f"claim cell is {len(m.group(2))} characters, not "
            f"{speil.TRUNC + 3}: {m.group(2)[:60]!r}")
        assert m.group(2).endswith("...")
        cells += 1
    assert cells > 200, f"the claim table looks empty ({cells} non-empty cells)"


def test_grav_json_is_a_projection_of_the_canonical_ledger():
    """Byte-for-byte identity on every field, with one declared representation
    difference: grav.json encodes "no text" as null where ledger.json uses ""."""
    ledger, grav, _ = _load()
    kanon = ledger["grav_pipeline"]["claims"]
    grav_claims = grav["claims"]
    assert len(grav_claims) == len(kanon), "the arrays are no longer twins"

    differing_text, differing_other = [], []
    for i, (g, k) in enumerate(zip(grav_claims, kanon)):
        assert (g.get("text") or "") == (k.get("text") or ""), (
            f"claims[{i}].text differs: grav={g.get('text')!r} "
            f"ledger={k.get('text')!r} — run efc_ledger_speil.py --skriv")
        for f in set(g) | set(k):
            if f == "text":
                continue
            if g.get(f) != k.get(f):
                differing_other.append((i, f))
        if (g.get("text") or "") != (k.get("text") or ""):
            differing_text.append(i)
    assert not differing_text
    assert not differing_other, f"fields besides text differ: {differing_other[:5]}"


def test_every_claim_cell_is_the_projection_of_its_canonical_text():
    """Both directions: each cell is built from the source, and each source
    claim has the cell its rendering demands."""
    ledger, _, index = _load()
    kanon = [c.get("text") or "" for c in ledger["grav_pipeline"]["claims"]]
    seen = set()
    for ln in index.split("\n"):
        m = speil.CLAIM_ROW.match(ln)
        if not m or not m.group(3).strip().startswith("❓") or m.group(4).strip() != "None":
            continue
        i = int(m.group(1)) - 1
        assert i < len(kanon), f"row {m.group(1)} has no claim behind it"
        assert m.group(2) == speil.projeksjon(kanon[i]), (
            f"row {m.group(1)} is not the projection of ledger.json claims[{i}]: "
            f"cell={m.group(2)[:60]!r} expected={speil.projeksjon(kanon[i])[:60]!r}")
        seen.add(m.group(1))
    assert len(seen) > 200


def test_the_check_reports_drift_when_the_twin_is_mutated(monkeypatch, tmp_path):
    """Mutation: the checker must FAIL on a single moved character, not only on
    a structural mismatch. Without this, "0 deviations" is an assertion nobody
    has seen fail."""
    ledger, grav, index = _load()
    kanon = kanoniske(ledger)
    idx = next(i for i, t in enumerate(kanon) if t)
    grav["claims"][idx]["text"] = kanon[idx] + " (drift)"
    gpath = tmp_path / "grav.json"
    gpath.write_text(json.dumps(grav, ensure_ascii=False), encoding="utf-8")

    def fake_load():
        return ledger, json.loads(gpath.read_text(encoding="utf-8")), index

    monkeypatch.setattr(speil, "_load", fake_load)
    rap = speil.sjekk()
    assert rap["grav_text_avvik"] == 1, rap
    assert any("differ" in f for f in rap["feil"]), rap


def test_a_stale_claim_cell_is_reported_as_drift(monkeypatch):
    """The other direction: a cell that is neither the old nor the new
    projection is a hand edit, and the script refuses it."""
    ledger, grav, index = _load()
    lines = index.split("\n")
    for n, ln in enumerate(lines):
        m = speil.CLAIM_ROW.match(ln)
        if m and m.group(3).strip().startswith("❓") and m.group(4).strip() == "None" \
                and m.group(2) != speil.EMPTY_CELL:
            lines[n] = f"| {m.group(1)} | hand-edited cell | {m.group(3)} | {m.group(4)} |"
            break
    mutated = "\n".join(lines)
    monkeypatch.setattr(speil, "_load", lambda: (ledger, grav, mutated))
    rap = speil.sjekk()
    assert rap["index_rader_avvik"] >= 1, rap


def kanoniske(ledger: dict) -> list[str]:
    return speil.kanoniske_tekster(ledger)
