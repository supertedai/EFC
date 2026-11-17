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

## The measurement is ONE step, not two

`--maal` writes three things from one reading of the bus: the snapshot, the
`domener` section of `schema/atlas_dekning.json`, and its `kilder` section —
the source axis. The last one is a DERIVATION, not a separate chore: it needs
the measurement and the names the nodes write, and both are here. It is
nevertheless not re-implemented here; `scripts/atlas_kilder.py` owns that
rule, and this module calls it.

Measured 2026-11-17, while it was still a chore: `--maal` updated `domener`
and the snapshot, whoever measured forgot `atlas_kilder.py --skriv`, and the
source axis kept the message counts from an earlier measurement — ~40
segments, silent, until a test said so, and then reconciled by hand. A step
that has to be REMEMBERED is not a derivation; it is a habit, and it slipped.

Everything is therefore derived BEFORE anything is written. A run that cannot
derive the source axis (no `schema/regime_nodes.jsonld` in the working tree,
say) writes NEITHER file: a new snapshot beside a stale source axis is the
exact state this step exists to remove.

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
NODER_STI = "schema/regime_nodes.jsonld"

#: The source axis has ONE implementation, in `atlas_kilder`, and the
#: measurement re-derives it (see `--maal`). Importing that module is what
#: keeps it at one: a copy here would be two truths about one axis, and the
#: copy that was not run would be the one that rotted.
for _sti in (ROT / "scripts",):
    if str(_sti) not in sys.path:
        sys.path.insert(0, str(_sti))

import atlas_kilder as ak  # noqa: E402

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
    out: dict = {"kilde": f"git:{ref}", "ref": ref, "commit": commit}
    for key, path in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI)):
        raw = _git(repo, "show", f"{ref}:{path}")
        try:
            out[key] = json.loads(raw)
        except json.JSONDecodeError as e:
            raise VolumFeil(f"{ref}:{path} is not valid JSON: {e}") from e
    return out


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
    counts: dict[str, int] = {}
    for domain, row in (snapshot.get("domener") or {}).items():
        subjects = row.get("emner")
        if not isinstance(subjects, dict):
            raise VolumFeil(
                f"the measurement does not carry a count per subject "
                f"({domain}: {type(subjects).__name__}). The snapshot "
                f"predates the volume measurement — run `atlas_volum.py "
                f"--maal` against the bus, or read a ref that already "
                f"carries the volume (`--ref HEAD`). The volume cannot be "
                f"derived from a list of names, and it must not be guessed.")
        counts[domain] = sum(subjects.values())
    return counts


def hull(coverage: dict, snapshot: dict | None = None, *,
         statuser: tuple[str, ...] | None = ("ikke_dekket",),
         top: int | None = None) -> list[dict]:
    """The gaps, sorted by MEANING — messages descending, then name.

    Alphabetical order is random information about the world: it says what
    the domain is called, not how much lies in it. The sorting here is the
    only reason `verden.vaer` (190 000) does not read like `verden.utdanning`
    (2 600).

    `statuser=None` gives every domain — then a `dekket` channel that
    carries a lot behind one node shows up too.
    """
    measured = meldinger_per_domene(snapshot) if snapshot else {}
    rows: list[dict] = []
    for name, row in (coverage.get("domener") or {}).items():
        if statuser is not None and row.get("status") not in statuser:
            continue
        subject_counts = ((snapshot or {}).get("domener", {})
                          .get(name, {}).get("emner") or {})
        subjects = sorted(
            ((e, subject_counts.get(e)) for e in (row.get("emner") or [])),
            key=lambda pair: (-(pair[1] or 0), pair[0]))
        rows.append({
            "domene": name,
            "status": row.get("status"),
            "meldinger": measured.get(name, row.get("meldinger", 0)),
            "noder": list(row.get("noder") or []),
            "emner": subjects,
        })
    rows.sort(key=lambda r: (-r["meldinger"], r["domene"]))
    return rows[:top] if top else rows


def _load_env(path: Path = NATS_ENV) -> bool:
    """Set `NATS_VERDEN` from the house's `.env` when the environment lacks it.

    The tool reads the URL from the environment because Hermes starts it
    with the user's own `.env`. When the script is run from a shell, it is
    not set — and then the measurement fails, reporting that NATS_VERDEN is
    missing, even though the key exists.
    """
    if os.environ.get("NATS_VERDEN"):
        return True
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in lines:
        if line.startswith("NATS_VERDEN="):
            os.environ["NATS_VERDEN"] = line.split("=", 1)[1].strip().strip("'\"")
            return True
    return False


def _short_subject(domain: str, subject: str) -> str:
    """`verden.vaer.prediksjon.metno` -> `prediksjon.metno`.

    The bus names the subject IN FULL; the domain is already the key. The
    snapshot (and the declaration) carries the short form — it is relative to
    the domain, and a full form would repeat the domain name in every row.
    """
    prefix = f"{domain}."
    return subject[len(prefix):] if subject.startswith(prefix) else subject


def maal_bussen(mcp_path: str | Path | None = None) -> dict:
    """Measure the bus: `{domene: {emne: antall}}` — and the empty streams.

    Fails LOUDLY when the tool or the credential is missing. A gap without a
    number is not a measured gap, and a guessed number is worse than no
    number: it looks like a measurement.
    """
    tool_path = Path(mcp_path or VERDEN_MCP)
    if not tool_path.exists():
        raise VolumFeil(
            f"the verden tool does not exist: {tool_path} — the measurement "
            f"cannot be made. Set VERDEN_MCP, or run where the tool lives.")
    if not _load_env():
        raise VolumFeil(
            "NATS_VERDEN is not set, and no .env carrying it was found "
            f"({NATS_ENV}). The measurement requires the user's OWN "
            f"consumer key.")
    spec = importlib.util.spec_from_file_location(
        "verden_mcp_volum", tool_path)
    if spec is None or spec.loader is None:
        raise VolumFeil(f"could not load {tool_path} as a module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    try:
        answer = module.verden_domener({})
    except Exception as e:                                    # noqa: BLE001
        raise VolumFeil(f"verden_domener failed: {type(e).__name__}: {e}") from e
    domains = {name: {_short_subject(name, r["emne"]): int(r["meldinger"])
                      for r in rows}
               for name, rows in sorted((answer.get("domener") or {}).items())}
    return {"domener": domains,
            "tomme_stroemmer": answer.get("tomme_stroemmer") or []}


def _write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def snapshot_data(domains: dict, *, lest_av: str,
                  maalt: str | None = None) -> dict:
    """The measurement in the shape of the file it is written to.

    A BUILDER, not a writer: the same object is written to
    `schema/nats_domener.snapshot.json` AND handed to the derivation of the
    source axis. Two readings of one measurement must not exist — not even as
    two dicts built a few lines apart.
    """
    maalt = maalt or datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
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
        "domener": {name: {"emner": dict(sorted(subjects.items()))}
                    for name, subjects in sorted(domains.items())},
    }


def skriv_snapshot(path: str | Path, domains: dict, *,
                   lest_av: str, maalt: str | None = None) -> dict:
    """Write the measurement. The provenance is data, not a comment."""
    data = snapshot_data(domains, lest_av=lest_av, maalt=maalt)
    _write_json(Path(path), data)
    return data


def les_noder(repo: Path) -> dict:
    """The node bank, read from the WORKING TREE — the same rule as the
    declaration, and for the same reason: the source axis is derived from the
    names the nodes write NOW, not from what a ref said when they were last
    committed.

    Raises rather than skipping the derivation. The alternative — measure the
    domains and leave the sources as they stood — is the drift this step
    exists to remove, and it is silent by construction: both files parse.
    """
    path = Path(repo) / NODER_STI
    if not path.exists():
        raise VolumFeil(
            f"{path} does not exist — the source axis (`kilder`) is derived "
            f"from the names the nodes write in lagdeling.kilde.kilde, and it "
            f"cannot be derived without the bank. Nothing was written: a "
            f"snapshot updated next to a stale source axis is the drift this "
            f"step exists to remove.")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise VolumFeil(f"{path} is not valid JSON: {e}") from e
    if not isinstance(data.get("nodes"), list):
        raise VolumFeil(
            f"{path} carries no `nodes` list — the bank cannot be read, and "
            f"the source axis cannot be derived from a guess. Nothing was "
            f"written.")
    return data


def oppdater_dekning(coverage: dict, domains: dict) -> tuple[dict, dict]:
    """Set `meldinger` per domain = the sum of the measured subject counts.

    Everything else in the declaration is the HUMAN'S: `status` and
    `begrunnelse` are a position taken, not a derivation. This function does
    not touch them — it writes only the number, and reports what it could
    not write: new domains and new subjects must trip the invariant until
    someone has taken a position on them.

    Returns `(updated, report)`.
    """
    measured = {name: sum(subjects.values())
                for name, subjects in domains.items()}
    report: dict = {"nye_domener": [], "nye_emner": {}, "borte": []}
    updated: dict = {}
    for name, row in (coverage.get("domener") or {}).items():
        if name not in measured:
            report["borte"].append(name)
        new_subjects = sorted(set(domains.get(name, {}))
                              - set(row.get("emner") or []))
        if new_subjects:
            report["nye_emner"][name] = new_subjects
        updated[name] = {
            "status": row.get("status"),
            "meldinger": measured.get(name, 0),
            "noder": list(row.get("noder") or []),
            "begrunnelse": row.get("begrunnelse", ""),
            "emner": list(row.get("emner") or []),
        }
    report["nye_domener"] = sorted(set(domains)
                                   - set(coverage.get("domener") or {}))
    result = dict(coverage)
    result["domener"] = updated
    return result, report


def format_table(rows: list[dict]) -> str:
    """The table the human reads — largest first, with the subjects below."""
    if not rows:
        return "  (no gaps in this slice)"
    width = max(len(r["domene"]) for r in rows)
    lines = []
    for r in rows:
        lines.append(f"{r['meldinger']:>10}  {r['status']:<11}  "
                     f"{r['domene']:<{width}}  "
                     f"{len(r['noder'])} node(s), "
                     f"{len(r['emner'])} subject(s)")
        for subject, count in r["emner"][:3]:
            value = "?" if count is None else f"{count}"
            lines.append(f"{'':>10}  {'':<11}  {subject}  {value}")
    return "\n".join(lines)


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
                    help="measure the bus and write the snapshot and BOTH "
                         "axes of the coverage file (domains and sources) — "
                         "one step, so the derivation cannot be forgotten")
    ap.add_argument("--torr", action="store_true",
                    help="with --maal: write nothing, show what would "
                         "have been written (and what would have tripped)")
    ap.add_argument("--repo", default=str(ROT))
    args = ap.parse_args(argv)

    repo = Path(args.repo)

    if args.maal:
        # THE MEASUREMENT READS THE WORKING TREE, not the ref: it writes to
        # the working tree, and a pre-image from the ref would silently have
        # discarded uncommitted changes to the declaration. Reading the ref
        # is for the one who ASKS; measuring is for the one who WRITES. The
        # node bank is read the same way, because the source axis is derived
        # from the names the nodes write — and the names that matter are the
        # ones standing in this tree.
        declaration_path = repo / DEKNING_STI
        if not declaration_path.exists():
            raise VolumFeil(f"{declaration_path} does not exist — it is the "
                            f"declaration that is to receive a volume, and "
                            f"it cannot be guessed into place")
        try:
            coverage = json.loads(
                declaration_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise VolumFeil(
                f"{declaration_path} is not valid JSON: {e}") from e
        measurement = maal_bussen()
        domains = measurement["domener"]
        noder = les_noder(repo)
        lest_av = os.environ.get(
            "ATLAS_LEST_AV",
            f"{os.environ.get('HERMES_PROFILE', 'unknown')} "
            f"(scripts/atlas_volum.py)")
        # EVERYTHING IS DERIVED BEFORE ANYTHING IS WRITTEN. A run that wrote
        # the snapshot and then failed on the source axis would leave exactly
        # the drift this step exists to remove: a fresh measurement beside a
        # stale derivation, and both files parse.
        snapshot = snapshot_data(domains, lest_av=lest_av)
        updated, report = oppdater_dekning(coverage, domains)
        updated["kilder"] = ak.seksjon_fra_maaling(
            snapshot, noder["nodes"], coverage.get("kilder") or {})
        if not args.torr:
            _write_json(repo / SNAPSHOT_STI, snapshot)
            _write_json(declaration_path, updated)
        for domain, subjects in sorted(
                domains.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"{sum(subjects.values()):>10}  {domain}")
        print(f"\nSOURCE AXIS: {len(updated['kilder'])} source segments "
              f"re-derived from the same measurement — no separate `--skriv` "
              f"step, because a step that has to be remembered is the reason "
              f"they rotted")
        # What the measurement CANNOT decide is named, not hidden: a `navn` is
        # a person's collection, an `eier` is a position, and a shared source
        # without an owner must carry its reason. The invariant trips until
        # somebody takes it — the same rule as the undeclared domains above.
        avvik = ak.avvik({"snapshot": snapshot, "dekning": updated,
                          "noder": noder})
        if avvik:
            print(f"\nSOURCE AXIS: {len(avvik)} deviation(s) the measurement "
                  f"cannot decide — a person must take a position, and the "
                  f"invariant will trip until one is taken:")
            for feil in avvik:
                print(f"    {feil}")
        if report["nye_domener"]:
            print(f"\nNOT DECLARED ({len(report['nye_domener'])}) — carries "
                  f"messages, is not listed in {DEKNING_STI}. The atlas does "
                  f"not know they exist, and the invariant must TRIP until "
                  f"someone has taken a position on them:")
            for domain in report["nye_domener"]:
                print(f"    {domain}  {sum(domains[domain].values())}")
        for domain, subjects in sorted(report["nye_emner"].items()):
            print(f"\nNEW SUBJECTS in {domain} — no position taken: "
                  f"{subjects}")
        if report["borte"]:
            print(f"\nDECLARED, BUT OUT OF THE MEASUREMENT: "
                  f"{report['borte']} — "
                  f"the declaration promises a world that is no longer there. "
                  f"Bus subjects inside the retention window disappear on "
                  f"their own; remove them from the file or explain why.")
        if args.torr:
            print("\n(--torr: nothing written)")
        return 0

    read = les_fra_ref(repo, args.ref)
    print(f"{read['kilde']} @ {read['commit'][:8]}", file=sys.stderr)
    rows = hull(read["dekning"], read["snapshot"],
                statuser=None if args.alle else ("ikke_dekket",),
                top=args.topp)
    print(format_table(rows))
    return 0


def _main_with_errors(argv: list[str] | None = None) -> int:
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
    sys.exit(_main_with_errors())
