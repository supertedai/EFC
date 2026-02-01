# EBE Core Principles - Quick Start Guide

## 5-Minute Overview

**Entropy-Bounded Empiricism (EBE)** provides a methodology for organizing physical claims by:
1. **S-axis**: Physical regime (entropy/complexity level)
2. **L-axis**: Epistemic layer (measurement proximity)

## Core Concept

```
Claim validity = f(S-regime, L-layer, proxy-chain)
```

## The Two Axes

### S-Axis (Physical Regimes)
| Regime | Description | Example |
|--------|-------------|---------|
| Low-S | Simple, low-entropy | Particle physics |
| Mid-S | Moderate complexity | Stellar dynamics |
| High-S | Complex, high-entropy | Galaxies, cosmology |

### L-Axis (Epistemic Layers)
| Layer | Description | Example |
|-------|-------------|---------|
| L0 | Raw measurement | Photon counts |
| L1 | Calibrated data | Flux values |
| L2 | Derived quantities | Distances, masses |
| L3 | Theoretical constructs | Dark matter density |

## Quick Implementation

```python
from ebe_core import EBEClassifier

classifier = EBEClassifier()

# Tag a measurement
result = classifier.classify(
    observable="galaxy_rotation_velocity",
    measurement_type="spectroscopic",
    regime="high_s"
)

print(f"S-regime: {result.s_regime}")
print(f"L-layer: {result.l_layer}")
print(f"Proxy depth: {result.proxy_depth}")
```

## Key Principles

1. **Regime-Gating**: Claims valid in one regime may not transfer to another
2. **Epistemic Degradation**: Confidence decreases as L-layer increases
3. **Proxy Transparency**: Document all transformations from L0 to Ln

## RCMP Integration

EBE provides the theoretical foundation for the **Regime-Consistent Measurement Protocol (RCMP)**:
- RCMP operationalizes EBE's principles
- Every RCMP validation requires (S, L) coordinates

## Next Steps

1. Read the full paper: `EBE_Core_Principles_v1_0-1.pdf`
2. Explore `src/` for Python implementations
3. See `examples/` for practical applications
4. Review `data/` for structured specifications

## Citation

```bibtex
@article{magnusson2026ebe,
  author = {Magnusson, Morten},
  title = {Entropy-Bounded Empiricism: Core Principles},
  year = {2026},
  doi = {10.6084/m9.figshare.31222903}
}
```
