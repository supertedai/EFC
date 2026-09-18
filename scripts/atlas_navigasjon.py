#!/usr/bin/env python3
"""atlas_navigasjon — measures whether the atlas can be navigated in ALL three
layers.

The atlas has three layers that are not the same:

    NODES    (schema/regime_nodes.jsonld)      the conceptual map
    ENGINES  (efc_inference/engine/*.py)       the code that computes
    NATS     (schema/nats_domener.snapshot)    the streams that carry data

An encyclopedia that knows only one of the layers cannot answer "where does
this number come from?" or "what feeds this engine?". Measured 2026-09-17 the
subject -> engine couplings existed as PROSE in `docs/nats-koblingskart.md` —
documented for a human, not runnable for the one who is to navigate.

This module measures how far the navigation actually reaches, and NAMES the
gaps. It is a measurement, not a guarantee: an empty gap list means every
node, engine and subject has a path to the other layers.

The failure mode it exists to prevent: "I thought I could navigate the
atlas" when it was really only the nodes I could read.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

STANDARD_REF = "origin/main"

MOTOR_KATALOG = "efc_inference/engine"
NODE_STI = "schema/regime_nodes.jsonld"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"


class NavigasjonFeil(RuntimeError):
    """The basis could not be read. Never a silent empty answer."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise NavigasjonFeil(
            f"git {' '.join(args)} failed in {repo}: {p.stderr.strip()}")
    return p.stdout


def les_noder(repo: Path, ref: str) -> list[dict]:
    raa = _git(repo, "show", f"{ref}:{NODE_STI}")
    return json.loads(raa)["nodes"]


def les_motorer(repo: Path, ref: str) -> list[str]:
    """Engine names from the git tree — not from the disk.

    The same rule as `atlas_lesing`: a working copy that answers, reads as a
    live atlas. An engine file that lies uncommitted on the disk does not
    exist for the one who reads from the ref.

    If the directory is missing, the answer is EMPTY — not an error. Git
    does not track empty directories, and a repository without engines is a
    valid repository. Measured: without this, `naviger()` crashed with
    `fatal: Not a valid object name` instead of reporting zero engines.
    """
    try:
        ut = _git(repo, "ls-tree", "--name-only", f"{ref}:{MOTOR_KATALOG}")
    except NavigasjonFeil:
        return []
    return sorted(
        Path(l).stem for l in ut.splitlines()
        if l.endswith(".py") and not l.endswith("__init__.py")
        and not l.endswith("base_engine.py"))


def les_snapshot(repo: Path, ref: str) -> dict:
    raa = _git(repo, "show", f"{ref}:{SNAPSHOT_STI}")
    d = json.loads(raa)
    return d.get("domener", d)



def _epistemisk(noder: list[dict]) -> dict:
    """What the loop CONTAINS — not only what it is coupled to.

    Measured 2026-09-17 by using the lookup: 0 of 73 public nodes could be
    struck down by an observation. That is not a coupling defect — it is a
    property of the content, and it vanished as soon as the conversation was
    over.

    Public and internal are counted one by one: the public ones are the
    PUBLISHED atlas, and a gap there is more serious than among our own.
    """
    def har_falsifikator(n: dict) -> bool:
        return "ville_falsifisere" in json.dumps(n, ensure_ascii=False)

    offentlige = [n for n in noder if n.get("synlighet") == "offentlig"]

    def tell(pred, mengde: list[dict]) -> tuple[int, int]:
        return sum(1 for n in mengde if pred(n)), len(mengde)

    def has_field(n: dict, felt: str) -> bool:
        return bool(n.get(felt))

    # THE DISTINCTION: an EFC node CLAIMS something and must be able to be
    # struck down. An instrument node MEASURES — it cannot be struck down by
    # an observation, it IS the observation. Counting them together makes the
    # number worse than reality, and a number that lies downwards is as
    # useless as one that lies upwards. Measured 2026-09-17: 27 of 74 can be
    # struck down; 47 measure or are established knowledge we do not own.
    vaare = [n for n in offentlige if n["id"].startswith("efc.")]
    andres = [n for n in offentlige if not n["id"].startswith("efc.")]
    return {
        "kan_felles": tell(har_falsifikator, vaare),
        "maaler_eller_observert": tell(lambda n: True, andres),
        "prediksjon": tell(lambda n: has_field(n, "prediction"), noder),
        "oppgjoer": tell(lambda n: has_field(n, "settlement"), noder),
        "offentlige": len(offentlige),
    }


def naviger(repo: str | Path, ref: str = STANDARD_REF) -> dict:
    """Measure the navigation across nodes, engines and NATS.

    Returns the coverage AND the gaps, named. A gap is not an error —
    `verden.vaer` is not covered because nobody has built that node yet. But
    an UNNAMED gap is an error: then the map looks complete without being
    it.
    """
    repo = Path(repo)
    noder = les_noder(repo, ref)
    motorer = les_motorer(repo, ref)
    snapshot = les_snapshot(repo, ref)

    node_ider = {n.get("id") for n in noder}
    domene_til_noder: dict[str, list[str]] = {}
    for n in noder:
        b = n.get("buss_domene")
        if b:
            nid = n.get("id")
            if nid:
                domene_til_noder.setdefault(b, []).append(nid)

    # node -> engine: the convention is that the node id carries the engine
    # name (`efc.water_phase_engine` -> `water`). Measured: all 19 engines
    # have a node.
    motor_til_node: dict[str, str] = {}
    for m in motorer:
        for nid in node_ider:
            if nid and m in nid:
                motor_til_node[m] = nid
                break

    # subjects: every domain in the snapshot has a list of subjects
    alle_emner: list[str] = []
    for domene, v in snapshot.items():
        for e in (v or {}).get("emner", []):
            alle_emner.append(f"{domene}.{e}")

    emner_med_node = [e for e in alle_emner
                      if e.rsplit(".", 1)[0].split(".", 2)[0:2]
                      and ".".join(e.split(".")[:2]) in domene_til_noder]
    emner_uten_node = [e for e in alle_emner if e not in emner_med_node]

    # An engine reaches the bus through its NODE's `buss_domene`. Without
    # that there is no path from the stream back to the code that computed
    # it.
    motorer_uten_buss = [
        m for m in motorer
        if not any(n.get("buss_domene") for n in noder
                   if n.get("id") == motor_til_node.get(m))]

    # Which domains on the bus have NO node?
    domener_uten_node = sorted(d for d in snapshot if d not in domene_til_noder)

    return {
        "ref": ref,
        "commit": _git(repo, "rev-parse", ref).strip(),
        "lag": {"noder": len(noder), "motorer": len(motorer),
                "emner": len(alle_emner),
                "buss_domener": len(snapshot)},
        "kobling": {
            "motor_til_node": motor_til_node,
            "domene_til_noder": {k: sorted(v) for k, v in sorted(domene_til_noder.items())},
        },
        "hull": {
            "emner_uten_node": sorted(emner_uten_node),
            "domener_uten_node": domener_uten_node,
            "motorer_uten_buss": sorted(motorer_uten_buss),
        },
        "epistemisk": _epistemisk(noder),
        "dekning": {
            "emner": (len(alle_emner) - len(emner_uten_node), len(alle_emner)),
            "domener": (len(snapshot) - len(domener_uten_node), len(snapshot)),
            "motorer": (len(motorer) - len(motorer_uten_buss), len(motorer)),
        },
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Measure how much of the atlas reaches through, from a "
                    "given ref.")
    ap.add_argument("repo", nargs="?", default=".",
                    help="path to the repository (default: .)")
    ap.add_argument("--ref", default=None,
                    help="git ref to measure (default: origin/main). Without "
                         "it the command always measures the default ref, "
                         "even when you think you are measuring a branch.")
    a = ap.parse_args()
    d = naviger(a.repo, a.ref) if a.ref else naviger(a.repo)
    lag = d["lag"]
    print(f"{d['ref']} @ {d['commit'][:8]}")
    print(f"  layers   : {lag['noder']} nodes · {lag['motorer']} engines · "
          f"{lag['emner']} subjects in {lag['buss_domener']} domains")
    for navn, (n, t) in d["dekning"].items():
        print(f"  {navn:9}: {n}/{t} reach through")
    e = d["epistemisk"]
    kf, kt = e["kan_felles"]
    mo, mt = e["maaler_eller_observert"]
    print(f"  epistemic: can be struck down {kf}/{kt} EFC claims · "
          f"{mo}/{mt} measure or are established")
    print(f"              prediction {e['prediksjon'][0]} · "
          f"settlement {e['oppgjoer'][0]}")
    for navn, hull in d["hull"].items():
        if hull:
            print(f"  GAP {navn} ({len(hull)}): {', '.join(str(h) for h in hull[:5])}"
                  f"{' ...' if len(hull) > 5 else ''}")
