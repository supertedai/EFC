#!/usr/bin/env python3
"""atlas_navigasjon — can the atlas be navigated in ALL three layers?

The atlas has three layers that are not the same:

    NODES    (schema/regime_nodes.jsonld)      the conceptual map
    ENGINES  (efc_inference/engine/*.py)       the code that computes
    NATS     (schema/nats_domener.snapshot)    the streams that carry data

A reference work that knows only one of the layers cannot answer «where
does this number come from?» or «what feeds this engine?». Measured
2026-09-17 the couplings topic -> engine existed as PROSE in
`docs/nats-koblingskart.md` — documented for a human, not runnable
for the one who is to navigate.

This module measures how far the navigation actually reaches, and NAMES
the holes. It is a measurement, not a guarantee: an empty hole list means
that every node, engine and topic has a path to the other layers.

The failure mode it exists to prevent: «I thought I could navigate the
atlas» when it was really only the nodes I could read.
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
    """Engine names from the git tree — not from disk.

    Same rule as `atlas_lesing`: a copy that answers reads as a live atlas.
    An engine file that sits uncommitted on disk does not exist for the one
    reading from the ref.

    If the directory is missing, the answer is EMPTY — not an error. Git does
    not track empty directories, and a repo without engines is a valid repo.
    Measured: without this, `naviger()` crashed with `fatal: Not a valid
    object name` instead of reporting zero engines.
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
    """What the LOOP CONTAINS — not just what it is coupled to.

    Measured 2026-09-17 by using the lookup: 0 of 73 public nodes could be
    felled by an observation. That is not a coupling error — it is a
    property of the content, and it vanished as soon as the conversation
    was over.

    Public and internal are counted separately: the public ones are the
    PUBLISHED atlas, and a hole there is more serious than among our own.
    """
    def har_falsifikator(n: dict) -> bool:
        return "ville_falsifisere" in json.dumps(n, ensure_ascii=False)

    offentlige = [n for n in noder if n.get("synlighet") == "offentlig"]

    def tell(pred, mengde: list[dict]) -> tuple[int, int]:
        return sum(1 for n in mengde if pred(n)), len(mengde)

    def har(n: dict, felt: str) -> bool:
        return bool(n.get(felt))

    # THE DISTINCTION: an EFC node CLAIMS something and must be able to be
    # felled. An instrument node MEASURES — it cannot be felled by an
    # observation, it IS the observation. Counting them together makes the
    # number worse than reality, and a number that lies downwards is as
    # unusable as one that lies upwards. Measured 2026-09-17: 27 of 74 can
    # be felled; 47 measure or are established knowledge we do not own.
    vaare = [n for n in offentlige if n["id"].startswith("efc.")]
    andres = [n for n in offentlige if not n["id"].startswith("efc.")]
    return {
        "kan_felles": tell(har_falsifikator, vaare),
        "maaler_eller_observert": tell(lambda n: True, andres),
        "prediksjon": tell(lambda n: har(n, "prediction"), noder),
        "oppgjoer": tell(lambda n: har(n, "settlement"), noder),
        "offentlige": len(offentlige),
    }


def naviger(repo: str | Path, ref: str = STANDARD_REF) -> dict:
    """Measure the navigation across nodes, engines and NATS.

    Returns the coverage AND the holes, named. A hole is not an error —
    `verden.vaer` is not covered because nobody has built that node yet.
    But an UNNAMED hole is an error: then the map looks complete without
    being so.
    """
    repo = Path(repo)
    noder = les_noder(repo, ref)
    motorer = les_motorer(repo, ref)
    snapshot = les_snapshot(repo, ref)

    # Set iteration was NOT deterministic. Measured 2026-09-18: the same
    # command on the same ref gave «31/32 reached · HOLE klima» in two of five
    # runs and «32/32» in three — the difference was PYTHONHASHSEED. `klima`
    # matches four nodes (`efc.klima_engine` WITH a bus domain and three
    # `verden.klima_*` without), and the one the set happened to yield first
    # won. A measurement that answers differently to the same question is
    # worse than no measurement: it looks right both times, and a hole that
    # comes and goes is not believed when it is real.
    node_ider = sorted(str(n["id"]) for n in noder if n.get("id"))

    domene_til_noder: dict[str, list[str]] = {}
    for n in noder:
        b = n.get("buss_domene")
        if b:
            nid = n.get("id")
            if nid:
                domene_til_noder.setdefault(b, []).append(nid)

    # node -> engine. The order is a RULE now, not a coincidence:
    #   1. the named engine node `efc.<motor>_engine`
    #   2. a node whose LAST segment is exactly `<motor>` or `<motor>_engine`
    #   3. otherwise nodes that contain the name
    # If more than one matches on the same level, the sorted first is chosen
    # — and the name is reported as AMBIGUOUS instead of being settled in
    # silence.
    motor_til_node: dict[str, str] = {}
    motor_flertydig: dict[str, list[str]] = {}
    for m in motorer:
        kandidater = [nid for nid in node_ider
                      if nid.split(".")[-1] in (f"{m}_engine", m)]
        if not kandidater:
            kandidater = [nid for nid in node_ider if nid.endswith(f".{m}")
                          or nid.endswith(f".{m}_engine")]
        if not kandidater:
            kandidater = [nid for nid in node_ider if m in nid]
        if not kandidater:
            continue
        precise_id = f"efc.{m}_engine"
        motor_til_node[m] = precise_id if precise_id in kandidater else kandidater[0]
        if len(kandidater) > 1:
            motor_flertydig[m] = kandidater

    # topics: each domain in the snapshot has a list of topics
    all_topics: list[str] = []
    for domene, v in snapshot.items():
        for e in (v or {}).get("emner", []):
            all_topics.append(f"{domene}.{e}")

    topics_with_node = [e for e in all_topics
                      if e.rsplit(".", 1)[0].split(".", 2)[0:2]
                      and ".".join(e.split(".")[:2]) in domene_til_noder]
    emner_uten_node = [e for e in all_topics if e not in topics_with_node]

    # An engine reaches the bus when its NODE has a `buss_domene`. Without
    # it there is no path from the stream back to the code that computed it.
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
                "emner": len(all_topics),
                "buss_domener": len(snapshot)},
        "kobling": {
            "motor_til_node": motor_til_node,
            "motor_flertydig": {k: v for k, v in sorted(motor_flertydig.items())},
            "domene_til_noder": {k: sorted(v) for k, v in sorted(domene_til_noder.items())},
        },
        "hull": {
            "emner_uten_node": sorted(emner_uten_node),
            "domener_uten_node": domener_uten_node,
            "motorer_uten_buss": sorted(motorer_uten_buss),
        },
        "epistemisk": _epistemisk(noder),
        "dekning": {
            "emner": (len(all_topics) - len(emner_uten_node), len(all_topics)),
            "domener": (len(snapshot) - len(domener_uten_node), len(snapshot)),
            "motorer": (len(motorer) - len(motorer_uten_buss), len(motorer)),
        },
    }


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        description="Measure how much of the atlas reaches through, from a given ref.")
    ap.add_argument("repo", nargs="?", default=".",
                    help="path to the repo (default: .)")
    ap.add_argument("--ref", default=None,
                    help="git ref to measure (default: origin/main). Without "
                         "this the command always measures the default ref, "
                         "also when you think you are measuring a branch.")
    a = ap.parse_args()
    d = naviger(a.repo, a.ref) if a.ref else naviger(a.repo)
    lag = d["lag"]
    # The word «engine» means two things in this house: the engine on disk
    # (32 files) and the node that carries it (`efc.*_engine`, 19). Measured
    # 2026-09-18 both stood as «motorer» — 32 here and 19 in SYSTEM.md — and
    # a word that means two numbers is not a name. Outward it is now called
    # ENGINE FILES here, and «engine nodes» in the text twin. The KEYS are
    # unchanged, because they are an API; the labels are for the eye — the
    # two other keys get their outward names here for the same reason.
    ETIKETT = {"motorer": "engine files", "emner": "topics",
               "domener": "domains"}
    print(f"{d['ref']} @ {d['commit'][:8]}")
    print(f"  layers   : {lag['noder']} nodes · {lag['motorer']} engine files · "
          f"{lag['emner']} topics in {lag['buss_domener']} domains")
    for navn, (n, t) in d["dekning"].items():
        print(f"  {ETIKETT.get(navn, navn):9}: {n}/{t} reached")
    e = d["epistemisk"]
    kf, kt = e["kan_felles"]
    mo, mt = e["maaler_eller_observert"]
    print(f"  epistemic: {kf}/{kt} EFC claims can be felled · "
          f"{mo}/{mt} measure or are established")
    print(f"              prediction {e['prediksjon'][0]} · "
          f"settlement {e['oppgjoer'][0]}")
    for navn, hull in d["hull"].items():
        if hull:
            print(f"  HOLE {navn} ({len(hull)}): {', '.join(str(h) for h in hull[:5])}"
                  f"{' ...' if len(hull) > 5 else ''}")
    # A name that points at several nodes is not a hole — but it must be SEEN,
    # not settled in silence by a random order.
    for m, kandidater in d["kobling"]["motor_flertydig"].items():
        print(f"  AMBIGUOUS engine {m}: {', '.join(kandidater)} "
              f"(chose {d['kobling']['motor_til_node'][m]})")
