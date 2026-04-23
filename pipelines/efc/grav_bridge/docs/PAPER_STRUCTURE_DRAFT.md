# Paper Structure Draft — Growth-Sector Closure

_Drafting scaffold. Not the paper itself. Fill in prose + derivations during write-up._

---

## Proposed title (three options, ranked)

1. **"A structural closure of growth-sector couplings between discrete gravity and cosmology"**
   _Works as section heading in a longer program. Emphasizes the structural nature._

2. **"Growth observables are insufficient to test entropy-flow → cosmology couplings: a structural result"**
   _Foregrounds the observable choice. Stronger methodological framing._

3. **"Multiplicative, local friction, and non-local memory couplings of EFC to growth are excluded by BAO+fσ8"**
   _Most literal; scannable title for database indexing._

**Recommendation:** #1 for the headline version, #3 as arXiv subtitle.

---

## Abstract (draft, ~150 words)

> Theories that modify General Relativity at cosmological scales must couple to observables through an operator structure that is rarely scrutinized independently of parameter inference. We test three independent coupling classes by which an entropy-flow cosmology (EFC) with measured discrete-gravity prefactor C ≈ 2.32 could enter the linear growth equation: (i) multiplicative G_eff-modification of the Poisson source, (ii) additive local friction on the velocity term, (iii) additive non-local memory friction breaking Markov evolution. Using DESI DR2 BAO, cosmic chronometer H(z), an fσ8 compilation, and the E_G observable literature, we find each class either structurally rejected or absorbed by the Ω_m–coupling degeneracy once geometry is locked by BAO+H(z). The growth-only E_G direction (Σ=1) carries no information independent of fσ8. The result is a constraint on coupling structure, not on parameters; it establishes that growth observables alone are insufficient to discriminate this theory class, and that the next informative direction must lie in lensing, gravitational slip, or direct cross-correlations.

---

## Proposed section layout

### 1. Introduction (~1 page)
- Frame the question: parameter inference in modified gravity vs structure elimination.
- Why coupling-structure independence matters: different operator classes can give same fσ8 signature but different E_G / lensing.
- EFC context: the discrete gravity sector yields C ≈ 2.32 (KT2 Grid-AQUAL result). The question is how this imports into cosmology.
- Thesis statement: the growth sector alone admits an empirically determinable closure.

### 2. Framework (~1 page)
- Growth ODE with CosmologyModel abstraction (you already have this; cite cosmology_model.py structure).
- Three coupling classes as modifications of the ODE:
  - Class A: source ∝ G_eff · ρ · δ
  - Class B: friction ∝ β · gate(a) · δ′
  - Class C: friction ∝ β · G(a) · δ′ with G(a) = ∫ gate
- Definitions of the gate g(a), screen(k), kernel G(a).
- Observables: fσ8 (RSD), BAO D_H/D_M/r_d, H(z), E_G.

### 3. Data (~½ page)
- DESI DR2 BAO (13 points, 13×13 covariance).
- Cosmic chronometer H(z) (9 points, diagonal).
- fσ8 compilation (7 points: 6dFGS, SDSS MGS, BOSS DR12 × 3 with 3×3 cov, VIPERS, FastSound).
- E_G literature (5 points: Amon+2018, Reyes+2010, Singh+2019, Blake+2016, de la Torre+2017).
- Sound horizon r_d = 147.09 Mpc (Planck 2018).

### 4. Methodology (~½ page)
- emcee sampler, 32 walkers × 1500 production + 300 burn-in, seed 42.
- Sanity anchors: each variant must reduce to FlatLCDM exactly at its LCDM limit (numerical identity within 10⁻¹⁰).
- Informative Gaussian prior on Ω_m from Step 1 BAO+H(z) used in Steps 2–3 to break the degeneracy.
- Savage–Dickey density ratio for BF(β=0).

### 5. Results — Phase 1: G_eff coupling
- k_Λ sweep at fixed C=2.32 (Table 1, Figure 1).
- Key finding: monotone Δχ² beyond visibility. 2σ exclusion at k_Λ ≈ 0.033; 4σ at k_Λ ≈ 0.053.
- No interior minimum. Visibility and rejection are locked together.

### 6. Results — Phase 2: Local friction
- Fs8-only MCMC shows r(Ω_m, β) = +0.85. Ω_m = 0.357 ± 0.088, β = +0.22 ± 0.47.
- BAO+Hz Ω_m posterior = 0.299 ± 0.009 (Table 2).
- Fs8 + Gaussian Ω_m prior: β → −0.02 ± 0.24, r → +0.19, BF(β=0) = 6.6. Collapse (Figure 2).

### 7. Results — Phase 3: Non-local memory
- Analytic kernel G(a) = δ_a · [ln(1 + e^((a−a_t)/δ_a)) − ln(1 + e^(−a_t/δ_a))].
- Same BAO lock procedure: β = −0.18 ± 0.91, r = +0.19, BF(β=0) = 3.4.
- Normalized comparison: VariantK β ≈ 2·VariantJ β at a=1, so result is equivalent null (Figure 3).

### 8. Results — Phase 4: E_G as redundant axis
- Growth-only modifications yield E_G(z) = Ω_m/f(z). Since fσ8 already measures f(z), E_G adds no orthogonal information with Σ=1.
- Quantitative demonstration: VariantJ β=+1 gives Δχ²(E_G) = +15, which equals the Δχ²(fσ8) for the same parameter. Same signal, different name (Figure 4).

### 9. Discussion — the structural result (~1 page)
- The three null results are not independent failures; they are one coupling-structure null manifesting through three ansätze.
- Why locality was not the bottleneck (Phase 3 settles this).
- Why E_G failed (Phase 4: ratio collapses under Σ=1).
- What this implies: the next informative direction is in the lensing/slip sector or cross-correlations.
- Explicit non-claims: not a statement about EFC's internal consistency; not a statement about KT2's discrete-gravity prefactor.

### 10. Conclusion (½ page)
- Strong statement of the structural closure.
- Explicit next-program items: (a) map which observables are non-degenerate with BAO-locked Ω_m, (b) build Σ-modification variant only after that mapping exists, (c) DESI DR2 fσ8 + Euclid lensing will tighten the constraint but the structural result stands.

### Appendix A — reproducibility
- Code organization, seeds, artifact paths.
- Sanity checks: LCDM identity at C=1 (Phase 1) and β=0 (Phases 2–3) verified to numerical precision.

### Appendix B — analytic derivations
- Memory kernel G(a) via logaddexp stability.
- E_G = Σ·Ω_{m,0}/f(z) derivation in quasi-static limit.

---

## Figures needed (4 main + 2 appendix)

**Figure 1** — Phase 1 k_Λ sweep curve. Δχ² vs k_Λ (log-x). Annotate 2σ, 3σ, 4σ thresholds; annotate the "invisibility floor" G_eff/G < 1.03 region; annotate the k_Λ=0.05 MCMC point. _Artifact: klambda_sweep_20260422_204436.json — need to add this plot; currently not produced._

**Figure 2** — Phase 2 corner: two panels, side-by-side.
  (a) Unrestricted fs8 MCMC — elongated diagonal degeneracy ridge.
  (b) With BAO Ω_m prior — near-circular posterior, β centered on 0.
  _Artifact: outputs/grav_bridge/variant_j_plots_20260422_211020/posterior_2d.png and step2_plots_20260422_212120/posterior_2d.png._

**Figure 3** — Phase 3 memory kernel G(a) overlay on gate g(a). Shows delay/smoothing. Small panel: β posterior for VariantJ (Step 2) vs VariantK (Step 3) on same axis, with "equivalent β_J" scale mapping.
  _Artifact: need to generate combined figure from existing chains._

**Figure 4** — Phase 4 E_G(z). Literature points with errorbars, LCDM curve, VariantJ best-fit curve, VariantJ β=+1 (excluded) curve.
  _Artifact: outputs/grav_bridge/phase4_e_g_plot_20260422_214807.png._

**Appendix Figure 1** — Residuals panel: fs8 data − model for LCDM and VariantJ best-fit. Shows χ² is the same.
  _Artifact: outputs/grav_bridge/step2_plots_*/residuals.png._

**Appendix Figure 2** — Sanity check: numerical identity at coupling = 0. Log-scale |Δfσ8| vs z for β=0 and C=1 cases; all points < 10⁻¹⁰.
  _Artifact: needs to be generated._

---

## Explicit claims (pull quotes for the paper)

- **C1.** For VariantI (multiplicative G_eff with low-pass Fourier screen), no k_Λ ∈ [0.003, 0.2] admits a fσ8-data-compatible signal with fixed C=2.32; the minimum Δχ² in the observable regime is ≥ 0.5 at k_Λ ≥ 0.015, and the posterior has no interior minimum.

- **C2.** For VariantJ (local friction) under BAO+H(z) Ω_m prior N(0.299, 0.009), the friction amplitude β = −0.020 ± 0.243 is consistent with zero at 0.08σ; BF(β=0) = 6.6.

- **C3.** For VariantK (non-local memory friction) under the same BAO prior, β = −0.18 ± 0.91 remains consistent with zero at 0.20σ; BF(β=0) = 3.4. When normalized to equivalent amplitude at a=1, the result is statistically indistinguishable from C2.

- **C4.** For all three variants, the E_G(z) predictions at best-fit parameters reproduce the literature compilation within 0.11 χ² of FlatLCDM; E_G with Σ=1 carries no independent discriminatory information beyond fσ8.

- **C5 (combined).** Any coupling of EFC to cosmology that modifies only the growth equation (source, local friction, or non-local memory friction) through a logistic-gate-mediated operator is either structurally excluded or unidentifiable under current BAO+fσ8+E_G data.

---

## What NOT to claim

- NOT: "EFC is falsified."
- NOT: "Modified gravity is ruled out."
- NOT: "C = 2.32 is incorrect."
- NOT: "A scalar-tensor MOND bridge cannot exist."
- NOT: "Future data cannot constrain this class" — just that current data cannot.

---

## Status of figures / scripts

| Figure | Scripts that exist | Missing |
|--------|-------------------|---------|
| 1 | klambda sweep → JSON | plot script for sweep curve |
| 2 | variant_j_mcmc + step2 produce individual corners | combined 2-panel figure |
| 3 | step2, step3 JSONs; G(a) analytic | combined overlay figure |
| 4 | phase4_e_g_plot_*.png exists | — |
| App 1 | step2_plots/residuals.png exists | — |
| App 2 | variant_i_sanity produces the zero comparison | dedicated plot script |

Three plot scripts need to be added before paper submission. All chains and summaries already exist.

---

## Recommended writing order

1. Fill in derivations in Appendix B first (forces mathematical consistency).
2. Write Results sections 5–8 from the existing summary JSONs (numbers are already verified).
3. Draft Discussion (section 9) — this is where the structural insight lives.
4. Write Introduction and Framework last, once the result is crystalline.
5. Abstract last, once all pieces fit.

---

_Ready to start writing whenever you give the go-ahead. I can draft any section in full prose from this scaffold — just point at which one._
