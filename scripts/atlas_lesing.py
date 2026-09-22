#!/usr/bin/env python3
"""atlas_lesing — read the atlas from a GIT-REF, never from a working tree.

THE RULE AS CODE, not as prose. The reason is measured: a test that reads a
document can only see that the words exist, not what they mean. A mutant that
flipped the rule to «read from the working copy» passed three document tests.
The meaning must therefore live in a function that can be run and mutated against.

The background, measured 2026-09-17: the atlas exists in several working
copies that do not show the same map. One working tree showed 72 nodes while
origin/main had 82; another clone stood on a later merged PR branch; a
maintenance worktree lacked `perspektiv` on all 45 nodes.

    A copy that answers reads like a living atlas.

The same failure mode as 2026-09-16 (atlas sync against components that were
not running) and 2026-09-14 (memory available, but not steering).

NOTE on freshness: `origin/main` is a remote-tracking ref and can be
outdated. This module therefore does NOT fetch by itself — it reports which
commit it read, so that an outdated ref is visible in the result instead of in
the reader's assumption. `hent=False` is the default; set `hent=True` when the
reader wants the freshest possible.

THE API MAP — what the public functions take and give. Set up 2026-09-18
after a reader (me) guessed three of them wrong from memory: `finn` was
indexed as a list (it is a dict), `plasser` was read with a key that does not
exist, and `kjent_hull` was called under a name that was private. None of them
was an error in the atlas — all were an error in the interface.

    les_atlas(repo, ref)            -> dict   the whole atlas
    finn(repo, emne, ref)           -> dict   {antall, hull, for_bredt, raad, ...}
    akser(atlas)                    -> dict   {sti: (antall, eksempelverdier)}
    roter_akse(atlas, akse, verdi)  -> list[dict]
    roter(atlas, node=, ...)        -> dict
    helhet(atlas, node_id)          -> dict   {episenter, felt, motor, ...}
    plasser(atlas, tekst)           -> dict   {status, forslag, naere_noder, ...}
    node_verdig(plassering)         -> dict   {node_verdig, terskel, grunn}
    skriv_inntak(atlas, tekst, fil) -> dict   the retain fragment into the queue
    les_inntak(fil)                 -> list   the queue back; a bad line raises
    bekreft(atlas, tekst, generator)-> dict   did it arrive, and is it visible
    bekreft_fra_ref(repo, tekst)    -> dict   the same, read from a ref
    inntak_status(repo, fil)        -> dict   the whole queue, one answer per row
    kjent_hull(repo, emne, ref)     -> dict | None
    naboer/hop/hop_stier/fragment   -> the coupling graph
    maaleformer/proxy_kjeder        -> what measures, via what
    sjekk_usikkerhet(atlas, repo)   -> list[str]  every post against its own source

THE RULE they all follow: an entrance that does not know, SAYS so. `finn`
answers THE ATLAS DOES NOT KNOW rather than giving a loose hit; `plasser`
answers `uten_hjem` rather than guessing a domain.

THE RETAIN INTAKE is the atlas's own `retain`: the session's insights are
proposed as fragments to `plasser()`, each of them with provenance, and each
of them with the threshold written down (see `NODE_TERSKEL`) — because
automation that maps everything fills the atlas with noise. Whoever adds one
confirms afterwards with `--bekreft` that the fragment arrived, and the answer
is built by the atlas and not by the queue: the queue is the working memory,
the atlas is the truth.
"""

from __future__ import annotations

import json
import collections
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

    Returns an object that NAMES the source it read, so that an outdated or
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
            f"{ref}:{sti} in {repo} lacks 'nodes' — "
            f"keys: {sorted(data)[:8] if isinstance(data, dict) else type(data).__name__}")
    # Note: the schema is NOT read here. This function reads the atlas, and an
    # atlas also exists without a schema (synthetic repos in tests, partial
    # extractions). The requirements are read where they are used — see
    # `skjema_krav()`.
    return {
        "kilde": f"git:{ref}",
        "ref": ref,
        "commit": commit,
        "sti": sti,
        "noder": data["nodes"],
        "repo": str(repo),
    }


def skjema_krav(atlas: dict) -> list[str]:
    """Which fields does the schema REQUIRE of a node? One place, not two.

    Measured 2026-09-18: `plasser` computed this as every field in the bank
    minus seven hardcoded exceptions — and among the exceptions lay
    `buss_domene` and `falsifiserbarhet`. A new node was therefore asked for
    `coupling.empathy_note`, but NOT for the bus domain or the falsifier: the
    two fields the rest of the house rests on. A list that cannot discover that
    it has itself become wrong is not a requirement — it is a memory.

    Raises AtlasLesingFeil when no source exists. An empty requirement list
    would mean «no requirements», and that answer looks like knowledge.
    """
    if atlas.get("skjema_krav"):
        return list(atlas["skjema_krav"])
    if atlas.get("repo") and atlas.get("ref"):
        return _skjema_krav(Path(atlas["repo"]), atlas["ref"])
    raise AtlasLesingFeil(
        "the atlas has no source for the requirements: neither 'skjema_krav', "
        "'repo' nor 'ref' exists — then the requirements cannot be read")


def _skjema_krav(repo: Path, ref: str,
                 sti: str = "schema/regime_node.schema.json") -> list[str]:
    """Read which fields the schema REQUIRES of a node — one place, not two.

    Raises AtlasLesingFeil if the schema is missing or does not declare
    `required`. An empty list would mean «no requirements», and that is an
    answer that looks like knowledge.
    """
    raa = _git(repo, "show", f"{ref}:{sti}")
    try:
        skjema = json.loads(raa)
    except json.JSONDecodeError as e:
        raise AtlasLesingFeil(f"{ref}:{sti} is not valid JSON: {e}") from e
    krav = ((skjema.get("$defs") or {}).get("RegimeNode") or {}).get("required")
    if not krav:
        raise AtlasLesingFeil(
            f"{ref}:{sti} declares no required list for RegimeNode")
    return list(krav)


def _har_falsifikator(node: dict) -> bool:
    """Does the node carry an observation that would fell it?

    `ville_falsifisere` is the name in the schema, measured 2026-09-17. A node
    that cannot be felled by anything is a claim — and the reader must be able
    to see the difference without reading the whole node.
    """
    return "ville_falsifisere" in json.dumps(node, ensure_ascii=False)


# ---------------------------------------------------------------------------
# THE UNCERTAINTY LAYER — every number must be able to carry how certain it is
#
# ADR-086 §3.1: the field is optional, closed and additive. The source HAS
# the information (k = 0.415 ± 0.029 stands in its own paper); the atlas lost
# it in the transfer. The diagnosis is therefore not «get uncertainty», but
# «stop throwing it away» — and then there is the one rule that makes the
# layer worth anything: A VALUE ALWAYS HAS A SOURCE.
#
# The checker stands here and not in the schema, deliberately. The schema says
# what a post IS; this one says whether the post HOLDS UP against its source.
# And the C10 gate cannot require the field before it is changed with human
# words (`t_2e60afa6`) — a requirement that cannot be made in the schema must
# be made where it actually runs.
# ---------------------------------------------------------------------------

# The post's and the source's keys. The same three in the schema
# ($defs/Usikkerhetspost, $defs/Usikkerhetskilde) — two lists would drift, and
# one of them would keep quiet.
USIKKERHETSPOST_NOKLER = ("storrelse", "verdi", "feilgrense", "kilde")
USIKKERHETSKILDE_NOKLER = ("fil", "linje", "ordrett")

_TALL_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_GRENSE_RE = re.compile(r"±\s*([0-9]+(?:\.[0-9]+)?)")


def _tall_i(tekst: str) -> list[float]:
    return [float(t) for t in _TALL_RE.findall(tekst)]


def _grenser_pa(tekst: str) -> list[float]:
    """The numbers that stand right after a ± — the SOURCE's own error bounds."""
    return [float(g) for g in _GRENSE_RE.findall(tekst)]


def _like_tall(a: float, b: float) -> bool:
    """0.029 written as 0.029 and as 2.9e-2 is the same bound to a human."""
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def _sporet(repo: Path, fil: str) -> bool:
    """Is the file in the repo? An untracked «source» does not exist as a source."""
    p = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch",
                        "--", fil], capture_output=True, text=True)
    return p.returncode == 0


def _sjekk_usikkerhetspost(node_id: str, nr: int, post, repo: Path) -> list[str]:
    """One post against its own source file. Every way out names why."""
    hvor = f"{node_id}/usikkerhet/{nr}"
    if not isinstance(post, dict):
        return [f"{hvor}: the post is not an object"]
    if isinstance(post.get("storrelse"), str) and post["storrelse"].strip():
        hvor = f"{hvor} «{post['storrelse']}»"

    # Type guard FIRST: a missing key must not give a TypeError in the
    # diagnosis branch — then the reader crashes exactly where it is supposed
    # to say what is wrong.
    mangler = [k for k in USIKKERHETSPOST_NOKLER if k not in post]
    if mangler:
        return [f"{hvor}: missing {', '.join(mangler)}"]

    verdi, grense = post["verdi"], post["feilgrense"]
    for navn, v in (("verdi", verdi), ("feilgrense", grense)):
        if isinstance(v, bool) or not isinstance(v, (int, float, type(None))):
            return [f"{hvor}: {navn} is not a number or null"]
    kilde = post["kilde"]
    if not isinstance(kilde, dict):
        return [f"{hvor}: usikkerhet without a source"]
    mangler = [k for k in USIKKERHETSKILDE_NOKLER if k not in kilde]
    if mangler:
        return [f"{hvor}: kilde is missing {', '.join(mangler)}"]

    fil, linje, ordrett = kilde["fil"], kilde["linje"], kilde["ordrett"]
    if not isinstance(fil, str) or not fil.strip():
        return [f"{hvor}: kilde.fil is empty"]
    if fil.startswith("/") or ".." in fil.split("/"):
        return [f"{hvor}: kilde.fil must be a path in the repo, not {fil!r}"]
    if not _sporet(repo, fil):
        return [f"{hvor}: kilde.fil {fil} is not tracked in the repo"]
    if isinstance(linje, bool) or not isinstance(linje, int) or linje < 1:
        return [f"{hvor}: kilde.linje is not a positive integer"]
    try:
        linjer = (repo / fil).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [f"{hvor}: {fil} could not be read — {e}"]
    if linje > len(linjer):
        return [f"{hvor}: {fil} has {len(linjer)} lines, the post points at {linje}"]
    tekst = linjer[linje - 1]

    ut: list[str] = []
    if not isinstance(ordrett, str) or not ordrett.strip():
        ut.append(f"{hvor}: kilde.ordrett is empty — a quotation must be readable")
    elif ordrett not in tekst:
        ut.append(f"{hvor}: ordrett does not stand at {fil}:{linje}: {ordrett!r}")

    if isinstance(verdi, (int, float)) and not any(_like_tall(verdi, t)
                                                  for t in _tall_i(tekst)):
        ut.append(f"{hvor}: verdi {verdi} does not stand at {fil}:{linje}")

    grenser = _grenser_pa(tekst)
    if grense is None:
        if grenser:
            ut.append(f"{hvor}: the source STATES an error bound ({grenser}) at "
                      f"{fil}:{linje} — the post says it does not")
    elif not grenser:
        ut.append(f"{hvor}: feilgrense {grense} is stated, but {fil}:{linje} "
                  f"states none (no ±) — 0 and guessing are not an answer")
    elif not any(_like_tall(grense, g) for g in grenser):
        ut.append(f"{hvor}: feilgrense {grense} is not the one the source states "
                  f"({grenser}) at {fil}:{linje}")
    return ut


def sjekk_usikkerhet(atlas: dict, repo: str | Path | None = None) -> list[str]:
    """Every post in the uncertainty layer against ITS OWN source. Empty = clean.

    Returns problems, not a verdict: every problem names the node, the post and
    what did not match, so that the answer can be read as a correction.

    The rules, all measured against the source and none against the schema:

      * the post must have `storrelse` and a `kilde` with file, line and a
        VERBATIM excerpt of the line;
      * the file must be tracked in the repo, and the line must exist there;
      * `verdi` must stand on the line the post points at;
      * `feilgrense` is either a number the source states after a ± ON THAT
        LINE, or `null` — and `null` requires that the line states none.

    The last one is the whole reason `null` is an answer and 0 is not: an error
    bound of 0 that the source does not say is a guess written as a
    measurement. `β = 0.16 (free amplitude)` is the test case — it must stand
    as a hole.

    `repo` falls back to `atlas['repo']` (which `les_atlas` sets), and if both
    are missing we raise: a check without sources would have answered «all
    well» on every post, and that answer looks like knowledge.
    """
    sti = repo if repo is not None else atlas.get("repo")
    if not sti:
        raise AtlasLesingFeil(
            "the uncertainty layer cannot be checked without a repo: neither "
            "'repo' nor atlas['repo'] exists — then there are no sources to read")
    repo = Path(sti)

    # Both the atlas layer ('noder', from les_atlas) and the raw file
    # ('nodes') are read. An atlas WITHOUT a node key RAISES here, and that is
    # deliberate: a check that does not find the nodes would have answered «all
    # well» on every post, and that answer looks like knowledge — exactly the
    # failure mode this layer exists to prevent.
    noder = atlas.get("noder")
    if noder is None:
        noder = atlas.get("nodes")
    if noder is None:
        raise AtlasLesingFeil(
            "the atlas has neither 'noder' nor 'nodes' — then there are no "
            "posts to check, and «no problems» would have been an empty answer")

    ut: list[str] = []
    for node in noder or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "?")
        usikkerhet = node.get("usikkerhet")
        if usikkerhet is None:
            continue  # OPTIONAL: a node without the layer is not a problem
        if not isinstance(usikkerhet, dict):
            ut.append(f"{node_id}: usikkerhet is not an object")
            continue
        poster = usikkerhet.get("poster")
        if not isinstance(poster, list) or not poster:
            ut.append(f"{node_id}: usikkerhet without poster — an empty field that looks filled")
            continue
        for nr, post in enumerate(poster):
            ut.extend(_sjekk_usikkerhetspost(node_id, nr, post, repo))
    return ut


def _dekning(repo: Path, ref: str, hent: bool) -> dict:
    """Read the coverage file from the SAME ref. If it is missing, the answer is
    empty — not an error.

    The coverage status is a separate artefact (`schema/atlas_dekning.json`),
    not a field on the nodes. Without this the lookup reads only the nodes, and
    must answer «does not know» about something someone has actually measured
    and found missing.
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
    """Is the subject a domain someone has measured? Searches the domain NAME, not
    the content.

    Only a hit on the name counts. A hit on a begrunnelse would have made
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
                    # OPTIONAL: PR #475 puts measured message volume per
                    # domain into the coverage file. If it exists, it is shown —
                    # and then a hole of 190 770 can be told apart from one of
                    # 228. If it does not exist, the lookup works as before; a
                    # reference work that does not work before another PR lands
                    # is a reference work that does not work.
                    "meldinger": v.get("meldinger")}
    return None


def _norm(s: str) -> str:
    """Hyphen, underscore and space are the same separator.

    A reference work that does not see that `energy-flow` and `energy flow` are
    the same word answers «does not know» about a word it actually owns.
    """
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def _navnerom(repo: Path, ref: str, emne: str) -> list[dict]:
    """Find registered concepts without pretending they are atlas nodes.

    Two things must NOT be swallowed silently: a concept without `@id` is a
    defect in the register (not a usable hit), and invalid JSON in the PRIMARY
    concept register is an error — not «not found». A reference work that turns
    a read error into «does not know» has answered something other than what it
    was asked."""
    naal = _norm(emne)
    funn = []
    for sti in ("docs/concepts.jsonld", "docs/ontology.jsonld"):
        try:
            data = json.loads(_git(repo, "show", f"{ref}:{sti}"))
        except json.JSONDecodeError as feil:
            raise AtlasLesingFeil(f"{sti} is not valid JSON: {feil}") from feil
        except AtlasLesingFeil:
            # The file does not exist on this ref. That is a measured absence of
            # an OPTIONAL register, not a defect — and it is not reported as a hit.
            continue
        for post in data.get("@graph", []):
            kandidater = [post.get("@id"), post.get("label")]
            for felt in ("skos:prefLabel", "skos:notation", "skos:altLabel"):
                verdi = post.get(felt)
                verdier = verdi if isinstance(verdi, list) else [verdi]
                kandidater.extend(
                    v.get("@value") if isinstance(v, dict) else v for v in verdier)
            if any(isinstance(v, str) and _norm(v) == naal for v in kandidater):
                if not isinstance(post.get("@id"), str) or not post["@id"]:
                    raise AtlasLesingFeil(
                        f"{sti}: a concept matches «{emne}» but lacks @id — "
                        "the register is defective, and a hit without an id "
                        "cannot be re-checked")
                funn.append({"id": post["@id"], "kilde": sti})
    unike = {}
    for post in funn:
        unike.setdefault(post["id"], post)
    return sorted(unike.values(), key=lambda x: x["id"] or "")


def finn(repo: str | Path, emne: str, ref: str = STANDARD_REF, *,
         hent: bool = False) -> dict:
    """Look up a subject in the atlas — reads from `ref`, never from the working
    tree.

    The difference from `les_atlas`: this one answers a QUESTION. `les_atlas`
    gives you the whole map and lets you search; the price for that is that the
    atlas is not consulted spontaneously. Measured 2026-09-17: the module had
    an exit and no entrance.

    The answer is ALWAYS shaped the same, also when it is empty:

        {"emne", "antall", "hull", "treff", "kilde", "ref", "commit"}

    `hull: True` means «the atlas does not know» — that is an answer, not an
    error, and it can be told apart from an error because an error RAISES. A
    reference work that cannot say «I do not know» says «no» out of ignorance.

    Every hit names its epistemic status, so that the reader does not have to
    read the whole node to know what is known and what is stipulated.
    """
    if not emne or not emne.strip():
        raise AtlasLesingFeil(
            "empty subject — a lookup without a question would have matched "
            "everything and thus answered nothing")
    atlas = les_atlas(repo, ref, hent=hent, sti="schema/regime_nodes.jsonld")
    # Measured 2026-09-18: `--emne "energy-flow"` hit, `--emne "energy flow"`
    # gave 0 hits. The words Morten uses have BOTH forms, and a reference work
    # that does not see that answers «does not know» about a word it owns.
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
    # `\\b` counts `_` as a WORD CHARACTER. But in node ids `_` SEPARATES
    # parts: `homo.sovn_vaaken`, `efc.solar_flare_engine`. With `\b`, `sovn`
    # was weakened to a substring even though it is a part of its own in the id
    # (measured in review 2026-09-17). We therefore define the word character
    # explicitly, so that `_`, `.` and `-` are all separators — and `sol` in
    # `solid` is still a substring.
    _ORDTEGN = "a-z0-9æøå"
    ordmonster = re.compile(
        rf"(?<![{_ORDTEGN}])" + re.escape(naal) + rf"(?![{_ORDTEGN}])")
    treff = []
    for n in atlas["noder"]:
        tekst = _norm(json.dumps(n, ensure_ascii=False))
        if naal not in tekst:
            continue
        # Three levels, not two. «sol» hit `batteri.lading` as a WORD — because
        # the word exists in a text inside the node — but the node is not about
        # sol. And «sol» hit `h2o.solid` as a substring of «solid». Without the
        # distinction the reader has to guess which hits are real.
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
    # Registered concepts ALWAYS answer with the namespace hit — also when a
    # node mentions the words.
    #
    # The first version added the namespace hit ONLY when no node hit, and that
    # was a silent dependency on the content. Measured 2026-09-18
    # (t_af77c6da): the uncertainty layer's `kilde.fil` wrote
    # «docs/papers/efc/Energy-Flow-Cosmology-Unified-Analysis-of-BAO/
    # index.json» into obs.bao — and the answer to «Energy-Flow Cosmology» went
    # from «registered concept: efc:EFC» to «word in obs.bao». The register is
    # the atlas's answer to «do I own this concept?», and that answer must not
    # depend on which nodes happen to cite a file.
    registrert = _navnerom(Path(repo), ref, emne)
    if registrert:
        treff.extend({
            "trefftype": "navnerom",
            "id": post["id"],
            "synlighet": None,
            "perspektiv": None,
            "fase": None,
            "buss_domene": None,
            "har_prediksjon": False,
            "har_oppgjoer": False,
            "har_falsifikator": False,
            # Machine-readable NON-COVERAGE. Review 2026-09-18: a namespace hit
            # gave a non-empty hit list, and a reader (or a downstream call)
            # could conclude «covered». The atlas does NOT have the node — it
            # has the concept in the namespace. The two fields say so without
            # anyone having to read the prose.
            "har_node": False,
            "dekning": "navnerom_uten_node",
            "grunn": (f"registered in {post['kilde']}, but is not a "
                      "node in schema/regime_nodes.jsonld"),
        } for post in registrert)
    # Precision is the order: a node that CARRIES the word in the id or that
    # COVERS the domain says more than the register does; the register says
    # more than a loose word in a text. The namespace hit therefore stands
    # between them — not last, which was an inheritance from when it was only
    # a fallback.
    _rang = {"id": 0, "domene": 1, "navnerom": 2, "ord": 3, "delstreng": 4}
    # Within the same rank: public before internal. The public ones are the
    # core of the published atlas; the internal ones are context.
    treff.sort(key=lambda x: (_rang[x["trefftype"]],
                              x["synlighet"] != "offentlig",
                              x["id"] or ""))
    # «Too broad» rests on whether the search has ANYTHING PRECISE — not on a
    # count.
    #
    # The first version used «>50 hits or >60 % of the atlas». Review round 4
    # measured it against real questions: sol=20, energi=25, kosmos=32, h2o=36 —
    # all far below, instrument=82 above. No real question lay anywhere near,
    # so the number was guessed. Worse: `efc` gives 68 hits of which 32 are
    # PRECISE — a count threshold called it broad, which is the exact opposite.
    #
    # The criterion is therefore: a hit is precise if it stands in the node id
    # or covers a bus domain. If there are no precise hits AND the answer does
    # not fit in the display, the search is broad — no matter how large the
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
# `--alle`). It could look up and list. It could NOT filter on perspective, not
# tell a measured node from a derived one, not show proxy chains. The rotation
# did not exist.
# ---------------------------------------------------------------------------

#: Phases where the node MEASURES something — it has an instrument in the world.
_MAALENDE_FASER = frozenset({"instrument", "observation"})

#: Phases where the node is DERIVED — computed, not measured.
_AVLEDEDE_FASER = frozenset({"regime_engine", "computation_engine",
                             "theoretical", "stable"})


def roter(atlas: dict, *, node: str | None = None,
          perspektiv: str | None = None, fase: str | None = None,
          domene: str | None = None) -> list[dict]:
    """Rotate in the atlas across the fields.

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
    """Separate what MEASURES from what is derived.

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
    """What goes via what — through every link.

    `measure.proxy_chain` says which links separate the measured from the
    concluded. A node without a chain says it reads directly; one with three
    links says that three things must hold.
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
# The solution is not twenty flags: it is FINDING the axes yourself, so that an
# axis added tomorrow also works tomorrow.
# ---------------------------------------------------------------------------

def _bla(sti: str, v, ut: dict) -> None:
    """Walk through a node and collect every path as an axis.

    Both the leaf AND the parent are registered: `analogi.avbildning` is
    useful, but `analogi` is the axis — a node that HAS the isomorphism must be
    found on it.
    """
    if isinstance(v, dict):
        ut.setdefault(sti, []).append(f"<{len(v)} felt>")
        for k, x in v.items():
            _bla(f"{sti}.{k}", x, ut)
    elif isinstance(v, list):
        ut.setdefault(sti, []).extend(str(x) for x in v)
    elif v is None:
        # `None` is not a value. `str(None)` became literally «None», which is
        # truthy — and made `nivaa.forelder` an axis with 113 nodes that
        # answered 33, with «None» as an offered value.
        # Measured 2026-09-18.
        return
    else:
        ut.setdefault(sti, []).append(str(v))


def akser(atlas: dict) -> dict[str, tuple[int, list[str]]]:
    """Find ALL the axes in the atlas — also the ones that did not exist yesterday.

    Returns `{sti: (number of nodes that have it, sample values)}`.
    Nested fields are walked with a dot: `emergence.loop`,
    `epistemikk.sannhetsstatus`.
    """
    raa: dict[str, set] = {}
    antall: dict[str, int] = {}
    for n in atlas.get("noder") or []:
        blad: dict[str, list] = {}
        for k, v in n.items():
            _bla(k, v, blad)
        for sti, verdier in blad.items():
            # An axis exists only if it has a VALUE. `nivaa.forelder` is `None`
            # on 80 of 113 nodes; counting those as a value made the axis offer
            # 113 and answer with 33. Measured 2026-09-18.
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

# The owner's question forms are their own name layer, not free text that must
# be hoped to hit in the node prose. Normalised keys make space, hyphen and
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
    """Resolve a human name to (sti, verdi). Three classes.

    1. THE NAME IS THE PATH      -> (sti, None)
    2. THE NAME IS AN ALIAS      -> (sti, None)
    3. THE NAME IS A VALUE       -> (perspektiv, verdi)  <- third class
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
    «ALL of this must be global in the atlas and you must immediately know what
    is what where etc.». That is not a search — it is the state.
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
        # only axes that SEPARATE, and only short values: a free text is not a
        # category. «Immediately» means it has to be readable.
        if len(fordeling) < 2:
            continue
        if any(len(v) > 34 or " " in v for v, _ in fordeling[:8]):
            continue
        ut.append((sti, fordeling))
    return ut


def roter_akse(atlas: dict, akse: str, verdi: str | None = None) -> list[dict]:
    """Rotate around ONE axis — top level or nested.

    `verdi=None` gives every node that HAS the axis. An unknown axis fails
    loudly with suggestions, because an empty answer would have hidden that the
    name was wrong.
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
        # An empty list and an empty string are not a value.
        # `emergence.properties` is `[]` on 99 of 113 nodes; counting those made
        # the axis answer 113 where it had 99. Measured 2026-09-18.
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
# KOBLINGENE — 1-hop, 2-hop, 3-hop
#
# Measured 2026-09-18: the tool had `--emne`, `--akse`, `--node`,
# `--oversikt` and `--proxy`. It had NO hops. The couplings existed in the
# data — nivaa.forelder, coupling, analogi, stipulasjoner.motor,
# buss_domene, measure.proxy_chain — and none of them could be FOLLOWED.
# ---------------------------------------------------------------------------

def _mekanisme(noder: list[dict]) -> dict[str, dict]:
    return {x["id"]: x for x in noder}


def _koblinger(n: dict, atlas: dict) -> dict[str, list[str]]:
    """Which nodes hang together with this one, and HOW.

    The coupling type is the point: «same domain» is weaker than «is parent».
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
    """1-HOP: what hangs together with this, and how. `KeyError` if unknown."""
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
    """The PATHS, not just the set: WHY they hang together.

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
    """Rotate around ONE fragment: the node, its couplings, and neighbours of neighbours.

    «rotate around every fragment of an observation we make» — when an
    observation comes in, it must be possible to insert it and see it from all
    sides.
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


#: What kind of answer each field demands of whoever places something new.
#: Settled with Morten 2026-09-18, after an input that wanted `--plasser` to
#: become "structure is computed, assessments are proposed, claims are required".
#:
#:   struktur  — derivable from the fragment's place in the chain. Filled, with grounds.
#:   vurdering — computable as a candidate, but the semantics must be approved.
#:   paastand  — cannot be derived from anything. It IS the node's content.
#:
#: `phase` was proposed as an enum. Measured 2026-09-18: 26 values, of which 19
#: used once ("solid (ice Ih)", "coexistence (solid + liquid + gas)"); the core
#: is seven values and covers 107 of 126 nodes. A closed enum would have
#: rejected 19 real values. The phase is therefore core + residue, not closed.
FELTKLASSE = {
    "id": "struktur", "synlighet": "struktur", "buss_domene": "struktur",
    "nivaa": "struktur", "phase": "struktur", "sektor": "struktur",
    "perspektiv": "vurdering", "maale_paradigme": "vurdering",
    "rcmp": "vurdering",
}
#: Fields the schema does NOT require, but which the house falls on. Measured
#: 2026-09-18 these were on the hardcoded exemption list in this function —
#: exactly inverted from what the rest of the house is built on.
HUSETS_KRAV = ("buss_domene", "ville_falsifisere", "falsifiserbarhet",
               "prediction", "settlement")


#: The readers whose ANSWER counts as "someone reads this field". One list,
#: used by the measurement (scripts/atlas_feltvekt.py) and by `plasser`.
LESERE = ("atlas_lesing", "atlas_inngang", "atlas_navigasjon", "atlas_volum",
          "efc_atlas_generator")

#: Measured 2026-09-19 by MUTATION, not by counting: the field was emptied on
#: every node that carries it inside a throwaway repo, and each of the five
#: readers was asked again. The tuple is the readers whose answer CHANGED.
#:
#: An empty tuple means no reader notices the field disappear — the field is
#: dead weight for a new node and the requirement should be argued for, not
#: assumed. A field NOT in this table has no measurement behind it at all;
#: `plasser` reports that instead of guessing, and `umaalte_krav()` names them.
#:
#: Measured on 403a9c64 (origin/main), 22 of 22 requirements:
#:
#:     atlas_lesing 22 · atlas_inngang 7 · atlas_navigasjon 6
#:     efc_atlas_generator 6 · atlas_volum 0
#:
#: **No requirement is read by nobody, so this table shrinks nothing.** The
#: field that comes closest is read by one reader. `atlas_volum` changes for
#: none of the 22: it reads the bus measurement and the coverage declaration,
#: not the node fields — a result, not a missing probe.
#:
#: Re-measure with (takes about half a minute, touches no bank):
#:
#:     python3 scripts/atlas_feltvekt.py . --ref origin/main
#:     python3 scripts/atlas_feltvekt.py . --ref origin/main --python
FELT_LESERE: dict[str, tuple[str, ...]] = {
    "id": ("atlas_lesing", "atlas_inngang", "atlas_navigasjon",
           "efc_atlas_generator"),
    "regime": ("atlas_lesing", "atlas_inngang"),
    "phase": ("atlas_lesing", "atlas_inngang"),
    "measure": ("atlas_lesing", "efc_atlas_generator"),
    "episenter": ("atlas_lesing",),
    "buffer": ("atlas_lesing", "efc_atlas_generator"),
    "ontology": ("atlas_lesing",),
    "observer": ("atlas_lesing",),
    "emergence": ("atlas_lesing",),
    "fractal": ("atlas_lesing",),
    "coupling": ("atlas_lesing",),
    "perspektiv": ("atlas_lesing", "efc_atlas_generator"),
    "stipulasjoner": ("atlas_lesing",),
    "epistemikk": ("atlas_lesing", "atlas_inngang", "efc_atlas_generator"),
    "maale_paradigme": ("atlas_lesing", "atlas_inngang",
                        "efc_atlas_generator"),
    "nivaa": ("atlas_lesing",),
    "synlighet": ("atlas_lesing", "atlas_inngang", "atlas_navigasjon"),
    "buss_domene": ("atlas_lesing", "atlas_inngang", "atlas_navigasjon"),
    "ville_falsifisere": ("atlas_lesing", "atlas_navigasjon"),
    "falsifiserbarhet": ("atlas_lesing",),
    "prediction": ("atlas_lesing", "atlas_navigasjon"),
    "settlement": ("atlas_lesing", "atlas_navigasjon"),
}


def feltet_leses(felt: str) -> bool:
    """Does any of the five readers change its answer when the field goes?

    False for a field that was MEASURED and read by nobody. Use `er_maalt`
    when the two must be told apart: an unmeasured field is not evidence.
    """
    return bool(FELT_LESERE.get(felt))


def er_maalt(felt: str) -> bool:
    """Is there a mutation measurement behind this requirement?"""
    return felt in FELT_LESERE


def umaalte_krav(krav, tabell: dict | None = None) -> list[str]:
    """The requirements that stand in a group with no measurement behind them.

    A requirement called read — or called unread — without a measurement is an
    opinion wearing the numbers of a measurement. This is the one place that
    says so, and the test that pins the separation runs it.
    """
    t = FELT_LESERE if tabell is None else tabell
    return [f for f in krav if f not in t]


#: Function words, Norwegian and English. They describe nothing and can
#: therefore not carry a placement: «med» and «som» stand in almost every node
#: text.
STOPPORD = frozenset("""
og av til for med den det de en et som er var paa fra ved mot over under
mellom uten etter mens naar hvor hva hvem hvis saa men eller ikke bare kan
skal vil maa bor blir ble har hadde sine sin sitt seg selv dette disse denne
deres vart vaere alle noen noe annet andre mer mest minst slik slike hvert
hver samt baade enten verken dess fordi dersom
the and for with that this from into over under between without after while
when where what which who whose than then also not only can will shall must
may be been being has have had its their our your his her they them we you it
""".split())


def _stamme(a: str, b: str, n: int = 5) -> bool:
    """«vulkansk» and «vulkan» are one word to a human, not to ==.

    Lifted out of `plasser()` 2026-09-18: the confirmation (see `bekreft`)
    has to split on EXACTLY the same word rule as the placement. Two rules
    for «one word» would give an answer where the fragment is carried by a
    node the placement did not find — or the other way round.
    """
    return len(a) >= n and len(b) >= n and a[:n] == b[:n]


def plasser(atlas: dict, tekst: str) -> dict:
    """Place a NEW fragment — and say what remains.

    The entrance is not a hole. It is a list of what the fragment must fill in
    to become a node: which domain it belongs in, which nodes it resembles, and
    which fields are missing.
    """
    if not tekst.strip():
        return {"status": "tomt", "forslag": [], "mangler": []}

    alle = akser(atlas)
    # Function words carry no placement. Measured 2026-09-18: the fragment
    # «varmepumpe med CO2 som kjolemiddel» matched on «med» and «som» — words
    # that stand in almost every node — and the answer became «naere noder:
    # homo.fluxus, homo.homeostase_buffer, homo.hjerte_syklus,
    # homo.cellesyklus». A list that LOOKS like a placement suggestion but is
    # noise is the same class as the fallback that answers. The requirement is
    # therefore that the word describes something.
    ord_i = {w for w in _norm(tekst).split()
             if len(w) > 2 and w not in STOPPORD}
    noder = atlas.get("noder") or []

    # which domains do the words name? The domains are read from the NODES,
    # not from `akser()`. Measured 2026-09-18: `akser()` truncates the sample
    # values to six (`sorted(raa[sti])[:6]`), and that is a DISPLAY rule — yet
    # plasser() read it as the candidate list. Then only the first six
    # domains alphabetically could give `hjem_funnet`, and «hav» got «ingen
    # anelse» while `verden.hav` was in the bank. A display limit must not
    # decide what the atlas KNOWS.
    domener = sorted({n["buss_domene"] for n in noder if n.get("buss_domene")})
    treff_domener = [d for d in domener
                     if any(w in _norm(d) for w in ord_i)]

    # which nodes share words with the fragment? The weight is put where the
    # word ACTUALLY describes something: the target and the regime, not all
    # texts in the node.
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
                        "kobling": ("the nodes share words with the fragment — "
                                    "WORD LIKENESS, not a placement suggestion")})
    if not forslag:
        # no domain string matched: use the DOMAINS OF THE NEAR NODES.
        # The fallback must not suggest the alphabet — it must suggest what the
        # fragment RESEMBLES. (Measured 2026-09-18: «vulkansk aske» pointed at
        # kosmos.asteroider/galakser/hoper, that is, only the first three.)
        sett: list[str] = []
        for _, nid in naere[:8]:
            x = next((y for y in noder if y["id"] == nid), None)
            d = (x or {}).get("buss_domene")
            if d and d not in sett:
                sett.append(d)
        forslag = [{"domene": d, "noder": [],
                    "kobling": "word likeness — not a known domain choice"}
                   for d in sett[:4]]
        if not forslag:
            forslag = [{"domene": d, "noder": [],
                        "kobling": "no idea — an alphabetical view, not a suggestion"}
                       for d in alle.get("buss_domene", (0, []))[1][:3]]

    if forslag and len(treff_domener) > 0:
        status = "hjem_funnet"
        domene_visshet = "vet"
        domene_grunnlag = "explicit hit on buss_domene"
    elif naere_noder and naere[0][0] >= 2:
        status = "svakt"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "word similarity only — not a known domain"
    else:
        status = "uten_hjem"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "no domain clue"

    # What kind of answer does each field demand? Three classes, settled
    # 2026-09-18:
    #   struktur  — derivable from the fragment's place in the chain; filled,
    #               with a reason
    #   vurdering — computable as a candidate, but the semantics must be approved
    #   paastand  — must be declared explicitly; cannot be derived from anything
    #
    # And the requirements come from the schema, not from a handwritten list.
    # Measured 2026-09-18: `buss_domene` and `falsifiserbarhet` lay among the
    # hardcoded exceptions, so a new node was asked for `coupling.empathy_note`
    # but not for bus domain or falsifier — the two fields the rest rests on.
    krav_fra_skjemaet = skjema_krav(atlas)

    fylt = {f: sum(1 for n in noder
                   if n.get(f) not in (None, "", [], {}))
            for f in set(krav_fra_skjemaet) | set(HUSETS_KRAV)}
    krav = []
    for f in list(krav_fra_skjemaet) + [x for x in HUSETS_KRAV
                                        if x not in krav_fra_skjemaet]:
        klasse = FELTKLASSE.get(f, "paastand")
        lesere = list(FELT_LESERE.get(f, ()))
        post = {"felt": f,
                "klasse": klasse,
                "kilde": "skjema" if f in krav_fra_skjemaet else "huset",
                "fylt_i_banken": f"{fylt.get(f, 0)}/{len(noder)}",
                "lesere": lesere, "lesere_av": len(LESERE),
                "maalt": er_maalt(f), "leses": bool(lesere),
                "forslag": None, "grunn": None}
        if not post["maalt"]:
            # No measurement is not the same as no reader. Saying "unread"
            # here would be a guess wearing the clothes of a measurement.
            post["grunn"] = ("no mutation measurement behind this requirement — "
                             "run scripts/atlas_feltvekt.py")
        elif not post["leses"]:
            post["grunn"] = (f"measured by mutation: none of the {len(LESERE)} "
                             f"readers changes its answer when it is emptied")
        if klasse == "struktur":
            post["forslag"], post["grunn"] = _utled_struktur(
                f, tekst, noder, treff_domener,
                alle.get("synlighet", (0, []))[1])
        krav.append(post)

    return {
        "status": status,
        "domene_visshet": domene_visshet,
        "domene_grunnlag": domene_grunnlag,
        "tekst": tekst,
        "forslag": forslag,
        "naere_noder": naere_noder,
        "krav": krav,
        "mangler": [k["felt"] for k in krav],
        "oppsummering": {
            "struktur": sum(1 for k in krav if k["klasse"] == "struktur"),
            "vurdering": sum(1 for k in krav if k["klasse"] == "vurdering"),
            "paastand": sum(1 for k in krav if k["klasse"] == "paastand"),
            # THE SEPARATION: requirements some reader reads, against fields
            # no reader touches — with the measured number behind each one.
            "leses": sum(1 for k in krav if k["leses"]),
            "uten_leser": sum(1 for k in krav if k["maalt"] and not k["leses"]),
            "uten_leser_felt": [k["felt"] for k in krav
                                if k["maalt"] and not k["leses"]],
            "umaalt": [k["felt"] for k in krav if not k["maalt"]],
            "lesere_av": len(LESERE),
        },
        "aksene": {k: alle[k][1][:6] for k in
                   ("perspektiv", "phase", "synlighet") if k in alle},
    }


def _utled_struktur(felt: str, tekst: str, noder: list,
                    treff_domener: list, synlighet: list) -> tuple:
    """Derive a structure field — or say why it could not be derived.

    Never a guess presented as a value. If it cannot be derived we say so:
    this is exactly where a fragment silently turns into a fact.
    """
    if felt == "id":
        if len(treff_domener) == 1:
            ord_i = [w for w in _norm(tekst).split()
                     if len(w) > 2 and w not in STOPPORD]
            if ord_i:
                prefiks = treff_domener[0].split(".")[-1]
                return (f"{prefiks}.{ord_i[0]}",
                        "the domain's prefix + the fragment's first content "
                        "word — a SUGGESTION, not a decision")
        return None, "without a known domain there is no id to build on"
    if felt == "synlighet":
        # The default is read from the bank, not from the code: if the bank
        # changes, the suggestion changes.
        verdier = [n.get("synlighet") for n in noder if n.get("synlighet")]
        if not verdier:
            return None, "no visibility value to read the default from"
        vanligst = max(set(verdier), key=verdier.count)
        return vanligst, (f"{verdier.count(vanligst)}/{len(verdier)} "
                          f"of the nodes in the bank")
    if felt == "buss_domene":
        if len(treff_domener) == 1:
            return treff_domener[0], "the fragment mentions one known domain"
        if len(treff_domener) > 1:
            return None, (f"ambiguous: {', '.join(treff_domener[:3])} — "
                          f"the choice is an assessment")
        return None, "the fragment hits no known domain"
    if felt == "sektor":
        for d in treff_domener:
            verdier = [(n.get("maale_paradigme") or {}).get("sektor")
                       for n in noder if n.get("buss_domene") == d]
            verdier = [v for v in verdier if v]
            if len(set(verdier)) == 1:
                return verdier[0], f"all {len(verdier)} nodes in {d} have this"
            if verdier:
                talt = collections.Counter(verdier).most_common()
                return None, (f"ambiguous in {d}: "
                              + ", ".join(f"{v} ({c})" for v, c in talt[:3])
                              + " — the choice is an assessment")
        return None, "no known place to read the sector from"
    if felt == "nivaa":
        return None, ("can be derived once the parent is chosen: the index "
                      "must be higher than the parent's")
    if felt == "phase":
        kjerne = ["instrument", "regime_engine", "observation",
                  "computation_engine", "theoretical", "stable", "observer"]
        return None, ("core: " + ", ".join(kjerne)
                      + " — a new value is a deliberate choice, not free text")
    return None, "no derivation rule for this field"


# ---------------------------------------------------------------------------
# THE WHOLE — everything about a node, in one reading
#
# Morten, 2026-09-18: «if we are talking about h2o, BAO, the rainbow or victron
# now, you must immediately via the atlas get a local-global interconnection,
# see emergence, see epicentre, the vectors, the fields, domain, cross-domain,
# more hops in all directions, see paradigm, see consensus, see academia, see
# emergence, see all the fractals the measured emergence has, be able to rotate
# around what we measure, know what we measure, whether it is via proxy, with
# which measurement methods, and the instrument».
#
# Measured before: the answer existed only as thirteen separate commands.
# ---------------------------------------------------------------------------

def kjent_hull(repo: str | Path, emne: str,
               ref: str = STANDARD_REF, *, hent: bool = False) -> dict | None:
    """Is the topic a KNOWN hole — a domain somebody has measured and found empty?

    This is the public entrance. The private `_kjent_hull` takes the coverage
    file that is already read; this one does the lookup itself, because a
    reader who asks «is this a known hole?» does not have the coverage file at
    hand — they have a topic.

    Set up 2026-09-18: `kjent_hull` existed, but was called `_kjent_hull` and
    took a different parameter than the one a reader would have guessed. An
    entrance that cannot be found does not work — no matter how correct it is.
    """
    return _kjent_hull(_dekning(Path(repo), ref, hent), emne)


def helhet(atlas: dict, node_id: str) -> dict:
    """EVERYTHING about a node — the six parts, in one reading.

    Not a summary: each part is the raw value from the node, because a summary
    would hide exactly what one is looking for.
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

    # CROSS-DOMAIN: which OTHER domains the node reaches via hops
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
    """The whole thing as readable text — for the CLI and for the eye."""
    h = helhet(atlas, node_id)
    if not h["finnes"]:
        return (f"ERROR: `{node_id}` does not exist. Nearby: "
                f"{', '.join(h['naere']) or 'none'}")
    L: list[str] = [f"=== {h['id']} ==="]
    L.append(f"  felt/regime : {h['felt'].get('name', '?')}")
    v = h["felt"].get("validity")
    if v:
        L.append(f"  validity    : {v[:150]}")
    L.append(f"  domain      : {h['domene'] or '(none)'}")
    L.append(f"  engine      : {h.get('motor') or '(none — not an engine node)'}")
    L.append(f"  epicentre   : {h['episenter'] or '(none)'}")
    L.append("")
    L.append("  THE MEASUREMENT")
    for k, navn in (("hva", "what"), ("hvem", "who"), ("hvor", "where"),
                    ("instrument", "instrument"), ("kompresjon", "compression")):
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
    L.append(f"  FRACTALS    {len(h['fraktaler'])} segments")
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
        L.append(f"  CROSS-DOMAIN {', '.join(h['kryssdomene'][:5])}")
    if h.get("falsifiserbarhet"):
        L.append(f"  FALSIFIER   {h['falsifiserbarhet'][:130]}")
    return "\n".join(L)


def skriv_inntak(atlas: dict, tekst: str, fil: str | Path, *,
                 kilde: str = "samtale") -> dict:
    """Append one retain fragment to the queue file, without creating a node.

    The threshold (see `node_verdig`) is written WITH the fragment. A
    fragment that is not node-worthy stays in the queue with its reason
    instead of being hidden, so whoever reads the queue can see what was
    considered and why the answer was no.
    """
    plassering = plasser(atlas, tekst)
    dom = node_verdig(plassering)
    record = {
        "tekst": tekst,
        "tidspunkt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plasseringsstatus": plassering["status"],
        "domene_visshet": plassering.get("domene_visshet"),
        "domene_grunnlag": plassering.get("domene_grunnlag"),
        "forslag": plassering.get("forslag", []),
        "naere_noder": plassering.get("naere_noder", []),
        "mangler": plassering.get("mangler", []),
        "node_verdig": dom["node_verdig"],
        "terskel": dom["terskel"],
        "terskel_grunn": dom["grunn"],
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


def les_inntak(fil: str | Path) -> list[dict]:
    """Read the queue back. An unreadable line RAISES — it has to be seen.

    Same rule as the rest of the module: an entrance that does not know,
    says so. A queue where half the lines are silently skipped answers «not
    in» about a fragment that may have been there.
    """
    sti = Path(fil)
    if not sti.exists():
        return []
    ut = []
    for nr, linje in enumerate(sti.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            ut.append(json.loads(linje))
        except json.JSONDecodeError as e:
            raise ValueError(f"{sti}:{nr} is not valid JSON: {e}") from e
    return ut


# ---------------------------------------------------------------------------
# THE RETAIN INTAKE — the threshold and the closed loop
#
# Morten, 2026-09-18, translated here along with the rest of this block: «all
# of it goes into the atlas — the ATLAS frame uses the same methodology as
# hindsight retain, really.» And in the same breath: «automation that maps
# everything would fill the atlas with noise.»
#
# The two sentences do not contradict each other: a retain without a
# threshold is not a retain, it is a log. The threshold therefore lives here
# as DATA — it can be read, run and mutated against, not remembered.
# ---------------------------------------------------------------------------

#: A word shorter than this does not carry a fragment in the atlas: «aske»
#: is a word, a glue word is not. Deliberately STRICTER than the placement
#: (3), because the confirmation reads the WHOLE node — a wide rule there
#: would answer «inne» to almost anything, and a confirmation that always
#: says yes confirms nothing.
_MIN_ORD = 4

#: How large a share of the fragment words a node has to carry to count as a
#: carrier. MEASURED 2026-09-18 against origin/main, with «minst ett ord» as
#: the rule: «vulkanutbrudd avkjoler stratosfaeren gjennom aerosoler» got
#: four hits — every one on «gjennom», none on vulkanutbrudd; «Bondi-Hoyle
#: akselerasjon i mellomstjerne medium» got four hits, every one on
#: «mellomstjerne», in h2o nodes. A confirmation that says «inne» on a glue
#: word confirms nothing. One half separates the measured real hits
#: (trippelpunktet for vann 2 of 2, lensing av bakgrunnsstraaling 2 of 2,
#: SO2 flux out of monitored volcanoes 3 of 3) from the noise — and leaves
#: «vulkansk aske i stratosfaeren» as NOT in, which is right: the volcano
#: node does not carry the ash, it carries the VHP status list.
NODE_ANDEL = 0.5

#: The threshold for NODE-WORTHY, keyed on the placement's OWN status (not
#: on a fresh judgement): status -> (node_verdig, grunn).
NODE_TERSKEL: dict[str, tuple[bool, str]] = {
    "hjem_funnet": (True,
                    "explicit domain hit — the fragment owns a domain"),
    "svakt": (True,
              "two or more shared words with a named node"),
    "uten_hjem": (False,
                  "no domain owner — the fragment stays in the queue "
                  "until a human chooses"),
    "tomt": (False, "empty fragment"),
}


def node_verdig(plassering: dict) -> dict:
    """The threshold: is the fragment node-worthy — and why, or why not?

    The answer is ALWAYS a verdict WITH a reason, also when the verdict is
    no. A fragment left in the queue with nobody able to see why is the same
    error class the rest of the house exists to prevent: an absence read as
    a choice.
    """
    status = plassering.get("status") or "uten_hjem"
    dom, grunn = NODE_TERSKEL.get(
        status, (False, f"unknown placement status «{status}» — not approved"))
    return {"node_verdig": dom, "terskel": status, "grunn": grunn}


def _ordlaug(tekst: str) -> set[str]:
    """The words in a text — without the JSON punctuation.

    MEASURED 2026-09-18, in a minimal bank: `json.dumps` puts a quotation
    mark up against the value, so `{"name": "trippelpunktet for vann"}` gives
    the word «"trippelpunktet» — and `_stamme` compares five characters, one
    of which is that quotation mark. A fragment the atlas DOES carry was
    reported as `ikke_inne`. In the real bank the words sat inside a
    sentence, so the error stayed hidden until a test used a bank of its
    own.
    """
    return set(re.findall(r"[^\W_]+", _norm(tekst)))


def _ord_i(tekst: str) -> set[str]:
    """The fragment's distinctive words — normalised like the rest of the module."""
    return {w for w in _ordlaug(tekst) if len(w) >= _MIN_ORD}


def _treff_i(noder: list[dict], ord_i: set[str]) -> list[dict]:
    """Which nodes carry the fragment's words — how many, and in which fields.

    The whole node is read, not only the weighted fields. A fragment can
    land in `ontology.assumes`, in a prose field or in `regime.validity`,
    and a confirmation that only looks at `measure` would answer `ikke_inne`
    about a fragment that IS in. The field name is reported, so the strength
    of the hit can be re-checked — a word does not count the same in every
    field.

    `id` is NOT read: it is the node's name, not its content. A fragment
    that only hits a node because the name happens to share a stem with it
    is not a fragment the atlas carries.

    The share (`andel`) is how large a part of the fragment's words the node
    carries. It is computed HERE and not in the call, because it is the same
    measurement no matter who asks — and the verdict (see `bekreft`) reads
    it.
    """
    ut = []
    for n in noder:
        felt: list[str] = []
        truffet: set[str] = set()
        for navn, verdi in n.items():
            if navn == "id":
                continue
            ord_n = _ordlaug(json.dumps(verdi, ensure_ascii=False))
            for o in ord_i:
                if o in ord_n or any(_stamme(o, x) for x in ord_n):
                    truffet.add(o)
                    if navn not in felt:
                        felt.append(navn)
        if felt:
            ut.append({"id": n["id"], "felt": felt, "ord": sorted(truffet),
                       "andel": len(truffet) / len(ord_i) if ord_i else 0.0})
    return sorted(ut, key=lambda d: -d["andel"])


def _generator_fra(repo: str | Path, ref: str) -> dict:
    """The generator's own tables — read from the SAME ref as the bank.

    The generator is what decides whether a node becomes VISIBLE in the
    atlas: without code and without a placement it refuses to build. That
    validation is not repeated here — it is RUN, and it is read from the
    same commit as the bank. Otherwise the two answer from different points
    in time, and a fragment could stand as «visible» because the working
    tree was further ahead than the ref.

    Returns the module namespace (KODER, PLASSERING), or {} when the file is
    not on the ref.
    """
    sti = "scripts/maintenance/efc_atlas_generator.py"
    try:
        kilde = _git(Path(repo), "show", f"{ref}:{sti}")
    except AtlasLesingFeil:
        return {}
    ns: dict = {"__name__": "efc_atlas_generator_fra_ref",
                "__file__": str(Path(repo) / sti)}
    exec(compile(kilde, f"{ref}:{sti}", "exec"), ns)  # noqa: S102
    return ns


def _hvorfor_ikke_synlig(d: dict) -> str:
    """Which link of the closed loop is missing for this node."""
    mangler = []
    if not d["kode"]:
        mangler.append("no entry in KODER — the generator refuses to build")
    if not d["plassering"]:
        mangler.append("no entry in PLASSERING — the chapter is not selected")
    if d["synlighet"] != "offentlig":
        mangler.append(f"visibility: {d['synlighet'] or 'missing'}")
    return "; ".join(mangler) or "unknown"


def bekreft(atlas: dict, tekst: str, generator: dict, *,
            atlas_for: dict | None = None) -> dict:
    """Closed loop: did the fragment COME IN — and is it VISIBLE in the atlas?

    The answer is built from what the atlas ITSELF says, not from the queue:
    the queue is the working memory, the atlas is the truth. A fragment is
    in when a node in the bank carries your words, AND the generator takes
    it (code + placement), AND it is public. All three links are reported —
    also when the answer is no, because a confirmation that only says «no»
    hides which link is missing, and then whoever added the fragment knows
    as little as before.

    `atlas_for` is the bank as it was WHEN the fragment was taken in. When
    it is given, the answer also says whether the hit is NEW since then:
    without it, yesterday's fragment would read as «in» because of a node
    that already existed, and the intake would be credited with something it
    did not do.
    """
    ord_i = _ord_i(tekst)
    treff = _treff_i(atlas.get("noder") or [], ord_i)
    baerere = [t for t in treff if t["andel"] > NODE_ANDEL]
    for_noder = ({t["id"] for t in _treff_i(atlas_for.get("noder") or [], ord_i)
                  if t["andel"] > NODE_ANDEL}
                 if atlas_for is not None else None)

    koder = generator.get("KODER") or {}
    plas = generator.get("PLASSERING") or {}
    oppslag = {n["id"]: n for n in atlas.get("noder") or []}
    detaljer = []
    for t in baerere:
        n = oppslag.get(t["id"]) or {}
        kode, p = koder.get(t["id"]), plas.get(t["id"])
        detaljer.append({
            "id": t["id"],
            "felt": t["felt"],
            "ord": t["ord"],
            "andel": t["andel"],
            "kode": kode,
            "plassering": list(p) if p else None,
            "synlighet": n.get("synlighet"),
            "synlig": bool(kode and p and n.get("synlighet") == "offentlig"),
            "ontology_source": bool((n.get("ontology") or {}).get("source")),
            "ny_siden_inntaket": (None if for_noder is None
                                  else t["id"] not in for_noder),
        })

    synlige = [d for d in detaljer if d["synlig"]]
    if synlige:
        dom = "inne"
        grunn = f"{len(synlige)} visible node(s) carry the words"
    elif detaljer:
        dom = "i_banken_ikke_synlig"
        grunn = "; ".join(f"{d['id']}: {_hvorfor_ikke_synlig(d)}"
                          for d in detaljer[:4])
    else:
        dom = "ikke_inne"
        grunn = ("no node in the bank carries more than half of the words "
                 f"(the rule is NODE_ANDEL = {NODE_ANDEL})")

    naermest = None
    if not detaljer and treff:
        best = treff[0]["andel"]
        like = [t for t in treff if t["andel"] == best]
        naermest = {"andel": best, "ord": treff[0]["ord"],
                    "noder": [t["id"] for t in like[:3]],
                    "antall_paa_topp": len(like)}
        grunn += (f". Closest: {', '.join(naermest['noder'])}"
                  f"{' …' if len(like) > 3 else ''} with "
                  f"{len(treff[0]['ord'])} of {len(ord_i)} words "
                  f"({', '.join(treff[0]['ord'])})")

    truffet = sorted({o for t in treff for o in t["ord"]})
    return {
        "tekst": tekst,
        "dom": dom,
        "kom_inn": bool(synlige),
        "grunn": grunn,
        "atlas": {"kilde": atlas.get("kilde"), "ref": atlas.get("ref"),
                  "commit": atlas.get("commit")},
        "ord": {"i_fragmentet": sorted(ord_i), "truffet": truffet,
                "ikke_truffet": sorted(ord_i - set(truffet))},
        "andel_krav": NODE_ANDEL,
        "naermest": naermest,
        "noder": detaljer,
        "for": (None if atlas_for is None else {
            "commit": atlas_for.get("commit"),
            "noder_som_bar_ordene": sorted(for_noder or []),
        }),
    }


def bekreft_fra_ref(repo: str | Path, tekst: str, *, ref: str = STANDARD_REF,
                    hent: bool = False, at: str | None = None) -> dict:
    """The confirmation read from a ref — bank and generator tables from ONE commit.

    `at` is the commit the fragment was taken in at (from the queue). When
    it is given, the bank is also read as it was THEN, and the answer
    separates «came in now» from «was already there». A commit this clone
    does not have is reported as such — it does not guess that the fragment
    is new.
    """
    repo = Path(repo)
    atlas = les_atlas(repo, ref=ref, hent=hent)
    generator = _generator_fra(repo, ref)
    atlas_for = None
    if at and at != atlas.get("commit"):
        try:
            atlas_for = les_atlas(repo, ref=at)
        except AtlasLesingFeil:
            atlas_for = None
    svar = bekreft(atlas, tekst, generator, atlas_for=atlas_for)
    svar["for_ikke_lest"] = bool(at and atlas_for is None
                                 and at != atlas.get("commit"))
    return svar


def inntak_status(repo: str | Path, fil: str | Path, *,
                  ref: str = STANDARD_REF, hent: bool = False) -> dict:
    """The whole queue, confirmed against a ref — one read of the bank, one answer per row."""
    repo = Path(repo)
    atlas = les_atlas(repo, ref=ref, hent=hent)
    generator = _generator_fra(repo, ref)
    atlas_for: dict[str, dict | None] = {}
    svar = []
    for r in les_inntak(fil):
        commit = (r.get("proveniens") or {}).get("commit")
        if commit and commit != atlas.get("commit"):
            if commit not in atlas_for:
                try:
                    atlas_for[commit] = les_atlas(repo, ref=commit)
                except AtlasLesingFeil:
                    atlas_for[commit] = None
        svar.append(bekreft(atlas, r.get("tekst", ""), generator,
                            atlas_for=atlas_for.get(commit) if commit else None))
    return {"fil": str(fil), "atlas": {"kilde": atlas.get("kilde"),
                                       "ref": ref, "commit": atlas.get("commit")},
            "antall": len(svar), "svar": svar}



def bekreft_tekst(svar: dict) -> str:
    """The confirmation as human-readable text — one form for all three entrances."""
    a = svar.get("atlas") or {}
    L = [f"FRAGMENT: {svar.get('tekst', '')!r}",
         f"  atlas: {a.get('kilde')} @ {(a.get('commit') or '?')[:12]}"]
    o = svar.get("ord") or {"truffet": [], "i_fragmentet": [], "ikke_truffet": []}
    linje = (f"  words: hit {len(o['truffet'])} of {len(o['i_fragmentet'])} "
             f"({', '.join(o['truffet']) or 'none'})")
    if o.get("ikke_truffet"):
        linje += f" — not hit: {', '.join(o['ikke_truffet'])}"
    L.append(linje)
    L.append(f"  {svar['dom'].upper()} — {svar['grunn']}")
    for d in svar.get("noder") or []:
        L.append(f"    {d['id']}  ({len(d['ord'])} av "
                 f"{len(o['i_fragmentet'])} ord: {', '.join(d['ord'])})")
        L.append(f"      fields: {', '.join(d['felt'][:6])}")
        L.append(f"      code: {d['kode'] or 'MISSING'} · plassering: "
                 f"{tuple(d['plassering']) if d['plassering'] else 'MISSING'} · "
                 f"visibility: {d['synlighet'] or 'MISSING'}")
        rad = (f"      ontology.source: "
               f"{'set' if d['ontology_source'] else 'MISSING'}")
        if d.get("ny_siden_inntaket") is not None:
            rad += (f" · new since the intake: "
                    f"{'yes' if d['ny_siden_inntaket'] else 'no'}")
        L.append(rad)
    if svar.get("for"):
        L.append(f"  taken in at: {(svar['for']['commit'] or '?')[:12]} — "
                 f"nodes that carried the words then: "
                 f"{', '.join(svar['for']['noder_som_bar_ordene']) or 'none'}")
    if svar.get("for_ikke_lest"):
        L.append("  note: the intake commit is not in this clone — "
                 "before/after is not decided, so the answer says nothing "
                 "about whether the hit is new")
    return "\n".join(L)


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Read the atlas — or look something up in it.")
    p.add_argument("repo", nargs="?", default=".", help="path to the repo")
    p.add_argument("--emne", "-e", help="look up a topic instead of reading everything")
    p.add_argument("--ref", default=STANDARD_REF, help=f"git ref (default: {STANDARD_REF})")
    p.add_argument("--hent", action="store_true", help="fetch origin first")
    p.add_argument("--alle", action="store_true", help="show all hits, not just the strongest")
    p.add_argument("--node", help="rotate around ONE node — show all fields")
    p.add_argument("--perspektiv", help="rotate: filter on perspektiv (paradigm/consensus/academia)")
    p.add_argument("--fase", help="rotate: filter on phase (instrument/regime_engine/...)")
    p.add_argument("--domene", help="rotate: filter on buss_domene")
    p.add_argument("--maaleform", action="store_true",
                   help="rotate: separate what MEASURES from what is derived")
    p.add_argument("--proxy", action="store_true", help="rotate: show all proxy chains")
    p.add_argument("--akser", action="store_true",
                   help="list ALL the axes the atlas carries — also the new ones")
    p.add_argument("--akse", help="rotate around an arbitrary axis: `sti` or `sti=verdi`")
    p.add_argument("--alt", dest="alt", help="THE WHOLE: everything about a node, in one reading")
    p.add_argument("--plasser", help="place a NEW fragment: where does it belong, and what is missing")
    p.add_argument("--innta", help="take in a fragment into the retain queue (no node is created)")
    p.add_argument("--kilde", default="samtale", help="provenance source for --innta")
    p.add_argument("--inntak-fil", help="alternative JSONL file for --innta")
    p.add_argument("--bekreft", help="closed loop: did this fragment come IN to the atlas?")
    p.add_argument("--inntak-status", action="store_true",
                   help="closed loop for the WHOLE intake queue")
    p.add_argument("--hop", help="N hops from a node:  or ")
    p.add_argument("--fragment", help="rotate around ONE fragment: node + all couplings")
    p.add_argument("--oversikt", action="store_true",
                   help="THE WHOLE atlas at once: what is what, where, how many")
    a = p.parse_args()

    # THE WHOLE — everything about a node
    if a.alt:
        atlas = les_atlas(a.repo, ref=a.ref)
        print(helhet_tekst(atlas, a.alt))
        sys.exit(0)

    # THE RETAIN INTAKE — the queue, the threshold and the closed loop.
    # No node is created automatically: the intake PROPOSES, a human chooses.
    if a.innta:
        atlas = les_atlas(a.repo, ref=a.ref)
        generator = _generator_fra(a.repo, a.ref)
        fil = a.inntak_fil or str(Path(a.repo) / "data" / "inntak" /
                                  "atlas_fragmenter.jsonl")
        record = skriv_inntak(atlas, a.innta, fil, kilde=a.kilde)
        print(f"FRAGMENT: {a.innta!r}  ->  {record['plasseringsstatus']}")
        print(f"  provenance: {record['kilde']}")
        print(f"  threshold: {'NODE-WORTHY' if record['node_verdig'] else 'NOT node-worthy'}"
              f" ({record['terskel']}) — {record['terskel_grunn']}")
        print(f"  written to: {fil}")
        if record["node_verdig"]:
            print("  queue: fragment proposal — no node is created automatically")
        else:
            print("  queue: stays there — a human has to decide")
        # The closed loop, at once: the same read that wrote the fragment.
        print(bekreft_tekst(bekreft(atlas, a.innta, generator)))
        sys.exit(0)

    # THE CLOSED LOOP — did the fragment come in?
    if a.bekreft:
        print(bekreft_tekst(bekreft_fra_ref(a.repo, a.bekreft, ref=a.ref,
                                            hent=a.hent)))
        sys.exit(0)

    if a.inntak_status:
        fil = a.inntak_fil or str(Path(a.repo) / "data" / "inntak" /
                                  "atlas_fragmenter.jsonl")
        s = inntak_status(a.repo, fil, ref=a.ref, hent=a.hent)
        print(f"THE QUEUE: {s['fil']} — {s['antall']} fragment(s)")
        print(f"  atlas: {s['atlas']['kilde']} @ "
              f"{(s['atlas']['commit'] or '?')[:12]}")
        if not s["antall"]:
            print("  empty — nothing has been taken in here")
        for x in s["svar"]:
            print(bekreft_tekst(x))
        print(f"  {sum(1 for x in s['svar'] if x['kom_inn'])} inne av "
              f"{s['antall']}")
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
            print(f"  near nodes: {', '.join(p_['naere_noder'][:4])}")
        o = p_.get("oppsummering") or {}
        print(f"  {len(p_['mangler'])} fields before it is a node: "
              f"{o.get('struktur', 0)} structure (derived), "
              f"{o.get('vurdering', 0)} assessment (proposed), "
              f"{o.get('paastand', 0)} claim (declared explicitly)")
        print(f"  of those, {o.get('leses', 0)} are read by at least one of the "
              f"{o.get('lesere_av', 0)} readers and "
              f"{o.get('uten_leser', 0)} by nobody:")
        print(f"    fields with no reader: "
              f"{', '.join(o.get('uten_leser_felt', [])) or '(none)'}")
        if o.get("umaalt"):
            print(f"    NOT MEASURED — no mutation measurement behind them: "
                  f"{', '.join(o['umaalt'])}")
        print("    (the schema still requires them — removing one from "
              "`required` is a decision, not a rule of code)")
        for k in p_.get("krav", []):
            merke = "SCHEMA" if k["kilde"] == "skjema" else "HOUSE "
            if k.get("forslag"):
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"= {k['forslag']!r}  ({k['grunn']})")
            elif k["klasse"] == "struktur":
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"could not be derived: {k['grunn']}")
            else:
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"filled {k['fylt_i_banken']} in the bank")
        sys.exit(0)

    # KOBLINGENE — 1-hop, 2-hop, 3-hop
    if a.hop or a.fragment:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.fragment:
            f = fragment(atlas, a.fragment)
            if not f["finnes"]:
                print(f"ERROR: 'the fragment {a.fragment}' does not exist. "
                      f"Nearby: {', '.join(f['naere']) or 'none'}")
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
            print(f"{len(stier)} nodes within {d or 1} hops from {node}:")
            for nid, (sti, typer) in sorted(stier.items(), key=lambda x: len(x[1][0]))[:22]:
                print(f"  {' -> '.join(sti)[:52]:54} [{' -> '.join(typer)}]")
        sys.exit(0)

    # THE OVERVIEW — global state, not a search
    if a.oversikt:
        atlas = les_atlas(a.repo, ref=a.ref)
        o = oversikt(atlas)
        print(f"THE ATLAS — {len(atlas.get('noder') or [])} nodes, "
              f"{len(o)} axes that separate")
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
            print(f"{len(treff)} nodes  axis={navn}"
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
                  + (f" perspective={a.perspektiv}" if a.perspektiv else "")
                  + (f" phase={a.fase}" if a.fase else "")
                  + (f" domain={a.domene}" if a.domene else ""))
            for n in treff:
                ep = (n.get("episenter") or "")[:56]
                print(f"  {n['id']:34} {n.get('phase','?'):18} {ep}")
        sys.exit(0)

    if a.emne:
        s = finn(a.repo, a.emne, ref=a.ref, hent=a.hent)
        akseinfo = f" via akse {s['akse']}" if s.get("akse") else ""
        print(f"{s['kilde']} @ {s['commit'][:8]} — {s['antall']} hit(s) on "
              f"«{s['emne']}»{akseinfo}")
        if s["hull"]:
            kh = s["kjent_hull"]
            if kh:
                ant = kh.get("meldinger")
                storrelse = f" · {ant} messages" if ant is not None else ""
                print(f"  KNOWN HOLE — measured as «{kh['status']}»{storrelse}")
                if kh.get("begrunnelse"):
                    print(f"  reason: {kh['begrunnelse']}")
                if ant is None:
                    print("  (size unknown — UKJENT: no measured volume for "
                          "this domain)")
            else:
                print("  THE ATLAS DOES NOT KNOW — no node carries this "
                      "topic, and it is not a measured coverage hole.")
            sys.exit(0)
        kh = s["kjent_hull"]
        if kh:
            print(f"  (the domain {kh['domene']} is measured as «{kh['status']}»)")
        if s["for_bredt"]:
            print(f"  TOO BROAD — {s['raad']}")
        # An answer of 80 lines is not an answer. Show the strongest, and say
        # how many lie below — the reader can ask for all with --alle.
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
            if t["trefftype"] == "navnerom":
                print(f"    reason: {t['grunn']}")
        if not a.alle and s["antall"] > _VIS_MAKS:
            print(f"  ... and {s['antall'] - _VIS_MAKS} more — use --alle for the whole list")
    else:
        d = les_atlas(a.repo, ref=a.ref, hent=a.hent)
        print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} nodes")
