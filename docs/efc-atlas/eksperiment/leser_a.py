"""System A: the current atlas reader, with no evidence-layer semantics."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

_RELATION_FILE = "schema/regime_nodes.jsonld"


def _nodes(bank: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {node["id"]: node for node in bank.get("nodes", []) if "id" in node}


def _relations(bank: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in bank.get("relations", []) if isinstance(r, dict)]


def _relations_between(bank: dict[str, Any], subject: str | None = None,
                       predicate: str | None = None, object_: str | None = None) -> list[dict[str, Any]]:
    return [r for r in _relations(bank)
            if (subject is None or r.get("subject") == subject)
            and (predicate is None or r.get("predicate") == predicate)
            and (object_ is None or r.get("object") == object_)]


def _answer(qid: str, value: Any, field: str, certainty: str = "hoy") -> dict[str, Any]:
    return {"id": qid, "svar": value, "grunnlag": f"{_RELATION_FILE}:{field}",
            "sikkerhet": certainty, "avstaar": False}


def _abstain(qid: str, field: str = "") -> dict[str, Any]:
    return {"id": qid, "svar": {}, "grunnlag": f"{_RELATION_FILE}:{field}" if field else "",
            "sikkerhet": "lav", "avstaar": True}


def _has_key(obj: Any, wanted: set[str]) -> bool:
    if isinstance(obj, dict):
        if any(key in wanted for key in obj):
            return True
        return any(_has_key(value, wanted) for value in obj.values())
    if isinstance(obj, list):
        return any(_has_key(value, wanted) for value in obj)
    return False


def _read_q1(bank: dict[str, Any]) -> dict[str, Any]:
    observations = sorted(r["object"] for r in _relations_between(bank, "efc.growth_engine", "OBSERVED_IN"))
    regimes = sorted(r["object"] for r in _relations_between(bank, "efc.growth_engine", "COUPLED_TO"))
    return _answer("Q1", {"observasjon": observations, "regime": regimes}, "relations")


def _read_q2(bank: dict[str, Any]) -> dict[str, Any]:
    nodes = _nodes(bank)
    order = ["obs.bao", "obs.fsigma8", "efc.growth_engine"]
    ids = [node_id for node_id in order
           if "prediction" in nodes.get(node_id, {}) and "settlement" in nodes.get(node_id, {})]
    return _answer("Q2", ids, "nodes:prediction,settlement")


def _read_q4(bank: dict[str, Any]) -> dict[str, Any]:
    value = {"subject": "efc.hubble_engine", "predicate": "OBSERVED_IN", "object": "obs.bao"}
    found = bool(_relations_between(bank, **{"subject": value["subject"], "predicate": value["predicate"], "object_": value["object"]}))
    return _answer("Q4", value if found else {}, "relations")


def _read_q5(bank: dict[str, Any]) -> dict[str, Any]:
    pair = {"homo.aksjonspotensial", "homo.hjerte_syklus"}
    rows = [r for r in _relations(bank) if r.get("predicate") == "ANALOGOUS_TO"
            and {r.get("subject"), r.get("object")} == pair]
    return _answer("Q5", {"syklus": bool(rows), "par": sorted(pair),
                            "predikat": "ANALOGOUS_TO", "rader": len(rows)}, "relations")


def _read_q6(bank: dict[str, Any]) -> dict[str, Any]:
    missing = []
    for node_id in ("obs.bao", "obs.fsigma8", "efc.growth_engine", "efc.rotation_engine",
                    "efc.lag_c0", "h2o.droplet", "homo.aksjonspotensial", "homo.hjerte_syklus"):
        node = _nodes(bank).get(node_id, {})
        covered = ("ville_falsifisere" in node or "falsifiserbarhet" in node
                   or isinstance(node.get("stipulasjoner"), dict)
                   and "ikke_falsifiserbar_grunn" in node["stipulasjoner"])
        if not covered:
            missing.append(node_id)
    return _answer("Q6", {"mangler": missing}, "nodes:falsifier")


def _read_q7(bank: dict[str, Any]) -> dict[str, Any]:
    nodes = _nodes(bank)
    count = sum(_has_key(node, {"uncertainty", "usikkerhet"}) for node in nodes.values())
    return _answer("Q7", {"antall": count}, "nodes:uncertainty")


def _read_q8(bank: dict[str, Any]) -> dict[str, Any]:
    targets = sorted(r["object"] for r in _relations_between(bank, "obs.bao", "OBSERVED_IN"))
    return _answer("Q8", targets, "relations")


def svar(bank: dict, key: dict) -> list[dict]:
    """Answer the questions using only fields, relations, and keyed prose fields."""
    readers = {"Q1": _read_q1, "Q2": _read_q2, "Q3": lambda b: _abstain("Q3"),
               "Q4": _read_q4, "Q5": _read_q5, "Q6": _read_q6,
               "Q7": lambda b: _abstain("Q7"), "Q8": _read_q8}
    result = []
    for question in key.get("sporsmal", []):
        qid = question["id"]
        result.append(readers.get(qid, lambda _b: _abstain(qid))(bank))
    return result


def _load_json_ref(ref: str, path: str) -> dict:
    raw = subprocess.check_output(["git", "show", f"{ref}:{path}"], text=True)
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    bank = _load_json_ref(args.ref, "schema/regime_nodes.jsonld")
    key = json.loads((Path(__file__).with_name("key.json")).read_text(encoding="utf-8"))
    print(json.dumps(svar(bank, key), ensure_ascii=False))


if __name__ == "__main__":
    main()
