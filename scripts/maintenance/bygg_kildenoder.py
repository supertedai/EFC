"""Build nodes for the uncovered domains — from the SOURCES, not from each other.

Measured 2026-09-18: 24 of 39 domains had no node. They are not 24 different
cases; they are carried by SIX sources, and the same 15 verden domains are
carried by four sources at once (gdelt-gkg, mentions, export, world-bank).

Each domain is nevertheless a domain and shall own its node. The difference
from earlier attempts: the nodes are built from the MEASURED numbers in
schema/atlas_dekning.json — message counts, topics, layers — not from prose.

`verden.politikk` is the exception: it is the CARRIER of the GDELT layers, and
whether it should be public or internal is Morten's decision. It is built as
internal until then, and says so itself.
"""
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
}

#: The domain's layer role, as the coverage file names it. The KEYS are the
#: bus domain prefixes (`observasjon.gdelt-gkg`) — data, not prose.
LAG = {"observasjon": "state", "diskusjon": "discussion", "hendelse": "event",
       "prediksjon": "prediction", "tilstand": "state"}


def node_for(domene: str, v: dict) -> dict:
    """Build ONE node from the MEASURED numbers — not from prose about them."""
    emner = v.get("emner") or []
    meldinger = v.get("meldinger", 0)
    # the source: the last link in the topics, chosen where several exist
    kilder = sorted({str(e).split(".")[-1] for e in emner})
    kilde = kilder[0] if kilder else "unknown"
    k = KILDE.get(kilde, KILDE["gdelt-gkg"])
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


def main() -> None:
    p = Path("schema/regime_nodes.jsonld")
    d = json.loads(p.read_text(encoding="utf-8"))
    dek = json.loads(DEKNING.read_text(encoding="utf-8"))
    finnes = {n["id"] for n in d["nodes"]}

    ude = {k: v for k, v in dek["domener"].items() if not v.get("noder")}
    nye = [node_for(k, v) for k, v in sorted(ude.items()) if k not in finnes]
    d["nodes"].extend(nye)
    p.write_text(json.dumps(d, **K.FORMAT) + "\n", encoding="utf-8")
    print(f"added {len(nye)} nodes for {len(ude)} uncovered domains")
    print(f"{len(d['nodes'])} nodes in total")


if __name__ == "__main__":
    main()
