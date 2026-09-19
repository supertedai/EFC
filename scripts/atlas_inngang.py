#!/usr/bin/env python3
"""Read one word or one node through memory, engine and NATS."""
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
    """The source could not be read."""


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True)
    if p.returncode:
        raise InngangFeil(f"git {' '.join(args)} feilet: {p.stderr.strip()}")
    return p.stdout


def json_ref(repo: Path, ref: str, sti: str) -> dict:
    return json.loads(git(repo, "show", f"{ref}:{sti}"))


def motorfiler(repo: Path, ref: str) -> list[str]:
    """Engine files in the git tree at `ref`.

    An EMPTY list means the directory exists and has no engines. The first
    version also swallowed "the directory does not exist" and answered the
    same — "no engine file" — and then a missing tree looks like a finding.
    When the directory does not exist, the call says so.
    """
    try:
        filer = git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_STI}")
    except InngangFeil as e:
        raise InngangFeil(
            f"{MOTOR_STI} does not exist at {ref} — the engine layer was not read"
        ) from e
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


def emne_oppslag(repo: Path, sha: str, ordet: str) -> tuple[list[str], bool]:
    """Share the resolver with `atlas_lesing` instead of having two truths.

    Measured in review 2026-09-18: this entry point looked up only EXACT node
    ids and bus domains. The word "entropy gradient" could then be answered
    with the do-not-know answer here, while `atlas_lesing --emne` answered
    with hits — two entry points, two answers, the same question. One entry
    point must not have its own dictionary.

    Returns (lines, is_registered_concept). The last flag exists because the
    do-not-know answer is the WRONG answer when the concept stands in the
    namespace: the atlas knows what the word is, it just has no node for it.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import atlas_lesing
    except ImportError as e:  # pragma: no cover - only when the file is missing
        return ([f"EMNE: not resolved — atlas_lesing could not be read ({e})"],
                False)
    svar = atlas_lesing.finn(repo, ordet, sha)
    treff = svar.get("treff", [])
    begrep = [t for t in treff if t.get("trefftype") == "navnerom"]
    linjer = [f"EMNE: {svar['antall']} hits in the bank"
              + (" — ATLASET VET IKKE" if svar.get("hull") else "")]
    for t in treff[:5]:
        merke = " (namespace, no node)" if t.get("trefftype") == "navnerom" else ""
        linjer.append(f"  {t.get('id', '?')}{merke}")
    if begrep:
        linjer.append(f"  the concept is registered, but has no node: "
                      f"{begrep[0].get('grunn', 'reason not stated')}")
    if svar.get("hull"):
        kjent = atlas_lesing._kjent_hull(
            atlas_lesing._dekning(repo, sha, False), ordet)
        if kjent:
            linjer.append(f"  known gap: {kjent.get('domene')} — "
                          f"{kjent.get('begrunnelse', 'no reason stated')}")
    return linjer, bool(begrep)


def les(repo: str | Path, ord_eller_node: str, ref: str = STANDARD_REF) -> str:
    repo = Path(repo)
    # ONE resolved commit. If we keep reading the moving ref, two files in
    # the same answer can come from different states when the ref moves.
    sha = git(repo, "rev-parse", ref).strip()
    atlas = json_ref(repo, sha, NODE_STI)
    node = next((n for n in atlas.get("nodes", [])
                 if n.get("id") == ord_eller_node), None)
    nats = json_ref(repo, sha, NATS_STI).get("domener", {})
    dekning = json_ref(repo, sha, DEKNING_STI)
    try:
        motorer = motorfiler(repo, sha)
        motor_feil = None
    except InngangFeil as e:
        # A NAMED absence, not "no engine file". A missing tree is not a
        # finding that the node has no engine.
        motorer, motor_feil = [], str(e)
    lines = [f"INNGANG: {ord_eller_node}", f"REF: {ref} @ {sha[:8]}"]
    if node is None:
        hull = kjent_hull(dekning, ord_eller_node)
        emne_linjer, er_begrep = emne_oppslag(repo, sha, ord_eller_node)
        if er_begrep:
            # The do-not-know answer is wrong when the concept is registered.
            # The atlas knows what the word IS; it just has no node for it.
            lines.append("NODE: no node — REGISTERED CONCEPT, no atlas node")
        elif hull is not None:
            lines += ["NODE: ingen node — KJENT HULL",
                      f"  domene: {hull['domene']}",
                      f"  status: {hull.get('status', 'unknown')}"]
            lines.append(f"  grunn: {hull.get('begrunnelse', 'no declared reason')}")
        else:
            lines.append("NODE: ingen node — ATLASET VET IKKE (ingen maaling)")
        lines += emne_linjer
        lines.append("MOTOR: no engine file")
        lines.append("BUSS: no bus path")
    else:
        regime = node.get("regime") or {}
        ep = node.get("epistemikk") or {}
        s_status = (node.get("maale_paradigme") or {}).get("s_regime", "not declared")
        lines += [f"NODE: {node['id']}",
                  # The field is named `phase`, not "code". The first version
                  # wrote "kode: regime_engine" — a name that lied about the
                  # content, because the node's code is the short identifier
                  # (RO, HB, …) that the generator owns. A field that presents
                  # a phase as a code is the same class as an answer that
                  # answers something else.
                  f"  fase: {node.get('phase', 'not declared')}",
                  f"  regime: {regime.get('name', 'not declared')}",
                  f"  synlighet: {node.get('synlighet', 'not declared')}",
                  f"  gyldighet: {regime.get('validity', regime.get('name', 'not declared'))}",
                  f"  epistemikk: sannhet={ep.get('sannhetsstatus', 'not declared')}; evidens={ep.get('evidensstatus', 'not declared')}",
                  f"  S-akse-status: {s_status}"]
        motor = node_motor(node["id"], motorer)
        if motor_feil:
            lines.append(f"MOTOR: not read — {motor_feil}")
        else:
            lines.append(f"MOTOR: {motor or 'no engine file'}"
                         + (" (derived from the node-id -> "
                            "engine-name naming convention, not a declared link)"
                            if motor else ""))
        domene = node.get("buss_domene")
        if domene and domene in nats:
            emner = nats[domene].get("emner", {})
            lines.append(f"BUSS: {domene}")
            lines.extend(f"  emne: {emne}" for emne in sorted(emner))
        else:
            grunn = node.get("lagdeling", {}).get("bussgrunn") or "no buss_domene declared"
            lines += ["BUSS: no bus path", f"  grunn: {grunn}"]
    lines.append("UTENFOR REKKEVIDDE: Hindsight-banken efc eies av MCP-verktoyene mcp__hindsight_efc__*; skriptet kan ikkje lese den.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Find where an atlas word lives.")
    ap.add_argument("ord_eller_node_id")
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("repo", nargs="?", default=".")
    a = ap.parse_args()
    try:
        print(les(a.repo, a.ord_eller_node_id, a.ref))
    except (InngangFeil, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
