# Cosmological Growth Constraints on Λ-Locked Discrete Entropic Gravity

**DOI:** [10.6084/m9.figshare.31348414](https://doi.org/10.6084/m9.figshare.31348414)

## AI-Friendly Package

**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper tests the **cosmological viability** of the discrete entropic gravity operator from [Magnusson 2026](../Discrete_Entropic_Gravity_on_a_Cubic_Graph_Emergent_Newton_and_MOND_Regimes_with_Λ-Locked_Screening/) (DOI: 10.6084/m9.figshare.31348411).

The effective gravitational coupling G_eff(k,a) derived from the discrete operator is embedded into the linear growth equation for matter perturbations. Three transition-scale scenarios are tested:

| Scenario | Transition scale | k_transition | σ₈(z=0) | Viable? |
|----------|-----------------|-------------|---------|---------|
| **A: Λ-locked** | L_Λ ~ 4.4 Gpc | 0.0014 h/Mpc | **0.814** | **Yes** |
| B: 10 Mpc | 10 Mpc | 0.1 h/Mpc | 367 | No |
| C: 1 Mpc | 1 Mpc | 1.0 h/Mpc | 24 098 | No |

**Key Result**: Only Λ-locking preserves realistic structure growth (σ₈ ≈ 0.8). Any sub-Hubble transition scale leads to catastrophic overgrowth (σ₈ >> 1), establishing **Λ-locking as a necessary condition** for cosmological consistency.

## Core Equations

### 1. Deep-MOND Enhancement (from companion paper)
```
g = C √(a₀ g_N)     where C ≈ 2.32
```

### 2. Scale-Dependent Effective Coupling (Lorentzian window)
```
G_eff(k) / G = 1 + (C² − 1) / (1 + (k/k_Λ)²)
```

### 3. Λ-Locked Transition Scale
```
k_Λ = 1/L_Λ,    L_Λ ∝ Λ^{-1/2} ~ 4.4 Gpc
```

### 4. Linear Growth Equation
```
δ'' + (2 + H'/H) δ' − (3/2) Ω_m(a) [G_eff(k)/G] δ = 0
```
where primes denote d/d(ln a).

### 5. Cosmological Viability Condition
```
L_Λ ≳ H₀⁻¹
```
This is not tuned — it follows directly from L_Λ ∝ Λ^{-1/2}, yielding L_Λ ~ 4.4 Gpc ≈ H₀⁻¹.

## Results Table

| Model | σ₈(z=0) | γ (growth index) | σ₈ excess vs ΛCDM |
|-------|---------|-----------------|-------------------|
| ΛCDM | 0.811 | 0.554 | — |
| Graph-AQUAL (Λ-locked) | 0.814 | 0.554 | 0.4% |
| Graph-AQUAL (10 Mpc) | 367 | 0.541 | × 452 |
| Graph-AQUAL (1 Mpc) | 24 098 | 0.536 | × 29 714 |

## Package Contents

```
Cosmological_Growth_Constraints_.../
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute introduction
├── MANIFEST.md                        # File listing with descriptions
├── CITATION.cff                       # Citation metadata
├── index.json                         # Machine-readable metadata
├── CosmologicalGrowthConstraints.jsonld # Schema.org semantic data
├── schema.json                        # JSON Schema for validation
├── citations.bib                      # BibTeX references
├── *.pdf                              # Original paper
│
├── data/
│   ├── parameters.json                # Cosmological and model parameters
│   ├── scenario_results.json          # σ₈ results for all three scenarios
│   └── geff_profiles.json             # G_eff(k)/G profiles per scenario
│
├── src/
│   ├── __init__.py
│   ├── geff_coupling.py               # Scale-dependent G_eff(k) model
│   ├── growth_equation.py             # Linear growth ODE solver
│   └── scenario_runner.py             # Run and compare all scenarios
│
└── examples/
    ├── run_scenarios.py               # Reproduce the σ₈ results table
    └── geff_profile.py                # Plot G_eff(k)/G for each scenario
```

## Quick Usage

```python
from src.geff_coupling import geff_ratio, lambda_locked_scale
from src.growth_equation import sigma8_excess

# Λ-locked transition scale
L_lambda = lambda_locked_scale()  # ~4.4 Gpc
k_lambda = 1.0 / L_lambda

# G_eff/G at various k
for k in [0.001, 0.01, 0.1, 1.0]:  # h/Mpc
    ratio = geff_ratio(k, k_lambda, C=2.32)
    print(f"  k = {k:.3f} h/Mpc: G_eff/G = {ratio:.4f}")
# k << k_Λ: full enhancement (C² ≈ 5.38)
# k >> k_Λ: screened (G_eff/G → 1)
```

## Physical Interpretation

- **Λ-locking is not tuned** — it is a structural consequence of setting the transition scale proportional to Λ^{-1/2}, which naturally yields L_Λ ~ H₀⁻¹.
- The growth index γ is **unchanged** across all scenarios because γ characterises f(Ω_m), which depends on background expansion, not on the amplitude of G_eff.
- The constraint L_Λ ≳ H₀⁻¹ applies **generically** to any modified gravity model with infrared enhancement, not just the graph-AQUAL operator.

## Limitations (explicitly stated in paper)

- Linear growth only; no nonlinear corrections or N-body verification
- No CMB angular power spectrum computed
- No full Boltzmann integration (CLASS/CAMB)
- G_eff(k) is a Lorentzian approximation to the full discrete operator
- Poisson-channel modification (μ(a) < 1) not activated

## Falsification Criteria

1. If Λ-locking produces σ₈ inconsistent with observed σ₈ = 0.811 ± 0.006 → **falsified** (currently passes: 0.814)
2. If sub-Hubble transitions could be made safe by any mechanism → weakens the necessity claim
3. Full Boltzmann integration must confirm the linear-growth result

## Epistemic Status

**Layer B**: Stress test establishing a necessary condition (Λ-locking) for cosmological consistency. Linear analysis only.

## Related EFC Papers

- [Discrete Entropic Gravity on Cubic Graph](../Discrete_Entropic_Gravity_on_a_Cubic_Graph_Emergent_Newton_and_MOND_Regimes_with_Λ-Locked_Screening/) — Companion paper defining the operator (DOI: 10.6084/m9.figshare.31348411)
- [H₀-RAR Unification](../Unified_Origin_of_the_Radial_Acceleration_Relation_and_the_Hubble_Tension_via_Entropic_Gravity_Modification/) — Entropic gravity modification (DOI: 10.6084/m9.figshare.31223908)

## Citation

```bibtex
@article{magnusson2026cosmogrowth,
  author  = {Magnusson, Morten},
  title   = {Cosmological Growth Constraints on {$\Lambda$}-Locked
             Discrete Entropic Gravity},
  year    = {2026},
  note    = {EFC Cosmological Growth Constraints v1.0}
}
```
