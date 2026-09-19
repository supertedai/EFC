"""Every generated surface that states how many nodes the atlas has must, on
the same surface, state how many of them have no group yet.

Measured 2026-09-19 against origin/main 403a9c64. The atlas counted its
published nodes in five surfaces; the group-less count had reached two of them:

    surface                                       total   group-less
    docs/efc-atlas/SYSTEM.md  "One paragraph"     yes     no
    docs/efc-atlas/SYSTEM.md  chapter-9 lede      yes     yes
    docs/efc-atlas/INDEKS.md  header              yes     yes
    docs/efc-atlas/atlas/data.mjs  META.onePara   yes     no
    docs/efc-atlas/atlas/data.mjs  META.stats     yes     no (atlas.html)

A headline that reads fuller than the map is the failure this file exists for:
§One paragraph said "116 nodes, 19 engine nodes, NATS bridges." and nothing
else, and 53 of those 116 have no group yet; the stat strip said "Nodes 116".

The counts below are DERIVED from the bank through the generator's own
accounting — the surfaces are compared with what the bank says today, never
with a literal. A surface that stops carrying the count, or a new surface that
counts nodes without it, fails here.

The surfaces are checked in two layers on purpose. The per-surface layer needs
only what the generator had before this card (`uten_gruppe_grunner` and
`_gruppe`), so the failure it reports is the missing count itself, and it names
the surface. The last layer pins that the wording comes from the ONE derivation
the generator now exposes, so a surface cannot keep a number of its own.
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN_PATH = ROOT / "scripts" / "maintenance" / "efc_atlas_generator.py"
BANK = ROOT / "schema" / "regime_nodes.jsonld"
ATLAS = ROOT / "docs" / "efc-atlas"
SYSTEM_MD = ATLAS / "SYSTEM.md"
INDEKS_MD = ATLAS / "INDEKS.md"
DATA_MJS = ATLAS / "atlas" / "data.mjs"
ATLAS_HTML = ATLAS / "atlas.html"
GENERATED = (SYSTEM_MD, INDEKS_MD, DATA_MJS, ATLAS_HTML)


def _generator():
    spec = importlib.util.spec_from_file_location("efc_atlas_generator", GEN_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


def _public_nodes() -> list[dict]:
    return [n for n in json.loads(BANK.read_text(encoding="utf-8"))["nodes"]
            if n.get("synlighet") == "offentlig"]


def _group_less(noder: list[dict]) -> int:
    """How many of them have no group yet — the generator's own rule."""
    return sum(GEN._gruppe(n["id"]) == "ghost" for n in noder)


def _text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _line_with(text: str, needle: str) -> str:
    treff = [l for l in text.splitlines() if needle in l]
    assert len(treff) == 1, f"expected exactly one line with {needle!r}, got {len(treff)}"
    return treff[0]


def _states_count(surface: str, noder: list[dict]) -> None:
    """Step one: the surface must carry the total AND the group-less count."""
    uten = _group_less(noder)
    assert uten > 0, "no group-less node in the bank: the counter is blind"
    assert f"{len(noder)}" in surface, (
        f"the surface no longer states the node total ({len(noder)}): {surface.strip()}")
    assert re.search(rf"(?<![\d.]){uten}(?![\d])", surface), (
        f"this surface counts {len(noder)} nodes and never says that {uten} of "
        f"them have no group yet: {surface.strip()}")


def _one_paragraph_section(text: str) -> str:
    """The body under "## One paragraph" — the surface, not the whole file."""
    deler = text.split("## One paragraph", 1)
    assert len(deler) == 2, "SYSTEM.md has no '## One paragraph' section"
    return deler[1].split("\n## ", 1)[0]


def _stats_cards_from_data() -> dict[str, str]:
    """META.stats in data.mjs, read as (key -> value) pairs."""
    tekst = _text(DATA_MJS)
    blokk = tekst[tekst.index("stats: ["):]
    blokk = blokk[:blokk.index("]")]
    par = re.findall(r"k:\s*'([^']+)',\s*v:\s*'([^']+)'", blokk)
    assert len(par) >= 2, blokk
    return dict(par)


def _stats_cards(html: str) -> dict[str, str]:
    """The rendered stat strip, read as the array the build writes."""
    linje = _line_with(html, "const STATS = ")
    start = linje.index("[", linje.index("const STATS = "))
    return {c["k"]: c["v"] for c in json.loads(linje[start:linje.rindex("]") + 1])}


# --- 1. the count is derived, not written ---------------------------------

def test_the_count_is_derived_and_moves_with_the_bank():
    """Drop one group-less node: the phrase must follow the bank.

    Without this, a phrase that happens to say 53 today would pass every other
    test in this file after the bank moved.
    """
    noder = _public_nodes()
    uten = [n for n in noder if GEN._gruppe(n["id"]) == "ghost"]
    assert len(uten) > 1, "too few group-less nodes in the bank to mutate"
    mindre = [n for n in noder if n["id"] != uten[0]["id"]]
    for spraak, anker in (("en", "of them"), ("nb", "")):
        full = GEN.uten_gruppe_frase(noder, spraak, anker)
        reduced = GEN.uten_gruppe_frase(mindre, spraak, anker)
        assert full != reduced, f"the {spraak} phrase is a constant: {full}"
        assert reduced.startswith(f"{len(uten) - 1} "), reduced


def test_the_split_sums_to_the_count_the_surfaces_state():
    noder = _public_nodes()
    grunn = GEN.uten_gruppe_grunner(noder)
    uten = _group_less(noder)
    assert uten > 0, "no group-less node: the counter is blind"
    assert sum(grunn.values()) == uten, (grunn, uten)


# --- 2. every counting surface carries it ---------------------------------

def test_system_md_one_paragraph_carries_the_group_less_count():
    noder = _public_nodes()
    seksjon = _one_paragraph_section(_text(SYSTEM_MD))
    assert f"{len(noder)} nodes" in seksjon, (
        f"'One paragraph' stopped stating the node total: {seksjon.strip()}")
    _states_count(seksjon, noder)


def test_system_md_chapter_lede_carries_the_group_less_count():
    noder = _public_nodes()
    linje = _line_with(_text(SYSTEM_MD), "**The whole atlas**")
    assert f"{len(noder)} nodes" in linje, linje
    _states_count(linje, noder)


def test_indeks_header_carries_the_group_less_count():
    """Count only: the header is Norwegian, and this file is English.

    The wording of the Norwegian header is already pinned, derived, by
    tests/test_atlas_indeks.py — including the split behind the number.
    """
    noder = _public_nodes()
    linje = _line_with(_text(INDEKS_MD), "publiserte noder")
    assert f"{len(noder)} publiserte noder" in linje, linje
    _states_count(linje, noder)


def test_data_mjs_one_para_and_chapter_lede_carry_the_group_less_count():
    noder = _public_nodes()
    tekst = _text(DATA_MJS)
    ene = _line_with(tekst, "onePara: `")
    assert f"{len(noder)} nodes" in ene, ene
    _states_count(ene, noder)
    lede = _line_with(tekst, '"lede": "Everything at once')
    _states_count(lede, noder)


def test_the_stat_strip_carries_the_group_less_count():
    """Both cards state the total, so both must state the group-less count."""
    noder = _public_nodes()
    flatene = (("data.mjs", _stats_cards_from_data()),
               ("atlas.html", _stats_cards(_text(ATLAS_HTML))))
    for hvor, by_key in flatene:
        for nokkel in ("Nodes", "S-axis"):
            assert nokkel in by_key, (hvor, by_key)
            assert str(len(noder)) in by_key[nokkel], (hvor, by_key)
            _states_count(f"{nokkel} {by_key[nokkel]}", noder)


def test_every_surface_is_written_by_the_generators_one_derivation():
    """One derivation, five surfaces: the wording comes from the generator.

    Without this, the surfaces could each keep their own number and the index
    header could move on its own — the drift that makes two counters of one
    thing worse than one.
    """
    noder = _public_nodes()
    kort = GEN.uten_gruppe_frase(noder, "en", "", med_grunn=False)
    hold = {
        "One paragraph": (
            _one_paragraph_section(_text(SYSTEM_MD)),
            GEN.uten_gruppe_frase(noder, "en", f"of the {len(noder)}")),
        "chapter-9 lede": (
            _line_with(_text(SYSTEM_MD), "**The whole atlas**"),
            GEN.uten_gruppe_frase(noder, "en", "of them")),
        "index header": (
            _line_with(_text(INDEKS_MD), "publiserte noder"),
            GEN.uten_gruppe_frase(noder, "nb")),
        "META.onePara": (
            _line_with(_text(DATA_MJS), "onePara: `"),
            GEN.uten_gruppe_frase(noder, "en", f"of the {len(noder)}")),
        "chapter-9 in data.mjs": (
            _line_with(_text(DATA_MJS), '"lede": "Everything at once'),
            GEN.uten_gruppe_frase(noder, "en", "of them")),
    }
    for navn, (flate, frase) in hold.items():
        assert frase in flate, f"{navn}: {frase!r} missing from {flate.strip()[:120]}"
    for hvor, by_key in (("data.mjs", _stats_cards_from_data()),
                         ("atlas.html", _stats_cards(_text(ATLAS_HTML)))):
        for nokkel in ("Nodes", "S-axis"):
            assert kort in by_key[nokkel], f"{hvor} card {nokkel!r}: {by_key}"


# --- 3. no counting line anywhere without it ------------------------------

def test_no_generated_line_states_the_total_without_the_group_less_count():
    """The generalised gate: a NEW surface that counts nodes fails here too.

    This is the part that survives the named surfaces above, and it names the
    offending line. The predicate is declared: a line counts nodes when it
    carries the published total as a bare number and says node/noder/measured.
    """
    noder = _public_nodes()
    total = re.compile(rf"(?<![\d.]){len(noder)}(?![\d])")
    kontekst = re.compile(r"node|noder|measured", re.IGNORECASE)
    uten = _group_less(noder)
    assert uten > 0, "no group-less node: the gate is blind"
    antall = re.compile(rf"(?<![\d.]){uten}(?![\d])")
    sett: list[str] = []
    ufullstendige: list[str] = []
    for fil in GENERATED:
        for nr, linje in enumerate(_text(fil).splitlines(), 1):
            if not (total.search(linje) and kontekst.search(linje)):
                continue
            sett.append(f"{fil.name}:{nr}")
            if not antall.search(linje):
                ufullstendige.append(f"{fil.name}:{nr}  {linje.strip()[:100]}")
    assert len(sett) >= 4, (
        f"the gate found only {len(sett)} counting line(s) — it is not measuring "
        f"the surfaces it names: {sett}")
    assert not ufullstendige, (
        "these lines state how many nodes the atlas has without stating how many "
        "of them have no group yet:\n  " + "\n  ".join(ufullstendige))


# --- 4. no group-less node is counted as carrying something ---------------

def test_data_mjs_carries_ghost_per_node_and_the_count_matches():
    """The per-node truth behind the headline: the total is not a built count.

    Read from the generated data, so a build that drops the flag is caught here
    and not only in the surfaces that summarise it.
    """
    tekst = _text(DATA_MJS)
    start = tekst.index("export const NODES = ")
    slutt = tekst.index("\nexport const", start + 10)
    noder = json.loads(tekst[start:slutt][tekst[start:slutt].index("=") + 1:].strip().rstrip(";"))
    publiserte = _public_nodes()
    assert len(noder) == len(publiserte), (len(noder), len(publiserte))
    flagg = [n.get("ghost") for n in noder]
    assert all(isinstance(f, bool) for f in flagg), "a node carries no ghost flag"
    uten = _group_less(publiserte)
    assert sum(flagg) == uten, (sum(flagg), uten)
