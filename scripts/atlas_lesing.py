#!/usr/bin/env python3
"""atlas_lesing — read the atlas from a GIT REF, never from a working tree.

THE RULE AS CODE, not as prose. The reason is measured: a test that reads a
document can only see that the words are there, not what they mean. A mutant
that flipped the rule to «read from the working copy» passed three document
tests. The meaning must therefore live in a function that can be run and
mutated against.

The background, measured 2026-09-17: the atlas exists in several working
copies that do not show the same map. One working tree showed 72 nodes while
origin/main had 82; another clone sat on a later merged PR branch; a
maintenance worktree lacked `perspektiv` on all 45 nodes.

    A copy that answers reads like a living atlas.

The same failure mode as 2026-09-16 (atlas sync against components that were
not running) and 2026-09-14 (memory available, but not governing).

NOTE on freshness: `origin/main` is a remote-tracking ref and can be stale.
This module therefore does NOT fetch on its own — it reports which commit it
read, so that a stale ref is visible in the result instead of in the reader's
own assumption. `hent=False` is the default; set `hent=True` when the reader
wants the freshest possible.

THE API MAP — what the public functions take and give. Written 2026-09-18,
after a reader (me) guessed three of them wrong from memory: `finn` was
indexed as a list (it is a dict), `plasser` was read with a key that does not
exist, and `kjent_hull` was called under a name that was private. None of
them was a bug in the atlas — all were a bug in the interface.

    les_atlas(repo, ref)            -> dict   the whole atlas
    finn(repo, emne, ref)           -> dict   {antall, hull, for_bredt, raad, ...}
    akser(atlas)                    -> dict   {path: (count, example values)}
    roter_akse(atlas, akse, verdi)  -> list[dict]
    roter(atlas, node=, ...)        -> dict
    helhet(atlas, node_id)          -> dict   {episenter, felt, motor, ...}
    plasser(atlas, tekst)           -> dict   {status, forslag, naere_noder, ...}
    kjent_hull(repo, emne, ref)     -> dict | None
    naboer/hop/hop_stier/fragment   -> the coupling graph
    maaleformer/proxy_kjeder        -> what measures, through what

THE RULE they all follow: an entry point that does not know SAYS so. `finn`
answers «THE ATLAS DOES NOT KNOW» rather than giving a loose hit; `plasser`
answers `uten_hjem` rather than guessing a domain.
"""

from __future__ import annotations

import json
import datetime
import re
import subprocess
from pathlib import Path

STANDARD_REF = "origin/main"

# How many hits the CLI shows before it says «... and N more». An answer of
# 80 lines does not get read; the strongest hits are sorted first.
_VIS_MAKS = 15


class AtlasLesingFeil(RuntimeError):
    """The ref could not be read. Never a silent fallback to the working tree."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise AtlasLesingFeil(
            f"git {' '.join(args)} failed in {repo}: {p.stderr.strip()}")
    return p.stdout


def les_atlas(repo: str | Path, ref: str = STANDARD_REF, *,
              hent: bool = False, sti: str = "schema/regime_nodes.jsonld") -> dict:
    """Read the atlas from `ref` in `repo` — never from the working tree.

    Returns an object that NAMES the source it read, so that a stale or
    wrong ref is visible in the result.

    Raises AtlasLesingFeil if the ref does not exist. That is deliberate: a
    silent fallback to the working tree is exactly the failure mode this
    function exists to prevent.
    """
    repo = Path(repo)
    if hent:
        _git(repo, "fetch", "-q", "origin")
    commit = _git(repo, "rev-parse", ref).strip()
    raa = _git(repo, "show", f"{ref}:{sti}")
    try:
        data = json.loads(raa)
    except json.JSONDecodeError as e:
        raise AtlasLesingFeil(
            f"{ref}:{sti} in {repo} is not valid JSON: {e}") from e
    if not isinstance(data, dict) or "nodes" not in data:
        raise AtlasLesingFeil(
            f"{ref}:{sti} in {repo} is missing 'nodes' — "
            f"keys: {sorted(data)[:8] if isinstance(data, dict) else type(data).__name__}")
    return {
        "kilde": f"git:{ref}",
        "ref": ref,
        "commit": commit,
        "sti": sti,
        "noder": data["nodes"],
    }


def _har_falsifikator(node: dict) -> bool:
    """Does the node carry an observation that would fell it?

    `ville_falsifisere` is the name in the schema, measured 2026-09-17. A
    node that nothing can fell is a claim — and the reader must be able to
    see the difference without reading the whole node for themselves.
    """
    return "ville_falsifisere" in json.dumps(node, ensure_ascii=False)



def _dekning(repo: Path, ref: str, hent: bool) -> dict:
    """Read the coverage file from the SAME ref. Missing, the answer is empty — not a fault.

    The coverage status is its own artefact (`schema/atlas_dekning.json`),
    not a field on the nodes. Without this the lookup reads only the nodes
    and must answer «does not know» about something someone actually
    measured and found lacking.
    """
    try:
        raa = _git(repo, "show", f"{ref}:schema/atlas_dekning.json")
    except AtlasLesingFeil:
        return {"_mangler": True}
    try:
        d = json.loads(raa)
    except json.JSONDecodeError:
        return {"_mangler": True}
    dom = d.get("domener")
    return dom if isinstance(dom, dict) else {"_mangler": True}


def _kjent_hull(dekning: dict, naal: str) -> dict | None:
    """Is the subject a domain someone has measured? Searches the domain NAME, not the content.

    Only a hit on the name counts. A hit on a rationale would have turned
    «known» into «mentioned somewhere», and then the word loses its value.
    """
    if dekning.get("_mangler"):
        return None
    naal_lav = naal.lower()
    for domene, v in dekning.items():
        if not isinstance(v, dict):
            continue
        d_lav = domene.lower()
        if naal_lav == d_lav or naal_lav in d_lav.split("."):
            return {"domene": domene, "status": v.get("status"),
                    "noder": v.get("noder"), "begrunnelse": v.get("begrunnelse"),
                    # OPTIONAL: PR #475 puts a measured message volume per
                    # domain into the coverage file. If it is there, it is
                    # shown — and then a hole of 190 770 can be told apart
                    # from one of 228. If it is not there, the lookup works
                    # as before; a lookup that does not work before another
                    # PR lands is a lookup that does not work.
                    "meldinger": v.get("meldinger")}
    return None


def _norm(s: str) -> str:
    """Hyphen, underscore and space are the same separator.

    A lookup that cannot see that `energy-flow` and `energy flow` are the
    same word answers «does not know» about a word it actually owns.
    """
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def finn(repo: str | Path, emne: str, ref: str = STANDARD_REF, *,
         hent: bool = False) -> dict:
    """Look up a subject in the atlas — reads from `ref`, never from the working tree.

    The difference from `les_atlas`: this one answers a QUESTION. `les_atlas`
    gives you the whole map and lets you search; the price is that the atlas
    is not consulted on its own. Measured 2026-09-17: the module had an exit
    and no entrance.

    The answer is ALWAYS shaped the same way, also when it is empty:

        {"emne", "antall", "hull", "treff", "kilde", "ref", "commit"}

    `hull: True` means «the atlas does not know» — that is an answer, not a
    fault, and it can be told apart from a fault because a fault RAISES. A
    lookup that cannot say «I do not know» says «no» out of ignorance.

    Every hit names its epistemic status, so that the reader does not have
    to read the whole node to know what is established and what is
    stipulated.
    """
    if not emne or not emne.strip():
        raise AtlasLesingFeil(
            "empty subject — a lookup without a question would have matched "
            "everything and thereby answered nothing")
    atlas = les_atlas(repo, ref, hent=hent, sti="schema/regime_nodes.jsonld")
    # Measured 2026-09-18: `--emne "energy-flow"` hit, `--emne "energy flow"`
    # gave 0 hits. The words Morten uses have BOTH forms, and a lookup that
    # cannot see that answers «does not know» about a word it actually owns.
    naal = _norm(emne)
    if not naal:
        raise AtlasLesingFeil("empty subject after normalisation")
    dekning = _dekning(Path(repo), ref, hent)
    spoersmaalsakse = _loes_spoersmaalsakse(atlas, emne)
    if spoersmaalsakse:
        treff = []
        for n in roter_akse(atlas, spoersmaalsakse):
            treff.append({
                "trefftype": "akse",
                "id": n.get("id"),
                "synlighet": n.get("synlighet"),
                "perspektiv": n.get("perspektiv"),
                "fase": n.get("phase"),
                "buss_domene": n.get("buss_domene"),
                "har_prediksjon": bool(n.get("prediction")),
                "har_oppgjoer": bool(n.get("settlement")),
                "har_falsifikator": _har_falsifikator(n),
            })
        return {
            "emne": emne, "akse": spoersmaalsakse,
            "kilde": atlas["kilde"], "ref": ref, "commit": atlas["commit"],
            "antall": len(treff), "hull": not treff, "for_bredt": False,
            "raad": None, "kjent_hull": _kjent_hull(dekning, naal),
            "dekning_fil": "schema/atlas_dekning.json", "treff": treff,
        }
    # `\b` counts `_` as a WORD CHARACTER. But in node ids `_` SEPARATES
    # parts: `homo.sovn_vaaken`, `efc.solar_flare_engine`. With `\b`, `sovn`
    # was weakened to a substring even though it is its own part of the id
    # (measured in review 2026-09-17). We therefore define the word
    # character explicitly, so that `_`, `.` and `-` are all separators —
    # and `sol` in `solid` is still a substring.
    # THE CHARACTER SET IS DATA: it defines the word boundaries the search
    # uses, so the value must not move. It carries the Norwegian letters
    # verbatim and is therefore a DECLARED residual in the language gate's
    # baseline -- escaping it would hide the residual instead of recording it.
    _ORDTEGN = "a-z0-9æøå"
    ordmonster = re.compile(
        rf"(?<![{_ORDTEGN}])" + re.escape(naal) + rf"(?![{_ORDTEGN}])")
    treff = []
    for n in atlas["noder"]:
        tekst = _norm(json.dumps(n, ensure_ascii=False))
        if naal not in tekst:
            continue
        # Three levels, not two. «sol» hit `batteri.lading` as a WORD —
        # because the word exists in a text inside the node — but the node
        # is not about the sun. And «sol» hit `h2o.solid` as a substring of
        # «solid». Without the distinction the reader must guess which hits
        # are real.
        id_tekst = str(n.get("id", "")).lower()
        buss = str(n.get("buss_domene") or "").lower()
        if ordmonster.search(id_tekst):
            trefftype = "id"
        elif buss and (naal == buss or naal in buss.split(".")):
            # A node that COVERS the domain `verden.energi` is relevant for
            # «energi» even though the word only stands in the prose. Without
            # this, `efc.enerflyt_engine` ranked as loose prose.
            trefftype = "domene"
        elif ordmonster.search(tekst):
            trefftype = "ord"
        else:
            trefftype = "delstreng"
        treff.append({
            "trefftype": trefftype,
            "id": n.get("id"),
            "synlighet": n.get("synlighet"),
            "perspektiv": n.get("perspektiv"),
            "fase": n.get("phase"),
            "buss_domene": n.get("buss_domene"),
            "har_prediksjon": bool(n.get("prediction")),
            "har_oppgjoer": bool(n.get("settlement")),
            "har_falsifikator": _har_falsifikator(n),
        })
    _rang = {"id": 0, "domene": 1, "ord": 2, "delstreng": 3}
    # Within the same rank: public before internal. The public ones are the
    # core of the published atlas; the internal ones are context.
    treff.sort(key=lambda x: (_rang[x["trefftype"]],
                              x["synlighet"] != "offentlig",
                              x["id"] or ""))
    # «Too broad» rests on whether the search has ANYTHING PRECISE — not on
    # a count.
    #
    # The first version used «>50 hits or >60 % of the atlas». Review round 4
    # measured it against real questions: sol=20, energi=25, kosmos=32, h2o=36
    # — all far below, instrument=82 above. No real question came near, so
    # the number was guessed. Worse: `efc` gives 68 hits of which 32 are
    # PRECISE — a count threshold called that broad, which is the exact
    # opposite.
    #
    # The criterion is therefore: a hit is precise if it stands in the node
    # id or covers a bus domain. If there are no precise hits AND the answer
    # does not fit the display, the search is broad — no matter how large the
    # atlas grows.
    presise = [t for t in treff if t["trefftype"] in ("id", "domene")]
    for_bredt = not presise and len(treff) > _VIS_MAKS
    raad = None
    if for_bredt:
        raad = (f"no precise hits — all {len(treff)} are loose prose. "
                f"Use a more precise subject, or see the strongest below")
    return {
        "emne": emne,
        "akse": None,
        "kilde": atlas["kilde"],
        "ref": ref,
        "commit": atlas["commit"],
        "antall": len(treff),
        "hull": len(treff) == 0,
        "for_bredt": for_bredt,
        "raad": raad,
        "kjent_hull": _kjent_hull(dekning, naal),
        "dekning_fil": "schema/atlas_dekning.json",
        "treff": treff,
    }


# ---------------------------------------------------------------------------
# ROTATION — seeing the structure from every angle, not just looking up a subject
#
# Measured 2026-09-17: the tool had four flags (`--emne`, `--ref`, `--hent`,
# `--alle`). It could look up and list. It could NOT filter on perspektiv,
# could not tell a measured node from a derived one, could not show
# proxy chains. The rotation did not exist.
# ---------------------------------------------------------------------------

#: Phases where the node MEASURES something — it has an instrument in the world.
_MAALENDE_FASER = frozenset({"instrument", "observasjon"})

#: Phases where the node is DERIVED — computed, not measured.
_AVLEDEDE_FASER = frozenset({"regime_engine", "computation_engine",
                             "teoretisk", "stabil"})


def roter(atlas: dict, *, node: str | None = None,
          perspektiv: str | None = None, fase: str | None = None,
          domene: str | None = None) -> list[dict]:
    """Rotate through the atlas across the fields.

    One call, one angle. `node` gives the WHOLE node — every field, not a
    selection. `KeyError` when the node does not exist: an empty answer would
    have hidden that the name was wrong.
    """
    noder = atlas.get("noder") or []
    if node is not None:
        funn = [n for n in noder if n.get("id") == node]
        if not funn:
            raise KeyError(f"the node `{node}` does not exist in the atlas")
        return funn
    if perspektiv is not None:
        noder = [n for n in noder if n.get("perspektiv") == perspektiv]
    if fase is not None:
        noder = [n for n in noder if n.get("phase") == fase]
    if domene is not None:
        noder = [n for n in noder if n.get("buss_domene") == domene]
    return noder


def maaleformer(atlas: dict) -> dict[str, list[str]]:
    """Tell what MEASURES from what is derived.

    «measures or is established» was ONE number for 47 very different nodes.
    It does not tell a thermometer from a numerical solver. Here they are
    split.
    """
    ut: dict[str, list[str]] = {"instrument": [], "avledet": [], "ingen": []}
    for n in atlas.get("noder") or []:
        fase = n.get("phase")
        m = n.get("measure") or {}
        if fase in _MAALENDE_FASER:
            ut["instrument"].append(n["id"])
        elif fase in _AVLEDEDE_FASER or fase == "regime_engine":
            ut["avledet"].append(n["id"])
        elif m.get("instrument"):
            ut["instrument"].append(n["id"])
        else:
            ut["ingen"].append(n["id"])
    return ut


def proxy_kjeder(atlas: dict) -> dict[str, list[str]]:
    """What goes through what — at every step.

    `measure.proxy_chain` says which steps separate the measured from the
    concluded. A node without a chain says that it reads directly; one with
    three steps says that three things must hold.
    """
    ut: dict[str, list[str]] = {}
    for n in atlas.get("noder") or []:
        kjede = ((n.get("measure") or {}).get("proxy_chain")) or []
        if kjede:
            ut[n["id"]] = list(kjede)
    return ut



# ---------------------------------------------------------------------------
# THE AXES — all of them, not the six I happened to build
#
# Measured 2026-09-17: the atlas carried 21 top-level fields, all mandatory on
# all 86 nodes. The rotation covered six. Fifteen were invisible to the tool.
# The solution is not twenty flags: it is to FIND the axes themselves, so an
# axis added tomorrow also works tomorrow.
# ---------------------------------------------------------------------------

def _bla(sti: str, v, ut: dict) -> None:
    """Walk through a node and collect every path as an axis.

    Both the leaf AND the parent are registered: `analogi.avbildning` is
    useful, but `analogi` is the axis — a node that HAS the isomorphism must
    be findable on it.
    """
    if isinstance(v, dict):
        ut.setdefault(sti, []).append(f"<{len(v)} fields>")
        for k, x in v.items():
            _bla(f"{sti}.{k}", x, ut)
    elif isinstance(v, list):
        ut.setdefault(sti, []).extend(str(x) for x in v)
    elif v is None:
        # `None` is not a value. `str(None)` became literally «None»,
        # which is truthy — and made `nivaa.forelder` an axis with 113
        # nodes answering 33, with «None» as an offered value.
        # Measured 2026-09-18.
        return
    else:
        ut.setdefault(sti, []).append(str(v))


def akser(atlas: dict) -> dict[str, tuple[int, list[str]]]:
    """Find ALL the axes in the atlas — also the ones that did not exist yesterday.

    Returns `{path: (count, example values)}` — one entry per path, with the
    number of nodes that carry it and the example values the path takes.
    Nested fields are addressed with a dot: `emergence.loop`,
    `epistemikk.sannhetsstatus`.
    """
    raa: dict[str, set] = {}
    antall: dict[str, int] = {}
    for n in atlas.get("noder") or []:
        blad: dict[str, list] = {}
        for k, v in n.items():
            _bla(k, v, blad)
        for sti, verdier in blad.items():
            # An axis exists only if it HAS a value. `nivaa.forelder` is
            # `None` on 80 of 113 nodes; counting those as a value made the
            # axis offer 113 and answer 33. Measured 2026-09-18.
            if not any(v for v in verdier):
                continue
            antall[sti] = antall.get(sti, 0) + 1
            raa.setdefault(sti, set()).update(v for v in verdier if v)
    return {sti: (antall[sti], sorted(raa[sti])[:6]) for sti in antall}


def _les_sti(n: dict, akse: str):
    """Read a dot path from a node. `None` if it does not exist."""
    v = n
    for del_ in akse.split("."):
        if not isinstance(v, dict) or del_ not in v:
            return None
        v = v[del_]
    return v


#: The names MORTEN uses against the paths the atlas actually carries. Measured
#: 2026-09-17: `isomorphisme` is `analogi`, `loop` is `emergence.loop`,
#: and `paradigme`/`konsensus`/`akademia` are VALUES of `perspektiv` —
#: not axes. Three different classes; without this layer they look alike.
AKSE_ALIAS: dict[str, str] = {
    "isomorphisme": "analogi",
    "isomorfi": "analogi",
    "isomorfisme": "analogi",
    "loop": "emergence.loop",
    "loops": "emergence.loop",
    "sloeyfe": "emergence.loop",
    "sloyfe": "emergence.loop",
    "fraktal": "fractal.pattern",
    "fraktaler": "fractal.pattern",
    "hva_maales": "measure.target",
    "hvem_maaler": "measure.measurer",
    "hvor_maales": "measure.placement",
    "maaleinstrument": "measure.instrument",
    "instrument": "measure.instrument",
    "proxy": "measure.proxy_chain",
    "proxyer": "measure.proxy_chain",
    "observatoer": "observer",
    "kobling": "coupling",
    "domenet": "buss_domene",
    "domene": "buss_domene",
    "antakelser": "ontology.assumes",
    "kompresjon": "measure.compression",
    "rom": "nivaa.lengdeskala",
    "tid": "nivaa.tidsskala",
    "enheter": "maale_paradigme.enheter",
    "koordinater": "maale_paradigme.koordinater",
    "S": "maale_paradigme.s_regime",
    "s": "maale_paradigme.s_regime",
    "s_regime": "maale_paradigme.s_regime",
    "s-akse": "maale_paradigme.s_regime",
    "s-ax": "maale_paradigme.s_regime",
    "sannhet": "epistemikk.sannhetsstatus",
    "evidens": "epistemikk.evidensstatus",
}

# The owner's question forms are their own name layer, not free text that is
# hoped to hit in the node prose. Normalised keys make space, hyphen and
# underscore follow the same rule as the rest of the lookup.
SPOERSMAAL_AKSE: dict[str, str] = {
    "hva maaler": "measure.target",
    "hva maales": "measure.target",
    "hva måler": "measure.target",
    "hva måles": "measure.target",
    "hvem maaler": "measure.measurer",
    "hvem måler": "measure.measurer",
    "hvor maaler": "measure.placement",
    "hvor maales": "measure.placement",
    "hvor måler": "measure.placement",
    "hvor måles": "measure.placement",
    # THE KEY IS DATA: the owner's question forms are looked up verbatim, so
    # the value must not move. It is a DECLARED residual in the language
    # gate's baseline rather than hidden behind an escape.
    "med hva": "measure.instrument",
    "hvilket instrument": "measure.instrument",
    "via hvilken proxy": "measure.proxy_chain",
    "hvilke proxyer": "measure.proxy_chain",
    "hva komprimerer": "measure.compression",
}


def _loes_spoersmaalsakse(atlas: dict, spoersmaal: str) -> str | None:
    """Resolve an explicit question form, otherwise None — never a guess."""
    akse = SPOERSMAAL_AKSE.get(_norm(spoersmaal))
    if akse and akse in akser(atlas):
        return akse
    return None


def _loes_akse(atlas: dict, akse: str) -> tuple[str, str | None]:
    """Resolve a human name to (path, value). Three classes.

    1. THE NAME IS THE PATH       -> (path, None)
    2. THE NAME IS AN ALIAS       -> (path, None)
    3. THE NAME IS A VALUE        -> (perspektiv, verdi)  <- third class
    """
    alle = akser(atlas)
    if akse in alle:
        return akse, None
    if akse in AKSE_ALIAS and AKSE_ALIAS[akse] in alle:
        return AKSE_ALIAS[akse], None
    # third class: is it a VALUE of a known axis?
    for sti in ("perspektiv", "phase", "maale_paradigme.status",
                "epistemikk.sannhetsstatus", "epistemikk.evidensstatus"):
        verdier = alle.get(sti, (0, []))[1]
        if akse in verdier:
            return sti, akse
    raise KeyError(akse)


def oversikt(atlas: dict) -> list[tuple[str, list[tuple[str, int]]]]:
    """The WHOLE atlas at once — what is what, where, how many.

    Measured 2026-09-17: the rotation answered ONE question at a time. Morten:
    «ALL of this should be global in the atlas and you should immediately know
    what is what where etc». That is not a search — it is the state.
    """
    alle = akser(atlas)
    noder = atlas.get("noder") or []
    ut: list[tuple[str, list[tuple[str, int]]]] = []
    for sti in sorted(alle):
        telling: dict[str, int] = {}
        for n in noder:
            v = _les_sti(n, sti)
            if v is None:
                continue
            ledd = v if isinstance(v, list) else [v]
            for x in ledd:
                telling[str(x)] = telling.get(str(x), 0) + 1
        if not telling:
            continue
        fordeling = sorted(telling.items(), key=lambda x: -x[1])
        # only axes that DISTINGUISH, and only short values: free text is
        # not a category. «Immediately» means it must be readable.
        if len(fordeling) < 2:
            continue
        if any(len(v) > 34 or " " in v for v, _ in fordeling[:8]):
            continue
        ut.append((sti, fordeling))
    return ut


def roter_akse(atlas: dict, akse: str, verdi: str | None = None) -> list[dict]:
    """Rotate around ONE axis — top level or nested.

    `verdi=None` gives every node that HAS the axis. An unknown axis fails
    loudly with suggestions, because an empty answer would have hidden that
    the name was wrong.
    """
    alle = akser(atlas)
    try:
        akse, l_a_verdi = _loes_akse(atlas, akse)
        if l_a_verdi is not None and verdi is None:
            verdi = l_a_verdi
    except KeyError:
        rot = akse.split(".")[0]
        naere = sorted(a for a in alle
                       if rot in a or a.split(".")[0] in akse
                       or akse in AKSE_ALIAS)[:5]
        if not naere:  # no similarity — show the most used
            naere = [a for a, _ in sorted(alle.items(),
                                          key=lambda x: -x[1][0])[:6]]
        raise KeyError(
            f"the axis `{akse}` does not exist in the atlas. "
            f"Nearby: {', '.join(naere) if naere else 'none'}")
    ut = []
    for n in atlas.get("noder") or []:
        v = _les_sti(n, akse)
        # Empty list and empty string are not a value. `emergence.properties`
        # is `[]` on 99 of 113 nodes; counting those made the axis answer
        # 113 where it had 99. Measured 2026-09-18.
        if v is None or (isinstance(v, (list, str, dict)) and not v):
            continue
        if verdi is None:
            ut.append(n)
            continue
        str_v = [str(x) for x in v] if isinstance(v, list) else [str(v)]
        if verdi in str_v:
            ut.append(n)
    return ut



# ---------------------------------------------------------------------------
# THE COUPLINGS — 1-hop, 2-hop, 3-hop
#
# Measured 2026-09-18: the tool had `--emne`, `--akse`, `--node`,
# `--oversikt` and `--proxy`. It had NO hops. The couplings were in the
# data — nivaa.forelder, coupling, analogi, stipulasjoner.motor,
# buss_domene, measure.proxy_chain — and none of them could be FOLLOWED.
# ---------------------------------------------------------------------------

def _mekanisme(noder: list[dict]) -> dict[str, dict]:
    return {x["id"]: x for x in noder}


def _koblinger(n: dict, atlas: dict) -> dict[str, list[str]]:
    """Which nodes hang together with this one, and HOW.

    The coupling type is the point: «same domain» is weaker than «is a
    parent».
    """
    noder = atlas.get("noder") or []
    idx = _mekanisme(noder)
    ut: dict[str, list[str]] = {}

    forelder = (n.get("nivaa") or {}).get("forelder")
    if forelder and forelder in idx:
        ut["forelder"] = [forelder]

    barn = [x["id"] for x in noder
            if (x.get("nivaa") or {}).get("forelder") == n["id"]]
    if barn:
        ut["barn"] = barn

    dom = n.get("buss_domene")
    if dom:
        ut["samme_domene"] = [i for i, x in idx.items()
                              if i != n["id"] and x.get("buss_domene") == dom]

    if isinstance(n.get("analogi"), dict):
        ut["deler_analogi"] = [i for i, x in idx.items()
                               if i != n["id"] and isinstance(x.get("analogi"), dict)]

    motor = (n.get("stipulasjoner") or {}).get("motor")
    if motor:
        ut["samme_motor"] = [
            i for i, x in idx.items() if i != n["id"]
            and (x.get("stipulasjoner") or {}).get("motor") == motor]

    kilde = (n.get("ontology") or {}).get("source")
    if kilde:
        ut["samme_kilde"] = [
            i for i, x in idx.items() if i != n["id"]
            and (x.get("ontology") or {}).get("source") == kilde]

    ledd = set(((n.get("measure") or {}).get("proxy_chain")) or [])
    if ledd:
        ut["deler_proxy_ledd"] = [
            i for i, x in idx.items() if i != n["id"]
            and ledd.intersection(
                set(((x.get("measure") or {}).get("proxy_chain")) or []))]
    return ut


def naboer(atlas: dict, node_id: str) -> dict[str, list[str]]:
    """1-HOP: what hangs together with this one, and how. `KeyError` if unknown."""
    for n in atlas.get("noder") or []:
        if n["id"] == node_id:
            return _koblinger(n, atlas)
    raise KeyError(f"the node `{node_id}` does not exist in the atlas")


def hop(atlas: dict, node_id: str, d: int = 1) -> list[str]:
    """All nodes within `d` hops — the start node itself not included."""
    naboer(atlas, node_id)  # validates that the node exists
    sett = {node_id}
    front = {node_id}
    for _ in range(max(0, d)):
        ny: set[str] = set()
        for x in front:
            try:
                kob = naboer(atlas, x)
            except KeyError:
                continue
            for ider in kob.values():
                ny.update(ider)
        ny -= sett
        sett |= ny
        front = ny
    sett.discard(node_id)
    return sorted(sett)


def hop_stier(atlas: dict, node_id: str,
              d: int = 2) -> dict[str, tuple[list[str], list[str]]]:
    """The paths, not just the set: WHY they hang together.

    Returns `{node: (the path, the coupling types along the path)}`.
    """
    ut: dict[str, tuple[list[str], list[str]]] = {}
    sett = {node_id}
    front: list[tuple[str, list[str], list[str]]] = [(node_id, [node_id], [])]
    for _ in range(max(0, d)):
        ny: list[tuple[str, list[str], list[str]]] = []
        for x, sti, typer in front:
            try:
                kob = naboer(atlas, x)
            except KeyError:
                continue
            for type_, ider in kob.items():
                for i in ider:
                    if i in sett:
                        continue
                    sett.add(i)
                    ny.append((i, sti + [i], typer + [type_]))
                    ut[i] = (sti + [i], typer + [type_])
        front = ny
    return ut


def fragment(atlas: dict, node_id: str) -> dict:
    """Rotate around ONE fragment: the node, its couplings, and the
    neighbours of the neighbours.

    «rotate around every fragment an observation we make» — when an
    observation comes in, it must be possible to put it in and see it from
    every side.
    """
    treff = [x for x in atlas.get("noder") or [] if x["id"] == node_id]
    if not treff:
        rot = node_id.split(".")[0]
        return {"finnes": False, "sokt": node_id,
                "naere": [x["id"] for x in atlas.get("noder") or []
                          if rot in x["id"]][:5]}
    n = treff[0]
    kob = _koblinger(n, atlas)
    return {
        "finnes": True,
        "node": n,
        "koblinger": kob,
        "ett_hopp": len({i for ider in kob.values() for i in ider}),
        "to_hopp": len(hop(atlas, node_id, 2)),
        "tre_hopp": len(hop(atlas, node_id, 3)),
    }


def plasser(atlas: dict, tekst: str) -> dict:
    """Place a NEW fragment — and say what remains.

    The entrance is not a hole. It is a list of what the fragment must fill
    in to become a node: which domain it belongs to, which nodes it
    resembles, and which fields are missing.
    """
    if not tekst.strip():
        return {"status": "tomt", "forslag": [], "mangler": []}

    alle = akser(atlas)
    ord_i = {w for w in _norm(tekst).split() if len(w) > 2}
    noder = atlas.get("noder") or []

    # which domains do the words name?
    domener = alle.get("buss_domene", (0, []))[1]
    treff_domener = [d for d in domener
                     if any(w in _norm(d) for w in ord_i)]

    # which nodes share words with the fragment? The weight is put where the
    # word ACTUALLY describes something: the target and the regime, not every
    # text in the node.
    def _stamme(a: str, b: str, n: int = 5) -> bool:
        """«vulkansk» and «vulkan» are the same word to a human, not to ==."""
        return len(a) >= n and len(b) >= n and a[:n] == b[:n]

    def vekt(n: dict) -> int:
        m = n.get("measure") or {}
        r = n.get("regime") or {}
        tung = _norm(" ".join(str(m.get(k) or "") for k in
                              ("target", "measurer", "instrument"))
                     + " " + str(r.get("name") or "") + " " + str(r.get("validity") or ""))
        ord_t = set(tung.split())
        return sum(1 for w in ord_i
                   if w in ord_t or any(_stamme(w, x) for x in ord_t))

    naere = [(vekt(n), n["id"]) for n in noder]
    naere = sorted((x for x in naere if x[0] > 0), key=lambda x: -x[0])
    naere_noder = [i for _, i in naere[:6]]

    forslag = []
    for d in treff_domener:
        eiere = [n["id"] for n in noder if n.get("buss_domene") == d]
        forslag.append({"domene": d, "noder": eiere[:4],
                        "kobling": "the domain is named in the fragment"})
    if not forslag and naere_noder:
        forslag.append({"domene": "(avledet)", "noder": naere_noder[:4],
                        "kobling": "the domain is named in the fragment"})
    if not forslag:
        # no domain string matched: use the DOMAINS OF THE NEARBY NODES.
        # The fallback must not suggest the alphabet — it must suggest what
        # the fragment RESEMBLES. (Measured 2026-09-18: «vulkansk aske»
        # pointed at kosmos.asteroider/galakser/hoper, that is only the
        # first three.)
        sett: list[str] = []
        for _, nid in naere[:8]:
            x = next((y for y in noder if y["id"] == nid), None)
            d = (x or {}).get("buss_domene")
            if d and d not in sett:
                sett.append(d)
        forslag = [{"domene": d, "noder": [],
                    "kobling": "word similarity — not a known domain choice"}
                   for d in sett[:4]]
        if not forslag:
            forslag = [{"domene": d, "noder": [],
                        "kobling": "no idea — alphabetical display, not a suggestion"}
                       for d in alle.get("buss_domene", (0, []))[1][:3]]

    # what must be filled in? compared against a typical FULL node
    typisk = set()
    for n in noder:
        typisk |= set(n.keys())
    typisk -= {"id", "buss_domene", "prediction", "settlement",
               "ville_falsifisere", "analogi", "falsifiserbarhet"}
    mangler = sorted(typisk)

    if forslag and len(treff_domener) > 0:
        status = "hjem_funnet"
        domene_visshet = "vet"
        domene_grunnlag = "explicit hit on a bus domain"
    elif naere_noder and naere[0][0] >= 2:
        status = "svakt"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "word similarity only — not a known domain"
    else:
        status = "uten_hjem"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "no domain guess"

    return {
        "status": status,
        "domene_visshet": domene_visshet,
        "domene_grunnlag": domene_grunnlag,
        "tekst": tekst,
        "forslag": forslag,
        "naere_noder": naere_noder,
        "mangler": mangler,
        "aksene": {k: alle[k][1][:6] for k in
                   ("perspektiv", "phase", "synlighet") if k in alle},
    }


# ---------------------------------------------------------------------------
# THE WHOLE — everything about a node, in one reading
#
# Morten, 2026-09-18: «if we are talking about h2o, BAO, the rainbow or
# victron now, you should immediately get a local-global interconnection via
# the atlas, see emergence, see the epicentre, the vectors, the fields, the
# domain, the cross domain, more hops in all directions, see paradigme, see
# konsensus, see akademia, see emergence, see all the fractals the measured
# emergence has, be able to rotate around what we measure, know what we
# measure, whether it is via a proxy, with which measurement methods, and the
# instrument».
#
# Measured before: the answer existed only as thirteen separate commands.
# ---------------------------------------------------------------------------

def kjent_hull(repo: str | Path, emne: str,
               ref: str = STANDARD_REF, *, hent: bool = False) -> dict | None:
    """Is the subject a KNOWN hole — a domain someone has measured and found empty?

    This is the public entrance. The private `_kjent_hull` takes the coverage
    file that is already read; this one does the lookup itself, because a
    reader who asks «is this a known hole?» does not have the coverage file
    at hand — they have a subject.

    Written 2026-09-18: `kjent_hull` existed, but was called `_kjent_hull`
    and took a different parameter than the one a reader would have guessed.
    An entrance that cannot be found does not work — no matter how correct
    it is.
    """
    return _kjent_hull(_dekning(Path(repo), ref, hent), emne)


def helhet(atlas: dict, node_id: str) -> dict:
    """EVERYTHING about a node — the six parts, in one reading.

    Not a summary: each part is the raw value from the node, because a
    summary would have hidden exactly what is being asked about.
    """
    treff = [x for x in atlas.get("noder") or [] if x["id"] == node_id]
    if not treff:
        rot = node_id.split(".")[0]
        return {"finnes": False, "sokt": node_id,
                "naere": [x["id"] for x in atlas.get("noder") or []
                          if rot in x["id"]][:6]}
    n = treff[0]
    m = n.get("measure") or {}
    epi = n.get("epistemikk") or {}
    em = n.get("emergence") or {}
    fr = n.get("fractal") or {}
    reg = n.get("regime") or {}

    # THE COUPLINGS, both ways: «more hops in all directions»
    ut = _koblinger(n, atlas)
    ut_ider = {i for ider in ut.values() for i in ider}
    inn: dict[str, list[str]] = {}
    for x in atlas.get("noder") or []:
        if x["id"] == node_id:
            continue
        try:
            k = _koblinger(x, atlas)
        except KeyError:
            continue
        if node_id in {i for ider in k.values() for i in ider}:
            typer = [t for t, ider in k.items() if node_id in ider]
            inn[x["id"]] = typer

    # CROSS DOMAIN: which OTHER domains the node reaches via hops
    eget = n.get("buss_domene")
    kryss: list[str] = []
    for i in ut_ider | set(inn):
        x = next((y for y in atlas["noder"] if y["id"] == i), None)
        d = (x or {}).get("buss_domene")
        if d and d != eget and d not in kryss:
            kryss.append(d)

    return {
        "finnes": True,
        "id": node_id,
        "node": n,
        "episenter": n.get("episenter"),
        "felt": reg,
        "domene": eget,
        "maal": {
            "hva": m.get("target"),
            "hvem": m.get("measurer"),
            "hvor": m.get("placement"),
            "instrument": m.get("instrument"),
            "proxy": m.get("proxy_chain") or [],
            "kompresjon": m.get("compression"),
        },
        "perspektiv": {
            "perspektiv": n.get("perspektiv"),
            "sannhetsstatus": epi.get("sannhetsstatus"),
            "konsensusstatus": epi.get("konsensusstatus"),
            "evidensstatus": epi.get("evidensstatus"),
            "sosial_mekanisme": epi.get("sosial_mekanisme"),
            "konsensus_er_ikke_sannhet": epi.get("konsensus_er_ikke_sannhet"),
        },
        "emergence": em,
        "fraktaler": [fr.get("pattern"), fr.get("note")] + (em.get("properties") or []),
        "motor": (n.get("stipulasjoner") or {}).get("motor") or None,
        "stipulasjoner": n.get("stipulasjoner") or {},
        "observer": n.get("observer") or {},
        "coupling": n.get("coupling") or {},
        "buffer": n.get("buffer") or {},
        "ontology": n.get("ontology") or {},
        "maale_paradigme": n.get("maale_paradigme") or {},
        "nivaa": n.get("nivaa") or {},
        "koblinger": {"ut": ut, "inn": inn},
        "kryssdomene": kryss,
        "ett_hopp": len(ut_ider),
        "to_hopp": len(hop(atlas, node_id, 2)),
        "tre_hopp": len(hop(atlas, node_id, 3)),
        "falsifiserbarhet": n.get("ville_falsifisere"),
    }


def helhet_tekst(atlas: dict, node_id: str) -> str:
    """The whole as readable text — for the CLI and for the eye."""
    h = helhet(atlas, node_id)
    if not h["finnes"]:
        return (f"ERROR: `{node_id}` does not exist. Nearby: "
                f"{', '.join(h['naere']) or 'none'}")
    L: list[str] = [f"=== {h['id']} ==="]
    L.append(f"  felt/regime : {h['felt'].get('name', '?')}")
    v = h["felt"].get("validity")
    if v:
        L.append(f"  validity    : {v[:150]}")
    L.append(f"  domene      : {h['domene'] or '(none)'}")
    L.append(f"  motor       : {h.get('motor') or '(none — not an engine node)'}")
    L.append(f"  episenter   : {h['episenter'] or '(none)'}")
    L.append("")
    L.append("  THE MEASUREMENT")
    for k, navn in (("hva", "hva"), ("hvem", "hvem"), ("hvor", "hvor"),
                    ("instrument", "instrument"), ("kompresjon", "kompresjon")):
        if h["maal"].get(k):
            L.append(f"    {navn:11} {str(h['maal'][k])[:130]}")
    if h["maal"]["proxy"]:
        L.append(f"    proxy       {' -> '.join(str(x) for x in h['maal']['proxy'])[:130]}")
    else:
        L.append("    proxy       none — read directly")
    L.append("")
    L.append("  THE PERSPECTIVE")
    for k in ("perspektiv", "sannhetsstatus", "konsensusstatus",
              "evidensstatus", "sosial_mekanisme"):
        if h["perspektiv"].get(k):
            L.append(f"    {k:16} {str(h['perspektiv'][k])[:120]}")
    L.append("")
    L.append(f"  EMERGENCE   {str(h['emergence'].get('loop'))[:130]}")
    L.append(f"  FRACTALS    {len(h['fraktaler'])} parts")
    for f in h["fraktaler"][:3]:
        if f:
            L.append(f"    - {str(f)[:120]}")
    L.append("")
    L.append(f"  COUPLINGS   1-hop {h['ett_hopp']} · 2-hop {h['to_hopp']} · "
             f"3-hop {h['tre_hopp']}")
    for t, ider in h["koblinger"]["ut"].items():
        if ider:
            L.append(f"    ut  {t:17} {len(ider):3}  {', '.join(ider[:4])[:60]}")
    for i, typer in list(h["koblinger"]["inn"].items())[:6]:
        L.append(f"    inn {','.join(typer)[:17]:17}       {i}")
    if h["kryssdomene"]:
        L.append(f"  CROSS DOMAIN {', '.join(h['kryssdomene'][:5])}")
    if h.get("falsifiserbarhet"):
        L.append(f"  FALSIFIER    {h['falsifiserbarhet'][:130]}")
    return "\n".join(L)


def skriv_inntak(atlas: dict, tekst: str, fil: str | Path, *,
                 kilde: str = "samtale") -> dict:
    """Append one retain fragment to the queue file, without creating a node."""
    plassering = plasser(atlas, tekst)
    record = {
        "tekst": tekst,
        "tidspunkt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plasseringsstatus": plassering["status"],
        "domene_visshet": plassering.get("domene_visshet"),
        "domene_grunnlag": plassering.get("domene_grunnlag"),
        "forslag": plassering.get("forslag", []),
        "naere_noder": plassering.get("naere_noder", []),
        "mangler": plassering.get("mangler", []),
        "kilde": kilde,
        "proveniens_kilde": kilde,
        "proveniens": {
            "kilde": kilde,
            "atlas": atlas.get("kilde"),
            "commit": atlas.get("commit"),
        },
    }
    sti = Path(fil)
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("a", encoding="utf-8") as ut:
        ut.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Read the atlas — or look something up in it.")
    p.add_argument("repo", nargs="?", default=".", help="path to the repository")
    p.add_argument("--emne", "-e", help="look up a subject instead of reading everything")
    p.add_argument("--ref", default=STANDARD_REF, help=f"git ref (default: {STANDARD_REF})")
    p.add_argument("--hent", action="store_true", help="fetch origin first")
    p.add_argument("--alle", action="store_true", help="show all hits, not just the strongest")
    p.add_argument("--node", help="rotate around ONE node — show every field")
    p.add_argument("--perspektiv", help="rotate: filter on perspektiv (paradigme/konsensus/akademia)")
    p.add_argument("--fase", help="rotate: filter on phase (instrument/regime_engine/...)")
    p.add_argument("--domene", help="rotate: filter on buss_domene")
    p.add_argument("--maaleform", action="store_true",
                   help="rotate: separate what MEASURES from what is derived")
    p.add_argument("--proxy", action="store_true", help="rotate: show all proxy chains")
    p.add_argument("--akser", action="store_true",
                   help="list ALL the axes the atlas carries — also the new ones")
    p.add_argument("--akse", help="rotate around an arbitrary axis: `path` or `path=value`")
    p.add_argument("--alt", dest="alt", help="THE WHOLE: everything about a node, in one reading")
    p.add_argument("--plasser", help="place a NEW fragment: where does it belong, and what is missing")
    p.add_argument("--innta", help="receive a fragment into the retain queue (no node is created)")
    p.add_argument("--kilde", default="samtale", help="provenance source for --innta")
    p.add_argument("--inntak-fil", help="alternative JSONL file for --innta")
    p.add_argument("--hop", help="N hops from a node:  or ")
    p.add_argument("--fragment", help="rotate around ONE fragment: node + every coupling")
    p.add_argument("--oversikt", action="store_true",
                   help="THE WHOLE atlas at once: what is what, where, how many")
    a = p.parse_args()

    # THE WHOLE — everything about a node
    if a.alt:
        atlas = les_atlas(a.repo, ref=a.ref)
        print(helhet_tekst(atlas, a.alt))
        sys.exit(0)

    # RETAIN INTAKE — append-only queue, never automatic node creation
    if a.innta:
        atlas = les_atlas(a.repo, ref=a.ref)
        fil = a.inntak_fil or str(Path(a.repo) / "data" / "inntak" /
                                  "atlas_fragmenter.jsonl")
        record = skriv_inntak(atlas, a.innta, fil, kilde=a.kilde)
        print(f"FRAGMENT: {a.innta!r}  ->  {record['plasseringsstatus']}")
        print(f"  provenance: {record['kilde']}")
        print(f"  written to: {fil}")
        if record["plasseringsstatus"] == "uten_hjem":
            print("  queue: uten_hjem — human review required")
        else:
            print("  queue: fragment suggestion — no node created")
        sys.exit(0)

    # THE ENTRANCE — place a new fragment
    if a.plasser:
        atlas = les_atlas(a.repo, ref=a.ref)
        p_ = plasser(atlas, a.plasser)
        print(f"FRAGMENT: {a.plasser!r}  ->  {p_['status']}")
        print(f"  domain certainty: {p_.get('domene_visshet', 'unknown')} "
              f"({p_.get('domene_grunnlag', 'unknown basis')})")
        for f in p_["forslag"][:4]:
            print(f"  domain {f['domene']:26} {f['kobling']}")
            if f["noder"]:
                print(f"    neighbours: {', '.join(f['noder'])}")
        if p_.get("naere_noder"):
            print(f"  nearby nodes: {', '.join(p_['naere_noder'][:4])}")
        print(f"  must fill {len(p_['mangler'])} fields to become a node: "
              f"{', '.join(p_['mangler'][:6])} ...")
        sys.exit(0)

    # THE COUPLINGS — 1-hop, 2-hop, 3-hop
    if a.hop or a.fragment:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.fragment:
            f = fragment(atlas, a.fragment)
            if not f["finnes"]:
                print(f"ERROR: 'the fragment {a.fragment}' does not exist. Nearby: "
                      f"{', '.join(f['naere']) or 'none'}")
                sys.exit(1)
            print(f"=== {a.fragment} ===")
            print(f"  {f['node'].get('regime', {}).get('name', '?')}")
            print(f"  1-hop {f['ett_hopp']} · 2-hop {f['to_hopp']} · 3-hop {f['tre_hopp']}")
            for type_, ider in f["koblinger"].items():
                vis = ", ".join(ider[:5])
                print(f"  {type_:18} {len(ider):3}  {vis[:66]}")
        else:
            node, _, d = a.hop.partition(":")
            try:
                stier = hop_stier(atlas, node, int(d) if d else 1)
            except KeyError as e:
                print(f"ERROR: {e}")
                sys.exit(1)
            print(f"{len(stier)} nodes within {d or 1} hops of {node}:")
            for nid, (sti, typer) in sorted(stier.items(), key=lambda x: len(x[1][0]))[:22]:
                print(f"  {' -> '.join(sti)[:52]:54} [{' -> '.join(typer)}]")
        sys.exit(0)

    # THE OVERVIEW — global state, not a search
    if a.oversikt:
        atlas = les_atlas(a.repo, ref=a.ref)
        o = oversikt(atlas)
        print(f"THE ATLAS — {len(atlas.get('noder') or [])} nodes, "
              f"{len(o)} axes that distinguish")
        for sti, ford in o:
            linje = " · ".join(f"{v} ({n})" for v, n in ford[:6])
            print(f"  {sti:26} {linje[:92]}")
        sys.exit(0)

    # THE AXES — generic rotation, not twenty flags
    if a.akser or a.akse:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.akser:
            alle = akser(atlas)
            print(f"{len(alle)} axes in the atlas:")
            for sti, (n, verdier) in sorted(alle.items()):
                v = ", ".join(verdier[:4]) + (" ..." if len(verdier) > 4 else "")
                print(f"  {sti:34} {n:3}  {v[:66]}")
        else:
            navn, _, verdi = a.akse.partition("=")
            try:
                treff = roter_akse(atlas, navn, verdi or None)
                sti, lv = _loes_akse(atlas, navn)
                if lv is not None and not verdi:
                    verdi = lv
            except KeyError as e:
                print(f"ERROR: {e}")
                sys.exit(1)
            print(f"{len(treff)} nodes  akse={navn}"
                  + (f"={verdi}" if verdi else "")
                  + (f"  ({sti})" if sti != navn else ""))
            for n in treff:
                v = _les_sti(n, sti)
                print(f"  {n['id']:34} {str(v)[:60]}")
                klarhet = (n.get("maale_paradigme") or {}).get("klarhetsfunksjon")
                if klarhet:
                    print(f"    {klarhet}")
        sys.exit(0)

    # ROTATION — the four angles that did not exist 2026-09-17
    if a.node or a.perspektiv or a.fase or a.domene or a.maaleform or a.proxy:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.node:
            try:
                treff = roter(atlas, node=a.node)
            except KeyError as e:
                print(f"ERROR: {e}")
                sys.exit(1)
            for n in treff:
                print(f"=== {n['id']} ===")
                for felt, v in n.items():
                    if felt == "id":
                        continue
                    if isinstance(v, (dict, list)):
                        print(f"  {felt}: {json.dumps(v, ensure_ascii=False)[:200]}")
                    else:
                        print(f"  {felt}: {v}")
        elif a.maaleform:
            for form, ider in sorted(maaleformer(atlas).items()):
                print(f"{form:12} ({len(ider)}): {', '.join(ider[:6])}"
                      f"{' ...' if len(ider) > 6 else ''}")
        elif a.proxy:
            kj = proxy_kjeder(atlas)
            print(f"{len(kj)} nodes with a proxy chain:")
            for nid, ledd in sorted(kj.items()):
                print(f"  {nid}: {' -> '.join(ledd)}")
        else:
            treff = roter(atlas, perspektiv=a.perspektiv, fase=a.fase, domene=a.domene)
            print(f"{len(treff)} nodes"
                  + (f" perspektiv={a.perspektiv}" if a.perspektiv else "")
                  + (f" fase={a.fase}" if a.fase else "")
                  + (f" domene={a.domene}" if a.domene else ""))
            for n in treff:
                ep = (n.get("episenter") or "")[:56]
                print(f"  {n['id']:34} {n.get('phase','?'):18} {ep}")
        sys.exit(0)

    if a.emne:
        s = finn(a.repo, a.emne, ref=a.ref, hent=a.hent)
        akseinfo = f" via akse {s['akse']}" if s.get("akse") else ""
        print(f"{s['kilde']} @ {s['commit'][:8]} — {s['antall']} hit(s) on «{s['emne']}»{akseinfo}")
        if s["hull"]:
            kh = s["kjent_hull"]
            if kh:
                ant = kh.get("meldinger")
                storrelse = f" · {ant} messages" if ant is not None else ""
                print(f"  KNOWN HOLE — measured as «{kh['status']}»{storrelse}")
                if kh.get("begrunnelse"):
                    print(f"  rationale: {kh['begrunnelse']}")
                if ant is None:
                    print("  (size not measured — comes from PR #475)")
            else:
                print("  THE ATLAS DOES NOT KNOW — no node carries this subject, "
                      "and it is not a measured coverage hole.")
            sys.exit(0)
        kh = s["kjent_hull"]
        if kh:
            print(f"  (the domain {kh['domene']} is measured as «{kh['status']}»)")
        if s["for_bredt"]:
            print(f"  TOO BROAD — {s['raad']}")
        # An answer of 80 lines is not an answer. Show the strongest, and say
        # how many are below — the reader can ask for all with --alle.
        viste = s["treff"] if a.alle else s["treff"][:_VIS_MAKS]
        for t in viste:
            merker = []
            if t["har_falsifikator"]:
                merker.append("can be felled")
            if t["har_prediksjon"]:
                merker.append("has prediction")
            if t["har_oppgjoer"]:
                merker.append("is settled")
            if t["buss_domene"]:
                merker.append(f"buss:{t['buss_domene']}")
            tt = "" if t["trefftype"] == "id" else f" ({t['trefftype']})"
            print(f"  {t['id']:<34} {t['synlighet'] or '?':<9} "
                  f"{t['perspektiv'] or '':<10} {' · '.join(merker)}{tt}")
        if not a.alle and s["antall"] > _VIS_MAKS:
            print(f"  ... and {s['antall'] - _VIS_MAKS} more — use --alle for the full list")
    else:
        d = les_atlas(a.repo, ref=a.ref, hent=a.hent)
        print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} nodes")
