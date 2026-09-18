#!/usr/bin/env python3
"""Les eitt ord eller ein node gjennom minne, motor og NATS."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

STANDARD_REF = "origin/main"
NODE_STI = "schema/regime_nodes.jsonld"
DEKNING_STI = "schema/atlas_dekning.json"
NATS_STI = "schema/nats_domener.snapshot.json"
MOTOR_STI = "efc_inference/engine"


class InngangFeil(RuntimeError):
    """Grunnlaget kunne ikkje lesast."""


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True)
    if p.returncode:
        raise InngangFeil(f"git {' '.join(args)} feilet: {p.stderr.strip()}")
    return p.stdout


def json_ref(repo: Path, ref: str, sti: str) -> dict:
    return json.loads(git(repo, "show", f"{ref}:{sti}"))


def motorfiler(repo: Path, ref: str) -> list[str]:
    try:
        filer = git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_STI}")
    except InngangFeil:
        return []
    return sorted(Path(x).stem for x in filer.splitlines()
                  if x.endswith(".py") and Path(x).stem not in {"__init__", "base_engine"})


def node_motor(node_id: str, motorer: list[str]) -> str | None:
    suffix = node_id.rsplit(".", 1)[-1]
    if not suffix.endswith("_engine"):
        return None
    navn = suffix[:-7]
    return f"{navn}.py" if navn in motorer else None


def kjent_hull(dekning: dict, ordet: str) -> dict | None:
    needle = ordet.lower().replace("-", "_")
    for domene, data in sorted(dekning.get("domener", {}).items()):
        if needle == domene.lower() or needle in domene.lower().split("."):
            return {"domene": domene, **data}
        if any(needle == str(n).lower() for n in data.get("noder", [])):
            return None
    return None


def les(repo: str | Path, ord_eller_node: str, ref: str = STANDARD_REF) -> str:
    repo = Path(repo)
    commit = git(repo, "rev-parse", ref).strip()
    atlas = json_ref(repo, ref, NODE_STI)
    node = next((n for n in atlas.get("nodes", [])
                 if n.get("id") == ord_eller_node), None)
    nats = json_ref(repo, ref, NATS_STI).get("domener", {})
    dekning = json_ref(repo, ref, DEKNING_STI)
    motorer = motorfiler(repo, ref)
    lines = [f"INNGANG: {ord_eller_node}", f"REF: {ref} @ {commit[:8]}"]
    if node is None:
        hull = kjent_hull(dekning, ord_eller_node)
        if hull is not None:
            lines += ["NODE: ingen node — KJENT HULL",
                      f"  domene: {hull['domene']}",
                      f"  status: {hull.get('status', 'ukjent')}"]
            lines.append(f"  grunn: {hull.get('begrunnelse', 'ingen deklarert grunn')}")
        else:
            lines.append("NODE: ingen node — ATLASET VET IKKE (ingen maaling)")
        lines.append("MOTOR: ingen motorfil")
        lines.append("BUSS: ingen buss-vei")
    else:
        regime = node.get("regime") or {}
        ep = node.get("epistemikk") or {}
        s_status = (node.get("maale_paradigme") or {}).get("s_regime", "ikke deklarert")
        lines += [f"NODE: {node['id']}",
                  # Feltet heter `phase`, ikke «kode». Foerste utgave skrev
                  # «kode: regime_engine» — et navn som loey om innholdet, for
                  # nodens kode er den korte identifikatoren (RO, HB, …) som
                  # generatoren eier. Et felt som presenterer en fase som en
                  # kode er samme klasse som et svar som svarer paa noe annet.
                  f"  fase: {node.get('phase', 'ikke deklarert')}",
                  f"  regime: {regime.get('name', 'ikke deklarert')}",
                  f"  synlighet: {node.get('synlighet', 'ikke deklarert')}",
                  f"  gyldighet: {regime.get('validity', regime.get('name', 'ikke deklarert'))}",
                  f"  epistemikk: sannhet={ep.get('sannhetsstatus', 'ikke deklarert')}; evidens={ep.get('evidensstatus', 'ikke deklarert')}",
                  f"  S-akse-status: {s_status}"]
        motor = node_motor(node["id"], motorer)
        lines.append(f"MOTOR: {motor or 'ingen motorfil'}")
        domene = node.get("buss_domene")
        if domene and domene in nats:
            emner = nats[domene].get("emner", {})
            lines.append(f"BUSS: {domene}")
            lines.extend(f"  emne: {emne}" for emne in sorted(emner))
        else:
            grunn = node.get("lagdeling", {}).get("bussgrunn") or "noden deklarerer ikkje buss_domene"
            lines += ["BUSS: ingen buss-vei", f"  grunn: {grunn}"]
    lines.append("UTENFOR REKKEVIDDE: Hindsight-banken efc eies av MCP-verktoyene mcp__hindsight_efc__*; skriptet kan ikkje lese den.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Finn kvar eit atlasord lever.")
    ap.add_argument("ord_eller_node_id")
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("repo", nargs="?", default=".")
    a = ap.parse_args()
    try:
        print(les(a.repo, a.ord_eller_node_id, a.ref))
    except (InngangFeil, json.JSONDecodeError) as e:
        print(f"FEIL: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
