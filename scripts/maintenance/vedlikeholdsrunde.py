#!/usr/bin/env python3
"""vedlikeholdsrunde.py — den ukentlige eierskapsløkken.

Kjører hele sjekkebatteriet og OPPRETTER kanban-kort på
energy-flow-cosmology for hver funnklasse med funn — med idempotens
(samme funnklasse får ikke to åpne kort). Dette er mekanismen som gjør
eierskapet LEVENDE: sjekk → funn → kort → dispatcher → researcher fikser
→ CI bekrefter → neste runde.

Bruk: python3 scripts/maintenance/vedlikeholdsrunde.py [--dry-run]
Exit: 0 = runde ferdig (kort opprettet eller ikke nødvendig), 1 = sjekkfeil.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[2]
MAINT = ROT / "scripts" / "maintenance"
BRETT = "energy-flow-cosmology"
HERMES = "/home/morten/.hermes/hermes-agent/venv/bin/hermes"

SJEKKER = [
    ("statement-graf", "statement_graph_check.py", []),
    ("repo-contract", "validate_repo.py", []),
    ("aktivitetslogg", "validate_activity_log.py", []),
    ("lenker", "validate_links.py", ["--maks-eksterne", "15"]),
    ("verifier-bench", "verifier_bench.py", []),
]


def _kjor(navn: str, skript: str, ekstra: list[str]) -> tuple[int, dict]:
    r = subprocess.run([sys.executable, str(MAINT / skript), "--json"] + ekstra,
                       capture_output=True, text=True, timeout=300, cwd=str(ROT))
    try:
        return r.returncode, json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return r.returncode, {"raa": (r.stdout or "")[:200]}


def _apne_kort_titler() -> set[str]:
    env = {"HERMES_KANBAN_HOME": "/opt/hermes-tavle",
           "PATH": "/usr/local/bin:/usr/bin:/bin"}
    r = subprocess.run([HERMES, "kanban", "--board", BRETT, "list", "--json"],
                       capture_output=True, text=True, timeout=60, env=env)
    try:
        d = json.loads(r.stdout or "{}")
    except json.JSONDecodeError:
        return set()
    rader = d.get("tasks") or d.get("rows") or []
    return {t.get("title", "") for t in rader if t.get("status") not in
            ("done", "archived")}


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


def hoved() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    a = p.parse_args()
    apne = _apne_kort_titler() if not a.dry_run else set()
    print("vedlikeholdsrunde:")
    totalt_funn = 0
    for navn, skript, ekstra in SJEKKER:
        rc, ut = _kjor(navn, skript, ekstra)
        funn = []
        if navn == "statement-graf":
            funn = (ut.get("harde") or []) + (ut.get("dangling_reference") or [])
        elif navn == "repo-contract":
            funn = ut.get("feil") or []
        elif navn == "aktivitetslogg":
            funn = ut.get("feil") or []
        elif navn == "lenker":
            funn = (ut.get("harde") or []) + (ut.get("funn") or [])
        elif navn == "verifier-bench":
            funn = [] if rc == 0 else [{"type": "bench_gap"}]
        print(f"  {navn}: rc={rc}, {len(funn)} funn")
        totalt_funn += len(funn)
        if funn:
            tittel = f"[vedlikehold] {navn}: {len(funn)} funn"
            if not a.dry_run and any(tittel.split(':')[0] in t for t in apne):
                print(f"  → åpent kort finnes allerede for {navn}; hopper")
                continue
            kropp = (f"Automatisk funn fra vedlikeholdsrunden "
                     f"({__import__('datetime').datetime.now():%Y-%m-%d}).\n\n"
                     f"Sjekk: scripts/maintenance/{skript}\n\n"
                     f"Funn:\n```json\n{json.dumps(funn[:40], ensure_ascii=False, indent=1)}\n```\n\n"
                     f"Fiks i branch → PR → CI → merge. Lukk kortet etter readback.")
            _lag_kort(tittel, kropp, a.dry_run)
    print(f"  totalt: {totalt_funn} funn")
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
