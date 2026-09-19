"""efc_atlas_generator — generer atlasets data.mjs FRA regime_nodes.jsonld.

En kilde, to visninger: regime_nodes.jsonld er sannheten; atlaset er
et SPEIL. Ingen dobbelbokfoering — data.mjs bygges alltid herfra, og
en drift mellom banken og atlaset er en feil i denne fila, ikke en
feil i atlaset.

    python3 scripts/maintenance/efc_atlas_generator.py

Kapitlene foelger nivaa-grafens plataa-kjeder: hvert kapittel avsloerer
en kjede av gangen (progressiv avsloering), og det siste viser alt.
"""
from __future__ import annotations

import json
import pathlib

ROT = pathlib.Path(__file__).resolve().parents[2]
ATLAS_DIR = ROT / "docs" / "efc-atlas" / "atlas"
JSONLD = ROT / "schema" / "regime_nodes.jsonld"

#: Koden er nodens KORTE IDENTIFIKATOR (1-2 tegn) — ikke en visuell etikett.
#:
#: Maalt 2026-09-17: tabellen dekket 28 av 82 noder; resten falt tilbake til
#: `nid[:2].upper()`. De 73 offentlige nodene fikk dermed 18 koder — «EF»
#: pekte paa 20 noder, «OB» paa 20 — og 15 av de 28 noeklene navnga noder som
#: ikke finnes (efc.hubble, efc.water, … de heter `*_engine` i banken). Ingen
#: av feilene var synlige, fordi fallbacken svarte i stedet for aa si fra.
#:
#: Koden ER en identifikator, og den brukes som en: `build.mjs` bygger
#: spoersmaal-ID-er av den (`Q-<kode><n>`, og indeksen sier «Reference by
#: ID»), og FLOWS navngir hoppene sine med den (HA, BI, VU, EF). En kode som
#: peker paa tjue noder samtidig identifiserer ingen av dem.
#:
#: Derfor: hver node i banken SKAL staa her, koden skal vaere entydig, og
#: generatoren FEILER heller enn aa gjette (se `manglende_koder`). Brikken
#: som tegner koden er 16 px bred (template.html), derav 1-2 tegn.
#:
#: Koden er stabil: den foelger noden, ikke navnet den hadde i en tidligere
#: tanke. Endres en node-id, skal koden flyttes med — testen
#: `test_deklarasjonen_raatner_ikke` feller etterlatte noekler.
KODER = {
    "kosmos.romfart": "RF",
    "kosmos.gammaglimt": "KG",
    "kosmos.interstellart": "KI",
    "kosmos.maane": "MA",
    "kosmos.noeytrinoer": "NO",
    "kosmos.planetsystem": "PL",
    "kosmos.roentgentransienter": "KR",
    "kosmos.stjerner": "ST",
    "kosmos.uklassifisert": "UK",
    "verden.arbeid": "AR",
    "verden.demografi": "DE",
    "verden.finans": "FI",
    "verden.geopolitikk": "VG",
    "verden.handel": "VH",
    "verden.helse": "HE",
    "verden.infrastruktur": "VI",
    "verden.kommunikasjon": "KO",
    "verden.lov": "LO",
    "verden.militaer": "MI",
    "verden.politikk": "PO",
    "verden.sikkerhet": "SI",
    "verden.teknologi": "TE",
    "verden.transport": "VT",
    "verden.utdanning": "UT",
    "verden.vaer": "VV",
    "opus.dommekraft": "OD",
    "kosmos.asteroider": "KA",
    "efc.efc_background_engine": "EE",
    "efc.lag_s": "LS",
    "efc.lag_d": "LD",
    "efc.lag_c0": "C0",
    # Rot og selv-referanse
    "efc.l0": "L0", "efc.l1": "L1", "efc.l2": "L2", "efc.l3": "L3",
    # Gitteret — publiserte arbeider
    "efc.grid_higgs": "GH", "efc.gr_qft_bro": "GQ",
    "efc.grid_mikrofysikk": "GM", "efc.grid_mikro_engine": "GE",
    "efc.double_slit": "DS", "efc.sort_hull": "SH",
    # Kosmos — motorene paa bussen
    "efc.mu_kz_engine": "MK", "efc.growth_engine": "GR",
    "efc.rotation_engine": "RO", "efc.hubble_engine": "HB",
    "efc.lensing_engine": "LN", "efc.cluster_engine": "CL",
    "efc.transient_engine": "TR", "efc.romvaer_engine": "RV",
    "efc.orbital_engine": "OR", "efc.tidevann_engine": "TI",
    "efc.klima_engine": "KL", "efc.solar_flare_engine": "SF",
    "efc.jordskjelv_engine": "JS",
    # Broer — gap-domenene
    "verden.hav": "HA", "verden.biosfaere": "BI",
    "kosmos.jord.vulkan": "VU",
    # Strukturer — vann og kjemi
    "kjemi.periodesystemet": "PS", "efc.water_phase_engine": "WA",
    "h2o.solid": "SO", "h2o.liquid": "LI", "h2o.gas": "GA",
    "h2o.supercritical": "SC", "h2o.triple_point": "TP",
    "h2o.droplet": "DR", "lys.sol": "LY", "optikk.dispersjon": "OP",
    "regnbue": "RB", "regnbue.observator": "OB",
    # Samfunn — energiflyt
    "efc.enerflyt_engine": "EF", "efc.oekonomi_engine": "OK",
    "efc.samfunn_engine": "SA", "efc.victron_cccv_engine": "VC",
    # Observasjoner — hver med sitt eget maal
    "obs.bao": "BA", "obs.cmb_tt": "TT", "obs.cmb_lensing": "LC",
    "obs.bbn": "BB", "obs.fsigma8": "F8", "obs.s8": "S8",
    "obs.eg": "EG", "obs.isw": "IS", "obs.ksz": "KS",
    "obs.cluster_mass": "CM", "obs.cluster_hmf": "HM", "obs.rar": "RA",
    "obs.bullet": "BU", "obs.satellites": "SL", "obs.jwst_ems": "JW",
    "obs.gw_ct": "GW", "obs.pta_gwb": "PA", "obs.h0_tension": "H0",
    "obs.w0wa": "W0", "obs.cc": "CC",
    # Live stream instruments — each code identifies exactly one node
    "kosmos.galakser_mast": "KM", "verden.klima_gdelt": "GG",
    "verden.klima_worldbank": "WB",
    "verden.miljo_mikrobiom": "MX", "verden.miljo_gdelt": "GY",
    "verden.oekonomi_worldbank": "OX", "verden.oekonomi_imf": "IX",
    "verden.oekonomi_gdelt": "OY",
    "kosmos.romvaer_swpc": "RK", "kosmos.sol_goes": "SG",
    "kosmos.transienter_alerce": "TA",
    "kosmos.kosmologi_desi_bao": "DB", "verden.klima_isbre": "IB",
    # Homo — regime-motoren
    "homo.fluxus": "HF", "homo.homeostase_buffer": "HO",
    "homo.feber_regime": "FE", "homo.aksjonspotensial": "AP",
    "homo.hjerte_syklus": "HJ", "homo.genregulering": "GN",
    "homo.cellesyklus": "CY", "homo.metabolisme": "ME",
    "homo.immunologi": "IM", "homo.sovn_vaaken": "SV",
    "homo.okologi": "OE", "homo.evolusjon": "EV",
    # Interne noder — ikke publisert, men samme navnerom
    "batteri.celle": "BC", "batteri.lading": "BL",
    "batteri.buffer": "BF", "batteri.inverter": "IN",
    "efc.selv.atlas": "AT", "efc.selv.skjema": "SK",
    "efc.selv.paradigme_tid": "PT", "efc.selv.paradigme_masse": "PM",
}

#: Gruppe- og kapittel-tilhoerighet: (gruppe, kapittel).
PLASSERING = {
    "batteri.buffer": ("ghost", 8),
    "batteri.celle": ("ghost", 8),
    "batteri.inverter": ("ghost", 8),
    "batteri.lading": ("ghost", 8),
    "efc.selv.atlas": ("ghost", 8),
    "efc.selv.paradigme_masse": ("ghost", 8),
    "efc.selv.skjema": ("ghost", 8),
    "kosmos.gammaglimt": ("kosmos", 3),
    "kosmos.interstellart": ("kosmos", 3),
    "kosmos.maane": ("kosmos", 3),
    "kosmos.noeytrinoer": ("kosmos", 3),
    "kosmos.planetsystem": ("kosmos", 3),
    "kosmos.roentgentransienter": ("kosmos", 3),
    "kosmos.romfart": ("kosmos", 3),
    "kosmos.stjerner": ("kosmos", 3),
    "kosmos.uklassifisert": ("kosmos", 3),
    "opus.dommekraft": ("ghost", 8),
    "verden.arbeid": ("samfunn", 6),
    "verden.demografi": ("samfunn", 6),
    "verden.finans": ("samfunn", 6),
    "verden.geopolitikk": ("samfunn", 6),
    "verden.handel": ("samfunn", 6),
    "verden.helse": ("samfunn", 6),
    "verden.infrastruktur": ("samfunn", 6),
    "verden.kommunikasjon": ("samfunn", 6),
    "verden.lov": ("samfunn", 6),
    "verden.militaer": ("samfunn", 6),
    "verden.miljo_mikrobiom": ("samfunn", 6),
    "verden.miljo_gdelt": ("samfunn", 6),
    "verden.oekonomi_worldbank": ("samfunn", 6),
    "verden.oekonomi_imf": ("samfunn", 6),
    "verden.oekonomi_gdelt": ("samfunn", 6),
    "verden.politikk": ("samfunn", 6),
    "verden.sikkerhet": ("samfunn", 6),
    "verden.teknologi": ("samfunn", 6),
    "verden.transport": ("samfunn", 6),
    "verden.utdanning": ("samfunn", 6),
    # Ghost er et VALG: disse er maalt aa ikke ha en gruppe ennaa.
    "efc.efc_background_engine": ("ghost", 8),
    "efc.jordskjelv_engine": ("ghost", 8),
    "efc.l1": ("ghost", 8),
    "efc.l2": ("ghost", 8),
    "efc.l3": ("ghost", 8),
    "efc.lag_c0": ("ghost", 8),
    "efc.lag_d": ("ghost", 8),
    "efc.lag_s": ("ghost", 8),
    "efc.solar_flare_engine": ("ghost", 8),
    "h2o.droplet": ("ghost", 8),
    "h2o.gas": ("ghost", 8),
    "h2o.liquid": ("ghost", 8),
    "h2o.solid": ("ghost", 8),
    "h2o.supercritical": ("ghost", 8),
    "h2o.triple_point": ("ghost", 8),
    "homo.aksjonspotensial": ("ghost", 8),
    "homo.cellesyklus": ("ghost", 8),
    "homo.evolusjon": ("ghost", 8),
    "homo.feber_regime": ("ghost", 8),
    "homo.fluxus": ("ghost", 8),
    "homo.genregulering": ("ghost", 8),
    "homo.hjerte_syklus": ("ghost", 8),
    "homo.homeostase_buffer": ("ghost", 8),
    "homo.immunologi": ("ghost", 8),
    "homo.metabolisme": ("ghost", 8),
    "homo.okologi": ("ghost", 8),
    "homo.sovn_vaaken": ("ghost", 8),
    "kosmos.asteroider": ("ghost", 8),
    "lys.sol": ("ghost", 8),
    "obs.bao": ("ghost", 8),
    "obs.bbn": ("ghost", 8),
    "obs.bullet": ("ghost", 8),
    "obs.cc": ("ghost", 8),
    "obs.cluster_hmf": ("ghost", 8),
    "obs.cluster_mass": ("ghost", 8),
    "obs.cmb_lensing": ("ghost", 8),
    "obs.cmb_tt": ("ghost", 8),
    "obs.eg": ("ghost", 8),
    "obs.fsigma8": ("ghost", 8),
    "obs.gw_ct": ("ghost", 8),
    "obs.h0_tension": ("ghost", 8),
    "obs.isw": ("ghost", 8),
    "obs.jwst_ems": ("ghost", 8),
    "obs.ksz": ("ghost", 8),
    "obs.pta_gwb": ("ghost", 8),
    "obs.rar": ("ghost", 8),
    "obs.s8": ("ghost", 8),
    "obs.satellites": ("ghost", 8),
    "obs.w0wa": ("ghost", 8),
    "kosmos.galakser_mast": ("kosmos", 3),
    "verden.klima_gdelt": ("samfunn", 6),
    "verden.klima_worldbank": ("samfunn", 6),
    "kosmos.romvaer_swpc": ("kosmos", 3), "kosmos.sol_goes": ("kosmos", 3),
    "kosmos.transienter_alerce": ("kosmos", 3),
    "kosmos.kosmologi_desi_bao": ("kosmos", 3), "verden.klima_isbre": ("samfunn", 6),
    "optikk.dispersjon": ("ghost", 8),
    "regnbue": ("ghost", 8),
    "regnbue.observator": ("ghost", 8),
    "verden.vaer": ("ghost", 8),
    "efc.l0": ("roots", 1), "efc.selv.paradigme_tid": ("epist", 7),
    "efc.grid_higgs": ("grid", 2), "efc.gr_qft_bro": ("grid", 2),
    "efc.grid_mikrofysikk": ("grid", 2), "efc.grid_mikro_engine": ("grid", 2),
    "efc.double_slit": ("grid", 2), "efc.sort_hull": ("grid", 2),
    "efc.mu_kz_engine": ("kosmos", 3), "efc.growth_engine": ("kosmos", 3),
    "efc.rotation_engine": ("kosmos", 3), "efc.hubble_engine": ("kosmos", 3),
    "efc.lensing_engine": ("kosmos", 3), "efc.cluster_engine": ("kosmos", 3),
    "efc.transient_engine": ("kosmos", 3),
    "efc.romvaer_engine": ("kosmos", 3), "efc.orbital_engine": ("kosmos", 3),
    "efc.tidevann_engine": ("kosmos", 3), "efc.klima_engine": ("kosmos", 3),
    "verden.hav": ("broer", 4), "verden.biosfaere": ("broer", 4),
    "kosmos.jord.vulkan": ("broer", 4),
    "kjemi.periodesystemet": ("struktur", 5),
    "efc.water_phase_engine": ("struktur", 5),
    "efc.victron_cccv_engine": ("struktur", 5),
    "efc.enerflyt_engine": ("samfunn", 6), "efc.oekonomi_engine": ("samfunn", 6),
    "efc.samfunn_engine": ("samfunn", 6),
}

GRUPPER = [
    {"id": "roots", "title": "The roots — time and self"},
    {"id": "grid", "title": "The grid — your published works"},
    {"id": "kosmos", "title": "Cosmos — engines on the bus"},
    {"id": "broer", "title": "Bridges — gap domains, round two"},
    {"id": "struktur", "title": "Structures — H2O and chemistry"},
    {"id": "samfunn", "title": "Society — energy flow"},
    {"id": "epist", "title": "Epistemics"},
    {"id": "ghost", "title": "No group yet"},
]

#: De tre bro-kjedene som dataflyt. Hoppene navngir nodene med KODEN — det
#: er derfor koden maa vaere entydig: «EF» betyr `efc.enerflyt_engine`, og
#: bare den. (At rendereren i atlas/template.html i dag slår opp hoppene i
#: `id`-navnerommet og derfor ikke tegner dem, er en egen feil med egen
#: rotårsak — den hoerer ikke i denne tabellen.)
FLOWS = [
    {"id": "hav", "name": "Ocean state",
     "hops": [["HA", "KL", "temperature proxy",
               {"emne": "verden.klima.tilstand.noaa-tides"}, "xy"]]},
    {"id": "bio", "name": "Biosphere counts",
     "hops": [["BI", "EF", "species counts",
               {"emne": "verden.miljo.tilstand.gbif-planter"}, "xy"]]},
    {"id": "vul", "name": "Volcano state",
     "hops": [["VU", "TR", "activity level",
               {"emne": "kosmos.jord.tilstand.usgs-vulkan"}, "yx"]]},
]


def _kap(navn: str) -> int:
    if navn not in PLASSERING:
        raise SystemExit(
            f"[efc-atlas] `{navn}` staar ikke i PLASSERING — og en fallback "
            f"ville skjult at noen glemte den. Legg den i riktig gruppe, "
            f"eller si eksplisitt at den er ghost.")
    return PLASSERING[navn][1]



#: Why a node has no group. "Ghost" is a CHOICE in PLASSERING: measured to not
#: yet have a group. That is a PLACEMENT fact, not a build status — and the
#: text turned it into "designed and not built", which is untrue for the
#: observations, for the regimes, and for phases that already have an engine.
#: Measured 2026-09-18 on the 53: 20 observations, 18 regime nodes, 5 phases
#: with an engine, 10 others.
def gruppe_grunn(node: dict) -> str:
    """WHY this node has no group. "" when it has one."""
    fase = str(node.get("phase") or "")
    motor = str((node.get("stipulasjoner") or {}).get("motor") or "").strip()
    if fase == "observasjon":
        return "observasjon"
    if "regime" in fase:
        return "regime"
    if motor:
        return "motor"
    return "ovrig"


def uten_gruppe_grunner(noder: list[dict]) -> dict[str, int]:
    """Split the group-less by WHAT is missing — measured, not assumed."""
    tell = {"observasjon": 0, "regime": 0, "har_motor": 0, "ovrige": 0}
    for n in noder:
        if _gruppe(n["id"]) != "ghost":
            continue
        fase = str(n.get("phase") or "")
        motor = str((n.get("stipulasjoner") or {}).get("motor") or "").strip()
        if fase == "observasjon":
            tell["observasjon"] += 1
        elif "regime" in fase:
            tell["regime"] += 1
        elif motor:
            tell["har_motor"] += 1
        else:
            tell["ovrige"] += 1
    return tell


def uten_gruppe_frase(noder: list[dict], spraak: str = "en",
                      anker: str = "of them", med_grunn: bool = True) -> str:
    """The group-less count, and why — derived once, carried by every surface.

    A surface that states how many nodes the atlas has must state this number
    in the same breath: "116 nodes" alone reads as a map fuller than it is.
    Measured 2026-09-19: the count reached the index header and the chapter-9
    lede, and not the one-paragraph lede or the atlas stat strip.

    ONE derivation, and the call site only chooses the connective — several
    wordings with their own numbers would drift apart, and a counter that is
    almost right is worse than none. `med_grunn=False` is the compact form for
    a nowrap stat card, where the split does not fit.
    """
    gr = uten_gruppe_grunner(noder)
    antall = sum(gr.values())
    if spraak == "nb":
        tekst = f"{antall} uten gruppe ennaa"
        if not med_grunn:
            return tekst
        return (f"{tekst} ({gr['observasjon']} observasjoner, {gr['regime']} "
                f"regimenoder, {gr['har_motor']} med motor, {gr['ovrige']} "
                f"ovrige)")
    tekst = f"{antall}{' ' + anker if anker else ''} without a group yet"
    if not med_grunn:
        return tekst
    return (f"{tekst} ({gr['observasjon']} observations, {gr['regime']} regime "
            f"nodes, {gr['har_motor']} with an engine, {gr['ovrige']} other)")


def _gruppe(navn: str) -> str:
    if navn not in PLASSERING:
        raise SystemExit(
            f"[efc-atlas] `{navn}` staar ikke i PLASSERING — se _kapittel().")
    return PLASSERING[navn][0]


def _perspektiv_tekst(p: str | None) -> str:
    return {"akademia": "academia", "konsensus": "consensus",
            "paradigme": "paradigm"}.get(p or "", "agnostic")


#: Tekstgrensene for det atlaset RENDERER. De staar her og ikke spredt som
#: `[:70]` inne i `_node_rad`, fordi testen i `tests/test_atlas_lesbarhet.py`
#: leser dem: en grense som ikke kan leses av en test kan ikke laases.
GRENSER = {"short": 14, "one": 70, "what": 90, "how": 80, "sosial": 120,
           "sakse": 120}


def klipp(tekst: str, grense: int) -> str:
    """Kutt paa ordgrense — og SI at det er kuttet.

    Maalt 2026-09-18 (origin/main f4a3e4f2): `[:70]`, `[:90]` og `[:80]` kuttet
    midt i ord. Det ga atlaset «fase identifisert via P_sat(T) o», «rotation
    engin» og «holder temperaturen under oppvarming . Epistemic». En avkuttet
    streng uten merke ser ut som hele teksten og blir lest som den — samme
    klasse som fallbacken som svarer: svaret finnes, men det svarer ikke paa
    det det ser ut som det svarer paa.

    Kutter paa naermeste ordgrense innenfor grensen og henger paa «…» naar noe
    faktisk ble borte. Ett tegn er billigere enn et svar som lyver om at det er
    komplett.

    Ett tilfelle har ingen ordgrense: naar det FOERSTE ordet alene er lengre enn
    grensen, finnes det ikke noe mellomrom aa kutte paa. Da kuttes tokenet — og
    merkes. Det er den ene tillatte midt-i-ord-kuttingen, og den er bare mulig
    fordi alternativet (aa kutte uten merke) er det funksjonen finnes for aa
    hindre.
    """
    t = " ".join(str(tekst or "").split())
    if len(t) <= grense:
        return t
    if " " not in t[:grense + 1]:
        return t[:grense].rstrip() + "…"
    return t[:grense + 1].rsplit(" ", 1)[0].rstrip(" ,;:—-·") + "…"


def klipp_med_status(tekst: str, grense: int) -> tuple[str, bool]:
    """`klipp()` pluss om noe faktisk ble borte.

    Punktet etter bufferrolla skal ikke staa etter et kuttemerke. Foerste
    utgave gjettet dette ved aa se etter «…» i RESULTATET — og tok da feil for
    en banktekst som selv slutter med «…», og bommet paa en tekst som slutter
    med «...». Kutteren vet svaret; derfor returnerer den det.
    """
    kuttet = len(" ".join(str(tekst or "").split())) > grense
    return klipp(tekst, grense), kuttet


def kode_for(nid: str) -> str:
    """Nodens korte identifikator. Ingen fallback.

    En node uten kode er en feil som skal SEES. Fallbacken
    (`nid[:2].upper()`) gjorde den usynlig i maanedene den sto her: den
    svarte med en kode som saa riktig ut, og 20 noder delte den.
    """
    try:
        return KODER[nid]
    except KeyError:
        raise KeyError(
            f"{nid} har ingen kode. Legg den inn i KODER i "
            f"scripts/maintenance/efc_atlas_generator.py — koden er nodens "
            f"korte identifikator, og spoersmaal-ID-er (Q-<kode><n>) og "
            f"FLOWS-hopp bygges av den.") from None


def manglende_koder(noder: list[dict]) -> list[str]:
    """Noder i banken uten deklarert kode, sortert. Skal vaere tom."""
    return sorted(n["id"] for n in noder if n["id"] not in KODER)


def foreldede_koder(noder: list[dict]) -> list[str]:
    """Koder deklarert for noder som ikke finnes, sortert. Skal vaere tom.

    Fanget ikke seg selv: 15 av de 28 noeklene navnga noder som aldri har
    eksistert under det navnet (`efc.hubble` mot `efc.hubble_engine`), og
    fallbacken svarte i stedet for aa melde fra.
    """
    id_er = {n["id"] for n in noder}
    return sorted(set(KODER) - id_er)


def kollisjoner(noder: list[dict]) -> dict[str, list[str]]:
    """Koder som baeres av mer enn en node: {kode: [node-id, …]}."""
    per: dict[str, list[str]] = {}
    for n in noder:
        if n["id"] in KODER:
            per.setdefault(KODER[n["id"]], []).append(n["id"])
    return {k: sorted(v) for k, v in sorted(per.items()) if len(v) > 1}


def sakse_tekst(node: dict) -> str:
    """S-aksen som lesbar tekst — tom streng naar den ikke er maalt.

    S-aksen (regime, sektor, klarhet, EBE, RCMP) ble skrevet til data.mjs som
    `sAxis`, men ingen av de to byggene leser den noekkelen: node-panelet viser
    `what`/`how`/`cond`, og teksttvillingen likesaa. Rendereren er dessuten en
    READ-ONLY kopi av skillens assets, saa den kan ikke utvides herfra. Laget
    maa derfor uttrykkes i et felt visningene FAKTISK leser — `how` er det
    rette: regimet og maalekjeden er hvordan noden er bygget.

    Rekkefoelgen er maalerekken: regime -> sektor -> klarhet -> EBE -> RCMP.
    """
    mp = node.get("maale_paradigme") or {}
    parter: list[str] = []
    if mp.get("s_regime"):
        parter.append(f"regime {mp['s_regime']}")
    if mp.get("sektor"):
        parter.append(f"sektor {mp['sektor']}")
    if mp.get("klarhetsfunksjon"):
        parter.append(f"klarhet {klipp(mp['klarhetsfunksjon'], GRENSER['sakse'])}")
    if mp.get("ebe_function"):
        parter.append(f"EBE {klipp(mp['ebe_function'], GRENSER['sakse'])}")
    rcmp = node.get("rcmp")
    if isinstance(rcmp, dict) and rcmp:
        felt = [f"{k}={klipp(str(v), GRENSER['sakse'])}"
                for k, v in rcmp.items() if v not in (None, "", [], {})]
        if felt:
            parter.append("RCMP " + "; ".join(felt))
    return " · ".join(parter)


def _node_rad(node: dict, i: int) -> dict:
    nid = node["id"]
    gr = _gruppe(nid)
    kap = _kap(nid)
    navn = nid.split(".")[-1].replace("_", " ")
    ep = node.get("epistemikk", {})
    maal = node.get("measure", {})
    buf = node.get("buffer", {})
    # Spoersmaalene her er ikke skrevet av generatoren.
    #
    # Maalt 2026-09-18: for hver node uten evidens la generatoren inn linjen
    # «no evidence yet — hypothesis marked honestly». Den var IDENTISK for alle
    # sju, den spurte ikke om noe, og den gjentok `how` («Epistemic: … ingen»)
    # inne i spoersmaalsfanen. «7 open · 0 resolved» var dermed ett og samme
    # ord sju ganger — fallbacken som svarer, i spoersmaalsfanen.
    #
    # Evidensstatusen staar der den er maalt: i `how`. Et ekte aapent
    # spoersmaal maa komme FRA BANKEN (et felt paa noden), aldri fra
    # generatorens penn — en generator som dikter spoersmaal lager arbeidsko
    # av sin egen mal.
    cond = []
    # Et EKTE aapent spoersmaal kommer fra banken — feltet `open_questions` paa
    # noden. Generatoren skriver aldri et spoersmaal selv (se `cond = []` over).
    for spm in node.get("open_questions") or []:
        if isinstance(spm, str) and spm.strip():
            cond.append(spm.strip())
        elif isinstance(spm, dict) and str(spm.get("q", "")).strip():
            cond.append({k: v for k, v in spm.items()
                         if k in ("q", "r", "to") and str(v).strip()})
    if node.get("stipulasjoner", {}).get("motor") in (None, "", "KANDIDAT "
        "(broen venter paa konnektor-deploy)"):
        pass
    motor = node.get("stipulasjoner", {}).get("motor", "")
    if motor and motor.startswith("KANDIDAT"):
        cond.append({"q": f"{nid}: motor waits for connector deploy",
                     "to": "connector deploy (human step)"})
    # One-lineren er det foerste brukeren leser naar de hover-er over en node.
    # Den skal svare paa HVA tingen er. Foer aapnet den med perspektivet, og da
    # begynte ALLE 116 nodene med samme ord («Perspective: …»): en mal som sier
    # hvem som mener det, ikke hva det er — og som dyttet substansen bakerst,
    # der `[:70]` kuttet den. Perspektivet er ikke borte: det staar i `steps`
    # og som kort merke til slutt.
    substans = klipp(maal.get("target", ""), GRENSER["one"])
    perspektiv = _perspektiv_tekst(node.get("perspektiv"))
    # `role` kan mangle, vaere None eller tom. Foer ga None/"" en tom tekst, og
    # linja ble «Buffer role: . Epistemic: …»; «—» sier at feltet ikke er
    # utfylt, som er sant.
    bufferrolle, bufferrolle_kuttet = klipp_med_status(
        buf.get("role") or "—", GRENSER["how"])
    # Et kutt slutter paa «…». Da skal malens eget punktum ikke etter, ellers
    # staar det «… tolkning…. Epistemic» — et kuttemerke og et punktum som
    # begge proever aa avslutte samme setning. Punktet leses fra kuttets
    # STATUS, ikke fra et tegn i resultatet: en banktekst kan selv slutte med
    # «…», og da ville tegnet loyet.
    punktum = "" if bufferrolle_kuttet else "."
    # S-aksen maa staa i `how` for aa bli SETT: det er feltet begge byggene
    # viser. Den settes bare inn naar den er maalt — 96 identiske «ikke maalt»
    # ville vaert samme mal som spoersmaalsfanen nettopp ble ryddet for.
    # Tomrommet meldes i stedet EN gang, som tall i META.stats.
    sakse = sakse_tekst(node)
    return {
        "id": nid.replace(".", "-").replace("_", "-")[:40],
        "code": kode_for(nid),
        "name": nid,
        "short": klipp(navn, GRENSER["short"]),
        "group": gr,
        "gx": 1.5 + (i % 6) * 2.4,
        "gy": -1 + (i // 6) * 2.6,
        "w": 2, "d": 2, "h": 34,
        "kind": "tall" if node.get("phase") == "motor" else "box",
        "ghost": gr == "ghost",
        "one": (f"{substans} · perspektiv: {perspektiv}" if substans
                else f"perspektiv: {perspektiv}"),
        # `what` er to merkede deler — instrumentet OG proxy-kjeden — ikke ett
        # felt. Grensen gjelder hver del, saa hele feltet kan bli lengre enn
        # GRENSER["what"]. Det er tilsiktet: en felles grense ville kuttet
        # instrumentet for aa faa plass til kjeden.
        "what": f"{klipp(maal.get('instrument', ''), GRENSER['what'])} — "
                f"proxy chain: "
                f"{klipp(' -> '.join(maal.get('proxy_chain', [''])), GRENSER['what'])}",
        "how": f"Buffer role: {bufferrolle}{punktum} "
               f"Epistemic: {ep.get('sannhetsstatus', '—')} / "
               f"{ep.get('evidensstatus', '—')} / "
               f"{ep.get('konsensusstatus', '—')}."
               # S-aksen slutter ofte med punktum selv (RCMP-deklarasjonen
               # gjorde det: «… gyldighetsdomene.». Derfor settes hale-punktumet
               # bare naar teksten ikke allerede avslutter seg.
               + (f" S-axis: {sakse}"
                  f"{'' if sakse.endswith(('.', '…')) else '.'}" if sakse else ""),
        "sAxis": {
            "regime": node.get("maale_paradigme", {}).get("s_regime"),
            "sector": node.get("maale_paradigme", {}).get("sektor"),
            "ebe": node.get("maale_paradigme", {}).get("ebe_function"),
            # `klarhetsfunksjon` var utfylt paa like mange noder som s_regime
            # (19 av 126, maalt 2026-09-18) og ble IKKE lest av generatoren:
            # S-aksen saa tommere ut i atlaset enn den er i banken.
            "klarhet": node.get("maale_paradigme", {}).get("klarhetsfunksjon"),
            "rcmp": node.get("rcmp"),
        },
        "steps": [["Perspective", perspektiv],
                  ["Epistemics",
                   f"{ep.get('sannhetsstatus', '—')} / "
                   f"{ep.get('evidensstatus', '—')} / "
                   f"{ep.get('konsensusstatus', '—')}"],
                  ["Social mechanism",
                   klipp(ep.get("sosial_mekanisme", "—"), GRENSER["sosial"])]],
        "cond": cond,
    }


def _indeks(noder: list[dict], rader: list[dict]) -> str:
    grupper = {r["group"]: [] for r in rader}
    for rad, node in zip(rader, noder):
        grupper[rad["group"]].append((rad, node))
    titler = {"roots": "Roots", "grid": "The grid", "kosmos": "Cosmos",
              "broer": "Bridges", "struktur": "Structures",
              "samfunn": "Society", "epist": "Epistemics",
              "ghost": "No group yet"}
    evidens = sum((node.get("epistemikk") or {}).get("evidensstatus") == "ingen"
                  for node in noder)
    spoersmaal = sum(len(node.get("open_questions") or []) for node in noder)
    lines = ["# Atlasindeks", "",
             (f"> {len(noder)} publiserte noder · "
              f"{uten_gruppe_frase(noder, 'nb')} · "
              f"{evidens} mangler evidens · {spoersmaal} aapne spoersmaal"), "",
             "Hver rad er generert fra samme bank som atlaset.", ""]
    for gruppe in ("roots", "grid", "kosmos", "broer", "struktur", "samfunn",
                   "epist", "ghost"):
        if not grupper.get(gruppe):
            continue
        lines.append(f"## {titler[gruppe]}")
        for rad, node in grupper[gruppe]:
            st = sakse_tekst(node) or "ikke maalt"
            stip = node.get("stipulasjoner") or {}
            motor = stip.get("motor") or "ikke oppgitt"
            buss = stip.get("buss_status") or "ikke oppgitt"
            spm = len(node.get("open_questions") or [])
            perspektiv = _perspektiv_tekst(node.get("perspektiv"))
            # Linja er en LESEFLAte, ikke en dump. Foerste utgave ga ni kolonner
            # uten navn — blant dem «1 · nei» — og perspektivet sto BAAE som
            # avkuttet hale av one-lineren og som egen kolonne. Et tall uten
            # etikett er en gaate, ikke en opplysning; den som skanner skal
            # kunne lese raden uten aa sla opp hva kolonnene betyr.
            substans = rad["one"].split(" · perspektiv:")[0].strip()
            lines.append(f"- **{rad['code']} · {node['id']}**"
                         + (f" — {klipp(substans, 90)}" if substans else ""))
            lines.append("  " + " · ".join([
                f"perspektiv={perspektiv}",
                f"motor={motor}",
                f"buss={klipp(str(buss), 40)}",
                f"S-akse={klipp(st, 60)}",
                f"spoersmaal={spm}",
                (f"gruppe=ingen ({gruppe_grunn(node)})" if rad["ghost"]
                 else "gruppe=ja"),
            ]))
        lines.append("")
    lines.append("## Uten gruppe ennaa")
    lines.append("")
    for rad, node in (item for item in sum(grupper.values(), []) if item[0]["ghost"]):
        lines.append(f"- {node['id']} — {klipp(node.get('navn') or node['id'], 100)}")
    lines.append("")
    return "\n".join(line.rstrip() for line in lines) + "\n"


def hoved() -> int:
    atlas = json.load(open(JSONLD, encoding="utf-8"))
    alle = atlas["nodes"]

    # Kode-preflight. Denne staar FOER noe skrives, og den FEILER — den
    # gjetter ikke. Rekkefoelgen er poenget: et atlas som bygges med en
    # kode som peker paa tjue noder, er verre enn et atlas som ikke
    # bygges, fordi det foerste ser ferdig ut.
    mangler = manglende_koder(alle)
    if mangler:
        print(f"FEIL: {len(mangler)} node(r) i banken mangler kode i KODER:")
        for m in mangler:
            print(f"  {m}")
        print("Koden er nodens korte identifikator (Q-ID-er og FLOWS-hopp "
              "bygges av den). Legg den inn i KODER i denne fila.")
        return 1
    doede = foreldede_koder(alle)
    if doede:
        print(f"FEIL: {len(doede)} kode(r) er deklarert for noder som ikke "
              f"finnes:")
        for d in doede:
            print(f"  {d} -> {KODER[d]}")
        print("Tabellen har raatnet (en node-id er endret uten at koden "
              "flyttet med). Rett noekkelen.")
        return 1
    koll = kollisjoner(alle)
    if koll:
        print(f"FEIL: {len(koll)} kode(r) baeres av flere noder:")
        for k, ids in koll.items():
            print(f"  {k}: {', '.join(ids)}")
        print("En kode som peker paa flere noder identifiserer ingen av "
              "dem. Velg en entydig kode per node.")
        return 1
    print(f"koder: {len(KODER)} entydige for {len(alle)} noder")

    # Bare offentlige noder gaar til GitHub Pages. Filteret er DEKLARERT per
    # node (`synlighet`), ikke en skjult regel her — en node som forsvinner
    # uten at noen ser hvorfor er samme feilklasse som resten av huset
    # finnes for aa hindre. Interne noder er ikke slettet: de lever videre
    # i det komplette atlaset, og telles eksplisitt i utskriften saa
    # tilbakeholdelsen er synlig.
    noder = [n for n in alle if n.get("synlighet") == "offentlig"]
    interne = [n["id"] for n in alle if n.get("synlighet") != "offentlig"]
    print(f"nodes: {len(noder)} offentlige av {len(alle)}")
    if interne:
        print(f"  holdt tilbake ({len(interne)}): {', '.join(sorted(interne))}")

    # Tallene under er DYNAMISKE med vilje. De stod hardkodet som «82 nodes,
    # 79 relations» og «82 nodes, 18 engines», og ble dermed staaende og
    # lyve i det offentlige kartet i det oyeblikket filteret tok virkning —
    # 73 noder publisert, 82 paastatt. Det røpet i tillegg at noe var holdt
    # tilbake, som er noeyaktig det filteret skal skjule.
    offentlige_id = {n["id"] for n in noder}
    relasjoner = [r for r in atlas.get("relations", [])
                  if r.get("subject") in offentlige_id
                  and r.get("object") in offentlige_id]
    motorer = sum(1 for n in noder if "_engine" in str(n.get("id", "")))

    rader = [_node_rad(n, i) for i, n in enumerate(noder)]
    # Ghost-noder: de uten PLASSERING og med epistemikk «ingen»
    for r in rader:
        nid = r["name"]
        if nid not in PLASSERING:
            r["group"] = "ghost"
            r["ghost"] = True

    # Kapitler: 1-8 + hele-systemet (9)
    kap = {i: [] for i in range(1, 9)}
    for r in rader:
        k = _kap(r["name"])
        kap.setdefault(k, []).append(r["id"])

    ch = []
    TITLER = {
        1: "Roots — time and self",
        2: "The grid — your published works",
        3: "Cosmos — engines on the bus",
        4: "Bridges — gap domains",
        5: "Structures — H2O and chemistry",
        6: "Society — energy flow",
        7: "Epistemics",
        8: "No group yet",
    }
    for k in sorted(kap):
        if k == 8 and not kap[k]:
            continue
        ch.append({
            "id": f"ch{k}",
            "title": TITLER[k],
            "reveal": kap[k],
            "lede": f"Chapter {k} of 9 — a few structures at a time.",
            "story": "<p>Revealed: " + ", ".join(sorted(kap[k])) + ".</p>",
            "flow": None,
        })
    # Chapter 9 is where someone sees the WHOLE atlas. It must say what the
    # atlas is made of — not just how many boxes there are. Measured 2026-09-18:
    # 116 published nodes, of which 53 have no group yet, and 7 carry no
    # evidence. The split says WHY a node has no group: an observation is not
    # an unbuilt thing, and a node with an engine is not unbuilt either.
    # Both numbers are DERIVED here, never written by hand.
    uten_evidens = sum(1 for n in noder
                       if (n.get("epistemikk") or {}).get("evidensstatus")
                       == "ingen")
    ch.append({
        "id": "all", "title": "The whole atlas",
        "reveal": [], "lede": f"Everything at once — {len(noder)} nodes, "
                              f"{uten_gruppe_frase(noder, 'en', 'of them')}, "
                              f"{len(relasjoner)} relations.",
        "story": "<p>Free exploration. Hover, click to pin, go inside.</p>"
                 f"<p>{uten_evidens} nodes carry no evidence yet — that is what "
                 f"<i>epistemic: … / ingen / …</i> in “How it's built” says. "
                 f"Open questions are not generated: they come from the bank, "
                 f"and none is registered.</p>",
        "flow": None,
    })

    # FLOWS: de tre bro-kjedene som dataflyt (tabellen staar oeverst i fila)
    flows = FLOWS

    # S-aksen maalt paa N av M noder. Tallet staar EN gang, i headeren: et tomt
    # felt og et felt som ikke finnes er to ulike svar, og bare ett av dem er et
    # hull. En linje per node («ikke maalt») ville derimot vaert den samme malen
    # som spoersmaalsfanen nettopp ble ryddet for.
    sakse_maalt = sum(1 for n in noder if sakse_tekst(n))

    indeks = _indeks(noder, rader)
    (ATLAS_DIR.parent / "INDEKS.md").write_text(indeks, encoding="utf-8")

    # The two remaining surfaces that count nodes: the one-paragraph lede and
    # the atlas stat strip. Both carry the group-less count from the SAME
    # derivation as the index header and the chapter-9 lede — the strip uses
    # the compact form because a stat card is nowrap and the split does not fit.
    uten_gruppe_en = uten_gruppe_frase(noder, "en", "of them")
    uten_gruppe_egne = uten_gruppe_frase(noder, "en", f"of the {len(noder)}")
    uten_gruppe_kort = uten_gruppe_frase(noder, "en", "", med_grunn=False)

    data = f"""// GENERERT av scripts/maintenance/efc_atlas_generator.py —
// IKKE rediger for haand. Kilden er schema/regime_nodes.jsonld.
export const META = {{
  title: 'EFC',
  artifactUrl: '',
  sourcePath: 'schema/regime_nodes.jsonld',
  buildCmd: 'node docs/efc-atlas/atlas/build.mjs',
  stats: [{{ k: 'Nodes', v: '{len(noder)} · {uten_gruppe_kort}' }},
          {{ k: 'S-axis', v: '{sakse_maalt} of {len(noder)} measured · {uten_gruppe_kort}' }},
          {{ k: 'Perspectives', v: 'paradigm / consensus / academia' }}],
  intro: `_**One source, two views.** This atlas is generated from regime_nodes.jsonld — the bank is the truth; the atlas is its mirror._`,
  onePara: `Energy-Flow Cosmology: an entropic, structural atlas of the universe — from grid microphysics to society's energy flow. {len(noder)} nodes, {motorer} engine nodes, NATS bridges. {uten_gruppe_egne}.`,
  platformGives: 'NATS bus, engines, review fan-out, the EFC bank.',
  weOwn: 'The atlas itself — every node, every epistemic declaration, every threshold.',
  costModel: [],
  filesystem: `schema/regime_nodes.jsonld\\n  efc_inference/engine/*.py\\n  efc_inference/bridge/*.py`,
}};

export const DECISIONS = [
  {{ axis: 'Epistemics', decision: 'truth, evidence and consensus are three separate axes — consensus is never truth (const true).', adr: 'schema/regime_node.schema.json' }},
  {{ axis: 'Levels', decision: 'a parent must have a lower index than its child; no cycles.', adr: 'tests/test_epistemikk_v6.py' }},
  {{ axis: 'Analogy', decision: 'every analogy carries both an avbildning and a bryter_der — without the disanalogy it does not harden.', adr: 'schema/regime_node.schema.json' }},
  {{ axis: 'Sources', decision: 'a finding belongs to the bank it came from — not where I sat when I found it.', adr: 'SOUL.md' }},
];

export const GROUPS = {json.dumps(GRUPPER, indent=2)};

export const NODES = {json.dumps(rader, indent=2)};

export const FLOWS = {json.dumps(flows, indent=2)};

export const CH = {json.dumps(ch, indent=2)};

export const HOW_HTML = `<div class="eyebrow">EFC · generated</div><h1 class="t">How it's built</h1><div class="sub">one source, two views</div>
<h3 class="sec">Source</h3><pre>schema/regime_nodes.jsonld — the atlas bank</pre>
<h3 class="sec">Generator</h3><pre>scripts/maintenance/efc_atlas_generator.py</pre>`;
"""
    # Trailing whitespace bryter git diff --check — stripp hver linje
    data = "\n".join(linje.rstrip() for linje in data.splitlines()) + "\n"
    (ATLAS_DIR / "data.mjs").write_text(data, encoding="utf-8")
    print("data.mjs written:", len(data), "bytes")

    # Bygg begge visningene og stripp whitespace fra build-outputen
    # (build.mjs skriver tomme linjer med mellomrom i SYSTEM.md).
    import subprocess as _sp
    r = _sp.run(["node", "build.mjs"], capture_output=True, text=True,
                cwd=ATLAS_DIR, timeout=120)
    if r.returncode != 0:
        print(r.stderr[-600:])
        return 1
    for navn in ("SYSTEM.md", "atlas.html"):
        p = ATLAS_DIR.parent / navn
        tekst = p.read_text(encoding="utf-8")
        p.write_text("\n".join(l.rstrip() for l in
                                tekst.splitlines()) + "\n",
                     encoding="utf-8")
    print(r.stdout.strip()[-120:] or "built")
    return 0


if __name__ == "__main__":
    raise SystemExit(hoved())
