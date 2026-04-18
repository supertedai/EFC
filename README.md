# Energy-Flow Cosmology (EFC)

> **Core Principle**: Energy flows along entropy gradients — this generates spacetime, structure, and awareness.

> 🧭 **New here?** Start at the [**EFC Wiki → Home**](./docs/wiki/Home.md) — role-based routing for readers, physicists, reproducers, and AI agents.

## In plain English (a 60-second version)

Today's standard picture of the universe says **95%** of it is made of two invisible ingredients — **dark matter** (the glue that holds galaxies together) and **dark energy** (the pressure that makes space expand faster and faster) — neither ever detected in a laboratory. The 5% we can actually measure is the only part nobody argues about.

**EFC proposes a simpler idea:** gravity adjusts itself where disorder (entropy) is still building up, and behaves like ordinary Einstein gravity everywhere else. **One mechanism, two numbers, no invisible particles required.**

But the deepest difference is **ontological, not parametric.** ΛCDM treats spacetime as a fixed stage and dark matter / dark energy as *ingredients* populating it. EFC treats **energy and entropy as primary** — spacetime, the effective gravitational response, and even *time itself* (as an index over irreversible Grid transitions, *Axiom 0*) emerge from energy flowing along entropy gradients through a discrete substrate. The "dark sector" is not a set of missing particles; it is what a coarse-grained observer measures when cross-regime physics is read with single-regime rulers (*Regime-Consistent Measurement Principle*). Same observations, fewer primitives, different picture of what the universe is made of. See the [Elevator Pitch](./docs/public/EFC_Elevator_Pitch.html) for the full side-by-side.

Across **103 independent tests** so far (galaxy rotation curves, the cosmic microwave background, galaxy cluster collisions, cosmic expansion), EFC has not been ruled out. It does not yet *outperform* the standard model — the margins are too small to call a winner — but it survives every test. The decisive experiments are pre-registered in the [Stage-IV Data Roadmap](./docs/public/EFC_Stage-IV_Data_Roadmap.html).

**Status:** candidate theory under test. Non-rejectable. Not proven. Not falsified. Global verdict remains **OPEN**.

**What EFC does NOT claim:** that it is proven correct, that standard cosmology is wrong, or that dark matter is "disproven." It only claims: *here is a simpler alternative that current data cannot rule out, with explicit kill criteria the next generation of surveys will test.*

---

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.30656828-blue)](https://doi.org/10.6084/m9.figshare.30656828)
[![ORCID](https://img.shields.io/badge/ORCID-0009--0002--4860--5095-green)](https://orcid.org/0009-0002-4860-5095)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Validation Ledger](https://img.shields.io/badge/Validation_Ledger-v3.17-orange)](./docs/public/EFC_Validation_Ledger.html)
[![AI Packages](https://img.shields.io/badge/AI_Packages-150-brightgreen)](#ai-friendly-paper-packages)

> **NEW (April 12, 2026)**: **[Euclid DR1 Pre-Registration Pipeline](./pipelines/efc/euclid_dr1/)** ([DOI 10.6084/m9.figshare.31990053](https://doi.org/10.6084/m9.figshare.31990053)) — Complete Boltzmann-calibrated prediction pipeline using custom `efc_logistic` gravity model in hi_class. SHA-256 sealed benchmark (B0=0.02, M0=0.06): σ₈ +1.21%, P(k) +2.09%, lensing −6.01%, E_G −3.98%. 36-point parameter scan. Stability: M0≥3B0. Planck ISW: M0<0.1. Predictions frozen for Euclid DR1 (October 2026).

> **NEW (April 11, 2026)**: **[Kill-Test v6 Universality on SPARC 175](./docs/papers/efc/Kill-Test%20v6%20Universality_SPARC175/)** ([DOI 10.6084/m9.figshare.31986762](https://doi.org/10.6084/m9.figshare.31986762)) — Extended Kill-Test v6 probe-2 methodology to all 175 SPARC galaxies (identical `scipy.differential_evolution` pipeline, seed = 42, AIC model comparison). **EFC win rate 60.2%** on 171 successfully fitted galaxies (42.1% EFC_decisive); median ΔAIC = +6.21 (favours EFC); median χ²_red 0.44 (EFC) vs 1.69 (NFW); Mann-Whitney FLOW vs LATENT p ≈ 0; Spearman ρ(ΔAIC, v_max) = 0.11 (no mass bias); DDO 154 anchor cross-check: ΔAIC = +125.2. **Cherry-picking objection against probe-2 refuted; universality verdict CONFIRMED at single-component level.**

> **NEW (April 9, 2026)**: **[EFC White Paper Series (Parts 1-4)](./docs/papers/efc/efc_white_paper_part_1_to_4/)** — Canonical four-part reference. [Part 1](https://doi.org/10.6084/m9.figshare.31970886): Recovery conditions (EFC ⊃ ΛCDM). [Part 2](https://doi.org/10.6084/m9.figshare.31970898): Field equations & observable mapping. [Part 3](https://doi.org/10.6084/m9.figshare.31970904): Validation ledger & falsification protocol (102 tests, 5 kill criteria). [Part 4](https://doi.org/10.6084/m9.figshare.31970907): Regime susceptibility T(S) & dynamical dark energy.

> **NEW (April 9, 2026)**: [EFC Consciousness Bridge](https://doi.org/10.6084/m9.figshare.31969983) — Closes the open bridge between cosmological entropy field S and EFC-C cognitive variables via a **three-equation system** with one free parameter (γ). Non-separable functional C = Ω̂κ̂(1 − e^{−γΩ̂κ̂}), coupled dynamics, dimensionless regime-indexed variables L0–L3. 5/5 propofol predictions consistent. K = 4.4 ± 0.6 from SPARC.

> **NEW (April 8, 2026)**: [EFC vs ΛCDM — Complete Kill-Test v6](https://doi.org/10.6084/m9.figshare.31964847) — Six-probe kill-test L0→L3. All **four cobaya minimize runs return Δχ² ≤ 0** (MGCAMB −0.45, A_lens proxy −0.81, A_lens free −0.70, K₀/m² −0.30). **Stage: Non-rejectable model.**

> **NEW (April 8, 2026)**: [Bullet Cluster Under EFC](https://doi.org/10.6084/m9.figshare.31963668) — Four-axis confrontation with three JWST-era studies. PIEMD A_sig baseline null (p = 0.98). Pre-registered δκ shock-front test pending as decisive discriminator.

> **NEW (April 8, 2026)**: [KT3b Cross-Regime Measurement Failure](https://doi.org/10.6084/m9.figshare.31963821) — Null result diagnosed as cross-regime measurement failure (RCMP violations V1/V2/V3). Three valid replacement architectures proposed.

> **Earlier (April 2026)**: [WP4 BOSS Transfer](https://doi.org/10.6084/m9.figshare.31954125) (Δχ² = −7.77, k_eff = 0) · [Multi-epoch fσ₈ Growth](https://doi.org/10.6084/m9.figshare.31955871) (null, B = 0 within 1σ) · [DES Y6 P3 PASS](https://doi.org/10.6084/m9.figshare.31951992) (0.944 ± 0.018 vs 0.95 ± 0.03) · [ΛCDM as Special Case](https://doi.org/10.6084/m9.figshare.31943361) (DESI DR2: α = −0.14 ± 0.21)

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
| **Validation Ledger** | [`EFC_Validation_Ledger.html`](./docs/public/EFC_Validation_Ledger.html) (v3.17 public / v4.8 internal) |
| **Papers** | 150 papers in [`/docs/papers/efc/`](./docs/papers/efc/) |
| **AI Packages** | 138 with executable Python + structured data (100% coverage) |
| **Stage** | **Non-rejectable model** — Δχ² ≤ 0 across all probes; global verdict OPEN |
| **Validation Reports** | EFC-VAL-2026-002 through 007 (6 hand-curated 10/10 packages) |
| **Consolidation** | [ΛCDM as Special Case of EFC](https://doi.org/10.6084/m9.figshare.31943361) — single reference for full programme |

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
- **No-Go**: Background-level H(z) modification cannot suppress σ₈ (ΔE² ≤ 0); all growth effects enter via perturbation sector ([31333414](https://doi.org/10.6084/m9.figshare.31333414))

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
| **Consolidation** | Full Programme | ΛCDM as Special Case of EFC | [31943361](https://doi.org/10.6084/m9.figshare.31943361) |

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

The [Validation Ledger](./docs/public/EFC_Validation_Ledger.html) (v3.17 / v4.8 internal) tracks 103 public tests. Overall stage: **Non-rejectable model** (global verdict OPEN).

### EFC White Paper Series (Canonical Reference)

| Part | Title | DOI |
|------|-------|-----|
| **Part 1** | Recovery Conditions and the LCDM Limit | [31970886](https://doi.org/10.6084/m9.figshare.31970886) |
| **Part 2** | Field Equations and Observable Mapping | [31970898](https://doi.org/10.6084/m9.figshare.31970898) |
| **Part 3** | Data, Validation Ledger, and Falsification Protocol | [31970904](https://doi.org/10.6084/m9.figshare.31970904) |
| **Part 4** | Regime Susceptibility and Cross-Scale Mapping | [31970907](https://doi.org/10.6084/m9.figshare.31970907) |

### Hand-Curated Validation Reports (10/10 AI-Friendly Packages)

| Report | Title | Key Result | DOI |
|--------|-------|-----------|-----|
| **EFC-VAL-2026-002** | WP4 BOSS DR12 Transfer | Δχ² = −7.77 (k_eff = 0; 71% in constrained eigenmodes) | [31954125](https://doi.org/10.6084/m9.figshare.31954125) |
| **EFC-VAL-2026-003** | Multi-epoch fσ₈ Growth | Null: B = 0 within 1σ; Δχ² = 0.10 (0.06σ) | [31955871](https://doi.org/10.6084/m9.figshare.31955871) |
| **EFC-VAL-2026-004** | Bullet Cluster Under EFC | A_sig = −6.9e-4 (p = 0.98 null); δκ shock test pending | [31963668](https://doi.org/10.6084/m9.figshare.31963668) |
| **EFC-VAL-2026-005** | KT3b Cross-Regime Failure | RCMP violations V1/V2/V3; 3 valid architectures proposed | [31963821](https://doi.org/10.6084/m9.figshare.31963821) |
| **EFC-VAL-2026-006** | EFC vs ΛCDM Kill-Test v6 | 4/4 cobaya Δχ² ≤ 0; K₀ = 1.552, m² = 0.00318 | [31964847](https://doi.org/10.6084/m9.figshare.31964847) |
| **EFC-VAL-2026-007** | EFC Consciousness Bridge | Three-equation system; 1 free param (γ); 5/5 propofol consistent | [31969983](https://doi.org/10.6084/m9.figshare.31969983) |
| **EFC-VAL-2026-008** | Kill-Test v6 Universality (SPARC 175) | 60.2% EFC win rate on 171/175; median ΔAIC = +6.21; cherry-picking refuted | [31986762](https://doi.org/10.6084/m9.figshare.31986762) |

### Selected Earlier Results
| Test | Status | Reference |
|------|--------|-----------|
| P3 — DES Y6 lensing S₈ ratio | **PASS** (0.944 ± 0.018 vs 0.95 ± 0.03, 0.3σ) | [31951992](https://doi.org/10.6084/m9.figshare.31951992) |
| ΛCDM as Special Case (Consolidation) | DESI DR2: α = −0.14 ± 0.21 | [31943361](https://doi.org/10.6084/m9.figshare.31943361) |
| EFC Screening (k = 0.415, 174 SPARC) | Completed | [31940469](https://doi.org/10.6084/m9.figshare.31940469) |
| EFC Relativistic Action | μ < 1, Σ > 1, η ≠ 1, c_T = c | [31876324](https://doi.org/10.6084/m9.figshare.31876324) |
| Covariant EFT (c_gw = c, RAR = BE) | Structural results | [31878334](https://doi.org/10.6084/m9.figshare.31878334) |
| Galaxy rotation curves (SPARC175) | Completed | [31047703](https://doi.org/10.6084/m9.figshare.31047703) |
| KiDS-1000 cosmic shear | Completed | [31224739](https://doi.org/10.6084/m9.figshare.31224739) |
| Connectome heterogeneity (r = −0.97) | Empirical (Spor 2) | [31940370](https://doi.org/10.6084/m9.figshare.31940370) |

### Falsification Conditions (F1–F7 + FA1–FA6)
Pre-registered conditions that would falsify EFC sectors. F7 (η=1) formally **PASSED** by relativistic derivation. Six action-level conditions (FA1–FA6) govern the perturbation sector. See [Validation Ledger](./docs/public/EFC_Validation_Ledger.html) for details.

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
| **Background No-Go Theorem** | [31333414](https://doi.org/10.6084/m9.figshare.31333414) | Three-pillar proof: sign lemma + CLASS + CMB+BAO → background sector empty |
| Perturbation-Level σ₈ Suppression | [31333600](https://doi.org/10.6084/m9.figshare.31333600) | μ₀=0.85, 73% gap closure |
| Systematic CMB Localization | [31368433](https://doi.org/10.6084/m9.figshare.31368433) | α≈0 under CMB+BAO |
| Discrete Entropic Gravity (Graph-AQUAL) | [31348411](https://doi.org/10.6084/m9.figshare.31348411) | Newton + MOND + Λ-screening |
| EFC Closure Conjectures | [31224466](https://doi.org/10.6084/m9.figshare.31224466) | Closure ansätze |
| EFC Relativistic Action | [31876324](https://doi.org/10.6084/m9.figshare.31876324) | μ<1, Σ>1, η≠1, c_T=c |
| Covariant EFT (Entropy-Driven Gravity) | [31878334](https://doi.org/10.6084/m9.figshare.31878334) | c_gw=c theorem, RAR=BE |
| Grid Microphysics to RAR | [31878760](https://doi.org/10.6084/m9.figshare.31878760) | BE RAR from 3 assumptions |
| Gradient-Coupled Grid Action | [31941465](https://doi.org/10.6084/m9.figshare.31941465) | E ∝ √g from minimal Lagrangian, operator uniqueness |
| Regime Transition Test | [31941543](https://doi.org/10.6084/m9.figshare.31941543) | μ<1 (linear) ↔ μ>1 (non-linear), R∝k⁻⁴, Δχ²=−0.03 |
| **Scale-Localised Modified Gravity** | [31985313](https://doi.org/10.6084/m9.figshare.31985313) | Band-pass R(k,a); E_G bump ~7% at k_c=0.05 h/Mpc; testable 2.5–3.5σ |

### Track 1–3 + Bridge + Synthesis
| Paper | DOI | Key Result |
|-------|-----|------------|
| EFC Screening Model (Track 1) | [31940469](https://doi.org/10.6084/m9.figshare.31940469) | k=0.415, g†=2.51e-10, C=4.4 |
| EFC-C Cognitive Entropy (Track 2) | [31940505](https://doi.org/10.6084/m9.figshare.31940505) | Neural entropy gradients, 3 predictions |
| RLHF Thermodynamic Isomorphism (Track 3) | [31940535](https://doi.org/10.6084/m9.figshare.31940535) | J = −F exactly, 3 predictions |
| Connectome Degree Heterogeneity | [31940370](https://doi.org/10.6084/m9.figshare.31940370) | r = −0.97, κ from degree ratio |
| Cross-Domain Bridge Equations | [31940547](https://doi.org/10.6084/m9.figshare.31940547) | B1/B2, unified gradient flow |
| Homo Fluxus v2.0 (Civilization Map) | [31940604](https://doi.org/10.6084/m9.figshare.31940604) | Grid→EF→S→D→C, empirically anchored |
| **ΛCDM as Special Case of EFC** | [31943361](https://doi.org/10.6084/m9.figshare.31943361) | **Consolidation: ΛCDM = L0/L1 limit, DESI DR2 α=−0.14±0.21** |

### Validation Reports (EFC-VAL-2026 Series)
| Paper | DOI | Key Result |
|-------|-----|------------|
| WP4 BOSS DR12 Transfer (002) | [31954125](https://doi.org/10.6084/m9.figshare.31954125) | Δχ² = −7.77 frozen transfer |
| Multi-epoch fσ₈ Growth (003) | [31955871](https://doi.org/10.6084/m9.figshare.31955871) | Null: B = 0 within 1σ |
| Bullet Cluster Under EFC (004) | [31963668](https://doi.org/10.6084/m9.figshare.31963668) | A_sig PIEMD null (p = 0.98) |
| KT3b Cross-Regime Failure (005) | [31963821](https://doi.org/10.6084/m9.figshare.31963821) | RCMP V1/V2/V3, 3 architectures |
| EFC vs ΛCDM Kill-Test v6 (006) | [31964847](https://doi.org/10.6084/m9.figshare.31964847) | 4/4 Δχ² ≤ 0, non-rejectable |
| EFC Consciousness Bridge (007) | [31969983](https://doi.org/10.6084/m9.figshare.31969983) | Three-eq system, 1 free param |

### Methodology & AI
| Paper | DOI |
|-------|-----|
| Symbiosis Architecture | [30773684](https://doi.org/10.6084/m9.figshare.30773684) |
| Core Lock (Consistency Enforcement) | [31223503](https://doi.org/10.6084/m9.figshare.31223503) |
| ISW Consistency Audit | [31329082](https://doi.org/10.6084/m9.figshare.31329082) |

> See [`/docs/papers/efc/`](./docs/papers/efc/) for the complete collection of 150 papers, all with AI-friendly packages (100% coverage). Eight hand-curated 10/10 validation reports with full reproducible pipelines.

---

## AI-Friendly Paper Packages

All 150 papers have AI-friendly packages (100% coverage as of April 2026). Eight hand-curated 10/10 validation reports with full reproducible pipelines:

| Package | Module | Key Functionality |
|---------|--------|-------------------|
| **EFC vs ΛCDM Kill-Test v6** | `kill_test_suite.py`, `k_rho_bridge.py`, `gravitational_slip.py`, `cobaya_minimize.py` | Six-probe kill-test, K(ρ) bridge, sector decomposition |
| **Kill-Test v6 Universality (SPARC 175)** | `sparc175_killtest_universality.py` | Single-component EFC + NFW on all 175 SPARC galaxies; 60.2% EFC win rate |
| **Bullet Cluster Under EFC** | `asig_2d_piemd.py` | PIEMD 4-halo A_sig operator, bootstrap null test |
| **KT3b Cross-Regime** | `rcmp_check.py` | RCMP linter for V1/V2/V3 violations, 4 architecture factories |
| **Multi-epoch fσ₈ Growth** | `efc_multi_epoch_v2.py` | Full linear growth ODE, μ(a) gate, 14-point fit |
| **WP4 BOSS Transfer** | `wp4_transfer.py` | Regime gate, covariance diagnostics, Cholesky whitening |
| **Consciousness Bridge** | `consciousness_bridge.py` | Three-equation system, non-separable C, regime mapping |
| **Euclid DR1 Pre-Registration** | `efc_logistic_demo.py`, `run_benchmark.py` | hi_class Boltzmann with custom `efc_logistic` gravity model, SHA-256 sealed predictions |

Plus 127 auto-generated packages each containing:

| Package | Module | Key Classes |
|---------|--------|-------------|
| EFC Screening Model | `efc_screening.py` | EFCScreening, CrossScaleConsistency |
| EFC-C Cognitive Entropy | `efc_cognition.py` | NeuralEntropyProduction, EntropyGradient |
| RLHF Thermodynamics | `rlhf_thermodynamics.py` | BoltzmannPolicy, FreeEnergyObjective |
| Connectome Heterogeneity | `connectome_kappa.py` | CentrifugalEntropyScore, ConnectomeAnalysis |
| Cross-Domain Bridge | `bridge_equations.py` | UnifiedGradientFlow, BridgeB1StarStar |
| Gradient-Coupled Grid Action | `grid_action.py` | GridAction, GradientCouplingTheorem |
| ΛCDM as Special Case | `lcdm_special_case.py` | LCDMReduction, KillTestSuite |
| DES Y6 Lensing | `des_y6_validation.py` | P3LensingTest, EFCLensingPrediction |

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
│   ├── papers/efc/     # 150 papers with AI-friendly packages (100%)
│   ├── public/         # Validation Ledger (v3.15), Master Spec, figures
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
│   └── efc/
│       ├── native_v2_graph/  # Graph-AQUAL pipeline
│       │   ├── kernel/     # AQUAL, energy, fields, operators
│       │   └── tests/      # Kill tests (KT1–KT5)
│       └── euclid_dr1/      # Euclid DR1 pre-registration pipeline
│           ├── src/        # mu/eta/Sigma, hi_class bridge, mock likelihood
│           ├── config/     # hi_class .ini, cobaya .yaml
│           ├── data/       # Alpha table, benchmark, parameter scan, hi_class patch
│           ├── tests/      # 6 sanity checks (A–F)
│           └── docs/       # RCMP compliance matrix
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
