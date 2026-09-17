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

# Hvor mange treff CLI-en viser foer den sier «... og N flere». Et svar paa
# 80 linjer blir ikke lest; de sterkeste treffene er sortert foerst.
_VIS_MAKS = 15


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



def _dekning(repo: Path, ref: str, hent: bool) -> dict:
    """Les dekningsfilen fra SAMME ref. Mangler den, er svaret tomt — ikke en feil.

    Dekningsstatusen er et eget artefakt (`schema/atlas_dekning.json`), ikke
    et felt paa nodene. Uten dette leser oppslaget bare nodene, og maa svare
    «vet ikke» om noe noen faktisk har maalt og funnet manglende.
    """
    try:
        raa = _git(repo, "show", f"{ref}:schema/atlas_dekning.json")
    except AtlasLesingFeil:
        return {"_mangler": True}
    try:
        d = json.loads(raa)
    except json.JSONDecodeError:
        return {"_mangler": True}
    dom = d.get("domener")
    return dom if isinstance(dom, dict) else {"_mangler": True}


def _kjent_hull(dekning: dict, naal: str) -> dict | None:
    """Er emnet et domene noen har maalt? Seker paa domeneNAVN, ikke innhold.

    Bare et treff paa navnet teller. Et treff paa en begrunnelse ville gjort
    «kjent» til «nevnt et sted», og da mister ordet sin verdi.
    """
    if dekning.get("_mangler"):
        return None
    naal_lav = naal.lower()
    for domene, v in dekning.items():
        if not isinstance(v, dict):
            continue
        d_lav = domene.lower()
        if naal_lav == d_lav or naal_lav in d_lav.split("."):
            return {"domene": domene, "status": v.get("status"),
                    "noder": v.get("noder"), "begrunnelse": v.get("begrunnelse"),
                    # VALGFRITT: PR #475 legger maalt meldingsvolum per
                    # domene i dekningsfilen. Finnes det, vises det — og da
                    # kan et hull paa 190 770 skilles fra ett paa 228.
                    # Finnes det ikke, virker oppslaget som foer; et
                    # oppslagsverk som ikke virker foer en annen PR lander,
                    # er et oppslagsverk som ikke virker.
                    "meldinger": v.get("meldinger")}
    return None


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
    dekning = _dekning(Path(repo), ref, hent)
    # `\b` regner `_` som ORDTEGN. Men i node-id-er SKILLER `_` ledd:
    # `homo.sovn_vaaken`, `efc.solar_flare_engine`. Med `\b` ble `sovn`
    # svekket til delstreng selv om den er et eget ledd i id-en (maalt i
    # review 2026-09-17). Vi definerer derfor ordtegnet eksplisitt, slik at
    # `_`, `.` og `-` alle er separatorer — og `sol` i `solid` fortsatt er
    # en delstreng.
    _ORDTEGN = "a-z0-9æøå"
    ordmonster = re.compile(
        rf"(?<![{_ORDTEGN}])" + re.escape(naal) + rf"(?![{_ORDTEGN}])")
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
        buss = str(n.get("buss_domene") or "").lower()
        if ordmonster.search(id_tekst):
            trefftype = "id"
        elif buss and (naal == buss or naal in buss.split(".")):
            # En node som DEKKER domenet `verden.energi` er relevant for
            # «energi» selv om ordet bare staar i prosaen. Uten dette
            # rangerte `efc.enerflyt_engine` som loes prosa.
            trefftype = "domene"
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
    _rang = {"id": 0, "domene": 1, "ord": 2, "delstreng": 3}
    # Innen samme rang: offentlig foer intern. De offentlige er kjernen i
    # det publiserte atlaset; de interne er kontekst.
    treff.sort(key=lambda x: (_rang[x["trefftype"]],
                              x["synlighet"] != "offentlig",
                              x["id"] or ""))
    # «For bredt» hviler paa om soket har NOE PRESIST — ikke paa et antall.
    #
    # Foerste versjon brukte «>50 treff eller >60 % av atlaset». Review runde 4
    # maalte den mot ekte spoersmaal: sol=20, energi=25, kosmos=32, h2o=36 —
    # alle langt under, instrument=82 over. Ingen ekte spoersmaal laa i
    # naarheten, saa tallet var gjettet. Verre: `efc` gir 68 treff hvorav 32
    # PRESISE — en antalls-terskel kalte det bredt, som er stikk motsatt.
    #
    # Kriteriet er derfor: et treff er presist hvis det staar i node-id-en
    # eller dekker et buss-domene. Er det ingen presise treff OG svaret ikke
    # faar plass i visningen, er soket bredt — uansett hvor stort atlaset blir.
    presise = [t for t in treff if t["trefftype"] in ("id", "domene")]
    for_bredt = not presise and len(treff) > _VIS_MAKS
    raad = None
    if for_bredt:
        raad = (f"ingen presise treff — alle {len(treff)} er loes prosa. "
                f"Bruk et mer presist emne, eller se de sterkeste nedenfor")
    return {
        "emne": emne,
        "kilde": atlas["kilde"],
        "ref": ref,
        "commit": atlas["commit"],
        "antall": len(treff),
        "hull": len(treff) == 0,
        "for_bredt": for_bredt,
        "raad": raad,
        "kjent_hull": _kjent_hull(dekning, naal),
        "dekning_fil": "schema/atlas_dekning.json",
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
    p.add_argument("--alle", action="store_true", help="vis alle treff, ikke bare de sterkeste")
    a = p.parse_args()

    if a.emne:
        s = finn(a.repo, a.emne, ref=a.ref, hent=a.hent)
        print(f"{s['kilde']} @ {s['commit'][:8]} — {s['antall']} treff paa «{s['emne']}»")
        if s["hull"]:
            kh = s["kjent_hull"]
            if kh:
                ant = kh.get("meldinger")
                storrelse = f" · {ant} meldinger" if ant is not None else ""
                print(f"  KJENT HULL — maalt som «{kh['status']}»{storrelse}")
                if kh.get("begrunnelse"):
                    print(f"  begrunnelse: {kh['begrunnelse']}")
                if ant is None:
                    print("  (stoerrelse ikke maalt — kommer fra PR #475)")
            else:
                print("  ATLASET VET IKKE — ingen node baerer dette emnet, "
                      "og det er ikke et maalt dekningshull.")
            sys.exit(0)
        kh = s["kjent_hull"]
        if kh:
            print(f"  (domenet {kh['domene']} er maalt som «{kh['status']}»)")
        if s["for_bredt"]:
            print(f"  FOR BREDT — {s['raad']}")
        # Et svar paa 80 linjer er ikke et svar. Vis de sterkeste, og si
        # hvor mange som ligger under — leseren kan be om alle med --alle.
        viste = s["treff"] if a.alle else s["treff"][:_VIS_MAKS]
        for t in viste:
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
        if not a.alle and s["antall"] > _VIS_MAKS:
            print(f"  ... og {s['antall'] - _VIS_MAKS} flere — bruk --alle for hele listen")
    else:
        d = les_atlas(a.repo, ref=a.ref, hent=a.hent)
        print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} noder")
