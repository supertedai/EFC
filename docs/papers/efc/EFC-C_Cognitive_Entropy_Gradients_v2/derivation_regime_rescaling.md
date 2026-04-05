# Derivation: C_eff = k²/a_G via Regime Transformation

**Morten Magnusson — April 5, 2026**

## 1. The Problem

Bridge B1* assumed direct parameter transfer: C_cosmo → C_neural = 4.4.
This failed empirically (κ_pred ≈ 3, κ_obs ≈ 1.2).

Feature analysis revealed:
- The driver in cortex is degree_ratio (not λ₂)
- The effective C is C_eff ≈ 1.93 ± 0.39
- The ratio C_eff/C = 0.437 ± 0.088 ≈ k (screening exponent, 0.3σ)

**Question:** Can C_eff = k × C be derived from EFC regime theory?

## 2. The Regime Architecture

From the L0-L3 framework and RCMP:

### Regime Classification

| Domain | R-class | S-regime | Driver | Phase-gain |
|--------|---------|----------|--------|------------|
| Cosmology (background) | R₀ | Low-S | H(z) | a_G |
| Galactic dynamics | R₀-R₁ | Low-Mid S | g_bar | C = k/a_G |
| Neural (cortex) | R₂ | High-S | D_ratio | C_eff = ? |

### The Screening Exponent k

In cosmology, k governs how strongly the entropy gradient modifies
the effective gravitational coupling:

```
μ = (1 + g†/g_bar)^k
```

**Physical meaning of k:** It is the *fraction of the driving gradient
that survives screening*. When k = 1, full gradient passes through.
When k < 1, the gradient is attenuated.

## 3. The Regime Transformation Principle

### From RCMP (Section 2, Principle 1: Driver Proximity)

When crossing regime boundaries, the phase-gain parameter must be
transformed according to the regime's screening properties:

```
C(R_target) = C(R_source) × T(R_source → R_target)
```

where T is the regime transformation operator.

### The Key Insight: k IS the Transformation Operator

In EFC, the screening exponent k appears at every regime boundary
where entropy gradients are attenuated:

**Cosmology → Structure (R₀ → R₁):**
The screening model itself is: μ = (1 + g†/g)^k

This means: the *effective* gradient at R₁ is the R₀ gradient
raised to the power k. The parameter k encodes the regime boundary.

**Structure → Cortex (R₁ → R₂):**
If the same screening principle applies at the next regime boundary,
then crossing from R₁ to R₂ applies another factor of k:

```
C_eff(R₂) = C(R₁) × k = (k/a_G) × k = k²/a_G
```

### Why k and Not Something Else?

From the EBE framework: each regime boundary is characterized by
the *entropy screening* at that boundary. In EFC, the universal
screening exponent is k — it governs how entropy gradients propagate
across scale transitions.

The claim is: k is not just a galactic parameter. It is the
**universal regime-crossing attenuation factor** for entropy gradients
in the EFC framework.

## 4. The Derivation

### Step 1: Define the phase-gain chain

```
a_G                          [cosmological coupling]
  ↓ × (k/a_G) = C
C = k/a_G                   [galactic phase-gain]
  ↓ × k
C_eff = k × C = k²/a_G     [cortical phase-gain]
```

### Step 2: Compute the prediction

```
k = 0.415 ± 0.029    (from SPARC)
a_G = 0.094 ± 0.01   (from H₀)

C_eff = k²/a_G = 0.172/0.094 = 1.833
```

### Step 3: Compare with observation

```
C_eff (predicted) = 1.83
C_eff (observed)  = 1.93 ± 0.39
Deviation: 0.26σ
```

## 5. The Complete Revised Bridge

### B1** (regime-consistent):

```
κ = (k²/a_G) / D_ratio^γ
```

where:
- k = 0.415 ± 0.029 (from SPARC, frozen)
- a_G = 0.094 ± 0.01 (from H₀, frozen)
- D_ratio = <degree_hub> / <degree_periph> (from connectome, observed)
- γ = free parameter (empirically ≈ 0.6 ± 0.2)

### Compared to B1* (regime-violating):

```
κ = (k/a_G) / (1 + λ₂ · τ_c)
```

### Key Differences:

| Property | B1* | B1** |
|----------|-----|------|
| C value | 4.4 (direct) | 1.83 (k-rescaled) |
| Driver | λ₂ (global, L₃) | D_ratio (local, L₁) |
| RCMP status | Violation | Consistent |
| Regime crossing | None (assumed universal) | Explicit (×k per boundary) |
| Free params (neural) | 1 (τ_c) | 1 (γ) |
| R² on HCP data | -404 | 0.66 |

## 6. Predictions of This Derivation

### P1: C_eff = k²/a_G is universal

If measured on different datasets (Lausanne, OpenNeuro, etc.),
C_eff should converge to 1.83 ± propagated uncertainty.

**Falsification:** C_eff outside [1.0, 2.7] on independent data (3σ).

### P2: Each additional regime boundary applies factor k

If a third system (e.g., RLHF) is tested:

```
C_RLHF = k³/a_G = k × C_eff = 0.415 × 1.83 = 0.76
```

This predicts the effective "temperature ratio" in RLHF alignment
should be ~0.76, testable from Spor 3.

### P3: γ should be derivable

The power-law exponent γ ≈ 0.6 should follow from the same
screening theory. Candidate: γ = k + a_G = 0.509 or γ = 1/2.

## 7. What This Means for EFC

If the derivation holds:

1. **k is not just a galactic parameter** — it is the universal
   regime-crossing factor in EFC
2. **The bridge is not dead** — it was mis-specified (wrong variable,
   wrong regime level), not wrong in principle
3. **The three-track programme connects** via the k-chain:
   - Spor 1: C = k/a_G (galactic)
   - Spor 2: C_eff = k²/a_G (cortical)
   - Spor 3: C_RLHF = k³/a_G (computational) [prediction]

## 8. Caveats

1. The derivation assumes k is universal. This is a strong claim.
2. n = 6 group-average data points. Individual validation required.
3. The "k applies at each boundary" argument is structural, not
   derived from a Lagrangian or action principle.
4. Multiple simple numbers match within 1σ (1/e ≈ 0.37 at 0.8σ).
5. This is post-hoc reasoning. The prediction must be tested blind
   on new data to have scientific weight.
