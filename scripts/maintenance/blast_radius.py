#!/usr/bin/env python3
"""blast_radius.py — maskinelt beregnet blast-radius for en diff (fase 1).

BR = F × E × P × I. Alle faktorene er 1–4 og ALDRI lavere enn 1, slik at
«ukjent» ikke kan maskere risiko som «liten».

  F  berørte filer fra git-diffen   1 = én fil → 4 = >20 filer eller ukjent diff
  E  eierregisteret                 1 = én verifisert eier → 4 = ukjent eier
                                    eller ≥4 eiere
  P  offentlig overflate            1 = intern → 4 = tillitsgrense
                                    (api/**, auth/**, integrations/**, shared/**)
  I  irreversibilitet               1 = intern og git-reversibel → 4 = gate,
                                    scheduler, credential eller destruktivt

Eierskapet (governance/ownership-register.json, «0 filer uten eier») gjør F
og E beregnbare i dag; P og I kommer fra diff-klassifiseringen under.

Terskler — klasse → krav:

  1–3    liten        kan lande automatisk
  4–7    material     uavhengig reviewer + rollbackplan + readback
  8–15   høy          2 uavhengige kontroller (eller reviewer + verifier), ADR
  16–31  kritisk      eiersign-off + canary + MENNESKEGATE
  32+    blokkerende  freeze/quarantine; bare mennesket kan beslutte

En KRITISK TRIGGER overstyrer den numeriske scoren. Triggerne er:
privilegium (credential/hemmelighet), produksjon (figshare/** og
docs/public/** — det som er publisert ut av huset), destruktiv
(migrering/sletting), gate-endring (.github/**, governance/**, *gate*.py,
scheduler-skriptene) og ukjent grenseflate (fil uten eier i registeret). De
fire første gjør endringen BLOKKERENDE; ukjent grenseflate gjør den kritisk.

Hvorfor produksjon ikke er «alt under public/»: public/** og docs/** er
versjonert innhold som kan rettes i neste commit. figshare/** er en
deponering med DOI, og docs/public/** er det leseren faktisk ser. Det er de
to flatene som ikke kan trekkes tilbake med en commit — derfor er det de
som fyrer triggeren.

Bruk:
  python3 scripts/maintenance/blast_radius.py --diff origin/main
  python3 scripts/maintenance/blast_radius.py --diff "$BASE" --json
  python3 scripts/maintenance/blast_radius.py --diff origin/main --gate

Change-id (korrelasjonsnøkkelen mot risikoregisteret): --change-id hvis gitt,
ellers et kanban-/PR-id funnet i grennavnet (t_<hex>, pr<nummer>), ellers
«<base-sha>..<head-sha>». Gaten slår opp risikopostene med samme
source_change_id og krever en MENNESKELIG godkjent beslutning per gate-post:
én godkjent post dekker IKKE en annen post som fortsatt står «venter».

Exit: 0 = rapport (uten --gate), 1 = --gate avviste endringen, 2 = verktøyfeil
(ukjent ref, manglende/ugyldig eierregister, ugyldig risikoregister). En TOM
diff er F=1 og «liten»; et FEILENDE git-kall er exit 2 — aldri «ingen
endringer».
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
    """Feil som gjør målingen ugyldig — aldri «ingen risiko»."""


# --- regelverk -----------------------------------------------------------
# Høyeste treff vinner. Alle stier er relative til repo-roten.

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
        # gate og scheduler — endringen flytter en beslutningsgrense
        ".github/**", "governance/**", "*gate*.py",
        "scripts/maintenance/vedlikeholdsrunde.py",
        "scripts/maintenance/efc_inntak.py",
        "scripts/maintenance/efc_release_publisher.py",
        "scripts/maintenance/efc_seal_manifest.py",
        # credential/hemmelighet. Disse navnene er FORBUDT av
        # validate_repo.py — et treff her betyr at et forbudt navn likevel
        # er lagt inn, og da skal triggeren fyre, ikke tie.
        ".env*", "*.env", "*secret*", "*credential*", "*.pem", "*.key",
        # destruktivt/publisering — kan ikke trekkes tilbake med en commit
        "*migrat*", "*delete*", "figshare/**",
    )),
    (3, ("schema/**", "schemas/**", "*.schema.json", "logs/**",
         "docs/validation-ledger/**", ".seal-manifest.json")),
    (2, ("public/**", "docs/**", "evidence/**", "data/**",
         # auth/ er PROVENIENS (ORCID/forfatterskap) i dette repoet, ikke en
         # credential-store — derfor I=2 og ikke I=4. Det motsatte ville vært
         # å lese mappenavnet i stedet for innholdet.
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

# Triggere som gjør endringen blokkerende (alt annet er «minst kritisk»).
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
    """1 fil = 1, 2–3 = 2, 4–20 = 3, >20 = 4. Tom diff = 1 (ingen berøring)."""
    if antall_filer <= 1:
        return 1
    if antall_filer <= 3:
        return 2
    if antall_filer <= 20:
        return 3
    return 4


def e_faktor(eiere: list[str], ukjent_eier: bool) -> int:
    """Ukjent eier = 4. Ellers antall distinkte eiere (≥4 = 4)."""
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
    """Triggerne overstyrer scoren — aldri motsatt vei."""
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
    """Blast-klassenivået mappet til registerets grønn|gul|rød."""
    return REGISTERKLASSE[klasse_]


# --- git -----------------------------------------------------------------

def _git(rot: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=str(rot), capture_output=True,
                          timeout=60)


def endrede_filer(base: str, rot: Path) -> list[str]:
    """Filer endret mot `base` — pluss utrackede filer, slik at en kjøring
    før commit måler det samme som CI måler etter.

    INGEN diff-filter: en SLETTET fil er den mest irreversible endringen av
    alle, og en `--diff-filter=d` ville gjort den usynlig for scoreren.
    """
    r = _git(rot, "diff", "--name-only", "-z", base)
    if r.returncode != 0:
        raise VerktoyFeil(
            f"git diff mot «{base}» feilet: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
    filer = [s for s in r.stdout.decode("utf-8", errors="replace").split("\0") if s]
    u = _git(rot, "ls-files", "--others", "--exclude-standard", "-z")
    if u.returncode == 0:
        filer += [s for s in u.stdout.decode("utf-8", errors="replace").split("\0") if s]
    return sorted(set(filer))


def _rev(rot: Path, ref: str) -> str:
    r = _git(rot, "rev-parse", ref)
    if r.returncode != 0:
        raise VerktoyFeil(f"ukjent ref «{ref}»: {r.stderr.decode('utf-8', 'replace').strip()[:200]}")
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


# --- eierregister --------------------------------------------------------

def les_eierregister(sti: Path) -> dict:
    if not sti.is_file():
        raise VerktoyFeil(f"eierregisteret mangler: {sti}")
    try:
        return json.loads(sti.read_text(encoding="utf-8"))
    except json.JSONDecodeError as ex:
        raise VerktoyFeil(f"eierregisteret er ugyldig JSON: {ex}") from ex


def eiere_og_komponenter(filer: list[str], register: dict) -> tuple[list[str], list[str], bool]:
    """Returnerer (eiere, komponent-id-er, ukjent_eier)."""
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


# --- risikoregisteret (gate-oppslag) -------------------------------------

def les_poster(sti: Path) -> list[dict]:
    if not sti.is_file():
        raise VerktoyFeil(f"risikoregisteret mangler: {sti}")
    poster = []
    for nr, linje in enumerate(sti.read_text(encoding="utf-8").splitlines(), 1):
        if not linje.strip():
            continue
        try:
            poster.append(json.loads(linje))
        except json.JSONDecodeError as ex:
            raise VerktoyFeil(f"ugyldig JSON i {sti} linje {nr}: {ex}") from ex
    return poster


def slaa_opp_gate(poster: list[dict], change_id: str) -> dict:
    """Gaten for en change-id er oppfylt når HVER gate-post (gate_required=true)
    for change-id-en er godkjent av mennesket — ingen står «venter» og ingen er
    «avslått». Beslutningen er per post: én godkjent post dekker IKKE en annen
    post som fortsatt venter. Gaten slipper først gjennom når alle er avgjort
    og minst én er godkjent.
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


# --- hovedflyt -----------------------------------------------------------

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
                   help="git-ref å måle mot (f.eks. origin/main eller en SHA)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--gate", action="store_true",
                   help="avvis (exit 1) kritisk/blokkerende uten menneskelig godkjent beslutning")
    p.add_argument("--change-id", default=None)
    p.add_argument("--rot", default=None, help="repo-rot (standard: scriptets forelder³)")
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
            # JSON på stdout også ved verktøyfeil: vedlikeholdsrunden leser
            # «feil»-lista og lager et funn av den — en måling som ikke
            # kunne gjøres er ikke «ingen risiko».
            print(json.dumps({"feil": [{"type": "tool_error", "msg": str(ex)}]},
                             ensure_ascii=False, indent=1))
        else:
            print(f"blast-radius: verktøyfeil — {ex}", file=sys.stderr)
        return 2
    if a.json:
        print(json.dumps(ut, ensure_ascii=False, indent=1))
    else:
        fa = ut["faktorer"]
        print(f"blast-radius: {ut['score']} (F={fa['F']} × E={fa['E']} × "
              f"P={fa['P']} × I={fa['I']})")
        print(f"  klasse: {ut['klasse']} — {ut['krav']}")
        print(f"  triggere: {', '.join(ut['triggere']) or 'ingen'}")
        print(f"  filer: {ut['antall_filer']} | eiere: {', '.join(ut['eiere']) or '—'}")
        if ut["ukjent_eier"]:
            print("  UKJENT EIER: endringen rører filer uten komponent i eierregisteret")
        print(f"  change-id: {ut['change_id']}")
        print(f"  gate: {'oppfylt' if ut['gate']['oppfylt'] else 'ikke oppfylt'}"
              f" (risikopost: {ut['gate']['risk_id'] or 'ingen'})")
    if a.gate and ut["klasse"] in ("kritisk", "blokkerende") and not ut["gate"]["oppfylt"]:
        if not a.json:
            print(f"GATE: {ut['klasse']} endring uten menneskelig godkjent beslutning "
                  f"for change-id {ut['change_id']} — avvist", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
