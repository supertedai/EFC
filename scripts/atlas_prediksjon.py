#!/usr/bin/env python3
"""The armed prediction: what EFC waits for, and how far away it is.

Measured 2026-09-19. The three layers were not connected: the bus carries a
SEALED blind prediction (frozen 2026-02-18, DOI + sha256), five baseline
measurements and a NAMED arbiter -- and no atlas node carried any of it.

Two nodes carry the loop, and the bridge names both:
  * the MEASUREMENT node (obs.fsigma8) -- where the observation arrives, and
    which correctly cannot be felled: it IS the measurement;
  * the CLAIM node (efc.growth_engine) -- where the settlement LANDS, carrying
    the falsifier that names the arbiter criterion verbatim.

The bus's own field names are DATA, in the snapshot's `bus_fields` map, so this
code carries no language of its own about them. The arithmetic is done HERE and
never trusted from the file: the first version of the snapshot carried
hand-written derived numbers and they were wrong (it said z=0.93 was the nearest
baseline; z=0.85 is 0.15 away, not 0.23, and the gap is -1.21 sigma, not -1.44).

    python3 scripts/atlas_prediksjon.py
    python3 scripts/atlas_prediksjon.py --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
BRO = ROT / "schema" / "efc_fs8.bro.json"
ATLAS = ROT / "schema" / "regime_nodes.jsonld"


def les_bro() -> dict:
    return json.loads(BRO.read_text(encoding="utf-8"))


def _bus(bro: dict) -> dict:
    return bro["bus_fields"]


def _maybe_json(v):
    """Bus headers carry nested payloads as JSON strings. Parse, never guess."""
    if isinstance(v, str) and v.strip().startswith(("{", "[")):
        return json.loads(v)
    return v


def expected(bro: dict) -> dict:
    return _maybe_json(bro["prediction"][_bus(bro)["expected"]])


def freeze(bro: dict) -> dict:
    return _maybe_json(bro["prediction"][_bus(bro)["freeze"]])


def avvik_sigma(baseline: dict, forventet: dict) -> float:
    """Distance from the prediction to a baseline, in that baseline's OWN sigma.

    The bus's tolerance rule is explicit: within 1 sigma of the measurement's
    own uncertainty, not a fixed band.
    """
    return (baseline["fsigma8"] - forventet["fsigma8_efc"]) / baseline["sigma"]


def naermeste(bro: dict) -> dict:
    """The baseline closest in redshift to the prediction's window."""
    z = expected(bro)["z_eff"]
    return min(bro["baselines"], key=lambda b: abs(b["z_eff"] - z))


def tilstand(bro: dict) -> dict:
    n, f = naermeste(bro), expected(bro)
    p = bro["prediction"]
    return {
        "correlation": bro["correlation"],
        "measurement_node": bro["atlas_node_measurement"],
        "claim_node": bro["atlas_node_claim"],
        "sealed_doi": p[_bus(bro)["sealed_doi"]],
        "sealed_sha256": p[_bus(bro)["sealed_sha256"]][:16] + "…",
        "frozen": freeze(bro)["primary_freeze"]["timestamp_utc"],
        "expected": f,
        "criterion": p[_bus(bro)["criterion"]],
        "arbiter": p[_bus(bro)["arbiter"]],
        "awaits": p[_bus(bro)["awaits"]],
        "settlements": bro["counts"]["oppgjoer"],
        "baselines": len(bro["baselines"]),
        "nearest": {k: n[k] for k in ("survey", "tracer", "z_eff", "fsigma8", "sigma")},
        "distance_z": round(abs(n["z_eff"] - f["z_eff"]), 3),
        "gap_sigma_efc": round(avvik_sigma(n, f), 2),
        "hole": bro["derived"]["hull"],
    }


def falsifier_fra_atlaset(bro: dict) -> str | None:
    """The claim node's falsifier, read from the bank -- the settlement's landing."""
    d = json.loads(ATLAS.read_text(encoding="utf-8"))
    node = next((n for n in d["nodes"] if n["id"] == bro["atlas_node_claim"]), None)
    if not node:
        return None
    f = node.get("ville_falsifisere")
    return f if isinstance(f, str) else json.dumps(f, ensure_ascii=False) if f else None


def main() -> None:
    p = argparse.ArgumentParser(description="A sealed prediction, from the bus")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    bro = les_bro()
    t = tilstand(bro)

    if a.json:
        print(json.dumps(t, ensure_ascii=False, indent=2))
        return

    print(f"THE PREDICTION — {t['correlation']}")
    print(f"  measurement node: {t['measurement_node']}   claim node: {t['claim_node']}\n")
    print(f"  sealed:      DOI {t['sealed_doi']}  sha256 {t['sealed_sha256']}")
    print(f"  frozen:      {t['frozen']}  (before the data — blind)")
    f = t["expected"]
    print(f"  expected:    fsigma8 = {f['fsigma8_efc']}  (LCDM {f['fsigma8_lcdm']}, "
          f"separation {f['separasjon_sigma']} sigma at z = {f['z_eff']})")
    print(f"  criterion:   {t['criterion']}")
    print(f"  arbiter:     {t['arbiter']}  —  awaits: {t['awaits']}")
    print(f"  settlements: {t['settlements']}  (correctly open: the arbiter does not exist)\n")
    print(f"BASELINES ({t['baselines']}) — each with its own seq and msg id:")
    for b in sorted(bro["baselines"], key=lambda x: x["z_eff"]):
        mark = " <- nearest" if (b["survey"], b["tracer"]) == (
            t["nearest"]["survey"], t["nearest"]["tracer"]) else ""
        print(f"  z={b['z_eff']:<6} {b['survey']:10} {b['tracer']:8} "
              f"fsigma8={b['fsigma8']:.3f} +- {b['sigma']:.3f}   seq {b['seq']}{mark}")
    print(f"\n  the nearest measurement is {t['distance_z']} away in z, and "
          f"{t['gap_sigma_efc']:+.2f} sigma from EFC's number.")
    land = falsifier_fra_atlaset(bro)
    print(f"\nTHE SETTLEMENT LANDS ON {t['claim_node']}, whose falsifier reads:")
    print(f"  {land}")
    print(f"\nHOLE: {t['hole']}")


if __name__ == "__main__":
    main()
