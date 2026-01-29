# EFC Weak Lensing Phenomenology

[![DOI](https://img.shields.io/badge/DOI-10.6084%2Fm9.figshare.31188193-blue)](https://doi.org/10.6084/m9.figshare.31188193)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**A Testable μ(k,z) Framework and DES Y6 Validation Protocol**

---

## Quick Summary

This repository provides the theoretical infrastructure for testing **Energy-Flow Cosmology (EFC)** against weak gravitational lensing observations from the **Dark Energy Survey Year 6 (DES Y6)**.

### Key Result

```
μ(k,z) = 1 + A_μ × Θ(z_t - z) × 1/(1 + k²/k_*²)
```

Where:
- `A_μ` = free amplitude (constrained by data)
- `z_t = 2` = redshift transition (preserves CMB)
- `k_* = 0.1 h/Mpc` = scale filter

---

## What This Repository Contains

| Directory | Contents |
|-----------|----------|
| `docs/` | Paper (PDF + LaTeX), theory derivation |
| `src/` | Python implementation for CosmoSIS/Cobaya |
| `tests/` | Unit tests and validation |
| `data/` | Reference data and expected outputs |
| `AI_CONTEXT.md` | Machine-readable context for AI systems |

---

## Installation

```bash
git clone https://github.com/supertedai/efc-weak-lensing-phenomenology.git
cd efc-weak-lensing-phenomenology
pip install -r requirements.txt
```

---

## Quick Start

```python
from src.efc_weak_lensing import EFCParams, mu_efc, sigma_lens_efc

# Define EFC parameters
params = EFCParams(
    A_mu=-0.1,      # EFC amplitude (free parameter)
    z_t=2.0,        # Regime transition redshift
    k_star=0.1      # Scale filter [h/Mpc]
)

# Compute μ(k,z) on a grid
import numpy as np
k = np.logspace(-3, 1, 100)  # h/Mpc
z = np.array([0.3, 0.5, 0.7, 1.0])

mu = mu_efc(k, z, params)
sigma = sigma_lens_efc(k, z, params)

print(f"μ(k=0.1, z=0.5) = {mu_efc(0.1, 0.5, params):.3f}")
```

---

## Scientific Context

### The Problem

DES Y6 reports S₈ = 0.789 ± 0.012, approximately 2.6σ lower than Planck CMB predictions (~0.83). This "S₈ tension" motivates testing whether modified gravity can explain the discrepancy.

### The Gap We Identified

**EFC as published does not automatically predict modified lensing.**

The entropy field S(x) evolves independently of matter density. There is no coupling term `Σ = Σ(ρ_m)` in the action.

### Our Solution: Postulat A

We introduce a minimal operational closure:

```
δΣ(k,z) = ξ ρ_m(z) δ_m(k,z) g(z) h(k)
```

This is explicitly an **assumption**, not a derivation. It provides the minimal structure needed for testable predictions.

---

## Validation Protocol

### Pass/Fail Criteria

| Criterion | Pass | Fail |
|-----------|------|------|
| Δχ² (EFC vs ΛCDM) | ≥ 6 | < 2 |
| A_μ significance | > 2σ from 0 | consistent with 0 |
| AIC/BIC | prefers EFC | prefers ΛCDM |

### What Would Falsify This

1. **A_μ = 0**: No improvement over ΛCDM
2. **A_μ > 0**: Wrong sign (increases lensing)
3. **CMB lensing conflict**: Disagrees with Planck
4. **Nuisance degeneracy**: Absorbed by systematics

---

## Citation

```bibtex
@article{Magnusson2026_WL,
  author  = {Magnusson, Morten},
  title   = {{EFC Weak Lensing Phenomenology: A Testable $\mu(k,z)$ Framework 
             and DES Y6 Validation Protocol}},
  year    = {2026},
  month   = {January},
  doi     = {10.6084/m9.figshare.31188193},
  url     = {https://doi.org/10.6084/m9.figshare.31188193}
}
```

---

## Related Work

| Publication | DOI | Description |
|-------------|-----|-------------|
| EFC Field Equations | [10.6084/m9.figshare.30421807](https://doi.org/10.6084/m9.figshare.30421807) | Original field equations |
| EFC Master Specification | [10.6084/m9.figshare.30630500](https://doi.org/10.6084/m9.figshare.30630500) | Complete framework |
| This work | [10.6084/m9.figshare.31188193](https://doi.org/10.6084/m9.figshare.31188193) | Weak lensing phenomenology |

---

## License

This work is licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

## Author

**Morten Magnusson**  
Independent Researcher, Norway  
ORCID: [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)  
Web: [energyflow-cosmology.com](https://energyflow-cosmology.com)

---

*Developed in collaboration with the Symbiose AI research system.*
