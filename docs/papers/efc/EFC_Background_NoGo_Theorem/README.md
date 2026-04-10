# EFC Background No-Go Theorem: Why Background-Level Modification Cannot Suppress Structure Growth

## AI-Friendly Package

- **DOI:** [10.6084/m9.figshare.31333414](https://doi.org/10.6084/m9.figshare.31333414) (EFCLASS Sign Structure)
- **Version:** 1.0
- **Author:** Morten Magnusson (ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095))
- **Affiliation:** Symbiose Research, Sandnes, Norway
- **Date:** 2026-04-10
- **License:** CC-BY-4.0

---

## Overview

This package consolidates the **background sector no-go theorem** for Energy-Flow Cosmology (EFC). It collects three independent lines of evidence — an analytical sign lemma, numerical CLASS verification, and multi-probe observational constraints — demonstrating that the EFC background coupling channel (β · T(a) modification to the Friedmann equation) **cannot suppress σ₈** and is **observationally empty** under joint CMB + BAO constraints.

This is not a failure of EFC — it is a **structural boundary** that precisely defines the domain of validity. The background gate collapses to α ≈ 0 under observational constraints, redirecting all late-time EFC effects to the **perturbation sector** (μ, Σ, η modifications). This no-go theorem is a central architectural result: it explains *why* EFC must enter through the growth equation and lensing potential, not through the expansion history.

### Three Pillars of the No-Go

| Pillar | Method | Key Result | Reference |
|--------|--------|------------|-----------|
| **Analytical** | Sign lemma on ΔE²(z) | ΔE² ≤ 0 for all z > 0 → growth *enhanced*, not suppressed | [31333414](https://doi.org/10.6084/m9.figshare.31333414) |
| **Numerical** | CLASS v3.3.4 verification | ΔH/H = −0.3% to −1.1% (negative everywhere) | [31333414](https://doi.org/10.6084/m9.figshare.31333414) |
| **Observational** | CMB + BAO joint fit | α → 0 under all Planck + BAO combinations; α–H₀ degeneracy (r = 0.975) | [31368433](https://doi.org/10.6084/m9.figshare.31368433) |

---

## Key Results

### 1. Sign Lemma (Analytical Proof)

**Lemma 1 (Sign of ΔE²):** Under closure normalisation E(0) = 1 with amplitude A > 0 and monotonically activating gate function g(z):

> ΔE²(z) = A · [g(z) − g(0)] ≤ 0 for all z > 0

**Corollary:** H_EFC(z) ≤ H_ΛCDM(z) at all redshifts, reducing Hubble friction and *enhancing* structure growth. Any additive background gate modification structurally excludes σ₈ suppression.

### 2. Numerical Verification (CLASS v3.3.4)

Parameters: A = 0.15, z_t = 1.01, n = 6, h = 0.674, ω_b = 0.02237, ω_cdm = 0.1200

| z | ΔH/H [%] | fσ₈(ΛCDM) | fσ₈(EFC) | Change | Sign OK |
|---|----------|-----------|----------|--------|---------|
| 0.3 | −0.291 | — | — | — | Yes |
| 0.38 | — | 0.4749 | 0.4773 | +0.50% | Yes |
| 0.5 | −0.569 | — | — | — | Yes |
| 0.51 | — | 0.4731 | 0.4762 | +0.65% | Yes |
| 0.61 | — | 0.4679 | 0.4715 | +0.76% | Yes |
| 1.0 | −1.124 | — | — | — | Yes |
| 2.0 | −0.739 | — | — | — | Yes |
| 5.0 | −0.107 | — | — | — | Yes |

Growth is **enhanced** at all redshifts — opposite to the S₈ tension direction.

### 3. Observational Confirmation: Background Gate Empty

| Test | Dataset | Result | Status |
|------|---------|--------|--------|
| α collapse | Planck 2018 TT/TE/EE + BOSS/eBOSS BAO | α → 0 (\|Δχ²\| < 2σ in all combinations) | CONFIRMED |
| α–H₀ degeneracy | Same | correlation = 0.975 | CONFIRMED |
| Four-channel β test | BOSS DR12 BAO + RSD + CMB lensing + Pantheon+ | β = 0.08, Δχ² = −3.89 (2σ) but background only | CONSISTENT |
| Perturbation-level test | μ < 1 via MGCAMB | μ ≈ 0.94, Σ ≈ 1.05 → Δχ² = −0.45 | PASS |

**Conclusion:** The background sector is not merely disfavoured — it is structurally excluded for σ₈ suppression and observationally empty under CMB + BAO. All EFC effects must enter through the perturbation sector.

---

## Core Equations

### Modified Friedmann Equation

```
H²(a) = H₀² [Ω_m a⁻³ + Ω_Λ (1 + β · T(a))]
```

### Gate Function

```
g(z) = 1 / (1 + (a_t/a)^n)
```

### Closure Normalisation

```
Ω'_Λ = Ω_Λ − A · g(0)     (enforces E(0) = 1)
```

### Sign Lemma

```
ΔE²(z) = A · [g(z) − g(0)] ≤ 0    for all z > 0
```

Since g(z) is monotonically decreasing (gate activates at late times), g(z) ≤ g(0), so ΔE² ≤ 0.

### Perturbation-Sector Alternative

```
μ_EFC(k,z) = 1/(1 + R(k))    where R(k) = K₀ · Θ(ρ) · (Γ'φ̇)² · a⁴ / (M_Pl² · F · k⁴)
```

This is where EFC effects actually operate — through the Poisson equation modifier μ < 1 and lensing potential Σ > 1.

---

## Architectural Significance

```
┌────────────────────────────────────┐
│     EFC Modification Channels      │
├──────────────┬─────────────────────┤
│  Background  │    Perturbation     │
│  H²(a) mod   │   μ(k,z), Σ(k,z)   │
│              │                     │
│  ΔE² ≤ 0    │   μ ≈ 0.94          │
│  (enhances   │   Σ ≈ 1.05          │
│   growth)    │   η ≈ 1.10          │
│              │                     │
│  ❌ EXCLUDED │   ✅ ACTIVE          │
│  for σ₈     │   σ₈ suppression    │
│  suppression │   + lensing boost   │
└──────────────┴─────────────────────┘
```

This no-go theorem is **constructive**: it forces EFC into the perturbation sector, which makes sharper predictions (μ < 1, Σ > 1, η ≈ 1.10) that are independently testable by Euclid, DESI, and Rubin.

---

## Quick Start

```python
from src.background_nogo import BackgroundNoGo

# Verify the sign lemma numerically
nogo = BackgroundNoGo(A=0.15, z_t=1.01, n=6)
results = nogo.verify_sign_lemma()
for z, delta_E2 in results.items():
    print(f"z={z}: ΔE² = {delta_E2:.6f} {'✓' if delta_E2 <= 0 else '✗'}")

# Check growth enhancement
growth = nogo.compute_growth_enhancement()
for z, pct in growth.items():
    print(f"z={z}: Δfσ₈ = +{pct:.2f}% (enhanced, not suppressed)")
```

---

## Package Contents

```
EFC_Background_NoGo_Theorem/
├── README.md                           # This file
├── metadata.json                       # Package metadata
├── index.json                          # Full semantic index
├── schema.json                         # JSON Schema validation
├── CITATION.cff                        # Citation metadata
├── efc-background-nogo-theorem.jsonld  # Schema.org JSON-LD
├── citations.bib                       # BibTeX references
├── src/
│   ├── __init__.py                     # Package exports
│   └── background_nogo.py             # Sign lemma + growth computation
├── data/
│   ├── sign_lemma_verification.json   # CLASS numerical results
│   └── observational_constraints.json # CMB+BAO constraint summary
└── examples/
    └── verify_nogo.py                  # Reproduce all results
```

---

## Epistemic Status

**Layer B (numerical verification) → structural boundary.**

This is not a hypothesis awaiting confirmation — it is an analytical theorem (Lemma 1) with numerical verification and observational confirmation. The background no-go is a **closed result**: the sign structure of the Friedmann equation under closure normalisation is mathematically fixed. The only escape would be negative A (anti-coupling), which is excluded by the physical interpretation of β as an entropy-gradient amplitude.

---

## Falsification Criteria

This no-go theorem would be invalidated if:

| Condition | Would Imply |
|-----------|-------------|
| A mechanism is found where ΔE² > 0 with E(0) = 1 | Sign lemma violated; requires non-monotonic gate |
| Background-only modification produces σ₈ suppression | Analytical proof contains an error |
| α ≠ 0 detected at > 3σ in CMB + BAO joint fit | Background gate not empty; observational pillar fails |

None of these are currently viable.

---

## Related Packages

- **EFCLASS Sign Structure:** [31333414](https://doi.org/10.6084/m9.figshare.31333414) — Source of analytical proof
- **CMB Systematic Localization:** [31368433](https://doi.org/10.6084/m9.figshare.31368433) — Source of observational α-collapse
- **Four-Channel Consistency Test:** [31304980](https://doi.org/10.6084/m9.figshare.31304980) — β = 0.08 four-probe test
- **Perturbation-Level σ₈ Suppression:** [31333600](https://doi.org/10.6084/m9.figshare.31333600) — The perturbation alternative
- **Kill-Test v6:** [31964847](https://doi.org/10.6084/m9.figshare.31964847) — Full six-probe validation
- **Validation Ledger:** [EFC_Validation_Ledger.html](../../public/EFC_Validation_Ledger.html)
- **White Paper Series:** [EFC_White_Paper_Series.html](../../public/EFC_White_Paper_Series.html)

---

## Citation

```bibtex
@misc{magnusson2026nogo,
  author    = {Magnusson, Morten},
  title     = {{EFC Background No-Go Theorem: Why Background-Level Modification
                Cannot Suppress Structure Growth}},
  year      = {2026},
  doi       = {10.6084/m9.figshare.31333414},
  note      = {Consolidation package; primary results from EFCLASS Sign Structure
               and CMB Systematic Localization papers}
}
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
