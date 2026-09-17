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
    "efc.l0": ("roots", 1), "efc.selv.paradigme_tid": ("epist", 7),
    "efc.grid_higgs": ("grid", 2), "efc.gr_qft_bro": ("grid", 2),
    "efc.grid_mikrofysikk": ("grid", 2), "efc.grid_mikro_engine": ("grid", 2),
    "efc.double_slit": ("grid", 2), "efc.sort_hull": ("grid", 2),
    "efc.mu_kz": ("kosmos", 3), "efc.growth": ("kosmos", 3),
    "efc.rotation": ("kosmos", 3), "efc.hubble": ("kosmos", 3),
    "efc.lensing": ("kosmos", 3), "efc.cluster": ("kosmos", 3),
    "efc.transient": ("kosmos", 3),
    "efc.romvaer": ("kosmos", 3), "efc.orbital": ("kosmos", 3),
    "efc.tidevann": ("kosmos", 3), "efc.klima": ("kosmos", 3),
    "verden.hav": ("broer", 4), "verden.biosfaere": ("broer", 4),
    "kosmos.jord.vulkan": ("broer", 4),
    "kjemi.periodesystemet": ("struktur", 5),
    "efc.water": ("struktur", 5),
    "efc.victron_cccv_engine": ("struktur", 5),
    "efc.enerflyt": ("samfunn", 6), "efc.oekonomi": ("samfunn", 6),
    "efc.samfunn": ("samfunn", 6),
}

GRUPPER = [
    {"id": "roots", "title": "The roots — time and self"},
    {"id": "grid", "title": "The grid — your published works"},
    {"id": "kosmos", "title": "Cosmos — engines on the bus"},
    {"id": "broer", "title": "Bridges — gap domains, round two"},
    {"id": "struktur", "title": "Structures — H2O and chemistry"},
    {"id": "samfunn", "title": "Society — energy flow"},
    {"id": "epist", "title": "Epistemics"},
    {"id": "ghost", "title": "Not yet built"},
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
    return PLASSERING.get(navn, ("ghost", 8))[1]


def _gruppe(navn: str) -> str:
    return PLASSERING.get(navn, ("ghost", 8))[0]


def _perspektiv_tekst(p: str | None) -> str:
    return {"akademia": "academia", "konsensus": "consensus",
            "paradigme": "paradigm"}.get(p or "", "agnostic")


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


def _node_rad(node: dict, i: int) -> dict:
    nid = node["id"]
    gr = _gruppe(nid)
    kap = _kap(nid)
    navn = nid.split(".")[-1].replace("_", " ")
    ep = node.get("epistemikk", {})
    maal = node.get("measure", {})
    buf = node.get("buffer", {})
    cond = []
    if ep.get("evidensstatus") == "ingen":
        cond.append(f"{nid}: no evidence yet — hypothesis marked honestly")
    if node.get("stipulasjoner", {}).get("motor") in (None, "", "KANDIDAT "
        "(broen venter paa konnektor-deploy)"):
        pass
    motor = node.get("stipulasjoner", {}).get("motor", "")
    if motor and motor.startswith("KANDIDAT"):
        cond.append({"q": f"{nid}: motor waits for connector deploy",
                     "to": "connector deploy (human step)"})
    return {
        "id": nid.replace(".", "-").replace("_", "-")[:40],
        "code": kode_for(nid),
        "name": nid,
        "short": navn[:14],
        "group": gr,
        "gx": 1.5 + (i % 6) * 2.4,
        "gy": -1 + (i // 6) * 2.6,
        "w": 2, "d": 2, "h": 34,
        "kind": "tall" if node.get("phase") == "motor" else "box",
        "ghost": gr == "ghost",
        "one": f"Perspective: {_perspektiv_tekst(node.get('perspektiv'))}. "
               f"{maal.get('target', '')[:70]}",
        "what": f"{maal.get('instrument', '')[:90]} — "
                f"proxy chain: {' -> '.join(maal.get('proxy_chain', ['']))[:90]}",
        "how": f"Buffer role: {buf.get('role', '—')[:80]}. "
               f"Epistemic: {ep.get('sannhetsstatus', '—')} / "
               f"{ep.get('evidensstatus', '—')} / "
               f"{ep.get('konsensusstatus', '—')}.",
        "steps": [["Perspective", _perspektiv_tekst(node.get("perspektiv"))],
                  ["Epistemics",
                   f"{ep.get('sannhetsstatus', '—')} / "
                   f"{ep.get('evidensstatus', '—')} / "
                   f"{ep.get('konsensusstatus', '—')}"],
                  ["Social mechanism",
                   ep.get("sosial_mekanisme", "—")[:120]]],
        "cond": cond,
    }


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
        8: "Not yet built",
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
    ch.append({
        "id": "all", "title": "The whole atlas",
        "reveal": [], "lede": f"Everything at once — {len(noder)} nodes, "
                              f"{len(relasjoner)} relations.",
        "story": "<p>Free exploration. Hover, click to pin, go inside.</p>",
        "flow": None,
    })

    # FLOWS: de tre bro-kjedene som dataflyt (tabellen staar oeverst i fila)
    flows = FLOWS

    data = f"""// GENERERT av scripts/maintenance/efc_atlas_generator.py —
// IKKE rediger for haand. Kilden er schema/regime_nodes.jsonld.
export const META = {{
  title: 'EFC',
  artifactUrl: '',
  sourcePath: 'schema/regime_nodes.jsonld',
  buildCmd: 'node docs/efc-atlas/atlas/build.mjs',
  stats: [{{ k: 'Nodes', v: '{len(noder)}' }},
          {{ k: 'Perspectives', v: 'paradigm / consensus / academia' }}],
  intro: `_**One source, two views.** This atlas is generated from regime_nodes.jsonld — the bank is the truth; the atlas is its mirror._`,
  onePara: `Energy-Flow Cosmology: an entropic, structural atlas of the universe — from grid microphysics to society's energy flow. {len(noder)} nodes, {motorer} engines, NATS bridges.`,
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
