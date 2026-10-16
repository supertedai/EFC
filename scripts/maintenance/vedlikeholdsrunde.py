#!/usr/bin/env python3
"""vedlikeholdsrunde.py — den ukentlige eierskapsløkken.

KJØRES FRA SYSTEM-TIMEREN PÅ HERMES-VERTEN — ALDRI FRA CI. CI kjører bare
sjekkerne (read-only); denne prosessen OPPRETTER kanban-kort og trenger
derfor vertens hermes-tilgang. Idempotens: stabil kort-tittel per funnklasse
(uten antall), flock-lås mot samtidige runder, og hardt tak på kort per kjøring.

Bruk: python3 scripts/maintenance/vedlikeholdsrunde.py [--dry-run]
Exit: 0 = runde ferdig, 1 = sjekkfeil, 2 = write gate,
3 = kanban list unreadable (no cards created),
4 = no canonical work surface resolved (no cards created).

CARDS CARRY A WORK SURFACE. Every card is created with
`--workspace worktree:<surface>`, where the surface is the board's canonical
one: read from the flat-surface register through `flateopploser` -- the same
resolver the creator port and the dispatch backstop read -- and, when the
register cannot answer, measured as this repo's main clone with git. A card
without a surface is never created: `scratch` is always empty, so the
preflight rejects such a card as a code card in a scratch workspace, and no
worker can ever pick it up (measured 2026-10-05, t_216d8d76).
"""
from __future__ import annotations

import argparse
import fcntl
import importlib.util
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

#: Where the one path->surface resolver can live. Which surface a code card
#: gets belongs to `flateopploser` -- the module the creator port
#: (`kanban-skaper-porten`) and the dispatch backstop
#: (`kanbanstyrer.forhaandssjekk`) share. This file never parses
#: `flateregister.json` itself: one rule, one reader.
FLATEOPPLOSER_KANDIDATER = (
    "/home/morten/.hermes/hooks/flateopploser.py",
    "/opt/hermes-opus/flateopploser.py",
)

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


#: This round's own file, at the same relative path inside a surface. A surface
#: that does not carry the round cannot carry the round's cards either.
EGEN_STI = Path(__file__).resolve().relative_to(ROT)


def _er_kortflate(sti) -> bool:
    """Can this surface carry the round's cards? Measured, never assumed.

    Two demands, both read from the disk: it is the MAIN clone (`.git` is a
    directory -- a linked worktree carries a `.git` file and belongs to one
    card), and it carries this round at `EGEN_STI`. A surface missing either
    one is not a surface for these cards.
    """
    if not isinstance(sti, str) or not sti:
        return False
    p = Path(sti)
    return (p / ".git").is_dir() and (p / EGEN_STI).is_file()


def _flateopploser():
    """The resolver module, or None when it cannot be loaded.

    An explicit pointer (`FLATEOPPLOSER_STI`) is the only candidate when set.
    A module that will not import is not a rule: None, never a partial read.
    """
    kandidater = [os.environ.get("FLATEOPPLOSER_STI", "").strip()]
    kandidater += list(FLATEOPPLOSER_KANDIDATER)
    for sti in kandidater:
        if not sti:
            continue
        fil = Path(sti)
        if not fil.is_file():
            continue
        try:
            spec = importlib.util.spec_from_file_location("efc_flateopploser", fil)
            if spec is None or spec.loader is None:
                continue
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
            return modul
        except Exception:                                     # noqa: BLE001
            continue
    return None


def _flate_fra_register() -> tuple[str | None, str]:
    """The board's canonical surface, from the register, through the resolver.

    `(surface, reason)`: one of the two is always empty. Every failure is a
    reason, never a guess -- and `_kanonisk_flate` prints it, so a fallback is
    never silent.
    """
    modul = _flateopploser()
    if modul is None:
        return None, "flateopploser.py not found in any candidate"
    try:
        dom = modul.opplos(BRETT)
    except Exception as e:                                    # noqa: BLE001
        return None, f"the resolver raised {type(e).__name__}"
    if not isinstance(dom, dict):
        return None, "the resolver answered a shape this file cannot read"
    if dom.get("status") != "resolvert":
        return None, (f"the register did not resolve the board `{BRETT}`: "
                      f"{dom.get('status')}")
    sti = dom.get("path")
    if not _er_kortflate(sti):
        return None, (f"the register points at {sti}, which does not carry "
                      f"this round")
    return sti, ""


def _flate_fra_git(rot: Path = ROT) -> tuple[str | None, str]:
    """This repo's main clone, measured with git.

    `git rev-parse --git-common-dir` names the MAIN clone's `.git` also when
    this round runs from a linked worktree, and the main clone is exactly what
    the dispatcher anchors `<repo>/.worktrees/<card>` under.
    """
    try:
        r = subprocess.run(["git", "-C", str(rot), "rev-parse",
                            "--path-format=absolute", "--git-common-dir"],
                           capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as e:
        return None, f"git could not be run ({type(e).__name__})"
    if r.returncode != 0:
        return None, f"git answered rc={r.returncode} for {rot}"
    svar = Path(r.stdout.strip())
    kandidat = svar.parent if svar.name == ".git" else svar
    if not _er_kortflate(str(kandidat)):
        return None, f"the main clone {kandidat} does not carry this round"
    return str(kandidat), ""


def _kanonisk_flate(rot: Path = ROT) -> str | None:
    """The surface the cards get, or None when no surface can be resolved.

    The register answers first: it is the versioned, reviewed decision on where
    this board's work lives. This repo's main clone is the fallback, so a round
    still reaches a correct surface when the register cannot be read -- and the
    reason is printed, so the fallback is never silent.
    """
    sti, grunn = _flate_fra_register()
    if sti:
        return sti
    print(f"  surface: {grunn} -- measuring this repo's main clone",
          file=sys.stderr)
    sti, grunn = _flate_fra_git(rot)
    if sti:
        print(f"  surface: {sti} (main clone, measured with git)",
              file=sys.stderr)
        return sti
    print(f"  surface: {grunn}", file=sys.stderr)
    return None


def _lag_kort(tittel: str, kropp: str, dry: bool, flate: str) -> bool:
    """Create the card ON the board's canonical surface.

    `--workspace worktree:<flate>` is the point: a card created without it gets
    `scratch`, and scratch is always empty -- the preflight then rejects it as
    a code card in a scratch workspace, and no worker can ever pick it up
    (measured 2026-10-05, t_216d8d76). The dispatcher anchors
    `<flate>/.worktrees/<card>`: one worktree per card, off the main clone.
    """
    if not flate:
        print("  no surface to give the card; not creating it", file=sys.stderr)
        return False
    miljo = {"HERMES_KANBAN_HOME": "/opt/hermes-tavle",
             "PATH": "/usr/local/bin:/usr/bin:/bin"}
    cmd = [HERMES, "kanban", "--board", BRETT, "create", tittel,
           "--assignee", "researcher", "--priority", "50", "--body", kropp,
           "--workspace", f"worktree:{flate}"]
    if dry:
        print(f"  [dry-run] ville opprettet: {tittel} (worktree:{flate})")
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
    # The surface, resolved ONCE before any card exists. A round that cannot
    # resolve one creates no cards at all and exits 4: handing them `scratch`
    # would make every card a blocked card (see the module docstring).
    flate = None if kanban_unreadable else _kanonisk_flate()
    flate_missing = not kanban_unreadable and flate is None
    if flate_missing:
        print("  no canonical work surface -- creating no cards this round",
              file=sys.stderr)
    elif flate:
        print(f"  surface: {flate}")
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
        if (funn and not kanban_unreadable and flate
                and opprettet < MAKS_KORT_PER_KJOERING):
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
            if _lag_kort(tittel, kropp, a.dry_run, flate):
                opprettet += 1
            else:
                print(f"  → kortopprettelse feilet for {navn}; funnene står i loggen")
    print(f"  totalt: {totalt_funn} funn, {opprettet} kort opprettet")
    if kanban_unreadable:
        return 3
    if flate_missing:
        return 4
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
