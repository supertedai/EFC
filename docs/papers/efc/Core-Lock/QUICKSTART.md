# EBE Core Lock - Quick Start Guide

## 5-Minute Overview

**Core Lock** provides the mathematical engine for Entropy-Bounded Empiricism through a single constraint equation that governs how physical observables change across entropy regimes.

## The Core Equation

```
β_f(S) = -1/ΔS
```

Where:
- `β_f` = RG-flow beta function for observable f
- `S` = entropy parameter
- `ΔS` = characteristic entropy scale

## Grid State Function

The fundamental solution:

```
f(S) = f₀ exp(-S/ΔS)
```

This describes how any projected observable `f` varies with entropy `S`.

## Quick Implementation

```python
from core_lock import GridStateFunction, BetaConstraint

# Define grid state function
gsf = GridStateFunction(f0=1.0, delta_s=0.5)

# Compute observable at given entropy
s_value = 1.2
f_value = gsf.evaluate(s_value)
print(f"f({s_value}) = {f_value}")

# Verify beta constraint
beta = BetaConstraint(delta_s=0.5)
beta_value = beta.compute(s_value)
print(f"β_f({s_value}) = {beta_value}")
```

## Falsification Criterion

The correlation signature test:

```
d ln v / d ln c = a_v / a_c = constant
```

If this ratio varies beyond measurement uncertainty, the framework is falsified.

## Key Concepts

| Concept | Description |
|---------|-------------|
| Grid State | The pre-geometric substrate |
| β-constraint | Universal RG-flow behavior |
| Information Length | Conserved quantity in projections |
| Projection Laws | How observables emerge from grid |

## Epistemic Status

**Layer B**: Mathematical engine compatible with current null results (no new physics detected at high precision).

## Relationship to EBE

```
EBE Core Principles → Core Lock → Observable Predictions
     (Framework)      (Engine)      (Testable)
```

## Next Steps

1. Read the full paper: `Core_Lock.pdf`
2. Run simulations in `src/core_lock_simulation.py`
3. See `examples/` for verification tests
4. Review figures: `core_lock_survival_test.png`

## Citation

```bibtex
@article{magnusson2026corelock,
  author = {Magnusson, Morten},
  title = {EBE Core Lock v1.0: The S-Dynamic Foundation},
  year = {2026},
  doi = {10.6084/m9.figshare.31223503}
}
```
