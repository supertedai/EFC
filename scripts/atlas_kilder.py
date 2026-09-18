#!/usr/bin/env python3
"""atlas_kilder — dekningsfilens tredje akse: KILDEN.

Kort t_f...: «ti domener, én ueid kilde». Atlaset maaler eierskap per
BUSSDOMENE. En kilde som rutes inn i mange domener kan derfor ikke sees
som ueid: hvert domene har sin node, hver node staar som `dekket`, og
kilden de alle LESER staar uten eier. Maalt 2026-09-18:

    GDELT GKG     3 bussemner   20 domener   30 352 meldinger   17 lesere   0 eiere
    World Bank    1 bussemne    18 domener      302 meldinger    0 lesere   0 eiere
    MAST/CAOM     1 bussemne     6 domener      174 meldinger    0 lesere   0 eiere

Domeneaksen sier 39 av 39 dekket. Kildeaksen sier at den stoerste kilden
paa bussen — 30 352 meldinger — ikke eies av en eneste node.

## Hvorfor `navn` og ikke bare emneleddet

`docs/nats-koblingskart.md`: «Emnene har formen `<rot>.<domene>.<lag>.<kilde>`»
— det siste leddet ER kilden, og lista kan derfor UTLEDES av maalingen
istedenfor aa skrives i en Python-dict. Men tre ledd kan hoere til ETT
prosjekt: `gdelt-gkg`, `gdelt-mentions` og `gdelt-export` er tre lesninger
av ett korpus, ikke tre kilder. `navn` er den deklarerte samlingen, og den
er sjekkbar: alle tre maa navngi det samme, og det er navnet nodene selv
skriver i `lagdeling.kilde.kilde`.

## Terskelen, og hvorfor den er argumentert og ikke valgt

En kilde som baeres av ETT domene eies av det domenets node — lesningen ER
noden, og det finnes ingen skygge. Baeres den av TO eller flere, kan ingen
enkelt nodes eierskap dekke den: da maa fravaeret av eier staa NAVNGITT.
Det er den eneste terskelen her, og den foelger av hva et domene er.

    python3 scripts/atlas_kilder.py            # hele kildeinventaret
    python3 scripts/atlas_kilder.py --delt     # bare de som baeres av flere
    python3 scripts/atlas_kilder.py --sjekk    # deklarasjon mot maaling
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROT = Path(__file__).resolve().parents[1]
STANDARD_REF = "origin/main"
DEKNING_STI = "schema/atlas_dekning.json"
SNAPSHOT_STI = "schema/nats_domener.snapshot.json"
NODER_STI = "schema/regime_nodes.jsonld"

#: Statusene en kilde kan ha. De svarer til domeneaksens, men spoer om noe
#: annet: ikke «beskriver atlaset dette?» men «ER atlaset dette?».
#:   eid        en node ER kilden — deklarert i `eiere` og verifisert
#:   lest       noder navngir den som sin kilde; ingen node er den
#:   unavngitt  ingen node navngir den i det hele tatt
#:
#: Ordvalget er med vilje ikke «dekket/ikke_dekket»: en kilde baaret av ett
#: domene kan vaere dekket AV DOMENETS NODE (verden.klima sier selv at
#: noaa-tides er dekket) mens kilden fortsatt ikke er navngitt som kilde
#: noe sted. De to aksene maa kunne ha hver sin sannhet uten aa motsi
#: hverandre.
GYLDIGE_STATUS = {"eid", "lest", "unavngitt"}


class KildeFeil(RuntimeError):
    """Maalingen kunne ikke gjoeres. Aldri et gjettet tall."""


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True)
    if p.returncode != 0:
        raise KildeFeil(f"git {' '.join(args)} feilet i {repo}: {p.stderr.strip()}")
    return p.stdout


def les_fra_ref(repo: str | Path = ROT, ref: str = STANDARD_REF, *,
                hent: bool = False) -> dict:
    """Les maalingen, deklarasjonen og banken fra `ref` — ikke fra arbeidsstreet.

    Samme regel som `atlas_volum`: en arbeidskopi som svarer er ikke et
    levende atlas. `ref="."` er unntaket, og det finnes med vilje: en
    reviewer som har en uinnsendt endring maa kunne sjekke NETTOPP den
    fila, ellers blir sjekken mot `origin/main` et svar paa et annet
    spoersmaal enn det som ble stilt.
    """
    repo = Path(repo)
    if ref == ".":
        ut: dict = {"ref": ".", "commit": "(arbeidsstreet)"}
        for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI),
                            ("noder", NODER_STI)):
            ut[nokkel] = json.loads((repo / sti).read_text(encoding="utf-8"))
        return ut
    if hent:
        _git(repo, "fetch", "-q", "origin")
    ut = {"ref": ref, "commit": _git(repo, "rev-parse", ref).strip()}
    for nokkel, sti in (("snapshot", SNAPSHOT_STI), ("dekning", DEKNING_STI),
                        ("noder", NODER_STI)):
        try:
            ut[nokkel] = json.loads(_git(repo, "show", f"{ref}:{sti}"))
        except json.JSONDecodeError as e:
            raise KildeFeil(f"{ref}:{sti} er ikke gyldig JSON: {e}") from e
    return ut


def kildeinventar(snapshot: dict) -> dict[str, dict]:
    """Kildeleddene bussen baerer — UTLEDET av emnenavnene, maalt i meldinger.

    Ett ledd per emne er den eneste kilden vi har til kildenavnet som ikke
    er skrevet av oss: emnet baerer det selv. Volumet er summen av de
    MAALTE per-emne-tallene, ikke et skjoenn.
    """
    ut: dict[str, dict] = {}
    for domene, rad in (snapshot.get("domener") or {}).items():
        emner = rad.get("emner")
        if not isinstance(emner, dict):
            raise KildeFeil(
                f"maalingen baerer ikke antall per emne ({domene}: "
                f"{type(emner).__name__}). Kjoer `atlas_volum.py --maal` mot "
                f"bussen, eller les en ref som alt baerer volumet.")
        for emne, antall in emner.items():
            ledd = str(emne).split(".")[-1]
            k = ut.setdefault(ledd, {"meldinger": 0, "domener": {}})
            k["meldinger"] += antall
            k["domener"][domene] = k["domener"].get(domene, 0) + antall
    for k in ut.values():
        k["domener"] = dict(sorted(k["domener"].items(),
                                   key=lambda p: (-p[1], p[0])))
    return dict(sorted(ut.items()))


def navngitt(noder: list[dict], navn: str) -> list[str]:
    """Nodene som skriver `navn` som sin kilde — i sitt EGET felt.

    Ingen liste i deklarasjonen kan overleve at dette feltet endres, fordi
    testen utleder den herfra og sammenligner begge veier.
    """
    return sorted(
        n["id"] for n in noder
        if ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde") == navn)


def navn_for(ledd: str, dekl: dict) -> str | None:
    """Prosjektnavnet det deklarerte leddet hoerer til."""
    return (dekl.get("kilder", {}).get(ledd) or {}).get("navn")


def rapport(data: dict) -> list[dict]:
    """Én rad per kildeledd: hva bussen baerer, og hvem som sier noe om det."""
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    dekl = data["dekning"].get("kilder") or {}
    ut = []
    for ledd, målt in inv.items():
        rad = dekl.get(ledd) or {}
        navn = rad.get("navn")
        lesere = navngitt(noder, navn) if navn else []
        ut.append({
            "ledd": ledd,
            "navn": navn,
            "status": rad.get("status"),
            "meldinger": målt["meldinger"],
            "domener": list(målt["domener"]),
            "lesere": lesere,
            "eiere": sorted(rad.get("eiere") or []),
        })
    ut.sort(key=lambda r: (-len(r["domener"]), -r["meldinger"], r["ledd"]))
    return ut


def prosjekter(rader: list[dict]) -> list[dict]:
    """Slår sammen leddene som navngir samme prosjekt.

    Det er HER kortets spoersmaal besvares: tre bussemner med ett navn er
    ett korpus, og de maales som ett — ikke som tre kilder.
    """
    per: dict[str, dict] = {}
    for r in rader:
        n = r["navn"] or f"(uten navn: {r['ledd']})"
        p = per.setdefault(n, {"navn": n, "ledd": [], "meldinger": 0,
                               "domener": set(), "lesere": set(),
                               "eiere": set(), "status": set()})
        p["ledd"].append(r["ledd"])
        p["meldinger"] += r["meldinger"]
        p["domener"] |= set(r["domener"])
        p["lesere"] |= set(r["lesere"])
        p["eiere"] |= set(r["eiere"])
        p["status"].add(r["status"])
    ut = []
    for p in per.values():
        ut.append({**p, "domener": sorted(p["domener"]),
                   "lesere": sorted(p["lesere"]), "eiere": sorted(p["eiere"]),
                   "status": sorted(p["status"])})
    ut.sort(key=lambda p: (-len(p["domener"]), -p["meldinger"], p["navn"]))
    return ut


def avvik(data: dict) -> list[str]:
    """Deklarasjonen mot maalingen, BEGGE veier. Tom liste = ingen avvik.

    Sjekkene, i den rekkefoelgen de ble funnet:
      1. et kildeledd bussen baerer men deklarasjonen tier om
      2. et deklarert ledd som ikke lenger baerer noe
      3. `navn` som ikke er det nodene skriver (eller omvendt)
      4. en `eid`-kilde uten eier, eller en eier som ikke navngir kilden
      5. en eier som ikke finnes i banken
      6. lesere som ikke er de nodene som faktisk navngir kilden
      7. en node som navngir en kilde dens eget bussdomene ikke baerer
    """
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    dekl = data["dekning"].get("kilder")
    if dekl is None:
        return ["schema/atlas_dekning.json har ingen `kilder`-seksjon — "
                "kildeaksen er ikke deklarert i det hele tatt"]
    feil: list[str] = []
    bank = {n["id"]: n for n in noder}

    for ledd in sorted(set(inv) - set(dekl)):
        feil.append(
            f"kildeleddet «{ledd}» baerer {inv[ledd]['meldinger']} meldinger "
            f"over {len(inv[ledd]['domener'])} domene(r) uten aa staa i "
            f"atlas_dekning.json — atlaset vet ikke at kilden finnes")
    for ledd in sorted(set(dekl) - set(inv)):
        feil.append(f"deklarert for kildeleddet «{ledd}», som ikke lenger "
                    f"baerer meldinger")

    # navnene: hvert deklarerte navn maa vaere det nodene skriver, og hvert
    # navn nodene skriver maa staa deklarert.
    deklarerte = {r.get("navn") for r in dekl.values() if r.get("navn")}
    skrevne: set[str] = set()
    for n in noder:
        v = ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")
        if v:
            skrevne.add(str(v))
    for navn in sorted(deklarerte - skrevne):
        feil.append(f"«{navn}» er deklarert som kilde, men ingen node "
                    f"skriver det navnet i lagdeling.kilde.kilde")
    for navn in sorted(skrevne - deklarerte):
        feil.append(f"noder skriver kilden «{navn}», som ikke staar i "
                    f"atlas_dekning.json")

    # bredden: kilden en node leser maa baeres av nodens EGET bussdomene.
    # Uten denne kunne en generator gi en node en kilde den ikke har —
    # maalt: 3 noder fikk GDELT fordi oppslaget falt tilbake paa den.
    for n in noder:
        navn = ((n.get("lagdeling") or {}).get("kilde") or {}).get("kilde")
        dom = n.get("buss_domene")
        if not navn or not dom:
            continue
        baerer = any(dom in inv[ledd]["domener"]
                     for ledd, r in dekl.items() if r.get("navn") == navn)
        if not baerer:
            feil.append(
                f"{n['id']} sier at kilden er «{navn}», men domenet "
                f"{dom} baerer ingen av leddene til den kilden")

    for ledd, rad in sorted(dekl.items()):
        eiere = sorted(rad.get("eiere") or [])
        status = rad.get("status")
        if status not in GYLDIGE_STATUS:
            feil.append(f"{ledd}: ugyldig status {status!r}")
        if status == "eid" and not eiere:
            feil.append(f"{ledd} er «eid» uten en eier")
        if status != "eid" and eiere:
            feil.append(f"{ledd} navngir eiere {eiere}, men status er {status!r}")
        for e in eiere:
            if e not in bank:
                feil.append(f"{ledd}: eieren «{e}» finnes ikke i banken")
                continue
            skriver = ((bank[e].get("lagdeling") or {}).get("kilde") or {}).get("kilde")
            if skriver != rad.get("navn"):
                feil.append(f"{ledd}: eieren «{e}» skriver kilden {skriver!r}, "
                            f"ikke {rad.get('navn')!r}")
        # listen over lesere er utledet — den kan ikke skrives for haand
        if "lesere" in rad:
            maalt = navngitt(noder, rad.get("navn")) if rad.get("navn") else []
            if sorted(rad["lesere"]) != maalt:
                feil.append(f"{ledd}: deklarasjonen sier leserne "
                            f"{sorted(rad['lesere'])}, banken sier {maalt}")
        # en delt kilde uten eier maa bære grunnen sin
        if ledd in inv and len(inv[ledd]["domener"]) > 1 and status != "eid":
            if not str(rad.get("begrunnelse", "")).strip():
                feil.append(
                    f"{ledd} baeres av {len(inv[ledd]['domener'])} domener "
                    f"uten eier og uten begrunnelse — et fravaer av eier "
                    f"skal staa navngitt, ikke vaere stille")
    return feil


def _skriv_seksjon(data: dict, gammel: dict | None = None) -> dict:
    """Bygg `kilder`-seksjonen fra maalingen, med de deklarerte navnene.

    Navnene og begrunnelsene er de eneste feltene som ikke kan utledes —
    alt annet kommer fra bussen og fra banken, og testen utleder det paa
    nytt. Denne funksjonen er derfor en BYGGER, ikke en beslutning: den
    roerer ikke et navn eller en begrunnelse som alt staar der, og den
    leser dem fra FILA den skriver (ellers ville en ny kjoering slettet
    dem, siden maalingen kommer fra en ref uten seksjonen).
    """
    gammel = (data["dekning"].get("kilder") or {}) if gammel is None else gammel
    inv = kildeinventar(data["snapshot"])
    noder = data["noder"]["nodes"]
    ut: dict[str, dict] = {}
    for ledd, målt in inv.items():
        før = gammel.get(ledd) or {}
        navn = før.get("navn")
        lesere = navngitt(noder, navn) if navn else []
        eiere = sorted(før.get("eiere") or [])
        status = "eid" if eiere else ("lest" if lesere else "unavngitt")
        rad: dict = {"navn": navn, "status": status,
                     "meldinger": målt["meldinger"],
                     "domener": list(målt["domener"]), "lesere": lesere,
                     "eiere": eiere}
        if str(før.get("begrunnelse", "")).strip():
            rad["begrunnelse"] = før["begrunnelse"]
        ut[ledd] = rad
    return dict(sorted(ut.items()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", default=STANDARD_REF)
    ap.add_argument("--hent", action="store_true")
    ap.add_argument("--delt", action="store_true",
                    help="bare kilder baaret av flere enn ett domene")
    ap.add_argument("--sjekk", action="store_true",
                    help="deklarasjonen mot maalingen; exit 1 paa avvik")
    ap.add_argument("--skriv", action="store_true",
                    help="bygg `kilder`-seksjonen fra maalingen og skriv fila "
                         "(navn og begrunnelser som alt staar urørt)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.skriv:
        data = les_fra_ref(ROT, a.ref, hent=a.hent)
        sti = ROT / DEKNING_STI
        naa = json.loads(sti.read_text(encoding="utf-8"))
        naa["kilder"] = _skriv_seksjon(data, naa.get("kilder") or {})
        sti.write_text(json.dumps(naa, ensure_ascii=False, indent=2) + "\n",
                       encoding="utf-8")
        print(f"skrev {len(naa['kilder'])} kildeledd til {DEKNING_STI}")
        return 0

    data = les_fra_ref(ROT, a.ref, hent=a.hent)

    if a.sjekk:
        feil = avvik(data)
        for f in feil:
            print(f"AVVIK: {f}")
        print(f"{len(feil)} avvik" if feil else "kildene stemmer med maalingen")
        return 1 if feil else 0

    rader = rapport(data)
    if a.delt:
        rader = [r for r in rader if len(r["domener"]) > 1]
    if a.json:
        print(json.dumps(prosjekter(rader), ensure_ascii=False, indent=1))
        return 0

    print(f"ref {data['ref']} @ {data['commit'][:8]}")
    print(f"{len(rader)} kildeledd, "
          f"{sum(r['meldinger'] for r in rader)} meldinger maalt\n")
    for p in prosjekter(rader):
        eier = ", ".join(p["eiere"]) or ("INGEN" if p["lesere"] else "—")
        print(f"{p['meldinger']:8d} meld  {len(p['domener']):3d} domener  "
              f"{len(p['lesere']):3d} lesere  eier: {eier}")
        print(f"{'':>10}  {p['navn']}  [{', '.join(p['ledd'])}]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
