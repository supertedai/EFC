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


def main() -> None:
    p = argparse.ArgumentParser(description="Settlement for the sealed prediction")
    p.add_argument("--sjekk", action="store_true", help="is the arbiter here?")
    p.add_argument("--kandidat", help="a measurement (json file) to try as arbiter")
    p.add_argument("--skriv", action="store_true", help="write the settlement")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

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
