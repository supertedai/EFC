#!/usr/bin/env python3
"""atlas_lesing — les atlaset fra en GIT-REF, aldri fra et arbeidsstre.

REGELEN SOM KODE, ikke som prosa. Grunnen er maalt: en test som leser et
dokument kan bare se at ordene finnes, ikke hva de betyr. En mutant som
snudde regelen til «les fra arbeidskopien» passerte tre dokumenttester.
Meningen maa derfor bo i en funksjon som kan kjores og muteres mot.

Bakgrunnen, maalt 2026-09-17: atlaset finnes i flere arbeidskopier som ikke
viser samme kart. /opt/agent-work/EFC viste 72 noder mens origin/main hadde
82; /home/morten/EFC-review sto paa en senere merget PR-gren;
.worktrees/vedlikehold manglet `perspektiv` paa alle 45 noder.

    En kopi som svarer, leser som et levende atlas.

Samme feilmodus som 2026-09-16 (atlas-sync mot komponenter som ikke kjorte)
og 2026-09-14 (minne tilgjengelig, men ikke styrende).

MERK om ferskhet: `origin/main` er en remote-tracking ref og kan vaere
foreldet. Denne modulen henter derfor IKKE av seg selv — den rapporterer
hvilken commit den leste, slik at en foreldet ref er synlig i resultatet
i stedet for i leserens antakelse. `hent=False` er standard; sett
`hent=True` naar leseren vil ha ferskest mulig.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

STANDARD_REF = "origin/main"


class AtlasLesingFeil(RuntimeError):
    """Refen kunne ikke leses. Aldri stille fallback til arbeidsstreet."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise AtlasLesingFeil(
            f"git {' '.join(args)} feilet i {repo}: {p.stderr.strip()}")
    return p.stdout


def les_atlas(repo: str | Path, ref: str = STANDARD_REF, *,
              hent: bool = False, sti: str = "schema/regime_nodes.jsonld") -> dict:
    """Les atlaset fra `ref` i `repo` — aldri fra arbeidsstreet.

    Returnerer et objekt som NAVNGIR kilden den leste, slik at en foreldet
    eller feil ref er synlig i resultatet.

    Reiser AtlasLesingFeil hvis refen ikke finnes. Det er med vilje: en
    stille fallback til arbeidsstreet er noeyaktig feilmodusen denne
    funksjonen finnes for aa hindre.
    """
    repo = Path(repo)
    if hent:
        _git(repo, "fetch", "-q", "origin")
    commit = _git(repo, "rev-parse", ref).strip()
    raa = _git(repo, "show", f"{ref}:{sti}")
    try:
        data = json.loads(raa)
    except json.JSONDecodeError as e:
        raise AtlasLesingFeil(
            f"{ref}:{sti} i {repo} er ikke gyldig JSON: {e}") from e
    if not isinstance(data, dict) or "nodes" not in data:
        raise AtlasLesingFeil(
            f"{ref}:{sti} i {repo} mangler 'nodes' — "
            f"noekler: {sorted(data)[:8] if isinstance(data, dict) else type(data).__name__}")
    return {
        "kilde": f"git:{ref}",
        "ref": ref,
        "commit": commit,
        "sti": sti,
        "noder": data["nodes"],
    }


if __name__ == "__main__":
    import sys
    d = les_atlas(sys.argv[1] if len(sys.argv) > 1 else ".")
    print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} noder")
