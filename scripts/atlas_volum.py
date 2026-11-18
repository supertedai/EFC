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

## The third state: UKJENT — and why 0 is never it

A declared domain that does not stand in the measurement has NO measured
volume. It must not be written as `0`: zero is a claim that the source
ANSWERED with nothing, and the bus protocol cannot produce that number.
`verden_domener` builds the domains from the subjects that carry messages,
and a stream that carries nothing at all is NAMED in `tomme_stroemmer`
("created, waiting for a producer — not destroyed"). Measured 2026-09-22
(card t_7f8529cd, against the live bus): 38 domains, 117 subjects, the
smallest subject count 1, no domain summing to 0 — while the declared
domains `kosmos.exoplanet` and `kosmos.hoper` stood OUTSIDE the measurement
and the old write line turned both into `"meldinger": 0`.

The volume therefore has three states, and the file says which:

    an int >= 1   measured: the sum of the domain's measured subjects
    null          UKJENT: the domain is not in the measurement at all
    (absent)      UKJENT in a ref older than the volume field itself

`hull()` does not carry the previous number forward either. A stream that
has stopped answering would then read as unchanged — the same lie, one step
later — so the declaration's number is used only when no measurement was
handed in at all. The table writes UKJENT where the number would stand, in
the same column the subject counts already mark when they were not measured.

The rule is the house's, and it is older than this module: a source that
stops answering is shown as unknown, not as zero (ADR-043, the step-3 gate;
ADR-021 decision 1: "UKJENT is not NULL"). The same failure has been paid
for once already inside ADR-043: a dashboard drew "no deviations" on a tree
where nothing had been measured, because the value was the empty list rather
than `None` — and the test that stood guard asserted the empty list, and so
CEMENTED the defect it was written to catch. The test
`test_et_domene_ute_av_maalingen_skrives_som_ukjent` in
`tests/test_atlas_volum.py` asserted `0` in exactly that way, and is
rewritten here.

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

    `meldinger` is the MEASURED volume, or `None` when it was not measured:
    a domain that a supplied measurement does not carry is UKJENT, and the
    declaration's own number is NOT used for it (a stream that has stopped
    answering would otherwise read as unchanged). Without a measurement there
    is only the declaration's number — and a missing field is still `None`,
    never 0.
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
        meldinger = (row.get("meldinger") if snapshot is None
                     else measured.get(name))
        rows.append({
            "domene": name,
            "status": row.get("status"),
            "meldinger": meldinger,
            "noder": list(row.get("noder") or []),
            "emner": subjects,
        })
    # Measured volumes first, largest first; the ones that were never
    # measured last, by name. An unknown volume cannot take part in a ranking
    # by size, and sorting it first would claim it is the largest gap there is.
    rows.sort(key=lambda r: (r["meldinger"] is None,
                             -(r["meldinger"] or 0), r["domene"]))
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


def skriv_snapshot(path: str | Path, domains: dict, *,
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
        "domener": {name: {"emner": dict(sorted(subjects.items()))}
                    for name, subjects in sorted(domains.items())},
    }
    _write_json(Path(path), data)
    return data


def oppdater_dekning(coverage: dict, domains: dict) -> tuple[dict, dict]:
    """Set `meldinger` per domain = the sum of the measured subject counts.

    Everything else in the declaration is the HUMAN'S: `status` and
    `begrunnelse` are a position taken, not a derivation. This function does
    not touch them — it writes only the number, and reports what it could
    not write: new domains and new subjects must trip the invariant until
    someone has taken a position on them.

    A declared domain that the measurement does not carry gets `None` —
    UKJENT — never 0 and never the number from the previous measurement. 0
    would be a claim that the source answered with nothing; the bus builds
    its domains from the subjects that CARRY messages, so that number is not
    producible here. The domain is named in `report["borte"]`, and the
    invariant trips until a human has taken a position on it.

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
            "meldinger": measured.get(name),
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
    """The table the human reads — largest first, with the subjects below.

    A volume that was not measured is written UKJENT, not as a number: the
    reader who sees a size must be able to trust that somebody measured it.
    """
    if not rows:
        return "  (no gaps in this slice)"
    width = max(len(r["domene"]) for r in rows)
    lines = []
    for r in rows:
        meldinger = "UKJENT" if r["meldinger"] is None else f"{r['meldinger']}"
        lines.append(f"{meldinger:>10}  {r['status']:<11}  "
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
        lest_av = os.environ.get(
            "ATLAS_LEST_AV",
            f"{os.environ.get('HERMES_PROFILE', 'unknown')} "
            f"(scripts/atlas_volum.py)")
        if not args.torr:
            skriv_snapshot(repo / SNAPSHOT_STI, domains, lest_av=lest_av)
        updated, report = oppdater_dekning(coverage, domains)
        if not args.torr:
            _write_json(declaration_path, updated)
        for domain, subjects in sorted(
                domains.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"{sum(subjects.values()):>10}  {domain}")
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
                  f"their own; remove them from the file or explain why. "
                  f"Their `meldinger` is written as UKJENT (null) — 0 would "
                  f"be a measurement claim the bus never made, and the old "
                  f"number would hide that the source has stopped answering.")
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
