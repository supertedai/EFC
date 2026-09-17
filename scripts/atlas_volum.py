#!/usr/bin/env python3
"""atlas_volum — dekningsfilens manglende dimensjon: STØRRELSE.

Funnet ved å BRUKE atlasoppslaget (PR #472), ikke ved å teste det. Svaret
«KJENT HULL — målt som `ikke_dekket`» var riktig, men uten størrelse. Målt
2026-09-17 mot `verden_domener`:

    verden.vaer        190 229 meldinger    ikke_dekket
    verden.utdanning     2 598 meldinger    ikke_dekket

73× forskjell, samme svar. Et hull på 190 000 og ett på 200 er ikke samme
sak, og et kart som ikke kan skille dem, kan heller ikke si hvor neste
node skal bygges. `kosmos.kosmologi` er `dekket` med 1 prediksjon — kartet
vier altså mer struktur til den minste kanalen enn til den største.

## Volumet er en MÅLING, ikke en tabell

Tallene hentes fra bussen ved generering (`--maal`) og skrives til
`schema/nats_domener.snapshot.json`, som alt bærer måletidspunkt, kilde og
en utløpsdato (testen `test_snapshottet_har_ikke_gaatt_ut_paa_dato`).
Deklarasjonsfilens `meldinger` er UTLEDT som summen av snapshottets
per-emne-tall — ikke skrevet for hånd. Samme krav som `noder`-listene:
det som står i fila skal kunne utledes, og en test skal utlede det.

    En hardkodet volumtabell ville råtnet ved første endring i
    busstrafikken — og løyet på samme måte som «82 nodes» gjorde.

## Én implementasjon av buss-protokollen

`--maal` snakker med bussen gjennom husets eget verktøy for den, og kaller
`verden_domener` — samme kilde kortet ble målt mot. Stien til verktøyet
staar i miljoevariabelen `VERDEN_MCP`; modulen bærer den ikke selv (den
publiserte flaten skal ikke navngi en vert, og en noekkel som laa her ville
vaert en delt en). Protokollen — innboks-tilfeldighet, Nagle, rammebuffer —
er finjustert der; den dupliseres ikke her. En andre implementasjon ville
vaert to sannheter om samme grensesnitt, og den ene ville sviktet stille.

## Lesing

`hull()` sorterer etter STØRRELSE, ikke alfabetisk — det er hele
poenget. Den leser fra en git-ref (samme regel som `atlas_lesing`), slik
at en arbeidskopi som svarer ikke kan lese som et levende atlas.

    python3 scripts/atlas_volum.py --hull          # ikke_dekket, størst først
    python3 scripts/atlas_volum.py --alle          # alle domener, størst først
    python3 scripts/atlas_volum.py --maal          # mål bussen og skriv filene
"""

from __future__ import annotations

import argparse
import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
STANDARD_REF = "origin/main"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"
DEKNING_STI = "schema/atlas_dekning.json"

#: Husets verktøy for bussen. Stien kan pekes et annet sted med `VERDEN_MCP`
#: — den ligger utenfor repoet med vilje: nøkkelen er per dør (regel nr. 1 i
#: verden-mcp), og en nøkkel som lå i dette repoet ville vært en delt en.
VERDEN_MCP = Path(os.environ.get(
    "VERDEN_MCP", str(Path.home() / ".hermes" / "scripts" / "verden-mcp.py")))

#: Brukerens egen `.env` — der `NATS_VERDEN` står naar verktøyet kjoeres som
#: MCP-server under Hermes. Leses bare for aa sette miljoeet verktøyet selv
#: forventer; innholdet skrives aldri ut.
NATS_ENV = Path(os.environ.get(
    "NATS_ENV_FIL", str(Path.home() / ".hermes" / ".env")))


class VolumFeil(RuntimeError):
    """Maalingen eller lesingen kunne ikke gjoeres. Aldri et gjettet tall."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise VolumFeil(f"git {' '.join(args)} feilet i {repo}: "
                        f"{p.stderr.strip()}")
    return p.stdout


def les_fra_ref(repo: str | Path = ROT, ref: str = STANDARD_REF, *,
                hent: bool = False) -> dict:
    """Les maalingen og deklarasjonen fra `ref` — aldri fra arbeidsstreet.

    Returnerer begge filene sammen med den commiten de ble lest fra, slik
    at en foreldet ref er synlig i resultatet i stedet for i leserens
    antakelse.
    """
    repo = Path(repo)
    if hent:
        _git(repo, "fetch", "-q", "origin")
    commit = _git(repo, "rev-parse", ref).strip()
    ut: dict = {"kilde": f"git:{ref}", "ref": ref, "commit": commit}
    for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI)):
        raa = _git(repo, "show", f"{ref}:{sti}")
        try:
            ut[nokkel] = json.loads(raa)
        except json.JSONDecodeError as e:
            raise VolumFeil(f"{ref}:{sti} er ikke gyldig JSON: {e}") from e
    return ut


def meldinger_per_domene(snapshot: dict) -> dict[str, int]:
    """Summen av de MÅLTE per-emne-tallene, per domene.

    Deklarasjonsfilens `meldinger` skal være nøyaktig dette tallet. Testen
    utleder det paa nytt og sammenligner, saa feltet kan ikke råtne til en
    paastand fra en tidligere maaling.

    Reiser naar maalingen mangler tallene. Foerste utgave av filen bar
    emnene som en LISTE — den formen finnes i refs som er eldre enn denne
    modulen, og en leser som krasjet med `AttributeError: 'list' object has
    no attribute 'values'` sa ingenting om hva som manglet eller hva som
    skulle gjoeres. Formen sjekkes derfor eksplisitt.
    """
    ut: dict[str, int] = {}
    for domene, rad in (snapshot.get("domener") or {}).items():
        emner = rad.get("emner")
        if not isinstance(emner, dict):
            raise VolumFeil(
                f"maalingen baerer ikke antall per emne ({domene}: "
                f"{type(emner).__name__}). Snapshottet er fra foer volumet "
                f"ble maalt — kjoer `atlas_volum.py --maal` mot bussen, eller "
                f"les en ref som alt baerer volumet (`--ref HEAD`). "
                f"Volumet kan ikke utledes av en navneliste, og det skal "
                f"ikke gjettes.")
        ut[domene] = sum(emner.values())
    return ut


def hull(dekning: dict, snapshot: dict | None = None, *,
         statuser: tuple[str, ...] | None = ("ikke_dekket",),
         topp: int | None = None) -> list[dict]:
    """Hullene, sortert etter BETYDNING — meldinger synkende, saa navn.

    Alfabetisk rekkefølge er tilfeldig informasjon om verden: den sier
    hva domenet heter, ikke hvor mye som ligger i det. Sorteringen her er
    den eneste grunnen til at `verden.vaer` (190 000) ikke leses likt som
    `verden.utdanning` (2 600).

    `statuser=None` gir alle domener — da synes ogsaa en `dekket` kanal
    som baerer mye bak én node.
    """
    maalt = meldinger_per_domene(snapshot) if snapshot else {}
    rader: list[dict] = []
    for navn, rad in (dekning.get("domener") or {}).items():
        if statuser is not None and rad.get("status") not in statuser:
            continue
        emne_antall = ((snapshot or {}).get("domener", {})
                       .get(navn, {}).get("emner") or {})
        emner = sorted(
            ((e, emne_antall.get(e)) for e in (rad.get("emner") or [])),
            key=lambda p: (-(p[1] or 0), p[0]))
        rader.append({
            "domene": navn,
            "status": rad.get("status"),
            "meldinger": maalt.get(navn, rad.get("meldinger", 0)),
            "noder": list(rad.get("noder") or []),
            "emner": emner,
        })
    rader.sort(key=lambda r: (-r["meldinger"], r["domene"]))
    return rader[:topp] if topp else rader


def _last_env(sti: Path = NATS_ENV) -> bool:
    """Sett `NATS_VERDEN` fra husets `.env` naar miljoeet ikke alt har den.

    Verktøyet leser URL-en fra miljoeet fordi Hermes starter det med brukerens
    egen `.env`. Kjoeres scriptet fra en skallet, er den ikke satt — og da
    feiler maalingen med «NATS_VERDEN er ikke satt» selv om noekkelen finnes.
    """
    if os.environ.get("NATS_VERDEN"):
        return True
    try:
        linjer = sti.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for linje in linjer:
        if linje.startswith("NATS_VERDEN="):
            os.environ["NATS_VERDEN"] = linje.split("=", 1)[1].strip().strip("'\"")
            return True
    return False


def _kort_emne(domene: str, emne: str) -> str:
    """`verden.vaer.prediksjon.metno` -> `prediksjon.metno`.

    Bussen navngir emnet FULLT UT; domenet er alt noekkelen. Snapshottet
    (og deklarasjonen) bærer den korte formen — den er relativ til domenet,
    og en full form ville dobbeltfoert domenenavnet i hver rad.
    """
    prefiks = f"{domene}."
    return emne[len(prefiks):] if emne.startswith(prefiks) else emne


def maal_bussen(mcp_fil: str | Path | None = None) -> dict:
    """Mål bussen: `{domene: {emne: antall}}` — og de tomme stroemmene.

    Feiler HOYT naar verktøyet eller legitimasjonen mangler. Et hull uten
    tall er ikke et maalt hull, og et gjettet tall er verre enn ingen tall:
    det ser ut som en maaling.
    """
    fil = Path(mcp_fil or VERDEN_MCP)
    if not fil.exists():
        raise VolumFeil(
            f"verden-verktoeyet finnes ikke: {fil} — maalingen kan ikke "
            f"gjoeres. Sett VERDEN_MCP, eller kjoer der verktøyet bor.")
    if not _last_env():
        raise VolumFeil(
            "NATS_VERDEN er ikke satt, og ingen .env med den ble funnet "
            f"({NATS_ENV}). Maalingen krever brukerens EGEN konsumentnoekkel.")
    spec = importlib.util.spec_from_file_location("verden_mcp_volum", fil)
    if spec is None or spec.loader is None:
        raise VolumFeil(f"kunne ikke laste {fil} som modul")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    try:
        svar = modul.verden_domener({})
    except Exception as e:                                    # noqa: BLE001
        raise VolumFeil(f"verden_domener feilet: {type(e).__name__}: {e}") from e
    domener = {navn: {_kort_emne(navn, r["emne"]): int(r["meldinger"])
                      for r in rader}
               for navn, rader in sorted((svar.get("domener") or {}).items())}
    return {"domener": domener,
            "tomme_stroemmer": svar.get("tomme_stroemmer") or []}


def _skriv_json(sti: Path, data: dict) -> None:
    sti.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")


def skriv_snapshot(sti: str | Path, domener: dict, *,
                   lest_av: str, maalt: str | None = None) -> dict:
    """Skriv maalingen. Proveniensen er en del av dataene, ikke en kommentar."""
    maalt = maalt or datetime.datetime.now(
        datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "_proveniens": {
            "kilde": ("NATS-bussen, verden_domener (MCP) — emner og antall "
                      "meldinger lest av JetStream-stroemmenes eget "
                      "state.subjects"),
            "maalt": maalt,
            "lest_av": lest_av,
            "merknad": ("Per-emne-tall ER tilgjengelig: `state.subjects` i "
                        "STREAM.INFO bærer antall per emne. Den tidligere "
                        "merknaden her sa det motsatte — den var en antakelse "
                        "om NATS' overvåkings-API, ikke en måling av "
                        "JetStream-API-et. Tallene her er målte, og "
                        "dekningsfilens `meldinger` er summen av dem."),
        },
        "domener": {navn: {"emner": dict(sorted(emner.items()))}
                    for navn, emner in sorted(domener.items())},
    }
    _skriv_json(Path(sti), data)
    return data


def oppdater_dekning(dekning: dict, domener: dict) -> tuple[dict, dict]:
    """Sett `meldinger` per domene = summen av de maalte per-emne-tallene.

    Alt annet i deklarasjonen er MENNESKETS: `status` og `begrunnelse` er
    en stillingtagen, ikke en utledning. Denne funksjonen rører dem ikke —
    den skriver bare tallet, og rapporterer det den ikke kunne skrive:
    nye domener og nye emner skal felle invarianten inntil noen har tatt
    stilling til dem.

    Returnerer `(ny_dekning, rapport)`.
    """
    maalt = {navn: sum(emner.values()) for navn, emner in domener.items()}
    rapport: dict = {"nye_domener": [], "nye_emner": {}, "borte": []}
    ny: dict = {}
    for navn, rad in (dekning.get("domener") or {}).items():
        if navn not in maalt:
            rapport["borte"].append(navn)
        nye = sorted(set(domener.get(navn, {})) - set(rad.get("emner") or []))
        if nye:
            rapport["nye_emner"][navn] = nye
        ny[navn] = {
            "status": rad.get("status"),
            "meldinger": maalt.get(navn, 0),
            "noder": list(rad.get("noder") or []),
            "begrunnelse": rad.get("begrunnelse", ""),
            "emner": list(rad.get("emner") or []),
        }
    rapport["nye_domener"] = sorted(set(domener) - set(dekning.get("domener") or {}))
    ut = dict(dekning)
    ut["domener"] = ny
    return ut, rapport


def formater(rader: list[dict]) -> str:
    """Tabellen mennesket leser — størst først, med emnene under."""
    if not rader:
        return "  (ingen hull i dette utsnittet)"
    bredde = max(len(r["domene"]) for r in rader)
    linjer = []
    for r in rader:
        linjer.append(f"{r['meldinger']:>10}  {r['status']:<11}  "
                      f"{r['domene']:<{bredde}}  "
                      f"{len(r['noder'])} node(r), {len(r['emner'])} emne(r)")
        for emne, antall in r["emner"][:3]:
            tall = "?" if antall is None else f"{antall}"
            linjer.append(f"{'':>10}  {'':<11}  {emne}  {tall}")
    return "\n".join(linjer)


def hoved(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Dekningsfilens volum — maalt fra bussen, sortert etter "
                    "betydning.")
    ap.add_argument("--ref", default=STANDARD_REF,
                    help=f"git-ref aa lese fra (standard: {STANDARD_REF})")
    ap.add_argument("--topp", type=int, default=None,
                    help="vis bare de N stoerste")
    ap.add_argument("--hull", action="store_true",
                    help="ikke_dekket, stoerst foerst (standard)")
    ap.add_argument("--alle", action="store_true",
                    help="alle domener, ikke bare ikke_dekket")
    ap.add_argument("--maal", action="store_true",
                    help="maal bussen og skriv snapshot + dekningsfil")
    ap.add_argument("--torr", action="store_true",
                    help="med --maal: skriv ingenting, vis hva som ville blitt skrevet")
    ap.add_argument("--repo", default=str(ROT))
    args = ap.parse_args(argv)

    repo = Path(args.repo)

    if args.maal:
        # MAALINGEN LESER ARBEIDSSTREET, ikke refen: den skal skrive til
        # arbeidsstreet, og en pre-bilde fra refen ville stille kastet
        # ukommitterte endringer i deklarasjonen. Lesing av refen er for
        # den som SPOER; maaling er for den som SKRIVER.
        sti = repo / DEKNING_STI
        if not sti.exists():
            raise VolumFeil(f"{sti} finnes ikke — det er deklarasjonen som "
                            f"skal faa volum, og den kan ikke gjettes fram")
        try:
            dekning = json.loads(sti.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            raise VolumFeil(f"{sti} er ikke gyldig JSON: {e}") from e
        ny = maal_bussen()
        domener = ny["domener"]
        lest_av = os.environ.get(
            "ATLAS_LEST_AV",
            f"{os.environ.get('HERMES_PROFILE', 'ukjent')} "
            f"(scripts/atlas_volum.py)")
        if not args.torr:
            skriv_snapshot(repo / SNAPSHOT_STI, domener, lest_av=lest_av)
        ny_dekning, rapport = oppdater_dekning(dekning, domener)
        if not args.torr:
            _skriv_json(sti, ny_dekning)
        for domene, rader in sorted(
                domener.items(), key=lambda kv: -sum(kv[1].values())):
            print(f"{sum(rader.values()):>10}  {domene}")
        if rapport["nye_domener"]:
            print(f"\nIKKE DEKLARERT ({len(rapport['nye_domener'])}) — bærer "
                  f"meldinger, staar ikke i {DEKNING_STI}. Atlaset vet ikke at "
                  f"de finnes, og invarianten skal FELLE inntil noen har tatt "
                  f"stilling til dem:")
            for d in rapport["nye_domener"]:
                print(f"    {d}  {sum(domener[d].values())}")
        for domene, emner in sorted(rapport["nye_emner"].items()):
            print(f"\nNYE EMNER i {domene} — ikke tatt stilling til: {emner}")
        if rapport["borte"]:
            print(f"\nDEKLARERT, MEN UTE AV MAALINGEN: {rapport['borte']} — "
                  f"deklarasjonen lover en verden som ikke lenger er der. "
                  f"Buss-emner innenfor retensjonsvinduet forsvinner av seg "
                  f"selv; fjern dem fra filen eller forklar hvorfor.")
        if args.torr:
            print("\n(--torr: ingenting skrevet)")
        return 0

    lest = les_fra_ref(repo, args.ref)
    print(f"{lest['kilde']} @ {lest['commit'][:8]}", file=sys.stderr)
    rader = hull(lest["dekning"], lest["snapshot"],
                 statuser=None if args.alle else ("ikke_dekket",),
                 topp=args.topp)
    print(formater(rader))
    return 0


def _hoved_med_feil(argv: list[str] | None = None) -> int:
    """VolumFeil er et SVAR, ikke en stakksporing.

    En leser som faar «refen baerer ikke volumet ennaa» vet hva den skal
    gjoere; en leser som faar en stakksporing proever igjen og lurer paa om
    noe er i stykker. Meldingen gaar til stderr, ikke inn i tabellen.
    """
    try:
        return hoved(argv)
    except VolumFeil as e:
        print(f"atlas_volum: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(_hoved_med_feil())
