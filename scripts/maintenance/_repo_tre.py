"""Hvilke filer er repoet? Ett svar, ikke tre.

Målt 2026-09-17 (kanban t_12494ba1): tre instrumenter svarte hver for seg ved å
vandre over disken — `Path(".").rglob("*")`, `root.rglob("*")`, `os.walk(root)`.
I hovedklonen traff de `.worktrees/`: gitignorert (.gitignore), men til stede
på disken. Tre tester som var grønne i CI ble røde lokalt av den — «privat
adresse lekker», «legacy binding», «$id er ikke den tjente identifikatoren» —
fordi instrumentet leste arbeidsstreet og ikke kilden.

Regelen her: i et git-tre er svaret `git ls-files -z`, altså det som faktisk
publiseres, og det er likt i alle kloner. Er treet ikke et git-tre (en rigg i
en temp-katalog, en `git archive`-eksport), leses disken, og de ignorerte
katalogene hoppes over ved navn.

Bare indeksen leses, ikke `--others`: et svar som «ingen privat adresse i
treet» eller «én binding» skal gjelde det som er lagt inn i git, ellers
avhenger svaret av hva som tilfeldigvis ligger ulagt i arbeidsstreet.
Konsekvensen er at en NY fil må `git add`-es før verktøyet ser den.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path, PurePosixPath

# Kataloger som aldri er en del av repoet, uansett hvordan treet leses.
# `.worktrees/` er den målte: arbeidsflater under repoet, ignorert av git, men
# fullt synlige for en diskvandring.
IGNORERTE_KATALOGER = frozenset({
    ".git", ".worktrees", "node_modules", "__pycache__", ".venv", "venv",
})


def git_indeks(root: Path) -> list[str] | None:
    """Sporede stier, relative til `root`, eller None.

    None betyr «dette er ikke et git-tre jeg kan lese» — ikke «tomt tre» — og
    er det som skiller de to kildene til svar. `-z` fordi en sti med mellomrom
    eller en ikke-ASCII bokstav er en sti, og tekstmodus kvoterer begge.
    """
    try:
        ut = subprocess.run(["git", "-C", str(root), "ls-files", "-z"],
                            capture_output=True, timeout=180)
    except (OSError, subprocess.SubprocessError):
        return None
    if ut.returncode != 0:
        return None
    stier = [p for p in ut.stdout.decode("utf-8", "surrogateescape").split("\0") if p]
    # TOM LISTE ER ET SVAR — ikke «ingen indeks».
    #
    # Foerste utgave returnerte `stier or None`. Da ble et gyldig, tomt
    # git-tre behandlet som «ikke et git-tre», `filer()` falt tilbake til
    # diskvandring, og USPOREDE filer ble lest — i strid med premisset om at
    # git-treet er autoritativt. Reprodusert i review 2026-09-17:
    # `git init` + én usporet fil med privat innhold ble returnert.
    #
    # Docstringen over sa allerede at None betyr «ikke et git-tre jeg kan
    # lese» og ikke «tomt tre». Koden gjorde det motsatte av det den sa.
    return stier


def _fra_disk(root: Path, ignorerte: frozenset) -> list[str]:
    ut: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in ignorerte)
        for fn in filenames:
            ut.append((Path(dirpath) / fn).relative_to(root).as_posix())
    return ut


def filer(root: Path, suffixes=None, skip_dirs=(), skip_files=()) -> list[Path]:
    """Filene i treet, sortert på relativ sti.

    `suffixes` er en mengde endelser (None = alle), `skip_dirs` og
    `skip_files` er verktøyets egne unntak — de ignorerte katalogene over
    gjelder alltid i tillegg. Filer som står i indeksen, men er slettet fra
    disken, hoppes over: denne funksjonen svarer med filer som kan leses.
    """
    root = Path(root)
    ignorerte = IGNORERTE_KATALOGER | set(skip_dirs)
    utelatte = set(skip_files)
    indeks = git_indeks(root)
    if indeks is None:
        relative = _fra_disk(root, ignorerte)
    else:
        relative = [p for p in indeks
                    if not any(del_ in ignorerte for del_ in PurePosixPath(p).parts)]
    ut = []
    for rel in relative:
        if rel in utelatte:
            continue
        if suffixes is not None and PurePosixPath(rel).suffix not in suffixes:
            continue
        p = root / rel
        if p.is_file():
            ut.append(p)
    return sorted(ut, key=lambda q: q.relative_to(root).as_posix())
