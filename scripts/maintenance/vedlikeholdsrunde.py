#!/usr/bin/env python3
"""vedlikeholdsrunde.py — den ukentlige eierskapsløkken.

KJØRES FRA SYSTEM-TIMEREN PÅ HERMES-VERTEN — ALDRI FRA CI. CI kjører bare
sjekkerne (read-only); denne prosessen OPPRETTER kanban-kort og trenger
derfor vertens hermes-tilgang. Idempotens: stabil kort-tittel per funnklasse
(uten antall), flock-lås mot samtidige runder, og hardt tak på kort per kjøring.

Bruk: python3 scripts/maintenance/vedlikeholdsrunde.py [--dry-run]
Exit: 0 = runde ferdig, 1 = sjekkfeil, 2 = write gate,
3 = kanban list unreadable (no cards created).
"""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
MAINT = ROT / "scripts" / "maintenance"
BRETT = "energy-flow-cosmology"
HERMES = "/home/morten/.hermes/hermes-agent/venv/bin/hermes"
MAKS_KORT_PER_KJOERING = 5
LAAS = Path("/tmp/efc-vedlikeholdsrunde.lock")

SJEKKER = [
    ("statement-graf", "statement_graph_check.py", []),
    ("eierskap", "validate_ownership.py", []),
    ("repo-contract", "validate_repo.py", []),
    ("aktivitetslogg", "validate_activity_log.py", []),
    ("risikoregister", "validate_risk_register.py", []),
    ("blast-radius", "blast_radius.py", ["--diff", "origin/main"]),
    ("lenker", "validate_links.py", ["--maks-eksterne", "15"]),
    ("verifier-bench", "verifier_bench.py", []),
    # The dataset scan report declares its own expiry (stale_after_days) and
    # answers it read-only: a finding nobody has handled ages into a card
    # instead of ageing in silence inside a file that says everything is fine.
    ("dataset-report-age", "efc_dataset_scanner.py", ["--check-stale"]),
]


def _kjor(navn: str, skript: str, ekstra: list[str]) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, str(MAINT / skript), "--json"] + ekstra,
                       capture_output=True, text=True, timeout=300, cwd=str(ROT))
    try:
        return r.returncode, json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return r.returncode, {"raa": (r.stdout or "")[:200]}


def _open_titles_from_list(raw: str) -> set[str] | None:
    """Open card titles from `hermes kanban list --json`, or None when the
    answer cannot be read.

    Measured 2026-09-25: the CLI answers with a LIST of cards, not an object
    with `tasks`/`rows`. The old code called `.get` on the list and crashed
    (AttributeError); the unit has been failed since 2026-09-21.
    Both shapes are accepted. None -- not an empty set -- when the answer is
    unreadable: an empty set would mean "no open cards" and create duplicates.
    """
    try:
        d = json.loads(raw or "null")
    except json.JSONDecodeError:
        return None
    if isinstance(d, dict):
        # An object must CARRY the list. `{"error": ...}` or `{"tasks": null}`
        # is not "no open cards" -- it is an answer we do not understand.
        d = d.get("tasks", d.get("rows"))
    if not isinstance(d, list) or not all(isinstance(t, dict) for t in d):
        return None
    return {t.get("title", "") for t in d
            if t.get("status") not in ("done", "archived")}


def _apne_kort_titler() -> set[str] | None:
    env = {"HERMES_KANBAN_HOME": "/opt/hermes-tavle",
           "PATH": "/usr/local/bin:/usr/bin:/bin"}
    r = subprocess.run([HERMES, "kanban", "--board", BRETT, "list", "--json"],
                       capture_output=True, text=True, timeout=60, env=env)
    if r.returncode != 0:
        return None
    return _open_titles_from_list(r.stdout)


def _lag_kort(tittel: str, kropp: str, dry: bool) -> bool:
    miljo = {"HERMES_KANBAN_HOME": "/opt/hermes-tavle",
             "PATH": "/usr/local/bin:/usr/bin:/bin"}
    cmd = [HERMES, "kanban", "--board", BRETT, "create", tittel,
           "--assignee", "researcher", "--priority", "50", "--body", kropp]
    if dry:
        print(f"  [dry-run] ville opprettet: {tittel}")
        return True
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=miljo)
    return r.returncode == 0


def _kun_vert(dry: bool) -> bool:
    """TEKNISK skrive-gate, ikke dokumentasjon: kortopprettelse skjer bare
    når prosessen beviselig kjører på Hermes-verten (kanban-hjemmet finnes)
    og ikke er en CI-job. CI-runnere har verken /opt/hermes-tavle eller
    hermes-binæren."""
    if dry:
        return True
    if os.environ.get("CI"):
        return False
    if not Path("/opt/hermes-tavle/kanban.db").is_file():
        return False
    return Path(HERMES).is_file()


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    if not a.dry_run and not _kun_vert(a.dry_run):
        print("skrive-gate: kortopprettelse er kun tillatt på Hermes-verten",
              file=sys.stderr)
        return 2
    if not a.dry_run:
        laasfil = open(LAAS, "w", encoding="utf-8")
        try:
            fcntl.flock(laasfil, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            print("en annen runde kjører allerede — avslutter", file=sys.stderr)
            return 0
    apne = _apne_kort_titler() if not a.dry_run else set()
    kanban_unreadable = apne is None
    if kanban_unreadable:
        # Without the list of open cards idempotency cannot be guaranteed. The
        # checks still run and findings are logged, but no cards are created,
        # and the round exits 3 so the unit is failed for the right reason.
        print("kanban list could not be read -- creating no cards this round",
              file=sys.stderr)
        apne = set()
    print("vedlikeholdsrunde:")
    totalt_funn = 0
    opprettet = 0
    for navn, skript, ekstra in SJEKKER:
        rc, ut = _kjor(navn, skript, ekstra)
        funn = []
        if navn == "statement-graf":
            funn = (ut.get("harde") or []) + (ut.get("dangling_reference") or [])
        elif navn == "eierskap":
            funn = ut.get("feil") or []
        elif navn == "repo-contract":
            funn = ut.get("feil") or []
        elif navn == "aktivitetslogg":
            funn = ut.get("feil") or []
        elif navn == "risikoregister":
            funn = ut.get("feil") or []
        elif navn == "blast-radius":
            # funn = klasser over «liten» (material → blokkerende) pluss
            # verktøyfeil: en måling som ikke kunne gjøres er et funn, ikke
            # et tomt svar. Blast-scoreren returnerer exit 2 på verktøyfeil.
            funn = (ut.get("funn") or []) + (ut.get("feil") or [])
        elif navn == "lenker":
            funn = (ut.get("harde") or []) + (ut.get("funn") or [])
        elif navn == "verifier-bench":
            funn = [] if rc == 0 else [{"type": "bench_gap"}]
        elif navn == "dataset-report-age":
            # The scanner answers read-only: whatever the report does not say
            # (no expiry, no reader, an unreadable date) plus every finding past
            # its expiry is a finding class of its own.
            funn = (ut.get("problems") or []) + (ut.get("expired") or [])
            if rc != 0 and not funn:
                funn = [{"type": "scan_report_unreadable"}]
        print(f"  {navn}: rc={rc}, {len(funn)} funn")
        totalt_funn += len(funn)
        if funn and not kanban_unreadable and opprettet < MAKS_KORT_PER_KJOERING:
            # STABIL nøkkel: tittel uten antall, slik at ett åpent kort per
            # funnklasse er idempotens-nøkkelen (antall endres, klassen ikke).
            tittel = f"[vedlikehold] {navn}-funn"
            if not a.dry_run and any(tittel == t for t in apne):
                print(f"  → åpent kort finnes allerede: {tittel}; hopper")
                continue
            kropp = (f"Automatisk funn fra vedlikeholdsrunden "
                     f"({datetime.now():%Y-%m-%d}).\n\n"
                     f"Sjekk: scripts/maintenance/{skript}\n\n"
                     f"Funn:\n```json\n{json.dumps(funn[:40], ensure_ascii=False, indent=1)}\n```\n\n"
                     f"Fiks i branch → PR → CI → merge. Lukk kortet etter readback.")
            if _lag_kort(tittel, kropp, a.dry_run):
                opprettet += 1
            else:
                print(f"  → kortopprettelse feilet for {navn}; funnene står i loggen")
    print(f"  totalt: {totalt_funn} funn, {opprettet} kort opprettet")
    return 3 if kanban_unreadable else 0


if __name__ == "__main__":
    raise SystemExit(hoved())
