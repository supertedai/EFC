#!/usr/bin/env python3
"""The arbiter connector: publish the measurement when it exists, and nothing before.

Measured 2026-09-19 (card t_8e217b72, base 1d3842c5). The settlement path
(scripts/atlas_oppgjoer.py, PR #588) is fail-closed and says so in its own words:
with no message at z ~ 0.7 on the bus, an open settlement is the correct state —
settling against a baseline would be taking a non-arbiter as evidence
(schema/efc_fs8.arbiter.json:state_now.why_open_is_correct).

But a refusal is not a connector. NOTHING published the measurement when it
lands, so the arbiter could sit on the bus and never reach the subject the
declaration names: the loop would stay open with its arbiter in hand.

This is that connector, and it is fail-closed the same way:

  * NOTHING is published on the declaration's subject unless the candidate IS the
    declared arbiter — DESI DR2 full-shape, observable fsigma8, a galaxy-RSD
    tracer, z inside the declaration's own window, provenance (seq or
    Nats_Msg_Id), the measurement's OWN sigma, and the reference;
  * the settlement path's own gate is run on the very candidate that would be
    published. scripts/atlas_oppgjoer.py is the arbiter of its gates and is not
    re-implemented here: if it would refuse, this connector refuses;
  * a well-formed measurement that is NOT the arbiter is routed, not dropped: its
    declared home is the baseline feed (kosmos.kosmologi.tilstand.efc-fs8, see
    schema/efc_fs8.bro.json:topics.tilstand), where the twelve existing baselines
    live — and it is marked `arbiter: "nei"` so the guard that already reads the
    bus cannot mistake it for one;
  * a candidate that is not a measurement at all (no fields, no provenance, no
    sigma) is refused, publishes nowhere, and the run log says why.

Why the strictness: a connector that fills the subject with ANOTHER survey's
number is worse than an empty subject. The whole apparatus exists to prevent
taking a non-arbiter as evidence, and a connector is the one place where that
mistake would be invisible — it would look exactly like the arbiter arriving.

Subject, window, required fields and tracers are READ, never restated
(schema/efc_fs8.arbiter.json: expected_topic, must_arrive.{z_window,
required_fields, survey, release, analysis, tracers}). There is no second copy of
any of those rules here, so the connector cannot drift from the declaration it
serves. tests/test_atlas_arbiter_konnektor.py binds the declaration to the
arbiter's own lists (efc_inference/arbiter/sealed_fs8.py) for the same reason.

Two subjects carry one correlation, and they are not the same feed:

    kosmos.kosmologi.oppgjoer.efc-fs8           the MEASUREMENT — this connector
    kosmos.kosmologi.oppgjoer.efc-fs8-arbiter   the VERDICT     — arbiter_vakt_kjoer.py

NATS matches a subject token by token, so the second is not a refinement of the
first: `efc-fs8-arbiter` is its own token. Both lag words are `oppgjoer`, which is
the token VERDEN_PROGNOSE captures. An uncaptured lag word is the silent failure
measured 2026-09-17 (tests/test_arbiter_emne_kontrakt.py): the server answers +OK
and the message is gone with no error and no log.

The repo never reads the bus itself (docs/nats-koblingskart.md, "Leserens
grenser"). So does this connector: the measurement arrives as a file, the
producer credential comes from the environment (NATS_PRODUSENT, via the shared
best-effort publisher in scripts/maintenance/arbiter_vakt_kjoer.py) and never
from a file in this repository.

Usage:

    python3 scripts/atlas_arbiter_konnektor.py --sjekk
        # is the arbiter here? prints the armed state, exit 0.
        # exit 3 when a candidate IS the arbiter.

    python3 scripts/atlas_arbiter_konnektor.py --kandidat maaling.json
        # classifies the candidate, prints the message that WOULD be published
        # and the one command that closes the loop — and publishes nothing.

    python3 scripts/atlas_arbiter_konnektor.py --kandidat maaling.json \\
        --publiser --kandidat-ut maaling.flat.json
        # publishes, and writes the flat candidate the settlement path reads:
        #     python3 scripts/atlas_oppgjoer.py --kandidat maaling.flat.json --skriv

Exit codes: 0 = the settlement subject stays empty; 2 = could not measure
(declaration, snapshot or candidate unreadable); 3 = the arbiter is here.
"""
from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Callable, Iterable, Optional

ROT = Path(__file__).resolve().parents[1]
ARB = ROT / "schema" / "efc_fs8.arbiter.json"
BRO = ROT / "schema" / "efc_fs8.bro.json"
SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
LOGG = ROT / "logs" / "atlas-arbiter-konnektor.jsonl"

sys.path.insert(0, str(ROT / "scripts"))
import atlas_oppgjoer as oppgjoer  # noqa: E402  the settlement path's own gate

EXIT_SUBJECT_STAYS_EMPTY = 0
EXIT_COULD_NOT_MEASURE = 2
EXIT_ARBITER_HERE = 3

# The declaration names the window and the fields; this tuple names the fields
# that say WHICH instrument a measurement came from. They are not in
# required_fields because a baseline needs no release to be readable — but the
# arbiter is DESI DR2 full-shape and nothing else, so the connector may not
# publish without them.
IDENTITY_FIELDS = ("survey", "release", "analysis")

PUBLISHED_OK = "ok"


class CouldNotMeasure(Exception):
    """The connector could not read what it must read to answer at all."""


# ---------------------------------------------------------------------------
# What the declaration and the bridge say — read, always, never restated
# ---------------------------------------------------------------------------
def read_json(path) -> dict:
    try:
        d = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CouldNotMeasure(f"{path}: {exc}") from exc
    if not isinstance(d, dict):
        raise CouldNotMeasure(f"{path}: expected an object, found {type(d).__name__}")
    return d


def declaration() -> dict:
    return read_json(ARB)


def bridge() -> dict:
    return read_json(BRO)


def snapshot() -> dict:
    return read_json(SNAPSHOT)


def subject(arb: dict) -> str:
    """The settlement subject, as the declaration names it."""
    return arb["expected_topic"]


def baseline_subject(bro: dict) -> str:
    """Where a measurement that is NOT the arbiter belongs."""
    return bro["topics"]["tilstand"]


def window(arb: dict) -> tuple:
    lo, hi = arb["must_arrive"]["z_window"]
    return (lo, hi)


def required_fields(arb: dict) -> list:
    return list(arb["must_arrive"]["required_fields"])


def tracers(arb: dict) -> list:
    """The tracers that count. The rule is the sealed arbiter's own membership
    test (efc_inference/arbiter/sealed_fs8.py:TILLATTE_TRACERE, galakse-RSD); the
    declaration carries it so the connector does not need a second copy."""
    return [str(t).upper() for t in arb["must_arrive"]["tracers"]]


def measured_on(topic: str, snap: dict) -> int:
    """How many messages the snapshot names on this subject.

    The count is a MEASUREMENT (schema/nats_domener.snapshot.json), not this
    connector's opinion, and the snapshot is not the bus: it is the last reading.
    A subject carrying nothing is absent from `emner` — that is a measured zero,
    not a missing answer.
    """
    ledd = topic.split(".")
    if len(ledd) < 3:
        raise CouldNotMeasure(f"{topic!r} is not a bus subject")
    domene = ".".join(ledd[:2])
    emne = ".".join(ledd[2:])
    return int(snap.get("domener", {}).get(domene, {}).get("emner", {}).get(emne, 0))


def snapshot_provenance(snap: dict) -> dict:
    p = snap.get("_proveniens")
    return p if isinstance(p, dict) else {}


# ---------------------------------------------------------------------------
# The candidate: one flattener, so the two layers cannot disagree
# ---------------------------------------------------------------------------
def flat(kandidat: dict) -> dict:
    """A candidate in the settlement path's own form.

    The bus nests its values in `hoder`/`maalt` (tests/fixtures/nats-*.json); the
    settlement path reads ONE flat dict (scripts/atlas_oppgjoer.py:gate). The
    bridge between the two forms lives here and nowhere else, so a field cannot
    be present in one layer and missing in the other because two readers
    disagreed about where it lives.

    Provenance is spelled `Nats_Msg_Id` by the settlement path's required fields
    and `Nats-Msg-Id` by the bus header; both spellings are the same fact, and
    both are accepted on the way in.
    """
    ut: dict = {}
    for nokkel, verdi in (kandidat or {}).items():
        if nokkel in ("hoder", "maalt") and isinstance(verdi, dict):
            ut.update(verdi)
        else:
            ut[nokkel] = verdi
    if ut.get("Nats-Msg-Id") is not None and ut.get("Nats_Msg_Id") is None:
        ut["Nats_Msg_Id"] = ut["Nats-Msg-Id"]
    if ut.get("observabel") is not None and ut.get("observable") is None:
        ut["observable"] = ut["observabel"]
    if ut.get("sigma") is not None and ut.get("fsigma8_sigma") is None:
        ut["fsigma8_sigma"] = ut["sigma"]
    return ut


def _tall(v) -> bool:
    """A number, and not a bool wearing a number's clothes."""
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def _norm(v) -> str:
    """`full-shape`, `full shape` and `fullshape` are the same analysis."""
    return "".join(str(v).split()).replace("-", "").replace("_", "").lower()


# ---------------------------------------------------------------------------
# The routing decision — three routes, and no fourth
# ---------------------------------------------------------------------------
def classify(kandidat, arb: dict) -> dict:
    """Where a candidate belongs, and why it is not the arbiter if it is not.

        arbiter    the declared measurement: publish on expected_topic
        baseline   a well-formed measurement of the same observable that is NOT
                   it (another window, release, analysis or tracer): its declared
                   home is the baseline feed, never this subject
        refused    not a measurement at all (no fields, no provenance, no sigma):
                   publish nowhere. A number without these is a claim.

    The window is checked LAST so that a candidate which is both malformed and
    out of window is refused for the honest reason (it is not a measurement),
    not routed as a baseline it cannot be.
    """
    if not isinstance(kandidat, dict):
        return {"route": "refused", "candidate": {},
                "reasons": ["a candidate must be an object"]}
    c = flat(kandidat)
    if not c:
        return {"route": "refused", "candidate": {},
                "reasons": ["the candidate carries no fields"]}

    must = arb["must_arrive"]
    refusals: list[str] = []
    for felt in required_fields(arb):
        if c.get(felt) in (None, ""):
            refusals.append(
                f"missing required field {felt!r}: the declaration names it in "
                "must_arrive.required_fields, and a value without it cannot be read")
    for felt in IDENTITY_FIELDS:
        if c.get(felt) in (None, ""):
            refusals.append(
                f"missing identity field {felt!r}: the arbiter is "
                f"{must['survey']} {must['release']} {must['analysis']}")
    if c.get("observable") not in (None, must["observable"]):
        refusals.append(
            f"observable is {c['observable']!r}, not {must['observable']!r}")
    if not (c.get("seq") or c.get("Nats_Msg_Id")):
        refusals.append(
            "no provenance: neither seq nor Nats_Msg_Id — a number without a "
            "source is a claim, not a measurement")
    sigma = c.get("fsigma8_sigma")
    if not _tall(sigma) or sigma <= 0:
        refusals.append(
            f"fsigma8_sigma is {sigma!r}: the tolerance is the measurement's OWN "
            "sigma (the declaration's rule), so a positive number is required")
    if not _tall(c.get("z_eff")):
        refusals.append(
            f"z_eff is {c.get('z_eff')!r}, not a number — the window cannot be "
            "checked and the candidate cannot be routed")
    if refusals:
        return {"route": "refused", "candidate": c, "reasons": refusals}

    # Well-formed from here: it IS a measurement of the observable. Is it THE one?
    not_the_arbiter: list[str] = []
    survey = str(c["survey"]).lower()
    if must["survey"].lower() not in survey:
        not_the_arbiter.append(
            f"survey is {c['survey']!r}, not {must['survey']!r} "
            f"({must['release']} {must['analysis']})")
    if _norm(c["release"]) != _norm(must["release"]):
        not_the_arbiter.append(
            f"release is {c['release']!r}, not {must['release']!r}")
    if _norm(c["analysis"]) != _norm(must["analysis"]):
        not_the_arbiter.append(
            f"analysis is {c['analysis']!r}, not {must['analysis']!r}")
    tracer = str(c["tracer"]).upper()
    if tracer not in tracers(arb):
        not_the_arbiter.append(
            f"tracer is {c['tracer']!r}, not galaxy-RSD "
            f"({'/'.join(tracers(arb))}) — the sealed arbiter rejects it too, so "
            "publishing it here would put a number on the subject that its own "
            "arbiter cannot judge")

    lo, hi = float(window(arb)[0]), float(window(arb)[1])
    z = float(c["z_eff"])
    if not (lo <= z <= hi):
        not_the_arbiter.append(
            f"z_eff = {z} is outside the declared window [{lo}, {hi}] — the "
            "measurement is for another window, so it is a baseline and its home "
            "is the baseline feed")

    if not_the_arbiter:
        return {"route": "baseline", "candidate": c, "reasons": not_the_arbiter}

    # It claims to be the arbiter. The settlement path's gate has the last word:
    # one gate, one implementation, so the two halves cannot drift apart.
    settlement_fails = oppgjoer.gate(c, arb)
    if settlement_fails:
        return {"route": "refused", "candidate": c, "reasons": [
            "the settlement path would refuse this candidate, so the connector "
            f"refuses it too: {f}" for f in settlement_fails]}

    return {"route": "arbiter", "candidate": c,
            "reasons": [f"every gate passed: {must['survey']} {must['release']} "
                        f"{must['analysis']} {must['observable']} at z = {z} "
                        f"({c['tracer']}), z inside [{lo}, {hi}]"]}


# ---------------------------------------------------------------------------
# The bus message — the fields the declaration requires, plus its provenance
# ---------------------------------------------------------------------------
def message(candidate: dict, route: str, arb: dict, bro: dict) -> dict:
    """The message for a route, in the shape the bus already carries.

    `hoder`/`maalt` is the shape in tests/fixtures/nats-*.json and the shape
    efc_inference/arbiter/rapid_response.py reads, so this feed needs no second
    reader — and the baseline route writes `arbiter: "nei"`, which is the field
    that guard checks before it judges anything.

    Provenance is CARRIED, never invented: `seq` and `Nats_Msg_Id` are the source
    message's own identifiers, and they are what ties this publication back to a
    measurement. The outgoing message's own server id is not ours to write.
    """
    topic = subject(arb) if route == "arbiter" else baseline_subject(bro)
    ledd = topic.split(".")
    if len(ledd) != 4:
        raise CouldNotMeasure(
            f"{topic!r} is not <root>.<domain>.<layer>.<source> "
            "(docs/nats-koblingskart.md) — the layers cannot be derived from it")
    rot, domene, lag, undertype = ledd
    must = arb["must_arrive"]
    survey = str(candidate["survey"])
    release = str(candidate["release"])
    # The bus writes a survey and its release as one string ("DESI DR2") and the
    # guard that reads this feed requires BOTH tokens in `survey`
    # (efc_inference/arbiter/rapid_response.py:gjenkjenn). Join only when the
    # release is not already in the string, so a candidate that already names it
    # is carried verbatim instead of doubled.
    if _norm(release) not in _norm(survey):
        survey = f"{survey} {release}"
    return {
        "hoder": {
            "rot": rot, "domene": domene, "lag": lag, "undertype": undertype,
            "observabel": must["observable"],
            "survey": survey,
            "release": release,
            "analysis": candidate["analysis"],
            "tracer": candidate["tracer"],
            "referanse": candidate["referanse"],
            "arbiter": "ja" if route == "arbiter" else "nei",
            "korrelasjon": bro["correlation"],
            "kriterium": must["why"],
            "seq": candidate.get("seq"),
            "Nats_Msg_Id": candidate.get("Nats_Msg_Id"),
            "kilde": candidate.get("kilde", ""),
        },
        "maalt": {felt: candidate[felt]
                  for felt in ("fsigma8", "fsigma8_sigma", "z_eff")},
    }


def settlement_command(flat_path) -> str:
    """The ONE call that closes the loop, once the measurement exists."""
    return f"python3 scripts/atlas_oppgjoer.py --kandidat {flat_path} --skriv"


# ---------------------------------------------------------------------------
# The transport — one publisher in this house, reused and not copied
# ---------------------------------------------------------------------------
def publiser_best_effort(emne: str, payload: str) -> str:
    """Publish via NATS_PRODUSENT, best-effort, never crashing.

    The publisher is arbiter_vakt_kjoer.py's, imported lazily: one transport in
    this house means the two publishers cannot drift into two protocols. The
    import is lazy because that module pulls the arbiter (numpy) in, and a dry run
    — the normal run today — needs nothing but the standard library.
    """
    sys.path.insert(0, str(ROT / "scripts" / "maintenance"))
    import arbiter_vakt_kjoer  # noqa: PLC0415  (lazy: keeps dry runs stdlib-only)

    return arbiter_vakt_kjoer.publiser_best_effort(emne, payload)


# ---------------------------------------------------------------------------
# The run
# ---------------------------------------------------------------------------
def run(candidates: Iterable, transport: Optional[Callable[[str, str], str]] = None,
        do_publish: bool = False, flat_out=None, arb: Optional[dict] = None,
        bro: Optional[dict] = None, snap: Optional[dict] = None,
        now: Optional[str] = None, log_path=None) -> dict:
    """Classify every candidate, publish what may be published, log the rest.

    Returns the run record: what was routed where, why, and what was sent. The
    record is the connector's own log — it is written whether or not anything was
    published, because "nothing was published, and here is why" is the answer on
    every run until the arbiter exists.
    """
    arb = arb if arb is not None else declaration()
    bro = bro if bro is not None else bridge()
    snap = snap if snap is not None else snapshot()
    kandidater = list(candidates or [])

    emne = subject(arb)
    elementer: list[dict] = []
    sendinger: list[dict] = []
    for nr, kandidat in enumerate(kandidater, 1):
        dom = classify(kandidat, arb)
        element = {"nr": nr, "route": dom["route"], "reasons": dom["reasons"],
                   "candidate": dom["candidate"]}
        if dom["route"] != "refused":
            element["subject"] = (emne if dom["route"] == "arbiter"
                                  else baseline_subject(bro))
            element["message"] = message(dom["candidate"], dom["route"], arb, bro)
            # The declaration's required fields are checked on the message that
            # would actually go out — not only on the candidate that came in. The
            # two are built by different code, and a field lost between them is
            # exactly the failure a reader would never see: a message on the
            # subject that cannot be read as the measurement.
            mangler = [f for f in required_fields(arb)
                       if flat(element["message"]).get(f) in (None, "")]
            if mangler:
                element["route"] = "refused"
                element["reasons"] = [
                    f"the message would go out without the declared field {f!r} "
                    "— nothing is published" for f in mangler]
                for nokkel in ("subject", "message", "status"):
                    element.pop(nokkel, None)
                elementer.append(element)
                continue
            if not do_publish:
                element["status"] = "dry run — nothing was sent"
            elif transport is None:
                element["status"] = "no transport attached — nothing was sent"
            else:
                try:
                    element["status"] = transport(
                        element["subject"],
                        json.dumps(element["message"], ensure_ascii=False))
                except Exception as exc:  # noqa: BLE001  a transport may throw
                    # The house rule for this publisher (arbiter_vakt_kjoer.py,
                    # L-016): a transport that throws must not take the record
                    # with it. The routing and the reason are the deliverable of
                    # a run that could not send, so they are never lost.
                    element["status"] = f"publish failed: {exc}"
                sendinger.append({"subject": element["subject"],
                                  "status": element["status"]})
        elementer.append(element)

    telling = {rute: sum(1 for e in elementer if e["route"] == rute)
               for rute in ("arbiter", "baseline", "refused")}
    n_emnet = measured_on(emne, snap)

    flat_sti = None
    if flat_out and telling["arbiter"]:
        forste = next(e for e in elementer if e["route"] == "arbiter")
        sti = Path(flat_out)
        sti.parent.mkdir(parents=True, exist_ok=True)
        sti.write_text(json.dumps(forste["candidate"], ensure_ascii=False, indent=2)
                       + "\n", encoding="utf-8")
        flat_sti = str(sti)

    ok = [s for s in sendinger if s["status"] == PUBLISHED_OK]
    if not kandidater:
        beslutning, grunn = "armed", (
            f"no candidate was handed in and the snapshot names {n_emnet} message(s) "
            f"on {emne}: the arbiter does not exist, so nothing is published. "
            "The open settlement is the correct state — "
            + str(arb["state_now"]["why_open_is_correct"]))
    elif telling["arbiter"] and ok:
        beslutning, grunn = "published", (
            f"the arbiter is here: {len(ok)} message(s) published, "
            f"{telling['arbiter']} candidate(s) passed every gate")
    elif telling["arbiter"]:
        beslutning, grunn = "arbiter_here_nothing_sent", (
            f"a candidate IS the arbiter but nothing was sent "
            f"({sendinger[0]['status'] if sendinger else 'dry run'})")
    elif telling["baseline"]:
        beslutning, grunn = "nothing_published", (
            f"{telling['baseline']} candidate(s) are measurements but not the "
            f"arbiter; their home is {baseline_subject(bro)}, and nothing belongs "
            f"on {emne}")
    else:
        beslutning, grunn = "nothing_published", (
            f"{telling['refused']} candidate(s) are not measurements at all "
            "(no fields, no provenance or no sigma); nothing is published anywhere")

    if flat_sti and telling["arbiter"] > 1:
        grunn += (f" NB: {telling['arbiter']} arbiter candidates were handed in and "
                  f"the settlement file holds the first — the others are counted "
                  "here, not silently dropped.")

    return {
        "time": now or datetime.datetime.now(
            datetime.timezone.utc).isoformat(timespec="seconds"),
        "subject": emne,
        "baseline_subject": baseline_subject(bro),
        "window": list(window(arb)),
        "tracers": tracers(arb),
        "required_fields": required_fields(arb),
        "decision": beslutning,
        "reason": grunn,
        "counts": telling,
        "candidates": elementer,
        "published": sendinger,
        "subject_measured_messages": n_emnet,
        "snapshot": {"measured": snapshot_provenance(snap).get("maalt"),
                     "source": "schema/nats_domener.snapshot.json"},
        "settlement_command": settlement_command(flat_sti) if flat_sti else None,
        "flat_candidate": flat_sti,
        "log": str(log_path or LOGG),
    }


def append_log(record: dict, path) -> None:
    """Append the run record. One line per run, so the reason survives the run."""
    sti = Path(path)
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_candidates(stier: Iterable[str]) -> list:
    """Read candidates from files. A file may hold one object or a list of them."""
    ut: list = []
    for sti in stier:
        d = read_json(sti)
        if isinstance(d.get("kandidater"), list):
            ut.extend(d["kandidater"])
        else:
            ut.append(d)
    return ut


# ---------------------------------------------------------------------------
# The command line
# ---------------------------------------------------------------------------
def skriv_tilstand(arb: dict, bro: dict, snap: dict, out=print) -> None:
    """The armed state, from the declaration and the snapshot — not from prose."""
    emne = subject(arb)
    st = arb["state_now"]
    must = arb["must_arrive"]
    n = measured_on(emne, snap)
    prov = snapshot_provenance(snap)
    out(f"THE ARBITER CONNECTOR — {arb['correlation']}")
    out(f"  settlement subject:  {emne}")
    out(f"  baseline feed:       {baseline_subject(bro)}")
    out(f"  the arbiter:         {must['survey']} {must['release']} "
        f"{must['analysis']} {must['observable']} at z ~ {must['z_target']}")
    out(f"  window:              z in {must['z_window']}  "
        "(the declaration's own, and the binding one)")
    out(f"  tracers:             {'/'.join(tracers(arb))}")
    out(f"  required fields:     {', '.join(required_fields(arb))}")
    out(f"  measured on subject: {n} message(s)  "
        f"(schema/nats_domener.snapshot.json, measured {prov.get('maalt', '?')})")
    out(f"  armed since:         {st['armed_since']}  (sealed before the data)")
    naermest = st["nearest_existing"]
    out(f"  nearest today:       {naermest['survey']} {naermest['tracer']} "
        f"z={naermest['z_eff']} ({naermest['distance_z']} away) — outside the "
        "window, so it is a baseline")
    out("")
    out("Nothing is published, and that is the correct state:")
    out(f"  {st['why_open_is_correct']}")


def main(argv: Optional[list] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish the arbiter measurement when it exists — and not before.")
    parser.add_argument("--sjekk", action="store_true",
                        help="print the armed state")
    parser.add_argument("--kandidat", action="append", default=[],
                        help="a measurement (json file); repeat for more")
    parser.add_argument("--publiser", action="store_true",
                        help="publish (without it, nothing is ever sent)")
    parser.add_argument("--kandidat-ut", default=None,
                        help="write the settlement path's flat candidate here")
    parser.add_argument("--logg", default=str(LOGG), help="append the run record here")
    parser.add_argument("--json", action="store_true")
    a = parser.parse_args(argv)

    try:
        arb = declaration()
        bro = bridge()
        snap = snapshot()
        kandidater = load_candidates(a.kandidat)
    except CouldNotMeasure as exc:
        print(f"COULD NOT MEASURE — {exc}")
        return EXIT_COULD_NOT_MEASURE

    try:
        record = run(kandidater, transport=publiser_best_effort if a.publiser else None,
                     do_publish=a.publiser, flat_out=a.kandidat_ut, arb=arb, bro=bro,
                     snap=snap, log_path=a.logg)
    except CouldNotMeasure as exc:
        print(f"COULD NOT MEASURE — {exc}")
        return EXIT_COULD_NOT_MEASURE

    append_log(record, a.logg)

    if a.json:
        print(json.dumps(record, ensure_ascii=False, indent=2))
    else:
        if a.sjekk or not kandidater:
            skriv_tilstand(arb, bro, snap)
            print()
        for e in record["candidates"]:
            print(f"CANDIDATE {e['nr']} — route: {e['route']}   subject: "
                  f"{e.get('subject', '— none, it is not a measurement')}")
            for grunn in e["reasons"]:
                print(f"  - {grunn}")
            print(f"  status: {e.get('status', 'nothing to send')}")
            if e["route"] != "refused":
                print("  the message:")
                print(json.dumps(e["message"], ensure_ascii=False, indent=2))
        print(f"\nDECISION: {record['decision']}")
        print(f"  {record['reason']}")
        if record["flat_candidate"]:
            print(f"\n  flat candidate written to {record['flat_candidate']}")
            print(f"  close the loop with one call: {record['settlement_command']}")
        print(f"  log: {record['log']}")

    return EXIT_ARBITER_HERE if record["counts"]["arbiter"] else EXIT_SUBJECT_STAYS_EMPTY


if __name__ == "__main__":
    raise SystemExit(main())
