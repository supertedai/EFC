#!/usr/bin/env python3
"""atlas_volum — the missing dimension of the coverage file: SIZE.

Found by USING the atlas lookup (PR #472), not by testing it. The answer
"KNOWN GAP — measured as `ikke_dekket`" was correct, but without a size.
Measured 2026-09-17 against `verden_domener`:

    verden.vaer        190 229 messages    ikke_dekket
    verden.utdanning     2 598 messages    ikke_dekket

A 73× difference, the same answer. A gap of 190 000 and one of 200 are not
the same thing, and a map that cannot tell them apart cannot say where the
next node is to be built either. `kosmos.kosmologi` is `dekket` with 1
prediction — so the map grants more structure to the smallest channel than
to the largest one.

## The volume is a MEASUREMENT, not a table

The numbers are read from the bus at generation time (`--maal`) and written
to `schema/nats_domener.snapshot.json`, which already carries a measurement
time, a source and an expiry date (the test
`test_snapshottet_har_ikke_gaatt_ut_paa_dato`). The declaration file's
`meldinger` is DERIVED as the sum of the snapshot's per-subject numbers —
not written by hand. The same requirement as the `noder` lists: what stands
in the file must be derivable, and a test must derive it.

    A hardcoded volume table would rot at the first change in bus
    traffic — and would lie the same way "82 nodes" did.

## One implementation of the bus protocol

`--maal` talks to the bus through the house's own tool for it, and calls
`verden_domener` — the same source the card was measured against. The path
to the tool stands in the environment variable `VERDEN_MCP`; the module does
not carry it itself (the published surface must not name a host, and a key
that lay here would be a shared one). The protocol — inbox randomness,
Nagle, frame buffering — is fine-tuned there; it is not duplicated here. A
second implementation would be two truths about one interface, and one of
them would fail silently.

## Reading

`hull()` sorts by SIZE, not alphabetically — that is the whole point. It
reads from a git ref (the same rule as `atlas_lesing`), so that a working
copy that answers cannot read as a live atlas.

    python3 scripts/atlas_volum.py --hull          # ikke_dekket, largest first
    python3 scripts/atlas_volum.py --alle          # every domain, largest first
    python3 scripts/atlas_volum.py --maal          # measure the bus, write files
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
STANDARD_REF = "origin/main"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"
DEKNING_STI = "schema/atlas_dekning.json"

#: The house's tool for the bus. The path can be pointed elsewhere with
#: `VERDEN_MCP` — it lies outside the repository on purpose: the key is per
#: door (rule no. 1 in verden-mcp), and a key that lay in this repository
#: would be a shared one.
VERDEN_MCP = Path(os.environ.get(
    "VERDEN_MCP", str(Path.home() / ".hermes" / "scripts" / "verden-mcp.py")))

#: The user's own `.env` — where `NATS_VERDEN` stands when the tool runs as
#: an MCP server under Hermes. Read only to set the environment the tool
#: itself expects; the contents are never printed.
NATS_ENV = Path(os.environ.get(
    "NATS_ENV_FIL", str(Path.home() / ".hermes" / ".env")))


class VolumFeil(RuntimeError):
    """The measurement or the reading could not be done. Never a guessed
    number."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise VolumFeil(f"git {' '.join(args)} failed in {repo}: "
                        f"{p.stderr.strip()}")
    return p.stdout


def les_fra_ref(repo: str | Path = ROT, ref: str = STANDARD_REF, *,
                hent: bool = False) -> dict:
    """Read the measurement and the declaration from `ref`, never the worktree.

    Returns both files together with the commit they were read from, so that
    a stale ref is visible in the result instead of in the reader's
    assumption.
    """
    repo = Path(repo)
    if hent:
        _git(repo, "fetch", "-q", "origin")
    commit = _git(repo, "rev-parse", ref).strip()
    ut: dict = {"kilde": f"git:{ref}", "ref": ref, "commit": commit}
    for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI)):
        raa = _git(repo, "show", f"{ref}:{sti}")
        try:
            ut[nokkel] = json.loads(raa)
        except json.JSONDecodeError as e:
            raise VolumFeil(f"{ref}:{sti} is not valid JSON: {e}") from e
    return ut


def meldinger_per_domene(snapshot: dict) -> dict[str, int]:
    """The sum of the MEASURED per-subject numbers, per domain.

    The declaration file's `meldinger` must be exactly this number. The test
    derives it again and compares, so the field cannot rot into a claim from
    an earlier measurement.

    Raises when the measurement lacks the numbers. The first version of the
    file carried the subjects as a LIST — that form exists in refs older
    than this module, and a reader that crashed with `AttributeError: 'list'
    object has no attribute 'values'` said nothing about what was missing or
    what was to be done about it. The form is therefore checked explicitly.
    """
    ut: dict[str, int] = {}
    for domene, rad in (snapshot.get("domener") or {}).items():
        emner = rad.get("emner")
        if not isinstance(emner, dict):
            raise VolumFeil(
                f"the measurement does not carry a count per subject "
                f"({domene}: {type(emner).__name__}). The snapshot predates "
                f"the volume measurement — run `atlas_volum.py --maal` "
                f"against the bus, or read a ref that already carries the "
                f"volume (`--ref HEAD`). The volume cannot be derived from a "
                f"list of names, and it must not be guessed.")
        ut[domene] = sum(emner.values())
    return ut


def hull(dekning: dict, snapshot: dict | None = None, *,
         statuser: tuple[str, ...] | None = ("ikke_dekket",),
         topp: int | None = None) -> list[dict]:
    """The gaps, sorted by MEANING — messages descending, then name.

    Alphabetical order is random information about the world: it says what
    the domain is called, not how much lies in it. The sorting here is the
    only reason `verden.vaer` (190 000) does not read like `verden.utdanning`
    (2 600).

    `statuser=None` gives every domain — then a `dekket` channel that
    carries a lot behind one node shows up too.
    """
    maalt = meldinger_per_domene(snapshot) if snapshot else {}
    rader: list[dict] = []
    for navn, rad in (dekning.get("domener") or {}).items():
        if statuser is not None and rad.get("status") not in statuser:
            continue
        emne_antall = ((snapshot or {}).get("domener", {})
                       .get(navn, {}).get("emner") or {})
        emner = sorted(
            ((e, emne_antall.get(e)) for e in (rad.get("emner") or [])),
            key=lambda p: (-(p[1] or 0), p[0]))
        rader.append({
            "domene": navn,
            "status": rad.get("status"),
            "meldinger": maalt.get(navn, rad.get("meldinger", 0)),
            "noder": list(rad.get("noder") or []),
            "emner": emner,
        })
    rader.sort(key=lambda r: (-r["meldinger"], r["domene"]))
    return rader[:topp] if topp else rader


def _last_env(sti: Path = NATS_ENV) -> bool:
    """Set `NATS_VERDEN` from the house's `.env` when the environment lacks it.

    The tool reads the URL from the environment because Hermes starts it
    with the user's own `.env`. When the script is run from a shell, it is
    not set — and then the measurement fails, reporting that NATS_VERDEN is
    missing, even though the key exists.
    """
    if os.environ.get("NATS_VERDEN"):
        return True
    try:
        linjer = sti.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for linje in linjer:
        if linje.startswith("NATS_VERDEN="):
            os.environ["NATS_VERDEN"] = linje.split("=", 1)[1].strip().strip("'\"")
            return True
    return False


def _kort_emne(domene: str, emne: str) -> str:
    """`verden.vaer.prediksjon.metno` -> `prediksjon.metno`.

    The bus names the subject IN FULL; the domain is already the key. The
    snapshot (and the declaration) carries the short form — it is relative to
    the domain, and a full form would repeat the domain name in every row.
    """
    prefiks = f"{domene}."
    return emne[len(prefiks):] if emne.startswith(prefiks) else emne


def maal_bussen(mcp_fil: str | Path | None = None) -> dict:
    """Measure the bus: `{domene: {emne: antall}}` — and the empty streams.

    Fails LOUDLY when the tool or the credential is missing. A gap without a
    number is not a measured gap, and a guessed number is worse than no
    number: it looks like a measurement.
    """
    fil = Path(mcp_fil or VERDEN_MCP)
    if not fil.exists():
        raise VolumFeil(
            f"the verden tool does not exist: {fil} — the measurement "
            f"cannot be made. Set VERDEN_MCP, or run where the tool lives.")
    if not _last_env():
        raise VolumFeil(
            "NATS_VERDEN is not set, and no .env carrying it was found "
            f"({NATS_ENV}). The measurement requires the user's OWN "
            f"consumer key.")
    spec = importlib.util.spec_from_file_location("verden_mcp_volum", fil)
    if spec is None or spec.loader is None:
        raise VolumFeil(f"could not load {fil} as a module")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    try:
        svar = modul.verden_domener({})
    except Exception as e:                                    # noqa: BLE001
        raise VolumFeil(f"verden_domener failed: {type(e).__name__}: {e}") from e
    domener = {navn: {_kort_emne(navn, r["emne"]): int(r["meldinger"])
                      for r in rader}
               for navn, rader in sorted((svar.get("domener") or {}).items())}
    return {"domener": domener,
            "tomme_stroemmer": svar.get("tomme_stroemmer") or []}


def _skriv_json(sti: Path, data: dict) -> None:
    sti.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")


def skriv_snapshot(sti: str | Path, domener: dict, *,
                   lest_av: str, maalt: str | None = None) -> dict:
    """Write the measurement. The provenance is data, not a comment."""
    maalt = maalt or datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "_proveniens": {
            "kilde": ("The NATS bus, verden_domener (MCP) — subjects and "
                      "message counts read from the JetStream streams' own "
                      "state.subjects"),
            "maalt": maalt,
            "lest_av": lest_av,
            "merknad": ("Per-subject counts ARE available: `state.subjects` "
                        "in STREAM.INFO carries the count per subject. The "
                        "earlier note here said the opposite — it was an "
                        "assumption about NATS' monitoring API, not a "
                        "measurement of the JetStream API. The numbers here "
                        "are measured, and the coverage file's `meldinger` "
                        "is their sum."),
        },
        "domener": {navn: {"emner": dict(sorted(emner.items()))}
                    for navn, emner in sorted(domener.items())},
    }
    _skriv_json(Path(sti), data)
    return data


def oppdater_dekning(dekning: dict, domener: dict) -> tuple[dict, dict]:
    """Set `meldinger` per domain = the sum of the measured subject counts.

    Everything else in the declaration is the HUMAN'S: `status` and
    `begrunnelse` are a position taken, not a derivation. This function does
    not touch them — it writes only the number, and reports what it could
    not write: new domains and new subjects must trip the invariant until
    someone has taken a position on them.

    Returns `(ny_dekning, rapport)`.
    """
    maalt = {navn: sum(emner.values()) for navn, emner in domener.items()}
    rapport: dict = {"nye_domener": [], "nye_emner": {}, "borte": []}
    ny: dict = {}
    for navn, rad in (dekning.get("domener") or {}).items():
        if navn not in maalt:
            rapport["borte"].append(navn)
        nye = sorted(set(domener.get(navn, {})) - set(rad.get("emner") or []))
        if nye:
            rapport["nye_emner"][navn] = nye
        ny[navn] = {
            "status": rad.get("status"),
            "meldinger": maalt.get(navn, 0),
            "noder": list(rad.get("noder") or []),
            "begrunnelse": rad.get("begrunnelse", ""),
            "emner": list(rad.get("emner") or []),
        }
    rapport["nye_domener"] = sorted(set(domener) - set(dekning.get("domener") or {}))
    ut = dict(dekning)
    ut["domener"] = ny
    return ut, rapport


def formater(rader: list[dict]) -> str:
    """The table the human reads — largest first, with the subjects below."""
    if not rader:
        return "  (no gaps in this slice)"
    bredde = max(len(r["domene"]) for r in rader)
    linjer = []
    for r in rader:
        linjer.append(f"{r['meldinger']:>10}  {r['status']:<11}  "
                      f"{r['domene']:<{bredde}}  "
                      f"{len(r['noder'])} node(s), "
                      f"{len(r['emner'])} subject(s)")
        for emne, antall in r["emner"][:3]:
            tall = "?" if antall is None else f"{antall}"
            linjer.append(f"{'':>10}  {'':<11}  {emne}  {tall}")
    return "\n".join(linjer)


def hoved(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="The coverage file's volume — measured from the bus, "
                    "sorted by meaning.")
    ap.add_argument("--ref", default=STANDARD_REF,
                    help=f"git ref to read from (default: {STANDARD_REF})")
    ap.add_argument("--topp", type=int, default=None,
                    help="show only the N largest")
    ap.add_argument("--hull", action="store_true",
                    help="ikke_dekket, largest first (default)")
    ap.add_argument("--alle", action="store_true",
                    help="every domain, not only ikke_dekket")
    ap.add_argument("--maal", action="store_true",
                    help="measure the bus and write the snapshot + "
                         "coverage file")
    ap.add_argument("--torr", action="store_true",
                    help="with --maal: write nothing, show what would "
                         "have been written")
    ap.add_argument("--repo", default=str(ROT))
    args = ap.parse_args(argv)

    repo = Path(args.repo)

    if args.maal:
        # THE MEASUREMENT READS THE WORKING TREE, not the ref: it writes to
        # the working tree, and a pre-image from the ref would silently have
        # discarded uncommitted changes to the declaration. Reading the ref
        # is for the one who ASKS; measuring is for the one who WRITES.
        sti = repo / DEKNING_STI
        if not sti.exists():
            raise VolumFeil(f"{sti} does not exist — it is the declaration "
                            f"that is to receive a volume, and it cannot be "
                            f"guessed into place")
        try:
            dekning = json.loads(sti.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise VolumFeil(f"{sti} is not valid JSON: {e}") from e
        ny = maal_bussen()
        domener = ny["domener"]
        lest_av = os.environ.get(
            "ATLAS_LEST_AV",
            f"{os.environ.get('HERMES_PROFILE', 'unknown')} "
            f"(scripts/atlas_volum.py)")
        if not args.torr:
            skriv_snapshot(repo / SNAPSHOT_STI, domener, lest_av=lest_av)
        ny_dekning, rapport = oppdater_dekning(dekning, domener)
        if not args.torr:
            _skriv_json(sti, ny_dekning)
        for domene, rader in sorted(
                domener.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"{sum(rader.values()):>10}  {domene}")
        if rapport["nye_domener"]:
            print(f"\nNOT DECLARED ({len(rapport['nye_domener'])}) — carries "
                  f"messages, is not listed in {DEKNING_STI}. The atlas does "
                  f"not know they exist, and the invariant must TRIP until "
                  f"someone has taken a position on them:")
            for d in rapport["nye_domener"]:
                print(f"    {d}  {sum(domener[d].values())}")
        for domene, emner in sorted(rapport["nye_emner"].items()):
            print(f"\nNEW SUBJECTS in {domene} — no position taken: {emner}")
        if rapport["borte"]:
            print(f"\nDECLARED, BUT OUT OF THE MEASUREMENT: "
                  f"{rapport['borte']} — "
                  f"the declaration promises a world that is no longer there. "
                  f"Bus subjects inside the retention window disappear on "
                  f"their own; remove them from the file or explain why.")
        if args.torr:
            print("\n(--torr: nothing written)")
        return 0

    lest = les_fra_ref(repo, args.ref)
    print(f"{lest['kilde']} @ {lest['commit'][:8]}", file=sys.stderr)
    rader = hull(lest["dekning"], lest["snapshot"],
                 statuser=None if args.alle else ("ikke_dekket",),
                 topp=args.topp)
    print(formater(rader))
    return 0


def _hoved_med_feil(argv: list[str] | None = None) -> int:
    """VolumFeil is an ANSWER, not a stack trace.

    A reader who gets "the ref does not carry the volume yet" knows what to
    do; a reader who gets a stack trace tries again and wonders whether
    something is broken. The message goes to stderr, not into the table.
    """
    try:
        return hoved(argv)
    except VolumFeil as e:
        print(f"atlas_volum: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_hoved_med_feil())
