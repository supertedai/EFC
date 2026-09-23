# Generative synthesis — five seams, four packages, one hub

artifact_type: orchestrator_generative_synthesis
not_reviewer_output: true
run_id: deleg_d21ed669
delegation_id: deleg_90025b05
model: gpt-5.6-luna (all five; agreement = reading consistency, NOT independent validation)
status: NOT findings, NOT verdict, NOT claim-status — candidate hypotheses for a new claim-map round

---

## The hub (one question drives everything)

> **Which physical object — with which unit, normalization, density variable, and observable — is called Γ in each branch?**

Three seams radiate from it:

1. **The Γ seam** — form A/B/C + the BE normalization
2. **The a₀ seam** — MOND input → lattice prefactor → cosmic scale
3. **The transport seam** — static galactic response vs relativistic cosmological field

---

## Package 1 · The Γ response kernel (the form, the dimension, phase-vs-artifact)

**Belongs together:** Γ_A, Γ_B, Γ_C, the BE variable x, u=ρ/ρcrit, l_g, β, sign/unit/normalization.

**Verified algebra:** f(q)=q/(1+q) → Γ_A=f(u), Γ_C=f(√u), Γ_B=√u·f(u).

**The sharp finding (sa-0):** a real dimensional hole. β=4πG_N/3 lacks the reference length r_* (which stands in the docstring but not in the code), so x²/u = 4π/(3·l_g) = **2.59e35 m⁻¹** at l_g=Planck. √u=x requires l_g=4π/3 ≈ 4.19 m. The coordinate identity is therefore **dimensionally blocked**, not established.

**Correction to my own scaffold (important):** that Γ_B diverges as √u while A/C saturate proves that B is a *different function* — but **not** that B is a separate phase. sa-2 found that the sources use A/B/C on **overlapping domains** and describe A as an effective approximation to B; no u→S mapping exists. Γ_B's √u growth is a **high-u extrapolation artifact**, not an S→1 phase boundary.

**Status:** A/B/C = overlapping competing forms of the same Γ(ρ) target; model selection unexecuted (delta_chi2=null in all packages). Separate phase = hypothesis, not source-supported.

**Falsifier:** freeze one Γ0, ρcrit, l_g, β, unit, observable; run A/B/C against the same data + nuisance + likelihood.

---

## Package 2 · The a₀ ladder (five values, C=2.32 fit-not-derived)

**Belongs together:** all acceleration scales + the "5.4× MOND" claim.

**Provenance table (sa-1):**

| Value | Origin | Status |
|---|---|---|
| 1.2e-10 | MOND/SPARC input (a0_base) | empirically imported |
| 1.1e-10 | Verlinde 2016 scale | external frame |
| 6.5e-10 | EFC atlas value, sealed=false/flag | not frozen |
| 6.459e-10 | C²·a₀ = 2.32²·1.2e-10 | algebraic rescaling |
| 9.469e-10 | c²√Λ (lambda_screening.py actual) | separate Λ route |
| 5.097e-9 | C²·c²√Λ | yet another route |
| 6.544e-10 | cH₀(67.36) | cosmic reference |

**The decisive point (sa-1):** C=2.32 is **numerically converged** (2.443→2.354→2.320) but **not analytically derived** — no Watson-integral/Green-function derivation exists in the repo. A separate ledger route gives C_vw=2.2895.

**Therefore:** `a₀,eff=C²a₀` is a **computed rescaling**, not a free prediction. "EFC predicts 5.4× MOND" is too strong. The numerical closeness (atlas 6.5e-10 = cH₀ to 0.7%, C²a₀ to 1.3%) is **not-independent**: a₀ is MOND/SPARC input, C is an internal lattice measurement, the atlas value is itself unresolved.

**Falsifier:** derive C from the cubic Green function/Watson integral without H₀/Λ/SPARC in the input; vary H₀ and Λ independently and see whether C holds.

---

## Package 3 · The broken bridge (grid → RAR → relativistic)

**Belongs together:** S_grid, κeff=κ0+αg, E∝√g, μ_BE(g), G_eff(g), RAR, φ, □φ=Γrel(ρ), μ(k,z), Σ, η, dL^GW/dL^EM.

**This is NOT one chain — it is two, with a break:**

1. **grid→RAR** (most coherent micro-chain, but only to galactic response): grid-action→mode `verified`; mode→BE→RAR `declared` (the source itself says BE-occupation is input and a₀ is not derived).
2. **relativistic→cosmology** (new branch): `declared`, not executed (datasets_used=[]).

**Two sharp findings (sa-3):**

- **Sign/trend contradiction:** the covariant EFT (31878334) gives a classical correction that **increases** with g; the galactic response μ_BE(g) must **decrease**. The source itself says μ_BE had to be postulated by hand because the classical action gave the wrong trend. Edge: `contradicted`.
- **Object/unit break:** Γ in □φ=Γ(ρ) has unit [1/time], positive, saturating. dS/dρ is **negative** under decreasing density (dn/dρ<0). Same Greek letter, two different objects. Edge: `contradicted` (until a typed map exists).

**The √g exponent does not survive** into the relativistic action as the same object (√(-g) there is a metric measure, unrelated to E∝√g). Edge: `open_mapping`.

**The siren (dL^GW/dL^EM) must be held separately** — it is a declared relativistic prediction, not a consequence of RAR or the lattice-Γ.

**Falsifier:** one covariant reduction S_grid→relativistic action + Newton limit that gives the same μ_BE(g); typed map ξ→φ and (m_eff,κ0,α,lg,a₀)→(F,K,V,λ,Γ).

---

## Package 4 · The paradigm map (ΛCDM / MOND / EFC as measurement maps)

**Belongs together:** coordinate chart, measurand, instrument, proxy, nuisance, regime/phase, likelihood, out-of-sample.

**Status of the recovery edges (sa-4):**

- **EFC→ΛCDM (L0/L1):** `declared_formal_limit`, partial sector support, **not** equal-footing empirical recovery. Overlap on the H₀ background; CMB pending (Boltzmann solver). fσ8 drift: 0.430 (EFC) vs 0.449/0.452 (ΛCDM).
- **EFC→MOND (L3):** `declared_deep_MOND_limit`, phenomenological RAR overlap, **not** a mathematical limit; a₀ deviation ~5× unresolved (6.5e-10 vs 1.2e-10). Bullet: EFC 0.9993 vs MOND 0.

**This is the user's own requirement, made concrete:** MOND/ΛCDM/EFC are interpretation differences via different instruments/proxies on overlapping data — but it is **not proven** that they are the same truth until they are run in one shared measurement chain. RECOVERED_BY_LIMIT_OF is today an atlas declaration, not an executed likelihood.

**Calibration-free discriminators (holdout, not loose observables):**

1. **L0/L1:** E_G statistic (shared SO/Euclid data, covariance, nuisance, instrument).
2. **L3/RAR:** SPARC/RAR with frozen a₀ + shared M/L priors.
3. **Bullet:** Δκ as holdout.
4. **Dynamics:** fσ8, BAO, k-dependent growth.
5. **Relativistic:** lensing slip + siren ratio.

---

## Corrections to my own scaffold (made, visible)

1. **G4 was too strong:** "disjoint regimes" → "overlapping competing forms, model selection unexecuted". B's divergence is a functional difference, not phase evidence.
2. **F1 relabeled** (code-structure, not a discovered physical unification).
3. **F2 relabeled** (C=2.32 is a fit, not derived; a₀~cH₀ is inheritance, not an EFC finding).

## Candidate claims for a NEW claim-map version (atomized)

- C-Γ1: Γ_A/B/C share the saturation kernel f but are overlapping forms (not disjoint phases).
- C-Γ2: the BE normalization is dimensionally incomplete (β lacks r_*).
- C-a₀1: a₀ is a ladder of at least 6 values with mixed provenance.
- C-a₀2: C=2.32 is a numerically converged fit, not analytically derived.
- C-bro1: grid→RAR is declared; covariant EFT→μ_BE is contradicted (wrong trend).
- C-bro2: Γ in □φ=Γ(ρ) ≠ dS/dρ (unit + sign differ).
- C-bro3: the √g exponent does not survive into the relativistic action as the same object.
- C-lim1: EFC→ΛCDM is a formal limit, not an equal-footing recovery.
- C-lim2: EFC→MOND is phenomenological overlap, not a mathematical limit; a₀ deviation unresolved.
- C-disc: 5 calibration-free discriminators (E_G, RAR, bullet, fσ8, siren).

These do NOT go into verdict/claim_gate_matrix — they go to a NEW 9-role round with rotated mandates (dimensional analysis, asymptotics, regime, provenance, measurement theory, alternative paradigm, covariant bridge, reproduction, meta).
