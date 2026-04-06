# Energy-Flow Cosmology (EFC)

> **Core Principle**: Energy flows along entropy gradients — this generates spacetime, structure, and awareness.

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.30656828-blue)](https://doi.org/10.6084/m9.figshare.30656828)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4860--5095-green)](https://orcid.org/0009-0002-4860-5095)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Validation Ledger](https://img.shields.io/badge/Validation_Ledger-v3.7-orange)](./docs/public/EFC_Validation_Ledger.html)
[![AI Packages](https://img.shields.io/badge/AI_Packages-41+-brightgreen)](#ai-friendly-paper-packages)

---

## Quick Reference (AI + Human)

| Key | Value |
|-----|-------|
| **Author** | Morten Magnusson (Symbiose Research, Sandnes, Norway) |
| **ORCID** | [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095) |
| **Primary DOI** | [10.6084/m9.figshare.30656828](https://doi.org/10.6084/m9.figshare.30656828) |
| **Repository** | [github.com/supertedai/EFC](https://github.com/supertedai/EFC) |
| **Theory Site** | [energyflow-cosmology.com](https://energyflow-cosmology.com/) |
| **AI Navigation** | [`llms.txt`](./llms.txt) / [`AGENTS.md`](./AGENTS.md) |
| **Validation Ledger** | [`EFC_Validation_Ledger.html`](./docs/public/EFC_Validation_Ledger.html) (v3.7) |
| **Papers** | 119+ papers in [`/docs/papers/efc/`](./docs/papers/efc/) |
| **AI Packages** | 41+ with executable Python + structured data |

---

## What EFC Explains

| Phenomenon | Standard Model | EFC Interpretation |
|------------|----------------|-------------------|
| Galaxy rotation curves | Dark matter particles | Discrete entropic gravity (Graph-AQUAL) with Λ-locked screening |
| Cosmic acceleration | Dark energy (Λ) | Thermodynamic expansion via entropy-flow coupling |
| Structure formation | ΛCDM + inflation | Regime-dependent growth (μ < 1 suppresses σ₈) |
| S₈ tension | Systematic error? | L1→L2 regime transition via perturbation-level μ(a) |
| Gravitational waves | c_gw = c trivially | c_gw = c by theorem (both non-minimal and minimal coupling) |
| Radial Acceleration Relation | DM halo tuning | Bose–Einstein occupation number from entropy field |
| Brain functional variability | Unrelated to cosmology | Local degree heterogeneity drives entropy gradient (r ≈ −0.97) |
| RLHF alignment | Engineering heuristic | Algebraically exact thermodynamic free-energy minimisation |

---

## Core Equations

### Phenomenological Coupling (Background)
```
μ(a) = G_eff/G = 1 + βS(a)
```
- **β** = coupling constant (~0.16 from unified analysis)
- **S(a)** = entropy field (0 at CMB → 1 at late times)

### Regime Response Surface
```
μ(k,S) = 1 + R(k,S)
```
- **R(k,S)** = single global response surface for all probes

### EFC Relativistic Action (Cosmological Perturbations)
```
S = ∫ d⁴x √(-g) [ F(φ)R + K(ρ)(∂φ)² + λ(∇_μ φ - J_μ) + L_m ]
```
- **F(φ)R** = non-minimal coupling (entropy-stiffness → μ < 1)
- **K(ρ)** = density-dependent kinetic stiffness (automatic screening)
- **λ(∇φ - J)** = Lagrange-multiplier flow constraint (→ Σ > 1, η ≠ 1)
- **Result**: μ ≈ 0.94, Σ ≈ 1.05, η ≈ 1.10, c_T = c exactly

### Covariant EFT (Galactic Regime)
```
S = ∫ d⁴x √(-g) [ R/(16πG) + ½(∂S)² - V(S) - β|∂S|_ε S² + L_m ]
```
- Minimally coupled scalar S with gradient-field coupling
- **c_gw = c** exactly (theorem for minimally coupled class)
- **RAR** = Bose–Einstein occupation number: μ = 1/(exp(√(g/a₀)) - 1)

### EFC Screening Model (Track 1)
```
ln(μ) = k · ln(1 + g†/g_bar)
```
- **k** = 0.415 ± 0.029 (174 SPARC galaxies)
- **g†** = 2.51 × 10⁻¹⁰ m/s² (transition scale)
- **C** = k/a_G = 4.4 (cross-scale consistency)

### Unified Gradient-Flow Dynamics (Bridge)
```
dF/dt = −∫_Ω |∇ṡ(x,t)|² dV + B[ṡ]
```
- **F** = Helmholtz free energy (Lyapunov functional for all three regimes)
- Connects cosmology, neural entropy, and RLHF

### EFC Field Equation
```
G_μν = 8πG(T_μν + T^(Ef)_μν) + Λ_eff g_μν
```

---

## Multi-Sector Architecture

EFC is partitioned into six physical sectors, each with its own regime and observational constraints:

| Sector | Code | Domain | Key Observable |
|--------|------|--------|----------------|
| **Background** | BG | Expansion history (β, T(a)) | BAO, SN Ia, H(z) |
| **Growth** | GRW | Perturbation-level structure | fσ₈, μ(a), P(k) |
| **Lensing** | LEN | Metric response | κ, γ, Σ(k,z) |
| **Screening** | SCR | Density saturation Θ(ρ) | Solar System PPN, Cassini |
| **Propagation** | PROP | Wave transport | c_gw, standard sirens |
| **Discrete Gravity** | DGS | Graph-AQUAL operator | Rotation curves, SPARC, ξ/η regime |

---

## Three-Track Research Programme

| Track | Domain | Key Paper | DOI |
|-------|--------|-----------|-----|
| **Spor 1** | Galactic & Cosmological Dynamics | EFC Screening Model | [31940469](https://doi.org/10.6084/m9.figshare.31940469) |
| **Spor 2** | Neural Entropy & Psychiatric Biomarkers (EFC-C) | Cognitive Entropy Framework | [31940505](https://doi.org/10.6084/m9.figshare.31940505) |
| **Spor 3** | AI Architecture & Alignment (RLHF) | Thermodynamic Isomorphism | [31940535](https://doi.org/10.6084/m9.figshare.31940535) |
| **Bridge** | Cross-Domain Unification | Bridge Equations B1/B2 | [31940547](https://doi.org/10.6084/m9.figshare.31940547) |
| **Synthesis** | Civilization Map | Homo Fluxus v2.0 | [31940604](https://doi.org/10.6084/m9.figshare.31940604) |

---

## Regime Architecture (L0–L3)

| Regime | Epoch | S value | Physics |
|--------|-------|---------|---------|
| **L0** | Pre-inflation | S → 0 | Quantum-dominated |
| **L1** | CMB (z~1100) | S ≈ 0 | Linear, GR valid (μ≈1) |
| **L1→L2** | Transition | 0 < S < 1 | Regime change |
| **L2** | Late universe | S > 0 | Modified growth (μ<1 at perturbation level) |
| **L3** | Far future | S → 1 | Structure saturation |

**Regime Coordinates** (Discrete Gravity Sector):
- **ξ** = kL_grid — UV–IR transition coordinate
- **η** = μ_Λ Φ / |∇²Φ| — screening regime coordinate

---

## Validation Status

The [Validation Ledger](./docs/public/EFC_Validation_Ledger.html) (v3.7) tracks all empirical, structural, and theoretical results with a four-tier status hierarchy (T1–T4).

### Key Results
| Test | Status | Reference |
|------|--------|-----------|
| Unified BAO/SN/RSD (β=0.16) | T2 — Compatible (Δχ²=+1.7) | [31215613](https://doi.org/10.6084/m9.figshare.31215613) |
| Galaxy rotation curves (SPARC175) | T2 — Completed | [31047703](https://doi.org/10.6084/m9.figshare.31047703) |
| KiDS-1000 cosmic shear | T2 — Completed | [31224739](https://doi.org/10.6084/m9.figshare.31224739) |
| CMB systematic localization | T2 — α≈0 (CMB blind) | [31368433](https://doi.org/10.6084/m9.figshare.31368433) |
| Growth fσ₈ LOO robustness | T2 — α<0 at ~2σ | [31332730](https://doi.org/10.6084/m9.figshare.31332730) |
| EFC Screening (k=0.415, 174 galaxies) | T2 — Completed | [31940469](https://doi.org/10.6084/m9.figshare.31940469) |
| Solar System PPN/EP | T3 — Compatible (γ→1) | [31244827](https://doi.org/10.6084/m9.figshare.31244827) |
| GRAV→(μ,Σ) structural gap | **CLOSED** (v3.4) | [31876324](https://doi.org/10.6084/m9.figshare.31876324) |
| Covariant EFT (c_gw=c, RAR=BE) | T3 — Structural results | [31878334](https://doi.org/10.6084/m9.figshare.31878334) |
| Grid Microphysics (BE RAR derivation) | T3 — Microphysical bridge | [31878760](https://doi.org/10.6084/m9.figshare.31878760) |
| Gradient-Coupled Grid Action (E∝√g) | T3 — Structural | [31941465](https://doi.org/10.6084/m9.figshare.31941465) |
| Regime Transition Test (μ<1→μ>1) | T3 — Numerical consistency | [31941543](https://doi.org/10.6084/m9.figshare.31941543) |
| Void ISW Sign-Flip | T3 — Novel prediction | [31942677](https://doi.org/10.6084/m9.figshare.31942677) |
| Cosmic Dipole Working Note | T4 — Working note | [31942731](https://doi.org/10.6084/m9.figshare.31942731) |
| Entropy Budget Working Note | T4 — Working note | [31942734](https://doi.org/10.6084/m9.figshare.31942734) |
| Density of States Grid Modes | T3 — Microphysical derivation | [31942800](https://doi.org/10.6084/m9.figshare.31942800) |
| Connectome degree heterogeneity (r=−0.97) | T2 — Empirical (Spor 2) | [31940370](https://doi.org/10.6084/m9.figshare.31940370) |
| Cross-domain bridge equations (B1/B2) | T3 — Structural | [31940547](https://doi.org/10.6084/m9.figshare.31940547) |

### Falsification Conditions (F1–F7 + FA1–FA6)
Pre-registered conditions that would falsify EFC sectors. F7 (η=1) formally **PASSED** by relativistic derivation. Six action-level conditions (FA1–FA6) now govern the perturbation sector. See [Validation Ledger](./docs/public/EFC_Validation_Ledger.html) for details.

---

## Key Publications

### Foundational
| Paper | DOI | Status |
|-------|-----|--------|
| EFC v1.2: Foundational Framework | [30563738](https://doi.org/10.6084/m9.figshare.30563738) | Published |
| EFC v2.2: Cross-Field Integration | [30530156](https://doi.org/10.6084/m9.figshare.30530156) | Published |
| AUTH Layer (Provenance) | [30656828](https://doi.org/10.6084/m9.figshare.30656828) | Published |
| EFC Ontological Foundations | [31223668](https://doi.org/10.6084/m9.figshare.31223668) | Published |
| EBE Core Principles | [31222903](https://doi.org/10.6084/m9.figshare.31222903) | Published |

### Empirical Analysis
| Paper | DOI | Key Result |
|-------|-----|------------|
| R(k,S) Response Surface | [31211437](https://doi.org/10.6084/m9.figshare.31211437) | Theoretical framework |
| WP3: First Empirical Slice | [31215259](https://doi.org/10.6084/m9.figshare.31215259) | R≈+0.30 at (k,S) |
| Unified BAO/SN/RSD | [31215613](https://doi.org/10.6084/m9.figshare.31215613) | β=0.16, Δχ²=+1.7 |
| SPARC175 Regime Validation | [31047703](https://doi.org/10.6084/m9.figshare.31047703) | EBE partition |
| KiDS-1000 Cosmic Shear | [31224739](https://doi.org/10.6084/m9.figshare.31224739) | Regime-activated lensing |
| BOSS DR12 BAO Consistency | [31314922](https://doi.org/10.6084/m9.figshare.31314922) | Covariance-aware BAO |
| Growth fσ₈ Robustness (LOO) | [31332730](https://doi.org/10.6084/m9.figshare.31332730) | α<0 at ~2σ, 7/7 LOO |

### Structural & Theoretical
| Paper | DOI | Key Result |
|-------|-----|------------|
| Density Saturation PPN Recovery | [31244827](https://doi.org/10.6084/m9.figshare.31244827) | Solar System screening |
| EFCLASS Sign Structure | [31333414](https://doi.org/10.6084/m9.figshare.31333414) | ΔE²≤0 background exclusion |
| Perturbation-Level σ₈ Suppression | [31333600](https://doi.org/10.6084/m9.figshare.31333600) | μ₀=0.85, 73% gap closure |
| Systematic CMB Localization | [31368433](https://doi.org/10.6084/m9.figshare.31368433) | α≈0 under CMB+BAO |
| Discrete Entropic Gravity (Graph-AQUAL) | [31348411](https://doi.org/10.6084/m9.figshare.31348411) | Newton + MOND + Λ-screening |
| EFC Closure Conjectures | [31224466](https://doi.org/10.6084/m9.figshare.31224466) | Closure ansätze |
| EFC Relativistic Action | [31876324](https://doi.org/10.6084/m9.figshare.31876324) | μ<1, Σ>1, η≠1, c_T=c |
| Covariant EFT (Entropy-Driven Gravity) | [31878334](https://doi.org/10.6084/m9.figshare.31878334) | c_gw=c theorem, RAR=BE |
| Grid Microphysics to RAR | [31878760](https://doi.org/10.6084/m9.figshare.31878760) | BE RAR from 3 assumptions |
| Gradient-Coupled Grid Action | [31941465](https://doi.org/10.6084/m9.figshare.31941465) | E ∝ √g from minimal Lagrangian, operator uniqueness |
| Regime Transition Test | [31941543](https://doi.org/10.6084/m9.figshare.31941543) | μ<1 (linear) ↔ μ>1 (non-linear), R∝k⁻⁴, Δχ²=−0.03 |

### Track 1–3 + Bridge + Synthesis
| Paper | DOI | Key Result |
|-------|-----|------------|
| EFC Screening Model (Track 1) | [31940469](https://doi.org/10.6084/m9.figshare.31940469) | k=0.415, g†=2.51e-10, C=4.4 |
| EFC-C Cognitive Entropy (Track 2) | [31940505](https://doi.org/10.6084/m9.figshare.31940505) | Neural entropy gradients, 3 predictions |
| RLHF Thermodynamic Isomorphism (Track 3) | [31940535](https://doi.org/10.6084/m9.figshare.31940535) | J = −F exactly, 3 predictions |
| Connectome Degree Heterogeneity | [31940370](https://doi.org/10.6084/m9.figshare.31940370) | r = −0.97, κ from degree ratio |
| Cross-Domain Bridge Equations | [31940547](https://doi.org/10.6084/m9.figshare.31940547) | B1/B2, unified gradient flow |
| Homo Fluxus v2.0 (Civilization Map) | [31940604](https://doi.org/10.6084/m9.figshare.31940604) | Grid→EF→S→D→C, empirically anchored |

### Methodology & AI
| Paper | DOI |
|-------|-----|
| Symbiosis Architecture | [30773684](https://doi.org/10.6084/m9.figshare.30773684) |
| Core Lock (Consistency Enforcement) | [31223503](https://doi.org/10.6084/m9.figshare.31223503) |
| ISW Consistency Audit | [31329082](https://doi.org/10.6084/m9.figshare.31329082) |

> See [`/docs/papers/efc/`](./docs/papers/efc/) for the complete collection of 119+ papers with AI-optimized metadata.

---

## AI-Friendly Paper Packages

41+ papers have full AI-friendly packages with executable Python implementations:

| Package | Module | Key Classes |
|---------|--------|-------------|
| EFC Screening Model | `efc_screening.py` | EFCScreening, CrossScaleConsistency, BulletCluster |
| EFC-C Cognitive Entropy | `efc_cognition.py` | NeuralEntropyProduction, EntropyGradient, DisorderSignature |
| RLHF Thermodynamics | `rlhf_thermodynamics.py` | BoltzmannPolicy, FreeEnergyObjective, GrokkingPhaseTransition |
| Connectome Heterogeneity | `connectome_kappa.py` | CentrifugalEntropyScore, ConnectomeAnalysis, NetworkFeatures |
| Cross-Domain Bridge | `bridge_equations.py` | UnifiedGradientFlow, BridgeB1StarStar, BridgeB2Neural2RLHF |
| Homo Fluxus | `homo_fluxus.py` | EFCChain, EgoThermodynamics, DSMReframe, HomoFluxusNode |
| Gradient-Coupled Grid Action | `grid_action.py` | GridAction, GradientCouplingTheorem, OperatorElimination |
| Regime Transition Test | `regime_transition.py` | EFCRegimeTransition, SurvivalValley, SpatiotemporalGrid |
| Void ISW Sign-Flip | `void_isw.py` | ISWDecomposition, SignFlipAnalysis, AmplitudeRatio |
| Cosmic Dipole | `cosmic_dipole.py` | KinematicDipole, EntropyGradient, DipoleAmplitude |
| Entropy Budget | `entropy_budget.py` | CosmicEntropyInventory, BekensteinHawkingEntropy, ThermostatConjecture |
| Density of States Grid Modes | `density_of_states.py` | GridActivation, DensityOfStates, EntropyProductionFunction |
| Grid Microphysics | `grid_microphysics.py` | GridNode, BoseEinsteinRAR, LatticeDerivation |
| Covariant EFT | `covariant_eft.py` | CovEFT, GravWaveSpeed, BoseEinsteinRAR |
| CMB Localization | `cmb_localization.py` | CMBSurvival, LensingBarrier, BackgroundGate |
| Graph-AQUAL | `discrete_gravity.py` | GraphAQUAL, LambdaScreening, RegimeCoordinates |
| EFC Relativistic Action | `efc_relativistic_action.py` | RelativisticAction, PerturbationSector |

Each package includes:
- `src/<module>.py` — Importable Python with documented classes
- `data/<data>.json` — Structured parameters, results, tables
- `examples/<demo>.py` — Executable demonstration (tested)
- `index.json` + `schema.json` + `metadata.json` — Machine-readable metadata
- `*.jsonld` — Linked data
- `citations.bib` — BibTeX references

---

## Repository Structure

```
EFC/
├── auth/               # Origin & provenance (START HERE)
├── theory/             # Formal mathematics
│   └── formal/         # S, D, R, H, C0 models (LaTeX)
├── docs/
│   ├── papers/efc/     # 119+ papers with AI-optimized metadata
│   ├── public/         # Validation Ledger (v3.7), Master Spec, figures
│   ├── figures/        # Shared figures
│   ├── notebooks/      # Jupyter notebooks
│   └── notes/          # Research notes
├── src/
│   └── efc/            # Python modules
│       ├── core/       # Core EFC implementation
│       ├── entropy/    # Entropy calculations
│       ├── perturbation/  # Growth, gate, mu, background
│       ├── potential/  # Potential calculations
│       ├── solver/     # Grid-AQUAL solver & tests
│       ├── validation/ # Validation routines & SPARC I/O
│       └── meta/       # Co-field simulator
├── pipelines/
│   └── efc/native_v2_graph/  # Graph-AQUAL pipeline
│       ├── kernel/     # AQUAL, energy, fields, operators
│       └── tests/      # Kill tests (KT1–KT5)
├── schema/             # Ontology & JSON-LD contexts
├── api/                # Semantic REST API
├── jsonld/             # Linked data files
├── figshare/           # DOI mappings
├── integrations/
│   └── mcp/            # AI Agent MCP Server
├── scripts/            # Validation & plotting scripts
├── tools/              # Comparison utilities
├── meta/               # Meta-architecture & reflection
├── meta-graph/         # Graph structure & relationships
├── methodology/        # Scientific methodology
├── shared/             # Shared configurations
├── llms.txt            # AI navigation (machine-readable)
├── AGENTS.md           # AI integration guide
├── CITATION.cff        # Citation metadata
├── codemeta.json       # Software metadata (CodeMeta 2.0)
├── ecosystem.jsonld    # Ecosystem linked data
└── efc_integration_test.py  # Integration test suite
```

---

## For AI Agents

### Entry Points
1. **[`llms.txt`](./llms.txt)** — Machine-readable navigation
2. **[`AGENTS.md`](./AGENTS.md)** — Detailed integration guide
3. **[`/auth/`](./auth/)** — Provenance and identity
4. **[`/schema/global_schema.json`](./schema/global_schema.json)** — Domain definitions

### MCP Server
```bash
cd integrations/mcp && pip install -r requirements.txt && python efc_mcp_server.py
```

### Paper Metadata Structure
Each paper in `/docs/papers/efc/` contains:
- `README.md` — Human-readable summary
- `index.json` — Machine-readable index (concepts, equations, results)
- `schema.json` — Validation schema
- `metadata.json` — Structured metadata
- `*.jsonld` — Linked data
- `citations.bib` — BibTeX

AI-friendly packages additionally include:
- `src/__init__.py` + `src/<module>.py` — Importable Python implementation
- `data/<data>.json` — Structured data (parameters, results, tables)
- `examples/<demo>.py` — Executable demonstration scripts

---

## Ecosystem

| Surface | Purpose | URL |
|---------|---------|-----|
| GitHub | Technical implementation | [github.com/supertedai/EFC](https://github.com/supertedai/EFC) |
| Figshare | Peer-reviewed DOIs | [figshare.com/authors/Morten_Magnusson](https://figshare.com/authors/Morten_Magnusson/18515981) |
| Theory Site | Public documentation | [energyflow-cosmology.com](https://energyflow-cosmology.com/) |
| Personal | Hypothesis platform | [magnusson.as](https://www.magnusson.as/) |
| ORCID | Academic identity | [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095) |

---

## Citation

```bibtex
@misc{magnusson2026efc,
  author       = {Magnusson, Morten},
  title        = {Energy-Flow Cosmology (EFC)},
  year         = {2026},
  doi          = {10.6084/m9.figshare.30656828},
  url          = {https://github.com/supertedai/EFC},
  note         = {ORCID: 0009-0002-4860-5095}
}
```

---

## License

[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) — Morten Magnusson

---

*"Energy flows along entropy gradients — this is the fundamental dynamic of the Universe."*
