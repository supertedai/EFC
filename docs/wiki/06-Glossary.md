# 06 · Glossary

> Short definitions for the EFC vocabulary, with pointers to where each term is formally defined.

[🏠 Home](./Home.md) · [← For AI agents](./05-For-AI-Agents.md)

---

## Core concepts

**Energy-Flow Cosmology (EFC).** Candidate cosmological framework in which spacetime, structure, and awareness emerge from energy flowing along entropy gradients through a discrete substrate. Author: Morten Magnusson. Primary DOI: [10.6084/m9.figshare.30656828](https://doi.org/10.6084/m9.figshare.30656828).

**Core axiom.** *Energy flows along entropy gradients.* Spacetime curvature emerges from the resulting energy–entropy coupling. Dark matter and dark energy are reinterpreted as thermodynamic effects.

**Grid.** The discrete substrate out of which spacetime emerges. See [`efc-d-model/`](../../theory/formal/efc-d-model/).

**Axiom 0.** Time is an index over irreversible Grid transitions — not a background coordinate.

---

## Regime language

**Regimes L0–L3.** Physical zones indexed by entropy/density:

| Regime | Domain | ΛCDM match |
|---|---|---|
| L0 | High density, low entropy (solar system, inner galaxy) | Exact |
| L1 | Galactic outskirts | Screened transition |
| L2 | Cluster scales, perturbations | Modified μ, Σ, η |
| L3 | Cosmological background, voids | Full entropic response |

**Regime-Consistent Measurement Principle (RCMP).** Cross-regime measurements must use rulers matched to the regime being probed. Violations (V1/V2/V3) produce apparent nulls that are *measurement failures*, not physics failures.

**Regime susceptibility T(S).** Response function quantifying how gravitational coupling varies along the entropy axis. See [White Paper Part 4](https://doi.org/10.6084/m9.figshare.31970907).

---

## Key equations and parameters

**μ(a) = 1 + β·S(a).** Effective coupling at the background level. β ≈ 0.16 (unified BAO/SN/RSD).

**μ(k, S) = 1 + R(k, S).** Perturbation-sector response surface. R(k ≈ 0.13, S ≈ 0.30) ≈ +0.30.

**Σ, η.** Lensing and slip parameters. Perturbation valley: μ ∈ [0.93, 0.96], Σ ∈ [1.03, 1.07], η ≠ 1.

**Screening model.** ln(μ) = k·ln(1 + g†/g_bar), with k = 0.415 ± 0.029 and g† = 2.51×10⁻¹⁰ m/s² from 174 SPARC galaxies.

**Cross-scale constant C.** C = k / a_G ≈ 4.4 — screening/cosmological consistency.

**Unified gradient flow.** dF/dt = −∫|∇ṡ|² dV + B — Lyapunov functional across all regimes.

---

## Evidence-layer vocabulary

**Validation Ledger.** The single source of truth for all validated results. Rendered: [`EFC_Validation_Ledger.html`](../public/EFC_Validation_Ledger.html). Machine: [`evidence-register.json`](../validation-ledger/data/evidence-register.json), [`ledger.json`](../validation-ledger/data/ledger.json).

**Kill-test.** Pre-registered falsification experiment. Five kill criteria are active; failing any falsifies EFC.

**Sealed prediction.** A prediction whose numerical value is registered (via Figshare DOI and `sealed_predictions` in `index.json`) **before** the relevant data is unblinded.

**Tier (T1/T2/T3).** Internal importance ranking. T1 = canonical anchor paper; T2 = core support; T3 = subsidiary/working note.

**Paper type.** `theory` · `empirical_test` · `sealed_prediction` · `methodology` · `infrastructure` · `observational_pipeline`.

**Evidence layers 1/2/3.** (1) EFC publications with own DOI; (2) third-party arXiv (only in §4b); (3) EFC notes confronting externals. Mixing these is claim inflation and rejected by CI.

**Language discipline.** External observations are `consistent with` / `within EFC prediction band` — never `confirms EFC`.

---

## Three-track programme

**Spor 1 — Galactic & Cosmological Dynamics.** SPARC, BAO, CMB, lensing. Anchor: [EFC Screening Model](https://doi.org/10.6084/m9.figshare.31940469).

**Spor 2 — Neural Entropy / EFC-C.** Brain, psychiatry, RLHF. Anchor: [Cognitive Entropy Framework](https://doi.org/10.6084/m9.figshare.31940505).

**Spor 3 — Civilization / Homo Fluxus.** Anchor: [Homo Fluxus v2.0](https://doi.org/10.6084/m9.figshare.31940604).

**Spor 4 — Cross-domain bridges.** B1 (cosmology→neural), B2 (neural→RLHF). Anchor: [Closing the EFC Consciousness Bridge](https://doi.org/10.6084/m9.figshare.31969983).

---

## Stage vocabulary

**Non-rejectable model.** Current EFC stage: not falsified across 103+ tests, but not yet outperforming ΛCDM.

**Global verdict: OPEN.** Neither proven nor falsified.

**Stage-IV surveys.** Euclid DR1 (Oct 2026), DESI, SO, Rubin — the next decisive discriminators. Roadmap: [`EFC_Stage-IV_Data_Roadmap.html`](../public/EFC_Stage-IV_Data_Roadmap.html).

---

## Where things live (shortcuts)

| Thing | Path |
|---|---|
| Formal spec | [`theory/formal/`](../../theory/formal/) |
| All papers | [`docs/papers/efc/`](../papers/efc/) |
| Validation Ledger (rendered) | [`docs/public/EFC_Validation_Ledger.html`](../public/EFC_Validation_Ledger.html) |
| Machine index | [`llms.txt`](../../llms.txt) |
| Agent protocol | [`AGENTS.md`](../../AGENTS.md) |
| Pipelines | [`pipelines/efc/`](../../pipelines/efc/) |
| Maintenance | [`scripts/maintenance/`](../../scripts/maintenance/) |
| DOI registry | [`figshare/doi-map.json`](../../figshare/doi-map.json) |

---

[🏠 Back to Home](./Home.md)
