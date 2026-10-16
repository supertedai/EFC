#!/usr/bin/env python3
"""vedlikeholdsrunde.py — den ukentlige eierskapsløkken.

KJØRES FRA SYSTEM-TIMEREN PÅ HERMES-VERTEN — ALDRI FRA CI. CI kjører bare
sjekkerne (read-only); denne prosessen OPPRETTER kanban-kort og trenger
derfor vertens hermes-tilgang. Idempotens: stabil kort-tittel per funnklasse
(uten antall), flock-lås mot samtidige runder, og hardt tak på kort per kjøring.

Bruk: python3 scripts/maintenance/vedlikeholdsrunde.py [--dry-run]
Exit: 0 = round finished, 1 = a check could not be MEASURED (crash, timeout or
an answer that is not readable JSON -- the unit must fail, never pass as
"0 findings"), 2 = write gate, 3 = kanban list unreadable (no cards created).
3 wins over 1: it also means no cards were created this round.
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

# Which JSON keys carry the findings of each class. A class whose findings come
# from the exit code alone is not listed here (see _funn_fra).
FUNN_NOKLER: dict[str, tuple[str, ...]] = {
    "statement-graf": ("harde", "dangling_reference"),
    "eierskap": ("feil",),
    "repo-contract": ("feil",),
    "aktivitetslogg": ("feil",),
    "risikoregister": ("feil",),
    # Findings from the blast-radius scorer are the classes above «liten»
    # (material -> blokkerende) plus its tool errors: a measurement that could
    # not be made is a finding, not an empty answer. The scorer exits 2 on a
    # tool error.
    "blast-radius": ("funn", "feil"),
    "lenker": ("harde", "funn"),
    "dataset-report-age": ("problems", "expired"),
}

# The type EVERY class gets when it could not measure at all: an unreadable
# answer, a timeout, a crash, or a non-zero exit without a single recognised
# finding. One name for one failure mode, inherited by every class -- because a
# check that could not measure must never be filed as "0 findings".
MANGLENDE_MALING = "measurement_failed"
MAKS_RAATT = 400


def _kjor(navn: str, skript: str, ekstra: list[str]) -> tuple[int, dict, bool]:
    """Run one check. Answers (rc, the answer, readable).

    A crash, a timeout or an answer that is not JSON is an ANSWER too: the
    round must be able to say "could not measure" instead of dying with a
    traceback, or reading the failure as "0 findings".

    Measured 2026-09-21 (t_470cf3c0): one hanging check killed the whole round
    -- subprocess.TimeoutExpired was not caught, so the weekly unit failed with
    a traceback and no class was checked after the hanging one.

    Measured 2026-10-05 (t_c2c0ded1): statement_graph_check.py crashed with
    ModuleNotFoundError (no PyYAML in the interpreter on PATH), this function
    fell back to {"raa": "<traceback>"}, the class found no JSON key, and the
    round printed "rc=1, 0 funn" and exited 0. A crashed check was
    indistinguishable from a clean one.
    """
    argv = [sys.executable, str(MAINT / skript), "--json"] + ekstra
    try:
        r = subprocess.run(argv, capture_output=True, text=True, timeout=300,
                           cwd=str(ROT))
    except subprocess.TimeoutExpired as ex:
        return 124, {"raa": _raatt(ex.stdout), "stderr": _raatt(ex.stderr)}, False
    except OSError as ex:
        return 126, {"raa": f"{type(ex).__name__}: {ex}"}, False
    try:
        ut = json.loads(r.stdout or "")
    except json.JSONDecodeError:
        return r.returncode, {"raa": _raatt(r.stdout),
                              "stderr": _raatt(r.stderr)}, False
    if not isinstance(ut, dict):
        # Valid JSON of the wrong shape is not an answer we can read.
        return r.returncode, {"raa": _raatt(r.stdout)}, False
    return r.returncode, ut, True


def _raatt(tekst: str | bytes | None, maks: int = MAKS_RAATT) -> str:
    """The tail of a raw answer -- enough to name the failure in the card.

    Accepts bytes because subprocess.TimeoutExpired carries whatever the
    partial read produced, and this is exactly the path that must not raise:
    the round has to be able to name a check that never answered.
    """
    if tekst is None:
        return ""
    if isinstance(tekst, bytes):
        tekst = tekst.decode("utf-8", "replace")
    return tekst[-maks:]


def _malingsfeil(navn: str, rc: int, ut: dict, grunn: str) -> dict:
    """A finding that names the failed MEASUREMENT, with its raw evidence."""
    funn = {"type": MANGLENDE_MALING, "check": navn, "rc": rc, "grunn": grunn}
    for nokkel in ("raa", "stderr"):
        if ut.get(nokkel):
            funn[nokkel] = ut[nokkel]
    return funn


def _funn_fra(navn: str, rc: int, ut: dict, leste: bool) -> tuple[list, bool]:
    """Findings for one check, and whether the check could measure at all.

    THE RULE, inherited by every class: rc != 0, or an answer that cannot be
    read as a JSON object, WITHOUT a single recognised finding, is itself a
    finding -- with a type that names the failed measurement. Otherwise a check
    that could not measure would be filed as "0 findings", which is exactly
    what a clean run looks like, and a crashed check would age in silence.
    """
    if not leste:
        return [_malingsfeil(navn, rc, ut, "the answer is not readable JSON")], False
    funn: list = []
    for nokkel in FUNN_NOKLER.get(navn, ()):
        verdi = ut.get(nokkel)
        if isinstance(verdi, list):
            funn += verdi
    if navn == "verifier-bench" and rc != 0:
        # A readable non-zero exit IS this bench's finding channel: it exits 1
        # when it detects fewer known bugs than it carries. That is a gap, not
        # a failed measurement -- and a crash now arrives as an unreadable
        # answer above, so a crash can no longer be read as a gap.
        funn = [{"type": "bench_gap"}]
    if funn:
        return funn, True
    if rc != 0:
        return [_malingsfeil(navn, rc, ut,
                             "non-zero exit without a recognised finding")], False
    return [], True


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
    umaalt = 0
    for navn, skript, ekstra in SJEKKER:
        rc, ut, leste = _kjor(navn, skript, ekstra)
        funn, maalt = _funn_fra(navn, rc, ut, leste)
        if not maalt:
            umaalt += 1
        merke = "" if maalt else "  [COULD NOT MEASURE]"
        print(f"  {navn}: rc={rc}, {len(funn)} funn{merke}")
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
                     + ("NOTE: this class could not be MEASURED -- the finding "
                        "is the failed measurement, so \"0 findings\" here would "
                        "mean \"not looked at\". The raw answer is in the JSON "
                        "below.\n\n" if not maalt else "")
                     + f"Funn:\n```json\n{json.dumps(funn[:40], ensure_ascii=False, indent=1)}\n```\n\n"
                     f"Fiks i branch → PR → CI → merge. Lukk kortet etter readback.")
            if _lag_kort(tittel, kropp, a.dry_run):
                opprettet += 1
            else:
                print(f"  → kortopprettelse feilet for {navn}; funnene står i loggen")
    print(f"  totalt: {totalt_funn} funn, {opprettet} kort opprettet"
          + (f", {umaalt} check(s) could not be measured" if umaalt else ""))
    if kanban_unreadable:
        return 3
    if umaalt:
        # A check that could not measure must fail the unit, not just open a
        # card: the weekly round ran for weeks with a crashed check and exit 0
        # (t_470cf3c0), and the card alone leaves the unit green.
        print(f"{umaalt} check(s) could not be measured -- failing the round",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
