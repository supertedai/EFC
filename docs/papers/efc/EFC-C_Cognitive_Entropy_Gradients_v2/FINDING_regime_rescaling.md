# Critical Finding: C_eff/C ≈ k (Regime Rescaling)

**Date:** April 5, 2026
**Status:** Empirical observation requiring independent validation

## The Observation

From the multi-scale HCP analysis (6 parcellation scales, ENIGMA data):

```
C_eff / C_cosmo = 0.437 ± 0.088
k (screening exponent) = 0.415 ± 0.029
Difference: 0.3σ
```

**These match within 1σ.**

## What This Implies

If C_eff = k × C, then:

```
C_eff = k × (k/a_G) = k²/a_G = 0.415²/0.094 = 1.83
```

Observed: C_eff = 1.93 ± 0.39. Predicted: 1.83. Match: 0.3σ.

## Physical Interpretation (if real)

In cosmology (Low-S, R₀):
- Driver: g_bar (baryonic acceleration)
- Screening: μ = (1 + g†/g_bar)^k
- Phase-gain: C = k/a_G

In cortex (High-S, R₂):
- Driver: degree_ratio (local connectivity contrast)
- Screening: κ = C_eff / D_ratio^γ
- Phase-gain: C_eff = k × C = k²/a_G

**Interpretation:** The screening exponent k acts as a regime
transformation factor. The cosmological screening "applies twice"
when crossing from R₀ to R₂ — once for the cosmological-to-structure
transition, and once for the structure-to-cortex transition.

This is consistent with the L0-L3 regime architecture:
- L1 → L2 transition modifies C by factor k
- Each regime boundary applies one screening factor

## The Power-Law Exponent

```
γ = 0.598 ± 0.228
```

Consistent with γ = 1/2 (0.4σ), γ = k (0.8σ), and γ = ln(2) (0.4σ).
Not enough data to distinguish.

If γ = 1/2: κ = C_eff / √D_ratio (square-root screening)
If γ = k:   κ = C_eff / D_ratio^k (self-similar screening)

## Revised Bridge B1**

```
κ = (k²/a_G) / D_ratio^γ
```

where:
- k = 0.415 (from SPARC)
- a_G = 0.094 (from H₀)
- D_ratio = degree_hub / degree_periph (from connectome)
- γ ≈ 0.5-0.6 (from HCP fit)

**Zero free parameters from neural data** (if γ is derived).
**One free parameter** (γ) in current form.

## Caveats

1. **n = 6 data points.** This is suggestive, not conclusive.
2. **Group-average data.** Individual subjects may show different pattern.
3. **FC-CV proxy** ≠ MSE on BOLD. The entropy proxy is approximate.
4. **C_eff/C ≈ k could be numerical coincidence.** With only one ratio,
   many simple expressions match within 1σ (e.g., 1/e is at 0.8σ).
5. **γ is poorly constrained** (±0.23, 38% relative uncertainty).

## Falsification

This observation is falsified if:
1. Individual-subject HCP data gives C_eff/C outside [0.3, 0.6] (2σ from k)
2. γ is inconsistent with {1/2, k, ln(2)} at > 3σ with more data points
3. The relation breaks on independent datasets (OpenNeuro, Lausanne)

## What Makes This Non-Trivial

The rescaling factor k was NOT fit to neural data. It comes from
galaxy rotation curves (SPARC). Finding it again in the ratio
between cosmological and cortical phase-gain is either:

(a) A genuine regime transformation in a shared dynamical class, or
(b) A numerical coincidence at the 0.3σ level

Only more data can distinguish (a) from (b).

## References

- k, a_G, C: Magnusson (2026), Spor 1 (DOI: 10.6084/m9.figshare.31301953)
- HCP connectomes: ENIGMA Toolbox, MICA-MNI
- Regime theory: RCMP, EBE, L0-L3 (this repository)
