# Discrete Entropic Gravity on a Cubic Graph: Emergent Newtonian and MOND Regimes with Λ-Locked Screening

## AI-Friendly Package

**DOI**: [10.6084/m9.figshare.31348411](https://doi.org/10.6084/m9.figshare.31348411)
**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 16, 2026
**License**: CC-BY-4.0

## Overview

This paper constructs a **discrete gravity operator** defined purely on a cubic graph with entropic flux weighting between nodes. No continuum metric or General Relativity equations are assumed — the theory is defined entirely on graph topology.

The operator reproduces five key behaviours:

1. **Newtonian 1/r² scaling** in the strong-field (high-acceleration) regime
2. **MOND-like 1/r scaling** in the low-acceleration regime
3. **Λ-locked transition scale** set by a bulk entropic reservoir proportional to Λ
4. **Broken superposition** (13.7% nonlinear violation for two equal masses)
5. **External field effect (EFE)** — partial, consistent with nonlinear operator

Two quantitative departures from standard MOND are identified:

- A convergent **prefactor C ≈ 2.32**, implying an effective acceleration scale a₀,eff = C²a₀ ≈ 5.4 a₀
- A **weak mass-scaling exponent** r_trans ∝ M^0.18 (vs MOND expectation of M^0.5), reflecting Λ-dominance over local mass

## Core Equations

### 1. Discrete Gradient Magnitude
```
|∇Φ|_ij = |Φ_i − Φ_j| / a
```
where `a` is the lattice spacing on an N³ cubic graph.

### 2. AQUAL Weights (Interpolating Function)
```
w_ij = μ(|Φ_i − Φ_j| / (a₀ · a))
μ(x) = x / √(1 + x²)
```

### 3. Discrete Field Equation (Graph AQUAL)
```
Σ_{j~i} w_ij (Φ_j − Φ_i) = 4πGρ_i
```

### 4. Bulk Entropic Reservoir (Λ-Locking)
```
F_bulk = ½ μ_Λ (S_i − S_V)²
μ_Λ ∝ Λ
```

### 5. Screening Length and Acceleration Scale
```
L_Λ ∝ Λ^{-1/2}
a₀ = c² / L_Λ ∝ c² √Λ
```

### 6. Deep-MOND Prefactor
```
g_graph = C √(a₀ g_N)    where C → 2.32 as N → ∞
a₀,eff = C² a₀ ≈ 5.4 a₀
```

### 7. Linear Growth ODE (Cosmological Stability)
```
δ̈ + 2H(a)δ̇ − (3/2)Ω_m H₀² (1+z)³ δ = 0
```

## Kill Test Results

| Kill Test | Description | Result | Details |
|-----------|-------------|--------|---------|
| KT1 | Newton & MOND recovery | **PASS** | Newton slope: −2.00, MOND slopes: −0.99, −1.01 |
| KT2 | Prefactor convergence | **PASS** | C → 2.32 (independent of binning geometry) |
| KT3 | Mass scaling | **STRUCTURAL DEPARTURE** | r_trans ∝ M^0.18 (MOND expects M^0.5) |
| KT4 | Broken superposition | **PASS** | δΦ/Φ_max = 13.7% (smooth, not noise) |
| KT5 | External field effect | **PASS** | Monotonic decrease with external field strength |

### Prefactor Convergence Table

| N | C_cubic | C_sphere |
|---|---------|----------|
| 21 | 2.443 | 2.433 |
| 31 | 2.354 | 2.349 |
| 41 | 2.320 | 2.321 |

### Cosmological Stability Check

| Model | σ₈ | fσ₈(z=0.51) | ε₀ |
|-------|-----|-------------|-----|
| ΛCDM | 0.811 | 0.473 | — |
| This work (background) | 0.805 | 0.463 | 0.8% |

## Package Contents

```
Discrete_Entropic_Gravity_.../
├── README.md                          # This file
├── QUICKSTART.md                      # 5-minute introduction
├── MANIFEST.md                        # File listing with descriptions
├── CITATION.cff                       # Citation metadata
├── index.json                         # Machine-readable metadata
├── DiscreteEntropicGravity.jsonld      # Schema.org semantic data
├── schema.json                        # JSON Schema for validation
├── citations.bib                      # BibTeX references
├── *.pdf                              # Original paper
│
├── data/
│   ├── parameters.json                # Physical and lattice parameters
│   ├── kill_test_results.json         # All five kill-test outcomes
│   └── convergence_table.json         # Prefactor C vs grid size N
│
├── src/
│   ├── __init__.py
│   ├── cubic_graph.py                 # Cubic lattice graph construction
│   ├── aqual_operator.py              # Discrete AQUAL weights and field eq
│   ├── lambda_screening.py            # Bulk entropic term and Λ-locking
│   ├── kill_tests.py                  # Kill-test evaluation suite
│   └── growth_check.py                # Cosmological stability ODE
│
└── examples/
    ├── run_kill_tests.py              # Reproduce all five kill tests
    └── prefactor_convergence.py       # Plot C vs N convergence
```

## Quick Usage

```python
from src.aqual_operator import mu_interpolation, aqual_weight
from src.lambda_screening import screening_length, acceleration_scale

# AQUAL interpolating function
x = 5.0
mu_val = mu_interpolation(x)  # x / sqrt(1 + x^2) = 0.981

# Λ-locked screening length
import math
Lambda = 1.1e-52  # m^-2 (Planck 2018)
L_lambda = 1.0 / math.sqrt(Lambda)
a0 = (3e8)**2 * math.sqrt(Lambda)

# Prefactor correction
C = 2.32
a0_eff = C**2 * a0
print(f"a₀,eff / a₀ = {C**2:.2f}")  # 5.38
```

## Physical Interpretation

- **C ≠ 1** means the graph operator does not reproduce standard MOND. It produces a *discrete renormalization* of the infrared response intrinsic to the cubic topology.
- **Weak mass scaling** (exponent 0.18 vs 0.50) means the Λ-locked bulk entropic scale dominates over local mass in setting the Newton–MOND transition radius.
- Both deviations are *structural consequences* of graph topology + Λ-locking. Whether they improve or worsen agreement with observations remains to be tested.

## Falsification Criteria

1. The operator must recover g ∝ r⁻² (Newton) and g ∝ r⁻¹ (deep MOND) — **confirmed**
2. The prefactor C must converge under resolution refinement — **confirmed (C → 2.32)**
3. Any comparison with observed rotation curves must use a₀,eff = C²a₀, not a₀
4. The mass-scaling exponent (0.18) is a testable prediction against galaxy-scale data

## Epistemic Status

**Layer B**: Technical construction with controlled numerical tests. Does not claim equivalence to MOND or any cosmological model. Reports what the graph-based operator produces under controlled conditions.

## Related EFC Papers

- [Core Lock](../Core-Lock/) — Mathematical foundation (DOI: 10.6084/m9.figshare.31223503)
- [EBE Core Principles](../EBE-Core-Principles/) — Methodological framework (DOI: 10.6084/m9.figshare.31222903)
- [H₀-RAR Unification](../Unified_Origin_of_the_Radial_Acceleration_Relation_and_the_Hubble_Tension_via_Entropic_Gravity_Modification/) — Entropic gravity modification (DOI: 10.6084/m9.figshare.31223908)
- [SPARC 175](../Comprehensive-analysis-of-175-SPARC-galaxies-demonstrating-regime-dependent-validity-in-rotation-curve-modeling/) — Galaxy rotation curve analysis

## Citation

```bibtex
@article{magnusson2026discreteentropicgravity,
  author  = {Magnusson, Morten},
  title   = {Discrete Entropic Gravity on a Cubic Graph: Emergent Newtonian
             and MOND Regimes with {$\Lambda$}-Locked Screening},
  year    = {2026},
  doi     = {10.6084/m9.figshare.31348411},
  note    = {EFC Discrete Graph Gravity Technical Note v1.0}
}
```
