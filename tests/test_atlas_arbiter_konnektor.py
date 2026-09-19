"""The arbiter connector: it publishes the measurement when it exists, and nothing before.

Measured 2026-09-19 (base 1d3842c5). The settlement path (PR #588) refuses to
close against anything but the declared arbiter and proves it with tests that all
describe REFUSAL. What none of them could prove is the other half: that the
measurement reaches the subject when it arrives. A gate that never fires and a
connector that never publishes look identical from the bank.

So the tests below are three things at once:

  * the ARMED state — 0 messages on the settlement subject, nothing published,
    with the reason written down (the acceptance's own guard against closing the
    loop early);
  * the WINDOW — a measurement at z = 0.85 (the real eBOSS DR16 ELG baseline) and
    one at z = 0.55 both belong to the baseline feed. 0.55 is the discriminating
    case: it is INSIDE the arbiter module's own z window [0.5, 0.9], so a
    connector that carried that window instead of the declaration's [0.6, 0.8]
    would publish it as the arbiter;
  * the COUPLING — the message the connector would publish is fed to the
    settlement path's own gate, to the guard that already reads the bus
    (RapidResponseVakt), and (once, in a copy of the tree) through the one call
    that closes the loop. Nothing here re-implements a rule the other side owns.

The declaration is bound to the arbiter's own lists in both directions, because
two copies of the same rule is how the two halves drift apart — the failure
tests/test_arbiter_emne_kontrakt.py was written about.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROT))
sys.path.insert(0, str(ROT / "scripts"))
sys.path.insert(0, str(ROT / "scripts" / "maintenance"))

import atlas_arbiter_konnektor as K  # noqa: E402
import atlas_oppgjoer as O  # noqa: E402
import arbiter_vakt_kjoer as V  # noqa: E402
from efc_inference.arbiter.rapid_response import RapidResponseVakt  # noqa: E402
from efc_inference.arbiter.sealed_fs8 import (  # noqa: E402
    ANKER_EFC,
    TILLATTE_TRACERE,
    Z_MAKS,
    Z_MIN,
)

ARB = ROT / "schema" / "efc_fs8.arbiter.json"
BRO = ROT / "schema" / "efc_fs8.bro.json"


@pytest.fixture(scope="module")
def arb() -> dict:
    return K.declaration()


@pytest.fixture(scope="module")
def bro() -> dict:
    return K.bridge()


def _maaling(**kw) -> dict:
    """The declared arbiter, field for field — as a candidate, not as a claim."""
    k = {"observable": "fsigma8", "survey": "DESI", "release": "DR2",
         "analysis": "full-shape", "fsigma8": 0.430, "fsigma8_sigma": 0.030,
         "z_eff": 0.7, "tracer": "LRG", "referanse": "DESI 2025 VI",
         "seq": 99001, "Nats_Msg_Id": "efc-fs8.v1.DESI_DR2.LRG.0.7000.test",
         "kilde": "desi-dr2-full-shape"}
    k.update(kw)
    return k


def _buss(**kw) -> dict:
    """The same measurement in the shape the bus carries it (fixture shape)."""
    m = _maaling(**kw)
    return {"hoder": {"observabel": m["observable"], "survey": m["survey"],
                      "tracer": m["tracer"], "referanse": m["referanse"],
                      "release": m["release"], "analysis": m["analysis"],
                      "kilde": m["kilde"], "seq": m["seq"],
                      "Nats-Msg-Id": m["Nats_Msg_Id"]},
            "maalt": {"fsigma8": m["fsigma8"],
                      "fsigma8_sigma": m["fsigma8_sigma"],
                      "z_eff": m["z_eff"]}}


# ---------------------------------------------------------------------------
# The declaration is the only copy of the rules
# ---------------------------------------------------------------------------
def test_the_subject_is_the_declarations_own(arb: dict) -> None:
    """Read, not restated: the declaration names the subject this connector
    publishes on, and the lag word is the one the streams capture."""
    assert K.subject(arb) == arb["expected_topic"] == "kosmos.kosmologi.oppgjoer.efc-fs8"
    # The lag word is the token the streams match on (docs/nats-koblingskart.md;
    # measured in tests/test_arbiter_emne_kontrakt.py). The arbiter-VERDICT
    # subject already lives on the same token, so the token is a measured fact and
    # not an assumption about this one.
    lag = K.subject(arb).split(".")[2]
    assert lag == V.OPPGJOER_EMNE.split(".")[2] == "oppgjoer"


def test_the_two_oppgjoer_subjects_are_two_feeds(arb: dict) -> None:
    """The MEASUREMENT and the VERDICT are not the same subject, and NATS would
    not deliver one to a reader of the other: `efc-fs8-arbiter` is its own token."""
    assert K.subject(arb) != V.OPPGJOER_EMNE
    assert K.subject(arb).split(".")[:3] == V.OPPGJOER_EMNE.split(".")[:3]
    assert [e for e in K.subject(arb).split(".") if e.startswith("efc-fs8")] == ["efc-fs8"]


def test_the_window_is_the_declarations_and_inside_the_arbiters_own(arb: dict) -> None:
    """Two windows exist, and they are not the same size.

    The declaration says [0.6, 0.8]; the arbiter module's own guard says
    [0.5, 0.9]. The connector and the settlement path both read the
    DECLARATION'S — a measurement the declaration calls a baseline may not be
    published as the arbiter merely because the guard's window is wider. The
    relationship that must hold is containment, so a future widening of the
    declaration past the arbiter's own window fails here.
    """
    lo, hi = K.window(arb)
    assert (lo, hi) == (0.6, 0.8)
    assert Z_MIN <= lo and hi <= Z_MAKS, (
        f"the declaration's window {K.window(arb)} is not inside the arbiter's own "
        f"[{Z_MIN}, {Z_MAKS}] — the connector could then publish a measurement the "
        "arbiter calls out of window")


def test_the_declaration_and_the_arbiter_agree_on_the_tracers(arb: dict) -> None:
    """One list, two readers. The connector reads the declaration's copy."""
    assert set(K.tracers(arb)) == set(TILLATTE_TRACERE) == {"LRG", "ELG"}


def test_the_bus_expectation_is_the_sealed_anchor(arb: dict, bro: dict) -> None:
    """The settlement computes its gap against the bus's number; the arbiter
    judges against the sealed anchor. If those two ever part, the loop lands on
    the wrong reference and every test on either side still passes."""
    assert O.expected(bro)["fsigma8_efc"] == ANKER_EFC == 0.430


# ---------------------------------------------------------------------------
# The armed state: nothing is published, and the reason is written down
# ---------------------------------------------------------------------------
def test_the_settlement_subject_carries_no_message_today(arb: dict) -> None:
    """The acceptance's first bullet, measured — not asserted from prose."""
    snap = K.snapshot()
    assert K.measured_on(K.subject(arb), snap) == 0
    assert K.measured_on(K.baseline_subject(K.bridge()), snap) == 12


def test_nothing_is_published_when_the_arbiter_does_not_exist(tmp_path) -> None:
    sendt = []
    record = K.run([], transport=lambda e, p: sendt.append((e, p)) or "ok",
                   do_publish=True, flat_out=str(tmp_path / "flat.json"))
    assert sendt == []
    assert record["published"] == []
    assert record["counts"] == {"arbiter": 0, "baseline": 0, "refused": 0}
    assert record["decision"] == "armed"
    assert "the arbiter does not exist" in record["reason"]
    assert record["subject_measured_messages"] == 0
    assert record["flat_candidate"] is None
    assert not (tmp_path / "flat.json").exists()


def test_the_log_says_why_a_run_published_nothing(tmp_path) -> None:
    """The connector's own log is the only trace of a run that sends nothing."""
    logg = tmp_path / "logg.jsonl"
    K.append_log(K.run([], transport=None, do_publish=False), logg)
    K.append_log(K.run([_maaling(z_eff=0.85)], transport=None, do_publish=False), logg)
    linjer = [json.loads(x) for x in logg.read_text(encoding="utf-8").splitlines()]
    assert len(linjer) == 2
    assert linjer[0]["decision"] == "armed" and linjer[0]["reason"]
    assert linjer[1]["decision"] == "nothing_published" and linjer[1]["reason"]
    assert linjer[1]["counts"]["baseline"] == 1
    for linje in linjer:
        assert linje["subject"] == "kosmos.kosmologi.oppgjoer.efc-fs8"
        assert linje["published"] == []


# ---------------------------------------------------------------------------
# The window, enforced in the connector too
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("z", [0.85, 1.317, 0.55])
def test_a_measurement_outside_the_window_is_a_baseline(arb: dict, z: float) -> None:
    """z = 0.85 is the real eBOSS DR16 ELG baseline; z = 0.55 is inside the
    arbiter module's own [0.5, 0.9] and outside the declaration's, which is the
    case that separates the two windows."""
    dom = K.classify(_maaling(z_eff=z), arb)
    assert dom["route"] == "baseline", dom["reasons"]
    assert any("outside the declared window" in r for r in dom["reasons"])


def test_a_baseline_is_never_published_on_the_settlement_subject(arb: dict, bro: dict) -> None:
    sendt = []
    record = K.run([_maaling(z_eff=0.85)],
                   transport=lambda e, p: sendt.append((e, p)) or "ok", do_publish=True)
    assert record["counts"]["baseline"] == 1
    assert record["published"] == [{"subject": K.baseline_subject(bro), "status": "ok"}]
    emne, payload = sendt[0]
    assert emne == bro["topics"]["tilstand"]
    assert emne != K.subject(arb)
    melding = json.loads(payload)
    # The bus's own word for "this is not the arbiter" — the field the guard
    # checks before it judges anything.
    assert melding["hoder"]["arbiter"] == "nei"
    assert V.RapidResponseVakt().gjenkjenn(melding) is None


def test_another_survey_is_routed_to_the_baseline_feed(arb: dict) -> None:
    """A connector that fills the subject with another survey's number is worse
    than an empty subject. eBOSS DR16 at z = 0.7 is still not the arbiter."""
    dom = K.classify(_maaling(survey="eBOSS DR16", release="DR16"), arb)
    assert dom["route"] == "baseline", dom["reasons"]
    assert any("survey is" in r for r in dom["reasons"])


def test_another_release_is_not_the_arbiter(arb: dict) -> None:
    """DESI DR1 LRG+ELG at z = 0.7 — same survey, same window, wrong release."""
    dom = K.classify(_maaling(release="DR1", tracer="LRG+ELG"), arb)
    assert dom["route"] == "baseline", dom["reasons"]
    assert any("release is" in r for r in dom["reasons"])


def test_a_lya_tracer_is_not_the_arbiter(arb: dict) -> None:
    """The published DR2 Lya full-shape measurement cannot fell this criterion,
    so putting it on the subject would be publishing a number its own arbiter
    returns VENTER on."""
    dom = K.classify(_maaling(tracer="Lya", z_eff=0.7), arb)
    assert dom["route"] == "baseline", dom["reasons"]
    assert any("galaxy-RSD" in r for r in dom["reasons"])


# ---------------------------------------------------------------------------
# What is not a measurement at all: refused, and nothing is published anywhere
# ---------------------------------------------------------------------------
def test_no_provenance_no_publication(arb: dict) -> None:
    sendt = []
    record = K.run([_maaling(seq=None, Nats_Msg_Id=None)],
                   transport=lambda e, p: sendt.append((e, p)) or "ok", do_publish=True)
    assert sendt == []
    assert record["counts"]["refused"] == 1
    assert any("provenance" in r for r in record["candidates"][0]["reasons"])
    assert record["decision"] == "nothing_published"


def test_no_own_sigma_no_publication(arb: dict) -> None:
    """The tolerance is the measurement's OWN sigma (the declaration's rule)."""
    for sigma in (None, 0, -0.1, "0.05"):
        dom = K.classify(_maaling(fsigma8_sigma=sigma), arb)
        assert dom["route"] == "refused", (sigma, dom["reasons"])
        assert any("OWN sigma" in r or "cannot be read" in r for r in dom["reasons"])


def test_a_candidate_missing_a_required_field_is_refused(arb: dict) -> None:
    dom = K.classify(_maaling(referanse=None), arb)
    assert dom["route"] == "refused"
    assert any("referanse" in r for r in dom["reasons"])


def test_a_candidate_that_is_not_an_object_is_refused(arb: dict) -> None:
    for kandidat in ([], "0.43", 0.43, {}, {"hoder": {}, "maalt": {}}):
        assert K.classify(kandidat, arb)["route"] == "refused"


# ---------------------------------------------------------------------------
# The arbiter route: publish, and the published message must pass every gate
# ---------------------------------------------------------------------------
def test_the_arbiter_is_published_on_the_declared_subject(arb: dict) -> None:
    sendt = []
    record = K.run([_maaling()],
                   transport=lambda e, p: sendt.append((e, p)) or "ok", do_publish=True)
    assert record["counts"]["arbiter"] == 1
    assert len(sendt) == 1
    emne, payload = sendt[0]
    assert emne == arb["expected_topic"]
    melding = json.loads(payload)

    # Every field the declaration requires, on the flattened form the settlement
    # path reads — so the two layers cannot disagree about where a field lives.
    flat = K.flat(melding)
    for felt in arb["must_arrive"]["required_fields"]:
        assert flat.get(felt) not in (None, ""), felt

    # Provenance is carried, never invented: it is the source message's own.
    assert flat["seq"] == 99001
    assert flat["Nats_Msg_Id"] == "efc-fs8.v1.DESI_DR2.LRG.0.7000.test"
    assert flat["referanse"] == "DESI 2025 VI"
    assert melding["hoder"]["survey"] == "DESI DR2"
    assert melding["hoder"]["tracer"] == "LRG"
    assert melding["hoder"]["arbiter"] == "ja"


def test_the_published_message_passes_the_settlement_paths_own_gate(arb: dict) -> None:
    """One gate, one implementation: the connector refuses what the settlement
    path would refuse, because it asks the settlement path."""
    melding = K.message(K.classify(_maaling(), arb)["candidate"], "arbiter", arb, K.bridge())
    assert O.gate(K.flat(melding), arb) == []


def test_a_message_that_would_lose_a_declared_field_is_not_published(monkeypatch) -> None:
    """The required fields are checked on the message that would go OUT, not
    only on the candidate that came in: the two are built by different code, and
    a field lost between them would be invisible to every reader of the subject."""
    ekte = K.message

    def uten_referanse(candidate, route, arb, bro):
        melding = ekte(candidate, route, arb, bro)
        melding["hoder"].pop("referanse")
        return melding

    monkeypatch.setattr(K, "message", uten_referanse)
    sendt = []
    record = K.run([_maaling()], transport=lambda e, p: sendt.append((e, p)) or "ok",
                   do_publish=True)
    assert sendt == []
    assert record["counts"]["arbiter"] == 0 and record["counts"]["refused"] == 1
    assert any("referanse" in r for r in record["candidates"][0]["reasons"])


def test_the_published_message_is_judged_by_the_guard_that_reads_the_bus(arb: dict) -> None:
    """Producer and consumer are bound to each other in both directions: the
    guard must recognise THIS message as the arbiter measurement (and must not
    recognise the baseline-route one, tested above)."""
    melding = K.message(K.classify(_maaling(), arb)["candidate"], "arbiter", arb, K.bridge())
    gjenkjent = RapidResponseVakt().gjenkjenn(melding)
    assert gjenkjent == {"fsigma8": 0.430, "sigma": 0.030, "z_eff": 0.7,
                         "tracer": "LRG", "kilde": "desi-dr2-full-shape"}


def test_a_bus_shaped_candidate_is_read_as_well_as_a_flat_one(arb: dict) -> None:
    dom = K.classify(_buss(), arb)
    assert dom["route"] == "arbiter", dom["reasons"]
    assert dom["candidate"]["Nats_Msg_Id"] == "efc-fs8.v1.DESI_DR2.LRG.0.7000.test"


def test_a_message_the_declaration_cannot_place_is_not_built() -> None:
    """The subject must be <root>.<domain>.<layer>.<source>: the message derives
    its own layers from it, so a subject of another shape is a refusal to build,
    not a message with guessed layers."""
    arb = dict(K.declaration())
    arb["expected_topic"] = "kosmos.kosmologi.oppgjoer.efc-fs8.extra"
    with pytest.raises(K.CouldNotMeasure):
        K.message(K.classify(_maaling(), arb)["candidate"], "arbiter", arb, K.bridge())


# ---------------------------------------------------------------------------
# The transport: dry by default, and the publisher is the house's own
# ---------------------------------------------------------------------------
def test_nothing_is_sent_without_the_publish_flag(monkeypatch) -> None:
    monkeypatch.setenv("NATS_PRODUSENT", "nats://user:pw@nats.example.org:4222")
    record = K.run([_maaling()], transport=K.publiser_best_effort, do_publish=False)
    assert record["published"] == []
    assert record["candidates"][0]["status"] == "dry run — nothing was sent"


def test_publishing_without_a_transport_says_so(monkeypatch) -> None:
    record = K.run([_maaling()], transport=None, do_publish=True)
    assert record["published"] == []
    assert "no transport attached" in record["candidates"][0]["status"]
    assert record["decision"] == "arbiter_here_nothing_sent"


def test_the_transport_is_the_house_publisher(monkeypatch) -> None:
    """One publisher in this house: the connector's transport IS
    arbiter_vakt_kjoer's, so the two cannot drift into two protocols. Measured by
    the status the shared publisher returns when no credential is in the
    environment — the same input, the same string."""
    monkeypatch.delenv("NATS_PRODUSENT", raising=False)
    emne = K.subject(K.declaration())
    assert (K.publiser_best_effort(emne, "{}")
            == V.publiser_best_effort(emne, "{}")
            == "ingen produsent-legitimasjon (NATS_PRODUSENT mangler)")


def test_a_crashing_transport_does_not_lose_the_record(tmp_path) -> None:
    """The publication is best-effort; the routing record is not (L-016: a
    transport that throws must not take the artefact with it)."""
    def krasjer(emne, payload):
        raise RuntimeError("nettet falt ut")

    logg = tmp_path / "logg.jsonl"
    record = K.run([_maaling()], transport=krasjer, do_publish=True,
                   log_path=logg)
    assert record["counts"]["arbiter"] == 1
    assert "publish failed: nettet falt ut" in record["candidates"][0]["status"]
    assert record["published"] == [{"subject": K.subject(K.declaration()),
                                    "status": "publish failed: nettet falt ut"}]
    assert record["decision"] == "arbiter_here_nothing_sent"
    K.append_log(record, logg)
    assert json.loads(logg.read_text(encoding="utf-8"))["counts"]["arbiter"] == 1


# ---------------------------------------------------------------------------
# One call closes the loop — measured in a copy, never in this bank
# ---------------------------------------------------------------------------
def test_the_flat_candidate_closes_the_loop_in_one_call(tmp_path, arb: dict) -> None:
    """The acceptance, end to end and in a COPY of the tree.

    The connector publishes, writes the flat candidate the settlement path reads,
    and one call lands the settlement on efc.growth_engine. Run in a copy so the
    landed bank in this repository is not closed by a test: the last assertion is
    the acceptance's own — the real bank still carries no settlement.
    """
    rot = tmp_path / "rot"
    (rot / "schema").mkdir(parents=True)
    (rot / "scripts").mkdir()
    for fil in ("efc_fs8.arbiter.json", "efc_fs8.bro.json", "regime_nodes.jsonld"):
        shutil.copy(ROT / "schema" / fil, rot / "schema" / fil)
    shutil.copy(ROT / "scripts" / "atlas_oppgjoer.py", rot / "scripts" / "atlas_oppgjoer.py")

    sendt = []
    flat = tmp_path / "maaling.flat.json"
    record = K.run([_maaling()], transport=lambda e, p: sendt.append(e) or "ok",
                   do_publish=True, flat_out=str(flat),
                   arb=K.read_json(rot / "schema" / "efc_fs8.arbiter.json"),
                   bro=K.read_json(rot / "schema" / "efc_fs8.bro.json"))
    assert sendt == [arb["expected_topic"]]
    assert json.loads(flat.read_text(encoding="utf-8"))["fsigma8"] == 0.430
    assert record["settlement_command"] == K.settlement_command(flat)

    r = subprocess.run([sys.executable, "scripts/atlas_oppgjoer.py",
                        "--kandidat", str(flat), "--skriv"],
                       cwd=rot, capture_output=True, text=True)
    assert r.returncode == 0, (r.returncode, r.stdout, r.stderr)
    assert "WROTE efc.growth_engine.settlement_result" in r.stdout
    assert "CONFIRMED" in r.stdout

    bank = json.loads((rot / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
    node = next(n for n in bank["nodes"] if n["id"] == arb["claim_node"])
    land = node["settlement_result"]
    assert land["outcome"] == "confirmed" and land["gap_sigma"] == 0.0
    assert land["provenance"]["seq"] == 99001
    assert land["provenance"]["reference"] == "DESI 2025 VI"
    assert land["measured_against"] == "DESI LRG"

    # The acceptance's guard: the landed bank in THIS repository is untouched.
    ekte = json.loads((ROT / "schema" / "regime_nodes.jsonld").read_text(encoding="utf-8"))
    ekte_node = next(n for n in ekte["nodes"] if n["id"] == arb["claim_node"])
    assert "settlement_result" not in ekte_node


# ---------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------
def test_the_cli_is_armed_and_writes_its_log(tmp_path) -> None:
    logg = tmp_path / "logg.jsonl"
    assert K.main(["--sjekk", "--logg", str(logg)]) == K.EXIT_SUBJECT_STAYS_EMPTY
    linje = json.loads(logg.read_text(encoding="utf-8").splitlines()[0])
    assert linje["decision"] == "armed" and linje["published"] == []


def test_the_cli_reports_the_arbiter_with_exit_3(tmp_path) -> None:
    kandidat = tmp_path / "k.json"
    kandidat.write_text(json.dumps(_maaling()), encoding="utf-8")
    assert K.main(["--kandidat", str(kandidat), "--logg",
                   str(tmp_path / "logg.jsonl")]) == K.EXIT_ARBITER_HERE


def test_the_cli_could_not_measure_is_exit_2(tmp_path) -> None:
    broken = tmp_path / "k.json"
    broken.write_text("{broken json", encoding="utf-8")
    assert K.main(["--kandidat", str(broken), "--logg",
                   str(tmp_path / "logg.jsonl")]) == K.EXIT_COULD_NOT_MEASURE


def test_the_cli_classifies_a_baseline_with_exit_0(tmp_path) -> None:
    kandidat = tmp_path / "k.json"
    kandidat.write_text(json.dumps(_maaling(z_eff=0.85, survey="eBOSS DR16")),
                        encoding="utf-8")
    logg = tmp_path / "logg.jsonl"
    assert K.main(["--kandidat", str(kandidat), "--logg", str(logg)]) == 0
    linje = json.loads(logg.read_text(encoding="utf-8").splitlines()[0])
    assert linje["counts"]["baseline"] == 1
    assert linje["subject_measured_messages"] == 0


# ---------------------------------------------------------------------------
# The map external readers use
# ---------------------------------------------------------------------------
def test_the_documentation_names_the_subject(arb: dict) -> None:
    """docs/nats-koblingskart.md is the contract external readers use, and the
    card that built this connector names the subject. A subject that is published
    on and documented nowhere is one nobody can subscribe to."""
    kart = (ROT / "docs" / "nats-koblingskart.md").read_text(encoding="utf-8")
    assert arb["expected_topic"] in kart
    assert "atlas_arbiter_konnektor.py" in kart
