#!/usr/bin/env python3
"""atlas_feltvekt — is anyone READING this requirement? Measured by mutation.

The closure list said: stop requiring fields nobody reads. The first attempt at
that measured it by COUNTING: the field name was looked up in the five atlas
readers, and a field that appeared was called read. A count sees the word; it
does not see whether the field carries anything. `docs/atlas-lesing.md` states
the measured reason that fails: three tests that only required the words
"origin/main" and "working copy" to be present passed a mutant that said the
exact opposite.

So the instrument here is a MUTATION, not a count:

  1. the atlas is read from a ref, and a throwaway git repo is built holding
     only the files the readers need;
  2. for each requirement the field is EMPTIED (the key removed) on every node
     that carries it, and the mutation is committed to the throwaway repo;
  3. each of the five readers is asked again. A reader whose ANSWER changed
     reads the field. A reader that RAISES reads it too: it needed exactly
     what was taken away.

The question this answers is the one a count cannot: does the field carry
anything, or is a new node only filling in dead weight?

    python3 scripts/atlas_feltvekt.py . --ref origin/main

Declared limits, measured and deliberate:

  * "Emptied" means the KEY IS REMOVED, not set to an impossible value. For a
    field the schema requires that is the strongest reading of empty: no node
    has it at all.
  * The five readers are named in `atlas_lesing.LESERE`. `atlas_volum` reads
    the bus measurement and the coverage declaration, not the node fields —
    measured here as "no answer changes for any of the 22", which is a result
    and not a missing probe.
  * The field is emptied on EVERY carrier, but the node-specific readers are
    asked about the four carriers that carry the most text. If the answer does
    not move where the field is heaviest, it does not move anywhere else.
  * `efc_atlas_generator.hoved()` shells out to `node build.mjs`. The seam
    used here is the same two calls hoved() makes to turn the bank into atlas
    rows and the index: `[_node_rad(n, i) for ...]` and `_indeks(noder, rader)`.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROT = pathlib.Path(__file__).resolve().parents[1]
SKRIPT = ROT / "scripts"

for _sti in (SKRIPT, SKRIPT / "maintenance"):
    if str(_sti) not in sys.path:
        sys.path.insert(0, str(_sti))

import atlas_lesing as al          # noqa: E402
import atlas_inngang as ai         # noqa: E402
import atlas_navigasjon as an      # noqa: E402
import atlas_volum as av           # noqa: E402
import efc_atlas_generator as gen  # noqa: E402

LESERE = al.LESERE

#: Files a throwaway repo must hold for the five readers to answer at all.
#: `docs/concepts.jsonld` and `docs/ontology.jsonld` are optional registers:
#: they are copied when the ref has them, and their absence is not an error.
GRUNNFILER = ("schema/regime_nodes.jsonld", "schema/regime_node.schema.json",
              "schema/atlas_dekning.json", "schema/nats_domener.snapshot.json",
              "docs/concepts.jsonld", "docs/ontology.jsonld")

MOTORKATALOG = "efc_inference/engine"
MAKS_PROVER = 4
MAKS_NAALER = 3
MIN_ORD = 6

#: The commit a reader says it read changes WITH the mutation. A sha is not
#: evidence, and neither is the name of the ref, so both are removed before two
#: answers are compared.
_PROVENIENS = ("commit", "ref")
_SHA = re.compile(r"\b[0-9a-f]{7,40}\b")


class FeltvektFeil(RuntimeError):
    """The measurement could not be made. Never a guessed number."""


def _git(repo: pathlib.Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True)
    if p.returncode:
        raise FeltvektFeil(f"git {' '.join(args)} feilet i {repo}: "
                           f"{p.stderr.strip()}")
    return p.stdout


def _vis(repo: pathlib.Path, ref: str, sti: str) -> str:
    return _git(repo, "show", f"{ref}:{sti}")


def _uten_proveniens(v):
    if isinstance(v, dict):
        return {k: _uten_proveniens(x) for k, x in v.items()
                if k not in _PROVENIENS}
    if isinstance(v, list):
        return [_uten_proveniens(x) for x in v]
    return v


def kanon(v) -> str:
    """One answer, in the form two answers are compared in."""
    return _SHA.sub("<sha>", json.dumps(_uten_proveniens(v), sort_keys=True,
                                        ensure_ascii=False, default=str))


def _svar(fn, *a, **kw) -> str:
    """One reader answer — or the refusal it answered with.

    A raise is a reading: the reader needed exactly what the mutation took
    away. It is recorded with its type so the two answers can be compared.
    `SystemExit` is caught on purpose too: `efc_atlas_generator` refuses to
    build a bank it cannot place by raising it, and a refusal is an answer.
    """
    try:
        return kanon(fn(*a, **kw))
    except (Exception, SystemExit) as e:  # noqa: BLE001 - the reader's judgement
        return f"{type(e).__name__}: {e}"


def ord_i(v) -> list[str]:
    """Every word of six letters or more inside a field value, at any depth."""
    if isinstance(v, dict):
        return [w for x in v.values() for w in ord_i(x)]
    if isinstance(v, list):
        return [w for x in v for w in ord_i(x)]
    if isinstance(v, str):
        ut = []
        for w in v.replace("/", " ").replace(",", " ").split():
            w = "".join(c for c in w if c.isalnum() or c in "._-")
            if len(w) >= MIN_ORD:
                ut.append(w)
        return ut
    return []


def prover_noder(noder: list[dict], felt: str, maks: int = MAKS_PROVER) -> list[str]:
    """The nodes the field is asked about: the four heaviest carriers.

    Emptying happens on every carrier. The question is asked where the field
    carries the most text, for the same reason a magnet is tested at its
    strongest point: an answer that does not move there does not move.
    """
    bærere = [n for n in noder if n.get(felt) not in (None, "", [], {})]
    bærere.sort(key=lambda n: (-len(kanon(n.get(felt))), str(n.get("id"))))
    return [str(n["id"]) for n in bærere[:maks]]


def naaler(noder: list[dict], felt: str, maks: int = MAKS_NAALER) -> list[str]:
    """Questions the field itself answers: words out of its own values.

    The needle is taken FROM the field, never from its name, and the rarest
    words win: a word that sits in one node is one the answer can lose.
    """
    frek: dict[str, int] = {}
    for n in noder:
        for w in set(ord_i(n)):
            frek[w] = frek.get(w, 0) + 1
    kandidater: dict[str, int] = {}
    for n in noder:
        for w in set(ord_i(n.get(felt))):
            if felt.lower() in w.lower() or w.lower() in felt.lower():
                continue
            kandidater[w] = frek.get(w, 99)
    return [w for w, _ in sorted(kandidater.items(),
                                 key=lambda kv: (kv[1], kv[0]))[:maks]]


def _bygg(base: pathlib.Path, kilde: pathlib.Path, ref: str) -> str:
    """A throwaway repo with the bank and the declarations the readers need."""
    base.mkdir(parents=True, exist_ok=True)
    _git(base, "init", "-q", "-b", "main")
    _git(base, "config", "user.email", "feltvekt@local")
    _git(base, "config", "user.name", "atlas_feltvekt")
    for sti in GRUNNFILER:
        try:
            inn = _vis(kilde, ref, sti)
        except FeltvektFeil:
            continue
        p = base / sti
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(inn, encoding="utf-8")
    try:
        motorer = _vis(kilde, ref, MOTORKATALOG).splitlines()
    except FeltvektFeil:
        # A repo without an engine catalogue is a valid repo: git does not
        # track empty directories, and the readers name the absence.
        motorer = []
    for navn in motorer:
        if not navn.endswith(".py"):
            continue
        p = base / MOTORKATALOG / navn
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("", encoding="utf-8")
    _git(base, "add", "-A")
    _git(base, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "base")
    return _git(base, "rev-parse", "HEAD").strip()


def _prober(repo: pathlib.Path, ref: str, atlas: dict,
            ider: list[str], naaler_: list[str]) -> dict[str, dict]:
    """One answer per reader, from the ref that holds the mutated bank."""
    noder = atlas["noder"]
    rader = [_svar(gen._node_rad, n, i) for i, n in enumerate(noder)]
    dekning = av.les_fra_ref(repo, ref)
    hull = av.hull(dekning["dekning"].get("domener", {}), dekning["snapshot"])
    return {
        "atlas_lesing": {
            "akser": _svar(al.akser, atlas),
            "oversikt": _svar(al.oversikt, atlas),
            "maaleformer": _svar(al.maaleformer, atlas),
            "proxy_kjeder": _svar(al.proxy_kjeder, atlas),
            "plasser": _svar(al.plasser, atlas, "BAO maaling i galakser"),
            "helhet": [_svar(al.helhet, atlas, i) for i in ider],
            "naboer": [_svar(al.naboer, atlas, i) for i in ider],
            "hop": [_svar(al.hop, atlas, i, 2) for i in ider],
            "fragment": [_svar(al.fragment, atlas, i) for i in ider],
            "roter": _svar(al.roter, atlas, node=ider[0]),
            "roter_akse": [_svar(al.roter_akse, atlas, a)
                           for a in ("perspektiv", "phase", "synlighet")],
            "finn": [_svar(al.finn, repo, n, ref) for n in naaler_],
        },
        "atlas_inngang": {i: _svar(ai.read, repo, i, ref) for i in ider},
        "atlas_navigasjon": {"naviger": _svar(an.naviger, repo, ref)},
        "atlas_volum": {
            "hull": kanon(hull),
            "formater": _svar(av.format_table, hull),
            "meldinger": _svar(av.meldinger_per_domene, dekning["snapshot"]),
        },
        "efc_atlas_generator": {
            "rader": rader,
            "manglende_koder": _svar(gen.manglende_koder, noder),
            "foreldede_koder": _svar(gen.foreldede_koder, noder),
            "kollisjoner": _svar(gen.kollisjoner, noder),
            "indeks": _svar(gen._indeks, noder, rader),
            "sakse": [_svar(gen.sakse_tekst, n) for n in noder],
        },
    }


def maal(repo: str | pathlib.Path = ROT, ref: str = al.STANDARD_REF, *,
         bare: list[str] | None = None,
         maks_prover: int = MAKS_PROVER) -> dict:
    """Empty each requirement and measure which readers notice.

    Returns `{"kilde": ..., "lesere": [...], "felt": {felt: {...}}}` where each
    field carries the readers that CHANGED, the readers that did not, how many
    nodes carried it at all (`bar`), the nodes the question was asked about and
    the needles it was asked with.

    A field that NO node carries cannot be measured: emptying it changes the
    bank by nothing, so no reader can notice. It is reported with `bar: 0` and
    stays out of the table — an empty answer from a mutation that never
    happened is not a measurement.
    """
    kilde = pathlib.Path(repo)
    atlas = al.les_atlas(kilde, ref)
    krav = list(al.skjema_krav(atlas))
    krav += [f for f in al.HUSETS_KRAV if f not in krav]
    felt = [f for f in krav if bare is None or f in bare]

    tmp = pathlib.Path(tempfile.mkdtemp(prefix="atlas-feltvekt-"))
    try:
        grunn = _bygg(tmp, kilde, ref)
        sti = tmp / "schema" / "regime_nodes.jsonld"
        raa = json.loads(sti.read_text(encoding="utf-8"))
        atlas_grunn = al.les_atlas(tmp, grunn)
        ut: dict[str, dict] = {}
        for f in felt:
            ider = prover_noder(atlas_grunn["noder"], f, maks_prover)
            naaler_ = naaler(atlas_grunn["noder"], f)
            if not ider:
                ut[f] = {"lesere": [], "uendret": list(LESERE), "bar": 0,
                         "prover": [], "naaler": naaler_}
                continue
            data = json.loads(json.dumps(raa))
            for n in data["nodes"]:
                n.pop(f, None)
            sti.write_text(json.dumps(data, ensure_ascii=False, indent=1),
                           encoding="utf-8")
            _git(tmp, "add", "-A")
            _git(tmp, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
                 f"empty {f}")
            mut = _git(tmp, "rev-parse", "HEAD").strip()
            atlas_mut = al.les_atlas(tmp, mut)

            before = _prober(tmp, grunn, atlas_grunn, ider, naaler_)
            after = _prober(tmp, mut, atlas_mut, ider, naaler_)
            changed = [l for l in LESERE if before[l] != after[l]]
            ut[f] = {"lesere": changed,
                     "uendret": [l for l in LESERE if l not in changed],
                     "bar": len([n for n in atlas_grunn["noder"]
                                 if n.get(f) not in (None, "", [], {})]),
                     "prover": ider, "naaler": naaler_}
        return {"kilde": {"repo": str(kilde), "ref": ref,
                          "commit": atlas["commit"]},
                "lesere": list(LESERE), "felt": ut}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def tabell(maalt: dict) -> dict[str, tuple[str, ...]]:
    """The measured table, in the shape `atlas_lesing.FELT_LESERE` is written.

    Fields no node carries are left out on purpose: see `maal`.
    """
    return {f: tuple(v["lesere"]) for f, v in maalt["felt"].items()
            if v.get("bar", 1)}


def tabell_tekst(maalt: dict) -> str:
    linjer = [f"{maalt['kilde']['ref']} @ {maalt['kilde']['commit'][:8]} — "
              f"{len(maalt['felt'])} requirements, {len(maalt['lesere'])} readers"]
    for f, v in maalt["felt"].items():
        if not v.get("bar", 1):
            linjer.append(f"  {f:22} NOT MEASURED — no node in the bank "
                          f"carries it")
            continue
        linjer.append(f"  {f:22} {len(v['lesere'])}/{len(maalt['lesere'])}  "
                      f"{', '.join(v['lesere']) or '(no reader)'}")
    tomme = [f for f, v in maalt["felt"].items() if not v["lesere"]]
    linjer.append(f"requirements with no reader: {len(tomme)} of "
                  f"{len(maalt['felt'])}"
                  + (f" — {', '.join(tomme)}" if tomme else ""))
    return "\n".join(linjer)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Empty each requirement and measure which readers notice.")
    ap.add_argument("repo", nargs="?", default=".")
    ap.add_argument("--ref", default=al.STANDARD_REF)
    ap.add_argument("--felt", action="append", default=None,
                    help="measure only this requirement (repeatable)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--python", action="store_true",
                    help="print the measured table as it is written in "
                         "scripts/atlas_lesing.py")
    a = ap.parse_args(argv)
    try:
        maalt = maal(a.repo, a.ref, bare=a.felt)
    except (FeltvektFeil, al.AtlasLesingFeil) as e:
        print(f"SORRY: {e}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(maalt, ensure_ascii=False, indent=1))
    elif a.python:
        print("FELT_LESERE: dict[str, tuple[str, ...]] = {")
        for f, v in maalt["felt"].items():
            print(f"    {f!r}: {tuple(v['lesere'])!r},")
        print("}")
    else:
        print(tabell_tekst(maalt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
