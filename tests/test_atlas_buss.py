"""The bus claims in the atlas, measured — never written by hand.

Measured 2026-09-19 against the K2 tip (2373c513, PR #574 open):

    "116 nodes, 19 engine nodes, NATS bridges."      SYSTEM.md §One paragraph
                                                     no date, no consumer
    one measurement, and no runner at all            schema/nats_domener.snapshot.json
                                                     0 of 16 workflow files

Three separate statements live under the word "bus", and conflating them is how
the atlas ended up naming a capability it does not consume:

    domains measured in the snapshot                  measured, with provenance
    published nodes that name a bus route             a position in the bank
    published nodes that say nothing about the bus    the remaining holes
    schedules that run scripts/atlas_volum.py --maal  measured: none

"Consumed by code" and "consumed in drift" can both be true at once. The atlas
may state the first only with the measurement behind it, and the second only
with the count behind it — and it must say which one it is stating.

Every number below is DERIVED (from the bank, the snapshot and
.github/workflows) and compared against the surfaces the generator writes. A
number that moves in its source and not in a surface fails here, and so does a
surface that keeps a number of its own. The mutations in §3 are the point: a
phrase that happens to say 39 today would pass every readback without them.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
GEN_PATH = ROOT / "scripts" / "maintenance" / "efc_atlas_generator.py"
BANK = ROOT / "schema" / "regime_nodes.jsonld"
SNAPSHOT = ROOT / "schema" / "nats_domener.snapshot.json"
WORKFLOWS = ROOT / ".github" / "workflows"
ATLAS = ROOT / "docs" / "efc-atlas"
SYSTEM_MD = ATLAS / "SYSTEM.md"
DATA_MJS = ATLAS / "atlas" / "data.mjs"
ATLAS_HTML = ATLAS / "atlas.html"

#: The alarm the atlas points at when it names the bus as unconsumed in drift.
#: A pointer to a guard that does not exist is a hole that reads like a fix.
ALARM = ROOT / "tests" / "test_atlas_dekning.py"
ALARM_TEST = "test_snapshottet_har_ikke_gaatt_ut_paa_dato"


def _generator():
    spec = importlib.util.spec_from_file_location("efc_atlas_generator", GEN_PATH)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GEN = _generator()


def _text(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _public_nodes() -> list[dict]:
    return [n for n in json.loads(_text(BANK))["nodes"]
            if n.get("synlighet") == "offentlig"]


def _fakta(**kw) -> dict:
    return GEN.buss_fakta(_public_nodes(), **kw)


def _one_paragraph(text: str) -> str:
    deler = text.split("## One paragraph", 1)
    assert len(deler) == 2, "SYSTEM.md has no '## One paragraph' section"
    return deler[1].split("\n## ", 1)[0]


def _known_holes(text: str) -> str:
    deler = text.split("## Known holes", 1)
    assert len(deler) == 2, (
        "SYSTEM.md has no '## Known holes' section — the atlas stopped naming "
        "the bus as unconsumed")
    return deler[1].split("\n## ", 1)[0]


def _line_with(text: str, needle: str) -> str:
    treff = [l for l in text.splitlines() if needle in l]
    assert len(treff) == 1, f"expected one line with {needle!r}, got {len(treff)}"
    return treff[0]


def _bus_hull_from_data() -> list[str]:
    """META.busHull in data.mjs, read back as the array the build writes."""
    tekst = _text(DATA_MJS)
    start = tekst.index("busHull: [")
    slutt = tekst.index("\n]", start)
    return json.loads(tekst[start + len("busHull: "):slutt + len("\n]")])


def _how_html() -> str:
    """HOW_HTML in atlas.html — the interactive view's generated text."""
    linje = _line_with(_text(ATLAS_HTML), "const HOW_HTML = ")
    return json.loads(linje[len("const HOW_HTML = "):].rstrip(";"))


def _schedules(dir_: pathlib.Path) -> list[str]:
    """The generator's own predicate for "a schedule runs the measurement"."""
    return _fakta(workflows=dir_)["kadenser"]


# --- 1. three numbers, three sources, no literal ---------------------------

def test_the_three_numbers_are_read_from_their_own_source():
    """The bank, the snapshot and the schedules are counted, not transcribed."""
    f = _fakta()
    snap = json.loads(_text(SNAPSHOT))["domener"]
    noder = _public_nodes()
    assert f["domener"] == len(snap) > 0, (f["domener"], len(snap))
    assert f["publiserte"] == len(noder)
    assert f["navngir_vei"] + f["stille"] == f["publiserte"]
    assert f["navngir_vei"] > 0 and f["stille"] > 0, (
        "no bus routes at all, or every node names one — the counter is blind")
    assert f["arbeidsflyter"] == len(GEN.arbeidsflyt_filer(WORKFLOWS)), (
        f"the workflow count does not match {WORKFLOWS} — the scan is not "
        f"reading the directory it names")
    assert f["lest_av"] and f["maalt"] and f["dato"] == f["maalt"][:10]


# --- 2. every surface carries the derived numbers --------------------------

def test_the_one_paragraph_states_the_measurement_and_the_schedule():
    """§One paragraph is where "NATS bridges" stood without a date."""
    f = _fakta()
    frase = GEN.buss_frase(f)
    seksjon = _one_paragraph(_text(SYSTEM_MD))
    assert frase in seksjon, (
        f"the one paragraph does not carry the derived bus sentence:\n"
        f"  wanted: {frase}\n  section: {seksjon.strip()[:200]}")
    assert "NATS bridges" not in seksjon, (
        "the unsupported claim is back in the one paragraph")
    assert frase in _line_with(_text(DATA_MJS), "onePara: `"), (
        "the sentence reached SYSTEM.md and not META.onePara")


def test_the_known_holes_list_names_the_bus_as_unconsumed():
    """The atlas's own holes, with the number — the acceptance of this card."""
    f = _fakta()
    system = _known_holes(_text(SYSTEM_MD))
    data = " ".join(_bus_hull_from_data())
    for navn, flate in (("SYSTEM.md", system), ("data.mjs", data)):
        assert str(f["domener"]) in flate, (navn, "domain count missing")
        assert str(f["navngir_vei"]) in flate, (navn, "route count missing")
        assert str(f["stille"]) in flate, (navn, "silent count missing")
        assert re.search(rf"0 of {f['arbeidsflyter']}\b", flate), (
            f"{navn}: the hole does not state how many schedules run the "
            f"measurement")
        assert ".github/workflows" in flate, (
            f"{navn}: the hole does not name where a cadence would live")
    for punkt in GEN.buss_tekst(f):
        assert punkt in system, f"a hole paragraph did not reach SYSTEM.md: {punkt[:60]}"
        assert punkt in data, f"a hole paragraph did not reach data.mjs: {punkt[:60]}"


def test_the_interactive_view_carries_the_same_holes():
    """atlas.html is a generated surface too, and it reads no markdown."""
    f = _fakta()
    html = _how_html()
    assert "Known holes" in html, "the interactive view carries no holes section"
    for tekst in (f"{f['domener']} domains",
                  f"{f['navngir_vei']} of the published nodes name a bus route",
                  f"{f['stille']} say nothing",
                  f"0 of {f['arbeidsflyter']} workflow files"):
        assert tekst in html, f"the interactive view is missing: {tekst!r}"


# --- 3. the numbers move with their sources (mutation, not readback) -------

def test_a_removed_domain_moves_the_domain_count(tmp_path):
    """Delete one measured domain: the sentence must follow the measurement."""
    maaling = json.loads(_text(SNAPSHOT))
    assert len(maaling["domener"]) > 1
    maaling["domener"].pop(sorted(maaling["domener"])[0])
    kopi = tmp_path / "nats_domener.snapshot.json"
    kopi.write_text(json.dumps(maaling), encoding="utf-8")
    mindre = _fakta(snapshot=kopi)
    assert mindre["domener"] == _fakta()["domener"] - 1
    assert GEN.buss_frase(mindre) != GEN.buss_frase(_fakta())


def test_a_removed_route_moves_the_route_count(tmp_path):
    """Drop a node that names a route: both numbers must move, and sum."""
    noder = _public_nodes()
    vei = [n for n in noder if (n.get("stipulasjoner") or {}).get("buss_status")]
    assert len(vei) > 1, "too few bus routes in the bank to mutate"
    mindre = [n for n in noder if n["id"] != vei[0]["id"]]
    f = GEN.buss_fakta(mindre)
    assert f["navngir_vei"] == len(vei) - 1
    # The silent count is about nodes that say NOTHING, so dropping a node that
    # names a route must move the routes and leave the silence where it was.
    assert f["stille"] == len(noder) - len(vei)
    assert f["publiserte"] == len(mindre)
    assert f["navngir_vei"] + f["stille"] == f["publiserte"]


def test_a_workflow_that_runs_the_measurement_moves_the_wording(tmp_path):
    """Add the cadence the atlas says does not exist: the text must flip.

    This is the half that makes the hole honest in both directions: a cadence
    that appears must be NAMED by the surfaces, not contradicted by them.
    """
    (tmp_path / "atlas-maal.yml").write_text(
        "name: measure the bus\njobs:\n  m:\n    steps:\n"
        "      - run: python3 scripts/atlas_volum.py --maal\n",
        encoding="utf-8")
    planned = GEN.buss_fakta(_public_nodes(), workflows=tmp_path)
    current = _fakta()
    assert planned["kadenser"] == ["atlas-maal.yml"], planned["kadenser"]
    assert planned["arbeidsflyter"] == 1, (
        "the mutation scan and the tree scan disagree about what a workflow is")
    assert "no schedule" not in GEN.buss_frase(planned)
    assert "atlas-maal.yml" in GEN.buss_frase(planned)
    assert "no schedule" in GEN.buss_frase(current)
    # A near miss must NOT count: the name alone is not a cadence.
    (tmp_path / "atlas-volum-les.yml").write_text(
        "name: read the volume\n      - run: python3 scripts/atlas_volum.py "
        "--hull\n", encoding="utf-8")
    near_miss = GEN.buss_fakta(_public_nodes(), workflows=tmp_path)
    assert near_miss["kadenser"] == ["atlas-maal.yml"], (
        f"--hull is a reader, not the measurement: {near_miss['kadenser']}")


# --- 4. the claim matches the tree, today and every day --------------------

def test_the_no_schedule_claim_matches_the_workflows_on_disk():
    """Claim against reality, both ways.

    Today the tree has no cadence, so every surface must say so. Add one and
    this test names the workflow the surfaces fail to name — the failure mode
    being prevented is a hole that keeps reading "no schedule" after one
    appears.
    """
    f = _fakta()
    flater = {
        "SYSTEM.md §One paragraph": _one_paragraph(_text(SYSTEM_MD)),
        "SYSTEM.md Known holes": _known_holes(_text(SYSTEM_MD)),
        "data.mjs META.onePara": _line_with(_text(DATA_MJS), "onePara: `"),
        "data.mjs META.busHull": " ".join(_bus_hull_from_data()),
        "atlas.html HOW_HTML": _how_html(),
    }
    for navn, flate in flater.items():
        claims_none = re.search(r"no schedule", flate, re.IGNORECASE)
        if f["kadenser"]:
            for kadens in f["kadenser"]:
                assert kadens in flate, (
                    f"{navn} does not name the schedule {kadens} that runs the "
                    f"measurement")
            assert not claims_none, (
                f"{navn} claims no schedule while {f['kadenser']} runs the "
                f"measurement")
        else:
            assert claims_none, (
                f"{navn} does not say that nothing runs the measurement, while "
                f"{f['arbeidsflyter']} workflow files exist and none of them "
                f"does")


def test_a_missing_measurement_raises_instead_of_answering(tmp_path):
    """No snapshot, or one without provenance, is a hole — not a zero."""
    import pytest
    with pytest.raises(SystemExit):
        _fakta(snapshot=tmp_path / "finnes-ikke.json")
    uten_proveniens = tmp_path / "snapshot.json"
    uten_proveniens.write_text(json.dumps({"domener": {"a.b": {"emner": {}}}}),
                               encoding="utf-8")
    with pytest.raises(SystemExit):
        _fakta(snapshot=uten_proveniens)


def test_the_hole_points_at_an_alarm_that_exists():
    """The named 90-day guard is real, and it is still the one that fires."""
    assert ALARM.exists(), f"{ALARM} is gone — the hole points at nothing"
    kilde = _text(ALARM)
    assert f"def {ALARM_TEST}" in kilde, (
        f"{ALARM.name} no longer defines {ALARM_TEST}")
    assert ALARM_TEST in " ".join(_bus_hull_from_data()), (
        "the hole stopped naming the alarm that catches a stale measurement")
    assert "90" in " ".join(_bus_hull_from_data()), (
        "the hole names the alarm without its window")


def test_the_build_reads_the_measurement_and_never_writes_it():
    """A build that writes the snapshot would turn a measurement into a table."""
    for sti in (SNAPSHOT, BANK):
        before = hashlib.sha256(sti.read_bytes()).hexdigest()
        r = subprocess.run([sys.executable, str(GEN_PATH)],
                           capture_output=True, text=True, cwd=ROOT, timeout=180)
        assert r.returncode == 0, r.stderr[-400:]
        after = hashlib.sha256(sti.read_bytes()).hexdigest()
        assert before == after, (
            f"the build rewrote {sti.name} — the measurement is written by "
            f"`atlas_volum.py --maal`, not by the atlas")
    drift = subprocess.run(["git", "status", "--porcelain", "--", "schema/"],
                           capture_output=True, text=True, cwd=ROOT, timeout=30)
    assert drift.stdout.strip() == "", (
        f"the build left the measured files dirty:\n{drift.stdout}")
