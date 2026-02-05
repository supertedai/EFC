# M2 EFC ACTIVATION REPORT

**Date:** 2026-02-05
**Testbed:** KiDS-1000 Cosmic Shear (Flinc ξ± data)
**Status:** ✅ COMPLETE

---

## EXECUTIVE SUMMARY

EFC (Energy-Flow Cosmology) gravitational response modification has been
successfully integrated into the KCAP/CosmoSIS weak lensing pipeline.

**Key Finding:** EFC with α=0.05 **improves** the fit to KiDS-1000 data
compared to ΛCDM, with Δχ² = -37.2 (better fit).

---

## M2 IMPLEMENTATION

### M2.1: EFC Sigma Module
**File:** `ShearTestbed_v1/efc_sigma.py`

Implemented Σ(k,z) gravitational response:
```
Σ(k,z) = μ_EFC(k, S(z)) × [1 + η(k,z)] / 2

For M2 test (η=1):
Σ(k,z) = μ_EFC(k, z)
```

Phenomenological parametrization:
- Scale dependence: `k_factor = 1 + α × tanh((k - k_t)/0.05)`
- Redshift activation: `z_factor = 1 + α × (1 - z/z_a)` for z < z_a
- Combined: `Σ = k_factor × z_factor`

### M2.2: Standalone Test
All tests passed:
- ΛCDM limit: Σ = 1.0 exactly ✅
- Zero alpha limit: Σ = 1.0 exactly ✅
- 2D grid generation: Working ✅

### M2.3: KCAP Integration
**File:** `kcap/cosmosis-standard-library/structure/projection/efc_project_2d.py`

Extended `SpectrumCalculator` class to apply EFC modification:
```python
P_EFC(k,z) = P_ΛCDM(k,z) × Σ(k,z)²
```

Pipeline configurations created:
- `KiDS1000_Flinc_EFC_null.ini` - ΛCDM mode (null test)
- `KiDS1000_Flinc_EFC.ini` - Phenomenological mode (active EFC)

---

## M2.4: ΛCDM vs EFC COMPARISON RESULTS

### Test Parameters
| Parameter | Value |
|-----------|-------|
| EFC mode | phenomenological |
| α (alpha) | 0.05 |
| k_transition | 0.1 h/Mpc |
| z_activation | 0.5 |

### Σ(k,z) Statistics
| Statistic | Value |
|-----------|-------|
| Σ minimum | 0.9518 |
| Σ maximum | 1.1025 |
| Σ mean | 1.0248 |
| mean(Σ²) | 1.0520 |

### Likelihood Comparison

| Model | -ln(L) | χ² | χ²/dof |
|-------|--------|-----|--------|
| **ΛCDM baseline (M1.1)** | 349.68 | 699.4 | 3.59 |
| **EFC null test** | 349.68 | 699.4 | 3.59 |
| **EFC active (α=0.05)** | 331.08 | 662.2 | 3.40 |

### Key Results

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Δ(-ln(L))** | **-18.60** | EFC has HIGHER likelihood |
| **Δχ²** | **-37.2** | EFC is BETTER fit to data |
| **Σ² enhancement** | 5.2% | Mean power spectrum boost |

---

## INTERPRETATION

### Physical Meaning
The EFC modification with α=0.05 produces:
1. **Enhanced lensing at low redshift (z < 0.5):** Σ > 1
2. **Enhanced lensing at high k (k > 0.1 h/Mpc):** Σ > 1
3. **Combined effect:** ~5% average enhancement to P(k,z)

### Implications for S₈ Tension
The improvement in fit (Δχ² = -37.2) suggests that:
- EFC-type modifications could potentially address the S₈ tension
- The direction of the modification (enhanced lensing at low-z, high-k)
  is consistent with requiring LOWER S₈ to fit the data

### Caveats
- This is a phenomenological test with simplified parametrization
- Full EFC derivation requires proper field-theoretic calculation
- Parameter α=0.05 is arbitrary; proper inference needed
- Systematics not fully explored

---

## NULL TEST VALIDATION

The EFC null test (efc_mode='lcdm') produces **identical** results to M1.1:
- -ln(L) = 349.68 (both)
- This validates the EFC hook does not introduce numerical artifacts

---

## FILES CREATED

```
ShearTestbed_v1/
├── efc_sigma.py                          # EFC Sigma module
├── M2_EFC_ACTIVATION_REPORT.md           # This report
└── kcap/
    ├── cosmosis-standard-library/
    │   └── structure/projection/
    │       └── efc_project_2d.py         # EFC-enabled projection
    └── runs/config/
        ├── KiDS1000_Flinc_EFC.ini        # Active EFC config
        └── KiDS1000_Flinc_EFC_null.ini   # Null test config
```

---

## NEXT STEPS (M3)

1. **Parameter exploration:** Vary α, k_t, z_a to map likelihood surface
2. **MCMC inference:** Run chains to constrain EFC parameters
3. **Derived EFC:** Implement full field-theoretic Σ(k,z)
4. **Cross-validation:** Test against other weak lensing datasets

---

## M2 SIGN-OFF

**M2 EFC ACTIVATION: ✅ SUCCESSFUL**

- EFC module implemented and tested
- KCAP integration complete
- Null test validates hook (identical to ΛCDM)
- EFC improves fit to KiDS-1000 data (Δχ² = -37.2)

**Date:** 2026-02-05
**Pipeline Version:** v2.0 (EFC-enabled)
