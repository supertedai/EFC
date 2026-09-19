"""Build nodes for the 24 uncovered domains — from the SOURCES, not from each other.

Measured 2026-09-18: 24 of 39 domains had no node. They are not 24 different
cases; they are carried by SIX sources, and the same 15 verden domains are
carried by four sources at once (gdelt-gkg, mentions, export, world-bank).

Each domain is nevertheless a domain and shall own its node. The difference
from earlier attempts: the nodes are built from the MEASURED numbers in
schema/atlas_dekning.json — message counts, topics, layers — not from prose.

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

Language: English only, per the repo-wide language gate
(`scripts/maintenance/efc_spraakvakt.py`). The `KILDE` entries and the
`node_for()` templates are English too (t_648190ca): the recorded Norwegian debt
in this file was the generator that writes the nodes, so leaving it would have
written Norwegian back into the bank on the next run.

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

#: The source each uncovered domain is actually read from — measured, not guessed.
KILDE = {
    "gdelt-gkg": {
        "navn": "GDELT GKG",
        "hva": "global news streams coded to topic, actor and place",
        "hvem": "the GDELT project — machine coding of the world's news stream",
        "instrument": "the GKG pipeline; coded documents per topic",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "news stream -> GKG coding -> topic distribution -> new news stream",
        "fractal": "each topic is the whole corpus seen through one code; the same pattern in every share",
        "proxy": ["raw news text", "GKG codes (topic, actor, place)", "share per domain"],
    },
    "world-bank": {
        "navn": "World Bank",
        "hva": "state indicators per country and year",
        "hvem": "the World Bank — reported statistics",
        "instrument": "the countries' own reporting, harmonised by the bank",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "countries report -> the bank harmonises -> indicator -> new year",
        "fractal": "each country is the whole dataset in miniature — the same indicators, a different scale",
        "proxy": ["national statistics", "harmonisation", "indicator value"],
    },
    "gcn": {
        "navn": "GCN — Gamma-ray Coordinates Network",
        "hva": "alerts on transients in real time, from ground and space",
        "hvem": "observatories worldwide that report to GCN",
        "instrument": "Fermi, Swift and ground-based telescopes",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "detection -> alert -> follow-up -> new detection",
        "fractal": "each alert is the whole network in miniature — one instrument sees, everyone reads",
        "proxy": ["photons in", "detector threshold", "alert out"],
    },
    "jpl-horizons": {
        "navn": "JPL Horizons",
        "hva": "orbit positions computed from the DE441 ephemeris",
        "hvem": "JPL — computed, not measured",
        "instrument": "the DE441 ephemeris; no instrument read it off",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "avledet",
        "loop": "orbit -> position -> new position; the loop is deterministic, not measured",
        "fractal": "every celestial body is the whole solar system in miniature — the same laws, a different mass",
        "proxy": ["observations (historical)", "DE441 fit", "position"],
    },
    "who-gho": {
        "navn": "WHO Global Health Observatory",
        "hva": "health indicators per country",
        "hvem": "WHO — reported by the member states",
        "instrument": "national health registries, harmonised by WHO",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "countries report -> WHO harmonises -> indicator -> next year",
        "fractal": "each country is the whole health picture in miniature — the same indicators, a different coverage",
        "proxy": ["national health registry", "harmonisation", "indicator"],
    },
    "eurostat": {
        "navn": "Eurostat",
        "hva": "labour market and social statistics for Europe",
        "hvem": "Eurostat — from the member states' statistical agencies",
        "instrument": "national statistical agencies, harmonised",
        "perspektiv": "konsensus",
        "sannhet": "stottet",
        "konsensus": "institusjonell",
        "evidens": "direkte",
        "loop": "countries measure -> Eurostat harmonises -> indicator -> next quarter",
        "fractal": "each country is the whole labour market in miniature — the same indicators, a different structure",
        "proxy": ["national statistics", "harmonisation", "indicator"],
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

#: The domain's layer role, as the coverage file names it. The KEYS are the
#: bus domain prefixes (`observasjon.gdelt-gkg`) — data, not prose.
LAG = {"observasjon": "state", "diskusjon": "discussion", "hendelse": "event",
       "prediksjon": "prediction", "tilstand": "state"}

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
    lag = LAG.get(str(emner[0]).split(".")[0] if emner else "", "state")

    return {
        "id": domene,
        "regime": {
            "name": f"{domene.split('.')[-1]} — the {lag} layer from {k['navn']}",
            "validity": (
                f"applies to the part of {k['navn']} that covers {domene.split('.')[-1]}. "
                f"Measured volume: {meldinger} messages over {len(emner)} topic(s). "
                f"Further: the share is a READING of the corpus, not a separate measurement."),
        },
        "phase": "instrument",
        "measure": {
            "target": k["hva"],
            "measurer": k["hvem"],
            "instrument": k["instrument"],
            "proxy_chain": k["proxy"],
            "placement": "observation",
            "compression": f"all messages about {domene.split('.')[-1]} -> one share",
        },
        "episenter": (
            f"where the corpus becomes a share for {domene.split('.')[-1]} — "
            f"the number does not exist in the source, it arises in the reading"),
        "buffer": {
            "role": f"{k['navn']} is the buffer: it holds the state between updates",
            "note": "the source's, not the engine's",
        },
        "ontology": {
            "assumes": [
                f"{k['navn']} is available and complete enough for this share",
                "the share is comparable over time",
                f"the subject {emner[0] if emner else '?'} represents the domain",
            ],
            "source": f"the NATS stream, subject {domene}.* — measured in schema/atlas_dekning.json",
        },
        "observer": {
            "bandwidth": f"the share — only {domene.split('.')[-1]}, not the whole corpus",
            "awareness": "instrument_window",
            "er_del_av_systemet": True,
        },
        "emergence": {"loop": k["loop"], "properties": [f"{meldinger} messages"]},
        "fractal": {"pattern": k["fractal"], "note": "one domain, the same corpus"},
        "coupling": {
            "local": f"each message belongs to {domene.split('.')[-1]} locally",
            "global": "all 39 domains read the SAME corpus",
            "empathy_note": (
                "that a share is the largest does not mean it is the most important — "
                "it means the coding hit it most often"),
        },
        "perspektiv": k["perspektiv"],
        "stipulasjoner": {
            "stipulert_av_oss": False,
            "terskler": ["no thresholds of its own — the share is inherited from the coding"],
            "motor": "",
        },
        "epistemikk": {
            "sannhetsstatus": k["sannhet"],
            "evidensstatus": k["evidens"],
            "konsensusstatus": k["konsensus"],
            "sosial_mekanisme": (
                f"{k['navn']} — institutional source. The share is OUR READING "
                f"of it, not the source's own claim."),
            "konsensus_er_ikke_sannhet": True,
        },
        "maale_paradigme": {
            "koordinater": ["rom", "tid"],
            "enheter": "share of the corpus (0-1)",
            "status": "proxy",
            "alternativer": ["the source's own numbers, without our share reading"],
        },
        "nivaa": {"indeks": 2, "forelder": None, "tidsskala": "continuous",
                  "lengdeskala": "global"},
        "buss_domene": domene,
        "synlighet": "offentlig",
        "lagdeling": {
            "kilde": {"status": k["perspektiv"], "kilde": k["navn"],
                      "sannhet": k["sannhet"], "konsensus": k["konsensus"]},
            "analogi": {"status": "paradigme", "kilde": "our share reading",
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

    repaired = 0
    for i, n in enumerate(d["nodes"]):
        if n["id"] not in a.rett:
            continue
        if n["id"] not in dek["domener"]:
            raise KildeFeil(f"\"{n['id']}\" does not stand in "
                            f"atlas_dekning.json -- the source cannot be read "
                            f"from the measurement")
        d["nodes"][i] = rett(n, node_for(n["id"], dek["domener"][n["id"]]))
        repaired += 1

    finnes = {n["id"] for n in d["nodes"]}
    ude = {k: v for k, v in dek["domener"].items() if not v.get("noder")}
    nye = [node_for(k, v) for k, v in sorted(ude.items()) if k not in finnes]
    d["nodes"].extend(nye)
    p.write_text(json.dumps(d, **K.FORMAT) + "\n", encoding="utf-8")
    print(f"added {len(nye)} nodes for {len(ude)} uncovered domains")
    print(f"repaired {repaired} node(s) from the sources")
    print(f"{len(d['nodes'])} nodes in total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
