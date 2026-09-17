#!/usr/bin/env python3
"""atlas_lesing — les atlaset fra en GIT-REF, aldri fra et arbeidsstre.

REGELEN SOM KODE, ikke som prosa. Grunnen er maalt: en test som leser et
dokument kan bare se at ordene finnes, ikke hva de betyr. En mutant som
snudde regelen til «les fra arbeidskopien» passerte tre dokumenttester.
Meningen maa derfor bo i en funksjon som kan kjores og muteres mot.

Bakgrunnen, maalt 2026-09-17: atlaset finnes i flere arbeidskopier som ikke
viser samme kart. Ett arbeidsstre viste 72 noder mens origin/main hadde 82;
en annen klone sto paa en senere merget PR-gren; et vedlikeholds-worktree
manglet `perspektiv` paa alle 45 noder.

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
import re
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


def _har_falsifikator(node: dict) -> bool:
    """Bærer noden en observasjon som ville felle den?

    `ville_falsifisere` er navnet i skjemaet, maalt 2026-09-17. En node som
    ikke kan felles av noe, er en pastand — og leseren skal kunne se
    forskjellen uten aa lese hele noden selv.
    """
    return "ville_falsifisere" in json.dumps(node, ensure_ascii=False)


def finn(repo: str | Path, emne: str, ref: str = STANDARD_REF, *,
         hent: bool = False) -> dict:
    """Slaa opp et emne i atlaset — leser fra `ref`, aldri fra arbeidsstreet.

    Forskjellen fra `les_atlas`: denne svarer paa et SPOERSMAAL. `les_atlas`
    gir deg hele kartet og lar deg lete; prisen for det er at atlaset ikke
    blir konsultert spontant. Maalt 2026-09-17: modulen hadde en utgang og
    ingen inngang.

    Svaret er ALLTID formet likt, ogsaa naar det er tomt:

        {"emne", "antall", "hull", "treff", "kilde", "ref", "commit"}

    `hull: True` betyr «atlaset vet ikke» — det er et svar, ikke en feil,
    og det kan skilles fra en feil fordi en feil REISER. Et oppslagsverk som
    ikke kan si «jeg vet ikke», sier «nei» av uvitenhet.

    Hvert treff navngir sin epistemiske status, slik at leseren ikke maa
    lese hele noden for aa vite hva som er kjent og hva som er stipulert.
    """
    if not emne or not emne.strip():
        raise AtlasLesingFeil(
            "tomt emne — et oppslag uten spoersmaal ville matchet alt og "
            "dermed ikke svart paa noe")
    atlas = les_atlas(repo, ref, hent=hent, sti="schema/regime_nodes.jsonld")
    naal = emne.strip().lower()
    ordmonster = re.compile(r"\b" + re.escape(naal) + r"\b")
    treff = []
    for n in atlas["noder"]:
        tekst = json.dumps(n, ensure_ascii=False).lower()
        if naal not in tekst:
            continue
        # Tre nivaaer, ikke to. «sol» traff `batteri.lading` som ORD — fordi
        # ordet finnes i en tekst inne i noden — men noden handler ikke om
        # sol. Og «sol» traff `h2o.solid` som delstreng av «solid». Uten
        # skillet maa leseren gjette hvilke treff som er ekte.
        id_tekst = str(n.get("id", "")).lower()
        if ordmonster.search(id_tekst):
            trefftype = "id"
        elif ordmonster.search(tekst):
            trefftype = "ord"
        else:
            trefftype = "delstreng"
        treff.append({
            "trefftype": trefftype,
            "id": n.get("id"),
            "synlighet": n.get("synlighet"),
            "perspektiv": n.get("perspektiv"),
            "fase": n.get("phase"),
            "buss_domene": n.get("buss_domene"),
            "har_prediksjon": bool(n.get("prediction")),
            "har_oppgjoer": bool(n.get("settlement")),
            "har_falsifikator": _har_falsifikator(n),
        })
    _rang = {"id": 0, "ord": 1, "delstreng": 2}
    treff.sort(key=lambda x: (_rang[x["trefftype"]], x["id"] or ""))
    return {
        "emne": emne,
        "kilde": atlas["kilde"],
        "ref": ref,
        "commit": atlas["commit"],
        "antall": len(treff),
        "hull": len(treff) == 0,
        "treff": treff,
    }


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Les atlaset — eller slaa opp i det.")
    p.add_argument("repo", nargs="?", default=".", help="sti til repoet")
    p.add_argument("--emne", "-e", help="slaa opp et emne i stedet for aa lese alt")
    p.add_argument("--ref", default=STANDARD_REF, help=f"git-ref (standard: {STANDARD_REF})")
    p.add_argument("--hent", action="store_true", help="hent origin foerst")
    a = p.parse_args()

    if a.emne:
        s = finn(a.repo, a.emne, ref=a.ref, hent=a.hent)
        print(f"{s['kilde']} @ {s['commit'][:8]} — {s['antall']} treff paa «{s['emne']}»")
        if s["hull"]:
            print("  ATLASET VET IKKE — ingen node baerer dette emnet.")
            sys.exit(0)
        for t in s["treff"]:
            merker = []
            if t["har_falsifikator"]:
                merker.append("kan felles")
            if t["har_prediksjon"]:
                merker.append("har prediksjon")
            if t["har_oppgjoer"]:
                merker.append("er gjort opp")
            if t["buss_domene"]:
                merker.append(f"buss:{t['buss_domene']}")
            tt = "" if t["trefftype"] == "id" else f" ({t['trefftype']})"
            print(f"  {t['id']:<34} {t['synlighet'] or '?':<9} "
                  f"{t['perspektiv'] or '':<10} {' · '.join(merker)}{tt}")
    else:
        d = les_atlas(a.repo, ref=a.ref, hent=a.hent)
        print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} noder")
