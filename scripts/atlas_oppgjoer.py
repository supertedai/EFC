#!/usr/bin/env python3
"""The settlement path: close the loop when the arbiter lands, and NOT before.

Measured 2026-09-19. The sealed fsigma8 prediction sits armed on the bus with a
named arbiter (DESI DR2 full-shape, z~0.7) and 0 settlements -- correctly, because
no message on the bus has z ~ 0.7. The failure this guards against is the one the
whole apparatus exists to prevent: computing a settlement against the wrong
measurement, i.e. taking a non-arbiter as evidence.

So the path is FAIL-CLOSED.

    python3 scripts/atlas_oppgjoer.py --sjekk
        # is the arbiter here? -> prints the armed state, exit 0.
        # exit 3 when an arbiter candidate IS present.

    python3 scripts/atlas_oppgjoer.py --kandidat measurement.json
        # a candidate: checks every gate, computes the verdict, prints the block
        # that WOULD be written -- and writes nothing.

    python3 scripts/atlas_oppgjoer.py --kandidat measurement.json --skriv
        # writes the settlement into the claim node. Refuses unless the candidate
        # passes every gate (window, required fields, its own sigma, provenance).

A candidate must carry its own provenance (seq or Nats_Msg_Id) and its own
uncertainty: a number without a source is a claim, and a tolerance without the
measurement's own sigma is not the declared rule.

THE SAME QUESTION, PER NODE (measured 2026-09-20, card t_2d7a6537): the four
EFC engine nodes could neither be settled nor say why — two carried
`falsifiserbarhet: terskel_ikke_fastsatt` in a fragment, and every other engine
in the bank named its arbiter and its tolerance. The bank thus looked richer
than it was: `falsifikator_unike` counted 28 unique tests while the four
motors were silent about their own.

    python3 scripts/atlas_oppgjoer.py --sjekk --node efc.rotation_engine
        # ARMER — a complete contract, the arbiter named and not yet arrived (0)
        # NEKT  — the node says why it cannot be settled yet (2)
        # HULL  — neither: a defect, not a third state (4)

    python3 scripts/atlas_oppgjoer.py --alle
        # every node in the bank; exits 4 while any node is a hole — a silent
        # node is the ONE state that may not stand.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
BRO = ROT / "schema" / "efc_fs8.bro.json"
ARB = ROT / "schema" / "efc_fs8.arbiter.json"
ATLAS = ROT / "schema" / "regime_nodes.jsonld"

EXIT_ARMED = 0
EXIT_REFUSED = 2
EXIT_ARBITER_PRESENT = 3


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def expected(bro: dict) -> dict:
    """The prediction's expectation, nested in a bus header as a JSON string."""
    bus = bro["bus_fields"]
    v = bro["prediction"][bus["expected"]]
    return json.loads(v) if isinstance(v, str) else v


def gate(candidate: dict, arb: dict) -> list[str]:
    """Every gate a candidate must pass. Returns the FAILURES (empty = passed)."""
    fails: list[str] = []
    must = arb["must_arrive"]
    for felt in must["required_fields"]:
        if candidate.get(felt) in (None, ""):
            fails.append(f"missing field {felt!r}")
    if candidate.get("observable") and candidate["observable"] != must["observable"]:
        fails.append(f"observable is {candidate['observable']!r}, not {must['observable']!r}")
    lo, hi = must["z_window"]
    z = candidate.get("z_eff")
    if isinstance(z, (int, float)) and not (lo <= z <= hi):
        fails.append(
            f"z_eff = {z} is outside the window {must['z_window']} — the measurement "
            f"is for another window and cannot settle this prediction")
    if not candidate.get("seq") and not candidate.get("Nats_Msg_Id"):
        fails.append("no provenance: seq or Nats_Msg_Id is missing")
    s = candidate.get("fsigma8_sigma")
    if not isinstance(s, (int, float)) or s <= 0:
        fails.append("fsigma8_sigma must be a positive number — the tolerance is the "
                     "measurement's OWN sigma")
    return fails


def verdict(candidate: dict, exp: dict, arb: dict) -> dict:
    """The verdict, computed from the measurement's own sigma. Never a fixed band."""
    gap = (candidate["fsigma8"] - exp["fsigma8_efc"]) / candidate["fsigma8_sigma"]
    return {
        "gap_sigma": round(gap, 2),
        "formula": "(fsigma8 - fsigma8_efc) / fsigma8_sigma",
        "tolerance_rule": arb["tolerance_rule"],
        "outcome": "confirmed" if abs(gap) <= 1.0 else "contradicted",
        "compared_with": f"{candidate.get('survey', '?')} {candidate.get('tracer', '')}".strip(),
    }


EXIT_HOLE = 4

#: The five fields that make a node's case settleable — mapped onto the mirrored
#: bus form (`prediction` is CLOSED in the schema, so the card's names land here):
#:
#:   arbiter             -> prediction.arbiter_waiting_for
#:   expected_observable -> prediction.observable + prediction.expected
#:   tolerance           -> prediction.tolerance_rule
#:   maturity            -> prediction.arbiter_waiting_for (what must arrive first)
#:   settlement_rule     -> prediction.criteria
#:
#: `arbiter_waiting_for` therefore answers two of the five on purpose: in this
#: house the deadline IS «what must arrive before the case is ripe», and the
#: node may not name one without the other.
KONTRAKT_FELT = ("observable", "expected", "tolerance_rule",
                 "arbiter_waiting_for", "criteria")

#: The open settlement's own words. Measured on the three sealed contracts the
#: bank carried when this was written (`obs.fsigma8`, `obs.bao`,
#: `efc.growth_engine`): all three answer `waiting for arbiter: …`. A settlement
#: that does not say this has been WRITTEN — it is a judgement, not a wait.
VENTER_PREFIKS = "waiting for arbiter"


def kontrakt_mangler(node: dict) -> list[str]:
    """What a node's settlement contract is missing. Empty means complete.

    No field list is invented here: `prediction` is closed in the schema, so a
    field outside it would not validate. The correlation is the shared key —
    a settlement pointing at a DIFFERENT key belongs to another case.
    """
    p = node.get("prediction")
    if not isinstance(p, dict):
        return ["prediction"]
    mangler = [f for f in KONTRAKT_FELT if not str(p.get(f) or "").strip()]
    s = node.get("settlement")
    if not isinstance(s, dict):
        mangler.append("settlement")
    elif not mangler and str(s.get("correlation") or "") != str(
            p.get("correlation") or ""):
        mangler.append("settlement.correlation (does not match "
                       "prediction.correlation)")
    return mangler


def dom(node: dict) -> dict:
    """One node's verdict: is the case SETTLEABLE, or does the node say why not?

    Four answers, and each one is a measurement of the node — not a wish:

      armer     — a complete contract and an OPEN settlement: the arbiter is
                  named and has not arrived. The case can be settled the day it
                  lands, and only then.
      gjort_opp — the settlement carries a written outcome. Judged already.
      nekt      — no complete contract, and the node SAYS WHY: a falsifiability
                  status (`stub`, `terskel_ikke_fastsatt`) with a reason, an
                  instrument reason, or a falsifier that stands in prose only.
      hull      — neither. The node is SILENT about whether it can be felled,
                  and that is a defect, not a third state.
    """
    s = node.get("settlement") or {}
    utfall = str(s.get("outcome") or "").strip()
    if utfall and not utfall.startswith(VENTER_PREFIKS):
        return {"dom": "gjort_opp",
                "grunn": f"a settlement is written: {utfall[:100]}"}

    mangler = kontrakt_mangler(node)
    if not mangler:
        p = node["prediction"]
        return {"dom": "armer",
                "grunn": "the arbiter is named and has not arrived: "
                         f"{p['arbiter_waiting_for']}"}

    fb = node.get("falsifiserbarhet") or {}
    status = str(fb.get("status") or "").strip()
    grunn = str(fb.get("grunn") or "").strip()
    if status and grunn:
        return {"dom": "nekt", "slag": "status", "grunn": grunn,
                "mangler_av_kontrakt": mangler}
    if str((node.get("stipulasjoner") or {}).get(
            "ikke_falsifiserbar_grunn") or "").strip():
        return {"dom": "nekt", "slag": "instrument",
                "grunn": "the node declares why it cannot be felled: "
                         + str(node["stipulasjoner"]["ikke_falsifiserbar_grunn"]),
                "mangler_av_kontrakt": mangler}
    if str(node.get("ville_falsifisere") or "").strip():
        return {"dom": "nekt", "slag": "prosa",
                "grunn": "the falsifier stands in prose; no arbiter is named "
                         "in the contract form",
                "mangler_av_kontrakt": mangler}
    return {"dom": "hull",
            "grunn": "neither a settlement contract nor a stated reason — "
                     f"missing {', '.join(mangler)}",
            "mangler_av_kontrakt": mangler}


def dom_banken(bank: dict) -> dict:
    """Every node's verdict, and the counts. `hull` must be 0."""
    per: dict[str, dict] = {}
    telling = {"armer": 0, "gjort_opp": 0, "hull": 0}
    slag: dict[str, int] = {}
    for n in bank.get("nodes", []):
        d = dom(n)
        per[n["id"]] = d
        telling[d["dom"]] = telling.get(d["dom"], 0) + 1
        if d["dom"] == "nekt":
            slag[d.get("slag", "?")] = slag.get(d.get("slag", "?"), 0) + 1
    return {"noder": len(bank.get("nodes", [])), **telling,
            "nekt_slag": slag,
            "hull_noder": sorted(i for i, d in per.items() if d["dom"] == "hull"),
            "per_node": per}


def vis(dom_og_grunn: dict, node_id: str, p: dict) -> None:
    """One node's verdict as it will be read."""
    d = dom_og_grunn["dom"]
    print(f"{d.upper()} — {node_id}")
    if d == "armer":
        print(f"  correlation:  {p['correlation']}")
        print(f"  arbiter:      {p['arbiter_waiting_for']}")
        print(f"  observable:   {p['observable']}")
        print(f"  tolerance:    {p['tolerance_rule']}")
        print(f"  settlement:   {dom_og_grunn.get('grunn')}")
        print(f"  written by:   {p.get('basis', '—')}")
    else:
        print(f"  grunn:        {dom_og_grunn['grunn']}")


def hoved(app) -> int:
    """The per-node path: `--sjekk --node <id>`, or `--alle`."""
    bank = read(ATLAS)
    noder = {n["id"]: n for n in bank.get("nodes", [])}

    if app.alle:
        m = dom_banken(bank)
        if app.json:
            print(json.dumps({k: v for k, v in m.items()
                              if k != "per_node"}, ensure_ascii=False, indent=2))
        else:
            print(f"The bank: {m['noder']} nodes")
            print(f"  armer:      {m['armer']}  (a complete contract, the "
                  f"arbiter named and absent)")
            print(f"  gjort opp:  {m['gjort_opp']}  (a settlement is written)")
            print(f"  nekt:       {m['nekt']}  " + ", ".join(
                f"{k}: {v}" for k, v in sorted(m["nekt_slag"].items())))
            print(f"  hull:       {m['hull']}")
            if m["hull_noder"]:
                print("\nHOLE — a node that neither can be settled nor says "
                      "why (that is a defect, not a third state):")
                for i in m["hull_noder"]:
                    print(f"  {i}: {m['per_node'][i]['grunn']}")
                return EXIT_HOLE
        return EXIT_HOLE if m["hull"] else EXIT_ARMED

    ukjente = [i for i in app.node if i not in noder]
    if ukjente:
        print(f"REFUSED — not in the bank: {', '.join(ukjente)}")
        return EXIT_REFUSED

    siste = EXIT_ARMED
    for i in app.node:
        node = noder[i]
        d = dom(node)
        if d["dom"] == "hull":
            siste = EXIT_HOLE
        elif d["dom"] == "nekt":
            siste = max(siste, EXIT_REFUSED)
        if app.json:
            print(json.dumps({"node": i, **{k: v for k, v in d.items()},
                              "prediction": node.get("prediction"),
                              "settlement": node.get("settlement")},
                             ensure_ascii=False, indent=2))
        else:
            vis(d, i, node.get("prediction") or {})
            print()
    return siste


def main() -> None:
    p = argparse.ArgumentParser(description="Settlement for the sealed prediction")
    p.add_argument("--sjekk", action="store_true", help="is the arbiter here?")
    p.add_argument("--kandidat", help="a measurement (json file) to try as arbiter")
    p.add_argument("--skriv", action="store_true", help="write the settlement")
    p.add_argument("--node", action="append", default=[],
                   help="ask ONE node in the bank: armer / nekt / hull "
                        "(repeatable)")
    p.add_argument("--alle", action="store_true",
                   help="ask every node in the bank; exit 4 on any hole")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    if a.node or a.alle:
        raise SystemExit(hoved(a))

    bro, arb = read(BRO), read(ARB)
    exp = expected(bro)

    if not a.kandidat:
        st = arb["state_now"]
        if a.json:
            print(json.dumps(st, ensure_ascii=False, indent=2))
            return
        print(f"ARMED — {arb['correlation']}")
        print(f"  sealed since:   {st['armed_since']}  (blind, before the data)")
        m = arb["must_arrive"]
        print(f"  waiting for:    {m['survey']} {m['release']} {m['analysis']} "
              f"fsigma8 at z ~ {m['z_target']}")
        print(f"  expected topic: {arb['expected_topic']}")
        print(f"  settlements:    {st['settlements']}  (correctly open)")
        n = st["nearest_existing"]
        print(f"  nearest today:  {n['survey']} {n['tracer']} z={n['z_eff']} "
              f"({n['distance_z']} away)")
        print(f"\n  why open is correct: {st['why_open_is_correct']}")
        raise SystemExit(EXIT_ARMED)

    candidate = read(Path(a.kandidat))
    fails = gate(candidate, arb)
    if fails:
        print("REFUSED — the candidate is not the arbiter:")
        for x in fails:
            print(f"  - {x}")
        raise SystemExit(EXIT_REFUSED)

    v = verdict(candidate, exp, arb)
    block = {
        "correlation": bro["correlation"],
        "node": arb["claim_node"],
        "outcome": v["outcome"],
        "gap_sigma": v["gap_sigma"],
        "measured_against": v["compared_with"],
        "z_eff": candidate["z_eff"],
        "provenance": {"seq": candidate.get("seq"),
                       "Nats_Msg_Id": candidate.get("Nats_Msg_Id"),
                       "reference": candidate.get("referanse")},
        "criterion": arb["must_arrive"]["why"],
    }
    if a.json:
        print(json.dumps({"verdict": v, "block": block}, ensure_ascii=False, indent=2))
    else:
        print(f"THE ARBITER IS HERE — {v['compared_with']}")
        print(f"  measured:   fsigma8 = {candidate['fsigma8']} +- {candidate['fsigma8_sigma']} "
              f"at z = {candidate['z_eff']}")
        print(f"  expected:   {exp['fsigma8_efc']}  (gap {v['gap_sigma']:+.2f} sigma)")
        print(f"  tolerance:  {v['tolerance_rule']}")
        print(f"  VERDICT:    {v['outcome'].upper()}")

    if not a.skriv:
        print("\nNothing written (use --skriv). The block that WOULD be written:")
        print(json.dumps(block, ensure_ascii=False, indent=2))
        return

    bank = read(ATLAS)
    node = next((n for n in bank["nodes"] if n["id"] == arb["claim_node"]), None)
    if node is None:
        print(f"REFUSED — {arb['claim_node']} is not in the bank")
        raise SystemExit(EXIT_REFUSED)
    node.setdefault("settlement_result", {})
    node["settlement_result"].update(block)
    ATLAS.write_text(json.dumps(bank, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nWROTE {arb['claim_node']}.settlement_result — "
          f"{v['outcome']} at {v['gap_sigma']:+.2f} sigma.")


if __name__ == "__main__":
    main()
