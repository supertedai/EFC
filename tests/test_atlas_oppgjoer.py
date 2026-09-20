"""The settlement path must be fail-closed: it may NOT close against a non-arbiter.

Measured 2026-09-19. The sealed fsigma8 prediction is armed on the bus with a
named arbiter and 0 settlements. The failure guarded against here is the one the
apparatus exists to prevent: computing a settlement against the wrong
measurement -- taking a non-arbiter as evidence.

Every test but the last is about REFUSAL. The last proves the loop is still
open, i.e. that nothing has settled it yet.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT / "scripts"))

import atlas_oppgjoer as O  # noqa: E402

ARB = ROT / "schema" / "efc_fs8.arbiter.json"
BRO = ROT / "schema" / "efc_fs8.bro.json"


@pytest.fixture(scope="module")
def arb() -> dict:
    return O.read(ARB)


@pytest.fixture(scope="module")
def bro() -> dict:
    return O.read(BRO)


def _candidate(**kw) -> dict:
    k = {"observable": "fsigma8", "survey": "DESI", "release": "DR2",
         "analysis": "full-shape", "fsigma8": 0.43, "fsigma8_sigma": 0.05,
         "z_eff": 0.7, "tracer": "LRG+ELG", "referanse": "DESI 2025 VI",
         "seq": 999, "Nats_Msg_Id": "efc-fs8.v1.DESI_DR2.LRG+ELG.0.7000.test"}
    k.update(kw)
    return k


def test_the_loop_is_armed_and_that_is_recorded(arb: dict) -> None:
    assert arb["state_now"]["arbiter_present"] is False
    assert arb["state_now"]["settlements"] == 0
    assert arb["state_now"]["armed_since"].startswith("2026-02-18")
    assert arb["state_now"]["why_open_is_correct"]


def test_a_measurement_outside_the_window_is_refused(arb: dict) -> None:
    """DESI DR1 at z=0.93 is a real measurement and NOT the arbiter."""
    fails = O.gate(_candidate(z_eff=0.93), arb)
    assert any("outside the window" in f for f in fails), fails


def test_a_measurement_without_provenance_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(seq=None, Nats_Msg_Id=None), arb)
    assert any("provenance" in f for f in fails), fails


def test_a_measurement_without_its_own_sigma_is_refused(arb: dict) -> None:
    """The tolerance is the measurement's OWN sigma. No sigma, no settlement."""
    fails = O.gate(_candidate(fsigma8_sigma=None), arb)
    assert any("OWN sigma" in f for f in fails), fails
    fails = O.gate(_candidate(fsigma8_sigma=0), arb)
    assert any("positive number" in f for f in fails), fails


def test_a_missing_required_field_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(referanse=None), arb)
    assert any("referanse" in f for f in fails), fails


def test_a_wrong_observable_is_refused(arb: dict) -> None:
    fails = O.gate(_candidate(observable="sigma8"), arb)
    assert any("observable is" in f for f in fails), fails


def test_the_verdict_uses_the_measurements_own_sigma(bro: dict, arb: dict) -> None:
    """A value ON the prediction is confirmed; a distant one is contradicted."""
    exp = O.expected(bro)
    assert O.verdict(_candidate(fsigma8=0.43, fsigma8_sigma=0.05), exp, arb) == {
        "gap_sigma": 0.0, "formula": "(fsigma8 - fsigma8_efc) / fsigma8_sigma",
        "tolerance_rule": arb["tolerance_rule"], "outcome": "confirmed",
        "compared_with": "DESI LRG+ELG"}
    assert O.verdict(_candidate(fsigma8=0.55, fsigma8_sigma=0.05),
                     exp, arb)["outcome"] == "contradicted"
    # the SAME 0.06 gap passes or fails depending on the measurement's own sigma
    assert O.verdict(_candidate(fsigma8=0.49, fsigma8_sigma=0.05),
                     exp, arb)["outcome"] == "contradicted"
    assert O.verdict(_candidate(fsigma8=0.49, fsigma8_sigma=0.10),
                     exp, arb)["outcome"] == "confirmed"


def test_the_landed_bank_has_no_settlement_yet(arb: dict) -> None:
    """If this fails, the loop was closed against something that is not the arbiter."""
    bank = O.read(O.ATLAS)
    node = next(n for n in bank["nodes"] if n["id"] == arb["claim_node"])
    assert "settlement_result" not in node, (
        f"{arb['claim_node']} already carries a settlement — measured against what?")


# ---------------------------------------------------------------------------
# The same question PER NODE (card t_2d7a6537)
#
# Measured 2026-09-20, before this was built: the four EFC engine nodes could
# neither be settled nor say why. Two carried `falsifiserbarhet:
# terskel_ikke_fastsatt` in a FRAGMENT (the criterion cut off mid-sentence),
# two carried `stub`. The thresholds existed all along — in the sealed
# cross-survey note (DOI 10.6084/m9.figshare.32045592) and in the sealed
# DH_over_rd contract (DOI 10.6084/m9.figshare.32013156) — so the defect was
# not missing knowledge, it was an unnamed arbiter.
#
# THE THREE NUMBERS MUST NOT COLLAPSE INTO ONE (the meter in
# `metrikk/atlasoppgjoer.py` measures the same three):
#
#     nodes pointing at a test 33   how many nodes POINT at a test
#     unique tests             30   how many DIFFERENT tests exist
#     settled                   2   how many are JUDGED
#
# And `hull` must be 0: a node that neither can be settled nor says why is a
# defect, not a third state.
# ---------------------------------------------------------------------------

FIRE_MOTORER = ("efc.rotation_engine", "efc.lensing_engine",
                "efc.cluster_engine", "efc.efc_background_engine")

#: The fields the card names, as they land in the mirrored (closed) bus form.
KONTRAKT_FELT = ("observable", "expected", "tolerance_rule",
                 "arbiter_waiting_for", "criteria")


def _bank_noder() -> dict:
    bank = O.read(O.ATLAS)
    return {n["id"]: n for n in bank["nodes"]}


def test_ingen_node_er_taus_om_den_kan_gjores_opp() -> None:
    """Every node answers: armed, judged, or a stated reason. `hull` is 0."""
    m = O.dom_banken(O.read(O.ATLAS))
    assert m["noder"] == 126
    assert m["hull"] == 0, (
        f"{m['hull']} node(s) neither carry a contract nor say why they "
        f"cannot be settled: {m['hull_noder']}")
    assert m["armer"] == 5 and m["gjort_opp"] == 3, (
        f"armer {m['armer']} / gjort opp {m['gjort_opp']} — a node moved "
        f"between the two; that is a decision someone must make")
    assert m["nekt_slag"] == {"instrument": 86, "prosa": 30, "status": 2}, (
        f"the reasons changed class: {m['nekt_slag']}")


def test_hver_av_de_fire_motorene_har_en_entydig_avgjorelse() -> None:
    """ARMER or NEKT — never «neither», and never without its reason."""
    noder = _bank_noder()
    ventet = {"efc.rotation_engine": "armer",
              "efc.efc_background_engine": "armer",
              "efc.lensing_engine": "nekt",
              "efc.cluster_engine": "nekt"}
    for nid, hva in ventet.items():
        d = O.dom(noder[nid])
        assert d["dom"] == hva, f"{nid}: {d}"
        assert len(d["grunn"]) >= 40, f"{nid}: the reason is a fragment: {d['grunn']!r}"
    for nid in ("efc.lensing_engine", "efc.cluster_engine"):
        node = noder[nid]
        assert node["falsifiserbarhet"]["status"] == "stub", (
            f"{nid}: a stub must not be given a threshold — it computes "
            f"nothing, and the schema says a stub shall not count as "
            f"satisfied falsifiability")
    # Two nodes, two DIFFERENT reasons — one sentence on four nodes is one case.
    tekster = {noder[i]["falsifiserbarhet"]["grunn"] for i in
               ("efc.lensing_engine", "efc.cluster_engine")}
    assert len(tekster) == 2, "the two stubs share one generic reason"


def test_den_armerte_kontrakten_navngir_arbiter_toleranse_og_dom() -> None:
    """All five fields, an EXTERNAL arbiter, and the house's own verdict words."""
    noder = _bank_noder()
    for nid in ("efc.rotation_engine", "efc.efc_background_engine"):
        node, p = noder[nid], noder[nid]["prediction"]
        assert O.kontrakt_mangler(node) == [], (
            f"{nid}: incomplete contract: {O.kontrakt_mangler(node)}")
        for f in KONTRAKT_FELT:
            assert str(p[f]).strip(), f"{nid}.prediction.{f} is empty"
        # An arbiter is an instrument or a dataset — never the node's own text.
        arb = p["arbiter_waiting_for"]
        assert len(arb) > 8 and arb != nid, f"{nid}: the arbiter is nameless"
        assert nid not in arb, (
            f"{nid}: the node names ITSELF as the arbiter — a node cannot "
            f"judge itself by reading its own prediction")
        # The settlement rule must be the house's vocabulary, and `uavgjort`
        # is only legal WITH `blokkert` (sak.py:499-509).
        regel = json.loads(p["criteria"])["settlement_rule"]
        assert "stemte" in regel and "avvek" in regel, f"{nid}: {regel}"
        assert "uavgjort" in regel and "blokkert" in regel, (
            f"{nid}: «uavgjort» stands without «blokkert» — {regel}")
        # The measurement's own uncertainty, never a band chosen in the node.
        assert "sigma" in p["tolerance_rule"], f"{nid}: {p['tolerance_rule']}"
        assert "not a fixed band" in p["tolerance_rule"] or \
            "not a band chosen in the node" in p["tolerance_rule"], (
            f"{nid}: the tolerance does not say why it is what it is")
        assert json.loads(p["expected"]), f"{nid}: expected is not JSON"


def test_bakgrunnsmotoren_baerer_samme_sak_som_obs_bao() -> None:
    """One case, two nodes: the key is SHARED, not a second case invented."""
    noder = _bank_noder()
    bg, bao = noder["efc.efc_background_engine"], noder["obs.bao"]
    assert bg["prediction"]["correlation"] == bao["prediction"]["correlation"]
    assert bg["prediction"]["expected"] == bao["prediction"]["expected"]
    assert bg["prediction"]["sealed_doi"] == bao["prediction"]["sealed_doi"]
    assert bg["settlement"]["correlation"] == bg["prediction"]["correlation"]


def test_ingen_node_ble_gjort_opp_av_kortet() -> None:
    """The card makes the case SETTLEABLE, not judged: the arbiter has not landed."""
    noder = _bank_noder()
    for nid in ("efc.rotation_engine", "efc.efc_background_engine"):
        node = noder[nid]
        assert "settlement_result" not in node, (
            f"{nid} carries a settlement — measured against what?")
        assert node["settlement"]["outcome"].startswith(O.VENTER_PREFIKS), (
            f"{nid}: {node['settlement']['outcome']!r}")
        assert node["settlement"]["outcome_source"] == "arbiter"


def test_de_tre_tallene_holder_seg_fra_hverandre() -> None:
    """Pointer ≠ unique test ≠ judged. The meter reads the same three."""
    noder = _bank_noder()
    kan = [n for n in noder.values() if n.get("ville_falsifisere")]
    unike = {n["ville_falsifisere"] for n in kan}
    assert len(kan) == 33, f"nodes pointing at a test: {len(kan)}"
    assert len(unike) == 30, f"unique tests: {len(unike)}"
    assert len(unike) < len(kan), (
        "the two numbers collapsed: nodes sharing a text are one claim")
    # The four motors must NOT carry one generic threshold.
    fire = [noder[i].get("ville_falsifisere", "") for i in FIRE_MOTORER]
    assert len({t for t in fire if t}) == 2, (
        "the two contracts must be two distinct claims, and the two stubs "
        "must carry none")


def test_en_taus_node_er_et_hull_og_ikke_et_svar() -> None:
    """The tool must not answer «all well» on a node that says nothing.

    Measured on a copy: strip every falsifiability answer AND the contract —
    then the node is a HOLE, and `dom_banken` must name it.
    """
    bank = O.read(O.ATLAS)
    maal = next(n for n in bank["nodes"]
                if n["id"] == "efc.rotation_engine")
    maal.pop("ville_falsifisere", None)
    maal.pop("prediction", None)
    maal.pop("settlement", None)
    maal.pop("falsifiserbarhet", None)
    maal["stipulasjoner"].pop("ikke_falsifiserbar_grunn", None)
    d = O.dom(maal)
    assert d["dom"] == "hull", d
    m = O.dom_banken(bank)
    assert m["hull"] == 1 and m["hull_noder"] == ["efc.rotation_engine"], m["hull_noder"]


MOTORENE = ("efc.rotation_engine", "efc.lensing_engine",
            "efc.cluster_engine", "efc.efc_background_engine")


def test_de_fire_motorene_navngir_sin_arbiter() -> None:
    """K4 (coverage-rule plan, t_c3930d65): a threshold shall name WHICH KIND
    of arbiter it binds to — an observation or a derivation.

    A threshold that does not name its kind cannot be placed in the counter
    that splits judged contracts on that axis (K1). All four bind to an
    OBSERVATION: a fit, a lensing measurement, cluster profiles, DESI DR2.
    """
    bank = O.read(O.ATLAS)
    noder = {n["id"]: n for n in bank["nodes"]}
    for i in MOTORENE:
        a = O.kontrakt_arbiter(noder[i])
        assert a["slag"] == "observasjon", (
            f"{i}: arbiter kind is {a['slag']!r} — expected observasjon, and it "
            f"shall be DECLARED, not left for the reader to infer")


def test_utledningen_som_ikke_er_navngitt_er_et_hull() -> None:
    """The background engine's SECOND obligation is a derivation, and it is
    NOT named: WHICH limiting case must reproduce LCDM is still open.

    Measured 2026-09-20: the coverage-rule plan predicted 3 observasjon + 1
    utledning among the four, reading the phrase «reproduce LCDM in one
    limit» from the base text. That phrase named the MISSING piece, not an
    arbiter. The piece is still missing — so it is pinned as a hole with a
    name, and not as a second arbiter.
    """
    bank = O.read(O.ATLAS)
    node = next(n for n in bank["nodes"]
                if n["id"] == "efc.efc_background_engine")
    c = json.loads(node["prediction"]["criteria"])
    assert c["arbiter_kind"] == "observasjon", c
    assert c["second_arbiter_kind"] == "utledning", c
    assert c["second_arbiter"] is None, (
        "a second arbiter was declared — then it must be NAMED, and the "
        "hole this test pins must be removed in the same change")
    assert "NOT named" in c["second_arbiter_note"], c
