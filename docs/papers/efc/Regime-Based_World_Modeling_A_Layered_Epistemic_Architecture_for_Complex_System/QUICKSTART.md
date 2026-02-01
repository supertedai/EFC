# Regime-Based World Modeling - Quick Start Guide

## 5-Minute Overview

**RBWM** provides a coordinate system for organizing knowledge claims across:
1. **R-axis**: Regime complexity (field → structure → complex)
2. **L-axis**: Epistemic layer (raw → calibrated → derived → theoretical)

## The (R, L) Coordinate System

Every claim gets coordinates: `(R, L)`

### R-Axis: Physical Regimes
| Code | Regime | Scale | Example |
|------|--------|-------|---------|
| R0 | Field | Fundamental | QFT, spacetime |
| R1 | Structure | Organized | Atoms, crystals |
| R2 | Complex | Emergent | Biology, economics |

### L-Axis: Epistemic Layers
| Code | Layer | Proximity | Example |
|------|-------|-----------|---------|
| L0 | Raw | Direct | Sensor output |
| L1 | Calibrated | Processed | Corrected data |
| L2 | Derived | Computed | Inferred quantities |
| L3 | Theoretical | Model-dependent | Predictions |

## Quick Implementation

```python
from rbwm import WorldModel, Claim

# Create world model
model = WorldModel()

# Add a claim with coordinates
claim = Claim(
    statement="Galaxy rotation curves show flat profiles",
    r_regime="R2",
    l_layer="L2",
    driver="gravitational_acceleration",
    validity_domain="r > 5 kpc"
)

model.add_claim(claim)

# Check regime consistency
result = model.validate_transfer(
    source_regime="R1",
    target_regime="R2",
    claim=claim
)
print(f"Transfer valid: {result.is_valid}")
```

## Regime-Gating Principle

**Key Rule**: Claims cannot freely transfer between regimes without explicit justification.

```
R1 claim ─┬─→ R1 context: Valid
          └─→ R2 context: Requires gating check
```

## Driver Proximity

Claims are stronger when the measured quantity is close to the physical driver:

```
High proximity: Measure force → claim about force
Low proximity:  Measure light → claim about mass → claim about force
```

## Applications

| Domain | R-axis Use | L-axis Use |
|--------|------------|------------|
| Physics | Field/Structure/Complex | Measurement hierarchy |
| Biology | Molecular/Cellular/Organism | Observation layers |
| Economics | Micro/Meso/Macro | Data abstraction |
| AI | Subsymbolic/Symbolic/Emergent | Inference depth |

## Next Steps

1. Read the full paper: `Regime_Based_World_Modeling__A_Layered_Epistemic_Architecture_for_Complex_Systems-1.pdf`
2. Explore `src/` for implementations
3. See `examples/` for domain applications
4. Review `data/` for regime specifications

## Citation

```bibtex
@article{magnusson2026rbwm,
  author = {Magnusson, Morten},
  title = {Regime-Based World Modeling: A Layered Epistemic Architecture for Complex Systems},
  year = {2026},
  doi = {10.6084/m9.figshare.31223650}
}
```
