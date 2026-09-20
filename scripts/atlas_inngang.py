#!/usr/bin/env python3
"""Read one word or one node through memory, engine and NATS."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# The ref and path constants keep their names: atlas_navigasjon.py:30,33 and
# atlas_volum.py:64,66 define the same ones with the same values — the atlas
# tools read as one family, and a rename is one decision for all the modules,
# not five. Reported, not hidden.
STANDARD_REF = "origin/main"
NODE_STI = "schema/regime_nodes.jsonld"
DEKNING_STI = "schema/atlas_dekning.json"
NATS_STI = "schema/nats_domener.snapshot.json"
MOTOR_STI = "efc_inference/engine"


class EntryError(RuntimeError):
    """The basis could not be read."""


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True)
    if p.returncode:
        raise EntryError(f"git {' '.join(args)} failed: {p.stderr.strip()}")
    return p.stdout


def json_ref(repo: Path, ref: str, path: str) -> dict:
    return json.loads(git(repo, "show", f"{ref}:{path}"))


def engine_files(repo: Path, ref: str) -> list[str]:
    """Engine files in the git tree at `ref`.

    An EMPTY list means the directory exists and holds no engines. The first
    version also swallowed "the directory does not exist" and answered the same
    thing — "no engine file" — and then a missing tree looks like a finding.
    When the directory does not exist, the call says so.
    """
    try:
        files = git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_STI}")
    except EntryError as e:
        raise EntryError(
            f"{MOTOR_STI} does not exist at {ref} — the engine layer was not read"
        ) from e
    return sorted(Path(x).stem for x in files.splitlines()
                  if x.endswith(".py") and Path(x).stem not in {"__init__", "base_engine"})


def node_engine(node_id: str, engines: list[str]) -> str | None:
    suffix = node_id.rsplit(".", 1)[-1]
    if not suffix.endswith("_engine"):
        return None
    name = suffix[:-7]
    return f"{name}.py" if name in engines else None


def known_gap(coverage: dict, word: str) -> dict | None:
    needle = word.lower().replace("-", "_")
    for domain, data in sorted(coverage.get("domener", {}).items()):
        if needle == domain.lower() or needle in domain.lower().split("."):
            return {"domene": domain, **data}
        if any(needle == str(n).lower() for n in data.get("noder", [])):
            return None
    return None


def topic_lookup(repo: Path, sha: str, word: str) -> tuple[list[str], bool]:
    """Share the resolver with `atlas_lesing` instead of having two truths.

    Measured in review 2026-09-18: this entry point only looked up EXACT node
    ids and bus domains. The word "entropy gradient" could then be answered
    "THE ATLAS DOES NOT KNOW" here, while `atlas_lesing --emne` answered with
    hits — two entry points, two answers, one question. One entry point must
    not have a dictionary of its own.

    Returns (lines, is_registered_term). The last flag exists because "the
    atlas does not know" is the WRONG answer when the term stands in the
    namespace: the atlas knows what the word is, it just has no node for it.
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import atlas_lesing
    except ImportError as e:  # pragma: no cover - only when the file is missing
        return ([f"TOPIC: not looked up — atlas_lesing could not be read ({e})"],
                False)
    answer = atlas_lesing.finn(repo, word, sha)
    hits = answer.get("treff", [])
    terms = [t for t in hits if t.get("trefftype") == "navnerom"]
    lines = [f"TOPIC: {answer['antall']} hits in the bank"
             + (" — THE ATLAS DOES NOT KNOW" if answer.get("hull") else "")]
    for t in hits[:5]:
        tag = " (namespace, no node)" if t.get("trefftype") == "navnerom" else ""
        lines.append(f"  {t.get('id', '?')}{tag}")
    if terms:
        lines.append(f"  the term is registered, but has no node: "
                     f"{terms[0].get('grunn', 'no reason given')}")
    if answer.get("hull"):
        known = atlas_lesing._kjent_hull(
            atlas_lesing._dekning(repo, sha, False), word)
        if known:
            lines.append(f"  known gap: {known.get('domene')} — "
                         f"{known.get('begrunnelse', 'no reason given')}")
    return lines, bool(terms)


def read(repo: str | Path, word_or_node: str, ref: str = STANDARD_REF) -> str:
    repo = Path(repo)
    # ONE resolved commit. If we keep reading the moving ref, two files in the
    # same answer can come from two different states once the ref moves.
    sha = git(repo, "rev-parse", ref).strip()
    atlas = json_ref(repo, sha, NODE_STI)
    node = next((n for n in atlas.get("nodes", [])
                 if n.get("id") == word_or_node), None)
    nats = json_ref(repo, sha, NATS_STI).get("domener", {})
    coverage = json_ref(repo, sha, DEKNING_STI)
    try:
        engines = engine_files(repo, sha)
        engine_error = None
    except EntryError as e:
        # A NAMED absence, not "no engine file". A missing tree is not a
        # finding that the node has no engine.
        engines, engine_error = [], str(e)
    lines = [f"ENTRY: {word_or_node}", f"REF: {ref} @ {sha[:8]}"]
    if node is None:
        gap = known_gap(coverage, word_or_node)
        topic_lines, is_term = topic_lookup(repo, sha, word_or_node)
        if is_term:
            # "The atlas does not know" is the wrong answer when the term is
            # registered. The atlas knows what the word IS; it just has no
            # node for it.
            lines.append("NODE: no node — REGISTERED TERM, no atlas node")
        elif gap is not None:
            lines += ["NODE: no node — KNOWN GAP",
                      f"  domain: {gap['domene']}",
                      f"  status: {gap.get('status', 'unknown')}"]
            lines.append(f"  reason: {gap.get('begrunnelse', 'no declared reason')}")
        else:
            lines.append("NODE: no node — THE ATLAS DOES NOT KNOW (no measurement)")
        lines += topic_lines
        lines.append("ENGINE: no engine file")
        lines.append("BUS: no bus route")
    else:
        regime = node.get("regime") or {}
        ep = node.get("epistemikk") or {}
        s_status = (node.get("maale_paradigme") or {}).get("s_regime", "not declared")
        lines += [f"NODE: {node['id']}",
                  # The field is called `phase`, not "code". The first version
                  # printed "code: regime_engine" — a name that lied about the
                  # contents, because a node's code is the short identifier
                  # (RO, HB, …) that the generator owns. A field that presents
                  # a phase as a code is the same class as an answer that
                  # answers something else.
                  f"  phase: {node.get('phase', 'not declared')}",
                  f"  regime: {regime.get('name', 'not declared')}",
                  f"  visibility: {node.get('synlighet', 'not declared')}",
                  f"  validity: {regime.get('validity', regime.get('name', 'not declared'))}",
                  f"  epistemics: truth={ep.get('sannhetsstatus', 'not declared')}; evidence={ep.get('evidensstatus', 'not declared')}",
                  f"  S-axis status: {s_status}"]
        engine = node_engine(node["id"], engines)
        if engine_error:
            lines.append(f"ENGINE: not read — {engine_error}")
        else:
            lines.append(f"ENGINE: {engine or 'no engine file'}"
                         + (" (derived from the naming convention node-id -> "
                            "engine name, not from a declared coupling)"
                            if engine else ""))
        domain = node.get("buss_domene")
        if domain and domain in nats:
            topics = nats[domain].get("emner", {})
            lines.append(f"BUS: {domain}")
            lines.extend(f"  topic: {topic}" for topic in sorted(topics))
        else:
            reason = node.get("lagdeling", {}).get("bussgrunn") or "the node does not declare buss_domene"
            lines += ["BUS: no bus route", f"  reason: {reason}"]
    lines.append("OUT OF REACH: the Hindsight bank efc is owned by the MCP tools mcp__hindsight_efc__*; this script cannot read it.")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Find where an atlas word lives.")
    ap.add_argument("word_or_node_id")
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("repo", nargs="?", default=".")
    a = ap.parse_args()
    try:
        print(read(a.repo, a.word_or_node_id, a.ref))
    except (EntryError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
