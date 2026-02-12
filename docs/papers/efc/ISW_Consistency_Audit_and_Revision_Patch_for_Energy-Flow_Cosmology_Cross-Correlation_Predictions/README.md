# ISW Paper Revision Patch

## AI-Friendly Package

This package provides machine-readable data and reference implementations for:

**"ISW Paper Revision Patch: Proposed Corrections to ISW Cross-Correlation Predictions for EFC with DESI DR1 Tracers"**

- **Author**: Morten Magnusson
- **DOI**: [10.6084/m9.figshare.31329082](https://doi.org/10.6084/m9.figshare.31329082)
- **Date**: February 2026
- **Type**: WP2 Internal Note
- **Companion**: ISW Consistency Audit v1.1

---

## Summary

The ISW Consistency Audit (v1.1) established that the originally published A_ISW values (0.56 → 0.15) cannot be reproduced under any self-consistent channel. This revision patch proposes corrections that preserve the core EFC predictions while correcting the quantitative claims.

---

## Key Corrections

### Category 1: Retracted A_ISW Values

| Tracer  | z_eff | Original (withdrawn) | Revised |
|---------|-------|---------------------|---------|
| LRGz0   | 0.510 | ~~0.56~~            | 0.87    |
| LRGz1   | 0.706 | ~~0.43~~            | 0.87    |
| LRGz2   | 0.930 | ~~0.33~~            | 0.89    |
| LRG+ELG | 0.930 | ~~0.29~~            | 0.89    |
| ELG     | 1.317 | ~~0.15~~            | 0.92    |
| QSO     | 1.491 | ~~0.20~~            | 0.90    |

**Key insight**: A_ISW is nearly z-independent (0.87–0.92), representing a uniform ~11% suppression relative to ΛCDM, not the 44–85% originally claimed.

### Category 2: μ-Channel Interpretation

Two distinct interpretations must be distinguished:

1. **Growth-driven** (adopted):
   - Φ ∝ D(a)/a
   - μ affects ISW only through D(a) and f(a)
   - ISW source: S ∝ H(a)(D/a)(1-f)
   - Prediction: A_ISW ≈ 0.89 (positive)

2. **Potential-driven** (MG-type):
   - Φ ∝ μ(a)·D(a)/a
   - ISW kernel contains explicit dμ/d ln a term
   - Prediction: Anti-correlation (A < 0) for z_eff ≳ 0.6
   - Disfavoured by existing positive ISW detections

### Category 3: Cancellation Metric

The cancellation index C is **not applicable** under growth-driven ISW:
- No separate K_μ' channel exists
- Observable discriminator is now the uniform 11% suppression

---

## Elements Preserved

| Element | Status |
|---------|--------|
| Growth ODE, eq. (1) | Correct. μ(a) in growth equation is well-defined |
| μ(a) parameterisation | Correct. β = 0.16, a_t = 0.55, σ = 0.25 unchanged |
| Limber approximation | Valid. Exact non-Limber differs by < 3% |
| Tracer definitions | Valid. DESI DR1 bins and bias values unchanged |
| H(a) background | Valid. Fiducial ΛCDM background is correct |
| Qualitative prediction | Valid. EFC predicts A_ISW < 1 for all tracers |

---

## Revised Falsification Criterion

**Original**: C > 0.7, A < 0.5 at z_t

**Revised**: If A_ISW = 1.00 ± 0.05 across all bins in a combined multi-tracer stack, the EFC growth-channel modification would be excluded at > 2σ.

**Positive evidence**: A_ISW < 0.9 across multiple bins would constitute positive evidence for EFC.

---

## Validation Ledger Update

| Field | Current (v1.6) | Revised |
|-------|----------------|---------|
| Status | Completed | Under revision |
| A_ISW | 0.29–0.56 | 0.87–0.92 |
| C | 0.59–0.96 | Not applicable |
| Key discriminator | Tomographic C gradient | Uniform 11% suppression |

---

## Package Contents

```
ISW_Consistency_Audit_and_Revision_Patch/
├── README.md                    # This file
├── index.json                   # Machine-readable metadata
├── isw_revision_patch.pdf       # Original paper
├── src/
│   └── isw_revision.py          # Reference implementation
├── data/
│   └── revised_predictions.json # Revised A_ISW values
├── examples/
│   └── isw_revision_demo.py     # Demonstration script
├── CITATION.cff                 # Citation metadata
└── LICENSE                      # MIT License
```

---

## Quick Start

```python
from src.isw_revision import RevisedISWPredictions, ChannelComparison

# Get revised predictions
predictions = RevisedISWPredictions()

# Compare original vs revised
for tracer in predictions.tracers:
    original = predictions.get_original(tracer)
    revised = predictions.get_revised(tracer)
    print(f"{tracer}: {original:.2f} → {revised:.2f}")

# Channel comparison
channels = ChannelComparison()
print(f"Growth-driven: A_ISW ≈ {channels.growth_driven:.2f}")
print(f"Potential-driven at z>0.6: A_ISW < 0 (anti-correlation)")
```

---

## Core Equations

### Growth-Driven ISW Source

```
S ∝ H(a) × (D/a) × (1 - f)

where:
  f = d ln D / d ln a  (growth rate)
  D(a) = growth factor modified by μ(a)
```

### μ(a) Parameterisation (unchanged)

```
μ(a) = 1 + β × exp[-(a - a_t)² / (2σ²)]

Parameters:
  β = 0.16
  a_t = 0.55
  σ = 0.25
```

### Revised A_ISW Prediction

```
A_ISW^EFC ≈ 0.89 ± 0.03  (all tracers)

Suppression relative to ΛCDM: ~11%
z-dependence: negligible
```

---

## Key Findings

1. **Original A_ISW values cannot be reproduced** under any self-consistent channel
2. **Revised prediction**: Uniform ~11% suppression (A_ISW ≈ 0.89)
3. **No z-dependence** in growth-driven interpretation
4. **Cancellation metric C is not applicable** under growth-driven ISW
5. **Falsification threshold revised** to A_ISW = 1.00 ± 0.05

---

## Citation

```bibtex
@misc{magnusson2026isw_revision,
  author       = {Magnusson, Morten},
  title        = {{ISW Paper Revision Patch: Proposed Corrections to
                  ISW Cross-Correlation Predictions for EFC with
                  DESI DR1 Tracers}},
  year         = {2026},
  month        = feb,
  publisher    = {Figshare},
  doi          = {10.6084/m9.figshare.31329082},
  note         = {WP2 Internal Note, Companion to ISW Consistency Audit v1.1}
}
```

---

## Related Papers

- ISW Cross-Correlation Predictions for EFC with DESI DR1 Tracers (DOI: 10.6084/m9.figshare.31301953)
- ISW Consistency Audit v1.1 (companion document)
- EFC Regime-Transition Fit to DESI DR2 BAO (DOI: 10.6084/m9.figshare.31230703)
