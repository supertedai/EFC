// GENERERT av scripts/maintenance/efc_atlas_generator.py —
// IKKE rediger for haand. Kilden er schema/regime_nodes.jsonld.
export const META = {
  title: 'EFC',
  artifactUrl: '',
  sourcePath: 'schema/regime_nodes.jsonld',
  buildCmd: 'node docs/efc-atlas/atlas/build.mjs',
  stats: [{ k: 'Nodes', v: '116' },
          { k: 'S-axis', v: '39 of 116 measured' },
          { k: 'Perspectives', v: 'paradigm / consensus / academia' }],
  intro: `_**One source, two views.** This atlas is generated from regime_nodes.jsonld — the bank is the truth; the atlas is its mirror._`,
  onePara: `Energy-Flow Cosmology: an entropic, structural atlas of the universe — from grid microphysics to society's energy flow. 116 nodes, 19 engine nodes, NATS bridges.`,
  platformGives: 'NATS bus, engines, review fan-out, the EFC bank.',
  weOwn: 'The atlas itself — every node, every epistemic declaration, every threshold.',
  costModel: [],
  filesystem: `schema/regime_nodes.jsonld\n  efc_inference/engine/*.py\n  efc_inference/bridge/*.py`,
};

export const DECISIONS = [
  { axis: 'Epistemics', decision: 'truth, evidence and consensus are three separate axes — consensus is never truth (const true).', adr: 'schema/regime_node.schema.json' },
  { axis: 'Levels', decision: 'a parent must have a lower index than its child; no cycles.', adr: 'tests/test_epistemikk_v6.py' },
  { axis: 'Analogy', decision: 'every analogy carries both an avbildning and a bryter_der — without the disanalogy it does not harden.', adr: 'schema/regime_node.schema.json' },
  { axis: 'Sources', decision: 'a finding belongs to the bank it came from — not where I sat when I found it.', adr: 'SOUL.md' },
];

export const GROUPS = [
  {
    "id": "roots",
    "title": "The roots \u2014 time and self"
  },
  {
    "id": "grid",
    "title": "The grid \u2014 your published works"
  },
  {
    "id": "kosmos",
    "title": "Cosmos \u2014 engines on the bus"
  },
  {
    "id": "broer",
    "title": "Bridges \u2014 gap domains, round two"
  },
  {
    "id": "struktur",
    "title": "Structures \u2014 H2O and chemistry"
  },
  {
    "id": "samfunn",
    "title": "Society \u2014 energy flow"
  },
  {
    "id": "epist",
    "title": "Epistemics"
  },
  {
    "id": "ghost",
    "title": "No group yet"
  }
];

export const NODES = [
  {
    "id": "h2o-solid",
    "code": "SO",
    "name": "h2o.solid",
    "short": "solid",
    "group": "ghost",
    "gx": 1.5,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "termodynamisk fase \u00b7 perspektiv: academia",
    "what": "kalibrert termometer + barometer (kalibrert mot trippelpunktcellen) \u2014 proxy chain: temperatur via termisk ekspansjon (termometer) -> trykk via membran (barometer) -> fase\u2026",
    "how": "Buffer role: krystallgitteret + latent varme L_f: isen holder drikken ved 0 C til siste\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.solid: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "h2o-liquid",
    "code": "LI",
    "name": "h2o.liquid",
    "short": "liquid",
    "group": "ghost",
    "gx": 3.9,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "termodynamisk fase \u00b7 perspektiv: academia",
    "what": "kalibrert termometer + barometer \u2014 proxy chain: temperatur via termisk ekspansjon -> trykk via membran -> fase identifisert via P_sat(T)\u2026",
    "how": "Buffer role: hoey varmekapasitet (4.18 kJ/(kg*K)): vann holder temperaturen under oppvarming\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.liquid: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "h2o-gas",
    "code": "GA",
    "name": "h2o.gas",
    "short": "gas",
    "group": "ghost",
    "gx": 6.3,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "termodynamisk fase \u00b7 perspektiv: academia",
    "what": "kalibrert termometer + barometer (evt. hygrometer for damp) \u2014 proxy chain: temperatur via termisk ekspansjon -> trykk via membran -> dampinnhold via duggpunkt\u2026",
    "how": "Buffer role: gassens varmekapasitet og utvidelse demper lokale trykk- og\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.gas: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "h2o-supercritical",
    "code": "SC",
    "name": "h2o.supercritical",
    "short": "supercritical",
    "group": "ghost",
    "gx": 8.7,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "termodynamisk tilstand (ikke 'fase' \u2014 grensen er borte) \u00b7 perspektiv: academia",
    "what": "hoeytrykks-P-T-celle \u2014 proxy chain: temperatur via termoelement -> trykk via hoeytrykksmembran -> ingen faseobservabel\u2026",
    "how": "Buffer role: ingen fasegrense aa holde \u2014 bufferkapasiteten er kontinuerlig, uten latent varme. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.supercritical: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "h2o-triple-point",
    "code": "TP",
    "name": "h2o.triple_point",
    "short": "triple point",
    "group": "ghost",
    "gx": 11.1,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "temperaturskalaens referansepunkt \u00b7 perspektiv: academia",
    "what": "kalibrert trippelpunktcelle \u2014 ITS-90-referansen \u2014 proxy chain: trykk holdt konstant (611.657 Pa) -> temperatur avlest som celleveggens termiske likevekt\u2026",
    "how": "Buffer role: punktet absorberer energi uten temperaturstigning saa lenge tre faser\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.triple_point: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "lys-sol",
    "code": "LY",
    "name": "lys.sol",
    "short": "sol",
    "group": "ghost",
    "gx": 13.5,
    "gy": -1.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "elektromagnetisk straaling \u00b7 perspektiv: academia",
    "what": "prisme/gitter-spektrometer \u2014 proxy chain: boelgelengde via gitter-dispersjon -> intensitet via detektor -> farge som\u2026",
    "how": "Buffer role: solen er en enorm energikilde med tilnaermet stabil spektralfordeling over\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "lys.sol: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "h2o-droplet",
    "code": "DR",
    "name": "h2o.droplet",
    "short": "droplet",
    "group": "ghost",
    "gx": 1.5,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "draapeform og brytningsindeks \u00b7 perspektiv: academia",
    "what": "hoyhastighetskamera / refraktometer \u2014 proxy chain: draapeform via overflatespenning -> brytningsindeks via refraksjon (n ~ 1.33) ->\u2026",
    "how": "Buffer role: overflatespenningen holder draapen sfaerisk \u2014 en geometrisk buffer som demper\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "h2o.droplet: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "optikk-dispersjon",
    "code": "OP",
    "name": "optikk.dispersjon",
    "short": "dispersjon",
    "group": "ghost",
    "gx": 3.9,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "brytningsindeksen n(lambda) \u00b7 perspektiv: academia",
    "what": "spektrometer + prisme \u2014 proxy chain: avboyningsvinkel via Snells lov -> n(lambda) via vinkelmaaling -> fargeseparasjon som\u2026",
    "how": "Buffer role: vannets elektroniske struktur gir dispersjonen stabilitet \u2014 n(lambda) er en\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "optikk.dispersjon: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "regnbue",
    "code": "RB",
    "name": "regnbue",
    "short": "regnbue",
    "group": "ghost",
    "gx": 6.3,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "buens vinkel og fargerekkefoelge \u00b7 perspektiv: academia",
    "what": "retina eller CCD-sensor \u2014 proxy chain: farge via boelgelengde-dispersjon i draapen -> buevinkel via refraksjonsgeometri (~42\u2026",
    "how": "Buffer role: draapesvermen er en statistisk buffer \u2014 monsteret overlever at enkeltdraaper\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "regnbue: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "regnbue-observator",
    "code": "OB",
    "name": "regnbue.observator",
    "short": "observator",
    "group": "ghost",
    "gx": 8.7,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "buen som retnings- og fargemonster \u00b7 perspektiv: academia",
    "what": "retina (S-, M- og L-kjegler) \u2014 proxy chain: fotoner -> fotoreseptorer -> S/M/L-respons -> fargeopplevelse -> retning -> buens posisjon\u2026",
    "how": "Buffer role: oeyets adaptasjon (pupille, bleking av fotopigment) bufferer mot lysvariasjon\u2026 Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fagfellevurdering, l\u00e6rebok-kanonisering, karriereinsentiver \u2014 akademia forteller det som overlever vurderingen"
      ]
    ],
    "cond": [
      "regnbue.observator: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-water-phase-engine",
    "code": "WA",
    "name": "efc.water_phase_engine",
    "short": "water phase\u2026",
    "group": "struktur",
    "gx": 11.1,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "fasegrenser P_sat(T), T_m(P), P_sub(T) \u00b7 perspektiv: paradigm",
    "what": "WaterPhaseEngine (efc_inference/engine/water.py) \u2014 proxy chain: P_sat(T) via Watson L_v(T) -> T_m(P) via dv_melt = 1/rho_vann - 1/rho_is -> P_sub(T) via\u2026",
    "how": "Buffer role: gyldighetsomraadene er motorens buffer: utenfor dem svarer den NaN/unknown i\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-l0",
    "code": "L0",
    "name": "efc.l0",
    "short": "l0",
    "group": "roots",
    "gx": 13.5,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "urbetingelser og strukturfro \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 modellavhengig \u2014 proxy chain: inflasjonsprediksjoner -> P(k)-avtrykk i L1 -> ingen direkte observabel i L0",
    "how": "Buffer role: vakuumsvingningene er frobanken \u2014 en buffer av potensial som inflasjonen tapper. Epistemic: hypotese / proxy / minoritet. S-axis: regime S->0 \u00b7 klarhet C(S) ved S->0: udifferensiert klarhet \u2014 kompresjonsgrensen (singularitet) \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S->0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S->0: udifferensiert klarhet \u2014 kompresjonsgrensen (singularitet)",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": [
      "efc.l0: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-l1",
    "code": "L1",
    "name": "efc.l1",
    "short": "l1",
    "group": "ghost",
    "gx": 1.5,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "CMB-anisotropier og BAO-skala \u00b7 perspektiv: paradigm",
    "what": "CMB-kart + galakse-survey \u2014 proxy chain: temperaturanisotropier -> P(k) -> BAO-skala -> H(z) -> polarisasjon -> optisk dybde",
    "how": "Buffer role: plasmaets foton-elektron-kobling holder anisotropiene frosne til rekombinasjon\u2026 Epistemic: hypotese / proxy / minoritet. S-axis: regime S~0 \u00b7 klarhet C(S) ved S~0: begynnende klarhet \u2014 differensieringens terskel \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S~0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S~0: begynnende klarhet \u2014 differensieringens terskel",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": [
      "efc.l1: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-l2",
    "code": "L2",
    "name": "efc.l2",
    "short": "l2",
    "group": "ghost",
    "gx": 3.9,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "fsigma8, P(k), svak linse (S8) \u00b7 perspektiv: paradigm",
    "what": "galakse-survey + svak linse (KiDS, DES, Euclid) \u2014 proxy chain: galaksefordeling -> P(k) full-shape -> roedforskyvningsromforvrengning -> fsigma8 -> skj\u00e6r\u2026",
    "how": "Buffer role: strukturen selv er en treghetsbuffer: galakser og klynger holder masse mot\u2026 Epistemic: hypotese / proxy / minoritet. S-axis: regime S>0 \u00b7 klarhet C(S) ved S>0: differensiert klarhet \u2014 refleksjonens vindu, R over R_c~0.37 gir selvmodellering \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S>0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S>0: differensiert klarhet \u2014 refleksjonens vindu, R over R_c~0.37 gir selvmodellering",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": [
      "efc.l2: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-l3",
    "code": "L3",
    "name": "efc.l3",
    "short": "l3",
    "group": "ghost",
    "gx": 6.3,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "fjern-fremtid-tilstanden \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 predikert grense \u2014 proxy chain: vekstlovens asymptote -> S->1-tilstanden -> ingen maalbar proxy i dag",
    "how": "Buffer role: metningen ER en buffer: veksten bremses mot en grense i stedet for aa loepe\u2026 Epistemic: hypotese / proxy / minoritet. S-axis: regime S->1 \u00b7 klarhet C(S) ved S->1: mettet klarhet \u2014 altular-grensen, avtagende energitetthet \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S->1",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S->1: mettet klarhet \u2014 altular-grensen, avtagende energitetthet",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": [
      "efc.l3: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "obs-bao",
    "code": "BA",
    "name": "obs.bao",
    "short": "bao",
    "group": "ghost",
    "gx": 8.7,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "BAO-skalaen (r_d ~ 147 Mpc comoving) \u00b7 perspektiv: consensus",
    "what": "galakse-surveyer (DESI, eBOSS, BOSS) \u2014 proxy chain: galakse-korrelasjonsfunksjon -> BAO-topp ved ~150 Mpc -> BAO-topp -> D_H(z)/r_d\u2026",
    "how": "Buffer role: drag-epoch fryser lydskalaen inn i plasmaet \u2014 linjalen fryses i L1 og leses i L2. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=galakse-surveyer (DESI, eBOSS, BOSS); observabel=BAO-skalaen (r_d ~ 147 Mpc comoving); teori=BAO \u2014 standardlinjalen; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "galakse-surveyer (DESI, eBOSS, BOSS)",
        "observabel": "BAO-skalaen (r_d ~ 147 Mpc comoving)",
        "teori": "BAO \u2014 standardlinjalen",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "BAO-toppen ble kanonisert via SDSS/BOSS/eBOSS og DESI \u2014 store samarbeid med NSF/DOE-finansiering; survey-konkurransen og\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-cmb-tt",
    "code": "TT",
    "name": "obs.cmb_tt",
    "short": "cmb tt",
    "group": "ghost",
    "gx": 11.1,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "temperatur-/polarisasjonsspekteret \u00b7 perspektiv: consensus",
    "what": "Planck \u2014 proxy chain: temperaturspektrum -> P(k) -> toppavstand -> theta_* og r_s(z_*) -> polarisasjon -> optisk\u2026",
    "how": "Buffer role: rekombinasjonen fryser fotonene \u2014 signalet holdes til det slippes ved z ~ 1100. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=Planck; observabel=temperatur-/polarisasjonsspekteret; teori=CMB TT/EE/TE akustiske topper; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "Planck",
        "observabel": "temperatur-/polarisasjonsspekteret",
        "teori": "CMB TT/EE/TE akustiske topper",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "CMB-temperaturspekteret b\u00e6res av Planck-samarbeidets institusjonelle autoritet \u2014 resultatet ble kanonisert i l\u00e6reb\u00f8ker\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-cmb-lensing",
    "code": "LC",
    "name": "obs.cmb_lensing",
    "short": "cmb lensing",
    "group": "ghost",
    "gx": 13.5,
    "gy": 4.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "linsingspotensialet \u00b7 perspektiv: consensus",
    "what": "Planck, ACT, SPT \u2014 proxy chain: CMB-anisotropi-fordeling -> linsingspotensial -> linsingspotensial -> P(k) ved z ~ 2",
    "how": "Buffer role: fotonenes frie ferd er bufferen \u2014 de samler masseavtrykk underveis. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=Planck, ACT, SPT; observabel=linsingspotensialet; teori=CMB Lensing Reconstruction; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "Planck, ACT, SPT",
        "observabel": "linsingspotensialet",
        "teori": "CMB Lensing Reconstruction",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Lensing-konsensusen b\u00e6res av Planck og ACT/SPT \u2014 to konkurrerende instrumentgrupper som bekrefter hverandre; avviks-funn\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-bbn",
    "code": "BB",
    "name": "obs.bbn",
    "short": "bbn",
    "group": "ghost",
    "gx": 1.5,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "deuterium/hydrogen-forholdet \u00b7 perspektiv: consensus",
    "what": "quasar-spektroskopi \u2014 proxy chain: D/H i quasarskyer -> baryontetthet omega_b h^2 -> omega_b h^2 -> kryssjekk mot CMB",
    "how": "Buffer role: kjernereaksjonene fryser D/H ved T ~ 80 keV \u2014 et signal som aldri endres. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=quasar-spektroskopi; observabel=deuterium/hydrogen-forholdet; teori=BBN lette elementer; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "quasar-spektroskopi",
        "observabel": "deuterium/hydrogen-forholdet",
        "teori": "BBN lette elementer",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "BBN er kanonisert i l\u00e6reb\u00f8ker og b\u00e6res av den estetiske sammenhengen med CMB \u2014 \u00e5 teste den p\u00e5 nytt gir lite prestisje\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-fsigma8",
    "code": "F8",
    "name": "obs.fsigma8",
    "short": "fsigma8",
    "group": "ghost",
    "gx": 3.9,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "vekstraten fsigma8 \u00b7 perspektiv: consensus",
    "what": "BOSS, eBOSS, DESI \u2014 proxy chain: roedforskyvningsromforvrengning (RSD) -> f sigma8 -> f sigma8(z) -> vekstlovens form",
    "how": "Buffer role: strukturen selv er bufferen \u2014 gravitasjonell respons holder masse mot\u2026 Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=BOSS, eBOSS, DESI; observabel=vekstraten fsigma8; teori=f-sigma-8(z) line\u00e6r vekst; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "BOSS, eBOSS, DESI",
        "observabel": "vekstraten fsigma8",
        "teori": "f-sigma-8(z) line\u00e6r vekst",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "f\u03c38-m\u00e5lingene kommer fra store survey-samarbeid \u2014 karriereveiene ligger i samarbeidene, og systematikker publiseres\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-s8",
    "code": "S8",
    "name": "obs.s8",
    "short": "s8",
    "group": "ghost",
    "gx": 6.3,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "S8 = sigma8 sqrt(omega_m/0.3) \u00b7 perspektiv: consensus",
    "what": "KiDS, DES, HSC, Euclid \u2014 proxy chain: skj\u00e6r (svak linse) -> S8 -> S8 lav vs CMB-forventning -> tension",
    "how": "Buffer role: linsebildene holder avtrykket av masse langs synslinjen \u2014 en akkumulert buffer. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=KiDS, DES, HSC, Euclid; observabel=S8 = sigma8 sqrt(omega_m/0.3); teori=S8-tension; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "KiDS, DES, HSC, Euclid",
        "observabel": "S8 = sigma8 sqrt(omega_m/0.3)",
        "teori": "S8-tension",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "S8-tensionen er omstridt MELLOM instrument-tradisjoner \u2014 to fellesskap med egne karrierer leser samme data; hvem som har\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-eg",
    "code": "EG",
    "name": "obs.eg",
    "short": "eg",
    "group": "ghost",
    "gx": 8.7,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "E_G-krysset \u00b7 perspektiv: consensus",
    "what": "SDSS, KiDS+BOSS \u2014 proxy chain: linse (kappa) x RSD (beta) -> E_G -> E_G -> slip mellom lys og masse",
    "how": "Buffer role: to uavhengige proxyer buffrer hverandre \u2014 krysset er mer robust enn hver del. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=SDSS, KiDS+BOSS; observabel=E_G-krysset; teori=E_G gravitasjonsslip-statistikk; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "SDSS, KiDS+BOSS",
        "observabel": "E_G-krysset",
        "teori": "E_G gravitasjonsslip-statistikk",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "EG-m\u00e5linger er avhengige av f\u00e5 instrumenter \u2014 narrativet b\u00e6res av en liten gruppe spesialister med h\u00f8y publiseringsmakt\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-isw",
    "code": "IS",
    "name": "obs.isw",
    "short": "isw",
    "group": "ghost",
    "gx": 11.1,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "ISW-signalet \u00b7 perspektiv: consensus",
    "what": "CMB x galaksekart \u2014 proxy chain: CMB-kart x galaksefordeling -> ISW-kryss",
    "how": "Buffer role: fotonene integrerer potensialets tidsderivat over ferdselen \u2014 reisen er bufferen. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=CMB x galaksekart; observabel=ISW-signalet; teori=ISW krysskorrelasjon; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "CMB x galaksekart",
        "observabel": "ISW-signalet",
        "teori": "ISW krysskorrelasjon",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "ISW-signalet er svakt og var lenge omstridt \u2014 konsensusen vokste med CMB-tradisjonens autoritet, ikke med nye uavhengige\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-ksz",
    "code": "KS",
    "name": "obs.ksz",
    "short": "ksz",
    "group": "ghost",
    "gx": 13.5,
    "gy": 6.800000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "kSZ-signalet \u00b7 perspektiv: consensus",
    "what": "ACT, DES x SPT \u2014 proxy chain: CMB x galakser -> kSZ -> kSZ -> egenhastighetsfelt",
    "how": "Buffer role: elektronene i klynger spretter fotoner doppler \u2014 plasmaet er bufferen. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=ACT, DES x SPT; observabel=kSZ-signalet; teori=kSZ egenhastigheter; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "ACT, DES x SPT",
        "observabel": "kSZ-signalet",
        "teori": "kSZ egenhastigheter",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "kSZ er en ung tradisjon \u2014 konsensusen er institusjonell f\u00f8r den er replikert; f\u00e5 grupper har instrumentene"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-cluster-mass",
    "code": "CM",
    "name": "obs.cluster_mass",
    "short": "cluster mass",
    "group": "ghost",
    "gx": 1.5,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "M_500 fra flere kanaler \u00b7 perspektiv: consensus",
    "what": "Chandra, XMM, HST \u2014 proxy chain: rontgen (T_X) -> masse -> svak linse -> masse -> skaleringsrelasjoner -> masse",
    "how": "Buffer role: klyngens potensial holder gassen varm og lyset boeyd \u2014 to buffere, \u00e9n masse. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=Chandra, XMM, HST; observabel=M_500 fra flere kanaler; teori=klyngemasse-skalering; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "Chandra, XMM, HST",
        "observabel": "M_500 fra flere kanaler",
        "teori": "klyngemasse-skalering",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Hopemassene avhenger av r\u00f8ntgen/svak-lensing-kalibreringer fra noen f\u00e5 store samarbeid \u2014 konsensusen arver deres interne\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-cluster-hmf",
    "code": "HM",
    "name": "obs.cluster_hmf",
    "short": "cluster hmf",
    "group": "ghost",
    "gx": 3.9,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "halomassetetthetsfunksjonen \u00b7 perspektiv: consensus",
    "what": "DES, SDSS, eROSITA \u2014 proxy chain: antall klynger per masse -> N(M,z) -> N(M,z) -> sigma8 og vekst",
    "how": "Buffer role: kollapsen buffrer masse i halos \u2014 tellingen er buffernes fordeling. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=DES, SDSS, eROSITA; observabel=halomassetetthetsfunksjonen; teori=klyngehalo-massetetthet N(M,z); overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "DES, SDSS, eROSITA",
        "observabel": "halomassetetthetsfunksjonen",
        "teori": "klyngehalo-massetetthet N(M,z)",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Hopfunsjonen er forankret i numeriske simuleringer med egne kode-tradisjoner \u2014 konsensusen b\u00e6res av simuleringsgruppenes\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-rar",
    "code": "RA",
    "name": "obs.rar",
    "short": "rar",
    "group": "ghost",
    "gx": 6.3,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "a_obs vs a_bar \u00b7 perspektiv: consensus",
    "what": "SPARC \u2014 proxy chain: rotasjonskurver -> a_obs -> barionisk fordeling -> a_bar -> avvik -> a_obs/a_bar",
    "how": "Buffer role: galaksens potensial holder rotasjonen \u2014 dynamikken er bufferen. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=SPARC; observabel=a_obs vs a_bar; teori=Radial Acceleration Relation; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "SPARC",
        "observabel": "a_obs vs a_bar",
        "teori": "Radial Acceleration Relation",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "RAR (radial acceleration relation) er omstridt i MOND-debatten \u2014 to fellesskap med uforenlige narrativ leser samme data\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-bullet",
    "code": "BU",
    "name": "obs.bullet",
    "short": "bullet",
    "group": "ghost",
    "gx": 8.7,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "masse-gass-offseten \u00b7 perspektiv: consensus",
    "what": "HST + Chandra \u2014 proxy chain: linse (masse) vs rontgen (gass) -> offset delta-kappa",
    "how": "Buffer role: kollisjonen separerer komponentene \u2014 hendelsen er bufferen. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=HST + Chandra; observabel=masse-gass-offseten; teori=Bullet-klyngen delta-kappa; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "HST + Chandra",
        "observabel": "masse-gass-offseten",
        "teori": "Bullet-klyngen delta-kappa",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Bullet Cluster leses i MOND-debatten \u2014 to rammer med egne karrierebaner; bildet er det samme, fortellingen er kampen"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-satellites",
    "code": "SL",
    "name": "obs.satellites",
    "short": "satellites",
    "group": "ghost",
    "gx": 11.1,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "subhalo-populasjonen \u00b7 perspektiv: consensus",
    "what": "HST, simuleringer \u2014 proxy chain: telte dverg-satellitter vs predikerte -> underskudd -> tette kjerner vs cusp -> profil",
    "how": "Buffer role: subhalos holdes av vertens potensial \u2014 bufferen er tidevannsstrippingen. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=HST, simuleringer; observabel=subhalo-populasjonen; teori=manglende satellitter / TBTF / core-cusp; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "HST, simuleringer",
        "observabel": "subhalo-populasjonen",
        "teori": "manglende satellitter / TBTF / core-cusp",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Satellittproblemet b\u00e6res av simuleringstradisjonen vs observat\u00f8rene \u2014 et kjent spenningspunkt der konsensusen skifter\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-jwst-ems",
    "code": "JW",
    "name": "obs.jwst_ems",
    "short": "jwst ems",
    "group": "ghost",
    "gx": 13.5,
    "gy": 9.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "galakse-massefunksjonen ved z>10 \u00b7 perspektiv: consensus",
    "what": "JWST \u2014 proxy chain: JWST-fotometri -> masse ved z>10 -> massefunksjon -> kollapstidsskala",
    "how": "Buffer role: tidlige halos er de foerste bufferne \u2014 de foerste som holdt masse. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=JWST; observabel=galakse-massefunksjonen ved z>10; teori=tidlig massiv struktur (JWST z>10); overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "JWST",
        "observabel": "galakse-massefunksjonen ved z>10",
        "teori": "tidlig massiv struktur (JWST z>10)",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "JWST-funnene er nye og forhandles \u00c5PENT \u2014 hvert \u00abuventet\u00bb funn gir publisitet og dermed insentiv til spenning i\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-gw-ct",
    "code": "GW",
    "name": "obs.gw_ct",
    "short": "gw ct",
    "group": "ghost",
    "gx": 1.5,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "c_T fra GW170817 \u00b7 perspektiv: consensus",
    "what": "LIGO/Virgo \u2014 proxy chain: GW- og gammaankomst -> c_T/c innen 1e-15",
    "how": "Buffer role: 1.7-sekunders-forsinkelsen over 40 Mpc er maalingens buffer \u2014 reisen kalibrerer. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=LIGO/Virgo; observabel=c_T fra GW170817; teori=Gravitasjonsbolgehastighet c_T; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "LIGO/Virgo",
        "observabel": "c_T fra GW170817",
        "teori": "Gravitasjonsbolgehastighet c_T",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Gravitasjonsb\u00f8lger er en ung, raskt institusjonalisert tradisjon \u2014 LIGO/Virgo/KAGRA-samarbeidene har monopol p\u00e5 dataene\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-pta-gwb",
    "code": "PA",
    "name": "obs.pta_gwb",
    "short": "pta gwb",
    "group": "ghost",
    "gx": 3.9,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "GW-bakgrunnen ved nHz \u00b7 perspektiv: consensus",
    "what": "NANOGrav, EPTA \u2014 proxy chain: pulsar-timing-residualer -> Hellings-Downs-korrelasjon -> GW-bakgrunn",
    "how": "Buffer role: pulsarene ER bufferen \u2014 deres rotasjon holder fasen over aar. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=NANOGrav, EPTA; observabel=GW-bakgrunnen ved nHz; teori=PTA gravitasjonsbolge-bakgrunn; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "NANOGrav, EPTA",
        "observabel": "GW-bakgrunnen ved nHz",
        "teori": "PTA gravitasjonsbolge-bakgrunn",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "PTA-konsensusen bygges av noen f\u00e5 store samarbeid med ti\u00e5r lange datasett \u2014 dataene er private frem til publisering, s\u00e5\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-h0-tension",
    "code": "H0",
    "name": "obs.h0_tension",
    "short": "h0 tension",
    "group": "ghost",
    "gx": 6.3,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "H0 fra to uavhengige kanaler \u00b7 perspektiv: consensus",
    "what": "Planck vs SH0ES \u2014 proxy chain: CMB (LCDM-ekstrapolasjon) -> H0 ~ 67 -> cepheid/SN-stige -> H0 ~ 73 -> gap -> tension",
    "how": "Buffer role: to uavhengige maalekjeder buffrer hverandre \u2014 nettopp derfor kan ingen av dem\u2026 Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=Planck vs SH0ES; observabel=H0 fra to uavhengige kanaler; teori=Hubble-tension H0; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "Planck vs SH0ES",
        "observabel": "H0 fra to uavhengige kanaler",
        "teori": "Hubble-tension H0",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Hubble-tensionen er AKTUELT omstridt \u2014 avstandsskala vs CMB, to karriereveier; hver ny m\u00e5ling flytter narrativet, og\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-w0wa",
    "code": "W0",
    "name": "obs.w0wa",
    "short": "w0wa",
    "group": "ghost",
    "gx": 8.7,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "w(z)-parametriseringen \u00b7 perspektiv: consensus",
    "what": "DES, BAO+CMB \u2014 proxy chain: SN + BAO + CMB -> w0, wa -> w0, wa -> avvik fra -1",
    "how": "Buffer role: SN-lysets strekk over avstand er bufferen \u2014 ekspansjonshistorien er skrevet i\u2026 Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=DES, BAO+CMB; observabel=w(z)-parametriseringen; teori=w0-wa dynamisk moerk energi; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "DES, BAO+CMB",
        "observabel": "w(z)-parametriseringen",
        "teori": "w0-wa dynamisk moerk energi",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "m\u00f8rk-energi-parametriseringen er en konsensus KONVENSJON mer enn en m\u00e5ling \u2014 narrativet b\u00e6res av survey-designenes valg\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "obs-cc",
    "code": "CC",
    "name": "obs.cc",
    "short": "cc",
    "group": "ghost",
    "gx": 11.1,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "vakuumenergiens stoerrelse \u00b7 perspektiv: consensus",
    "what": "alle kanaler \u2014 proxy chain: alle observasjoner -> omega_Lambda ~ 0.7 -> naivt teoretisk QFT-estimat -> ~120\u2026",
    "how": "Buffer role: bakgrunnens akselerasjon er bufferen \u2014 den holder ekspansjonen oppe. Epistemic: modellrelativ / proxy / institusjonell. S-axis: RCMP instrument=alle kanaler; observabel=vakuumenergiens stoerrelse; teori=kosmologisk konstant / vakuumenergi; overlap=True; deklarasjon=RCMP: instrument, observabel og teori har overlappende gyldighetsdomene.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": {
        "instrument": "alle kanaler",
        "observabel": "vakuumenergiens stoerrelse",
        "teori": "kosmologisk konstant / vakuumenergi",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observabel og teori har overlappende gyldighetsdomene."
      }
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "modellrelativ / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "klynge-tellingens konsensus b\u00e6res av masse-kalibreringskjeden \u2014 en lang kjede av antakelser som hver for seg er\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-rotation-engine",
    "code": "RO",
    "name": "efc.rotation_engine",
    "short": "rotation\u2026",
    "group": "kosmos",
    "gx": 13.5,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "v(r) \u2014 rotasjonshastighet som funksjon av radius \u00b7 perspektiv: paradigm",
    "what": "observasjonssiden er galaksespektre; motoren regner kurven \u2014 proxy chain: spektrallinjer -> v(r) (observasjon) -> v(r) -> EFC-parametre (inferens)",
    "how": "Buffer role: galaksens materie-buffer holder kurven flat gjennom koplingsfeltet \u2014 tolkning\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-hubble-engine",
    "code": "HB",
    "name": "efc.hubble_engine",
    "short": "hubble engine",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "H(z) \u2014 ekspansjonsraten \u00b7 perspektiv: paradigm",
    "what": "observasjonssiden er BAO/kronometer; motoren regner raten \u2014 proxy chain: BAO/SNIa -> H(z) (observasjon) -> H(z) -> EFC-parametre (inferens)",
    "how": "Buffer role: bakgrunnsenergien er bufferen som holder ekspansjonen \u2014 modellert, ikke m\u00e5lt\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-growth-engine",
    "code": "GR",
    "name": "efc.growth_engine",
    "short": "growth engine",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "f\u03c38(z) \u2014 vekstrate ganger amplitude \u00b7 perspektiv: paradigm",
    "what": "observasjonssiden er RSD/ELG/QSO; motoren regner veksten \u2014 proxy chain: RSD-m\u00e5linger -> f\u03c38 (observasjon) -> f\u03c38 -> EFC-parametre (inferens)",
    "how": "Buffer role: strukturens materie-buffer vokser gjennom koplingsfeltet \u2014 modellert, ikke m\u00e5lt\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-lensing-engine",
    "code": "LN",
    "name": "efc.lensing_engine",
    "short": "lensing engine",
    "group": "kosmos",
    "gx": 6.3,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "kappa(theta) \u2014 konvergens som funksjon av vinkelposisjon \u00b7 perspektiv: paradigm",
    "what": "observasjonssiden er svak linsing; motoren regner ingenting enn\u00e5 \u2014 proxy chain: shear -> kappa (observasjon) -> kappa -> EFC-parametre (venter p\u00e5 fysikken)",
    "how": "Buffer role: strukturens masse-buffer b\u00f8yer lyset \u2014 mekanismen er observert, motoren\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-cluster-engine",
    "code": "CL",
    "name": "efc.cluster_engine",
    "short": "cluster engine",
    "group": "kosmos",
    "gx": 8.7,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "n(M,z) \u2014 halomassefunksjonen \u00b7 perspektiv: paradigm",
    "what": "observasjonssiden er hopetellinger; motoren regner ingenting enn\u00e5 \u2014 proxy chain: hopetelling -> n(M,z) (observasjon) -> n(M,z) -> EFC-parametre (venter p\u00e5 fysikken)",
    "how": "Buffer role: hopene er strukturens tetteste buffere \u2014 observert, ikke modellert her enn\u00e5. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-fluxus",
    "code": "HF",
    "name": "homo.fluxus",
    "short": "fluxus",
    "group": "ghost",
    "gx": 11.1,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "R \u2014 den indre refleksjonskoeffisienten \u00b7 perspektiv: paradigm",
    "what": "hf1\u2013hf5-observasjonskravene (falsifiserbare p\u00e5stander i rammeverket) \u2014 proxy chain: kohrens-proxyer \u2192 R (inferens) -> R \u2192 flytobjekt/flytsubjekt (terskel)",
    "how": "Buffer role: kroppens buffere (termisk, kjemisk, nevral) holder flytm\u00f8nsteret stabilt under\u2026 Epistemic: hypotese / proxy / minoritet. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-homeostase-buffer",
    "code": "HO",
    "name": "homo.homeostase_buffer",
    "short": "homeostase\u2026",
    "group": "ghost",
    "gx": 13.5,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "avvik fra setpunkt (\u0394T, \u0394pH, \u0394glukose) \u00b7 perspektiv: academia",
    "what": "fysiologiske sensorer; her er noden beskrivelse, ikke sensor \u2014 proxy chain: sensor \u2192 avvik -> avvik \u2192 kompensasjonsrespons",
    "how": "Buffer role: selve bufferen: kapasitet som demper endring \u2014 den brede logikken i ren form. Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "Levin 2019 (biologi) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av feltet."
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-feber-regime",
    "code": "FE",
    "name": "homo.feber_regime",
    "short": "feber regime",
    "group": "ghost",
    "gx": 1.5,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "kroppstemperatur mot setpunkt \u00b7 perspektiv: academia",
    "what": "termometer + pyrogen-mark\u00f8rer; her beskrivelse \u2014 proxy chain: pyrogener \u2192 setpunktsskifte -> temperatur \u2192 avstand til nytt setpunkt",
    "how": "Buffer role: bufferen bytter TARGET, ikke kapasitet \u2014 det er selve regimeskiftet. Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "fysiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av feltet."
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-aksjonspotensial",
    "code": "AP",
    "name": "homo.aksjonspotensial",
    "short": "aksjonspotensi\u2026",
    "group": "ghost",
    "gx": 3.9,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "membranpotensialet V(t) mot terskelen \u00b7 perspektiv: academia",
    "what": "fysiologisk m\u00e5ling; her beskrivelse \u2014 proxy chain: ionestr\u00f8mmer \u2192 V(t) -> V(t) mot V_th \u2192 spike",
    "how": "Buffer role: membranen er bufferen: gradienten lades og holdes til utl\u00f8sning. Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "nevrofysiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-hjerte-syklus",
    "code": "HJ",
    "name": "homo.hjerte_syklus",
    "short": "hjerte syklus",
    "group": "ghost",
    "gx": 6.3,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "slagvolum, frekvens, minuttvolum \u00b7 perspektiv: academia",
    "what": "fysiologisk m\u00e5ling; her beskrivelse \u2014 proxy chain: EKG \u2192 elektrisk syklus -> ekko \u2192 mekanisk syklus",
    "how": "Buffer role: ventriklene er bufferne: de fylles og t\u00f8mmes rytmisk \u2014 aldri til null, aldri\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "kardiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av feltet."
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-genregulering",
    "code": "GN",
    "name": "homo.genregulering",
    "short": "genregulering",
    "group": "ghost",
    "gx": 8.7,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "uttrykksniv\u00e5 per gen (mRNA/protein) \u00b7 perspektiv: academia",
    "what": "sekvensering; her beskrivelse av reguleringslogikken \u2014 proxy chain: TF-binding \u2192 uttrykk -> epigenetisk merke \u2192 terskelskifte",
    "how": "Buffer role: genomet holder reguleringsprogrammene lagret \u2014 en kapasitet som demper\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "molekylaerbiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. Atlaset bruker den som etablert, ikke som egen\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-cellesyklus",
    "code": "CY",
    "name": "homo.cellesyklus",
    "short": "cellesyklus",
    "group": "ghost",
    "gx": 11.1,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "fase per celle (G1/S/G2/M) \u00b7 perspektiv: academia",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: DNA-innhold \u2192 fase -> CDK/cyklin \u2192 sjekkpunkt-status",
    "how": "Buffer role: sjekkpunktene er bufferne: de holder syklusen til betingelsene er oppfylt. Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "cellebiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-metabolisme",
    "code": "ME",
    "name": "homo.metabolisme",
    "short": "metabolisme",
    "group": "ghost",
    "gx": 13.5,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "ATP/ADP-forhold, O\u2082-forbruk, substrat-fluks \u00b7 perspektiv: academia",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: O\u2082-forbruk \u2192 fluks -> ATP/ADP \u2192 reguleringsstatus",
    "how": "Buffer role: ATP-poolen og glykogenet er bufferne: kort- og langtidslager som demper\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "biokjemi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av feltet."
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-solar-flare-engine",
    "code": "SF",
    "name": "efc.solar_flare_engine",
    "short": "solar flare\u2026",
    "group": "ghost",
    "gx": 1.5,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "oppladningstid, utlost energi, GOES-klasse \u00b7 perspektiv: paradigm",
    "what": "SolarFlareEngine (efc_inference/engine/solar_flare.py) \u2014 proxy chain: B -> magnetisk energi (E = B^2/(2 mu_0) * V) -> energi -> GOES-klasse (kalibreringsproxy\u2026",
    "how": "Buffer role: magnetfeltet er bufferen: energien lades og holdes til terskelen krysses. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-jordskjelv-engine",
    "code": "JS",
    "name": "efc.jordskjelv_engine",
    "short": "jordskjelv\u2026",
    "group": "ghost",
    "gx": 3.9,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "gjentakelsestid, seismisk moment, moment-magnitude \u00b7 perspektiv: paradigm",
    "what": "JordskjelvEngine (efc_inference/engine/jordskjelv.py) \u2014 proxy chain: lade-rate -> gjentakelsestid -> spenningsfall -> slipp -> M0 -> Mw (Kanamori)",
    "how": "Buffer role: forkastningen er bufferen: spenningen lades og holdes til terskelen krysses. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-immunologi",
    "code": "IM",
    "name": "homo.immunologi",
    "short": "immunologi",
    "group": "ghost",
    "gx": 6.3,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "aktiveringsstatus, antistofftiter, hukommelsespopulasjon \u00b7 perspektiv: academia",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: faresignaler + antigenkonsentrasjon -> aktivering -> titer -> hukommelse",
    "how": "Buffer role: hukommelsen er bufferen: den senker terskelen og gj\u00f8r neste respons raskere. Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "immunologi (standard: Janeway/Matzinger) \u2014 fagfellevurdert og laerebokkanonisert. Atlaset bruker den som etablert, ikke\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-sovn-vaaken",
    "code": "SV",
    "name": "homo.sovn_vaaken",
    "short": "sovn vaaken",
    "group": "ghost",
    "gx": 8.7,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "s\u00f8vnstadium (v\u00e5ken/NREM/REM), homeostatisk trykk \u00b7 perspektiv: academia",
    "what": "klinisk m\u00e5ling; her beskrivelse \u2014 proxy chain: EEG-synkroni -> stadium -> v\u00e5kenhetsvarighet -> homeostatisk trykk",
    "how": "Buffer role: s\u00f8vnbehovet er bufferen: det akkumuleres i v\u00e5ken og t\u00f8mmes i s\u00f8vn \u2014 hjernens\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "sovnfysiologi (standard: Borbely, Steriade) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-okologi",
    "code": "OE",
    "name": "homo.okologi",
    "short": "okologi",
    "group": "ghost",
    "gx": 11.1,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "tilstandsvariabler (n\u00e6ringsstoffer, dekning, artssammensetning) \u00b7 perspektiv: academia",
    "what": "\u00f8kologisk overv\u00e5king; her beskrivelse \u2014 proxy chain: n\u00e6ringsstoffer -> tilstand -> dekning -> regime",
    "how": "Buffer role: \u00f8kosystemets bufferevne (resiliens) demper forstyrrelser \u2014 til bufferen er brukt\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "regime-shift-okologi (Scheffer) \u2014 fagfellevurdert og laerebokkanonisert. Atlaset bruker den som etablert, ikke som egen\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-evolusjon",
    "code": "EV",
    "name": "homo.evolusjon",
    "short": "evolusjon",
    "group": "ghost",
    "gx": 13.5,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "endringstakt i fenotype/art (morfologiske og molekyl\u00e6re rater) \u00b7 perspektiv: academia",
    "what": "paleontologisk/genomisk m\u00e5ling; her beskrivelse \u2014 proxy chain: fossilrekke -> morfologisk rate -> molekyl\u00e6r avstand -> tid siden splitt",
    "how": "Buffer role: stasis er holding: seleksjon og utviklingsbegrensninger holder fenotypen \u2014 til\u2026 Epistemic: stottet / replikert / institusjonell. S-axis: regime S~0.5 \u00b7 klarhet C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
      "klarhet": "C(S) ved S~0.5: differensiert klarhet i senuniversets biologiske mellomlag \u2014 observat\u00f8ren ser et smalt vindu.",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "evolusjonsbiologi (standard) \u2014 fagfellevurdert og laerebokkanonisert. ANALOGIEN til EFC er vaar egen og baeres ikke av\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-mu-kz-engine",
    "code": "MK",
    "name": "efc.mu_kz_engine",
    "short": "mu kz engine",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "mu(k,z) \u2014 effektiv Poisson-kobling \u00b7 perspektiv: paradigm",
    "what": "MuKZEngine (efc_inference/engine/mu_kz.py) \u2014 proxy chain: bakgrunns-innganger -> eps_F, eps_K, R -> eps_F, eps_K, R -> mu (eq. 28)",
    "how": "Buffer role: gyldighetsomraadet er modulens buffer: kvasi-statisk sub-horisont \u2014 utenfor det\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-romvaer-engine",
    "code": "RV",
    "name": "efc.romvaer_engine",
    "short": "romvaer engine",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "forventet Kp, stormniv\u00e5, utladningsbane \u00b7 perspektiv: paradigm",
    "what": "RomvaerEngine (efc_inference/engine/romvaer.py) \u2014 proxy chain: Bz, v -> ladestr\u00f8m (korrelasjonsproxy) -> Kp -> G-niv\u00e5 (NOAA-skalaen)",
    "how": "Buffer role: magnetosf\u00e6ren er bufferen: den holder ladningen fra solvinden til stormen\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-oekonomi-engine",
    "code": "OK",
    "name": "efc.oekonomi_engine",
    "short": "oekonomi\u2026",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "finansregime (hedge/spekulativ/ponzi), gjeldsgrad-drift \u00b7 perspektiv: paradigm",
    "what": "OekonomiEngine (efc_inference/engine/oekonomi.py) \u2014 proxy chain: gjeldsgrad -> regime (to terskler) -> stabile \u00e5r -> gjeldsgrad-drift (Minsky-momentet)",
    "how": "Buffer role: de stabile \u00e5rene er bufferen: tilliten bygges opp og gjelden akkumuleres \u2014 helt\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-orbital-engine",
    "code": "OR",
    "name": "efc.orbital_engine",
    "short": "orbital engine",
    "group": "kosmos",
    "gx": 8.7,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "periode, hastighet, spesifikk energi, Hill-sf\u00e6re \u00b7 perspektiv: paradigm",
    "what": "OrbitalEngine (efc_inference/engine/orbital.py) \u2014 proxy chain: a, e -> T (Kepler) -> a, r -> v (vis-viva) -> eps = -GM/(2a) -> holding/release",
    "how": "Buffer role: Hill-sf\u00e6ren er banens TILN\u00c6RMEDE stabilitetsbuffer: innenfor er sentralkroppens\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-klima-engine",
    "code": "KL",
    "name": "efc.klima_engine",
    "short": "klima engine",
    "group": "kosmos",
    "gx": 11.1,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "likevektstemperatur, tidskonstant, regimebryter \u00b7 perspektiv: paradigm",
    "what": "KlimaEngine (efc_inference/engine/klima.py) \u2014 proxy chain: solarkonstant + albedo -> innstr\u00e5ling -> eps sigma T^4 -> utstr\u00e5ling -> C -> bufferens\u2026",
    "how": "Buffer role: havets varmekapasitet er bufferen: den demper og forsinker alle forstyrrelser\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-samfunn-engine",
    "code": "SA",
    "name": "efc.samfunn_engine",
    "short": "samfunn engine",
    "group": "samfunn",
    "gx": 13.5,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "R0, utbruddsstatus, epidemi-banen \u00b7 perspektiv: paradigm",
    "what": "SamfunnEngine (efc_inference/engine/samfunn.py) \u2014 proxy chain: beta, gamma -> R0 -> R0 -> utbruddsstatus (terskel 1) -> SIR-banen -> kurveformen",
    "how": "Buffer role: reservoaret av mottagelige er bufferen: utbruddet t\u00f8mmer den, og n\u00e5r den er tom\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-tidevann-engine",
    "code": "TI",
    "name": "efc.tidevann_engine",
    "short": "tidevann\u2026",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "tidevannsakselerasjon, tidevannsh\u00f8yde, Roche-grense\u2026 \u00b7 perspektiv: paradigm",
    "what": "TidevannEngine (efc_inference/engine/tidevann.py) \u2014 proxy chain: m_obj, r -> a_t (differensiell gravitasjon) -> a_t -> h (\u00e5pent-hav-proxy) -> perioder ->\u2026",
    "how": "Buffer role: havet er bufferen: det l\u00f8ftes og senkes i den periodiske syklusen uten \u00e5 bryte\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-transient-engine",
    "code": "TR",
    "name": "efc.transient_engine",
    "short": "transient\u2026",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "holdetid, utlost energi, lettkurvens form \u00b7 perspektiv: paradigm",
    "what": "TransientEngine (efc_inference/engine/transient.py) \u2014 proxy chain: kjernemasse -> bindingsenergi (E = G*M^2/R) -> bindingsenergi -> utlost energi ved\u2026",
    "how": "Buffer role: kjernen er bufferen: massen bygges og holdes oppe til stabilitetsgrensen krysses. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "v\u00e5r egen ramme \u2014 b\u00e6res av oss, ikke av feltet; narrativet er v\u00e5rt eget, og det er en styrke \u00e5 vite det"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-enerflyt-engine",
    "code": "EF",
    "name": "efc.enerflyt_engine",
    "short": "enerflyt\u2026",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "bufferen S og driften dS/dt = P - C - L \u00b7 perspektiv: paradigm",
    "what": "statistikkbyraaer og nettoperatoerer \u2014 proxy chain: registrert produksjon -> forbruk -> bufferanslag \u2014 alle er regnskaps-proxyer, ikke direkte\u2026",
    "how": "Buffer role: S er samfunnets energibuffer \u2014 holdingen som absorberer ubalansen mellom\u2026 Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-grid-higgs",
    "code": "GH",
    "name": "efc.grid_higgs",
    "short": "grid higgs",
    "group": "grid",
    "gx": 8.7,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Grid-Higgs-rammen: entropisk og strukturell teori for gravitasjon\u2026 \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: verket er bufferen som holder bro-hypotesen til den testes. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": [
      "efc.grid_higgs: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-gr-qft-bro",
    "code": "GQ",
    "name": "efc.gr_qft_bro",
    "short": "gr qft bro",
    "group": "grid",
    "gx": 11.1,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Den termodynamiske broen mellom generell relativitet og\u2026 \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: verket er bufferen som holder bro-hypotesen til den testes. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": [
      "efc.gr_qft_bro: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-double-slit",
    "code": "DS",
    "name": "efc.double_slit",
    "short": "double slit",
    "group": "grid",
    "gx": 13.5,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Dobbeltspalten som grid-oppl\u00f8sningsfenomen: ontologisk utvidelse\u2026 \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: verket er bufferen som holder bro-hypotesen til den testes. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": [
      "efc.double_slit: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "efc-grid-mikrofysikk",
    "code": "GM",
    "name": "efc.grid_mikrofysikk",
    "short": "grid\u2026",
    "group": "grid",
    "gx": 1.5,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Fra grid-mikrofysikk til den radiale akselerasjonsrelasjonen \u2014 minimal\u2026 \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: verket er bufferen som holder bro-hypotesen til den testes. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-grid-mikro-engine",
    "code": "GE",
    "name": "efc.grid_mikro_engine",
    "short": "grid mikro\u2026",
    "group": "grid",
    "gx": 3.9,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Gamma(rho) og Deff(rho) \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 mikrofysisk avledning, modellavhengig \u2014 proxy chain: tetthet -> grid-mode-okkupering -> entropi-produksjon \u2014 ren teori-kjede",
    "how": "Buffer role: grid-modene er bufferen \u2014 okkuperte moders entropi lader opp med tettheten og\u2026 Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-sort-hull",
    "code": "SH",
    "name": "efc.sort_hull",
    "short": "sort hull",
    "group": "grid",
    "gx": 6.3,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "sorte hull som entropisk grense i Grid-Higgs-rammen \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 teoretisk \u2014 proxy chain: DOI -> verk -> avledning",
    "how": "Buffer role: BH som entropisk buffer i grid-teorien. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme"
      ]
    ],
    "cond": [
      "efc.sort_hull: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "kjemi-periodesystemet",
    "code": "PS",
    "name": "kjemi.periodesystemet",
    "short": "periodesysteme\u2026",
    "group": "struktur",
    "gx": 8.7,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "periodesystemets struktur (118 grunnstoff) \u00b7 perspektiv: academia",
    "what": "spektroskopi og kjemisk analyse \u2014 proxy chain: atomnummer -> periodisitet \u2014 konsensus-kartlegging",
    "how": "Buffer role: periodesystemet er bufferen som holder kjemien ordnet. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "academia"
      ],
      [
        "Epistemics",
        "stottet / replikert / institusjonell"
      ],
      [
        "Social mechanism",
        "IUPAC-konsensus, l\u00e6rebok-kanonisering"
      ]
    ],
    "cond": [
      "kjemi.periodesystemet: ingen buss-vei \u2014 emnet finnes ikke som domene i snapshotet (maalt 2026-09-18)"
    ]
  },
  {
    "id": "verden-hav",
    "code": "HA",
    "name": "verden.hav",
    "short": "hav",
    "group": "broer",
    "gx": 11.1,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "havtemperatur \u00b7 perspektiv: consensus",
    "what": "boeyestasjoner (tides & currents) \u2014 proxy chain: stasjon -> temperatur -> hav-energi",
    "how": "Buffer role: havet som varmebuffer i klimaet. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "NOAA-stasjonsnettet som konsensus-kanal"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-biosfaere",
    "code": "BI",
    "name": "verden.biosfaere",
    "short": "biosfaere",
    "group": "broer",
    "gx": 13.5,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "arts-tellinger (planteriket) \u00b7 perspektiv: consensus",
    "what": "taksonomisk soek \u2014 proxy chain: soek -> telling -> fotavtrykk",
    "how": "Buffer role: biosfaeren som energiflyt-buffer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "GBIF-taksonomien som konsensus-kanal"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-jord-vulkan",
    "code": "VU",
    "name": "kosmos.jord.vulkan",
    "short": "vulkan",
    "group": "broer",
    "gx": 1.5,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "vulkantilstand \u00b7 perspektiv: consensus",
    "what": "statusliste (alertLevel) \u2014 proxy chain: alertLevel -> aktivitet -> regime-status",
    "how": "Buffer role: vulkaner som jordas termiske buffer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "USGS-statuslisten som konsensus-kanal"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-vaer",
    "code": "VV",
    "name": "verden.vaer",
    "short": "vaer",
    "group": "ghost",
    "gx": 3.9,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "temperatur, vind, trykk, skydekke og fuktighet \u00b7 perspektiv: consensus",
    "what": "ett sted i ett gyldighetsvindu; baade forventet og utfall i samme melding \u2014 proxy chain: prognose -> forventet -> METAR-maaling -> utfall -> avvik = utfall minus forventet, per\u2026",
    "how": "Buffer role: atmosfaeren som buffer mellom prognose og virkelighet. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "MET Norway-prognose mot METAR-maaling \u2014 to uavhengige institusjonelle kanaler"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-asteroider",
    "code": "KA",
    "name": "kosmos.asteroider",
    "short": "asteroider",
    "group": "ghost",
    "gx": 6.3,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "treffsannsynlighet og Palermo-kumulativ per objekt \u00b7 perspektiv: consensus",
    "what": "Sentry-listen selv; oppgjoeret leser hele listen som fasit \u2014 proxy chain: bane -> treffsannsynlighet (prediksjon) -> liste -> revidert/utelukket (oppgjoer)",
    "how": "Buffer role: Sentry-listen er bufferen som holder risikobildet stabilt mellom revisjoner. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "JPL Sentry som konsensus-kanal"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-efc-background-engine",
    "code": "EE",
    "name": "efc.efc_background_engine",
    "short": "efc background\u2026",
    "group": "ghost",
    "gx": 8.7,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "H(z) og bakgrunns-feltene phi, phi_dot, rho_m, lambda_dot \u00b7 perspektiv: paradigm",
    "what": "EFCBackgroundSolver (efc_inference/engine/efc_background.py) \u2014 proxy chain: parametre (alpha, k0, omega_crit, gamma0, V0) -> ODE-system -> ODE-system -> tilstand (a\u2026",
    "how": "Buffer role: lambda er bufferen: responsfeltet som holder flyt-regnskapet naar phi ikke kan\u2026 Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / ingen / minoritet"
      ],
      [
        "Social mechanism",
        "vaar egen ramme \u2014 baeres av oss, ikke av feltet"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-lag-s",
    "code": "LS",
    "name": "efc.lag_s",
    "short": "lag s",
    "group": "ghost",
    "gx": 11.1,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "strukturen som energy-flow-feltet holder oppe \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 strukturen er avledet fra feltet, ikke maalt som struktur \u2014 proxy chain: energy-flow-felt -> tetthetsgradient -> potensial -> struktur -> struktur ->\u2026",
    "how": "Buffer role: haloen selv er bufferen: den holder formen mens feltet varierer under. Epistemic: hypotese / proxy / minoritet. S-axis: regime S>0 \u00b7 sektor S \u00b7 klarhet C(S) ved S>0: strukturell klarhet \u2014 formen leser energiflyten i likevekt \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S>0",
      "sector": "S",
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S>0: strukturell klarhet \u2014 formen leser energiflyten i likevekt",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "vaar ramme \u2014 erstatter mork materie, som er et MINORITETSstandpunkt mot LCDM"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-lag-d",
    "code": "LD",
    "name": "efc.lag_d",
    "short": "lag d",
    "group": "ghost",
    "gx": 13.5,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "energy-flow-feltet J_mu og dets divergens \u00b7 perspektiv: paradigm",
    "what": "aksjonen (master-spec, eq. 1) \u2014 proxy chain: aksjon -> feltligning -> J_mu -> ekspansjonshistorie -> J_mu -> Sigma (kildeledd)",
    "how": "Buffer role: F(phi) og K(rho) demper avvik fra LCDM avhengig av feltverdi. Epistemic: hypotese / proxy / minoritet. S-axis: regime S>0 \u00b7 sektor D \u00b7 klarhet C(S) ved S>0: dynamisk klarhet \u2014 tid, rom og hastighet emergerer fra energy flow under S \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S>0",
      "sector": "D",
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S>0: dynamisk klarhet \u2014 tid, rom og hastighet emergerer fra energy flow under S",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "vaar ramme \u2014 erstatter mork energi, som er konsensus i LCDM"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-lag-c0",
    "code": "C0",
    "name": "efc.lag_c0",
    "short": "lag c0",
    "group": "ghost",
    "gx": 1.5,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "entropi-feltet S og dets grenser \u00b7 perspektiv: paradigm",
    "what": "ingen direkte \u2014 S er et felt, ikke en maaling \u2014 proxy chain: S -> Omega-hat (differensiering) og kappa-hat (integrasjon) -> Omega x kappa -> C\u2026",
    "how": "Buffer role: entropien selv: den absorberer energi uten at strukturen endres, til grensen\u2026 Epistemic: hypotese / proxy / minoritet. S-axis: regime S->1 \u00b7 sektor C \u00b7 klarhet C(S) ved S->1: mettet klarhet lokalt \u2014 propofol-EEG (Omega, kappa) m\u00e5ler klarhetsvariasjon i liten skala \u00b7 EBE claim validity = f(S, L, proxy-chain).",
    "sAxis": {
      "regime": "S->1",
      "sector": "C",
      "ebe": "claim validity = f(S, L, proxy-chain)",
      "klarhet": "C(S) ved S->1: mettet klarhet lokalt \u2014 propofol-EEG (Omega, kappa) m\u00e5ler klarhetsvariasjon i liten skala",
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "paradigm"
      ],
      [
        "Epistemics",
        "hypotese / proxy / minoritet"
      ],
      [
        "Social mechanism",
        "vaar ramme \u2014 broen kosmologi-til-kognisjon er ikke etablert"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-gammaglimt",
    "code": "KG",
    "name": "kosmos.gammaglimt",
    "short": "gammaglimt",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "varsler om transienter i sanntid, fra bakke og rom \u00b7 perspektiv: consensus",
    "what": "Fermi, Swift og bakkebaserte teleskoper \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom\u2026 Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "GCN varsler naar noe DETEKTERES; andelen maaler instrumentets dekning, ikke himmelens aktivitet"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-interstellart",
    "code": "KI",
    "name": "kosmos.interstellart",
    "short": "interstellart",
    "group": "kosmos",
    "gx": 6.3,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Det interstellare er kjent fra et faatall objekter; andelen hviler paa en haandfull maalinger"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-maane",
    "code": "MA",
    "name": "kosmos.maane",
    "short": "maane",
    "group": "kosmos",
    "gx": 8.7,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "baneposisjoner regnet fra DE441-ephemeriden \u00b7 perspektiv: consensus",
    "what": "DE441-ephemeriden; ingen instrument leste av \u2014 proxy chain: observasjoner (historiske) -> DE441-tilpasning -> posisjon",
    "how": "Buffer role: JPL Horizons er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "Samme ephemeride som planetsystemet \u2014 to domener, ett regnestykke"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-noeytrinoer",
    "code": "NO",
    "name": "kosmos.noeytrinoer",
    "short": "noeytrinoer",
    "group": "kosmos",
    "gx": 11.1,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "varsler om transienter i sanntid, fra bakke og rom \u00b7 perspektiv: consensus",
    "what": "Fermi, Swift og bakkebaserte teleskoper \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom\u2026 Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Noytrinodeteksjon er en haandfull anlegg verden over \u2014 andelen maaler anleggene, ikke fluksene"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-planetsystem",
    "code": "PL",
    "name": "kosmos.planetsystem",
    "short": "planetsystem",
    "group": "kosmos",
    "gx": 13.5,
    "gy": 32.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "baneposisjoner regnet fra DE441-ephemeriden \u00b7 perspektiv: consensus",
    "what": "DE441-ephemeriden; ingen instrument leste av \u2014 proxy chain: observasjoner (historiske) -> DE441-tilpasning -> posisjon",
    "how": "Buffer role: JPL Horizons er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / proxy / institusjonell"
      ],
      [
        "Social mechanism",
        "JPL DE441 er en TILPASNING til historiske observasjoner; andelen maaler ephemeriden, ikke himmelen"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-roentgentransienter",
    "code": "KR",
    "name": "kosmos.roentgentransienter",
    "short": "roentgentransi\u2026",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "varsler om transienter i sanntid, fra bakke og rom \u00b7 perspektiv: consensus",
    "what": "Fermi, Swift og bakkebaserte teleskoper \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom\u2026 Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Roentgentransienter krever instrumenter som ser i det baandet; uten dem finnes de ikke i dataene"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-romfart",
    "code": "RF",
    "name": "kosmos.romfart",
    "short": "romfart",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Oppskytingsdata er institusjonelle og nasjonale; det som ikke annonseres, telles ikke"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-stjerner",
    "code": "ST",
    "name": "kosmos.stjerner",
    "short": "stjerner",
    "group": "kosmos",
    "gx": 6.3,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Stjernedata kommer fra surveyer med hver sin seleksjon; andelen baerer surveyens blikk"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-uklassifisert",
    "code": "UK",
    "name": "kosmos.uklassifisert",
    "short": "uklassifisert",
    "group": "kosmos",
    "gx": 8.7,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "varsler om transienter i sanntid, fra bakke og rom \u00b7 perspektiv: consensus",
    "what": "Fermi, Swift og bakkebaserte teleskoper \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom\u2026 Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Det uklassifiserte er definert ved at det IKKE passer \u2014 andelen maaler skjemaets grense, ikke fenomenet"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-arbeid",
    "code": "AR",
    "name": "verden.arbeid",
    "short": "arbeid",
    "group": "samfunn",
    "gx": 11.1,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "arbeidsmarkeds- og sosialstatistikk for Europa \u00b7 perspektiv: consensus",
    "what": "nasjonale statistikkbyr\u00e5er, harmonisert \u2014 proxy chain: nasjonal statistikk -> harmonisering -> indikator",
    "how": "Buffer role: Eurostat er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Eurostat og ILO maaler formell arbeidskraft; den uformelle okonomien er strukturelt fravaerende"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-demografi",
    "code": "DE",
    "name": "verden.demografi",
    "short": "demografi",
    "group": "samfunn",
    "gx": 13.5,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Folkeregistre er ujevnt utbygd; andelen maaler registreringen like mye som befolkningen"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-finans",
    "code": "FI",
    "name": "verden.finans",
    "short": "finans",
    "group": "samfunn",
    "gx": 1.5,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Finansielle stroemmer beveger seg raskere enn statistikken; andelen er et etterslep"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-geopolitikk",
    "code": "VG",
    "name": "verden.geopolitikk",
    "short": "geopolitikk",
    "group": "samfunn",
    "gx": 3.9,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Geopolitikk er et spraak om maktforhold; kodingsskjemaet velger hva som faar en etikett"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-handel",
    "code": "VH",
    "name": "verden.handel",
    "short": "handel",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Handel telles over grenser med tollskjema \u2014 tjenester og digitalt bytte faller utenfor"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-helse",
    "code": "HE",
    "name": "verden.helse",
    "short": "helse",
    "group": "samfunn",
    "gx": 8.7,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "WHO og nasjonale helseregistre setter hva som telles som helse; det som ikke rapporteres, finnes ikke i andelen"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-infrastruktur",
    "code": "VI",
    "name": "verden.infrastruktur",
    "short": "infrastruktur",
    "group": "samfunn",
    "gx": 11.1,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Infrastruktur telles naar den bygges og naar den feiler; den stille virkerdag er usynlig"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-kommunikasjon",
    "code": "KO",
    "name": "verden.kommunikasjon",
    "short": "kommunikasjon",
    "group": "samfunn",
    "gx": 13.5,
    "gy": 38.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Mediedekning er skjevt fordelt \u2014 rike land melder mer, saa andelen maaler mediet, ikke hendelsen"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-lov",
    "code": "LO",
    "name": "verden.lov",
    "short": "lov",
    "group": "samfunn",
    "gx": 1.5,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Lovgivning registreres naar den vedtas, ikke naar den virker \u2014 og ikke i land uten frie registre"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-militaer",
    "code": "MI",
    "name": "verden.militaer",
    "short": "militaer",
    "group": "samfunn",
    "gx": 3.9,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Milit\u00e6re forhold rapporteres av statene selv; det hemmelige er usynlig i korpuset, ikke i verden"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-politikk",
    "code": "PO",
    "name": "verden.politikk",
    "short": "politikk",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "GDELT koder verdens nyhetsstroem \u2014 andelen maaler hva som BLE skrevet om, ikke hva som skjedde"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-sikkerhet",
    "code": "SI",
    "name": "verden.sikkerhet",
    "short": "sikkerhet",
    "group": "samfunn",
    "gx": 8.7,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Sikkerhetshendelser rapporteres naar de er spektakulaere; den stille hverdagen telles ikke"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-teknologi",
    "code": "TE",
    "name": "verden.teknologi",
    "short": "teknologi",
    "group": "samfunn",
    "gx": 11.1,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Teknologinyheter er framtidsorientert: andelen maaler forventning, ikke utbredelse"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-transport",
    "code": "VT",
    "name": "verden.transport",
    "short": "transport",
    "group": "samfunn",
    "gx": 13.5,
    "gy": 40.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Transport maales der den registreres \u2014 uformell og lokal transport er usynlig"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-utdanning",
    "code": "UT",
    "name": "verden.utdanning",
    "short": "utdanning",
    "group": "samfunn",
    "gx": 1.5,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "globale nyhetsstr\u00f8mmer kodet til tema, akt\u00f8r og sted \u00b7 perspektiv: consensus",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Utdanningsstatistikk maaler skolegang, ikke laering \u2014 og land som ikke rapporterer, blir usynlige i samme andel"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-galakser-mast",
    "code": "KM",
    "name": "kosmos.galakser_mast",
    "short": "galakser mast",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "astronomiske observasjoner og katalogiserte kilder \u00b7 perspektiv: consensus",
    "what": "MAST CAOM observasjonskatalog \u2014 proxy chain: instrumentmetadata -> CAOM-observasjon -> katalogisert astronomisk kilde",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "MAST/CAOM b\u00e6rer m\u00e5lepraksisen og str\u00f8mmen gj\u00f8r den tilgjengelig; dette er en sosial kanal, ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-klima-gdelt",
    "code": "GG",
    "name": "verden.klima_gdelt",
    "short": "klima gdelt",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "klimarelatert omtale kodet i globale nyhetsdokumenter \u00b7 perspektiv: consensus",
    "what": "GDELT GKG-koding av dokument, tema, akt\u00f8r og sted \u2014 proxy chain: nyhetsdokument -> GKG-koder -> klimarelatert observasjon",
    "how": "Buffer role: GDELT-korpuset holder kodingen mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "GDELT-prosjektet b\u00e6rer m\u00e5lepraksisen og str\u00f8mmen gj\u00f8r den tilgjengelig; dette er en sosial kanal, ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-klima-worldbank",
    "code": "WB",
    "name": "verden.klima_worldbank",
    "short": "klima\u2026",
    "group": "samfunn",
    "gx": 8.7,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "klima- og utviklingsindikatorer per land og \u00e5r \u00b7 perspektiv: consensus",
    "what": "World Bank-indikatorenes innrapporterte og harmoniserte datasett \u2014 proxy chain: nasjonal rapportering -> harmonisering -> indikatorverdi -> tilstandsmelding",
    "how": "Buffer role: harmoniserte indikatorserier holder tilstanden mellom \u00e5rlige oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "World Bank b\u00e6rer klimaets institusjonelle m\u00e5lepraksis; str\u00f8mmen gj\u00f8r land- og \u00e5rsindikatorene tilgjengelige, men dette\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-miljo-mikrobiom",
    "code": "MX",
    "name": "verden.miljo_mikrobiom",
    "short": "miljo\u2026",
    "group": "samfunn",
    "gx": 11.1,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "microbial taxa and functional profiles across sampled environments \u00b7 perspektiv: consensus",
    "what": "MGnify microbiome profiles \u2014 proxy chain: sample -> sequence processing -> taxonomic and functional profile -> state message",
    "how": "Buffer role: MGnify-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "MGnify b\u00e6rer m\u00e5lepraksisen og str\u00f8mmen gj\u00f8r den tilgjengelig; dette er en sosial kanal, ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-miljo-gdelt",
    "code": "GY",
    "name": "verden.miljo_gdelt",
    "short": "miljo gdelt",
    "group": "samfunn",
    "gx": 13.5,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "environment-related coverage encoded in global news documents \u00b7 perspektiv: consensus",
    "what": "GDELT GKG coding of documents, themes, actors and places \u2014 proxy chain: news document -> GKG codes -> environmental observation",
    "how": "Buffer role: GDELT-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "GDELT b\u00e6rer milj\u00f8ets nyhetsm\u00e5lepraksis; str\u00f8mmen gj\u00f8r kodet omtale tilgjengelig, men dette er ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-oekonomi-worldbank",
    "code": "OX",
    "name": "verden.oekonomi_worldbank",
    "short": "oekonomi\u2026",
    "group": "samfunn",
    "gx": 1.5,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "economic indicators by country and year \u00b7 perspektiv: consensus",
    "what": "World Bank reported and harmonized indicator datasets \u2014 proxy chain: national reporting -> harmonization -> indicator value -> state message",
    "how": "Buffer role: World Bank-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "World Bank b\u00e6rer \u00f8konomiens institusjonelle m\u00e5lepraksis; str\u00f8mmen gj\u00f8r land- og \u00e5rsindikatorene tilgjengelige, men dette\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-oekonomi-imf",
    "code": "IX",
    "name": "verden.oekonomi_imf",
    "short": "oekonomi imf",
    "group": "samfunn",
    "gx": 3.9,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "macroeconomic projections and scenario indicators \u00b7 perspektiv: consensus",
    "what": "IMF DataMapper projections and macroeconomic scenarios \u2014 proxy chain: institutional projection -> DataMapper series -> forecast reading",
    "how": "Buffer role: IMF DataMapper-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "IMF DataMapper b\u00e6rer m\u00e5lepraksisen og str\u00f8mmen gj\u00f8r den tilgjengelig; dette er en sosial kanal, ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-oekonomi-gdelt",
    "code": "OY",
    "name": "verden.oekonomi_gdelt",
    "short": "oekonomi gdelt",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "economic coverage encoded in global news documents \u00b7 perspektiv: consensus",
    "what": "GDELT GKG coding of documents, themes, actors and places \u2014 proxy chain: news document -> GKG codes -> economic observation",
    "how": "Buffer role: GDELT-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "GDELT b\u00e6rer \u00f8konomiens nyhetsm\u00e5lepraksis; str\u00f8mmen gj\u00f8r kodet omtale tilgjengelig, men dette er ikke sannheten selv"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-romvaer-swpc",
    "code": "RK",
    "name": "kosmos.romvaer_swpc",
    "short": "romvaer swpc",
    "group": "kosmos",
    "gx": 8.7,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Kp-tilstand og stormniv\u00e5 \u00b7 perspektiv: consensus",
    "what": "SWPC Kp-m\u00e5ling \u2014 proxy chain: tilstand.swpc-kp -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "SWPCs operative Kp-skala og romvaerprognoser baerer praksisen; str\u00f8mmen gj\u00f8r tilstanden lesbar, men ikke sannheten selv."
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-sol-goes",
    "code": "SG",
    "name": "kosmos.sol_goes",
    "short": "sol goes",
    "group": "kosmos",
    "gx": 11.1,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "GOES r\u00f8ntgenfluks og flareklasse \u00b7 perspektiv: consensus",
    "what": "GOES X-ray instrument \u2014 proxy chain: tilstand.swpc-goes-xray -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "NOAA GOES-instrumenteringen og solfysikkens varslingsfellesskap baerer X-ray-m\u00e5lingen; observasjonen er et avgrenset\u2026"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-transienter-alerce",
    "code": "TA",
    "name": "kosmos.transienter_alerce",
    "short": "transienter\u2026",
    "group": "kosmos",
    "gx": 13.5,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "optiske transienthendelser \u00b7 perspektiv: consensus",
    "what": "ALeRCE alert stream \u2014 proxy chain: hendelse.alerce -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "ALeRCEs \u00e5pne transientfellesskap og varslingspipeline baerer denne optiske str\u00f8mmen; klassifisering er ikke identitet."
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-kosmologi-desi-bao",
    "code": "DB",
    "name": "kosmos.kosmologi_desi_bao",
    "short": "kosmologi desi\u2026",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 48.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "DESI BAO-observasjoner n\u00e5r str\u00f8mmen finnes \u00b7 perspektiv: consensus",
    "what": "venter p\u00e5 konnektor \u2014 proxy chain: observasjon.desi-bao -> (venter p\u00e5 str\u00f8m)",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "DESI-samarbeidet og BAO-praksisen er den ventede sosiale kanalen; frav\u00e6r av str\u00f8m er rapportert eksplisitt."
      ]
    ],
    "cond": [
      "kosmos.kosmologi_desi_bao: stroemmen finnes ikke \u2014 venter paa konnektor"
    ]
  },
  {
    "id": "verden-klima-isbre",
    "code": "IB",
    "name": "verden.klima_isbre",
    "short": "klima isbre",
    "group": "samfunn",
    "gx": 3.9,
    "gy": 48.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "isbre/glasiologi-observasjoner n\u00e5r str\u00f8mmen finnes \u00b7 perspektiv: consensus",
    "what": "venter p\u00e5 konnektor \u2014 proxy chain: observasjon.isbre -> (venter p\u00e5 str\u00f8m)",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "klarhet": null,
      "rcmp": null
    },
    "steps": [
      [
        "Perspective",
        "consensus"
      ],
      [
        "Epistemics",
        "stottet / direkte / institusjonell"
      ],
      [
        "Social mechanism",
        "Glasiologiens felt- og fjernm\u00e5lingsfellesskap er den ventede kanalen; isbreobservasjonen finnes ikke i bussen enn\u00e5."
      ]
    ],
    "cond": [
      "verden.klima_isbre: stroemmen finnes ikke \u2014 venter paa konnektor"
    ]
  }
];

export const FLOWS = [
  {
    "id": "hav",
    "name": "Ocean state",
    "hops": [
      [
        "HA",
        "KL",
        "temperature proxy",
        {
          "emne": "verden.klima.tilstand.noaa-tides"
        },
        "xy"
      ]
    ]
  },
  {
    "id": "bio",
    "name": "Biosphere counts",
    "hops": [
      [
        "BI",
        "EF",
        "species counts",
        {
          "emne": "verden.miljo.tilstand.gbif-planter"
        },
        "xy"
      ]
    ]
  },
  {
    "id": "vul",
    "name": "Volcano state",
    "hops": [
      [
        "VU",
        "TR",
        "activity level",
        {
          "emne": "kosmos.jord.tilstand.usgs-vulkan"
        },
        "yx"
      ]
    ]
  }
];

export const CH = [
  {
    "id": "ch1",
    "title": "Roots \u2014 time and self",
    "reveal": [
      "efc-l0"
    ],
    "lede": "Chapter 1 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-l0.</p>",
    "flow": null
  },
  {
    "id": "ch2",
    "title": "The grid \u2014 your published works",
    "reveal": [
      "efc-grid-higgs",
      "efc-gr-qft-bro",
      "efc-double-slit",
      "efc-grid-mikrofysikk",
      "efc-grid-mikro-engine",
      "efc-sort-hull"
    ],
    "lede": "Chapter 2 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-double-slit, efc-gr-qft-bro, efc-grid-higgs, efc-grid-mikro-engine, efc-grid-mikrofysikk, efc-sort-hull.</p>",
    "flow": null
  },
  {
    "id": "ch3",
    "title": "Cosmos \u2014 engines on the bus",
    "reveal": [
      "efc-rotation-engine",
      "efc-hubble-engine",
      "efc-growth-engine",
      "efc-lensing-engine",
      "efc-cluster-engine",
      "efc-mu-kz-engine",
      "efc-romvaer-engine",
      "efc-orbital-engine",
      "efc-klima-engine",
      "efc-tidevann-engine",
      "efc-transient-engine",
      "kosmos-gammaglimt",
      "kosmos-interstellart",
      "kosmos-maane",
      "kosmos-noeytrinoer",
      "kosmos-planetsystem",
      "kosmos-roentgentransienter",
      "kosmos-romfart",
      "kosmos-stjerner",
      "kosmos-uklassifisert",
      "kosmos-galakser-mast",
      "kosmos-romvaer-swpc",
      "kosmos-sol-goes",
      "kosmos-transienter-alerce",
      "kosmos-kosmologi-desi-bao"
    ],
    "lede": "Chapter 3 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-cluster-engine, efc-growth-engine, efc-hubble-engine, efc-klima-engine, efc-lensing-engine, efc-mu-kz-engine, efc-orbital-engine, efc-romvaer-engine, efc-rotation-engine, efc-tidevann-engine, efc-transient-engine, kosmos-galakser-mast, kosmos-gammaglimt, kosmos-interstellart, kosmos-kosmologi-desi-bao, kosmos-maane, kosmos-noeytrinoer, kosmos-planetsystem, kosmos-roentgentransienter, kosmos-romfart, kosmos-romvaer-swpc, kosmos-sol-goes, kosmos-stjerner, kosmos-transienter-alerce, kosmos-uklassifisert.</p>",
    "flow": null
  },
  {
    "id": "ch4",
    "title": "Bridges \u2014 gap domains",
    "reveal": [
      "verden-hav",
      "verden-biosfaere",
      "kosmos-jord-vulkan"
    ],
    "lede": "Chapter 4 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: kosmos-jord-vulkan, verden-biosfaere, verden-hav.</p>",
    "flow": null
  },
  {
    "id": "ch5",
    "title": "Structures \u2014 H2O and chemistry",
    "reveal": [
      "efc-water-phase-engine",
      "kjemi-periodesystemet"
    ],
    "lede": "Chapter 5 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-water-phase-engine, kjemi-periodesystemet.</p>",
    "flow": null
  },
  {
    "id": "ch6",
    "title": "Society \u2014 energy flow",
    "reveal": [
      "efc-oekonomi-engine",
      "efc-samfunn-engine",
      "efc-enerflyt-engine",
      "verden-arbeid",
      "verden-demografi",
      "verden-finans",
      "verden-geopolitikk",
      "verden-handel",
      "verden-helse",
      "verden-infrastruktur",
      "verden-kommunikasjon",
      "verden-lov",
      "verden-militaer",
      "verden-politikk",
      "verden-sikkerhet",
      "verden-teknologi",
      "verden-transport",
      "verden-utdanning",
      "verden-klima-gdelt",
      "verden-klima-worldbank",
      "verden-miljo-mikrobiom",
      "verden-miljo-gdelt",
      "verden-oekonomi-worldbank",
      "verden-oekonomi-imf",
      "verden-oekonomi-gdelt",
      "verden-klima-isbre"
    ],
    "lede": "Chapter 6 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-enerflyt-engine, efc-oekonomi-engine, efc-samfunn-engine, verden-arbeid, verden-demografi, verden-finans, verden-geopolitikk, verden-handel, verden-helse, verden-infrastruktur, verden-klima-gdelt, verden-klima-isbre, verden-klima-worldbank, verden-kommunikasjon, verden-lov, verden-militaer, verden-miljo-gdelt, verden-miljo-mikrobiom, verden-oekonomi-gdelt, verden-oekonomi-imf, verden-oekonomi-worldbank, verden-politikk, verden-sikkerhet, verden-teknologi, verden-transport, verden-utdanning.</p>",
    "flow": null
  },
  {
    "id": "ch7",
    "title": "Epistemics",
    "reveal": [],
    "lede": "Chapter 7 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: .</p>",
    "flow": null
  },
  {
    "id": "ch8",
    "title": "No group yet",
    "reveal": [
      "h2o-solid",
      "h2o-liquid",
      "h2o-gas",
      "h2o-supercritical",
      "h2o-triple-point",
      "lys-sol",
      "h2o-droplet",
      "optikk-dispersjon",
      "regnbue",
      "regnbue-observator",
      "efc-l1",
      "efc-l2",
      "efc-l3",
      "obs-bao",
      "obs-cmb-tt",
      "obs-cmb-lensing",
      "obs-bbn",
      "obs-fsigma8",
      "obs-s8",
      "obs-eg",
      "obs-isw",
      "obs-ksz",
      "obs-cluster-mass",
      "obs-cluster-hmf",
      "obs-rar",
      "obs-bullet",
      "obs-satellites",
      "obs-jwst-ems",
      "obs-gw-ct",
      "obs-pta-gwb",
      "obs-h0-tension",
      "obs-w0wa",
      "obs-cc",
      "homo-fluxus",
      "homo-homeostase-buffer",
      "homo-feber-regime",
      "homo-aksjonspotensial",
      "homo-hjerte-syklus",
      "homo-genregulering",
      "homo-cellesyklus",
      "homo-metabolisme",
      "efc-solar-flare-engine",
      "efc-jordskjelv-engine",
      "homo-immunologi",
      "homo-sovn-vaaken",
      "homo-okologi",
      "homo-evolusjon",
      "verden-vaer",
      "kosmos-asteroider",
      "efc-efc-background-engine",
      "efc-lag-s",
      "efc-lag-d",
      "efc-lag-c0"
    ],
    "lede": "Chapter 8 of 9 \u2014 a few structures at a time.",
    "story": "<p>Revealed: efc-efc-background-engine, efc-jordskjelv-engine, efc-l1, efc-l2, efc-l3, efc-lag-c0, efc-lag-d, efc-lag-s, efc-solar-flare-engine, h2o-droplet, h2o-gas, h2o-liquid, h2o-solid, h2o-supercritical, h2o-triple-point, homo-aksjonspotensial, homo-cellesyklus, homo-evolusjon, homo-feber-regime, homo-fluxus, homo-genregulering, homo-hjerte-syklus, homo-homeostase-buffer, homo-immunologi, homo-metabolisme, homo-okologi, homo-sovn-vaaken, kosmos-asteroider, lys-sol, obs-bao, obs-bbn, obs-bullet, obs-cc, obs-cluster-hmf, obs-cluster-mass, obs-cmb-lensing, obs-cmb-tt, obs-eg, obs-fsigma8, obs-gw-ct, obs-h0-tension, obs-isw, obs-jwst-ems, obs-ksz, obs-pta-gwb, obs-rar, obs-s8, obs-satellites, obs-w0wa, optikk-dispersjon, regnbue, regnbue-observator, verden-vaer.</p>",
    "flow": null
  },
  {
    "id": "all",
    "title": "The whole atlas",
    "reveal": [],
    "lede": "Everything at once \u2014 116 nodes, 53 of them without a group yet (20 observations, 18 regime nodes, 11 with an engine, 4 other), 78 relations.",
    "story": "<p>Free exploration. Hover, click to pin, go inside.</p><p>7 nodes carry no evidence yet \u2014 that is what <i>epistemic: \u2026 / ingen / \u2026</i> in \u201cHow it's built\u201d says. Open questions are not generated: they come from the bank, and none is registered.</p>",
    "flow": null
  }
];

export const HOW_HTML = `<div class="eyebrow">EFC · generated</div><h1 class="t">How it's built</h1><div class="sub">one source, two views</div>
<h3 class="sec">Source</h3><pre>schema/regime_nodes.jsonld — the atlas bank</pre>
<h3 class="sec">Generator</h3><pre>scripts/maintenance/efc_atlas_generator.py</pre>`;
