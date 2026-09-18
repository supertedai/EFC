#!/usr/bin/env python3
"""blast_radius.py — mechanically computed blast radius for a diff (phase 1).

BR = F × E × P × I. All the factors are 1–4 and NEVER lower than 1, so that
"unknown" cannot mask risk as "liten".

  F  touched files from the git diff 1 = one file → 4 = >20 files or an unknown diff
  E  the ownership register         1 = one verified owner → 4 = unknown owner
                                    or ≥4 owners
  P  public surface                 1 = internal → 4 = trust boundary
                                    (api/**, auth/**, integrations/**, shared/**)
  I  irreversibility                1 = internal and git-reversible → 4 = gate,
                                    scheduler, credential or destructive

The ownership (governance/ownership-register.json, "0 files without an owner") makes F
and E computable today; P and I come from the diff classification below.

Thresholds — class -> requirement:

  1–3    liten        can land automatically
  4–7    material     independent reviewer + rollback plan + readback
  8–15   høy          2 independent controls (or reviewer + verifier), ADR
  16–31  kritisk      owner sign-off + canary + HUMAN GATE
  32+    blokkerende  freeze/quarantine; only the human can decide

A CRITICAL TRIGGER overrides the numerical score. The triggers are:
privilegium (credential/secret), produksjon (figshare/** and
docs/public/** — what has been published out of the house), destruktiv
(migration/deletion), gate-endring (.github/**, governance/**, *gate*.py,
the scheduler scripts) and ukjent-grenseflate (file without an owner in the register). The
first four make the change BLOCKING; ukjent-grenseflate makes it kritisk.

Why produksjon is not "everything under public/": public/** and docs/** are
versioned content that can be corrected in the next commit. figshare/** is a
deposit with a DOI, and docs/public/** is what the reader actually sees. Those are the
two surfaces that cannot be withdrawn with a commit — that is why they are the
ones that fire the trigger.

Usage:
  python3 scripts/maintenance/blast_radius.py --diff origin/main
  python3 scripts/maintenance/blast_radius.py --diff "$BASE" --json
  python3 scripts/maintenance/blast_radius.py --diff origin/main --gate

Change id (the correlation key against the risk register): --change-id if given,
otherwise a kanban/PR id found in the branch name (t_<hex>, pr<number>), otherwise
"<base-sha>..<head-sha>". The gate looks up the risk entries with the same
source_change_id and requires a HUMAN-approved decision per gate entry:
one approved entry does NOT cover another entry that still stands "venter".

Exit: 0 = report (without --gate), 1 = --gate rejected the change, 2 = tool error
(unknown ref, missing/invalid ownership register, invalid risk register). An EMPTY
diff is F=1 and "liten"; a FAILING git call is exit 2 — never "no
changes".
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
EIERREGISTER = "governance/ownership-register.json"
RISIKOREGISTER = "governance/risiko/risiko-register.jsonl"


class VerktoyFeil(Exception):
    """Errors that make the measurement invalid — never "no risk"."""


# --- rule set ------------------------------------------------------------
# The highest hit wins. All paths are relative to the repo root.

P_REGLER: list[tuple[int, tuple[str, ...]]] = [
    (4, ("api/**", "auth/**", "integrations/**", "shared/**")),
    (3, ("public/**", "docs/**", "jsonld/**", "meta-graph/**", "figshare/**",
         "llms.txt", "ecosystem.jsonld", "codemeta.json", "CITATION.cff",
         "README.md")),
    (2, ("meta/**", "schema/**", "schemas/**", "evidence/**", "theory/**",
         "methodology/**", "data/**")),
]

I_REGLER: list[tuple[int, tuple[str, ...]]] = [
    (4, (
        # gate and scheduler — the change moves a decision boundary
        ".github/**", "governance/**", "*gate*.py",
        "scripts/maintenance/vedlikeholdsrunde.py",
        "scripts/maintenance/efc_inntak.py",
        "scripts/maintenance/efc_release_publisher.py",
        "scripts/maintenance/efc_seal_manifest.py",
        # credential/secret. These names are FORBIDDEN by
        # validate_repo.py — a hit here means that a forbidden name all the same
        # has been inserted, and then the trigger shall fire, not stay silent.
        ".env*", "*.env", "*secret*", "*credential*", "*.pem", "*.key",
        # destructive/publication — cannot be withdrawn with a commit
        "*migrat*", "*delete*", "figshare/**",
    )),
    (3, ("schema/**", "schemas/**", "*.schema.json", "logs/**",
         "docs/validation-ledger/**", ".seal-manifest.json")),
    (2, ("public/**", "docs/**", "evidence/**", "data/**",
         # auth/ is PROVENANCE (ORCID/authorship) in this repo, not a
         # credential store — therefore I=2 and not I=4. The opposite would have
         # been to read the directory name instead of the content.
         "auth/**")),
]

TRIGGER_REGLER: list[tuple[str, tuple[str, ...]]] = [
    ("privilegium", (".env*", "*.env", "*secret*", "*credential*", "*.pem",
                     "*.key")),
    ("produksjon", ("figshare/**", "docs/public/**")),
    ("destruktiv", ("*migrat*", "*delete*")),
    ("gate-endring", (".github/**", "governance/**", "*gate*.py",
                      "scripts/maintenance/vedlikeholdsrunde.py",
                      "scripts/maintenance/efc_inntak.py",
                      "scripts/maintenance/efc_release_publisher.py")),
]

# Triggers that make the change blocking (everything else is "at least kritisk").
BLOKKERENDE_TRIGGERE = ("privilegium", "produksjon", "destruktiv", "gate-endring")

KLASSE_KRAV = {
    "liten": "kan lande automatisk",
    "material": "uavhengig reviewer + rollbackplan + readback",
    "høy": "2 uavhengige kontroller (eller reviewer + verifier), ADR",
    "kritisk": "eiersign-off + canary + MENNESKEGATE",
    "blokkerende": "freeze/quarantine — bare mennesket kan beslutte",
}

REGISTERKLASSE = {
    "liten": "grønn", "material": "gul", "høy": "gul",
    "kritisk": "rød", "blokkerende": "rød",
}

CHANGE_ID = re.compile(r"(t_[0-9a-f]{8,}|pr[0-9]+)")


# --- faktorene (rene funksjoner) -----------------------------------------

def _treff(fil: str, moenster: str) -> bool:
    return fnmatch.fnmatch(fil, moenster)


def _maks(regler: list[tuple[int, tuple[str, ...]]], filer: list[str]) -> int:
    verdier = [v for v, moenstre in regler
               if any(_treff(f, m) for f in filer for m in moenstre)]
    return max(verdier) if verdier else 1


def f_faktor(antall_filer: int) -> int:
    """1 file = 1, 2–3 = 2, 4–20 = 3, >20 = 4. Empty diff = 1 (no touch)."""
    if antall_filer <= 1:
        return 1
    if antall_filer <= 3:
        return 2
    if antall_filer <= 20:
        return 3
    return 4


def e_faktor(eiere: list[str], ukjent_eier: bool) -> int:
    """Unknown owner = 4. Otherwise the number of distinct owners (>=4 = 4)."""
    if ukjent_eier:
        return 4
    antall = len({e for e in eiere if e})
    if antall <= 1:
        return 1
    if antall == 2:
        return 2
    if antall == 3:
        return 3
    return 4


def p_faktor(filer: list[str]) -> int:
    return _maks(P_REGLER, filer)


def i_faktor(filer: list[str]) -> int:
    return _maks(I_REGLER, filer)


def triggere(filer: list[str], ukjent_eier: bool) -> list[str]:
    ut = [navn for navn, moenstre in TRIGGER_REGLER
          if any(_treff(f, m) for f in filer for m in moenstre)]
    if ukjent_eier:
        ut.append("ukjent-grenseflate")
    return sorted(set(ut))


def score(f: int, e: int, p: int, i: int) -> int:
    return f * e * p * i


def klasse(br: int, triggerliste: list[str]) -> str:
    """The triggers override the score — never the other way."""
    if br >= 32 or any(t in BLOKKERENDE_TRIGGERE for t in triggerliste):
        return "blokkerende"
    if br >= 16 or triggerliste:
        return "kritisk"
    if br >= 8:
        return "høy"
    if br >= 4:
        return "material"
    return "liten"


def registerklasse(klasse_: str) -> str:
    """The blast class level mapped to the register's grønn|gul|rød."""
    return REGISTERKLASSE[klasse_]


# --- git -----------------------------------------------------------------

def _git(rot: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(rot), capture_output=True,
                          timeout=60)


def endrede_filer(base: str, rot: Path) -> list[str]:
    """Files changed against `base` — plus untracked files, so that a run
    before commit measures the same as CI measures after.

    NO diff filter: a DELETED file is the most irreversible change of
    all, and a `--diff-filter=d` would make it invisible to the scorer.
    """
    r = _git(rot, "diff", "--name-only", "-z", base)
    if r.returncode != 0:
        raise VerktoyFeil(
            f"git diff vs «{base}» failed: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    filer = [s for s in r.stdout.decode("utf-8", errors="replace").split("\0") if s]
    u = _git(rot, "ls-files", "--others", "--exclude-standard", "-z")
    if u.returncode == 0:
        filer += [s for s in u.stdout.decode("utf-8", errors="replace").split("\0") if s]
    return sorted(set(filer))


def _rev(rot: Path, ref: str) -> str:
    r = _git(rot, "rev-parse", ref)
    if r.returncode != 0:
        raise VerktoyFeil(f"unknown ref «{ref}»: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    return r.stdout.decode().strip()


def _grennavn(rot: Path) -> str:
    r = _git(rot, "rev-parse", "--abbrev-ref", "HEAD")
    return r.stdout.decode().strip() if r.returncode == 0 else ""


def finn_change_id(rot: Path, base: str, eksplisitt: str | None) -> str:
    if eksplisitt:
        return eksplisitt
    m = CHANGE_ID.search(_grennavn(rot))
    if m:
        return m.group(1)
    return f"{_rev(rot, base)[:12]}..{_rev(rot, 'HEAD')[:12]}"


# --- ownership register --------------------------------------------------

def les_eierregister(sti: Path) -> dict:
    if not sti.is_file():
        raise VerktoyFeil(f"the ownership register is missing: {sti}")
    try:
        return json.loads(sti.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        raise VerktoyFeil(f"the ownership register is invalid JSON: {ex}") from ex


def eiere_og_komponenter(filer: list[str], register: dict) -> tuple[list[str], list[str], bool]:
    """Returns (owners, component ids, unknown owner)."""
    komponenter = register.get("components") or []
    eiere: list[str] = []
    ider: list[str] = []
    ukjent = False
    for fil in filer:
        treff = [c for c in komponenter
                 if any(_treff(fil, g) for g in (c.get("coverage_glob") or []))]
        if not treff:
            ukjent = True
            ider.append(f"UKJENT:{fil}")
            continue
        for c in treff:
            ider.append(c.get("id", ""))
            eiere.append(c.get("owner", ""))
    return eiere, sorted(set(ider)), ukjent


# --- the risk register (gate lookup) -------------------------------------

def les_poster(sti: Path) -> list[dict]:
    if not sti.is_file():
        raise VerktoyFeil(f"the risk register is missing: {sti}")
    poster = []
    for nr, linje in enumerate(sti.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            poster.append(json.loads(linje))
        except json.JSONDecodeError as ex:
            raise VerktoyFeil(f"invalid JSON in {sti} line {nr}: {ex}") from ex
    return poster


def slaa_opp_gate(poster: list[dict], change_id: str) -> dict:
    """The gate for a change id is satisfied when EVERY gate entry (gate_required=true)
    for the change id is approved by the human ("menneske") — none stands "venter"
    and none is "avslått". The decision is per entry: one approved entry does NOT
    cover another entry that still waits. The gate only lets through once all are
    decided and at least one is approved.
    """
    mine = [p for p in poster if p.get("source_change_id") == change_id]
    gate_poster = [p for p in mine if p.get("gate_required") is True]
    venter = [p for p in gate_poster if p.get("gate_decision") == "venter"]
    avslaatt = [p for p in gate_poster if p.get("gate_decision") == "avslått"]
    godkjent = [p for p in gate_poster
                if p.get("gate_decision") == "godkjent"
                and p.get("gate_besluttet_av") == "menneske"]
    oppfylt = bool(godkjent) and not venter and not avslaatt
    return {
        "change_id": change_id,
        "poster": [p.get("risk_id") for p in mine],
        "venter": [p.get("risk_id") for p in venter],
        "avslaatt": [p.get("risk_id") for p in avslaatt],
        "oppfylt": oppfylt,
        "besluttet_av": godkjent[0].get("gate_besluttet_av") if godkjent else None,
        "risk_id": godkjent[0].get("risk_id") if godkjent else None,
    }


# --- main flow -----------------------------------------------------------

def regn_ut(base: str, rot: Path, eierregister: Path, risikoregister: Path,
            change_id: str | None) -> dict:
    filer = endrede_filer(base, rot)
    reg = les_eierregister(eierregister)
    eiere, komponenter, ukjent = eiere_og_komponenter(filer, reg)
    f = f_faktor(len(filer))
    e = e_faktor(eiere, ukjent)
    p = p_faktor(filer)
    i = i_faktor(filer)
    br = score(f, e, p, i)
    trig = triggere(filer, ukjent)
    kls = klasse(br, trig)
    cid = finn_change_id(rot, base, change_id)
    gate = slaa_opp_gate(les_poster(risikoregister), cid)
    funn = []
    if kls != "liten":
        funn.append({
            "type": "blast_radius",
            "klasse": kls,
            "score": br,
            "faktorer": {"F": f, "E": e, "P": p, "I": i},
            "triggere": trig,
            "krav": KLASSE_KRAV[kls],
            "change_id": cid,
            "gate_oppfylt": gate["oppfylt"],
            "registerklasse": registerklasse(kls),
        })
    return {
        "diff_base": base,
        "head": _rev(rot, "HEAD"),
        "change_id": cid,
        "antall_filer": len(filer),
        "filer": filer,
        "faktorer": {"F": f, "E": e, "P": p, "I": i},
        "score": br,
        "klasse": kls,
        "krav": KLASSE_KRAV[kls],
        "registerklasse": registerklasse(kls),
        "triggere": trig,
        "eiere": sorted({x for x in eiere if x}),
        "komponenter": komponenter,
        "ukjent_eier": ukjent,
        "gate": gate,
        "funn": funn,
    }


def hoved() -> int:
    p = argparse.ArgumentParser(description="Blast-radius = F × E × P × I")
    p.add_argument("--diff", required=True, metavar="BASE",
                   help="git ref to measure against (e.g. origin/main or a SHA)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--gate", action="store_true",
                   help="reject (exit 1) kritisk/blokkerende without a human-approved decision")
    p.add_argument("--change-id", default=None)
    p.add_argument("--rot", default=None, help="repo root (default: the script's parent³)")
    p.add_argument("--eierregister", default=None)
    p.add_argument("--risikoregister", default=None)
    a = p.parse_args()
    rot = Path(a.rot).resolve() if a.rot else ROT
    eierregister = Path(a.eierregister) if a.eierregister else rot / EIERREGISTER
    risikoregister = Path(a.risikoregister) if a.risikoregister else rot / RISIKOREGISTER
    try:
        ut = regn_ut(a.diff, rot, eierregister, risikoregister, a.change_id)
    except VerktoyFeil as ex:
        if a.json:
            # JSON on stdout also on a tool error: the maintenance round reads
            # the "feil" list and makes a finding of it — a measurement that could
            # not be made is not "no risk".
            print(json.dumps({"feil": [{"type": "tool_error", "msg": str(ex)}]},
                             ensure_ascii=False, indent=1))
        else:
            print(f"blast-radius: tool error — {ex}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(ut, ensure_ascii=False, indent=1))
    else:
        fa = ut["faktorer"]
        print(f"blast-radius: {ut['score']} (F={fa['F']} × E={fa['E']} × "
              f"P={fa['P']} × I={fa['I']})")
        print(f"  class: {ut['klasse']} — {ut['krav']}")
        print(f"  triggers: {', '.join(ut['triggere']) or 'none'}")
        print(f"  files: {ut['antall_filer']} | owners: {', '.join(ut['eiere']) or '—'}")
        if ut["ukjent_eier"]:
            print("  UNKNOWN OWNER: change touches files no component owns in the register")
        print(f"  change-id: {ut['change_id']}")
        print(f"  gate: {'satisfied' if ut['gate']['oppfylt'] else 'not satisfied'}"
              f" (risk entry: {ut['gate']['risk_id'] or 'none'})")
    if a.gate and ut["klasse"] in ("kritisk", "blokkerende") and not ut["gate"]["oppfylt"]:
        if not a.json:
            print(f"GATE: {ut['klasse']} change without a human-approved decision "
                  f"for change-id {ut['change_id']} — rejected", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
