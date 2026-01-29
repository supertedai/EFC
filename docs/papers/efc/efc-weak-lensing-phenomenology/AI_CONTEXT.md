# AI_CONTEXT.md — Machine-Readable Context for AI Systems

> This file provides structured context for AI assistants, coding agents, and automated systems working with this repository.

---

## Repository Purpose

```yaml
type: scientific-phenomenology-paper
domain: cosmology
subfield: weak-gravitational-lensing
theory: Energy-Flow-Cosmology
status: published
doi: 10.6084/m9.figshare.31188193
```

---

## Core Scientific Claim

```yaml
claim_type: phenomenology
claim_strength: conditional
claim_text: >
  EFC with Postulat A predicts μ(k,z) ≠ 1, which can be tested against DES Y6.
  This is NOT a claim that EFC explains S8 tension.
  This IS a falsifiable test protocol.
```

---

## Key Equations

### 1. EFC Action (Background)

```latex
S = ∫d⁴x √(-g) [ R/(16πG) - (κ_S/2)(∇S)² - V(S) - (κ_J/2)J_μJ^μ + γ∇_μS J^μ + λ(∇_μJ^μ - Σ) ]
```

### 2. Postulat A (Operational Assumption)

```latex
δΣ(k,z) = ξ ρ_m(z) δ_m(k,z) g(z) h(k)
```

**Status**: ASSUMPTION, not derivation

### 3. Modified Gravity Parameter (Main Result)

```latex
μ(k,z) = 1 + A_μ × Θ(z_t - z) × 1/(1 + k²/k_*²)
```

**Parameters**:
- `A_μ`: Free amplitude [-0.5, +0.5], constrained by data
- `z_t = 2`: Fixed, preserves CMB
- `k_* = 0.1 h/Mpc`: Fixed, DES-relevant scales

### 4. Lensing Parameter

```latex
Σ_lens(k,z) = μ(k,z)/2 × (1 + η) ≈ μ(k,z)
```

**Note**: η ≈ 1 (minimal slip assumption)

---

## Code Interface

### Primary Functions

```python
# Main API
from src.efc_weak_lensing import (
    EFCParams,           # Dataclass for parameters
    mu_efc,              # μ(k, z, params) -> float or array
    sigma_lens_efc,      # Σ_lens(k, z, params) -> float or array
    eta_efc,             # η(k, z, params) -> 1.0 (minimal model)
)

# CosmoSIS interface
from src.efc_weak_lensing import setup_cosmosis, execute_cosmosis

# Cobaya interface
from src.efc_weak_lensing import EFCLensing  # Theory class
```

### Parameter Ranges

```python
PARAM_RANGES = {
    'A_mu': {'min': -0.5, 'max': 0.5, 'fiducial': 0.0, 'unit': 'dimensionless'},
    'z_t': {'min': 1.0, 'max': 5.0, 'fiducial': 2.0, 'unit': 'redshift'},
    'k_star': {'min': 0.01, 'max': 1.0, 'fiducial': 0.1, 'unit': 'h/Mpc'},
}
```

---

## Validation Protocol

### Target Dataset

```yaml
dataset: DES-Y6-3x2pt
observables:
  - cosmic_shear
  - galaxy_clustering  
  - galaxy_galaxy_lensing
reference_s8: 0.789 ± 0.012
planck_s8: ~0.83
tension: 2.6σ
```

### Pass/Fail Criteria

```yaml
pass_conditions:
  - delta_chi2 >= 6
  - A_mu_significance > 2σ
  - AIC_BIC_prefers: EFC
  
fail_conditions:
  - delta_chi2 < 2
  - A_mu_consistent_with_zero: true
  - A_mu_sign: positive  # Wrong sign
  - CMB_lensing_conflict: true
```

---

## Limitations (CRITICAL)

```yaml
limitations:
  - id: L1
    description: "Postulat A is NOT derived from the action"
    severity: fundamental
    mitigation: "Future work: derive Σ(ρ_m) from first principles"
    
  - id: L2
    description: "No data fit performed"
    severity: scope
    mitigation: "This paper = predictions + protocol, not results"
    
  - id: L3
    description: "No unique EFC signature vs generic MG"
    severity: theoretical
    mitigation: "Need additional observables or predictions"
    
  - id: L4
    description: "Minimal slip (η ≈ 1)"
    severity: model
    mitigation: "Richer model could have η ≠ 1"
    
  - id: L5
    description: "Fixed z_t and k_*"
    severity: parametric
    mitigation: "Avoid over-parametrization; can be relaxed later"
```

---

## File Structure

```
efc-weak-lensing-phenomenology/
├── README.md                 # Human-readable overview
├── AI_CONTEXT.md            # THIS FILE - machine context
├── LICENSE                   # CC BY 4.0
├── requirements.txt          # Python dependencies
├── docs/
│   ├── efc_weak_lensing_paper.pdf    # Published paper
│   ├── efc_weak_lensing_paper.tex    # LaTeX source
│   └── DERIVATION.md                  # Step-by-step derivation
├── src/
│   ├── __init__.py
│   └── efc_weak_lensing.py           # Main implementation
├── tests/
│   ├── test_mu.py                     # Unit tests for μ(k,z)
│   └── test_limits.py                 # GR limit tests
└── data/
    └── expected_outputs.json          # Reference values
```

---

## Dependencies

```yaml
required:
  - numpy >= 1.20
  - scipy >= 1.7

optional:
  - cosmosis  # For CosmoSIS integration
  - cobaya    # For Cobaya integration
  - camb      # For power spectrum computation
  - matplotlib  # For plotting
```

---

## Semantic Tags

```yaml
tags:
  - cosmology
  - weak-lensing
  - modified-gravity
  - Energy-Flow-Cosmology
  - DES-Y6
  - S8-tension
  - phenomenology
  - falsification
  - open-science

related_concepts:
  - gravitational_slip
  - Poisson_equation
  - linear_perturbation_theory
  - quasi_static_approximation
  - cosmic_shear
  
mathematical_objects:
  - mu_k_z: "modified gravity parameter"
  - Sigma_lens: "lensing parameter"
  - eta: "gravitational slip"
  - delta_S: "entropy perturbation"
  - delta_m: "matter density contrast"
```

---

## Version History

```yaml
versions:
  - version: 1.0.0
    date: 2026-01-29
    doi: 10.6084/m9.figshare.31188193
    changes: "Initial release"
```

---

## Contact

```yaml
author:
  name: Morten Magnusson
  orcid: 0009-0002-4860-5095
  affiliation: Independent Researcher
  location: Norway
  website: https://energyflow-cosmology.com
```

---

## AI Usage Guidelines

```yaml
when_using_this_repo:
  do:
    - Cite the DOI when referencing results
    - Respect the limitations listed above
    - Use μ(k,z) formula exactly as specified
    - Note that Postulat A is an assumption
    
  do_not:
    - Claim EFC "explains" or "solves" S8 tension
    - Treat Postulat A as a derived result
    - Extrapolate beyond linear regime
    - Ignore the falsification criteria
```
