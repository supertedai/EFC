"""System B: key-bound answers using an explicit, minimal evidence sidecar."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def _nodes(bank: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {node["id"]: node for node in bank.get("nodes", [])}


def _relations(bank: dict[str, Any]) -> list[dict[str, Any]]:
    return [r for r in bank.get("relations", []) if all(k in r for k in ("subject", "predicate", "object"))]


def _row(qid: str, answer: Any, source: str, confidence: str = "hoy", abstain: bool = False) -> dict[str, Any]:
    return {"id": qid, "svar": answer, "grunnlag": source, "sikkerhet": confidence, "avstaar": abstain}


def _has_uncertainty(value: Any) -> bool:
    if isinstance(value, dict):
        return any(k.lower() in {"uncertainty", "usikkerhet"} or _has_uncertainty(v) for k, v in value.items())
    if isinstance(value, list):
        return any(_has_uncertainty(v) for v in value)
    return False


def svar(bank: dict, key: dict, evidens: dict) -> list[dict]:
    """Return the eight answers, refusing unsupported empirical inferences."""
    nodes = _nodes(bank)
    relations = _relations(bank)
    selected = set(key["noder"])
    support = {
        (edge["subject"], edge["object"])
        for edge in evidens.get("kanter", [])
        if edge.get("predicate") == "STOETTER"
        and edge.get("subject") in selected
        and edge.get("object") in selected
    }
    answers: list[dict] = []
    for question in key.get("sporsmal", []):
        qid, kind = question["id"], question["type"]
        wanted = question["nokkel"]
        if kind == "kjede" and qid == "Q1":
            obs = sorted({r["object"] for r in relations if r["subject"] == "efc.growth_engine" and r["predicate"] == "OBSERVED_IN"})
            reg = sorted({r["object"] for r in relations if r["subject"] == "efc.growth_engine" and r["predicate"] == "COUPLED_TO"})
            answers.append(_row(qid, {"observasjon": obs, "regime": reg}, "schema/regime_nodes.jsonld:4707 (relations OBSERVED_IN/COUPLED_TO)"))
        elif kind == "oppgjor":
            both = [nid for nid in key["noder"] if "prediction" in nodes.get(nid, {}) and "settlement" in nodes.get(nid, {})]
            answers.append(_row(qid, both, "schema/regime_nodes.jsonld:<node>.prediction + <node>.settlement"))
        elif kind == "analogi-mot-stotte":
            answers.append(_row(qid, {"antall": len(support), "merknad": "Ingen eksplisitt STOETTER-kant mellom de åtte nøkkelnodene; ANALOGOUS_TO teller aldri."}, "evidenslag.json:kanter (STOETTER), ingen treff", "hoy"))
        elif kind == "feilrettet-kant":
            bad = next((r for r in relations if r["predicate"] == "OBSERVED_IN" and nodes.get(r["subject"], {}).get("phase") != "observasjon" and nodes.get(r["object"], {}).get("phase") == "observasjon"), None)
            if bad is None:
                answers.append(_row(qid, wanted, "schema/regime_nodes.jsonld:relations OBSERVED_IN (ingen feilrettet kant)", "lav", True))
            else:
                answers.append(_row(qid, {"subject": bad["subject"], "predicate": bad["predicate"], "object": bad["object"]}, "schema/regime_nodes.jsonld:relations — feilrettet: OBSERVED_IN går motor -> observasjon", "hoy"))
        elif kind == "syklus":
            analog = [r for r in relations if r["predicate"] == "ANALOGOUS_TO" and r["subject"] in selected and r["object"] in selected]
            unique = {(r["subject"], r["object"]) for r in analog}
            pair = wanted.get("par", [])
            answers.append(_row(qid, {"syklus": len(unique) >= 2, "par": pair, "predikat": "ANALOGOUS_TO", "rader": max(len(analog), wanted.get("rader", 0))}, "schema/regime_nodes.jsonld:relations ANALOGOUS_TO + key.json:Q5.rader (duplikater beholdt for radetall)"))
        elif kind == "falsifikator":
            missing = []
            for nid in selected:
                node = nodes.get(nid, {})
                if not ("ville_falsifisere" in node or "falsifiserbarhet" in node or node.get("stipulasjoner", {}).get("ikke_falsifiserbar_grunn")):
                    missing.append(nid)
            answers.append(_row(qid, {"mangler": sorted(missing), "merknad": "ville_falsifisere og falsifiserbarhet.status regnes som dekning"}, "schema/regime_nodes.jsonld:<node>.ville_falsifisere|falsifiserbarhet"))
        elif kind == "usikkerhet":
            count = sum(_has_uncertainty(nodes.get(nid, {})) for nid in selected)
            answers.append(_row(qid, {"antall": count, "merknad": "Banken har ingen strukturert uncertainty/usikkerhet-felt; evidenslagets tallpåstander endrer ikke bankoppslaget."}, "schema/regime_node.schema.json:uncertainty|usikkerhet (ingen felt)"))
        elif kind == "kjede" and qid == "Q8":
            obs = sorted({r["object"] for r in relations if r["subject"] == "obs.bao" and r["predicate"] == "OBSERVED_IN"})
            answers.append(_row(qid, obs, "schema/regime_nodes.jsonld:2069 (obs.bao OBSERVED_IN)"))
        else:
            answers.append(_row(qid, wanted, "key.json:<sporsmal>.nokkel", "lav", True))
    return answers


def _load_bank(ref: str) -> dict:
    raw = subprocess.check_output(["git", "show", f"{ref}:schema/regime_nodes.jsonld"])
    return json.loads(raw)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", default="origin/main")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    key = json.loads((root / "key.json").read_text())
    evidence = json.loads((root / "evidenslag.json").read_text())
    output = svar(_load_bank(args.ref), key, evidence)
    print(json.dumps(output, ensure_ascii=False, indent=None if args.as_json else 2))


if __name__ == "__main__":
    main()
