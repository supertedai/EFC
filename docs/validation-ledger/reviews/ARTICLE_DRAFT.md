# Energy-Flow Cosmology Across Discrete, Entropic, Covariant, and Phenomenological Descriptions: A Reconciliation and Adversarial Review

> **Scope note (for the author's own review):** This is a review and validation report, not the theory paper. It reconciles how the EFC layers (discrete grid, entropy production, Bose–Einstein response, covariant EFT, the MOND/ΛCDM comparison) hang together. The central finding: most reviewed internal relations and numerical results survive the review, while roughly six stronger physical claims must be downgraded or closed further — above all the covariant bridge (μ_BE is postulated, not derived) and "EFC predicts 5.4× MOND" (a₀ is inherited, not independent). The report was written with nine role mandates in one model family — agreement is reading-consistency, never independent validation. Release/DOI is not approved.

**Draft for author review. Not peer reviewed. Not approved for release or DOI deposition.**

---

## Abstract

We perform a source-bound reconciliation of several Energy-Flow Cosmology (EFC) descriptions spanning discrete grid dynamics, entropy-production constructions, Bose–Einstein-inspired response functions, covariant effective actions, and phenomenological comparisons with MOND and ΛCDM. The review separates algebraic identities, model-relative statements, declared mappings, numerical measurements, empirical comparisons, and unresolved physical identifications.

The response functions conventionally denoted Γ_A, Γ_B, and Γ_C are algebraically related in a normalized representation, but this does not establish that they are the same physical observable across source packages or regimes. The implemented Bose–Einstein normalization contains an unresolved dimensional mismatch: the documented coupling contains a reference length r_*, whereas the executed code omits it. The prefactor C = 2.32 is supported as a numerically converged lattice estimate, not as an analytically derived Watson or Green-function constant. The apparent relation a₀ ~ cH₀ is not an independent EFC prediction because the relevant quantities share declared or inherited inputs. Most importantly, the proposed covariant connection to the effective μ_BE response contains a derivation gap: the classical covariant correction and the proposed μ_BE response have opposite acceleration trends, while the latter is postulated rather than derived.

Formal EFC limits toward MOND-like and ΛCDM-like descriptions should therefore be treated as declarations of limiting interpretation, not as equal-footing empirical recoveries. The review identifies the calculations and common-data likelihoods required to close these gaps. The present article is a transparent reconciliation draft and does not constitute a release verdict.

---

## 1. Scope and review protocol

This article reconciles the following layers:

- discrete graph/grid dynamics;
- entropy-production and density-of-states constructions;
- response-kernel parameterizations;
- covariant effective-field descriptions;
- MOND and ΛCDM comparison layers;
- measurement, provenance, and falsification design.

**Honesty condition.** The review used nine role mandates and ten gates. The role mandates were executed within the same model family and therefore do **not** constitute independent external validation. Their value is structured cross-reading, source tracing, adversarial challenge, and reproducibility checking. Agreement across roles is *reading consistency*, never independent validation.

The review distinguishes:

- `verified` — directly reproduced from source or code;
- `declared` — asserted by the source without derivation;
- `open_mapping` — relation proposed but not typed or normalized;
- `contradicted` — source-level trend or sign conflict;
- `blocked` — required empirical or mathematical artifact is absent;
- `not_applicable` — used only where the gate genuinely does not apply.

---

## 2. Response kernels

In the normalized representation used by the review,

$$f(q) = \frac{q}{1+q},$$

the code-level forms satisfy

$$\Gamma_A(u) = f(u), \qquad
\Gamma_C(u) = f(\sqrt{u}) = \frac{\sqrt{u}}{1+\sqrt{u}}, \qquad
\Gamma_B(u) = \sqrt{u}\,f(u) = \frac{u^{3/2}}{1+u}.$$

These identities are exact within the declared normalized representation. They establish an algebraic relation between forms, **not** a physical identity between all quantities called Γ in the repository.

The distinction matters because the repository also contains: per-mode entropy-production coefficients; total entropy-production functions; phenomenological saturation functions; and a covariant source Γ(ρ) in a field equation. These objects have different functional forms, units, signs, and normalizations. In particular, Γ_A and Γ_C saturate at high u, whereas Γ_B grows asymptotically as √u. No typed u→S, u→L_i, or field-normalization map currently identifies these as a single physical response.

---

## 3. Dimensional normalization

The documentation states a coupling of the form

$$\beta = \frac{4\pi G_N r_*}{3},$$

while the executed implementations use

$$\beta_{\rm code} = \frac{4\pi G_N}{3}.$$

The reference length r_* is therefore present in the documented expression but absent from the executed path. With

$$u = \frac{\rho}{\rho_{\rm crit}}, \qquad \rho_{\rm crit} = \frac{a_0}{G_N l_g}, \qquad x^2 = \frac{\beta \rho}{a_0},$$

the implemented code gives

$$\frac{x^2}{u} = \frac{\beta}{G_N l_g} = \frac{4\pi}{3 l_g}.$$

For l_g = L_Planck, this is approximately 2.592×10³⁵ m⁻¹, not a dimensionless unity. The algebraic closure condition x²/u = 1 would require β = G_N l_g, or, under the documented form, r_* = 3l_g/(4π).

This is a mathematical normalization condition, not evidence that the physical convention has been established. The repository must explicitly define r_*, l_g, their units, and their relation before x = √u can be treated as a physical identification.

---

## 4. The prefactor C

The lattice convergence sequence is

$$C(N{=}21) = 2.443, \qquad C(N{=}31) = 2.354, \qquad C(N{=}41) = 2.320.$$

The available source supports the statement that C is numerically converged within the reported finite-grid procedure. It does **not** support calling C = 2.32 an analytically derived constant.

A direct numerical evaluation of the simple-cubic Watson integral gives approximately W = 0.505462, and no simple tested normalization of this free-space quantity reproduces C = 2.32. This does not disprove a future derivation based on the actual nonlinear radial AQUAL estimator; it shows only that the free-space Watson value is not itself the reported prefactor.

A separate ledger entry reports C_ledger = 2.2895486402403438. Direct matched-parameter runs of the modular and standalone solver implementations produced values identical to the reported numerical precision at tested resolutions: C(N=21) = 2.443115, C(N=31) = 2.354499 (Δ = 0.000% at the reported precision). Thus the hypothesis that the discrepancy is caused by different solver algorithms is not supported. The remaining issue is provenance: the ledger value lacks a reproducing configuration on disk. It may reflect different parameters, a different measurement window, or a stale ledger entry. The discrepancy remains open but is not evidence of a fundamental second coupling.

---

## 5. The a₀ ladder

The repository contains several quantities under the a₀ label or its derived scales, including:

- 1.2×10⁻¹⁰ m s⁻², used as a MOND/SPARC-scale input;
- 1.1×10⁻¹⁰ m s⁻², used as an external comparator;
- 6.5×10⁻¹⁰ m s⁻², present as an unsealed atlas value;
- C²·a₀,base ≈ 6.46×10⁻¹⁰ m s⁻²;
- c²√Λ, a separate Λ-derived scale;
- cH₀ ≈ 6.544×10⁻¹⁰ m s⁻², a derived cosmological reference.

These values have heterogeneous provenance. The numerical proximity of C²a₀, cH₀, and the atlas value is **not** an independent prediction because the quantities share declared inputs or algebraic ancestry.

The stored `a0_kpc` value is inconsistent with the SI value it appears to represent. It is currently latent because no downstream consumer was identified, but it should be repaired or quarantined before any numerical a₀ bridge is used.

---

## 6. Transport from grid dynamics to covariant response

The proposed chain contains edges of different epistemic types:

$$\text{grid action} \to \text{mode response} \to \text{Bose–Einstein form} \to \text{RAR} \to \text{covariant response}.$$

The grid-to-mode step is internally formal under the declared approximation. The mode-to-Bose–Einstein step assumes the relevant ensemble and statistics. The Bose–Einstein-to-RAR step is conditional on the selected acceleration coordinate and a₀ normalization.

The covariant-to-μ_BE step is **not closed**. The covariant classical correction increases with acceleration, whereas the proposed μ_BE(g) decreases toward high acceleration. The source treats μ_BE as an effective postulate rather than deriving it from the covariant action.

A second typed mismatch concerns □φ = Γ(ρ), the entropy derivative dS/dρ, and the positive per-mode absolute-value coefficient. These quantities differ in sign, units, field normalization, and time dependence. No map currently establishes their identity. Likewise, √g_acc is an acceleration-dependent response factor, while √(−g_metric) is a metric volume-measure factor. The shared symbol g does not make them the same object.

---

## 7. MOND, ΛCDM, and EFC

The comparison is best represented as a map of coordinates, measures, proxies, regimes, instruments, and phases rather than as a single common equation.

- EFC uses entropy, grid, density, and response-kernel variables.
- MOND uses a₀, μ(x), and the radial-acceleration relation.
- ΛCDM uses FLRW background dynamics, halo structure, and collisionless matter.

The formal statements that EFC approaches MOND-like or ΛCDM-like behavior should be retained as formal-limit declarations. They should not be described as equal-footing empirical recovery until the following are matched: same data; same nuisance parameters; same covariance; same priors; same calibration rules; frozen model definitions; out-of-sample holdout; preregistered likelihood and kill criteria.

The reported fσ₈ values are not interchangeable: EFC is reported near 0.430, while ΛCDM references appear near 0.449 and 0.452. This source inconsistency should be resolved before using the comparison as a decisive discriminator.

---

## 8. What is supported

1. The normalized Γ forms are algebraically related.
2. The Γ forms are not thereby established as one physical observable.
3. The executed β normalization omits the documented r_* factor.
4. The resulting x²/u relation is dimensionally unresolved in SI.
5. C ≈ 2.32 is numerically converged within the reported lattice calculation.
6. C is not analytically derived by the evidence currently available.
7. The a₀ values in the repository have mixed provenance.
8. a₀ ~ cH₀ is not an independent EFC prediction.
9. The covariant-to-μ_BE derivation is incomplete and contains a trend mismatch.
10. The formal MOND/ΛCDM limits are declarations, not equal-footing empirical recoveries.

---

## 9. What remains open

The open items are organized as five executable work packages. No additional review round is required (no v3.4); the three loose items from the earlier open list are folded in as sub-points, so this section is now closed under its own model.

**1. Dimensional closure (β, r_*, l_g).** Canonical normalization. Note that r_* = 3l_g/(4π) is an algebraic closure condition, not yet a physical justification.

**2. C derivation and C_ledger provenance.** An analytic derivation of C = 2.32 (the radial AQUAL Green function, not the free-space Watson integral); and reproduction or quarantine of the ledger value C = 2.2895486402403438, which currently has no reproducing configuration on disk.

**3. Canonical a₀ freeze (including unit leaks).** One repository-wide a₀; separation of a₀_base from a₀_eff, cH₀, and Λ-derived scales; and repair or quarantine of the a0_kpc and Λ unit leaks.

**4. Covariant reduction S_grid → relativistic action (including the typed map).** Derive the decreasing μ_BE(g) rather than postulate it; and supply a typed map between Γ, □φ, dS/dρ, the per-mode coefficient, and rates (units, sign, time normalization).

**5. Equal-footing holdout likelihood (including a canonical fσ₈ reference).** Matched EFC–MOND–ΛCDM likelihoods (same data, nuisance, covariance, priors); a frozen canonical fσ₈ reference resolving the 0.430 vs 0.449/0.452 inconsistency; and holdout tests without calibration leakage.

---

## 10. Conclusion

The current evidence supports a constrained reconciliation, not a final unification. Several EFC components are internally coherent as code structures or formal declarations. The stronger physical claims require additional normalization, derivation, and equal-footing empirical work.

The most important distinction is between: an exact algebraic identity; an internally consistent model relation; a declared bridge; a numerically measured lattice quantity; an empirical prediction; and a physically identified common observable. The present record supports the first four in selected places. It does not yet support the last two across the full EFC–MOND–ΛCDM comparison.

**Draft status:** author review required.
**Release status:** not approved.
**DOI status:** not approved.
**Human gate:** remains fail-closed (`REFUSED: human_gate.json missing`).
