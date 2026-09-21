"""THE DECISION: a node must have TAKEN A POSITION, not just omitted the field.

Measured 2026-09-18 (card t_fc25238b): `plasser()` was called from ONE
place — the CLI itself. No hook, no CI. The entry point existed and sat
unused, and each of the night's four closings ended in the same sentence:
"I still have to remember to do it".

The generator already has two guards that FAIL: codes (#476) and
PLACEMENT (#507). Both caught their own author tonight. That is the
pattern.

The third guard is different: it must not require a node to be DONE — it
must require that the CHOICE has been made. An instrument node needs no
engine. But it must say so, not stay silent.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "schema" / "regime_nodes.jsonld"


@pytest.fixture(scope="module")
def nodes() -> list[dict]:
    d = json.loads(ATLAS.read_text(encoding="utf-8"))
    return d["nodes"]


def test_hver_node_har_tatt_stilling_til_buss_domene(nodes: list[dict]) -> None:
    """Either a domain, or a written reason for not having one."""
    missing = []
    for n in nodes:
        if n.get("buss_domene"):
            continue
        s = n.get("stipulasjoner") or {}
        if not s.get("buss_status"):
            missing.append(n["id"])
    assert not missing, (
        f"{len(missing)} node(s) have neither buss_domene nor buss_status: {missing[:8]}")


def test_hver_node_har_tatt_stilling_til_motor(nodes: list[dict]) -> None:
    """Same for engine: a working engine, or a reason for not having one."""
    missing = []
    for n in nodes:
        s = n.get("stipulasjoner") or {}
        if s.get("motor"):
            continue
        if not s.get("motor_status"):
            missing.append(n["id"])
    assert not missing, (
        f"{len(missing)} node(s) have neither motor nor motor_status: {missing[:8]}")


def test_statusene_sier_noe_om_hvorfor(nodes: list[dict]) -> None:
    """"none" is an answer; an empty string is an omission."""
    for n in nodes:
        s = n.get("stipulasjoner") or {}
        for field in ("buss_status", "motor_status"):
            v = s.get(field)
            if v is not None:
                assert v.strip(), f"{n['id']}.{field} is empty — say why"


def test_de_interne_forklarer_seg_selv(nodes: list[dict]) -> None:
    """The internal nodes are not an error — they are a choice that must stand."""
    internal = [n for n in nodes if n.get("synlighet") == "intern"]
    assert internal, "precondition: internal nodes exist"
    for n in internal:
        s = n.get("stipulasjoner") or {}
        assert n.get("buss_domene") or s.get("buss_status"), (
            f"{n['id']} is internal without justification — it must have a "
            f"buss_domene or a written reason for not having one")


# --- Falsifiability: the same rule as for bus and engine (card t_c11ffa45) --
#
# Measured 2026-09-18 from landed main: `ville_falsifisere` was missing on 82
# of 113 nodes, and the schema made the field OPTIONAL. The atlas tested that
# every node CAN carry the field — never that it HAS taken a position. The
# suite was green anyway, also for `obs.bao` — the node that carries the
# counter-evidence to our own regime.
#
# Measured 2026-09-19: 126 nodes (13 new since), 31 can be felled, 4 with a
# status, 91 with a written class.
#
# Measured 2026-09-20 (card t_2d7a6537): the four EFC engine nodes could not
# be settled at all — two carried `terskel_ikke_fastsatt` in a fragment, two
# `stub` — while their thresholds DO exist in sealed sources. Two of them
# (`efc.rotation_engine`, `efc.efc_background_engine`) now carry the contract
# and therefore a falsifier: 33 can be felled, 2 keep a status. The two
# remaining keep it deliberately: they compute nothing, and the schema says a
# node that says so shall NOT count as satisfied falsifiability.
#
# The rule is the same as for bus and engine: the choice must be TAKEN. An
# instrument node cannot be felled by an observation — that is a valid answer.
# An empty field is not an answer, and a text that recurs on fifty nodes is
# neither. This file measures that no node is SILENT (>= 1 answer);
# `test_atlas_motsigelse.py` measures that nobody answers twice (<= 1).

GRUNN = "ikke_falsifiserbar_grunn"

#: Texts that look like an answer without being one.
PLASSHOLDERE = ("vet ikke", "ukjent", "ikke relevant", "n/a", "todo",
                "fylles ut", "kommer", "tbd", "-")


def _grunn(n: dict) -> str | None:
    """The reason lives under `stipulasjoner`, like `buss_status` and
    `motor_status`."""
    return (n.get("stipulasjoner") or {}).get(GRUNN)


def test_hver_node_har_tatt_stilling_til_falsifiserbarhet(nodes: list[dict]) -> None:
    """Every node answers: a falsifier, a fixed status — or a reason.

    The population is ALL 126 nodes, not only the public ones. The numbers are
    pinned because both outcomes are real: a node that loses its falsifier, and
    a node that is reclassified, must be a choice someone has made — not
    something that happens while nobody looks.
    """
    def avgjort(n: dict) -> bool:
        return bool(n.get("ville_falsifisere") or n.get("falsifiserbarhet")
                    or _grunn(n))

    uten = [n["id"] for n in nodes if not avgjort(n)]
    assert not uten, (
        f"{len(uten)} of {len(nodes)} node(s) have not taken a position on "
        f"whether they can be felled: {uten[:8]}")
    kan = [n["id"] for n in nodes if n.get("ville_falsifisere")]
    skylder = [n["id"] for n in nodes if n.get("falsifiserbarhet")]
    maa = [n["id"] for n in nodes if _grunn(n)]
    assert len(nodes) == 126, f"the atlas changed size: {len(nodes)}"
    assert len(kan) == 33, (
        f"falsifiable: {len(kan)} — expected 33 (27 public + 4 "
        f"internal + the two engines given a contract 2026-09-20). If the "
        f"number fell, a node lost its falsifier")
    assert len(skylder) == 2, (
        f"with a falsifiability status: {len(skylder)} — expected 2 "
        f"(the two that compute nothing: lensing and cluster)")
    assert len(maa) == 91, (
        f"with a written reason: {len(maa)} — expected 91. If the number fell, "
        f"a node has been given a falsifier; someone must have decided that")
    assert len(kan) + len(skylder) + len(maa) == len(nodes), (
        "at least one node has answered twice — see test_atlas_motsigelse.py")


def test_grunnen_er_en_deklarert_klasse(nodes: list[dict]) -> None:
    """A shared reason must be a DECLARED class, not a silent copy.

    Measured 2026-09-19: 91 of the 126 nodes carry a rationale, and they use
    exactly three texts - 63 instrument nodes, 27 established-physics nodes
    and one self-description. Requiring a UNIQUE sentence per node would
    require 91 paraphrases of two ideas; that was this test's earlier demand,
    and the data broke it the right way.

    What must hold instead: the class vocabulary is CLOSED (the counts are
    pinned here, so a node joining or leaving a class is a decision someone
    made), every text is long enough to mean something, and no two texts are
    the same statement in two spellings.
    """
    tekster: dict[str, list[str]] = {}
    for n in nodes:
        t = _grunn(n)
        if t is None:
            continue
        assert t.strip(), f"{n['id']}.{GRUNN} is empty — say why"
        assert len(t) >= 40, (
            f"{n['id']}.{GRUNN} is {len(t)} characters — too short to mean anything")
        assert t.strip().lower() not in PLASSHOLDERE, (
            f"{n['id']}.{GRUNN} is a placeholder: {t!r}")
        tekster.setdefault(t, []).append(n["id"])

    def _nok(t: str) -> str:
        t = t.lower().replace("\u00e6", "ae").replace("\u00f8", "o").replace("\u00e5", "a")
        return re.sub(r"[^a-z0-9]+", "", t)

    sett: dict[str, str] = {}
    for t in tekster:
        nok = _nok(t)
        assert nok not in sett, (
            f"two reasons are the same statement in two spellings: "
            f"{sett[nok]!r} / {t!r}")
        sett[nok] = t

    klasse = sorted(len(ids) for ids in tekster.values() if len(ids) > 1)
    assert klasse == [27, 63], (
        f"the classes changed: {klasse} - expected [27, 63]. A node moved "
        f"between classes; that is a decision someone must make")

def test_grunnen_navngir_ikke_feltet_den_erstatter(nodes: list[dict]) -> None:
    """`atlas_lesing._har_falsifikator` reads the node as TEXT.

    It asks whether the string `ville_falsifisere` occurs in
    `json.dumps(node)` — so a reason that writes its own field name would
    count as a falsifier both in the lookup and in the navigation's
    `kan_felles`. The guard stands here because it is invisible in the data:
    it fires only when someone rephrases.
    """
    lekkasje = [n["id"] for n in nodes if "ville_falsifisere" in (_grunn(n) or "")]
    assert not lekkasje, (
        f"{len(lekkasje)} node(s) write the field name in their reason and "
        f"would be counted as falsifiable: {lekkasje[:6]}")
