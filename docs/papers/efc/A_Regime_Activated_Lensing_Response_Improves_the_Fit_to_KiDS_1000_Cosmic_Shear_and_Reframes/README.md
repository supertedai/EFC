# A Regime-Activated Lensing Response Improves the Fit to KiDS-1000 Cosmic Shear and Reframes the S8 Tension

## AI-Friendly Package

This package provides machine-readable data, code, and documentation for the paper
"A Regime-Activated Lensing Response Improves the Fit to KiDS-1000 Cosmic Shear and Reframes the S8 Tension"
by Morten Magnusson (2026).

**DOI**: [10.6084/m9.figshare.31271917](https://doi.org/10.6084/m9.figshare.31271917)

---

## Abstract

Weak gravitational lensing measurements from KiDS-1000 and other surveys report
S8 ≡ σ8√(Ωm/0.3) values 2–3σ below Planck-CMB predictions. We show that introducing
a regime-activated lensing response Σ(k,z) reduces −2lnL by ≈50.9, effectively resolving
the apparent tension. Σ captures scale- and redshift-dependent modifications to the
matter–light coupling, motivated by thermodynamic corrections that become significant
only where gravitational gradients exceed a characteristic scale.

---

## Key Results

| Parameter | Best-fit Value | Description |
|-----------|----------------|-------------|
| α | 0.10 | Amplitude of lensing response |
| k_trans | 0.1 h/Mpc | Transition wavenumber |
| z_activ | 0.5 | Activation redshift |
| Σ(pivot) | ≈1.13 | Response at k=0.3 h/Mpc, z=0.3 |
| Δ(-2lnL) | ≈-50.9 | Likelihood improvement |

### The S8 Tension Reframing

The paper argues that the S8 tension is not a discrepancy in σ8 but rather a
misattribution caused by assuming Σ=1:

- **Observed**: S8_WL = 0.759 (KiDS-1000)
- **Planck CMB**: S8_CMB = 0.834
- **Reinterpretation**: S_WL = σ8 × Σ = 0.734 × 1.13 ≈ 0.829

When accounting for the lensing response, the apparent tension dissolves.

---

## Model Description

### Lensing Response Function

The effective power spectrum is modified as:

```
P_eff(k,z) = P_ΛCDM(k,z) × Σ²(k,z)
```

where the lensing response Σ(k,z) is:

```
Σ(k,z) = Σ_k(k) × Σ_z(z)

Σ_k(k) = 1 + α × tanh((k - k_trans) / 0.05)
Σ_z(z) = 1 + α × (1 - z/z_activ)    for z < z_activ
       = 1                           for z ≥ z_activ
```

### Physical Motivation

In Energy-Flow Cosmology (EFC), entropy gradients modify the metric perturbation
that couples matter to light. This produces scale- and redshift-dependent corrections
to gravitational lensing that become significant only where:
- Wavenumber k exceeds k_trans (nonlinear clustering regime)
- Redshift z is below z_activ (late-time structure formation)

---

## Tomographic Fingerprint

The improvement is **not uniform** across tomographic bins:

| Bin Pair | Improvement per Datapoint |
|----------|---------------------------|
| Low-z (z < 0.5) | 3.2× average |
| High-z (z > 0.7) | 0.4× average |

This "fingerprint" matches the prediction: corrections should be strongest at
low redshift where structures are most evolved.

---

## Package Contents

```
├── README.md              # This file
├── index.json             # Machine-readable metadata and results
├── LICENSE                # CC-BY-4.0
├── CITATION.cff           # Citation metadata
├── src/
│   └── lensing_response.py    # Reference implementation of Σ(k,z)
├── data/
│   └── kids1000_results.json  # Fit results and likelihood data
└── examples/
    └── lensing_response_demo.py  # Demonstration script
```

---

## Quick Start

```python
from src.lensing_response import LensingResponse, S8Reframing

# Initialize with best-fit parameters
model = LensingResponse(alpha=0.10, k_trans=0.1, z_activ=0.5)

# Calculate lensing response at specific k, z
sigma = model.sigma(k=0.3, z=0.3)
print(f"Σ(k=0.3, z=0.3) = {sigma:.3f}")  # ≈1.13

# Effective power spectrum modification
p_ratio = model.power_ratio(k=0.3, z=0.3)
print(f"P_eff/P_ΛCDM = {p_ratio:.3f}")  # ≈1.28

# S8 tension reframing
reframe = S8Reframing()
result = reframe.reconcile(s8_wl=0.759, sigma8_true=0.734, sigma_pivot=1.13)
print(f"Reframed S_WL = {result['s_wl_reframed']:.3f}")  # ≈0.829
```

---

## Comparison with Standard ΛCDM

| Aspect | ΛCDM | ΛCDM + Σ(k,z) |
|--------|------|---------------|
| Free parameters | 6 | 9 (+3) |
| KiDS-1000 χ² | Reference | Δχ² ≈ -50.9 |
| S8 tension | 2-3σ | Resolved |
| Physical interpretation | σ8 difference | Lensing coupling difference |

---

## Relation to EFC Framework

This paper is part of the Energy-Flow Cosmology research program:

1. **Core theory**: Entropy gradients modify spacetime response
2. **Galaxy scales**: SPARC rotation curves, μ(g_bar) function
3. **Cluster scales**: Bullet Cluster, lensing-mass calibration
4. **Cosmological scales**: BAO, this work (weak lensing)

The lensing response Σ(k,z) is the cosmological manifestation of the
entropy-gradient coupling that appears as μ(g_bar) at galaxy scales.

---

## Citation

```bibtex
@article{magnusson2026lensing,
  author = {Magnusson, Morten},
  title = {A Regime-Activated Lensing Response Improves the Fit to
           KiDS-1000 Cosmic Shear and Reframes the S8 Tension},
  year = {2026},
  doi = {10.6084/m9.figshare.31271917},
  note = {Energy-Flow Cosmology Working Paper}
}
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
