"""The verification layer (epistemikk v7) — a fit result is NOT a posterior.

Card t_bf62ce48. K2 (card t_3f919915) measured a separator: a fit result and a
verified posterior are two DIFFERENT epistemic states. The atlas carried `proxy`
and nothing else, so «the posterior is not verified» read exactly like «the
measurement failed».

    fit ->[identifiability]-> inferable ->[sampling]-> posterior_verifisert

Every arrow is a NAMED transformation, so a break says WHERE and WHY instead of
only which status a node has. `inferens_feil` therefore never collapses into
«the measurement failed»: the state carries its cause, its diagnostics and its
instrument.

Two rules are held HERE and not in the schema, deliberately (the same limit the
uncertainty layer lives with, measured through C10: `scripts/maintenance/
efc_schema_check.py` reports every subschema with `properties` as open, so a
conditional requirement cannot be expressed in the dialect):

1. **A verdict carries its numbers.** `posterior_verifisert`, `inferens_feil`,
   `ikke_identifiserbar` and `uavklart` are claims, and a claim without its
   diagnostics is an empty word.
2. **A failure names its arrow and its cause.** `inferens_feil` and
   `ikke_identifiserbar` must say which transformation broke and why — and a
   chain that did not break must not carry a `brudd` at all.

The tests mutate the bank in memory and require the checker to FALL. A test that
only sees that the field exists sees the shape and not the meaning.
"""
from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

from atlas_lesing import (AtlasLesingFeil, VERIFISERING_AARSAKER,  # noqa: E402
                          VERIFISERING_BRUDD, VERIFISERING_DOMMER,
                          VERIFISERING_KJEDE, VERIFISERING_TILSTANDER,
                          VERIFISERING_TRANSFORMASJONER, VERIFISERING_METRIKKER,
                          VERIFISERING_ARBITER, sjekk_verifisering)
import efc_schema_check  # noqa: E402

SKJEMA_STI = ROT / "schema" / "regime_node.schema.json"
BANK_STI = ROT / "schema" / "regime_nodes.jsonld"

# The nodes whose evidence is taken from the SPARC fit, named here because the
# acceptance test below is about THEM: their numbers are fit-verified, and the
# atlas must be unable to read that as posterior-verified.
SPARC_NODER = ("efc.lag_s", "efc.lag_c0")
FILTER_NODE = "efc.l2"

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

requires_jsonschema = pytest.mark.skipif(
    jsonschema is None, reason="jsonschema not installed")


def _skjema() -> dict:
    return json.loads(SKJEMA_STI.read_text(encoding="utf-8"))


def _bank() -> dict:
    return json.loads(BANK_STI.read_text(encoding="utf-8"))


def _node(bank: dict, node_id: str) -> dict:
    return next(n for n in bank["nodes"] if n["id"] == node_id)


def _lagt(bank: dict):
    """(node, state) for every node that has taken a position."""
    for n in bank["nodes"]:
        v = (n.get("epistemikk") or {}).get("verifisering")
        if v is not None:
            yield n, v


def _dok(bank: dict, noder: list) -> dict:
    d = {k: v for k, v in bank.items() if k not in ("nodes", "relations")}
    d["nodes"] = noder
    d["relations"] = []
    return d


def _mutert(bank: dict, node_id: str, endre) -> dict:
    """The bank with ONE state changed — the mutation the test must kill."""
    ny = copy.deepcopy(bank)
    endre(_node(ny, node_id)["epistemikk"]["verifisering"])
    return ny


def _epi(bank: dict) -> dict:
    return _skjema()["$defs"]["RegimeNode"]["properties"]["epistemikk"]


# ---------------------------------------------------------------------------
# The field: optional, closed, additive — and never required
# ---------------------------------------------------------------------------

def test_feltet_er_deklarert_og_aldri_obligatorisk():
    """Declared inside epistemikk, closed, and NOT in either required list.

    Additive is the point: no existing node must be changed for the atlas to
    validate, or the layer would be a rewrite disguised as a measurement.
    """
    epi = _epi(_bank())
    assert "verifisering" in epi["properties"], "the field is not declared"
    assert "verifisering" not in epi.get("required", []), (
        "the field stands in epistemikk.required — then it is not additive, "
        "and no existing node can stay unchanged")
    rn = _skjema()["$defs"]["RegimeNode"]
    assert "verifisering" not in rn.get("required", [])
    felt = epi["properties"]["verifisering"]
    assert felt.get("type") == "object"
    assert felt.get("additionalProperties") is False, (
        "the field's own object is not closed — C10 reports it as open")

    # C10's own answer, not my reading of the schema.
    aapne = efc_schema_check.open_schemas(_skjema())
    assert aapne == [], f"the schema has open subschemas: {aapne[:3]}"


def test_vokabularet_finnes_ett_sted_og_koden_er_likt_skjemaet():
    """One definition per word: the schema's enums and the checker's sets.

    Two definitions of one word is a measured failure class in this repo — the
    code's own predicate and the test's countable must not disagree.
    """
    felt = _epi(_bank())["properties"]["verifisering"]
    props = felt["properties"]
    assert tuple(props["tilstand"]["enum"]) == tuple(VERIFISERING_TILSTANDER)
    brudd = props["brudd"]["properties"]
    assert tuple(brudd["transformasjon"]["enum"]) == \
        tuple(VERIFISERING_TRANSFORMASJONER)
    assert tuple(brudd["aarsak"]["enum"]) == tuple(VERIFISERING_AARSAKER)
    assert felt["required"] == ["tilstand", "instrument"]
    assert props["brudd"]["required"] == ["transformasjon", "aarsak"]

    # The arbiter's metrics: the schema holds the CLOSED SHAPE, the checker
    # holds the LINE. The two must name the same five fields in the same
    # order, or the gate and the schema drift apart.
    metrikker = props["metrikker"]
    assert tuple(metrikker["properties"]) == tuple(VERIFISERING_METRIKKER)
    assert metrikker["required"] == list(VERIFISERING_METRIKKER)
    assert metrikker["additionalProperties"] is False, (
        "metrikker is not closed — C10 reports it as open")
    assert tuple(f for f, _, _ in VERIFISERING_ARBITER) == VERIFISERING_METRIKKER

    # The chain is named, in order, and the failure states are real positions
    # on it — not synonyms for each other.
    assert VERIFISERING_KJEDE[0] == "fit"
    assert VERIFISERING_KJEDE[-1] == "posterior_verifisert"
    for t in VERIFISERING_DOMMER + VERIFISERING_BRUDD:
        assert t in VERIFISERING_TILSTANDER, t
    assert "uavklart" in VERIFISERING_DOMMER, (
        "an unresolved cause still carries what was measured so far")
    assert "uavklart" not in VERIFISERING_BRUDD, (
        "requiring the arrow on an unresolved cause would force a guess")


@requires_jsonschema
def test_en_node_uten_feltet_validerer_fortsatt():
    """Additive, measured: a node stripped of the layer must still validate."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, SPARC_NODER[0]))
    node["epistemikk"].pop("verifisering", None)
    jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))


@requires_jsonschema
def test_skjemaet_avviser_en_oppdiktet_tilstand():
    """Closed vocabulary: a new state is a decision, not a word."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, SPARC_NODER[0]))
    node["epistemikk"]["verifisering"]["tilstand"] = "delvis_verifisert"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))


@requires_jsonschema
def test_skjemaet_avviser_metrikker_med_oppdiktet_felt():
    """metrikker is a closed object: an invented key is a decision, not a word."""
    s, bank = _skjema(), _bank()
    node = copy.deepcopy(_node(bank, SPARC_NODER[0]))
    node["epistemikk"]["verifisering"]["metrikker"] = {
        "r_hat": 1.005, "bulk_ess": 500, "tail_ess": 500,
        "divergenser": 0, "energy_bfmi": 0.5, "vibber": "gode"}
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(s).validate(_dok(bank, [node]))


# ---------------------------------------------------------------------------
# The bank: cleaned states, and a counted coverage
# ---------------------------------------------------------------------------

def test_hver_state_i_banken_er_ren():
    bank = _bank()
    problemer = sjekk_verifisering(bank)
    assert problemer == [], problemer


def test_dekningen_telles_og_aldri_antas():
    """How many nodes have taken a position is a MEASUREMENT, not a default.

    The layer is optional, so «0 nodes carry it» and «every node carries it»
    must not read alike. The first is a finding about the atlas; the second is
    a finding about the work. Pinning a floor here makes the empty case fail
    loudly instead of looking like a clean run.
    """
    bank = _bank()
    lagt = list(_lagt(bank))
    assert lagt, "no node carries the verification layer — the field exists but is empty, and the answer «0» then looks like knowledge"

    ids = {n["id"] for n, _ in lagt}
    for nid in SPARC_NODER + (FILTER_NODE,):
        assert nid in ids, (
            f"{nid} carries SPARC evidence and has not taken a position — the "
            f"nodes the layer was written for are the ones that must answer")
    assert len(ids) <= len(bank["nodes"])


def test_det_finnes_baade_fit_only_og_brutte_kjeder():
    """The distinction the card asks for must be REPRESENTED in the bank.

    If every positioned node had the same state, the layer would be a label
    rather than a measurement: fit-verified and posterior-attempted-and-failed
    would be indistinguishable again.
    """
    tilstander = {v["tilstand"] for _, v in _lagt(_bank())}
    assert "fit_only" in tilstander, "no node states that it is fit-only"
    assert tilstander & {"inferens_feil", "ikke_identifiserbar", "uavklart"}, (
        "no node states that a posterior was attempted and did not land")


def test_sparc_tallene_er_fit_verifisert_og_ikke_posterior_verifisert():
    """THE ACCEPTANCE: the SPARC result is fit-verified, not posterior-verified.

    Measured (K2, t_3f919915): the NUTS re-test of the same SPARC data delivered
    no posterior at all. The node must therefore NOT claim a verified posterior,
    must name the arrow that broke (`sampling`), and must carry the numbers the
    verdict was reached with — a verdict without them is an empty word.
    """
    bank = _bank()
    for nid in SPARC_NODER:
        v = _node(bank, nid)["epistemikk"]["verifisering"]
        assert v["tilstand"] != "posterior_verifisert", (
            f"{nid} claims a verified posterior — no such posterior exists")
        assert v["tilstand"] == "inferens_feil", v["tilstand"]
        assert v["brudd"]["transformasjon"] == "sampling", (
            f"{nid}: the arrow that broke is the sampling step")
        d = v["diagnostikk"]
        assert "R-hat" in d and "3.47" in d, (
            f"{nid}: the verdict does not carry the measured R-hat — the "
            f"diagnostics are what separates «did not converge» from «failed»")
        assert "ESS" in d and "divergences" in d, nid
        assert v["instrument"].strip(), nid


def test_en_fit_only_node_forteller_hvorfor_den_er_fit_only():
    """`fit_only` is a position, not a hole: it says which run does NOT cover it.

    The scope question is the whole difference between «verified» and «not yet
    looked at»: the NUTS run samples a per-galaxy curve and carries neither k
    nor g†, so for the screening model it is another model — not a weak
    verification of this one.
    """
    bank = _bank()
    v = _node(bank, FILTER_NODE)["epistemikk"]["verifisering"]
    assert v["tilstand"] == "fit_only", v["tilstand"]
    assert v["instrument"].strip()
    assert "k" in v["diagnostikk"] and "g\u2020" in v["diagnostikk"], (
        "the state does not name what the run would have needed to contain — "
        "then «fit_only» reads as «not looked at»")


def test_ingen_node_baerer_en_dom_uten_et_instrument():
    """A source per state: every positioned node names what produced it."""
    for n, v in _lagt(_bank()):
        assert isinstance(v.get("instrument"), str) and v["instrument"].strip(), n["id"]


# ---------------------------------------------------------------------------
# The checker: a state that cannot be false is not a state
# ---------------------------------------------------------------------------

def test_sjekkeren_svarer_ikke_alt_vel_paa_et_atlas_uten_noder():
    """A check that does not find the nodes must RAISE, not answer «clean»."""
    with pytest.raises(AtlasLesingFeil):
        sjekk_verifisering({"epistemikk": {}})


def test_posterior_verifisert_med_alle_metrikker_innenfor_linja_godtas():
    """The gate is a LINE, not a ban: a verdict that carries all five numbers
    within threshold must pass — otherwise `posterior_verifisert` could never
    be written, and the strongest word would be a dead end rather than a claim
    one can reach."""
    bank = _bank()

    def innenfor(v: dict) -> None:
        v["tilstand"] = "posterior_verifisert"
        v.pop("brudd", None)
        v["metrikker"] = {"r_hat": 1.005, "bulk_ess": 1200, "tail_ess": 900,
                          "divergenser": 0, "energy_bfmi": 0.6}

    assert sjekk_verifisering(_mutert(bank, SPARC_NODER[0], innenfor)) == [], (
        "a posterior_verifisert with all five metrics within the line was "
        "rejected — then the gate is a ban, not a line")


def _oppdiktet_tilstand(v: dict) -> None:
    v["tilstand"] = "delvis_verifisert"


def _uten_instrument(v: dict) -> None:
    v["instrument"] = "  "


def _dom_uten_diagnostikk(v: dict) -> None:
    v.pop("diagnostikk", None)


def _brudd_fjernet(v: dict) -> None:
    v.pop("brudd", None)


def _brudd_paa_en_hel_kjede(v: dict) -> None:
    v["tilstand"] = "fit_only"


def _ukjent_transformasjon(v: dict) -> None:
    v["brudd"]["transformasjon"] = "flaks"


def _gjetett_aarsak(v: dict) -> None:
    """An invented cause: not a candidate at all, so the vocabulary holds it."""
    v["brudd"]["aarsak"] = "maybe"


def _posterior_uten_metrikker(v: dict) -> None:
    """The strongest word without the arbiter's five numbers is a claim."""
    v["tilstand"] = "posterior_verifisert"
    v.pop("brudd", None)          # a verified chain cannot carry a break
    v.pop("metrikker", None)


def _posterior_med_metrikker_utenfor_linja(v: dict) -> None:
    """All five present, but R-hat 1.2 does not meet the arbiter's line."""
    v["tilstand"] = "posterior_verifisert"
    v.pop("brudd", None)
    v["metrikker"] = {"r_hat": 1.2, "bulk_ess": 500, "tail_ess": 500,
                      "divergenser": 0, "energy_bfmi": 0.5}


def _posterior_med_manglende_metrikk(v: dict) -> None:
    """One of the five numbers missing — the shape is closed, so it fails."""
    v["tilstand"] = "posterior_verifisert"
    v.pop("brudd", None)
    v["metrikker"] = {"r_hat": 1.005, "bulk_ess": 500, "tail_ess": 500,
                      "divergenser": 0}


MUTASJONER = [
    ("an invented state", _oppdiktet_tilstand, "closed"),
    ("a state without an instrument", _uten_instrument, "instrument"),
    ("a verdict without its diagnostics", _dom_uten_diagnostikk, "diagnostikk"),
    ("a failure without a break", _brudd_fjernet, "brudd"),
    ("a break on an unbroken chain", _brudd_paa_en_hel_kjede, "unbroken"),
    ("an unknown arrow", _ukjent_transformasjon, "transformasjon"),
    ("an invented cause", _gjetett_aarsak, "aarsak"),
    ("posterior_verifisert without the arbiter's numbers",
     _posterior_uten_metrikker, "metrikker"),
    ("posterior_verifisert with a metric outside the line",
     _posterior_med_metrikker_utenfor_linja, "r_hat"),
    ("posterior_verifisert with one metric missing",
     _posterior_med_manglende_metrikk, "energy_bfmi"),
]


@pytest.mark.parametrize("navn,endre,ord", MUTASJONER,
                         ids=[m[0] for m in MUTASJONER])
def test_hver_regel_feller_sin_mutant(navn, endre, ord):
    """The detector must be able to FAIL: each rule kills one mutant.

    False-positive rate, declared up front: the checker cannot see the run, so
    it flags FORM only — and the forms below are the ones that make a state lie
    about what was measured.
    """
    bank = _bank()
    problemer = sjekk_verifisering(_mutert(bank, SPARC_NODER[0], endre))
    assert problemer, f"mutation «{navn}» passed the checker"
    assert any(ord in p for p in problemer), (
        f"«{navn}» was caught, but not with a reason: {problemer}")


def test_mutasjonen_av_en_hel_kjede_blir_fanget_av_den_egentlige_regelen():
    """Order matters: the break rule is read on the MUTATED state, not the old.

    A mutant that flips the state to `fit_only` while the `brudd` stays behind
    must be caught by the break rule itself — otherwise the first rule that
    trips would hide whether the second one works.
    """
    bank = _bank()

    def flip(v: dict) -> None:
        v["tilstand"] = "fit_only"

    problemer = sjekk_verifisering(_mutert(bank, SPARC_NODER[0], flip))
    assert any("unbroken" in p for p in problemer), problemer


def test_grensen_er_navngitt_sjekkeren_ser_formen_og_ikke_kjoeringen():
    """A DECLARED LIMIT, pinned so it cannot be forgotten or papered over.

    The checker reads the vocabulary, not the run: a cause that IS one of the
    candidates (`trakt`, say) passes on form alone, even when the diagnostics
    never separated it from its neighbours. Only a discriminating measurement
    can tell a candidate asserted as a cause from one that was read, and that
    measurement lives in the run — not in the bank.

    The alternative was a keyword matcher over the diagnostics text. It is
    deliberately NOT built: this repo has already measured what a list of words
    that looks like an answer does — a similarity list that read as a placement
    proposal while being noise (the placement lookup, measured 2026-09-18). The
    limit is named here instead, and the test fails if anyone hides it by
    making the state un-readable.
    """
    bank = _bank()

    def bytt_kandidat(v: dict) -> None:
        v["brudd"]["aarsak"] = "trakt"

    assert sjekk_verifisering(_mutert(bank, SPARC_NODER[0], bytt_kandidat)) == [], (
        "the checker started separating candidates from measured causes — then "
        "this declared limit is stale and must be re-measured, not kept")
    # And the state that WAS measured stands, so the limit is about the
    # checker, not about the bank having given up on naming anything.
    v = _node(bank, SPARC_NODER[0])["epistemikk"]["verifisering"]
    assert v["brudd"]["aarsak"] == "diagnostikk_uavklart", (
        "the bank no longer states the unresolved cause the card measured")
