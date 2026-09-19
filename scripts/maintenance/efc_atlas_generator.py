"""efc_atlas_generator — generates the atlas's data.mjs FROM regime_nodes.jsonld.

One source, two views: regime_nodes.jsonld is the truth; the atlas is
a MIRROR. No double bookkeeping — data.mjs is always built from here, and
a drift between the bank and the atlas is an error in this file, not an
error in the atlas.

    python3 scripts/maintenance/efc_atlas_generator.py

The chapters follow the plateau chains of the level graph: each chapter reveals
one chain at a time (progressive disclosure), and the last one shows everything.
"""
from __future__ import annotations

import json
import pathlib
import re

ROT = pathlib.Path(__file__).resolve().parents[2]
ATLAS_DIR = ROT / "docs" / "efc-atlas" / "atlas"
JSONLD = ROT / "schema" / "regime_nodes.jsonld"

#: The bus is a MEASUREMENT, not a table. `schema/nats_domener.snapshot.json`
#: is written by `scripts/atlas_volum.py --maal` and carries its own provenance
#: (`maalt`, `lest_av`); this generator may repeat what that file says and
#: nothing else. Measured 2026-09-19: the node bank reached the atlas with the
#: claim "NATS bridges", while 0 of the 16 workflow files in
#: `.github/workflows` run the measurement — so the snapshot ages by itself and
#: the atlas said nothing about it. A number typed in here would age exactly
#: like the retired "82 nodes" headline did.
BUS_SNAPSHOT = ROT / "schema" / "nats_domener.snapshot.json"
WORKFLOW_DIR = ROT / ".github" / "workflows"

#: The name a cadence would have to reference for the bus to be consumed in
#: drift. The scan below looks for it with the `--maal` flag.
MAALING = "atlas_volum"

#: The code is the node's SHORT IDENTIFIER (1-2 characters) — not a visual label.
#:
#: Measured 2026-09-17: the table covered 28 of 82 nodes; the rest fell back to
#: `nid[:2].upper()`. The 73 public nodes thereby got 18 codes — «EF»
#: pointed at 20 nodes, «OB» at 20 — and 15 of the 28 keys named nodes that
#: do not exist (efc.hubble, efc.water, … they are called `*_engine` in the bank). None
#: of the errors was visible, because the fallback answered instead of speaking up.
#:
#: The code IS an identifier, and it is used as one: `build.mjs` builds
#: question IDs from it (`Q-<code><n>`, and the index says «Reference by
#: ID»), and FLOWS names its hops with it (HA, BI, VU, EF). A code that
#: points at twenty nodes at once identifies none of them.
#:
#: Therefore: every node in the bank SHALL stand here, the code shall be unambiguous, and
#: the generator FAILS rather than guessing (see `manglende_koder`). The tile
#: that draws the code is 16 px wide (template.html), hence 1-2 characters.
#:
#: The code is stable: it follows the node, not the name it carried in an earlier
#: thought. If a node id changes, the code must move with it — the test
#: `test_deklarasjonen_raatner_ikke` kills orphaned keys.
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
    # Root and self-reference
    "efc.l0": "L0", "efc.l1": "L1", "efc.l2": "L2", "efc.l3": "L3",
    # The grid — published works
    "efc.grid_higgs": "GH", "efc.gr_qft_bro": "GQ",
    "efc.grid_mikrofysikk": "GM", "efc.grid_mikro_engine": "GE",
    "efc.double_slit": "DS", "efc.sort_hull": "SH",
    # Cosmos — the engines on the bus
    "efc.mu_kz_engine": "MK", "efc.growth_engine": "GR",
    "efc.rotation_engine": "RO", "efc.hubble_engine": "HB",
    "efc.lensing_engine": "LN", "efc.cluster_engine": "CL",
    "efc.transient_engine": "TR", "efc.romvaer_engine": "RV",
    "efc.orbital_engine": "OR", "efc.tidevann_engine": "TI",
    "efc.klima_engine": "KL", "efc.solar_flare_engine": "SF",
    "efc.jordskjelv_engine": "JS",
    # Bridges — the gap domains
    "verden.hav": "HA", "verden.biosfaere": "BI",
    "kosmos.jord.vulkan": "VU",
    # Structures — water and chemistry
    "kjemi.periodesystemet": "PS", "efc.water_phase_engine": "WA",
    "h2o.solid": "SO", "h2o.liquid": "LI", "h2o.gas": "GA",
    "h2o.supercritical": "SC", "h2o.triple_point": "TP",
    "h2o.droplet": "DR", "lys.sol": "LY", "optikk.dispersjon": "OP",
    "regnbue": "RB", "regnbue.observator": "OB",
    # Society — energy flow
    "efc.enerflyt_engine": "EF", "efc.oekonomi_engine": "OK",
    "efc.samfunn_engine": "SA", "efc.victron_cccv_engine": "VC",
    # Observations — each with its own target
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
    # Homo — the regime engine
    "homo.fluxus": "HF", "homo.homeostase_buffer": "HO",
    "homo.feber_regime": "FE", "homo.aksjonspotensial": "AP",
    "homo.hjerte_syklus": "HJ", "homo.genregulering": "GN",
    "homo.cellesyklus": "CY", "homo.metabolisme": "ME",
    "homo.immunologi": "IM", "homo.sovn_vaaken": "SV",
    "homo.okologi": "OE", "homo.evolusjon": "EV",
    # Internal nodes — not published, but the same namespace
    "batteri.celle": "BC", "batteri.lading": "BL",
    "batteri.buffer": "BF", "batteri.inverter": "IN",
    "efc.selv.atlas": "AT", "efc.selv.skjema": "SK",
    "efc.selv.paradigme_tid": "PT", "efc.selv.paradigme_masse": "PM",
}

#: Group and chapter membership: (group, chapter).
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
    # Ghost is a CHOICE: these have been measured not to have a group yet.
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

#: The three bridge chains as data flow. The hops name the nodes by their CODE — that
#: is why the code must be unambiguous: «EF» means `efc.enerflyt_engine`, and
#: only that. (That the renderer in atlas/template.html today looks the hops up in the
#: `id` namespace and therefore does not draw them is a separate bug with its own
#: root cause — it does not belong in this table.)
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
            f"[efc-atlas] `{navn}` is not in PLASSERING — and a fallback "
            f"would hide that someone forgot it. Put it in the right group, "
            f"or say explicitly that it is ghost.")
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
    if fase == "observation":
        return "observation"
    if "regime" in fase:
        return "regime"
    if motor:
        return "engine"
    return "other"


def uten_gruppe_grunner(noder: list[dict]) -> dict[str, int]:
    """Split the group-less by WHAT is missing — measured, not assumed."""
    tell = {"observation": 0, "regime": 0, "engine": 0, "other": 0}
    for n in noder:
        if _gruppe(n["id"]) != "ghost":
            continue
        fase = str(n.get("phase") or "")
        motor = str((n.get("stipulasjoner") or {}).get("motor") or "").strip()
        if fase == "observation":
            tell["observation"] += 1
        elif "regime" in fase:
            tell["regime"] += 1
        elif motor:
            tell["engine"] += 1
        else:
            tell["other"] += 1
    return tell


def uten_gruppe_frase(noder: list[dict], anker: str = "of them",
                      med_grunn: bool = True) -> str:
    """The group-less count, and why — derived once, carried by every surface.

    A surface that states how many nodes the atlas has must state this number
    in the same breath: "116 nodes" alone reads as a map fuller than it is.
    Measured 2026-09-19: the count reached the index header and the chapter-9
    lede, and not the one-paragraph lede or the atlas stat strip.

    ONE derivation, and the call site only chooses the connective — several
    wordings with their own numbers would drift apart, and a counter that is
    almost right is worse than none. `med_grunn=False` is the compact form for
    a nowrap stat card, where the split does not fit.

    One language, deliberately: the surfaces are English, so a `spraak`
    parameter that could also render the phrase in Norwegian was removed
    (t_648190ca) rather than left in the producer as an unused branch.
    """
    gr = uten_gruppe_grunner(noder)
    antall = sum(gr.values())
    tekst = f"{antall}{' ' + anker if anker else ''} without a group yet"
    if not med_grunn:
        return tekst
    return (f"{tekst} ({gr['observation']} observations, {gr['regime']} regime "
            f"nodes, {gr['engine']} with an engine, {gr['other']} other)")


def arbeidsflyt_filer(katalog: pathlib.Path | None = None) -> list[pathlib.Path]:
    """The workflow files a cadence would have to live in.

    Both extensions are read: GitHub Actions accepts `.yml` and `.yaml`, and a
    scan that looked for only one of them would miss exactly the cadence it
    exists to find.
    """
    katalog = katalog or WORKFLOW_DIR
    if not katalog.is_dir():
        return []
    return sorted(list(katalog.glob("*.yml")) + list(katalog.glob("*.yaml")))


def buss_fakta(noder: list[dict], snapshot: pathlib.Path | None = None,
               workflows: pathlib.Path | None = None) -> dict:
    """What reads the bus, what does not, and the numbers behind both.

    Three separate claims, three separate measurements, no hand-written number:

      * the MEASUREMENT — the domain count and the provenance (`maalt`,
        `lest_av`) are read from the snapshot `--maal` wrote;
      * the ROUTES — how many published nodes name a bus route, and how many
        say nothing (a field on the node, counted here);
      * the SCHEDULE — the workflow files that run the measurement. Measured
        2026-09-19: none of them does.

    The third one is why this function exists: "NATS bridges" is a claim about
    consumption, and consumption is not a property of the bank. A missing
    snapshot, or one without provenance, RAISES — a guessed number is
    indistinguishable from a measurement once it is printed, and this atlas is
    read by people who cannot see where the number came from.
    """
    sti = snapshot or BUS_SNAPSHOT
    if not sti.exists():
        raise SystemExit(
            f"[efc-atlas] {sti} is missing — the bus is measured, never "
            f"guessed. Run `python3 scripts/atlas_volum.py --maal` on a door "
            f"that holds the bus key, then rebuild.")
    maaling = json.loads(sti.read_text(encoding="utf-8"))
    domener = maaling.get("domener") or {}
    prov = maaling.get("_proveniens") or {}
    if not domener or not prov.get("maalt") or not prov.get("lest_av"):
        raise SystemExit(
            f"[efc-atlas] {sti} carries no provenance (`maalt` / `lest_av`) "
            f"or no domains — a snapshot without a date is a claim that ages "
            f"in silence. Measure again instead of rebuilding the atlas.")

    vei = [n for n in noder if (n.get("stipulasjoner") or {}).get("buss_status")]
    filer = arbeidsflyt_filer(workflows)
    kadenser = []
    for fil in filer:
        tekst = fil.read_text(encoding="utf-8")
        if MAALING in tekst and "--maal" in tekst:
            kadenser.append(fil.name)

    return {
        "domener": len(domener),
        "maalt": str(prov["maalt"]),
        "dato": str(prov["maalt"])[:10],
        "lest_av": str(prov["lest_av"]),
        "publiserte": len(noder),
        "navngir_vei": len(vei),
        "stille": len(noder) - len(vei),
        "kadenser": kadenser,
        "arbeidsflyter": len(filer),
    }


def buss_frase(f: dict) -> str:
    """One sentence for the one-paragraph lede: what reads the bus, what does not.

    It replaces "NATS bridges", which claimed consumption the tree does not
    have. The sentence is a function of the facts, so a cadence that appears
    later moves the text instead of contradicting it.
    """
    if f["kadenser"]:
        kadens = ("scheduled by "
                  + ", ".join(f"`.github/workflows/{n}`" for n in f["kadenser"]))
    else:
        kadens = (f"and no schedule runs that measurement "
                  f"(0 of {f['arbeidsflyter']} workflow files)")
    return (f"The NATS bus: {f['domener']} domains, measured {f['dato']} by "
            f"{f['lest_av']} — read by measurement code, {kadens}.")


def buss_tekst(f: dict) -> list[str]:
    """The atlas's own holes, in its own words — one paragraph per claim.

    `Known holes` is where the atlas names what it does NOT cover. The bus
    belongs there, not in a capability list: it is read by code and consumed by
    no runner, and those two statements can both be true at once. That is the
    distinction this section exists to keep.
    """
    if f["kadenser"]:
        kadens = ("The measurement IS scheduled: "
                  + ", ".join(f"`.github/workflows/{n}`" for n in f["kadenser"])
                  + " run `scripts/atlas_volum.py --maal`.")
    else:
        kadens = (f"No schedule runs that measurement: "
                  f"{len(f['kadenser'])} of {f['arbeidsflyter']} workflow files "
                  f"in `.github/workflows` reference it, so the snapshot ages "
                  f"by itself.")
    return [
        ("**The bus is read by code, not consumed in drift.** "
         f"`scripts/atlas_volum.py --maal` reads the JetStream streams' "
         f"`state.subjects` through the house's own `verden_domener` (MCP) and "
         f"writes `schema/nats_domener.snapshot.json` with its own provenance: "
         f"{f['domener']} domains, measured {f['maalt']} by {f['lest_av']}. "
         f"{kadens} Until a door holding the bus key measures again, the only "
         f"alarm is "
         f"`tests/test_atlas_dekning.py::test_snapshottet_har_ikke_gaatt_ut_paa_dato` "
         f"at 90 days — a stale measurement that still answers, which is the "
         f"failure mode the atlas exists to name."),
        ("**Bus routes in the node bank.** "
         f"{f['navngir_vei']} of the published nodes name a bus route; the "
         f"other {f['stille']} say nothing. A named route is a connection the "
         f"bank has taken a position on, not traffic the atlas has seen."),
    ]


def buss_html(f: dict) -> str:
    """The same holes for the interactive view, which reads no markdown.

    Backticks become <code>: HOW_HTML is a JS template literal, so a stray
    backtick ends the string and the whole build fails on the parse. Measured —
    the first build after this card was written died exactly there.
    """
    avsnitt = []
    for p in buss_tekst(f):
        p = re.sub(r"`([^`]*)`", r"<code>\1</code>", p).replace("**", "")
        avsnitt.append(f"<p>{p}</p>")
    return '<h3 class="sec">Known holes</h3>' + "".join(avsnitt)


def _gruppe(navn: str) -> str:
    if navn not in PLASSERING:
        raise SystemExit(
            f"[efc-atlas] `{navn}` is not in PLASSERING — see `_kapittel()`.")
    return PLASSERING[navn][0]


def _perspektiv_tekst(p: str | None) -> str:
    return {"akademia": "academia", "konsensus": "consensus",
            "paradigme": "paradigm"}.get(p or "", "agnostic")


#: The text limits for the atlas RENDERS. They stand here and not spread out as
#: `[:70]` inside `_node_rad`, because the test in `tests/test_atlas_lesbarhet.py`
#: reads them: a limit that a test cannot read cannot be locked.
GRENSER = {"short": 14, "one": 70, "what": 90, "how": 80, "sosial": 120,
           "sakse": 120}


def klipp(tekst: str, grense: int) -> str:
    """Cut at the word boundary — and SAY that it was cut.

    Measured 2026-09-18 (origin/main f4a3e4f2): `[:70]`, `[:90]` and `[:80]` cut
    mid-word. That gave the atlas «fase identifisert via P_sat(T) o», «rotation
    engin» and «holder temperaturen under oppvarming . Epistemic». A truncated
    string with no mark looks like the whole text and is read as it — the same
    class as the fallback that answers: the answer exists, but it does not answer
    what it looks like it answers.

    Cuts at the nearest word boundary within the limit and appends «…» when something
    actually was lost. One character is cheaper than an answer that lies about being
    complete.

    One case has no word boundary: when the FIRST word alone is longer than
    the limit, there is no space to cut at. Then the token is cut — and
    marked. That is the one permitted mid-word cut, and it is only possible
    because the alternative (cutting without a mark) is what the function exists to
    prevent.
    """
    t = " ".join(str(tekst or "").split())
    if len(t) <= grense:
        return t
    if " " not in t[:grense + 1]:
        return t[:grense].rstrip() + "…"
    return t[:grense + 1].rsplit(" ", 1)[0].rstrip(" ,;:—-·") + "…"


def klipp_med_status(tekst: str, grense: int) -> tuple[str, bool]:
    """`klipp()` plus whether something actually was lost.

    The full stop after the buffer role shall not follow a cut mark. The first
    version guessed this by looking for «…» in the RESULT — and then read wrong
    for a bank text that itself ends with «…», and missed a text that ends
    with «...». The cutter knows the answer; therefore it returns it.
    """
    kuttet = len(" ".join(str(tekst or "").split())) > grense
    return klipp(tekst, grense), kuttet


def kode_for(nid: str) -> str:
    """The node's short identifier. No fallback.

    A node without a code is an error that must be SEEN. The fallback
    (`nid[:2].upper()`) made it invisible in the months it stood here: it
    answered with a code that looked right, and 20 nodes shared it.
    """
    try:
        return KODER[nid]
    except KeyError:
        raise KeyError(
            f"{nid} has no code. Put it into KODER in "
            f"scripts/maintenance/efc_atlas_generator.py — the code is the node's "
            f"short identifier, and question IDs (Q-<code><n>) and the "
            f"FLOWS hops are built from it.") from None


def manglende_koder(noder: list[dict]) -> list[str]:
    """Nodes in the bank without a declared code, sorted. Shall be empty."""
    return sorted(n["id"] for n in noder if n["id"] not in KODER)


def foreldede_koder(noder: list[dict]) -> list[str]:
    """Codes declared for nodes that do not exist, sorted. Shall be empty.

    Did not catch itself: 15 of the 28 keys named nodes that have never
    existed under that name (`efc.hubble` vs `efc.hubble_engine`), and the
    fallback answered instead of reporting.
    """
    id_er = {n["id"] for n in noder}
    return sorted(set(KODER) - id_er)


def kollisjoner(noder: list[dict]) -> dict[str, list[str]]:
    """Codes carried by more than one node: {code: [node-id, …]}."""
    per: dict[str, list[str]] = {}
    for n in noder:
        if n["id"] in KODER:
            per.setdefault(KODER[n["id"]], []).append(n["id"])
    return {k: sorted(v) for k, v in sorted(per.items()) if len(v) > 1}


def sakse_tekst(node: dict) -> str:
    """The S-axis as readable text — an empty string when it is not measured.

    The S-axis (regime, sector, clarity, EBE, RCMP) was written to data.mjs as
    `sAxis`, but neither of the two builds reads that key: the node panel shows
    `what`/`how`/`cond`, and so does the text twin. The renderer is a HAND-COPIED
    copy of the skill's asset, not read-only: this copy carries the code-namespace
    fix from #506 (pinned by tests/test_atlas_flows.py, red before it), and the
    asset carries the same mechanism since 2026-09-19 — so the two agree, and any
    further edit must be made in BOTH, or the next `cp` from SKILL.md drops it.
    The layer must therefore be expressed in a field the views ACTUALLY read —
    `how` is the right one: the regime and the measurement chain are how the node
    is built.

    The order is the measurement chain: regime -> sector -> clarity -> EBE -> RCMP.
    """
    mp = node.get("maale_paradigme") or {}
    parter: list[str] = []
    if mp.get("s_regime"):
        parter.append(f"regime {mp['s_regime']}")
    if mp.get("sektor"):
        parter.append(f"sector {mp['sektor']}")
    if mp.get("klarhetsfunksjon"):
        parter.append(f"clarity {klipp(mp['klarhetsfunksjon'], GRENSER['sakse'])}")
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
    # The questions here are not written by the generator.
    #
    # Measured 2026-09-18: for every node without evidence the generator inserted the line
    # «no evidence yet — hypothesis marked honestly». It was IDENTICAL for all
    # seven, it asked about nothing, and it repeated `how` («Epistemic: … ingen») inside the
    # question tab. «7 open · 0 resolved» was thereby one and the same
    # word seven times — the fallback that answers, in the question tab.
    #
    # The evidence status stands where it is measured: in `how`. A real open
    # question must come FROM THE BANK (a field on the node), never from
    # the generator's pen — a generator that makes up questions produces busywork
    # out of its own template.
    cond = []
    # A REAL open question comes from the bank — the field `open_questions` on
    # the node. The generator never writes a question itself (see `cond = []` above).
    for spm in node.get("open_questions") or []:
        if isinstance(spm, str) and spm.strip():
            cond.append(spm.strip())
        elif isinstance(spm, dict) and str(spm.get("q", "")).strip():
            cond.append({k: v for k, v in spm.items()
                         if k in ("q", "r", "to") and str(v).strip()})
    # The literal below is the bank's declared value in `stipulasjoner.motor`
    # (a data enum) and is compared verbatim — it stays as it is in the bank.
    if node.get("stipulasjoner", {}).get("motor") in (None, "", "KANDIDAT "
        "(broen venter paa konnektor-deploy)"):
        pass
    motor = node.get("stipulasjoner", {}).get("motor", "")
    if motor and motor.startswith("KANDIDAT"):
        cond.append({"q": f"{nid}: motor waits for connector deploy",
                     "to": "connector deploy (human step)"})
    # The one-liner is the first thing the user reads when they hover a node.
    # It shall answer WHAT the thing is. Previously it opened with the perspective, and then
    # ALL 116 nodes began with the same word («Perspective: …»): a template that says
    # who holds the view, not what it is — and that pushed the substance to the back,
    # where `[:70]` cut it. The perspective is not gone: it stands in `steps`
    # and as a short mark at the end.
    substans = klipp(maal.get("target", ""), GRENSER["one"])
    perspektiv = _perspektiv_tekst(node.get("perspektiv"))
    # `role` may be missing, be None or empty. Previously None/"" gave an empty text, and
    # the line became «Buffer role: . Epistemic: …»; «—» says that the field is not
    # filled in, which is true.
    bufferrolle, bufferrolle_kuttet = klipp_med_status(
        buf.get("role") or "—", GRENSER["how"])
    # A cut ends with «…». Then the template's own full stop shall not follow, otherwise
    # it reads «… tolkning…. Epistemic» — a cut mark and a full stop that
    # both try to end the same sentence. The full stop is read from the cut's
    # STATUS, not from a character in the result: a bank text can itself end with
    # «…», and then the character would have lied.
    punktum = "" if bufferrolle_kuttet else "."
    # The S-axis must stand in `how` to be SEEN: that is the field both builds
    # show. It is only inserted when it is measured — 96 identical «not measured»
    # would have been the same template the question tab was just cleaned of.
    # The emptiness is reported instead ONCE, as a number in META.stats.
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
        "one": (f"{substans} · perspective: {perspektiv}" if substans
                else f"perspective: {perspektiv}"),
        # `what` is two labelled parts — the instrument AND the proxy chain — not one
        # field. The limit applies to each part, so the whole field can become longer than
        # GRENSER["what"]. That is intentional: a shared limit would cut the
        # instrument to make room for the chain.
        "what": f"{klipp(maal.get('instrument', ''), GRENSER['what'])} — "
                f"proxy chain: "
                f"{klipp(' -> '.join(maal.get('proxy_chain', [''])), GRENSER['what'])}",
        "how": f"Buffer role: {bufferrolle}{punktum} "
               f"Epistemic: {ep.get('sannhetsstatus', '—')} / "
               f"{ep.get('evidensstatus', '—')} / "
               f"{ep.get('konsensusstatus', '—')}."
               # The S-axis often ends with a full stop itself (the RCMP declaration
               # did: «… gyldighetsdomene.». Therefore the tail full stop is only set
               # when the text does not already end itself.
               + (f" S-axis: {sakse}"
                  f"{'' if sakse.endswith(('.', '…')) else '.'}" if sakse else ""),
        "sAxis": {
            "regime": node.get("maale_paradigme", {}).get("s_regime"),
            "sector": node.get("maale_paradigme", {}).get("sektor"),
            "ebe": node.get("maale_paradigme", {}).get("ebe_function"),
            # `klarhetsfunksjon` was filled in on as many nodes as s_regime
            # (19 of 126, measured 2026-09-18) and was NOT read by the generator:
            # the S-axis looked emptier in the atlas than it is in the bank.
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
    lines = ["# Atlas index", "",
             (f"> {len(noder)} published nodes · "
              f"{uten_gruppe_frase(noder, '')} · "
              f"{evidens} without evidence · {spoersmaal} open questions"), "",
             "Each row is generated from the same bank as the atlas.", ""]
    for gruppe in ("roots", "grid", "kosmos", "broer", "struktur", "samfunn",
                   "epist", "ghost"):
        if not grupper.get(gruppe):
            continue
        lines.append(f"## {titler[gruppe]}")
        for rad, node in grupper[gruppe]:
            st = sakse_tekst(node) or "not measured"
            stip = node.get("stipulasjoner") or {}
            motor = stip.get("motor") or "not specified"
            buss = stip.get("buss_status") or "not specified"
            spm = len(node.get("open_questions") or [])
            perspektiv = _perspektiv_tekst(node.get("perspektiv"))
            # The line is a READING SURFACE, not a dump. The first version gave nine columns
            # without names — among them «1 · nei» — and the perspective stood BOTH as
            # the truncated tail of the one-liner and as a separate column. A number without
            # a label is a riddle, not information; whoever scans shall
            # be able to read the row without looking up what the columns mean.
            substans = rad["one"].split(" · perspective:")[0].strip()
            lines.append(f"- **{rad['code']} · {node['id']}**"
                         + (f" — {klipp(substans, 90)}" if substans else ""))
            lines.append("  " + " · ".join([
                f"perspective={perspektiv}",
                f"engine={motor}",
                f"bus={klipp(str(buss), 40)}",
                f"S-axis={klipp(st, 60)}",
                f"questions={spm}",
                (f"group=none ({gruppe_grunn(node)})" if rad["ghost"]
                 else "group=yes"),
            ]))
        lines.append("")
    lines.append("## With no group yet")
    lines.append("")
    for rad, node in (item for item in sum(grupper.values(), []) if item[0]["ghost"]):
        lines.append(f"- {node['id']} — {klipp(node.get('navn') or node['id'], 100)}")
    lines.append("")
    return "\n".join(line.rstrip() for line in lines) + "\n"


def hoved() -> int:
    atlas = json.load(open(JSONLD, encoding="utf-8"))
    alle = atlas["nodes"]

    # Code preflight. It stands BEFORE anything is written, and it FAILS — it
    # does not guess. The order is the point: an atlas built with a
    # code that points at twenty nodes is worse than an atlas that is not
    # built, because the first one looks finished.
    mangler = manglende_koder(alle)
    if mangler:
        print(f"ERROR: {len(mangler)} node(s) in the bank are missing a code in KODER:")
        for m in mangler:
            print(f"  {m}")
        print("The code is the node's short identifier (Q-IDs and the FLOWS hops "
              "are built from it). Put it into KODER in this file.")
        return 1
    doede = foreldede_koder(alle)
    if doede:
        print(f"ERROR: {len(doede)} code(s) are declared for nodes that do not "
              f"exist:")
        for d in doede:
            print(f"  {d} -> {KODER[d]}")
        print("The table has rotted (a node id was changed without the code "
              "moving along). Fix the key.")
        return 1
    koll = kollisjoner(alle)
    if koll:
        print(f"ERROR: {len(koll)} code(s) are carried by several nodes:")
        for k, ids in koll.items():
            print(f"  {k}: {', '.join(ids)}")
        print("A code that points at several nodes identifies none of "
              "them. Choose an unambiguous code per node.")
        return 1
    print(f"codes: {len(KODER)} unambiguous for {len(alle)} nodes")

    # Only public nodes go to GitHub Pages. The filter is DECLARED per
    # node (`synlighet`), not a hidden rule here — a node that disappears
    # without anyone seeing why is the same error class the rest of the house
    # exists to prevent. Internal nodes are not deleted: they live on
    # in the complete atlas, and are counted explicitly in the output so
    # the withholding is visible.
    noder = [n for n in alle if n.get("synlighet") == "offentlig"]
    interne = [n["id"] for n in alle if n.get("synlighet") != "offentlig"]
    print(f"nodes: {len(noder)} public of {len(alle)}")
    if interne:
        print(f"  withheld ({len(interne)}): {', '.join(sorted(interne))}")

    # The numbers below are DYNAMIC on purpose. They stood hardcoded as «82 nodes,
    # 79 relations» and «82 nodes, 18 engines», and thereby stayed and
    # lied in the public map the moment the filter took effect —
    # 73 nodes published, 82 claimed. It besides revealed that something was held
    # back, which is exactly what the filter is meant to hide.
    offentlige_id = {n["id"] for n in noder}
    relasjoner = [r for r in atlas.get("relations", [])
                  if r.get("subject") in offentlige_id
                  and r.get("object") in offentlige_id]
    motorer = sum(1 for n in noder if "_engine" in str(n.get("id", "")))

    rader = [_node_rad(n, i) for i, n in enumerate(noder)]
    # Ghost nodes: those without PLASSERING and with epistemics «ingen»
    for r in rader:
        nid = r["name"]
        if nid not in PLASSERING:
            r["group"] = "ghost"
            r["ghost"] = True

    # Chapters: 1-8 + the whole system (9)
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
                              f"{uten_gruppe_frase(noder, 'of them')}, "
                              f"{len(relasjoner)} relations.",
        "story": "<p>Free exploration. Hover, click to pin, go inside.</p>"
                 f"<p>{uten_evidens} nodes carry no evidence yet — that is what "
                 f"<i>epistemic: … / ingen / …</i> in “How it's built” says. "
                 f"Open questions are not generated: they come from the bank, "
                 f"and none is registered.</p>",
        "flow": None,
    })

    # FLOWS: the three bridge chains as data flow (the table stands at the top of the file)
    flows = FLOWS

    # The S-axis measured on N of M nodes. The number stands ONCE, in the header: an empty
    # field and a field that does not exist are two different answers, and only one of them is a
    # gap. One line per node («not measured») would on the other hand have been the same template
    # that the question tab was just cleaned of.
    sakse_maalt = sum(1 for n in noder if sakse_tekst(n))

    indeks = _indeks(noder, rader)
    (ATLAS_DIR.parent / "INDEKS.md").write_text(indeks, encoding="utf-8")

    # The two remaining surfaces that count nodes: the one-paragraph lede and
    # the atlas stat strip. Both carry the group-less count from the SAME
    # derivation as the index header and the chapter-9 lede — the strip uses
    # the compact form because a stat card is nowrap and the split does not fit.
    uten_gruppe_en = uten_gruppe_frase(noder, "of them")
    uten_gruppe_egne = uten_gruppe_frase(noder, f"of the {len(noder)}")
    uten_gruppe_kort = uten_gruppe_frase(noder, "", med_grunn=False)

    # The bus, measured three ways: the snapshot's own numbers, the routes the
    # bank names, and the schedules that run the measurement (measured
    # 2026-09-19: none of them does). The readout is printed so the number in
    # the surfaces can be traced to the run that produced it.
    buss = buss_fakta(noder)
    print(f"bus: {buss['domener']} domains measured {buss['maalt']} by "
          f"{buss['lest_av']} · {buss['navngir_vei']} of {buss['publiserte']} "
          f"nodes name a route · {buss['stille']} silent · "
          f"{len(buss['kadenser'])} of {buss['arbeidsflyter']} workflows run "
          f"the measurement")

    data = f"""// GENERATED by scripts/maintenance/efc_atlas_generator.py —
// DO NOT edit by hand. The source is schema/regime_nodes.jsonld.
export const META = {{
  title: 'EFC',
  artifactUrl: '',
  sourcePath: 'schema/regime_nodes.jsonld',
  buildCmd: 'node docs/efc-atlas/atlas/build.mjs',
  stats: [{{ k: 'Nodes', v: '{len(noder)} · {uten_gruppe_kort}' }},
          {{ k: 'S-axis', v: '{sakse_maalt} of {len(noder)} measured · {uten_gruppe_kort}' }},
          {{ k: 'Perspectives', v: 'paradigm / consensus / academia' }}],
  intro: `_**One source, two views.** This atlas is generated from regime_nodes.jsonld — the bank is the truth; the atlas is its mirror._`,
  onePara: `Energy-Flow Cosmology: an entropic, structural atlas of the universe — from grid microphysics to society's energy flow. {len(noder)} nodes, {motorer} engine nodes. {buss_frase(buss)} {uten_gruppe_egne}.`,
  platformGives: 'NATS bus (read by measurement code, scheduled by nothing — see Known holes), engines, review fan-out, the EFC bank.',
  busHull: {json.dumps(buss_tekst(buss), indent=2)},
  weOwn: 'The atlas itself — every node, every epistemic declaration, every threshold.',
  costModel: [],
  filesystem: `schema/regime_nodes.jsonld\\\\n  efc_inference/engine/*.py\\\\n  efc_inference/bridge/*.py`,
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
<h3 class="sec">Generator</h3><pre>scripts/maintenance/efc_atlas_generator.py</pre>
{buss_html(buss)}`;
"""
    # Trailing whitespace breaks git diff --check — strip every line
    data = "\n".join(linje.rstrip() for linje in data.splitlines()) + "\n"
    (ATLAS_DIR / "data.mjs").write_text(data, encoding="utf-8")
    print("data.mjs written:", len(data), "bytes")

    # Build both views and strip whitespace from the build output
    # (build.mjs writes blank lines with spaces in SYSTEM.md).
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
