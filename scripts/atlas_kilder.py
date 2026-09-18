#!/usr/bin/env python3
"""atlas_kilder -- the third axis of the coverage file: the SOURCE.

Card t_f...: "ten domains, one unowned source". The atlas measures ownership per
BUS DOMAIN. A source routed into many domains therefore cannot be seen as
unowned: every domain has its node, every node stands as `covered`, and the
source they all READ stands without an owner. Measured 2026-09-18:

    GDELT GKG     3 bus subjects   20 domains   30 352 messages   17 readers   0 owners
    World Bank    1 bus subject    18 domains      302 messages    0 readers   0 owners
    MAST/CAOM     1 bus subject     6 domains      174 messages    0 readers   0 owners

The domain axis says 39 of 39 covered. The source axis says the largest source
on the bus -- 30 352 messages -- is owned by no node at all.

## Why `navn` and not just the subject segment

`docs/nats-koblingskart.md`: "Subjects have the form
`<root>.<domain>.<layer>.<source>`" -- the last segment IS the source, and the
list can therefore be DERIVED from the measurement instead of written into a
dict. But three segments may belong to ONE project: `gdelt-gkg`,
`gdelt-mentions` and `gdelt-export` are three readings of one corpus, not three
sources. `navn` is the declared collection, and it is checkable: all three must
name the same thing, and it is the name the nodes themselves write in
`lagdeling.kilde.kilde`.

## The threshold, and why it is argued and not chosen

A source carried by ONE domain is owned by that domain's node -- the reading IS
the node, and there is no shadow. Carried by TWO or more, no single node's
ownership can cover it: then the absence of an owner must stand NAMED. That is
the only threshold here, and it follows from what a domain is.

    python3 scripts/atlas_kilder.py            # the whole source inventory
    python3 scripts/atlas_kilder.py --delt     # only those carried by several
    python3 scripts/atlas_kilder.py --sjekk    # declaration against measurement

Language: English only, per the repo-wide language gate
(`scripts/maintenance/efc_spraakvakt.py`), which fails on any Norwegian this
change adds under `scripts/`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
STANDARD_REF = "origin/main"
DEKNING_STI = "schema/atlas_dekning.json"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"
NODER_STI = "schema/regime_nodes.jsonld"

#: The statuses a source can have. They answer the domain axis's statuses, but
#: ask something else: not "does the atlas describe this?" but "IS the atlas
#: this?".
#:   eid        a node IS the source -- declared in `eiere` and verified
#:   lest       nodes name it as their source; no node is it
#:   unavngitt  no node names it at all
#:
#: The wording is deliberately not "covered/not covered": a source carried by
#: one domain can be covered BY THAT DOMAIN'S NODE (verden.klima says itself
#: that noaa-tides is covered) while the source still is not named as a source
#: anywhere. The two axes must be able to hold separate truths without
#: contradicting each other.
GYLDIGE_STATUS = {"eid", "lest", "unavngitt"}


class KildeFeil(RuntimeError):
    """The measurement could not be made. Never a guessed number."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise KildeFeil(f"git {' '.join(args)} failed in {repo}: "
                        f"{p.stderr.strip()}")
    return p.stdout


def les_fra_ref(repo: str | Path = ROT, ref: str = STANDARD_REF, *,
                hent: bool = False) -> dict:
    """Read the measurement, the declaration and the bank from `ref` -- not from
    the working tree.

    The same rule as `atlas_volum`: a working copy that answers is not a living
    atlas. `ref="."` is the exception, and it exists on purpose: a reviewer with
    an unsubmitted change must be able to check THAT file, or the check against
    `origin/main` becomes an answer to a different question than the one asked.
    """
    repo = Path(repo)
    if ref == ".":
        ut: dict = {"ref": ".", "commit": "(the working tree)"}
        for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI),
                            ("noder", NODER_STI)):
            ut[nokkel] = json.loads((repo / sti).read_text(encoding="utf-8"))
        return ut
    if hent:
        _git(repo, "fetch", "-q", "origin")
    ut = {"ref": ref, "commit": _git(repo, "rev-parse", ref).strip()}
    for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI),
                        ("noder", NODER_STI)):
        try:
            ut[nokkel] = json.loads(_git(repo, "show", f"{ref}:{sti}"))
        except json.JSONDecodeError as e:
            raise KildeFeil(f"{ref}:{sti} is not valid JSON: {e}") from e
    return ut


def kildeinventar(snapshot: dict) -> dict[str, dict]:
    """The source segments the bus carries -- DERIVED from the subject names,
    measured in messages.

    One segment per subject is the only source we have for the source name that
    we did not write ourselves: the subject carries it. The volume is the sum of
    the MEASURED per-subject numbers, not an estimate.
    """
    ut: dict[str, dict] = {}
    for domene, rad in (snapshot.get("domener") or {}).items():
        emner = rad.get("emner")
        if not isinstance(emner, dict):
            raise KildeFeil(
                f"the measurement does not carry a count per subject ({domene}: "
                f"{type(emner).__name__}). Run `atlas_volum.py --maal` against "
                f"the bus, or read a ref that already carries the volume.")
        for emne, antall in emner.items():
            ledd = str(emne).split(".")[-1]
            k = ut.setdefault(ledd, {"meldinger": 0, "domener": {}})
            k["meldinger"] += antall
            k["domener"][domene] = k["domener"].get(domene, 0) + antall
    for k in ut.values():
        k["domener"] = dict(sorted(k["domener"].items(),
                                   key=lambda p: (-p[1], p[0])))
    return dict(sorted(ut.items()))


def navngitt(noder: list[dict], navn: str) -> list[str]:
    """The nodes that write `navn` as their source -- in their OWN field.

    No list in the declaration can survive this field changing, because the
    test derives it here and compares both directions.
    """
    return sorted(
        n["id"] for n in noder
        if ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde") == navn)


def navn_for(ledd: str, dekl: dict) -> str | None:
    """The project name the declared segment belongs to."""
    return (dekl.get("kilder", {}).get(ledd) or {}).get("navn")


def rapport(data: dict) -> list[dict]:
    """One row per source segment: what the bus carries, and who says anything
    about it."""
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    dekl = data["dekning"].get("kilder") or {}
    ut = []
    for ledd, maalt in inv.items():
        rad = dekl.get(ledd) or {}
        navn = rad.get("navn")
        lesere = navngitt(noder, navn) if navn else []
        ut.append({
            "ledd": ledd,
            "navn": navn,
            "status": rad.get("status"),
            "meldinger": maalt["meldinger"],
            "domener": list(maalt["domener"]),
            "lesere": lesere,
            "eiere": sorted(rad.get("eiere") or []),
        })
    ut.sort(key=lambda r: (-len(r["domener"]), -r["meldinger"], r["ledd"]))
    return ut


def prosjekter(rader: list[dict]) -> list[dict]:
    """Joins the segments that name the same project.

    It is HERE the card's question is answered: three bus subjects with one name
    are one corpus, and they are measured as one -- not as three sources.
    """
    per: dict[str, dict] = {}
    for r in rader:
        n = r["navn"] or f"(uten navn: {r['ledd']})"
        p = per.setdefault(n, {"navn": n, "ledd": [], "meldinger": 0,
                               "domener": set(), "lesere": set(),
                               "eiere": set(), "status": set()})
        p["ledd"].append(r["ledd"])
        p["meldinger"] += r["meldinger"]
        p["domener"] |= set(r["domener"])
        p["lesere"] |= set(r["lesere"])
        p["eiere"] |= set(r["eiere"])
        p["status"].add(r["status"])
    ut = []
    for p in per.values():
        ut.append({**p, "domener": sorted(p["domener"]),
                   "lesere": sorted(p["lesere"]), "eiere": sorted(p["eiere"]),
                   "status": sorted(p["status"])})
    ut.sort(key=lambda p: (-len(p["domener"]), -p["meldinger"], p["navn"]))
    return ut


def avvik(data: dict) -> list[str]:
    """The declaration against the measurement, BOTH directions. Empty list =
    no deviation.

    The checks, in the order they were found:
      1. a source segment the bus carries but the declaration is silent about
      2. a declared segment that no longer carries anything
      3. a `navn` that is not what the nodes write (or the other way round)
      4. an `eid` source without an owner, or an owner that does not name it
      5. an owner that does not exist in the bank
      6. readers that are not the nodes actually naming the source
      7. a node naming a source its own bus domain does not carry
    """
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    dekl = data["dekning"].get("kilder")
    if dekl is None:
        return ["schema/atlas_dekning.json has no `kilder` section -- "
                "the source axis is not declared at all"]
    feil: list[str] = []
    bank = {n["id"]: n for n in noder}

    for ledd in sorted(set(inv) - set(dekl)):
        feil.append(
            f"the source segment \"{ledd}\" carries {inv[ledd]['meldinger']} "
            f"messages over {len(inv[ledd]['domener'])} domain(s) without "
            f"standing in atlas_dekning.json -- the atlas does not know that "
            f"the source exists")
    for ledd in sorted(set(dekl) - set(inv)):
        feil.append(f"declared for the source segment \"{ledd}\", which no "
                    f"longer carries messages")

    # the names: every declared name must be what the nodes write, and every
    # name the nodes write must stand declared.
    deklarerte = {r.get("navn") for r in dekl.values() if r.get("navn")}
    skrevne: set[str] = set()
    for n in noder:
        v = ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")
        if v:
            skrevne.add(str(v))
    for navn in sorted(deklarerte - skrevne):
        feil.append(f"\"{navn}\" is declared as a source, but no node writes "
                    f"that name in lagdeling.kilde.kilde")
    for navn in sorted(skrevne - deklarerte):
        feil.append(f"nodes write the source \"{navn}\", which does not stand "
                    f"in atlas_dekning.json")

    # the breadth: the source a node reads must be carried by the node's OWN bus
    # domain. Without this a generator could give a node a source it does not
    # have -- measured: 3 nodes got GDELT because the lookup fell back on it.
    for n in noder:
        navn = ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")
        dom = n.get("buss_domene")
        if not navn or not dom:
            continue
        baerer = any(dom in inv[ledd]["domener"]
                     for ledd, r in dekl.items() if r.get("navn") == navn)
        if not baerer:
            feil.append(
                f"{n['id']} says the source is \"{navn}\", but the domain "
                f"{dom} carries none of the segments of that source")

    for ledd, rad in sorted(dekl.items()):
        eiere = sorted(rad.get("eiere") or [])
        status = rad.get("status")
        if status not in GYLDIGE_STATUS:
            feil.append(f"{ledd}: invalid status {status!r}")
        if status == "eid" and not eiere:
            feil.append(f"{ledd} is `eid` without an owner")
        if status != "eid" and eiere:
            feil.append(f"{ledd} names the owners {eiere}, but the status is "
                        f"{status!r}")
        for e in eiere:
            if e not in bank:
                feil.append(f"{ledd}: the owner \"{e}\" does not exist in the bank")
                continue
            skriver = ((bank[e].get("lagdeling") or {}).get("kilde")
                       or {}).get("kilde")
            if skriver != rad.get("navn"):
                feil.append(f"{ledd}: the owner \"{e}\" writes the source "
                            f"{skriver!r}, not {rad.get('navn')!r}")
        # the list of readers is derived -- it cannot be written by hand
        if "lesere" in rad:
            maalt = navngitt(noder, rad.get("navn")) if rad.get("navn") else []
            if sorted(rad["lesere"]) != maalt:
                feil.append(f"{ledd}: the declaration says the readers "
                            f"{sorted(rad['lesere'])}, the bank says {maalt}")
        # a shared source without an owner must carry its reason
        if ledd in inv and len(inv[ledd]["domener"]) > 1 and status != "eid":
            if not str(rad.get("begrunnelse", "")).strip():
                feil.append(
                    f"{ledd} is carried by {len(inv[ledd]['domener'])} domains "
                    f"without an owner and without a reason -- an absence of an "
                    f"owner must stand named, not be silent")
    return feil


def _skriv_seksjon(data: dict, gammel: dict | None = None) -> dict:
    """Build the `kilder` section from the measurement, with the declared names.

    The names and the reasons are the only fields that cannot be derived --
    everything else comes from the bus and from the bank, and the test derives
    it again. This function is therefore a BUILDER, not a decision: it does not
    touch a name or a reason that already stands there, and it reads them from
    the FILE it writes (otherwise a new run would have deleted them, since the
    measurement comes from a ref without the section).
    """
    gammel = (data["dekning"].get("kilder") or {}) if gammel is None else gammel
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    ut: dict[str, dict] = {}
    for ledd, maalt in inv.items():
        før = gammel.get(ledd) or {}
        navn = før.get("navn")
        lesere = navngitt(noder, navn) if navn else []
        eiere = sorted(før.get("eiere") or [])
        status = "eid" if eiere else ("lest" if lesere else "unavngitt")
        rad: dict = {"navn": navn, "status": status,
                     "meldinger": maalt["meldinger"],
                     "domener": list(maalt["domener"]), "lesere": lesere,
                     "eiere": eiere}
        if str(før.get("begrunnelse", "")).strip():
            rad["begrunnelse"] = før["begrunnelse"]
        ut[ledd] = rad
    return dict(sorted(ut.items()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("--hent", action="store_true")
    ap.add_argument("--delt", action="store_true",
                    help="only sources carried by more than one domain")
    ap.add_argument("--sjekk", action="store_true",
                    help="the declaration against the measurement; exit 1 on "
                         "deviations")
    ap.add_argument("--skriv", action="store_true",
                    help="build the `kilder` section from the measurement and "
                         "write the file (names and reasons already there are "
                         "left untouched)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.skriv:
        data = les_fra_ref(ROT, a.ref, hent=a.hent)
        sti = ROT / DEKNING_STI
        naa = json.loads(sti.read_text(encoding="utf-8"))
        naa["kilder"] = _skriv_seksjon(data, naa.get("kilder") or {})
        sti.write_text(json.dumps(naa, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"wrote {len(naa['kilder'])} source segments to {DEKNING_STI}")
        return 0

    data = les_fra_ref(ROT, a.ref, hent=a.hent)

    if a.sjekk:
        feil = avvik(data)
        for f in feil:
            print(f"AVVIK: {f}")
        print(f"{len(feil)} deviation(s)" if feil
              else "the sources agree with the measurement")
        return 1 if feil else 0

    rader = rapport(data)
    if a.delt:
        rader = [r for r in rader if len(r["domener"]) > 1]
    if a.json:
        print(json.dumps(prosjekter(rader), ensure_ascii=False, indent=1))
        return 0

    print(f"ref {data['ref']} @ {data['commit'][:8]}")
    print(f"{len(rader)} source segments, "
          f"{sum(r['meldinger'] for r in rader)} messages measured\n")
    for p in prosjekter(rader):
        eier = ", ".join(p["eiere"]) or ("NONE" if p["lesere"] else "--")
        print(f"{p['meldinger']:8d} msg  {len(p['domener']):3d} domains  "
              f"{len(p['lesere']):3d} readers  owner: {eier}")
        print(f"{'':>10}  {p['navn']}  [{', '.join(p['ledd'])}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
