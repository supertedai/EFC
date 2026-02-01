# The Hubble Tension as Regime Mismatch

## AI-Friendly Package

**DOI**: [10.6084/m9.figshare.31224247](https://doi.org/10.6084/m9.figshare.31224247)
**Version**: 1.0
**Author**: Morten Magnusson (ORCID: 0009-0002-4860-5095)
**Date**: February 2026
**License**: CC-BY-4.0

## Overview

This paper proposes that the Hubble tension is **not** a temporal evolution problem but a **regime mismatch**:

| Probe Type | Regime | Effective G | H₀ Inferred |
|------------|--------|-------------|-------------|
| CMB (Planck) | Background | G₀ | 67.4 |
| BAO | Background | G₀ | ~67 |
| SN Ia + Cepheids | Structure | G_eff > G₀ | 73.0 |
| TRGB | Structure | G_eff > G₀ | ~70 |
| Masers | Structure | G_eff > G₀ | ~73 |

**Key Insight**: The tension arises because different measurement methods probe different gravitational regimes—not because H₀ changed over time.

## The Two Regimes

### Background Regime (Linear, Smooth)
- CMB, BAO measurements
- Probes the homogeneous universe
- Measures G₀ (bare gravitational constant)

### Structure Regime (Nonlinear, Collapsed)
- SNe Ia, Cepheids, TRGB, Masers
- Probes inside galaxies and clusters
- Measures G_eff = G₀ exp(a_G · ΔΦ)

## Core Equations

### 1. Regime-Dependent Gravity
```
G_eff(R) = {
    G₀,                      R = background
    G₀ exp(a_G · ΔΦ),        R = structure
}
```

### 2. The Friedmann Constraint
From H² ∝ G_eff · ρ:
```
2 ΔH/H = ΔG/G
```
Therefore:
```
a_H₀ = ½ a_G    (NOT fitted!)
```

### 3. Numerical Prediction
With a_G ≈ 0.094 and ΔΦ ≈ 1.71:
```
ln(H_structure / H_background) = ½ × 0.094 × 1.71 = 0.080
H_structure / H_background = exp(0.080) = 1.083
H₀_structure = 67.4 × 1.083 = 73.0 km/s/Mpc  ✓
```

## Physical Interpretation

| Interpretation | Claim | Implication |
|----------------|-------|-------------|
| **Standard** | H₀ changed over time | Requires new physics in expansion history |
| **Regime** | Different probes see different G | Natural consequence of entropic gravity |

In EFC, gravity emerges from entropy gradients. Collapsed structures have higher local entropy production → G_eff > G₀ in structures.

## Falsification Conditions

1. **Environment dependence**: SNe in voids should give lower H₀ than SNe in clusters
2. **Standard candle systematics**: SN Ia magnitude should show environment-dependent residuals (ΔM ~ 0.02 mag)
3. **Probe consistency**: All background probes → ~67; all structure probes → ~73
4. **a_G from SPARC**: Must yield a_G ≈ 0.1 ± 0.02

**Fail condition**: If SN Ia residuals show NO environmental dependence at ΔM ~ 0.02 mag level

## Package Contents

```
├── README.md                 # This file
├── QUICKSTART.md            # 5-minute introduction
├── MANIFEST.md              # File listing
├── CITATION.cff             # Citation metadata
├── LICENSE                  # CC-BY-4.0
├── index.json               # Machine-readable metadata
├── RegimeMismatch.jsonld    # Schema.org semantic data
├── schema.json              # JSON Schema
├── citations.bib            # BibTeX references
│
├── src/
│   ├── __init__.py
│   ├── regime_classifier.py  # Classify probes by regime
│   ├── g_effective.py        # G_eff calculation
│   ├── h0_predictor.py       # H₀ prediction by regime
│   └── falsification.py      # Falsification test framework
│
├── data/
│   ├── probe_classification.json  # Probe → regime mapping
│   ├── h0_measurements.json       # H₀ values by probe
│   └── parameters.json            # Framework parameters
│
└── examples/
    ├── regime_analysis.py    # Classify and predict
    └── falsification_test.py # Test falsification criteria
```

## Quick Usage

```python
from src.regime_classifier import classify_probe, Regime
from src.h0_predictor import predict_h0_by_regime

# Classify a measurement
regime = classify_probe("SN_Ia_Cepheids")
print(f"Regime: {regime}")  # Regime.STRUCTURE

# Predict H₀ for each regime
h0_bg = predict_h0_by_regime(Regime.BACKGROUND)
h0_st = predict_h0_by_regime(Regime.STRUCTURE)
print(f"Background: {h0_bg:.1f}, Structure: {h0_st:.1f}")
# Background: 67.4, Structure: 73.0
```

## Key Distinction from H₀-RAR Unification Paper

| Paper | Focus |
|-------|-------|
| H₀-RAR Unification | Derives a_G from MOND, predicts H₀ |
| **This paper** | Explains WHY probes disagree (regime mismatch) |

Both papers use the same framework but address different aspects of the Hubble tension.

## Epistemic Status

**Layer B**: Regime-reinterpretation hypothesis, not yet independent measurement.

Confirmation requires:
- Environment-dependent analysis of standard candles
- Direct a_G determination from SPARC rotation curves

## Related EFC Papers

- [H₀-RAR Unification](../Unified_Origin_of_the_Radial_Acceleration_Relation_and_the_Hubble_Tension_via_Entropic_Gravity_Modification/) - Derives a_G ≈ 0.1
- [Core Lock](../Core-Lock/) - Mathematical engine
- [EBE Core Principles](../EBE-Core-Principles/) - Methodology

## Citation

```bibtex
@article{magnusson2026regimemismatch,
  author = {Magnusson, Morten},
  title = {The Hubble Tension as Regime Mismatch: Background Gravity
           vs Structure Gravity in Energy-Flow Cosmology},
  year = {2026},
  doi = {10.6084/m9.figshare.31224247}
}
```
