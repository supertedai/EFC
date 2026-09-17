#!/usr/bin/env python3
"""efc_auto_changelog.py — registerpost + deterministisk changelog-projeksjon.

To steg, i denne rekkefølgen:

1. REGISTRER (append-only). Endringene leses fra COMMIT-DIFFEN
   (``git diff <base>..HEAD``), ikke fra arbeidskopien: en endring er det som
   er committet, og bare det. Alle filkategorier dekkes — papers,
   docs/public, ledger-data, scripts, workflows, kode, schema, config og
   rotfiler. Unntatt er loggens og projeksjonens egne utdata
   (``IGNORERTE_STIER`` i efc_change_id.py): de ER loggen og dens speil, ikke
   endringer — uten unntaket ville hver projeksjon registrert seg selv og
   aldri konvergert.

   Hver registrert endring blir en ``file_changed``-linje i
   ``logs/activity.jsonl`` med change_id, commit-sha og blob-oid. Registreringen
   er idempotent på innhold: en sti med samme blob-oid registreres ikke to
   ganger. Det er det som gjør at en landing (merge eller squash) ikke dobler
   hele endringssettet når den lokale mainen tar igjen origin/main.

   Kjente blindsoner (målt, ikke pyntet):
     * en fil som føres tilbake til NØYAKTIG samme innhold (revert + re-apply)
       gir ingen ny registerpost — innholdet er allerede logget;
     * endringer som aldri committes, finnes ikke for registreringen.

2. PROJISER. ``docs/validation-ledger/data/changelog.json`` (nøkkelen
   ``activity_projection``) og den markerte regionen i
   ``docs/public/EFC_Changelog.html`` bygges deterministisk fra loggen (se
   efc_change_id.py). Er flatene allerede i samsvar med loggen, skrives
   ingenting — kjøringen er da en ren no-op.

Bruk:
  python3 scripts/maintenance/efc_auto_changelog.py                 # bygg
  python3 scripts/maintenance/efc_auto_changelog.py --torr          # vis, ikke skriv
  python3 scripts/maintenance/efc_auto_changelog.py --uten-registrering
  python3 scripts/maintenance/efc_auto_changelog.py --base <ref> --head <ref>
  python3 scripts/maintenance/efc_auto_changelog.py --json

Sjekken som avgjør om flatene er i samsvar ligger i ``efc_changelog_check.py``
(CI-inngangen). Denne filen skriver; den sjekker ikke.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from efc_change_id import (  # noqa: E402
    EVENT_ID_RE,
    GENERATOR,
    GENERATORVERSJON,
    IGNORERTE_STIER,
    KILDELOGG,
    META_AKSJON,
    beregn_change_id,
    html_region,
    input_hash,
    json_projeksjon,
    json_tekst,
    les_logg,
    projeksjonsinput,
    sett_inn_region,
)

# MERK: ingen nav-normalisering her. _nav_helper.ensure_nav() er eldre enn
# efc_navbar_sync.py og fjerner den røde «du er her»-markeringen
# (color:#c22) fra siden den skriver til — målt med
# `efc_navbar_sync.py --check`: navbar_drift på EFC_Changelog.html. Denne
# generatoren skriver bare sin egen region; navbaren eies av navbar-syncen.

REPO = Path(__file__).resolve().parents[2]
LOGG = REPO / KILDELOGG
CHANGELOG_JSON = REPO / "docs" / "validation-ledger" / "data" / "changelog.json"
CHANGELOG_HTML = REPO / "docs" / "public" / "EFC_Changelog.html"

ROLLE_ENUM = {"researcher", "orchestrator", "faber", "opus-core", "verifier",
              "legacy", "menneske", "auto"}
STATUS_NAVN = {"A": "added", "D": "deleted", "M": "modified", "R": "renamed",
               "C": "copied", "T": "typechange"}


# --------------------------------------------------------------------------
# git
# --------------------------------------------------------------------------
def _git(*args: str) -> str:
    res = subprocess.run(["git", *args], cwd=str(REPO), capture_output=True,
                         text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)}: {res.stderr.strip()[:200]}")
    return res.stdout


def _git_mykt(*args: str) -> str:
    try:
        return _git(*args).strip()
    except Exception:
        return ""


def standard_base(head: str = "HEAD") -> str:
    """merge-base mot origin/main; faller tilbake på HEAD~1 om den mangler."""
    base = _git_mykt("merge-base", "origin/main", head)
    if base:
        return base
    return _git_mykt("rev-parse", f"{head}~1")


def endrede_stier(base: str, head: str) -> list[tuple[str, str]]:
    """[(status, sti)] for commit-diffen base..head — alle kategorier."""
    rå = _git("diff", "--name-status", "-z", base, head)
    deler = [d for d in rå.split("\0") if d]
    ut: list[tuple[str, str]] = []
    i = 0
    while i < len(deler):
        status = deler[i]
        if status[:1] in ("R", "C"):          # omdøping/kopi: gammel + ny sti
            if i + 2 >= len(deler):
                break
            ut.append((status[:1], deler[i + 2]))
            i += 3
            continue
        if i + 1 >= len(deler):
            break
        ut.append((status[:1], deler[i + 1]))
        i += 2
    return [(s, sti) for s, sti in ut if sti not in IGNORERTE_STIER]


def _siste_commit(sti: str, base: str, head: str) -> str:
    return _git_mykt("log", "--format=%H", "-1", f"{base}..{head}", "--", sti)


def _commit_meta(sha: str) -> dict:
    rå = _git_mykt("show", "-s", "--format=%cI%x00%s%x00%b", sha)
    deler = rå.split("\0")
    dato = deler[0].strip() if deler else ""
    emne = deler[1].strip() if len(deler) > 1 else ""
    kropp = deler[2] if len(deler) > 2 else ""
    try:
        iso = datetime.fromisoformat(dato).astimezone(timezone.utc).isoformat()
    except ValueError:
        iso = datetime.now(timezone.utc).isoformat()
    return {"occurred_at": iso, "emne": emne, "kropp": kropp}


def _trailer(kropp: str, nøkler: tuple[str, ...]) -> str:
    for linje in kropp.splitlines():
        ren = linje.strip()
        for nøkkel in nøkler:
            if ren.lower().startswith(nøkkel):
                verdi = ren[len(nøkkel):].strip(" :\t")
                if verdi:
                    return verdi.split()[0]
    return ""


def neste_event_id(hendelser: list[dict], aar: str) -> str:
    høyeste = 0
    for hendelse in hendelser:
        m = EVENT_ID_RE.match(str(hendelse.get("event_id") or ""))
        if m:
            høyeste = max(høyeste, int(m.group(2)))
    return f"EVT-{aar}-{høyeste + 1:06d}"


def kjente_sti_blob(hendelser: list[dict]) -> set[tuple[str, str]]:
    """(sti, blob) for endringer som allerede står i loggen."""
    kjent: set[tuple[str, str]] = set()
    for hendelse in hendelser:
        blob = str(hendelse.get("blob") or "")
        if not blob:
            continue
        for sti in (hendelse.get("files") or []):
            kjent.add((str(sti), blob))
    return kjent


def registrer(base: str, head: str, tørr: bool) -> dict:
    """Legg nye endringer fra commit-diffen inn i aktivitetsloggen."""
    hendelser, feil = les_logg(LOGG)
    if feil:
        return {"registrert": [], "hoppet_over": [], "feil": feil}
    kjent = kjente_sti_blob(hendelser)
    nye: list[dict] = []
    hoppet_over: list[str] = []
    for status, sti in endrede_stier(base, head):
        blob = "" if status == "D" else _git_mykt("rev-parse", f"{head}:{sti}")
        if blob and (sti, blob) in kjent:
            hoppet_over.append(sti)
            continue
        commit = _siste_commit(sti, base, head)
        meta = (_commit_meta(commit) if commit else
                {"occurred_at": datetime.now(timezone.utc).isoformat(),
                 "emne": "", "kropp": ""})
        aktør = _trailer(meta["kropp"], ("aktør:", "aktor:"))
        rolle = aktør.lower() if aktør.lower() in ROLLE_ENUM else "auto"
        kort = _trailer(meta["kropp"], ("oppgave:", "kort "))
        kort = kort if kort.startswith("t_") else f"auto:{commit[:7]}"
        hendelse = {
            "event_id": neste_event_id(hendelser + nye, meta["occurred_at"][:4]),
            "occurred_at": meta["occurred_at"],
            "action": "file_changed",
            "role": rolle,
            "kanban_card": kort,
            "files": [sti],
            "why": f"commit {commit[:7]}: {meta['emne']}"[:400],
            "result": "success",
            "reversible": True,
            "commit": commit,
            "blob": blob,
            "status": STATUS_NAVN.get(status, "modified"),
        }
        hendelse["change_id"] = beregn_change_id(hendelse)
        nye.append(hendelse)
        kjent.add((sti, blob))
    if nye and not tørr:
        with open(LOGG, "a", encoding="utf-8") as f:
            for hendelse in nye:
                f.write(json.dumps(hendelse, ensure_ascii=False) + "\n")
    return {"registrert": nye, "hoppet_over": hoppet_over, "feil": []}


def sikre_proveniens(hendelser: list[dict], inn_hash: str, tørr: bool) -> dict | None:
    """Loggfør generatorversjon + input_hash som en projection_built-hendelse.

    Append-only og idempotent: finnes allerede en metatypelinje med samme
    (generator, versjon, input_hash), skrives ingenting.
    """
    for hendelse in hendelser:
        if (hendelse.get("action") == META_AKSJON
                and hendelse.get("generator") == GENERATOR
                and hendelse.get("generator_version") == GENERATORVERSJON
                and hendelse.get("input_hash") == inn_hash):
            return None
    tid = datetime.now(timezone.utc).isoformat()
    meta = {
        "event_id": neste_event_id(hendelser, tid[:4]),
        "occurred_at": tid,
        "action": META_AKSJON,
        "role": "auto",
        "kanban_card": "auto-projeksjon",
        "files": [str(CHANGELOG_JSON.relative_to(REPO)),
                  str(CHANGELOG_HTML.relative_to(REPO))],
        "why": (f"changelog-projeksjon bygget: generator={GENERATOR} "
                f"version={GENERATORVERSJON} input_hash={inn_hash}"),
        "result": "success",
        "reversible": True,
        "generator": GENERATOR,
        "generator_version": GENERATORVERSJON,
        "input_hash": inn_hash,
    }
    meta["change_id"] = beregn_change_id(meta)
    if not tørr:
        with open(LOGG, "a", encoding="utf-8") as f:
            f.write(json.dumps(meta, ensure_ascii=False) + "\n")
    return meta


def _skriv(sti: Path, tekst: str, tørr: bool) -> bool:
    """Skriv bare når innholdet faktisk endrer seg (idempotent kjøring)."""
    gammelt = sti.read_text(encoding="utf-8") if sti.is_file() else None
    if gammelt == tekst:
        return False
    if not tørr:
        sti.write_text(tekst, encoding="utf-8")
    return True


def projiser(tørr: bool) -> dict:
    """Bygg de to flatene fra loggen. Returnerer hva som ble skrevet."""
    hendelser, feil = les_logg(LOGG)
    if feil:
        return {"skrevet": [], "feil": feil, "input_hash": None}
    oppføringer, statistikk = projeksjonsinput(hendelser)
    inn_hash = input_hash(oppføringer)
    meta = sikre_proveniens(hendelser, inn_hash, tørr)

    skrevet: list[str] = []
    try:
        eksisterende = json.loads(CHANGELOG_JSON.read_text(encoding="utf-8"))
    except FileNotFoundError:
        eksisterende = {}
    except json.JSONDecodeError as ex:
        return {"skrevet": [], "input_hash": inn_hash,
                "feil": [{"type": "changelog_json_ugyldig", "msg": str(ex)[:120]}]}
    ny_json = json_tekst(json_projeksjon(eksisterende, oppføringer))
    if _skriv(CHANGELOG_JSON, ny_json, tørr):
        skrevet.append(str(CHANGELOG_JSON.relative_to(REPO)))

    if CHANGELOG_HTML.is_file():
        html = CHANGELOG_HTML.read_text(encoding="utf-8")
        aar = (oppføringer[0]["date"][:4] if oppføringer
               else str(datetime.now(timezone.utc).year))
        ny_html = sett_inn_region(html, html_region(oppføringer), aar)
        if _skriv(CHANGELOG_HTML, ny_html, tørr):
            skrevet.append(str(CHANGELOG_HTML.relative_to(REPO)))
    else:
        skrevet.append(f"(mangler: {CHANGELOG_HTML.relative_to(REPO)})")

    return {"skrevet": skrevet, "feil": [], "input_hash": inn_hash,
            "endringer": len(oppføringer), "statistikk": statistikk,
            "proveniens": meta}


def hoved(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--base", help="commit-range start (default: merge-base origin/main HEAD)")
    p.add_argument("--head", default="HEAD")
    p.add_argument("--torr", "--dry-run", action="store_true", dest="torr",
                   help="vis hva som ville blitt skrevet")
    p.add_argument("--uten-registrering", action="store_true",
                   help="bare projiser, ikke les commit-diffen")
    p.add_argument("--json", action="store_true")
    a = p.parse_args(argv)

    rapport: dict = {"generator": GENERATOR, "generator_version": GENERATORVERSJON,
                     "torr": a.torr}
    if a.uten_registrering:
        rapport["registrering"] = {"registrert": [], "hoppet_over": [], "feil": []}
    else:
        base = a.base or standard_base(a.head)
        if not base:
            rapport["registrering"] = {
                "registrert": [], "hoppet_over": [],
                "feil": [{"type": "ingen_base", "msg": "fant ingen merge-base"}]}
        else:
            rapport["base"] = base
            try:
                rapport["registrering"] = registrer(base, a.head, a.torr)
            except Exception as ex:      # git-feil skal ikke stoppe vedlikeholdet
                rapport["registrering"] = {
                    "registrert": [], "hoppet_over": [],
                    "feil": [{"type": "git_feil", "msg": str(ex)[:200]}]}
    rapport["projeksjon"] = projiser(a.torr)

    if a.json:
        print(json.dumps(rapport, ensure_ascii=False, indent=1))
    else:
        reg = rapport["registrering"]
        print(f"[{GENERATOR}] base={rapport.get('base', '-')} head={a.head}"
              f"{' (tørrkjøring)' if a.torr else ''}")
        print(f"  registrert: {len(reg['registrert'])} endring(er), "
              f"hoppet over (allerede logget): {len(reg['hoppet_over'])}")
        for hendelse in reg["registrert"]:
            print(f"    + {hendelse['change_id']} {hendelse['files'][0]}")
        for feil in reg["feil"]:
            print(f"    ! {feil}")
        proj = rapport["projeksjon"]
        print(f"  projeksjon: input_hash={proj.get('input_hash')} "
              f"endringer={proj.get('endringer')}")
        print(f"  skrevet: {proj.get('skrevet')}")
        for feil in proj.get("feil", []):
            print(f"    ! {feil}")
    return 0


if __name__ == "__main__":
    sys.exit(hoved())
