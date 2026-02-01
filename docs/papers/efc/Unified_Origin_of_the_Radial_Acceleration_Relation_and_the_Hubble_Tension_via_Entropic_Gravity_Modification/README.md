# Unified Origin of the Radial Acceleration Relation and the Hubble Tension via Entropic Gravity Modification

## AI-Friendly Package

**DOI**: [10.6084/m9.figshare.31223908](https://doi.org/10.6084/m9.figshare.31223908)
**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper demonstrates that two major anomalies in modern astrophysics arise from the **same physical mechanism**:

1. **Hubble Tension**: The 4-6σ discrepancy between H₀ measured from CMB (~67.4 km/s/Mpc) vs local methods (~73 km/s/Mpc)
2. **Radial Acceleration Relation (RAR)**: The tight correlation between observed and baryonic accelerations in galaxies

**Key Result**: Using the gravitational coupling coefficient a_G ≈ 0.1 from MOND/RAR phenomenology, combined with the Friedmann constraint a_H₀ = ½a_G, we predict H₀ ≈ 74 km/s/Mpc—matching observations within **1.2%**.

## Core Equations

### 1. Grid State Function (from Core Lock)
```
f(S) = f₀ exp(-S/ΔS)
```

### 2. Accumulated Phase
```
Φ(S) = (ΔS/f₀)[exp(S/ΔS) - 1]
```
With normalization ΔS = f₀ = 1: Φ(S) = eˢ - 1

### 3. Entropy Mapping S(z)
```
S(z) = ½[1 - tanh((ln(1+z) - ln(1+z_trans))/Δ)]
```
With z_trans = 3 (Cosmic Noon), Δ = 0.5

### 4. Observable Projection Law
```
ln(X/X₀) = a_X · Φ(S)
```

### 5. Effective Gravitational Coupling
```
G_eff(S) = G₀ exp(a_G · ΔΦ)
```

### 6. The Friedmann Constraint (NOT fitted!)
```
a_H₀ = ½ a_G
```
This factor of ½ emerges directly from the Friedmann equation structure H² ∝ G_eff · ρ.

## Key Results

### From Hubble Tension Data
| Parameter | Value | Source |
|-----------|-------|--------|
| H₀ (SH0ES) | 73.0 km/s/Mpc | Local |
| H₀ (Planck) | 67.4 km/s/Mpc | CMB |
| ln(73.0/67.4) | 0.0798 | - |
| ΔΦ | 1.71 | - |
| a_H₀ | 0.0467 | Derived |
| a_G | 0.094 | = 2 × a_H₀ |

### From MOND Transition Zone
| g_bar/a₀ | μ | μ⁻¹ | ln(μ⁻¹) | Implied a_G |
|----------|------|------|---------|-------------|
| 1.0 | 0.500 | 2.000 | 0.693 | 0.406 |
| 2.0 | 0.667 | 1.500 | 0.405 | 0.238 |
| **5.0** | **0.833** | **1.200** | **0.182** | **0.107** |
| 10.0 | 0.909 | 1.100 | 0.095 | 0.056 |

### Comparison
| Source | a_G | Method |
|--------|-----|--------|
| H₀ tension | 0.094 | Cosmological |
| MOND transition (g/a₀=5) | 0.107 | Galactic |
| **Discrepancy** | **14%** | - |

### Prediction
Using a_G = 0.107 from MOND (independent of H₀):
```
H₀_pred = 67.4 × exp(0.107/2 × 1.71) = 73.9 km/s/Mpc
```
**Observed**: 73.0 km/s/Mpc
**Deviation**: 1.2%

## Physical Interpretation

The cosmic web and large-scale filamentary structures reside in the MOND transition zone (g_bar ≈ few × a₀), where gravitational enhancement is approximately 10-20%. This explains why:

1. **Galaxy rotation curves** show MOND-like behavior
2. **Cosmological H₀** differs between early and late universe measurements

Both are manifestations of the same entropy-driven gravitational modification.

## Package Contents

```
├── README.md                 # This file
├── QUICKSTART.md            # 5-minute introduction
├── MANIFEST.md              # File listing
├── CITATION.cff             # Citation metadata
├── LICENSE                  # CC-BY-4.0
├── index.json               # Machine-readable metadata
├── H0Unification.jsonld     # Schema.org semantic data
├── schema.json              # JSON Schema
├── citations.bib            # BibTeX references
│
├── docs/
│   ├── core_lock_review.md   # Core Lock dynamics
│   ├── entropy_mapping.md    # S(z) sigmoid function
│   ├── friedmann_constraint.md # The ½ factor derivation
│   └── mond_connection.md    # MOND/RAR connection
│
├── src/
│   ├── __init__.py
│   ├── entropy_mapping.py    # S(z) implementation
│   ├── phase_calculator.py   # Φ(S) computation
│   ├── h0_predictor.py       # H₀ prediction from a_G
│   ├── mond_interpolation.py # MOND μ(x) functions
│   └── unification.py        # Full unification analysis
│
├── data/
│   ├── h0_measurements.json  # H₀ data (SH0ES, Planck)
│   ├── mond_table.json       # MOND interpolation table
│   └── parameters.json       # Framework parameters
│
└── examples/
    ├── h0_prediction.py      # Predict H₀ from MOND
    └── unification_demo.py   # Full demonstration
```

## Quick Usage

```python
from src.h0_predictor import predict_h0
from src.mond_interpolation import compute_aG_from_mond

# Get a_G from MOND transition zone
aG = compute_aG_from_mond(g_ratio=5.0, delta_phi=1.71)
print(f"a_G from MOND: {aG:.3f}")  # 0.107

# Predict H₀
h0_pred = predict_h0(
    h0_cmb=67.4,
    aG=aG,
    delta_phi=1.71
)
print(f"Predicted H₀: {h0_pred:.1f} km/s/Mpc")  # 73.9
```

## Falsification Criteria

This framework is **falsifiable**:

1. **a_G from SPARC fits** must yield ~0.1
2. **Correlation signature** d ln v / d ln c must be constant
3. **Independent H₀ measurements** must converge toward ~74 km/s/Mpc

## Epistemic Status

**Layer B**: Mathematical prediction compatible with current observations.

The value a_G ≈ 0.1 from MOND phenomenology is an order-of-magnitude consistency check. A full empirical determination from SPARC rotation curve data is needed for definitive confirmation.

## Related EFC Papers

- [Core Lock](../Core-Lock/) - Mathematical engine (DOI: 10.6084/m9.figshare.31223503)
- [EBE Core Principles](../EBE-Core-Principles/) - Methodology (DOI: 10.6084/m9.figshare.31222903)
- [RCMP](../The-Regime-Consistent-Measurement-Principle-RCMP-A-Methodological-Framework-for-Multi-Scale-Physics/) - Measurement protocol

## Citation

```bibtex
@article{magnusson2026h0unification,
  author = {Magnusson, Morten},
  title = {Unified Origin of the Radial Acceleration Relation and the
           Hubble Tension via Entropic Gravity Modification},
  year = {2026},
  doi = {10.6084/m9.figshare.31223908},
  note = {EFC-H0 Unification Paper v1.0}
}
```
