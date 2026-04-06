# ISW Cross-Correlation Predictions for Energy-Flow Cosmology with DESI DR1 Tracers

## Overview

Computes ISW-galaxy cross-correlation angular power spectra C_l^Tg for EFC using linear perturbation theory. Introduces the cancellation metric C to quantify opposite-sign contributions from standard and transition kernels.

**Author:** Morten Magnusson
**Affiliation:** Symbiose Research, Sandnes, Norway
**ORCID:** [0009-0002-4860-5095](https://orcid.org/0009-0002-4860-5095)
**DOI:** [10.6084/m9.figshare.31301953](https://doi.org/10.6084/m9.figshare.31301953)
**License:** CC-BY-4.0

---

## Key Results

- Cancellation metric C increases monotonically with tracer overlap with z_t
- EFC predicts A_ISW = 0.29-0.56 vs LCDM A_ISW = 1.0
- Opposite-sign kernel contributions near z_t cause suppression
- Decisive test: Tomographic C_l^Tg in DESI spectroscopic bins overlapping z_t

---

## Core Equations

### Modified Poisson Equation

```
nabla^2 Phi = 4 pi G mu(a) rho_bar delta
mu(a) = 1 + beta * S(a)
```

### ISW Kernel

```
K(a) = d/d(ln a) [mu * D / a] = K_mu + K_mu'
```

### Cancellation Metric

```
C = 1 - |sum_l C_l,tot^Tg| / (|sum_l C_l,mu^Tg| + |sum_l C_l,mu'^Tg|)
```

---

## Quick Start

```python
from src.isw_cross_correlation import ISWCrossCorrelation

isw = ISWCrossCorrelation(beta=0.16, a_t=0.55)
C_metric = isw.cancellation_metric(z_eff=0.93)
print(f"Cancellation metric C = {C_metric:.2f}")
```

---

## License

This work is licensed under [CC-BY-4.0](https://creativecommons.org/licenses/by/4.0/).
