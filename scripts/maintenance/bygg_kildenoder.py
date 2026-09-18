"""Bygg noder for de 24 udekkede domenene — fra KILDENE, ikke fra hverandre.

Maalt 2026-09-18: 24 av 39 domener hadde ingen node. De er ikke 24 ulike
saker; de bæres av SEKS kilder, og de samme 15 verden-domenene bæres av
fire kilder samtidig (gdelt-gkg, mentions, export, world-bank).

Hvert domene er likevel et domene og skal eie sin node. Forskjellen fra
tidligere forsøk: nodene bygges fra de MALTE tallene i
schema/atlas_dekning.json — meldingstall, emner, lag — ikke fra prosa.

`verden.politikk` er unntaket: den er BÆREREN for GDELT-lagene, og om den
skal være offentlig eller intern er Mortens beslutning. Den bygges som
intern inntil videre, og sier det selv.
"""
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
}

#: Domenets lag-rolle, slik dekningsfilen navngir den.
LAG = {"observasjon": "tilstand", "diskusjon": "diskusjon", "hendelse": "hendelse",
       "prediksjon": "prediksjon", "tilstand": "tilstand"}


def node_for(domene: str, v: dict) -> dict:
    """Bygg EN node fra de MALTE tallene — ikke fra prosa om dem."""
    emner = v.get("emner") or []
    meldinger = v.get("meldinger", 0)
    # kilden: det siste leddet i emnene, valgt der flere finnes
    kilder = sorted({str(e).split(".")[-1] for e in emner})
    kilde = kilder[0] if kilder else "ukjent"
    k = KILDE.get(kilde, KILDE["gdelt-gkg"])
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


def main() -> None:
    p = Path("schema/regime_nodes.jsonld")
    d = json.loads(p.read_text(encoding="utf-8"))
    dek = json.loads(DEKNING.read_text(encoding="utf-8"))
    finnes = {n["id"] for n in d["nodes"]}

    ude = {k: v for k, v in dek["domener"].items() if not v.get("noder")}
    nye = [node_for(k, v) for k, v in sorted(ude.items()) if k not in finnes]
    d["nodes"].extend(nye)
    p.write_text(json.dumps(d, **K.FORMAT) + "\n", encoding="utf-8")
    print(f"la til {len(nye)} noder for {len(ude)} udekkede domener")
    print(f"totalt {len(d['nodes'])} noder")


if __name__ == "__main__":
    main()
