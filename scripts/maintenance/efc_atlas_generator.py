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

#: Kode-bokstaver per node (1-2 tegn) — stabil saalenge atlaset lever.
KODER = {
    "efc.l0": "L0", "efc.selv.paradigme_tid": "PT",
    "efc.grid_higgs": "GH", "efc.gr_qft_bro": "GQ",
    "efc.grid_mikrofysikk": "GM", "efc.grid_mikro_engine": "GE",
    "efc.mu_kz": "MK", "efc.growth": "GR", "efc.rotation": "RO",
    "efc.hubble": "HB", "efc.lensing": "LN", "efc.cluster": "CL",
    "efc.enerflyt": "EF", "efc.victron_cccv_engine": "VC",
    "efc.water": "WA", "efc.klima": "KL", "efc.romvaer": "RV",
    "efc.orbital": "OR", "efc.tidevann": "TI", "efc.transient": "TR",
    "efc.oekonomi": "OK", "efc.samfunn": "SA",
    "efc.double_slit": "DS", "efc.sort_hull": "SH",
    "verden.hav": "HA", "verden.biosfaere": "BI",
    "kosmos.jord.vulkan": "VU", "kjemi.periodesystemet": "PS",
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


def _kap(navn: str) -> int:
    return PLASSERING.get(navn, ("ghost", 8))[1]


def _gruppe(navn: str) -> str:
    return PLASSERING.get(navn, ("ghost", 8))[0]


def _perspektiv_tekst(p: str | None) -> str:
    return {"akademia": "academia", "konsensus": "consensus",
            "paradigme": "paradigm"}.get(p or "", "agnostic")


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
        "code": KODER.get(nid, nid[:2].upper()),
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

    # FLOWS: de tre bro-kjedene som dataflyt
    flows = [
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
