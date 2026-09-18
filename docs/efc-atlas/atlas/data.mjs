// GENERERT av scripts/maintenance/efc_atlas_generator.py —
// IKKE rediger for haand. Kilden er schema/regime_nodes.jsonld.
export const META = {
  title: 'EFC',
  artifactUrl: '',
  sourcePath: 'schema/regime_nodes.jsonld',
  buildCmd: 'node docs/efc-atlas/atlas/build.mjs',
  stats: [{ k: 'Nodes', v: '116' },
          { k: 'Perspectives', v: 'paradigm / consensus / academia' }],
  intro: `_**One source, two views.** This atlas is generated from regime_nodes.jsonld — the bank is the truth; the atlas is its mirror._`,
  onePara: `Energy-Flow Cosmology: an entropic, structural atlas of the universe — from grid microphysics to society's energy flow. 116 nodes, 19 engines, NATS bridges.`,
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
    "title": "Not yet built"
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
    "one": "Perspective: academia. termodynamisk fase",
    "what": "calibrated thermometer + barometer (calibrated against the triple-point cell) \u2014 proxy chain: temperatur via termisk ekspansjon (termometer) -> trykk via membran (barometer) -> fase id",
    "how": "Buffer role: the crystal lattice + latent heat L_f: the ice holds the drink at 0 C until the . Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. termodynamisk fase",
    "what": "kalibrert termometer + barometer \u2014 proxy chain: temperatur via termisk ekspansjon -> trykk via membran -> phase identified via P_sat(T) an",
    "how": "Buffer role: high heat capacity (4.18 kJ/(kg*K)): water holds the temperature during heating . Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. termodynamisk fase",
    "what": "kalibrert termometer + barometer (evt. hygrometer for damp) \u2014 proxy chain: temperatur via termisk ekspansjon -> trykk via membran -> dampinnhold via duggpunkt (hygro",
    "how": "Buffer role: the gas's heat capacity and expansion damp local pressure and temperature gradie. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. thermodynamic state (not 'phase' \u2014 the boundary is gone)",
    "what": "hoeytrykks-P-T-celle \u2014 proxy chain: temperatur via termoelement -> trykk via hoeytrykksmembran -> no phase observable \u2014 the li",
    "how": "Buffer role: ingen fasegrense aa holde \u2014 bufferkapasiteten er kontinuerlig, uten latent varme. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. temperaturskalaens referansepunkt",
    "what": "kalibrert trippelpunktcelle \u2014 ITS-90-referansen \u2014 proxy chain: trykk holdt konstant (611.657 Pa) -> temperature read as the cell wall's thermal equilibri",
    "how": "Buffer role: the point absorbs energy with no temperature rise as long as three phases coexis. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. elektromagnetisk straaling",
    "what": "prisme/gitter-spektrometer \u2014 proxy chain: boelgelengde via gitter-dispersjon -> intensitet via detektor -> colour as an observer pro",
    "how": "Buffer role: the sun is an enormous energy source with an approximately stable spectral distr. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. drop shape and refractive index",
    "what": "hoyhastighetskamera / refraktometer \u2014 proxy chain: draapeform via overflatespenning -> brytningsindeks via refraksjon (n ~ 1.33) -> draapesto",
    "how": "Buffer role: the surface tension holds the droplet spherical \u2014 a geometric buffer that damps . Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. brytningsindeksen n(lambda)",
    "what": "spektrometer + prisme \u2014 proxy chain: avboyningsvinkel via Snells lov -> n(lambda) via vinkelmaaling -> colour separation as a p",
    "how": "Buffer role: water's electronic structure gives the dispersion stability \u2014 n(lambda) is a mat. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. the bow's angle and colour order",
    "what": "retina eller CCD-sensor \u2014 proxy chain: farge via boelgelengde-dispersjon i draapen -> buevinkel via refraksjonsgeometri (~42 grad",
    "how": "Buffer role: the droplet swarm is a statistical buffer \u2014 the pattern survives individual drop. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
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
    "one": "Perspective: academia. the arc as a direction and colour pattern",
    "what": "retina (S, M and L cones) \u2014 proxy chain: fotoner -> fotoreseptorer -> S/M/L-respons -> fargeopplevelse -> retning -> buens posisjon",
    "how": "Buffer role: the eye's adaptation (pupil, bleaching of photopigment) buffers against light va. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "peer review, textbook canonisation, career incentives \u2014 academia tells what survives the assessment"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-water-phase-engine",
    "code": "WA",
    "name": "efc.water_phase_engine",
    "short": "water phase en",
    "group": "struktur",
    "gx": 11.1,
    "gy": 1.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. phase boundaries P_sat(T), T_m(P), P_sub(T)",
    "what": "WaterPhaseEngine (efc_inference/engine/water.py) \u2014 proxy chain: P_sat(T) via Watson L_v(T) -> T_m(P) via dv_melt = 1/rho_vann - 1/rho_is -> P_sub(T) via c",
    "how": "Buffer role: the validity ranges are the engine's buffer: outside them it answers NaN/unknown. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. initial conditions and structure seeds",
    "what": "ingen direkte \u2014 modellavhengig \u2014 proxy chain: inflasjonsprediksjoner -> P(k)-avtrykk i L1 -> ingen direkte observabel i L0",
    "how": "Buffer role: the vacuum fluctuations are the seed bank \u2014 a buffer of potential that inflation. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S->0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
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
    "one": "Perspective: paradigm. CMB anisotropies and BAO scale",
    "what": "CMB-kart + galakse-survey \u2014 proxy chain: temperaturanisotropier -> P(k) -> BAO-skala -> H(z) -> polarisasjon -> optisk dybde",
    "how": "Buffer role: the plasma's photon-electron coupling keeps the anisotropies frozen until recomb. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S~0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
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
    "one": "Perspective: paradigm. fsigma8, P(k), svak linse (S8)",
    "what": "galakse-survey + svak linse (KiDS, DES, Euclid) \u2014 proxy chain: galaksefordeling -> P(k) full-shape -> roedforskyvningsromforvrengning -> fsigma8 -> skj\u00e6r",
    "how": "Buffer role: the structure itself is an inertia buffer: galaxies and clusters hold mass again. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S>0",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
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
    "one": "Perspective: paradigm. fjern-fremtid-tilstanden",
    "what": "ingen direkte \u2014 predikert grense \u2014 proxy chain: vekstlovens asymptote -> S->1-tilstanden -> ingen maalbar proxy i dag",
    "how": "Buffer role: the saturation IS a buffer: growth is braked against a limit instead of running . Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S->1",
      "sector": null,
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
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
    "one": "Perspective: consensus. BAO-skalaen (r_d ~ 147 Mpc comoving)",
    "what": "galakse-surveyer (DESI, eBOSS, BOSS) \u2014 proxy chain: galakse-korrelasjonsfunksjon -> BAO-topp ved ~150 Mpc -> BAO-topp -> D_H(z)/r_d, D_M(z)/r_",
    "how": "Buffer role: the drag epoch freezes the sound scale into the plasma \u2014 the ruler is frozen in . Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "galakse-surveyer (DESI, eBOSS, BOSS)",
        "observabel": "BAO-skalaen (r_d ~ 147 Mpc comoving)",
        "teori": "BAO \u2014 standardlinjalen",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The BAO peak was canonized via SDSS/BOSS/eBOSS and DESI \u2014 large collaborations with NSF/DOE funding; the survey competit"
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
    "one": "Perspective: consensus. temperatur-/polarisasjonsspekteret",
    "what": "Planck \u2014 proxy chain: temperaturspektrum -> P(k) -> peak distance -> theta_* and r_s(z_*) -> polarisasjon -> opt",
    "how": "Buffer role: recombination freezes the photons \u2014 the signal is held until it is released at z. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "Planck",
        "observabel": "temperatur-/polarisasjonsspekteret",
        "teori": "CMB TT/EE/TE akustiske topper",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The CMB temperature spectrum is carried by the Planck collaboration's institutional authority \u2014 the result was canonised"
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
    "one": "Perspective: consensus. linsingspotensialet",
    "what": "Planck, ACT, SPT \u2014 proxy chain: CMB-anisotropi-fordeling -> linsingspotensial -> linsingspotensial -> P(k) ved z ~ 2",
    "how": "Buffer role: fotonenes frie ferd er bufferen \u2014 de samler masseavtrykk underveis. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "Planck, ACT, SPT",
        "observabel": "linsingspotensialet",
        "teori": "CMB Lensing Reconstruction",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The lensing consensus is carried by Planck and ACT/SPT \u2014 two competing instrument groups that confirm each other; anomal"
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
    "one": "Perspective: consensus. deuterium/hydrogen-forholdet",
    "what": "quasar-spektroskopi \u2014 proxy chain: D/H i quasarskyer -> baryontetthet omega_b h^2 -> omega_b h^2 -> cross-check against CMB",
    "how": "Buffer role: the nuclear reactions freeze D/H at T ~ 80 keV \u2014 a signal that never changes. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "quasar-spektroskopi",
        "observabel": "deuterium/hydrogen-forholdet",
        "teori": "BBN lette elementer",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "BBN is canonised in textbooks and carried by the aesthetic connection with the CMB \u2014 re-testing it yields little prestig"
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
    "one": "Perspective: consensus. vekstraten fsigma8",
    "what": "BOSS, eBOSS, DESI \u2014 proxy chain: roedforskyvningsromforvrengning (RSD) -> f sigma8 -> f sigma8(z) -> vekstlovens form",
    "how": "Buffer role: the structure itself is the buffer \u2014 gravitational response holds mass against t. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "BOSS, eBOSS, DESI",
        "observabel": "vekstraten fsigma8",
        "teori": "f-sigma-8(z) line\u00e6r vekst",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "the f\u03c38 measurements come from large survey collaborations \u2014 the career paths lie in the collaborations, and systematics"
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
    "one": "Perspective: consensus. S8 = sigma8 sqrt(omega_m/0.3)",
    "what": "KiDS, DES, HSC, Euclid \u2014 proxy chain: skj\u00e6r (svak linse) -> S8 -> S8 lav vs CMB-forventning -> tension",
    "how": "Buffer role: linsebildene holder avtrykket av masse langs synslinjen \u2014 en akkumulert buffer. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "KiDS, DES, HSC, Euclid",
        "observabel": "S8 = sigma8 sqrt(omega_m/0.3)",
        "teori": "S8-tension",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The S8 tension is disputed BETWEEN instrument traditions \u2014 two communities with their own careers read the same data; wh"
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
    "one": "Perspective: consensus. E_G-krysset",
    "what": "SDSS, KiDS+BOSS \u2014 proxy chain: linse (kappa) x RSD (beta) -> E_G -> E_G -> slip between light and mass",
    "how": "Buffer role: to uavhengige proxyer buffrer hverandre \u2014 krysset er mer robust enn hver del. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "SDSS, KiDS+BOSS",
        "observabel": "E_G-krysset",
        "teori": "E_G gravitasjonsslip-statistikk",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "EG measurements depend on few instruments \u2014 the narrative is carried by a small group of specialists with high publicati"
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
    "one": "Perspective: consensus. ISW-signalet",
    "what": "CMB x galaksekart \u2014 proxy chain: CMB-kart x galaksefordeling -> ISW-kryss",
    "how": "Buffer role: fotonene integrerer potensialets tidsderivat over ferdselen \u2014 reisen er bufferen. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "CMB x galaksekart",
        "observabel": "ISW-signalet",
        "teori": "ISW krysskorrelasjon",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The ISW signal is weak and was long disputed \u2014 the consensus grew with the authority of the CMB tradition, not with new "
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
    "one": "Perspective: consensus. kSZ-signalet",
    "what": "ACT, DES x SPT \u2014 proxy chain: CMB x galakser -> kSZ -> kSZ -> egenhastighetsfelt",
    "how": "Buffer role: elektronene i klynger spretter fotoner doppler \u2014 plasmaet er bufferen. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "ACT, DES x SPT",
        "observabel": "kSZ-signalet",
        "teori": "kSZ egenhastigheter",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "kSZ is a young tradition \u2014 the consensus is institutional before it is replicated; few groups have the instruments"
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
    "one": "Perspective: consensus. M_500 from several channels",
    "what": "Chandra, XMM, HST \u2014 proxy chain: rontgen (T_X) -> masse -> svak linse -> masse -> skaleringsrelasjoner -> masse",
    "how": "Buffer role: the cluster's potential keeps the gas hot and the light bent \u2014 two buffers, one . Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "Chandra, XMM, HST",
        "observabel": "M_500 from several channels",
        "teori": "klyngemasse-skalering",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The halo masses depend on X-ray/weak-lensing calibrations from a few large collaborations \u2014 the consensus inherits their"
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
    "one": "Perspective: consensus. halomassetetthetsfunksjonen",
    "what": "DES, SDSS, eROSITA \u2014 proxy chain: antall klynger per masse -> N(M,z) -> N(M,z) -> sigma8 and growth",
    "how": "Buffer role: kollapsen buffrer masse i halos \u2014 tellingen er buffernes fordeling. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "DES, SDSS, eROSITA",
        "observabel": "halomassetetthetsfunksjonen",
        "teori": "klyngehalo-massetetthet N(M,z)",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The halo function is anchored in numerical simulations with their own code traditions \u2014 the consensus is carried by the "
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
    "one": "Perspective: consensus. a_obs vs a_bar",
    "what": "SPARC \u2014 proxy chain: rotasjonskurver -> a_obs -> barionisk fordeling -> a_bar -> avvik -> a_obs/a_bar",
    "how": "Buffer role: galaksens potensial holder rotasjonen \u2014 dynamikken er bufferen. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "SPARC",
        "observabel": "a_obs vs a_bar",
        "teori": "Radial Acceleration Relation",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "RAR (radial acceleration relation) is contested in the MOND debate \u2014 two communities with incompatible narratives read t"
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
    "one": "Perspective: consensus. masse-gass-offseten",
    "what": "HST + Chandra \u2014 proxy chain: linse (masse) vs rontgen (gass) -> offset delta-kappa",
    "how": "Buffer role: kollisjonen separerer komponentene \u2014 hendelsen er bufferen. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "HST + Chandra",
        "observabel": "masse-gass-offseten",
        "teori": "Bullet-klyngen delta-kappa",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The Bullet Cluster is read in the MOND debate \u2014 two frames with their own career paths; the image is the same, the story"
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
    "one": "Perspective: consensus. subhalo-populasjonen",
    "what": "HST, simuleringer \u2014 proxy chain: telte dverg-satellitter vs predikerte -> underskudd -> tette kjerner vs cusp -> profil",
    "how": "Buffer role: subhalos holdes av vertens potensial \u2014 bufferen er tidevannsstrippingen. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "HST, simuleringer",
        "observabel": "subhalo-populasjonen",
        "teori": "manglende satellitter / TBTF / core-cusp",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The satellite problem is carried by the simulation tradition vs the observers \u2014 a known point of tension where the conse"
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
    "one": "Perspective: consensus. galakse-massefunksjonen ved z>10",
    "what": "JWST \u2014 proxy chain: JWST-fotometri -> masse ved z>10 -> massefunksjon -> kollapstidsskala",
    "how": "Buffer role: early halos are the first buffers \u2014 the first to hold mass. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "JWST",
        "observabel": "galakse-massefunksjonen ved z>10",
        "teori": "tidlig massiv struktur (JWST z>10)",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The JWST findings are new and are negotiated OPENLY \u2014 every \u00abunexpected\u00bb finding yields publicity and thereby an incenti"
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
    "one": "Perspective: consensus. c_T from GW170817",
    "what": "LIGO/Virgo \u2014 proxy chain: GW and gamma arrival -> c_T/c within 1e-15",
    "how": "Buffer role: 1.7-sekunders-forsinkelsen over 40 Mpc er maalingens buffer \u2014 reisen kalibrerer. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "LIGO/Virgo",
        "observabel": "c_T from GW170817",
        "teori": "Gravitasjonsbolgehastighet c_T",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "Gravitational waves are a young, rapidly institutionalized tradition \u2014 the LIGO/Virgo/KAGRA collaborations hold a monopo"
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
    "one": "Perspective: consensus. GW-bakgrunnen ved nHz",
    "what": "NANOGrav, EPTA \u2014 proxy chain: pulsar-timing-residualer -> Hellings-Downs-korrelasjon -> GW-bakgrunn",
    "how": "Buffer role: pulsarene ER bufferen \u2014 deres rotasjon holder fasen over aar. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "NANOGrav, EPTA",
        "observabel": "GW-bakgrunnen ved nHz",
        "teori": "PTA gravitasjonsbolge-bakgrunn",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The PTA consensus is built by a few large collaborations with decade-long data sets \u2014 the data are private until publica"
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
    "one": "Perspective: consensus. H0 from two independent channels",
    "what": "Planck vs SH0ES \u2014 proxy chain: CMB (LCDM-ekstrapolasjon) -> H0 ~ 67 -> cepheid/SN-stige -> H0 ~ 73 -> gap -> tension",
    "how": "Buffer role: to uavhengige maalekjeder buffrer hverandre \u2014 nettopp derfor kan ingen av dem sk. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "Planck vs SH0ES",
        "observabel": "H0 from two independent channels",
        "teori": "Hubble-tension H0",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "The Hubble tension is CURRENTLY contested \u2014 distance scale vs CMB, two career paths; every new measurement shifts the na"
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
    "one": "Perspective: consensus. w(z)-parametriseringen",
    "what": "DES, BAO+CMB \u2014 proxy chain: SN + BAO + CMB -> w0, wa -> w0, wa -> deviation from -1",
    "how": "Buffer role: SN-lysets strekk over avstand er bufferen \u2014 ekspansjonshistorien er skrevet i de. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "DES, BAO+CMB",
        "observabel": "w(z)-parametriseringen",
        "teori": "w0-wa dynamisk moerk energi",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "m\u00f8rk-energi-parametriseringen er en konsensus KONVENSJON mer enn en m\u00e5ling \u2014 narrativet b\u00e6res av survey-designenes valg "
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
    "one": "Perspective: consensus. vakuumenergiens stoerrelse",
    "what": "alle kanaler \u2014 proxy chain: alle observasjoner -> omega_Lambda ~ 0.7 -> naivt teoretisk QFT-estimat -> ~120 stoerrelse",
    "how": "Buffer role: bakgrunnens akselerasjon er bufferen \u2014 den holder ekspansjonen oppe. Epistemic: modellrelativ / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
      "rcmp": {
        "instrument": "alle kanaler",
        "observabel": "vakuumenergiens stoerrelse",
        "teori": "kosmologisk konstant / vakuumenergi",
        "overlap": true,
        "deklarasjon": "RCMP: instrument, observable and theory have overlapping domains of validity."
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
        "the cluster count's consensus is carried by the mass-calibration chain \u2014 a long chain of assumptions each of which is co"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-rotation-engine",
    "code": "RO",
    "name": "efc.rotation_engine",
    "short": "rotation engin",
    "group": "kosmos",
    "gx": 13.5,
    "gy": 12.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. v(r) \u2014 rotation velocity as a function of radius",
    "what": "the observation side is galaxy spectra; the engine computes the curve \u2014 proxy chain: spectral lines -> v(r) (observation) -> v(r) -> EFC parameters (inference)",
    "how": "Buffer role: the matter buffer of the galaxy keeps the curve flat through the coupling field . Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. H(z) \u2014 the expansion rate",
    "what": "the observation side is BAO/chronometers; the engine computes the rate \u2014 proxy chain: BAO/SNIa -> H(z) (observation) -> H(z) -> EFC parameters (inference)",
    "how": "Buffer role: the background energy is the buffer that holds the expansion \u2014 modelled, not mea. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. f\u03c38(z) \u2014 growth rate times amplitude",
    "what": "the observation side is RSD/ELG/QSO; the engine computes the growth \u2014 proxy chain: RSD measurements -> f\u03c38 (observation) -> f\u03c38 -> EFC parameters (inference)",
    "how": "Buffer role: the structure's matter buffer grows through the coupling field \u2014 modelled, not m. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. kappa(theta) \u2014 convergence as a function of angular position",
    "what": "the observation side is weak lensing; the engine computes nothing yet \u2014 proxy chain: shear -> kappa (observation) -> kappa -> EFC parameters (awaiting the physics)",
    "how": "Buffer role: the structure's mass buffer bends light \u2014 the mechanism is observed, the engine . Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. n(M,z) \u2014 the halo mass function",
    "what": "the observation side is halo counts; the engine computes nothing yet \u2014 proxy chain: halo counts -> n(M,z) (observation) -> n(M,z) -> EFC parameters (awaiting the physics)",
    "how": "Buffer role: the halos are the structure's densest buffers \u2014 observed, not modelled here yet. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. R \u2014 den indre refleksjonskoeffisienten",
    "what": "hf1\u2013hf5-observasjonskravene (falsifiserbare p\u00e5stander i rammeverket) \u2014 proxy chain: kohrens-proxyer \u2192 R (inferens) -> R \u2192 flytobjekt/flytsubjekt (terskel)",
    "how": "Buffer role: kroppens buffere (termisk, kjemisk, nevral) holder flytm\u00f8nsteret stabilt under t. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-homeostase-buffer",
    "code": "HO",
    "name": "homo.homeostase_buffer",
    "short": "homeostase buf",
    "group": "ghost",
    "gx": 13.5,
    "gy": 14.600000000000001,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "Perspective: academia. deviation from setpoint (\u0394T, \u0394pH, \u0394glucose)",
    "what": "physiological sensors; here the node is a description, not a sensor \u2014 proxy chain: sensor \u2192 avvik -> avvik \u2192 kompensasjonsrespons",
    "how": "Buffer role: the buffer itself: capacity that damps change \u2014 the broad logic in pure form. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "Levin 2019 (biology) \u2014 peer-reviewed and canonised in textbooks. THE ANALOGY to EFC is our own and is not carried by the"
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
    "one": "Perspective: academia. body temperature against setpoint",
    "what": "termometer + pyrogen-mark\u00f8rer; her beskrivelse \u2014 proxy chain: pyrogener \u2192 setpunktsskifte -> temperature \u2192 distance to the new setpoint",
    "how": "Buffer role: the buffer switches TARGET, not capacity \u2014 that is the regime shift itself. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "physiology (standard) \u2014 peer-reviewed and canonised in textbooks. The ANALOGY to EFC is our own and is not carried by th"
      ]
    ],
    "cond": []
  },
  {
    "id": "homo-aksjonspotensial",
    "code": "AP",
    "name": "homo.aksjonspotensial",
    "short": "aksjonspotensi",
    "group": "ghost",
    "gx": 3.9,
    "gy": 17.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "Perspective: academia. the membrane potential V(t) against the threshold",
    "what": "fysiologisk m\u00e5ling; her beskrivelse \u2014 proxy chain: ionestr\u00f8mmer \u2192 V(t) -> V(t) vs V_th \u2192 spike",
    "how": "Buffer role: the membrane is the buffer: the gradient charges and is held until release. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "neurophysiology (standard) \u2014 peer-reviewed and textbook-canonized. The ANALOGY to EFC is our own and is not carried by t"
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
    "one": "Perspective: academia. slagvolum, frekvens, minuttvolum",
    "what": "fysiologisk m\u00e5ling; her beskrivelse \u2014 proxy chain: EKG \u2192 elektrisk syklus -> ekko \u2192 mekanisk syklus",
    "how": "Buffer role: the ventricles are the buffers: they fill and empty rhythmically \u2014 never to zero. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "cardiology (standard) \u2014 peer-reviewed and textbook-canonized. The ANALOGY to EFC is our own and is not carried by the fi"
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
    "one": "Perspective: academia. uttrykksniv\u00e5 per gen (mRNA/protein)",
    "what": "sekvensering; her beskrivelse av reguleringslogikken \u2014 proxy chain: TF-binding \u2192 uttrykk -> epigenetisk merke \u2192 terskelskifte",
    "how": "Buffer role: the genome keeps the regulatory programs stored \u2014 a capacity that damps random e. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "molecular biology (standard) \u2014 peer-reviewed and textbook-canonized. The atlas uses it as established, not as its own cl"
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
    "one": "Perspective: academia. fase per celle (G1/S/G2/M)",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: DNA-innhold \u2192 fase -> CDK/cyklin \u2192 sjekkpunkt-status",
    "how": "Buffer role: the checkpoints are the buffers: they hold the cycle until the conditions are me. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "cell biology (standard) \u2014 peer-reviewed and canonised in textbooks. THE ANALOGY to EFC is our own and is not carried by "
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
    "one": "Perspective: academia. ATP/ADP-forhold, O\u2082-forbruk, substrat-fluks",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: O\u2082-forbruk \u2192 fluks -> ATP/ADP \u2192 reguleringsstatus",
    "how": "Buffer role: The ATP pool and glycogen are the buffers: short- and long-term stores that damp. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "biochemistry (standard) \u2014 peer-reviewed and canonized in textbooks. The ANALOGY to EFC is our own and is not carried by "
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-solar-flare-engine",
    "code": "SF",
    "name": "efc.solar_flare_engine",
    "short": "solar flare en",
    "group": "ghost",
    "gx": 1.5,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "Perspective: paradigm. charging time, released energy, GOES class",
    "what": "SolarFlareEngine (efc_inference/engine/solar_flare.py) \u2014 proxy chain: B -> magnetic energy (E = B^2/(2 mu_0) * V) -> energy -> GOES class (calibration proxy: 1e",
    "how": "Buffer role: the magnetic field is the buffer: the energy is charged and held until the thres. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-jordskjelv-engine",
    "code": "JS",
    "name": "efc.jordskjelv_engine",
    "short": "jordskjelv eng",
    "group": "ghost",
    "gx": 3.9,
    "gy": 19.8,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "Perspective: paradigm. recurrence time, seismic moment, moment magnitude",
    "what": "JordskjelvEngine (efc_inference/engine/jordskjelv.py) \u2014 proxy chain: charge rate -> recurrence time -> stress drop -> slip -> M0 -> Mw (Kanamori)",
    "how": "Buffer role: the fault is the buffer: the stress charges and is held until the threshold is c. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: academia. aktiveringsstatus, antistofftiter, hukommelsespopulasjon",
    "what": "laboratoriem\u00e5ling; her beskrivelse \u2014 proxy chain: faresignaler + antigenkonsentrasjon -> aktivering -> titer -> hukommelse",
    "how": "Buffer role: memory is the buffer: it lowers the threshold and makes the next response faster. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "immunology (standard: Janeway/Matzinger) \u2014 peer-reviewed and textbook-canonized. The atlas uses it as established, not a"
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
    "one": "Perspective: academia. s\u00f8vnstadium (v\u00e5ken/NREM/REM), homeostatisk trykk",
    "what": "klinisk m\u00e5ling; her beskrivelse \u2014 proxy chain: EEG-synkroni -> stadium -> v\u00e5kenhetsvarighet -> homeostatisk trykk",
    "how": "Buffer role: the need for sleep is the buffer: it accumulates while awake and is drained in s. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "sleep physiology (standard: Borbely, Steriade) \u2014 peer-reviewed and textbook-canonized. The ANALOGY to EFC is our own and"
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
    "one": "Perspective: academia. tilstandsvariabler (n\u00e6ringsstoffer, dekning, artssammensetning)",
    "what": "\u00f8kologisk overv\u00e5king; her beskrivelse \u2014 proxy chain: n\u00e6ringsstoffer -> tilstand -> dekning -> regime",
    "how": "Buffer role: the ecosystem's buffer capacity (resilience) damps disturbances \u2014 until the buff. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "regime-shift ecology (Scheffer) \u2014 peer-reviewed and canonised in textbooks. The atlas uses it as established, not as its"
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
    "one": "Perspective: academia. rate of change in phenotype/species (morphological and molecular rates",
    "what": "paleontologisk/genomisk m\u00e5ling; her beskrivelse \u2014 proxy chain: fossilrekke -> morfologisk rate -> molekyl\u00e6r avstand -> tid siden splitt",
    "how": "Buffer role: stasis is holding: selection and developmental constraints hold the phenotype \u2014 . Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": "S~0.5",
      "sector": null,
      "ebe": null,
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
        "evolutionary biology (standard) \u2014 peer-reviewed and canonised in textbooks. The ANALOGY to EFC is our own and is not car"
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
    "one": "Perspective: paradigm. mu(k,z) \u2014 the effective Poisson coupling",
    "what": "MuKZEngine (efc_inference/engine/mu_kz.py) \u2014 proxy chain: background inputs -> eps_F, eps_K, R -> eps_F, eps_K, R -> mu (eq. 28)",
    "how": "Buffer role: the validity range is the module's buffer: quasi-static sub-horizon \u2014 outside it. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. expected Kp, storm level, discharge trajectory",
    "what": "RomvaerEngine (efc_inference/engine/romvaer.py) \u2014 proxy chain: Bz, v -> charging current (correlation proxy) -> Kp -> G level (the NOAA scale)",
    "how": "Buffer role: the magnetosphere is the buffer: it holds the charge from the solar wind until t. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-oekonomi-engine",
    "code": "OK",
    "name": "efc.oekonomi_engine",
    "short": "oekonomi engin",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 22.400000000000002,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. financial regime (hedge/spekulativ/ponzi), leverage drift",
    "what": "OekonomiEngine (efc_inference/engine/oekonomi.py) \u2014 proxy chain: leverage ratio -> regime (two thresholds) -> stable years -> leverage drift (the Minsky mo",
    "how": "Buffer role: the stable years are the buffer: trust builds up and the debt accumulates \u2014 unti. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. period, velocity, specific energy, Hill sphere",
    "what": "OrbitalEngine (efc_inference/engine/orbital.py) \u2014 proxy chain: a, e -> T (Kepler) -> a, r -> v (vis-viva) -> eps = -GM/(2a) -> holding/release",
    "how": "Buffer role: the Hill sphere is the orbit's APPROXIMATE stability buffer: inside it the centr. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. equilibrium temperature, time constant, regime switch",
    "what": "KlimaEngine (efc_inference/engine/klima.py) \u2014 proxy chain: solar constant + albedo -> incoming radiation -> eps sigma T^4 -> outgoing radiation -> C ",
    "how": "Buffer role: the ocean's heat capacity is the buffer: it damps and delays all disturbances \u2014 . Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
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
    "one": "Perspective: paradigm. R0, outbreak status, the epidemic trajectory",
    "what": "SamfunnEngine (efc_inference/engine/samfunn.py) \u2014 proxy chain: beta, gamma -> R0 -> R0 -> outbreak status (threshold 1) -> the SIR trajectory -> the shap",
    "how": "Buffer role: the reservoir of susceptibles is the buffer: the outbreak drains it, and when it. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-tidevann-engine",
    "code": "TI",
    "name": "efc.tidevann_engine",
    "short": "tidevann engin",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. tidal acceleration, tidal height, Roche limit, phase-lock status",
    "what": "TidevannEngine (efc_inference/engine/tidevann.py) \u2014 proxy chain: m_obj, r -> a_t (differential gravity) -> a_t -> h (open-ocean proxy) -> periods -> phase-",
    "how": "Buffer role: the sea is the buffer: it is raised and lowered in the periodic cycle without br. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-transient-engine",
    "code": "TR",
    "name": "efc.transient_engine",
    "short": "transient engi",
    "group": "kosmos",
    "gx": 3.9,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. hold time, released energy, the lightcurve's form",
    "what": "TransientEngine (efc_inference/engine/transient.py) \u2014 proxy chain: core mass -> binding energy (E = G*M^2/R) -> binding energy -> released energy at the stab",
    "how": "Buffer role: the core is the buffer: the mass is built up and held up until the stability lim. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field; the narrative is our own, and it is a strength to know it"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-enerflyt-engine",
    "code": "EF",
    "name": "efc.enerflyt_engine",
    "short": "enerflyt engin",
    "group": "samfunn",
    "gx": 6.3,
    "gy": 25.0,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. the buffer S and the drift dS/dt = P - C - L",
    "what": "statistics agencies and grid operators \u2014 proxy chain: registered production -> consumption -> buffer estimate \u2014 all are accounting proxies, not ",
    "how": "Buffer role: S is society's energy buffer \u2014 the holding that absorbs the imbalance between pr. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
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
    "one": "Perspective: paradigm. The Grid-Higgs framework: entropic and structural theory of gravity, d",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: the work is the buffer that holds the bridge hypothesis until it is tested. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.grid_higgs: no evidence yet \u2014 hypothesis marked honestly"
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
    "one": "Perspective: paradigm. The thermodynamic bridge between general relativity and quantum field ",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: the work is the buffer that holds the bridge hypothesis until it is tested. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.gr_qft_bro: no evidence yet \u2014 hypothesis marked honestly"
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
    "one": "Perspective: paradigm. The double-slit as a grid-resolution phenomenon: ontological extension",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: the work is the buffer that holds the bridge hypothesis until it is tested. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.double_slit: no evidence yet \u2014 hypothesis marked honestly"
    ]
  },
  {
    "id": "efc-grid-mikrofysikk",
    "code": "GM",
    "name": "efc.grid_mikrofysikk",
    "short": "grid mikrofysi",
    "group": "grid",
    "gx": 1.5,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. From grid microphysics to the radial acceleration relation \u2014 minimal g",
    "what": "ingen direkte \u2014 teoretisk verk \u2014 proxy chain: DOI -> papir -> avledning \u2014 litteraturkjede",
    "how": "Buffer role: the work is the buffer that holds the bridge hypothesis until it is tested. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.grid_mikrofysikk: no evidence yet \u2014 hypothesis marked honestly"
    ]
  },
  {
    "id": "efc-grid-mikro-engine",
    "code": "GE",
    "name": "efc.grid_mikro_engine",
    "short": "grid mikro eng",
    "group": "grid",
    "gx": 3.9,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: paradigm. Gamma(rho) and Deff(rho)",
    "what": "no direct one \u2014 microphysical derivation, model-dependent \u2014 proxy chain: density -> grid-mode occupancy -> entropy production \u2014 a pure theory chain",
    "how": "Buffer role: the grid modes are the buffer \u2014 the entropy of occupied modes charges with the d. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.grid_mikro_engine: no evidence yet \u2014 hypothesis marked honestly"
    ]
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
    "one": "Perspective: paradigm. black holes as an entropic boundary in the Grid-Higgs frame",
    "what": "ingen direkte \u2014 teoretisk \u2014 proxy chain: DOI -> verk -> avledning",
    "how": "Buffer role: BH as entropic buffer in the grid theory. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
      "efc.sort_hull: no evidence yet \u2014 hypothesis marked honestly"
    ]
  },
  {
    "id": "kjemi-periodesystemet",
    "code": "PS",
    "name": "kjemi.periodesystemet",
    "short": "periodesysteme",
    "group": "struktur",
    "gx": 8.7,
    "gy": 27.6,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: academia. periodesystemets struktur (118 grunnstoff)",
    "what": "spectroscopy and chemical analysis \u2014 proxy chain: atomnummer -> periodisitet \u2014 konsensus-kartlegging",
    "how": "Buffer role: the periodic table is the buffer that keeps the chemistry ordered. Epistemic: stottet / replikert / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
    "cond": []
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
    "one": "Perspective: consensus. havtemperatur",
    "what": "boeyestasjoner (tides & currents) \u2014 proxy chain: stasjon -> temperatur -> hav-energi",
    "how": "Buffer role: the ocean as heat buffer in the climate. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The NOAA station network as a consensus channel"
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
    "one": "Perspective: consensus. arts-tellinger (planteriket)",
    "what": "taksonomisk soek \u2014 proxy chain: soek -> telling -> fotavtrykk",
    "how": "Buffer role: the biosphere as energy-flow buffer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The GBIF taxonomy as consensus channel"
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
    "one": "Perspective: consensus. vulkantilstand",
    "what": "statusliste (alertLevel) \u2014 proxy chain: alertLevel -> aktivitet -> regime-status",
    "how": "Buffer role: volcanoes as the thermal buffer of the Earth. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The USGS status list as consensus channel"
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
    "one": "Perspective: consensus. temperature, wind, pressure, cloud cover and humidity",
    "what": "one place in one validity window; both expected and outcome in the same message \u2014 proxy chain: prognose -> forventet -> METAR-maaling -> utfall -> avvik = utfall minus forventet, per st",
    "how": "Buffer role: the atmosphere as buffer between prediction and reality. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "MET Norway forecast against METAR measurement \u2014 two independent institutional channels"
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
    "one": "Perspective: consensus. impact probability and Palermo cumulative per object",
    "what": "The Sentry list itself; the reconciliation reads the whole list as the answer key \u2014 proxy chain: bane -> treffsannsynlighet (prediksjon) -> liste -> revidert/utelukket (oppgjoer)",
    "how": "Buffer role: The Sentry list is the buffer that keeps the risk picture stable between revisio. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "JPL Sentry as consensus channel"
      ]
    ],
    "cond": []
  },
  {
    "id": "efc-efc-background-engine",
    "code": "EE",
    "name": "efc.efc_background_engine",
    "short": "efc background",
    "group": "ghost",
    "gx": 8.7,
    "gy": 30.200000000000003,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": true,
    "one": "Perspective: paradigm. H(z) and the background fields phi, phi_dot, rho_m, lambda_dot",
    "what": "EFCBackgroundSolver (efc_inference/engine/efc_background.py) \u2014 proxy chain: parameters (alpha, k0, omega_crit, gamma0, V0) -> ODE system -> ODE system -> state (a, E,",
    "how": "Buffer role: lambda is the buffer: the response field that keeps the flow accounting when phi. Epistemic: hypotese / ingen / minoritet.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "our own frame \u2014 carried by us, not by the field"
      ]
    ],
    "cond": [
      "efc.efc_background_engine: no evidence yet \u2014 hypothesis marked honestly"
    ]
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
    "one": "Perspective: paradigm. the structure that the energy-flow field holds up",
    "what": "none directly \u2014 the structure is derived from the field, not measured as structure \u2014 proxy chain: energy-flow-felt -> tetthetsgradient -> potensial -> struktur -> struktur -> rotasjonskurv",
    "how": "Buffer role: haloen selv er bufferen: den holder formen mens feltet varierer under. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S>0",
      "sector": "S",
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our frame \u2014 replaces dark matter, which is a MINORITY position against LCDM"
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
    "one": "Perspective: paradigm. the energy-flow field J_mu and its divergence",
    "what": "aksjonen (master-spec, eq. 1) \u2014 proxy chain: aksjon -> feltligning -> J_mu -> ekspansjonshistorie -> J_mu -> Sigma (kildeledd)",
    "how": "Buffer role: F(phi) and K(rho) damp deviations from LCDM depending on the field value. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S>0",
      "sector": "D",
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our frame \u2014 replaces dark energy, which is consensus in LCDM"
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
    "one": "Perspective: paradigm. the entropy field S and its boundaries",
    "what": "none directly \u2014 S is a field, not a measurement \u2014 proxy chain: S -> Omega-hat (differentiation) and kappa-hat (integration) -> Omega x kappa -> C (FALSIF",
    "how": "Buffer role: entropy itself: it absorbs energy without the structure changing, until the limi. Epistemic: hypotese / proxy / minoritet.",
    "sAxis": {
      "regime": "S->1",
      "sector": "C",
      "ebe": "claim validity = f(S, L, proxy-chain)",
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
        "our frame \u2014 the cosmology-to-cognition bridge is not established"
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
    "one": "Perspective: consensus. alerts on transients in real time, from ground and space",
    "what": "Fermi, Swift and ground-based telescopes \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom op. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "GCN alerts when something is DETECTED; the fraction measures the coverage of the instrument, not the activity of the sky"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The interstellar is known from a few objects; the fraction rests on a handful of measurements"
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
    "one": "Perspective: consensus. orbit positions computed from the DE441 ephemeris",
    "what": "DE441-ephemeriden; ingen instrument leste av \u2014 proxy chain: observasjoner (historiske) -> DE441-tilpasning -> posisjon",
    "how": "Buffer role: JPL Horizons er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The same ephemeris as the planetary system \u2014 two domains, one calculation"
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
    "one": "Perspective: consensus. alerts on transients in real time, from ground and space",
    "what": "Fermi, Swift and ground-based telescopes \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom op. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Neutrino detection is a handful of facilities worldwide \u2014 the fraction measures the facilities, not the fluxes"
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
    "one": "Perspective: consensus. orbit positions computed from the DE441 ephemeris",
    "what": "DE441-ephemeriden; ingen instrument leste av \u2014 proxy chain: observasjoner (historiske) -> DE441-tilpasning -> posisjon",
    "how": "Buffer role: JPL Horizons er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / proxy / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "JPL DE441 is a FIT to historical observations; the fraction measures the ephemeris, not the sky"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-roentgentransienter",
    "code": "KR",
    "name": "kosmos.roentgentransienter",
    "short": "roentgentransi",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 35.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. alerts on transients in real time, from ground and space",
    "what": "Fermi, Swift and ground-based telescopes \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom op. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "X-ray transients require instruments that see in that band; without them they do not exist in the data"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Launch data are institutional and national; what is not announced is not counted"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Stellar data come from surveys each with its own selection; the proportion carries the survey's gaze"
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
    "one": "Perspective: consensus. alerts on transients in real time, from ground and space",
    "what": "Fermi, Swift and ground-based telescopes \u2014 proxy chain: fotoner inn -> detektorterskel -> varsel ut",
    "how": "Buffer role: GCN \u2014 Gamma-ray Coordinates Network er bufferen: den holder tilstanden mellom op. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The unclassified is defined by the fact that it does NOT fit \u2014 the proportion measures the schema's boundary, not the ph"
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
    "one": "Perspective: consensus. labour market and social statistics for Europe",
    "what": "nasjonale statistikkbyr\u00e5er, harmonisert \u2014 proxy chain: nasjonal statistikk -> harmonisering -> indikator",
    "how": "Buffer role: Eurostat er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Eurostat and ILO measure formal labour; the informal economy is structurally absent"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Population registers are unevenly developed; the proportion measures the registration as much as the population"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Geopolitics is a language of power relations; the coding scheme chooses what gets a label"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Trade is counted across borders with customs forms \u2014 services and digital exchange fall outside"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "WHO and national health registries define what counts as health; what is not reported does not exist in the share"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Infrastructure is counted when it is built and when it fails; the quiet working day is invisible"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Media coverage is unevenly distributed \u2014 rich countries report more, so the share measures the medium, not the event"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Legislation is registered when it is adopted, not when it takes effect \u2014 and not in countries without free registers"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Military matters are reported by the states themselves; the secret is invisible in the corpus, not in the world"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "GDELT encodes the world's news stream \u2014 the proportion measures what was WRITTEN about, not what happened"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Safety incidents are reported when they are spectacular; the quiet everyday is not counted"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Technology news is future-oriented: the share measures expectation, not adoption"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Transport is measured where it is registered \u2014 informal and local transport is invisible"
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
    "one": "Perspective: consensus. global news streams coded to topic, actor and place",
    "what": "GKG-pipelinen; kodede dokumenter per tema \u2014 proxy chain: r\u00e5 nyhetstekst -> GKG-koder (tema, akt\u00f8r, sted) -> andel per domene",
    "how": "Buffer role: GDELT GKG er bufferen: den holder tilstanden mellom oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Education statistics measure schooling, not learning \u2014 and countries that do not report become invisible in the same fra"
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
    "one": "Perspective: consensus. astronomical observations and catalogued sources",
    "what": "MAST CAOM observasjonskatalog \u2014 proxy chain: instrumentmetadata -> CAOM-observasjon -> katalogisert astronomisk kilde",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "MAST/CAOM carries the measurement practice and the stream makes it available; this is a social channel, not the truth it"
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
    "one": "Perspective: consensus. klimarelatert omtale kodet i globale nyhetsdokumenter",
    "what": "GDELT GKG coding of document, topic, actor and place \u2014 proxy chain: nyhetsdokument -> GKG-koder -> klimarelatert observasjon",
    "how": "Buffer role: GDELT-korpuset holder kodingen mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "the GDELT project carries the measurement practice and the stream makes it available; this is a social channel, not the "
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-klima-worldbank",
    "code": "WB",
    "name": "verden.klima_worldbank",
    "short": "klima worldban",
    "group": "samfunn",
    "gx": 8.7,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. climate and development indicators per country and year",
    "what": "the World Bank indicators' reported and harmonised datasets \u2014 proxy chain: nasjonal rapportering -> harmonisering -> indikatorverdi -> tilstandsmelding",
    "how": "Buffer role: harmoniserte indikatorserier holder tilstanden mellom \u00e5rlige oppdateringer. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "World Bank carries the climate's institutional measurement practice; the stream makes the country and year indicators av"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-miljo-mikrobiom",
    "code": "MX",
    "name": "verden.miljo_mikrobiom",
    "short": "miljo mikrobio",
    "group": "samfunn",
    "gx": 11.1,
    "gy": 43.2,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. microbial taxa and functional profiles across sampled environments",
    "what": "MGnify microbiome profiles \u2014 proxy chain: sample -> sequence processing -> taxonomic and functional profile -> state message",
    "how": "Buffer role: MGnify-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "MGnify carries the measurement practice and the stream makes it available; this is a social channel, not the truth itsel"
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
    "one": "Perspective: consensus. environment-related coverage encoded in global news documents",
    "what": "GDELT GKG coding of documents, themes, actors and places \u2014 proxy chain: news document -> GKG codes -> environmental observation",
    "how": "Buffer role: GDELT-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "GDELT carries the environment's news measurement practice; the stream makes coded coverage available, but this is not th"
      ]
    ],
    "cond": []
  },
  {
    "id": "verden-oekonomi-worldbank",
    "code": "OX",
    "name": "verden.oekonomi_worldbank",
    "short": "oekonomi world",
    "group": "samfunn",
    "gx": 1.5,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. economic indicators by country and year",
    "what": "World Bank reported and harmonized indicator datasets \u2014 proxy chain: national reporting -> harmonization -> indicator value -> state message",
    "how": "Buffer role: World Bank-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "World Bank carries the economy's institutional measurement practice; the stream makes the country and year indicators av"
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
    "one": "Perspective: consensus. macroeconomic projections and scenario indicators",
    "what": "IMF DataMapper projections and macroeconomic scenarios \u2014 proxy chain: institutional projection -> DataMapper series -> forecast reading",
    "how": "Buffer role: IMF DataMapper-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "IMF DataMapper carries the measurement practice and the stream makes it available; this is a social channel, not the tru"
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
    "one": "Perspective: consensus. economic coverage encoded in global news documents",
    "what": "GDELT GKG coding of documents, themes, actors and places \u2014 proxy chain: news document -> GKG codes -> economic observation",
    "how": "Buffer role: GDELT-kilden holder m\u00e5lekontrakten mellom meldinger. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "GDELT carries the economy's news measurement practice; the stream makes coded coverage available, but this is not the tr"
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
    "one": "Perspective: consensus. Kp state and storm level",
    "what": "SWPC Kp-m\u00e5ling \u2014 proxy chain: tilstand.swpc-kp -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "SWPC's operational Kp scale and space weather forecasts carry the practice; the stream makes the state readable, but not"
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
    "one": "Perspective: consensus. GOES X-ray flux and flare class",
    "what": "GOES X-ray instrument \u2014 proxy chain: tilstand.swpc-goes-xray -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "NOAA's GOES instrumentation and solar physics' alerting community carry the X-ray measurement; the observation is a deli"
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-transienter-alerce",
    "code": "TA",
    "name": "kosmos.transienter_alerce",
    "short": "transienter al",
    "group": "kosmos",
    "gx": 13.5,
    "gy": 45.800000000000004,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. optiske transienthendelser",
    "what": "ALeRCE alert stream \u2014 proxy chain: hendelse.alerce -> instrumentavlesning -> atlasobservasjon",
    "how": "Buffer role: str\u00f8mmen holder kildens m\u00e5ling. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "ALeRCE's open transient community and alert pipeline carry this optical stream; classification is not identity."
      ]
    ],
    "cond": []
  },
  {
    "id": "kosmos-kosmologi-desi-bao",
    "code": "DB",
    "name": "kosmos.kosmologi_desi_bao",
    "short": "kosmologi desi",
    "group": "kosmos",
    "gx": 1.5,
    "gy": 48.4,
    "w": 2,
    "d": 2,
    "h": 34,
    "kind": "box",
    "ghost": false,
    "one": "Perspective: consensus. DESI BAO-observasjoner n\u00e5r str\u00f8mmen finnes",
    "what": "venter p\u00e5 konnektor \u2014 proxy chain: observasjon.desi-bao -> (venter p\u00e5 str\u00f8m)",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "The DESI collaboration and the BAO practice are the expected social channel; the absence of a stream is reported explici"
      ]
    ],
    "cond": []
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
    "one": "Perspective: consensus. isbre/glasiologi-observasjoner n\u00e5r str\u00f8mmen finnes",
    "what": "venter p\u00e5 konnektor \u2014 proxy chain: observasjon.isbre -> (venter p\u00e5 str\u00f8m)",
    "how": "Buffer role: observasjonskatalogen holder metadata mellom uttrekk. Epistemic: stottet / direkte / institusjonell.",
    "sAxis": {
      "regime": null,
      "sector": null,
      "ebe": null,
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
        "Glaciology's field and remote-sensing community is the expected channel; the glacier observation does not exist on the b"
      ]
    ],
    "cond": []
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
    "title": "Not yet built",
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
    "lede": "Everything at once \u2014 116 nodes, 79 relations.",
    "story": "<p>Free exploration. Hover, click to pin, go inside.</p>",
    "flow": null
  }
];

export const HOW_HTML = `<div class="eyebrow">EFC · generated</div><h1 class="t">How it's built</h1><div class="sub">one source, two views</div>
<h3 class="sec">Source</h3><pre>schema/regime_nodes.jsonld — the atlas bank</pre>
<h3 class="sec">Generator</h3><pre>scripts/maintenance/efc_atlas_generator.py</pre>`;
