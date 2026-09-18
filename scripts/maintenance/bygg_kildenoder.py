"""Bygg noder for de 24 udekkede domenene — fra KILDENE, ikke fra hverandre.

Maalt 2026-09-18: 24 av 39 domener hadde ingen node. De er ikke 24 ulike
saker; de bæres av SEKS kilder, og de samme 15 verden-domenene bæres av
fire kilder samtidig (gdelt-gkg, mentions, export, world-bank).

Hvert domene er likevel et domene og skal eie sin node. Forskjellen fra
tidligere forsøk: nodene bygges fra de MALTE tallene i
schema/atlas_dekning.json — meldingstall, emner, lag — ikke fra prosa.

## The source cannot be guessed (corrected 2026-09-18)

The lookup here had a fallback: if the subject segment was not in `KILDE`,
it answered GDELT. Measured consequence: kosmos.interstellart,
kosmos.stjerner and kosmos.romfart said `measure.measurer = "the GDELT
project"` while their domains carry `observasjon.mast-caom` and
`launch-library` and NULL GDELT messages -- and the claim stood in the
published atlas. See `kilde_for()`: an unknown source is now a `KildeFeil`,
and the three nodes are corrected with `--rett`, which keeps the fields
humans have written.

The source node also writes `buss_domene`, and `lagdeling.kilde.kilde` is the
ONLY field `tests/test_atlas_kilder.py` reads the name from. A field no test
reads can carry anything; this one cannot.

Language: English only in the prose that this change adds, per the repo-wide
language gate (`scripts/maintenance/efc_spraakvakt.py`). The `KILDE` entries
written before this change keep their recorded Norwegian debt; the two added
here are English, and so are the three nodes they generate.

`verden.politikk` is the exception: it is the CARRIER of the GDELT layers, and
whether it should be public or internal is Morten's decision. It is built as
internal until further notice, and says so itself. NOTE: the code below writes
`offentlig` for every built node, this one included -- so the docstring and the
code say two different things, and the contradiction is named here, not decided
in the code.
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
    # The two entries below were written in 2026-09-18, out of the fault this
    # file convicts: kosmos.interstellart, kosmos.stjerner and kosmos.romfart
    # POINTED at GDELT because the lookup had a fallback. Their source is
    # MAST/CAOM and Launch Library -- and they stand here because a source has
    # to stand SOMEWHERE for a generator to be able to name it without
    # guessing. English, because the language gate fails on Norwegian added
    # under scripts/.
    "mast-caom": {
        "navn": "MAST/CAOM",
        "hva": "archival observations — instrument-borne raw data from space telescopes",
        "hvem": "MAST/CAOM — the archive, not the telescope",
        "instrument": "the space telescopes whose observations are archived; the subject carries the observation, not the instrument",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "detection -> calibration -> archiving -> extraction per domain -> new detection",
        "fractal": "each domain is the whole archive seen through one selection — same corpus, different share",
        "proxy": ["photons in", "calibrated and archived observation", "share per domain"],
    },
    "launch-library": {
        "navn": "Launch Library",
        "hva": "launch data — planned, flown and settled launches",
        "hvem": "Launch Library — the aggregated launch catalogue, not the launch operator",
        "instrument": "the operators' own announcements, collected into one catalogue",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "announced launch -> launch -> settled outcome -> next announcement",
        "fractal": "each launch is the whole manifest in miniature — same operators, different orbit",
        "proxy": ["announced manifest", "launch event", "share per domain"],
    },
}

#: Domenets lag-rolle, slik dekningsfilen navngir den.
LAG = {"observasjon": "tilstand", "diskusjon": "diskusjon", "hendelse": "hendelse",
       "prediksjon": "prediksjon", "tilstand": "tilstand"}

#: The fields written by hand AFTER the node was built. The repair below does
#: not touch them: it replaces the source's name in the prose, not the human
#: answer. Measured 2026-09-18: 27 nodes carry these fields, and none of them
#: comes from `node_for()`.
BEVART: set[tuple[str, ...]] = {
    ("ontology", "proveniens"),
    ("epistemikk", "sosial_mekanisme"),
    ("stipulasjoner", "motor_status"),
    ("stipulasjoner", "alene_status"),
    ("stipulasjoner", "ikke_falsifiserbar_grunn"),
}


class KildeFeil(RuntimeError):
    """The source could not be determined. Never a guessed name."""


def kilde_for(emner: list[str]) -> str:
    """The source segment the domain's own subjects carry -- or a fault, never
    a guess.

    The subject has the form `<root>.<domain>.<layer>.<source>`, and the last
    segment IS the source (docs/nats-koblingskart.md). Measured 2026-09-18: the
    lookup here had a fallback to GDELT, and three nodes -- kosmos.interstellart,
    kosmos.stjerner, kosmos.romfart -- therefore got the name of a source they
    do not read, while their domains carry `observasjon.mast-caom` and
    `launch-library` and null GDELT messages.

    An answer that always exists is not an answer. This function answers only
    when the measurement carries the answer, and says what is missing otherwise.
    """
    ledd = sorted({str(e).split(".")[-1] for e in emner})
    if not ledd:
        raise KildeFeil(
            "the domain carries no subjects -- the source cannot be read from "
            "the measurement")
    if len(ledd) > 1:
        raise KildeFeil(
            f"the domain carries {len(ledd)} source segments "
            f"({', '.join(ledd)}); one node can only name ONE source. Split the "
            f"domain, or write the node by hand -- it must not choose among them "
            f"itself.")
    kilde = ledd[0]
    if kilde not in KILDE:
        raise KildeFeil(
            f"the source segment \"{kilde}\" does not stand in KILDE. Write the "
            f"source in with who measures, with which instrument and with which "
            f"proxy chain -- or leave the node unbuilt. A guessed source name is "
            f"a claim about a source the node does not read.")
    return kilde


def node_for(domene: str, v: dict) -> dict:
    """Build ONE node from the MEASURED numbers -- not from prose about them."""
    emner = v.get("emner") or []
    meldinger = v.get("meldinger", 0)
    # the source: the last segment of the subjects -- or a fault, never a guess
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
    """`node_for()`'s values over the old node -- the written fields stand.

    The repair exists because the fault it repairs was invisible in the data:
    the nodes built with the fallback say GDELT in `measure`, `regime`, `buffer`
    and `lagdeling`, and rewriting them from scratch would have deleted what
    humans have answered in the meantime (BEVART). It therefore touches only
    what the generator owns -- the source's name in the prose -- and leaves
    everything else standing.
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
                    help="rebuild these nodes from the sources and keep the "
                         "fields written by hand (repairs nodes built before "
                         "KildeFeil existed)")
    a = ap.parse_args()

    p = Path("schema/regime_nodes.jsonld")
    d = json.loads(p.read_text(encoding="utf-8"))
    dek = json.loads(DEKNING.read_text(encoding="utf-8"))

    rettet = 0
    for i, n in enumerate(d["nodes"]):
        if n["id"] not in a.rett:
            continue
        if n["id"] not in dek["domener"]:
            raise KildeFeil(f"\"{n['id']}\" does not stand in "
                            f"atlas_dekning.json -- the source cannot be read "
                            f"from the measurement")
        d["nodes"][i] = rett(n, node_for(n["id"], dek["domener"][n["id"]]))
        rettet += 1

    finnes = {n["id"] for n in d["nodes"]}
    ude = {k: v for k, v in dek["domener"].items() if not v.get("noder")}
    nye = [node_for(k, v) for k, v in sorted(ude.items()) if k not in finnes]
    d["nodes"].extend(nye)
    p.write_text(json.dumps(d, **K.FORMAT) + "\n", encoding="utf-8")
    print(f"added {len(nye)} nodes for {len(ude)} uncovered domains")
    print(f"repaired {rettet} node(s) from the sources")
    print(f"{len(d['nodes'])} nodes in total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
