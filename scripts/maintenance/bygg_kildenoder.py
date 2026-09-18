"""Bygg noder for de 24 udekkede domenene — fra KILDENE, ikke fra hverandre.

Maalt 2026-09-18: 24 av 39 domener hadde ingen node. De er ikke 24 ulike
saker; de bæres av SEKS kilder, og de samme 15 verden-domenene bæres av
fire kilder samtidig (gdelt-gkg, mentions, export, world-bank).

Hvert domene er likevel et domene og skal eie sin node. Forskjellen fra
tidligere forsøk: nodene bygges fra de MALTE tallene i
schema/atlas_dekning.json — meldingstall, emner, lag — ikke fra prosa.

## Kilden kan ikke gjettes (rettet 2026-09-18)

Oppslaget her hadde en fallback: sto ikke emneleddet i `KILDE`, svarte den
GDELT. Maalt konsekvens: kosmos.interstellart, kosmos.stjerner og
kosmos.romfart sa `measure.measurer = «GDELT-prosjektet»` mens domenene
deres bærer `observasjon.mast-caom` og `launch-library` og NULL
GDELT-meldinger — og påstanden sto i det publiserte atlaset. Se
`kilde_for()`: ukjent kilde er nå en `KildeFeil`, og de tre nodene er
rettet med `--rett`, som beholder feltene mennesker har skrevet.

Kildenoden skriver også `buss_domene`, og `lagdeling.kilde.kilde` er det
ENESTE feltet `tests/test_atlas_kilder.py` leser navnet fra. Et felt ingen
test leser kan bære hva som helst; dette kan ikke.

`verden.politikk` er unntaket: den er BÆREREN for GDELT-lagene, og om den
skal være offentlig eller intern er Mortens beslutning. Den bygges som
intern inntil videre, og sier det selv. MERK: koden under skriver
`offentlig` for alle byggede noder, også denne — docstringen og koden sier
altså to ulike ting, og motsigelsen er navngitt her, ikke avgjort i koden.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import efc_bro_konvensjon as K  # noqa: E402

DEKNING = Path("schema/atlas_dekning.json")

#: Kilden hver udekket domene faktisk leses fra — maalt, ikke gjettet.
KILDE = {
    "gdelt-gkg": {
        "navn": "GDELT GKG",
        "hva": "globale nyhetsstrømmer kodet til tema, aktør og sted",
        "hvem": "GDELT-prosjektet — maskinell koding av verdens nyhetsstrøm",
        "instrument": "GKG-pipelinen; kodede dokumenter per tema",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "nyhetsstrøm -> GKG-koding -> temafordeling -> ny nyhetsstrøm",
        "fractal": "hvert tema er hele korpuset sett gjennom én kode; samme mønster i hver andel",
        "proxy": ["rå nyhetstekst", "GKG-koder (tema, aktør, sted)", "andel per domene"],
    },
    "world-bank": {
        "navn": "World Bank",
        "hva": "tilstandsindikatorer per land og år",
        "hvem": "Verdensbanken — innrapportert statistikk",
        "instrument": "landenes egen innrapportering, harmonisert av banken",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "land rapporterer -> banken harmoniserer -> indikator -> nyttår",
        "fractal": "hvert land er hele datasettet i miniatyr — samme indikatorer, ulik skala",
        "proxy": ["nasjonal statistikk", "harmonisering", "indikatorverdi"],
    },
    "gcn": {
        "navn": "GCN — Gamma-ray Coordinates Network",
        "hva": "varsler om transienter i sanntid, fra bakke og rom",
        "hvem": "observatorier verden over som melder inn til GCN",
        "instrument": "Fermi, Swift og bakkebaserte teleskoper",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "deteksjon -> varsel -> oppfølging -> ny deteksjon",
        "fractal": "hvert varsel er hele nettverket i miniatyr — ett instrument ser, alle leser",
        "proxy": ["fotoner inn", "detektorterskel", "varsel ut"],
    },
    "jpl-horizons": {
        "navn": "JPL Horizons",
        "hva": "baneposisjoner regnet fra DE441-ephemeriden",
        "hvem": "JPL — regnet, ikke målt",
        "instrument": "DE441-ephemeriden; ingen instrument leste av",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "avledet",
        "loop": "bane -> posisjon -> ny posisjon; loopen er deterministisk, ikke målt",
        "fractal": "hvert himmellegeme er hele solsystemet i miniatyr — samme lover, ulik masse",
        "proxy": ["observasjoner (historiske)", "DE441-tilpasning", "posisjon"],
    },
    "who-gho": {
        "navn": "WHO Global Health Observatory",
        "hva": "helseindikatorer per land",
        "hvem": "WHO — innrapportert fra medlemslandene",
        "instrument": "nasjonale helseregistre, harmonisert av WHO",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "land rapporterer -> WHO harmoniserer -> indikator -> neste år",
        "fractal": "hvert land er hele helsebildet i miniatyr — samme indikatorer, ulik dekning",
        "proxy": ["nasjonalt helseregister", "harmonisering", "indikator"],
    },
    "eurostat": {
        "navn": "Eurostat",
        "hva": "arbeidsmarkeds- og sosialstatistikk for Europa",
        "hvem": "Eurostat — fra medlemslandenes statistikkbyråer",
        "instrument": "nasjonale statistikkbyråer, harmonisert",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "land måler -> Eurostat harmoniserer -> indikator -> neste kvartal",
        "fractal": "hvert land er hele arbeidsmarkedet i miniatyr — samme indikatorer, ulik struktur",
        "proxy": ["nasjonal statistikk", "harmonisering", "indikator"],
    },
    # De to leddene under er skrevet inn 2026-09-18, av feilen denne filen
    # feller: kosmos.interstellart, kosmos.stjerner og kosmos.romfart PEKTE
    # paa GDELT fordi oppslaget hadde en fallback. Kilden deres er MAST/CAOM
    # og Launch Library — og de staar her fordi de maa stå ET STED for at en
    # generator skal kunne navngi dem uten aa gjette.
    "mast-caom": {
        "navn": "MAST/CAOM",
        "hva": "arkivobservasjoner — instrumentbårne rådata fra romteleskoper",
        "hvem": "MAST/CAOM — arkivet, ikke teleskopet",
        "instrument": "romteleskopene hvis observasjoner arkiveres; emnet bærer observasjonen, ikke instrumentet",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "deteksjon -> kalibrering -> arkivering -> uttrekk per domene -> ny deteksjon",
        "fractal": "hvert domene er hele arkivet sett gjennom én seleksjon — samme korpus, ulik andel",
        "proxy": ["fotoner inn", "kalibrert og arkivert observasjon", "andel per domene"],
    },
    "launch-library": {
        "navn": "Launch Library",
        "hva": "oppskytingsdata — planlagte, oppskutte og oppgjorte oppskytninger",
        "hvem": "Launch Library — den aggregerte oppskytingskatalogen, ikke oppskytingsaktøren",
        "instrument": "oppskytingsaktørenes egne annonseringer, samlet i én katalog",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "annonsert oppskytning -> oppskytning -> oppgjort utfall -> neste annonsering",
        "fractal": "hver oppskytning er hele manifestet i miniatyr — samme aktører, ulik bane",
        "proxy": ["annonsert manifest", "oppskytingshendelse", "andel per domene"],
    },
}

#: Domenets lag-rolle, slik dekningsfilen navngir den.
LAG = {"observasjon": "tilstand", "diskusjon": "diskusjon", "hendelse": "hendelse",
       "prediksjon": "prediksjon", "tilstand": "tilstand"}

#: Feltene som er skrevet for haand ETTER at noden ble bygget. Rettingen
#: nedenfor rører dem ikke: den erstatter kildens navn i prosaen, ikke
#: menneskets svar. Maalt 2026-09-18: 27 noder bærer disse feltene, og ingen
#: av dem kommer fra `node_for()`.
BEVART: set[tuple[str, ...]] = {
    ("ontology", "proveniens"),
    ("epistemikk", "sosial_mekanisme"),
    ("stipulasjoner", "motor_status"),
    ("stipulasjoner", "alene_status"),
    ("stipulasjoner", "ikke_falsifiserbar_grunn"),
}


class KildeFeil(RuntimeError):
    """Kilden kunne ikke bestemmes. Aldri et gjettet navn."""


def kilde_for(emner: list[str]) -> str:
    """Kildeleddet domenets egne emner bærer — eller en feil, aldri et gjett.

    Emnet har formen `<rot>.<domene>.<lag>.<kilde>`, og det siste leddet ER
    kilden (docs/nats-koblingskart.md, docs/efc-atlas/SYSTEM.md). Maalt
    2026-09-18: oppslaget her hadde en fallback til GDELT, og tre noder —
    kosmos.interstellart, kosmos.stjerner, kosmos.romfart — fikk derfor
    navnet på en kilde de ikke leser, mens domenene deres bærer
    `observasjon.mast-caom` og `launch-library` og null GDELT-meldinger.

    Et svar som alltid finnes, er ikke et svar. Denne funksjonen svarer bare
    når målingen bærer svaret, og sier hva som mangler ellers.
    """
    ledd = sorted({str(e).split(".")[-1] for e in emner})
    if not ledd:
        raise KildeFeil(
            "domenet bærer ingen emner — kilden kan ikke leses fra målingen")
    if len(ledd) > 1:
        raise KildeFeil(
            f"domenet bærer {len(ledd)} kildeledd ({', '.join(ledd)}); én "
            f"node kan bare navngi ÉN kilde. Del domenet opp, eller skriv "
            f"noden for hånd — den skal ikke velge blant dem selv.")
    kilde = ledd[0]
    if kilde not in KILDE:
        raise KildeFeil(
            f"kildeleddet «{kilde}» står ikke i KILDE. Skriv kilden inn med "
            f"hvem som måler, med hvilket instrument og med hvilken "
            f"proxy-kjede — eller la noden stå ubygd. Et gjettet kildenavn er "
            f"en påstand om en kilde noden ikke leser.")
    return kilde


def node_for(domene: str, v: dict) -> dict:
    """Bygg EN node fra de MALTE tallene — ikke fra prosa om dem."""
    emner = v.get("emner") or []
    meldinger = v.get("meldinger", 0)
    # kilden: det siste leddet i emnene — eller en feil, aldri et gjett
    kilde = kilde_for(emner)
    k = KILDE[kilde]
    lag = LAG.get(str(emner[0]).split(".")[0] if emner else "", "tilstand")

    return {
        "id": domene,
        "regime": {
            "name": f"{domene.split('.')[-1]} — {lag}slaget fra {k['navn']}",
            "validity": (
                f"gjelder den delen av {k['navn']} som dekker {domene.split('.')[-1]}. "
                f"Maalt volum: {meldinger} meldinger over {len(emner)} emne(r). "
                f"Re videre: andelen er en LESNING av korpuset, ikke en egen måling."),
        },
        "phase": "instrument",
        "measure": {
            "target": k["hva"],
            "measurer": k["hvem"],
            "instrument": k["instrument"],
            "proxy_chain": k["proxy"],
            "placement": "observasjon",
            "compression": f"alle meldinger om {domene.split('.')[-1]} -> én andel",
        },
        "episenter": (
            f"der korpuset blir en andel for {domene.split('.')[-1]} — "
            f"tallet finnes ikke i kilden, det oppstaar i lesningen"),
        "buffer": {
            "role": f"{k['navn']} er bufferen: den holder tilstanden mellom oppdateringer",
            "note": "kildens, ikke motorens",
        },
        "ontology": {
            "assumes": [
                f"{k['navn']} er tilgjengelig og komplett nok for denne andelen",
                "andelen er sammenlignbar over tid",
                f"emnet {emner[0] if emner else '?'} representerer domenet",
            ],
            "source": f"NATS-stroemmen, emne {domene}.* — maalt i schema/atlas_dekning.json",
        },
        "observer": {
            "bandwidth": f"andelen — bare {domene.split('.')[-1]}, ikke hele korpuset",
            "awareness": "instrument_window",
            "er_del_av_systemet": True,
        },
        "emergence": {"loop": k["loop"], "properties": [f"{meldinger} meldinger"]},
        "fractal": {"pattern": k["fractal"], "note": "ett domene, samme korpus"},
        "coupling": {
            "local": f"hver melding hoerer til {domene.split('.')[-1]} lokalt",
            "global": f"alle 39 domener leser det SAMME korpuset",
            "empathy_note": (
                "at en andel er stoerst betyr ikke at den er viktigst — "
                "den betyr at kodingen traff den oftest"),
        },
        "perspektiv": k["perspektiv"],
        "stipulasjoner": {
            "stipulert_av_oss": False,
            "terskler": ["ingen egne terskler — andelen arves fra kodingen"],
            "motor": "",
        },
        "epistemikk": {
            "sannhetsstatus": k["sannhet"],
            "evidensstatus": k["evidens"],
            "konsensusstatus": k["konsensus"],
            "sosial_mekanisme": (
                f"{k['navn']} — institusjonell kilde. Andelen er vaar LESNING "
                f"av den, ikke kildens egen pastand."),
            "konsensus_er_ikke_sannhet": True,
        },
        "maale_paradigme": {
            "koordinater": ["rom", "tid"],
            "enheter": "andel av korpuset (0-1)",
            "status": "proxy",
            "alternativer": ["kildens egne tall, uten vaar andelslesning"],
        },
        "nivaa": {"indeks": 2, "forelder": None, "tidsskala": "løpende",
                  "lengdeskala": "globalt"},
        "buss_domene": domene,
        "synlighet": "offentlig",
        "lagdeling": {
            "kilde": {"status": k["perspektiv"], "kilde": k["navn"],
                      "sannhet": k["sannhet"], "konsensus": k["konsensus"]},
            "analogi": {"status": "paradigme", "kilde": "vaar andelslesning",
                        "sannhet": "hypotese", "konsensus": "minoritet"},
        },
    }


def rett(gammel: dict, ny: dict, sti: tuple[str, ...] = ()) -> dict:
    """`node_for()` sine verdier over den gamle noden — de skrevne feltene står.

    Rettingen finnes fordi feilen den retter var usynlig i dataene: nodene
    bygget med fallbacken sier GDELT i `measure`, `regime`, `buffer` og
    `lagdeling`, og en omskriving fra bunnen ville slettet det menneskene har
    svart på i mellomtiden (BEVART). Den rører derfor bare det generatoren
    selv eier — kildens navn i prosaen — og lar alt annet stå.
    """
    ut = dict(gammel)
    for nokkel, verdi in ny.items():
        gren = sti + (nokkel,)
        if gren in BEVART and nokkel in gammel:
            continue
        if nokkel in ut and isinstance(ut[nokkel], dict) and isinstance(verdi, dict):
            ut[nokkel] = rett(ut[nokkel], verdi, gren)
        else:
            ut[nokkel] = verdi
    return ut


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--rett", nargs="+", metavar="DOMENE", default=[],
                    help="bygg disse nodene på nytt fra kildene og behold "
                         "feltene som er skrevet for hånd (reparerer noder "
                         "bygget før KildeFeil fantes)")
    a = ap.parse_args()

    p = Path("schema/regime_nodes.jsonld")
    d = json.loads(p.read_text(encoding="utf-8"))
    dek = json.loads(DEKNING.read_text(encoding="utf-8"))

    rettet = 0
    for i, n in enumerate(d["nodes"]):
        if n["id"] not in a.rett:
            continue
        if n["id"] not in dek["domener"]:
            raise KildeFeil(f"«{n['id']}» står ikke i atlas_dekning.json — "
                            f"kilden kan ikke leses fra målingen")
        d["nodes"][i] = rett(n, node_for(n["id"], dek["domener"][n["id"]]))
        rettet += 1

    finnes = {n["id"] for n in d["nodes"]}
    ude = {k: v for k, v in dek["domener"].items() if not v.get("noder")}
    nye = [node_for(k, v) for k, v in sorted(ude.items()) if k not in finnes]
    d["nodes"].extend(nye)
    p.write_text(json.dumps(d, **K.FORMAT) + "\n", encoding="utf-8")
    print(f"la til {len(nye)} noder for {len(ude)} udekkede domener")
    print(f"rettet {rettet} node(r) fra kildene")
    print(f"totalt {len(d['nodes'])} noder")
    return 0


if __name__ == "__main__":
    sys.exit(main())
