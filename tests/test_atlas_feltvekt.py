"""Which requirements a new node must fill — and which of them ANYONE reads.

Pins the separation `plasser` answers with: the requirements a reader reads,
against the fields no reader touches — with the measured number behind each
one.

The measurement behind every entry is a MUTATION, not a count
(`scripts/atlas_feltvekt.py`): the field is emptied on every node that carries
it, inside a throwaway repo, and each of the five readers is asked again. A
count sees the word; the mutation sees whether the field carries anything.
`docs/atlas-lesing.md` records the measured reason the difference matters:
three tests that only required the words to be present passed a mutant that
said the exact opposite.

What must not rot:

* A requirement standing in either group WITHOUT a measurement fails here.
  That is the failure this file exists to make impossible.
* The recorded table is compared against a FRESH mutation, so a stale number
  is red instead of quoted.
* The mutation runs in a throwaway repo. No node in the bank may change for
  the measurement to be possible.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import atlas_feltvekt as fv   # noqa: E402
import atlas_lesing        # noqa: E402
from _gitmiljo import AMBARTE_CONFIG_VARS, AMBARTE_REPO_VARS  # noqa: E402

TEKST = "BAO maaling i galakser"


def kravene(atlas: dict) -> list[str]:
    """The same list `plasser` walks: the schema first, then the house's own."""
    ut = list(atlas_lesing.skjema_krav(atlas))
    return ut + [f for f in atlas_lesing.HUSETS_KRAV if f not in ut]


@pytest.fixture(scope="module")
def maalt():
    """The mutation, run once for the module — a run is not cheap.

    The ambient git variables are removed first: `tests/_gitmiljo.py` measured
    what an inherited GIT_DIR does to a test that builds its own repo, and this
    measurement builds five readers' worth of them.
    """
    with pytest.MonkeyPatch.context() as mp:
        for navn in AMBARTE_REPO_VARS + AMBARTE_CONFIG_VARS:
            mp.delenv(navn, raising=False)
        yield fv.maal(ROT, "HEAD")


@pytest.fixture(scope="module")
def atlas() -> dict:
    return atlas_lesing.les_atlas(ROT, ref="HEAD")


# --- the measurement itself -------------------------------------------------

def test_the_measurement_covers_every_requirement(maalt, atlas):
    """Measured on every requirement, and on nothing else."""
    krav = kravene(atlas)
    mangler = atlas_lesing.umaalte_krav(krav, fv.tabell(maalt))
    assert not mangler, (
        f"these requirements have no mutation measurement behind them: "
        f"{mangler} — run scripts/atlas_feltvekt.py and record the numbers")
    ukjente = sorted(set(fv.tabell(maalt)) - set(krav))
    assert not ukjente, (
        f"the measurement weighs fields the atlas no longer requires: "
        f"{ukjente} — remove them or argue for the requirement")


def test_the_recorded_table_matches_a_fresh_mutation(maalt):
    """The recorded numbers are a measurement, not a quotation."""
    fersk = fv.tabell(maalt)
    assert fersk == atlas_lesing.FELT_LESERE, (
        "the recorded table is stale. Re-measure with\n"
        "    python3 scripts/atlas_feltvekt.py . --ref origin/main --python")


def test_a_requirement_in_a_group_without_a_measurement_is_named(atlas):
    """The check the acceptance turns on: no number, no group."""
    krav = kravene(atlas)
    uten = {f: v for f, v in atlas_lesing.FELT_LESERE.items()
            if f != "fractal"}
    assert atlas_lesing.umaalte_krav(krav, uten) == ["fractal"], (
        "a requirement with no measurement must be named, not classified")


# --- what `plasser` answers with --------------------------------------------

def test_every_requirement_carries_the_measured_readers(atlas):
    p = atlas_lesing.plasser(atlas, TEKST)
    assert {k["felt"] for k in p["krav"]} == set(kravene(atlas)), p["krav"]
    for k in p["krav"]:
        assert k["maalt"] is True, k
        assert k["lesere"] == list(atlas_lesing.FELT_LESERE[k["felt"]]), k
        assert k["lesere_av"] == len(atlas_lesing.LESERE), k
        assert k["leses"] == bool(k["lesere"]), k


def test_the_readers_are_named_and_nothing_else(atlas):
    p = atlas_lesing.plasser(atlas, TEKST)
    for k in p["krav"]:
        assert set(k["lesere"]) <= set(atlas_lesing.LESERE), k
    assert len(atlas_lesing.LESERE) == len(set(atlas_lesing.LESERE)) == 5, (
        "the reader list is the five the closure list names; a sixth reader "
        "changes every number in the table and must be re-measured")


def test_the_summary_separates_the_two(atlas):
    p = atlas_lesing.plasser(atlas, TEKST)
    o = p["oppsummering"]
    maalt = {k["felt"] for k in p["krav"] if k["maalt"]}
    assert o["leses"] + o["uten_leser"] + len(o["umaalt"]) == len(p["krav"]), o
    assert o["leses"] == sum(1 for k in p["krav"] if k["leses"]), o
    assert set(o["uten_leser_felt"]) == {k["felt"] for k in p["krav"]
                                         if k["maalt"] and not k["leses"]}, o
    assert o["lesere_av"] == len(atlas_lesing.LESERE), o
    assert len(maalt) == len(p["krav"]) - len(o["umaalt"]), o


def test_nothing_is_called_unread_without_a_measurement(atlas):
    """A field nobody reads and a field nobody measured are two answers."""
    p = atlas_lesing.plasser(atlas, TEKST)
    tomt = {k: v for k, v in atlas_lesing.FELT_LESERE.items() if not v}
    o = p["oppsummering"]
    assert o["uten_leser"] == len(tomt), (
        f"the summary counts {o['uten_leser']} unread requirement(s), the "
        f"measurement has {len(tomt)}: {sorted(tomt)}")
    assert sorted(o["uten_leser_felt"]) == sorted(tomt), o


def test_the_premise_of_k1_is_measured_today(atlas):
    """K1: stop requiring fields nobody reads. Measured: there are none.

    The premise was measured again on 2026-09-19 and did NOT survive: every
    requirement is read by at least one reader. If this turns red, a
    requirement has become dead weight and `plasser` names it.
    """
    p = atlas_lesing.plasser(atlas, TEKST)
    o = p["oppsummering"]
    assert o["uten_leser"] == 0, (
        f"{o['uten_leser']} requirement(s) are read by nobody: "
        f"{o['uten_leser_felt']} — the closure list can shrink, but the "
        f"schema is a human decision (C10 gate, t_2e60afa6)")


# --- an empty mutation is not a measurement ---------------------------------

def _liten_bank(tmp_path: Path) -> Path:
    """A minimal repo where one requirement is carried by NO node."""
    import json

    from _gitmiljo import rent_gitmiljo

    miljo = rent_gitmiljo(tmp_path / "hjem")
    rot = tmp_path / "bank"
    (rot / "schema").mkdir(parents=True)
    (rot / "schema" / "regime_node.schema.json").write_text(
        json.dumps({"$defs": {"RegimeNode": {"required": ["id", "episenter"]}}}),
        encoding="utf-8")
    (rot / "schema" / "regime_nodes.jsonld").write_text(
        json.dumps({"nodes": [{"id": "a.b", "synlighet": "offentlig"}]}),
        encoding="utf-8")
    for sti in ("schema/atlas_dekning.json", "schema/nats_domener.snapshot.json"):
        (rot / sti).write_text(json.dumps({"domener": {}}), encoding="utf-8")
    felles = ["-c", "user.email=t@e.org", "-c", "user.name=t",
              "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=rot, env=miljo,
                   check=True)
    subprocess.run(["git", *felles, "add", "-A"], cwd=rot, env=miljo,
                   check=True)
    subprocess.run(["git", *felles, "commit", "-qm", "base"], cwd=rot,
                   env=miljo, check=True)
    return rot


def test_a_requirement_no_node_carries_is_not_measured(tmp_path):
    """Emptying a field the bank does not have changes nothing — and says so.

    A vacuous mutation answers "no reader noticed"; that answer would look
    exactly like a finding. It must be named as unmeasured instead.
    """
    rot = _liten_bank(tmp_path)
    with pytest.MonkeyPatch.context() as mp:
        for navn in AMBARTE_REPO_VARS + AMBARTE_CONFIG_VARS:
            mp.delenv(navn, raising=False)
        maalt = fv.maal(rot, "HEAD")

    assert maalt["felt"]["episenter"]["bar"] == 0, maalt["felt"]["episenter"]
    assert "episenter" not in fv.tabell(maalt), (
        "a mutation that changed nothing was recorded as a measurement")
    assert "id" in fv.tabell(maalt), maalt["felt"]["id"]
    assert atlas_lesing.umaalte_krav(["id", "episenter"], fv.tabell(maalt)) \
        == ["episenter"]


# --- the bank is not the measurement's playground ---------------------------

def test_the_measurement_leaves_the_bank_alone(tmp_path):
    """No node in the bank may be forced to change for the build to go."""
    from _gitmiljo import rent_gitmiljo

    miljo = rent_gitmiljo(tmp_path / "hjem")
    miljo.update({"GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@e.org"})
    ut = subprocess.run(
        ["git", "-C", str(ROT), "status", "--porcelain", "--",
         "schema/regime_nodes.jsonld"],
        capture_output=True, text=True, env=miljo, check=True).stdout.strip()
    assert not ut, f"the bank was edited by the measurement: {ut}"
