# Epistemic Layer Structure (L0-L3)

## Overview

The RCMP framework uses a four-layer epistemic hierarchy to classify measurements and derived quantities by their distance from direct observation.

## Layer Definitions

### L0: Direct Measurement

**Definition:** Raw sensor output with minimal processing.

**Characteristics:**
- Immediate instrument reading
- No model-dependent interpretation
- Uncertainty is purely instrumental

**Examples:**
| Domain | L0 Measurement |
|--------|----------------|
| Galaxy dynamics | Spectral line wavelength |
| Cosmology | Photon counts |
| Particle physics | Detector hits |
| Climate science | Thermometer reading |

**Uncertainty sources:**
- Sensor noise
- Calibration drift
- Environmental factors

### L1: Calibrated Observable

**Definition:** Instrument-corrected measurement.

**Characteristics:**
- Standard calibrations applied
- Instrument response modeled
- Background subtracted

**Examples:**
| Domain | L1 Observable |
|--------|---------------|
| Galaxy dynamics | Rotation velocity V(R) |
| Cosmology | Apparent magnitude |
| Particle physics | Particle momentum |
| Climate science | Calibrated temperature |

**Transformation from L0:**
- Instrument response function
- Calibration coefficients
- Background subtraction

**Uncertainty additions:**
- Calibration uncertainty
- Background estimation error
- Response function uncertainty

### L2: Derived Quantity

**Definition:** Quantity computed from L1 observables using physical models.

**Characteristics:**
- Requires physical assumptions
- Model-dependent
- Multiple L1 inputs may combine

**Examples:**
| Domain | L2 Quantity |
|--------|-------------|
| Galaxy dynamics | Centripetal acceleration $g_{obs}$ |
| Cosmology | Distance modulus |
| Particle physics | Invariant mass |
| Climate science | Heat flux |

**Transformation from L1:**
- Physical model application
- Coordinate transformations
- Error propagation through equations

**Uncertainty additions:**
- Model uncertainty
- Parameter uncertainty
- Systematic effects

### L3: Theoretical Construct

**Definition:** Quantity inferred from L2 via theoretical framework.

**Characteristics:**
- Theory-dependent
- May involve unobservable entities
- Highest interpretation dependency

**Examples:**
| Domain | L3 Construct |
|--------|--------------|
| Galaxy dynamics | Dark matter density profile |
| Cosmology | Hubble parameter |
| Particle physics | Quark mass |
| Climate science | Climate sensitivity |

**Transformation from L2:**
- Theoretical model fitting
- Inverse problem solutions
- Parameter inference

**Uncertainty additions:**
- Theoretical model uncertainty
- Degeneracies
- Prior dependencies

## Layer Transitions

### L0 → L1: Calibration
```
Raw data → Calibration model → Observable
         ↓
    σ_calibration added
```

### L1 → L2: Physical Derivation
```
Observable → Physical model → Derived quantity
           ↓
      σ_model added
```

### L2 → L3: Theoretical Inference
```
Derived quantity → Theoretical framework → Construct
                 ↓
           σ_theory added
```

## Uncertainty Accumulation

Total uncertainty at layer $n$:

$$\sigma_n = \sqrt{\sigma_{n-1}^2 + \sigma_{transition}^2}$$

Or with correlations:

$$\sigma_n^2 = \sigma_{n-1}^2 + \sigma_{transition}^2 + 2\rho\sigma_{n-1}\sigma_{transition}$$

## Example: Galaxy Rotation Curve

### Complete Layer Chain

| Layer | Quantity | Transformation | σ Added |
|-------|----------|----------------|---------|
| L0 | Spectral line λ | Raw measurement | 0.001 |
| L1 | Velocity V | Doppler formula + inclination | 0.02 |
| L2 | Acceleration $g_{obs}$ | $g = V^2/R$ | 0.05 |
| L3 | DM density $ρ_{DM}$ | NFW profile fit | 0.2 |

### Proxy Chain Documentation

```json
{
  "chain": [
    {
      "layer": "L0",
      "quantity": "spectral_wavelength",
      "sigma": 0.001,
      "assumptions": []
    },
    {
      "layer": "L1",
      "quantity": "rotation_velocity",
      "sigma": 0.02,
      "assumptions": ["thin disk", "circular orbits", "known inclination"]
    },
    {
      "layer": "L2",
      "quantity": "centripetal_acceleration",
      "sigma": 0.05,
      "assumptions": ["Newtonian gravity", "known distance"]
    },
    {
      "layer": "L3",
      "quantity": "dark_matter_density",
      "sigma": 0.2,
      "assumptions": ["NFW profile", "spherical halo", "equilibrium"]
    }
  ],
  "total_sigma": 0.21
}
```

## RCMP Implications

### Driver Proximity by Layer

The physical driver is most directly accessible at lower layers:

- **L1-L2 transition** is often where driver coupling occurs
- **L3 constructs** are typically inferred, not directly coupled

### Regime Tagging

Each layer should carry regime information:

```python
measurement = {
    "value": 2.3e-11,
    "layer": "L2",
    "regime": "low_acceleration",
    "regime_boundary": "g_bar < 1e-11 m/s²"
}
```

### Cross-Validation Across Layers

Different proxy chains may reach the same L2/L3 quantity:

```
Chain A: L0_spectral → L1_velocity → L2_acceleration
Chain B: L0_photometry → L1_surface_brightness → L2_mass → L2_acceleration
```

Comparing chains provides cross-validation.

## Best Practices

1. **Always document layer assignments**
2. **Track uncertainty through each transition**
3. **Identify assumptions at each step**
4. **Prefer lower-layer comparisons when possible**
5. **Be explicit about L3 theory dependence**

---

*Reference: RCMP Framework, Section 3.1*
