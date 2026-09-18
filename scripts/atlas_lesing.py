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

API-KARTET — hva de offentlige funksjonene tar og gir. Satt opp 2026-09-18
etter at en leser (jeg) gjettet tre av dem feil fra husken: `finn` ble
indeksert som en liste (den er en dict), `plasser` ble lest med en noekkel
som ikke finnes, og `kjent_hull` ble kalt under et navn som var privat.
Ingen av dem var en feil i atlaset — alle var en feil i grensesnittet.

    les_atlas(repo, ref)            -> dict   hele atlaset
    finn(repo, emne, ref)           -> dict   {antall, hull, for_bredt, raad, ...}
    akser(atlas)                    -> dict   {sti: (antall, eksempelverdier)}
    roter_akse(atlas, akse, verdi)  -> list[dict]
    roter(atlas, node=, ...)        -> dict
    helhet(atlas, node_id)          -> dict   {episenter, felt, motor, ...}
    plasser(atlas, tekst)           -> dict   {status, forslag, naere_noder, ...}
    kjent_hull(repo, emne, ref)     -> dict | None
    naboer/hop/hop_stier/fragment   -> koblingsgrafen
    maaleformer/proxy_kjeder        -> hva maaler, via hva
    sjekk_usikkerhet(atlas, repo)   -> list[str]  hver post mot sin egen kilde

REGELEN de alle foelger: en inngang som ikke vet, SIER det. `finn` svarer
«ATLASET VET IKKE» heller enn aa gi et loest treff; `plasser` svarer
`uten_hjem` heller enn aa gjette et domene.
"""

from __future__ import annotations

import json
import collections
import datetime
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
    # Merk: skjemaet leses IKKE her. Denne funksjonen leser atlaset, og et
    # atlas finnes ogsaa uten skjema (syntetiske repoer i tester, delvise
    # uttrekk). Kravene hentes der de brukes — se `skjema_krav()`.
    return {
        "kilde": f"git:{ref}",
        "ref": ref,
        "commit": commit,
        "sti": sti,
        "noder": data["nodes"],
        "repo": str(repo),
    }


def skjema_krav(atlas: dict) -> list[str]:
    """Hvilke felt KREVER skjemaet av en node? Ett sted, ikke to.

    Maalt 2026-09-18: `plasser` regnet dette ut som alle felt i banken minus
    sju hardkodede unntak — og blant unntakene laa `buss_domene` og
    `falsifiserbarhet`. En ny node ble altsaa bedt om `coupling.empathy_note`,
    men IKKE om buss-domene eller falsifikator: de to feltene resten av huset
    hviler paa. En liste som ikke kan oppdage at den selv har blitt feil er
    ikke et krav — den er et minne.

    Reiser AtlasLesingFeil naar ingen kilde finnes. En tom kravliste ville
    betydd «ingen krav», og det svaret ser ut som kunnskap.
    """
    if atlas.get("skjema_krav"):
        return list(atlas["skjema_krav"])
    if atlas.get("repo") and atlas.get("ref"):
        return _skjema_krav(Path(atlas["repo"]), atlas["ref"])
    raise AtlasLesingFeil(
        "atlaset har ingen kravkilde: verken 'skjema_krav', 'repo' eller "
        "'ref' finnes — da kan kravene ikke leses")


def _skjema_krav(repo: Path, ref: str,
                 sti: str = "schema/regime_node.schema.json") -> list[str]:
    """Les hvilke felt skjemaet KREVER av en node — ett sted, ikke to.

    Reiser AtlasLesingFeil hvis skjemaet mangler eller ikke deklarerer
    `required`. En tom liste ville betydd «ingen krav», og det er et svar
    som ser ut som kunnskap.
    """
    raa = _git(repo, "show", f"{ref}:{sti}")
    try:
        skjema = json.loads(raa)
    except json.JSONDecodeError as e:
        raise AtlasLesingFeil(f"{ref}:{sti} er ikke gyldig JSON: {e}") from e
    krav = ((skjema.get("$defs") or {}).get("RegimeNode") or {}).get("required")
    if not krav:
        raise AtlasLesingFeil(
            f"{ref}:{sti} deklarerer ingen required-liste for RegimeNode")
    return list(krav)


def _har_falsifikator(node: dict) -> bool:
    """Bærer noden en observasjon som ville felle den?

    `ville_falsifisere` er navnet i skjemaet, maalt 2026-09-17. En node som
    ikke kan felles av noe, er en pastand — og leseren skal kunne se
    forskjellen uten aa lese hele noden selv.
    """
    return "ville_falsifisere" in json.dumps(node, ensure_ascii=False)


# ---------------------------------------------------------------------------
# USIKKERHETSLAGET — hvert tall skal kunne bære hvor sikkert det er
#
# ADR-086 §3.1: feltet er valgfritt, lukket og additivt. Kilden HAR
# informasjonen (k = 0.415 ± 0.029 står i sitt eget paper); atlaset mistet den
# i overføringen. Diagnosen er derfor ikke «skaff usikkerhet», men «slutt å
# kaste den» — og da er den ene regelen som gjør laget verdt noe: EN VERDI HAR
# ALLTID EN KILDE.
#
# Sjekkeren står her og ikke i skjemaet, med vilje. Skjemaet sier hva en post
# ER; denne sier om posten STÅR SEG mot kilden sin. Og C10-gaten kan ikke
# kreve feltet før den endres med menneskeord (`t_2e60afa6`) — et krav som
# ikke kan stilles i skjemaet må stilles der det faktisk kjører.
# ---------------------------------------------------------------------------

# Postens og kildens nøkler. Samme tre i skjemaet ($defs/Usikkerhetspost,
# $defs/Usikkerhetskilde) — to lister ville driftet, og den ene ville tiet.
USIKKERHETSPOST_NOKLER = ("storrelse", "verdi", "feilgrense", "kilde")
USIKKERHETSKILDE_NOKLER = ("fil", "linje", "ordrett")

_TALL_RE = re.compile(r"[0-9]+(?:\.[0-9]+)?")
_GRENSE_RE = re.compile(r"±\s*([0-9]+(?:\.[0-9]+)?)")


def _tall_i(tekst: str) -> list[float]:
    return [float(t) for t in _TALL_RE.findall(tekst)]


def _grenser_pa(tekst: str) -> list[float]:
    """Tallene som står rett etter et ± — KILDENS egne feilgrenser."""
    return [float(g) for g in _GRENSE_RE.findall(tekst)]


def _like_tall(a: float, b: float) -> bool:
    """0.029 skrevet som 0.029 og som 2.9e-2 er samme grense for et menneske."""
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def _sporet(repo: Path, fil: str) -> bool:
    """Er filen i repoet? En usporet «kilde» finnes ikke som kilde."""
    p = subprocess.run(["git", "-C", str(repo), "ls-files", "--error-unmatch",
                        "--", fil], capture_output=True, text=True)
    return p.returncode == 0


def _sjekk_usikkerhetspost(node_id: str, nr: int, post, repo: Path) -> list[str]:
    """Én post mot sin egen kildefil. Hver vei ut navngir hvorfor."""
    hvor = f"{node_id}/usikkerhet/{nr}"
    if not isinstance(post, dict):
        return [f"{hvor}: posten er ikke et objekt"]
    if isinstance(post.get("storrelse"), str) and post["storrelse"].strip():
        hvor = f"{hvor} «{post['storrelse']}»"

    # Typevakt FØRST: en manglende nøkkel skal ikke gi en TypeError i
    # diagnosegrenen — da krasjer leseren nettopp der den skal si hva som er galt.
    mangler = [k for k in USIKKERHETSPOST_NOKLER if k not in post]
    if mangler:
        return [f"{hvor}: mangler {', '.join(mangler)}"]

    verdi, grense = post["verdi"], post["feilgrense"]
    for navn, v in (("verdi", verdi), ("feilgrense", grense)):
        if isinstance(v, bool) or not isinstance(v, (int, float, type(None))):
            return [f"{hvor}: {navn} er ikke et tall eller null"]
    kilde = post["kilde"]
    if not isinstance(kilde, dict):
        return [f"{hvor}: usikkerhet uten kilde"]
    mangler = [k for k in USIKKERHETSKILDE_NOKLER if k not in kilde]
    if mangler:
        return [f"{hvor}: kilde mangler {', '.join(mangler)}"]

    fil, linje, ordrett = kilde["fil"], kilde["linje"], kilde["ordrett"]
    if not isinstance(fil, str) or not fil.strip():
        return [f"{hvor}: kilde.fil er tom"]
    if fil.startswith("/") or ".." in fil.split("/"):
        return [f"{hvor}: kilde.fil maa vaere en sti i repoet, ikke {fil!r}"]
    if not _sporet(repo, fil):
        return [f"{hvor}: kilde.fil {fil} er ikke sporet i repoet"]
    if isinstance(linje, bool) or not isinstance(linje, int) or linje < 1:
        return [f"{hvor}: kilde.linje er ikke et positivt heltall"]
    try:
        linjer = (repo / fil).read_text(encoding="utf-8").splitlines()
    except OSError as e:
        return [f"{hvor}: {fil} kunne ikke leses — {e}"]
    if linje > len(linjer):
        return [f"{hvor}: {fil} har {len(linjer)} linjer, posten viser til {linje}"]
    tekst = linjer[linje - 1]

    ut: list[str] = []
    if not isinstance(ordrett, str) or not ordrett.strip():
        ut.append(f"{hvor}: kilde.ordrett er tom — et sitat maa kunne leses")
    elif ordrett not in tekst:
        ut.append(f"{hvor}: ordrett staar ikke paa {fil}:{linje}: {ordrett!r}")

    if isinstance(verdi, (int, float)) and not any(_like_tall(verdi, t)
                                                  for t in _tall_i(tekst)):
        ut.append(f"{hvor}: verdi {verdi} staar ikke paa {fil}:{linje}")

    grenser = _grenser_pa(tekst)
    if grense is None:
        if grenser:
            ut.append(f"{hvor}: kilden OPPGIR en feilgrense ({grenser}) paa "
                      f"{fil}:{linje} — posten sier den ikke gjoer det")
    elif not grenser:
        ut.append(f"{hvor}: feilgrense {grense} er oppgitt, men {fil}:{linje} "
                  f"oppgir ingen (ingen ±) — 0 og gjetting er ikke et svar")
    elif not any(_like_tall(grense, g) for g in grenser):
        ut.append(f"{hvor}: feilgrense {grense} er ikke den kilden oppgir "
                  f"({grenser}) paa {fil}:{linje}")
    return ut


def sjekk_usikkerhet(atlas: dict, repo: str | Path | None = None) -> list[str]:
    """Hver post i usikkerhetslaget mot SIN EGEN kilde. Tom liste = rent.

    Returnerer problemer, ikke en dom: hvert problem navngir noden, posten og
    hva som ikke stemte, slik at svaret kan leses som en rettelse.

    Reglene, alle maalt mot kilden og ingen mot skjemaet:

      * posten maa ha `storrelse` og en `kilde` med fil, linje og et ORDRETT
        utsnitt av linjen;
      * filen maa vaere sporet i repoet, og linjen maa finnes der;
      * `verdi` maa staa paa linjen posten viser til;
      * `feilgrense` er enten et tall kilden oppgir etter et ± PAA DEN LINJEN,
        eller `null` — og `null` krever at linjen ikke oppgir noen.

    Det siste er hele grunnen til at `null` er et svar og 0 ikke er det: en
    feilgrense paa 0 som kilden ikke sier, er en gjetning skrevet som en
    maaling. `β = 0.16 (free amplitude)` er prøven — den skal staa som hull.

    `repo` faller tilbake til `atlas['repo']` (som `les_atlas` setter), og
    mangler begge, reiser vi: en sjekk uten kilder ville svart «alt vel» paa
    hver post, og det svaret ser ut som kunnskap.
    """
    sti = repo if repo is not None else atlas.get("repo")
    if not sti:
        raise AtlasLesingFeil(
            "usikkerhetslaget kan ikke sjekkes uten repo: hverken 'repo' eller "
            "atlas['repo'] finnes — da er det ingen kilder aa lese")
    repo = Path(sti)

    # Baade atlas-laget ('noder', fra les_atlas) og raafila ('nodes') leses.
    # Et atlas UTEN nodenoekkel REISER her, og det er med vilje: en sjekk som
    # ikke finner nodene ville svart «alt vel» paa hver post, og det svaret ser
    # ut som kunnskap — noeyaktig feilmodusen dette laget finnes for aa hindre.
    noder = atlas.get("noder")
    if noder is None:
        noder = atlas.get("nodes")
    if noder is None:
        raise AtlasLesingFeil(
            "atlaset har hverken 'noder' eller 'nodes' — da er det ingen poster "
            "aa sjekke, og «ingen problemer» ville vaert et tomt svar")

    ut: list[str] = []
    for node in noder or []:
        if not isinstance(node, dict):
            continue
        node_id = str(node.get("id") or "?")
        usikkerhet = node.get("usikkerhet")
        if usikkerhet is None:
            continue  # VALGFRITT: en node uten laget er ikke et problem
        if not isinstance(usikkerhet, dict):
            ut.append(f"{node_id}: usikkerhet er ikke et objekt")
            continue
        poster = usikkerhet.get("poster")
        if not isinstance(poster, list) or not poster:
            ut.append(f"{node_id}: usikkerhet uten poster — tomt felt som ser fylt ut")
            continue
        for nr, post in enumerate(poster):
            ut.extend(_sjekk_usikkerhetspost(node_id, nr, post, repo))
    return ut


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


def _norm(s: str) -> str:
    """Bindestrek, understrek og mellomrom er samme skilletegn.

    Et oppslagsverk som ikke ser at `energy-flow` og `energy flow` er samme
    ord, svarer «vet ikke» paa et ord det faktisk eier.
    """
    return " ".join(s.lower().replace("-", " ").replace("_", " ").split())


def _navnerom(repo: Path, ref: str, emne: str) -> list[dict]:
    """Finn registrerte begreper uten aa late som de er atlasnoder.

    To ting skal IKKE svelges stille: et begrep uten `@id` er en defekt i
    registeret (ikke et brukbart treff), og ugyldig JSON i det PRIMAERE
    begrepsregisteret er en feil — ikke «ikke funnet». Et oppslagsverk som
    gjor en lesefeil om til «vet ikke», har svart paa noe annet enn det ble
    spurt om.
    """
    naal = _norm(emne)
    funn = []
    for sti in ("docs/concepts.jsonld", "docs/ontology.jsonld"):
        try:
            data = json.loads(_git(repo, "show", f"{ref}:{sti}"))
        except json.JSONDecodeError as feil:
            raise AtlasLesingFeil(f"{sti} er ikke gyldig JSON: {feil}") from feil
        except AtlasLesingFeil:
            # Fila finnes ikke paa denne refen. Det er et maalt fravaer av et
            # VALGFRITT register, ikke en defekt — og det meldes ikke som treff.
            continue
        for post in data.get("@graph", []):
            kandidater = [post.get("@id"), post.get("label")]
            for felt in ("skos:prefLabel", "skos:notation", "skos:altLabel"):
                verdi = post.get(felt)
                verdier = verdi if isinstance(verdi, list) else [verdi]
                kandidater.extend(
                    v.get("@value") if isinstance(v, dict) else v for v in verdier)
            if any(isinstance(v, str) and _norm(v) == naal for v in kandidater):
                if not isinstance(post.get("@id"), str) or not post["@id"]:
                    raise AtlasLesingFeil(
                        f"{sti}: et begrep matcher «{emne}» men mangler @id — "
                        "registeret er defekt, og et treff uten id kan ikke "
                        "etterproeves")
                funn.append({"id": post["@id"], "kilde": sti})
    unike = {}
    for post in funn:
        unike.setdefault(post["id"], post)
    return sorted(unike.values(), key=lambda x: x["id"] or "")


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
    # Maalt 2026-09-18: `--emne "energy-flow"` traff, `--emne "energy flow"`
    # gav 0 treff. Ordene Morten bruker har BEGGE former, og et oppslagsverk
    # som ikke ser det, svarer «vet ikke» paa et ord det faktisk eier.
    naal = _norm(emne)
    if not naal:
        raise AtlasLesingFeil("tomt emne etter normalisering")
    dekning = _dekning(Path(repo), ref, hent)
    spoersmaalsakse = _loes_spoersmaalsakse(atlas, emne)
    if spoersmaalsakse:
        treff = []
        for n in roter_akse(atlas, spoersmaalsakse):
            treff.append({
                "trefftype": "akse",
                "id": n.get("id"),
                "synlighet": n.get("synlighet"),
                "perspektiv": n.get("perspektiv"),
                "fase": n.get("phase"),
                "buss_domene": n.get("buss_domene"),
                "har_prediksjon": bool(n.get("prediction")),
                "har_oppgjoer": bool(n.get("settlement")),
                "har_falsifikator": _har_falsifikator(n),
            })
        return {
            "emne": emne, "akse": spoersmaalsakse,
            "kilde": atlas["kilde"], "ref": ref, "commit": atlas["commit"],
            "antall": len(treff), "hull": not treff, "for_bredt": False,
            "raad": None, "kjent_hull": _kjent_hull(dekning, naal),
            "dekning_fil": "schema/atlas_dekning.json", "treff": treff,
        }
    # `\\b` regner `_` som ORDTEGN. Men i node-id-er SKILLER `_` ledd:
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
        tekst = _norm(json.dumps(n, ensure_ascii=False))
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
    if not treff:
        registrert = _navnerom(Path(repo), ref, emne)
        if registrert:
            treff = [{
                "trefftype": "navnerom",
                "id": post["id"],
                "synlighet": None,
                "perspektiv": None,
                "fase": None,
                "buss_domene": None,
                "har_prediksjon": False,
                "har_oppgjoer": False,
                "har_falsifikator": False,
                # Maskinlesbar IKKE-DEKNING. Review 2026-09-18: et navneromstreff
                # ga en ikke-tom treffliste, og en leser (eller et
                # nedstroemskall) kunne konkludere «dekket». Atlaset HAR ikke
                # noden — det har begrepet i navnerommet. De to feltene sier
                # det uten at noen maa lese prosaen.
                "har_node": False,
                "dekning": "navnerom_uten_node",
                "grunn": (f"registrert i {post['kilde']}, men er ikke en "
                          "node i schema/regime_nodes.jsonld"),
            } for post in registrert]
    _rang = {"id": 0, "domene": 1, "ord": 2, "delstreng": 3,
             "navnerom": 4}
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
        "akse": None,
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


# ---------------------------------------------------------------------------
# ROTASJON — aa se strukturen fra alle vinkler, ikke bare slaa opp et emne
#
# Maalt 2026-09-17: verktoeyet hadde fire flagg (`--emne`, `--ref`, `--hent`,
# `--alle`). Det kunne slaa opp og liste. Det kunne IKKE filtrere paa
# perspektiv, ikke skille en maalt node fra en avledet, ikke vise
# proxy-kjeder. Rotasjonen fantes ikke.
# ---------------------------------------------------------------------------

#: Faser der noden MAALER noe — den har et instrument i verden.
_MAALENDE_FASER = frozenset({"instrument", "observasjon"})

#: Faser der noden er AVLEDET — regnet, ikke maalt.
_AVLEDEDE_FASER = frozenset({"regime_engine", "computation_engine",
                             "teoretisk", "stabil"})


def roter(atlas: dict, *, node: str | None = None,
          perspektiv: str | None = None, fase: str | None = None,
          domene: str | None = None) -> list[dict]:
    """Roter i atlaset paa tvers av feltene.

    Ett kall, én vinkel. `node` gir HELE noden — alle felt, ikke et utvalg.
    `KeyError` naar noden ikke finnes: et tomt svar ville skjult at navnet
    var feil.
    """
    noder = atlas.get("noder") or []
    if node is not None:
        funn = [n for n in noder if n.get("id") == node]
        if not funn:
            raise KeyError(f"noden `{node}` finnes ikke i atlaset")
        return funn
    if perspektiv is not None:
        noder = [n for n in noder if n.get("perspektiv") == perspektiv]
    if fase is not None:
        noder = [n for n in noder if n.get("phase") == fase]
    if domene is not None:
        noder = [n for n in noder if n.get("buss_domene") == domene]
    return noder


def maaleformer(atlas: dict) -> dict[str, list[str]]:
    """Skill hva som MAALER fra hva som er avledet.

    «maaler eller er etablert» var ETT tall for 47 svaert ulike noder. Det
    skiller ikke et termometer fra en numerisk loeser. Her deles de.
    """
    ut: dict[str, list[str]] = {"instrument": [], "avledet": [], "ingen": []}
    for n in atlas.get("noder") or []:
        fase = n.get("phase")
        m = n.get("measure") or {}
        if fase in _MAALENDE_FASER:
            ut["instrument"].append(n["id"])
        elif fase in _AVLEDEDE_FASER or fase == "regime_engine":
            ut["avledet"].append(n["id"])
        elif m.get("instrument"):
            ut["instrument"].append(n["id"])
        else:
            ut["ingen"].append(n["id"])
    return ut


def proxy_kjeder(atlas: dict) -> dict[str, list[str]]:
    """Hva gaar via hva — i alle ledd.

    `measure.proxy_chain` sier hvilke ledd som skiller det maalte fra det
    konkluderte. En node uten kjede sier at den leser direkte; en med tre
    ledd sier at tre ting maa holde.
    """
    ut: dict[str, list[str]] = {}
    for n in atlas.get("noder") or []:
        kjede = ((n.get("measure") or {}).get("proxy_chain")) or []
        if kjede:
            ut[n["id"]] = list(kjede)
    return ut



# ---------------------------------------------------------------------------
# AKSENE — alle, ikke de seks jeg tilfeldigvis bygde
#
# Maalt 2026-09-17: atlaset bar 21 toppnivaa-felt, alle obligatoriske paa
# alle 86 noder. Rotasjonen dekket seks. Femten var usynlige for verktoeyet.
# Loesningen er ikke tjue flagg: den er aa FINNE aksene selv, saa en akse
# som legges til i morgen ogsaa virker i morgen.
# ---------------------------------------------------------------------------

def _bla(sti: str, v, ut: dict) -> None:
    """Gaa gjennom en node og samle hver sti som en akse.

    Baade bladet OG forelderen registreres: `analogi.avbildning` er nyttig,
    men `analogi` er aksen — en node som HAR isomorfien skal finnes paa den.
    """
    if isinstance(v, dict):
        ut.setdefault(sti, []).append(f"<{len(v)} felt>")
        for k, x in v.items():
            _bla(f"{sti}.{k}", x, ut)
    elif isinstance(v, list):
        ut.setdefault(sti, []).extend(str(x) for x in v)
    elif v is None:
        # `None` er ikke en verdi. `str(None)` ble bokstavelig talt «None»,
        # som er truthy — og gjorde `nivaa.forelder` til en akse med 113
        # noder som svarte 33, med «None» som en tilbudt verdi.
        # Maalt 2026-09-18.
        return
    else:
        ut.setdefault(sti, []).append(str(v))


def akser(atlas: dict) -> dict[str, tuple[int, list[str]]]:
    """Finn ALLE aksene i atlaset — ogsaa de som ikke fantes i gaar.

    Returnerer `{sti: (antall noder som har den, eksempelverdier)}`.
    Nestede felt gaas med dot: `emergence.loop`, `epistemikk.sannhetsstatus`.
    """
    raa: dict[str, set] = {}
    antall: dict[str, int] = {}
    for n in atlas.get("noder") or []:
        blad: dict[str, list] = {}
        for k, v in n.items():
            _bla(k, v, blad)
        for sti, verdier in blad.items():
            # En akse finnes bare hvis den har en VERDI. `nivaa.forelder` er
            # `None` paa 80 av 113 noder; aa telle dem som en verdi gjorde at
            # aksen tilboed 113 og svarte med 33. Maalt 2026-09-18.
            if not any(v for v in verdier):
                continue
            antall[sti] = antall.get(sti, 0) + 1
            raa.setdefault(sti, set()).update(v for v in verdier if v)
    return {sti: (antall[sti], sorted(raa[sti])[:6]) for sti in antall}


def _les_sti(n: dict, akse: str):
    """Les en dot-sti fra en node. `None` om den ikke finnes."""
    v = n
    for del_ in akse.split("."):
        if not isinstance(v, dict) or del_ not in v:
            return None
        v = v[del_]
    return v


#: Navnene MORTEN bruker mot stiene atlaset faktisk barer. Maalt
#: 2026-09-17: `isomorphisme` er `analogi`, `loop` er `emergence.loop`,
#: og `paradigme`/`konsensus`/`akademia` er VERDIER av `perspektiv` —
#: ikke akser. Tre ulike klasser; uten dette laget ser de like ut.
AKSE_ALIAS: dict[str, str] = {
    "isomorphisme": "analogi",
    "isomorfi": "analogi",
    "isomorfisme": "analogi",
    "loop": "emergence.loop",
    "loops": "emergence.loop",
    "sloeyfe": "emergence.loop",
    "sloyfe": "emergence.loop",
    "fraktal": "fractal.pattern",
    "fraktaler": "fractal.pattern",
    "hva_maales": "measure.target",
    "hvem_maaler": "measure.measurer",
    "hvor_maales": "measure.placement",
    "maaleinstrument": "measure.instrument",
    "instrument": "measure.instrument",
    "proxy": "measure.proxy_chain",
    "proxyer": "measure.proxy_chain",
    "observatoer": "observer",
    "kobling": "coupling",
    "domenet": "buss_domene",
    "domene": "buss_domene",
    "antakelser": "ontology.assumes",
    "kompresjon": "measure.compression",
    "rom": "nivaa.lengdeskala",
    "tid": "nivaa.tidsskala",
    "enheter": "maale_paradigme.enheter",
    "koordinater": "maale_paradigme.koordinater",
    "S": "maale_paradigme.s_regime",
    "s": "maale_paradigme.s_regime",
    "s_regime": "maale_paradigme.s_regime",
    "s-akse": "maale_paradigme.s_regime",
    "s-ax": "maale_paradigme.s_regime",
    "sannhet": "epistemikk.sannhetsstatus",
    "evidens": "epistemikk.evidensstatus",
}

# Eierens spoersmaalsformer er et eget navnelag, ikke fritekst som skal
# haapes aa treffe i nodeprosaen. Normaliserte nøkler gjør at mellomrom,
# bindestrek og understrek følger samme regel som resten av oppslaget.
SPOERSMAAL_AKSE: dict[str, str] = {
    "hva maaler": "measure.target",
    "hva maales": "measure.target",
    "hva måler": "measure.target",
    "hva måles": "measure.target",
    "hvem maaler": "measure.measurer",
    "hvem måler": "measure.measurer",
    "hvor maaler": "measure.placement",
    "hvor maales": "measure.placement",
    "hvor måler": "measure.placement",
    "hvor måles": "measure.placement",
    "med hva": "measure.instrument",
    "hvilket instrument": "measure.instrument",
    "via hvilken proxy": "measure.proxy_chain",
    "hvilke proxyer": "measure.proxy_chain",
    "hva komprimerer": "measure.compression",
}


def _loes_spoersmaalsakse(atlas: dict, spoersmaal: str) -> str | None:
    """Loes en eksplisitt spoersmaalsform, ellers None — aldri gjetting."""
    akse = SPOERSMAAL_AKSE.get(_norm(spoersmaal))
    if akse and akse in akser(atlas):
        return akse
    return None


def _loes_akse(atlas: dict, akse: str) -> tuple[str, str | None]:
    """Loes et menneskelig navn til (sti, verdi). Tre klasser.

    1. NAVNET ER STIEN          -> (sti, None)
    2. NAVNET ER ET ALIAS       -> (sti, None)
    3. NAVNET ER EN VERDI       -> (perspektiv, verdi)  <- tredje klasse
    """
    alle = akser(atlas)
    if akse in alle:
        return akse, None
    if akse in AKSE_ALIAS and AKSE_ALIAS[akse] in alle:
        return AKSE_ALIAS[akse], None
    # tredje klasse: er det en VERDI av en kjent akse?
    for sti in ("perspektiv", "phase", "maale_paradigme.status",
                "epistemikk.sannhetsstatus", "epistemikk.evidensstatus"):
        verdier = alle.get(sti, (0, []))[1]
        if akse in verdier:
            return sti, akse
    raise KeyError(akse)


def oversikt(atlas: dict) -> list[tuple[str, list[tuple[str, int]]]]:
    """HELE atlaset paa én gang — hva som er hva, hvor, hvor mange.

    Maalt 2026-09-17: rotasjonen svarte paa ETT spoersmaal om gangen. Morten:
    «ALT dette skal vaere globalt i atlaset og du skal umiddelbart vite hva
    som er hva hvor osv». Det er ikke et soek — det er tilstanden.
    """
    alle = akser(atlas)
    noder = atlas.get("noder") or []
    ut: list[tuple[str, list[tuple[str, int]]]] = []
    for sti in sorted(alle):
        telling: dict[str, int] = {}
        for n in noder:
            v = _les_sti(n, sti)
            if v is None:
                continue
            ledd = v if isinstance(v, list) else [v]
            for x in ledd:
                telling[str(x)] = telling.get(str(x), 0) + 1
        if not telling:
            continue
        fordeling = sorted(telling.items(), key=lambda x: -x[1])
        # bare akser som SKILLER, og bare korte verdier: en fritekst er
        # ikke en kategori. «Umiddelbart» betyr at det maa kunne leses.
        if len(fordeling) < 2:
            continue
        if any(len(v) > 34 or " " in v for v, _ in fordeling[:8]):
            continue
        ut.append((sti, fordeling))
    return ut


def roter_akse(atlas: dict, akse: str, verdi: str | None = None) -> list[dict]:
    """Roter rundt EN akse — toppnivaa eller nested.

    `verdi=None` gir alle noder som HAR aksen. Ukjent akse feiler hoeyt med
    forslag, fordi et tomt svar ville skjult at navnet var feil.
    """
    alle = akser(atlas)
    try:
        akse, l_a_verdi = _loes_akse(atlas, akse)
        if l_a_verdi is not None and verdi is None:
            verdi = l_a_verdi
    except KeyError:
        rot = akse.split(".")[0]
        naere = sorted(a for a in alle
                       if rot in a or a.split(".")[0] in akse
                       or akse in AKSE_ALIAS)[:5]
        if not naere:  # ingen likhet — vis de mest brukte
            naere = [a for a, _ in sorted(alle.items(),
                                          key=lambda x: -x[1][0])[:6]]
        raise KeyError(
            f"aksen `{akse}` finnes ikke i atlaset. "
            f"Nærliggende: {', '.join(naere) if naere else 'ingen'}")
    ut = []
    for n in atlas.get("noder") or []:
        v = _les_sti(n, akse)
        # Tom liste og tom streng er ikke en verdi. `emergence.properties`
        # er `[]` paa 99 av 113 noder; aa telle dem gjorde at aksen svarte
        # 113 der den hadde 99. Maalt 2026-09-18.
        if v is None or (isinstance(v, (list, str, dict)) and not v):
            continue
        if verdi is None:
            ut.append(n)
            continue
        str_v = [str(x) for x in v] if isinstance(v, list) else [str(v)]
        if verdi in str_v:
            ut.append(n)
    return ut



# ---------------------------------------------------------------------------
# KOBLINGENE — 1-hop, 2-hop, 3-hop
#
# Maalt 2026-09-18: verktoeyet hadde `--emne`, `--akse`, `--node`,
# `--oversikt` og `--proxy`. Det hadde INGEN hopp. Koblingene fantes i
# dataene — nivaa.forelder, coupling, analogi, stipulasjoner.motor,
# buss_domene, measure.proxy_chain — og ingen av dem kunne FOELGES.
# ---------------------------------------------------------------------------

def _mekanisme(noder: list[dict]) -> dict[str, dict]:
    return {x["id"]: x for x in noder}


def _koblinger(n: dict, atlas: dict) -> dict[str, list[str]]:
    """Hvilke noder henger sammen med denne, og HVORDAN.

    Koblingstypen er poenget: «samme domene» er svakere enn «er forelder».
    """
    noder = atlas.get("noder") or []
    idx = _mekanisme(noder)
    ut: dict[str, list[str]] = {}

    forelder = (n.get("nivaa") or {}).get("forelder")
    if forelder and forelder in idx:
        ut["forelder"] = [forelder]

    barn = [x["id"] for x in noder
            if (x.get("nivaa") or {}).get("forelder") == n["id"]]
    if barn:
        ut["barn"] = barn

    dom = n.get("buss_domene")
    if dom:
        ut["samme_domene"] = [i for i, x in idx.items()
                              if i != n["id"] and x.get("buss_domene") == dom]

    if isinstance(n.get("analogi"), dict):
        ut["deler_analogi"] = [i for i, x in idx.items()
                               if i != n["id"] and isinstance(x.get("analogi"), dict)]

    motor = (n.get("stipulasjoner") or {}).get("motor")
    if motor:
        ut["samme_motor"] = [
            i for i, x in idx.items() if i != n["id"]
            and (x.get("stipulasjoner") or {}).get("motor") == motor]

    kilde = (n.get("ontology") or {}).get("source")
    if kilde:
        ut["samme_kilde"] = [
            i for i, x in idx.items() if i != n["id"]
            and (x.get("ontology") or {}).get("source") == kilde]

    ledd = set(((n.get("measure") or {}).get("proxy_chain")) or [])
    if ledd:
        ut["deler_proxy_ledd"] = [
            i for i, x in idx.items() if i != n["id"]
            and ledd.intersection(
                set(((x.get("measure") or {}).get("proxy_chain")) or []))]
    return ut


def naboer(atlas: dict, node_id: str) -> dict[str, list[str]]:
    """1-HOP: hva henger denne sammen med, og hvordan. `KeyError` om ukjent."""
    for n in atlas.get("noder") or []:
        if n["id"] == node_id:
            return _koblinger(n, atlas)
    raise KeyError(f"noden `{node_id}` finnes ikke i atlaset")


def hop(atlas: dict, node_id: str, d: int = 1) -> list[str]:
    """Alle noder innen `d` hopp — startnoden selv ikke med."""
    naboer(atlas, node_id)  # validerer at noden finnes
    sett = {node_id}
    front = {node_id}
    for _ in range(max(0, d)):
        ny: set[str] = set()
        for x in front:
            try:
                kob = naboer(atlas, x)
            except KeyError:
                continue
            for ider in kob.values():
                ny.update(ider)
        ny -= sett
        sett |= ny
        front = ny
    sett.discard(node_id)
    return sorted(sett)


def hop_stier(atlas: dict, node_id: str,
              d: int = 2) -> dict[str, tuple[list[str], list[str]]]:
    """Stiene, ikke bare mengden: HVORFOR henger de sammen.

    Returnerer `{node: (stien, koblingstypene langs stien)}`.
    """
    ut: dict[str, tuple[list[str], list[str]]] = {}
    sett = {node_id}
    front: list[tuple[str, list[str], list[str]]] = [(node_id, [node_id], [])]
    for _ in range(max(0, d)):
        ny: list[tuple[str, list[str], list[str]]] = []
        for x, sti, typer in front:
            try:
                kob = naboer(atlas, x)
            except KeyError:
                continue
            for type_, ider in kob.items():
                for i in ider:
                    if i in sett:
                        continue
                    sett.add(i)
                    ny.append((i, sti + [i], typer + [type_]))
                    ut[i] = (sti + [i], typer + [type_])
        front = ny
    return ut


def fragment(atlas: dict, node_id: str) -> dict:
    """Roter rundt ETT fragment: noden, dens koblinger, og naboers naboer.

    «rotere rundt hver fragment en observasjon vi gjor» — naar en observasjon
    kommer inn, skal den kunne settes inn og sees fra alle kanter.
    """
    treff = [x for x in atlas.get("noder") or [] if x["id"] == node_id]
    if not treff:
        rot = node_id.split(".")[0]
        return {"finnes": False, "sokt": node_id,
                "naere": [x["id"] for x in atlas.get("noder") or []
                          if rot in x["id"]][:5]}
    n = treff[0]
    kob = _koblinger(n, atlas)
    return {
        "finnes": True,
        "node": n,
        "koblinger": kob,
        "ett_hopp": len({i for ider in kob.values() for i in ider}),
        "to_hopp": len(hop(atlas, node_id, 2)),
        "tre_hopp": len(hop(atlas, node_id, 3)),
    }


#: Hva slags svar et felt krever av den som plasserer noe nytt.
#: Avklart med Morten 2026-09-18, etter et innspill som ville gjort `--plasser`
#: om til «struktur beregnes, vurderinger foreslaas, paastander kreves».
#:
#:   struktur  — utledbar fra fragmentets plass i kjeden. Fylles, med grunn.
#:   vurdering — beregnbar som kandidat, men semantikken maa godkjennes.
#:   paastand  — kan ikke utledes av noe. Den ER nodens innhold.
#:
#: `phase` ble foreslaatt gjort til enum. Maalt 2026-09-18: 26 verdier, hvorav
#: 19 brukt én gang («solid (ice Ih)», «coexistence (solid + liquid + gas)»);
#: kjernen er sju verdier og dekker 107 av 126 noder. Et lukket enum ville
#: avvist 19 ekte verdier. Fasen er derfor delt — kjerne + rest — ikke lukket.
FELTKLASSE = {
    "id": "struktur", "synlighet": "struktur", "buss_domene": "struktur",
    "nivaa": "struktur",
    "phase": "struktur", "sektor": "struktur",
    "perspektiv": "vurdering", "maale_paradigme": "vurdering",
    "rcmp": "vurdering",
}
#: Felt skjemaet ikke krever, men som huset feller paa. Maalt 2026-09-18 laa
#: `buss_domene` og `falsifiserbarhet` blant de hardkodede unntakene i denne
#: funksjonen, altsaa stikk i strid med hva resten av huset bygger paa.
HUSETS_KRAV = ("buss_domene", "ville_falsifisere", "falsifiserbarhet",
               "prediction", "settlement")


#: Funksjonsord, norske og engelske. De beskriver ikke noe og kan derfor ikke
#: baere en plassering: «med» og «som» staar i nesten hver nodetekst.
STOPPORD = frozenset("""
og av til for med den det de en et som er var paa fra ved mot over under
mellom uten etter mens naar hvor hva hvem hvis saa men eller ikke bare kan
skal vil maa bor blir ble har hadde sine sin sitt seg selv dette disse denne
deres vart vaere alle noen noe annet andre mer mest minst slik slike hvert
hver samt baade enten verken dess fordi dersom
the and for with that this from into over under between without after while
when where what which who whose than then also not only can will shall must
may be been being has have had its their our your his her they them we you it
""".split())


def plasser(atlas: dict, tekst: str) -> dict:
    """Plasser et NYTT fragment — og si hva som gjenstaar.

    Inngangen er ikke et hull. Den er en liste over hva fragmentet maa
    utfylle for aa bli en node: hvilket domene det horer i, hvilke noder
    det ligner, og hvilke felt som mangler.
    """
    if not tekst.strip():
        return {"status": "tomt", "forslag": [], "mangler": []}

    alle = akser(atlas)
    # Funksjonsord baerer ingen plassering. Maalt 2026-09-18: fragmentet
    # «varmepumpe med CO2 som kjolemiddel» matchet paa «med» og «som» — ord som
    # staar i nesten hver node — og svaret ble «naere noder: homo.fluxus,
    # homo.homeostase_buffer, homo.hjerte_syklus, homo.cellesyklus». En liste
    # som SER ut som et plasseringsforslag, men er stoy, er samme klasse som
    # fallbacken som svarer. Kravet er derfor at ordet beskriver noe.
    ord_i = {w for w in _norm(tekst).split()
             if len(w) > 2 and w not in STOPPORD}
    noder = atlas.get("noder") or []

    # hvilke domener nevner ordene?
    domener = alle.get("buss_domene", (0, []))[1]
    treff_domener = [d for d in domener
                     if any(w in _norm(d) for w in ord_i)]

    # hvilke noder deler ord med fragmentet? Vekten legges der ordet FAKTISK
    # beskriver noe: maalet og regimet, ikke alle tekster i noden.
    def _stamme(a: str, b: str, n: int = 5) -> bool:
        """«vulkansk» og «vulkan» er samme ord for et menneske, ikke for ==."""
        return len(a) >= n and len(b) >= n and a[:n] == b[:n]

    def vekt(n: dict) -> int:
        m = n.get("measure") or {}
        r = n.get("regime") or {}
        tung = _norm(" ".join(str(m.get(k) or "") for k in
                              ("target", "measurer", "instrument"))
                     + " " + str(r.get("name") or "") + " " + str(r.get("validity") or ""))
        ord_t = set(tung.split())
        return sum(1 for w in ord_i
                   if w in ord_t or any(_stamme(w, x) for x in ord_t))

    naere = [(vekt(n), n["id"]) for n in noder]
    naere = sorted((x for x in naere if x[0] > 0), key=lambda x: -x[0])
    naere_noder = [i for _, i in naere[:6]]

    forslag = []
    for d in treff_domener:
        eiere = [n["id"] for n in noder if n.get("buss_domene") == d]
        forslag.append({"domene": d, "noder": eiere[:4],
                        "kobling": "domenet nevnes i fragmentet"})
    if not forslag and naere_noder:
        forslag.append({"domene": "(avledet)", "noder": naere_noder[:4],
                        "kobling": ("noder deler ord med fragmentet — "
                                    "ORDLIKHET, ikke et plasseringsforslag")})
    if not forslag:
        # ingen domene-streng matchet: bruk DOMENENE TIL DE NAERE NODENE.
        # Fallback-en skal ikke foreslaa alfabetet — den skal foreslaa det
        # fragmentet LIGNER. (Maalt 2026-09-18: «vulkansk aske» pekte paa
        # kosmos.asteroider/galakser/hoper, altsaa bare de tre forste.)
        sett: list[str] = []
        for _, nid in naere[:8]:
            x = next((y for y in noder if y["id"] == nid), None)
            d = (x or {}).get("buss_domene")
            if d and d not in sett:
                sett.append(d)
        forslag = [{"domene": d, "noder": [],
                    "kobling": "ordlikhet — ikke et kjent domenevalg"}
                   for d in sett[:4]]
        if not forslag:
            forslag = [{"domene": d, "noder": [],
                        "kobling": "ingen anelse — alfabetisk visning, ikke forslag"}
                       for d in alle.get("buss_domene", (0, []))[1][:3]]

    if forslag and len(treff_domener) > 0:
        status = "hjem_funnet"
        domene_visshet = "vet"
        domene_grunnlag = "eksplisitt treff paa buss_domene"
    elif naere_noder and naere[0][0] >= 2:
        status = "svakt"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "bare ordlikhet — ikke et kjent domene"
    else:
        status = "uten_hjem"
        domene_visshet = "ingen_anelse"
        domene_grunnlag = "ingen domeneanelse"

    # Hva slags svar krever hvert felt? Tre klasser, avklart 2026-09-18:
    #   struktur  — utledbar fra fragmentets plass i kjeden; fylles, med grunn
    #   vurdering — beregnbar som kandidat, men semantikken maa godkjennes
    #   paastand  — maa deklareres eksplisitt; kan ikke utledes av noe
    #
    # Og kravene kommer fra skjemaet, ikke fra en haandskrevet liste. Maalt
    # 2026-09-18: `buss_domene` og `falsifiserbarhet` laa blant de hardkodede
    # unntakene, saa en ny node ble bedt om `coupling.empathy_note` men ikke
    # om buss-domene eller falsifikator — de to feltene resten hviler paa.
    krav_fra_skjemaet = skjema_krav(atlas)

    fylt = {f: sum(1 for n in noder
                   if n.get(f) not in (None, "", [], {}))
            for f in set(krav_fra_skjemaet) | set(HUSETS_KRAV)}
    krav = []
    for f in list(krav_fra_skjemaet) + [x for x in HUSETS_KRAV
                                        if x not in krav_fra_skjemaet]:
        klasse = FELTKLASSE.get(f, "paastand")
        post = {"felt": f,
                "klasse": klasse,
                "kilde": "skjema" if f in krav_fra_skjemaet else "huset",
                "fylt_i_banken": f"{fylt.get(f, 0)}/{len(noder)}",
                "forslag": None, "grunn": None}
        if klasse == "struktur":
            post["forslag"], post["grunn"] = _utled_struktur(
                f, tekst, noder, treff_domener,
                alle.get("synlighet", (0, []))[1])
        krav.append(post)

    return {
        "status": status,
        "domene_visshet": domene_visshet,
        "domene_grunnlag": domene_grunnlag,
        "tekst": tekst,
        "forslag": forslag,
        "naere_noder": naere_noder,
        "krav": krav,
        "mangler": [k["felt"] for k in krav],
        "oppsummering": {
            "struktur": sum(1 for k in krav if k["klasse"] == "struktur"),
            "vurdering": sum(1 for k in krav if k["klasse"] == "vurdering"),
            "paastand": sum(1 for k in krav if k["klasse"] == "paastand"),
        },
        "aksene": {k: alle[k][1][:6] for k in
                   ("perspektiv", "phase", "synlighet") if k in alle},
    }


def _utled_struktur(felt: str, tekst: str, noder: list,
                    treff_domener: list, synlighet: list) -> tuple:
    """Utled et strukturfelt — eller si hvorfor det ikke kunne utledes.

    Aldri en gjetning presentert som en verdi. Kan vi ikke utlede det,
    sier vi det, for det er noeyaktig her et fragment blir til en fasit
    hvis vi tier.
    """
    if felt == "id":
        if len(treff_domener) == 1:
            ord_i = [w for w in _norm(tekst).split()
                     if len(w) > 2 and w not in STOPPORD]
            if ord_i:
                prefiks = treff_domener[0].split(".")[-1]
                return (f"{prefiks}.{ord_i[0]}",
                        "domenets prefiks + fragmentets foerste innholdsord "
                        "— et FORSLAG, ikke et vedtak")
        return None, "uten kjent domene finnes ingen id aa bygge paa"
    if felt == "synlighet":
        # Standarden leses fra banken, ikke fra koden: endrer banken seg,
        # endrer forslaget seg.
        verdier = [n.get("synlighet") for n in noder if n.get("synlighet")]
        if not verdier:
            return None, "ingen synlighetsverdi aa lese standarden fra"
        vanligst = max(set(verdier), key=verdier.count)
        return vanligst, (f"{verdier.count(vanligst)}/{len(verdier)} "
                          f"av nodene i banken")
    if felt == "buss_domene":
        if len(treff_domener) == 1:
            return treff_domener[0], "fragmentet nevner ett kjent domene"
        if len(treff_domener) > 1:
            return None, (f"flertydig: {', '.join(treff_domener[:3])} — "
                          f"valget er en vurdering")
        return None, "fragmentet treffer ikke noe kjent domene"
    if felt == "sektor":
        for d in treff_domener:
            verdier = [(n.get("maale_paradigme") or {}).get("sektor")
                       for n in noder if n.get("buss_domene") == d]
            verdier = [v for v in verdier if v]
            if len(set(verdier)) == 1:
                return verdier[0], f"alle {len(verdier)} nodene i {d} har denne"
            if verdier:
                talt = collections.Counter(verdier).most_common()
                return None, (f"flertydig i {d}: "
                              + ", ".join(f"{v} ({c})" for v, c in talt[:3])
                              + " — valget er en vurdering")
        return None, "ingen kjent plass aa lese sektoren fra"
    if felt == "nivaa":
        return None, ("kan utledes naar forelderen er valgt: indeksen maa "
                      "vaere hoeyere enn forelderens")
    if felt == "phase":
        kjerne = ["instrument", "regime_engine", "observasjon",
                  "computation_engine", "teoretisk", "stabil", "observer"]
        return None, ("kjerne: " + ", ".join(kjerne)
                      + " — en ny verdi er et bevisst valg, ikke en fritekst")
    return None, "ingen utledningsregel for dette feltet"


# ---------------------------------------------------------------------------
# HELHETEN — alt om en node, i én lesning
#
# Morten, 2026-09-18: «om vi snakker om h2o, BAO, regnbuen eller victron nå
# skal du umiddelbart via atlaset få en lokalglobal sammenkobling, se
# emergence, se episenter, vektorene, feltene, domene, kryssdomene, flere
# hops i alle retninger, se paradigme, se konsensus, se akademia, se
# emergence, se alle fraktalene den målte emergencen har, kunne rotere rundt
# det vi måler, vite hva vi måler, om det er via proxy, med hvilke
# målemetoder, og instrumentet».
#
# Maalt foer: svaret fantes bare som tretten separate kommandoor.
# ---------------------------------------------------------------------------

def kjent_hull(repo: str | Path, emne: str,
               ref: str = STANDARD_REF, *, hent: bool = False) -> dict | None:
    """Er emnet et KJENT hull — et domene noen har maalt og funnet tomt?

    Dette er den offentlige inngangen. Den private `_kjent_hull` tar
    dekningsfilen som alt er lest; denne gjor oppslaget selv, fordi en
    leser som spoer «er dette et kjent hull?» ikke har dekningsfilen
    for haanden — hen har et emne.

    Satt opp 2026-09-18: `kjent_hull` fantes, men het `_kjent_hull` og
    tok en annen parameter enn den en leser ville gjettet. En inngang
    som ikke kan finnes, virker ikke — uansett hvor riktig den er.
    """
    return _kjent_hull(_dekning(Path(repo), ref, hent), emne)


def helhet(atlas: dict, node_id: str) -> dict:
    """ALT om en node — de seks delene, i én lesning.

    Ikke et sammendrag: hver del er den raa verdien fra noden, fordi et
    sammendrag ville skjult nettopp det man spor etter.
    """
    treff = [x for x in atlas.get("noder") or [] if x["id"] == node_id]
    if not treff:
        rot = node_id.split(".")[0]
        return {"finnes": False, "sokt": node_id,
                "naere": [x["id"] for x in atlas.get("noder") or []
                          if rot in x["id"]][:6]}
    n = treff[0]
    m = n.get("measure") or {}
    epi = n.get("epistemikk") or {}
    em = n.get("emergence") or {}
    fr = n.get("fractal") or {}
    reg = n.get("regime") or {}

    # KOBLINGENE, begge veier: «flere hops i alle retninger»
    ut = _koblinger(n, atlas)
    ut_ider = {i for ider in ut.values() for i in ider}
    inn: dict[str, list[str]] = {}
    for x in atlas.get("noder") or []:
        if x["id"] == node_id:
            continue
        try:
            k = _koblinger(x, atlas)
        except KeyError:
            continue
        if node_id in {i for ider in k.values() for i in ider}:
            typer = [t for t, ider in k.items() if node_id in ider]
            inn[x["id"]] = typer

    # KRYSSDOMENE: hvilke ANDRE domener noden naar via hopp
    eget = n.get("buss_domene")
    kryss: list[str] = []
    for i in ut_ider | set(inn):
        x = next((y for y in atlas["noder"] if y["id"] == i), None)
        d = (x or {}).get("buss_domene")
        if d and d != eget and d not in kryss:
            kryss.append(d)

    return {
        "finnes": True,
        "id": node_id,
        "node": n,
        "episenter": n.get("episenter"),
        "felt": reg,
        "domene": eget,
        "maal": {
            "hva": m.get("target"),
            "hvem": m.get("measurer"),
            "hvor": m.get("placement"),
            "instrument": m.get("instrument"),
            "proxy": m.get("proxy_chain") or [],
            "kompresjon": m.get("compression"),
        },
        "perspektiv": {
            "perspektiv": n.get("perspektiv"),
            "sannhetsstatus": epi.get("sannhetsstatus"),
            "konsensusstatus": epi.get("konsensusstatus"),
            "evidensstatus": epi.get("evidensstatus"),
            "sosial_mekanisme": epi.get("sosial_mekanisme"),
            "konsensus_er_ikke_sannhet": epi.get("konsensus_er_ikke_sannhet"),
        },
        "emergence": em,
        "fraktaler": [fr.get("pattern"), fr.get("note")] + (em.get("properties") or []),
        "motor": (n.get("stipulasjoner") or {}).get("motor") or None,
        "stipulasjoner": n.get("stipulasjoner") or {},
        "observer": n.get("observer") or {},
        "coupling": n.get("coupling") or {},
        "buffer": n.get("buffer") or {},
        "ontology": n.get("ontology") or {},
        "maale_paradigme": n.get("maale_paradigme") or {},
        "nivaa": n.get("nivaa") or {},
        "koblinger": {"ut": ut, "inn": inn},
        "kryssdomene": kryss,
        "ett_hopp": len(ut_ider),
        "to_hopp": len(hop(atlas, node_id, 2)),
        "tre_hopp": len(hop(atlas, node_id, 3)),
        "falsifiserbarhet": n.get("ville_falsifisere"),
    }


def helhet_tekst(atlas: dict, node_id: str) -> str:
    """Helheten som lesbar tekst — for CLI og for oeyet."""
    h = helhet(atlas, node_id)
    if not h["finnes"]:
        return (f"FEIL: `{node_id}` finnes ikke. Nærliggende: "
                f"{', '.join(h['naere']) or 'ingen'}")
    L: list[str] = [f"=== {h['id']} ==="]
    L.append(f"  felt/regime : {h['felt'].get('name', '?')}")
    v = h["felt"].get("validity")
    if v:
        L.append(f"  gyldighet   : {v[:150]}")
    L.append(f"  domene      : {h['domene'] or '(ingen)'}")
    L.append(f"  motor       : {h.get('motor') or '(ingen — ikke en motor-node)'}")
    L.append(f"  episenter   : {h['episenter'] or '(ingen)'}")
    L.append("")
    L.append("  MAALET")
    for k, navn in (("hva", "hva"), ("hvem", "hvem"), ("hvor", "hvor"),
                    ("instrument", "instrument"), ("kompresjon", "kompresjon")):
        if h["maal"].get(k):
            L.append(f"    {navn:11} {str(h['maal'][k])[:130]}")
    if h["maal"]["proxy"]:
        L.append(f"    proxy       {' -> '.join(str(x) for x in h['maal']['proxy'])[:130]}")
    else:
        L.append("    proxy       ingen — lest direkte")
    L.append("")
    L.append("  PERSPEKTIVET")
    for k in ("perspektiv", "sannhetsstatus", "konsensusstatus",
              "evidensstatus", "sosial_mekanisme"):
        if h["perspektiv"].get(k):
            L.append(f"    {k:16} {str(h['perspektiv'][k])[:120]}")
    L.append("")
    L.append(f"  EMERGENCE   {str(h['emergence'].get('loop'))[:130]}")
    L.append(f"  FRAKTALER   {len(h['fraktaler'])} ledd")
    for f in h["fraktaler"][:3]:
        if f:
            L.append(f"    - {str(f)[:120]}")
    L.append("")
    L.append(f"  KOBLINGER   1-hop {h['ett_hopp']} · 2-hop {h['to_hopp']} · "
             f"3-hop {h['tre_hopp']}")
    for t, ider in h["koblinger"]["ut"].items():
        if ider:
            L.append(f"    ut  {t:17} {len(ider):3}  {', '.join(ider[:4])[:60]}")
    for i, typer in list(h["koblinger"]["inn"].items())[:6]:
        L.append(f"    inn {','.join(typer)[:17]:17}       {i}")
    if h["kryssdomene"]:
        L.append(f"  KRYSSDOMENE {', '.join(h['kryssdomene'][:5])}")
    if h.get("falsifiserbarhet"):
        L.append(f"  FALSIFIKATOR {h['falsifiserbarhet'][:130]}")
    return "\n".join(L)


def skriv_inntak(atlas: dict, tekst: str, fil: str | Path, *,
                 kilde: str = "samtale") -> dict:
    """Append one retain fragment to the queue file, without creating a node."""
    plassering = plasser(atlas, tekst)
    record = {
        "tekst": tekst,
        "tidspunkt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "plasseringsstatus": plassering["status"],
        "domene_visshet": plassering.get("domene_visshet"),
        "domene_grunnlag": plassering.get("domene_grunnlag"),
        "forslag": plassering.get("forslag", []),
        "naere_noder": plassering.get("naere_noder", []),
        "mangler": plassering.get("mangler", []),
        "kilde": kilde,
        "proveniens_kilde": kilde,
        "proveniens": {
            "kilde": kilde,
            "atlas": atlas.get("kilde"),
            "commit": atlas.get("commit"),
        },
    }
    sti = Path(fil)
    sti.parent.mkdir(parents=True, exist_ok=True)
    with sti.open("a", encoding="utf-8") as ut:
        ut.write(json.dumps(record, ensure_ascii=False) + "\n")
    return record


if __name__ == "__main__":
    import argparse
    import sys

    p = argparse.ArgumentParser(description="Les atlaset — eller slaa opp i det.")
    p.add_argument("repo", nargs="?", default=".", help="sti til repoet")
    p.add_argument("--emne", "-e", help="slaa opp et emne i stedet for aa lese alt")
    p.add_argument("--ref", default=STANDARD_REF, help=f"git-ref (standard: {STANDARD_REF})")
    p.add_argument("--hent", action="store_true", help="hent origin foerst")
    p.add_argument("--alle", action="store_true", help="vis alle treff, ikke bare de sterkeste")
    p.add_argument("--node", help="roter rundt EN node — vis alle felt")
    p.add_argument("--perspektiv", help="roter: filtrer paa perspektiv (paradigme/konsensus/akademia)")
    p.add_argument("--fase", help="roter: filtrer paa fase (instrument/regime_engine/...)")
    p.add_argument("--domene", help="roter: filtrer paa buss_domene")
    p.add_argument("--maaleform", action="store_true",
                   help="roter: skill hva som MAALER fra hva som er avledet")
    p.add_argument("--proxy", action="store_true", help="roter: vis alle proxy-kjeder")
    p.add_argument("--akser", action="store_true",
                   help="list ALLE aksene atlaset barer — ogsaa de nye")
    p.add_argument("--akse", help="roter rundt en vilkaarlig akse: `sti` eller `sti=verdi`")
    p.add_argument("--alt", dest="alt", help="HELHETEN: alt om en node, i én lesning")
    p.add_argument("--plasser", help="plasser et NYTT fragment: hvor horer det, og hva mangler")
    p.add_argument("--innta", help="ta imot et fragment i retain-koeen (ingen node opprettes)")
    p.add_argument("--kilde", default="samtale", help="provenienskilde for --innta")
    p.add_argument("--inntak-fil", help="alternativ JSONL-fil for --innta")
    p.add_argument("--hop", help="N hopp fra en node:  eller ")
    p.add_argument("--fragment", help="roter rundt ETT fragment: node + alle koblinger")
    p.add_argument("--oversikt", action="store_true",
                   help="HELE atlaset paa én gang: hva som er hva, hvor, hvor mange")
    a = p.parse_args()

    # HELHETEN — alt om en node
    if a.alt:
        atlas = les_atlas(a.repo, ref=a.ref)
        print(helhet_tekst(atlas, a.alt))
        sys.exit(0)

    # RETAIN-INNTAK — append-only koe, aldri automatisk node-oppretting
    if a.innta:
        atlas = les_atlas(a.repo, ref=a.ref)
        fil = a.inntak_fil or str(Path(a.repo) / "data" / "inntak" /
                                  "atlas_fragmenter.jsonl")
        record = skriv_inntak(atlas, a.innta, fil, kilde=a.kilde)
        print(f"FRAGMENT: {a.innta!r}  ->  {record['plasseringsstatus']}")
        print(f"  proveniens: {record['kilde']}")
        print(f"  written to: {fil}")
        if record["plasseringsstatus"] == "uten_hjem":
            print("  koe: uten_hjem — menneskelig vurdering kreves")
        else:
            print("  koe: fragment-forslag — ingen node opprettet")
        sys.exit(0)

    # INNGANGEN — plasser et nytt fragment
    if a.plasser:
        atlas = les_atlas(a.repo, ref=a.ref)
        p_ = plasser(atlas, a.plasser)
        print(f"FRAGMENT: {a.plasser!r}  ->  {p_['status']}")
        print(f"  domenevisshet: {p_.get('domene_visshet', 'ukjent')} "
              f"({p_.get('domene_grunnlag', 'ukjent grunnlag')})")
        for f in p_["forslag"][:4]:
            print(f"  domene {f['domene']:26} {f['kobling']}")
            if f["noder"]:
                print(f"    naboer: {', '.join(f['noder'])}")
        if p_.get("naere_noder"):
            print(f"  naere noder: {', '.join(p_['naere_noder'][:4])}")
        o = p_.get("oppsummering") or {}
        print(f"  maa utfylle {len(p_['mangler'])} felt for aa bli en node: "
              f"{o.get('struktur', 0)} struktur (utledes), "
              f"{o.get('vurdering', 0)} vurdering (foreslaas), "
              f"{o.get('paastand', 0)} paastand (kreves eksplisitt)")
        for k in p_.get("krav", []):
            merke = "SKJEMA" if k["kilde"] == "skjema" else "HUSET "
            if k.get("forslag"):
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"= {k['forslag']!r}  ({k['grunn']})")
            elif k["klasse"] == "struktur":
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"kunne ikke utledes: {k['grunn']}")
            else:
                print(f"    [{merke}] {k['felt']:<17} {k['klasse']:<9} "
                      f"fylt {k['fylt_i_banken']} i banken")
        sys.exit(0)

    # KOBLINGENE — 1-hop, 2-hop, 3-hop
    if a.hop or a.fragment:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.fragment:
            f = fragment(atlas, a.fragment)
            if not f["finnes"]:
                print(f"FEIL: 'fragmentet {a.fragment}' finnes ikke. Nærliggende: "
                      f"{', '.join(f['naere']) or 'ingen'}")
                sys.exit(1)
            print(f"=== {a.fragment} ===")
            print(f"  {f['node'].get('regime', {}).get('name', '?')}")
            print(f"  1-hop {f['ett_hopp']} · 2-hop {f['to_hopp']} · 3-hop {f['tre_hopp']}")
            for type_, ider in f["koblinger"].items():
                vis = ", ".join(ider[:5])
                print(f"  {type_:18} {len(ider):3}  {vis[:66]}")
        else:
            node, _, d = a.hop.partition(":")
            try:
                stier = hop_stier(atlas, node, int(d) if d else 1)
            except KeyError as e:
                print(f"FEIL: {e}")
                sys.exit(1)
            print(f"{len(stier)} noder innen {d or 1} hopp fra {node}:")
            for nid, (sti, typer) in sorted(stier.items(), key=lambda x: len(x[1][0]))[:22]:
                print(f"  {' -> '.join(sti)[:52]:54} [{' -> '.join(typer)}]")
        sys.exit(0)

    # OVERSIKTEN — global tilstand, ikke et soek
    if a.oversikt:
        atlas = les_atlas(a.repo, ref=a.ref)
        o = oversikt(atlas)
        print(f"ATLASET — {len(atlas.get('noder') or [])} noder, "
              f"{len(o)} akser som skiller")
        for sti, ford in o:
            linje = " · ".join(f"{v} ({n})" for v, n in ford[:6])
            print(f"  {sti:26} {linje[:92]}")
        sys.exit(0)

    # AKSENE — generisk rotasjon, ikke tjue flagg
    if a.akser or a.akse:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.akser:
            alle = akser(atlas)
            print(f"{len(alle)} akser i atlaset:")
            for sti, (n, verdier) in sorted(alle.items()):
                v = ", ".join(verdier[:4]) + (" ..." if len(verdier) > 4 else "")
                print(f"  {sti:34} {n:3}  {v[:66]}")
        else:
            navn, _, verdi = a.akse.partition("=")
            try:
                treff = roter_akse(atlas, navn, verdi or None)
                sti, lv = _loes_akse(atlas, navn)
                if lv is not None and not verdi:
                    verdi = lv
            except KeyError as e:
                print(f"FEIL: {e}")
                sys.exit(1)
            print(f"{len(treff)} noder  akse={navn}"
                  + (f"={verdi}" if verdi else "")
                  + (f"  ({sti})" if sti != navn else ""))
            for n in treff:
                v = _les_sti(n, sti)
                print(f"  {n['id']:34} {str(v)[:60]}")
                klarhet = (n.get("maale_paradigme") or {}).get("klarhetsfunksjon")
                if klarhet:
                    print(f"    {klarhet}")
        sys.exit(0)

    # ROTASJON — de fire vinklene som ikke fantes 2026-09-17
    if a.node or a.perspektiv or a.fase or a.domene or a.maaleform or a.proxy:
        atlas = les_atlas(a.repo, ref=a.ref)
        if a.node:
            try:
                treff = roter(atlas, node=a.node)
            except KeyError as e:
                print(f"FEIL: {e}")
                sys.exit(1)
            for n in treff:
                print(f"=== {n['id']} ===")
                for felt, v in n.items():
                    if felt == "id":
                        continue
                    if isinstance(v, (dict, list)):
                        print(f"  {felt}: {json.dumps(v, ensure_ascii=False)[:200]}")
                    else:
                        print(f"  {felt}: {v}")
        elif a.maaleform:
            for form, ider in sorted(maaleformer(atlas).items()):
                print(f"{form:12} ({len(ider)}): {', '.join(ider[:6])}"
                      f"{' ...' if len(ider) > 6 else ''}")
        elif a.proxy:
            kj = proxy_kjeder(atlas)
            print(f"{len(kj)} noder med proxy-kjede:")
            for nid, ledd in sorted(kj.items()):
                print(f"  {nid}: {' -> '.join(ledd)}")
        else:
            treff = roter(atlas, perspektiv=a.perspektiv, fase=a.fase, domene=a.domene)
            print(f"{len(treff)} noder"
                  + (f" perspektiv={a.perspektiv}" if a.perspektiv else "")
                  + (f" fase={a.fase}" if a.fase else "")
                  + (f" domene={a.domene}" if a.domene else ""))
            for n in treff:
                ep = (n.get("episenter") or "")[:56]
                print(f"  {n['id']:34} {n.get('phase','?'):18} {ep}")
        sys.exit(0)

    if a.emne:
        s = finn(a.repo, a.emne, ref=a.ref, hent=a.hent)
        akseinfo = f" via akse {s['akse']}" if s.get("akse") else ""
        print(f"{s['kilde']} @ {s['commit'][:8]} — {s['antall']} treff paa «{s['emne']}»{akseinfo}")
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
            if t["trefftype"] == "navnerom":
                print(f"    grunn: {t['grunn']}")
        if not a.alle and s["antall"] > _VIS_MAKS:
            print(f"  ... og {s['antall'] - _VIS_MAKS} flere — bruk --alle for hele listen")
    else:
        d = les_atlas(a.repo, ref=a.ref, hent=a.hent)
        print(f"{d['kilde']} @ {d['commit'][:8]} — {len(d['noder'])} noder")
